"""Loss valuation: turn the OEE losses into lost units and money.

Each loss measured in time is also a number of units that could have been made
at the ideal rate, and, given a value per unit, an amount of money. This puts a
figure on availability, performance and quality losses so the biggest one in
money, not just in time, stands out.
"""

from __future__ import annotations

from dataclasses import dataclass

from ._result import OEEResult, data_hash, utcnow
from ._version import __version__


@dataclass(frozen=True)
class ValuationResult:
    """Lost units (and money) by loss category."""

    name: str | None
    lost_units: dict
    lost_value: dict | None
    value_per_unit: float | None
    meta: dict

    def summary(self) -> str:
        lines = [
            f"loss value{' ' + self.name if self.name else ''} "
            f"- {self.meta.get('computed_at', '')}",
            f"  availability   {round(self.lost_units['availability'], 1)} units",
            f"  performance    {round(self.lost_units['performance'], 1)} units",
            f"  quality        {round(self.lost_units['quality'], 1)} units",
            f"  total lost     {round(self.lost_units['total'], 1)} units",
        ]
        if self.lost_value is not None:
            lines.append(f"  total value    {round(self.lost_value['total'], 2)}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "schema": 1,
            "name": self.name,
            "lost_units": self.lost_units,
            "lost_value": self.lost_value,
            "value_per_unit": self.value_per_unit,
            "meta": self.meta,
        }


def loss_value(result: OEEResult, *, value_per_unit=None,
               name: str | None = None) -> ValuationResult:
    """Lost units, and optionally money, by loss category from an OEEResult.

    The result must come from ``oee()`` or ``from_log()`` (it needs the times and
    counts). Units lost = loss time / ideal cycle time, so each loss is expressed
    as the good units that could have been produced at the ideal rate.
    """
    if result.net_run_time is None or not result.total_count:
        raise ValueError(
            "loss_value needs a result from oee() or from_log() with counts")
    if result.net_run_time <= 0:
        raise ValueError("cannot value losses when there is no net run time")
    assert (result.availability_loss is not None
            and result.performance_loss is not None
            and result.quality_loss is not None)  # set with net_run_time

    ideal_cycle = result.net_run_time / result.total_count
    avail = result.availability_loss / ideal_cycle
    perf = result.performance_loss / ideal_cycle
    qual = result.quality_loss / ideal_cycle
    lost_units = {
        "availability": avail,
        "performance": perf,
        "quality": qual,
        "total": avail + perf + qual,
    }

    lost_value = None
    if value_per_unit is not None:
        v = float(value_per_unit)
        if v < 0:
            raise ValueError("value_per_unit must be non-negative")
        lost_value = {k: u * v for k, u in lost_units.items()}

    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "input_hash": data_hash({"hash": result.meta.get("input_hash"),
                                 "value_per_unit": value_per_unit}),
    }
    return ValuationResult(name=name, lost_units=lost_units, lost_value=lost_value,
                           value_per_unit=value_per_unit, meta=meta)
