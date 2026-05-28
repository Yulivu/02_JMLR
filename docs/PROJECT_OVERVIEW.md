# Project Overview

生成时间：2026-05-26

## 1. 主线

```text
Tensorized Regular-Language Posterior Algebra for CRFs
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
P5/R5-prep in progress: AutoDL/HPC engineering prepared locally; WNUT17 BIO/NER stress + feature viability local checks passed; target-machine smoke pending
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

尚未完成：

- fresh proof-check；
- JMLR 级完整实验；
- AutoDL target-machine smoke；
- B5/B6/WFST-style 更 faithful baseline；
- 全任务/全 baseline diagnostic aggregation；
- paper-writing gate。

## 5. 项目路线图与进度

当前处在：

```text
P5 in progress: AutoDL/HPC 工程入口已本地准备，等待目标机器 smoke
```

更具体地说：主问题、理论对象、代码骨架、初步证据、仓库结构已经稳定；JMLR 前实验协议、retail auxiliary slice、formal run list 和 R0 本地 smoke 已完成冻结与本地验收。根据 review，P6 前必须补 canonical BIO/NER slice；现在已冻结为 WNUT17 Emerging Entities，数据 gate 已通过本地 audit。R5 B0-B6 stress smoke 已显示 hidden posterior conflict；feature viability smoke 已显示 WNUT17 可以学到非零 entity F1，但 event mass 在该 regime 里接近饱和。现在还没有进入论文写作，也还没有进入正式 AutoDL/HPC 大规模实验。当前 P5 仍只做工程适配和 formal-run 前置检查。

| Phase | 阶段目标 | 当前状态 | 已有产物 | 还缺什么 | 下一步判定 |
|---|---|---|---|---|---|
| P0 | 立项与问题定义 | done | 主线固定为 `Tensorized Regular-Language Posterior Algebra for CRFs` | 无关键缺口 | 已通过 |
| P1 | 理论对象最小闭环 | mostly done | `P_theta(L|x)` 定义、DFA/product-transfer reference code、theory tests | fresh proof-check 和论文级证明文本 | 补 proof audit |
| P2 | 本地机制验证 | mostly done | posterior algebra tests、event CRF tests、controlled/semi-real/real-source local probes | 不能当作正式 benchmark claim | 保留为路线证据 |
| P3 | JMLR 前实验协议冻结 | revised-frozen | `docs/EXPERIMENT_PLAN.md`、baseline table、formal run list、suite/config scaffold、retail slice v1、WNUT17 BIO/NER data gate、B0-B6 stress smoke、feature viability smoke、R5 two-regime protocol | AutoDL target smoke 未跑 | 进入 P5 target smoke |
| P4 | 本地正式 smoke | done | `r0_controlled_smoke`、`r0_semi_real_smoke`、`r0_real_source_smoke` 全部通过；schema audit 通过 | R0 是 smoke，不是正式结论 | 已通过 |
| P5 | AutoDL/HPC 工程化 | in progress | `autodl_smoke` suite、preflight、runbook、launcher、WNUT17 data gate 已建立 | 还需要在 AutoDL/HPC 机器上实际通过 | 当前阶段 |
| P6 | JMLR formal runs | not started | R1-R8 run list 已规划；WNUT17 B0-B6 local stress smoke 支持 R5 可继续 | R5 多 seed/grid 正式结果未跑完 | 产出完整 evidence package |
| P7 | result-to-claim audit | not started | claim/evidence matrix 初版 | 需要根据正式结果更新主张边界 | 决定能写到什么强度 |
| P8 | 论文写作前冻结 | not started | 当前 docs 可作为材料 | 最终实验、图表、反例、限制、复现实验说明 | 通过后进入写论文 |

简化判断：

```text
项目不是早期想法阶段；已经进入“论文前扎实实验准备阶段”。
P3/P4 工程门禁已通过；paper route 已根据 review 收缩，P6 前 BIO/NER canonical data gate 已补齐为 WNUT17，并完成 B0-B6 stress smoke 与 feature viability smoke。
项目还不是 JMLR-ready，也还没有到正式写论文阶段。
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

1. 保持 P5 AutoDL smoke 工程入口；
2. 在 AutoDL 目标机器上跑 P5 smoke；
3. 明确 complexity story：CRF x DFA product state、rule complexity、batching/memory；
4. 将 rank/MPO 降为 appendix；
5. 只有 R5 local smoke 和 P5 target-machine smoke 都通过后，才进入 P6 formal runs。
