import json

import pytest

import oee


def _vorne(**over):
    kw = dict(planned_production_time=420, downtime=47, ideal_rate=60,
              total_count=19271, reject_count=423)
    kw.update(over)
    return oee.oee(**kw)


def test_basic_factors_and_oee():
    r = _vorne()
    assert r.oee == pytest.approx(0.7480, abs=0.001)
    assert r.availability == pytest.approx(0.8881, abs=0.001)
    assert not r.world_class
    assert not r.meets_target


def test_run_time_and_downtime_agree():
    a = oee.oee(planned_production_time=420, downtime=47, ideal_rate=60,
                total_count=19271, reject_count=423)
    b = oee.oee(planned_production_time=420, run_time=373, ideal_rate=60,
                total_count=19271, reject_count=423)
    assert a.oee == pytest.approx(b.oee)


def test_ideal_rate_and_cycle_agree():
    a = oee.oee(planned_production_time=420, downtime=47, ideal_rate=60,
                total_count=19271, reject_count=423)
    b = oee.oee(planned_production_time=420, downtime=47, ideal_cycle_time=1 / 60,
                total_count=19271, reject_count=423)
    assert a.performance == pytest.approx(b.performance)


def test_waterfall_adds_up():
    r = _vorne(all_time=480)
    assert r.schedule_loss + r.planned_production_time == pytest.approx(r.all_time)
    assert r.availability_loss + r.run_time == pytest.approx(r.planned_production_time)
    assert r.performance_loss + r.net_run_time == pytest.approx(r.run_time)
    assert r.quality_loss + r.fully_productive_time == pytest.approx(r.net_run_time)
    assert r.oee == pytest.approx(r.fully_productive_time / r.planned_production_time)


def test_teep_is_oee_times_utilization():
    r = _vorne(all_time=480)
    assert r.teep == pytest.approx(r.oee * r.utilization, abs=1e-9)


def test_performance_over_100_is_capped_and_flagged():
    r = oee.oee(planned_production_time=100, run_time=100, ideal_cycle_time=2,
                total_count=100, good_count=100)
    assert r.performance == 1.0
    assert r.performance_raw == pytest.approx(2.0)
    assert any(a.indicator == "performance" for a in r.alerts)


def test_world_class_flag():
    r = oee.oee_from_factors(0.90, 0.95, 0.999)
    assert r.world_class
    assert r.oee == pytest.approx(0.8541, abs=0.001)


def test_to_dict_json_serializable():
    d = _vorne(all_time=480).to_dict()
    json.dumps(d)
    assert d["schema"] == 1
    assert "input_hash" in d["meta"]
    assert d["factors"]["oee"] == pytest.approx(0.7480, abs=0.001)


def test_summary_plain_text():
    t = _vorne().summary()
    assert "OEE" in t and "Verdict" in t
    assert "—" not in t  # no em dash


def test_provenance_changes_with_input():
    a = _vorne().meta["input_hash"]
    b = _vorne(reject_count=500).meta["input_hash"]
    assert a != b


@pytest.mark.parametrize("over", [
    {"planned_production_time": 0},
    {"downtime": 500},                 # run time negative
    {"total_count": 0},
    {"good_count": 99999},             # good > total
])
def test_invalid_inputs_raise(over):
    with pytest.raises(ValueError):
        _vorne(**over)


def test_both_run_and_downtime_raises():
    with pytest.raises(ValueError):
        oee.oee(planned_production_time=420, run_time=373, downtime=47,
                ideal_rate=60, total_count=100, good_count=100)


def test_factors_out_of_range_raises():
    with pytest.raises(ValueError):
        oee.oee_from_factors(1.2, 0.9, 0.9)
