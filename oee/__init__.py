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
from .core import oee, oee_from_factors

__all__ = [
    "oee", "oee_from_factors", "aggregate",
    "OEEResult", "Alert", "__version__",
]
