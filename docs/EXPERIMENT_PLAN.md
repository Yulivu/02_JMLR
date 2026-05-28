# Experiment Plan

生成时间：2026-05-26

## 1. 实验总目标

Paper identity:

```text
decoded output legality is not posterior consistency.
```

实验必须围绕这个问题组织：

```text
hard-constrained decoding 可以修最终输出；
P_theta(L|x) 暴露模型后验里是否仍有大量非法结构概率质量。
```

实验只服务三个主张：

| Claim | 含义 | 需要证据 |
|---|---|---|
| C1 Computation | `P_theta(L|x)` 是明确可计算的 posterior event | theory package + sanity tests |
| C2 Training | event loss 能稳定提高 posterior event mass | controlled / semi-real / real-source |
| C3 Diagnostic | low `P_theta(L|x)` 能定位错误或 hidden conflict | bottom/top risk + correlation/AUC |

不把实验目标设成：

```text
证明 B4 全面优于所有 baseline；
证明真实 benchmark superiority；
证明任意 CRF/DFA 都低秩；
证明 hard constraint 没用。
```

## 2. 方法与 Baseline

主方法：

```text
B4_semi_event_lambda:
CRF supervised NLL + lambda * event loss on labeled/unlabeled inputs
event loss = -log P_theta(L|x)
```

Baseline / ablation：

| ID | 名称 | 作用 | JMLR 必须 |
|---|---|---|---|
| B0 | unconstrained CRF | 原始 CRF baseline | yes |
| B1 | B0 + hard-constrained decoding | 区分“修输出”和“改后验” | yes |
| B2 | labeled event training | 检查 event term 加在 labeled 上是否有效 | yes |
| B3 | event training + hard constraint | 检查 event training 和 hard decoding 是否互补 | yes |
| B4 | semi-event training | 主方法 | yes |
| B5 | rule-feature CRF | 对照“把规则当局部 feature” | yes |
| B6 | posterior-regularization-style | 对照“后验约束训练” | yes |
| B7 | WFST-style constrained objective/eval | reviewer pressure baseline | design required, run if feasible |

Hyperparameter grids:

```text
event lambda in {0.05, 0.1, 0.2, 0.5, 1.0}
rule-feature weight in {0.2, 0.5, 0.8, 1.2, 2.0}
PR tau in {0.6, 0.7, 0.8, 0.9}
PR eta in {0.2, 0.5, 1.0, 2.0}
```

## 3. 数据与任务

### Canonical BIO / NER Structured Benchmark

用途：作为 reviewer-facing canonical structured prediction block。

核心问题：

```text
constrained decoding 后输出可以是合法 BIO，
但 baseline CRF posterior 是否仍然有大量非法 BIO probability mass？
event training 是否能提高 P_theta(BIO-legal|x)，减少 hidden posterior conflict？
```

这是 P6 前最高优先级补强项。相比 invoice/stock 字段，BIO/NER 更标准、更容易让 reviewer 理解，也更直接地区分本项目和 constrained decoding。

冻结选择：

```text
WNUT17 Emerging Entities BIO/NER slice
```

协议入口：

```text
docs/BIO_NER_SLICE_PROTOCOL.md
```

本地数据：

```text
data/raw/wnut17/train.conll
data/raw/wnut17/dev.conll
data/raw/wnut17/test.conll
```

注意：test split 使用 upstream `emerging.test.annotated`；不要使用 `emerging.test.conll`，因为后者包含逗号分隔多标注标签，不是严格单标签 BIO。

纳入标准：

- public / citable source；
- BIO 或 BIOES 标签；
- 能构造 CRF-style sequence labeling setup；
- BIO legality 是明确 regular language；
- 能报告 unconstrained prediction、constrained decoding、posterior BIO-legal mass；
- 能构造 hidden-conflict cases：decoded output legal but `P_theta(BIO-legal|x)` low；
- 能跑 B0-B6，B7/WFST-style if feasible。

P6 前必须冻结：

```text
dataset source
label scheme
split
preprocessing
label vocabulary
BIO legality DFA
max length / batching policy
```

当前已冻结：

| Item | Decision |
|---|---|
| dataset source | WNUT17 Emerging Entities from `leondz/emerging_entities_17` |
| license/data note | CC-BY 4.0 per upstream README; citation required |
| local path | `data/raw/wnut17/` |
| label scheme | strict single-label BIO after type uppercase normalization |
| split | upstream train/dev/test annotated |
| BIO data audit | train/dev/test gold labels pass strict BIO legality |

### WNUT17 R5 Viability Update

