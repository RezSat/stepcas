from __future__ import annotations

from collections.abc import Sequence

from stepcas import Expr, Step, TraceResult


def assert_trace_rule_sequence(
    trace: Sequence[Step] | TraceResult, expected_rules: Sequence[str]
) -> None:
    steps = trace.steps if isinstance(trace, TraceResult) else trace
    assert [step.rule for step in steps] == list(expected_rules)


def assert_trace_before_after_integrity(start_expr: Expr, trace_result: TraceResult) -> None:
    current = start_expr
    for index, step in enumerate(trace_result.steps):
        assert step.before == current, f"step {index} before-expression mismatch"
        current = step.after
    assert current == trace_result.expr
