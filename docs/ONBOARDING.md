# Onboarding

## The five questions every new contributor asks

1. **What is this project?** A versioned, schema-validated registry of financial conventions (day count, business day, roll, frequency), each with a test case and a `source_url` to the ISDA/ICMA spec it implements.
2. **What is the tech stack?** Python 3.10+, JSON Schema (draft-07), pytest, GitHub Actions. No network, no AI, no databases. Everything is deterministic.
3. **How do I run it?** `pytest tests/`, `python3 tools/validate.py`, `python3 cli.py get ACT/360 --start 2026-01-01 --end 2026-01-31`.
4. **Where do I start?** The `good first issue` labeled issue. It is the `ACT/365` extension. It will break the CI, and you will fix it. That is the point.
5. **Who do I ask?** Open an issue with the `question` label. Do not DM. The answer helps the next person.

## Your Week 1 task

1. Clone the repo.
2. Run `pytest tests/`. It shows **1 passed**. That is the green seed.
3. Run `python3 tools/validate.py`. It shows **OK**.
4. Run `python3 cli.py get ACT/360 --start 2026-01-01 --end 2026-01-31`. It prints **30**.
5. Open the `good first issue` ticket titled **"Add ACT/365 & CONTRIBUTORS.md"**.
6. Follow the ticket steps. The first time you run `pytest` after editing the fixture, it will fail. **That failure is yours.** Fix it, push, and open a PR.
7. The Quality Manager will review. When the CI is green, your PR is merged.

## What you are learning

- How a versioned registry is structured (JSON, schema, exports, wrapper, CI).
- How a test case with a `source_url` makes a formula defensible.
- How CI catches a math error before the code reaches a user.
- How the QuantOS release discipline works (the six version sites, the ADR rule, the `release.sh` gate).
