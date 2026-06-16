"""Yield metrics: first pass yield and rolled throughput yield.

These extend the single-step quality factor of OEE to a multi-step line. First
pass yield (FPY) is the fraction good first time at one step; rolled throughput
yield (RTY) is the product of the step yields - the chance a unit passes every
step without rework.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass

from ._result import data_hash, utcnow
from ._version import __version__


@dataclass(frozen=True)
class YieldResult:
    """Per-step first pass yields and the rolled throughput yield."""

    name: str | None
    rty: float
    step_yields: tuple[float, ...]
    normalized_yield: float
    n_steps: int
    meta: dict

    def summary(self) -> str:
        lines = [
            f"yield{' ' + self.name if self.name else ''} "
            f"- {self.meta.get('computed_at', '')}",
            f"  steps          {self.n_steps}",
            f"  RTY            {round(100 * self.rty, 1)}%",
            f"  normalized     {round(100 * self.normalized_yield, 1)}% per step",
        ]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "schema": 1,
            "name": self.name,
            "rty": self.rty,
            "step_yields": list(self.step_yields),
            "normalized_yield": self.normalized_yield,
            "n_steps": self.n_steps,
            "meta": self.meta,
        }


def first_pass_yield(good, total) -> float:
    """Fraction good first time at one step: good / total."""
    good = float(good)
    total = float(total)
    if total <= 0:
        raise ValueError("total must be positive")
    if not 0 <= good <= total:
        raise ValueError("good must be between 0 and total")
    return good / total


def _step_yield(step) -> float:
    if isinstance(step, Mapping):
        return first_pass_yield(step["good"], step["total"])
    if isinstance(step, (tuple, list)):
        return first_pass_yield(step[0], step[1])
    value = float(step)
    if not 0 <= value <= 1:
        raise ValueError("a step yield must be between 0 and 1")
    return value


def rolled_throughput_yield(steps, *, name: str | None = None) -> YieldResult:
    """Rolled throughput yield across steps (the product of the step yields).

    Each step is a yield between 0 and 1, a ``(good, total)`` pair, or a mapping
    with ``good`` and ``total``.
    """
    steps = list(steps)
    if not steps:
        raise ValueError("rolled_throughput_yield needs at least one step")
    step_yields = tuple(_step_yield(s) for s in steps)
    rty = math.prod(step_yields)
    n = len(step_yields)
    normalized = rty ** (1 / n) if n else 0.0
    meta = {
        "computed_at": utcnow(),
        "version": __version__,
        "input_hash": data_hash({"yields": list(step_yields)}),
    }
    return YieldResult(name=name, rty=rty, step_yields=step_yields,
                       normalized_yield=normalized, n_steps=n, meta=meta)
