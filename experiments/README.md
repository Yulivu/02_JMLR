# Experiments

Experiment assets and retained outputs.

```text
configs/                  Hand-written experiment intent.
suites/                   Reproducible task collections.
runs/                     Ignored raw run outputs and local checks.
results/event_training/   Current retained raw results and formal_pre_paper schema.
visualizations/           Curated paper-facing figures and summary tables.
```

Executable experiment code lives under:

```text
src/tensor_crf_jmlr/event_training/
```

Thin orchestration scripts live under:

```text
scripts/
```

New experiment runs should write to `experiments/runs/`. Move only reviewed,
canonical artifacts into `experiments/results/`.
