# AI Review Packet

生成时间：2026-05-27

用途：把项目 idea、理论对象、已有证据、实验路线、当前阶段和主要风险合并成一个文件，供外部 AI / researcher reviewer 快速审核。

请 reviewer 重点判断：

1. 这个 idea 是否有足够独立性；
2. 当前 claim 是否过强或过弱；
3. P6 formal run design 是否足够支撑 JMLR 路线；
4. baseline / diagnostic / BIO-NER slice 是否还有明显缺口；
5. 如果结果不理想，论文定位应该如何降级。

## 1. One-Sentence Idea

本项目研究：

```text
Tensorized Regular-Language Posterior Algebra for CRFs
```

最简解释：

```text
不要只看 CRF 最终输出是否满足规则；
而是计算 CRF 整个后验分布里，有多少概率质量真的落在规则语言 L 中。
```

核心信号：

```text
P_theta(L | x)
```

直观含义：

```text
模型内部到底有多少概率相信这个 regular-language rule？
```

## 2. Motivation

传统 hard-constrained decoding 只能保证最后输出合法，但可能掩盖模型内部冲突。例如模型最高分答案被修成合法输出，但模型后验的大部分概率质量仍然在非法结构上。

本项目把规则从“输出后的过滤器”变成“后验分布里的可计算事件”：

| 用途 | 含义 |
|---|---|
| Audit | 最高分输出合法但 `P_theta(L|x)` 很低，说明模型并不真正相信规则 |
| Training | 用 `-log P_theta(L|x)` 作为 event loss，推动后验质量进入合法集合 |
| Diagnostic | 低 `P_theta(L|x)` 样本可能是错误或 hidden conflict |
| Theory | 用 product automaton transfer 精确表示 event mass；rank/MPO 仅作 appendix support |

## 3. Relation To uMPS

一句话：

```text
uMPS 告诉我们，正则语言可以成为概率模型里的可计算事件；
我们把这个视角接到 CRF 条件后验上，研究 P_theta(y in L | x)。
```

| uMPS | 本项目 |
|---|---|
| 生成式序列模型 | 条件 CRF 后验 |
| 问生成字符串是否落入 regex event | 问标签后验是否相信 regular-language rule |
| 关注 u-MPS 张量网络模型 | 关注 CRF posterior event mass |
| `P(s in R)` | `P_theta(y in L | x)` |

## 4. Theory Object

固定有限标签集、有限长度、输入 `x`、CRF-style score、regular language `L`，以及识别 `L` 的 complete DFA。

核心对象：

```text
Z_theta(x)       = total CRF posterior normalizer
Z_{theta,L}(x)   = mass of sequences accepted by L
P_theta(L | x)   = Z_{theta,L}(x) / Z_theta(x)
```

Product automaton idea:

```text
CRF local context state × DFA state
```

每条 accepted product path 对应一条满足规则的 label sequence；路径权重对应 CRF sequence score 的 exponentiated weight。因此 summing accepted paths gives event mass.

## 5. Theory Package And Guardrails

| ID | Statement | Status | Scope |
|---|---|---|---|
| T0 | finite posterior setup is well-defined | provable | finite labels/length/score |
| T1 | product automaton transfer computes event mass exactly | provable | complete DFA, fixed convention |
| T2 | event transfer has conditional nonnegative MPO rank membership | appendix / optional | needs explicit rank assumptions |
| T3 | positive-cone transfer approximation controls event mass multiplicatively | provable | nonnegative matrices and boundary vectors |
| C1 | posterior probability control | conditional | needs numerator and denominator control |
| C2 | log event/posterior control | conditional | needs strict positivity |

Allowed claims:

- `P_theta(L|x)` is a well-defined CRF posterior event signal;
- product automaton transfer computes event mass;
- event loss can be studied as a training signal;
- low event mass can be tested as diagnostic signal;
- conditional rank membership under explicit assumptions.

Forbidden claims:

