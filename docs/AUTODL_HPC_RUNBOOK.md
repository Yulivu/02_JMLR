# AutoDL / HPC Runbook

Status: P5 engineering preparation.

This runbook is only for environment validation and smoke execution. It must not
change the frozen P3 protocol and must not be treated as formal JMLR evidence.

## Preconditions

- P3/P4 passed locally.
- Repository is synced to GitHub.
- `data/raw/online_retail.xlsx` is present on the machine.
- Python 3.10+ is available.
- No formal experiment should be launched until the smoke suite passes.

## Data Policy

AutoDL is treated as offline except for GitHub access.

Current P5 smoke data is already tracked in this repo:

```text
data/raw/online_retail.xlsx
```

After cloning from GitHub, verify it:

```bash
python scripts/data/verify_data.py --strict
```

If a future dataset is too large for GitHub, upload the original file with
FileZilla/SFTP into `data/raw/`, then add or update `data/DATA_MANIFEST.md`.
Do not depend on runtime downloads from UCI/Kaggle/other external websites on
AutoDL.

## First Command On Machine

```bash
python -m pip install -e ".[dev]"
python scripts/data/verify_data.py --strict
```

## Preflight

```bash
python scripts/hpc/preflight_autodl.py \
  --suite experiments/suites/autodl_smoke.yaml \
  --report experiments/runs/preflight/autodl_preflight.json
```

Optional stricter CUDA check:

```bash
python scripts/hpc/preflight_autodl.py \
  --suite experiments/suites/autodl_smoke.yaml \
  --strict-cuda
```

## Smoke Run

Dry run:

```bash
python scripts/run_experiment_suite.py --suite experiments/suites/autodl_smoke.yaml --dry-run
```

Full smoke:

```bash
bash scripts/hpc/run_autodl_smoke.sh
```

Expected output bundles:

```text
experiments/runs/autodl_smoke/r0_controlled_smoke/
experiments/runs/autodl_smoke/r0_semi_real_smoke/
experiments/runs/autodl_smoke/r0_real_source_smoke/
```

## Pass Criteria

```bash
python scripts/analysis/audit_run_bundles.py \
  --runs-dir experiments/runs/autodl_smoke \
  --require r0_controlled_smoke r0_semi_real_smoke r0_real_source_smoke
python -m pytest
python -m ruff check src scripts
```

P5 passes only when preflight, dry-run, smoke run, bundle audit, tests, and lint
all pass on the AutoDL/HPC machine.

## Do Not

- Do not write smoke output into `experiments/results/`.
- Do not edit `docs/EXPERIMENT_PLAN.md` after seeing smoke results unless making
  an explicit protocol revision.
- Do not start R1-R7 formal runs during P5.
- Do not interpret P5 smoke metrics as paper evidence.
