import json

import pytest

import oee


def _result():
    return oee.oee(planned_production_time=480, downtime=80, ideal_cycle_time=0.5,
                   total_count=700, reject_count=100)


def test_lost_units_by_category():
    v = oee.loss_value(_result())
    # ideal cycle 0.5: 80 min down -> 160 units; quality loss -> reject 100 units
    assert v.lost_units["availability"] == pytest.approx(160)
    assert v.lost_units["performance"] == pytest.approx(100)
    assert v.lost_units["quality"] == pytest.approx(100)
    assert v.lost_units["total"] == pytest.approx(360)


def test_lost_value_money():
    v = oee.loss_value(_result(), value_per_unit=10)
    assert v.lost_value["total"] == pytest.approx(3600)
    assert v.lost_value["availability"] == pytest.approx(1600)


def test_needs_a_counts_result():
    with pytest.raises(ValueError):
        oee.loss_value(oee.oee_from_factors(0.9, 0.9, 0.9))


def test_to_dict_and_summary():
    v = oee.loss_value(_result(), value_per_unit=10)
    json.dumps(v.to_dict())
    assert "units" in v.summary()
