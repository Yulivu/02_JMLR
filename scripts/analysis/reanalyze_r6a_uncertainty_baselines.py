"""Compare R6a event risk against standard uncertainty baselines when available."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


DEFAULT_CASES = Path("experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/r6a_field_diagnostic_formal/diagnostic_cases.csv")
DEFAULT_OUTPUT = Path("experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic")

BASELINES = {
    "event_risk_1_minus_p": ("baseline_p_event", lambda value: 1.0 - value),
    "token_marginal_entropy": ("baseline_token_marginal_entropy", lambda value: value),
    "sequence_entropy": ("baseline_sequence_entropy", lambda value: value),
    "viterbi_margin_inverse": ("baseline_viterbi_margin", lambda value: -value),
    "max_sequence_probability_inverse": ("baseline_max_sequence_prob", lambda value: -value),
    "neg_log_viterbi_probability": ("baseline_neg_log_viterbi_prob", lambda value: value),
}

GENERIC_BASELINES = {
    "token_marginal_entropy": BASELINES["token_marginal_entropy"],
    "sequence_entropy": BASELINES["sequence_entropy"],
    "viterbi_margin_inverse": BASELINES["viterbi_margin_inverse"],
    "max_sequence_probability_inverse": BASELINES["max_sequence_probability_inverse"],
    "neg_log_viterbi_probability": BASELINES["neg_log_viterbi_probability"],
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def parse_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def rankdata(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) <= 1:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = sum((x - mx) ** 2 for x in xs) ** 0.5
    den_y = sum((y - my) ** 2 for y in ys) ** 0.5
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)


def spearman(xs: list[float], ys: list[float]) -> float:
    return pearson(rankdata(xs), rankdata(ys))


def auroc(labels: list[int], scores: list[float]) -> float:
    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return 0.0
    ranks = rankdata(scores)
    pos_rank_sum = sum(rank for rank, label in zip(ranks, labels) if label)
    return (pos_rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


def average_precision(labels: list[int], scores: list[float]) -> float:
    positives = sum(labels)
    if positives == 0:
        return 0.0
    ordered = sorted(zip(scores, labels), key=lambda item: item[0], reverse=True)
    tp = 0
    precision_sum = 0.0
    for idx, (_score, label) in enumerate(ordered, start=1):
        if label:
            tp += 1
            precision_sum += tp / idx
    return precision_sum / positives


def groups(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["source"], row["task"])].append(row)
    grouped[("all", "all")] = rows
    return grouped


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for (source, task), group in sorted(groups(rows).items()):
        labels = [0 if parse_bool(row["baseline_exact"]) else 1 for row in group]
        char_errors = [1.0 - float(row["baseline_char_acc"]) for row in group]
        for name, (field, transform) in BASELINES.items():
            scores = [transform(float(row[field])) for row in group]
            ordered = sorted(zip(scores, labels), key=lambda item: item[0], reverse=True)
            n = max(1, len(ordered) // 5)
            bottom = ordered[:n]
            top = ordered[-n:]
            out.append(
                {
                    "source": source,
                    "task": task,
                    "baseline": name,
                    "cases": len(group),
                    "exact_error_rate": mean(labels),
                    "auroc_exact_error": auroc(labels, scores),
                    "auprc_exact_error": average_precision(labels, scores),
                    "spearman_char_error": spearman(scores, char_errors),
                    "top20_risk_exact_error": mean(label for _score, label in bottom),
                    "bottom20_risk_exact_error": mean(label for _score, label in top),
                    "risk_gap": mean(label for _score, label in bottom) - mean(label for _score, label in top),
                }
            )
    return out


def complementarity_rows(rows: list[dict[str, str]], *, bins: int = 10) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    event_scores = [1.0 - float(row["baseline_p_event"]) for row in rows]
    labels = [0 if parse_bool(row["baseline_exact"]) else 1 for row in rows]
    for baseline_name, (field, transform) in GENERIC_BASELINES.items():
        generic_scores = [transform(float(row[field])) for row in rows]
        ordered_indices = sorted(range(len(rows)), key=lambda idx: generic_scores[idx])
        weighted_gap_sum = 0.0
        total_cases = 0
        bin_count = 0
        for bin_idx in range(bins):
            start = bin_idx * len(ordered_indices) // bins
            end = (bin_idx + 1) * len(ordered_indices) // bins
            chunk = ordered_indices[start:end]
            if len(chunk) < 2:
                continue
            median_event = sorted(event_scores[idx] for idx in chunk)[len(chunk) // 2]
            low = [idx for idx in chunk if event_scores[idx] <= median_event]
            high = [idx for idx in chunk if event_scores[idx] > median_event]
            if not low or not high:
                continue
            low_error = mean(labels[idx] for idx in low)
            high_error = mean(labels[idx] for idx in high)
            gap = high_error - low_error
            weighted_gap_sum += gap * len(chunk)
            total_cases += len(chunk)
            bin_count += 1
            out.append(
                {
                    "baseline": baseline_name,
                    "generic_risk_bin": bin_idx + 1,
                    "cases": len(chunk),
                    "low_event_cases": len(low),
                    "high_event_cases": len(high),
                    "low_event_exact_error": low_error,
                    "high_event_exact_error": high_error,
                    "event_within_bin_error_gap": gap,
                    "mean_generic_risk": mean(generic_scores[idx] for idx in chunk),
                    "mean_event_risk": mean(event_scores[idx] for idx in chunk),
                }
            )
        if total_cases:
            out.append(
                {
                    "baseline": baseline_name,
                    "generic_risk_bin": "weighted_mean",
                    "cases": total_cases,
                    "low_event_cases": "",
                    "high_event_cases": "",
                    "low_event_exact_error": "",
                    "high_event_exact_error": "",
                    "event_within_bin_error_gap": weighted_gap_sum / total_cases,
                    "mean_generic_risk": "",
                    "mean_event_risk": "",
                }
            )
        elif bin_count == 0:
            out.append(
                {
                    "baseline": baseline_name,
                    "generic_risk_bin": "weighted_mean",
                    "cases": 0,
                    "low_event_cases": "",
                    "high_event_cases": "",
                    "low_event_exact_error": "",
                    "high_event_exact_error": "",
                    "event_within_bin_error_gap": 0.0,
                    "mean_generic_risk": "",
                    "mean_event_risk": "",
                }
            )
    return out


def missing_fields(rows: list[dict[str, str]]) -> list[str]:
    if not rows:
        return []
    fields = set(rows[0])
    return [field for field, _transform in BASELINES.values() if field not in fields]


def write_missing_plan(path: Path, missing: list[str]) -> None:
    lines = [
        "# R6a Uncertainty Baseline Reanalysis Plan",
        "",
        "The existing downloaded R6a `diagnostic_cases.csv` does not contain all uncertainty baseline fields needed for a fair comparison.",
        "",
        "Missing fields:",
        "",
    ]
    lines.extend(f"- `{field}`" for field in missing)
    lines.extend(
        [
            "",
            "Implemented preparation:",
            "",
            "- `src/tensor_crf_jmlr/event_training/posterior_event_diagnostic.py` now writes Viterbi probability, Viterbi margin, token marginal entropy, and sequence entropy fields on rerun.",
            "- This script will produce AUROC/AUPRC/Spearman/quantile-gap tables once those enriched cases are available.",
            "",
            "Rerun command:",
            "",
            "```powershell",
            "python -m tensor_crf_jmlr.event_training.posterior_event_diagnostic --output-dir experiments/runs/local_checks/r6a_uncertainty_enriched --seed-count 10 --semi-tasks product_code amount date dose --real-tasks stock_5d invoice_6d invoice_c6d",
            "python scripts/analysis/reanalyze_r6a_uncertainty_baselines.py --cases experiments/runs/local_checks/r6a_uncertainty_enriched/diagnostic_cases.csv --output-dir experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic",
            "```",
            "",
            "Claim boundary: do not report uncertainty-baseline superiority until the enriched rerun is produced and audited.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_report(path: Path, rows: list[dict[str, object]], complementarity: list[dict[str, object]]) -> None:
    overall = [row for row in rows if row["source"] == "all" and row["task"] == "all"]
    lines = [
        "# R6a Uncertainty Baseline Reanalysis",
        "",
        "This report compares event risk against available uncertainty baselines on exact-error ranking.",
        "",
        "| baseline | AUROC | AUPRC | Spearman char error | top20 risk error | bottom20 risk error | risk gap |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in overall:
        lines.append(
            "| {baseline} | {auroc:.4f} | {auprc:.4f} | {rho:.4f} | {top:.4f} | {bottom:.4f} | {gap:.4f} |".format(
                baseline=row["baseline"],
                auroc=float(row["auroc_exact_error"]),
                auprc=float(row["auprc_exact_error"]),
                rho=float(row["spearman_char_error"]),
                top=float(row["top20_risk_exact_error"]),
                bottom=float(row["bottom20_risk_exact_error"]),
                gap=float(row["risk_gap"]),
            )
        )
    lines.extend(
        [
            "",
            "## Complementarity Check",
            "",
            "Within each generic-uncertainty decile, cases are split by event risk `1 - P_theta(L|x)`.",
            "A positive weighted gap means high event risk still has higher exact-error rate after controlling coarsely for the generic baseline.",
            "",
            "| controlled generic baseline | weighted within-bin event-risk error gap |",
            "|---|---:|",
        ]
    )
    for row in complementarity:
        if row["generic_risk_bin"] != "weighted_mean":
            continue
        lines.append(
            "| {baseline} | {gap:.4f} |".format(
                baseline=row["baseline"],
                gap=float(row["event_within_bin_error_gap"]),
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The event-risk score has positive exact-error ranking signal, but standard uncertainty baselines are stronger overall in this rerun.",
            "Therefore the paper should not claim diagnostic superiority over entropy, margin, or max-probability uncertainty.",
            "The complementarity check asks only whether event risk carries some rule-specific residual signal within coarse uncertainty strata; it is not a causal or calibration result.",
            "The safe claim is narrower: `1 - P_theta(L|x)` is an interpretable rule-specific posterior-consistency signal with positive risk-ranking value, not a universal or dominant uncertainty score.",
            "",
            "Boundary: this is ranking evidence only, not calibration and not benchmark superiority.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    rows = read_csv(Path(args.cases))
    output_dir = Path(args.output_dir)
    missing = missing_fields(rows)
    if missing:
        write_missing_plan(output_dir / "R6A_UNCERTAINTY_BASELINE_PLAN.md", missing)
        print(f"WROTE {output_dir / 'R6A_UNCERTAINTY_BASELINE_PLAN.md'}")
        return
    metrics = metric_rows(rows)
    complementarity = complementarity_rows(rows)
    write_csv(output_dir / "r6a_uncertainty_baseline_metrics.csv", metrics)
    write_csv(output_dir / "r6a_uncertainty_complementarity.csv", complementarity)
    write_report(output_dir / "R6A_UNCERTAINTY_BASELINE_REANALYSIS.md", metrics, complementarity)
    print(f"WROTE {output_dir / 'r6a_uncertainty_baseline_metrics.csv'}")
    print(f"WROTE {output_dir / 'r6a_uncertainty_complementarity.csv'}")
    print(f"WROTE {output_dir / 'R6A_UNCERTAINTY_BASELINE_REANALYSIS.md'}")


if __name__ == "__main__":
    main()
