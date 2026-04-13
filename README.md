# stepcas

`stepcas` is a step-first symbolic algebra engine for Python.

It is not trying to be a tiny SymPy clone. The goal is different:

- compute exact symbolic results,
- preserve a human-readable chain of reasoning,
- expose intermediate transformations,
- stay small enough to audit,
- scale toward a serious computer algebra platform.

## Why this exists

Many symbolic systems are powerful but opaque. Many AI math systems are fluent but not always grounded in real computation. `stepcas` aims to sit in the middle:

- exact symbolic core,
- explicit rewrite engine,
- step trace as a first-class artifact,
- Python library + CLI now,
- web API later.

## Current status

This starter implements:

- immutable expression tree,
- parser for a Python-like math subset,
- simplification with step tracing,
- canonical ordering for addition and multiplication with explicit trace steps (`canonical-order-add` and `canonical-order-mul`),
- additive-only like-term collection with explicit trace steps (`collect-like-terms-add`) without expansion/factoring, plus mul-level repeated-base merging via `merge-repeated-bases-mul` (for example `x*x**2 -> x**3`),
- one-variable polynomial degree utility (`polynomial_degree`) for already-expanded forms,
- one-variable polynomial coefficient extraction (`polynomial_coefficients`) for already-expanded forms,
- one-variable dense polynomial coefficient vectors (`polynomial_coeff_vector`) for already-expanded forms,
- one-variable polynomial evaluation (`polynomial_evaluate`) for already-expanded forms,
- one-variable polynomial leading-term extraction (`polynomial_leading_term`) for already-expanded forms,
- one-variable polynomial leading-coefficient extraction (`polynomial_leading_coefficient`) for already-expanded forms,
- one-variable polynomial trailing-coefficient extraction (`polynomial_trailing_coefficient`) for already-expanded forms,
- one-variable polynomial trailing-term extraction (`polynomial_trailing_term`) for already-expanded forms,
- symbolic differentiation for a useful subset,
- linear-form extraction for expressions in `a*x + b` form,
- core linear equation solving API (`solve_linear_equation`) with step tracing,
- schema-versioned JSON serializers for `Expr`, `Step`, and `TraceResult` (`expr_to_json`, `step_to_json`, `trace_result_to_json`),
- CLI commands for `simplify`, `diff`, and `solve` with optional `--json` output and structured JSON errors (`error.code`, `error.message`),
- reproducible benchmark harness for simplify/differentiate/solve workloads with runtime and step-count output,
- test suite,
- repo scaffolding for agentic development.

Polynomial utilities validate `variable` strictly: it must be a single symbol name (for example, `"x"`).
`polynomial_trailing_coefficient` returns the degree-zero coefficient and yields `0` when no constant term is present.
`polynomial_trailing_term` returns the lowest-degree non-zero term as `(degree, coefficient)` and returns `(0, 0)` for the zero polynomial.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

Simplify an expression:

```bash
stepcas simplify "x + 0 + 2 + 3" --steps
```

Differentiate an expression:

```bash
stepcas diff "x**3 + 2*x + 5" x --steps
```

Solve a linear equation (`lhs = rhs`):

```bash
stepcas solve "2*x + 3" "11" x
```

Get machine-readable JSON output from CLI commands:

```bash
stepcas simplify "x + 0 + 2 + 3" --steps --json
stepcas diff "x**3 + 2*x + 5" x --json
stepcas solve "2*x + 3" "11" x --steps --json
```

When `--json` is enabled and an operation fails, the CLI emits a structured
error payload containing `error.code` and `error.message`.

Use as a library:

