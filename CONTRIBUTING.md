# Contributing to fin-conventions

## The four rules for scripts

1. **No heredocs for patch scripts.** Write `/tmp/script.py`, run it standalone, check its exit code. Heredocs hide quoting bugs.
2. **`set -euo pipefail` at the top of every shell script.** No exceptions.
3. **Adversarial tests on `/tmp` copies**, never on the working tree. If a script mutates the tree, the tree is the test.
4. **File-first.** Write a script to a file, run the file, read the output. Do not paste multi-line commands into a terminal.

## The source rule

Every convention in `fin-conventions.json` **must** have a `source_url` pointing to the ISDA or ICMA specification it implements. Wikipedia, blog posts, and aggregator libraries are not acceptable sources.

Every test case in `tests/fixtures/conventions.test.json` **must** also have a `source_url`. A test case without a `source_url` is a guess, not a convention.

## The math-oracle rule

The `tests/fixtures/conventions.test.json` file is the source of truth for the math. If a convention's Python implementation disagrees with the fixture, the Python is wrong, not the fixture. If the fixture is wrong, the Quality Manager fixes it in a separate PR, with the `source_url` updated.

## The PR checklist

- [ ] `python3 tools/validate.py` passes.
- [ ] `python3 tools/export_csv.py --check` passes.
- [ ] `python3 tools/export_sql.py --check` passes.
- [ ] `pytest tests/` passes.
- [ ] If I added a convention, its test case has a `source_url`.
- [ ] If I changed a schema, I added an ADR.

## The version sites

There are six sites that carry the version. `tools/check_version_consistency.py` verifies them:

1. `VERSION`
2. `CHANGELOG.md` top released heading
3. `README.md` badge (once added)
4. `wrappers/python/pyproject.toml`
5. `wrappers/python/fin_conventions/__init__.py` `__version__`
6. `fin-conventions.json` `meta.version`

## The ADR discipline

Any change to a convention's formula, or any new top-level field in the schema, requires an ADR in `docs/decisions/`. The ADR is written by the contributor, reviewed by the Quality Manager, and merged in the same PR.
