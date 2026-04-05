from __future__ import annotations

import argparse
from typing import Iterable

from .differentiate import differentiate
from .parser import parse_expr
from .simplify import simplify
from .trace import Step, TraceResult


def main() -> None:
    parser = argparse.ArgumentParser(prog="stepcas")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simplify_parser = subparsers.add_parser("simplify", help="Simplify an expression")
    simplify_parser.add_argument("expression")
    simplify_parser.add_argument("--steps", action="store_true")

    diff_parser = subparsers.add_parser("diff", help="Differentiate an expression")
    diff_parser.add_argument("expression")
    diff_parser.add_argument("variable")
    diff_parser.add_argument("--steps", action="store_true")

    args = parser.parse_args()
    if args.command == "simplify":
        result = simplify(parse_expr(args.expression), trace=args.steps)
    else:
        result = differentiate(parse_expr(args.expression), args.variable, trace=args.steps)

    if isinstance(result, TraceResult):
        print(f"result: {result.expr}")
        _print_steps(result.steps)
        return

    print(result)


def _print_steps(steps: Iterable[Step]) -> None:
    for index, step in enumerate(steps, start=1):
        print(f"{index}. [{step.rule}] {step.before} -> {step.after}")
        if step.explanation:
            print(f"   {step.explanation}")


if __name__ == "__main__":
    main()
