# Benchmarks

`stepcas` includes a reproducible benchmark harness for core symbolic workloads:

- `simplify`
- `differentiate`
- `solve`

Each workload reports runtime metrics (`median_ms`, `min_ms`, `max_ms`) and
`step_count`, so regressions are visible both in speed and rewrite growth.

## Run benchmarks

```bash
stepcas-benchmark
```

Optional controls:

```bash
stepcas-benchmark --iterations 50 --warmups 10
stepcas-benchmark --json
```

## Record a baseline

Use `--baseline-out` to persist a JSON baseline snapshot:

```bash
stepcas-benchmark --iterations 50 --warmups 10 --baseline-out benchmarks/baseline.json
```

The baseline file includes:

- benchmark schema version,
- capture timestamp,
- Python/platform metadata,
- run settings,
- per-case runtime and step-count metrics.

## Reproducibility notes

For meaningful comparisons, keep these fixed between runs:

1. Python version
2. machine/OS environment
3. benchmark settings (`iterations`, `warmups`)
4. workload set (default benchmark cases)

Because runtime can vary from background load, use median runtime for trend
tracking and use `step_count` as the deterministic structural signal.
