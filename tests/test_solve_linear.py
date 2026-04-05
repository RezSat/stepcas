from stepcas import (
    InfiniteLinearSolutions,
    LinearSolveKind,
    NoLinearSolution,
    SolvedLinearEquation,
    parse_expr,
    simplify,
    solve_linear_equation,
)
from stepcas.errors import LinearFormError


def test_solve_linear_equation_returns_unique_solution() -> None:
    result = solve_linear_equation(simplify(parse_expr("2*x + 4")), simplify(parse_expr("10")), "x")

    assert isinstance(result, SolvedLinearEquation)
    assert result.kind is LinearSolveKind.SOLVED
    assert result.variable == "x"
    assert result.value.value == 3


def test_solve_linear_equation_returns_no_solution_for_inconsistent_case() -> None:
    result = solve_linear_equation(
        simplify(parse_expr("x + 1")), simplify(parse_expr("x + 2")), "x"
    )

    assert isinstance(result, NoLinearSolution)
    assert result.kind is LinearSolveKind.NO_SOLUTION
    assert result.reason == "inconsistent_constants"


def test_solve_linear_equation_returns_infinite_solutions_for_identity() -> None:
    result = solve_linear_equation(
        simplify(parse_expr("x + 1")), simplify(parse_expr("x + 1")), "x"
    )

    assert isinstance(result, InfiniteLinearSolutions)
    assert result.kind is LinearSolveKind.INFINITE_SOLUTIONS
    assert result.reason == "identity"


def test_solve_linear_equation_handles_zero_coefficient_inconsistent_case() -> None:
    result = solve_linear_equation(simplify(parse_expr("0*x + 3")), simplify(parse_expr("5")), "x")

    assert isinstance(result, NoLinearSolution)
    assert result.kind is LinearSolveKind.NO_SOLUTION


def test_solve_linear_equation_handles_zero_coefficient_identity_case() -> None:
    result = solve_linear_equation(simplify(parse_expr("0*x + 3")), simplify(parse_expr("3")), "x")

    assert isinstance(result, InfiniteLinearSolutions)
    assert result.kind is LinearSolveKind.INFINITE_SOLUTIONS


def test_solve_linear_equation_trace_includes_isolate_and_divide_steps() -> None:
    traced = solve_linear_equation(
        simplify(parse_expr("2*x + 4")),
        simplify(parse_expr("10")),
        "x",
        trace=True,
    )

    assert [step.rule for step in traced.steps] == ["solve-linear-isolate", "solve-linear-divide"]


def test_solve_linear_equation_trace_classifies_zero_coefficient_inconsistency() -> None:
    traced = solve_linear_equation(
        simplify(parse_expr("x + 1")),
        simplify(parse_expr("x + 2")),
        "x",
        trace=True,
    )

    assert [step.rule for step in traced.steps] == [
        "solve-linear-isolate",
        "solve-linear-classify-inconsistent",
    ]


def test_solve_linear_equation_trace_classifies_zero_coefficient_identity() -> None:
    traced = solve_linear_equation(
        simplify(parse_expr("x + 1")),
        simplify(parse_expr("x + 1")),
        "x",
        trace=True,
    )

    assert [step.rule for step in traced.steps] == [
        "solve-linear-isolate",
        "solve-linear-classify-identity",
    ]


def test_solve_linear_equation_isolates_terms_from_both_sides() -> None:
    result = solve_linear_equation(
        simplify(parse_expr("3*x + 1")), simplify(parse_expr("x + 5")), "x"
    )

    assert isinstance(result, SolvedLinearEquation)
    assert result.value.value == 2


def test_solve_linear_equation_divide_preserves_non_integer_quotient() -> None:
    result = solve_linear_equation(simplify(parse_expr("2*x")), simplify(parse_expr("1")), "x")

    assert isinstance(result, SolvedLinearEquation)
    assert result.value.value == 0.5


def test_solve_linear_equation_rejects_non_linear_inputs() -> None:
    try:
        solve_linear_equation(simplify(parse_expr("x**2")), simplify(parse_expr("3")), "x")
    except LinearFormError:
        return
    raise AssertionError("Expected LinearFormError for nonlinear solve input")


def test_solve_linear_equation_rejects_unsupported_symbol_inputs() -> None:
    try:
        solve_linear_equation(simplify(parse_expr("x + y")), simplify(parse_expr("3")), "x")
    except LinearFormError:
        return
    raise AssertionError("Expected LinearFormError for unsupported symbol solve input")
