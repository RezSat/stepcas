from __future__ import annotations

from .errors import (
    POLYNOMIAL_NON_POLYNOMIAL_FORM,
    POLYNOMIAL_UNSUPPORTED_STRUCTURE,
    POLYNOMIAL_UNSUPPORTED_SYMBOL,
    PolynomialError,
)
from .expression import Add, Expr, Mul, Number, Pow, Symbol


def polynomial_degree(expr: Expr, variable: str) -> int:
    """Return the degree of a one-variable polynomial expression."""

    if isinstance(expr, Add):
        if not expr.terms:
            return 0
        return max(_term_degree(term, variable) for term in expr.terms)
    return _term_degree(expr, variable)


def _term_degree(term: Expr, variable: str) -> int:
    if isinstance(term, Number):
        return 0

    if isinstance(term, Symbol):
        if term.name == variable:
            return 1
        raise PolynomialError(
            f"Expression contains unsupported symbol '{term.name}'",
            code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
        )

    if isinstance(term, Pow):
        return _pow_degree(term, variable)

    if isinstance(term, Mul):
        return _mul_degree(term, variable)

    if _contains_variable(term, variable):
        raise PolynomialError(
            "Expression requires expansion before polynomial degree extraction",
            code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
        )

    if _contains_other_symbol(term, variable):
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

    if _contains_other_symbol(expr, variable):
        raise PolynomialError(
            "Expression contains unsupported symbols for one-variable polynomial extraction",
            code=POLYNOMIAL_UNSUPPORTED_SYMBOL,
        )

    if _contains_variable(expr, variable):
        raise PolynomialError(
            "Expression is not a polynomial in the target variable",
            code=POLYNOMIAL_NON_POLYNOMIAL_FORM,
        )

    raise PolynomialError(
        "Expression has unsupported structure for polynomial degree extraction",
        code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
    )


def _mul_degree(expr: Mul, variable: str) -> int:
    total_degree = 0
    for factor in expr.factors:
        if isinstance(factor, Add) and _contains_variable(factor, variable):
            raise PolynomialError(
                "Expression requires expansion before polynomial degree extraction",
                code=POLYNOMIAL_UNSUPPORTED_STRUCTURE,
            )
        total_degree += _term_degree(factor, variable)
    return total_degree


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


def _contains_variable(expr: Expr, variable: str) -> bool:
    if isinstance(expr, Symbol):
        return expr.name == variable
    if isinstance(expr, Add):
        return any(_contains_variable(term, variable) for term in expr.terms)
    if isinstance(expr, Mul):
        return any(_contains_variable(factor, variable) for factor in expr.factors)
    if isinstance(expr, Pow):
        return _contains_variable(expr.base, variable) or _contains_variable(
            expr.exponent, variable
        )
    return False


def _contains_other_symbol(expr: Expr, variable: str) -> bool:
    if isinstance(expr, Symbol):
        return expr.name != variable
    if isinstance(expr, Add):
        return any(_contains_other_symbol(term, variable) for term in expr.terms)
    if isinstance(expr, Mul):
        return any(_contains_other_symbol(factor, variable) for factor in expr.factors)
    if isinstance(expr, Pow):
        return _contains_other_symbol(expr.base, variable) or _contains_other_symbol(
            expr.exponent, variable
        )
    return False
