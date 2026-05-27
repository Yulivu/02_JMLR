"""Data and synthetic-case helpers for event-training local probes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


PAD = "<PAD>"
UNK = "<UNK>"


@dataclass(frozen=True)
class SequenceDataset:
    name: str
    tokens: list[list[str]]
    labels: list[list[str]]


def read_conll(
    path: str | Path,
    *,
    max_sentences: int | None = None,
    max_len: int | None = None,
) -> SequenceDataset:
    path = Path(path)
    sentences: list[list[str]] = []
    labels: list[list[str]] = []
    current_tokens: list[str] = []
    current_labels: list[str] = []
    for raw_line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            if current_tokens:
                if max_len is None or len(current_tokens) <= max_len:
                    sentences.append(current_tokens)
                    labels.append(current_labels)
                current_tokens = []
                current_labels = []
                if max_sentences is not None and len(sentences) >= max_sentences:
                    break
            continue
        parts = line.split()
        if len(parts) >= 2:
            current_tokens.append(parts[0])
            current_labels.append(parts[-1])
    if current_tokens and (max_sentences is None or len(sentences) < max_sentences):
        if max_len is None or len(current_tokens) <= max_len:
            sentences.append(current_tokens)
            labels.append(current_labels)
    return SequenceDataset(path.stem, sentences, labels)


def normalize_bio_label(label: str) -> str:
    if label == "O":
        return label
    prefix, sep, label_type = label.partition("-")
    if sep != "-" or prefix not in {"B", "I"}:
        raise ValueError(f"unexpected BIO label: {label!r}")
    return f"{prefix}-{label_type.upper()}"


def normalize_bio_dataset(dataset: SequenceDataset) -> SequenceDataset:
    return SequenceDataset(
        name=dataset.name,
        tokens=dataset.tokens,
        labels=[[normalize_bio_label(label) for label in labels] for labels in dataset.labels],
    )


def filter_dataset_by_length(dataset: SequenceDataset, *, max_len: int) -> SequenceDataset:
    tokens: list[list[str]] = []
    labels: list[list[str]] = []
    for token_seq, label_seq in zip(dataset.tokens, dataset.labels):
        if len(token_seq) <= max_len:
            tokens.append(token_seq)
            labels.append(label_seq)
    return SequenceDataset(name=f"{dataset.name}_maxlen{max_len}", tokens=tokens, labels=labels)


def take_dataset(dataset: SequenceDataset, *, start: int = 0, count: int | None = None, name: str | None = None) -> SequenceDataset:
    end = None if count is None else start + count
    return SequenceDataset(
        name=name or dataset.name,
        tokens=dataset.tokens[start:end],
        labels=dataset.labels[start:end],
    )


def make_synthetic_bio_dataset(
    *,
    repeats: int = 8,
    dev_repeats: int = 3,
) -> tuple[SequenceDataset, SequenceDataset]:
    patterns = [
        (["sx", "ix", "out", "out"], ["B-X", "I-X", "O", "O"]),
        (["out", "sx", "ix", "out"], ["O", "B-X", "I-X", "O"]),
        (["out", "out", "sx", "ix"], ["O", "O", "B-X", "I-X"]),
        (["sx", "out", "sx", "ix"], ["B-X", "O", "B-X", "I-X"]),
        (["amb", "ix", "out", "sx"], ["B-X", "I-X", "O", "B-X"]),
        (["out", "amb", "ix", "out"], ["O", "B-X", "I-X", "O"]),
    ]
    train_tokens: list[list[str]] = []
    train_labels: list[list[str]] = []
    dev_tokens: list[list[str]] = []
    dev_labels: list[list[str]] = []
    for _ in range(repeats):
        for tokens, labels in patterns:
            train_tokens.append(tokens)
            train_labels.append(labels)
    for _ in range(dev_repeats):
        for tokens, labels in patterns:
            dev_tokens.append(tokens)
            dev_labels.append(labels)
    return (
        SequenceDataset("synthetic_bio_train", train_tokens, train_labels),
        SequenceDataset("synthetic_bio_dev", dev_tokens, dev_labels),
    )


def make_transition_sparse_bio_dataset(
    *,
    repeats: int = 1,
    dev_repeats: int = 3,
) -> tuple[SequenceDataset, SequenceDataset]:
    """Make a deliberately under-trained BIO stress case.

    The goal is not realism. The small number of transition examples keeps the
    baseline away from saturation, so event regularization has room to move
    posterior mass toward the BIO-legal set.
    """

    patterns = [
        (["sx", "ix", "out", "out"], ["B-X", "I-X", "O", "O"]),
        (["out", "sx", "ix", "out"], ["O", "B-X", "I-X", "O"]),
        (["amb", "ix", "out", "sx"], ["B-X", "I-X", "O", "B-X"]),
    ]
    train_tokens: list[list[str]] = []
    train_labels: list[list[str]] = []
    dev_tokens: list[list[str]] = []
    dev_labels: list[list[str]] = []
    for _ in range(repeats):
        for tokens, labels in patterns:
            train_tokens.append(tokens)
            train_labels.append(labels)
    for _ in range(dev_repeats):
        for tokens, labels in patterns:
            dev_tokens.append(tokens)
            dev_labels.append(labels)
    return (
        SequenceDataset("synthetic_transition_sparse_train", train_tokens, train_labels),
        SequenceDataset("synthetic_transition_sparse_dev", dev_tokens, dev_labels),
    )


def make_tiny_conll_like_dataset(
    name: str,
    *,
    repeats: int = 6,
) -> SequenceDataset:
    """Small built-in BIO sample used when archived CoNLL files are absent."""

    patterns = [
        (["John", "Smith", "works", "there"], ["B-PER", "I-PER", "O", "O"]),
        (["Alice", "left", "Paris"], ["B-PER", "O", "B-LOC"]),
        (["OpenAI", "is", "hiring"], ["B-ORG", "O", "O"]),
        (["Mary", "visited", "Berlin"], ["B-PER", "O", "B-LOC"]),
        (["IBM", "hired", "Bob"], ["B-ORG", "O", "B-PER"]),
    ]
    tokens: list[list[str]] = []
    labels: list[list[str]] = []
    for _ in range(repeats):
        for token_seq, label_seq in patterns:
            tokens.append(token_seq)
            labels.append(label_seq)
    return SequenceDataset(name, tokens, labels)


def build_vocab(sequences: Sequence[Sequence[str]]) -> dict[str, int]:
    vocab = {PAD: 0, UNK: 1}
    for seq in sequences:
        for token in seq:
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab


def build_label_vocab(label_sequences: Sequence[Sequence[str]]) -> dict[str, int]:
    labels = sorted({label for seq in label_sequences for label in seq})
    if "O" in labels:
        labels.remove("O")
        labels = ["O"] + labels
    return {label: idx for idx, label in enumerate(labels)}


def encode_dataset(
    dataset: SequenceDataset,
    word_to_idx: dict[str, int],
    label_to_idx: dict[str, int],
) -> list[tuple[list[int], list[int]]]:
    encoded = []
    unk = word_to_idx[UNK]
    for tokens, labels in zip(dataset.tokens, dataset.labels):
        word_ids = [word_to_idx.get(token, unk) for token in tokens]
        label_ids = [label_to_idx[label] for label in labels]
        encoded.append((word_ids, label_ids))
    return encoded

