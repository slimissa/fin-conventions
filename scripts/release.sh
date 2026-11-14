#!/usr/bin/env bash
#
# Deterministic release pipeline for fin-conventions.
#
#   scripts/release.sh <version>            cut a release
#   scripts/release.sh <version> --dry-run  print every step without
#                                            changing files or pushing
#
# Refuses on:
#   dirty tree / wrong branch / CHANGELOG section missing
#   HEAD different from a freshly fetched origin/main
#   VERSION already equal to the target
#   version sites not in agreement AFTER regeneration
#   failing gate (validate, mojibake, pytest, exports)
#   gh missing (CI could not be polled)
#
# Shape: preconditions -> version sites -> regenerate -> gate ->
# commit -> CI -> tag -> verification doc.
#
# fin-conventions is smaller than ISO 10383: one wrapper, no Parquet,
# no snapshots, no cross-registry, no manifest. The gate reflects
# that. Do not port checks that reference files that do not exist.

set -euo pipefail

cd "$(dirname "$0")/.."

VERSION="${1:-}"
DRY_RUN="${2:-}"

if [[ -z "$VERSION" ]]; then
    echo "usage: scripts/release.sh <version> [--dry-run]" >&2
    exit 2
fi

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "FAIL: not semver: $VERSION" >&2
    exit 2
fi

step() { echo; echo "=== $* ==="; }
run()  {
    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        echo "[dry-run] $*"
    else
        "$@"
    fi
}

GATE_LOG=()
gate() {
    local rc=0
    run "$@" || rc=$?
    GATE_LOG+=("$rc|$*")
    if [[ "$rc" -ne 0 ]]; then
        echo "FAIL: gate failed (exit $rc): $*" >&2
        exit "$rc"
    fi
}

# --- Preconditions ---------------------------------------------------------

step "Preconditions"

git fetch origin main \
    || { echo "FAIL: git fetch origin main failed" >&2; exit 1; }

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[[ "$BRANCH" == "main" ]] || { echo "FAIL: not on main ($BRANCH)" >&2; exit 1; }

LOCAL_SHA="$(git rev-parse HEAD)"
REMOTE_SHA="$(git rev-parse origin/main)"
[[ "$LOCAL_SHA" == "$REMOTE_SHA" ]] || {
    echo "FAIL: HEAD ($LOCAL_SHA) != origin/main ($REMOTE_SHA)" >&2
    exit 1
}

if [[ -n "$(git status --porcelain)" ]]; then
    echo "FAIL: working tree is not clean" >&2
    git status --short >&2
    exit 1
fi

if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo "FAIL: tag v$VERSION already exists locally" >&2
    exit 1
fi
REMOTE_TAG="$(git ls-remote --tags origin "refs/tags/v$VERSION")" \
    || { echo "FAIL: git ls-remote against origin failed" >&2; exit 1; }
if [[ -n "$REMOTE_TAG" ]]; then
    echo "FAIL: tag v$VERSION already exists on origin" >&2
    exit 1
fi

grep -q "## \[$VERSION\]" CHANGELOG.md \
    || { echo "FAIL: CHANGELOG.md has no [${VERSION}] section" >&2; exit 1; }

command -v gh >/dev/null 2>&1 || {
    echo "FAIL: gh CLI is required to poll CI before tagging" >&2
    exit 1
}

echo "  preconditions OK"

# --- Version sites ---------------------------------------------------------

step "Version sites"

CURRENT="$(cat VERSION)"
if [[ "$CURRENT" == "$VERSION" ]]; then
    echo "FAIL: VERSION is already $VERSION" >&2
    exit 1
fi

echo "  $CURRENT -> $VERSION"

if [[ "$DRY_RUN" != "--dry-run" ]]; then
    echo "$VERSION" > VERSION

    python3 - <<PY
import json, re
from pathlib import Path
v = "$VERSION"

