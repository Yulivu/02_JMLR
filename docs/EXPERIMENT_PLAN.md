# Experiment Plan

生成时间：2026-05-26

## 1. 实验总目标

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

JMLR 需要至少一个冻结的 public / real-source formal slice。

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
| UCI Online Retail Extended | 保留 real-source small-field block，不单独承担 benchmark claim |
| Public receipt / invoice-like field dataset | JMLR formal public slice 优先候选 |
| Real field value + fixed OCR-like noise | 可作为 controlled-real bridge，不能称 fully real OCR benchmark |

## 4. 指标

Primary:

```text
mean_p_event
delta_p_event
unconstrained_legal_rate
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
| R4 | real-source small | invoice_6d, invoice_c6d, stock_5d | B0-B6 | 10 | B5/B6 grid |
| R5 | public slice | frozen public fields | B0-B6 | 10 | default + best grids |
| R6 | diagnostic full | all tasks from R1-R5 | B0, B1, B4, B5, B6 | 10 | best-dev |
| R7 | sensitivity | selected positive tasks | B0, B4 | 10 | lambda/unlabeled/rule complexity |

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
| S1 | freeze public slice data note | no |
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
| Public/real slice v1 | UCI Online Retail field slice: `invoice_6d`, `invoice_c6d`, `stock_5d` | frozen-with-scope | public real-source small-field block, not standalone benchmark claim |
| Formal run list | R0-R7 table in this document | frozen | Changes require explicit protocol update before seeing results |
| Output routing | new runs under `experiments/runs/`; curated results under `experiments/results/` | frozen | AutoDL block remains ignored until explicitly curated |

### Public / Real Slice v1

| Slice ID | Source | Fields | Rule IDs | Claim Boundary |
|---|---|---|---|---|
| `retail_fields_v1` | UCI Online Retail, local copy at `data/raw/online_retail.xlsx` | `InvoiceNo`, `StockCode` | `invoice_6d`, `invoice_c6d`, `stock_5d` | real-source small-field evidence only; not a general OCR or benchmark-superiority claim |

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

## 10. Go / No-Go

Proceed to AutoDL/HPC engineering only if:

```text
R0 local smoke passes;
public slice decision is frozen;
schema output is valid;
run-list is accepted before seeing final results.
```

Do not proceed if:

```text
baseline definitions are moving;
public slice is not frozen;
metrics are not fixed;
result-to-claim mapping is unclear.
```

## 11. JMLR Decision Standard

Maintain JMLR route only if:

- fresh proof-check does not fail;
- B4 posterior event mass is stable across controlled/semi-real/real-source;
- B5/B6 do not fully dominate B4;
- public/real-source slice gives at least partial positive evidence;
- diagnostic bottom/top separation is clear.

Downgrade if:

- B5/B6 are clearly stronger: position as posterior-event algebra/auditability;
- public slice fails: controlled/semi-real theory paper route only;
- diagnostic fails: remove diagnostic claim;
- proof-check fails: stop paper route until theory repair.