```python
from stepcas import (
    LinearSolveKind,
    expr_to_json,
    differentiate,
    extract_linear_form,
    parse_expr,
    polynomial_coeff_vector,
    polynomial_coefficients,
    polynomial_degree,
    polynomial_evaluate,
    polynomial_leading_coefficient,
    polynomial_leading_term,
    polynomial_trailing_coefficient,
    polynomial_trailing_term,
    simplify,
    solve_linear_equation,
)

expr = parse_expr("x**3 + 2*x + 5")
result = differentiate(expr, "x", trace=True)
print(result.expr)
for step in result.steps:
    print(step.rule, step.before, "=>", step.after)

trace_payload = expr_to_json(expr)
print(trace_payload["schema_version"], trace_payload["object"])

linear = extract_linear_form(parse_expr("3*x - 7"), "x")
print(linear.coefficient, linear.constant)  # 3 -7

degree = polynomial_degree(parse_expr("3*x**4 + 2*x - 1"), "x")
print(degree)  # 4

coefficients = polynomial_coefficients(parse_expr("3*x**2 - 2*x + 5"), "x")
print(coefficients)  # {2: 3, 1: -2, 0: 5}

vector = polynomial_coeff_vector(parse_expr("3*x**4 - 2*x + 5"), "x")
print(vector)  # [3, 0, 0, -2, 5]

evaluated = polynomial_evaluate(parse_expr("3*x**2 - 2*x + 5"), "x", 2)
print(evaluated)  # 13

leading = polynomial_leading_term(parse_expr("3*x**4 - 2*x + 5"), "x")
print(leading)  # (4, 3)

leading_coefficient = polynomial_leading_coefficient(parse_expr("3*x**4 - 2*x + 5"), "x")
print(leading_coefficient)  # 3

trailing_coefficient = polynomial_trailing_coefficient(parse_expr("3*x**4 - 2*x + 5"), "x")
print(trailing_coefficient)  # 5

trailing = polynomial_trailing_term(parse_expr("3*x**4 - 2*x + 5"), "x")
print(trailing)  # (0, 5)

solved = solve_linear_equation(parse_expr("2*x + 3"), parse_expr("11"), "x")
if solved.kind == LinearSolveKind.SOLVED:
    print(solved.variable, solved.value)  # x 4
```

`schema_version` is included in every serializer payload and should be used as the client compatibility key.

Linear equation solving returns typed outcomes for solved, no-solution, and
infinite-solution cases (`SolvedLinearEquation`, `NoLinearSolution`,
`InfiniteLinearSolutions`) tagged by `LinearSolveKind`.

Error handling is exposed through a shared hierarchy rooted at `StepcasError`,
with domain-specific subclasses such as `ParseError`, `DifferentiationError`,
`RewriteError`, and `LinearFormError`. Each carries a stable machine-friendly
`code` and `domain` (for example: `linear.nonlinear_form`,
`linear.unsupported_structure`, and `linear.unsupported_symbol`).


## OpenCode workflow

This repository is set up to work well with OpenCode in two styles:

1. Interactive TUI when you want to inspect and steer manually.
2. Headless server plus one-shot `opencode run --attach ...` calls when you want clean, task-scoped sessions.

Recommended for this project:

- keep one long-lived `opencode serve` process running
- use separate `opencode run --attach ...` calls for planning, implementation, debugging, and review
- avoid a never-ending optimization loop, this project is product engineering, not a single-metric ratchet

PowerShell helpers are included under `scripts/`.

## Architecture

The long-term design is four layers:

1. **Core expression system**
2. **Rule and rewrite engine**
3. **Step trace and explanation layer**
4. **Frontends**: Python API, CLI, web API, UI

See `docs/architecture.md` and `program.md`.

## Benchmarks

Run the benchmark harness:

```bash
stepcas-benchmark
```

Record a baseline snapshot:

```bash
stepcas-benchmark --iterations 50 --warmups 10 --baseline-out benchmarks/baseline.json
```

See `docs/benchmarks.md` for usage and reproducibility guidance.

## Autonomous company mode

This repo also includes a lightweight local supervisor under `company/` and helper scripts under `scripts/`. Use that mode if you want StepCAS work to proceed task by task with minimal intervention, while still being easy to pause and resume.