# fin-conventions.json -> meta.version
p = Path("fin-conventions.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["meta"]["version"] = v
p.write_text(json.dumps(d, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
             encoding="utf-8")

# wrappers/python/pyproject.toml
p = Path("wrappers/python/pyproject.toml")
p.write_text(re.sub(r'^version\s*=\s*"[^"]+"', f'version = "{v}"',
                    p.read_text(encoding="utf-8"), count=1, flags=re.M),
             encoding="utf-8")

# wrappers/python/fin_conventions/__init__.py -> __version__
p = Path("wrappers/python/fin_conventions/__init__.py")
p.write_text(re.sub(r'^__version__\s*=\s*"[^"]+"', f'__version__ = "{v}"',
                    p.read_text(encoding="utf-8"), count=1, flags=re.M),
             encoding="utf-8")

# README.md -> registry badge (if present)
p = Path("README.md")
text = p.read_text(encoding="utf-8")
text = re.sub(r'badge/registry-[0-9]+\.[0-9]+\.[0-9]+-',
              f'badge/registry-{v}-', text)
p.write_text(text, encoding="utf-8")
PY
fi

# --- Regenerate ------------------------------------------------------------

step "Regenerate exports"
run python3 tools/export_csv.py
run python3 tools/export_sql.py

# --- Gate ------------------------------------------------------------------

step "Version consistency (after regeneration)"
gate python3 tools/check_version_consistency.py

step "Validation gate"
gate python3 tools/validate.py
gate python3 tools/check_mojibake.py
gate python3 -m pytest tests/ -q
gate python3 tools/export_csv.py --check
gate python3 tools/export_sql.py --check

# --- Commit, push ----------------------------------------------------------

step "Commit and push"
run git add -A
run git commit -m "Release v$VERSION"
run git push origin main

# --- Poll CI ---------------------------------------------------------------

CI_POLL_INTERVAL=15
CI_POLL_MAX=40

if [[ "$DRY_RUN" != "--dry-run" ]]; then
    step "Waiting for CI"

    SHA="$(git rev-parse HEAD)"
    elapsed=0
    CI_GREEN=false

    while [ "$elapsed" -lt $((CI_POLL_INTERVAL * CI_POLL_MAX)) ]; do
        sleep "$CI_POLL_INTERVAL"
        elapsed=$((elapsed + CI_POLL_INTERVAL))

        RUNS=$(gh run list --limit 30 \
            --json databaseId,headSha,status,conclusion,workflowName \
            --jq ".[] | select(.headSha == \"$SHA\") | \"\(.databaseId)|\(.status)|\(.conclusion // \"pending\")|\(.workflowName)\"" \
            2>/dev/null || echo "")

        if [ -z "$RUNS" ]; then
            echo "  no runs yet (${elapsed}s)"
            continue
        fi

        ALL_COMPLETE=true
        FAILED=false
        while IFS='|' read -r id status conclusion name; do
            if [ "$status" != "completed" ]; then
                ALL_COMPLETE=false
                break
            fi
            if [ "$conclusion" != "success" ]; then
                FAILED=true
                echo "  workflow '$name' (run $id) concluded '$conclusion'" >&2
            fi
        done <<< "$RUNS"

        if [ "$FAILED" = "true" ]; then
            echo "FAIL: CI failed on $SHA" >&2
            exit 1
        fi

        if [ "$ALL_COMPLETE" = "true" ]; then
            echo "  CI passed after ${elapsed}s"
            CI_GREEN=true
            break
        fi

        echo "  waiting... (${elapsed}s)"
    done

    if [ "$CI_GREEN" != "true" ]; then
        echo "FAIL: CI did not complete within " \
             "$((CI_POLL_INTERVAL * CI_POLL_MAX))s" >&2
        exit 1
    fi
fi

# --- Tag -------------------------------------------------------------------

step "Tag v$VERSION"
TAG_MSG="$(python3 - <<PY
import re
text = open("CHANGELOG.md", encoding="utf-8").read()
m = re.search(r"## \[$VERSION\][^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
print((m.group(1).strip() if m else "")[:4000])
PY
)"
[[ -n "$TAG_MSG" ]] || {
    echo "FAIL: CHANGELOG.md [$VERSION] section has no body" >&2
    exit 1
}
TAG_MSG_FILE="$(mktemp)"
printf 'Release v%s\n\n%s\n' "$VERSION" "$TAG_MSG" > "$TAG_MSG_FILE"
[[ -s "$TAG_MSG_FILE" ]] || { echo "FAIL: empty tag message" >&2; exit 1; }
[[ "$(head -n 1 "$TAG_MSG_FILE")" == "Release v$VERSION" ]] || {
    echo "FAIL: tag message header is wrong" >&2
    exit 1
}
if grep -qE '\[(TODO|TBD|PASTE)\]' "$TAG_MSG_FILE"; then
    echo "FAIL: tag message contains a placeholder" >&2
    exit 1
fi
run git tag -a "v$VERSION" -F "$TAG_MSG_FILE" --cleanup=verbatim

if [[ "$DRY_RUN" != "--dry-run" ]]; then
    RECORDED="$(git for-each-ref --format='%(contents)' "refs/tags/v$VERSION")"
    WANTED="$(cat "$TAG_MSG_FILE")"
    if [[ "$RECORDED" != "$WANTED" ]]; then
        git tag -d "v$VERSION" >/dev/null
        rm -f "$TAG_MSG_FILE"
        echo "FAIL: git recorded a different tag message than the file; local tag v$VERSION deleted, nothing pushed" >&2
        exit 1
    fi
fi
rm -f "$TAG_MSG_FILE"
run git push origin "v$VERSION"

# --- Verification doc ------------------------------------------------------

step "Write verification doc"
DOC="docs/v${VERSION}-verification.md"
if [[ "$DRY_RUN" != "--dry-run" ]]; then
    {
        echo "# v$VERSION verification"
        echo
        echo "Released: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        echo "Commit:     $(git rev-parse "v$VERSION^{commit}")"
        echo "Tag object: $(git rev-parse "v$VERSION")"
        echo
        echo "## Gates"
        echo
        echo "Exit codes, in the order the gates ran. A gate that failed would have stopped the release before this file was written."
        echo
        for g in "${GATE_LOG[@]}"; do
            echo "- \`${g#*|}\` — exit ${g%%|*}"
        done
    } > "$DOC"
    git add "$DOC"
    git commit -m "docs: v$VERSION verification"
    git push origin main
fi

echo
echo "Released v$VERSION."