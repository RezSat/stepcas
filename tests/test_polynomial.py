import pytest

from stepcas import Number, Symbol, parse_expr, polynomial_degree, simplify
from stepcas.errors import (
    POLYNOMIAL_NON_POLYNOMIAL_FORM,
    POLYNOMIAL_UNSUPPORTED_STRUCTURE,
    POLYNOMIAL_UNSUPPORTED_SYMBOL,
    PolynomialError,
)


def test_polynomial_degree_constant_is_zero() -> None:
    assert polynomial_degree(Number(7), "x") == 0


def test_polynomial_degree_symbol_is_one() -> None:
    assert polynomial_degree(Symbol("x"), "x") == 1


def test_polynomial_degree_univariate_sum_uses_highest_power() -> None:
    expr = simplify(parse_expr("3*x**4 + 2*x - 1"))
    assert polynomial_degree(expr, "x") == 4


def test_polynomial_degree_handles_repeated_symbol_factors() -> None:
    expr = simplify(parse_expr("2*x*x"))
    assert polynomial_degree(expr, "x") == 2


def test_polynomial_degree_rejects_other_symbols() -> None:
    expr = simplify(parse_expr("y + 1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_degree(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_UNSUPPORTED_SYMBOL


def test_polynomial_degree_rejects_negative_exponents() -> None:
    expr = simplify(parse_expr("x**-1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_degree(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_NON_POLYNOMIAL_FORM


def test_polynomial_degree_rejects_non_integer_exponents() -> None:
    expr = simplify(parse_expr("x**0.5"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_degree(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_NON_POLYNOMIAL_FORM


def test_polynomial_degree_rejects_unexpanded_structure() -> None:
    expr = simplify(parse_expr("2*(x+1)"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_degree(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_UNSUPPORTED_STRUCTURE
