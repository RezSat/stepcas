# ADR 0003: Solve scope boundaries

## Status
Accepted

## Context

`stepcas` now includes equation solving, but full symbolic solving is broad and high risk for correctness and trace quality. We need a narrow contract that is reliable and easy to extend.

## Decision

The built-in solver scope is limited to single-variable linear equations represented in linear form:

- accepted target shape is reducible to `a*x + b = 0` (or equivalent after rearrangement),
- outcomes are typed as solved, no-solution, or infinite-solutions,
- non-linear or unsupported structures return structured domain errors,
- every successful solve path preserves explicit trace steps.

### Input simplification

The solver optionally simplifies both sides before extraction:

- `simplify_input=True` enables preprocessing simplification of the input expressions,
- when enabled, every simplification step appears before solve steps in the returned trace,
- this allows mathematically equivalent expressions (e.g., `2*x + (3 + 1)`) to be solved without manual preprocessing.

### Scope boundaries

The solver explicitly does NOT support:

- polynomial equations of degree > 1 (non-linear),
- equations with multiple target variables,
- trigonometric, exponential, or logarithmic expressions,
- piece-wise or conditional expressions,
- equations with non-numeric coefficients.

## Consequences

### Positive

- strong correctness boundary for the first solver release,
- clear user expectations for supported equations,
- easier extension path to richer solve domains.

### Negative

- many valid math problems remain intentionally unsupported,
- callers must branch on typed outcomes and error codes.
