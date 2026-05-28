"""Audit downloaded P6 R8 complexity scaling results."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def audit_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for row in rows:
        out.append(
            {
                "setting": row["setting"],
                "sequence_length": int(row["sequence_length"]),
                "label_count": int(row["label_count"]),
                "dfa_states": int(row["dfa_states"]),
                "context_order": int(row["context_order"]),
                "product_state_count": int(row["product_state_count"]),
                "mean_seconds": f(row, "mean_seconds"),
                "seconds_per_product_state": f(row, "mean_seconds") / max(1, int(row["product_state_count"])),
                "claim_use": "reference CPU complexity sanity",
            }
        )
    return out


def fmt(value: object) -> str:
    return f"{value:.6f}" if isinstance(value, float) else str(value)


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    max_row = max(rows, key=lambda row: float(row["mean_seconds"]))
    max_state_row = max(rows, key=lambda row: int(row["product_state_count"]))
    lines = [
        "# P6 R8 Complexity Result-to-Claim Audit",
        "",
        "This audit summarizes downloaded AutoDL R8 complexity outputs. It is an evidence audit, not a paper section.",
        "",
        "## Key Numbers",
        "",
        f"- max_mean_seconds: `{fmt(max_row['mean_seconds'])}` at setting `{max_row['setting']}`",
        f"- max_product_state_count: `{max_state_row['product_state_count']}` at setting `{max_state_row['setting']}`",
        "",
        "## Detailed Rows",
        "",
        "| setting | T | labels | DFA states | context order | product states | mean seconds |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {setting} | {t} | {labels} | {dfa} | {m} | {states} | {sec} |".format(
                setting=row["setting"],
                t=row["sequence_length"],
                labels=row["label_count"],
                dfa=row["dfa_states"],
                m=row["context_order"],
                states=row["product_state_count"],
                sec=fmt(row["mean_seconds"]),
            )
        )
    lines.extend(
        [
            "",
            "## Claim Audit",
            "",
            "| Claim | Status | Evidence | Boundary |",
            "|---|---|---|---|",
            "| Reference product-transfer scaling was measured | supported | R8 varies sequence length, label count, DFA states, and context order | reference CPU implementation only |",
            "| Complexity story can report product-state dependence | supported | runtime increases with larger product-state configurations | report as sanity/scaling, not optimized benchmark |",
            "| Optimized runtime superiority | not supported | no optimized implementation or competing systems measured | do not claim speed advantage |",
            "| Arbitrary low-rank advantage | not supported | R8 does not test low-rank approximation | keep rank/MPO in appendix scope |",
            "",
            "## Decision",
            "",
            "```text",
            "R8 supports a conservative complexity/scaling discussion.",
            "R8 does not support speed, GPU, low-rank, or superiority claims.",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs-dir",
        default="experiments/runs/autodl_jmlr_block/p6_r8_complexity/r8_complexity_scaling_formal",
    )
    parser.add_argument("--output-dir", default="experiments/results/event_training/formal_pre_paper/p6_r8_complexity")
    args = parser.parse_args()

    rows = audit_rows(read_csv(Path(args.runs_dir) / "complexity_runs.csv"))
    output_dir = Path(args.output_dir)
    write_csv(output_dir / "p6_r8_complexity_audit_rows.csv", rows)
    write_markdown(output_dir / "P6_R8_COMPLEXITY_RESULT_TO_CLAIM_AUDIT.md", rows)
    print(f"WROTE {output_dir / 'p6_r8_complexity_audit_rows.csv'}")
    print(f"WROTE {output_dir / 'P6_R8_COMPLEXITY_RESULT_TO_CLAIM_AUDIT.md'}")


if __name__ == "__main__":
    main()