本地验证显示 WNUT17 需要拆成两个 regime，而不是用一个配置同时承担所有 claim：

| Regime | Setting | What It Shows | Limitation |
|---|---|---|---|
| diagnostic stress | word-id tiny CRF, 25 labeled, 1 epoch | constrained outputs can be legal while `P(BIO|x)` is very low; B4 raises posterior event mass | entity F1 remains 0, so no NER usefulness claim |
| task viability | feature CRF, 500 labeled, 5 epochs, 3 seeds | B0 learns nonzero entity F1 around 0.17 | `P(BIO|x)` saturates around 0.98, so hidden conflict is weak |

Feature viability 3-seed averages:

| Variant | mean `P(BIO|x)` | delta vs B0 | hidden conflict | token acc | entity F1 |
|---|---:|---:|---:|---:|---:|
| B0 | 0.9822 | 0.0000 | 0.0067 | 0.8779 | 0.1728 |
| B4 | 0.9896 | 0.0074 | 0.0022 | 0.8747 | 0.1541 |
| B5 | 0.9861 | 0.0039 | 0.0056 | 0.8773 | 0.1699 |
| B6 | 0.9895 | 0.0073 | 0.0000 | 0.8632 | 0.1298 |

Decision:

```text
Do not launch formal AutoDL R5 yet.
First freeze R5 as a two-regime design: diagnostic stress + task viability.
```

仍需在 R5 implementation 前完成：

| Item | Remaining |
|---|---|
| max length / batching policy | local smoke cap currently `max_len=40`; formal cap still needs timing/coverage decision |
| B0-B6 implementation | local stress smoke exists for B0-B6; formal multi-seed/grid package still pending |
| B7 WFST-style | design-if-feasible |
| hidden conflict dev smoke | stress smoke passed: B0 `mean_p_event=0.0591`, constrained legal rate `1.0`, hidden conflict rate `1.0`; B4 raises `mean_p_event` to `0.3454`; B5/B6 also raise event mass but less than B4 |

### Controlled Format

用途：验证机制稳定，不是单任务偶然。

```text
DATE
DDDLL
LL-DDD
LLDDD
```

建议：

```text
labeled_size = 25
unlabeled_size = 100
dev_size = 300
seeds = 20 first, expand to 50 if variance is high
```

### Semi-Real Format Fields

用途：接近表单/OCR 字段，但仍可控。

```text
amount        -> $DD.DD
date          -> DDDD-DD-DD
dose          -> DDDmg
product_code  -> LL-DDD
```

建议：

```text
labeled_size in {5, 10, 25, 50}
unlabeled_size in {0, 25, 100, 500}
seeds = 10 first, 20 if JMLR route remains positive
```

### Real-Source Small Fields

当前来源：

```text
UCI Online Retail
InvoiceNo -> invoice_6d, invoice_c6d
StockCode -> stock_5d
```

注意：

```text
invoice_6d / stock_5d legal rate 容易饱和；
主解释必须使用 posterior mass、exact/char、diagnostic，不只看 legal rate。
```

### Public / Real Formal Slice

JMLR 需要至少一个冻结的 canonical structured prediction slice。优先级现在高于 retail small-field。

纳入标准：

- public source；
- regular language 明确；
- B0 `P_theta(L|x)` 不应接近 1，或明确作为 saturation diagnostic；
- 能构造 labeled/unlabeled/dev/test；
- label alphabet 稳定；
- noise channel 固定；
- 能跑 B0-B6；
- 每个字段有 rule id、source note、split seed。

候选：

| Candidate | 结论 |
|---|---|
| BIO/NER public benchmark | P6 formal public slice 最高优先级 |
| UCI Online Retail Extended | 保留 real-source small-field auxiliary block，不单独承担 benchmark claim |
| Public receipt / invoice-like field dataset | 可作为 second public slice，而非替代 BIO/NER |
| Real field value + fixed OCR-like noise | 可作为 controlled-real bridge，不能称 fully real OCR benchmark |

## 4. 指标

Primary:

```text
mean_p_event
delta_p_event
unconstrained_legal_rate
constrained_decoded_legal_rate
hidden_conflict_rate
char_accuracy
exact_sequence_accuracy
bottom/top exact error gap
```

Secondary:

```text
mean_nll
hidden_conflict_rate
low_p_event_rate
diagnostic correlation / AUC
lambda-task tradeoff
```

主表必须报告：

```text
mean
95% CI
up-rate over seeds
delta vs B0
best-dev and default setting
negative/tradeoff cases
```

## 5. Formal Run List