- JMLR-ready already;
- benchmark superiority already;
- arbitrary CRF/DFA/regular language low-rank advantage;
- hard constraints are useless;
- current tests prove real-world usefulness.

## 6. Current Stage

Current status:

```text
P5 in progress
AutoDL/HPC engineering prepared locally
WNUT17 BIO/NER data gate frozen locally
WNUT17 B0-B6 local stress smoke passed
target-machine smoke pending
```

Roadmap:

| Phase | Goal | Status | Evidence / Artifact | Remaining |
|---|---|---|---|---|
| P0 | problem definition | done | mainline fixed | none |
| P1 | theory object closed loop | mostly done | posterior algebra, DFA/product-transfer tests | fresh proof-check |
| P2 | local mechanism validation | mostly done | controlled/semi-real/real-source probes | not benchmark evidence |
| P3 | experiment protocol freeze | revised-frozen | frozen protocol plus reviewer-route update; WNUT17 BIO/NER data gate and B0-B6 stress smoke | R5 multi-seed/grid before P6 |
| P4 | local R0 smoke | done | controlled/semi-real/real-source smoke + schema audit | smoke only |
| P5 | AutoDL/HPC engineering | in progress | preflight, runbook, autodl smoke suite, WNUT17 data manifest | target-machine smoke |
| P6 | formal runs | not started | R1-R8 planned; R5 data source frozen; B0-B6 smoke positive | WNUT17 multi-seed/grid formal R5 runs |
| P7 | result-to-claim audit | not started | claim/evidence matrix draft | update after P6 |
| P8 | pre-writing freeze | not started | docs/code foundation | final figures/tables/limits |

## 7. Existing Evidence

Existing evidence supports entering formal validation. It does not yet support final paper claims.

| Evidence | Positive Signal | Boundary |
|---|---|---|
| Core algebra tests | finite posterior algebra and product transfer align | small finite sanity only |
| Event CRF tests | event probability and gradients work in tiny CRF setting | not benchmark |
| Gradient mechanism | illegal BIO gradients are penalized | not training evidence alone |
| Controlled format probes | event training raises posterior event mass on format tasks | limited seeds, incomplete baselines |
| Semi-real field probes | amount/date/dose/product_code show positive posterior-mass trends | B5/B6 competitive |
| Real-source small fields | invoice/stock fields show positive posterior mass and some exact/char gains | small-field, not general OCR |
| Diagnostic probes | bottom `P_theta(L|x)` samples have higher error than top samples | representative tasks only |

Important local numbers:

| Block | Task | Delta `P_theta(L|x)` / Risk Signal |
|---|---|---:|
| semi-real | amount | +0.1422 |
| semi-real | date | +0.1953 |
| semi-real | dose | +0.0608 |
| semi-real | product_code | +0.1642 |
| real-source | invoice_6d | +0.0573 |
| real-source | invoice_c6d | +0.0661 |
| real-source | stock_5d | +0.0543 |
| diagnostic | bottom vs top event mass | bottom samples have much higher error |

Current supported claim:

```text
P_theta(L|x) is a computable, auditable, trainable CRF posterior event signal.
```

Current unsupported claim:

```text
B4 is empirically superior to all baselines on real benchmarks.
```

## 8. Baselines

| ID | Name | Purpose | Required |
|---|---|---|---|
| B0 | unconstrained CRF | original baseline | yes |
| B1 | B0 + hard-constrained decoding | distinguish output repair from posterior training | yes |
| B2 | labeled event training | event term on labeled samples | yes |
| B3 | event training + hard constraint | complementarity with hard decoding | yes |
| B4 | semi-event training | main method | yes |
| B5 | rule-feature CRF | rule-as-feature baseline | yes |
| B6 | posterior-regularization-style | posterior constraint baseline | yes |
| B7 | WFST-style constrained objective/eval | reviewer pressure baseline | design if feasible |

Reviewer pressure point:

```text
If B5/B6 dominate B4, the paper should pivot from empirical superiority
to posterior-event algebra + auditability + diagnostic value.
```

