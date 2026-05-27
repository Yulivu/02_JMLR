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

Data gates:

```powershell
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
```

Only refresh WNUT17 from GitHub when intentionally updating the frozen data
gate:

```powershell
python scripts/data/fetch_wnut17.py
```

WNUT17 R5 local smoke:

```powershell
python scripts/run_experiment_suite.py --suite experiments/suites/r5_wnut17_smoke.yaml
```

Keep scripts thin: parse config, call package modules, and write outputs under
`experiments/runs/` unless explicitly curating results.

AutoDL/HPC smoke entry points:

```powershell
python scripts/hpc/preflight_autodl.py --suite experiments/suites/autodl_smoke.yaml
python scripts/run_experiment_suite.py --suite experiments/suites/autodl_smoke.yaml --dry-run
```

On Linux/AutoDL:

```bash
bash scripts/hpc/run_autodl_smoke.sh
```
