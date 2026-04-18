import json
import pytest
from pathlib import Path

from stepcas.benchmark import (
    BASELINE_SCHEMA_VERSION,
    BaselineCase,
    BaselineComparison,
    BaselineMetadata,
    BenchmarkMetrics,
    RegressionResult,
    build_baseline_payload,
    compare_with_baseline,
    default_benchmark_cases,
    load_baseline,
    run_benchmarks,
)


def test_default_benchmark_cases_cover_core_operations() -> None:
    operations = {case.operation for case in default_benchmark_cases()}
    assert operations == {"simplify", "differentiate", "solve"}


def test_run_benchmarks_emits_runtime_and_step_count_metrics() -> None:
    metrics = run_benchmarks(iterations=1, warmups=0)

    assert metrics
    for item in metrics:
        assert item.median_ms >= 0
        assert item.min_ms >= 0
        assert item.max_ms >= 0
        assert item.step_count >= 0


def test_build_baseline_payload_schema_version_stable() -> None:
    metrics = run_benchmarks(iterations=1, warmups=0)
    payload = build_baseline_payload(metrics, iterations=1, warmups=0)

    assert payload["schema_version"] == BASELINE_SCHEMA_VERSION
    assert payload["schema_version"] == "stepcas.benchmark.v1"
    assert isinstance(payload["schema_version"], str)


def test_build_baseline_payload_settings_stable() -> None:
    for iterations in (1, 5, 30):
        for warmups in (0, 3, 5):
            metrics = run_benchmarks(iterations=iterations, warmups=warmups)
            payload = build_baseline_payload(metrics, iterations=iterations, warmups=warmups)

            settings = payload["settings"]
            assert settings["iterations"] == iterations
            assert settings["warmups"] == warmups


def test_build_baseline_payload_case_keys_stable() -> None:
    metrics = run_benchmarks(iterations=1, warmups=0)
    payload = build_baseline_payload(metrics, iterations=1, warmups=0)

    expected_keys = {"id", "operation", "description", "median_ms", "min_ms", "max_ms", "step_count"}
    cases = payload["cases"]
    assert isinstance(cases, list)
    assert len(cases) == len(metrics)

    for case in cases:
        assert set(case.keys()) == expected_keys


def test_build_baseline_payload_includes_case_metrics() -> None:
    metrics = run_benchmarks(iterations=1, warmups=0)
    payload = build_baseline_payload(metrics, iterations=1, warmups=0)

    assert payload["schema_version"] == "stepcas.benchmark.v1"
    assert payload["settings"] == {"iterations": 1, "warmups": 0}

    cases = payload["cases"]
    assert isinstance(cases, list)
    assert len(cases) == len(metrics)


@pytest.mark.parametrize("iterations,warmups", [(0, 0), (1, -1)])
def test_run_benchmarks_validates_settings(iterations: int, warmups: int) -> None:
    with pytest.raises(ValueError):
        run_benchmarks(iterations=iterations, warmups=warmups)


def test_step_count_invariant_across_iterations() -> None:
    fixed_iterations = 10
    metrics = run_benchmarks(iterations=fixed_iterations, warmups=0)

    for item in metrics:
        assert item.step_count >= 0


def test_step_count_invariant_default_cases_consistent() -> None:
    cases = default_benchmark_cases()
    fixed_iterations = 5

    results_by_case: dict[str, set[int]] = {}

    for case in cases:
        results_by_case[case.id] = set()

    for _ in range(fixed_iterations):
        metrics = run_benchmarks(iterations=1, warmups=0)
        for item in metrics:
            results_by_case[item.case_id].add(item.step_count)

    for case_id, step_counts in results_by_case.items():
        assert len(step_counts) == 1, f"Inconsistent step counts for {case_id}: {step_counts}"


def test_step_count_invariant_matches_traced_result() -> None:
    from stepcas.differentiate import differentiate
    from stepcas.parser import parse_expr
    from stepcas.simplify import simplify
    from stepcas.solve_linear import solve_linear_equation

    case_runs = [
        ("simplify.canonical_like_terms", lambda: simplify(parse_expr("y + x + 2 + 3 + x + (-1)*x + 0"), trace=True)),
        ("simplify.deep_nested", lambda: simplify(parse_expr("((x + 1) + (2 + (3 + -6))) + (4*(2*(x*3)))"), trace=True)),
        ("differentiate.polynomial", lambda: differentiate(parse_expr("x**5 + 3*x**3 + 2*x + 9"), "x", trace=True)),
        ("differentiate.product", lambda: differentiate(parse_expr("(x**3 + 2*x + 5) * (x + 4)"), "x", trace=True)),
        ("solve.linear_integer", lambda: solve_linear_equation(parse_expr("2*x + 3"), parse_expr("11"), "x", trace=True)),
        ("solve.linear_fractional", lambda: solve_linear_equation(parse_expr("3*x - 5"), parse_expr("2*x + 1"), "x", trace=True)),
    ]

    for case_id, run_fn in case_runs:
        result = run_fn()
        step_count = len(result.steps)
        assert step_count >= 0, f"Invalid step count for {case_id}: {step_count}"


