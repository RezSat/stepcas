from __future__ import annotations

from .errors import (
    POLYNOMIAL_NON_POLYNOMIAL_FORM,
    POLYNOMIAL_UNSUPPORTED_STRUCTURE,
    POLYNOMIAL_UNSUPPORTED_SYMBOL,
    PolynomialError,
)
from .expression import Add, Expr, Mul, Number, Pow, Symbol
from .variable_analysis import contains_other_symbol, contains_variable
from .variable_validation import validate_target_variable


NumberLike = int | float


def polynomial_coefficients(expr: Expr, variable: str) -> dict[int, NumberLike]:
    """Return degree-to-coefficient mapping for a one-variable polynomial."""

    validate_target_variable(
        variable,
        error_cls=PolynomialError,
        code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
    )

    terms = expr.terms if isinstance(expr, Add) else (expr,)
    coefficients: dict[int, NumberLike] = {}

    for term in terms:
        coefficient, degree = _term_coefficient_degree(term, variable)
        coefficients[degree] = coefficients.get(degree, 0) + coefficient

    normalized = {
        degree: coefficient for degree, coefficient in coefficients.items() if coefficient != 0
    }

    if not normalized:
        return {0: 0}

    return dict(sorted(normalized.items(), reverse=True))


def polynomial_degree(expr: Expr, variable: str) -> int:
    """Return the degree of a one-variable polynomial expression."""

    coefficients = polynomial_coefficients(expr, variable)
    return max(coefficients)


def polynomial_coeff_vector(expr: Expr, variable: str) -> list[NumberLike]:
    """Return dense highest-degree-first coefficients for a one-variable polynomial."""

    coefficients = polynomial_coefficients(expr, variable)
    max_degree = max(coefficients)
    return [coefficients.get(degree, 0) for degree in range(max_degree, -1, -1)]


def polynomial_evaluate(expr: Expr, variable: str, value: NumberLike) -> NumberLike:
    """Evaluate a one-variable polynomial expression at a numeric value."""

    if not isinstance(value, (int, float)):
        raise TypeError("Evaluation value must be an int or float")

    coefficients = polynomial_coeff_vector(expr, variable)
    use_float = isinstance(value, float) or any(
        isinstance(coefficient, float) for coefficient in coefficients
    )

    if use_float:
        result = 0.0
        numeric_value = float(value)
        for coefficient in coefficients:
            result = (result * numeric_value) + float(coefficient)
        return result

    result = 0
    for coefficient in coefficients:
        result = (result * value) + coefficient
    return result


def polynomial_leading_term(expr: Expr, variable: str) -> tuple[int, NumberLike]:
    """Return (degree, coefficient) for the leading term of a one-variable polynomial."""

    coefficients = polynomial_coefficients(expr, variable)
    degree = max(coefficients)
    return degree, coefficients[degree]


def polynomial_leading_coefficient(expr: Expr, variable: str) -> NumberLike:
    """Return the leading coefficient of a one-variable polynomial."""

    return polynomial_leading_term(expr, variable)[1]


def polynomial_trailing_coefficient(expr: Expr, variable: str) -> NumberLike:
    """Return the constant-term (degree-zero) coefficient of a polynomial."""

    return polynomial_coefficients(expr, variable).get(0, 0)


def polynomial_trailing_term(expr: Expr, variable: str) -> tuple[int, NumberLike]:
    """Return (degree, coefficient) for the lowest-degree term of a polynomial."""

    coefficients = polynomial_coefficients(expr, variable)
    degree = min(coefficients)
    return degree, coefficients[degree]


def _term_degree(term: Expr, variable: str) -> int:
    return _term_coefficient_degree(term, variable)[1]


def _term_coefficient_degree(term: Expr, variable: str) -> tuple[NumberLike, int]:
    if isinstance(term, Number):
        return term.value, 0

    if isinstance(term, Symbol):
        if term.name == variable:
            return 1, 1
        raise PolynomialError(
            f"Expression contains unsupported symbol '{term.name}'",
            code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
        )

    if isinstance(term, Pow):
        return 1, _pow_degree(term, variable)

    if isinstance(term, Mul):
        return _mul_coefficient_degree(term, variable)

    if contains_variable(term, variable):
        raise PolynomialError(
            "Expression requires expansion before polynomial degree extraction",
            code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
        )

    if contains_other_symbol(term, variable):
        raise PolynomialError(
            "Expression contains unsupported symbols for one-variable polynomial extraction",
            code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
        )

    raise PolynomialError(
        "Expression has unsupported structure for polynomial degree extraction",
        code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
    )


def _pow_degree(expr: Pow, variable: str) -> int:
    if (
        isinstance(expr.base, Symbol)
        and expr.base.name == variable
        and isinstance(expr.exponent, Number)
    ):
        exponent = _non_negative_integer_exponent(expr.exponent)
        return exponent

    if contains_other_symbol(expr, variable):
        raise PolynomialError(
            "Expression contains unsupported symbols for one-variable polynomial extraction",
            code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
        )

    if contains_variable(expr, variable):
        raise PolynomialError(
            "Expression is not a polynomial in the target variable",
            code=POLYNOMIAL_NON_POLYNOMIAL_FORM,
        )

    raise PolynomialError(
        "Expression has unsupported structure for polynomial degree extraction",
        code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
    )


def _mul_degree(expr: Mul, variable: str) -> int:
    return _mul_coefficient_degree(expr, variable)[1]


def _mul_coefficient_degree(expr: Mul, variable: str) -> tuple[NumberLike, int]:
    coefficient: NumberLike = 1
    total_degree = 0

    for factor in expr.factors:
        if isinstance(factor, Number):
            coefficient *= factor.value
            continue

        if isinstance(factor, Symbol):
            if factor.name == variable:
                total_degree += 1
                continue
            raise PolynomialError(
                f"Expression contains unsupported symbol '{factor.name}'",
                code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
            )

        if isinstance(factor, Pow):
            total_degree += _pow_degree(factor, variable)
            continue

        if isinstance(factor, Add) and contains_variable(factor, variable):
            raise PolynomialError(
                "Expression requires expansion before polynomial degree extraction",
                code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
            )

        if contains_variable(factor, variable):
            raise PolynomialError(
                "Expression requires expansion before polynomial degree extraction",
                code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
            )

        if contains_other_symbol(factor, variable):
            raise PolynomialError(
                "Expression contains unsupported symbols for one-variable polynomial extraction",
                code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
            )

        raise PolynomialError(
            "Expression has unsupported structure for polynomial degree extraction",
            code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
        )

    return coefficient, total_degree


def _non_negative_integer_exponent(exponent: Number) -> int:
    value = exponent.value
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, float) and value.is_integer() and value >= 0:
        return int(value)
    raise PolynomialError(
        "Expression is not a polynomial in the target variable",
        code=POLYNOMIAL_NON_POLYNOMIAL_FORM,
    )



