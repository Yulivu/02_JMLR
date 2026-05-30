#!/usr/bin/env bash
set -euo pipefail

SUITE="experiments/suites/jmlr_cpu_upgrade_formal_plan.yaml"
RUN_DIR="experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade"
SUITE_JOBS="${JMLR_SUITE_JOBS:-3}"

export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export NUMEXPR_NUM_THREADS="${NUMEXPR_NUM_THREADS:-1}"

python -m pip install -e ".[dev]"
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
python scripts/data/fetch_conll2000_chunking.py

python scripts/hpc/preflight_autodl.py \
  --suite "${SUITE}" \
  --data-file data/raw/conll2000_chunking/train.txt \
  --report experiments/runs/preflight/jmlr_cpu_upgrade_preflight.json

python scripts/run_experiment_suite.py --suite "${SUITE}" --dry-run
python scripts/run_experiment_suite.py --suite "${SUITE}" --jobs "${SUITE_JOBS}"

python scripts/analysis/audit_run_bundles.py \
  --runs-dir "${RUN_DIR}" \
  --require \
    public_conll2000_chunking_formal \
    b7_constrained_product_formal \
    r7_sensitivity_formal

python -m pytest
python -m ruff check src scripts
