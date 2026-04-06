from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .expression import Equation, Expr, Mul, Number, Symbol
from .errors import LINEAR_UNSUPPORTED_SYMBOL, LinearFormError
from .linear_form import extract_linear_form
from .trace import Step
from .variable_validation import validate_target_variable


class LinearSolveKind(str, Enum):
    SOLVED = "solved"
    NO_SOLUTION = "no_solution"
    INFINITE_SOLUTIONS = "infinite_solutions"


@dataclass(frozen=True)
class SolvedLinearEquation:
    kind: LinearSolveKind
    variable: str
    value: Number


@dataclass(frozen=True)
class NoLinearSolution:
    kind: LinearSolveKind
    reason: str


@dataclass(frozen=True)
class InfiniteLinearSolutions:
    kind: LinearSolveKind
    reason: str


LinearSolveResult = SolvedLinearEquation | NoLinearSolution | InfiniteLinearSolutions


@dataclass(frozen=True)
class LinearSolveTraceResult:
    result: LinearSolveResult
    steps: list[Step]


def solve_linear_equation(
    lhs: Expr,
    rhs: Expr,
    variable: str,
    trace: bool = False,
) -> LinearSolveResult | LinearSolveTraceResult:
    variable = validate_target_variable(
        variable,
        error_cls=LinearFormError,
        code=LINEAR_UNSUPPORTED_SYMBOL,
    )
    steps: list[Step] = []

    lhs_form = extract_linear_form(lhs, variable)
    rhs_form = extract_linear_form(rhs, variable)

    coefficient = lhs_form.coefficient - rhs_form.coefficient
    constant = rhs_form.constant - lhs_form.constant

    isolated = Equation(
        Mul(Number(coefficient), Symbol(variable)),
        Number(constant),
    )
    steps.append(
        Step(
            rule="solve-linear-isolate",
            before=Equation(lhs, rhs),
            after=isolated,
            explanation="Move variable terms to the left and constants to the right",
        )
    )

    if coefficient == 0:
        if constant == 0:
            result: LinearSolveResult = InfiniteLinearSolutions(
                kind=LinearSolveKind.INFINITE_SOLUTIONS,
                reason="identity",
            )
            steps.append(
                Step(
                    rule="solve-linear-classify-identity",
                    before=isolated,
                    after=isolated,
                    explanation="The equation reduces to 0 = 0, so every value satisfies it",
                )
            )
        else:
            result = NoLinearSolution(
                kind=LinearSolveKind.NO_SOLUTION,
                reason="inconsistent_constants",
            )
            steps.append(
                Step(
                    rule="solve-linear-classify-inconsistent",
                    before=isolated,
                    after=isolated,
                    explanation="The equation reduces to 0 = c with c != 0, so it is inconsistent",
                )
            )
    else:
        quotient = constant / coefficient
        value = Number(
            int(quotient) if isinstance(quotient, float) and quotient.is_integer() else quotient
        )
        solved = Equation(Symbol(variable), value)
        steps.append(
            Step(
                rule="solve-linear-divide",
                before=isolated,
                after=solved,
                explanation="Divide both sides by the nonzero coefficient of the variable",
            )
        )
        result = SolvedLinearEquation(
            kind=LinearSolveKind.SOLVED,
            variable=variable,
            value=value,
        )

    if trace:
        return LinearSolveTraceResult(result=result, steps=steps)
    return result
