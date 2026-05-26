# 2_Tensor_CRF_JMLR

主线：

```text
Tensorized Regular-Language Posterior Algebra for CRFs
```

最简定位：本项目研究如何在 CRF 原始后验里计算 regular-language rule 的事件概率 `P_theta(L|x)`，并验证它能否作为训练信号和诊断信号。

## 当前结构

```text
docs/
  PROJECT_OVERVIEW.md          项目定位、当前状态、下一步
  THEORY_AND_GUARDRAILS.md     理论对象、定理包、禁止主张
  EVIDENCE_AND_AUDIT.md        当前证据、baseline audit、claim gate
  EXPERIMENT_PLAN.md           JMLR 前实验协议、run list、AutoDL gate
  presentation/                HTML 展示页
  references/                  参考论文与 reading notes

data/                          原始数据与数据说明
experiments/                   实验结果、后续 configs/suites/runs/visualizations
scripts/                       稳定后才沉淀的命令行入口
src/tensor_crf_jmlr/           Python package source code
```

核心代码模块：

```text
posterior_event_algebra/       后验事件代数、DFA、product-transfer、MPO sanity
event_training/                事件训练信号、local/semi-real/real-source probes、smoke tests
```

## 安装与检查

建议先用 editable install，使 `python -m tensor_crf_jmlr...` 入口在本地稳定可用：

```powershell
python -m pip install -e ".[dev]"
```

快速检查：

```powershell
python -c "import tensor_crf_jmlr; print('tensor_crf_jmlr import ok')"
python -m pytest
```

## 推荐阅读顺序

```text
docs/PROJECT_OVERVIEW.md
docs/THEORY_AND_GUARDRAILS.md
docs/EVIDENCE_AND_AUDIT.md
docs/EXPERIMENT_PLAN.md
```

展示项目价值：

```text
docs/presentation/project_value_presentation_cn.html
```

参考材料：

```text
docs/references/REFERENCE_INDEX.md
```

## 当前状态

方向、理论对象、实验路线已经固定；当前处在论文写作前的“实验与理论验证加固”阶段。

已支持：`P_theta(L|x)` 的小规模精确计算、有限 sanity、local/semi-real/real-source probes、baseline fairness 初审、AutoDL 正式实验 gate。

未支持：JMLR-ready empirical claim、benchmark superiority、任意 CRF/DFA 的低秩优势、全面优于 hard constraint / WFST / posterior regularization。

下一步：冻结严格实验协议、冻结 public/real slice、完成本地 smoke，然后再决定是否上 AutoDL 扩展正式实验。
