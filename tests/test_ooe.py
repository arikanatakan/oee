import pytest

import oee


def test_ooe_between_teep_and_oee():
    r = oee.oee(planned_production_time=420, downtime=47, ideal_rate=60,
                total_count=19271, reject_count=423, all_time=480,
                planned_downtime=33)
    assert r.teep <= r.ooe <= r.oee
    assert r.operating_time == 453
    assert r.ooe == pytest.approx(r.fully_productive_time / r.operating_time)
    assert r.ooe_availability == pytest.approx(r.run_time / r.operating_time)


def test_ooe_none_without_planned_downtime():
    r = oee.oee(planned_production_time=420, downtime=47, ideal_rate=60,
                total_count=19271, reject_count=423)
    assert r.ooe is None
    assert r.operating_time is None


def test_ooe_in_summary_and_dict():
    r = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                total_count=80, good_count=80, planned_downtime=20)
    assert "OOE" in r.summary()
    assert r.to_dict()["factors"]["ooe"] is not None
    assert r.to_dict()["times"]["operating_time"] == 120


def test_negative_planned_downtime_raises():
    with pytest.raises(ValueError):
        oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                total_count=80, good_count=80, planned_downtime=-5)


def test_aggregate_rolls_up_ooe():
    m1 = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                 total_count=80, good_count=80, planned_downtime=10)
    m2 = oee.oee(planned_production_time=300, run_time=150, ideal_cycle_time=1,
                 total_count=150, good_count=135, planned_downtime=20)
    agg = oee.aggregate([m1, m2])
    assert agg.operating_time == 430
    assert agg.ooe == pytest.approx(agg.fully_productive_time / agg.operating_time)
