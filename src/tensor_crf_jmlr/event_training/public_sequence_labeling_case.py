"""Optional public BIO/sequence-labeling case-study runner.

The default target is CoNLL-2000 chunking if local files are present under
``data/raw/conll2000_chunking``. Missing data produces an explicit pending plan
instead of fabricated results.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import torch

from .bio_event import bio_sequence_allowed, extract_strict_bio_spans
from .constrained_product_baseline import constrained_product_viterbi_model, make_bio_dfa
from .data_utils import SequenceDataset, build_label_vocab, build_vocab, encode_dataset, normalize_bio_dataset, take_dataset
from .event_crf import TinyLinearChainCRF
from .run_probe import set_seed
from .wnut17_bio_probe import (
    VARIANTS,
    build_feature_vocab,
    encode_feature_dataset,
    log_event_probability_bio,
    train_model,
    viterbi,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_DIR = REPO_ROOT / "data" / "raw" / "conll2000_chunking"


@dataclass
class PublicCaseRun:
    dataset: str
    variant: str
    seed: int
    train_sentences: int
    unlabeled_sentences: int
    dev_sentences: int
    max_len: int
    epochs: int
    use_features: bool
    mean_p_event: float
    hidden_conflict_rate: float
    unconstrained_legal_rate: float
    constrained_decoded_legal_rate: float
    b7_legal_rate: float
    token_accuracy: float
    constrained_token_accuracy: float
    b7_token_accuracy: float
    span_f1: float
    constrained_span_f1: float
    b7_span_f1: float
    notes: str


@dataclass
class PublicCaseDetail:
    dataset: str
    variant: str
    seed: int
    case_id: str
    baseline_p_event: float
    event_risk_1_minus_p: float
    exact_error: int
    token_error: float
    span_error: int
    hidden_conflict: bool
    viterbi_log_prob: float
    neg_log_viterbi_probability: float
    max_sequence_probability: float
    viterbi_margin: float
    token_marginal_entropy: float
    sequence_entropy: float


def read_conll2000(path: Path, *, max_sentences: int | None = None, max_len: int | None = None) -> SequenceDataset:
    tokens: list[list[str]] = []
    labels: list[list[str]] = []
    current_tokens: list[str] = []
    current_labels: list[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            if current_tokens:
                if max_len is None or len(current_tokens) <= max_len:
                    tokens.append(current_tokens)
                    labels.append(current_labels)
                current_tokens = []
                current_labels = []
                if max_sentences is not None and len(tokens) >= max_sentences:
                    break
            continue
        parts = line.split()
        if len(parts) >= 3:
            current_tokens.append(parts[0])
            current_labels.append(parts[-1])
    if current_tokens and (max_sentences is None or len(tokens) < max_sentences):
        if max_len is None or len(current_tokens) <= max_len:
            tokens.append(current_tokens)
            labels.append(current_labels)
    return SequenceDataset(path.stem, tokens, labels)


def _token_accuracy(pred: Sequence[int], gold: Sequence[int]) -> float:
    return sum(int(a == b) for a, b in zip(pred, gold)) / max(1, len(gold))


def _span_counts(pred_labels: Sequence[str], gold_labels: Sequence[str]) -> tuple[int, int, int]:
    pred_spans = extract_strict_bio_spans(pred_labels)
    gold_spans = extract_strict_bio_spans(gold_labels)
    return len(pred_spans & gold_spans), len(pred_spans), len(gold_spans)


def _f1(tp: int, pred: int, gold: int) -> float:
    if tp == 0 or pred == 0 or gold == 0:
        return 0.0
    precision = tp / pred
    recall = tp / gold
    return 2.0 * precision * recall / (precision + recall)


def _decode(label_names: Sequence[str], ids: Sequence[int]) -> list[str]:
    return [label_names[idx] for idx in ids]


def _top2_viterbi_scores(model: TinyLinearChainCRF, emissions: torch.Tensor) -> tuple[float, float]:
    neg_inf = -1.0e30
    top2 = torch.stack([model.start + emissions[0], torch.full_like(model.start, neg_inf)], dim=1)
    for pos in range(1, emissions.shape[0]):
        candidates: list[list[float]] = [[] for _ in range(emissions.shape[1])]
        for prev in range(emissions.shape[1]):
            for rank in range(2):
                prev_score = float(top2[prev, rank].detach().cpu().item())
                if prev_score <= neg_inf / 2:
                    continue
                for curr in range(emissions.shape[1]):
                    score = (
                        prev_score
                        + float(model.transitions[prev, curr].detach().cpu().item())
                        + float(emissions[pos, curr].detach().cpu().item())
                    )
                    candidates[curr].append(score)
        next_top2 = torch.full_like(top2, neg_inf)
        for curr, scores in enumerate(candidates):
            best = sorted(scores, reverse=True)[:2]
            for rank, score in enumerate(best):
                next_top2[curr, rank] = score
        top2 = next_top2
    best_scores = sorted((float(value) for value in top2.flatten().detach().cpu().tolist()), reverse=True)
    best = best_scores[0]
    second = best_scores[1] if len(best_scores) > 1 else neg_inf
    return best, second


def log_partition_from_emissions(model: TinyLinearChainCRF, emissions: torch.Tensor) -> torch.Tensor:
    alpha = model.start + emissions[0]
    for pos in range(1, emissions.shape[0]):
        scores = alpha[:, None] + model.transitions + emissions[pos][None, :]
        alpha = torch.logsumexp(scores, dim=0)
    return torch.logsumexp(alpha, dim=0)


def uncertainty_summary(model: TinyLinearChainCRF, word_ids: Sequence[int] | Sequence[Sequence[int]]) -> dict[str, float]:
    emissions = model.emission_scores(word_ids)
    log_z = log_partition_from_emissions(model, emissions)
    best_score, second_score = _top2_viterbi_scores(model, emissions)
    log_z_value = float(log_z.detach().cpu().item())
    viterbi_log_prob = best_score - log_z_value
    max_sequence_prob = math.exp(min(0.0, viterbi_log_prob))
    margin = best_score - second_score if second_score > -1.0e29 else float("inf")

    alpha: list[torch.Tensor] = [model.start + emissions[0]]
    for pos in range(1, emissions.shape[0]):
        scores = alpha[-1][:, None] + model.transitions + emissions[pos][None, :]
        alpha.append(torch.logsumexp(scores, dim=0))

    beta: list[torch.Tensor] = [torch.zeros_like(model.start) for _ in range(emissions.shape[0])]
    for pos in range(emissions.shape[0] - 2, -1, -1):
        scores = model.transitions + emissions[pos + 1][None, :] + beta[pos + 1][None, :]
        beta[pos] = torch.logsumexp(scores, dim=1)

    token_entropy = 0.0
    expected_score = 0.0
    for pos in range(emissions.shape[0]):
        marg = torch.exp(alpha[pos] + beta[pos] - log_z)
        token_entropy += float((-(marg * torch.log(torch.clamp(marg, min=1.0e-12))).sum()).detach().cpu().item())
        expected_score += float((marg * emissions[pos]).sum().detach().cpu().item())
        if pos == 0:
            expected_score += float((marg * model.start).sum().detach().cpu().item())
    for pos in range(1, emissions.shape[0]):
        pair_log = alpha[pos - 1][:, None] + model.transitions + emissions[pos][None, :] + beta[pos][None, :] - log_z
        pair_marg = torch.exp(pair_log)
        expected_score += float((pair_marg * model.transitions).sum().detach().cpu().item())

    sequence_entropy = max(0.0, log_z_value - expected_score)
    return {
        "viterbi_log_prob": viterbi_log_prob,
        "neg_log_viterbi_probability": -viterbi_log_prob,
        "max_sequence_probability": max_sequence_prob,
        "viterbi_margin": margin,
        "token_marginal_entropy": token_entropy,
        "sequence_entropy": sequence_entropy,
    }


def evaluate(
    model: TinyLinearChainCRF,
    dev: list[tuple[list[int] | list[list[int]], list[int]]],
    *,
    label_names: Sequence[str],
    variant,
    seed: int,
    train_sentences: int,
    unlabeled_sentences: int,
    max_len: int,
    epochs: int,
    use_features: bool,
    hidden_conflict_threshold: float,
) -> tuple[PublicCaseRun, list[PublicCaseDetail]]:
    p_events: list[float] = []
    hidden = 0
    unconstrained_legal = 0
    constrained_legal = 0
    b7_legal = 0
    token_scores: list[float] = []
    constrained_token_scores: list[float] = []
    b7_token_scores: list[float] = []
    tp = pred_total = gold_total = 0
    c_tp = c_pred_total = c_gold_total = 0
    b7_tp = b7_pred_total = b7_gold_total = 0
    dfa = make_bio_dfa(label_names)
    details: list[PublicCaseDetail] = []
    for case_idx, (word_ids, gold) in enumerate(dev):
        with torch.no_grad():
            p_event = float(torch.exp(log_event_probability_bio(model, word_ids, rule_bias=variant.rule_bias)).cpu().item())
            pred, _ = viterbi(model, word_ids, constrained=False, rule_bias=variant.rule_bias)
            constrained_pred, _ = viterbi(model, word_ids, constrained=True, rule_bias=variant.rule_bias)
            b7_pred, _ = constrained_product_viterbi_model(model, word_ids, dfa)
            uncertainty = uncertainty_summary(model, word_ids)
        pred_labels = _decode(label_names, pred)
        constrained_labels = _decode(label_names, constrained_pred)
        b7_labels = _decode(label_names, b7_pred)
        gold_labels = _decode(label_names, gold)
        p_events.append(p_event)
        unconstrained_legal += int(bio_sequence_allowed(pred_labels))
        constrained_legal += int(bio_sequence_allowed(constrained_labels))
        b7_legal += int(bio_sequence_allowed(b7_labels))
        hidden += int(bio_sequence_allowed(constrained_labels) and p_event < hidden_conflict_threshold)
        token_scores.append(_token_accuracy(pred, gold))
        constrained_token_scores.append(_token_accuracy(constrained_pred, gold))
        b7_token_scores.append(_token_accuracy(b7_pred, gold))
        row_tp, row_pred, row_gold = _span_counts(pred_labels, gold_labels)
        row_c_tp, row_c_pred, row_c_gold = _span_counts(constrained_labels, gold_labels)
        row_b7_tp, row_b7_pred, row_b7_gold = _span_counts(b7_labels, gold_labels)
        tp += row_tp
        pred_total += row_pred
        gold_total += row_gold
        c_tp += row_c_tp
        c_pred_total += row_c_pred
        c_gold_total += row_c_gold
        b7_tp += row_b7_tp
        b7_pred_total += row_b7_pred
        b7_gold_total += row_b7_gold
        exact_error = int(tuple(pred) != tuple(gold))
        details.append(
            PublicCaseDetail(
                dataset="conll2000_chunking",
                variant=variant.name,
                seed=seed,
                case_id=f"conll2000_{seed}_{case_idx:04d}",
                baseline_p_event=p_event,
                event_risk_1_minus_p=1.0 - p_event,
                exact_error=exact_error,
                token_error=1.0 - _token_accuracy(pred, gold),
                span_error=int(extract_strict_bio_spans(pred_labels) != extract_strict_bio_spans(gold_labels)),
                hidden_conflict=bio_sequence_allowed(constrained_labels) and p_event < hidden_conflict_threshold,
                **uncertainty,
            )
        )
    return PublicCaseRun(
        dataset="conll2000_chunking",
        variant=variant.name,
        seed=seed,
        train_sentences=train_sentences,
        unlabeled_sentences=unlabeled_sentences,
        dev_sentences=len(dev),
        max_len=max_len,
        epochs=epochs,
        use_features=use_features,
        mean_p_event=sum(p_events) / max(1, len(p_events)),
        hidden_conflict_rate=hidden / max(1, len(dev)),
        unconstrained_legal_rate=unconstrained_legal / max(1, len(dev)),
        constrained_decoded_legal_rate=constrained_legal / max(1, len(dev)),
        b7_legal_rate=b7_legal / max(1, len(dev)),
        token_accuracy=sum(token_scores) / max(1, len(token_scores)),
        constrained_token_accuracy=sum(constrained_token_scores) / max(1, len(constrained_token_scores)),
        b7_token_accuracy=sum(b7_token_scores) / max(1, len(b7_token_scores)),
        span_f1=_f1(tp, pred_total, gold_total),
        constrained_span_f1=_f1(c_tp, c_pred_total, c_gold_total),
        b7_span_f1=_f1(b7_tp, b7_pred_total, b7_gold_total),
        notes="public BIO/chunking case study; not SOTA or benchmark-superiority evidence",
    ), details


def write_pending(output_dir: Path, data_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Public Sequence Labeling Case Pending",
        "",
        "No result was generated because required local data files are missing.",
        "",
        "Expected files:",
        "",
        f"- `{data_dir / 'train.txt'}`",
        f"- `{data_dir / 'test.txt'}`",
        "",
        "Prepare command:",
        "",
        "```powershell",
        "python scripts/data/fetch_conll2000_chunking.py",
        "```",
        "",
        "Smoke command:",
        "",
        "```powershell",
        "python -m tensor_crf_jmlr.event_training.public_sequence_labeling_case --output-dir experiments/runs/local_checks/public_conll2000_chunking_smoke --train-size 80 --unlabeled-size 80 --dev-size 80 --epochs 1 --use-features",
        "```",
        "",
        "Required reported metrics after data is available: unconstrained posterior event mass, constrained decoded legality, task metric, hidden posterior conflict, B4 event-mass movement, B7 constrained baseline behavior, and uncertainty baselines if available.",
        "",
    ]
    (output_dir / "PUBLIC_CASE_PENDING.md").write_text("\n".join(lines), encoding="utf-8")


def write_outputs(output_dir: Path, rows: list[PublicCaseRun], details: list[PublicCaseDetail]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    pending_path = output_dir / "PUBLIC_CASE_PENDING.md"
    if pending_path.exists():
        pending_path.unlink()
    row_dicts = [asdict(row) for row in rows]
    detail_dicts = [asdict(row) for row in details]
    (output_dir / "public_case_runs.json").write_text(json.dumps(row_dicts, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "public_case_details.json").write_text(
        json.dumps(detail_dicts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "public_case_runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row_dicts[0]))
        writer.writeheader()
        writer.writerows(row_dicts)
    with (output_dir / "public_case_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row_dicts[0]))
        writer.writeheader()
        writer.writerows(row_dicts)
    if detail_dicts:
        with (output_dir / "public_case_details.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(detail_dicts[0]))
            writer.writeheader()
            writer.writerows(detail_dicts)
    lines = [
        "# Public Sequence Labeling Case Audit",
        "",
        "This is a public BIO/chunking case study. It is not a SOTA or benchmark-superiority experiment.",
        "",
        "| variant | P(BIO|x) | hidden conflict | unconstrained legal | constrained legal | B7 legal | token acc | constrained token acc | B7 token acc | span F1 | B7 span F1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {variant} | {p:.4f} | {hidden:.4f} | {ul:.4f} | {cl:.4f} | {b7l:.4f} | {ta:.4f} | {cta:.4f} | {b7ta:.4f} | {f1:.4f} | {b7f1:.4f} |".format(
                variant=row.variant,
                p=row.mean_p_event,
                hidden=row.hidden_conflict_rate,
                ul=row.unconstrained_legal_rate,
                cl=row.constrained_decoded_legal_rate,
                b7l=row.b7_legal_rate,
                ta=row.token_accuracy,
                cta=row.constrained_token_accuracy,
                b7ta=row.b7_token_accuracy,
                f1=row.span_f1,
                b7f1=row.b7_span_f1,
            )
        )
    lines.extend(
        [
            "",
            "Claim boundary: use this only to strengthen the public structured-prediction case if the run is audited. Do not claim superiority without a frozen full protocol and stronger baselines.",
            "",
        ]
    )
    (output_dir / "PUBLIC_SEQUENCE_LABELING_CASE_AUDIT.md").write_text("\n".join(lines), encoding="utf-8")


def run_case(
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
) -> None:
    if not (data_dir / "train.txt").is_file() or not (data_dir / "test.txt").is_file():
        write_pending(output_dir, data_dir)
        return
    train_full = normalize_bio_dataset(read_conll2000(data_dir / "train.txt", max_len=max_len))
    test_full = normalize_bio_dataset(read_conll2000(data_dir / "test.txt", max_len=max_len))
    labeled_ds = take_dataset(train_full, start=0, count=train_size, name="conll2000_train_labeled")
    unlabeled_ds = take_dataset(train_full, start=train_size, count=unlabeled_size, name="conll2000_train_unlabeled")
    dev_ds = take_dataset(test_full, start=0, count=dev_size, name="conll2000_test_smoke")
    label_to_idx = build_label_vocab(train_full.labels)
    label_names = [label for label, _idx in sorted(label_to_idx.items(), key=lambda item: item[1])]
    if use_features:
        feature_vocab = build_feature_vocab([labeled_ds, unlabeled_ds])
        labeled = encode_feature_dataset(labeled_ds, feature_vocab, label_to_idx)
        unlabeled = [word_ids for word_ids, _labels in encode_feature_dataset(unlabeled_ds, feature_vocab, label_to_idx)]
        dev = encode_feature_dataset(dev_ds, feature_vocab, label_to_idx)
        vocab_size = len(feature_vocab)
    else:
        vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens)
        labeled = encode_dataset(labeled_ds, vocab, label_to_idx)
        unlabeled = [word_ids for word_ids, _labels in encode_dataset(unlabeled_ds, vocab, label_to_idx)]
        dev = encode_dataset(dev_ds, vocab, label_to_idx)
        vocab_size = len(vocab)
    rows: list[PublicCaseRun] = []
    details: list[PublicCaseDetail] = []
    for variant_name in ("B0_unconstrained", "B4_semi_event_0.1"):
        variant = VARIANTS[variant_name]
        set_seed(seed)
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
        run, run_details = evaluate(
            model,
            dev,
            label_names=label_names,
            variant=variant,
            seed=seed,
            train_sentences=len(labeled),
            unlabeled_sentences=len(unlabeled),
            max_len=max_len,
            epochs=epochs,
            use_features=use_features,
            hidden_conflict_threshold=0.7,
        )
        rows.append(run)
        details.extend(run_details)
    write_outputs(output_dir, rows, details)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--output-dir", default="experiments/runs/local_checks/public_conll2000_chunking_smoke")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-size", type=int, default=80)
    parser.add_argument("--unlabeled-size", type=int, default=80)
    parser.add_argument("--dev-size", type=int, default=80)
    parser.add_argument("--max-len", type=int, default=40)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--lr", type=float, default=0.05)
    parser.add_argument("--use-features", action="store_true")
    args = parser.parse_args()
    run_case(
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
    )


if __name__ == "__main__":
    main()
