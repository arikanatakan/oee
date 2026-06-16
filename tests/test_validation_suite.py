"""Check oee against published and hand-derived worked examples."""

import json
from pathlib import Path

import pytest

import oee

CASES = json.loads((Path(__file__).parent / "validation_cases.json").read_text())["cases"]


def _compute(case):
    if case["method"] == "time_and_counts":
        return oee.oee(**case["inputs"])
    if case["method"] == "factors":
        return oee.oee_from_factors(**case["inputs"])
    raise ValueError(case["method"])


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_case(case):
    result = _compute(case)
    tol = case["tol"]
    for field, expected in case["expected"].items():
        actual = getattr(result, field)
        assert actual == pytest.approx(expected, abs=tol), f"{case['id']}.{field}"
