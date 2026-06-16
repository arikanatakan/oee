"""Generate the oee framework figure (academic style).

Top: the OEE core (inputs, the engine, the OEEResult). Bottom: the metric
family around OEE.
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

fig, ax = plt.subplots(figsize=(12, 7.0))
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
ax.text(3, 93.5, "manufacturing effectiveness for Python", fontsize=9.5,
        color=MUT, ha="left", fontstyle="italic")

# ---- Top tier: the OEE core ------------------------------------------------
for x, t in [(12, "Inputs"), (40, "OEE engine"), (74, "Result")]:
    ax.text(x, 89, t, ha="center", fontsize=9.3, color=MUT, fontstyle="italic")

box(12, 80, 18, 8, "Times & counts", NEUT_F, NEUT_E, fs=8.0)
box(12, 68, 18, 8, "Event log", NEUT_F, NEUT_E, fs=8.0)

ax.add_patch(FancyBboxPatch((25, 57), 30, 35,
             boxstyle="round,pad=0.4,rounding_size=1.6",
             linewidth=1.3, edgecolor=CONT_E, facecolor=CONT_F, zorder=0))
for y, t in [(84, "Availability  =  run / planned"),
             (76, "Performance  =  ideal time / run"),
             (68, "Quality  =  good / total"),
             (60, "time waterfall  +  six big losses")]:
    box(40, y, 26, 6.6, t, ANA_F, ANA_E, fs=7.6)

box(74, 71.5, 22, 29,
    "OEEResult\n\nOEE · OOE · TEEP\nwaterfall · six losses\n\n"
    "meta\nversion · hash · timestamp",
    RES_F, RES_E, fs=8.3, bold=True)

for y in (80, 68):
    arrow(21.2, y, 24.6, 71.5)
arrow(55.2, 71.5, 62.8, 71.5)

# ---- Bottom tier: the metric family ----------------------------------------
ax.text(50, 47.5, "The metric family around OEE", ha="center", fontsize=11.5,
        fontweight="bold", color=INK)

family = [
    (11, "reliability\nMTBF · MTTR\navailability", "availability driver"),
    (30.5, "yield\nFPY · RTY", "quality driver"),
    (50, "capacity\ntakt · required rate", None),
    (69.5, "loss valuation\nunits · money", None),
    (89, "roll-up · Pareto\ncharts", None),
]
for x, t, annot in family:
    box(x, 33, 17.5, 11.5, t, OPT_F, OPT_E, fs=7.9)
    if annot:
        ax.text(x, 25, annot, ha="center", fontsize=7.1, color=MUT,
                fontstyle="italic")

box(50, 12, 88, 8,
    "computed from the standard definitions      ·      zero core dependencies\n"
    "validated against five published worked examples + the Nakajima benchmark",
    BAN_F, BAN_E, fs=7.9, tcol=MUT)

fig.savefig("assets/framework.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("wrote assets/framework.png")
