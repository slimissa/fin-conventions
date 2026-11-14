#!/usr/bin/env python3
"""
Detect UTF-8 / Latin-1 round-trip corruption in text files.
"""
import sys
from pathlib import Path

# Build patterns from hex so this file does not contain the mojibake it detects.
BAD_PATTERNS = [
    bytes.fromhex("c3a9").decode("latin-1"),
    bytes.fromhex("c3a8").decode("latin-1"),
    bytes.fromhex("c3a0").decode("latin-1"),
    bytes.fromhex("c3a2").decode("latin-1"),
    bytes.fromhex("c3b4").decode("latin-1"),
    bytes.fromhex("c3a7").decode("latin-1"),
    bytes.fromhex("e28099").decode("latin-1"),
    bytes.fromhex("e2809c").decode("latin-1"),
    bytes.fromhex("e2809d").decode("latin-1"),
    bytes.fromhex("e28093").decode("latin-1"),
    bytes.fromhex("e28094").decode("latin-1"),
    bytes.fromhex("c2a0").decode("latin-1"),
    bytes.fromhex("c2a3").decode("latin-1"),
    bytes.fromhex("c2a9").decode("latin-1"),
]

def scan(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for pat in BAD_PATTERNS:
        if pat in text:
            hits.append(repr(pat))
    fences = text.count("```")
    if fences % 2 != 0:
        hits.append(f"unclosed code fence ({fences} ```)")
    return hits

def main():
    self_path = Path(__file__).resolve()
    roots = [Path("README.md"), Path("CONTRIBUTING.md"), Path("CHANGELOG.md")]
    roots += list(Path("docs").rglob("*.md"))
    roots += list(Path("tests").rglob("*.py"))
    roots += list(Path("tools").rglob("*.py"))

    failed = False
    for path in roots:
        if not path.exists():
            continue
        if path.resolve() == self_path:
            continue
        hits = scan(path)
        if hits:
            failed = True
            print(f"FAIL: {path}: {hits}", file=sys.stderr)
    if failed:
        return 1
    print("OK: no mojibake, no unclosed fences")
    return 0

if __name__ == "__main__":
    sys.exit(main())
