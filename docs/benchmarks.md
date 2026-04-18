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

## Compare against baseline

Use `--baseline-in` to load a baseline and compare current runs:

```bash
stepcas-benchmark --baseline-in benchmarks/baseline.json
```

## Threshold-based regression detection

Set thresholds to detect regressions:

```bash
stepcas-benchmark \
  --baseline-in benchmarks/baseline.json \
  --threshold-runtime-pct 10.0 \
  --threshold-steps 5
```

- `--threshold-runtime-pct`: Acceptable runtime increase percentage (default 0.0). Only slowdowns count.
- `--threshold-steps`: Acceptable step-count increase (default 0). Only step-count growth counts.

When a regression is detected, the CLI exits with code 1 and prints a table
showing which cases exceeded the thresholds.

Use `--json` to get structured output including both baseline comparison
data and current metrics.

## Reproducibility notes

For meaningful comparisons, keep these fixed between runs:

1. Python version
2. machine/OS environment
3. benchmark settings (`iterations`, `warmups`)
4. workload set (default benchmark cases)

Because runtime can vary from background load, use median runtime for trend
tracking and use `step_count` as the deterministic structural signal.
