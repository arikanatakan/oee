"""End-to-end example: one shift on a beverage bottling line.

Runs the whole toolkit on one realistic scenario: the OEE factors and the
full time waterfall, the six big losses and their Pareto, the same shift from
an event log, reliability (the availability driver), a correct roll-up across
machines, rolled throughput yield (the quality driver), capacity against
demand, and the money behind the losses.

The line is a filler (the bottleneck), a labeler and a case packer over an
eight-hour shift. The numbers are illustrative of a real bottling line, not a
specific plant's data; the filler reproduces the canonical Vorne worked
example (OEE 74.79%) so the headline figure is recognisable. Run with:

    python examples/bottling_line.py
"""

import oee

# Filler - the bottleneck, analysed in full. One 8-hour shift, minutes.
FILLER = dict(
    planned_production_time=420,   # 480 min shift - 60 of breaks/scheduled
    downtime=47,                   # unplanned: 20 changeover + 27 breakdowns
    ideal_rate=60,                 # bottles per minute at nameplate speed
    total_count=19271,
    reject_count=423,
    all_time=480,                  # calendar time the line is owned this shift
    planned_downtime=30,           # the breaks (for OOE over operating time)
    setup_time=20,                 # of the 47 down, 20 was changeover
    startup_rejects=100,           # of the 423 rejects, 100 were at startup
    name="filler",
)


def main() -> None:
    print("== 1. Filler OEE, the time waterfall and the effectiveness family ==")
    r = oee.oee(**FILLER)
    print(f"  availability {r.availability:.3f}  x  performance {r.performance:.3f}"
          f"  x  quality {r.quality:.3f}  =  OEE {r.oee:.3f}")
    print(f"  OEE {r.oee:.1%}  >=  OOE {r.ooe:.1%}  >=  TEEP {r.teep:.1%}")
    print(f"  waterfall (min): planned {r.planned_production_time:.0f}"
          f" -> run {r.run_time:.0f} -> net run {r.net_run_time:.1f}"
          f" -> fully productive {r.fully_productive_time:.1f}")
    print(f"  losses (min): availability {r.availability_loss:.0f},"
          f" performance {r.performance_loss:.1f}, quality {r.quality_loss:.1f}\n")

    print("== 2. The six big losses, ranked (Pareto, minutes) ==")
    for e in oee.pareto(r.six_losses):
        print(f"  {e.label:32} {e.value:6.1f}  {e.share:5.1%}  cum {e.cumulative:5.1%}")
    print()

    print("== 3. Same shift from an event log -> downtime reasons -> Pareto ==")
    rl = oee.from_log(
        planned_production_time=420,
        runs=[{"count": 19271, "good": 18848, "ideal_rate": 60}],
        downtime_events=[
            {"reason": "changeover",          "duration": 20, "planned": True},
            {"reason": "jam",                 "duration": 14},
            {"reason": "capper fault",        "duration": 9},
            {"reason": "no bottles upstream", "duration": 4},
        ],
    )
    print(f"  OEE from the log {rl.oee:.3f} (matches the direct calc {r.oee:.3f})")
    for e in oee.pareto(rl.downtime_reasons):
        print(f"  {e.label:32} {e.value:6.0f}  {e.share:5.1%}  cum {e.cumulative:5.1%}")
    print()

    print("== 4. Reliability of the filler (the availability driver) ==")
    rel = oee.reliability(operating_time=r.run_time, repair_times=[12, 9, 6])
    print(f"  3 breakdowns over {r.run_time:.0f} min up: MTBF {rel.mtbf:.1f} min,"
          f" MTTR {rel.mttr:.1f} min, inherent availability {rel.availability:.1%}\n")

    print("== 5. Roll up the line, correctly (not by averaging the OEEs) ==")
    machines = [
        r,  # filler: planned 420
        oee.oee(planned_production_time=240, downtime=12, ideal_rate=80,
                total_count=16000, reject_count=80, all_time=300,
                planned_downtime=20, name="labeler"),
        oee.oee(planned_production_time=480, downtime=95, ideal_rate=45,
                total_count=16200, reject_count=240, all_time=540,
                planned_downtime=30, name="case packer"),
    ]
    line = oee.aggregate(machines, name="line")
    naive = sum(m.oee for m in machines) / len(machines)
    for m in machines:
        print(f"  {m.name:14} planned {m.planned_production_time:4.0f} min   OEE {m.oee:.3f}")
    print(f"  line OEE {line.oee:.3f}  (time-weighted)   vs the misleading "
          f"simple average {naive:.3f}\n")

    print("== 6. Rolled throughput yield across the three stations (quality) ==")
    ry = oee.rolled_throughput_yield(
        [(18848, 19271), (15920, 16000), (15960, 16200)], name="line quality")
    fpy = ", ".join(f"{y:.3%}" for y in ry.step_yields)
    print(f"  station first-pass yields: {fpy}")
    print(f"  rolled throughput yield {ry.rty:.3%}  (lower than any one station)\n")

    print("== 7. Capacity against demand ==")
    demand = 18000  # good bottles required this shift
    cap = oee.capacity(available_time=420, demand=demand, cycle_time=1 / 60)
    print(f"  takt time {cap.takt_time * 60:.2f} s/bottle, required rate"
          f" {cap.required_rate:.1f}/min")
    print(f"  at nameplate speed the filler can make {cap.max_output:.0f}; demand"
          f" {demand} -> {cap.utilization_needed:.1%} of takt needed,"
          f" meets demand: {cap.meets_demand}\n")

    print("== 8. The money behind the filler's losses ==")
    val = oee.loss_value(r, value_per_unit=0.50)   # $0.50 contribution per bottle
    u, v = val.lost_units, val.lost_value
    print(f"  lost good bottles this shift: availability {u['availability']:.0f},"
          f" performance {u['performance']:.0f}, quality {u['quality']:.0f}"
          f"  -> total {u['total']:.0f}")
    print(f"  at $0.50/bottle that is ${v['total']:,.0f} of lost contribution"
          f" in one shift")


if __name__ == "__main__":
    main()
