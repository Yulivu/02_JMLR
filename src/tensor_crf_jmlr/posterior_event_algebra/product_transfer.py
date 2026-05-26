"""Product automaton transfer computations for tiny finite cases."""

from __future__ import annotations

from itertools import product
from math import exp
from typing import Callable, Hashable, Sequence, Tuple

from .dfa import DFA
from .indexing import (
    CONTEXT_ORDER_M,
    FIRST_ORDER_REDUCED,
    make_score_free_u0,
    make_scored_v1,
    validate_convention,
)


START = "__START__"
Label = Hashable
Context = Tuple[Hashable, ...]
Matrix = list[list[float]]


def context_states(labels: Sequence[Label], m: int) -> list[Context]:
    if m <= 0:
        raise ValueError("m must be positive")
    if m == 1:
        return [()]
    alphabet_with_start = (START,) + tuple(labels)
    return [tuple(ctx) for ctx in product(alphabet_with_start, repeat=m - 1)]


def initial_context(m: int) -> Context:
    if m <= 0:
        raise ValueError("m must be positive")
    return () if m == 1 else tuple(START for _ in range(m - 1))


def update_context(context: Context, label: Label, m: int) -> Context:
    if m <= 0:
        raise ValueError("m must be positive")
    if m == 1:
        return ()
    if len(context) != m - 1:
        raise ValueError("context length does not match m")
    return tuple((context + (label,))[-(m - 1) :])


def build_product_states(contexts: Sequence[Context], dfa_states: Sequence[Hashable]):
    return [(context, q) for context in contexts for q in dfa_states]


def _state_index(states: Sequence[object]) -> dict[object, int]:
    return {state: idx for idx, state in enumerate(states)}


def _row_vector_times_matrix(row: Sequence[float], matrix: Matrix) -> list[float]:
    if not matrix:
        return []
    if len(row) != len(matrix):
        raise ValueError("row and matrix dimensions are incompatible")
    width = len(matrix[0])
    out = [0.0 for _ in range(width)]
    for i, value in enumerate(row):
        if value == 0.0:
            continue
        for j in range(width):
            out[j] += value * matrix[i][j]
    return out


def _dot(row: Sequence[float], col: Sequence[float]) -> float:
    if len(row) != len(col):
        raise ValueError("dot-product dimensions are incompatible")
    return sum(a * b for a, b in zip(row, col))


def build_transfer_context_order_m(
    labels: Sequence[Label],
    contexts: Sequence[Context],
    dfa: DFA,
    m: int,
    G_t: Callable[[Context, Label], float],
) -> tuple[Matrix, list[tuple[Context, Hashable]]]:
    product_states = build_product_states(contexts, dfa.states)
    index = _state_index(product_states)
    matrix = [[0.0 for _ in product_states] for _ in product_states]
    for row, (context, q) in enumerate(product_states):
        for label in labels:
            c_next = update_context(context, label, m)
            q_next = dfa.step(q, label)
            col = index[(c_next, q_next)]
            matrix[row][col] += G_t(context, label)
    return matrix, product_states


def event_partition_transfer_context_order_m(
    labels: Sequence[Label],
    T: int,
    m: int,
    G_fns: Sequence[Callable[[Context, Label], float]],
    dfa: DFA,
) -> float:
    if T != len(G_fns):
        raise ValueError("G_fns length must equal T")
    validate_convention(CONTEXT_ORDER_M, T, uses_scored_initial=False, includes_M1=T >= 1)
    contexts = context_states(labels, m)
    c0 = initial_context(m)
    product_states = build_product_states(contexts, dfa.states)
    alpha = make_score_free_u0(product_states, c0, dfa.start)
    for G_t in G_fns:
        matrix, matrix_states = build_transfer_context_order_m(labels, contexts, dfa, m, G_t)
        if matrix_states != product_states:
            raise AssertionError("product-state order drifted")
        alpha = _row_vector_times_matrix(alpha, matrix)
    b = dfa.terminal_vector(product_states)
    return _dot(alpha, b)


def context_order_m_score(
    sequence: Sequence[Label],
    m: int,
    phi_fns: Sequence[Callable[[Context, Label], float]],
) -> float:
    if len(sequence) != len(phi_fns):
        raise ValueError("sequence length and phi_fns length differ")
    context = initial_context(m)
    total = 0.0
    for label, phi_t in zip(sequence, phi_fns):
        total += phi_t(context, label)
        context = update_context(context, label, m)
    return total


def label_state_list(labels: Sequence[Label], dfa_states: Sequence[Hashable]):
    return [(label, q) for label in labels for q in dfa_states]


def build_transfer_first_order_reduced(
    labels: Sequence[Label],
    dfa: DFA,
    e_t_fn: Callable[[Label], float],
    a_t_fn: Callable[[Label, Label], float],
) -> tuple[Matrix, list[tuple[Label, Hashable]]]:
    states = label_state_list(labels, dfa.states)
    index = _state_index(states)
    matrix = [[0.0 for _ in states] for _ in states]
    for row, (prev_label, q) in enumerate(states):
        for label in labels:
            q_next = dfa.step(q, label)
            col = index[(label, q_next)]
            matrix[row][col] += exp(e_t_fn(label) + a_t_fn(prev_label, label))
    return matrix, states


def event_partition_transfer_first_order_reduced(
    labels: Sequence[Label],
    T: int,
    e_fns: Sequence[Callable[[Label], float]],
    a_fns: Sequence[Callable[[Label, Label], float]],
    dfa: DFA,
) -> float:
    if T != len(e_fns) or T != len(a_fns):
        raise ValueError("e_fns and a_fns must both have length T")
    validate_convention(FIRST_ORDER_REDUCED, T, uses_scored_initial=True, includes_M1=False)
    states = label_state_list(labels, dfa.states)
    alpha = make_scored_v1(states, labels, dfa, e_fns[0])
    for pos in range(1, T):
        matrix, matrix_states = build_transfer_first_order_reduced(
            labels, dfa, e_fns[pos], a_fns[pos]
        )
        if matrix_states != states:
            raise AssertionError("label-state order drifted")
        alpha = _row_vector_times_matrix(alpha, matrix)
    b = [1 if q in dfa.accepting else 0 for _, q in states]
    return _dot(alpha, b)


def first_order_reduced_score(
    sequence: Sequence[Label],
    e_fns: Sequence[Callable[[Label], float]],
    a_fns: Sequence[Callable[[Label, Label], float]],
) -> float:
    if len(sequence) != len(e_fns) or len(sequence) != len(a_fns):
        raise ValueError("sequence and factor lengths differ")
    if not sequence:
        return 0.0
    total = e_fns[0](sequence[0])
    for pos in range(1, len(sequence)):
        total += e_fns[pos](sequence[pos]) + a_fns[pos](sequence[pos - 1], sequence[pos])
    return total

