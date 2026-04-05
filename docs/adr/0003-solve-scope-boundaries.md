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

## Consequences

### Positive

- strong correctness boundary for the first solver release,
- clear user expectations for supported equations,
- easier extension path to richer solve domains.

### Negative

- many valid math problems remain intentionally unsupported,
- callers must branch on typed outcomes and error codes.
