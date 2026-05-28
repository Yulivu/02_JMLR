# R5 WNUT17 Formal Protocol

Generated: 2026-05-28

## 1. Purpose

R5 is not designed to prove WNUT17 benchmark superiority. Its role is to use a canonical BIO/NER structured prediction dataset to test the paper's main distinction:

```text
decoded BIO legality is not posterior BIO consistency.
```

Local smoke tests showed that one WNUT17 configuration cannot carry every claim. Therefore R5 is frozen as a two-regime protocol:

| Regime | Role | Claim Boundary |
|---|---|---|
| R5a diagnostic stress | show that hard-constrained decoded output can be legal while baseline posterior BIO mass is low | supports hidden posterior conflict; does not support NER F1 usefulness |
| R5b task viability | show that WNUT17 is learnable by the local feature CRF | supports benchmark viability; does not support hidden-conflict strength or B4 F1 superiority |

## 2. Frozen Data

| Item | Decision |
|---|---|
| Dataset | WNUT17 Emerging Entities |
| Local path | `data/raw/wnut17/` |
| Train | `train.conll` from upstream `wnut17train.conll` |
| Dev | `dev.conll` from upstream `emerging.dev.conll` |
| Test | `test.conll` from upstream `emerging.test.annotated` |
| Label normalization | uppercase entity type after `B-` / `I-` |
| Event | strict BIO legality |

Do not use upstream `emerging.test.conll`; it contains comma-separated multi-annotation labels.

## 3. Systems

| ID | Meaning | R5a | R5b |
|---|---|---:|---:|
| B0 | unconstrained CRF | yes | yes |
| B1 | B0 + hard-constrained decoding | yes | yes |
| B2 | labeled event training | yes | yes |
| B3 | B2 + hard-constrained decoding | yes | yes |
| B4 | semi-event training | yes | yes |
| B5 | rule-feature baseline | yes | yes |
| B6 | posterior-regularization-style baseline | yes | yes |
| B7 | WFST-style baseline | design-only for now | design-only for now |

B7 remains design-if-feasible. It is not part of the first audited R5 formal pass.

## 4. Formal AutoDL Run Settings

### R5a Diagnostic Stress Formal

```text
seeds = 0..9
train_size = 25
unlabeled_size = 100
dev_size = 300
max_len = 40
epochs = 1
systems = B0-B6
```

Primary metrics:

```text
mean_p_event
delta_p_event_vs_b0
hidden_conflict_rate
constrained_legal_rate
token_accuracy
entity_f1
```

### R5b Feature Viability Formal

```text
seeds = 0..9
train_size = 500
unlabeled_size = 500
dev_size = 500
max_len = 40
epochs = 5
systems = B0-B6
```

Primary metrics:

```text
entity_f1
token_accuracy
mean_p_event
hidden_conflict_rate
delta_p_event_vs_b0
```

## 5. Formal Result Audit

AutoDL R5 formal runs were downloaded locally and audited into:

```text
experiments/results/event_training/formal_pre_paper/r5_wnut17/
```

Curated files:

```text
r5_wnut17_audit_summary.csv
R5_RESULT_TO_CLAIM_AUDIT.md
```

Raw run folders remain under ignored `experiments/runs/` and should not be committed.

### R5a Diagnostic Stress Results

10-seed audited means:

| Variant | `P(BIO|x)` | delta vs B0 | hidden conflict | token acc | entity F1 |
|---|---:|---:|---:|---:|---:|
| B0 | 0.0566 | 0.0000 | 1.0000 | 0.8711 | 0.0000 |
| B1 | 0.0566 | 0.0000 | 1.0000 | 0.8711 | 0.0000 |
| B2 | 0.0576 | 0.0010 | 1.0000 | 0.8711 | 0.0000 |
| B3 | 0.0576 | 0.0010 | 1.0000 | 0.8711 | 0.0000 |
| B4 | 0.3389 | 0.2822 | 0.9963 | 0.8711 | 0.0000 |
| B5 | 0.1608 | 0.1042 | 1.0000 | 0.8711 | 0.0000 |
| B6 | 0.1703 | 0.1137 | 1.0000 | 0.8711 | 0.0000 |

