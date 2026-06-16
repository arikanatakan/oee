import pytest

mpl = pytest.importorskip("matplotlib")
mpl.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.axes import Axes  # noqa: E402

import oee  # noqa: E402


@pytest.fixture(autouse=True)
def _close_figures():
    yield
    plt.close("all")


def _sample():
    return oee.oee(planned_production_time=480, downtime=80, ideal_cycle_time=0.5,
                   total_count=700, reject_count=100, setup_time=30,
                   startup_rejects=40)


def test_waterfall_returns_axes():
    assert isinstance(oee.waterfall(_sample()), Axes)


def test_waterfall_on_factors_result_raises():
    with pytest.raises(ValueError):
        oee.waterfall(oee.oee_from_factors(0.9, 0.9, 0.9))


def test_losses_pareto_on_result():
    assert isinstance(oee.losses_pareto(_sample()), Axes)


def test_losses_pareto_on_mapping():
    assert isinstance(oee.losses_pareto({"jam": 50, "changeover": 30}), Axes)


def test_losses_pareto_empty_raises():
    with pytest.raises(ValueError):
        oee.losses_pareto({})


def test_trend_returns_axes():
    a = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
                total_count=80, good_count=80, name="s1")
    b = oee.oee(planned_production_time=100, run_time=80, ideal_cycle_time=1,
                total_count=75, good_count=70, name="s2")
    assert isinstance(oee.trend([a, b], factors=True), Axes)


def test_trend_empty_raises():
    with pytest.raises(ValueError):
        oee.trend([])
