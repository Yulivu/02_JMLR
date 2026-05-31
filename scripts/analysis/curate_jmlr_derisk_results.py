"""Curate local de-risking sprint runs into review-stage audit files."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from statistics import mean, stdev


DEFAULT_R7_RUN = Path("experiments/runs/local_checks/r7_sensitivity_derisk_formal_wrapped")
DEFAULT_PUBLIC_SMOKE = Path("experiments/runs/local_checks/public_conll2000_chunking_multiseed_tiny_smoke")
DEFAULT_RESULTS = Path("experiments/results/event_training/formal_pre_paper")


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


def metadata(run_dir: Path) -> dict[str, object]:
    meta_path = run_dir / "run_metadata.json"
    if not meta_path.is_file():
        return {"git_commit": "local-direct-run", "config": "", "returncode": 0, "duration_seconds": ""}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def repo_state() -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--short"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return f"{commit}+dirty" if status else commit


def command_block(command: object) -> list[str]:
    if isinstance(command, list) and command:
        return ["```text", " ".join(str(part) for part in command), "```"]
    return ["```text", "", "```"]


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def aggregate_public_rows(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    metrics = [
        "mean_p_event",
        "hidden_conflict_rate",
        "unconstrained_legal_rate",
        "b7_legal_rate",
        "token_accuracy",
        "span_f1",
    ]
    out: list[dict[str, object]] = []
    variants = sorted({row["variant"] for row in rows})
    for variant in variants:
        group = [row for row in rows if row["variant"] == variant]
        agg: dict[str, object] = {"variant": variant, "seeds": len(group)}
        for metric in metrics:
            values = [f(row, metric) for row in group]
            agg[f"{metric}_mean"] = mean(values)
            agg[f"{metric}_std"] = stdev(values) if len(values) > 1 else 0.0
        out.append(agg)
    return out


def r7_derisk_key_rows(summary: list[dict[str, str]], boundaries: list[dict[str, str]]) -> list[dict[str, object]]:
    boundary_by_task = {row["task"]: row for row in boundaries}
    rows: list[dict[str, object]] = []
    for row in summary:
        boundary = boundary_by_task[row["task"]]
        keep = row["variant"] == "B0_unconstrained" or row["variant"] == boundary["best_event_variant"]
        if row["task"] == "product_code_swapped_rule" and row["variant"] == "B4_semi_event_0.1":
            keep = True
        if not keep:
            continue
        rows.append(
            {
                "task": row["task"],
                "variant": row["variant"],
                "runs": int(row["runs"]),
                "P_event": f(row, "mean_p_event"),
                "delta_P_event": f(row, "delta_p_event"),
                "delta_legal_rate": f(row, "delta_unconstrained_event_rate"),
                "delta_char_acc": f(row, "delta_char_accuracy"),
                "delta_exact_acc": f(row, "delta_exact_sequence_accuracy"),
                "tradeoff_observed": boundary["event_task_tradeoff_observed"],
                "boundary": boundary_label(boundary),
            }
        )
    return rows


def boundary_label(row: dict[str, str]) -> str:
    if row["event_task_tradeoff_observed"] == "True":
        return "event/task tradeoff"
    if row["legal_rate_not_useful"] == "True":
        return "legal-rate-not-useful"
    if row["baseline_saturated"] == "True":
        return "baseline-saturated"
    return "ordinary"


def write_r7_derisk_audit(results_root: Path, run_dir: Path) -> None:
    out_dir = results_root / "r7_sensitivity"
    summary = read_csv(run_dir / "r7_sensitivity_summary.csv")
    boundaries = read_csv(run_dir / "r7_sensitivity_boundaries.csv")
    key_rows = r7_derisk_key_rows(summary, boundaries)
    write_csv(out_dir / "r7_sensitivity_derisk_key_rows.csv", key_rows)
    write_csv(out_dir / "r7_sensitivity_derisk_boundaries.csv", [dict(row) for row in boundaries])

    meta = metadata(run_dir)
    wrapper_command = [
        "python",
        "scripts/exp1/run_event_training_task.py",
        "--config",
        str(meta.get("config", "")),
        "--out-dir",
        str(meta.get("out_dir", run_dir.as_posix())),
    ]
    lines = [
        "# R7 Sensitivity De-Risk Audit",
        "",
        "This audit adds an explicit negative boundary to R7. The `product_code_swapped_rule` data are generated as product codes, but the event rule audits the swapped pattern `DD-LLL`. This rule is intentionally weakly related to task correctness.",
        "",
        "## Provenance",
        "",
        f"- raw bundle: `{run_dir.as_posix()}`",
        f"- git commit: `{meta.get('git_commit')}`",
        f"- curation repo state: `{repo_state()}`",
        f"- config: `{meta.get('config')}`",
        f"- returncode: `{meta.get('returncode')}`",
        f"- duration_seconds: `{meta.get('duration_seconds')}`",
        f"- started_at_utc: `{meta.get('started_at_utc', '')}`",
        f"- ended_at_utc: `{meta.get('ended_at_utc', '')}`",
        "",
        "Wrapper command:",
        "",
        *command_block(wrapper_command),
        "",
        "Executed module command:",
        "",
        *command_block(meta.get("command")),
        "",
        "## Key Rows",
        "",
        "| task | variant | runs | P(event) | delta P | delta legal rate | delta char acc | delta exact acc | boundary |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in key_rows:
        lines.append(
            "| {task} | {variant} | {runs} | {P_event:.4f} | {delta_P_event:+.4f} | {delta_legal_rate:+.4f} | {delta_char_acc:+.4f} | {delta_exact_acc:+.4f} | {boundary} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Allowed: event loss can move posterior event mass, but if the rule is weakly related or misleading for the task, task metrics can degrade sharply.",
            "",
            "Boundary: this directly rules out any claim that event loss is a general accuracy method. It also shows why the paper must treat rule choice as an audit-design assumption.",
            "",
        ]
    )
    (out_dir / "R7_SENSITIVITY_DERISK_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def write_public_multiseed_smoke_audit(results_root: Path, run_dir: Path) -> None:
    out_dir = results_root / "public_sequence_labeling"
    rows = read_csv(run_dir / "public_case_summary.csv")
    agg_rows = aggregate_public_rows(rows)
    write_csv(out_dir / "conll2000_public_multiseed_tiny_smoke_summary.csv", agg_rows)
    meta = metadata(run_dir)
    wrapper_command = [
        "python",
        "scripts/exp1/run_event_training_task.py",
        "--config",
        str(meta.get("config", "")),
        "--out-dir",
        str(meta.get("out_dir", run_dir.as_posix())),
    ]
    lines = [
        "# CoNLL2000 Public Multiseed Tiny Smoke Audit",
        "",
        "This is a three-seed plumbing smoke only. It uses 30/30/30 train/unlabeled/dev examples for one epoch and must not be reported as formal evidence.",
        "",
        "## Provenance",
        "",
        f"- raw bundle: `{run_dir.as_posix()}`",
        f"- git commit: `{meta.get('git_commit')}`",
        f"- config: `{meta.get('config')}`",
        f"- returncode: `{meta.get('returncode')}`",
        f"- duration_seconds: `{meta.get('duration_seconds')}`",
        f"- started_at_utc: `{meta.get('started_at_utc', '')}`",
        f"- ended_at_utc: `{meta.get('ended_at_utc', '')}`",
        "",
        "Wrapper command:",
        "",
        *command_block(wrapper_command),
        "",
        "Executed module command:",
        "",
        *command_block(meta.get("command")),
        "",
        "## Aggregate Rows",
        "",
        "| variant | seeds | P(BIO) mean | P(BIO) std | hidden conflict mean | token acc mean | span F1 mean |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in agg_rows:
        lines.append(
            "| {variant} | {seeds} | {mean_p_event_mean:.4f} | {mean_p_event_std:.4f} | {hidden_conflict_rate_mean:.4f} | {token_accuracy_mean:.4f} | {span_f1_mean:.4f} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Formal Multiseed Status",
            "",
            "This tiny run remains a plumbing smoke only. The full 1000/1000/1000 three-seed run is curated separately when available:",
            "",
            "```bash",
            "python scripts/analysis/curate_jmlr_cpu_upgrade_results.py --public-multiseed-run experiments/runs/local_checks/public_conll2000_chunking_multiseed_full",
            "```",
            "",
            "Boundary: do not use this tiny smoke as C13 evidence even when a full multiseed run exists.",
            "",
        ]
    )
    (out_dir / "CONLL2000_PUBLIC_MULTISEED_TINY_SMOKE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--r7-run", default=str(DEFAULT_R7_RUN))
    parser.add_argument("--public-smoke-run", default=str(DEFAULT_PUBLIC_SMOKE))
    parser.add_argument("--results-root", default=str(DEFAULT_RESULTS))
    args = parser.parse_args()
    results_root = Path(args.results_root)
    r7_run = Path(args.r7_run)
    public_smoke_run = Path(args.public_smoke_run)
    if r7_run.is_dir():
        write_r7_derisk_audit(results_root, r7_run)
    if public_smoke_run.is_dir():
        write_public_multiseed_smoke_audit(results_root, public_smoke_run)


if __name__ == "__main__":
    main()
