# Scripts

Command-line wrappers and future automation entry points.

Preferred reproducible entry points:

```powershell
python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml --task r0_controlled_smoke
python scripts/analysis/audit_run_bundles.py `
  --runs-dir experiments/runs/local_checks `
  --require r0_controlled_smoke r0_semi_real_smoke r0_real_source_smoke
```

Direct module runs remain available for development, for example:

```powershell
python -m tensor_crf_jmlr.event_training.formal_validation_runner --seed-count 10
```

Keep scripts thin: parse config, call package modules, and write outputs under
`experiments/runs/` unless explicitly curating results.
