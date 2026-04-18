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


@dataclass(frozen=True)
class BaselineCase:
    case_id: str
    operation: str
    description: str
    median_ms: float
    min_ms: float
    max_ms: float
    step_count: int


@dataclass(frozen=True)
class BaselineMetadata:
    schema_version: str
    captured_at: str
    python: str
    platform: str
    iterations: int
    warmups: int
    cases: tuple[BaselineCase, ...]


@dataclass(frozen=True)
class RegressionResult:
    case_id: str
    baseline_median_ms: float
    current_median_ms: float
    baseline_step_count: int
    current_step_count: int
    runtime_regression_pct: float
    step_count_regression: int


@dataclass(frozen=True)
class BaselineComparison:
    baseline: BaselineMetadata
    current: Sequence[BenchmarkMetrics]
    regressions: tuple[RegressionResult, ...]


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


def load_baseline(path: Path) -> BaselineMetadata:
    data = json.loads(path.read_text(encoding="utf-8"))
    schema = data.get("schema_version", "")
    if schema != BASELINE_SCHEMA_VERSION:
        raise ValueError(f"Unsupported baseline schema: {schema}")
    settings = data.get("settings", {})
    cases_data = data.get("cases", [])
    baseline_cases = tuple(
        BaselineCase(
            case_id=c["id"],
            operation=c["operation"],
            description=c["description"],
            median_ms=c["median_ms"],
            min_ms=c["min_ms"],
            max_ms=c["max_ms"],
            step_count=c["step_count"],
        )
        for c in cases_data
    )
    return BaselineMetadata(
        schema_version=schema,
        captured_at=data.get("captured_at", ""),
        python=data.get("python", ""),
        platform=data.get("platform", ""),
        iterations=settings.get("iterations", 0),
        warmups=settings.get("warmups", 0),
        cases=baseline_cases,
    )


def compare_with_baseline(
    baseline: BaselineMetadata,
    current: Sequence[BenchmarkMetrics],
    threshold_runtime_pct: float = 0.0,
    threshold_steps: int = 0,
) -> BaselineComparison:
    baseline_by_id = {c.case_id: c for c in baseline.cases}
    regressions: list[RegressionResult] = []

    for cur in current:
        base = baseline_by_id.get(cur.case_id)
        if base is None:
            continue

        runtime_regression_pct = ((cur.median_ms - base.median_ms) / base.median_ms) * 100
        step_count_regression = cur.step_count - base.step_count

        exceeds_runtime = runtime_regression_pct > threshold_runtime_pct
        exceeds_steps = step_count_regression > threshold_steps

        if exceeds_runtime or exceeds_steps:
            regressions.append(
                RegressionResult(
                    case_id=cur.case_id,
                    baseline_median_ms=base.median_ms,
                    current_median_ms=cur.median_ms,
                    baseline_step_count=base.step_count,
                    current_step_count=cur.step_count,
                    runtime_regression_pct=round(runtime_regression_pct, 2),
                    step_count_regression=step_count_regression,
                )
            )

    return BaselineComparison(
        baseline=baseline,
        current=current,
        regressions=tuple(regressions),
    )


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
        "--baseline-in",
        type=Path,
        help="Path to baseline JSON for comparison",
    )
    parser.add_argument(
        "--threshold-runtime-pct",
        type=float,
        default=0.0,
        help="Acceptable runtime regression percentage threshold (absolute, default 0.0)",
    )
    parser.add_argument(
        "--threshold-steps",
        type=int,
        default=0,
        help="Acceptable step-count regression threshold (absolute, default 0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit benchmark results as JSON",
    )

    args = parser.parse_args()

    metrics = run_benchmarks(iterations=args.iterations, warmups=args.warmups)
    payload = build_baseline_payload(metrics, iterations=args.iterations, warmups=args.warmups)

    baseline = None
    if args.baseline_in is not None:
        baseline = load_baseline(args.baseline_in)

    if baseline is not None:
        comparison = compare_with_baseline(
            baseline,
            metrics,
            threshold_runtime_pct=args.threshold_runtime_pct,
            threshold_steps=args.threshold_steps,
        )
        if args.json:
            output_payload = {
                "comparison": {
                    "baseline_schema": comparison.baseline.schema_version,
                    "baseline_captured_at": comparison.baseline.captured_at,
                    "regressions": [
                        {
                            "case_id": r.case_id,
                            "baseline_median_ms": r.baseline_median_ms,
                            "current_median_ms": r.current_median_ms,
                            "baseline_step_count": r.baseline_step_count,
                            "current_step_count": r.current_step_count,
                            "runtime_regression_pct": r.runtime_regression_pct,
                            "step_count_regression": r.step_count_regression,
                        }
                        for r in comparison.regressions
                    ],
                },
                "current": payload,
            }
            print(json.dumps(output_payload, indent=2))
        else:
            _print_table(metrics)
            _print_comparison(comparison)

        if comparison.regressions:
            print("\nREGRESSION DETECTED")
            print(f"  {len(comparison.regressions)} case(s) exceeded threshold(s)")
            sys.exit(1)
        else:
            print("\nNo regressions detected")
    else:
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


def _print_comparison(comparison: BaselineComparison) -> None:
    if not comparison.regressions:
        return
    print("\nRegressions:")
    print("case                           baseline_ms  current_ms  runtime_pct  base_steps  cur_steps  step_diff")
    print("-----------------------------  -----------  ----------  -----------  ---------  ---------  ---------")
    for r in comparison.regressions:
        print(
            f"{r.case_id:<29}  {r.baseline_median_ms:>11.3f}  {r.current_median_ms:>10.3f}"
            f"  {r.runtime_regression_pct:>11.2f}  {r.baseline_step_count:>9}  {r.current_step_count:>9}"
            f"  {r.step_count_regression:>9}"
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
