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

查看当前可复现实验 suite：

```powershell
python scripts/run_experiment_suite.py --suite experiments/suites/current_repro.yaml --dry-run
```

运行最小本地 smoke：

```powershell
python scripts/run_experiment_suite.py `
  --suite experiments/suites/current_repro.yaml `
  --task r0_controlled_smoke
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

方向、理论对象、实验路线已经固定；P3/P4 已本地通过，当前处在 P5-ready：可以开始 AutoDL/HPC 工程化，但还没有进入正式大规模实验或论文写作。

总路线图和进度表见：`docs/PROJECT_OVERVIEW.md` 的“项目路线图与进度”。

已支持：`P_theta(L|x)` 的小规模精确计算、有限 sanity、local/semi-real/real-source probes、baseline fairness 初审、AutoDL 正式实验 gate。

未支持：JMLR-ready empirical claim、benchmark superiority、任意 CRF/DFA 的低秩优势、全面优于 hard constraint / WFST / posterior regularization。

下一步：在不改动冻结协议的前提下，做 AutoDL/HPC runner、device、config 适配；适配通过后再进入 formal runs。

P5 AutoDL/HPC 工程入口：

```text
docs/AUTODL_HPC_RUNBOOK.md
experiments/suites/autodl_smoke.yaml
scripts/hpc/preflight_autodl.py
scripts/hpc/run_autodl_smoke.sh
```
