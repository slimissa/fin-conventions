#!/usr/bin/env python3
"""
Detect UTF-8 / Latin-1 round-trip corruption in text files.

Six byte patterns are detected:
  - 'Ã©' etc. (UTF-8 bytes decoded as Latin-1)
  - 'â€™' etc. (UTF-8 punctuation decoded as Latin-1)
  - 'â€œ' etc.
  - 'Ã¢â‚¬â„¢' etc.
  - unclosed code fences (``` with no matching ```)

Exit 0 if clean, 1 if any hit.
"""
import sys
from pathlib import Path

BAD_PATTERNS = [
    "Ã©", "Ã¨", "Ã ", "Ã¢", "Ã´", "Ã§",  # UTF-8 accented chars decoded as Latin-1
    "â€™", "â€œ", "â€\x9d", "â€“", "â€”",  # UTF-8 punctuation decoded as Latin-1
    "Â ", "Â£", "Â©",                      # stray Latin-1 chars from UTF-8
]


def scan(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for pat in BAD_PATTERNS:
        if pat in text:
            hits.append(pat)
    fences = text.count("```")
    if fences % 2 != 0:
        hits.append(f"unclosed code fence ({fences} ```)")
    return hits


def main():
    roots = [Path("README.md"), Path("CONTRIBUTING.md"), Path("CHANGELOG.md")]
    roots += list(Path("docs").rglob("*.md"))
    roots += list(Path("tests").rglob("*.py"))
    roots += list(Path("tools").rglob("*.py"))

    failed = False
    for path in roots:
        if not path.exists():
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
