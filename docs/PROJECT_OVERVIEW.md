# Project Overview

生成时间：2026-05-26

## 1. 主线

```text
Posterior Regular-Language Event Mass for Conditional Random Fields
```

最简说法：

```text
给定输入 x、CRF 后验 P_theta(y|x)、规则语言 L，
我们计算 CRF 原始后验里有多少概率质量落在 L 中：
P_theta(L|x)。
```

这不是一个新的解码器，也不是简单把输出修合法。它问的是：

```text
模型内部到底有多少概率相信这个规则？
```

## 2. 项目价值

传统 hard constraint decoding 主要保证最终输出合法，但可能掩盖模型内部冲突。本项目把规则从“输出后的过滤器”变成“后验分布里的可计算事件”：

- 可以审计：最高分答案合法但 `P_theta(L|x)` 很低，说明模型并不真正相信规则；
- 可以训练：用 `-log P_theta(L|x)` 作为事件训练信号，推动后验质量进入合法集合；
- 可以诊断：低 `P_theta(L|x)` 样本更可能是错误或 hidden conflict；
- 可以理论化：事件质量可以通过 product automaton transfer 精确表示；rank/MPO 相关内容只作为 appendix support。

## 3. Paper Identity

当前最强主线不是 tensor rank，也不是另一个 constrained decoder，而是：

```text
posterior-level regular-language event semantics
```

论文需要让 reviewer 迅速理解：

```text
decoded output legality != posterior consistency
```

也就是说，hard-constrained decoding 可以把最终输出修合法，但不能告诉我们模型后验里是否仍然有大量非法概率质量。`P_theta(L|x)` 把“模型是否真的相信规则”变成了可计算、可训练、可审计的对象。

主文应围绕四件事：

1. exact posterior event transfer；
2. event training；
3. hidden posterior conflict diagnostic；
4. canonical BIO/NER structured benchmark。

MPO/rank membership 只作为 appendix / optional theory support，不作为 paper identity。

## 4. 当前状态

当前阶段：

```text
Pre-paper evidence package completed at audited-block level; HPC paused; external review / paper-prep next
```

已完成：

- 核心对象和研究方向固定；
- theory package 已成形；
- `src/tensor_crf_jmlr/posterior_event_algebra/` 小规模 posterior algebra sanity 通过；
- event CRF smoke tests 通过；
- controlled / semi-real / real-source small-field 本地证据已整理；
- baseline fairness、claim-evidence、AutoDL gate 已有当前版本；
- WNUT17 BIO/NER canonical slice 已冻结为 P6 前 reviewer-facing benchmark；
- WNUT17 R5 local stress smoke 已能跑 B0-B6，并展示 hard-constrained legal output 与低 posterior BIO mass 的 hidden conflict；
- WNUT17 feature-based viability smoke 已让 B0 entity F1 离开 0，但该配置下 posterior event mass 接近饱和；
- HTML 展示页保留为项目解释材料。
- AutoDL R5 formal runs 已下载并完成 result-to-claim audit；
- R5a 支持 hidden posterior conflict 和 posterior event training signal；
- R5b 支持 WNUT17 不是 all-O toy，但不支持 B4 的 NER F1 superiority。
- R1/R2/R4/R6a/R8 已完成并审计；
- final claim table、B7/R3/R7 route decision、fresh proof audit、JMLR outline、proof prose 已完成。

尚未完成：

- fresh proof-check；
- JMLR 级最终写作包；
- full P6 formal package beyond R5；
- B5/B6/WFST-style 更 faithful baseline；
- 全任务/全 baseline diagnostic aggregation；
- paper-writing gate。

## 5. 项目路线图与进度

当前处在：

```text
R5 audited: WNUT17 BIO/NER formal block 已完成审计；完整 P6 还没完成
```

更具体地说：主问题、理论对象、代码骨架、仓库结构、正式实验块和审计结果已经稳定。canonical BIO/NER slice 已冻结为 WNUT17 Emerging Entities，R5/R1/R2/R4/R6a/R8 已完成并审计。当前不继续上 HPC；下一步是外部审核、related work 定位、diagnostic reanalysis、本地 table generation 和正式论文写作准备。

