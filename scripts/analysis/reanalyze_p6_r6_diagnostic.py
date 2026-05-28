"""Reanalyze P6 R6a diagnostic cases with ranking metrics and risk curves."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


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


def group_cases(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["source"], row["task"])].append(row)
    return groups


def metric_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    groups = group_cases(rows)
    groups[("all", "all")] = rows
    out: list[dict[str, object]] = []
    for (source, task), group in sorted(groups.items()):
        risk_scores = [1.0 - float(row["baseline_p_event"]) for row in group]
        exact_errors = [0 if parse_bool(row["baseline_exact"]) else 1 for row in group]
        char_errors = [1.0 - float(row["baseline_char_acc"]) for row in group]
        hidden = [1 if parse_bool(row["hidden_conflict"]) else 0 for row in group]
        bottom = sorted(group, key=lambda row: float(row["baseline_p_event"]))[: max(1, len(group) // 5)]
        out.append(
            {
                "source": source,
                "task": task,
                "cases": len(group),
                "exact_error_rate": mean(exact_errors),
                "hidden_conflict_rate": mean(hidden),
                "auroc_exact_error": auroc(exact_errors, risk_scores),
                "auprc_exact_error": average_precision(exact_errors, risk_scores),
                "spearman_risk_char_error": spearman(risk_scores, char_errors),
                "bottom20_exact_error": mean(0 if parse_bool(row["baseline_exact"]) else 1 for row in bottom),
                "bottom20_hidden_conflict_rate": mean(1 if parse_bool(row["hidden_conflict"]) else 0 for row in bottom),
                "bottom20_mean_risk_score": mean(1.0 - float(row["baseline_p_event"]) for row in bottom),
            }
        )
    return out


def risk_curve_rows(rows: list[dict[str, str]], *, bins: int = 10) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    groups = group_cases(rows)
    groups[("all", "all")] = rows
    for (source, task), group in sorted(groups.items()):
        ordered = sorted(group, key=lambda row: float(row["baseline_p_event"]))
        n = len(ordered)
        for decile in range(bins):
            start = decile * n // bins
            end = (decile + 1) * n // bins
            chunk = ordered[start:end]
            out.append(
                {
                    "source": source,
                    "task": task,
                    "risk_decile": decile + 1,
                    "cases": len(chunk),
                    "mean_baseline_p_event": mean(float(row["baseline_p_event"]) for row in chunk),
                    "exact_error_rate": mean(0 if parse_bool(row["baseline_exact"]) else 1 for row in chunk),
                    "char_error_rate": mean(1.0 - float(row["baseline_char_acc"]) for row in chunk),
                    "hidden_conflict_rate": mean(1 if parse_bool(row["hidden_conflict"]) else 0 for row in chunk),
                }
            )
    return out


def fmt(value: object) -> str:
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def write_report(path: Path, metrics: list[dict[str, object]], risk_rows: list[dict[str, object]]) -> None:
    all_row = next(row for row in metrics if row["source"] == "all" and row["task"] == "all")
    lines = [
        "# P6 R6a Diagnostic Reanalysis",
        "",
        "This reanalysis uses the existing R6a diagnostic cases. No new experiment or HPC run was performed.",
        "",
        "## Overall Metrics",
        "",
        "| cases | exact error | hidden conflict | AUROC exact error | AUPRC exact error | Spearman risk-char error |",
        "|---:|---:|---:|---:|---:|---:|",
        "| {cases} | {err} | {hidden} | {auroc} | {auprc} | {rho} |".format(
            cases=all_row["cases"],
            err=fmt(all_row["exact_error_rate"]),
            hidden=fmt(all_row["hidden_conflict_rate"]),
            auroc=fmt(all_row["auroc_exact_error"]),
            auprc=fmt(all_row["auprc_exact_error"]),
            rho=fmt(all_row["spearman_risk_char_error"]),
        ),
        "",
        "## Per-Task Metrics",
        "",
        "| source | task | cases | AUROC | AUPRC | Spearman | bottom20 exact err | bottom20 hidden conflict |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in metrics:
        if row["source"] == "all":
            continue
        lines.append(
            "| {source} | {task} | {cases} | {auroc} | {auprc} | {rho} | {b20} | {hc} |".format(
                source=row["source"],
                task=row["task"],
                cases=row["cases"],
                auroc=fmt(row["auroc_exact_error"]),
                auprc=fmt(row["auprc_exact_error"]),
                rho=fmt(row["spearman_risk_char_error"]),
                b20=fmt(row["bottom20_exact_error"]),
                hc=fmt(row["bottom20_hidden_conflict_rate"]),
            )
        )
    lines.extend(
        [
            "",
            "## Overall Risk Curve",
            "",
            "| risk decile | mean P(L|x) | exact error | char error | hidden conflict |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for row in risk_rows:
        if row["source"] == "all" and row["task"] == "all":
            lines.append(
                "| {decile} | {p} | {err} | {char} | {hidden} |".format(
                    decile=row["risk_decile"],
                    p=fmt(row["mean_baseline_p_event"]),
                    err=fmt(row["exact_error_rate"]),
                    char=fmt(row["char_error_rate"]),
                    hidden=fmt(row["hidden_conflict_rate"]),
                )
            )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Allowed: `P_theta(L|x)` provides a useful ranking/risk signal for the audited field-style tasks.",
            "",
            "Not allowed: this does not prove calibration, universal error prediction, or benchmark superiority.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        default="experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/r6a_field_diagnostic_formal/diagnostic_cases.csv",
    )
    parser.add_argument("--output-dir", default="experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic")
    args = parser.parse_args()

    rows = read_csv(Path(args.cases))
    metrics = metric_rows(rows)
    risk_rows = risk_curve_rows(rows)
    output_dir = Path(args.output_dir)
    write_csv(output_dir / "diagnostic_ranking_metrics.csv", metrics)
    write_csv(output_dir / "diagnostic_risk_curve.csv", risk_rows)
    write_report(output_dir / "P6_R6A_DIAGNOSTIC_REANALYSIS.md", metrics, risk_rows)
    print(f"WROTE {output_dir / 'diagnostic_ranking_metrics.csv'}")
    print(f"WROTE {output_dir / 'diagnostic_risk_curve.csv'}")
    print(f"WROTE {output_dir / 'P6_R6A_DIAGNOSTIC_REANALYSIS.md'}")


if __name__ == "__main__":
    main()
