# ADR 0005: Error taxonomy contract

## Status
Accepted

## Context

The project spans parser, rewrites, differentiation, solving, and frontends. Raw exception text is not a stable contract for users or automation. We need a consistent error model across library and CLI boundaries.

## Decision

We will standardize on a shared typed error taxonomy:

- all domain errors inherit from a common `StepcasError` root,
- each error provides stable machine-readable `code` and `domain`,
- CLI JSON failures emit `{ "error": { "code", "message" } }`,
- new domains must add explicit codes instead of reusing generic messages.

## Consequences

### Positive

- reliable error handling for scripts and UI clients,
- clearer debugging and test assertions,
- safer extension across new algorithm domains.

### Negative

- more up-front taxonomy design when adding features,
- compatibility burden if existing codes need to change.
