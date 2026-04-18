# Web API Design

This document describes the planned HTTP API surface for stepcas when deployed as a web service. The design reuses the existing trace and error contracts defined in the Python API.

## Guiding principles

1. Stateless computation. Each request contains all inputs needed for evaluation.
2. Structured responses. Both success and error payloads follow schemas versioned separately from the service.
3. Trace-first. Every nontrivial operation returns step information usable for educational or debugging purposes.
4. Thin transport. The HTTP layer translates between JSON and the internal expression model.

## Base URL and versioning

```
GET /api/v1/<endpoint>
```

The `v1` segment denotes the API version. The service exposes a `GET /api/v1/version` endpoint returning the current API version and the engine version.

All request and response payloads include a `schema_version` field. The current schema version is `1.0`.

## Endpoints

### Evaluate expression

```
POST /api/v1/eval
```

Computes a numeric result from an expression.

**Request**

```json
{
  "schema_version": "1.0",
  "expression": "x^2 + 3*x + 2",
  "variables": {
    "x": 5
  }
}
```

**Response (success)**

```json
{
  "schema_version": "1.0",
  "result": 42,
  "trace": [
    {
      "rule": "evaluate",
      "before": "x^2 + 3*x + 2",
      "after": "42"
    }
  ]
}
```

**Response (error)**

```json
{
  "schema_version": "1.0",
  "error": {
    "code": "E003",
    "message": "unsupported structure: derivative",
    "details": {}
  }
}
```

### Simplify expression

```
POST /api/v1/simplify
```

Simplifies an expression using the canonical simplification rules.

**Request**

```json
{
  "schema_version": "1.0",
  "expression": "2*x + 0"
}
```

**Response (success)**

```json
{
  "schema_version": "1.0",
  "result": "2*x",
  "trace": [
    {
      "rule": "simplify-add-zero",
      "before": "2*x + 0",
      "after": "2*x"
    }
  ]
}
```

### Differentiate expression

```
POST /api/v1/diff
```

Computes the derivative of an expression with respect to a variable.

**Request**

```json
{
  "schema_version": "1.0",
  "expression": "x^2",
  "variable": "x"
}
```

**Response (success)**

```json
{
  "schema_version": "1.0",
  "result": "2*x",
  "trace": [
    {
      "rule": "derivative-power",
      "before": "x^2",
      "after": "2*x"
    }
  ]
}
```

### Solve linear equation

```
POST /api/v1/solve/linear
```

Solves a linear equation for a specified variable.

**Request**

```json
{
  "schema_version": "1.0",
  "lhs": "3*x + 5",
  "rhs": "14",
  "variable": "x"
}
```

**Response (success)**

```json
{
  "schema_version": "1.0",
  "result": "x = 3",
  "trace": [
    {
      "rule": "solve-linear",
      "before": "3*x + 5 = 14",
      "after": "x = 3"
    }
  ]
}
```

### Transform with custom rules

```
POST /api/v1/transform
```

Applies a named transformation algorithm to an expression.

**Request**

```json
{
  "schema_version": "1.0",
  "expression": "(x + 1)^2",
  "algorithm": "expand"
}
```

**Response (success)**

```json
{
  "schema_version": "1.0",
  "result": "x^2 + 2*x + 1",
  "trace": [
    {
      "rule": "expand-binomial",
      "before": "(x + 1)^2",
      "after": "x^2 + 2*x + 1"
    }
  ]
}
```

## Request-response contracts

### Common request fields

| Field            | Type    | Required | Description                                   |
|-----------------|--------|----------|-----------------------------------------------|
| schema_version  | string | yes      | Version string matching the current schema.  |
| expression      | string | yes      | Input expression in text form.                 |
| variables       | object | no       | Variable substitutions for evaluation.        |
| variable        | string | no       | Target variable for differentiation or solve.|
| algorithm       | string | no       | Named algorithm to apply.                     |
| options         | object | no       | Algorithm-specific options.                  |

### Common response fields

| Field            | Type    | Description                                   |
|-----------------|--------|-----------------------------------------------|
| schema_version  | string | Version matching the request.                  |
| result          | string | Output expression in text form.                |
| trace           | array  | Array of step objects.                         |
| error           | object | Error envelope (present on failure).            |

### Trace object structure

Each step in the trace array follows the existing JSON trace schema:

```json
{
  "rule": "rule-id",
  "before": "expression-string",
  "after": "expression-string",
  "metadata": {}
}
```

This structure reuses the `step` model defined in the core engine, ensuring consistent trace format across CLI, Python API, and web API.

## Error envelopes

All errors return a JSON envelope with this structure:

```json
{
  "schema_version": "1.0",
  "error": {
    "code": "E000",
    "message": "short human-readable message",
    "details": {}
  }
}
```

### Error codes

| Code   | Name                    | Description                                        |
|--------|------------------------|---------------------------------------------------|
| E000   | unknown                | Unclassified internal error.                        |
| E001   | parse_error            | Expression failed to parse.                       |
| E002   | invalid_input          | Request missing required fields.                    |
| E003   | unsupported_structure | Expression contains unsupported forms.          |
| E004   | no_solution           | Solver failed to find a solution.                |
| E005   | timeout               | Computation exceeded time limit.                 |

The error codes correspond to the error taxonomy defined in ADR 0005. The `details` field carries contextual information such as the position of a parse error or the variable that caused an unsupported-structure error.

## Trace payload reuse strategy

### From engine to API

The web API reuses the same trace objects produced by the Python API. No translation layer transforms the trace. This ensures that:

1. Every step visible in the CLI appears identically in the API.
2. Educational tools can consume traces from either interface.
3. Debugging information is consistent across all frontends.

### Nested trace composition

When algorithms compose multiple rules, each rule contributes one step to the trace array. The order of steps reflects the order of application:

```
[step_from_preprocess, step_from_solve, step_from_simplify]
```

This flat array structure is preserved in the API response.

### Trace pruning for size

Large expressions can produce very long traces. The service accepts an `options.max_steps` field in the request to truncate the trace:

```json
{
  "schema_version": "1.0",
  "expression": "...",
  "options": {
    "max_steps": 100
  }
}
```

When the trace exceeds the limit, the response includes an `overflow` flag:

```json
{
  "schema_version": "1.0",
  "result": "...",
  "trace": [...],
  "overflow": true
}
```

### Step metadata

Step metadata carries additional information such as visibility and phase flags. These are optionally included in the trace and are defined in ADR for step metadata contract.

## Deployment considerations

### Stateless design

Each endpoint is stateless. The service can be scaled horizontally without session affinity. All state is carried in the request payload.

### Rate limiting

Endpoints accept an optional `request_id` field for idempotency. Rate limiting is applied at the proxy layer, not described here.

### Timeouts

The service enforces a default timeout of 30 seconds per request. Long-running computations return `E005` error.

### Future extensions

Additional endpoints will follow the same patterns:
- `POST /api/v1/integrate` for symbolic integration.
- `POST /api/v1/factor` for factoring polynomials.
- `GET /api/v1/trace/<request_id>` for retrieving past traces by ID.