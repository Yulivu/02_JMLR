"""Generate paper-ready tables from curated audit CSV files."""

from __future__ import annotations

import argparse
import csv
import subprocess
from pathlib import Path
from typing import Iterable


DEFAULT_RESULTS = Path("experiments/results/event_training/formal_pre_paper")
DEFAULT_OUTPUT = Path("experiments/results/paper_tables")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object, digits: int = 4) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    text = str(value)
    try:
        return f"{float(text):.{digits}f}"
    except ValueError:
        return text


def write_markdown(path: Path, title: str, rows: list[dict[str, object]]) -> None:
    fields = list(rows[0].keys())
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row[field]) for field in fields) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip()


def table_claims() -> list[dict[str, object]]:
    return [
        {
            "claim": "posterior event object",
            "status": "supported",
            "evidence": "finite theory + product-transfer tests",
            "boundary": "finite Y,T; complete DFA",
        },
        {
            "claim": "decoded legality != posterior consistency",
            "status": "supported",
            "evidence": "R5a B0 P(BIO|x)=0.0566 with constrained legality 1",
            "boundary": "diagnostic stress, not NER usefulness",
        },
        {
            "claim": "semi-event training raises event mass",
            "status": "supported-with-boundary",
            "evidence": "R5a/R1/R2/R4 B4 positive event-mass movement",
            "boundary": "not benchmark superiority",
        },
        {
            "claim": "low event mass is a risk signal",
            "status": "supported-with-boundary",
            "evidence": "R6a AUROC 0.7088, AUPRC 0.8470",
            "boundary": "field-style tasks; not calibration",
        },
        {
            "claim": "complexity story",
            "status": "supported-with-boundary",
            "evidence": "R8 reference CPU product-transfer scaling",
            "boundary": "not optimized runtime or low-rank superiority",
        },
    ]


def table_r5(results_dir: Path) -> list[dict[str, object]]:
    rows = read_csv(results_dir / "r5_wnut17" / "r5_wnut17_audit_summary.csv")
    selected = []
    keep = {"B0_unconstrained", "B4_semi_event_0.1", "B5_rule_feature_0.8", "B6_pr_style_tau0.7"}
    for row in rows:
        if row["variant"] not in keep:
            continue
        selected.append(
            {
                "block": row["block"],
                "variant": row["variant"],
                "seeds": row["seeds"],
                "P_event": fmt(row["mean_p_event_mean"]),
                "delta_P": fmt(row["delta_p_event_vs_b0_mean"]),
                "hidden_conflict": fmt(row["hidden_conflict_rate_mean"]),
                "entity_F1": fmt(row["entity_f1_mean"]),
                "claim_use": "hidden-conflict existence" if row["block"] == "r5a_diagnostic_stress" else "task viability boundary",
            }
        )
    return selected


def table_training(results_dir: Path) -> list[dict[str, object]]:
    rows = read_csv(results_dir / "p6_r1_r2_r4" / "p6_r1_r2_r4_block_summary.csv")
    selected = []
    for row in rows:
        if row["variant_family"] not in {"B4", "B5", "B6"}:
            continue
        selected.append(
            {
                "block": row["block"],
                "family": row["variant_family"],
                "rows": row["rows"],
                "mean_delta_P": fmt(row["mean_delta_p_event"]),
                "positive_P_rate": fmt(row["positive_p_event_rate"]),
                "mean_delta_legal": fmt(row["mean_delta_legal_rate"]),
                "mean_delta_char": fmt(row["mean_delta_char_accuracy"]),
                "mean_delta_exact": fmt(row["mean_delta_exact_accuracy"]),
            }
        )
    return selected


def table_diagnostic(results_dir: Path) -> list[dict[str, object]]:
    rows = read_csv(results_dir / "p6_r6_diagnostic" / "diagnostic_ranking_metrics.csv")
    selected = []
    for row in rows:
        selected.append(
            {
                "source": row["source"],
                "task": row["task"],
                "cases": row["cases"],
                "AUROC": fmt(row["auroc_exact_error"]),
                "AUPRC": fmt(row["auprc_exact_error"]),
                "Spearman": fmt(row["spearman_risk_char_error"]),
                "bottom20_exact_error": fmt(row["bottom20_exact_error"]),
                "bottom20_hidden_conflict": fmt(row["bottom20_hidden_conflict_rate"]),
            }
        )
    return selected


def table_complexity(results_dir: Path) -> list[dict[str, object]]:
    rows = read_csv(results_dir / "p6_r8_complexity" / "p6_r8_complexity_audit_rows.csv")
    selected = []
    for row in rows:
        if row["setting"] == "vary_length_dfa" and row["sequence_length"] not in {"10", "40", "80"}:
            continue
        selected.append(
            {
                "setting": row["setting"],
                "T": row["sequence_length"],
                "labels": row["label_count"],
                "dfa_states": row["dfa_states"],
                "context_order": row["context_order"],
                "product_states": row["product_state_count"],
                "mean_seconds": fmt(row["mean_seconds"], digits=6),
            }
        )
    return selected


def write_table_set(output_dir: Path, name: str, title: str, rows: list[dict[str, object]]) -> None:
    write_csv(output_dir / f"{name}.csv", rows)
    write_markdown(output_dir / f"{name}.md", title, rows)


def write_index(output_dir: Path, names: Iterable[str], commit: str) -> None:
    lines = [
        "# Paper Tables Index",
        "",
        f"Generated from curated audit CSVs at commit `{commit}`.",
        "",
        "| Table | CSV | Markdown |",
        "|---|---|---|",
    ]
    for name in names:
        lines.append(f"| `{name}` | `{name}.csv` | `{name}.md` |")
    lines.extend(
        [
            "",
            "Boundary:",
            "",
            "```text",
            "These are paper-prep tables, not final submitted tables.",
            "Do not infer benchmark superiority from these summaries.",
            "```",
            "",
        ]
    )
    (output_dir / "PAPER_TABLES_INDEX.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    tables = {
        "table_1_claim_summary": ("Claim Summary", table_claims()),
        "table_2_r5_wnut17": ("R5 WNUT17 Boundary Results", table_r5(results_dir)),
        "table_3_event_training_signal": ("R1/R2/R4 Event-Mass Movement", table_training(results_dir)),
        "table_4_diagnostic_ranking": ("R6a Diagnostic Ranking", table_diagnostic(results_dir)),
        "table_5_complexity_scaling": ("R8 Complexity Scaling", table_complexity(results_dir)),
    }
    for name, (title, rows) in tables.items():
        write_table_set(output_dir, name, title, rows)
        print(f"WROTE {output_dir / f'{name}.csv'}")
        print(f"WROTE {output_dir / f'{name}.md'}")
    write_index(output_dir, tables.keys(), git_commit())
    print(f"WROTE {output_dir / 'PAPER_TABLES_INDEX.md'}")


if __name__ == "__main__":
    main()
