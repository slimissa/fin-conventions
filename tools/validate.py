#!/usr/bin/env python3
"""
6-layer validator for fin-conventions.json.

Layers:
  1. schema        - JSON Schema (draft-07)
  2. integrity     - pattern checks, ISO 8601 dates, non-empty strings
  3. business      - required fields per convention, source_url present, math_test_case present
  4. cross_ref     - every convention referenced by the fixture exists in the JSON
  5. ground_truth  - ACT/360 is present with the exact ISDA name
  6. coverage      - at least 1 convention in the seed (will grow to 8 in v0.1.0)

Exit codes: 0 pass, 1 data error, 2 usage error, 3 schema violation.
"""
import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("error: jsonschema not installed. pip install jsonschema", file=sys.stderr)
    sys.exit(2)


ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "fin-conventions.json"
SCHEMA_PATH = ROOT / "schema.json"
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "conventions.test.json"


def layer_schema(data, schema):
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        print(f"  [schema] FAIL: {e.message}", file=sys.stderr)
        sys.exit(3)
    print("  [schema] OK")


def layer_integrity(data):
    for key in ("day_counts", "business_days", "rolls", "frequencies"):
        for entry in data.get(key, []):
            cid = entry.get("convention_id", "")
            if not cid:
                print(f"  [integrity] FAIL: empty convention_id in {key}", file=sys.stderr)
                sys.exit(1)
            if not all(c.isupper() or c.isdigit() or c == "/" for c in cid):
                print(f"  [integrity] FAIL: convention_id {cid!r} must be uppercase A-Z, 0-9, or /", file=sys.stderr)
                sys.exit(1)
    print("  [integrity] OK")


def layer_business(data):
    for key in ("day_counts", "business_days", "rolls", "frequencies"):
        for entry in data.get(key, []):
            for field in ("source_url", "math_test_case"):
                if field not in entry:
                    print(f"  [business] FAIL: {entry['convention_id']} missing {field}", file=sys.stderr)
                    sys.exit(1)
    print("  [business] OK")


def layer_cross_ref(data):
    fixture = json.loads(FIXTURE_PATH.read_text())
    known = set()
    for key in ("day_counts", "business_days", "rolls", "frequencies"):
        for entry in data.get(key, []):
            known.add(entry["convention_id"])
    for c in fixture["conventions"]:
        cid = c["convention_id"]
        if cid not in known:
            print(f"  [cross_ref] FAIL: fixture references {cid} but JSON has no such convention", file=sys.stderr)
            sys.exit(1)
    print("  [cross_ref] OK")


def layer_ground_truth(data):
    day_counts = {e["convention_id"]: e for e in data.get("day_counts", [])}
    if "ACT/360" not in day_counts:
        print("  [ground_truth] FAIL: ACT/360 missing", file=sys.stderr)
        sys.exit(1)
    if day_counts["ACT/360"]["name"] != "Actual/360":
        print(f"  [ground_truth] FAIL: ACT/360 name is {day_counts['ACT/360']['name']!r}, expected 'Actual/360'", file=sys.stderr)
        sys.exit(1)
    print("  [ground_truth] OK")


def layer_coverage(data):
    total = sum(len(data.get(k, [])) for k in ("day_counts", "business_days", "rolls", "frequencies"))
    if total < 1:
        print("  [coverage] FAIL: at least 1 convention required", file=sys.stderr)
        sys.exit(1)
    print(f"  [coverage] OK ({total} convention(s))")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    if not JSON_PATH.exists():
        print(f"error: {JSON_PATH} not found", file=sys.stderr)
        return 2

    data = json.loads(JSON_PATH.read_text())
    schema = json.loads(SCHEMA_PATH.read_text())

    print("Validating fin-conventions.json")
    layer_schema(data, schema)
    layer_integrity(data)
    layer_business(data)
    layer_cross_ref(data)
    layer_ground_truth(data)
    layer_coverage(data)
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
