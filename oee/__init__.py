"""oee - Overall Equipment Effectiveness for Python.

Compute OEE (Availability x Performance x Quality) from machine times and piece
counts, get the full time waterfall and the three loss categories, TEEP and
utilization, and roll figures up correctly across machines and shifts. Every
result carries provenance and a JSON-safe payload.

    import oee

    r = oee.oee(
        planned_production_time=420,   # minutes
        downtime=47,
        ideal_cycle_time=1 / 60,       # minutes per piece
        total_count=19271,
        reject_count=423,
    )
    r.oee            # 0.7479
    r.summary()      # the factor and loss breakdown

Computed from the standard definitions and validated against published worked
examples.
"""

from ._result import Alert, OEEResult
from ._version import __version__
from .aggregate import aggregate
from .capacity import CapacityResult, capacity, takt_time
from .core import from_log, oee, oee_from_factors
from .pareto import ParetoEntry, pareto
from .plot import losses_pareto, trend, waterfall
from .reliability import ReliabilityResult, reliability
from .valuation import ValuationResult, loss_value
from .yields import YieldResult, first_pass_yield, rolled_throughput_yield

__all__ = [
    # OEE and the effectiveness family (OEE, OOE, TEEP)
    "oee", "oee_from_factors", "from_log", "aggregate", "pareto",
    "waterfall", "losses_pareto", "trend",
    # reliability (the availability driver)
    "reliability",
    # yield (the quality driver)
    "first_pass_yield", "rolled_throughput_yield",
    # capacity and loss valuation
    "takt_time", "capacity", "loss_value",
    # result types
    "OEEResult", "Alert", "ParetoEntry", "ReliabilityResult", "YieldResult",
    "CapacityResult", "ValuationResult", "__version__",
]
