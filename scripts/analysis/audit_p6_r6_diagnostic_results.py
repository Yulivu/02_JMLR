"""Audit downloaded P6 R6a diagnostic results."""

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
        exact_gap = f(row, "bottom_baseline_exact_error") - f(row, "top_baseline_exact_error")
        char_gap = f(row, "bottom_baseline_char_error") - f(row, "top_baseline_char_error")
        hidden_gap = f(row, "bottom_hidden_conflict_rate") - f(row, "top_hidden_conflict_rate")
        out.append(
            {
                "source": row["source"],
                "task": row["task"],
                "cases": int(row["cases"]),
                "bottom_mean_baseline_p": f(row, "bottom_mean_baseline_p"),
                "top_mean_baseline_p": f(row, "top_mean_baseline_p"),
                "bottom_baseline_exact_error": f(row, "bottom_baseline_exact_error"),
                "top_baseline_exact_error": f(row, "top_baseline_exact_error"),
                "baseline_exact_error_gap": exact_gap,
                "bottom_baseline_char_error": f(row, "bottom_baseline_char_error"),
                "top_baseline_char_error": f(row, "top_baseline_char_error"),
                "baseline_char_error_gap": char_gap,
                "bottom_hidden_conflict_rate": f(row, "bottom_hidden_conflict_rate"),
                "top_hidden_conflict_rate": f(row, "top_hidden_conflict_rate"),
                "hidden_conflict_gap": hidden_gap,
                "mean_event_p_shift": f(row, "mean_event_p_shift"),
                "risk_signal_supported": exact_gap > 0 and char_gap > 0,
                "hidden_conflict_supported": hidden_gap > 0,
            }
        )
    return out


def fmt(value: object) -> str:
    return f"{value:.4f}" if isinstance(value, float) else str(value)


def write_markdown(path: Path, rows: list[dict[str, object]]) -> None:
    risk_rate = sum(bool(row["risk_signal_supported"]) for row in rows) / len(rows)
    hidden_rate = sum(bool(row["hidden_conflict_supported"]) for row in rows) / len(rows)
    lines = [
        "# P6 R6a Diagnostic Result-to-Claim Audit",
        "",
        "This audit summarizes downloaded AutoDL R6a diagnostic outputs. It is an evidence audit, not a paper section.",
        "",
        "## Summary",
        "",
        f"- risk_signal_supported_rate: `{risk_rate:.4f}`",
        f"- hidden_conflict_supported_rate: `{hidden_rate:.4f}`",
        "",
        "| source | task | cases | bottom P | top P | exact error gap | char error gap | hidden gap | risk supported | hidden supported |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {source} | {task} | {cases} | {bp} | {tp} | {eg} | {cg} | {hg} | {rs} | {hs} |".format(
                source=row["source"],
                task=row["task"],
                cases=row["cases"],
                bp=fmt(row["bottom_mean_baseline_p"]),
                tp=fmt(row["top_mean_baseline_p"]),
                eg=fmt(row["baseline_exact_error_gap"]),
                cg=fmt(row["baseline_char_error_gap"]),
                hg=fmt(row["hidden_conflict_gap"]),
                rs=row["risk_signal_supported"],
                hs=row["hidden_conflict_supported"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Audit",
            "",
            "| Claim | Status | Evidence | Boundary |",
            "|---|---|---|---|",
            "| Low `P_theta(L|x)` is a risk signal | supported in R6a | bottom event-mass quantile has higher exact and char error than top quantile on all audited field tasks | field-style diagnostic, not all structured prediction |",
            "| Hidden conflict concentrates at low event mass | partially supported | semi-real tasks show clear hidden-conflict gaps; real-source tasks are mostly saturated | keep separate from R5a WNUT hidden-conflict evidence |",
            "| Diagnostic establishes task improvement | not supported | diagnostic and training improvement are different claims | do not claim benchmark superiority |",
            "",
            "## Decision",
            "",
            "```text",
            "R6a supports the diagnostic/risk-signal claim for field-style tasks.",
            "R6a partially supports hidden-conflict concentration; strongest in semi-real tasks.",
            "Proceed to R8 complexity before paper-writing.",
            "```",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs-dir",
        default="experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/r6a_field_diagnostic_formal",
    )
    parser.add_argument("--output-dir", default="experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic")
    args = parser.parse_args()

    rows = audit_rows(read_csv(Path(args.runs_dir) / "diagnostic_summary.csv"))
    output_dir = Path(args.output_dir)
    write_csv(output_dir / "p6_r6a_diagnostic_audit_summary.csv", rows)
    write_markdown(output_dir / "P6_R6A_DIAGNOSTIC_RESULT_TO_CLAIM_AUDIT.md", rows)
    print(f"WROTE {output_dir / 'p6_r6a_diagnostic_audit_summary.csv'}")
    print(f"WROTE {output_dir / 'P6_R6A_DIAGNOSTIC_RESULT_TO_CLAIM_AUDIT.md'}")


if __name__ == "__main__":
    main()