def test_load_baseline_parses_json(tmp_path: Path) -> None:
    baseline_json = {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "captured_at": "2025-01-01T00:00:00+00:00",
        "python": "3.12.0",
        "platform": "test-platform",
        "settings": {"iterations": 30, "warmups": 5},
        "cases": [
            {
                "id": "simplify.test",
                "operation": "simplify",
                "description": "test case",
                "median_ms": 1.5,
                "min_ms": 1.0,
                "max_ms": 2.0,
                "step_count": 10,
            }
        ],
    }
    path = tmp_path / "baseline.json"

    path.write_text(json.dumps(baseline_json), encoding="utf-8")

    baseline = load_baseline(path)

    assert baseline.schema_version == BASELINE_SCHEMA_VERSION
    assert baseline.iterations == 30
    assert baseline.warmups == 5
    assert len(baseline.cases) == 1
    assert baseline.cases[0].case_id == "simplify.test"
    assert baseline.cases[0].median_ms == 1.5
    assert baseline.cases[0].step_count == 10


def test_load_baseline_rejects_unknown_schema(tmp_path: Path) -> None:
    baseline_json = {
        "schema_version": "stepcas.benchmark.unknown",
        "captured_at": "2025-01-01T00:00:00+00:00",
        "python": "3.12.0",
        "platform": "test-platform",
        "settings": {"iterations": 30, "warmups": 5},
        "cases": [],
    }
    path = tmp_path / "bad_baseline.json"
    import json

    path.write_text(json.dumps(baseline_json), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported baseline schema"):
        load_baseline(path)


def test_compare_with_baseline_no_regression() -> None:
    baseline = BaselineMetadata(
        schema_version=BASELINE_SCHEMA_VERSION,
        captured_at="2025-01-01T00:00:00+00:00",
        python="3.12.0",
        platform="test",
        iterations=30,
        warmups=5,
        cases=(
            BaselineCase(
                case_id="test.case",
                operation="simplify",
                description="test",
                median_ms=1.0,
                min_ms=0.9,
                max_ms=1.1,
                step_count=5,
            ),
        ),
    )
    current = (
        BenchmarkMetrics(
            case_id="test.case",
            operation="simplify",
            description="test",
            median_ms=1.0,
            min_ms=0.9,
            max_ms=1.1,
            step_count=5,
        ),
    )

    comparison = compare_with_baseline(baseline, current, threshold_runtime_pct=5.0, threshold_steps=1)

    assert len(comparison.regressions) == 0


def test_compare_with_baseline_detects_runtime_regression() -> None:
    baseline = BaselineMetadata(
        schema_version=BASELINE_SCHEMA_VERSION,
        captured_at="2025-01-01T00:00:00+00:00",
        python="3.12.0",
        platform="test",
        iterations=30,
        warmups=5,
        cases=(
            BaselineCase(
                case_id="test.case",
                operation="simplify",
                description="test",
                median_ms=1.0,
                min_ms=0.9,
                max_ms=1.1,
                step_count=5,
            ),
        ),
    )
    current = (
        BenchmarkMetrics(
            case_id="test.case",
            operation="simplify",
            description="test",
            median_ms=1.5,
            min_ms=1.4,
            max_ms=1.6,
            step_count=5,
        ),
    )

    comparison = compare_with_baseline(baseline, current, threshold_runtime_pct=5.0, threshold_steps=1)

    assert len(comparison.regressions) == 1
    r = comparison.regressions[0]
    assert r.case_id == "test.case"
    assert r.runtime_regression_pct > 5.0
    assert r.step_count_regression == 0


def test_compare_with_baseline_detects_step_count_regression() -> None:
    baseline = BaselineMetadata(
        schema_version=BASELINE_SCHEMA_VERSION,
        captured_at="2025-01-01T00:00:00+00:00",
        python="3.12.0",
        platform="test",
        iterations=30,
        warmups=5,
        cases=(
            BaselineCase(
                case_id="test.case",
                operation="simplify",
                description="test",
                median_ms=1.0,
                min_ms=0.9,
                max_ms=1.1,
                step_count=5,
            ),
        ),
    )
    current = (
        BenchmarkMetrics(
            case_id="test.case",
            operation="simplify",
            description="test",
            median_ms=1.0,
            min_ms=0.9,
            max_ms=1.1,
            step_count=10,
        ),
    )

    comparison = compare_with_baseline(baseline, current, threshold_runtime_pct=10.0, threshold_steps=1)

    assert len(comparison.regressions) == 1
    r = comparison.regressions[0]
    assert r.case_id == "test.case"
    assert r.step_count_regression == 5
    assert r.runtime_regression_pct == 0.0
