import pytest

from stepcas.benchmark import build_baseline_payload, default_benchmark_cases, run_benchmarks


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
