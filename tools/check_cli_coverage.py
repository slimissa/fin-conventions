#!/usr/bin/env python3
"""
Assert that `cli.py list` includes every convention in the fixture, and that
`cli.py get <id> --start <d1> --end <d2>` returns the fixture's expected value.

Exit 0 if all match, 1 with a named error otherwise.
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

    listed = subprocess.run(
        [sys.executable, "cli.py", "list"],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    if listed.returncode != 0:
        print(f"ERROR: cli.py list exited {listed.returncode}", file=sys.stderr)
        print(listed.stderr, file=sys.stderr)
        return 1
    listed_ids = listed.stdout.split()

    for cid in fixture_ids:
        if cid not in listed_ids:
            print(f"ERROR: {cid} is in the fixture but not in `cli.py list`", file=sys.stderr)
            return 1

    for c in fixture["conventions"]:
        tc = c["math_test_case"]
        actual = subprocess.run(
            [sys.executable, "cli.py", "get", c["convention_id"],
             "--start", tc["start"], "--end", tc["end"]],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        if actual.returncode != 0:
            print(f"ERROR: cli.py get {c['convention_id']} exited {actual.returncode}",
                  file=sys.stderr)
            print(actual.stderr, file=sys.stderr)
            return 1
        got = actual.stdout.strip()
        want = str(tc["expected"])
        if got != want:
            print(f"ERROR: cli.py get {c['convention_id']} returned {got!r}, "
                  f"expected {want!r}", file=sys.stderr)
            return 1

    print(f"OK: {len(fixture_ids)} convention(s) listed and calculable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
