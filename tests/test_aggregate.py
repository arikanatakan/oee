import pytest

import oee


def test_rollup_is_not_the_average_of_oees():
    m1 = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                 total_count=80, good_count=80)
    m2 = oee.oee(planned_production_time=300, run_time=150, ideal_cycle_time=1,
                 total_count=150, good_count=135)
    agg = oee.aggregate([m1, m2])
    naive = (m1.oee + m2.oee) / 2
    assert agg.oee == pytest.approx(0.5375, abs=1e-4)
    assert agg.oee != pytest.approx(naive, abs=1e-3)


def test_buckets_sum():
    m1 = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                 total_count=80, good_count=80)
    m2 = oee.oee(planned_production_time=300, run_time=150, ideal_cycle_time=1,
                 total_count=150, good_count=135)
    agg = oee.aggregate([m1, m2])
    assert agg.planned_production_time == 400
    assert agg.run_time == 240
    assert agg.total_count == 230
    assert agg.good_count == 215
    assert agg.oee == pytest.approx(agg.fully_productive_time / agg.planned_production_time)


def test_single_part_matches_itself():
    m = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                total_count=80, good_count=80)
    agg = oee.aggregate([m])
    assert agg.oee == pytest.approx(m.oee)
    assert agg.availability == pytest.approx(m.availability)


def test_teep_when_all_parts_have_all_time():
    m1 = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                 total_count=80, good_count=80, all_time=120)
    m2 = oee.oee(planned_production_time=300, run_time=150, ideal_cycle_time=1,
                 total_count=150, good_count=135, all_time=360)
    agg = oee.aggregate([m1, m2])
    assert agg.teep is not None
    assert agg.utilization == pytest.approx(400 / 480)


def test_teep_none_when_a_part_lacks_all_time():
    m1 = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                 total_count=80, good_count=80, all_time=120)
    m2 = oee.oee(planned_production_time=300, run_time=150, ideal_cycle_time=1,
                 total_count=150, good_count=135)
    agg = oee.aggregate([m1, m2])
    assert agg.teep is None


def test_factors_only_part_cannot_be_aggregated():
    f = oee.oee_from_factors(0.9, 0.9, 0.9)
    with pytest.raises(ValueError):
        oee.aggregate([f])


def test_empty_raises():
    with pytest.raises(ValueError):
        oee.aggregate([])


def test_non_result_raises():
    with pytest.raises(TypeError):
        oee.aggregate([{"oee": 0.5}])
