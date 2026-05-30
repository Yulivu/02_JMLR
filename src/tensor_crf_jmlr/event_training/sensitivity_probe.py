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
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
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
    event_loss,
    labels_follow_pattern,
    log_event_probability,
    nll_loss,
    pr_style_loss,
    make_dataset,
    run_settings,
    summarize_runs,
    train_model,
    viterbi,
)


DIFFICULTY_TASKS = {
    "easy_saturated": ("stock_like_digits", ("D", "D", "D"), "short digit-only field; often saturated"),
    "medium": ("product_code", ("L", "L", "-", "D", "D", "D"), "mixed product-code field"),
    "hard": ("date", ("D", "D", "D", "D", "-", "D", "D", "-", "D", "D"), "longer date-like field"),
    "irrelevant_rule": (
        "product_code_swapped_rule",
        ("L", "L", "-", "D", "D", "D"),
        "product-code data audited against swapped DD-LLL event rule; intentionally weakly related to task correctness",
    ),
}


@dataclass(frozen=True)
class R7TaskSpec:
    name: str
    data_task: SemiRealTask
    event_task: SemiRealTask
    description: str

    @property
    def pattern_string(self) -> str:
        if self.data_task.pattern == self.event_task.pattern:
            return self.data_task.pattern_string
        return f"{self.data_task.pattern_string}->{self.event_task.pattern_string}"


def make_task_specs(levels: Sequence[str]) -> list[R7TaskSpec]:
    tasks_by_name = {task.name: task for task in TASKS}
    out: list[R7TaskSpec] = []
    for level in levels:
        name, pattern, description = DIFFICULTY_TASKS[level]
        if level == "irrelevant_rule":
            data_task = tasks_by_name["product_code"]
            event_task = SemiRealTask("swapped_product_rule", ("D", "D", "-", "L", "L", "L"), description)
            out.append(R7TaskSpec(name, data_task, event_task, description))
        elif name in tasks_by_name:
            task = tasks_by_name[name]
            out.append(R7TaskSpec(task.name, task, task, description))
        else:
            task = SemiRealTask(name, pattern, description)
            out.append(R7TaskSpec(task.name, task, task, description))
    return out


def make_tasks(levels: Sequence[str]) -> list[SemiRealTask]:
    return [spec.data_task for spec in make_task_specs(levels)]


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


def _train_model_for_spec(
    spec: R7TaskSpec,
    labeled: list[tuple[list[int], list[int]]],
    unlabeled: list[list[int]],
    vocab_size: int,
    *,
    variant: VariantConfig,
    seed: int,
    epochs: int,
    lr: float,
) -> torch.nn.Module:
    from .event_crf import TinyLinearChainCRF

    torch.manual_seed(seed)
    random.seed(seed)
    model = TinyLinearChainCRF(vocab_size, spec.data_task.label_names)
    model.assert_cpu_only()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for _epoch in range(epochs):
        labeled_order = list(range(len(labeled)))
        random.shuffle(labeled_order)
        for idx in labeled_order:
            word_ids, label_ids = labeled[idx]
            optimizer.zero_grad(set_to_none=True)
            loss = nll_loss(model, spec.data_task, word_ids, label_ids, rule_bias=variant.rule_bias)
            if variant.labeled_lam:
                loss = loss + variant.labeled_lam * event_loss(model, spec.event_task, word_ids, rule_bias=variant.rule_bias)
            if variant.pr_eta:
                loss = loss + variant.pr_eta * pr_style_loss(
                    model,
                    spec.event_task,
                    word_ids,
                    tau=variant.pr_tau,
                    rule_bias=variant.rule_bias,
                )
            loss.backward()
            optimizer.step()
        if unlabeled and (variant.unlabeled_lam or variant.pr_eta):
            unlabeled_order = list(range(len(unlabeled)))
            random.shuffle(unlabeled_order)
            for idx in unlabeled_order:
                optimizer.zero_grad(set_to_none=True)
                loss = torch.tensor(0.0)
                if variant.unlabeled_lam:
                    loss = loss + variant.unlabeled_lam * event_loss(
                        model,
                        spec.event_task,
                        unlabeled[idx],
                        rule_bias=variant.rule_bias,
                    )
                if variant.pr_eta:
                    loss = loss + variant.pr_eta * pr_style_loss(
                        model,
                        spec.event_task,
                        unlabeled[idx],
                        tau=variant.pr_tau,
                        rule_bias=variant.rule_bias,
                    )
                loss.backward()
                optimizer.step()
    return model


