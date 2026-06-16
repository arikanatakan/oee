# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project uses
[semantic versioning](https://semver.org/).

## [0.1.2] - 2026-06-16

### Added

- Optional charts (install with `pip install oee[plot]`): `waterfall()` (the OEE
  time waterfall), `losses_pareto()` (a Pareto of the six big losses or any
  reason breakdown) and `trend()` (OEE and the factors over a sequence of
  results). matplotlib is an optional extra, so the core stays dependency-free.

## [0.1.1] - 2026-06-16

### Added

- The six big losses. `oee()` now returns `six_losses`, splitting the
  availability, performance and quality losses into breakdowns, setup and
  adjustments, minor stops and reduced speed (reported combined), process
  defects and reduced yield. Optional `setup_time` and `startup_rejects`
  arguments drive the availability and quality splits, `aggregate()` sums the
  six losses across machines, and `summary()` names the biggest loss.
- `pareto()` - rank any named breakdown (downtime reasons, the six losses,
  reject reasons) largest first, with each one's share and the running
  cumulative share, so the vital few losses to target stand out.
- `from_log()` - compute OEE from an event log of production runs and downtime
  events (each with a reason and an optional planned flag). It aggregates the
  runs (which may use different rates), splits the availability loss using the
  planned events, and attaches `downtime_reasons` ready for `pareto()`.

## [0.1.0] - 2026-06-16

First release.

### Added

- `oee()` - Overall Equipment Effectiveness from machine times and piece counts:
  availability, performance and quality, the full time waterfall (planned, run,
  net run and fully productive time, with schedule, availability, performance and
  quality losses), and TEEP and utilization when total calendar time is given.
- `oee_from_factors()` - OEE from the three factors directly.
- `aggregate()` - correct roll-up across machines, lines and shifts by summing
  the time and count buckets rather than averaging OEE figures.
- `OEEResult` - factors, waterfall, losses, `world_class` and `meets_target`
  flags, data-quality alerts (for example capped performance), `summary()` and a
  JSON-safe `to_dict()` with provenance.
- Validation against the Vorne *Fast Guide to OEE* worked example and
  hand-derived cases.
