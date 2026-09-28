# Research results protocol

This project records evidence by phase and module under `results/`.

## Directory layout

```text
results/
  phase-1/
    m1-inventory/
    m2-calibration/
    m3-baselines/
```

Each module directory contains:

- `summary.md`: status, scope, current conclusion, and next gate.
- `findings.md`: observations, quality checks, failures, and unresolved questions.
- `notes.md`: decisions, commands, assumptions, and limitations.
- `metrics/`: CSV or JSON values when a metric is computed.
- `figures/`: PNG or SVG plots when a metric or graph is computed.

## Metric evidence rule

Never report a metric without saving its source values and a figure. The summary must identify the data manifest or product version, split, units, code commit, and figure filename. Figures should have readable labels, a caption in the summary, and a deterministic generation command. If a module has no metric or graph, keep the result as text and do not create a fake plot.

## Scientific record rule

Record failed quality gates as findings. Keep raw archives and large intermediate cubes outside this directory and outside Git. A module is complete only when its summary states what was verified, what remains unverified, and the next gate.
