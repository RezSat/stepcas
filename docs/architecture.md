# Architecture

## North star

`stepcas` should become a computation engine with explanation as a native feature, not a decorative add-on.

## Core ideas

### 1. Expressions are immutable values

The core tree must be stable, hashable, and easy to compare. This supports memoization, rule matching, caching, and persistent step traces.

### 2. Rewrites are explicit

Every non-trivial symbolic transformation should be modelled as a named rule:

- simplify-add-zero
- simplify-mul-one
- fold-constants-add
- collect-like-terms-add
- derivative-power

This creates a traceable symbolic pipeline.
Like-term collection is currently additive-only and relies on ordering rewrites to preserve canonical form.

### 3. Steps are data

A step is not just a string. It should be a structured object with:

- rule id,
- before expression,
- after expression,
- optional explanation,
- optional metadata.

### 4. Algorithms are orchestration over rules

Differentiation, simplification, solving, factoring, and integration should be orchestrators that call rules and emit steps.

### 5. Frontends are thin

CLI, Python API, web API, and UI must depend on the same core engine and step trace format.

## Growth path

### Phase 1

- arithmetic expressions,
- simplification,
- differentiation,
- basic solving,
- traceable JSON output.

### Phase 2

- rational forms,
- polynomials,
- better canonicalization,
- factor/expand,
- assumptions.

### Phase 3

- equation systems,
- matrices,
- calculus extensions,
- parser language,
- web API.

### Phase 4

- educational explanation layer,
- notebook widgets,
- web solver UI,
- LLM bridge adapters.
