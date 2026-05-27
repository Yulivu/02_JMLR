"""WNUT17 BIO/NER local smoke for the R5 gate.

This runner is intentionally small. It checks whether the frozen WNUT17 slice
can support the posterior-event story before spending formal-run budget.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Sequence

import torch

from .bio_event import bio_sequence_allowed, extract_strict_bio_spans
from .data_utils import (
    SequenceDataset,
    build_label_vocab,
    build_vocab,
    encode_dataset,
    filter_dataset_by_length,
    normalize_bio_dataset,
    read_conll,
    take_dataset,
)
from .event_crf import TinyLinearChainCRF
from .run_probe import set_seed


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "raw" / "wnut17"
DEFAULT_HIDDEN_CONFLICT_THRESHOLD = 0.7


@dataclass(frozen=True)
class VariantConfig:
    name: str
    labeled_lam: float = 0.0
    unlabeled_lam: float = 0.0


@dataclass
class WnutRun:
    block: str
    variant: str
    seed: int
    train_sentences: int
    unlabeled_sentences: int
    dev_sentences: int
    max_len: int
    epochs: int
    lr: float
    label_count: int
    vocab_size: int
    mean_p_event: float
    median_p_event: float
    mean_illegal_mass: float
    low_p_event_rate: float
    unconstrained_legal_rate: float
    constrained_legal_rate: float
    hidden_conflict_rate: float
    token_accuracy: float
    constrained_token_accuracy: float
    entity_f1: float
    constrained_entity_f1: float
    mean_nll: float
    notes: str


@dataclass
class WnutCase:
    case_id: str
    variant: str
    seed: int
    tokens: str
    gold: str
    unconstrained_pred: str
    constrained_pred: str
    p_event: float
    unconstrained_legal: bool
    constrained_legal: bool
    token_accuracy: float
    constrained_token_accuracy: float
    hidden_conflict: bool


def load_split(data_dir: Path, split: str, *, max_len: int) -> SequenceDataset:
    filename = {"train": "train.conll", "dev": "dev.conll", "test": "test.conll"}[split]
    dataset = normalize_bio_dataset(read_conll(data_dir / filename))
    return filter_dataset_by_length(dataset, max_len=max_len)


def train_model(
    labeled: list[tuple[list[int], list[int]]],
    unlabeled: list[list[int]],
    *,
    vocab_size: int,
    label_names: Sequence[str],
    variant: VariantConfig,
    seed: int,
    epochs: int,
    lr: float,
) -> TinyLinearChainCRF:
    set_seed(seed)
    model = TinyLinearChainCRF(vocab_size, label_names)
    model.assert_cpu_only()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for _epoch in range(epochs):
        labeled_order = list(range(len(labeled)))
        random.shuffle(labeled_order)
        for idx in labeled_order:
            word_ids, label_ids = labeled[idx]
            optimizer.zero_grad(set_to_none=True)
            loss = model.neg_log_likelihood(word_ids, label_ids)
            if variant.labeled_lam:
                loss = loss - variant.labeled_lam * model.log_event_probability_bio(word_ids)
            loss.backward()
            optimizer.step()
        if unlabeled and variant.unlabeled_lam:
            unlabeled_order = list(range(len(unlabeled)))
            random.shuffle(unlabeled_order)
            for idx in unlabeled_order:
                optimizer.zero_grad(set_to_none=True)
                loss = -variant.unlabeled_lam * model.log_event_probability_bio(unlabeled[idx])
                loss.backward()
                optimizer.step()
    return model


def token_accuracy(pred: Sequence[int], gold: Sequence[int]) -> float:
    return sum(int(a == b) for a, b in zip(pred, gold)) / max(1, len(gold))


def entity_counts(pred_labels: Sequence[str], gold_labels: Sequence[str]) -> tuple[int, int, int]:
    pred_spans = extract_strict_bio_spans(pred_labels)
    gold_spans = extract_strict_bio_spans(gold_labels)
    true_positive = len(pred_spans & gold_spans)
    return true_positive, len(pred_spans), len(gold_spans)


def f1_from_counts(true_positive: int, predicted: int, gold: int) -> float:
    if predicted == 0 or gold == 0 or true_positive == 0:
        return 0.0
    precision = true_positive / predicted
    recall = true_positive / gold
    return 2.0 * precision * recall / (precision + recall)


def decode(label_names: Sequence[str], label_ids: Sequence[int]) -> list[str]:
    return [label_names[idx] for idx in label_ids]


def evaluate_model(
    model: TinyLinearChainCRF,
    dev: list[tuple[list[int], list[int]]],
    *,
    label_names: Sequence[str],
    variant: VariantConfig,
    seed: int,
    train_sentences: int,
    unlabeled_sentences: int,
    max_len: int,
    epochs: int,
    lr: float,
    vocab_size: int,
    hidden_conflict_threshold: float,
    id_to_token: dict[int, str],
) -> tuple[WnutRun, list[WnutCase]]:
    p_values: list[float] = []
    nlls: list[float] = []
    unconstrained_legal = 0
    constrained_legal = 0
    hidden_conflicts = 0
    token_scores: list[float] = []
    constrained_token_scores: list[float] = []
    tp = pred_total = gold_total = 0
    c_tp = c_pred_total = c_gold_total = 0
    cases: list[WnutCase] = []

    for idx, (word_ids, gold) in enumerate(dev):
        with torch.no_grad():
            p_event = float(torch.exp(model.log_event_probability_bio(word_ids)).cpu().item())
            nll = float(model.neg_log_likelihood(word_ids, gold).cpu().item()) / max(1, len(gold))
            pred, _ = model.viterbi(word_ids, constrained=False)
            c_pred, _ = model.viterbi(word_ids, constrained=True)
        pred_labels = decode(label_names, pred)
        c_pred_labels = decode(label_names, c_pred)
        gold_labels = decode(label_names, gold)
        pred_legal = bio_sequence_allowed(pred_labels)
        c_pred_legal = bio_sequence_allowed(c_pred_labels)
        hidden_conflict = c_pred_legal and p_event < hidden_conflict_threshold

        p_values.append(p_event)
        nlls.append(nll)
        unconstrained_legal += int(pred_legal)
        constrained_legal += int(c_pred_legal)
        hidden_conflicts += int(hidden_conflict)
        token_scores.append(token_accuracy(pred, gold))
        constrained_token_scores.append(token_accuracy(c_pred, gold))
        row_tp, row_pred_total, row_gold_total = entity_counts(pred_labels, gold_labels)
        row_c_tp, row_c_pred_total, row_c_gold_total = entity_counts(c_pred_labels, gold_labels)
        tp += row_tp
        pred_total += row_pred_total
        gold_total += row_gold_total
        c_tp += row_c_tp
        c_pred_total += row_c_pred_total
        c_gold_total += row_c_gold_total

        if hidden_conflict or len(cases) < 8:
            cases.append(
                WnutCase(
                    case_id=f"wnut17_dev_{seed}_{idx:04d}",
                    variant=variant.name,
                    seed=seed,
                    tokens=" ".join(id_to_token.get(token_id, "<UNK>") for token_id in word_ids),
                    gold=" ".join(gold_labels),
                    unconstrained_pred=" ".join(pred_labels),
                    constrained_pred=" ".join(c_pred_labels),
                    p_event=p_event,
                    unconstrained_legal=pred_legal,
                    constrained_legal=c_pred_legal,
                    token_accuracy=token_scores[-1],
                    constrained_token_accuracy=constrained_token_scores[-1],
                    hidden_conflict=hidden_conflict,
                )
            )

    sorted_p = sorted(p_values)
    median = sorted_p[len(sorted_p) // 2] if sorted_p else 0.0
    run = WnutRun(
        block="r5_wnut17_bio_local_smoke",
        variant=variant.name,
        seed=seed,
        train_sentences=train_sentences,
        unlabeled_sentences=unlabeled_sentences,
        dev_sentences=len(dev),
        max_len=max_len,
        epochs=epochs,
        lr=lr,
        label_count=len(label_names),
        vocab_size=vocab_size,
        mean_p_event=mean(p_values),
        median_p_event=median,
        mean_illegal_mass=1.0 - mean(p_values),
        low_p_event_rate=mean(1.0 if p < hidden_conflict_threshold else 0.0 for p in p_values),
        unconstrained_legal_rate=unconstrained_legal / max(1, len(dev)),
        constrained_legal_rate=constrained_legal / max(1, len(dev)),
        hidden_conflict_rate=hidden_conflicts / max(1, len(dev)),
        token_accuracy=mean(token_scores),
        constrained_token_accuracy=mean(constrained_token_scores),
        entity_f1=f1_from_counts(tp, pred_total, gold_total),
        constrained_entity_f1=f1_from_counts(c_tp, c_pred_total, c_gold_total),
        mean_nll=mean(nlls),
        notes="WNUT17 local smoke only; not formal R5 evidence",
    )
    cases.sort(key=lambda row: (not row.hidden_conflict, row.p_event))
    return run, cases[:20]


def write_table(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(output_dir: Path, runs: list[WnutRun], cases: list[WnutCase]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_rows = [asdict(row) for row in runs]
    case_rows = [asdict(row) for row in cases]
    summary = summarize_runs(runs)
    (output_dir / "runs.json").write_text(json.dumps(run_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "case_studies.json").write_text(json.dumps(case_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    write_table(output_dir / "runs.csv", run_rows)
    write_table(output_dir / "summary.csv", summary)
    write_table(output_dir / "case_studies.csv", case_rows)
    write_report(output_dir, summary, cases)


def summarize_runs(runs: Sequence[WnutRun]) -> list[dict[str, object]]:
    by_key = {(run.seed, run.variant): run for run in runs}
    rows: list[dict[str, object]] = []
    for run in runs:
        baseline = by_key.get((run.seed, "B0_unconstrained"))
        delta_p = run.mean_p_event - baseline.mean_p_event if baseline is not None else 0.0
        rows.append(
            {
                "block": run.block,
                "variant": run.variant,
                "seed": run.seed,
                "train_sentences": run.train_sentences,
                "unlabeled_sentences": run.unlabeled_sentences,
                "dev_sentences": run.dev_sentences,
                "max_len": run.max_len,
                "mean_p_event": run.mean_p_event,
                "delta_p_event_vs_b0": delta_p,
                "mean_illegal_mass": run.mean_illegal_mass,
                "low_p_event_rate": run.low_p_event_rate,
                "unconstrained_legal_rate": run.unconstrained_legal_rate,
                "constrained_legal_rate": run.constrained_legal_rate,
                "hidden_conflict_rate": run.hidden_conflict_rate,
                "token_accuracy": run.token_accuracy,
                "constrained_token_accuracy": run.constrained_token_accuracy,
                "entity_f1": run.entity_f1,
                "constrained_entity_f1": run.constrained_entity_f1,
                "mean_nll": run.mean_nll,
            }
        )
    return rows


def write_report(output_dir: Path, summary: list[dict[str, object]], cases: list[WnutCase]) -> None:
    lines = [
        "# WNUT17 BIO/NER R5 Local Smoke",
        "",
        "This is a pre-formal gate, not R5 formal evidence.",
        "",
        "## Summary",
        "",
        "| variant | seed | mean P(BIO|x) | illegal mass | unconstrained legal | constrained legal | hidden conflict | token acc | entity F1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary:
        lines.append(
            "| {variant} | {seed} | {p:.4f} | {illegal:.4f} | {ulegal:.4f} | {clegal:.4f} | {hidden:.4f} | {tok:.4f} | {f1:.4f} |".format(
                variant=row["variant"],
                seed=int(row["seed"]),
                p=float(row["mean_p_event"]),
                illegal=float(row["mean_illegal_mass"]),
                ulegal=float(row["unconstrained_legal_rate"]),
                clegal=float(row["constrained_legal_rate"]),
                hidden=float(row["hidden_conflict_rate"]),
                tok=float(row["token_accuracy"]),
                f1=float(row["entity_f1"]),
            )
        )
    hidden_cases = [case for case in cases if case.hidden_conflict]
    lines.extend(
        [
            "",
            "## Gate Reading",
            "",
            "- Pass signal: `constrained_legal_rate` is high while B0 `hidden_conflict_rate` is nonzero.",
            "- Stronger pass signal: B4 raises `P(BIO|x)` without collapsing token/entity metrics.",
            "- Hold signal: B0 `mean_p_event` is saturated near 1 or hidden conflict is absent.",
            "",
            f"Hidden-conflict case rows retained: {len(hidden_cases)}.",
            "",
        ]
    )
    if hidden_cases:
        lines.extend(
            [
                "## Example Cases",
                "",
                "| case | P(BIO|x) | tokens | unconstrained | constrained | gold |",
                "|---|---:|---|---|---|---|",
            ]
        )
        for case in hidden_cases[:8]:
            lines.append(
                f"| `{case.case_id}` | {case.p_event:.4f} | `{case.tokens}` | `{case.unconstrained_pred}` | `{case.constrained_pred}` | `{case.gold}` |"
            )
    (output_dir / "audit.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_smoke(
    *,
    data_dir: Path,
    output_dir: Path,
    seed: int,
    train_size: int,
    unlabeled_size: int,
    dev_size: int,
    max_len: int,
    epochs: int,
    lr: float,
    hidden_conflict_threshold: float,
) -> None:
    train_full = load_split(data_dir, "train", max_len=max_len)
    dev_full = load_split(data_dir, "dev", max_len=max_len)
    labeled_ds = take_dataset(train_full, start=0, count=train_size, name="wnut17_train_labeled")
    unlabeled_ds = take_dataset(train_full, start=train_size, count=unlabeled_size, name="wnut17_train_unlabeled")
    dev_ds = take_dataset(dev_full, start=0, count=dev_size, name="wnut17_dev_smoke")

    vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens)
    label_to_idx = build_label_vocab(train_full.labels)
    label_names = [label for label, _idx in sorted(label_to_idx.items(), key=lambda item: item[1])]
    labeled = encode_dataset(labeled_ds, vocab, label_to_idx)
    unlabeled = [word_ids for word_ids, _labels in encode_dataset(unlabeled_ds, vocab, label_to_idx)]
    dev = encode_dataset(dev_ds, vocab, label_to_idx)
    id_to_token = {idx: token for token, idx in vocab.items()}

    variants = [
        VariantConfig("B0_unconstrained"),
        VariantConfig("B4_semi_event_0.1", labeled_lam=0.1, unlabeled_lam=0.1),
    ]
    runs: list[WnutRun] = []
    cases: list[WnutCase] = []
    for variant in variants:
        model = train_model(
            labeled,
            unlabeled,
            vocab_size=len(vocab),
            label_names=label_names,
            variant=variant,
            seed=seed,
            epochs=epochs,
            lr=lr,
        )
        run, variant_cases = evaluate_model(
            model,
            dev,
            label_names=label_names,
            variant=variant,
            seed=seed,
            train_sentences=len(labeled),
            unlabeled_sentences=len(unlabeled),
            max_len=max_len,
            epochs=epochs,
            lr=lr,
            vocab_size=len(vocab),
            hidden_conflict_threshold=hidden_conflict_threshold,
            id_to_token=id_to_token,
        )
        runs.append(run)
        cases.extend(variant_cases)
    write_outputs(output_dir, runs, cases)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output-dir", default="experiments/runs/local_checks/r5_wnut17_bio_smoke")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-size", type=int, default=200)
    parser.add_argument("--unlabeled-size", type=int, default=300)
    parser.add_argument("--dev-size", type=int, default=120)
    parser.add_argument("--max-len", type=int, default=40)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--hidden-conflict-threshold", type=float, default=DEFAULT_HIDDEN_CONFLICT_THRESHOLD)
    args = parser.parse_args()

    run_smoke(
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
        seed=args.seed,
        train_size=args.train_size,
        unlabeled_size=args.unlabeled_size,
        dev_size=args.dev_size,
        max_len=args.max_len,
        epochs=args.epochs,
        lr=args.lr,
        hidden_conflict_threshold=args.hidden_conflict_threshold,
    )


if __name__ == "__main__":
    main()
