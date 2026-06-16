"""Generate the oee framework figure (academic style).

The flow: inputs (times and counts, or an event log), the OEE engine, the
OEEResult, and how it is consumed.
Run:  python assets/framework.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5})

INK = "#1f2d3d"
MUT = "#5b6b7b"
NEUT_F, NEUT_E = "#eef1f4", "#9aa7b3"
ANA_F, ANA_E = "#eef3f8", "#3b6ea5"
RES_F, RES_E = "#d4e4f4", "#2c5f8a"
OPT_F, OPT_E = "#e3f1ec", "#3a8f78"
CONT_F, CONT_E = "#f7f9fb", "#c9d2db"
BAN_F, BAN_E = "#f5f7f9", "#cdd6df"
ARROW = "#7c8a99"

fig, ax = plt.subplots(figsize=(12, 6.4))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, text, fill, edge, fs=8.2, bold=False, tcol=INK):
    ax.add_patch(FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.35,rounding_size=1.4",
        linewidth=1.25, edgecolor=edge, facecolor=fill, zorder=2))
    ax.text(x, y, text, ha="center", va="center", color=tcol, fontsize=fs,
            fontweight="bold" if bold else "normal", zorder=5)


def arrow(x0, y0, x1, y1, color=ARROW, lw=1.15):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=1,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=1, shrinkB=1))


ax.text(3, 97.5, "oee", fontsize=13.5, fontweight="bold", color=INK, ha="left")
ax.text(3, 93.3, "Overall Equipment Effectiveness for Python", fontsize=9.5,
        color=MUT, ha="left", fontstyle="italic")

for x, t in [(12, "Inputs"), (43, "OEE engine"), (73, "Result"),
             (92, "Consumption")]:
    ax.text(x, 88, t, ha="center", fontsize=9.5, color=MUT, fontstyle="italic")

# inputs
box(12, 72, 18, 9, "Times & counts\nplanned · run / down\nideal rate · total / good",
    NEUT_F, NEUT_E, fs=7.7)
box(12, 55, 18, 9, "Event log\nproduction runs +\ndowntime events", NEUT_F, NEUT_E,
    fs=7.7)
ax.text(12, 45.5, "same time unit  ·  one or more machines", ha="center",
        fontsize=7.2, color=MUT, fontstyle="italic")

# engine container
ax.add_patch(FancyBboxPatch((25, 38), 36, 46,
             boxstyle="round,pad=0.4,rounding_size=1.6",
             linewidth=1.3, edgecolor=CONT_E, facecolor=CONT_F, zorder=0))
rows = [
    (76, "Availability    =    run / planned"),
    (66, "Performance    =    ideal time / run"),
    (56, "Quality    =    good / total"),
    (46, "time waterfall    +    six big losses"),
]
for y, t in rows:
    box(43, y, 32, 7.2, t, ANA_F, ANA_E, fs=7.6)

# result
box(73, 61, 20, 42,
    "OEEResult\n\nA · P · Q · OEE\nTEEP · utilization\nwaterfall · six losses\n\n"
    "meta\nversion · input hash\ntimestamp",
    RES_F, RES_E, fs=8.3, bold=True)

# consumption
cons = [(76, "aggregate()\ncorrect roll-up"), (61, "pareto()\nvital-few losses"),
        (46, "charts\nwaterfall · pareto · trend")]
for y, t in cons:
    box(92, y, 15, 9, t, OPT_F, OPT_E, fs=7.5)

# arrows
for y in (72, 55):
    arrow(21.2, y, 24.6, 61)
arrow(61.2, 61, 62.8, 61)
for y in (76, 61, 46):
    arrow(83.2, 61, 84.4, y)

# banner
box(50, 13.5, 86, 9,
    "computed from the standard definitions      ·      zero core dependencies\n"
    "validated against published worked examples (Vorne · TeepTrak · Nakajima)",
    BAN_F, BAN_E, fs=7.9, tcol=MUT)

fig.savefig("assets/framework.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("wrote assets/framework.png")
