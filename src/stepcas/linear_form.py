from __future__ import annotations

from dataclasses import dataclass

from .errors import (
    LINEAR_NONLINEAR_FORM,
    LINEAR_UNSUPPORTED_STRUCTURE,
    LINEAR_UNSUPPORTED_SYMBOL,
    LinearFormError,
)
from .expression import Add, Expr, Mul, Number, Pow, Symbol


@dataclass(frozen=True)
class LinearForm:
    variable: str
    coefficient: int | float
    constant: int | float


def extract_linear_form(expr: Expr, variable: str) -> LinearForm:
    coefficient, constant = _extract_coefficients(expr, variable)
    return LinearForm(variable=variable, coefficient=coefficient, constant=constant)


def _extract_coefficients(expr: Expr, variable: str) -> tuple[int | float, int | float]:
    if isinstance(expr, Add):
        coefficient = 0
        constant = 0
        for term in expr.terms:
            term_coefficient, term_constant = _extract_term(term, variable)
            coefficient += term_coefficient
            constant += term_constant
        return coefficient, constant
    return _extract_term(expr, variable)


def _extract_term(term: Expr, variable: str) -> tuple[int | float, int | float]:
    if isinstance(term, Number):
        return 0, term.value

    if isinstance(term, Symbol):
        if term.name == variable:
            return 1, 0
        raise LinearFormError(
            f"Expression contains unsupported symbol '{term.name}'",
            code=LINEAR_UNSUPPORTED_SYMBOL,
        )

    if isinstance(term, Pow):
        return _extract_pow(term, variable)

    if isinstance(term, Mul):
        return _extract_mul(term, variable)

    if _contains_variable(term, variable):
        raise LinearFormError(
            "Expression has unsupported linear structure for extraction",
            code=LINEAR_UNSUPPORTED_STRUCTURE,
        )

    if _contains_other_symbol(term, variable):
        raise LinearFormError(
            "Expression contains unsupported symbols for one-variable linear extraction",
            code=LINEAR_UNSUPPORTED_SYMBOL,
        )

    raise LinearFormError(
        "Expression has unsupported structure for linear extraction",
        code=LINEAR_UNSUPPORTED_STRUCTURE,
    )


def _extract_pow(expr: Pow, variable: str) -> tuple[int | float, int | float]:
    if (
        isinstance(expr.base, Symbol)
        and expr.base.name == variable
        and isinstance(expr.exponent, Number)
    ):
        if expr.exponent.value == 1:
            return 1, 0
        raise LinearFormError(
            "Expression is non-linear in the target variable",
            code=LINEAR_NONLINEAR_FORM,
        )

    if _contains_variable(expr, variable):
        raise LinearFormError(
            "Expression is non-linear in the target variable",
            code=LINEAR_NONLINEAR_FORM,
        )

    if _contains_other_symbol(expr, variable):
        raise LinearFormError(
            "Expression contains unsupported symbols for one-variable linear extraction",
            code=LINEAR_UNSUPPORTED_SYMBOL,
        )

    raise LinearFormError(
        "Expression has unsupported structure for linear extraction",
        code=LINEAR_UNSUPPORTED_STRUCTURE,
    )


def _extract_mul(expr: Mul, variable: str) -> tuple[int | float, int | float]:
    coefficient = 1
    variable_count = 0

    for factor in expr.factors:
        if isinstance(factor, Number):
            coefficient *= factor.value
            continue

        if isinstance(factor, Symbol):
            if factor.name == variable:
                variable_count += 1
            else:
                raise LinearFormError(
                    f"Expression contains unsupported symbol '{factor.name}'",
                    code=LINEAR_UNSUPPORTED_SYMBOL,
                )
            continue

        if isinstance(factor, Pow):
            if (
                isinstance(factor.base, Symbol)
                and factor.base.name == variable
                and isinstance(factor.exponent, Number)
            ):
                if factor.exponent.value == 1:
                    variable_count += 1
                else:
                    raise LinearFormError(
                        "Expression is non-linear in the target variable",
                        code=LINEAR_NONLINEAR_FORM,
                    )
                continue

        if _contains_variable(factor, variable):
            raise LinearFormError(
                "Expression has unsupported linear structure for extraction",
                code=LINEAR_UNSUPPORTED_STRUCTURE,
            )

        if _contains_other_symbol(factor, variable):
            raise LinearFormError(
                "Expression contains unsupported symbols for one-variable linear extraction",
                code=LINEAR_UNSUPPORTED_SYMBOL,
            )

        raise LinearFormError(
            "Expression has unsupported structure for linear extraction",
            code=LINEAR_UNSUPPORTED_STRUCTURE,
        )

    if variable_count == 0:
        return 0, coefficient

    if variable_count == 1:
        return coefficient, 0

    raise LinearFormError(
        "Expression is non-linear in the target variable",
        code=LINEAR_NONLINEAR_FORM,
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
