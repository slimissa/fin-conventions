import json
from pathlib import Path

import pytest


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "conventions.test.json"


@pytest.fixture(scope="session")
def fixture_data():
    return json.loads(FIXTURE_PATH.read_text())


@pytest.fixture(scope="session")
def conventions(fixture_data):
    return fixture_data["conventions"]


@pytest.fixture(scope="session")
def convention_ids(conventions):
    return [c["convention_id"] for c in conventions]