| Run ID | Stage | Tasks | Systems | Seeds | Grid |
|---|---|---|---|---:|---|
| R0 | local smoke | one task per block | B0, B4 | 1 | default |
| R1 | controlled robustness | DATE, DDDLL, LL-DDD, LLDDD | B0-B4 | 20 | lambda grid |
| R2 | semi-real main | amount, date, dose, product_code | B0-B6 | 10 | B5/B6 grid |
| R3 | semi-real low-label | amount, product_code | B0, B4, best B5, best B6 | 10 | labeled/unlabeled grid |
| R4 | real-source small auxiliary | invoice_6d, invoice_c6d, stock_5d | B0-B6 | 10 | B5/B6 grid |
| R5 | canonical BIO/NER public slice | frozen BIO/NER sequence labeling task | B0-B7 if feasible | 10 | default + best grids |
| R6 | diagnostic full | all tasks from R1-R5 | B0, B1, B4, B5, B6 | 10 | best-dev |
| R7 | sensitivity | selected positive tasks | B0, B4 | 10 | lambda/unlabeled/rule complexity |
| R8 | complexity scaling | selected controlled + BIO/NER lengths/rules | B0, B4 | 3 | sequence length / DFA states / batch size |

Default settings:

```text
epochs = 5 initially
lr = 0.08 unless dev instability appears
labeled_size = 25
unlabeled_size = 100
dev_size >= 300
test_size >= 500 when available
```

## 6. Output Contract

Formal results must enter:

```text
experiments/results/event_training/formal_pre_paper/
```

Each block should expose:

```text
runs.csv
runs.json
summary.csv
summary.json
case_studies.csv
audit.md
fairness_audit.md when B5/B6 are involved
```

AutoDL results, if launched, must enter:

```text
experiments/results/event_training/formal_pre_paper/autodl_jmlr_block/
```

## 7. Execution Order

| Stage | Action | AutoDL/HPC |
|---|---|---|
| S0 | freeze experiment protocol | no |
| S1 | freeze canonical BIO/NER slice data note | no; done for WNUT17 |
| S2 | freeze config table and run list | no |
| S3 | local CPU smoke, one seed per block | no |
| S4 | audit smoke schema | no |
| S5 | then adapt runner/device/config | yes |
| S6 | formal AutoDL runs | yes |
| S7 | result-to-claim audit | no |

Hard rule:

```text
Do not handle AutoDL/HPC engineering before S0-S4 pass.
```

## 8. P3/P4 Gate Snapshot

冻结日期：2026-05-27

### P3 Frozen Decisions

| Item | Frozen Decision | Status | Notes |
|---|---|---|---|
| Target claims | C1 computation, C2 training signal, C3 diagnostic signal | frozen | 不主张 benchmark superiority |
| Baseline set | B0-B6 required; B7 WFST-style design-if-feasible | frozen | B5/B6 是 reviewer pressure baseline |
| Primary metrics | `mean_p_event`, delta, legal rate, char/exact accuracy, diagnostic bottom/top gap | frozen | 主表必须有 mean/CI/up-rate/negative cases |
| Controlled tasks | DATE, DDDLL, LL-DDD, LLDDD | frozen | R0 smoke uses LLDDD |
| Semi-real tasks | amount, date, dose, product_code | frozen | R0 smoke uses product_code |
| Retail small-field slice | UCI Online Retail field slice: `invoice_6d`, `invoice_c6d`, `stock_5d` | frozen-with-scope | auxiliary real-source small-field block, not standalone benchmark claim |
| Canonical structured slice | BIO/NER public benchmark | required-before-P6 | must be frozen before formal runs |
| Formal run list | R0-R8 table in this document | revised-frozen | BIO/NER and complexity rows added before formal results |
| Output routing | new runs under `experiments/runs/`; curated results under `experiments/results/` | frozen | AutoDL block remains ignored until explicitly curated |

### Public / Real Slice v1

| Slice ID | Source | Fields | Rule IDs | Claim Boundary |
|---|---|---|---|---|
| `retail_fields_v1` | UCI Online Retail, local copy at `data/raw/online_retail.xlsx` | `InvoiceNo`, `StockCode` | `invoice_6d`, `invoice_c6d`, `stock_5d` | real-source small-field evidence only; not a general OCR or benchmark-superiority claim |
| `wnut17_bio` | WNUT17 Emerging Entities, local copy at `data/raw/wnut17/` | NER BIO sequence labels | `bio_legal` | primary reviewer-facing structured prediction slice; no superiority claim until R5 formal results |

### Canonical BIO/NER Slice Gate

