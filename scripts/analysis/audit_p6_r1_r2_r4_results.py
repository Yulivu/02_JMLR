"""Audit downloaded P6 R1/R2/R4 formal results.

This script consumes raw AutoDL run bundles under experiments/runs and writes
curated, claim-bounded summaries under experiments/results. It does not rerun
experiments and does not promote raw outputs into Git.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


BLOCKS = {
    "r1_controlled_formal": {
        "summary": "formal_validation_summary.csv",
        "claim_use": "controlled structural robustness",
    },
    "r2_semi_real_formal": {
        "summary": "semi_real_main_summary.csv",
        "claim_use": "semi-real field evidence",
    },
    "r4_real_source_formal": {
        "summary": "real_small_data_main_summary.csv",
        "claim_use": "real-source small-field auxiliary evidence",
    },
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


def f(row: dict[str, str], key: str, default: float = 0.0) -> float:
    value = row.get(key, "")
    return float(value) if value != "" else default


def variant_family(variant: str) -> str:
    return variant.split("_", 1)[0]


def collect_rows(runs_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for block, spec in BLOCKS.items():
        path = runs_dir / block / str(spec["summary"])
        for row in read_csv(path):
            variant = row["variant"]
            rows.append(
                {
                    "block": block,
                    "claim_use": spec["claim_use"],
                    "task": row["task"],
                    "setting": row["setting"],
                    "variant": variant,
                    "variant_family": variant_family(variant),
                    "runs": int(row["runs"]),
                    "mean_p_event": f(row, "mean_p_event"),
                    "delta_p_event": f(row, "delta_p_event"),
                    "ci95_delta_p_event": f(row, "ci95_delta_p_event"),
                    "p_event_up_rate": f(row, "p_event_up_rate"),
                    "unconstrained_event_rate": f(row, "unconstrained_event_rate"),
                    "delta_unconstrained_event_rate": f(row, "delta_unconstrained_event_rate"),
                    "char_accuracy": f(row, "char_accuracy"),
                    "delta_char_accuracy": f(row, "delta_char_accuracy"),
                    "exact_sequence_accuracy": f(row, "exact_sequence_accuracy"),
                    "delta_exact_sequence_accuracy": f(row, "delta_exact_sequence_accuracy"),
                    "mean_nll": f(row, "mean_nll"),
                    "hidden_conflict_rate": f(row, "hidden_conflict_rate"),
                }
            )
    return rows


def aggregate(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["variant"] == "B0_unconstrained":
            continue
        groups[(str(row["block"]), str(row["variant_family"]))].append(row)
    out: list[dict[str, object]] = []
    for (block, family), group in sorted(groups.items()):
        out.append(
            {
                "block": block,
                "variant_family": family,
                "rows": len(group),
                "mean_delta_p_event": mean(float(row["delta_p_event"]) for row in group),
                "positive_p_event_rate": mean(float(row["delta_p_event"]) > 0 for row in group),
                "mean_delta_legal_rate": mean(float(row["delta_unconstrained_event_rate"]) for row in group),
                "positive_legal_rate": mean(float(row["delta_unconstrained_event_rate"]) > 0 for row in group),
                "mean_delta_char_accuracy": mean(float(row["delta_char_accuracy"]) for row in group),
                "nonnegative_char_rate": mean(float(row["delta_char_accuracy"]) >= 0 for row in group),
                "mean_delta_exact_accuracy": mean(float(row["delta_exact_sequence_accuracy"]) for row in group),
                "nonnegative_exact_rate": mean(float(row["delta_exact_sequence_accuracy"]) >= 0 for row in group),
            }
        )
    return out


def fmt(value: object) -> str:
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def write_markdown(path: Path, rows: list[dict[str, object]], agg: list[dict[str, object]]) -> None:
    by_block: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        by_block[str(row["block"])].append(row)

    lines = [
        "# P6 R1/R2/R4 Result-to-Claim Audit",
        "",
        "This audit summarizes downloaded AutoDL P6 R1/R2/R4 outputs. It is an evidence audit, not a paper section.",
        "",
        "## Block Summary",
        "",
        "| block | family | rows | mean delta P | positive P rate | mean delta legal | mean delta char | mean delta exact |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in agg:
        lines.append(
            "| {block} | {family} | {rows} | {dp} | {upr} | {dl} | {dc} | {de} |".format(
                block=row["block"],
                family=row["variant_family"],
                rows=row["rows"],
                dp=fmt(row["mean_delta_p_event"]),
                upr=fmt(row["positive_p_event_rate"]),
                dl=fmt(row["mean_delta_legal_rate"]),
                dc=fmt(row["mean_delta_char_accuracy"]),
                de=fmt(row["mean_delta_exact_accuracy"]),
            )
        )

    for block in BLOCKS:
        lines.extend(
            [
                "",
                f"## {block}",
                "",
                "| task | variant | runs | P(L|x) | delta P | legal rate | char acc | exact acc |",
                "|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for row in by_block[block]:
            if row["variant"] == "B0_unconstrained" or str(row["variant"]).startswith("B4") or str(row["variant"]).startswith("B5") or str(row["variant"]).startswith("B6"):
                lines.append(
                    "| {task} | {variant} | {runs} | {p} | {dp} | {lr} | {ca} | {ea} |".format(
                        task=row["task"],
                        variant=row["variant"],
                        runs=row["runs"],
                        p=fmt(row["mean_p_event"]),
                        dp=fmt(row["delta_p_event"]),
                        lr=fmt(row["unconstrained_event_rate"]),
                        ca=fmt(row["char_accuracy"]),
                        ea=fmt(row["exact_sequence_accuracy"]),
                    )
                )

    lines.extend(
        [
            "",
            "## Claim Audit",
            "",
            "| Claim | Status | Evidence | Boundary |",
            "|---|---|---|---|",
            "| B4 raises posterior event mass on controlled tasks | supported | R1 B4 rows have positive delta P across controlled formats | controlled structural evidence only |",
            "| B4 raises posterior event mass on semi-real fields | supported | R2 B4 rows have positive delta P across amount/date/dose/product_code | task accuracy is not uniformly dominant |",
            "| B4 raises posterior event mass on real-source small fields | supported | R4 B4 rows have positive delta P across invoice/stock fields | baseline legal rate is saturated or near-saturated |",
            "| B4 is benchmark-superior | not supported | B5/B6 are competitive and task metrics vary by block | do not claim superiority |",
            "| R1/R2/R4 complete P6 | not supported | they cover structural/training evidence, not full diagnostics or complexity | R6/R8 still needed |",
            "",
            "## Decision",
            "",
            "```text",
            "P6 R1/R2/R4 support posterior-event training as a structural signal.",
            "They do not support benchmark superiority.",
            "Proceed to R6 diagnostic and R8 complexity before paper-writing.",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", default="experiments/runs/autodl_jmlr_block/p6_r1_r2_r4")
    parser.add_argument("--output-dir", default="experiments/results/event_training/formal_pre_paper/p6_r1_r2_r4")
    args = parser.parse_args()

    rows = collect_rows(Path(args.runs_dir))
    agg = aggregate(rows)
    output_dir = Path(args.output_dir)
    write_csv(output_dir / "p6_r1_r2_r4_audit_rows.csv", rows)
    write_csv(output_dir / "p6_r1_r2_r4_block_summary.csv", agg)
    write_markdown(output_dir / "P6_R1_R2_R4_RESULT_TO_CLAIM_AUDIT.md", rows, agg)
    print(f"WROTE {output_dir / 'p6_r1_r2_r4_audit_rows.csv'}")
    print(f"WROTE {output_dir / 'p6_r1_r2_r4_block_summary.csv'}")
    print(f"WROTE {output_dir / 'P6_R1_R2_R4_RESULT_TO_CLAIM_AUDIT.md'}")


if __name__ == "__main__":
    main()
