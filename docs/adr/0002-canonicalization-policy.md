# ADR 0002: Canonicalization policy and current scope

## Status
Accepted

## Context

Expression ordering affects equality checks, simplify stability, and test repeatability. Without a canonical policy, equivalent expressions can render with different shapes and produce noisy step traces.

The current engine supports arithmetic simplification and additive like-term collection, but does not yet perform general expansion or factoring.

## Decision

We will enforce canonical ordering for commutative operations in current scope:

- apply deterministic ordering for `Add` and `Mul` nodes,
- run ordering rewrites as explicit visible steps,
- keep like-term collection additive-only for exact matches,
- do not perform expansion or factoring during canonicalization.

## Consequences

### Positive

- stable expression output for users and tests,
- predictable step traces across runs,
- clearer boundaries between canonicalization and future polynomial transforms.

### Negative

- equivalent forms that need expansion/factoring are not normalized yet,
- future broad canonicalization work must be introduced as new scoped rules.
