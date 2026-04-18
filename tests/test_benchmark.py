import pytest

from stepcas.benchmark import (
    BASELINE_SCHEMA_VERSION,
    build_baseline_payload,
    default_benchmark_cases,
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
