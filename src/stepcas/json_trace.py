from __future__ import annotations

from typing import Any

from .expression import Add, Equation, Expr, Mul, Number, Pow, Symbol
from .trace import Step, TraceResult

SCHEMA_VERSION = "stepcas.v1"


def expr_to_json(expr: Expr) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "object": "expr",
        "data": _expr_data(expr),
    }


def step_to_json(step: Step) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "object": "step",
        "data": _step_data(step),
    }


def trace_result_to_json(result: TraceResult) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "object": "trace_result",
        "data": {
            "expr": _expr_data(result.expr),
            "steps": [_step_data(step) for step in result.steps],
        },
    }


def _expr_data(expr: Expr) -> dict[str, Any]:
    if isinstance(expr, Number):
        number_type = "float" if isinstance(expr.value, float) else "int"
        return {
            "kind": "number",
            "number_type": number_type,
            "value": expr.value,
        }
    if isinstance(expr, Symbol):
        return {
            "kind": "symbol",
            "name": expr.name,
        }
    if isinstance(expr, Add):
        return {
            "kind": "add",
            "terms": [_expr_data(term) for term in expr.terms],
        }
    if isinstance(expr, Mul):
        return {
            "kind": "mul",
            "factors": [_expr_data(factor) for factor in expr.factors],
        }
    if isinstance(expr, Pow):
        return {
            "kind": "pow",
            "base": _expr_data(expr.base),
            "exponent": _expr_data(expr.exponent),
        }
    if isinstance(expr, Equation):
        return {
            "kind": "equation",
            "lhs": _expr_data(expr.lhs),
            "rhs": _expr_data(expr.rhs),
        }
    raise TypeError(f"Unsupported Expr for JSON serialization: {expr!r}")


def _step_data(step: Step) -> dict[str, Any]:
    return {
        "rule": step.rule,
        "before": _expr_data(step.before),
        "after": _expr_data(step.after),
        "explanation": step.explanation,
        "metadata": _json_object(step.metadata),
    }


def _json_object(value: dict[str, Any]) -> dict[str, Any]:
    return {key: _json_value(item) for key, item in value.items()}


def _json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("Step metadata must use string keys for JSON serialization")
            normalized[key] = _json_value(item)
        return normalized
    raise TypeError(f"Unsupported metadata value for JSON serialization: {value!r}")
