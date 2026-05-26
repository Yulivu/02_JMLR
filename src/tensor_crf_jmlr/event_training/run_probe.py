"""Run CPU-only event-training local probes.

The outputs are local-probe evidence only. They are not benchmark results.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import asdict, dataclass
from math import nan
from pathlib import Path
from statistics import mean, median
from typing import Sequence

import torch

from .bio_event import bio_sequence_allowed
from .data_utils import (
    SequenceDataset,
    build_label_vocab,
    build_vocab,
    encode_dataset,
    make_tiny_conll_like_dataset,
    make_synthetic_bio_dataset,
    make_transition_sparse_bio_dataset,
    read_conll,
)
from .event_crf import TinyLinearChainCRF


REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data" / "raw"


@dataclass
class RunResult:
    dataset: str
    split: str
    seed: int
    lam: float
    epochs: int
    train_sentences: int
    dev_sentences: int
    mean_p_event: float
    median_p_event: float
    mean_nll: float
    token_accuracy: float
    legal_viterbi_rate: float
    constrained_legal_rate: float
    conflict_count: int
    mean_gold_path_prob: float
    mean_legal_non_gold_mass: float
    mean_illegal_mass: float
    top_legal_mass: float
    notes: str


def set_seed(seed: int) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(1)


def train_model(
    train_data: list[tuple[list[int], list[int]]],
    vocab_size: int,
    label_names: Sequence[str],
    *,
    lam: float,
    seed: int,
    epochs: int,
    lr: float = 0.1,
) -> TinyLinearChainCRF:
    set_seed(seed)
    model = TinyLinearChainCRF(vocab_size, label_names)
    model.assert_cpu_only()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for _epoch in range(epochs):
        order = list(range(len(train_data)))
        random.shuffle(order)
        for idx in order:
            word_ids, label_ids = train_data[idx]
            optimizer.zero_grad(set_to_none=True)
            loss = model.event_regularized_loss(word_ids, label_ids, lam)
            if not torch.isfinite(loss):
                raise RuntimeError("non-finite loss in probe training")
            loss.backward()
            optimizer.step()
    return model


def evaluate_model(
    model: TinyLinearChainCRF,
    dev_data: list[tuple[list[int], list[int]]],
    *,
    label_names: Sequence[str],
    dataset_name: str,
    split: str,
    seed: int,
    lam: float,
    epochs: int,
    train_sentences: int,
) -> RunResult:
    p_events: list[float] = []
    nlls: list[float] = []
    total_tokens = 0
    correct_tokens = 0
    legal_viterbi = 0
    constrained_legal = 0
    conflict_count = 0
    gold_path_probs: list[float] = []
    legal_non_gold_masses: list[float] = []
    illegal_masses: list[float] = []
    top_legal_masses: list[float] = []
    for word_ids, gold in dev_data:
        with torch.no_grad():
            log_p = model.log_event_probability_bio(word_ids)
            p_event = float(torch.exp(log_p).cpu().item())
            gold_path_prob = float(torch.exp(model.log_path_probability(word_ids, gold)).cpu().item())
            nll = float(model.neg_log_likelihood(word_ids, gold).cpu().item())
            pred, _ = model.viterbi(word_ids, constrained=False)
            constrained_pred, _ = model.viterbi(word_ids, constrained=True)
            pred_labels = [label_names[idx] for idx in pred]
            constrained_labels = [label_names[idx] for idx in constrained_pred]
            legal_viterbi += int(bio_sequence_allowed(pred_labels))
            constrained_legal += int(bio_sequence_allowed(constrained_labels))
            conflict_count += int(bio_sequence_allowed(constrained_labels) and p_event < 0.7)
            if len(word_ids) <= 8 and len(label_names) ** len(word_ids) <= 200_000:
                legal_paths = model.legal_path_distribution(word_ids, top_k=3)
                top_legal_masses.append(sum(prob for _path, prob in legal_paths))
            p_events.append(p_event)
            gold_path_probs.append(gold_path_prob)
            legal_non_gold_masses.append(max(0.0, p_event - gold_path_prob))
            illegal_masses.append(max(0.0, 1.0 - p_event))
            nlls.append(nll / max(1, len(word_ids)))
            total_tokens += len(gold)
            correct_tokens += sum(int(a == b) for a, b in zip(pred, gold))
    return RunResult(
        dataset=dataset_name,
        split=split,
        seed=seed,
        lam=lam,
        epochs=epochs,
        train_sentences=train_sentences,
        dev_sentences=len(dev_data),
        mean_p_event=mean(p_events),
        median_p_event=median(p_events),
        mean_nll=mean(nlls),
        token_accuracy=correct_tokens / max(1, total_tokens),
        legal_viterbi_rate=legal_viterbi / max(1, len(dev_data)),
        constrained_legal_rate=constrained_legal / max(1, len(dev_data)),
        conflict_count=conflict_count,
        mean_gold_path_prob=mean(gold_path_probs),
        mean_legal_non_gold_mass=mean(legal_non_gold_masses),
        mean_illegal_mass=mean(illegal_masses),
        top_legal_mass=mean(top_legal_masses) if top_legal_masses else nan,
        notes="diagnostic-only; not benchmark/usefulness evidence",
    )


def run_dataset(
    train: SequenceDataset,
    dev: SequenceDataset,
    *,
    dataset_name: str,
    lams: Sequence[float],
    seeds: Sequence[int],
    epochs: int,
) -> list[RunResult]:
    word_to_idx = build_vocab(train.tokens)
    label_to_idx = build_label_vocab(train.labels)
    label_names = [label for label, _idx in sorted(label_to_idx.items(), key=lambda item: item[1])]
    train_encoded = encode_dataset(train, word_to_idx, label_to_idx)
    dev_encoded = encode_dataset(dev, word_to_idx, label_to_idx)
    results: list[RunResult] = []
    for seed in seeds:
        for lam in lams:
            model = train_model(
                train_encoded,
                len(word_to_idx),
                label_names,
                lam=lam,
                seed=seed,
                epochs=epochs,
            )
            results.append(
                evaluate_model(
                    model,
                    dev_encoded,
                    label_names=label_names,
                    dataset_name=dataset_name,
                    split=dev.name,
                    seed=seed,
                    lam=lam,
                    epochs=epochs,
                    train_sentences=len(train_encoded),
                )
            )
    return results


def summarize_by_dataset_lambda(results: Sequence[RunResult]) -> list[dict[str, float | str]]:
    groups: dict[tuple[str, float], list[RunResult]] = {}
    for result in results:
        groups.setdefault((result.dataset, result.lam), []).append(result)
    rows: list[dict[str, float | str]] = []
    for (dataset, lam), group in sorted(groups.items()):
        rows.append(
            {
                "dataset": dataset,
                "lambda": lam,
                "runs": len(group),
                "mean_p_event": mean(r.mean_p_event for r in group),
                "median_p_event": mean(r.median_p_event for r in group),
                "mean_nll": mean(r.mean_nll for r in group),
                "token_accuracy": mean(r.token_accuracy for r in group),
                "conflict_count": sum(r.conflict_count for r in group),
                "mean_gold_path_prob": mean(r.mean_gold_path_prob for r in group),
                "mean_legal_non_gold_mass": mean(r.mean_legal_non_gold_mass for r in group),
                "mean_illegal_mass": mean(r.mean_illegal_mass for r in group),
                "top_legal_mass": mean(r.top_legal_mass for r in group),
            }
        )
    return rows


def write_outputs(results: Sequence[RunResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_dicts = [asdict(result) for result in results]
    (output_dir / "probe_results.json").write_text(
        json.dumps(result_dicts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "probe_runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(result_dicts[0].keys()))
        writer.writeheader()
        writer.writerows(result_dicts)
    summary = summarize_by_dataset_lambda(results)
    (output_dir / "probe_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "probe_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)


def write_conflict_demo(output_dir: Path) -> None:
    """Write a fixed-potential demo where hard constraints hide posterior conflict."""

    label_names = ("O", "B-X", "I-X")
    model = TinyLinearChainCRF(vocab_size=3, label_names=label_names)
    with torch.no_grad():
        model.start[:] = torch.tensor([3.0, 0.0, -5.0])
        model.transitions[:] = torch.tensor(
            [
                [-1.0, -2.0, 3.0],
                [-2.0, -2.0, 2.0],
                [-2.0, -2.0, 0.0],
            ]
        )
        model.emissions.weight.zero_()
        model.emissions.weight[1] = torch.tensor([2.0, 0.0, -5.0])
        model.emissions.weight[2] = torch.tensor([0.0, 0.0, 2.0])
    word_ids = [1, 2]
    unconstrained, unconstrained_score = model.viterbi(word_ids, constrained=False)
    constrained, constrained_score = model.viterbi(word_ids, constrained=True)
    unconstrained_labels = [label_names[idx] for idx in unconstrained]
    constrained_labels = [label_names[idx] for idx in constrained]
    log_p_event = model.log_event_probability_bio(word_ids)
    payload = {
        "purpose": "fixed-potential smoke for hard-constraint-hidden conflict",
        "word_ids": word_ids,
        "unconstrained_viterbi": unconstrained_labels,
        "unconstrained_is_bio_legal": bio_sequence_allowed(unconstrained_labels),
        "unconstrained_score": unconstrained_score,
        "constrained_viterbi": constrained_labels,
        "constrained_is_bio_legal": bio_sequence_allowed(constrained_labels),
        "constrained_score": constrained_score,
        "p_event": float(torch.exp(log_p_event).detach().cpu().item()),
        "log_p_event": float(log_p_event.detach().cpu().item()),
        "claim_boundary": "diagnostic mechanism only; not a benchmark or usefulness result",
    }
    (output_dir / "conflict_demo.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def read_conll_or_builtin(
    filename: str,
    *,
    fallback_name: str,
    max_sentences: int | None = None,
    max_len: int | None = None,
) -> SequenceDataset:
    path = DATA_DIR / filename
    if path.exists():
        return read_conll(path, max_sentences=max_sentences, max_len=max_len)
    return make_tiny_conll_like_dataset(f"{fallback_name}_builtin")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/results/event_training")
    parser.add_argument("--epochs", type=int, default=15)
    args = parser.parse_args()

    all_results: list[RunResult] = []
    synthetic_train, synthetic_dev = make_synthetic_bio_dataset()
    all_results.extend(
        run_dataset(
            synthetic_train,
            synthetic_dev,
            dataset_name="synthetic_bio",
            lams=(0.0, 0.1, 0.5, 1.0),
            seeds=(0, 1, 2),
            epochs=args.epochs,
        )
    )
    sparse_train, sparse_dev = make_transition_sparse_bio_dataset()
    all_results.extend(
        run_dataset(
            sparse_train,
            sparse_dev,
            dataset_name="synthetic_transition_sparse",
            lams=(0.0, 0.5, 1.0, 2.0),
            seeds=(0, 1, 2),
            epochs=2,
        )
    )
    sample_train = read_conll_or_builtin("sample_english_train.conll", fallback_name="sample_english_train")
    sample_dev = read_conll_or_builtin("sample_english_test.conll", fallback_name="sample_english_test")
    all_results.extend(
        run_dataset(
            sample_train,
            sample_dev,
            dataset_name="sample_english",
            lams=(0.0, 0.1, 0.5),
            seeds=(0, 1, 2),
            epochs=args.epochs,
        )
    )
    conll_train = read_conll_or_builtin(
        "conll2003_train.conll",
        fallback_name="conll2003_train",
        max_sentences=200,
        max_len=30,
    )
    conll_dev = read_conll_or_builtin(
        "conll2003_dev.conll",
        fallback_name="conll2003_dev",
        max_sentences=100,
        max_len=30,
    )
    all_results.extend(
        run_dataset(
            conll_train,
            conll_dev,
            dataset_name="conll2003_tiny",
            lams=(0.0, 0.1, 0.5),
            seeds=(0, 1, 2),
            epochs=args.epochs,
        )
    )
    write_outputs(all_results, Path(args.output_dir))
    write_conflict_demo(Path(args.output_dir))


if __name__ == "__main__":
    main()

