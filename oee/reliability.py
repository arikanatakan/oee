"""Reliability metrics: MTBF, MTTR and inherent availability.

These explain the availability factor of OEE: how often the equipment fails
(MTBF) and how long it takes to recover (MTTR). Inherent availability is
MTBF / (MTBF + MTTR).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ._result import data_hash, utcnow
from ._version import __version__


@dataclass(frozen=True)
class ReliabilityResult:
    """Mean time between failures, mean time to repair and availability."""

    name: str | None
    mtbf: float | None
    mttr: float | None
    availability: float
    failures: int
    operating_time: float
    total_repair_time: float
    meta: dict

    def summary(self) -> str:
        lines = [
            f"reliability{' ' + self.name if self.name else ''} "
            f"- {self.meta.get('computed_at', '')}",
            f"  failures       {self.failures}",
            f"  MTBF           {'n/a' if self.mtbf is None else round(self.mtbf, 3)}",
            f"  MTTR           {'n/a' if self.mttr is None else round(self.mttr, 3)}",
            f"  Availability   {round(100 * self.availability, 1)}%",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "schema": 1,
            "name": self.name,
            "mtbf": self.mtbf,
            "mttr": self.mttr,
            "availability": self.availability,
            "failures": self.failures,
            "operating_time": self.operating_time,
            "total_repair_time": self.total_repair_time,
            "meta": self.meta,
        }


def _finite(value, label):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"{label} must be a number")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def reliability(operating_time, *, failures=None, repair_times=None,
                total_repair_time=None, name: str | None = None) -> ReliabilityResult:
    """MTBF, MTTR and inherent availability from operating time and failures.

    Give the repair durations as ``repair_times`` (a list), or give the number
    of ``failures`` and the ``total_repair_time``. ``operating_time`` is the
    uptime over the period.
    """
    op = _finite(operating_time, "operating_time")
    if op < 0:
        raise ValueError("operating_time must be non-negative")

    if repair_times is not None:
        if failures is not None or total_repair_time is not None:
            raise ValueError("give repair_times, or failures and total_repair_time")
        durations = [_finite(d, "repair_times[]") for d in repair_times]
        if any(d < 0 for d in durations):
            raise ValueError("repair durations must be non-negative")
        n = len(durations)
        total_repair = math.fsum(durations)
    else:
        if failures is None or total_repair_time is None:
            raise ValueError("give repair_times, or failures and total_repair_time")
        n = int(failures)
        if n < 0:
            raise ValueError("failures must be non-negative")
        total_repair = _finite(total_repair_time, "total_repair_time")
        if total_repair < 0:
            raise ValueError("total_repair_time must be non-negative")

    if n == 0:
        mtbf = mttr = None
        availability = 1.0
    else:
        mtbf = op / n
        mttr = total_repair / n
        denom = op + total_repair
        availability = op / denom if denom > 0 else 1.0

    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "input_hash": data_hash({"op": op, "n": n, "repair": total_repair}),
    }
    return ReliabilityResult(name=name, mtbf=mtbf, mttr=mttr,
                             availability=availability, failures=n,
                             operating_time=op, total_repair_time=total_repair,
                             meta=meta)
