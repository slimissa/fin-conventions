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

## Before your first PR: the fresh clone

Before you open your first PR, clone the repo in a new directory and run the seven checks:

    cd /tmp
    git clone https://github.com/slimissa/fin-conventions.git fresh-check
    cd fresh-check
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt
    pytest tests/ -q
    python3 tools/validate.py
    python3 tools/check_version_consistency.py
    python3 tools/check_mojibake.py
    python3 cli.py get ACT/360 --start 2026-01-01 --end 2026-01-31
    python3 tools/check_cli_coverage.py
    python3 tools/check_wrapper_coverage.py

All seven should pass. If they do, your clone is green and your PR starts from a known state.

**Why the fresh clone matters.** The CI checks what the CI is configured to check. The fresh clone checks what the CI is not configured to check. The seed's own `tools/check_wrapper_coverage.py` was caught by a fresh clone, not by the CI, because the CI's `check-wrappers` job did not call the helper until a fresh clone reported its absence. Your first PR should be checked by both: the CI on every push, and a fresh clone on Day 1.

The fresh clone is not a redundancy. It is a second opinion.
