# BIO/NER Slice Protocol

生成时间：2026-05-28

## 1. Decision

P6 formal runs 前冻结一个 canonical structured prediction slice：

```text
WNUT17 Emerging Entities BIO/NER slice
```

理由：

- public shared-task NER dataset；
- 原始文件可从 GitHub 获取，适合 AutoDL 只能访问 GitHub 的约束；
- 数据声明清楚，许可为 CC-BY 4.0；
- 标签是 BIO-style NER 标签，BIO legality 是自然 regular-language event；
- 相比 retail fields，更容易让 reviewer 立即理解 hidden posterior conflict。

当前定位：

```text
WNUT17 BIO/NER = primary reviewer-facing structured prediction slice
retail_fields_v1 = auxiliary real-source small-field slice
```

## 2. Source

| Item | Value |
|---|---|
| Dataset | WNUT17 Emerging Entities |
| Repository | `https://github.com/leondz/emerging_entities_17` |
| Paper | Derczynski et al., WNUT 2017 Shared Task on Novel and Emerging Entity Recognition |
| License | CC-BY 4.0 according to dataset README |
| Local path | `data/raw/wnut17/` |

Frozen files:

| Split | Upstream File | Local File |
|---|---|---|
| train | `wnut17train.conll` | `data/raw/wnut17/train.conll` |
| dev | `emerging.dev.conll` | `data/raw/wnut17/dev.conll` |
| test | `emerging.test.annotated` | `data/raw/wnut17/test.conll` |

The files are small enough to track in Git after license and citation notes are
kept in this protocol and the data manifest.

Do not use `emerging.test.conll` directly for the strict BIO slice: that file
contains comma-separated multi-annotation labels. The frozen strict BIO test
file is `emerging.test.annotated`.

## 3. Event Definition

Core event:

```text
L_BIO = set of tag sequences satisfying strict BIO legality
```

Strict BIO legality:

- first tag cannot be `I-*`;
- `I-X` can only follow `B-X` or `I-X`;
- `B-X` and `O` are always allowed after any previous legal tag;
- entity type comparison is case-sensitive after normalization.

Label normalization:

```text
B-person   -> B-PERSON
I-location -> I-LOCATION
O          -> O
```

The frozen code should report both the raw label inventory and the normalized
label inventory.

## 4. Required Metrics

R5 must report:

| Metric | Meaning |
|---|---|
| `mean_p_event` | average `P_theta(L_BIO | x)` |
| `delta_p_event` | difference against B0 |
| `unconstrained_legal_rate` | legal rate of unconstrained Viterbi output |
| `constrained_decoded_legal_rate` | legal rate after BIO-constrained decoding |
| `hidden_conflict_rate` | constrained output legal but posterior event mass below threshold |
| `token_accuracy` | token-level label accuracy |
| `entity_f1` | strict entity span F1 if implemented before P6 |
| `bottom_top_error_gap` | diagnostic gap between low and high event-mass samples |

Default hidden-conflict threshold:

```text
P_theta(L_BIO | x) < 0.7
```

The threshold must be reported as a diagnostic setting, not tuned on test.

## 5. Systems

Minimum R5 systems:

| ID | Required For WNUT17 |
|---|---|
| B0 unconstrained CRF | yes |
| B1 hard-constrained decoding | yes |
| B2 labeled event training | yes |
| B3 event training + hard constraint | yes |
| B4 semi-event training | yes |
| B5 rule-feature CRF | yes |
| B6 posterior-regularization-style | yes |
| B7 WFST-style | design-if-feasible |

R5 is not allowed to claim accuracy superiority unless B4 beats or matches
strong baselines under the frozen metric table.

## 6. Smoke Before Formal Runs

Before P6:

```powershell
python scripts/data/fetch_wnut17.py
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
python -m pytest
python -m ruff check src scripts
```

Pass condition:

- all three WNUT17 files exist and match the manifest hashes;
- split stats and label inventory are emitted;
- gold labels pass strict BIO legality after normalization;
- existing tests and lint remain green.

## 7. Go / No-Go

GO to R5 implementation if:

- WNUT17 files are present locally and tracked or uploaded;
- BIO audit passes;
- current CRF implementation can handle the label vocabulary and length cap;
- B0/B1/B4 smoke can produce non-saturated event-mass values.

HOLD or downgrade if:

- WNUT17 event mass saturates near 1 under B0;
- max sequence length makes exact event computation too slow without batching changes;
- B5/B6 are not implementable with comparable tuning;
- hidden posterior conflict is absent on dev.

Downgrade route:

```text
Use WNUT17 only as a diagnostic case study, keep the main claim as posterior-event algebra and auditability, and do not claim benchmark superiority.
```
