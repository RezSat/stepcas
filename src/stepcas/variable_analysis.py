from __future__ import annotations

from .expression import Add, Expr, Mul, Pow, Symbol


def contains_variable(expr: Expr, variable: str) -> bool:
    """Check if expression contains the given variable symbol."""
    if isinstance(expr, Symbol):
        return expr.name == variable
    if isinstance(expr, Add):
        return any(contains_variable(term, variable) for term in expr.terms)
    if isinstance(expr, Mul):
        return any(contains_variable(factor, variable) for factor in expr.factors)
    if isinstance(expr, Pow):
        return contains_variable(expr.base, variable) or contains_variable(
            expr.exponent, variable
        )
    return False


def contains_other_symbol(expr: Expr, variable: str) -> bool:
    """Check if expression contains any symbol other than the given variable."""
    if isinstance(expr, Symbol):
        return expr.name != variable
    if isinstance(expr, Add):
        return any(contains_other_symbol(term, variable) for term in expr.terms)
    if isinstance(expr, Mul):
        return any(contains_other_symbol(factor, variable) for factor in expr.factors)
    if isinstance(expr, Pow):
        return contains_other_symbol(expr.base, variable) or contains_other_symbol(
            expr.exponent, variable
        )
    return False