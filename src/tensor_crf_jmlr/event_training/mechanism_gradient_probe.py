"""Gradient mechanism probe for BIO event regularization.

This is a CPU-only local mechanism check, not an experiment or benchmark.  It
uses a zero-potential CRF so the direction of ``-log P(L|x)`` can be inspected
without training.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

import torch

from .bio_event import bio_start_allowed, bio_transition_allowed
from .event_crf import TinyLinearChainCRF


@dataclass
class GradientFeatureRow:
    feature_type: str
    feature: str
    allowed_by_bio: bool
    gradient_of_event_loss: float
    optimizer_step_effect: str


@dataclass
class GradientSummary:
    label_names: list[str]
    sequence_length: int
    event_probability_at_zero_potentials: float
    illegal_start_count: int
    illegal_start_min_gradient: float
    illegal_start_mean_gradient: float
    illegal_transition_count: int
    illegal_transition_min_gradient: float
    illegal_transition_mean_gradient: float
    legal_transition_count: int
    legal_transition_negative_gradient_count: int
    legal_transition_min_gradient: float
    legal_transition_max_gradient: float
    sanity_status: str
    claim_boundary: str


def _effect_from_gradient(gradient: float, tol: float = 1e-12) -> str:
    if gradient > tol:
        return "梯度下降会降低这个分数"
    if gradient < -tol:
        return "梯度下降会提高这个分数"
    return "近似不变"


def run_gradient_probe(output_dir: Path) -> None:
    label_names = ["O", "B-X", "I-X", "B-Y", "I-Y"]
    model = TinyLinearChainCRF(vocab_size=8, label_names=label_names).double()
    model.assert_cpu_only()
    with torch.no_grad():
        model.emissions.weight.zero_()
        model.start.zero_()
        model.transitions.zero_()

    word_ids = [1, 2, 3, 4]
    loss = -model.log_event_probability_bio(word_ids)
    p_event = float(torch.exp(model.log_event_probability_bio(word_ids)).detach().cpu().item())
    loss.backward()

    rows: list[GradientFeatureRow] = []
    start_grad = model.start.grad.detach().cpu()
    transition_grad = model.transitions.grad.detach().cpu()

    for idx, label in enumerate(label_names):
        grad = float(start_grad[idx].item())
        rows.append(
            GradientFeatureRow(
                feature_type="start",
                feature=f"START->{label}",
                allowed_by_bio=bio_start_allowed(label),
                gradient_of_event_loss=grad,
                optimizer_step_effect=_effect_from_gradient(grad),
            )
        )

    for prev_idx, prev_label in enumerate(label_names):
        for curr_idx, curr_label in enumerate(label_names):
            grad = float(transition_grad[prev_idx, curr_idx].item())
            rows.append(
                GradientFeatureRow(
                    feature_type="transition",
                    feature=f"{prev_label}->{curr_label}",
                    allowed_by_bio=bio_transition_allowed(prev_label, curr_label),
                    gradient_of_event_loss=grad,
                    optimizer_step_effect=_effect_from_gradient(grad),
                )
            )

    illegal_start_grads = [
        row.gradient_of_event_loss
        for row in rows
        if row.feature_type == "start" and not row.allowed_by_bio
    ]
    illegal_transition_grads = [
        row.gradient_of_event_loss
        for row in rows
        if row.feature_type == "transition" and not row.allowed_by_bio
    ]
    legal_transition_grads = [
        row.gradient_of_event_loss
        for row in rows
        if row.feature_type == "transition" and row.allowed_by_bio
    ]
    legal_negative_count = sum(1 for grad in legal_transition_grads if grad < -1e-12)
    status = "PASS" if min(illegal_start_grads + illegal_transition_grads) > 1e-12 and legal_negative_count > 0 else "WARN"

    summary = GradientSummary(
        label_names=label_names,
        sequence_length=len(word_ids),
        event_probability_at_zero_potentials=p_event,
        illegal_start_count=len(illegal_start_grads),
        illegal_start_min_gradient=min(illegal_start_grads),
        illegal_start_mean_gradient=mean(illegal_start_grads),
        illegal_transition_count=len(illegal_transition_grads),
        illegal_transition_min_gradient=min(illegal_transition_grads),
        illegal_transition_mean_gradient=mean(illegal_transition_grads),
        legal_transition_count=len(legal_transition_grads),
        legal_transition_negative_gradient_count=legal_negative_count,
        legal_transition_min_gradient=min(legal_transition_grads),
        legal_transition_max_gradient=max(legal_transition_grads),
        sanity_status=status,
        claim_boundary="只支持机制 sanity；不支持 benchmark、usefulness 或真实任务性能 claim",
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    row_dicts = [asdict(row) for row in rows]
    (output_dir / "mechanism_gradient_rows.json").write_text(
        json.dumps(row_dicts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "mechanism_gradient_rows.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row_dicts[0].keys()))
        writer.writeheader()
        writer.writerows(row_dicts)

    (output_dir / "mechanism_gradient_summary.json").write_text(
        json.dumps(asdict(summary), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    top_illegal = sorted(
        [row for row in rows if not row.allowed_by_bio],
        key=lambda row: row.gradient_of_event_loss,
        reverse=True,
    )[:8]
    top_legal_raise = sorted(
        [row for row in rows if row.allowed_by_bio],
        key=lambda row: row.gradient_of_event_loss,
    )[:8]
    report = [
        "# 训练信号梯度机制检查",
        "",
        "结论：",
        "",
        f"```text\n{summary.sanity_status}：局部梯度机制 sanity 通过。\nHOLD：不能升级为 usefulness / benchmark / real-task claim。\n```",
        "",
        "这个 probe 不训练模型。它把 CRF 的 start / transition / emission 势都设为 0，只检查训练项",
        "`-log P_theta(L|x)` 的梯度方向。梯度下降中，正梯度会降低对应 score，负梯度会提高对应 score。",
        "",
        "## 摘要",
        "",
        f"- 标签集合：`{', '.join(label_names)}`",
        f"- 序列长度：`{summary.sequence_length}`",
        f"- 零势能 `P_theta(L|x)`：`{summary.event_probability_at_zero_potentials:.6f}`",
        f"- 非法 BIO 起点：`{summary.illegal_start_count}` 个，最小梯度 `{summary.illegal_start_min_gradient:.6f}`",
        f"- 非法 BIO 转移：`{summary.illegal_transition_count}` 个，最小梯度 `{summary.illegal_transition_min_gradient:.6f}`",
        f"- 负梯度合法转移：`{summary.legal_transition_negative_gradient_count}` / `{summary.legal_transition_count}`",
        "",
        "## 被压低的非法 feature",
        "",
        "| feature | 梯度 | 优化效果 |",
        "|---|---:|---|",
    ]
    for row in top_illegal:
        report.append(
            f"| `{row.feature}` | {row.gradient_of_event_loss:.6f} | {row.optimizer_step_effect} |"
        )
    report.extend(
        [
            "",
            "## 被抬高的合法 feature",
            "",
            "| feature | 梯度 | 优化效果 |",
            "|---|---:|---|",
        ]
    )
    for row in top_legal_raise:
        report.append(
            f"| `{row.feature}` | {row.gradient_of_event_loss:.6f} | {row.optimizer_step_effect} |"
        )
    report.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "允许说：这个检查支持一个局部机制解释，即 `-log P_theta(L|x)` 会对 BIO 非法起点和非法转移产生降低分数的梯度，并会给部分合法转移提高分数。",
            "",
            "不能说：这证明了真实任务效果、benchmark superiority、最佳 lambda，或比 constrained CRF / WFST / posterior regularization 全面更好。",
            "",
        ]
    )
    report_dir = output_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "TRAINING_SIGNAL_GRADIENT_MECHANISM_REPORT.md").write_text(
        "\n".join(report),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/results/event_training")
    args = parser.parse_args()
    run_gradient_probe(Path(args.output_dir))


if __name__ == "__main__":
    main()
