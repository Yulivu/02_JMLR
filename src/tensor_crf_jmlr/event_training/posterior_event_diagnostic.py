"""Sample-level posterior event risk diagnostics.

This script runs a small CPU diagnostic on representative semi-real and
real-source tasks. It estimates whether low baseline posterior event mass is
associated with higher error or hard-constraint conflict.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

import torch

from .real_small_data_retail_probe import (
    TASKS as REAL_TASKS,
    build_pool,
    load_field_values,
    make_dataset as make_real_dataset,
    split_pool,
)
from .semi_real_format_probe import (
    TASKS as SEMI_TASKS,
    VARIANTS,
    ProbeSetting,
    build_vocab,
    encode,
    emission_scores,
    labels_follow_pattern,
    log_event_probability,
    log_partition_from_emissions,
    make_dataset as make_semi_dataset,
    train_model,
    viterbi,
)


@dataclass
class DiagnosticCase:
    source: str
    task: str
    seed: int
    case_id: str
    tokens: str
    gold: str
    baseline_pred: str
    baseline_constrained_pred: str
    event_pred: str
    event_constrained_pred: str
    baseline_p_event: float
    event_p_event: float
    baseline_viterbi_log_prob: float
    baseline_neg_log_viterbi_prob: float
    baseline_max_sequence_prob: float
    baseline_viterbi_margin: float
    baseline_token_marginal_entropy: float
    baseline_sequence_entropy: float
    baseline_legal: bool
    event_legal: bool
    baseline_exact: bool
    event_exact: bool
    baseline_char_acc: float
    event_char_acc: float
    hidden_conflict: bool


def write_table(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    path.with_suffix(".json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def char_acc(pred: list[int], gold: list[int]) -> float:
    return sum(int(a == b) for a, b in zip(pred, gold)) / max(1, len(gold))


def decode(label_names: tuple[str, ...], ids: list[int]) -> str:
    return "".join(label_names[idx] for idx in ids)


def _top2_viterbi_scores(model, emissions: torch.Tensor) -> tuple[float, float]:
    neg_inf = -1.0e30
    top2 = torch.stack([model.start + emissions[0], torch.full_like(model.start, neg_inf)], dim=1)
    for pos in range(1, emissions.shape[0]):
        candidates: list[list[float]] = [[] for _ in range(emissions.shape[1])]
        for prev in range(emissions.shape[1]):
            for rank in range(2):
                prev_score = float(top2[prev, rank].detach().cpu().item())
                if prev_score <= neg_inf / 2:
                    continue
                for curr in range(emissions.shape[1]):
                    score = (
                        prev_score
                        + float(model.transitions[prev, curr].detach().cpu().item())
                        + float(emissions[pos, curr].detach().cpu().item())
                    )
                    candidates[curr].append(score)
        next_top2 = torch.full_like(top2, neg_inf)
        for curr, scores in enumerate(candidates):
            best = sorted(scores, reverse=True)[:2]
            for rank, score in enumerate(best):
                next_top2[curr, rank] = score
        top2 = next_top2
    best_scores = sorted((float(value) for value in top2.flatten().detach().cpu().tolist()), reverse=True)
    best = best_scores[0]
    second = best_scores[1] if len(best_scores) > 1 else neg_inf
    return best, second


def uncertainty_summary(model, task, word_ids: list[int]) -> dict[str, float]:
    emissions = emission_scores(model, task, word_ids)
    log_z = log_partition_from_emissions(model, emissions)
    best_score, second_score = _top2_viterbi_scores(model, emissions)
    log_z_value = float(log_z.detach().cpu().item())
    viterbi_log_prob = best_score - log_z_value
    max_sequence_prob = math.exp(min(0.0, viterbi_log_prob))
    margin = best_score - second_score if second_score > -1.0e29 else float("inf")

    alpha: list[torch.Tensor] = [model.start + emissions[0]]
    for pos in range(1, emissions.shape[0]):
        scores = alpha[-1][:, None] + model.transitions + emissions[pos][None, :]
        alpha.append(torch.logsumexp(scores, dim=0))

    beta: list[torch.Tensor] = [torch.zeros_like(model.start) for _ in range(emissions.shape[0])]
    for pos in range(emissions.shape[0] - 2, -1, -1):
        scores = model.transitions + emissions[pos + 1][None, :] + beta[pos + 1][None, :]
        beta[pos] = torch.logsumexp(scores, dim=1)

    token_entropy = 0.0
    expected_score = 0.0
    for pos in range(emissions.shape[0]):
        marg = torch.exp(alpha[pos] + beta[pos] - log_z)
        token_entropy += float((-(marg * torch.log(torch.clamp(marg, min=1.0e-12))).sum()).detach().cpu().item())
        expected_score += float((marg * emissions[pos]).sum().detach().cpu().item())
        if pos == 0:
            expected_score += float((marg * model.start).sum().detach().cpu().item())
    for pos in range(1, emissions.shape[0]):
        pair_log = alpha[pos - 1][:, None] + model.transitions + emissions[pos][None, :] + beta[pos][None, :] - log_z
        pair_marg = torch.exp(pair_log)
        expected_score += float((pair_marg * model.transitions).sum().detach().cpu().item())

    sequence_entropy = max(0.0, log_z_value - expected_score)
    return {
        "baseline_viterbi_log_prob": viterbi_log_prob,
        "baseline_neg_log_viterbi_prob": -viterbi_log_prob,
        "baseline_max_sequence_prob": max_sequence_prob,
        "baseline_viterbi_margin": margin,
        "baseline_token_marginal_entropy": token_entropy,
        "baseline_sequence_entropy": sequence_entropy,
    }


def evaluate_cases(*, source: str, task, labeled, unlabeled, dev, vocab: dict[str, int], seed: int) -> list[DiagnosticCase]:
    baseline = train_model(
        task,
        labeled,
        unlabeled,
        len(vocab),
        variant=VARIANTS["B0_unconstrained"],
        seed=seed,
        epochs=5,
        lr=0.08,
    )
    event_model = train_model(
        task,
        labeled,
        unlabeled,
        len(vocab),
        variant=VARIANTS["B4_semi_event_0.1"],
        seed=seed,
        epochs=5,
        lr=0.08,
    )
    inv_vocab = {idx: token for token, idx in vocab.items()}
    rows: list[DiagnosticCase] = []
    for idx, (word_ids, gold) in enumerate(dev):
        with torch.no_grad():
            base_p = float(torch.exp(log_event_probability(baseline, task, word_ids)).item())
            event_p = float(torch.exp(log_event_probability(event_model, task, word_ids)).item())
            base_pred, _ = viterbi(baseline, task, word_ids)
            base_c_pred, _ = viterbi(baseline, task, word_ids, constrained=True)
            event_pred, _ = viterbi(event_model, task, word_ids)
            event_c_pred, _ = viterbi(event_model, task, word_ids, constrained=True)
            uncertainty = uncertainty_summary(baseline, task, word_ids)
        base_legal = labels_follow_pattern(task, baseline.label_names, base_pred)
        base_c_legal = labels_follow_pattern(task, baseline.label_names, base_c_pred)
        event_legal = labels_follow_pattern(task, event_model.label_names, event_pred)
        rows.append(
            DiagnosticCase(
                source=source,
                task=task.name,
                seed=seed,
                case_id=f"{source}_{task.name}_{seed}_{idx:04d}",
                tokens=" ".join(inv_vocab.get(token_id, "<UNK>") for token_id in word_ids),
                gold=decode(tuple(task.label_names), gold),
                baseline_pred=decode(tuple(task.label_names), base_pred),
                baseline_constrained_pred=decode(tuple(task.label_names), base_c_pred),
                event_pred=decode(tuple(task.label_names), event_pred),
                event_constrained_pred=decode(tuple(task.label_names), event_c_pred),
                baseline_p_event=base_p,
                event_p_event=event_p,
                **uncertainty,
                baseline_legal=base_legal,
                event_legal=event_legal,
                baseline_exact=tuple(base_pred) == tuple(gold),
                event_exact=tuple(event_pred) == tuple(gold),
                baseline_char_acc=char_acc(base_pred, gold),
                event_char_acc=char_acc(event_pred, gold),
                hidden_conflict=base_c_legal and base_p < 0.5,
            )
        )
    return rows


def semi_real_cases(task_names: list[str], seed_count: int) -> list[DiagnosticCase]:
    tasks = [task for task in SEMI_TASKS if task.name in set(task_names)]
    setting = ProbeSetting(
        block="diagnostic",
        name="labeled25_unlabeled100",
        labeled_size=25,
        unlabeled_size=100,
        dev_size=300,
        epochs=5,
        lr=0.08,
        seeds=tuple(range(seed_count)),
        variants=("B0_unconstrained", "B4_semi_event_0.1"),
    )
    rows: list[DiagnosticCase] = []
    for task in tasks:
        label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
        for seed in setting.seeds:
            labeled_ds = make_semi_dataset(task, f"{task.name}_labeled", setting.labeled_size, seed=1100 + seed)
            unlabeled_ds = make_semi_dataset(task, f"{task.name}_unlabeled", setting.unlabeled_size, seed=2200 + seed)
            dev_ds = make_semi_dataset(task, f"{task.name}_dev", setting.dev_size, seed=3300 + seed)
            vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens + dev_ds.tokens)
            labeled = encode(labeled_ds, vocab, label_to_idx)
            unlabeled = [word_ids for word_ids, _labels in encode(unlabeled_ds, vocab, label_to_idx)]
            dev = encode(dev_ds, vocab, label_to_idx)
            rows.extend(evaluate_cases(source="semi_real", task=task, labeled=labeled, unlabeled=unlabeled, dev=dev, vocab=vocab, seed=seed))
    return rows


def real_source_cases(task_names: list[str], seed_count: int) -> list[DiagnosticCase]:
    invoices, stocks = load_field_values()
    task_set = set(task_names)
    tasks = [task for task in REAL_TASKS if task.name in task_set]
    pools = {task.name: build_pool(task, invoices, stocks) for task in tasks}
    rows: list[DiagnosticCase] = []
    for task in tasks:
        label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
        for seed in range(seed_count):
            labeled_vals, unlabeled_vals, dev_vals = split_pool(
                pools[task.name],
                labeled_size=25,
                unlabeled_size=100,
                dev_size=300,
                seed=1000 + seed,
            )
            labeled_ds = make_real_dataset(task, labeled_vals, f"{task.name}_labeled", seed=1200 + seed)
            unlabeled_ds = make_real_dataset(task, unlabeled_vals, f"{task.name}_unlabeled", seed=2200 + seed)
            dev_ds = make_real_dataset(task, dev_vals, f"{task.name}_dev", seed=3200 + seed)
            vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens + dev_ds.tokens)
            labeled = encode(labeled_ds, vocab, label_to_idx)
            unlabeled = [word_ids for word_ids, _labels in encode(unlabeled_ds, vocab, label_to_idx)]
            dev = encode(dev_ds, vocab, label_to_idx)
            rows.extend(evaluate_cases(source="real_source", task=task, labeled=labeled, unlabeled=unlabeled, dev=dev, vocab=vocab, seed=seed))
    return rows


def quantile_summary(cases: list[DiagnosticCase], *, q: float = 0.2) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[DiagnosticCase]] = {}
    for case in cases:
        grouped.setdefault((case.source, case.task), []).append(case)
    rows: list[dict[str, object]] = []
    for (source, task), group in sorted(grouped.items()):
        ordered = sorted(group, key=lambda row: row.baseline_p_event)
        n = max(1, int(len(ordered) * q))
        bottom = ordered[:n]
        top = ordered[-n:]
        rows.append(
            {
                "source": source,
                "task": task,
                "cases": len(group),
                "quantile": q,
                "bottom_mean_baseline_p": mean(row.baseline_p_event for row in bottom),
                "top_mean_baseline_p": mean(row.baseline_p_event for row in top),
                "bottom_baseline_exact_error": mean(1.0 - float(row.baseline_exact) for row in bottom),
                "top_baseline_exact_error": mean(1.0 - float(row.baseline_exact) for row in top),
                "bottom_event_exact_error": mean(1.0 - float(row.event_exact) for row in bottom),
                "top_event_exact_error": mean(1.0 - float(row.event_exact) for row in top),
                "bottom_baseline_char_error": mean(1.0 - row.baseline_char_acc for row in bottom),
                "top_baseline_char_error": mean(1.0 - row.baseline_char_acc for row in top),
                "bottom_event_char_error": mean(1.0 - row.event_char_acc for row in bottom),
                "top_event_char_error": mean(1.0 - row.event_char_acc for row in top),
                "bottom_hidden_conflict_rate": mean(float(row.hidden_conflict) for row in bottom),
                "top_hidden_conflict_rate": mean(float(row.hidden_conflict) for row in top),
                "mean_event_p_shift": mean(row.event_p_event - row.baseline_p_event for row in group),
            }
        )
    return rows


def write_report(output_dir: Path, summary: list[dict[str, object]]) -> None:
    lines = [
        "# Posterior Event Risk Diagnostic Report",
        "",
        "This report is generated by a short CPU diagnostic rerun on representative tasks.",
        "It is not a benchmark and should be used as a pre-paper diagnostic gate.",
        "",
        "## Quantile Summary",
        "",
        "| source | task | cases | bottom P | top P | bottom base err | top base err | bottom event err | top event err | hidden bottom | hidden top |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| {source} | {task} | {cases} | {bp:.4f} | {tp:.4f} | {bbe:.4f} | {tbe:.4f} | {bee:.4f} | {tee:.4f} | {bh:.4f} | {th:.4f} |".format(
                source=row["source"],
                task=row["task"],
                cases=int(row["cases"]),
                bp=float(row["bottom_mean_baseline_p"]),
                tp=float(row["top_mean_baseline_p"]),
                bbe=float(row["bottom_baseline_exact_error"]),
                tbe=float(row["top_baseline_exact_error"]),
                bee=float(row["bottom_event_exact_error"]),
                tee=float(row["top_event_exact_error"]),
                bh=float(row["bottom_hidden_conflict_rate"]),
                th=float(row["top_hidden_conflict_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation Rules",
            "",
            "- If bottom baseline error is higher than top baseline error, low `P_theta(L|x)` is useful as a risk signal.",
            "- If hidden-conflict rate concentrates in the bottom quantile, hard constraints can mask posterior uncertainty.",
            "- If event exact error does not improve, the diagnostic claim can still survive while task-improvement claims remain limited.",
            "- This report does not prove benchmark usefulness or superiority over local-style B5/B6 baselines.",
            "",
        ]
    )
    (output_dir / "POSTERIOR_EVENT_RISK_DIAGNOSTIC_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/results/event_training/formal_pre_paper/diagnostic")
    parser.add_argument("--seed-count", type=int, default=3)
    parser.add_argument("--semi-tasks", nargs="*", default=["product_code", "amount"])
    parser.add_argument("--real-tasks", nargs="*", default=["stock_5d", "invoice_6d"])
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = semi_real_cases(args.semi_tasks, args.seed_count) + real_source_cases(args.real_tasks, args.seed_count)
    case_dicts = [asdict(row) for row in cases]
    summary = quantile_summary(cases)
    write_table(output_dir / "diagnostic_cases.csv", case_dicts)
    write_table(output_dir / "diagnostic_summary.csv", summary)
    write_report(output_dir, summary)


if __name__ == "__main__":
    main()
