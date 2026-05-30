"""R7 lambda/rule sensitivity probe.

This runner reuses the semi-real field machinery and reports event-mass/task
tradeoffs across lambda values and rule difficulty levels. It is a boundary
study, not an accuracy method.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Sequence

import torch

from .semi_real_format_probe import (
    LAMBDA_VARIANTS,
    TASKS,
    ProbeRun,
    ProbeSetting,
    SemiRealTask,
    VariantConfig,
    build_vocab,
    encode,
    evaluate_model,
    make_dataset,
    run_settings,
    summarize_runs,
    train_model,
)


DIFFICULTY_TASKS = {
    "easy_saturated": ("stock_like_digits", ("D", "D", "D"), "short digit-only field; often saturated"),
    "medium": ("product_code", ("L", "L", "-", "D", "D", "D"), "mixed product-code field"),
    "hard": ("date", ("D", "D", "D", "D", "-", "D", "D", "-", "D", "D"), "longer date-like field"),
}


def make_tasks(levels: Sequence[str]) -> list[SemiRealTask]:
    tasks_by_name = {task.name: task for task in TASKS}
    out: list[SemiRealTask] = []
    for level in levels:
        name, pattern, description = DIFFICULTY_TASKS[level]
        if name in tasks_by_name:
            out.append(tasks_by_name[name])
        else:
            out.append(SemiRealTask(name, pattern, description))
    return out


def write_table(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def boundary_rows(summary: Sequence[dict[str, float | str | int]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    grouped: dict[str, list[dict[str, float | str | int]]] = {}
    for row in summary:
        grouped.setdefault(str(row["task"]), []).append(row)
    for task, group in sorted(grouped.items()):
        non_baseline = [row for row in group if row["variant"] != "B0_unconstrained"]
        best_event = max(non_baseline, key=lambda row: float(row["delta_p_event"]))
        best_exact = max(non_baseline, key=lambda row: float(row["delta_exact_sequence_accuracy"]))
        saturated = max(float(row["mean_p_event"]) for row in group if row["variant"] == "B0_unconstrained") > 0.95
        legal_rate_not_useful = max(float(row["delta_unconstrained_event_rate"]) for row in non_baseline) <= 0.0
        tradeoff = any(float(row["delta_p_event"]) > 0 and float(row["delta_exact_sequence_accuracy"]) < 0 for row in non_baseline)
        rows.append(
            {
                "task": task,
                "baseline_saturated": saturated,
                "legal_rate_not_useful": legal_rate_not_useful,
                "best_event_variant": best_event["variant"],
                "best_delta_p_event": best_event["delta_p_event"],
                "best_exact_variant": best_exact["variant"],
                "best_delta_exact_sequence_accuracy": best_exact["delta_exact_sequence_accuracy"],
                "event_task_tradeoff_observed": tradeoff,
            }
        )
    return rows


def _run_one_job(payload: tuple[SemiRealTask, ProbeSetting, int, str, VariantConfig]) -> ProbeRun:
    task, setting, seed, _variant_name, variant = payload
    torch.set_num_threads(1)
    label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
    labeled_ds = make_dataset(task, f"{task.name}_labeled", setting.labeled_size, seed=1100 + seed)
    unlabeled_ds = make_dataset(task, f"{task.name}_unlabeled", setting.unlabeled_size, seed=2200 + seed)
    dev_ds = make_dataset(task, f"{task.name}_dev", setting.dev_size, seed=3300 + seed)
    vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens + dev_ds.tokens)
    labeled = encode(labeled_ds, vocab, label_to_idx)
    unlabeled = [word_ids for word_ids, _labels in encode(unlabeled_ds, vocab, label_to_idx)]
    dev = encode(dev_ds, vocab, label_to_idx)
    model = train_model(
        task,
        labeled,
        unlabeled,
        len(vocab),
        variant=variant,
        seed=seed,
        epochs=setting.epochs,
        lr=setting.lr,
    )
    return evaluate_model(model, task, dev, setting=setting, variant=variant, seed=seed)


def run_settings_parallel(
    tasks: Sequence[SemiRealTask],
    setting: ProbeSetting,
    variants: dict[str, VariantConfig],
    *,
    workers: int,
) -> list[ProbeRun]:
    jobs = [
        (task, setting, seed, variant_name, variants[variant_name])
        for task in tasks
        for seed in setting.seeds
        for variant_name in setting.variants
    ]
    if not jobs:
        return []
    max_workers = min(workers, len(jobs))
    runs: list[ProbeRun] = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_run_one_job, job) for job in jobs]
        for future in as_completed(futures):
            runs.append(future.result())
    return sorted(runs, key=lambda row: (row.task, row.seed, row.variant))


def write_report(output_dir: Path, summary: Sequence[dict[str, float | str | int]], boundaries: Sequence[dict[str, object]]) -> None:
    lines = [
        "# R7 Lambda / Rule Sensitivity Probe",
        "",
        "This is a sensitivity and boundary study. It is not benchmark evidence.",
        "",
        "## Lambda Tradeoff",
        "",
        "| task | variant | runs | P(L|x) | delta P | delta legal rate | delta exact acc |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        if row["variant"] == "B0_unconstrained":
            continue
        lines.append(
            "| {task} | {variant} | {runs} | {p:.4f} | {dp:+.4f} | {dl:+.4f} | {de:+.4f} |".format(
                task=row["task"],
                variant=row["variant"],
                runs=int(row["runs"]),
                p=float(row["mean_p_event"]),
                dp=float(row["delta_p_event"]),
                dl=float(row["delta_unconstrained_event_rate"]),
                de=float(row["delta_exact_sequence_accuracy"]),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary Cases",
            "",
            "| task | baseline saturated | best event variant | best delta P | best exact variant | best delta exact | event/task tradeoff observed |",
            "|---|---|---|---:|---|---:|---|",
        ]
    )
    for row in boundaries:
        lines.append(
            "| {task} | {sat} | {bev} | {bdp:+.4f} | {bex} | {bde:+.4f} | {trade} |".format(
                task=row["task"],
                sat=f"{row['baseline_saturated']} / legal-rate-not-useful={row['legal_rate_not_useful']}",
                bev=row["best_event_variant"],
                bdp=float(row["best_delta_p_event"]),
                bex=row["best_exact_variant"],
                bde=float(row["best_delta_exact_sequence_accuracy"]),
                trade=row["event_task_tradeoff_observed"],
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Allowed: event loss can move posterior event mass, and the tradeoff depends on lambda and rule difficulty.",
            "",
            "Forbidden: event training always improves accuracy, event risk is universally useful, or saturated/not-useful rules provide meaningful diagnostic value.",
            "",
        ]
    )
    (output_dir / "R7_SENSITIVITY_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def run_probe(*, output_dir: Path, seed_count: int, quick: bool, difficulty_levels: Sequence[str], workers: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    seeds = tuple(range(min(seed_count, 2) if quick else seed_count))
    tasks = make_tasks(difficulty_levels)
    setting = ProbeSetting(
        block="r7_sensitivity",
        name="lambda_rule_difficulty",
        labeled_size=25,
        unlabeled_size=100,
        dev_size=80 if quick else 250,
        epochs=2 if quick else 5,
        lr=0.08,
        seeds=seeds,
        variants=tuple(LAMBDA_VARIANTS.keys()),
    )
    resolved_workers = (os.cpu_count() or 1) if workers == 0 else workers
    if resolved_workers > 1:
        runs = run_settings_parallel(tasks, setting, LAMBDA_VARIANTS, workers=resolved_workers)
    else:
        runs = run_settings(tasks, [setting], LAMBDA_VARIANTS)
    run_dicts = [asdict(row) for row in runs]
    summary = summarize_runs(runs)
    boundaries = boundary_rows(summary)
    (output_dir / "r7_sensitivity_runs.json").write_text(json.dumps(run_dicts, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "r7_sensitivity_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_table(output_dir / "r7_sensitivity_runs.csv", run_dicts)
    write_table(output_dir / "r7_sensitivity_summary.csv", summary)
    write_table(output_dir / "r7_sensitivity_boundaries.csv", boundaries)
    write_report(output_dir, summary, boundaries)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/runs/local_checks/r7_sensitivity_smoke")
    parser.add_argument("--seed-count", type=int, default=3)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--difficulty-levels", nargs="*", default=["easy_saturated", "medium", "hard"])
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Parallel worker processes for seed/rule/lambda jobs. Use 0 for all available CPU cores.",
    )
    args = parser.parse_args()
    unknown = sorted(set(args.difficulty_levels) - set(DIFFICULTY_TASKS))
    if unknown:
        raise SystemExit(f"unknown difficulty levels: {', '.join(unknown)}")
    run_probe(
        output_dir=Path(args.output_dir),
        seed_count=args.seed_count,
        quick=args.quick,
        difficulty_levels=args.difficulty_levels,
        workers=args.workers,
    )


if __name__ == "__main__":
    main()
