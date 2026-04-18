import pytest

from stepcas import Add, Mul, Number, Pow, Symbol, differentiate
from stepcas.errors import DIFFERENTIATE_UNSUPPORTED_SYMBOL, DifferentiationError

from tests.trace_helpers import assert_trace_before_after_integrity, assert_trace_rule_sequence


def test_differentiate_constant() -> None:
    assert differentiate(Number(9), "x") == Number(0)


def test_differentiate_variable() -> None:
    assert differentiate(Symbol("x"), "x") == Number(1)


def test_differentiate_variable_trace_rule_sequence_and_integrity() -> None:
    expr = Symbol("x")

    trace_result = differentiate(expr, "x", trace=True)
    assert trace_result.expr == Number(1)
    assert_trace_rule_sequence(trace_result, ["derivative-symbol"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_differentiate_power() -> None:
    assert differentiate(Pow(Symbol("x"), Number(3)), "x") == Mul(
        Number(3), Pow(Symbol("x"), Number(2))
    )


def test_differentiate_power_trace_rule_sequence() -> None:
    expr = Pow(Symbol("x"), Number(3))
    trace_result = differentiate(expr, "x", trace=True)

    assert trace_result.expr == Mul(Number(3), Pow(Symbol("x"), Number(2)))
    assert_trace_rule_sequence(
        trace_result,
        ["derivative-symbol", "derivative-power", "fold-mul-constants"],
    )


def test_differentiate_constant_trace_rule_sequence_and_integrity() -> None:
    expr = Number(9)

    trace_result = differentiate(expr, "x", trace=True)

    assert trace_result.expr == Number(0)
    assert_trace_rule_sequence(trace_result, ["derivative-constant"])
    assert_trace_before_after_integrity(expr, trace_result)


def test_differentiate_sum() -> None:
    assert differentiate(Add(Pow(Symbol("x"), Number(2)), Mul(Number(2), Symbol("x"))), "x") == Add(
        Number(2),
        Mul(Number(2), Symbol("x")),
    )


@pytest.mark.parametrize("invalid_variable", ["", "1x", "x+y", None, 1])
def test_differentiate_rejects_invalid_target_variable_identifiers(
    invalid_variable: object,
) -> None:
    with pytest.raises(DifferentiationError) as exc_info:
        differentiate(Symbol("x"), invalid_variable)

    assert exc_info.value.code == DIFFERENTIATE_UNSUPPORTED_SYMBOL


def test_differentiate_product_mixed_constant_symbol() -> None:
    assert differentiate(Mul(Number(3), Symbol("x")), "x") == Number(3)


def test_differentiate_product_mixed_constant_symbol_trace() -> None:
    expr = Mul(Number(3), Symbol("x"))
    trace_result = differentiate(expr, "x", trace=True)

    assert trace_result.expr == Number(3)
    assert_trace_rule_sequence(
        trace_result,
        ["derivative-constant", "derivative-symbol", "derivative-product", "fold-mul-constants", "collapse-single-mul"],
    )
    assert_trace_before_after_integrity(expr, trace_result)


def test_differentiate_product_multiple_constant_symbol() -> None:
    assert differentiate(Mul(Number(2), Number(3), Symbol("x")), "x") == Number(6)


def test_differentiate_product_all_constant() -> None:
    assert differentiate(Mul(Number(3), Number(5)), "x") == Number(0)


def test_differentiate_product_all_constant_trace() -> None:
    expr = Mul(Number(3), Number(5))
    trace_result = differentiate(expr, "x", trace=True)

    assert trace_result.expr == Number(0)
    assert_trace_rule_sequence(
        trace_result,
        ["derivative-constant", "derivative-constant", "derivative-product"],
    )
    assert_trace_before_after_integrity(expr, trace_result)


def test_differentiate_product_two_symbols_one_variable() -> None:
    assert differentiate(Mul(Symbol("x"), Symbol("y")), "x") == Symbol("y")
