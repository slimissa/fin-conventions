#!/usr/bin/env python3
"""
Export fin-conventions.json to fin-conventions.csv.

The CSV has one row per convention, columns:
  convention_id, type, name, description, formula, source_url

--check mode: regenerate in memory, compare with the committed CSV, exit 1 if different.
"""
import argparse
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "fin-conventions.json"
CSV_PATH = ROOT / "fin-conventions.csv"

COLUMNS = ["convention_id", "type", "name", "description", "formula", "source_url"]
SECTION_TO_TYPE = {
    "day_counts": "day_count",
    "business_days": "business_day",
    "rolls": "roll",
    "frequencies": "frequency",
}


def rows():
    data = json.loads(JSON_PATH.read_text())
    for section, type_name in SECTION_TO_TYPE.items():
        for entry in data.get(section, []):
            yield {
                "convention_id": entry["convention_id"],
                "type": type_name,
                "name": entry["name"],
                "description": entry["description"],
                "formula": entry["formula"],
                "source_url": entry["source_url"],
            }


def render():
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in rows():
        writer.writerow(row)
    return buf.getvalue()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()

    expected = render()

    if args.check:
        if not CSV_PATH.exists():
            print(f"error: {CSV_PATH} not found. Run without --check to regenerate.", file=sys.stderr)
            return 1
        actual = CSV_PATH.read_text()
        if actual != expected:
            print(f"error: {CSV_PATH} is out of sync with {JSON_PATH}. Run without --check to regenerate.", file=sys.stderr)
            return 1
        print("OK: fin-conventions.csv in sync")
        return 0

    CSV_PATH.write_text(expected)
    print(f"wrote {CSV_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
