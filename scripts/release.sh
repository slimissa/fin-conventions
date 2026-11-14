#!/usr/bin/env bash
# Release gate for fin-conventions.
# Usage:
#   scripts/release.sh 0.0.1         # run the gate, then tag
#   scripts/release.sh 0.0.1 --dry-run  # run the gate, print what would happen
set -euo pipefail

VERSION="${1:-}"
DRY_RUN="${2:-}"

if [ -z "$VERSION" ]; then
    echo "usage: scripts/release.sh <version> [--dry-run]" >&2
    exit 2
fi

if [ "$(cat VERSION)" != "$VERSION" ]; then
    echo "error: VERSION file is $(cat VERSION), expected $VERSION" >&2
    exit 1
fi

echo "==> validate"
python3 tools/validate.py

echo "==> version consistency"
python3 tools/check_version_consistency.py

echo "==> mojibake"
python3 tools/check_mojibake.py

echo "==> pytest"
python3 -m pytest tests/ -q

echo "==> exports"
python3 tools/export_csv.py --check
python3 tools/export_sql.py --check

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "==> dry run: gate passed, not tagging"
    exit 0
fi

if ! git diff --quiet; then
    echo "error: working tree is dirty. Commit or stash first." >&2
    exit 1
fi

git tag -a "v$VERSION" -m "Release v$VERSION"
echo "==> tagged v$VERSION"
echo "==> to push: git push origin v$VERSION"
