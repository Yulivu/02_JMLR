# AutoDL / HPC Runbook

Status: P5 engineering preparation.

This runbook is only for environment validation and smoke execution. It must not
change the frozen P3 protocol and must not be treated as formal JMLR evidence.

This runbook adapts the general `docs/runbooks/GITHUB_AUTODL_FILEZILLA_WORKFLOW.md`
process to this repository.

## Project Values

```text
PROJECT: 02_jmlr
GitHub SSH URL: git@github.com:Yulivu/02_JMLR.git
branch: master
server repo dir: /root/autodl-tmp/02_JMLR
local repo: C:\Users\debuf\Desktop\research_projects\2_Tensor_CRF_JMLR
```

## Preconditions

- P3/P4 passed locally.
- Repository is synced to GitHub.
- `data/raw/online_retail.xlsx` and `data/raw/wnut17/*.conll` are present on the machine.
- Python 3.10+ is available.
- No formal experiment should be launched until the smoke suite passes.

## Server Bootstrap

Create an AutoDL machine-specific SSH key. Do not copy a local private key to
AutoDL.

```bash
mkdir -p /root/.ssh /root/autodl-tmp
chmod 700 /root/.ssh

ssh-keygen -t ed25519 \
  -C "autodl_02_jmlr_$(date +%Y%m%d_%H%M)" \
  -f /root/.ssh/id_ed25519_02_jmlr \
  -N ""

cat > /root/.ssh/config <<'EOF'
Host github.com
  HostName github.com
  User git
  IdentityFile /root/.ssh/id_ed25519_02_jmlr
  IdentitiesOnly yes
EOF

chmod 600 /root/.ssh/config /root/.ssh/id_ed25519_02_jmlr
chmod 644 /root/.ssh/id_ed25519_02_jmlr.pub
cat /root/.ssh/id_ed25519_02_jmlr.pub
```

Add the printed public key to GitHub as a deploy key:

```text
Yulivu/02_JMLR -> Settings -> Deploy keys -> Add deploy key
```

Usually do not enable write access. Then test:

```bash
ssh -T git@github.com
```

Clone or update:

```bash
cd /root/autodl-tmp
git clone git@github.com:Yulivu/02_JMLR.git
cd /root/autodl-tmp/02_JMLR
git checkout master
git rev-parse --short HEAD
git status --short
```

If the repo already exists:

```bash
cd /root/autodl-tmp/02_JMLR
git pull --ff-only
git rev-parse --short HEAD
```

## Data Policy

AutoDL is treated as offline except for GitHub access.

Current P5 smoke and BIO/NER gate data are already tracked in this repo:

```text
data/raw/online_retail.xlsx
data/raw/wnut17/train.conll
data/raw/wnut17/dev.conll
data/raw/wnut17/test.conll
```

After cloning from GitHub, verify it:

```bash
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
```

If a future dataset is too large for GitHub, upload the original file with
FileZilla/SFTP into `data/raw/`, then add or update `data/DATA_MANIFEST.md`.
Do not depend on runtime downloads from UCI/Kaggle/other external websites on
AutoDL.

## First Command On Machine

```bash
bash scripts/autodl_setup.sh
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

## R5 WNUT17 Formal Plan

After P5 target-machine smoke passes, review the frozen R5 protocol:

```text
docs/protocols/R5_WNUT17_FORMAL_PROTOCOL.md
```

Dry-run the formal plan first:

```bash
python scripts/run_experiment_suite.py --suite experiments/suites/r5_wnut17_formal_plan.yaml --dry-run
```

The formal-plan suite is disabled by default. Do not enable or run it until the
user explicitly approves formal R5 execution on AutoDL.

## FileZilla Paths

Current required data is tracked in Git, so no FileZilla upload is needed for
P5 smoke or R5 WNUT17 first formal pass.

If a future dataset is too large for GitHub, upload only the missing data files
to the expected path, for example:

```text
server: /root/autodl-tmp/02_JMLR/data/raw/
server: /root/autodl-tmp/02_JMLR/data/processed/
```

Do not upload the whole local repository over the server clone, and do not
upload `.git/`.

Download result folders after runs:

```text
server: /root/autodl-tmp/02_JMLR/experiments/runs/autodl_smoke/
local:  C:\Users\debuf\Desktop\research_projects\2_Tensor_CRF_JMLR\experiments\runs\autodl_smoke\
```

For later R5 formal runs:

```text
server: /root/autodl-tmp/02_JMLR/experiments/runs/autodl_jmlr_block/r5_wnut17/
local:  C:\Users\debuf\Desktop\research_projects\2_Tensor_CRF_JMLR\experiments\runs\autodl_jmlr_block\r5_wnut17\
```

After downloading results, audit locally before copying anything into
`experiments/results/`.

## P6 R1/R2/R4 Formal Block

After R5 is audited, the next AutoDL block is controlled/semi-real/real-source
formal evidence:

```text
experiments/suites/p6_r1_r2_r4_formal_plan.yaml
```

Run only after pulling the commit that contains this suite.

Dry-run:

```bash
python scripts/run_experiment_suite.py \
  --suite experiments/suites/p6_r1_r2_r4_formal_plan.yaml \
  --dry-run
