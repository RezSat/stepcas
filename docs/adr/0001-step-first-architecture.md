# ADR 0001: Step-first architecture

## Status
Accepted

## Context

The project aims to support exact symbolic computation while also exposing intermediate reasoning. Traditional CAS systems often compute correctly but make it difficult to inspect every transformation. Many tutoring products expose steps, but their internal engine is not always available as a reusable open source library.

## Decision

We will treat step traces as a first-class concern in the architecture. Core algorithms must be capable of emitting structured step records. User-facing explanation strings may be derived from these records later.

## Consequences

### Positive

- better auditability,
- easier educational frontends,
- stronger AI integration,
- cleaner testing of symbolic behavior.

### Negative

- more design overhead,
- algorithms must be careful not to lose intermediate state,
- some optimizations may need trace-preserving variants.
