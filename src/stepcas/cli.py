from __future__ import annotations

import argparse
import json
from typing import Iterable

from .differentiate import differentiate
from .errors import StepcasError
from .json_trace import SCHEMA_VERSION, expr_to_json, step_to_json, trace_result_to_json
from .parser import parse_expr
from .simplify import simplify
from .solve_linear import (
    InfiniteLinearSolutions,
    LinearSolveResult,
    LinearSolveTraceResult,
    NoLinearSolution,
    SolvedLinearEquation,
    solve_linear_equation,
)
from .trace import Step, TraceResult


def main() -> None:
    parser = argparse.ArgumentParser(prog="stepcas")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simplify_parser = subparsers.add_parser("simplify", help="Simplify an expression")
    simplify_parser.add_argument("expression")
    simplify_parser.add_argument("--steps", action="store_true")
    simplify_parser.add_argument("--json", action="store_true")

    diff_parser = subparsers.add_parser("diff", help="Differentiate an expression")
    diff_parser.add_argument("expression")
    diff_parser.add_argument("variable")
    diff_parser.add_argument("--steps", action="store_true")
    diff_parser.add_argument("--json", action="store_true")

    solve_parser = subparsers.add_parser("solve", help="Solve a linear equation lhs = rhs")
    solve_parser.add_argument("lhs")
    solve_parser.add_argument("rhs")
    solve_parser.add_argument("variable")
    solve_parser.add_argument("--steps", action="store_true")
    solve_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    try:
        if args.command == "simplify":
            result = simplify(parse_expr(args.expression), trace=args.steps)
        elif args.command == "diff":
            result = differentiate(parse_expr(args.expression), args.variable, trace=args.steps)
        else:
            result = solve_linear_equation(
                parse_expr(args.lhs),
                parse_expr(args.rhs),
                args.variable,
                trace=args.steps,
            )
    except Exception as error:
        if not args.json:
            raise

        print(json.dumps(_error_payload(error)))
        raise SystemExit(1) from error

    if args.json:
        print(json.dumps(_result_payload(result)))
        return

    if isinstance(result, TraceResult):
        print(f"result: {result.expr}")
        _print_steps(result.steps)
        return

    if isinstance(result, LinearSolveTraceResult):
        print(f"result: {_format_linear_result(result.result)}")
        _print_steps(result.steps)
        return

    if isinstance(result, (SolvedLinearEquation, NoLinearSolution, InfiniteLinearSolutions)):
        print(_format_linear_result(result))
        return

    print(result)


def _print_steps(steps: Iterable[Step]) -> None:
    for index, step in enumerate(steps, start=1):
        print(f"{index}. [{step.rule}] {step.before} -> {step.after}")
        if step.explanation:
            print(f"   {step.explanation}")


def _result_payload(
    result: object,
) -> dict[str, object]:
    if isinstance(result, TraceResult):
        return trace_result_to_json(result)
    if isinstance(result, LinearSolveTraceResult):
        return {
            "schema_version": SCHEMA_VERSION,
            "object": "linear_solve_trace_result",
            "data": {
                "result": _linear_result_data(result.result),
                "steps": [step_to_json(step)["data"] for step in result.steps],
            },
        }
    if isinstance(result, (SolvedLinearEquation, NoLinearSolution, InfiniteLinearSolutions)):
        return {
            "schema_version": SCHEMA_VERSION,
            "object": "linear_solve_result",
            "data": _linear_result_data(result),
        }
    return expr_to_json(result)


def _linear_result_data(result: LinearSolveResult) -> dict[str, object]:
    if isinstance(result, SolvedLinearEquation):
        return {
            "kind": result.kind.value,
            "variable": result.variable,
            "value": expr_to_json(result.value)["data"],
        }
    return {
        "kind": result.kind.value,
        "reason": result.reason,
    }


def _format_linear_result(result: LinearSolveResult) -> str:
    if isinstance(result, SolvedLinearEquation):
        return f"{result.variable} = {result.value}"
    if isinstance(result, NoLinearSolution):
        return f"no solution ({result.reason})"
    return f"infinite solutions ({result.reason})"


def _error_payload(error: Exception) -> dict[str, object]:
    if isinstance(error, StepcasError):
        return {
            "error": {
                "code": error.code,
                "message": str(error),
            }
        }
    return {
        "error": {
            "code": "internal.error",
            "message": str(error),
        }
    }


if __name__ == "__main__":
    main()
