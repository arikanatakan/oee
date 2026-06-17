"""Capacity metrics: takt time and the required rate.

Takt time is the pace a line must hold to meet demand (available time per unit).
Given a cycle time it also says whether the line can keep up and how much of the
takt each unit consumes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ._result import data_hash, utcnow
from ._version import __version__


@dataclass(frozen=True)
class CapacityResult:
    """Takt time, required rate and (with a cycle time) feasibility."""

    name: str | None
    takt_time: float
    required_rate: float
    max_output: float | None
    meets_demand: bool | None
    utilization_needed: float | None
    demand: float
    available_time: float
    meta: dict

    def summary(self) -> str:
        lines = [
            f"capacity{' ' + self.name if self.name else ''} "
            f"- {self.meta.get('computed_at', '')}",
            f"  takt time      {round(self.takt_time, 4)} per unit",
            f"  required rate  {round(self.required_rate, 4)} units per time",
        ]
        if self.max_output is not None and self.utilization_needed is not None:
            lines.append(f"  max output     {round(self.max_output, 1)} units")
            lines.append(f"  meets demand   {self.meets_demand}")
            lines.append(
                f"  takt used      {round(100 * self.utilization_needed, 1)}%")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "schema": 1,
            "name": self.name,
            "takt_time": self.takt_time,
            "required_rate": self.required_rate,
            "max_output": self.max_output,
            "meets_demand": self.meets_demand,
            "utilization_needed": self.utilization_needed,
            "demand": self.demand,
            "available_time": self.available_time,
            "meta": self.meta,
        }


def _positive(value, label):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{label} must be a positive finite number")
    return value


def takt_time(available_time, demand) -> float:
    """The pace needed to meet demand: available time per unit."""
    return _positive(available_time, "available_time") / _positive(demand, "demand")


def capacity(available_time, demand, *, cycle_time=None,
             name: str | None = None) -> CapacityResult:
    """Takt time, required rate, and whether a cycle time can meet demand."""
    available = _positive(available_time, "available_time")
    dem = _positive(demand, "demand")
    takt = available / dem
    required_rate = dem / available

    max_output = meets_demand = utilization_needed = None
    if cycle_time is not None:
        cycle = _positive(cycle_time, "cycle_time")
        max_output = available / cycle
        meets_demand = max_output >= dem
        utilization_needed = cycle / takt

    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "input_hash": data_hash({"available": available, "demand": dem,
                                 "cycle": cycle_time}),
    }
    return CapacityResult(name=name, takt_time=takt, required_rate=required_rate,
                          max_output=max_output, meets_demand=meets_demand,
                          utilization_needed=utilization_needed, demand=dem,
                          available_time=available, meta=meta)
