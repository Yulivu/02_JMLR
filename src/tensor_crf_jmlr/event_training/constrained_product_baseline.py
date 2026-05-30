"""Faithful constrained-product decoding baseline.

This module implements B7 as constrained Viterbi decoding over the product of a
first-order CRF state and a DFA monitor. It is intentionally a decoding
baseline, not a WFST replacement system and not an event-mass method.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import torch

from tensor_crf_jmlr.posterior_event_algebra.dfa import DFA

from .bio_event import bio_sequence_allowed, extract_strict_bio_spans
from .data_utils import build_label_vocab, build_vocab, encode_dataset, normalize_bio_dataset, take_dataset
from .wnut17_bio_probe import DEFAULT_DATA_DIR, VARIANTS, build_feature_vocab, encode_feature_dataset, load_split, train_model


DEAD = "__DEAD__"
OUT = "__OUT__"


@dataclass
class B7Run:
    block: str
    variant: str
    source_model: str
    seed: int
    train_sentences: int
    unlabeled_sentences: int
    dev_sentences: int
    max_len: int
    epochs: int
    lr: float
    label_count: int
    vocab_size: int
    decoded_legal_rate: float
    token_accuracy: float
    entity_f1: float
    mean_constrained_score: float
    uses_event_training: bool
    uses_event_mass_for_decoding: bool
    notes: str


@dataclass
class B7Case:
    case_id: str
    variant: str
    seed: int
    tokens: str
    gold: str
    prediction: str
    legal: bool
    token_accuracy: float


def make_bio_dfa(label_names: Sequence[str]) -> DFA:
    """Build a complete DFA for strict BIO legality over integer label ids."""

    entity_types = sorted({label[2:] for label in label_names if label.startswith(("B-", "I-"))})
    states = (OUT, *(f"IN:{entity_type}" for entity_type in entity_types), DEAD)
    alphabet = tuple(range(len(label_names)))
    delta: dict[tuple[str, int], str] = {}
    for state in states:
        for label_id, label in enumerate(label_names):
            if state == DEAD:
                next_state = DEAD
            elif label == "O":
                next_state = OUT
            elif label.startswith("B-"):
                next_state = f"IN:{label[2:]}"
            elif label.startswith("I-"):
                wanted = f"IN:{label[2:]}"
                next_state = wanted if state == wanted else DEAD
            else:
                next_state = DEAD
            delta[(state, label_id)] = next_state
    dfa = DFA(
        name="strict-bio",
        states=states,
        alphabet=alphabet,
        start=OUT,
        accepting=frozenset(state for state in states if state != DEAD),
        delta=delta,
    )
    dfa.validate_complete()
    return dfa


def constrained_product_viterbi(
    emissions: torch.Tensor,
    start_scores: torch.Tensor,
    transitions: torch.Tensor,
    dfa: DFA,
) -> tuple[list[int], float]:
    """Decode the best sequence accepted by ``dfa`` under first-order CRF scores."""

    if emissions.ndim != 2:
        raise ValueError("emissions must have shape [T, num_labels]")
    length, num_labels = emissions.shape
    if length == 0:
        return [], 0.0
    if start_scores.numel() != num_labels or transitions.shape != (num_labels, num_labels):
        raise ValueError("CRF score tensors are dimensionally inconsistent")

    device = emissions.device
    dfa_states = tuple(dfa.states)
    state_index = {state: idx for idx, state in enumerate(dfa_states)}
    neg_inf = torch.tensor(-1.0e30, dtype=emissions.dtype, device=device)
    scores = torch.full((num_labels, len(dfa_states)), neg_inf, dtype=emissions.dtype, device=device)
    backpointers: list[dict[tuple[int, int], tuple[int, int]]] = []

    for label in range(num_labels):
        q_next = dfa.step(dfa.start, label)
        q_idx = state_index[q_next]
        scores[label, q_idx] = start_scores[label] + emissions[0, label]

    for pos in range(1, length):
        next_scores = torch.full_like(scores, neg_inf)
        step_back: dict[tuple[int, int], tuple[int, int]] = {}
        for prev_label in range(num_labels):
            for q_idx, q in enumerate(dfa_states):
                prev_score = scores[prev_label, q_idx]
                if float(prev_score.detach().cpu().item()) <= -1.0e29:
                    continue
                for label in range(num_labels):
                    q_next = dfa.step(q, label)
                    next_q_idx = state_index[q_next]
                    candidate = prev_score + transitions[prev_label, label] + emissions[pos, label]
                    if candidate > next_scores[label, next_q_idx]:
                        next_scores[label, next_q_idx] = candidate
                        step_back[(label, next_q_idx)] = (prev_label, q_idx)
        scores = next_scores
        backpointers.append(step_back)

    best_label = -1
    best_q_idx = -1
    best_score = neg_inf
    accepting_indices = {state_index[state] for state in dfa.accepting}
    for label in range(num_labels):
        for q_idx in accepting_indices:
            if scores[label, q_idx] > best_score:
                best_score = scores[label, q_idx]
                best_label = label
                best_q_idx = q_idx
    if best_label < 0:
        raise RuntimeError(f"DFA {dfa.name!r} accepts no sequence at this length")

    path = [best_label]
    key = (best_label, best_q_idx)
    for step_back in reversed(backpointers):
        key = step_back[key]
        path.append(key[0])
    path.reverse()
    return path, float(best_score.detach().cpu().item())


def _emissions(model: torch.nn.Module, word_ids: Sequence[int] | Sequence[Sequence[int]]) -> torch.Tensor:
    return model.emission_scores(word_ids)  # type: ignore[attr-defined]


def constrained_product_viterbi_model(
    model: torch.nn.Module,
    word_ids: Sequence[int] | Sequence[Sequence[int]],
    dfa: DFA,
) -> tuple[list[int], float]:
    return constrained_product_viterbi(
        _emissions(model, word_ids),
        model.start,  # type: ignore[attr-defined]
        model.transitions,  # type: ignore[attr-defined]
        dfa,
    )


def token_accuracy(pred: Sequence[int], gold: Sequence[int]) -> float:
    return sum(int(a == b) for a, b in zip(pred, gold)) / max(1, len(gold))


def entity_counts(pred_labels: Sequence[str], gold_labels: Sequence[str]) -> tuple[int, int, int]:
    pred_spans = extract_strict_bio_spans(pred_labels)
    gold_spans = extract_strict_bio_spans(gold_labels)
    return len(pred_spans & gold_spans), len(pred_spans), len(gold_spans)


def f1_from_counts(true_positive: int, predicted: int, gold: int) -> float:
    if true_positive == 0 or predicted == 0 or gold == 0:
        return 0.0
    precision = true_positive / predicted
    recall = true_positive / gold
    return 2.0 * precision * recall / (precision + recall)


def decode(label_names: Sequence[str], label_ids: Sequence[int]) -> list[str]:
    return [label_names[idx] for idx in label_ids]


def evaluate_b7(
    model: torch.nn.Module,
    dev: list[tuple[list[int] | list[list[int]], list[int]]],
    *,
    label_names: Sequence[str],
    seed: int,
    train_sentences: int,
    unlabeled_sentences: int,
    max_len: int,
    epochs: int,
    lr: float,
    vocab_size: int,
    source_model: str,
    uses_event_training: bool,
    token_lookup: dict[int, str],
) -> tuple[B7Run, list[B7Case]]:
    dfa = make_bio_dfa(label_names)
    legal = 0
    token_scores: list[float] = []
    constrained_scores: list[float] = []
    tp = pred_total = gold_total = 0
    cases: list[B7Case] = []
    for idx, (word_ids, gold) in enumerate(dev):
        with torch.no_grad():
            pred, score = constrained_product_viterbi_model(model, word_ids, dfa)
        pred_labels = decode(label_names, pred)
        gold_labels = decode(label_names, gold)
        is_legal = bio_sequence_allowed(pred_labels)
        legal += int(is_legal)
        score_value = token_accuracy(pred, gold)
        token_scores.append(score_value)
        constrained_scores.append(score)
        row_tp, row_pred, row_gold = entity_counts(pred_labels, gold_labels)
        tp += row_tp
        pred_total += row_pred
        gold_total += row_gold
        if len(cases) < 20:
            cases.append(
                B7Case(
                    case_id=f"b7_dev_{seed}_{idx:04d}",
                    variant="B7_constrained_product_decode",
                    seed=seed,
                    tokens=token_lookup.get(idx, "<FEATURES>"),
                    gold=" ".join(gold_labels),
                    prediction=" ".join(pred_labels),
                    legal=is_legal,
                    token_accuracy=score_value,
                )
            )
    run = B7Run(
        block="b7_constrained_product_decode",
        variant="B7_constrained_product_decode",
        source_model=source_model,
        seed=seed,
        train_sentences=train_sentences,
        unlabeled_sentences=unlabeled_sentences,
        dev_sentences=len(dev),
        max_len=max_len,
        epochs=epochs,
        lr=lr,
        label_count=len(label_names),
        vocab_size=vocab_size,
        decoded_legal_rate=legal / max(1, len(dev)),
        token_accuracy=sum(token_scores) / max(1, len(token_scores)),
        entity_f1=f1_from_counts(tp, pred_total, gold_total),
        mean_constrained_score=sum(constrained_scores) / max(1, len(constrained_scores)),
        uses_event_training=uses_event_training,
        uses_event_mass_for_decoding=False,
        notes=(
            "faithful constrained-product Viterbi over CRF x strict-BIO DFA; "
            "decoding baseline only, not a WFST replacement or superiority claim"
        ),
    )
    return run, cases


def write_outputs(output_dir: Path, runs: list[B7Run], cases: list[B7Case]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_rows = [asdict(row) for row in runs]
    case_rows = [asdict(row) for row in cases]
    (output_dir / "b7_runs.json").write_text(json.dumps(run_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "b7_cases.json").write_text(json.dumps(case_rows, indent=2, ensure_ascii=False), encoding="utf-8")
    if run_rows:
        with (output_dir / "b7_runs.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(run_rows[0]))
            writer.writeheader()
            writer.writerows(run_rows)
        with (output_dir / "b7_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(run_rows[0]))
            writer.writeheader()
            writer.writerows(run_rows)
    if case_rows:
        with (output_dir / "b7_cases.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(case_rows[0]))
            writer.writeheader()
            writer.writerows(case_rows)
    write_audit_template(output_dir, runs)


def write_audit_template(output_dir: Path, runs: Sequence[B7Run]) -> None:
    lines = [
        "# B7 Constrained-Product Decoding Baseline Audit",
        "",
        "This is a constrained decoding baseline over CRF state x DFA state. It uses the same strict BIO language as the posterior event mass computation, but it does not use original posterior event mass for decoding.",
        "",
        "## Paper Table Row Schema",
        "",
        "| block | variant | source model | legal rate | token accuracy | entity F1 | uses event training | uses event mass for decoding | notes |",
        "|---|---|---|---:|---:|---:|---|---|---|",
    ]
    for run in runs:
        lines.append(
            "| {block} | {variant} | {source} | {legal:.4f} | {tok:.4f} | {f1:.4f} | {train} | {mass} | {notes} |".format(
                block=run.block,
                variant=run.variant,
                source=run.source_model,
                legal=run.decoded_legal_rate,
                tok=run.token_accuracy,
                f1=run.entity_f1,
                train=run.uses_event_training,
                mass=run.uses_event_mass_for_decoding,
                notes=run.notes,
            )
        )
    lines.extend(
        [
            "",
            "## What This Answers",
            "",
            "- Whether a faithful constrained-product decoder can produce legal outputs and what task metrics it gets.",
            "- Whether decoded legality should be separated from original posterior event consistency in tables.",
            "",
            "## What This Does Not Answer",
            "",
            "- It is not a full WFST toolkit or constrained-CRF training system.",
            "- It does not show that posterior event training beats constrained structured methods.",
            "- It does not use `P_theta(L|x)` as a B7 advantage.",
            "",
            "## Status",
            "",
            "Smoke rows are local validation only. Full B7 rows remain pending until the suite command is run and audited.",
            "",
        ]
    )
    (output_dir / "B7_RESULT_AUDIT_TEMPLATE.md").write_text("\n".join(lines), encoding="utf-8")


def run_wnut17_smoke(
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
    use_features: bool,
    include_b4: bool,
) -> None:
    train_full = load_split(data_dir, "train", max_len=max_len)
    dev_full = load_split(data_dir, "dev", max_len=max_len)
    labeled_ds = take_dataset(train_full, start=0, count=train_size, name="wnut17_train_labeled")
    unlabeled_ds = take_dataset(train_full, start=train_size, count=unlabeled_size, name="wnut17_train_unlabeled")
    dev_ds = take_dataset(dev_full, start=0, count=dev_size, name="wnut17_dev_b7")

    label_to_idx = build_label_vocab(normalize_bio_dataset(train_full).labels)
    label_names = [label for label, _idx in sorted(label_to_idx.items(), key=lambda item: item[1])]
    if use_features:
        feature_vocab = build_feature_vocab([labeled_ds, unlabeled_ds])
        labeled = encode_feature_dataset(normalize_bio_dataset(labeled_ds), feature_vocab, label_to_idx)
        unlabeled = [
            word_ids
            for word_ids, _labels in encode_feature_dataset(normalize_bio_dataset(unlabeled_ds), feature_vocab, label_to_idx)
        ]
        dev = encode_feature_dataset(normalize_bio_dataset(dev_ds), feature_vocab, label_to_idx)
        vocab_size = len(feature_vocab)
    else:
        vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens)
        labeled = encode_dataset(normalize_bio_dataset(labeled_ds), vocab, label_to_idx)
        unlabeled = [word_ids for word_ids, _labels in encode_dataset(normalize_bio_dataset(unlabeled_ds), vocab, label_to_idx)]
        dev = encode_dataset(normalize_bio_dataset(dev_ds), vocab, label_to_idx)
        vocab_size = len(vocab)
    token_lookup = {idx: " ".join(tokens) for idx, tokens in enumerate(dev_ds.tokens)}

    runs: list[B7Run] = []
    cases: list[B7Case] = []
    source_specs = [("B0_unconstrained", VARIANTS["B0_unconstrained"], False)]
    if include_b4:
        source_specs.append(("B4_semi_event_0.1", VARIANTS["B4_semi_event_0.1"], True))
    for source_model, variant, uses_event_training in source_specs:
        model = train_model(
            labeled,
            unlabeled,
            vocab_size=vocab_size,
            label_names=label_names,
            variant=variant,
            seed=seed,
            epochs=epochs,
            lr=lr,
            use_features=use_features,
        )
        run, run_cases = evaluate_b7(
            model,
            dev,
            label_names=label_names,
            seed=seed,
            train_sentences=len(labeled),
            unlabeled_sentences=len(unlabeled),
            max_len=max_len,
            epochs=epochs,
            lr=lr,
            vocab_size=vocab_size,
            source_model=source_model,
            uses_event_training=uses_event_training,
            token_lookup=token_lookup,
        )
        runs.append(run)
        cases.extend(run_cases)
    write_outputs(output_dir, runs, cases)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-kind", default="wnut17_bio")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output-dir", default="experiments/runs/local_checks/b7_constrained_product_smoke")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-size", type=int, default=40)
    parser.add_argument("--unlabeled-size", type=int, default=40)
    parser.add_argument("--dev-size", type=int, default=40)
    parser.add_argument("--max-len", type=int, default=30)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--use-features", action="store_true")
    parser.add_argument("--include-b4", action="store_true")
    args = parser.parse_args()
    if args.task_kind != "wnut17_bio":
        raise SystemExit(f"unsupported B7 task kind: {args.task_kind}")
    run_wnut17_smoke(
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
        seed=args.seed,
        train_size=args.train_size,
        unlabeled_size=args.unlabeled_size,
        dev_size=args.dev_size,
        max_len=args.max_len,
        epochs=args.epochs,
        lr=args.lr,
        use_features=args.use_features,
        include_b4=args.include_b4,
    )


if __name__ == "__main__":
    main()
