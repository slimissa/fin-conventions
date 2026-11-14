#!/usr/bin/env python3
"""
fin-conventions CLI.

    python3 cli.py get ACT/360 --start 2026-01-01 --end 2026-01-31
    # -> 30

    python3 cli.py list
    # -> ACT/360
"""
import argparse
import sys

from wrappers.python.fin_conventions import Convention, calculate


def cmd_get(args):
    try:
        result = calculate(args.convention_id, args.start, args.end)
    except KeyError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except NotImplementedError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(result)
    return 0


def cmd_list(args):
    import json
    from pathlib import Path
    registry = json.loads((Path(__file__).parent / "fin-conventions.json").read_text())
    for key in ("day_counts", "business_days", "rolls", "frequencies"):
        for entry in registry.get(key, []):
            print(entry["convention_id"])
    return 0


def main():
    p = argparse.ArgumentParser(prog="fin-conventions")
    sub = p.add_subparsers(dest="command", required=True)

    g = sub.add_parser("get", help="Calculate a convention for a date range")
    g.add_argument("convention_id")
    g.add_argument("--start", required=True)
    g.add_argument("--end", required=True)
    g.set_defaults(func=cmd_get)

    l = sub.add_parser("list", help="List all conventions")
    l.set_defaults(func=cmd_list)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