| Item | Requirement |
|---|---|
| role | primary reviewer-facing structured prediction benchmark |
| required before | P6 formal runs |
| core event | BIO legality as regular language |
| central case study | constrained decoded output legal, but baseline `P_theta(BIO-legal|x)` low |
| must report | posterior legal mass, constrained legal output, hidden conflict, task metrics |
| failure mode | if unavailable, downgrade JMLR empirical route before spending formal-run budget |

Status:

```text
data gate frozen and locally audited; R5 B0-B6 one-seed stress smoke passed; formal multi-seed/grid implementation still pending.
```

### P4 R0 Smoke Suite

| R0 Task | Block | Config | Output Bundle | Required |
|---|---|---|---|---|
| `r0_controlled_smoke` | controlled format | `experiments/configs/exp1/formal_validation_smoke.yaml` | `experiments/runs/local_checks/r0_controlled_smoke/` | yes |
| `r0_semi_real_smoke` | semi-real format | `experiments/configs/exp2/semi_real_quick.yaml` | `experiments/runs/local_checks/r0_semi_real_smoke/` | yes |
| `r0_real_source_smoke` | real-source small-field | `experiments/configs/exp3/real_source_quick.yaml` | `experiments/runs/local_checks/r0_real_source_smoke/` | yes |

Acceptance commands:

```powershell
python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml
python scripts/analysis/audit_run_bundles.py `
  --runs-dir experiments/runs/local_checks `
  --require r0_controlled_smoke r0_semi_real_smoke r0_real_source_smoke
python -m pytest
python -m ruff check src scripts
```

P4 passes only if all required R0 bundles exist, each bundle has `resolved_config.yaml`, `run_metadata.json`, `summary.md`, and runner-produced run/summary artifacts, and pytest/ruff remain green.

### P4 Validation Record

验证日期：2026-05-27

| Check | Command / Target | Status |
|---|---|---|
| R0 dry-run | `python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml --dry-run` | PASS |
| R0 full smoke | `python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml` | PASS |
| Bundle schema | `scripts/analysis/audit_run_bundles.py` over all three R0 bundles | PASS |
| Tests | `python -m pytest` | PASS, 44 tests |
| Lint | `python -m ruff check src scripts` | PASS |

Conclusion:

```text
P3/P4 gate passed locally. The project may proceed to P5 AutoDL/HPC engineering,
but must not change the frozen protocol without an explicit protocol revision.
```

## 9. P5 AutoDL/HPC Engineering Plan

P5 is an engineering gate, not a formal evidence run.

| Item | Artifact | Pass Condition |
|---|---|---|
| AutoDL/HPC runbook | `docs/AUTODL_HPC_RUNBOOK.md` | commands are explicit and do not alter P3 protocol |
| Environment preflight | `scripts/hpc/preflight_autodl.py` | package imports, data file, suite structure, and output routing pass |
| Smoke suite | `experiments/suites/autodl_smoke.yaml` | routes only to `experiments/runs/autodl_smoke/` |
| Smoke launcher | `scripts/hpc/run_autodl_smoke.sh` | runs preflight, dry-run, smoke suite, bundle audit, pytest, ruff |
| Result protection | `.gitignore` + suite output paths | no smoke output enters `experiments/results/` |

P5 is complete only after the same checks pass on the AutoDL/HPC machine. Local
validation of these scripts is necessary but not sufficient to mark P5 done.

P5 must not launch R1-R8 formal runs. P5 also must not treat retail smoke as a substitute for BIO/NER slice selection.

## 10. Go / No-Go

Proceed to AutoDL/HPC engineering only if:

```text
R0 local smoke passes;
retail auxiliary slice decision is frozen;
schema output is valid;
run-list is accepted before seeing final results.
```

Do not proceed if:

```text
baseline definitions are moving;
BIO/NER canonical slice plan is unclear before P6;
metrics are not fixed;
result-to-claim mapping is unclear.
```

## 11. JMLR Decision Standard

Maintain JMLR route only if:

- fresh proof-check does not fail;
- canonical BIO/NER slice demonstrates hidden posterior conflict;
- B4 posterior event mass is stable across controlled/semi-real/real-source;
- B5/B6 do not fully dominate B4;
- retail small-field slice gives at least auxiliary positive evidence;
- diagnostic bottom/top separation is clear.

Downgrade if:

- B5/B6 are clearly stronger: position as posterior-event algebra/auditability;
- BIO/NER slice fails or is unavailable: downgrade JMLR empirical route before formal runs;
- retail slice fails: keep it auxiliary or remove real-source claim;
- diagnostic fails: remove diagnostic claim;
- proof-check fails: stop paper route until theory repair.
