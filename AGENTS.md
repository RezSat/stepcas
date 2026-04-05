# stepcas agent rules

This repository builds `stepcas`, a step-first symbolic algebra engine for Python.

## Mission

Build an exact symbolic math system that is:
- importable as a Python library
- usable from the terminal
- explainable through explicit step traces
- ready to grow into a web API and UI
- small, testable, and scalable

## Read first

Before making changes, read these files in order:
1. `README.md`
2. `program.md`
3. `docs/architecture.md`
4. `docs/roadmap.md`
5. the relevant files under `src/stepcas/`
6. the relevant tests under `tests/`

## Core engineering rules

1. Plan before editing.
2. Prefer the smallest change that solves the problem cleanly.
3. Preserve explicit step tracing. Do not hide transformations in opaque helper code.
4. Keep the expression model immutable.
5. Add or update tests with every behavior change.
6. Run focused tests first, then the full test suite when the change is ready.
7. Do not add dependencies unless the human explicitly approves.
8. Do not rewrite unrelated code while solving a targeted task.
9. Keep docs in sync when public behavior or architecture changes.
10. Commit in small, human-looking commits.

## Session workflow

For each task:
1. Create or update a short plan.
2. Inspect the relevant code and tests.
3. Implement one coherent slice.
4. Run focused verification.
5. Run the full suite if the slice is complete.
6. Update docs if needed.
7. Commit with a narrow message.

## Branching

- Keep `main` stable.
- Use feature branches such as `feat/canonical-ordering`, `fix/parser-negative-power`, `docs/explanation-traces`.
- Merge only after tests pass.

## Testing commands

- focused tests: `pytest tests/test_parser.py -q`
- full tests: `pytest -q`

## Quality commands

- lint: `ruff check .`
- format only if explicitly requested by the human or already part of the workflow

## Step trace rules

When adding a rewrite, think about:
- rule name
- preconditions
- output expression
- whether the step should be visible to end users
- whether repeated application can loop

## What not to do

- no giant one-shot refactors
- no fake benchmarks
- no hidden behavior changes without tests
- no replacing symbolic logic with LLM guesses
- no nested `opencode` invocations from inside OpenCode itself

## Preferred agent responsibilities

- `lead-engineer`: orchestration, task decomposition, final decisions
- `math-architect`: algebraic design, canonical forms, rewrite design
- `test-engineer`: tests, regression checks, failure triage
- `benchmark-engineer`: performance checks and benchmark harnesses
- `debug-engineer`: bug isolation and reproduction
- `doc-writer`: README, ADRs, roadmap, developer docs
- `prompt-improver`: improve agent prompts, command templates, and workflow docs

## Commit style

Use small commits such as:
- `parser: reject malformed unary chains`
- `simplify: collapse single-term add nodes`
- `diff: simplify constant-factor products`
- `tests: cover cli diff steps output`
- `docs: clarify rewrite trace contract`
