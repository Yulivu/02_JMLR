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
