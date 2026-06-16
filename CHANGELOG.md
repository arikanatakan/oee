# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project uses
[semantic versioning](https://semver.org/).

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
