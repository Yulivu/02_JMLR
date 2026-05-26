"""Export existing local probe results into the formal pre-paper schema.

This is a mechanical consolidation step. It does not rerun experiments.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable


RESULTS_DIR = Path("experiments/results/event_training")
OUT_DIR = RESULTS_DIR / "formal_pre_paper"


RUN_FIELDS = [
    "block",
    "task_family",
    "task",
    "setting",
    "seed",
    "variant",
    "variant_family",
    "train_objective",
    "decode_mode",
    "parameters_from",
    "rule_id",
    "same_split",
    "same_seed",
    "same_rule",
    "same_label_alphabet",
    "labeled_size",
    "unlabeled_size",
    "dev_size",
    "epochs",
    "lr",
    "lambda",
    "weight",
    "tau",
    "eta",
    "rule_feature_weight",
    "pr_tau",
    "pr_eta",
    "p_event",
    "illegal_mass",
    "low_p_event_rate",
    "unconstrained_legal_rate",
    "constrained_legal_rate",
    "char_accuracy",
    "constrained_char_accuracy",
    "exact_sequence_accuracy",
    "constrained_exact_sequence_accuracy",
    "nll",
    "hidden_conflict_count",
    "hidden_conflict_rate",
    "fairness_flags",
    "claim_use",
    "notes",
]


SUMMARY_FIELDS = [
    "block",
    "task_family",
    "task",
    "setting",
    "variant",
    "variant_family",
    "runs",
    "mean_p_event",
    "delta_p_event",
    "ci95_delta_p_event",
    "up_rate_p_event",
    "mean_illegal_mass",
    "delta_illegal_mass",
    "low_p_event_rate",
    "unconstrained_event_rate",
    "delta_unconstrained_event_rate",
    "up_rate_legal",
    "constrained_event_rate",
    "char_accuracy",
    "delta_char_accuracy",
    "up_rate_char",
    "constrained_char_accuracy",
    "delta_constrained_char_accuracy",
    "exact_sequence_accuracy",
    "delta_exact_sequence_accuracy",
    "up_rate_exact",
    "constrained_exact_sequence_accuracy",
    "delta_constrained_exact_sequence_accuracy",
    "mean_nll",
    "hidden_conflict_rate",
    "fairness_flags",
    "claim_use",
    "notes",
]


CASE_FIELDS = [
    "block",
    "task_family",
    "task",
    "setting",
    "seed",
    "case_id",
    "tokens",
    "gold",
    "b0_prediction",
    "b0_constrained_prediction",
    "variant_prediction",
    "variant_constrained_prediction",
    "b0_p_event",
    "variant_p_event",
    "b0_legal",
    "variant_legal",
    "b0_exact",
    "variant_exact",
    "conflict_type",
    "notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: Iterable[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row_list = [{field: row.get(field, "") for field in fields} for row in rows]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(row_list)
    path.with_suffix(".json").write_text(json.dumps(row_list, indent=2, ensure_ascii=False), encoding="utf-8")


def variant_family(variant: str) -> str:
    return variant.split("_", 1)[0] if variant else ""


def train_objective(variant: str) -> str:
    family = variant_family(variant)
    return {
        "B0": "crf_nll",
        "B1": "crf_nll",
        "B2": "labeled_event",
        "B3": "event_plus_constraint",
        "B4": "semi_event",
        "B5": "rule_feature",
        "B6": "pr_style",
    }.get(family, "")


def parse_float_suffix(variant: str, key: str) -> str:
    if key == "tau":
        match = re.search(r"tau([0-9.]+)$", variant)
    else:
        match = re.search(r"_([0-9.]+)$", variant)
    return match.group(1) if match else ""


def event_lambda(variant: str) -> str:
    family = variant_family(variant)
    if family in {"B2", "B4"}:
        return parse_float_suffix(variant, "lambda")
    return ""


def rule_weight(variant: str) -> str:
    return parse_float_suffix(variant, "weight") if variant_family(variant) == "B5" else ""


def pr_tau(variant: str) -> str:
    return parse_float_suffix(variant, "tau") if variant_family(variant) == "B6" else ""


def fairness_flags(row: dict[str, str], *, block_name: str) -> str:
    flags = ["warn_b1_b3_not_independent_rows"]
    variant = row.get("variant", "")
    if variant_family(variant) in {"B5", "B6"}:
        flags.append("warn_local_style_baseline")
    subblock = row.get("block", "")
    if "learning" in subblock or "lambda" in subblock or "tradeoff" in subblock:
        flags.append("warn_partial_baseline_grid")
    if block_name == "block_A_controlled":
        flags.append("warn_controlled_no_b5_b6")
    return ";".join(dict.fromkeys(flags))


def claim_use(block_name: str) -> str:
    return {
        "block_A_controlled": "controlled structural evidence only",
        "block_D_semi_real": "partial semi-real evidence",
        "block_E_real_source_small": "real-source small-field local evidence",
    }[block_name]


def normalize_run(row: dict[str, str], *, block_name: str, task_family: str) -> dict[str, object]:
    variant = row.get("variant", "")
    return {
        "block": row.get("block") or block_name,
        "task_family": task_family,
        "task": row.get("task", ""),
        "setting": row.get("setting", ""),
        "seed": row.get("seed", ""),
        "variant": variant,
        "variant_family": variant_family(variant),
        "train_objective": train_objective(variant),
        "decode_mode": "unconstrained",
        "parameters_from": "",
        "rule_id": row.get("pattern", ""),
        "same_split": "true",
        "same_seed": "true",
        "same_rule": "true",
        "same_label_alphabet": "true",
        "labeled_size": row.get("labeled_size", ""),
        "unlabeled_size": row.get("unlabeled_size", ""),
        "dev_size": row.get("dev_size", ""),
        "epochs": row.get("epochs", ""),
        "lr": row.get("lr", ""),
        "lambda": event_lambda(variant),
        "weight": rule_weight(variant),
        "tau": pr_tau(variant),
        "eta": "1.0" if variant_family(variant) == "B6" else "",
        "rule_feature_weight": rule_weight(variant),
        "pr_tau": pr_tau(variant),
        "pr_eta": "1.0" if variant_family(variant) == "B6" else "",
        "p_event": row.get("mean_p_event", ""),
        "illegal_mass": row.get("mean_illegal_mass", ""),
        "low_p_event_rate": row.get("low_p_event_rate", ""),
        "unconstrained_legal_rate": row.get("unconstrained_event_rate", ""),
        "constrained_legal_rate": row.get("constrained_event_rate", ""),
        "char_accuracy": row.get("char_accuracy", ""),
        "constrained_char_accuracy": row.get("constrained_char_accuracy", ""),
        "exact_sequence_accuracy": row.get("exact_sequence_accuracy", ""),
        "constrained_exact_sequence_accuracy": row.get("constrained_exact_sequence_accuracy", ""),
        "nll": row.get("mean_nll", ""),
        "hidden_conflict_count": "",
        "hidden_conflict_rate": row.get("hidden_conflict_rate", ""),
        "fairness_flags": fairness_flags(row, block_name=block_name),
        "claim_use": claim_use(block_name),
        "notes": row.get("notes", ""),
    }


def normalize_summary(row: dict[str, str], *, block_name: str, task_family: str) -> dict[str, object]:
    variant = row.get("variant", "")
    return {
        "block": row.get("block") or block_name,
        "task_family": task_family,
        "task": row.get("task", ""),
        "setting": row.get("setting", ""),
        "variant": variant,
        "variant_family": variant_family(variant),
        "runs": row.get("runs", ""),
        "mean_p_event": row.get("mean_p_event", ""),
        "delta_p_event": row.get("delta_p_event", ""),
        "ci95_delta_p_event": row.get("ci95_delta_p_event", ""),
        "up_rate_p_event": row.get("p_event_up_rate", ""),
        "mean_illegal_mass": row.get("mean_illegal_mass", ""),
        "delta_illegal_mass": row.get("delta_illegal_mass", ""),
        "low_p_event_rate": row.get("low_p_event_rate", ""),
        "unconstrained_event_rate": row.get("unconstrained_event_rate", ""),
        "delta_unconstrained_event_rate": row.get("delta_unconstrained_event_rate", ""),
        "up_rate_legal": row.get("event_rate_up_rate", ""),
        "constrained_event_rate": row.get("constrained_event_rate", ""),
        "char_accuracy": row.get("char_accuracy", ""),
        "delta_char_accuracy": row.get("delta_char_accuracy", ""),
        "up_rate_char": row.get("char_accuracy_up_rate", ""),
        "constrained_char_accuracy": row.get("constrained_char_accuracy", ""),
        "delta_constrained_char_accuracy": row.get("delta_constrained_char_accuracy", ""),
        "exact_sequence_accuracy": row.get("exact_sequence_accuracy", ""),
        "delta_exact_sequence_accuracy": row.get("delta_exact_sequence_accuracy", ""),
        "up_rate_exact": row.get("exact_sequence_up_rate", ""),
        "constrained_exact_sequence_accuracy": row.get("constrained_exact_sequence_accuracy", ""),
        "delta_constrained_exact_sequence_accuracy": row.get("delta_constrained_exact_sequence_accuracy", ""),
        "mean_nll": row.get("mean_nll", ""),
        "hidden_conflict_rate": row.get("hidden_conflict_rate", ""),
        "fairness_flags": fairness_flags(row, block_name=block_name),
        "claim_use": claim_use(block_name),
        "notes": "",
    }


def is_exact(pred: str, gold: str) -> str:
    return str(pred == gold).lower()


def is_legal(pred: str, pattern: str) -> str:
    if not pred:
        return ""
    if len(pred) != len(pattern):
        return "false"
    for ch, group in zip(pred, pattern):
        if group == "L" and not ch.isalpha():
            return "false"
        if group == "D" and not ch.isdigit():
            return "false"
        if group not in {"L", "D"} and ch != group:
            return "false"
    return "true"


def normalize_case(row: dict[str, str], *, block_name: str, task_family: str, setting: str) -> dict[str, object]:
    pattern = {
        "product_code": "LL-DDD",
        "amount": "$DD.DD",
        "date": "DDDD-DD-DD",
        "dose": "DDDmg",
        "invoice_6d": "DDDDDD",
        "invoice_c6d": "LDDDDDD",
        "stock_5d": "DDDDD",
    }.get(row.get("task", ""), "")
    b0_pred = row.get("baseline_pred", "")
    variant_pred = row.get("event_pred", "")
    gold = row.get("gold", "")
    return {
        "block": block_name,
        "task_family": task_family,
        "task": row.get("task", ""),
        "setting": setting,
        "seed": row.get("seed", ""),
        "case_id": "",
        "tokens": row.get("tokens", ""),
        "gold": gold,
        "b0_prediction": b0_pred,
        "b0_constrained_prediction": row.get("baseline_constrained_pred", ""),
        "variant_prediction": variant_pred,
        "variant_constrained_prediction": row.get("event_constrained_pred", ""),
        "b0_p_event": row.get("baseline_p_event", ""),
        "variant_p_event": row.get("event_p_event", ""),
        "b0_legal": is_legal(b0_pred, pattern),
        "variant_legal": is_legal(variant_pred, pattern),
        "b0_exact": is_exact(b0_pred, gold),
        "variant_exact": is_exact(variant_pred, gold),
        "conflict_type": "hard_constraint_masks_low_p",
        "notes": row.get("comment", "posterior shift case study"),
    }


def export_block(
    *,
    block_name: str,
    task_family: str,
    run_files: list[str],
    summary_files: list[str],
    case_file: str | None = None,
    case_setting: str = "",
) -> None:
    block_dir = OUT_DIR / block_name
    runs: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    for name in run_files:
        runs.extend(normalize_run(row, block_name=block_name, task_family=task_family) for row in read_csv(RESULTS_DIR / name))
    for name in summary_files:
        summaries.extend(
            normalize_summary(row, block_name=block_name, task_family=task_family) for row in read_csv(RESULTS_DIR / name)
        )
    write_csv(block_dir / "runs.csv", runs, RUN_FIELDS)
    write_csv(block_dir / "summary.csv", summaries, SUMMARY_FIELDS)
    if case_file:
        cases = [
            normalize_case(row, block_name=block_name, task_family=task_family, setting=case_setting)
            for row in read_csv(RESULTS_DIR / case_file)
        ]
        for idx, row in enumerate(cases):
            row["case_id"] = f"{block_name}_case_{idx:04d}"
        write_csv(block_dir / "case_studies.csv", cases, CASE_FIELDS)
    else:
        write_csv(block_dir / "case_studies.csv", [], CASE_FIELDS)
    audit = [
        f"# {block_name} Formal Pre-Paper Export Audit",
        "",
        "This directory is generated from existing local probe CSV files.",
        "No new experiment was run by the export step.",
        "",
        "## Scope",
        "",
        f"- task_family: `{task_family}`",
        f"- runs rows: `{len(runs)}`",
        f"- summary rows: `{len(summaries)}`",
        "",
        "## Known Warnings",
        "",
        "- B1/B3 hard-constrained variants are represented through constrained metric fields, not independent rows.",
        "- B5/B6 are local-style baselines unless a future implementation reproduces a specific related-work method.",
        "- These exports preserve local-probe scope and do not create benchmark evidence.",
        "",
    ]
    (block_dir / "audit.md").write_text("\n".join(audit), encoding="utf-8")


def main() -> None:
    global RESULTS_DIR, OUT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default=str(RESULTS_DIR))
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    args = parser.parse_args()
    RESULTS_DIR = Path(args.results_dir)
    OUT_DIR = Path(args.output_dir)

    export_block(
        block_name="block_A_controlled",
        task_family="controlled_format",
        run_files=["formal_validation_runs.csv"],
        summary_files=["formal_validation_summary.csv"],
    )
    export_block(
        block_name="block_D_semi_real",
        task_family="semi_real_field",
        run_files=[
            "semi_real_main_runs.csv",
            "semi_real_learning_curve_runs.csv",
            "semi_real_lambda_tradeoff_runs.csv",
        ],
        summary_files=[
            "semi_real_main_summary.csv",
            "semi_real_learning_curve_summary.csv",
            "semi_real_lambda_tradeoff_summary.csv",
        ],
        case_file="semi_real_case_studies.csv",
        case_setting="case_labeled25_unlabeled100",
    )
    export_block(
        block_name="block_E_real_source_small",
        task_family="real_source_small_field",
        run_files=[
            "real_small_data_main_runs.csv",
            "real_small_data_learning_runs.csv",
            "real_small_data_lambda_runs.csv",
        ],
        summary_files=[
            "real_small_data_main_summary.csv",
            "real_small_data_learning_summary.csv",
            "real_small_data_lambda_summary.csv",
        ],
        case_file="real_small_data_case_studies.csv",
        case_setting="real_case_l25_u100",
    )


if __name__ == "__main__":
    main()
