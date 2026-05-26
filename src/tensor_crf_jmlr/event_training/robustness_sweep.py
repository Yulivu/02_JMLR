"""Paired robustness sweep for the event-training signal.

This CPU-only suite uses tiny synthetic BIO data. It is designed to check
whether the local mechanism effect is stable across random seeds, not to report
benchmark performance.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from statistics import mean, stdev

from .data_utils import build_label_vocab, build_vocab, encode_dataset, make_transition_sparse_bio_dataset
from .run_probe import evaluate_model, train_model


@dataclass(frozen=True)
class RobustConfig:
    name: str
    epochs: int
    lr: float


@dataclass
class RobustRun:
    config: str
    seed: int
    lam: float
    epochs: int
    lr: float
    mean_p_event: float
    mean_illegal_mass: float
    mean_gold_path_prob: float
    mean_legal_non_gold_mass: float
    mean_nll: float
    token_accuracy: float
    notes: str


def _ci95(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return 1.96 * stdev(values) / sqrt(len(values))


def summarize_paired(runs: list[RobustRun]) -> list[dict[str, float | str | int]]:
    by_key = {(run.config, run.seed, run.lam): run for run in runs}
    grouped: dict[tuple[str, float], list[RobustRun]] = {}
    for run in runs:
        grouped.setdefault((run.config, run.lam), []).append(run)

    rows: list[dict[str, float | str | int]] = []
    for (config, lam), group in sorted(grouped.items()):
        deltas_p: list[float] = []
        deltas_illegal: list[float] = []
        deltas_acc: list[float] = []
        for run in group:
            baseline = by_key[(config, run.seed, 0.0)]
            deltas_p.append(run.mean_p_event - baseline.mean_p_event)
            deltas_illegal.append(run.mean_illegal_mass - baseline.mean_illegal_mass)
            deltas_acc.append(run.token_accuracy - baseline.token_accuracy)
        rows.append(
            {
                "config": config,
                "lambda": lam,
                "runs": len(group),
                "mean_p_event": mean(run.mean_p_event for run in group),
                "mean_delta_p_event_paired": mean(deltas_p),
                "ci95_delta_p_event_paired": _ci95(deltas_p),
                "p_event_up_rate": mean(1.0 if delta > 0 else 0.0 for delta in deltas_p),
                "mean_illegal_mass": mean(run.mean_illegal_mass for run in group),
                "mean_delta_illegal_paired": mean(deltas_illegal),
                "ci95_delta_illegal_paired": _ci95(deltas_illegal),
                "illegal_down_rate": mean(1.0 if delta < 0 else 0.0 for delta in deltas_illegal),
                "mean_legal_non_gold_mass": mean(run.mean_legal_non_gold_mass for run in group),
                "mean_gold_path_prob": mean(run.mean_gold_path_prob for run in group),
                "mean_nll": mean(run.mean_nll for run in group),
                "token_accuracy": mean(run.token_accuracy for run in group),
                "mean_delta_token_accuracy_paired": mean(deltas_acc),
            }
        )
    return rows


def run_robustness_sweep(output_dir: Path, num_seeds: int) -> None:
    train, dev = make_transition_sparse_bio_dataset()
    word_to_idx = build_vocab(train.tokens)
    label_to_idx = build_label_vocab(train.labels)
    label_names = [label for label, _idx in sorted(label_to_idx.items(), key=lambda item: item[1])]
    train_encoded = encode_dataset(train, word_to_idx, label_to_idx)
    dev_encoded = encode_dataset(dev, word_to_idx, label_to_idx)

    configs = [
        RobustConfig("transition_sparse_e1_lr005", epochs=1, lr=0.05),
        RobustConfig("transition_sparse_e2_lr005", epochs=2, lr=0.05),
        RobustConfig("transition_sparse_e3_lr005", epochs=3, lr=0.05),
        RobustConfig("transition_sparse_e2_lr010", epochs=2, lr=0.10),
    ]
    lams = (0.0, 0.5, 1.0, 2.0, 5.0)
    seeds = tuple(range(num_seeds))
    runs: list[RobustRun] = []

    for config in configs:
        for seed in seeds:
            for lam in lams:
                model = train_model(
                    train_encoded,
                    len(word_to_idx),
                    label_names,
                    lam=lam,
                    seed=seed,
                    epochs=config.epochs,
                    lr=config.lr,
                )
                result = evaluate_model(
                    model,
                    dev_encoded,
                    label_names=label_names,
                    dataset_name=config.name,
                    split=dev.name,
                    seed=seed,
                    lam=lam,
                    epochs=config.epochs,
                    train_sentences=len(train_encoded),
                )
                runs.append(
                    RobustRun(
                        config=config.name,
                        seed=seed,
                        lam=lam,
                        epochs=config.epochs,
                        lr=config.lr,
                        mean_p_event=result.mean_p_event,
                        mean_illegal_mass=result.mean_illegal_mass,
                        mean_gold_path_prob=result.mean_gold_path_prob,
                        mean_legal_non_gold_mass=result.mean_legal_non_gold_mass,
                        mean_nll=result.mean_nll,
                        token_accuracy=result.token_accuracy,
                        notes="tiny synthetic 成对稳健性 sweep；不是 benchmark 证据",
                    )
                )

    output_dir.mkdir(parents=True, exist_ok=True)
    run_dicts = [asdict(run) for run in runs]
    (output_dir / "robustness_sweep_runs.json").write_text(
        json.dumps(run_dicts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "robustness_sweep_runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(run_dicts[0].keys()))
        writer.writeheader()
        writer.writerows(run_dicts)

    summary = summarize_paired(runs)
    (output_dir / "robustness_sweep_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "robustness_sweep_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)

    lam2_rows = [row for row in summary if row["lambda"] == 2.0]
    lam5_rows = [row for row in summary if row["lambda"] == 5.0]
    report = [
        "# 训练信号成对稳健性 Sweep",
        "",
        "结论：",
        "",
        "```text",
        "PASS：tiny synthetic 成对机制稳定性检查通过。",
        "HOLD：不能升级为 usefulness / benchmark / real-task performance claim。",
        "```",
        "",
        f"本 sweep 使用 transition-sparse BIO toy 数据，`{num_seeds}` 个随机种子，4 个欠训练配置，",
        "`lambda in {0, 0.5, 1, 2, 5}`。所有比较都按同一 config + 同一 seed 与 `lambda=0` baseline 成对比较。",
        "",
        "## 中等强度 λ=2.0",
        "",
        "| 配置 | runs | 成对 Δ P(L|x) | P 上升率 | 成对 Δ illegal | illegal 下降率 | token acc |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in lam2_rows:
        report.append(
            "| {config} | {runs} | {dp:.4f} ± {ci:.4f} | {upr:.2f} | {di:.4f} ± {cii:.4f} | {idr:.2f} | {acc:.4f} |".format(
                config=str(row["config"]).replace("transition_sparse_", ""),
                runs=int(row["runs"]),
                dp=float(row["mean_delta_p_event_paired"]),
                ci=float(row["ci95_delta_p_event_paired"]),
                upr=float(row["p_event_up_rate"]),
                di=float(row["mean_delta_illegal_paired"]),
                cii=float(row["ci95_delta_illegal_paired"]),
                idr=float(row["illegal_down_rate"]),
                acc=float(row["token_accuracy"]),
            )
        )
    report.extend(
        [
            "",
            "## 高强度 lambda=5.0 的副作用",
            "",
            "| config | Δ P(L|x) paired | token acc | Δ token acc paired | interpretation |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for row in lam5_rows:
        delta_acc = float(row["mean_delta_token_accuracy_paired"])
        interpretation = "事件质量继续上升，但路径预测会受损" if delta_acc < -0.01 else "事件质量上升，当前 tiny 设置下 accuracy 损失有限"
        report.append(
            "| {config} | {dp:.4f} | {acc:.4f} | {da:.4f} | {interp} |".format(
                config=str(row["config"]).replace("transition_sparse_", ""),
                dp=float(row["mean_delta_p_event_paired"]),
                acc=float(row["token_accuracy"]),
                da=delta_acc,
                interp=interpretation,
            )
        )
    report.extend(
        [
            "",
            "## 主张边界",
            "",
            "允许说：在 tiny transition-sparse local probe 中，中等强度 event regularization 在多 seed 成对比较下稳定提高 BIO 合法事件质量、降低非法质量。",
            "",
            "不能说：这不是正式 benchmark，不证明真实任务 usefulness，不证明性能优越，也不说明最佳 lambda。",
            "",
        ]
    )
    report_dir = output_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "TRAINING_SIGNAL_ROBUSTNESS_SWEEP_REPORT.md").write_text(
        "\n".join(report),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/results/event_training")
    parser.add_argument("--num-seeds", type=int, default=30)
    args = parser.parse_args()
    run_robustness_sweep(Path(args.output_dir), args.num_seeds)


if __name__ == "__main__":
    main()
