# Contributing

Thanks for your interest in oee.

## Development setup

```
git clone https://github.com/arikanatakan/oee
cd oee
python -m pip install -e ".[dev]"
```

## Before opening a pull request

```
ruff check .
pytest
```

Both must pass. New metrics should come with a validation case in
`tests/validation_cases.json`: the inputs and the expected factors, taken from a
published worked example (cite the source) or derived by hand and documented in
the case.

## Scope

oee is the calculation layer for Overall Equipment Effectiveness. It does not
collect data or connect to machines (that is the job of an MES or an IoT
dashboard); it computes OEE, the time waterfall and the losses from data you
already have. New metrics are welcome when they are computed from a standard
definition and validated.

## Conventions

- Keep the `OEEResult` contract append-only: add fields, do not rename or remove.
- Compute from the standard OEE definitions; flag suspect data (for example a
  performance above 100%) rather than hiding it.
