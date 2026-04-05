from __future__ import annotations

from .expression import Add, Expr, Mul, Number, Pow, Symbol
from .simplify import simplify
from .trace import Step, TraceResult


class DifferentiationError(ValueError):
    pass


def differentiate(expr: Expr, variable: str, trace: bool = False) -> Expr | TraceResult:
    steps: list[Step] = []
    result = _differentiate(expr, variable, steps)
    simplified = simplify(result, trace=True)
    steps.extend(simplified.steps)
    if trace:
        return TraceResult(expr=simplified.expr, steps=steps)
    return simplified.expr


def _differentiate(expr: Expr, variable: str, steps: list[Step]) -> Expr:
    if isinstance(expr, Number):
        after = Number(0)
        steps.append(Step("derivative-constant", expr, after, "The derivative of a constant is zero"))
        return after
    if isinstance(expr, Symbol):
        after = Number(1 if expr.name == variable else 0)
        explanation = (
            "Differentiate the variable with respect to itself"
            if expr.name == variable
            else "Treat other symbols as constants"
        )
        steps.append(Step("derivative-symbol", expr, after, explanation))
        return after
    if isinstance(expr, Add):
        after = Add(*[_differentiate(term, variable, steps) for term in expr.terms])
        steps.append(Step("derivative-sum", expr, after, "Differentiate each term of the sum"))
        return after
    if isinstance(expr, Mul):
        terms = []
        for index, factor in enumerate(expr.factors):
            differentiated = _differentiate(factor, variable, steps)
            new_factors = list(expr.factors)
            new_factors[index] = differentiated
            terms.append(Mul(*new_factors))
        after = Add(*terms)
        steps.append(Step("derivative-product", expr, after, "Apply the product rule"))
        return after
    if isinstance(expr, Pow):
        if isinstance(expr.exponent, Number):
            new_exponent = Number(expr.exponent.value - 1)
            after = Mul(expr.exponent, Pow(expr.base, new_exponent), _differentiate(expr.base, variable, steps))
            steps.append(
                Step(
                    "derivative-power",
                    expr,
                    after,
                    "Apply the power rule and chain rule",
                )
            )
            return after
        raise DifferentiationError("Only constant exponents are supported in this starter")
    raise DifferentiationError(f"Unsupported expression for differentiation: {expr!r}")
