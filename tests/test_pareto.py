import pytest

import oee


def test_sorted_largest_first():
    p = oee.pareto({"jam": 12, "changeover": 30, "no_operator": 5})
    assert [e.label for e in p] == ["changeover", "jam", "no_operator"]
    assert [e.value for e in p] == [30, 12, 5]


def test_shares_and_cumulative():
    p = oee.pareto({"a": 60, "b": 30, "c": 10})
    assert p[0].share == pytest.approx(0.6)
    assert p[1].cumulative == pytest.approx(0.9)
    assert p[-1].cumulative == pytest.approx(1.0)
    assert sum(e.share for e in p) == pytest.approx(1.0)


def test_ties_broken_by_label():
    p = oee.pareto({"b": 10, "a": 10})
    assert [e.label for e in p] == ["a", "b"]


def test_runs_on_six_losses():
    r = oee.oee(planned_production_time=480, downtime=80, ideal_cycle_time=0.5,
                total_count=700, reject_count=100, setup_time=30, startup_rejects=40)
    p = oee.pareto(r.six_losses)
    assert p[0].cumulative <= 1.0 + 1e-9
    assert p[-1].cumulative == pytest.approx(1.0)
    # every loss accounted for
    assert {e.label for e in p} == set(r.six_losses)


def test_empty_returns_empty():
    assert oee.pareto({}) == []


def test_all_zero_gives_zero_shares():
    p = oee.pareto({"a": 0, "b": 0})
    assert all(e.share == 0.0 for e in p)


def test_negative_value_raises():
    with pytest.raises(ValueError):
        oee.pareto({"a": -1})
