"""Audit downloaded R5 WNUT17 formal results."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev


METRICS = (
    "mean_p_event",
    "delta_p_event_vs_b0",
    "mean_illegal_mass",
    "hidden_conflict_rate",
    "token_accuracy",
    "constrained_token_accuracy",
    "entity_f1",
    "constrained_entity_f1",
    "mean_nll",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def ci95(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return 1.96 * stdev(values) / (len(values) ** 0.5)


def summarize_block(block_name: str, path: Path) -> list[dict[str, object]]:
    rows = read_csv(path)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["variant"]].append(row)
    summary: list[dict[str, object]] = []
    for variant, group in sorted(grouped.items()):
        output: dict[str, object] = {
            "block": block_name,
            "variant": variant,
            "seeds": len(group),
            "up_rate_delta_p_event": mean(float(row["delta_p_event_vs_b0"]) > 0.0 for row in group),
        }
        for metric in METRICS:
            values = [float(row[metric]) for row in group]
            output[f"{metric}_mean"] = mean(values)
            output[f"{metric}_ci95"] = ci95(values)
        summary.append(output)
    return summary


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    by_block: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_block[str(row["block"])].append(row)

    lines = [
        "# R5 WNUT17 Result-to-Claim Audit",
        "",
        "This audit summarizes downloaded AutoDL R5 outputs. It is an evidence audit, not a paper section.",
        "",
    ]
    for block in ("r5a_diagnostic_stress", "r5b_feature_viability"):
        lines.extend(
            [
                f"## {block}",
                "",
                "| variant | seeds | P(BIO|x) | delta P | up-rate | hidden conflict | token acc | entity F1 | NLL |",
                "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in by_block[block]:
            lines.append(
                "| {variant} | {seeds} | {p} | {dp} | {up} | {hc} | {tok} | {f1} | {nll} |".format(
                    variant=row["variant"],
                    seeds=row["seeds"],
                    p=fmt(row["mean_p_event_mean"]),
                    dp=fmt(row["delta_p_event_vs_b0_mean"]),
                    up=fmt(row["up_rate_delta_p_event"]),
                    hc=fmt(row["hidden_conflict_rate_mean"]),
                    tok=fmt(row["token_accuracy_mean"]),
                    f1=fmt(row["entity_f1_mean"]),
                    nll=fmt(row["mean_nll_mean"]),
                )
            )
        lines.append("")

    lines.extend(
        [
            "## Claim Audit",
            "",
            "| Claim | Status | Evidence | Boundary |",
            "|---|---|---|---|",
            "| Hidden posterior conflict exists | supported in R5a | B0 has very low `P(BIO|x)` and hidden conflict near 1 while constrained legality is 1 | R5a has entity F1 = 0, so it is diagnostic only |",
            "| Semi-event training raises posterior BIO mass | supported in R5a | B4 has the largest positive delta P over B0 among B2/B4/B5/B6 | In R5b, event mass is already saturated |",
            "| WNUT17 is not pure all-O toy | supported in R5b | B0 entity F1 is nonzero over 10 seeds | F1 remains modest; no benchmark superiority claim |",
            "| B4 improves NER F1 | not supported | B4 entity F1 is not consistently above B0 in R5b | Do not claim task-performance improvement |",
            "| B5/B6 dominate B4 | not supported overall | B5/B6 are competitive in R5b but weaker than B4 for R5a posterior mass | Keep baseline discussion nuanced |",
            "",
            "## Decision",
            "",
            "```text",
            "R5 supports the paper's posterior-event diagnostic story.",
            "R5 does not support NER benchmark superiority.",
            "Use R5a for hidden conflict and R5b for task viability.",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", default="experiments/runs/autodl_jmlr_block/r5_wnut17")
    parser.add_argument("--output-dir", default="experiments/results/event_training/formal_pre_paper/r5_wnut17")
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    output_dir = Path(args.output_dir)
    rows = []
    rows.extend(summarize_block("r5a_diagnostic_stress", runs_dir / "r5a_diagnostic_stress" / "summary.csv"))
    rows.extend(summarize_block("r5b_feature_viability", runs_dir / "r5b_feature_viability" / "summary.csv"))
    write_csv(output_dir / "r5_wnut17_audit_summary.csv", rows)
    write_markdown(output_dir / "R5_RESULT_TO_CLAIM_AUDIT.md", rows)
    print(f"WROTE {output_dir / 'r5_wnut17_audit_summary.csv'}")
    print(f"WROTE {output_dir / 'R5_RESULT_TO_CLAIM_AUDIT.md'}")


if __name__ == "__main__":
    main()
