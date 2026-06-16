"""Roll OEE up across machines, lines, shifts or periods.

OEE figures must not be averaged: a fast machine and a slow one do not combine
to the mean of their OEEs. The correct roll-up sums the underlying time and
count buckets and recomputes the factors from the totals, which this does.
"""

from __future__ import annotations

from ._result import Alert, OEEResult, data_hash, utcnow
from ._version import __version__

_REQUIRED = ("planned_production_time", "run_time", "net_run_time",
             "fully_productive_time", "total_count", "good_count")


def aggregate(parts, *, target_oee: float = 0.85,
              name: str | None = None) -> OEEResult:
    """Combine several OEEResults into one by summing their time/count buckets."""
    parts = list(parts)
    if not parts:
        raise ValueError("aggregate needs at least one result")
    for i, part in enumerate(parts):
        if not isinstance(part, OEEResult):
            raise TypeError("aggregate expects OEEResult instances")
        for field in _REQUIRED:
            if getattr(part, field) is None:
                raise ValueError(
                    f"part {i} has no {field}; aggregate needs results created "
                    "from times and counts (oee(), not oee_from_factors())")

    s_planned = sum(p.planned_production_time for p in parts)
    s_run = sum(p.run_time for p in parts)
    s_net = sum(p.net_run_time for p in parts)
    s_fp = sum(p.fully_productive_time for p in parts)
    s_total = sum(p.total_count for p in parts)
    s_good = sum(p.good_count for p in parts)

    availability = s_run / s_planned if s_planned else 0.0
    performance = s_net / s_run if s_run else 0.0
    quality = s_fp / s_net if s_net else 0.0
    oee_value = s_fp / s_planned if s_planned else 0.0

    if all(p.all_time is not None for p in parts):
        s_all = sum(p.all_time for p in parts)
        utilization = s_planned / s_all if s_all else 0.0
        teep = s_fp / s_all if s_all else 0.0
        schedule_loss = s_all - s_planned
    else:
        s_all = utilization = teep = schedule_loss = None

    loss_keys = ("breakdowns", "setup_and_adjustments",
                 "minor_stops_and_reduced_speed", "process_defects", "reduced_yield")
    if all(p.six_losses is not None for p in parts):
        six_losses = {k: sum(p.six_losses[k] for p in parts) for k in loss_keys}
    else:
        six_losses = None

    if all(p.downtime_reasons is not None for p in parts):
        downtime_reasons: dict | None = {}
        for part in parts:
            for reason, value in part.downtime_reasons.items():
                downtime_reasons[reason] = downtime_reasons.get(reason, 0.0) + value
    else:
        downtime_reasons = None

    alerts: list[Alert] = []
    if oee_value < target_oee:
        alerts.append(Alert(
            "oee", f"OEE {oee_value * 100:.1f}% is below the target "
            f"{target_oee * 100:.0f}%", "info"))

    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "method": "aggregate",
        "parts": len(parts),
        "input_hash": data_hash([p.meta.get("input_hash") for p in parts]),
    }
    return OEEResult(
        name=name, availability=availability, performance=performance,
        quality=quality, oee=oee_value, performance_raw=performance,
        utilization=utilization, teep=teep,
        planned_production_time=s_planned, run_time=s_run, net_run_time=s_net,
        fully_productive_time=s_fp, all_time=s_all, schedule_loss=schedule_loss,
        availability_loss=s_planned - s_run, performance_loss=s_run - s_net,
        quality_loss=s_net - s_fp, six_losses=six_losses,
        downtime_reasons=downtime_reasons,
        total_count=s_total, good_count=s_good,
        reject_count=s_total - s_good, target_oee=target_oee,
        alerts=tuple(alerts), meta=meta,
    )
