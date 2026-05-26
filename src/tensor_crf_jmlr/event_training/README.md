# 事件训练信号本地 Probe

这是 Project 2 的 CPU-only 本地机制与实验 probe。

它检查 regular-language posterior event probability 能否作为 tiny CRF 的训练信号：

```text
Loss = CRF_NLL(x, y_gold) - lambda * log P_theta(L|x)
```

## 运行

```powershell
python -m unittest discover -s src\tensor_crf_jmlr\event_training\tests -v
python -m tensor_crf_jmlr.event_training.run_probe --epochs 15
python -m tensor_crf_jmlr.event_training.mechanism_gradient_probe
python -m tensor_crf_jmlr.event_training.robustness_sweep --num-seeds 30
python -m tensor_crf_jmlr.event_training.formal_validation_runner --seed-count 10
python -m tensor_crf_jmlr.event_training.semi_real_format_probe --seed-count 5
python -m tensor_crf_jmlr.event_training.real_small_data_retail_probe --seed-count 5
python -m tensor_crf_jmlr.event_training.formal_pre_paper_export
```

## 输出约定

Raw CSV/JSON 保存在：

```text
experiments/results/event_training/
```

统一 pre-paper schema 保存在：

```text
experiments/results/event_training/formal_pre_paper/
```

runner 生成的 markdown 报告统一保存在：

```text
experiments/results/event_training/reports/
```

probe 根目录只保留代码、测试、数据入口和本 README，不再保留散落实验报告。

## 禁止主张

- 不是 benchmark；
- 不是 GPU run；
- 不是完整真实数据实验；
- 不支持 usefulness 或 benchmark superiority；
- 不支持任意 CRF / DFA / regular language 的低秩优势。
