# ADR 0004: JSON trace schema contract

## Status
Accepted

## Context

CLI and API clients consume expression and trace outputs. As integrations grow (web API, UI, automation), ad hoc JSON shape changes would break downstream systems.

## Decision

We will publish a schema-versioned JSON contract for trace-related payloads:

- serializers include `schema_version` as the compatibility key,
- expression, step, and trace result objects have explicit top-level object tags,
- CLI `--json` output follows this shared contract,
- schema changes require explicit version management.

## Consequences

### Positive

- stable integration surface for tooling and frontends,
- clearer migration path when payloads evolve,
- easier validation and contract testing.

### Negative

- extra maintenance overhead when fields change,
- stricter review needed for output-shape edits.
