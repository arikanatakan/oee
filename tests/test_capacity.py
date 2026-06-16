import json

import pytest

import oee


def test_takt_time():
    assert oee.takt_time(480, 240) == pytest.approx(2.0)


def test_capacity_feasible():
    c = oee.capacity(480, 240, cycle_time=1.5)
    assert c.takt_time == pytest.approx(2.0)
    assert c.required_rate == pytest.approx(0.5)
    assert c.max_output == pytest.approx(320)
    assert c.meets_demand is True
    assert c.utilization_needed == pytest.approx(0.75)


def test_capacity_infeasible():
    c = oee.capacity(480, 240, cycle_time=2.5)
    assert c.meets_demand is False
    assert c.utilization_needed == pytest.approx(1.25)


def test_capacity_without_cycle_time():
    c = oee.capacity(480, 240)
    assert c.max_output is None
    assert c.meets_demand is None


def test_to_dict_and_summary():
    c = oee.capacity(480, 240, cycle_time=1.5)
    json.dumps(c.to_dict())
    assert "takt" in c.summary()


@pytest.mark.parametrize("call", [
    lambda: oee.takt_time(480, 0),
    lambda: oee.capacity(0, 240),
    lambda: oee.capacity(480, 240, cycle_time=-1),
])
def test_errors(call):
    with pytest.raises(ValueError):
        call()
