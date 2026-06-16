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
from collections.abc import Mapping
from dataclasses import replace

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
        good_count=None, reject_count=None, all_time=None, planned_downtime=None,
        setup_time=None, startup_rejects=None,
        target_oee: float = 0.85, name: str | None = None) -> OEEResult:
    """Compute OEE and the time/loss waterfall from times and piece counts.

    Optional ``setup_time`` splits the availability loss into setup-and-
    adjustments and breakdowns; optional ``startup_rejects`` (a count) splits the
    quality loss into reduced yield and process defects. Together with the
    performance loss these give the six big losses (the two performance losses,
    minor stops and reduced speed, are reported combined; splitting them needs
    event-level data).
    """
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

    operating_time = ooe_availability = ooe_value = None
    if planned_downtime is not None:
        pd = _finite(planned_downtime, "planned_downtime")
        if pd < 0:
            raise ValueError("planned_downtime must be non-negative")
        operating_time = planned + pd
        ooe_availability = run / operating_time if operating_time > 0 else 0.0
        ooe_value = fully_productive / operating_time if operating_time > 0 else 0.0

    if not 0 < target_oee <= 1:
        raise ValueError("target_oee must be in (0, 1]")
    if oee_value < target_oee:
        alerts.append(Alert(
            "oee", f"OEE {oee_value * 100:.1f}% is below the target "
            f"{target_oee * 100:.0f}%", "info"))

    availability_loss = planned - run
    performance_loss = run - net_run
    quality_loss = net_run - fully_productive
    if setup_time is not None:
        setup = _finite(setup_time, "setup_time")
        if not -1e-9 <= setup <= availability_loss + 1e-9:
            raise ValueError("setup_time must be between 0 and the downtime")
        setup = min(max(setup, 0.0), availability_loss)
    else:
        setup = 0.0
    if startup_rejects is not None:
        su = _finite(startup_rejects, "startup_rejects")
        if not -1e-9 <= su <= reject + 1e-9:
            raise ValueError("startup_rejects must be between 0 and reject_count")
        reduced_yield = quality_loss * (su / reject) if reject > 0 else 0.0
    else:
        reduced_yield = 0.0
    six_losses = {
        "breakdowns": availability_loss - setup,
        "setup_and_adjustments": setup,
        "minor_stops_and_reduced_speed": performance_loss,
        "process_defects": quality_loss - reduced_yield,
        "reduced_yield": reduced_yield,
    }

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
        utilization=utilization, teep=teep, ooe=ooe_value,
        ooe_availability=ooe_availability, operating_time=operating_time,
        planned_production_time=planned, run_time=run, net_run_time=net_run,
        fully_productive_time=fully_productive, all_time=all_time,
        schedule_loss=schedule_loss, availability_loss=availability_loss,
        performance_loss=performance_loss, quality_loss=quality_loss,
        six_losses=six_losses, downtime_reasons=None,
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
        performance_raw=p, utilization=None, teep=None, ooe=None,
        ooe_availability=None, operating_time=None,
        planned_production_time=None, run_time=None, net_run_time=None,
        fully_productive_time=None, all_time=None, schedule_loss=None,
        availability_loss=None, performance_loss=None, quality_loss=None,
        six_losses=None, downtime_reasons=None,
        total_count=None, good_count=None, reject_count=None,
        target_oee=target_oee, alerts=tuple(alerts), meta=meta,
    )


def from_log(planned_production_time, *, runs, downtime_events=None,
             all_time=None, startup_rejects=None, target_oee: float = 0.85,
             name: str | None = None) -> OEEResult:
    """Compute OEE from an event log of production runs and downtime events.

    Each entry in ``runs`` is a mapping with ``count``, one of ``good`` or
    ``reject``, and one of ``ideal_cycle_time`` or ``ideal_rate`` (runs may use
    different rates). Each entry in ``downtime_events`` is a mapping with a
    ``duration``, a ``reason``, and an optional ``planned`` flag (planned stops
    become setup and adjustments, the rest breakdowns). The result carries
    ``downtime_reasons`` for a Pareto, plus the usual waterfall and six losses.
    """
    if isinstance(runs, Mapping):
        runs = [runs]
    runs = list(runs)
    if not runs:
        raise ValueError("from_log needs at least one production run")

    total = good = ideal_net_run = 0.0
    for i, run in enumerate(runs):
        count = _finite(run["count"], f"runs[{i}].count")
        if count < 0:
            raise ValueError(f"runs[{i}].count must be non-negative")
        if ("good" in run) == ("reject" in run):
            raise ValueError(f"runs[{i}] needs exactly one of good or reject")
        g = (_finite(run["good"], f"runs[{i}].good") if "good" in run
             else count - _finite(run["reject"], f"runs[{i}].reject"))
        if not 0 <= g <= count:
            raise ValueError(f"runs[{i}].good must be between 0 and count")
        if ("ideal_cycle_time" in run) == ("ideal_rate" in run):
            raise ValueError(
                f"runs[{i}] needs exactly one of ideal_cycle_time or ideal_rate")
        if "ideal_cycle_time" in run:
            cycle = _finite(run["ideal_cycle_time"], f"runs[{i}].ideal_cycle_time")
        else:
            rate = _finite(run["ideal_rate"], f"runs[{i}].ideal_rate")
            if rate <= 0:
                raise ValueError(f"runs[{i}].ideal_rate must be positive")
            cycle = 1.0 / rate
        if cycle <= 0:
            raise ValueError(f"runs[{i}].ideal_cycle_time must be positive")
        total += count
        good += g
        ideal_net_run += count * cycle
    if total <= 0:
        raise ValueError("the production runs have no pieces")
    effective_cycle = ideal_net_run / total

    downtime_reasons: dict[str, float] = {}
    total_downtime = 0.0
    setup = 0.0
    for j, event in enumerate(downtime_events or []):
        duration = _finite(event["duration"], f"downtime_events[{j}].duration")
        if duration < 0:
            raise ValueError(f"downtime_events[{j}].duration must be non-negative")
        reason = str(event.get("reason", "unspecified"))
        total_downtime += duration
        downtime_reasons[reason] = downtime_reasons.get(reason, 0.0) + duration
        if bool(event.get("planned", False)):
            setup += duration

    result = oee(
        planned_production_time, downtime=total_downtime,
        ideal_cycle_time=effective_cycle, total_count=total, good_count=good,
        all_time=all_time, setup_time=setup if downtime_events else None,
        startup_rejects=startup_rejects, target_oee=target_oee, name=name,
    )
    meta = {
        **result.meta,
        "method": "event_log",
        "input_hash": data_hash({
            "planned": float(planned_production_time), "total": total,
            "good": good, "net_run": ideal_net_run,
            "downtime_reasons": downtime_reasons,
        }),
    }
    return replace(result, downtime_reasons=downtime_reasons, meta=meta)

