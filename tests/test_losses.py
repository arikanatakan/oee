import json

import pytest

import oee

# planned 480, run 400 (down 80), ideal cycle 0.5, 700 pieces, 100 rejected.
# net run = 350, fully productive = 300.
# availability loss 80, performance loss 50, quality loss 50.
BASE = dict(planned_production_time=480, downtime=80, ideal_cycle_time=0.5,
            total_count=700, reject_count=100)


def test_six_losses_present_and_keys():
    r = oee.oee(**BASE)
    assert set(r.six_losses) == {
        "breakdowns", "setup_and_adjustments", "minor_stops_and_reduced_speed",
        "process_defects", "reduced_yield",
    }


def test_six_losses_sum_to_total_loss():
    r = oee.oee(**BASE)
    total_loss = r.planned_production_time - r.fully_productive_time
    assert sum(r.six_losses.values()) == pytest.approx(total_loss)
    assert total_loss == pytest.approx(180)


def test_performance_bucket_equals_performance_loss():
    r = oee.oee(**BASE)
    assert r.six_losses["minor_stops_and_reduced_speed"] == pytest.approx(r.performance_loss)


def test_availability_split_defaults_to_breakdowns():
    r = oee.oee(**BASE)
    assert r.six_losses["setup_and_adjustments"] == 0.0
    assert r.six_losses["breakdowns"] == pytest.approx(r.availability_loss)


def test_setup_time_splits_availability():
    r = oee.oee(**BASE, setup_time=30)
    assert r.six_losses["setup_and_adjustments"] == pytest.approx(30)
    assert r.six_losses["breakdowns"] == pytest.approx(50)
    assert (r.six_losses["breakdowns"] + r.six_losses["setup_and_adjustments"]
            == pytest.approx(r.availability_loss))


def test_quality_split_defaults_to_process_defects():
    r = oee.oee(**BASE)
    assert r.six_losses["reduced_yield"] == 0.0
    assert r.six_losses["process_defects"] == pytest.approx(r.quality_loss)


def test_startup_rejects_split_quality():
    r = oee.oee(**BASE, startup_rejects=40)
    assert r.six_losses["reduced_yield"] == pytest.approx(20)
    assert r.six_losses["process_defects"] == pytest.approx(30)
    assert (r.six_losses["reduced_yield"] + r.six_losses["process_defects"]
            == pytest.approx(r.quality_loss))


def test_setup_time_over_downtime_raises():
    with pytest.raises(ValueError):
        oee.oee(**BASE, setup_time=120)


def test_startup_rejects_over_reject_raises():
    with pytest.raises(ValueError):
        oee.oee(**BASE, startup_rejects=200)


def test_factors_result_has_no_six_losses():
    r = oee.oee_from_factors(0.9, 0.9, 0.9)
    assert r.six_losses is None


def test_to_dict_includes_six_losses():
    d = oee.oee(**BASE, setup_time=30, startup_rejects=40).to_dict()
    json.dumps(d)
    assert d["six_losses"]["setup_and_adjustments"] == pytest.approx(30)


def test_summary_shows_biggest_loss():
    t = oee.oee(**BASE).summary()
    assert "Biggest loss" in t


def test_aggregate_sums_six_losses():
    a = oee.oee(**BASE, setup_time=30)
    b = oee.oee(**BASE, setup_time=10)
    agg = oee.aggregate([a, b])
    assert agg.six_losses["setup_and_adjustments"] == pytest.approx(40)
    assert agg.six_losses["breakdowns"] == pytest.approx(
        a.six_losses["breakdowns"] + b.six_losses["breakdowns"])
