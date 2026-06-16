import json

import pytest

import oee


def test_mtbf_mttr_availability():
    r = oee.reliability(1000, failures=5, total_repair_time=50)
    assert r.mtbf == pytest.approx(200)
    assert r.mttr == pytest.approx(10)
    assert r.availability == pytest.approx(1000 / 1050)
    assert r.failures == 5


def test_repair_times_list():
    r = oee.reliability(1000, repair_times=[10, 10, 10, 10, 10])
    assert r.failures == 5
    assert r.mttr == pytest.approx(10)
    assert r.mtbf == pytest.approx(200)


def test_no_failures_full_availability():
    r = oee.reliability(1000, failures=0, total_repair_time=0)
    assert r.mtbf is None
    assert r.mttr is None
    assert r.availability == 1.0


def test_to_dict_and_summary():
    r = oee.reliability(1000, failures=5, total_repair_time=50)
    json.dumps(r.to_dict())
    assert "MTBF" in r.summary()


@pytest.mark.parametrize("kw", [
    {},                                                       # neither
    {"failures": 5, "total_repair_time": 50, "repair_times": [1]},  # both
])
def test_input_errors(kw):
    with pytest.raises(ValueError):
        oee.reliability(1000, **kw)


def test_negative_operating_time_raises():
    with pytest.raises(ValueError):
        oee.reliability(-1, failures=1, total_repair_time=1)
