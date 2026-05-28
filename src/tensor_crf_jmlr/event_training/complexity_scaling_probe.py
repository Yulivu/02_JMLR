"""Complexity scaling probe for CRF x DFA posterior event transfer.

This module measures small CPU wall-clock scaling for the reference product
transfer implementation. It is a complexity audit, not an optimized benchmark
and not a low-rank claim.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import time
from dataclasses import asdict, dataclass
from math import exp, sqrt
from pathlib import Path
from statistics import mean, stdev
from typing import Callable

from tensor_crf_jmlr.posterior_event_algebra.dfa import make_mod_count_monitor
from tensor_crf_jmlr.posterior_event_algebra.product_transfer import (
    event_partition_transfer_first_order_reduced,
    event_partition_transfer_context_order_m,
)


@dataclass(frozen=True)
class ScalingSetting:
    setting: str
    sequence_length: int
    label_count: int
    dfa_states: int
    context_order: int
    repeats: int
    seed: int


@dataclass
class ScalingRun:
    setting: str
    sequence_length: int
    label_count: int
    dfa_states: int
    context_order: int
    product_state_count: int
    repeats: int
    seed: int
    mean_seconds: float
    min_seconds: float
    max_seconds: float
    event_partition: float
    notes: str


def ci95(values: list[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return 1.96 * stdev(values) / sqrt(len(values))


def make_positive_first_order_factors(
    labels: tuple[int, ...],
    sequence_length: int,
    *,
    seed: int,
) -> tuple[list[Callable[[int], float]], list[Callable[[int, int], float]]]:
    rng = random.Random(seed)
    emissions = [{label: rng.uniform(-0.2, 0.2) for label in labels} for _ in range(sequence_length)]
    transitions = [
        {(prev, label): rng.uniform(-0.1, 0.1) for prev in labels for label in labels}
        for _ in range(sequence_length)
    ]

    def make_e(table: dict[int, float]) -> Callable[[int], float]:
        return lambda label, table=table: table[label]

    def make_a(table: dict[tuple[int, int], float]) -> Callable[[int, int], float]:
        return lambda prev, label, table=table: table[(prev, label)]

    return [make_e(table) for table in emissions], [make_a(table) for table in transitions]


def make_context_factors(
    labels: tuple[int, ...],
    sequence_length: int,
    *,
    seed: int,
) -> list[Callable[[tuple[object, ...], int], float]]:
    rng = random.Random(seed)
    weights = [{label: exp(rng.uniform(-0.2, 0.2)) for label in labels} for _ in range(sequence_length)]

    def make_g(table: dict[int, float]) -> Callable[[tuple[object, ...], int], float]:
        return lambda _context, label, table=table: table[label]

    return [make_g(table) for table in weights]


def run_setting(setting: ScalingSetting) -> ScalingRun:
    labels = tuple(range(setting.label_count))
    dfa = make_mod_count_monitor(labels, symbol=0, modulus=setting.dfa_states, accepting_residues={0})
    product_state_count = setting.label_count * len(dfa.states) if setting.context_order == 1 else (
        ((setting.label_count + 1) ** (setting.context_order - 1)) * len(dfa.states)
    )
    durations: list[float] = []
    value = 0.0
    for repeat in range(setting.repeats):
        seed = setting.seed + repeat
        started = time.perf_counter()
        if setting.context_order == 1:
            e_fns, a_fns = make_positive_first_order_factors(labels, setting.sequence_length, seed=seed)
            value = event_partition_transfer_first_order_reduced(
                labels,
                setting.sequence_length,
                e_fns,
                a_fns,
                dfa,
            )
        else:
            g_fns = make_context_factors(labels, setting.sequence_length, seed=seed)
            value = event_partition_transfer_context_order_m(
                labels,
                setting.sequence_length,
                setting.context_order,
                g_fns,
                dfa,
            )
        durations.append(time.perf_counter() - started)
    return ScalingRun(
        setting=setting.setting,
        sequence_length=setting.sequence_length,
        label_count=setting.label_count,
        dfa_states=len(dfa.states),
        context_order=setting.context_order,
        product_state_count=product_state_count,
        repeats=setting.repeats,
        seed=setting.seed,
        mean_seconds=mean(durations),
        min_seconds=min(durations),
        max_seconds=max(durations),
        event_partition=value,
        notes="reference CPU product-transfer scaling; not optimized benchmark evidence",
    )


def default_settings(seed_count: int, repeats: int) -> list[ScalingSetting]:
    settings: list[ScalingSetting] = []
    seed = 0
    for sequence_length in (10, 20, 40, 80):
        for dfa_states in (2, 4, 8, 16):
            settings.append(
                ScalingSetting(
                    setting="vary_length_dfa",
                    sequence_length=sequence_length,
                    label_count=8,
                    dfa_states=dfa_states,
                    context_order=1,
                    repeats=repeats,
                    seed=seed,
                )
            )
            seed += seed_count
    for label_count in (4, 8, 16, 32):
        settings.append(
            ScalingSetting(
                setting="vary_label_count",
                sequence_length=40,
                label_count=label_count,
                dfa_states=8,
                context_order=1,
                repeats=repeats,
                seed=seed,
            )
        )
        seed += seed_count
    for context_order in (1, 2):
        settings.append(
            ScalingSetting(
                setting="context_order_sanity",
                sequence_length=30,
                label_count=6,
                dfa_states=4,
                context_order=context_order,
                repeats=repeats,
                seed=seed,
            )
        )
        seed += seed_count
    return settings


def summarize(runs: list[ScalingRun]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    groups: dict[str, list[ScalingRun]] = {}
    for run in runs:
        groups.setdefault(run.setting, []).append(run)
    for setting, group in sorted(groups.items()):
        rows.append(
            {
                "setting": setting,
                "rows": len(group),
                "min_product_state_count": min(run.product_state_count for run in group),
                "max_product_state_count": max(run.product_state_count for run in group),
                "min_mean_seconds": min(run.mean_seconds for run in group),
                "max_mean_seconds": max(run.mean_seconds for run in group),
                "mean_seconds_ci95": ci95([run.mean_seconds for run in group]),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: object) -> str:
    return f"{value:.6f}" if isinstance(value, float) else str(value)


def write_report(output_dir: Path, runs: list[ScalingRun], summary: list[dict[str, object]]) -> None:
    lines = [
        "# R8 Complexity Scaling Report",
        "",
        "This report measures the reference CPU product-transfer implementation.",
        "It is not an optimized runtime benchmark and does not support arbitrary low-rank claims.",
        "",
        "## Summary",
        "",
        "| setting | rows | product states min-max | mean seconds min-max |",
        "|---|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| {setting} | {rows} | {pmin}-{pmax} | {smin}-{smax} |".format(
                setting=row["setting"],
                rows=row["rows"],
                pmin=row["min_product_state_count"],
                pmax=row["max_product_state_count"],
                smin=fmt(row["min_mean_seconds"]),
                smax=fmt(row["max_mean_seconds"]),
            )
        )
    lines.extend(
        [
            "",
            "## Detailed Runs",
            "",
            "| setting | T | labels | DFA states | context order | product states | mean seconds |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for run in runs:
        lines.append(
            "| {setting} | {t} | {labels} | {dfa} | {m} | {states} | {sec} |".format(
                setting=run.setting,
                t=run.sequence_length,
                labels=run.label_count,
                dfa=run.dfa_states,
                m=run.context_order,
                states=run.product_state_count,
                sec=fmt(run.mean_seconds),
            )
        )
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "Allowed: product-state size and wall-clock scale with sequence length, label count, context order, and DFA states in the reference implementation.",
            "",
            "Not allowed: optimized speed claim, GPU claim, arbitrary low-rank claim, or benchmark superiority claim.",
            "",
        ]
    )
    (output_dir / "R8_COMPLEXITY_SCALING_REPORT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/results/event_training/formal_pre_paper/r8_complexity")
    parser.add_argument("--seed-count", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    runs = [run_setting(setting) for setting in default_settings(args.seed_count, args.repeats)]
    run_dicts = [asdict(run) for run in runs]
    summary = summarize(runs)
    write_csv(output_dir / "complexity_runs.csv", run_dicts)
    write_csv(output_dir / "complexity_summary.csv", summary)
    (output_dir / "complexity_runs.json").write_text(json.dumps(run_dicts, indent=2), encoding="utf-8")
    (output_dir / "complexity_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_report(output_dir, runs, summary)


if __name__ == "__main__":
    main()
