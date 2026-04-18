import pytest

from stepcas import Expr, Number, Pow, Symbol, differentiate, parse_expr
from stepcas.errors import (
    DIFFERENTIATE_NON_CONSTANT_EXPONENT,
    DIFFERENTIATE_UNSUPPORTED_SYMBOL,
    DIFFERENTIATE_UNSUPPORTED_EXPRESSION,
    LINEAR_NONLINEAR_FORM,
    LINEAR_UNSUPPORTED_SYMBOL,
    PARSE_SYNTAX_ERROR,
    PARSE_UNSUPPORTED_SYNTAX,
    REWRITE_INVALID_RULE_RESULT,
    REWRITE_ITERATION_LIMIT_EXCEEDED,
    REWRITE_STEP_LIMIT_EXCEEDED,
    DifferentiationError,
    LinearFormError,
    ParseError,
    RewriteError,
    StepcasError,
)
from stepcas.linear_form import extract_linear_form
from stepcas.rewrite import rewrite_fixpoint


def test_parse_error_uses_shared_hierarchy_and_syntax_code() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse_expr("(")

    err = exc_info.value
    assert isinstance(err, StepcasError)
    assert isinstance(err, ValueError)
    assert err.domain == "parse"
    assert err.code == PARSE_SYNTAX_ERROR


def test_parse_error_uses_stable_unsupported_syntax_code() -> None:
    with pytest.raises(ParseError) as exc_info:
        parse_expr("f(x)")

    assert exc_info.value.code == PARSE_UNSUPPORTED_SYNTAX


def test_differentiation_error_uses_shared_hierarchy_and_stable_code() -> None:
    with pytest.raises(DifferentiationError) as exc_info:
        differentiate(Pow(Symbol("x"), Symbol("y")), "x")

    err = exc_info.value
    assert isinstance(err, StepcasError)
    assert isinstance(err, ValueError)
    assert err.domain == "differentiate"
    assert err.code == DIFFERENTIATE_NON_CONSTANT_EXPONENT


def test_differentiation_error_code_for_unsupported_expression() -> None:
    with pytest.raises(DifferentiationError) as exc_info:
        differentiate(Expr(), "x")

    assert exc_info.value.code == DIFFERENTIATE_UNSUPPORTED_EXPRESSION


def test_differentiation_error_code_for_invalid_target_variable() -> None:
    with pytest.raises(DifferentiationError) as exc_info:
        differentiate(Number(1), "1x")

    assert exc_info.value.code == DIFFERENTIATE_UNSUPPORTED_SYMBOL


def test_rewrite_error_has_stable_code_for_invalid_rule_result_shape() -> None:
    with pytest.raises(RewriteError) as exc_info:
        rewrite_fixpoint(Number(1), [("bad-rule", lambda expr: Number(2))], [])

    err = exc_info.value
    assert isinstance(err, StepcasError)
    assert isinstance(err, ValueError)
    assert err.domain == "rewrite"
    assert err.code == REWRITE_INVALID_RULE_RESULT


def test_linear_form_error_uses_shared_hierarchy_and_stable_code() -> None:
    with pytest.raises(LinearFormError) as exc_info:
        extract_linear_form(parse_expr("x**2"), "x")

    err = exc_info.value
    assert isinstance(err, StepcasError)
    assert isinstance(err, ValueError)
    assert err.domain == "linear"
    assert err.code == LINEAR_NONLINEAR_FORM


def test_linear_form_error_code_for_invalid_target_variable() -> None:
    with pytest.raises(LinearFormError) as exc_info:
        extract_linear_form(parse_expr("x + 1"), "x+y")

    assert exc_info.value.code == LINEAR_UNSUPPORTED_SYMBOL


def test_rewrite_error_raises_when_iteration_limit_exceeded() -> None:
    """Test that non-terminating rule set hits iteration limit."""

    def non_terminating_rule(expr):
        return Number(1), "Always return 1"

    with pytest.raises(RewriteError) as exc_info:
        rewrite_fixpoint(Number(0), [("non-terminating", non_terminating_rule)], [], max_iterations=3)

    err = exc_info.value
    assert err.domain == "rewrite"
    assert err.code == REWRITE_ITERATION_LIMIT_EXCEEDED


def test_rewrite_error_raises_when_step_limit_exceeded() -> None:
    """Test that non-terminating rule set hits step limit."""

    def ping_pong_rule(expr):
        if isinstance(expr, Number) and expr.value == 0:
            return Number(1), "flip to 1"
        if isinstance(expr, Number) and expr.value == 1:
            return Number(0), "flip to 0"
        return None

    with pytest.raises(RewriteError) as exc_info:
        rewrite_fixpoint(Number(0), [("ping-pong", ping_pong_rule)], [], max_steps=3)

    err = exc_info.value
    assert err.domain == "rewrite"
    assert err.code == REWRITE_STEP_LIMIT_EXCEEDED
