from stepcas import (
    Add,
    Equation,
    Mul,
    Number,
    Pow,
    SCHEMA_VERSION,
    Step,
    Symbol,
    TraceResult,
    expr_to_json,
    step_to_json,
    trace_result_to_json,
)


def test_expr_to_json_uses_schema_envelope_and_stable_node_kinds() -> None:
    payload = expr_to_json(Equation(Add(Symbol("x"), Number(1)), Mul(Number(2), Symbol("y"))))

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["object"] == "expr"
    assert payload["data"]["kind"] == "equation"
    assert payload["data"]["lhs"]["kind"] == "add"
    assert payload["data"]["rhs"]["kind"] == "mul"


def test_expr_to_json_number_includes_explicit_numeric_type() -> None:
    int_payload = expr_to_json(Number(3))
    float_payload = expr_to_json(Number(3.0))

    assert int_payload["data"] == {"kind": "number", "number_type": "int", "value": 3}
    assert float_payload["data"] == {"kind": "number", "number_type": "float", "value": 3.0}


def test_expr_to_json_nested_pow_shape_is_typed_and_ordered() -> None:
    payload = expr_to_json(Pow(Add(Symbol("x"), Number(1)), Number(2)))

    assert payload["data"] == {
        "kind": "pow",
        "base": {
            "kind": "add",
            "terms": [
                {"kind": "symbol", "name": "x"},
                {"kind": "number", "number_type": "int", "value": 1},
            ],
        },
        "exponent": {"kind": "number", "number_type": "int", "value": 2},
    }


def test_step_to_json_includes_nullable_explanation_and_metadata() -> None:
    step = Step(
        rule="rule-id",
        before=Symbol("x"),
        after=Number(1),
        explanation=None,
        metadata={"phase": "simplify", "visible": True, "tags": ("core", "v1")},
    )

    payload = step_to_json(step)

    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["object"] == "step"
    assert payload["data"]["explanation"] is None
    assert payload["data"]["metadata"] == {
        "phase": "simplify",
        "visible": True,
        "tags": ["core", "v1"],
    }


def test_trace_result_to_json_is_deterministic_and_stable() -> None:
    trace = TraceResult(
        expr=Symbol("x"),
        steps=[
            Step("first", Symbol("x"), Symbol("x"), "noop", {"index": 1}),
            Step("second", Symbol("x"), Symbol("x"), "noop", {"index": 2}),
        ],
    )

    first = trace_result_to_json(trace)
    second = trace_result_to_json(trace)

    assert first == second
    assert first["schema_version"] == SCHEMA_VERSION
    assert first["object"] == "trace_result"
    assert [step["rule"] for step in first["data"]["steps"]] == ["first", "second"]


def test_step_metadata_rejects_non_json_serializable_types() -> None:
    # Test that set is not JSON-serializable - should raise TypeError
    step_with_set = Step(
        rule="bad",
        before=Symbol("x"),
        after=Number(1),
        metadata={"tags": {"a", "b"}},
    )
    import json
    try:
        payload = step_to_json(step_with_set)
        json_str = json.dumps(payload)
        json.loads(json_str)
        raise AssertionError("Expected TypeError for non-JSON-serializable set")
    except TypeError as e:
        # Expected: serialization rejected
        assert "Unsupported metadata value" in str(e)


def test_step_metadata_rejects_object_instance() -> None:
    # Test that arbitrary objects are not JSON-serializable - should raise TypeError
    class Custom:
        pass
    step_with_object = Step(
        rule="bad",
        before=Symbol("x"),
        after=Number(1),
        metadata={"custom": Custom()},
    )
    import json
    try:
        payload = step_to_json(step_with_object)
        json_str = json.dumps(payload)
        json.loads(json_str)
        raise AssertionError("Expected TypeError for non-JSON-serializable object")
    except TypeError as e:
        # Expected: serialization rejected
        assert "Unsupported metadata value" in str(e)
