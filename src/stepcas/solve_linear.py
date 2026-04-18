from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .expression import Equation, Expr, Mul, Number, Symbol
from .errors import LINEAR_UNSUPPORTED_SYMBOL, LinearFormError
from .linear_form import LinearForm, extract_linear_form
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


def extract_both_linear_forms(
    lhs: Expr,
    rhs: Expr,
    variable: str,
) -> tuple[LinearForm, LinearForm]:
    """Extract linear forms from both sides of an equation.

    Args:
        lhs: Left-hand side expression
        rhs: Right-hand side expression
        variable: Target variable to solve for

    Returns:
        Tuple of (lhs_form, rhs_form)

    Raises:
        LinearFormError: If extraction fails for either side
    """
    lhs_form = extract_linear_form(lhs, variable)
    rhs_form = extract_linear_form(rhs, variable)
    return lhs_form, rhs_form


def compute_isolated_form(
    lhs_form: LinearForm,
    rhs_form: LinearForm,
) -> tuple[int | float, int | float]:
    """Compute coefficient and constant after moving terms to isolate variable.

    Args:
        lhs_form: Linear form of left-hand side
        rhs_form: Linear form of right-hand side

    Returns:
        Tuple of (coefficient, constant) for the isolated form a*x = b
    """
    coefficient = lhs_form.coefficient - rhs_form.coefficient
    constant = rhs_form.constant - lhs_form.constant
    return coefficient, constant


def build_isolate_step(
    original_eq: Equation,
    isolated_eq: Equation,
) -> Step:
    """Build the isolate step that moves variable terms to left and constants to right.

    Args:
        original_eq: Original equation before isolation
        isolated_eq: The isolated equation after moving terms

    Returns:
        Step representing the isolation transformation
    """
    return Step(
        rule="solve-linear-isolate",
        before=original_eq,
        after=isolated_eq,
        explanation="Move variable terms to the left and constants to the right",
    )


def build_identity_classification_step(isolated_eq: Equation) -> Step:
    """Build the step classifying an identity (0 = 0) case.

    Args:
        isolated_eq: The isolated equation that reduced to identity

    Returns:
        Step classifying the identity case
    """
    return Step(
        rule="solve-linear-classify-identity",
        before=isolated_eq,
        after=isolated_eq,
        explanation="The equation reduces to 0 = 0, so every value satisfies it",
    )


def build_inconsistent_classification_step(isolated_eq: Equation) -> Step:
    """Build the step classifying an inconsistent (0 = c where c != 0) case.

    Args:
        isolated_eq: The isolated equation that reduced to inconsistency

    Returns:
        Step classifying the inconsistent case
    """
    return Step(
        rule="solve-linear-classify-inconsistent",
        before=isolated_eq,
        after=isolated_eq,
        explanation="The equation reduces to 0 = c with c != 0, so it is inconsistent",
    )


def build_divide_step(
    isolated_eq: Equation,
    solved_eq: Equation,
) -> Step:
    """Build the divide step solving for the variable.

    Args:
        isolated_eq: The isolated equation before division
        solved_eq: The solved equation after division

    Returns:
        Step representing the division transformation
    """
    return Step(
        rule="solve-linear-divide",
        before=isolated_eq,
        after=solved_eq,
        explanation="Divide both sides by the nonzero coefficient of the variable",
    )


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

    lhs_form, rhs_form = extract_both_linear_forms(lhs, rhs, variable)

    coefficient, constant = compute_isolated_form(lhs_form, rhs_form)

    original_eq = Equation(lhs, rhs)
    isolated_eq = Equation(
        Mul(Number(coefficient), Symbol(variable)),
        Number(constant),
    )
    steps.append(build_isolate_step(original_eq, isolated_eq))

    if coefficient == 0:
        if constant == 0:
            result: LinearSolveResult = InfiniteLinearSolutions(
                kind=LinearSolveKind.INFINITE_SOLUTIONS,
                reason="identity",
            )
            steps.append(build_identity_classification_step(isolated_eq))
        else:
            result = NoLinearSolution(
                kind=LinearSolveKind.NO_SOLUTION,
                reason="inconsistent_constants",
            )
            steps.append(build_inconsistent_classification_step(isolated_eq))
    else:
        quotient = constant / coefficient
        value = Number(
            int(quotient) if isinstance(quotient, float) and quotient.is_integer() else quotient
        )
        solved_eq = Equation(Symbol(variable), value)
        steps.append(build_divide_step(isolated_eq, solved_eq))
        result = SolvedLinearEquation(
            kind=LinearSolveKind.SOLVED,
            variable=variable,
            value=value,
        )

    if trace:
        return LinearSolveTraceResult(result=result, steps=steps)
    return result