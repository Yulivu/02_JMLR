# Experiment Suites

Suites select reproducible tasks from `experiments/configs/`.

Use dry run first:

```powershell
python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml --dry-run
```

Available suites:

| Suite | Purpose |
|---|---|
| `current_repro.yaml` | Local P4 R0 smoke suite |
| `autodl_smoke.yaml` | P5 AutoDL/HPC engineering smoke suite |
| `r5_wnut17_smoke.yaml` | WNUT17 BIO/NER R5 local stress smoke |
| `r5_wnut17_viability.yaml` | WNUT17 feature-based nonzero-F1 viability check |
| `r5_wnut17_formal_plan.yaml` | Frozen R5 two-regime AutoDL formal plan, disabled by default |
| `p6_r1_r2_r4_formal_plan.yaml` | Formal controlled, semi-real, and real-source blocks |
| `p6_r6_diagnostic_formal_plan.yaml` | Formal R6a field diagnostic block |
| `p6_r8_complexity_formal_plan.yaml` | Formal R8 complexity scaling block |
