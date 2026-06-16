import json

import pytest

import oee


def test_rty_is_product_of_step_yields():
    r = oee.rolled_throughput_yield([0.99, 0.98, 0.97])
    assert r.rty == pytest.approx(0.99 * 0.98 * 0.97)
    assert r.n_steps == 3
    assert r.normalized_yield == pytest.approx(r.rty ** (1 / 3))


def test_rty_from_counts():
    r = oee.rolled_throughput_yield([{"good": 95, "total": 100},
                                     {"good": 90, "total": 95}])
    assert r.step_yields[0] == pytest.approx(0.95)
    assert r.rty == pytest.approx(0.95 * (90 / 95))


def test_rty_from_pairs():
    r = oee.rolled_throughput_yield([(95, 100), (90, 95)])
    assert r.step_yields[0] == pytest.approx(0.95)


def test_first_pass_yield():
    assert oee.first_pass_yield(95, 100) == pytest.approx(0.95)


def test_to_dict_and_summary():
    r = oee.rolled_throughput_yield([0.99, 0.98])
    json.dumps(r.to_dict())
    assert "RTY" in r.summary()


def test_empty_raises():
    with pytest.raises(ValueError):
        oee.rolled_throughput_yield([])


def test_yield_out_of_range_raises():
    with pytest.raises(ValueError):
        oee.rolled_throughput_yield([1.5])
