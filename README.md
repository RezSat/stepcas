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
- symbolic differentiation for a useful subset,
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
from stepcas import parse_expr, simplify, differentiate

expr = parse_expr("x**3 + 2*x + 5")
result = differentiate(expr, "x", trace=True)
print(result.expr)
for step in result.steps:
    print(step.rule, step.before, "=>", step.after)
```

## Architecture

The long-term design is four layers:

1. **Core expression system**
2. **Rule and rewrite engine**
3. **Step trace and explanation layer**
4. **Frontends**: Python API, CLI, web API, UI

See `docs/architecture.md` and `program.md`.
