"""Indexing and boundary guards for proof-audited transfer conventions."""

from __future__ import annotations

from math import exp
from typing import Callable, Hashable, Sequence, Tuple

from .dfa import DFA


Label = Hashable
State = Hashable


CONTEXT_ORDER_M = "context_order_m"
FIRST_ORDER_REDUCED = "first_order_reduced"


def transfer_index_set(convention: str, T: int) -> Tuple[int, ...]:
    if T < 0:
        raise ValueError("T must be nonnegative")
    if convention == CONTEXT_ORDER_M:
        return tuple(range(1, T + 1))
    if convention == FIRST_ORDER_REDUCED:
        return tuple(range(2, T + 1))
    raise ValueError(f"unknown convention {convention!r}")


def validate_convention(
    convention: str,
    T: int,
    uses_scored_initial: bool,
    includes_M1: bool,
) -> None:
    if convention == CONTEXT_ORDER_M:
        if uses_scored_initial:
            raise ValueError("context/order-m convention requires score-free u_0")
        if T >= 1 and not includes_M1:
            raise ValueError("context/order-m convention must include M_1")
        return
    if convention == FIRST_ORDER_REDUCED:
        if not uses_scored_initial:
            raise ValueError("first-order reduced convention requires scored v_1")
        if includes_M1:
            raise ValueError("first-order reduced convention must not include M_1")
        return
    raise ValueError(f"unknown convention {convention!r}")


def identity_matrix(size: int) -> list[list[float]]:
    if size < 0:
        raise ValueError("size must be nonnegative")
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]


def make_score_free_u0(
    product_states: Sequence[Tuple[object, State]],
    c0: object,
    q_start: State,
) -> list[float]:
    return [1.0 if (c, q) == (c0, q_start) else 0.0 for c, q in product_states]


def make_scored_v1(
    label_states: Sequence[Tuple[Label, State]],
    labels: Sequence[Label],
    dfa: DFA,
    e1_fn: Callable[[Label], float],
) -> list[float]:
    label_set = set(labels)
    result = []
    for label, q in label_states:
        if label not in label_set:
            raise ValueError(f"label state has unknown label {label!r}")
        target_q = dfa.step(dfa.start, label)
        result.append(exp(e1_fn(label)) if q == target_q else 0.0)
    return result

