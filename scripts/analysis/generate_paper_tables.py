"""Generate review-stage paper tables from curated audit CSV files."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from pathlib import Path
from typing import Iterable


DEFAULT_RESULTS = Path("experiments/results/event_training/formal_pre_paper")
DEFAULT_OUTPUT = Path("experiments/results/paper_tables")
DEFAULT_CLAIMS = Path("docs/manuscript/FINAL_CLAIM_TABLE.md")


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
    if isinstance(value, int):
        return str(value)
    return str(value)


def numfmt(value: object, digits: int = 4) -> str:
    text = str(value)
    if re.fullmatch(r"-?\d+", text):
        return text
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
    commit = result.stdout.strip()
    try:
        status = subprocess.run(
            ["git", "status", "--short"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return commit
    return f"{commit}+dirty" if status.stdout.strip() else commit


def split_markdown_row(line: str) -> list[str]:
    cells: list[str] = []
    current: list[str] = []
    in_code = False
    for char in line.strip().strip("|"):
        if char == "`":
            in_code = not in_code
            current.append(char)
        elif char == "|" and not in_code:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    cells.append("".join(current).strip())
    return cells


def parse_markdown_table(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = split_markdown_row(line)
        if {"Claim ID", "Claim", "Level", "Evidence", "Boundary"}.issubset(set(cells)):
            headers = cells
            continue
        if headers is not None and len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


def table_claims(claims_path: Path) -> list[dict[str, object]]:
    rows = parse_markdown_table(claims_path)
    selected = []
    included_levels = {"Formal foundation", "Sanity / Appendix", "Appendix"}
    for row in rows:
        if not row.get("Claim ID", "").startswith("C"):
            continue
        level = row.get("Level", "")
        if not level.startswith("Main") and level not in included_levels:
            continue
        selected.append(
            {
                "claim_id": row["Claim ID"],
                "claim": row["Claim"],
                "level": level,
                "evidence": row["Evidence"],
                "boundary": row["Boundary"],
            }
        )
    return selected


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
                "P_event": numfmt(row["mean_p_event_mean"]),
                "delta_P": numfmt(row["delta_p_event_vs_b0_mean"]),
                "hidden_conflict": numfmt(row["hidden_conflict_rate_mean"]),
                "entity_F1": numfmt(row["entity_f1_mean"]),
                "claim_use": "hidden-conflict diagnostic evidence" if row["block"] == "r5a_diagnostic_stress" else "task viability boundary",
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
                "mean_delta_P": numfmt(row["mean_delta_p_event"]),
                "positive_P_rate": numfmt(row["positive_p_event_rate"]),
                "mean_delta_legal": numfmt(row["mean_delta_legal_rate"]),
                "mean_delta_char": numfmt(row["mean_delta_char_accuracy"]),
                "mean_delta_exact": numfmt(row["mean_delta_exact_accuracy"]),
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
                "base_exact_error": numfmt(row["exact_error_rate"]),
                "AUROC": numfmt(row["auroc_exact_error"]),
                "AUPRC": numfmt(row["auprc_exact_error"]),
                "Spearman": numfmt(row["spearman_risk_char_error"]),
                "bottom20_exact_error": numfmt(row["bottom20_exact_error"]),
                "bottom20_hidden_conflict": numfmt(row["bottom20_hidden_conflict_rate"]),
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
                "mean_seconds": numfmt(row["mean_seconds"], digits=6),
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
        f"Generated from curated audit CSVs using repository state `{commit}`.",
        "",
        "This is table-generation provenance, not a claim that later documentation-only",
        "handoff commits changed the curated numeric evidence.",
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
    parser.add_argument("--claims", default=str(DEFAULT_CLAIMS))
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    claims_path = Path(args.claims)
    output_dir.mkdir(parents=True, exist_ok=True)

    tables = {
        "table_1_claim_summary": ("Claim Summary", table_claims(claims_path)),
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
