import pytest

from stepcas import (
    Number,
    Symbol,
    polynomial_coeff_vector,
    polynomial_evaluate,
    parse_expr,
    polynomial_coefficients,
    polynomial_degree,
    polynomial_leading_coefficient,
    polynomial_leading_term,
    polynomial_trailing_coefficient,
    polynomial_trailing_term,
    simplify,
)
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


def test_polynomial_coefficients_collect_like_powers() -> None:
    expr = simplify(parse_expr("3*x**4 + 2*x - 5*x + 7"))
    assert polynomial_coefficients(expr, "x") == {4: 3, 1: -3, 0: 7}


def test_polynomial_coefficients_multiplied_symbol_factors() -> None:
    expr = simplify(parse_expr("2*x*x"))
    assert polynomial_coefficients(expr, "x") == {2: 2}


def test_polynomial_coefficients_zero_polynomial() -> None:
    expr = simplify(parse_expr("x - x"))
    assert polynomial_coefficients(expr, "x") == {0: 0}


def test_polynomial_coefficients_rejects_non_polynomial_power() -> None:
    expr = simplify(parse_expr("x**-1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_coefficients(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_NON_POLYNOMIAL_FORM


def test_polynomial_coefficients_rejects_other_symbols() -> None:
    expr = simplify(parse_expr("x + y"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_coefficients(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_UNSUPPORTED_SYMBOL


def test_polynomial_coeff_vector_returns_dense_coefficients() -> None:
    expr = simplify(parse_expr("3*x**4 - 2*x + 5"))
    assert polynomial_coeff_vector(expr, "x") == [3, 0, 0, -2, 5]


def test_polynomial_coeff_vector_zero_polynomial() -> None:
    expr = simplify(parse_expr("x - x"))
    assert polynomial_coeff_vector(expr, "x") == [0]


def test_polynomial_coeff_vector_rejects_invalid_variable_name() -> None:
    expr = simplify(parse_expr("x + 1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_coeff_vector(expr, "x+y")

    assert exc_info.value.code == POLYNOMIAL_UNSUPPORTED_SYMBOL


def test_polynomial_evaluate_integer_value_returns_integer_result() -> None:
    expr = simplify(parse_expr("3*x**2 - 2*x + 5"))
    assert polynomial_evaluate(expr, "x", 2) == 13


def test_polynomial_evaluate_rejects_invalid_value_type() -> None:
    expr = simplify(parse_expr("x + 1"))
    with pytest.raises(TypeError) as exc_info:
        polynomial_evaluate(expr, "x", "2")

    assert "Evaluation value must be an int or float" in str(exc_info.value)


def test_polynomial_evaluate_float_value_returns_float_result() -> None:
    expr = simplify(parse_expr("3*x**2 - 2*x + 5"))
    assert polynomial_evaluate(expr, "x", 0.5) == pytest.approx(4.75)


def test_polynomial_evaluate_float_coefficients_with_integer_value() -> None:
    expr = simplify(parse_expr("0.5*x**2 + 1.5*x + 2.0"))
    assert polynomial_evaluate(expr, "x", 2) == pytest.approx(7.0)


def test_polynomial_evaluate_rejects_unexpanded_structure() -> None:
    expr = simplify(parse_expr("2*(x+1)"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_evaluate(expr, "x", 3)

    assert exc_info.value.code == POLYNOMIAL_UNSUPPORTED_STRUCTURE


def test_polynomial_evaluate_rejects_unexpanded_product_of_sums() -> None:
    expr = simplify(parse_expr("(x+1)*(x+2)"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_evaluate(expr, "x", 3)

    assert exc_info.value.code == POLYNOMIAL_UNSUPPORTED_STRUCTURE


def test_polynomial_leading_term_selects_highest_power() -> None:
    expr = simplify(parse_expr("3*x**4 + 2*x - 1"))
    assert polynomial_leading_term(expr, "x") == (4, 3)


def test_polynomial_leading_term_collects_like_powers() -> None:
    expr = simplify(parse_expr("5*x**3 - 2*x**3 + x"))
    assert polynomial_leading_term(expr, "x") == (3, 3)


def test_polynomial_leading_term_zero_polynomial() -> None:
    expr = simplify(parse_expr("x - x"))
    assert polynomial_leading_term(expr, "x") == (0, 0)


def test_polynomial_leading_term_rejects_unexpanded_structure() -> None:
    expr = simplify(parse_expr("2*(x+1)"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_leading_term(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_UNSUPPORTED_STRUCTURE


def test_polynomial_leading_term_rejects_non_polynomial_power() -> None:
    expr = simplify(parse_expr("x**-1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_leading_term(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_NON_POLYNOMIAL_FORM


def test_polynomial_leading_coefficient_selects_highest_power() -> None:
    expr = simplify(parse_expr("3*x**4 + 2*x - 1"))
    assert polynomial_leading_coefficient(expr, "x") == 3


def test_polynomial_leading_coefficient_collects_like_powers() -> None:
    expr = simplify(parse_expr("5*x**3 - 2*x**3 + x"))
    assert polynomial_leading_coefficient(expr, "x") == 3


def test_polynomial_leading_coefficient_zero_polynomial() -> None:
    expr = simplify(parse_expr("x - x"))
    assert polynomial_leading_coefficient(expr, "x") == 0


def test_polynomial_leading_coefficient_rejects_non_polynomial_power() -> None:
    expr = simplify(parse_expr("x**-1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_leading_coefficient(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_NON_POLYNOMIAL_FORM


def test_polynomial_trailing_coefficient_returns_constant_term() -> None:
    expr = simplify(parse_expr("3*x**4 - 2*x + 5"))
    assert polynomial_trailing_coefficient(expr, "x") == 5


def test_polynomial_trailing_coefficient_returns_zero_when_missing_constant() -> None:
    expr = simplify(parse_expr("3*x**4 - 2*x"))
    assert polynomial_trailing_coefficient(expr, "x") == 0


def test_polynomial_trailing_coefficient_zero_polynomial() -> None:
    expr = simplify(parse_expr("x - x"))
    assert polynomial_trailing_coefficient(expr, "x") == 0


def test_polynomial_trailing_coefficient_rejects_non_polynomial_power() -> None:
    expr = simplify(parse_expr("x**-1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_trailing_coefficient(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_NON_POLYNOMIAL_FORM


def test_polynomial_trailing_term_selects_lowest_nonzero_power() -> None:
    expr = simplify(parse_expr("3*x**4 - 2*x + 5"))
    assert polynomial_trailing_term(expr, "x") == (0, 5)


def test_polynomial_trailing_term_handles_missing_constant_term() -> None:
    expr = simplify(parse_expr("3*x**4 - 2*x"))
    assert polynomial_trailing_term(expr, "x") == (1, -2)


def test_polynomial_trailing_term_zero_polynomial() -> None:
    expr = simplify(parse_expr("x - x"))
    assert polynomial_trailing_term(expr, "x") == (0, 0)


def test_polynomial_trailing_term_rejects_non_polynomial_power() -> None:
    expr = simplify(parse_expr("x**-1"))
    with pytest.raises(PolynomialError) as exc_info:
        polynomial_trailing_term(expr, "x")

    assert exc_info.value.code == POLYNOMIAL_NON_POLYNOMIAL_FORM
