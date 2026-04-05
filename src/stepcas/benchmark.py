from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns
from typing import Callable, Sequence, cast

from .differentiate import differentiate
from .parser import parse_expr
from .simplify import simplify
from .solve_linear import LinearSolveTraceResult, solve_linear_equation
from .trace import TraceResult


BASELINE_SCHEMA_VERSION = "stepcas.benchmark.v1"


@dataclass(frozen=True)
class BenchmarkCase:
    id: str
    operation: str
    description: str
    run: Callable[[], int]


@dataclass(frozen=True)
class BenchmarkMetrics:
    case_id: str
    operation: str
    description: str
    median_ms: float
    min_ms: float
    max_ms: float
    step_count: int


def default_benchmark_cases() -> tuple[BenchmarkCase, ...]:
    simplify_cases = (
        BenchmarkCase(
            id="simplify.canonical_like_terms",
            operation="simplify",
            description="canonical ordering and additive like-term collection",
            run=_make_simplify_runner("y + x + 2 + 3 + x + (-1)*x + 0"),
        ),
        BenchmarkCase(
            id="simplify.deep_nested",
            operation="simplify",
            description="nested add/mul flattening and constant folding",
            run=_make_simplify_runner("((x + 1) + (2 + (3 + -6))) + (4*(2*(x*3)))"),
        ),
    )

    differentiate_cases = (
        BenchmarkCase(
            id="differentiate.polynomial",
            operation="differentiate",
            description="polynomial derivative with simplification",
            run=_make_differentiate_runner("x**5 + 3*x**3 + 2*x + 9", "x"),
        ),
        BenchmarkCase(
            id="differentiate.product",
            operation="differentiate",
            description="product rule expansion and simplification",
            run=_make_differentiate_runner("(x**3 + 2*x + 5) * (x + 4)", "x"),
        ),
    )

    solve_cases = (
        BenchmarkCase(
            id="solve.linear_integer",
            operation="solve",
            description="linear solve with integer quotient",
            run=_make_solve_runner("2*x + 3", "11", "x"),
        ),
        BenchmarkCase(
            id="solve.linear_fractional",
            operation="solve",
            description="linear solve with fractional quotient",
            run=_make_solve_runner("3*x - 5", "2*x + 1", "x"),
        ),
    )

    return simplify_cases + differentiate_cases + solve_cases


def run_benchmarks(
    iterations: int = 30,
    warmups: int = 5,
    cases: Sequence[BenchmarkCase] | None = None,
) -> list[BenchmarkMetrics]:
    if iterations <= 0:
        raise ValueError("iterations must be greater than zero")
    if warmups < 0:
        raise ValueError("warmups must be zero or greater")

    selected_cases = tuple(cases) if cases is not None else default_benchmark_cases()
    metrics: list[BenchmarkMetrics] = []

    for case in selected_cases:
        for _ in range(warmups):
            case.run()

        durations_ms: list[float] = []
        step_count = 0

        for _ in range(iterations):
            start_ns = perf_counter_ns()
            step_count = case.run()
            elapsed_ms = (perf_counter_ns() - start_ns) / 1_000_000
            durations_ms.append(elapsed_ms)

        metrics.append(
            BenchmarkMetrics(
                case_id=case.id,
                operation=case.operation,
                description=case.description,
                median_ms=round(statistics.median(durations_ms), 3),
                min_ms=round(min(durations_ms), 3),
                max_ms=round(max(durations_ms), 3),
                step_count=step_count,
            )
        )

    return metrics


def build_baseline_payload(
    metrics: Sequence[BenchmarkMetrics],
    iterations: int,
    warmups: int,
) -> dict[str, object]:
    return {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "settings": {"iterations": iterations, "warmups": warmups},
        "cases": [
            {
                "id": item.case_id,
                "operation": item.operation,
                "description": item.description,
                "median_ms": item.median_ms,
                "min_ms": item.min_ms,
                "max_ms": item.max_ms,
                "step_count": item.step_count,
            }
            for item in metrics
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="stepcas-benchmark",
        description="Run reproducible simplify/differentiate/solve benchmarks",
    )
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument(
        "--baseline-out",
        type=Path,
        help="Optional JSON path for recording a benchmark baseline",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit benchmark results as JSON",
    )

    args = parser.parse_args()

    metrics = run_benchmarks(iterations=args.iterations, warmups=args.warmups)
    payload = build_baseline_payload(metrics, iterations=args.iterations, warmups=args.warmups)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_table(metrics)

    if args.baseline_out is not None:
        args.baseline_out.parent.mkdir(parents=True, exist_ok=True)
        args.baseline_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Recorded baseline: {args.baseline_out}")


def _print_table(metrics: Sequence[BenchmarkMetrics]) -> None:
    print("case                           operation      median_ms  min_ms  max_ms  steps")
    print("-----------------------------  -----------  ---------  ------  ------  -----")
    for item in metrics:
        print(
            f"{item.case_id:<29}  {item.operation:<11}"
            f"  {item.median_ms:>9.3f}  {item.min_ms:>6.3f}"
            f"  {item.max_ms:>6.3f}  {item.step_count:>5}"
        )


def _make_simplify_runner(source: str) -> Callable[[], int]:
    expr = parse_expr(source)

    def run() -> int:
        traced = cast(TraceResult, simplify(expr, trace=True))
        return len(traced.steps)

    return run


def _make_differentiate_runner(source: str, variable: str) -> Callable[[], int]:
    expr = parse_expr(source)

    def run() -> int:
        traced = cast(TraceResult, differentiate(expr, variable, trace=True))
        return len(traced.steps)

    return run


def _make_solve_runner(lhs_source: str, rhs_source: str, variable: str) -> Callable[[], int]:
    lhs = parse_expr(lhs_source)
    rhs = parse_expr(rhs_source)

    def run() -> int:
        traced = cast(LinearSolveTraceResult, solve_linear_equation(lhs, rhs, variable, trace=True))
        return len(traced.steps)

    return run


if __name__ == "__main__":
    main()
