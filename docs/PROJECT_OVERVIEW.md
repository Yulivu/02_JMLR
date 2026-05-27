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
- 可以理论化：事件质量可以通过 product automaton transfer 精确表示，并在显式假设下讨论 rank membership 和误差边界。

## 3. 当前状态

当前阶段：

```text
P5-ready: P3/P4 passed, AutoDL/HPC engineering not started
```

已完成：

- 核心对象和研究方向固定；
- theory package 已成形；
- `src/tensor_crf_jmlr/posterior_event_algebra/` 小规模 posterior algebra sanity 通过；
- event CRF smoke tests 通过；
- controlled / semi-real / real-source small-field 本地证据已整理；
- baseline fairness、claim-evidence、AutoDL gate 已有当前版本；
- HTML 展示页保留为项目解释材料。

尚未完成：

- fresh proof-check；
- JMLR 级完整实验；
- public/real formal slice 冻结；
- B5/B6/WFST-style 更 faithful baseline；
- 全任务/全 baseline diagnostic aggregation；
- paper-writing gate。

## 4. 项目路线图与进度

当前处在：

```text
P5-ready: P3/P4 已通过，下一步才是 AutoDL/HPC 工程化
```

更具体地说：主问题、理论对象、代码骨架、初步证据、仓库结构已经稳定；JMLR 前实验协议、public/real slice v1、formal run list 和 R0 本地 smoke 已完成冻结与本地验收。现在还没有进入论文写作，也还没有进入正式 AutoDL/HPC 大规模实验。下一道关键门槛是 P5：只做工程适配，不提前修改实验协议。

| Phase | 阶段目标 | 当前状态 | 已有产物 | 还缺什么 | 下一步判定 |
|---|---|---|---|---|---|
| P0 | 立项与问题定义 | done | 主线固定为 `Tensorized Regular-Language Posterior Algebra for CRFs` | 无关键缺口 | 已通过 |
| P1 | 理论对象最小闭环 | mostly done | `P_theta(L|x)` 定义、DFA/product-transfer reference code、theory tests | fresh proof-check 和论文级证明文本 | 补 proof audit |
| P2 | 本地机制验证 | mostly done | posterior algebra tests、event CRF tests、controlled/semi-real/real-source local probes | 不能当作正式 benchmark claim | 保留为路线证据 |
| P3 | JMLR 前实验协议冻结 | done | `docs/EXPERIMENT_PLAN.md`、baseline table、formal run list、suite/config scaffold、public/real slice v1 | B7/WFST-style 仍是 design-if-feasible，不阻塞 P3 | 已通过 |
| P4 | 本地正式 smoke | done | `r0_controlled_smoke`、`r0_semi_real_smoke`、`r0_real_source_smoke` 全部通过；schema audit 通过 | R0 是 smoke，不是正式结论 | 已通过 |
| P5 | AutoDL/HPC 工程化 | not started | AutoDL gate 已写入计划；P3/P4 已满足进入条件 | runner/device/config 还未适配 | 当前下一步 |
| P6 | JMLR formal runs | not started | run list 已规划 | R1-R7 正式结果未跑完 | 产出完整 evidence package |
| P7 | result-to-claim audit | not started | claim/evidence matrix 初版 | 需要根据正式结果更新主张边界 | 决定能写到什么强度 |
| P8 | 论文写作前冻结 | not started | 当前 docs 可作为材料 | 最终实验、图表、反例、限制、复现实验说明 | 通过后进入写论文 |

简化判断：

```text
项目不是早期想法阶段；已经进入“论文前扎实实验准备阶段”。
P3/P4 已通过；但还不是 JMLR-ready，也还没有到正式写论文阶段。
```

主路线图入口：

```text
docs/EXPERIMENT_PLAN.md
```

其中最重要的两张表是：

- `Formal Run List`：R0-R7，要跑哪些实验；
- `Execution Order`：S0-S7，什么时候才能上 AutoDL/HPC。

## 5. 当前最安全主张

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

## 6. 与 uMPS 的关系

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

## 7. 当前 repo 结构

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

## 8. 推荐阅读顺序

1. `docs/PROJECT_OVERVIEW.md`
2. `docs/THEORY_AND_GUARDRAILS.md`
3. `docs/EVIDENCE_AND_AUDIT.md`
4. `docs/EXPERIMENT_PLAN.md`
5. `docs/presentation/project_value_presentation_cn.html`

## 9. 下一步

按顺序执行：

1. 冻结 JMLR 实验协议；
2. 冻结 public / real field slice；
3. 冻结 formal run list；
4. 本地 CPU smoke 每个 block 1 seed；
5. smoke 通过后再处理 AutoDL/HPC runner/device/config。
