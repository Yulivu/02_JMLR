#!/usr/bin/env bash
set -euo pipefail

SUITE="experiments/suites/jmlr_cpu_upgrade_formal_plan.yaml"
RUN_DIR="experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade"

python -m pip install -e ".[dev]"
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
python scripts/data/fetch_conll2000_chunking.py

python scripts/hpc/preflight_autodl.py \
  --suite "${SUITE}" \
  --data-file data/raw/conll2000_chunking/train.txt \
  --report experiments/runs/preflight/jmlr_cpu_upgrade_preflight.json

python scripts/run_experiment_suite.py --suite "${SUITE}" --dry-run
python scripts/run_experiment_suite.py --suite "${SUITE}"

python scripts/analysis/audit_run_bundles.py \
  --runs-dir "${RUN_DIR}" \
  --require \
    public_conll2000_chunking_formal \
    b7_constrained_product_formal \
    r7_sensitivity_formal

python -m pytest
python -m ruff check src scripts
