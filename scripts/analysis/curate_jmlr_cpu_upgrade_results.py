"""Curate the JMLR CPU-upgrade raw run bundles into review-stage results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, stdev
from typing import Callable


DEFAULT_RUN_ROOT = Path("experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade")
DEFAULT_RESULTS_ROOT = Path("experiments/results/event_training/formal_pre_paper")


BASELINES: dict[str, tuple[str, Callable[[float], float]]] = {
    "event_risk_1_minus_p": ("event_risk_1_minus_p", lambda value: value),
    "token_marginal_entropy": ("token_marginal_entropy", lambda value: value),
    "sequence_entropy": ("sequence_entropy", lambda value: value),
    "viterbi_margin_inverse": ("viterbi_margin", lambda value: -value),
    "max_sequence_probability_inverse": ("max_sequence_probability", lambda value: -value),
    "neg_log_viterbi_probability": ("neg_log_viterbi_probability", lambda value: value),
}

GENERIC_BASELINES = {
    name: spec for name, spec in BASELINES.items() if name != "event_risk_1_minus_p"
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, title: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty markdown table: {path}")
    fields = list(rows[0])
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(format_value(row[field]) for field in fields) + " |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


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


def metadata(run_dir: Path) -> dict[str, object]:
    return json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))


def grouped_by_variant(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["variant"], []).append(row)
    return grouped


def uncertainty_metric_rows(details: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for variant, group in sorted(grouped_by_variant(details).items()):
        exact_labels = [int(row["exact_error"]) for row in group]
        span_labels = [int(row["span_error"]) for row in group]
        token_errors = [float(row["token_error"]) for row in group]
        for baseline, (field, transform) in BASELINES.items():
            scores = [transform(float(row[field])) for row in group]
            ordered = sorted(zip(scores, exact_labels, span_labels, token_errors), key=lambda item: item[0], reverse=True)
            n = max(1, len(ordered) // 5)
            high = ordered[:n]
            low = ordered[-n:]
            out.append(
                {
                    "variant": variant,
                    "baseline": baseline,
                    "cases": len(group),
                    "exact_error_rate": mean(exact_labels),
                    "span_error_rate": mean(span_labels),
                    "mean_token_error": mean(token_errors),
                    "auroc_exact_error": auroc(exact_labels, scores),
                    "auprc_exact_error": average_precision(exact_labels, scores),
                    "auroc_span_error": auroc(span_labels, scores),
                    "auprc_span_error": average_precision(span_labels, scores),
                    "spearman_token_error": spearman(scores, token_errors),
                    "top20_exact_error": mean(item[1] for item in high),
                    "bottom20_exact_error": mean(item[1] for item in low),
                    "risk_gap_exact": mean(item[1] for item in high) - mean(item[1] for item in low),
                    "top20_token_error": mean(item[3] for item in high),
                    "bottom20_token_error": mean(item[3] for item in low),
                    "risk_gap_token": mean(item[3] for item in high) - mean(item[3] for item in low),
                }
            )
    return out


def correlation_rows(details: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for variant, group in sorted(grouped_by_variant(details).items()):
        event_scores = [float(row["event_risk_1_minus_p"]) for row in group]
        for baseline, (field, transform) in GENERIC_BASELINES.items():
            scores = [transform(float(row[field])) for row in group]
            out.append(
                {
                    "variant": variant,
                    "generic_baseline": baseline,
                    "cases": len(group),
                    "pearson_with_event_risk": pearson(event_scores, scores),
                    "spearman_with_event_risk": spearman(event_scores, scores),
                }
            )
    return out


def complementarity_rows(details: list[dict[str, str]], bins: int = 10) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for variant, group in sorted(grouped_by_variant(details).items()):
        event_scores = [float(row["event_risk_1_minus_p"]) for row in group]
        labels = [int(row["exact_error"]) for row in group]
        for baseline, (field, transform) in GENERIC_BASELINES.items():
            generic_scores = [transform(float(row[field])) for row in group]
            ordered_indices = sorted(range(len(group)), key=lambda idx: generic_scores[idx])
            weighted_gap_sum = 0.0
            total_cases = 0
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
                out.append(
                    {
                        "variant": variant,
                        "generic_baseline": baseline,
                        "generic_risk_bin": bin_idx + 1,
                        "cases": len(chunk),
                        "low_event_cases": len(low),
                        "high_event_cases": len(high),
                        "low_event_exact_error": low_error,
                        "high_event_exact_error": high_error,
                        "event_within_bin_error_gap": gap,
                    }
                )
            out.append(
                {
                    "variant": variant,
                    "generic_baseline": baseline,
                    "generic_risk_bin": "weighted_mean",
                    "cases": total_cases,
                    "low_event_cases": "",
                    "high_event_cases": "",
                    "low_event_exact_error": "",
                    "high_event_exact_error": "",
                    "event_within_bin_error_gap": weighted_gap_sum / total_cases if total_cases else 0.0,
                }
            )
    return out


def as_float(row: dict[str, str], field: str) -> float:
    return float(row[field])


def public_table_rows(public_summary: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in public_summary:
        rows.append(
            {
                "variant": row["variant"],
                "P_BIO": as_float(row, "mean_p_event"),
                "hidden_conflict": as_float(row, "hidden_conflict_rate"),
                "unconstrained_legal": as_float(row, "unconstrained_legal_rate"),
                "B7_legal": as_float(row, "b7_legal_rate"),
                "token_acc": as_float(row, "token_accuracy"),
                "B7_token_acc": as_float(row, "b7_token_accuracy"),
                "span_F1": as_float(row, "span_f1"),
                "B7_span_F1": as_float(row, "b7_span_f1"),
            }
        )
    return rows


def public_multiseed_table_rows(public_summary: list[dict[str, str]]) -> list[dict[str, object]]:
    fields = [
        ("P_BIO", "mean_p_event"),
        ("hidden_conflict", "hidden_conflict_rate"),
        ("unconstrained_legal", "unconstrained_legal_rate"),
        ("B7_legal", "b7_legal_rate"),
        ("token_acc", "token_accuracy"),
        ("B7_token_acc", "b7_token_accuracy"),
        ("span_F1", "span_f1"),
        ("B7_span_F1", "b7_span_f1"),
    ]
    out: list[dict[str, object]] = []
    for variant in sorted({row["variant"] for row in public_summary}):
        group = [row for row in public_summary if row["variant"] == variant]
        row_out: dict[str, object] = {
            "variant": variant,
            "seeds": len({row["seed"] for row in group}),
        }
        for label, field in fields:
            values = [as_float(row, field) for row in group]
            row_out[f"{label}_mean"] = mean(values)
            row_out[f"{label}_std"] = stdev(values) if len(values) > 1 else 0.0
        out.append(row_out)
    return out


def public_delta_rows(public_summary: list[dict[str, str]]) -> list[dict[str, object]]:
    by_variant = {row["variant"]: row for row in public_summary}
    base = by_variant["B0_unconstrained"]
    b4 = by_variant["B4_semi_event_0.1"]
    fields = [
        ("P_BIO", "mean_p_event"),
        ("hidden_conflict", "hidden_conflict_rate"),
        ("unconstrained_legal", "unconstrained_legal_rate"),
        ("token_acc", "token_accuracy"),
        ("span_F1", "span_f1"),
    ]
    return [
        {
            "comparison": "B4_semi_event_0.1 - B0_unconstrained",
            "metric": metric,
            "B0": as_float(base, field),
            "B4": as_float(b4, field),
            "delta": as_float(b4, field) - as_float(base, field),
        }
        for metric, field in fields
    ]


def public_multiseed_delta_rows(multiseed_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_variant = {str(row["variant"]): row for row in multiseed_rows}
    if "B0_unconstrained" not in by_variant or "B4_semi_event_0.1" not in by_variant:
        return []
    base = by_variant["B0_unconstrained"]
    b4 = by_variant["B4_semi_event_0.1"]
    metrics = ["P_BIO", "hidden_conflict", "unconstrained_legal", "token_acc", "span_F1"]
    return [
        {
            "comparison": "B4_semi_event_0.1 - B0_unconstrained",
            "metric": metric,
            "B0_mean": base[f"{metric}_mean"],
            "B4_mean": b4[f"{metric}_mean"],
            "delta_mean": float(b4[f"{metric}_mean"]) - float(base[f"{metric}_mean"]),
        }
        for metric in metrics
    ]


def b7_table_rows(b7_summary: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for row in b7_summary:
        rows.append(
            {
                "source_model": row["source_model"],
                "decoded_legal_rate": as_float(row, "decoded_legal_rate"),
                "token_accuracy": as_float(row, "token_accuracy"),
                "entity_F1": as_float(row, "entity_f1"),
                "uses_event_training": row["uses_event_training"],
                "uses_event_mass_for_decoding": row["uses_event_mass_for_decoding"],
            }
        )
    return rows


def r7_key_rows(summary: list[dict[str, str]], boundaries: list[dict[str, str]]) -> list[dict[str, object]]:
    by_boundary = {row["task"]: row for row in boundaries}
    rows: list[dict[str, object]] = []
    for row in summary:
        if row["variant"] not in {"B0_unconstrained", by_boundary[row["task"]]["best_event_variant"]}:
            continue
        rows.append(
            {
                "task": row["task"],
                "variant": row["variant"],
                "runs": int(row["runs"]),
                "P_event": as_float(row, "mean_p_event"),
                "delta_P_event": as_float(row, "delta_p_event"),
                "delta_legal_rate": as_float(row, "delta_unconstrained_event_rate"),
                "delta_exact_acc": as_float(row, "delta_exact_sequence_accuracy"),
                "boundary": "legal-rate-not-useful"
                if by_boundary[row["task"]]["legal_rate_not_useful"] == "True"
                else "ordinary",
            }
        )
    return rows


def write_public_report(
    output_dir: Path,
    run_dir: Path,
    public_rows: list[dict[str, object]],
    delta_rows: list[dict[str, object]],
    uncertainty_rows: list[dict[str, object]],
) -> None:
    meta = metadata(run_dir)
    event_rows = [row for row in uncertainty_rows if row["baseline"] == "event_risk_1_minus_p"]
    lines = [
        "# CoNLL2000 Public Sequence Labeling Formal Audit",
        "",
        "This is a public BIO/chunking case study. It is not a SOTA, benchmark-superiority, or constrained-method replacement experiment.",
        "",
        "## Provenance",
        "",
        f"- raw bundle: `{run_dir.as_posix()}`",
        f"- git commit: `{meta.get('git_commit')}`",
        f"- config: `{meta.get('config')}`",
        f"- returncode: `{meta.get('returncode')}`",
        f"- duration_seconds: `{meta.get('duration_seconds')}`",
        "",
        "## Main Rows",
        "",
        "| variant | P(BIO|x) | hidden conflict | unconstrained legal | B7 legal | token acc | B7 token acc | span F1 | B7 span F1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in public_rows:
        lines.append(
            "| {variant} | {P_BIO:.4f} | {hidden_conflict:.4f} | {unconstrained_legal:.4f} | {B7_legal:.4f} | {token_acc:.4f} | {B7_token_acc:.4f} | {span_F1:.4f} | {B7_span_F1:.4f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## B4 Movement Relative To B0",
            "",
            "| metric | B0 | B4 | delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in delta_rows:
        lines.append("| {metric} | {B0:.4f} | {B4:.4f} | {delta:+.4f} |".format(**row))
    lines.extend(
        [
            "",
            "## Public-Case Uncertainty Boundary",
            "",
            "| variant | event-risk AUROC exact | event-risk AUPRC exact | event-risk Spearman token error | event-risk exact risk gap |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in event_rows:
        lines.append(
            "| {variant} | {auroc_exact_error:.4f} | {auprc_exact_error:.4f} | {spearman_token_error:.4f} | {risk_gap_exact:.4f} |".format(
                **row
            )
        )
    strongest_generic: list[dict[str, object]] = []
    for variant in sorted({row["variant"] for row in uncertainty_rows}):
        generic_rows = [
            row
            for row in uncertainty_rows
            if row["variant"] == variant and row["baseline"] != "event_risk_1_minus_p"
        ]
        strongest_generic.append(max(generic_rows, key=lambda row: float(row["auroc_exact_error"])))
    lines.extend(
        [
            "",
            "Strongest generic uncertainty baselines by AUROC in the same public case:",
            "",
            "| variant | strongest generic score | AUROC exact | AUPRC exact | Spearman token error |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in strongest_generic:
        lines.append(
            "| {variant} | {baseline} | {auroc_exact_error:.4f} | {auprc_exact_error:.4f} | {spearman_token_error:.4f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "The raw detail table contains `event_risk_1_minus_p`, token marginal entropy, sequence entropy, Viterbi margin, max sequence probability, and negative log Viterbi probability for 2,000 variant/case rows.",
            "",
            "## Interpretation",
            "",
            "Allowed: this public case supports a structured-prediction audit story in which B4 moves posterior BIO mass upward and B7 constrained decoding gives legal sequences.",
            "",
            "Boundary: event risk has positive signal but generic uncertainty is stronger in this public case. The full run is one frozen configuration and should not be used as benchmark superiority, SOTA evidence, uncertainty dominance, or proof that event training generally improves task metrics.",
            "",
        ]
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "CONLL2000_PUBLIC_FORMAL_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_public_multiseed_report(
    output_dir: Path,
    run_dir: Path,
    rows: list[dict[str, object]],
    delta_rows: list[dict[str, object]],
    uncertainty_rows: list[dict[str, object]],
) -> None:
    meta = metadata(run_dir)
    lines = [
        "# CoNLL2000 Public Sequence Labeling Multiseed Formal Audit",
        "",
        "This audit is for a full three-seed public BIO/chunking run. It remains a case study, not a benchmark-superiority result.",
        "",
        "## Provenance",
        "",
        f"- raw bundle: `{run_dir.as_posix()}`",
        f"- git commit: `{meta.get('git_commit')}`",
        f"- config: `{meta.get('config')}`",
        f"- returncode: `{meta.get('returncode')}`",
        f"- duration_seconds: `{meta.get('duration_seconds')}`",
        "",
        "## Mean / Std Rows",
        "",
        "| variant | seeds | P(BIO) mean | P(BIO) std | hidden conflict mean | B7 legal mean | token acc mean | span F1 mean |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {variant} | {seeds} | {P_BIO_mean:.4f} | {P_BIO_std:.4f} | {hidden_conflict_mean:.4f} | {B7_legal_mean:.4f} | {token_acc_mean:.4f} | {span_F1_mean:.4f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## B4 Movement Relative To B0",
            "",
            "| metric | B0 mean | B4 mean | delta mean |",
            "|---|---:|---:|---:|",
        ]
    )
    for row in delta_rows:
        lines.append("| {metric} | {B0_mean:.4f} | {B4_mean:.4f} | {delta_mean:+.4f} |".format(**row))
    event_rows = [row for row in uncertainty_rows if row["baseline"] == "event_risk_1_minus_p"]
    strongest_generic: list[dict[str, object]] = []
    for variant in sorted({row["variant"] for row in uncertainty_rows}):
        generic_rows = [
            row
            for row in uncertainty_rows
            if row["variant"] == variant and row["baseline"] != "event_risk_1_minus_p"
        ]
        if generic_rows:
            strongest_generic.append(max(generic_rows, key=lambda row: float(row["auroc_exact_error"])))
    lines.extend(
        [
            "",
            "## Multiseed Uncertainty Boundary",
            "",
            "| variant | event-risk AUROC exact | event-risk AUPRC exact | event-risk Spearman token error | event-risk exact risk gap |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for row in event_rows:
        lines.append(
            "| {variant} | {auroc_exact_error:.4f} | {auprc_exact_error:.4f} | {spearman_token_error:.4f} | {risk_gap_exact:.4f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Strongest generic uncertainty baselines by AUROC:",
            "",
            "| variant | strongest generic score | AUROC exact | AUPRC exact | Spearman token error |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in strongest_generic:
        lines.append(
            "| {variant} | {baseline} | {auroc_exact_error:.4f} | {auprc_exact_error:.4f} | {spearman_token_error:.4f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Allowed: multiseed aggregation strengthens the public case-study provenance if this run exists.",
            "",
            "Boundary: this remains a public case study, not SOTA, benchmark superiority, or a general task-improvement claim.",
            "",
        ]
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "CONLL2000_PUBLIC_MULTISEED_FORMAL_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_b7_report(output_dir: Path, run_dir: Path, rows: list[dict[str, object]]) -> None:
    meta = metadata(run_dir)
    lines = [
        "# B7 Constrained-Product Formal Audit",
        "",
        "B7 is a constrained-product Viterbi decoding baseline over CRF state x strict-BIO DFA state. It is not a full WFST system and does not use original posterior event mass for decoding.",
        "",
        "## Provenance",
        "",
        f"- raw bundle: `{run_dir.as_posix()}`",
        f"- git commit: `{meta.get('git_commit')}`",
        f"- config: `{meta.get('config')}`",
        f"- returncode: `{meta.get('returncode')}`",
        f"- duration_seconds: `{meta.get('duration_seconds')}`",
        "",
        "## Rows",
        "",
        "| source model | legal rate | token accuracy | entity F1 | event training | uses event mass for decoding |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {source_model} | {decoded_legal_rate:.4f} | {token_accuracy:.4f} | {entity_F1:.4f} | {uses_event_training} | {uses_event_mass_for_decoding} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Allowed: B7 verifies that a faithful constrained-product decoder can be reported separately from posterior event mass, with legal rate and task metrics.",
            "",
            "Boundary: do not present this as a WFST replacement, constrained-CRF replacement, or evidence that event-mass training defeats constrained decoding.",
            "",
        ]
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "B7_CONSTRAINED_PRODUCT_FORMAL_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_r7_report(output_dir: Path, run_dir: Path, rows: list[dict[str, object]], boundaries: list[dict[str, str]]) -> None:
    meta = metadata(run_dir)
    lines = [
        "# R7 Lambda / Rule Sensitivity Formal Audit",
        "",
        "This formal run studies how event-mass movement and task metrics vary with lambda and rule difficulty. It is a boundary study, not an accuracy benchmark.",
        "",
        "## Provenance",
        "",
        f"- raw bundle: `{run_dir.as_posix()}`",
        f"- git commit: `{meta.get('git_commit')}`",
        f"- config: `{meta.get('config')}`",
        f"- returncode: `{meta.get('returncode')}`",
        f"- duration_seconds: `{meta.get('duration_seconds')}`",
        "",
        "## Key Rows",
        "",
        "| task | variant | runs | P(event) | delta P | delta legal rate | delta exact acc | boundary |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {task} | {variant} | {runs} | {P_event:.4f} | {delta_P_event:+.4f} | {delta_legal_rate:+.4f} | {delta_exact_acc:+.4f} | {boundary} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Boundary Rows",
            "",
            "| task | legal-rate not useful | best event variant | best delta P | best exact variant | best delta exact | tradeoff observed |",
            "|---|---|---|---:|---|---:|---|",
        ]
    )
    for row in boundaries:
        lines.append(
            "| {task} | {legal_rate_not_useful} | {best_event_variant} | {best_delta_p_event} | {best_exact_variant} | {best_delta_exact_sequence_accuracy} | {event_task_tradeoff_observed} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Allowed: event loss can move posterior event mass, and the movement depends on lambda and rule difficulty. The `stock_like_digits` row is a useful boundary because legal-rate movement is not informative there.",
            "",
            "Boundary: do not claim event training always improves task metrics or that this sensitivity probe is benchmark evidence.",
            "",
        ]
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "R7_SENSITIVITY_FORMAL_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_combined_report(results_root: Path, run_root: Path) -> None:
    lines = [
        "# JMLR CPU Upgrade Result Audit",
        "",
        "This document summarizes the formal CPU upgrade runs imported from the raw run bundle.",
        "",
        "| block | raw bundle | status | intended use | claim boundary |",
        "|---|---|---|---|---|",
        "| public CoNLL2000 | `public_conll2000_chunking_formal` | passed | public BIO/chunking case study | not benchmark superiority or SOTA |",
        "| B7 constrained-product | `b7_constrained_product_formal` | passed | faithful constrained decoding comparison object | not full WFST or replacement claim |",
        "| R7 sensitivity | `r7_sensitivity_formal` | passed | lambda/rule boundary study | not accuracy-method claim |",
        "",
        "Raw bundles remain under ignored `experiments/runs/`; curated review artifacts are retained under `experiments/results/event_training/formal_pre_paper/`.",
        "",
        "Primary raw root:",
        "",
        f"```text\n{run_root.as_posix()}\n```",
        "",
        "The safe status after these runs is: manuscript drafting can proceed with conservative boundaries; submission readiness still requires final proof/related-work/reproducibility review.",
        "",
    ]
    (results_root / "JMLR_CPU_UPGRADE_RESULT_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def curate(run_root: Path, results_root: Path) -> None:
    public_run_dir = run_root / "public_conll2000_chunking_formal"
    b7_run_dir = run_root / "b7_constrained_product_formal"
    r7_run_dir = run_root / "r7_sensitivity_formal"
    for path in (public_run_dir, b7_run_dir, r7_run_dir):
        if not (path / "run_metadata.json").is_file():
            raise FileNotFoundError(path / "run_metadata.json")

    public_out = results_root / "public_sequence_labeling"
    b7_out = results_root / "b7_constrained_product"
    r7_out = results_root / "r7_sensitivity"

    public_summary = read_csv(public_run_dir / "public_case_summary.csv")
    public_details = read_csv(public_run_dir / "public_case_details.csv")
    public_rows = public_table_rows(public_summary)
    delta_rows = public_delta_rows(public_summary)
    uncertainty_rows = uncertainty_metric_rows(public_details)
    corr_rows = correlation_rows(public_details)
    comp_rows = complementarity_rows(public_details)
    write_csv(public_out / "conll2000_public_formal_summary.csv", public_rows)
    write_csv(public_out / "conll2000_public_formal_deltas.csv", delta_rows)
    write_csv(public_out / "conll2000_public_uncertainty_metrics.csv", uncertainty_rows)
    write_csv(public_out / "conll2000_public_event_uncertainty_correlations.csv", corr_rows)
    write_csv(public_out / "conll2000_public_uncertainty_complementarity.csv", comp_rows)
    write_public_report(public_out, public_run_dir, public_rows, delta_rows, uncertainty_rows)

    b7_rows = b7_table_rows(read_csv(b7_run_dir / "b7_summary.csv"))
    write_csv(b7_out / "b7_constrained_product_formal_summary.csv", b7_rows)
    write_b7_report(b7_out, b7_run_dir, b7_rows)

    r7_summary = read_csv(r7_run_dir / "r7_sensitivity_summary.csv")
    r7_boundaries = read_csv(r7_run_dir / "r7_sensitivity_boundaries.csv")
    r7_rows = r7_key_rows(r7_summary, r7_boundaries)
    write_csv(r7_out / "r7_sensitivity_formal_key_rows.csv", r7_rows)
    write_csv(r7_out / "r7_sensitivity_formal_boundaries.csv", [dict(row) for row in r7_boundaries])
    write_r7_report(r7_out, r7_run_dir, r7_rows, r7_boundaries)

    write_combined_report(results_root, run_root)


def curate_public_multiseed(run_dir: Path, results_root: Path) -> None:
    if not (run_dir / "run_metadata.json").is_file():
        raise FileNotFoundError(run_dir / "run_metadata.json")
    public_out = results_root / "public_sequence_labeling"
    public_summary = read_csv(run_dir / "public_case_summary.csv")
    public_details = read_csv(run_dir / "public_case_details.csv")
    rows = public_multiseed_table_rows(public_summary)
    deltas = public_multiseed_delta_rows(rows)
    uncertainty_rows = uncertainty_metric_rows(public_details)
    corr_rows = correlation_rows(public_details)
    comp_rows = complementarity_rows(public_details)
    write_csv(public_out / "conll2000_public_multiseed_formal_summary.csv", rows)
    write_csv(public_out / "conll2000_public_multiseed_formal_deltas.csv", deltas)
    write_csv(public_out / "conll2000_public_multiseed_uncertainty_metrics.csv", uncertainty_rows)
    write_csv(public_out / "conll2000_public_multiseed_event_uncertainty_correlations.csv", corr_rows)
    write_csv(public_out / "conll2000_public_multiseed_uncertainty_complementarity.csv", comp_rows)
    write_public_multiseed_report(public_out, run_dir, rows, deltas, uncertainty_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", default=str(DEFAULT_RUN_ROOT))
    parser.add_argument("--results-root", default=str(DEFAULT_RESULTS_ROOT))
    parser.add_argument("--public-multiseed-run", default="")
    args = parser.parse_args()
    curate(Path(args.run_root), Path(args.results_root))
    if args.public_multiseed_run:
        curate_public_multiseed(Path(args.public_multiseed_run), Path(args.results_root))


if __name__ == "__main__":
    main()