Interpretation:

```text
R5a supports hidden posterior conflict and posterior-event training signal.
It does not support NER usefulness because entity F1 is zero.
```

### R5b Feature Viability Results

10-seed audited means:

| Variant | `P(BIO|x)` | delta vs B0 | hidden conflict | token acc | entity F1 |
|---|---:|---:|---:|---:|---:|
| B0 | 0.9824 | 0.0000 | 0.0088 | 0.8859 | 0.1660 |
| B1 | 0.9824 | 0.0000 | 0.0088 | 0.8860 | 0.1665 |
| B2 | 0.9832 | 0.0007 | 0.0078 | 0.8860 | 0.1652 |
| B3 | 0.9832 | 0.0007 | 0.0078 | 0.8861 | 0.1657 |
| B4 | 0.9865 | 0.0041 | 0.0074 | 0.8819 | 0.1522 |
| B5 | 0.9864 | 0.0040 | 0.0058 | 0.8859 | 0.1645 |
| B6 | 0.9868 | 0.0044 | 0.0060 | 0.8804 | 0.1463 |

Interpretation:

```text
R5b supports WNUT17 viability because B0 has nonzero entity F1.
It does not support B4 improving NER F1.
Posterior BIO mass is already saturated in this regime.
```

## 6. Result-To-Claim Decision

| Claim | R5 Status | Boundary |
|---|---|---|
| hidden posterior conflict exists | supported in R5a | diagnostic-only; entity F1 is zero |
| semi-event training raises posterior BIO mass | supported in R5a | event mass is saturated in R5b |
| WNUT17 is not an all-O toy | supported in R5b | F1 is modest |
| B4 improves NER F1 | not supported | do not claim task-performance improvement |
| B4 dominates B5/B6 | not supported overall | B5/B6 are competitive depending on metric/regime |

Current R5 conclusion:

```text
Use R5a for hidden posterior conflict.
Use R5b for task viability.
Do not use R5 for benchmark superiority.
```

## 7. Reproduction Commands

Dry-run:

```bash
python scripts/run_experiment_suite.py --suite experiments/suites/r5_wnut17_formal_plan.yaml --dry-run
```

Formal runs:

```bash
python scripts/exp1/run_event_training_task.py \
  --config experiments/configs/exp5/wnut17_r5a_diagnostic_formal.yaml \
  --out-dir experiments/runs/autodl_jmlr_block/r5_wnut17/r5a_diagnostic_stress

python scripts/exp1/run_event_training_task.py \
  --config experiments/configs/exp5/wnut17_r5b_feature_formal.yaml \
  --out-dir experiments/runs/autodl_jmlr_block/r5_wnut17/r5b_feature_viability
```

Local audit after FileZilla download:

```bash
python scripts/analysis/audit_run_bundles.py \
  --runs-dir experiments/runs/autodl_jmlr_block/r5_wnut17 \
  --require r5a_diagnostic_stress r5b_feature_viability

python scripts/analysis/audit_r5_wnut17_results.py \
  --runs-dir experiments/runs/autodl_jmlr_block/r5_wnut17 \
  --output-dir experiments/results/event_training/formal_pre_paper/r5_wnut17
```

## 8. Next Route After R5

R5 is a useful formal block but not the whole P6 package. The next route is:

1. keep R5 claims narrow and audited;
2. run R1/R2/R4 to test posterior event mass across controlled, semi-real, and real-source tasks;
3. run R6 to decide whether low event mass is a general diagnostic signal;
4. run R8 to answer complexity and scaling questions;
5. design B7 or explicitly justify why it remains out of scope.
