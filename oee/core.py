"""Overall Equipment Effectiveness from the standard definitions.

OEE = Availability x Performance x Quality, with

    Availability = run time / planned production time
    Performance  = (ideal cycle time x total count) / run time
    Quality      = good count / total count

All times must be in the same unit, and ``ideal_cycle_time`` in that unit per
piece (or pass ``ideal_rate`` in pieces per that unit). The full time waterfall
(planned -> run -> net run -> fully productive) and each loss are returned, plus
TEEP and utilization when ``all_time`` is given.
"""

from __future__ import annotations

import math

from ._result import Alert, OEEResult, data_hash, utcnow
from ._version import __version__


def _finite(value: float, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{label} must be a number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def _exactly_one(a, b, name_a: str, name_b: str):
    if (a is None) == (b is None):
        raise ValueError(f"provide exactly one of {name_a} or {name_b}")
    return a, b


def oee(planned_production_time, *, run_time=None, downtime=None,
        ideal_cycle_time=None, ideal_rate=None, total_count,
        good_count=None, reject_count=None, all_time=None,
        target_oee: float = 0.85, name: str | None = None) -> OEEResult:
    """Compute OEE and the time/loss waterfall from times and piece counts."""
    planned = _finite(planned_production_time, "planned_production_time")
    if planned <= 0:
        raise ValueError("planned_production_time must be positive")

    _exactly_one(run_time, downtime, "run_time", "downtime")
    run = _finite(run_time, "run_time") if run_time is not None \
        else planned - _finite(downtime, "downtime")
    if not 0 <= run <= planned:
        raise ValueError("run_time must be between 0 and planned_production_time")

    _exactly_one(ideal_cycle_time, ideal_rate, "ideal_cycle_time", "ideal_rate")
    if ideal_cycle_time is not None:
        cycle = _finite(ideal_cycle_time, "ideal_cycle_time")
    else:
        rate = _finite(ideal_rate, "ideal_rate")
        if rate <= 0:
            raise ValueError("ideal_rate must be positive")
        cycle = 1.0 / rate
    if cycle <= 0:
        raise ValueError("ideal_cycle_time must be positive")

    total = _finite(total_count, "total_count")
    if total <= 0:
        raise ValueError("total_count must be positive")
    _exactly_one(good_count, reject_count, "good_count", "reject_count")
    good = _finite(good_count, "good_count") if good_count is not None \
        else total - _finite(reject_count, "reject_count")
    if not 0 <= good <= total:
        raise ValueError("good_count must be between 0 and total_count")
    reject = total - good

    alerts: list[Alert] = []

    availability = run / planned if planned else 0.0

    ideal_time_total = cycle * total
    performance_raw = ideal_time_total / run if run > 0 else 0.0
    if performance_raw > 1.0 + 1e-9:
        performance = 1.0
        net_run = run
        alerts.append(Alert(
            "performance", "performance exceeds 100%; capped at 100% (check "
            "ideal_cycle_time / ideal_rate and counts)", "warning"))
    else:
        performance = performance_raw
        net_run = ideal_time_total

    quality = good / total
    fully_productive = quality * net_run
    oee_value = availability * performance * quality

    schedule_loss = None
    utilization = None
    teep = None
    if all_time is not None:
        at = _finite(all_time, "all_time")
        if at < planned:
            raise ValueError("all_time must be at least planned_production_time")
        schedule_loss = at - planned
        utilization = planned / at if at > 0 else 0.0
        teep = fully_productive / at if at > 0 else 0.0

    if not 0 < target_oee <= 1:
        raise ValueError("target_oee must be in (0, 1]")
    if oee_value < target_oee:
        alerts.append(Alert(
            "oee", f"OEE {oee_value * 100:.1f}% is below the target "
            f"{target_oee * 100:.0f}%", "info"))

    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "method": "time_and_counts",
        "input_hash": data_hash({
            "planned": planned, "run": run, "cycle": cycle,
            "total": total, "good": good, "all_time": all_time,
        }),
    }
    return OEEResult(
        name=name, availability=availability, performance=performance,
        quality=quality, oee=oee_value, performance_raw=performance_raw,
        utilization=utilization, teep=teep,
        planned_production_time=planned, run_time=run, net_run_time=net_run,
        fully_productive_time=fully_productive, all_time=all_time,
        schedule_loss=schedule_loss, availability_loss=planned - run,
        performance_loss=run - net_run, quality_loss=net_run - fully_productive,
        total_count=total, good_count=good, reject_count=reject,
        target_oee=target_oee, alerts=tuple(alerts), meta=meta,
    )


def oee_from_factors(availability, performance, quality, *,
                     target_oee: float = 0.85, name: str | None = None) -> OEEResult:
    """Compute OEE from the three factors directly (no times or counts)."""
    a = _finite(availability, "availability")
    p = _finite(performance, "performance")
    q = _finite(quality, "quality")
    alerts: list[Alert] = []
    for label, value in (("availability", a), ("performance", p), ("quality", q)):
        if not 0 <= value <= 1.0 + 1e-9:
            raise ValueError(f"{label} must be between 0 and 1")
    if not 0 < target_oee <= 1:
        raise ValueError("target_oee must be in (0, 1]")
    oee_value = a * p * q
    if oee_value < target_oee:
        alerts.append(Alert(
            "oee", f"OEE {oee_value * 100:.1f}% is below the target "
            f"{target_oee * 100:.0f}%", "info"))
    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "method": "factors",
        "input_hash": data_hash({"a": a, "p": p, "q": q}),
    }
    return OEEResult(
        name=name, availability=a, performance=p, quality=q, oee=oee_value,
        performance_raw=p, utilization=None, teep=None,
        planned_production_time=None, run_time=None, net_run_time=None,
        fully_productive_time=None, all_time=None, schedule_loss=None,
        availability_loss=None, performance_loss=None, quality_loss=None,
        total_count=None, good_count=None, reject_count=None,
        target_oee=target_oee, alerts=tuple(alerts), meta=meta,
    )
