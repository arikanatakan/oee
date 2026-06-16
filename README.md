# oee

[![CI](https://github.com/arikanatakan/oee/actions/workflows/ci.yml/badge.svg)](https://github.com/arikanatakan/oee/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/oee)](https://pypi.org/project/oee/)
[![License: MIT](https://img.shields.io/github/license/arikanatakan/oee)](LICENSE)

Overall Equipment Effectiveness for Python.

Compute OEE (Availability x Performance x Quality) from machine times and piece
counts, get the full time waterfall and the three loss categories, TEEP and
utilization, and roll figures up correctly across machines and shifts. Computed
from the standard definitions and validated against published worked examples.

## Motivation

OEE is the standard manufacturing efficiency metric, but Python has no library
for it: what exists is monitoring *applications* (Flask/Django dashboards) or
one-off tutorial scripts. The arithmetic looks trivial (three numbers
multiplied) and that is exactly why it is usually done wrong:

* the time waterfall (planned -> run -> net run -> fully productive) and where
  each loss sits is skipped;
* TEEP and utilization (which capture schedule loss) are left out;
* and figures are *averaged* across machines, which is incorrect: a fast machine
  and a slow one do not combine to the mean of their OEEs.

`oee` does these properly, from the standard definitions, and returns one result
with the factors, the waterfall, every loss, and provenance.

```
pip install oee
```

No runtime dependencies.

## Usage

The canonical worked example (Vorne's *Fast Guide to OEE*):

```python
import oee

r = oee.oee(
    planned_production_time=420,   # minutes (480 shift - 60 of breaks)
    downtime=47,
    ideal_rate=60,                 # pieces per minute
    total_count=19271,
    reject_count=423,
    all_time=480,                  # optional, for TEEP and utilization
)
r.availability   # 0.888
r.performance    # 0.861
r.quality        # 0.978
r.oee            # 0.748
r.teep           # 0.654
print(r.summary())
```

Roll up across machines (correctly, not by averaging):

```python
m1 = oee.oee(planned_production_time=100, run_time=90, ideal_cycle_time=1,
             total_count=80, good_count=80)     # OEE 0.80
m2 = oee.oee(planned_production_time=300, run_time=150, ideal_cycle_time=1,
             total_count=150, good_count=135)   # OEE 0.45

line = oee.aggregate([m1, m2])
line.oee         # 0.5375, not the 0.625 average of the two
```

When you already have the three factors:

```python
oee.oee_from_factors(0.90, 0.95, 0.999).world_class   # True (OEE >= 85%)
```

Every result carries the factors, the time waterfall, the losses, `world_class`
and `meets_target` flags, `summary()`, and a JSON-safe `to_dict()` with
provenance (version, input hash, timestamp).

## What it computes

| Group | Output |
|-------|--------|
| Factors | availability, performance, quality, OEE |
| Extended | TEEP, utilization (when total calendar time is given) |
| Waterfall | planned -> run -> net run -> fully productive time, with schedule, availability, performance and quality losses |
| Roll-up | correct aggregation across machines, lines and shifts |

All times must be in the same unit; `ideal_cycle_time` is that unit per piece
(or pass `ideal_rate` in pieces per that unit). Performance above 100% is capped
and flagged, since it means the ideal rate or counts are off.

## Status

Version 0.1.0. Single-machine OEE, the time waterfall, TEEP/utilization, and
correct roll-up. The `OEEResult` contract is append-only from here.

## Roadmap

| Version | Scope |
|---------|-------|
| 0.2 | the six big losses (breakdown/setup, minor stops/speed, defects/startup) and a downtime-reason Pareto; computing OEE from an event log |
| 0.3 | plotting (the OEE waterfall, six-big-losses and trend charts) as an optional extra |
| 0.4 | an MCP server so an agent can compute and explain OEE |

Out of scope: data collection / machine connectivity (that is the job of an
MES or an IoT dashboard); `oee` is the calculation layer they can build on.

## License

MIT. Written and maintained by [Atakan Arikan](https://github.com/arikanatakan),
MSc Student at Tsinghua University and Politecnico di Milano.