def _evaluate_model_for_spec(
    model: torch.nn.Module,
    spec: R7TaskSpec,
    dev: list[tuple[list[int], list[int]]],
    *,
    setting: ProbeSetting,
    variant: VariantConfig,
    seed: int,
) -> ProbeRun:
    from statistics import mean

    p_values: list[float] = []
    nlls: list[float] = []
    unconstrained_event = 0
    constrained_event = 0
    hidden_conflict = 0
    total_chars = 0
    correct_chars = 0
    constrained_correct_chars = 0
    exact_sequences = 0
    constrained_exact_sequences = 0
    for word_ids, gold in dev:
        with torch.no_grad():
            p_event = float(torch.exp(log_event_probability(model, spec.event_task, word_ids, rule_bias=variant.rule_bias)).item())
            nll = float(nll_loss(model, spec.data_task, word_ids, gold, rule_bias=variant.rule_bias).item()) / len(gold)
            pred, _score = viterbi(model, spec.data_task, word_ids, constrained=False, rule_bias=variant.rule_bias)
            c_pred, _c_score = viterbi(model, spec.event_task, word_ids, constrained=True, rule_bias=variant.rule_bias)
        p_values.append(p_event)
        nlls.append(nll)
        pred_is_event = labels_follow_pattern(spec.event_task, model.label_names, pred)
        c_pred_is_event = labels_follow_pattern(spec.event_task, model.label_names, c_pred)
        unconstrained_event += int(pred_is_event)
        constrained_event += int(c_pred_is_event)
        hidden_conflict += int(c_pred_is_event and p_event < 0.5)
        exact_sequences += int(tuple(pred) == tuple(gold))
        constrained_exact_sequences += int(tuple(c_pred) == tuple(gold))
        for pred_idx, c_pred_idx, gold_idx in zip(pred, c_pred, gold):
            total_chars += 1
            correct_chars += int(pred_idx == gold_idx)
            constrained_correct_chars += int(c_pred_idx == gold_idx)
    return ProbeRun(
        block=setting.block,
        task=spec.name,
        pattern=spec.pattern_string,
        setting=setting.name,
        variant=variant.name,
        seed=seed,
        labeled_size=setting.labeled_size,
        unlabeled_size=setting.unlabeled_size,
        dev_size=setting.dev_size,
        epochs=setting.epochs,
        lr=setting.lr,
        mean_p_event=mean(p_values),
        mean_illegal_mass=1.0 - mean(p_values),
        low_p_event_rate=mean(1.0 if p < 0.5 else 0.0 for p in p_values),
        unconstrained_event_rate=unconstrained_event / len(dev),
        constrained_event_rate=constrained_event / len(dev),
        char_accuracy=correct_chars / total_chars,
        constrained_char_accuracy=constrained_correct_chars / total_chars,
        exact_sequence_accuracy=exact_sequences / len(dev),
        constrained_exact_sequence_accuracy=constrained_exact_sequences / len(dev),
        mean_nll=mean(nlls),
        hidden_conflict_rate=hidden_conflict / len(dev),
        notes=f"R7 sensitivity boundary probe; event_rule={spec.event_task.pattern_string}; not benchmark evidence",
    )


def _run_one_job(payload: tuple[R7TaskSpec, ProbeSetting, int, str, VariantConfig]) -> ProbeRun:
    spec, setting, seed, _variant_name, variant = payload
    torch.set_num_threads(1)
    label_to_idx = {label: idx for idx, label in enumerate(spec.data_task.label_names)}
    labeled_ds = make_dataset(spec.data_task, f"{spec.name}_labeled", setting.labeled_size, seed=1100 + seed)
    unlabeled_ds = make_dataset(spec.data_task, f"{spec.name}_unlabeled", setting.unlabeled_size, seed=2200 + seed)
    dev_ds = make_dataset(spec.data_task, f"{spec.name}_dev", setting.dev_size, seed=3300 + seed)
    vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens + dev_ds.tokens)
    labeled = encode(labeled_ds, vocab, label_to_idx)
    unlabeled = [word_ids for word_ids, _labels in encode(unlabeled_ds, vocab, label_to_idx)]
    dev = encode(dev_ds, vocab, label_to_idx)
    if spec.data_task.pattern == spec.event_task.pattern and spec.data_task.name == spec.event_task.name:
        model = train_model(
            spec.data_task,
            labeled,
            unlabeled,
            len(vocab),
            variant=variant,
            seed=seed,
            epochs=setting.epochs,
            lr=setting.lr,
        )
    else:
        model = _train_model_for_spec(
            spec,
            labeled,
            unlabeled,
            len(vocab),
            variant=variant,
            seed=seed,
            epochs=setting.epochs,
            lr=setting.lr,
        )
    return _evaluate_model_for_spec(model, spec, dev, setting=setting, variant=variant, seed=seed)


def run_settings_parallel(
    task_specs: Sequence[R7TaskSpec],
    setting: ProbeSetting,
    variants: dict[str, VariantConfig],
    *,
    workers: int,
) -> list[ProbeRun]:
    jobs = [
        (spec, setting, seed, variant_name, variants[variant_name])
        for spec in task_specs
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
        "| task | variant | runs | P(L|x) | delta P | delta legal rate | delta exact acc | delta constrained exact |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        if row["variant"] == "B0_unconstrained":
            continue
        lines.append(
            "| {task} | {variant} | {runs} | {p:.4f} | {dp:+.4f} | {dl:+.4f} | {de:+.4f} | {dce:+.4f} |".format(
                task=row["task"],
                variant=row["variant"],
                runs=int(row["runs"]),
                p=float(row["mean_p_event"]),
                dp=float(row["delta_p_event"]),
                dl=float(row["delta_unconstrained_event_rate"]),
                de=float(row["delta_exact_sequence_accuracy"]),
                dce=float(row["delta_constrained_exact_sequence_accuracy"]),
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
    task_specs = make_task_specs(difficulty_levels)
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
        runs = run_settings_parallel(task_specs, setting, LAMBDA_VARIANTS, workers=resolved_workers)
    else:
        ordinary_tasks = [spec.data_task for spec in task_specs if spec.data_task == spec.event_task]
        custom_specs = [spec for spec in task_specs if spec.data_task != spec.event_task]
        runs = run_settings(ordinary_tasks, [setting], LAMBDA_VARIANTS)
        for spec in custom_specs:
            for seed in setting.seeds:
                for variant_name in setting.variants:
                    runs.append(_run_one_job((spec, setting, seed, variant_name, LAMBDA_VARIANTS[variant_name])))
        runs = sorted(runs, key=lambda row: (row.task, row.seed, row.variant))
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
