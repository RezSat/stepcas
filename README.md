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
- additive-only exact like-term collection with explicit trace steps (`collect-like-terms-add`) without expansion/factoring,
- symbolic differentiation for a useful subset,
- linear-form extraction for expressions in `a*x + b` form,
- terminal interface,
- test suite,
- repo scaffolding for agentic development.

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

Use as a library:

```python
from stepcas import differentiate, extract_linear_form, parse_expr, simplify

expr = parse_expr("x**3 + 2*x + 5")
result = differentiate(expr, "x", trace=True)
print(result.expr)
for step in result.steps:
    print(step.rule, step.before, "=>", step.after)

linear = extract_linear_form(parse_expr("3*x - 7"), "x")
print(linear.coefficient, linear.constant)  # 3 -7
```

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

## Autonomous company mode

This repo also includes a lightweight local supervisor under `company/` and helper scripts under `scripts/`. Use that mode if you want StepCAS work to proceed task by task with minimal intervention, while still being easy to pause and resume.
