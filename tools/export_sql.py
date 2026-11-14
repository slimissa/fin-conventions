#!/usr/bin/env python3
"""
Export fin-conventions.json to fin-conventions.sqlite.sql.

The SQL file creates one table, `conventions`, with one row per convention.

--check mode: regenerate in memory, compare with the committed SQL, exit 1 if different.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "fin-conventions.json"
SQL_PATH = ROOT / "fin-conventions.sqlite.sql"

SECTION_TO_TYPE = {
    "day_counts": "day_count",
    "business_days": "business_day",
    "rolls": "roll",
    "frequencies": "frequency",
}


def esc(s):
    return s.replace("'", "''")


def render():
    data = json.loads(JSON_PATH.read_text())
    out = [
        "-- fin-conventions, generated from fin-conventions.json",
        f"-- version: {data['meta']['version']}",
        "",
        "BEGIN;",
        "",
        "DROP TABLE IF EXISTS conventions;",
        "CREATE TABLE conventions (",
        "    convention_id  TEXT PRIMARY KEY,",
        "    type           TEXT NOT NULL,",
        "    name           TEXT NOT NULL,",
        "    description    TEXT NOT NULL,",
        "    formula        TEXT NOT NULL,",
        "    source_url     TEXT NOT NULL",
        ");",
        "",
    ]
    for section, type_name in SECTION_TO_TYPE.items():
        for entry in data.get(section, []):
            out.append(
                "INSERT INTO conventions VALUES ("
                f"'{esc(entry['convention_id'])}', "
                f"'{type_name}', "
                f"'{esc(entry['name'])}', "
                f"'{esc(entry['description'])}', "
                f"'{esc(entry['formula'])}', "
                f"'{esc(entry['source_url'])}'"
                ");"
            )
    out.append("")
    out.append("COMMIT;")
    out.append("")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()

    expected = render()

    if args.check:
        if not SQL_PATH.exists():
            print(f"error: {SQL_PATH} not found. Run without --check to regenerate.", file=sys.stderr)
            return 1
        actual = SQL_PATH.read_text()
        if actual != expected:
            print(f"error: {SQL_PATH} is out of sync with {JSON_PATH}. Run without --check to regenerate.", file=sys.stderr)
            return 1
        print("OK: fin-conventions.sqlite.sql in sync")
        return 0

    SQL_PATH.write_text(expected)
    print(f"wrote {SQL_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