## 9. P6 Formal Run Design

Formal runs are R1-R8. R0 is only smoke and already passed locally.

| Run ID | Stage | Tasks | Systems | Seeds | Grid |
|---|---|---|---|---:|---|
| R1 | controlled robustness | DATE, DDDLL, LL-DDD, LLDDD | B0-B4 | 20 | lambda grid |
| R2 | semi-real main | amount, date, dose, product_code | B0-B6 | 10 | B5/B6 grid |
| R3 | semi-real low-label | amount, product_code | B0, B4, best B5, best B6 | 10 | labeled/unlabeled grid |
| R4 | real-source small auxiliary | invoice_6d, invoice_c6d, stock_5d | B0-B6 | 10 | B5/B6 grid |
| R5 | canonical BIO/NER public slice | frozen BIO/NER task | B0-B7 if feasible | 10 | default + best grids |
| R6 | diagnostic full | all tasks from R1-R5 | B0, B1, B4, B5, B6 | 10 | best-dev |
| R7 | sensitivity | selected positive tasks | B0, B4 | 10 | lambda/unlabeled/rule complexity |
| R8 | complexity scaling | selected controlled + BIO/NER lengths/rules | B0, B4 | 3 | length / DFA states / batch size |

Primary metrics:

```text
mean_p_event
delta_p_event
unconstrained_legal_rate
char_accuracy
exact_sequence_accuracy
bottom/top exact error gap
```

Secondary metrics:

```text
mean_nll
hidden_conflict_rate
low_p_event_rate
diagnostic correlation / AUC
lambda-task tradeoff
```

Decision standard:

- maintain JMLR route if B4 posterior event mass is stable across controlled/semi-real/real-source;
- B5/B6 do not fully dominate B4;
- public/real slice gives at least partial positive evidence;
- diagnostic bottom/top separation is clear;
- fresh proof-check does not fail.

## 10. Public / Real Slice

Current auxiliary frozen v1:

| Slice ID | Source | Fields | Rule IDs | Claim Boundary |
|---|---|---|---|---|
| `retail_fields_v1` | UCI Online Retail local copy | `InvoiceNo`, `StockCode` | `invoice_6d`, `invoice_c6d`, `stock_5d` | auxiliary real-source small-field evidence only, not primary benchmark |

BIO/NER data gate now frozen before P6:

```text
canonical BIO/NER public structured prediction slice = WNUT17 Emerging Entities
```

The BIO/NER slice should demonstrate hidden posterior conflict:

```text
constrained decoded output legal, but baseline P_theta(BIO-legal|x) low.
```

Local data artifacts:

```text
docs/BIO_NER_SLICE_PROTOCOL.md
data/raw/wnut17/train.conll
data/raw/wnut17/dev.conll
data/raw/wnut17/test.conll
```

Important data note: `test.conll` is copied from upstream `emerging.test.annotated`; upstream `emerging.test.conll` is not used because it contains comma-separated multi-annotation labels.

Local stress-smoke signal:

| System | `mean_p_event` | constrained legal rate | hidden conflict rate | token acc | entity F1 |
|---|---:|---:|---:|---:|---:|
| B0 | 0.0591 | 1.0000 | 1.0000 | 0.8731 | 0.0000 |
| B2 | 0.0603 | 1.0000 | 1.0000 | 0.8731 | 0.0000 |
| B4 | 0.3454 | 1.0000 | 1.0000 | 0.8731 | 0.0000 |
| B5 | 0.1635 | 1.0000 | 1.0000 | 0.8731 | 0.0000 |
| B6 | 0.1697 | 1.0000 | 1.0000 | 0.8731 | 0.0000 |

Interpretation: WNUT17 can expose posterior BIO inconsistency under a low-resource stress setting, and semi-event training moves posterior mass upward more than the current B5/B6 smoke baselines. It does not yet show entity-level task usefulness.

Data policy:

