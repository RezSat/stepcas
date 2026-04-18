# ADR 0007: Stable step metadata keys

## Status

Accepted

## Context

The `Step` dataclass includes a `metadata: Dict[str, Any]` field. As integrations grow (web API, UI, explainability layer), we need stable metadata keys that are:
- explicitly documented for consumers,
- JSON-serializable without ad-hoc conversion,
- usable for filtering, sorting, and visibility control.

## Decision

We will define stable metadata keys that the system uses and exports:

### Reserved keys

| Key | Type | Description |
|-----|------|-------------|
| `phase` | str | Execution phase: "parse", "canonicalize", "simplify", "differentiate", "solve" |
| `visible` | bool | Whether the step should be shown to end users (default: true) |

### Recommended keys

| Key | Type | Description |
|-----|------|-------------|
| `index` | int | Step ordinal in the trace (1-indexed) |
| `tags` | list[str] | Categorization tags for the step |

### Custom keys

Consumers may add custom keys, but they must be JSON-serializable (str, bool, int, float, None, list, dict with str keys).

## Consequences

### Positive

- predictable step metadata surface for API and UI consumers,
- filtering and sorting by phase/visibility is reliable,
- clear contract for JSON trace exports.

### Negative

- reserved key semantics must be maintained across versions,
- custom keys with incompatible types will fail at serialization time.