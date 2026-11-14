"""
The math-oracle test. Parameterized over the fixture.

When the seed ships, only ACT/360 is in the fixture, so this test collects
one case and passes. When a student adds ACT/365 to the fixture, this test
collects two cases; if the implementation is missing, the second case fails
with KeyError('ACT/365'). That failure is the first red CI.
"""
import pytest

from fin_conventions import calculate


@pytest.mark.parametrize(
    "convention",
    [
        pytest.param(c, id=c["convention_id"])
        for c in __import__("json").loads(
            (__import__("pathlib").Path(__file__).parent / "fixtures" / "conventions.test.json").read_text()
        )["conventions"]
    ],
)
def test_math(convention):
    tc = convention["math_test_case"]
    result = calculate(convention["convention_id"], tc["start"], tc["end"])
    assert result == tc["expected"], (
        f"{convention['convention_id']} from {tc['start']} to {tc['end']}: "
        f"expected {tc['expected']}, got {result}. "
        f"Source: {tc['source_url']}"
    )
