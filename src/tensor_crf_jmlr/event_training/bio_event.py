"""BIO regular-language utilities for tiny CRF event probes."""

from __future__ import annotations

from itertools import product
from typing import Iterable, Sequence


NEG_INF = -1.0e9


def bio_type(label: str) -> str | None:
    if label.startswith("B-") or label.startswith("I-"):
        return label[2:]
    return None


def is_bio_label(label: str) -> bool:
    return label == "O" or label.startswith("B-") or label.startswith("I-")


def bio_start_allowed(label: str) -> bool:
    if not is_bio_label(label):
        raise ValueError(f"not a BIO label: {label!r}")
    return not label.startswith("I-")


def bio_transition_allowed(prev_label: str, next_label: str) -> bool:
    if not is_bio_label(prev_label) or not is_bio_label(next_label):
        raise ValueError(f"not BIO labels: {prev_label!r}, {next_label!r}")
    if not next_label.startswith("I-"):
        return True
    next_type = bio_type(next_label)
    return prev_label in {f"B-{next_type}", f"I-{next_type}"}


def bio_sequence_allowed(labels: Sequence[str]) -> bool:
    if not labels:
        return True
    if not bio_start_allowed(labels[0]):
        return False
    return all(bio_transition_allowed(a, b) for a, b in zip(labels, labels[1:]))


def extract_strict_bio_spans(labels: Sequence[str]) -> set[tuple[int, int, str]]:
    spans: set[tuple[int, int, str]] = set()
    start: int | None = None
    span_type: str | None = None
    for idx, label in enumerate(labels):
        if label == "O":
            if start is not None and span_type is not None:
                spans.add((start, idx, span_type))
            start = None
            span_type = None
            continue
        prefix, _, current_type = label.partition("-")
        if prefix == "B":
            if start is not None and span_type is not None:
                spans.add((start, idx, span_type))
            start = idx
            span_type = current_type
        elif prefix == "I" and start is not None and span_type == current_type:
            continue
        else:
            if start is not None and span_type is not None:
                spans.add((start, idx, span_type))
            start = None
            span_type = None
    if start is not None and span_type is not None:
        spans.add((start, len(labels), span_type))
    return spans


def make_bio_masks(label_names: Sequence[str]):
    labels = list(label_names)
    start_allowed = [bio_start_allowed(label) for label in labels]
    transition_allowed = [
        [bio_transition_allowed(prev_label, next_label) for next_label in labels]
        for prev_label in labels
    ]
    return start_allowed, transition_allowed


def enumerate_label_paths(num_labels: int, length: int) -> Iterable[tuple[int, ...]]:
    if length < 0:
        raise ValueError("length must be nonnegative")
    return product(range(num_labels), repeat=length)

