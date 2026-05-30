# JMLR CPU Upgrade Runbook

Updated: 2026-05-30

This runbook prepares a CPU-only machine for the remaining upgrade runs:

- public CoNLL2000 full run with public-case uncertainty fields;
- B7 constrained-product formal run;
- R7 lambda/rule sensitivity formal run.

No GPU is required. Do not rent a GPU for this block.

## Machine Choice

Use a CPU instance with:

```text
Python >= 3.10
RAM >= 16 GB recommended
Disk >= 20 GB free
Network access to GitHub for clone and CoNLL2000 mirror fetch
```

The code is CPU-only; `torch.cuda.is_available()` may be false.

For a multi-core CPU machine, the one-command script runs the three suite tasks
concurrently by default (`JMLR_SUITE_JOBS=3`) and lets R7 sensitivity use all
available CPU cores for its seed/rule/lambda worker pool (`workers: 0` in the
formal config). BLAS/PyTorch intra-op thread counts default to 1 to avoid
oversubscription. Override only if the machine is shared:

```bash
JMLR_SUITE_JOBS=2 bash scripts/hpc/run_jmlr_cpu_upgrade_formal.sh
```

## Suite

```text
experiments/suites/jmlr_cpu_upgrade_formal_plan.yaml
```

It runs:

| Task | Output bundle |
|---|---|
| `public_conll2000_chunking_formal` | `experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/public_conll2000_chunking_formal` |
| `b7_constrained_product_formal` | `experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/b7_constrained_product_formal` |
| `r7_sensitivity_formal` | `experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/r7_sensitivity_formal` |

## One-Command Run

After cloning/pulling the target commit on the CPU machine:

```bash
bash scripts/hpc/run_jmlr_cpu_upgrade_formal.sh
```

The script:

1. installs the repo in editable mode with dev dependencies;
2. verifies tracked WNUT17/retail data;
3. fetches CoNLL2000 chunking text files with official-host attempts and GitHub mirror fallback;
4. runs preflight on the CPU formal suite;
5. dry-runs the suite;
6. runs the suite;
7. audits run bundles;
8. runs tests and lint.

## Manual Commands

```bash
python -m pip install -e ".[dev]"
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
python scripts/data/fetch_conll2000_chunking.py

python scripts/hpc/preflight_autodl.py \
  --suite experiments/suites/jmlr_cpu_upgrade_formal_plan.yaml \
  --data-file data/raw/conll2000_chunking/train.txt \
  --report experiments/runs/preflight/jmlr_cpu_upgrade_preflight.json

python scripts/run_experiment_suite.py \
  --suite experiments/suites/jmlr_cpu_upgrade_formal_plan.yaml \
  --dry-run

python scripts/run_experiment_suite.py \
  --suite experiments/suites/jmlr_cpu_upgrade_formal_plan.yaml \
  --jobs 3
```

Audit:

```bash
python scripts/analysis/audit_run_bundles.py \
  --runs-dir experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade \
  --require \
    public_conll2000_chunking_formal \
    b7_constrained_product_formal \
    r7_sensitivity_formal

python -m pytest
python -m ruff check src scripts
```

## Download Results

After completion, download:

```text
server: /root/autodl-tmp/02_JMLR/experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/
local:  C:\Users\debuf\Desktop\research_projects\2_Tensor_CRF_JMLR\experiments\runs\autodl_jmlr_block\jmlr_cpu_upgrade\
```

Do not copy raw bundles into `experiments/results/` directly. Run local result-to-claim audits first.

## Claim Boundary

These runs are for evidence closure, not superiority claims. In particular:

```text
public CoNLL2000: report event-mass movement, B7 behavior, uncertainty fields, and task-metric boundary.
B7: report legal decoded output and task metric; do not call it a full WFST system.
R7: report lambda/rule sensitivity, including unhelpful or saturated cases.
```
