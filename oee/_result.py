"""The result contract: one ``OEEResult`` per computation, carrying the three
factors, the time waterfall, the loss categories, provenance and a JSON-safe
payload, so a calculation can be reproduced and audited later.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

SCHEMA = 1
WORLD_CLASS_OEE = 0.85


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def data_hash(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()[:16]


@dataclass(frozen=True)
class Alert:
    """A data-quality or benchmark note attached to a result."""

    indicator: str
    message: str
    severity: str = "warning"  # info | warning | error

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.indicator}: {self.message}"


def _pct(value: float | None) -> float | None:
    return None if value is None else round(100.0 * value, 1)


@dataclass(frozen=True)
class OEEResult:
    """Overall Equipment Effectiveness and the time/loss breakdown behind it."""

    name: str | None
    availability: float
    performance: float
    quality: float
    oee: float
    performance_raw: float
    utilization: float | None
    teep: float | None
    planned_production_time: float | None
    run_time: float | None
    net_run_time: float | None
    fully_productive_time: float | None
    all_time: float | None
    schedule_loss: float | None
    availability_loss: float | None
    performance_loss: float | None
    quality_loss: float | None
    six_losses: dict | None
    downtime_reasons: dict | None
    total_count: float | None
    good_count: float | None
    reject_count: float | None
    target_oee: float
    alerts: tuple[Alert, ...]
    meta: dict

    @property
    def world_class(self) -> bool:
        """True when OEE meets the widely cited world-class level of 85%."""
        return self.oee >= WORLD_CLASS_OEE

    @property
    def meets_target(self) -> bool:
        return self.oee >= self.target_oee

    @property
    def ok(self) -> bool:
        """True when no error-severity (data-quality) alert was raised."""
        return not any(a.severity == "error" for a in self.alerts)

    def _verdict(self) -> str:
        if self.world_class:
            return "world-class"
        if self.meets_target:
            return "meets target"
        return "below target"

    def summary(self) -> str:
        head = "oee" + (f" {self.name}" if self.name else "")
        lines = [
            f"{head} - {self.meta.get('computed_at', '')}",
            f"  Availability   {_pct(self.availability):>5}%",
            f"  Performance    {_pct(self.performance):>5}%",
            f"  Quality        {_pct(self.quality):>5}%",
            f"  OEE            {_pct(self.oee):>5}%",
        ]
        if self.teep is not None:
            lines.append(f"  TEEP           {_pct(self.teep):>5}%")
        if self.six_losses and self.planned_production_time:
            name, value = max(self.six_losses.items(), key=lambda kv: kv[1])
            share = _pct(value / self.planned_production_time)
            lines.append(f"  Biggest loss   {name} ({share}% of planned time)")
        for alert in self.alerts:
            lines.append("  " + str(alert))
        lines.append(f"Verdict: OEE {_pct(self.oee)}% - {self._verdict()}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA,
            "name": self.name,
            "factors": {
                "availability": self.availability,
                "performance": self.performance,
                "quality": self.quality,
                "oee": self.oee,
                "performance_raw": self.performance_raw,
                "utilization": self.utilization,
                "teep": self.teep,
            },
            "times": {
                "all_time": self.all_time,
                "planned_production_time": self.planned_production_time,
                "run_time": self.run_time,
                "net_run_time": self.net_run_time,
                "fully_productive_time": self.fully_productive_time,
            },
            "losses": {
                "schedule_loss": self.schedule_loss,
                "availability_loss": self.availability_loss,
                "performance_loss": self.performance_loss,
                "quality_loss": self.quality_loss,
            },
            "six_losses": self.six_losses,
            "downtime_reasons": self.downtime_reasons,
            "counts": {
                "total_count": self.total_count,
                "good_count": self.good_count,
                "reject_count": self.reject_count,
            },
            "world_class": self.world_class,
            "meets_target": self.meets_target,
            "target_oee": self.target_oee,
            "alerts": [
                {"indicator": a.indicator, "message": a.message, "severity": a.severity}
                for a in self.alerts
            ],
            "meta": self.meta,
        }
