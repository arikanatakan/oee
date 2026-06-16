"""Optional charts for OEE results.

These need matplotlib, which is kept out of the core: install with the extra,
``pip install oee[plot]``. Each function draws onto a matplotlib Axes and
returns it, so the figure can be saved or composed further.
"""

from __future__ import annotations

from .pareto import pareto

INK = "#1f2d3d"
MUT = "#5b6b7b"
LEVEL_F, LEVEL_E = "#eef3f8", "#3b6ea5"
LOSS_F, LOSS_E = "#f4e3e1", "#c2695f"
PROD_F, PROD_E = "#e3f1ec", "#3a8f78"
CUM_E = "#2c5f8a"


def _require_matplotlib():
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:  # pragma: no cover - import guard
        raise ModuleNotFoundError(
            "oee charts need matplotlib; install it with: pip install 'oee[plot]'"
        ) from exc
    return plt


def _clean(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MUT)
    ax.spines["bottom"].set_color(MUT)
    ax.tick_params(colors=MUT, labelsize=8)
    ax.title.set_color(INK)


def waterfall(result, *, ax=None):
    """The OEE time waterfall: planned time cascading down through the
    availability, performance and quality losses to fully productive time."""
    plt = _require_matplotlib()
    if result.planned_production_time is None:
        raise ValueError(
            "waterfall needs a result from oee() or from_log(), not from factors")

    p = result.planned_production_time
    run = result.run_time
    net = result.net_run_time
    fp = result.fully_productive_time
    bars = [
        ("Planned", 0.0, p, LEVEL_F, LEVEL_E),
        ("Avail.\nloss", run, p - run, LOSS_F, LOSS_E),
        ("Run", 0.0, run, LEVEL_F, LEVEL_E),
        ("Perf.\nloss", net, run - net, LOSS_F, LOSS_E),
        ("Net run", 0.0, net, LEVEL_F, LEVEL_E),
        ("Quality\nloss", fp, net - fp, LOSS_F, LOSS_E),
        ("Fully\nproductive", 0.0, fp, PROD_F, PROD_E),
    ]
    if ax is None:
        _, ax = plt.subplots(figsize=(8.5, 4.6))
    for i, (_, bottom, height, fc, ec) in enumerate(bars):
        ax.bar(i, height, bottom=bottom, width=0.72, facecolor=fc, edgecolor=ec,
               linewidth=1.2, zorder=3)
    ax.set_xticks(range(len(bars)))
    ax.set_xticklabels([b[0] for b in bars])
    ax.set_ylabel("time", color=MUT)
    ax.set_title(f"OEE waterfall  -  OEE {result.oee * 100:.1f}%", fontweight="bold")
    ax.grid(axis="y", color="#eef1f4", zorder=0)
    _clean(ax)
    return ax


def losses_pareto(losses, *, ax=None, threshold=0.8):
    """A Pareto of the losses: bars largest first with a cumulative-share line.

    ``losses`` may be an OEEResult (its six big losses are used) or any
    label -> value mapping, such as a result's ``downtime_reasons``.
    """
    plt = _require_matplotlib()
    mapping = losses.six_losses if hasattr(losses, "six_losses") else losses
    if not mapping:
        raise ValueError("no losses to chart")
    entries = pareto(mapping)
    labels = [e.label.replace("_", " ") for e in entries]
    values = [e.value for e in entries]
    cumulative = [e.cumulative * 100 for e in entries]

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 4.8))
    x = range(len(entries))
    ax.bar(x, values, width=0.7, facecolor=LOSS_F, edgecolor=LOSS_E,
           linewidth=1.2, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("loss", color=MUT)
    ax.set_title("Loss Pareto", fontweight="bold")
    _clean(ax)

    ax2 = ax.twinx()
    ax2.plot(x, cumulative, color=CUM_E, marker="o", markersize=4, linewidth=1.5,
             zorder=4)
    ax2.axhline(threshold * 100, color=MUT, linestyle="--", linewidth=1)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("cumulative %", color=MUT)
    ax2.spines["top"].set_visible(False)
    ax2.tick_params(colors=MUT, labelsize=8)
    return ax


def trend(results, *, labels=None, factors=False, ax=None):
    """OEE over a sequence of results (shifts, days, machines).

    With ``factors=True`` the availability, performance and quality lines are
    drawn alongside OEE.
    """
    plt = _require_matplotlib()
    results = list(results)
    if not results:
        raise ValueError("trend needs at least one result")
    if labels is None:
        labels = [r.name if r.name else str(i + 1) for i, r in enumerate(results)]
    x = range(len(results))

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 4.6))
    ax.plot(x, [r.oee * 100 for r in results], color=PROD_E, marker="o",
            markersize=4, linewidth=2, label="OEE", zorder=4)
    if factors:
        for label, color, attr in (("Availability", LEVEL_E, "availability"),
                                    ("Performance", "#7c8a99", "performance"),
                                    ("Quality", LOSS_E, "quality")):
            ax.plot(x, [getattr(r, attr) * 100 for r in results], color=color,
                    marker=".", markersize=4, linewidth=1.1, label=label, zorder=3)
        ax.legend(frameon=False, fontsize=8)
    ax.axhline(85, color=MUT, linestyle="--", linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("%", color=MUT)
    ax.set_ylim(0, 105)
    ax.set_title("OEE trend", fontweight="bold")
    ax.grid(axis="y", color="#eef1f4", zorder=0)
    _clean(ax)
    return ax
