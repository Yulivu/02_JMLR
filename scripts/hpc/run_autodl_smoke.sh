#!/usr/bin/env bash
set -euo pipefail

python -m pip install -e ".[dev]"
python scripts/hpc/preflight_autodl.py \
  --suite experiments/suites/autodl_smoke.yaml \
  --report experiments/runs/preflight/autodl_preflight.json
python scripts/run_experiment_suite.py --suite experiments/suites/autodl_smoke.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/autodl_smoke.yaml
python scripts/analysis/audit_run_bundles.py \
  --runs-dir experiments/runs/autodl_smoke \
  --require r0_controlled_smoke r0_semi_real_smoke r0_real_source_smoke
python -m pytest
python -m ruff check src scripts
