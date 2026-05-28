# R5 WNUT17 Formal Protocol

生成时间：2026-05-28

## 1. Purpose

R5 的目标不是证明 WNUT17 上的 benchmark superiority，而是用一个标准 BIO/NER 数据集支撑论文主线：

```text
decoded BIO legality is not posterior BIO consistency.
```

本地检查已经显示，一个 WNUT17 配置不能同时承担所有 claim。因此 R5 正式设计冻结为 two-regime protocol：

| Regime | Role | Claim Boundary |
|---|---|---|
| R5a diagnostic stress | 展示 hard-constrained decoded output 合法，但 baseline posterior BIO mass 很低 | 支持 hidden posterior conflict，不支持 NER F1 usefulness |
| R5b task viability | 展示 WNUT17 不是 all-O toy，feature CRF 能学到非零 entity F1 | 支持 benchmark viability，不支持 hidden-conflict 强结论 |

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

B7 remains design-if-feasible. It is not required for the first AutoDL formal pass unless reviewer feedback makes it mandatory.

## 4. Frozen Local Smoke Evidence

### R5a Diagnostic Stress Smoke

Setting:

```text
word-id CRF
train_size = 25
unlabeled_size = 100
dev_size = 200
max_len = 40
epochs = 1
seed = 0
```

Key result:

| Variant | mean `P(BIO|x)` | hidden conflict | entity F1 |
|---|---:|---:|---:|
| B0 | 0.0591 | 1.0000 | 0.0000 |
| B4 | 0.3454 | 1.0000 | 0.0000 |
| B5 | 0.1635 | 1.0000 | 0.0000 |
| B6 | 0.1697 | 1.0000 | 0.0000 |

Interpretation:

```text
This regime shows posterior conflict but not NER usefulness.
```

### R5b Feature Viability Smoke

Setting:

```text
feature CRF
train_size = 500
unlabeled_size = 500
dev_size = 300
max_len = 40
epochs = 5
seeds = 0,1,2
```

3-seed averages:

| Variant | mean `P(BIO|x)` | hidden conflict | token acc | entity F1 |
|---|---:|---:|---:|---:|
| B0 | 0.9822 | 0.0067 | 0.8779 | 0.1728 |
| B4 | 0.9896 | 0.0022 | 0.8747 | 0.1541 |
| B5 | 0.9861 | 0.0056 | 0.8773 | 0.1699 |
| B6 | 0.9895 | 0.0000 | 0.8632 | 0.1298 |

Interpretation:

```text
This regime shows WNUT17 is learnable by the local CRF, but posterior BIO mass saturates.
```

## 5. Formal AutoDL Run Plan

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

Primary table:

```text
mean_p_event
delta_p_event_vs_b0
hidden_conflict_rate
constrained_legal_rate
token_accuracy
entity_f1
```

Pass condition:

- B0 hidden-conflict rate remains clearly nonzero;
- B4 raises `P(BIO|x)` over B0 on most seeds;
- entity F1 is explicitly reported as not the purpose of this regime.

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

Primary table:

```text
entity_f1
token_accuracy
mean_p_event
hidden_conflict_rate
delta_p_event_vs_b0
```

Pass condition:

- B0 entity F1 is consistently nonzero;
- posterior event mass saturation is reported honestly;
- B4 is not claimed to improve NER performance unless it actually does.

## 6. Output Contract

Formal R5 output should be curated under:

```text
experiments/results/event_training/formal_pre_paper/r5_wnut17/
```

Expected files:

```text
r5a_diagnostic_stress/runs.csv
r5a_diagnostic_stress/summary.csv
r5a_diagnostic_stress/case_studies.csv
r5a_diagnostic_stress/audit.md

r5b_feature_viability/runs.csv
r5b_feature_viability/summary.csv
r5b_feature_viability/case_studies.csv
r5b_feature_viability/audit.md

R5_RESULT_TO_CLAIM_AUDIT.md
```

Raw AutoDL outputs should first land under `experiments/runs/` and only be copied into `experiments/results/` after audit.

## 7. Go / No-Go

GO to AutoDL formal R5 only after:

- current repo is pushed to GitHub;
- `python scripts/data/verify_data.py --strict` passes on target machine;
- `python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17` passes on target machine;
- `bash scripts/hpc/run_autodl_smoke.sh` passes on target machine;
- `experiments/suites/r5_wnut17_formal_plan.yaml` dry-run is reviewed.

NO-GO if:

- target machine cannot reproduce data hashes;
- B0-B6 definitions change after seeing formal results;
- formal outputs are routed directly into curated results without audit;
- the narrative starts claiming WNUT17 NER superiority from the diagnostic stress block.
