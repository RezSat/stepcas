# ADR 0006: Web endpoint response contracts

## Status

Accepted

## Context

The CLI currently provides JSON output via `--json` flag, but there is no formal web API endpoint contracts. As we prepare for Phase 2 (web API), we need stable response shapes for success and failure payloads across `/simplify`, `/diff`, and `/solve` endpoints.

## Decision

We will define a unified web endpoint response contract with schema versioning and structured error codes.

### Schema versioning

The API uses `schema_version` at the top level of every response:

```
{ "schema_version": "stepcas.api.v1", ... }
```

The version format is `stepcas.api.v{N}` where N increments with breaking changes to the contract.

### Success response shapes

#### `/simplify` endpoint

Success (no trace):
```json
{
  "schema_version": "stepcas.api.v1",
  "object": "simplify_result",
  "data": {
    "expression": <expr_json>
  }
}
```

Success (with trace):
```json
{
  "schema_version": "stepcas.api.v1",
  "object": "simplify_trace_result",
  "data": {
    "result": <expr_json>,
    "steps": [<step_json>, ...]
  }
}
```

#### `/diff` endpoint

Success (no trace):
```json
{
  "schema_version": "stepcas.api.v1",
  "object": "diff_result",
  "data": {
    "expression": <expr_json>,
    "variable": "x"
  }
}
```

Success (with trace):
```json
{
  "schema_version": "stepcas.api.v1",
  "object": "diff_trace_result",
  "data": {
    "result": <expr_json>,
    "variable": "x",
    "steps": [<step_json>, ...]
  }
}
```

#### `/solve` endpoint

Success (solved):
```json
{
  "schema_version": "stepcas.api.v1",
  "object": "solve_result",
  "data": {
    "kind": "solved",
    "variable": "x",
    "value": <expr_json>
  }
}
```

Success (no solution):
```json
{
  "schema_version": "stepcas.api.v1",
  "object": "solve_result",
  "data": {
    "kind": "no_solution",
    "reason": "inconsistent_constants"
  }
}
```

Success (infinite solutions):
```json
{
  "schema_version": "stepcas.api.v1",
  "object": "solve_result",
  "data": {
    "kind": "infinite_solutions",
    "reason": "identity"
  }
}
```

Solve with trace wraps in `solve_trace_result` with added `steps` array.

### Failure response shapes

All errors use a consistent envelope:

```json
{
  "schema_version": "stepcas.api.v1",
  "error": {
    "code": "parse.syntax",
    "message": "Unexpected character at position 3",
    "domain": "parse",
    "details": {}
  }
}
```

The `code` field is the stable machine-readable identifier.
The `message` field is human-readable and may change.
The `domain` field categorizes the error source.
The `details` field contains structured debug information (optional).

### Error codes by domain

| Domain | Code | Trigger |
|--------|------|---------|
| parse | parse.syntax | Invalid token sequence |
| parse | parse.unsupported_syntax | Recognized but unsupported syntax |
| differentiate | differentiate.non_constant_exponent | Power with non-constant exponent |
| differentiate | differentiate.unsupported_symbol | Invalid variable name |
| differentiate | differentiate.unsupported_expression | Unsupported expression type |
| linear | linear.nonlinear_form | Equation not reducible to linear |
| linear | linear.unsupported_symbol | Invalid variable name |
| linear | linear.unsupported_structure | Non-equation input |
| internal | internal.error | Unexpected runtime error |

### Version migration path

- Client sends `schema_version` in request header: `X-Stepcas-Schema-Version: stepcas.api.v1`
- Server responds with the version it used to process the request
- If client version differs from server version, client should migrate
- Deprecation: older versions work for 2 release cycles after new version introduction

## Consequences

### Positive

- Clear contract for web API consumers
- Versioned API prevents breaking integrations
- Consistent error handling across endpoints
- Trace information available in success payloads for debugging

### Negative

- More verbose JSON than CLI ad-hoc output
- Requires discipline to maintain version discipline
- Initial overhead before web API implementation begins