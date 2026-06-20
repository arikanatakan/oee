"""Render the bottling-line example's charts as one side-by-side panel.

Composes the three chart views of the worked example in examples/bottling_line.py
- the OEE time waterfall, the six-big-losses Pareto, and the OEE trend across
the line's machines - into a single figure with balanced, tuned scales.
Run:  python assets/example_bottling.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import oee

# Same inputs as examples/bottling_line.py.
filler = oee.oee(
    planned_production_time=420, downtime=47, ideal_rate=60,
    total_count=19271, reject_count=423, all_time=480, planned_downtime=30,
    setup_time=20, startup_rejects=100, name="filler",
)
labeler = oee.oee(
    planned_production_time=240, downtime=12, ideal_rate=80,
    total_count=16000, reject_count=80, all_time=300, planned_downtime=20,
    name="labeler",
)
packer = oee.oee(
    planned_production_time=480, downtime=95, ideal_rate=45,
    total_count=16200, reject_count=240, all_time=540, planned_downtime=30,
    name="case packer",
)
line = oee.aggregate([filler, labeler, packer], name="line")

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16.5, 4.7))

oee.waterfall(filler, ax=ax1)
ax1.set_ylim(0, 440)                     # minutes; headroom above planned 420

oee.losses_pareto(filler, ax=ax2)
ax2.set_ylim(0, 60)                      # minutes of loss; matches the bars

oee.trend([filler, labeler, packer], factors=True, ax=ax3)
ax3.set_ylim(0, 105)                     # percent
ax3.set_title(f"OEE by machine  -  line {line.oee * 100:.1f}%", fontweight="bold")

fig.suptitle("Bottling line, one shift  -  examples/bottling_line.py",
             fontsize=12, fontweight="bold", color="#1f2d3d", x=0.012, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.subplots_adjust(wspace=0.34)
fig.savefig("assets/example_bottling.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("wrote assets/example_bottling.png  | line OEE", round(line.oee, 4))
