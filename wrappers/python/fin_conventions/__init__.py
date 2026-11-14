"""
fin-conventions: the 7th QuantOS registry.

Every convention is defined in fin-conventions.json at the repo root, with a
math_test_case and a source_url. This module is the runtime interface: it
loads the JSON and dispatches calculate() calls to the correct implementation.
"""
from pathlib import Path
import json
from typing import Optional

__version__ = "0.0.1"

_REGISTRY_PATH = Path(__file__).resolve().parents[3] / "fin-conventions.json"


class Convention:
    def __init__(self, data: dict):
        self.data = data

    @property
    def convention_id(self) -> str:
        return self.data["convention_id"]

    @property
    def name(self) -> str:
        return self.data["name"]

    @property
    def description(self) -> str:
        return self.data["description"]

    @property
    def formula(self) -> str:
        return self.data["formula"]

    @property
    def source_url(self) -> str:
        return self.data["source_url"]

    @classmethod
    def get(cls, convention_id: str) -> "Convention":
        registry = json.loads(_REGISTRY_PATH.read_text())
        for key in ("day_counts", "business_days", "rolls", "frequencies"):
            for entry in registry.get(key, []):
                if entry["convention_id"] == convention_id:
                    return cls(entry)
        raise KeyError(f"unknown convention: {convention_id}")


def calculate(convention_id: str, start: str, end: str, calendar: Optional[list] = None) -> float:
    """
    Calculate the convention for the given date range.

    Only the conventions listed in fin-conventions.json are supported.
    Raises NotImplementedError for a convention that exists in the JSON but
    has no Python implementation yet (which is the state a student will be in
    during Week 2).
    """
    if convention_id == "ACT/360":
        from datetime import date
        d1 = date.fromisoformat(start)
        d2 = date.fromisoformat(end)
        return (d2 - d1).days
    raise NotImplementedError(f"calculate() not implemented for {convention_id}")
