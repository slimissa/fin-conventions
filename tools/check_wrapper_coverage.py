#!/usr/bin/env python3
"""
Assert that `calculate(id, start, end)` returns without NotImplementedError
for every convention in the fixture.

The wrapper is the third surface (after the JSON and the CLI). The ACT/365 PR
omits the wrapper update; this tool catches the omission so the student learns
the full surface-coverage lesson in their first PR.

Exit 0 if every fixture convention is calculable by the wrapper, 1 otherwise.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "conventions.test.json"


def main():
    fixture = json.loads(FIXTURE.read_text())
    fixture_ids = [c["convention_id"] for c in fixture["conventions"]]

    for cid in fixture_ids:
        result = subprocess.run(
            [
                sys.executable, "-c",
                "from fin_conventions import calculate\n"
                f"calculate({cid!r}, '2026-01-01', '2026-01-31')\n"
                "print('OK')\n",
            ],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        if result.returncode != 0:
            print(f"ERROR: wrapper does not know {cid}", file=sys.stderr)
            print(result.stderr.strip(), file=sys.stderr)
            return 1

    print(f"OK: wrapper knows all {len(fixture_ids)} fixture convention(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
