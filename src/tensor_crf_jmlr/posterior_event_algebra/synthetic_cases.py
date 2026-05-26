"""Deterministic tiny synthetic score factories for sanity tests."""

from __future__ import annotations

from math import exp
from typing import Callable, Hashable, Sequence

from .product_transfer import Context, START


Label = Hashable


def make_context_phi_fns(T: int, labels: Sequence[Label], low_prob_symbol: Label | None = None):
    label_to_idx = {label: idx for idx, label in enumerate(labels)}

    def make_phi(pos: int) -> Callable[[Context, Label], float]:
        def phi(context: Context, label: Label) -> float:
            label_idx = label_to_idx[label]
            if low_prob_symbol is not None and label == low_prob_symbol:
                return -18.0
            context_score = 0.0
            for offset, item in enumerate(context):
                if item != START:
                    context_score += 0.03 * (offset + 1) * (label_to_idx[item] + 1)
                else:
                    context_score -= 0.02 * (offset + 1)
            return 0.11 * (pos + 1) * (label_idx + 1) + context_score

        return phi

    return [make_phi(pos) for pos in range(T)]


def phi_to_G(phi_fns):
    return [lambda context, label, phi=phi: exp(phi(context, label)) for phi in phi_fns]


def make_first_order_factors(T: int, labels: Sequence[Label], low_prob_symbol: Label | None = None):
    label_to_idx = {label: idx for idx, label in enumerate(labels)}

    def make_e(pos: int):
        def e(label: Label) -> float:
            if low_prob_symbol is not None and label == low_prob_symbol:
                return -18.0
            idx = label_to_idx[label]
            return 0.13 * (pos + 1) * (idx + 1) - 0.04 * ((pos + idx) % 2)

        return e

    def make_a(pos: int):
        def a(prev: Label, label: Label) -> float:
            prev_idx = label_to_idx[prev]
            idx = label_to_idx[label]
            return 0.05 * (prev_idx + 1) * (idx + 1) + 0.02 * pos * (idx - prev_idx)

        return a

    e_fns = [make_e(pos) for pos in range(T)]
    a_fns = [lambda _prev, _label: 0.0] + [make_a(pos) for pos in range(1, T)]
    return e_fns, a_fns