- AutoDL/HPC is treated as offline except for GitHub access.
- Current required data is tracked in repo: `data/raw/online_retail.xlsx`.
- Data hash is recorded in `data/DATA_MANIFEST.md`.
- Future large data must be uploaded manually to `data/raw/` and added to manifest.

## 11. P5 AutoDL/HPC Status

P5 is engineering only, not evidence.

Artifacts:

| Artifact | Purpose |
|---|---|
| `docs/AUTODL_HPC_RUNBOOK.md` | target-machine runbook |
| `experiments/suites/autodl_smoke.yaml` | AutoDL smoke suite |
| `scripts/hpc/preflight_autodl.py` | environment/data/suite preflight |
| `scripts/hpc/run_autodl_smoke.sh` | preflight + dry-run + smoke + audit + tests |
| `scripts/data/verify_data.py` | offline data verification |

P5 passes only if the target AutoDL/HPC machine passes:

```bash
python scripts/data/verify_data.py --strict
python scripts/hpc/preflight_autodl.py --suite experiments/suites/autodl_smoke.yaml
bash scripts/hpc/run_autodl_smoke.sh
```

## 12. Key Risks

| Risk | Impact | Mitigation |
|---|---|---|
| B5/B6 dominate B4 | cannot claim empirical superiority | pivot to algebra/auditability/diagnostic |
| missing BIO/NER implementation | reviewer may see task as engineered field extraction | implement WNUT17 R5 runner and hidden-conflict smoke before P6 |
| public slice too weak | JMLR empirical strength weaker | downgrade before spending formal-run budget |
| B7 not implemented | reviewer may ask about WFST/constrained structured methods | design if feasible, or clearly scope |
| diagnostic weak | remove or downgrade diagnostic claim | do full R6 before writing |
| proof-check fails | theory section blocked | repair theory before paper writing |
| current CRF too tiny | reviewer may see toy-only evidence | strengthen public/semi-real formal runs |

## 13. Questions For Reviewer

1. Is the core idea meaningfully distinct from hard-constrained decoding, rule features, and posterior regularization?
2. Is `P_theta(L|x)` as posterior event mass a useful enough object for a methods/theory paper?
3. Are C1/C2/C3 the right claims, or should one be removed before formal runs?
4. Are B0-B6 sufficient, or is B7/WFST-style baseline mandatory?
5. Is R1-R8 strong enough for JMLR if results are positive?
6. Is WNUT17 strong enough as the primary BIO/NER public benchmark, or should a second BIO/NER slice be added?
7. If B4 is not empirically dominant but diagnostic signal is strong, what is the right paper positioning?
8. Are the theory guardrails appropriately conservative, especially around conditional MPO rank membership?

## 14. Minimal Repository Pointers

```text
docs/PROJECT_OVERVIEW.md
docs/PAPER_POSITIONING.md
docs/ROUTE_REVIEW_CHECKLIST.md
docs/EXPERIMENT_PLAN.md
docs/EVIDENCE_AND_AUDIT.md
docs/THEORY_AND_GUARDRAILS.md
docs/AUTODL_HPC_RUNBOOK.md
src/tensor_crf_jmlr/posterior_event_algebra/
src/tensor_crf_jmlr/event_training/
experiments/suites/current_repro.yaml
experiments/suites/autodl_smoke.yaml
```

## 15. Current Bottom Line

The project is past idea-only stage. It has:

- fixed posterior-event object;
- local theory/code sanity;
- preliminary controlled/semi-real/real-source positive evidence;
- frozen P3/P4 protocol and smoke;
- frozen WNUT17 BIO/NER data gate plus B0-B6 stress smoke;
- P5 AutoDL/HPC engineering prepared locally.

It does not yet have:

- fresh external proof-check;
- WNUT17 multi-seed/grid R5 formal runs;
- JMLR-ready empirical package;
- benchmark superiority claim;
- full diagnostic coverage.

Reviewer should judge whether the current plan is strong enough to proceed into P6 formal runs, and what should be strengthened before spending AutoDL/HPC budget.
