# ADR 0001: Clone the ISO 10383 architecture

**Status:** Accepted
**Date:** 2026-01-01

## Context

The `fin-conventions` registry is the 7th in the QuantOS family. The first six registries share a common architecture: RAW data, CURATED JSON, flat exports (SQL, CSV), a language wrapper, a 6-layer validator, a CI pipeline, and a `release.sh` gate.

## Decision

`fin-conventions` will clone the ISO 10383 architecture. We will not invent a new project structure, a new validator pattern, or a new release process. The same six-layer validator, the same `export_csv.py` / `export_sql.py` pattern, the same `release.sh` gate, the same `check_mojibake.py`.

The one deviation: `fin-conventions` has no RAW layer (the conventions are authored directly in JSON, not fetched from an upstream CSV). The validator's cross-reference layer is also different (it references convention IDs, not ISINs or MICs).

## Consequences

- The students inherit a working pattern. They do not reinvent it.
- The `release.sh` gate is shorter (6 checks, not 18) but it is the same shape.
- The `check_version_consistency.py` has 6 sites, not 9.

## Alternatives considered

- **A new architecture tailored to math.** Rejected: the students would spend Week 1 reinventing the validator instead of writing the math.
- **A minimal repo with no CI.** Rejected: the CI is the lesson, not the decoration.
