#!/usr/bin/env python3
"""
Verify the six version sites agree on the version in VERSION.

Sites:
  1. VERSION
  2. CHANGELOG.md top released heading
  3. README.md badge (if present, and once added)
  4. wrappers/python/pyproject.toml
  5. wrappers/python/fin_conventions/__init__.py __version__
  6. fin-conventions.json meta.version

Exit 0 if all agree, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_version():
    return (ROOT / "VERSION").read_text().strip()


def check_changelog(v):
    text = (ROOT / "CHANGELOG.md").read_text()
    headings = re.findall(r"^## \[([^\]]+)\]", text, re.M)
    released = [h for h in headings if h.lower() != "unreleased"]
    if not released:
        return None
    if released[0] != v:
        return f"CHANGELOG.md: top released heading is {released[0]!r}, expected {v!r}"
    return None


def check_pyproject(v):
    text = (ROOT / "wrappers" / "python" / "pyproject.toml").read_text()
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    if not m:
        return "pyproject.toml: no 'version = \"x.y.z\"' line"
    if m.group(1) != v:
        return f"pyproject.toml: version is {m.group(1)!r}, expected {v!r}"
    return None


def check_init(v):
    text = (ROOT / "wrappers" / "python" / "fin_conventions" / "__init__.py").read_text()
    m = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.M)
    if not m:
        return "__init__.py: no '__version__ = \"x.y.z\"' line"
    if m.group(1) != v:
        return f"__init__.py: __version__ is {m.group(1)!r}, expected {v!r}"
    return None


def check_json(v):
    data = json.loads((ROOT / "fin-conventions.json").read_text())
    actual = data.get("meta", {}).get("version")
    if actual != v:
        return f"fin-conventions.json: meta.version is {actual!r}, expected {v!r}"
    return None


def check_readme(v):
    path = ROOT / "README.md"
    if not path.exists():
        return None
    text = path.read_text()
    m = re.search(r"registry-([0-9.]+)-", text)
    if not m:
        return None  # badge not added yet; not a failure
    if m.group(1) != v:
        return f"README.md: badge is {m.group(1)!r}, expected {v!r}"
    return None


def main():
    v = read_version()
    errors = []
    for name, fn in [
        ("CHANGELOG.md", check_changelog),
        ("pyproject.toml", check_pyproject),
        ("__init__.py", check_init),
        ("fin-conventions.json", check_json),
        ("README.md", check_readme),
    ]:
        err = fn(v)
        if err:
            errors.append(err)

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK: all sites agree on {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
