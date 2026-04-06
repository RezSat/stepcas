import pytest

from stepcas import Number, Symbol, extract_linear_form, parse_expr, simplify
from stepcas.errors import (
    LINEAR_NONLINEAR_FORM,
    LINEAR_UNSUPPORTED_STRUCTURE,
    LINEAR_UNSUPPORTED_SYMBOL,
    LinearFormError,
)


def test_extract_linear_form_from_symbol() -> None:
    form = extract_linear_form(Symbol("x"), "x")
    assert form.coefficient == 1
    assert form.constant == 0


def test_extract_linear_form_from_scaled_variable() -> None:
    expr = simplify(parse_expr("2*x"))
    form = extract_linear_form(expr, "x")
    assert form.coefficient == 2
    assert form.constant == 0


def test_extract_linear_form_from_variable_plus_constant() -> None:
    expr = simplify(parse_expr("x + 3"))
    form = extract_linear_form(expr, "x")
    assert form.coefficient == 1
    assert form.constant == 3


def test_extract_linear_form_from_constant_plus_variable() -> None:
    expr = simplify(parse_expr("3 + x"))
    form = extract_linear_form(expr, "x")
    assert form.coefficient == 1
    assert form.constant == 3


def test_extract_linear_form_from_negative_variable_plus_constant() -> None:
    expr = simplify(parse_expr("-x + 1"))
    form = extract_linear_form(expr, "x")
    assert form.coefficient == -1
    assert form.constant == 1


def test_extract_linear_form_from_constant_only() -> None:
    form = extract_linear_form(Number(7), "x")
    assert form.coefficient == 0
    assert form.constant == 7


def test_extract_linear_form_rejects_squared_variable() -> None:
    expr = simplify(parse_expr("x**2"))
    with pytest.raises(LinearFormError) as exc_info:
        extract_linear_form(expr, "x")

    assert exc_info.value.code == LINEAR_NONLINEAR_FORM


def test_extract_linear_form_rejects_product_with_two_variable_factors() -> None:
    expr = simplify(parse_expr("x*x"))
    with pytest.raises(LinearFormError) as exc_info:
        extract_linear_form(expr, "x")

    assert exc_info.value.code == LINEAR_NONLINEAR_FORM


def test_extract_linear_form_rejects_distribution_required_structure() -> None:
    expr = simplify(parse_expr("2*(x+1)"))
    with pytest.raises(LinearFormError) as exc_info:
        extract_linear_form(expr, "x")

    assert exc_info.value.code == LINEAR_UNSUPPORTED_STRUCTURE


def test_extract_linear_form_rejects_other_symbols() -> None:
    expr = simplify(parse_expr("y + 1"))
    with pytest.raises(LinearFormError) as exc_info:
        extract_linear_form(expr, "x")

    assert exc_info.value.code == LINEAR_UNSUPPORTED_SYMBOL


@pytest.mark.parametrize("invalid_variable", ["", "1x", "x+y", None, 1])
def test_extract_linear_form_rejects_invalid_target_variable_identifiers(
    invalid_variable: object,
) -> None:
    with pytest.raises(LinearFormError) as exc_info:
        extract_linear_form(Number(1), invalid_variable)

    assert exc_info.value.code == LINEAR_UNSUPPORTED_SYMBOL