```

Formal execution:

```bash
python scripts/run_experiment_suite.py \
  --suite experiments/suites/p6_r1_r2_r4_formal_plan.yaml
```

Equivalent one-by-one commands:

```bash
python scripts/exp1/run_event_training_task.py \
  --config experiments/configs/exp1/r1_controlled_formal.yaml \
  --out-dir experiments/runs/autodl_jmlr_block/p6_r1_r2_r4/r1_controlled_formal

python scripts/exp1/run_event_training_task.py \
  --config experiments/configs/exp2/r2_semi_real_formal.yaml \
  --out-dir experiments/runs/autodl_jmlr_block/p6_r1_r2_r4/r2_semi_real_formal

python scripts/exp1/run_event_training_task.py \
  --config experiments/configs/exp3/r4_real_source_formal.yaml \
  --out-dir experiments/runs/autodl_jmlr_block/p6_r1_r2_r4/r4_real_source_formal
```

Bundle audit:

```bash
python scripts/analysis/audit_run_bundles.py \
  --runs-dir experiments/runs/autodl_jmlr_block/p6_r1_r2_r4 \
  --require r1_controlled_formal r2_semi_real_formal r4_real_source_formal
```

Download with FileZilla after completion:

```text
server: /root/autodl-tmp/02_JMLR/experiments/runs/autodl_jmlr_block/p6_r1_r2_r4/
local:  C:\Users\debuf\Desktop\research_projects\2_Tensor_CRF_JMLR\experiments\runs\autodl_jmlr_block\p6_r1_r2_r4\
```

Do not copy these raw outputs into `experiments/results/` until a local
result-to-claim audit script has been run.

## P6 R6 Diagnostic Formal Block

After R1/R2/R4 are downloaded and audited, the next AutoDL block is R6a
field-style posterior event diagnostic:

```text
experiments/suites/p6_r6_diagnostic_formal_plan.yaml
```

Dry-run:

```bash
python scripts/run_experiment_suite.py \
  --suite experiments/suites/p6_r6_diagnostic_formal_plan.yaml \
  --dry-run
```

Formal execution:

```bash
python scripts/run_experiment_suite.py \
  --suite experiments/suites/p6_r6_diagnostic_formal_plan.yaml
```

Bundle audit:

```bash
python scripts/analysis/audit_run_bundles.py \
  --runs-dir experiments/runs/autodl_jmlr_block/p6_r6_diagnostic \
  --require r6a_field_diagnostic_formal
```

Download with FileZilla after completion:

```text
server: /root/autodl-tmp/02_JMLR/experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/
local:  C:\Users\debuf\Desktop\research_projects\2_Tensor_CRF_JMLR\experiments\runs\autodl_jmlr_block\p6_r6_diagnostic\
```

Scope boundary:

```text
R6a tests whether low P_theta(L|x) is a sample-level diagnostic signal on
semi-real and real-source field-style tasks. WNUT hidden-conflict evidence is
handled by R5a; R6a should not be used to claim benchmark superiority.
```

## P6 R8 Complexity Formal Block

After R6a is downloaded and audited, run R8 complexity scaling:

```text
experiments/suites/p6_r8_complexity_formal_plan.yaml
```

Dry-run:

```bash
python scripts/run_experiment_suite.py \
  --suite experiments/suites/p6_r8_complexity_formal_plan.yaml \
  --dry-run
```

Formal execution:

```bash
python scripts/run_experiment_suite.py \
  --suite experiments/suites/p6_r8_complexity_formal_plan.yaml
```

Bundle audit:

```bash
python scripts/analysis/audit_run_bundles.py \
  --runs-dir experiments/runs/autodl_jmlr_block/p6_r8_complexity \
  --require r8_complexity_scaling_formal
```

Download with FileZilla after completion:

```text
server: /root/autodl-tmp/02_JMLR/experiments/runs/autodl_jmlr_block/p6_r8_complexity/
local:  C:\Users\debuf\Desktop\research_projects\2_Tensor_CRF_JMLR\experiments\runs\autodl_jmlr_block\p6_r8_complexity\
```

Scope boundary:

```text
R8 measures reference CPU product-transfer scaling with sequence length, label
count, DFA states, and context order. It must not be described as an optimized
runtime benchmark, GPU result, arbitrary low-rank result, or superiority claim.
```

## Do Not

- Do not write smoke output into `experiments/results/`.
- Do not edit `docs/protocols/EXPERIMENT_PLAN.md` after seeing smoke results unless making
  an explicit protocol revision.
- Do not start R1-R8 formal runs during P5.
- Do not run `r5_wnut17_formal_plan.yaml` before P5 target-machine smoke passes.
- Do not interpret P5 smoke metrics as paper evidence.
- Do not use FileZilla to overwrite the whole repo or sync `.git/`.
- Do not hand-edit server code for formal experiments; change locally, commit,
  push, then `git pull --ff-only` on AutoDL.
