import json

import pytest

import oee


def test_reproduces_vorne_from_a_log():
    r = oee.from_log(
        420,
        runs=[{"count": 19271, "good": 18848, "ideal_rate": 60}],
        downtime_events=[{"reason": "breakdown", "duration": 47}],
        all_time=480,
    )
    assert r.oee == pytest.approx(0.7480, abs=0.001)
    assert r.meta["method"] == "event_log"
    assert r.downtime_reasons == {"breakdown": 47}


def test_planned_downtime_becomes_setup():
    r = oee.from_log(
        480,
        runs=[{"count": 700, "good": 600, "ideal_cycle_time": 0.5}],
        downtime_events=[
            {"reason": "changeover", "duration": 30, "planned": True},
            {"reason": "jam", "duration": 50},
        ],
    )
    assert r.six_losses["setup_and_adjustments"] == pytest.approx(30)
    assert r.six_losses["breakdowns"] == pytest.approx(50)
    assert r.downtime_reasons == {"changeover": 30, "jam": 50}


def test_pareto_on_downtime_reasons():
    r = oee.from_log(
        480,
        runs=[{"count": 700, "good": 600, "ideal_cycle_time": 0.5}],
        downtime_events=[{"reason": "changeover", "duration": 30},
                         {"reason": "jam", "duration": 50}],
    )
    assert oee.pareto(r.downtime_reasons)[0].label == "jam"


def test_multiple_runs_with_different_rates():
    r = oee.from_log(
        100,
        runs=[{"count": 100, "good": 100, "ideal_rate": 10},
              {"count": 200, "good": 190, "ideal_cycle_time": 0.05}],
        downtime_events=[{"reason": "x", "duration": 10}],
    )
    assert r.total_count == 300
    assert r.good_count == 290
    assert 0 < r.oee < 1


def test_single_run_as_mapping():
    r = oee.from_log(420, runs={"count": 19271, "good": 18848, "ideal_rate": 60},
                     downtime_events=[{"reason": "d", "duration": 47}])
    assert r.total_count == 19271


def test_no_downtime_events_means_full_availability():
    r = oee.from_log(480, runs=[{"count": 700, "good": 700, "ideal_cycle_time": 0.5}])
    assert r.availability == pytest.approx(1.0)
    assert r.downtime_reasons == {}


def test_to_dict_has_downtime_reasons():
    r = oee.from_log(480, runs=[{"count": 700, "good": 600, "ideal_cycle_time": 0.5}],
                     downtime_events=[{"reason": "jam", "duration": 50}])
    d = r.to_dict()
    json.dumps(d)
    assert d["downtime_reasons"] == {"jam": 50}


def test_aggregate_merges_downtime_reasons():
    a = oee.from_log(100, runs=[{"count": 50, "good": 50, "ideal_rate": 1}],
                     downtime_events=[{"reason": "jam", "duration": 10}])
    b = oee.from_log(100, runs=[{"count": 50, "good": 45, "ideal_rate": 1}],
                     downtime_events=[{"reason": "jam", "duration": 5},
                                      {"reason": "setup", "duration": 3}])
    agg = oee.aggregate([a, b])
    assert agg.downtime_reasons == {"jam": 15, "setup": 3}


@pytest.mark.parametrize("kwargs", [
    {"runs": []},
    {"runs": [{"count": 100, "ideal_rate": 60}]},                  # no good/reject
    {"runs": [{"count": 100, "good": 100}]},                       # no rate
    {"runs": [{"count": 100, "good": 100, "ideal_rate": 60}],
     "downtime_events": [{"reason": "x", "duration": -5}]},        # negative
])
def test_invalid_log_raises(kwargs):
    with pytest.raises(ValueError):
        oee.from_log(420, **kwargs)
