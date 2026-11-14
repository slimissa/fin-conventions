# fin-conventions

**The 7th QuantOS registry. Standardizing the mathematical rules of finance.**

> This repository is a scaffold. The `TODO` sections below will be filled in by the ACM student branch over six weeks.

## What it is

A versioned, schema-validated registry of financial conventions: day count, business day, roll, and frequency. Each convention is a JSON entry with a mathematical definition, a test case, and a `source_url` pointing to the ISDA or ICMA specification it implements.

## The Data Model

TODO: describe the four top-level arrays (`day_counts`, `business_days`, `rolls`, `frequencies`) and the `meta` object.

## The Math

TODO: list the 8–10 conventions in the MVP, with their formulas.

## The Wrapper

TODO: document `Convention.get(id).calculate(start, end)`.

## The Exports

TODO: document `fin-conventions.csv` and `fin-conventions.sql`.

## The CI Pipeline

TODO: describe the six CI jobs and what each one proves.

## The 6-Week Roadmap

TODO: paste the roadmap.

## Consuming it from QuantOS

TODO: describe how DeBou, Exchange Calendar, and the apps will consume this registry.

## Contributing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md).

## License

Apache 2.0. See [`LICENSE`](./LICENSE).

