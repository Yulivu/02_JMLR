"""Finite brute-force posterior event algebra.

All routines are intended for tiny synthetic sanity checks. They do not train
models, read datasets, benchmark anything, or make usefulness claims.
"""

from __future__ import annotations

from itertools import product
from math import exp, isfinite
from typing import Callable, Dict, Hashable, Iterable, Sequence, Tuple


Label = Hashable
SequenceT = Tuple[Label, ...]
ScoreFn = Callable[[Sequence[Label]], float]
AcceptsFn = Callable[[Sequence[Label]], bool]


def enumerate_label_sequences(labels: Sequence[Label], T: int) -> Iterable[SequenceT]:
    if T < 0:
        raise ValueError("T must be nonnegative")
    labels_tuple = tuple(labels)
    if not labels_tuple and T > 0:
        raise ValueError("labels must be nonempty when T > 0")
    return product(labels_tuple, repeat=T)


def _positive_weight(score: float) -> float:
    if not isfinite(score):
        raise ValueError(f"score must be finite, got {score!r}")
    return exp(score)


def partition_bruteforce(labels: Sequence[Label], T: int, score_fn: ScoreFn) -> float:
    total = 0.0
    for seq in enumerate_label_sequences(labels, T):
        total += _positive_weight(score_fn(seq))
    return total


def event_partition_bruteforce(
    labels: Sequence[Label],
    T: int,
    score_fn: ScoreFn,
    accepts_fn: AcceptsFn,
) -> float:
    total = 0.0
    for seq in enumerate_label_sequences(labels, T):
        if accepts_fn(seq):
            total += _positive_weight(score_fn(seq))
    return total


def event_probability_bruteforce(
    labels: Sequence[Label],
    T: int,
    score_fn: ScoreFn,
    accepts_fn: AcceptsFn,
) -> Dict[str, float | str]:
    Z = partition_bruteforce(labels, T, score_fn)
    if Z <= 0.0:
        raise ValueError("finite positive potentials should give Z > 0")
    Z_L = event_partition_bruteforce(labels, T, score_fn, accepts_fn)
    status = "positive_event" if Z_L > 0.0 else "zero_event"
    return {
        "Z": Z,
        "Z_L": Z_L,
        "P_L": Z_L / Z,
        "status": status,
    }


def restricted_distribution(
    labels: Sequence[Label],
    T: int,
    score_fn: ScoreFn,
    accepts_fn: AcceptsFn,
) -> Dict[SequenceT, float] | Dict[str, str]:
    Z_L = event_partition_bruteforce(labels, T, score_fn, accepts_fn)
    if Z_L <= 0.0:
        return {"status": "zero_event"}
    dist: Dict[SequenceT, float] = {}
    for seq in enumerate_label_sequences(labels, T):
        if accepts_fn(seq):
            dist[seq] = _positive_weight(score_fn(seq)) / Z_L
    return dist