| Phase | 阶段目标 | 当前状态 | 已有产物 | 还缺什么 | 下一步判定 |
|---|---|---|---|---|---|
| P0 | 立项与问题定义 | done | 主线收缩为 posterior regular-language event mass / posterior consistency auditing | 无关键缺口 | 已通过 |
| P1 | 理论对象最小闭环 | mostly done | `P_theta(L|x)` 定义、DFA/product-transfer reference code、theory tests | fresh proof-check 和论文级证明文本 | 补 proof audit |
| P2 | 本地机制验证 | mostly done | posterior algebra tests、event CRF tests、controlled/semi-real/real-source local probes | 不能当作正式 benchmark claim | 保留为路线证据 |
| P3 | JMLR 前实验协议冻结 | revised-frozen | `docs/EXPERIMENT_PLAN.md`、baseline table、formal run list、suite/config scaffold、retail slice v1、WNUT17 BIO/NER data gate、B0-B6 stress smoke、feature viability smoke、R5 two-regime protocol | 后续只能通过显式 protocol revision 修改 | 已通过 |
| P4 | 本地正式 smoke | done | `r0_controlled_smoke`、`r0_semi_real_smoke`、`r0_real_source_smoke` 全部通过；schema audit 通过 | R0 是 smoke，不是正式结论 | 已通过 |
| P5 | AutoDL/HPC 工程化 | done | `autodl_smoke` suite、preflight、runbook、launcher、WNUT17 data gate；AutoDL Linux smoke passed on commit `cdc3a5f` | 无当前阻塞 | 已通过 |
| R5 | WNUT17 BIO/NER formal block | done-with-boundary | R5a/R5b 10-seed AutoDL formal runs；`R5_RESULT_TO_CLAIM_AUDIT.md` | 只支持 posterior-conflict / viability，不支持 F1 superiority | 纳入 P6 证据包 |
| P6 | JMLR formal runs | mostly done / route-review needed | R5、R1/R2/R4、R6a、R8 已完成并审计 | 是否补 R3/R7/B7 需要本地路线判断 | 进入 pre-paper evidence gate |
| P7 | result-to-claim audit | partial | R5 claim audit 已完成 | 需要根据全部 formal 结果更新主张边界 | 决定能写到什么强度 |
| P8 | 论文写作前冻结 | in progress | outline/proof/review materials 已有 | 外部 review、related work 正文、final tables | 通过后进入写论文 |

简化判断：

```text
项目不是早期想法阶段；已经进入“论文前扎实实验准备阶段”。
P3/P4/P5 工程门禁已通过；paper route 已根据 review 收缩，BIO/NER canonical data gate 已补齐为 WNUT17，并完成 R5 formal audit。
项目还不是 JMLR-ready submission package，但已经进入 paper-prep / external-review 阶段。
```

主路线图入口：

```text
docs/EXPERIMENT_PLAN.md
```

其中最重要的两张表是：

- `Formal Run List`：R0-R8，要跑哪些实验；
- `Execution Order`：S0-S7，什么时候才能上 AutoDL/HPC。

## 6. 当前最安全主张

可以说：

```text
P_theta(L|x) 是一个可计算、可审计、可训练的 CRF posterior event signal。
```

也可以说：

```text
local controlled / semi-real / real-source small-field probes 支持它作为结构训练信号和诊断信号的路线。
```

不能说：

- 项目已经 JMLR-ready；
- 已经证明 benchmark superiority；
- 已经全面优于 hard constraint / rule-feature / posterior regularization / WFST；
- 任意 CRF / DFA / regular language 都有低秩优势；
- 当前 local probes 等于正式真实任务结论。

## 7. 与 uMPS 的关系

一句话：

```text
uMPS 告诉我们，正则语言可以成为概率模型里的可计算事件；我们把这个视角接到 CRF 条件后验上，研究 P_theta(y in L | x)。
```

区别：

| uMPS | 本项目 |
|---|---|
| 生成式序列模型 | 条件 CRF 后验 |
| 问生成字符串是否落入 regex event | 问标签后验是否相信 regular-language rule |
| 关注 u-MPS 张量网络模型 | 关注 CRF posterior event mass |
| `P(s in R)` | `P_theta(y in L | x)` |

## 8. 当前 repo 结构

```text
docs/
  PROJECT_OVERVIEW.md
  THEORY_AND_GUARDRAILS.md
  EXPERIMENT_PLAN.md
  EVIDENCE_AND_AUDIT.md
  presentation/
  references/

src/tensor_crf_jmlr/posterior_event_algebra/
  finite posterior algebra, DFA, product transfer, indexing, MPO sanity

src/tensor_crf_jmlr/event_training/
  event CRF helpers, local/semi-real/real-source runners, smoke tests

data/
  raw research data used by local probes

experiments/
  retained results plus future configs, suites, runs, and visualizations
```

## 9. 推荐阅读顺序

1. `docs/PROJECT_OVERVIEW.md`
2. `docs/PAPER_POSITIONING.md`
3. `docs/ROUTE_REVIEW_CHECKLIST.md`
4. `docs/EXPERIMENT_PLAN.md`
5. `docs/EVIDENCE_AND_AUDIT.md`
6. `docs/THEORY_AND_GUARDRAILS.md`
7. `docs/presentation/project_value_presentation_cn.html`

## 10. 下一步

按顺序执行：

1. 固定 R5 审计边界：R5a 讲 hidden posterior conflict，R5b 讲 task viability，不讲 F1 superiority；
2. 执行 R1/R2/R4，补 controlled、semi-real、real-source formal evidence；
3. 阅读 `docs/PRE_PAPER_EVIDENCE_GATE.md`，完成本地 pre-paper route review；
4. 判断是否需要补 R3/R7/B7；
5. fresh proof-check / theory consistency audit。
