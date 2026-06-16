"""Pareto analysis of named losses.

Sort contributions (downtime reasons, the six big losses, reject reasons) from
largest to smallest, with each one's share and the running cumulative share, so
the vital few losses to target stand out from the trivial many.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class ParetoEntry:
    """One row of a Pareto: a label, its value, its share and the cumulative
    share up to and including it (entries are returned largest first)."""

    label: str
    value: float
    share: float
    cumulative: float


def pareto(items: Mapping[str, float]) -> list[ParetoEntry]:
    """Rank ``items`` (label -> non-negative amount) largest first, with shares.

    The cumulative share shows where the 80% line falls, i.e. the few reasons
    that drive most of the loss. Works on a downtime-reason mapping, on a
    result's ``six_losses``, or on any non-negative breakdown.
    """
    pairs = []
    for label, value in items.items():
        amount = float(value)
        if not math.isfinite(amount) or amount < 0:
            raise ValueError(f"value for {label!r} must be finite and non-negative")
        pairs.append((str(label), amount))

    pairs.sort(key=lambda kv: (-kv[1], kv[0]))
    total = math.fsum(amount for _, amount in pairs)

    entries: list[ParetoEntry] = []
    cumulative = 0.0
    for label, amount in pairs:
        share = amount / total if total > 0 else 0.0
        cumulative += share
        entries.append(ParetoEntry(label, amount, share, cumulative))
    return entries
