"""Tiny nonnegative MPO/rank-construction sanity helpers.

This module is intentionally small and explicit. It checks reconstruction and
rank bookkeeping for synthetic proof objects; it is not a tensor library,
training system, benchmark, or evidence of arbitrary low-rank structure.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Dict, Hashable, Iterable, Mapping, Sequence, Tuple

from .dfa import DFA, make_parity_monitor
from .product_transfer import START, context_states, update_context


Mode = str
Value = Hashable
Key = Tuple[Value, ...]
Tensor = Dict[Key, float]
CoreEntry = Tuple[int, Value, int]


@dataclass(frozen=True)
class MPOCore:
    """One nonnegative MPO core for one physical mode."""

    mode: Mode
    left_dim: int
    right_dim: int
    entries: Mapping[CoreEntry, float]

    def __post_init__(self) -> None:
        if self.left_dim < 1 or self.right_dim < 1:
            raise ValueError("core bond dimensions must be positive")
        for (left, _value, right), coeff in self.entries.items():
            if not (0 <= left < self.left_dim):
                raise ValueError(f"left bond index out of range in {self.mode!r}")
            if not (0 <= right < self.right_dim):
                raise ValueError(f"right bond index out of range in {self.mode!r}")
            if coeff < 0:
                raise ValueError("nonnegative MPO cores cannot have negative entries")


@dataclass(frozen=True)
class MPO:
    name: str
    mode_order: Tuple[Mode, ...]
    mode_values: Mapping[Mode, Tuple[Value, ...]]
    cores: Tuple[MPOCore, ...]
    rank_bound: int
    note: str = "rank_construction_sanity_only"

    def __post_init__(self) -> None:
        if self.rank_bound < 1:
            raise ValueError("rank_bound must be positive")
        if len(self.cores) != len(self.mode_order):
            raise ValueError("number of cores must match mode_order")
        if not self.cores:
            raise ValueError("MPO must have at least one core")
        if self.cores[0].left_dim != 1 or self.cores[-1].right_dim != 1:
            raise ValueError("MPO boundary bond dimensions must be one")
        for idx, (mode, core) in enumerate(zip(self.mode_order, self.cores)):
            if mode not in self.mode_values:
                raise ValueError(f"missing values for mode {mode!r}")
            if core.mode != mode:
                raise ValueError(f"core {idx} has mode {core.mode!r}, expected {mode!r}")
            if idx + 1 < len(self.cores) and core.right_dim != self.cores[idx + 1].left_dim:
                raise ValueError("adjacent core bond dimensions do not match")
            allowed = set(self.mode_values[mode])
            for (_left, value, _right) in core.entries:
                if value not in allowed:
                    raise ValueError(f"core entry value {value!r} is not allowed for mode {mode!r}")
        if self.actual_max_bond_dim() > self.rank_bound:
            raise ValueError("rank_bound cannot be smaller than the explicit core max bond")

    @property
    def tensor(self) -> Tensor:
        """Dense reconstruction view kept for the existing sanity tests."""

        return reconstruct_mpo(self)

    def actual_max_bond_dim(self) -> int:
        if len(self.cores) <= 1:
            return 1
        return max(core.right_dim for core in self.cores[:-1])


@dataclass(frozen=True)
class LocalExtractor:
    """Local source-value extractor used by rank-preserving mode insertion."""

    target_mode: Mode
    fn: Callable[[Value], Value]

    def __call__(self, target_value: Value) -> Value:
        return self.fn(target_value)


def _make_core(
    mode: Mode,
    left_dim: int,
    right_dim: int,
    entries: Mapping[CoreEntry, float],
) -> MPOCore:
    return MPOCore(mode, left_dim, right_dim, dict(entries))


def _identity_core(mode: Mode, values: Sequence[Value], bond_dim: int) -> MPOCore:
    entries: dict[CoreEntry, float] = {}
    for bond in range(bond_dim):
        for value in values:
            entries[(bond, value, bond)] = 1.0
    return _make_core(mode, bond_dim, bond_dim, entries)


def max_bond_dim(mpo: MPO) -> int:
    return mpo.actual_max_bond_dim()


def reconstruct_mpo(mpo: MPO) -> Tensor:
    tensor: Tensor = {}
    for key in all_keys(mpo.mode_order, mpo.mode_values):
        active = {0: 1.0}
        for value, core in zip(key, mpo.cores):
            next_active: dict[int, float] = {}
            for (left, core_value, right), coeff in core.entries.items():
                if core_value != value or left not in active:
                    continue
                next_active[right] = next_active.get(right, 0.0) + active[left] * coeff
            active = next_active
            if not active:
                break
        tensor[key] = active.get(0, 0.0)
    return tensor


def all_keys(mode_order: Sequence[Mode], mode_values: Mapping[Mode, Sequence[Value]]):
    return product(*(tuple(mode_values[mode]) for mode in mode_order))


def _guard_labels(labels: Sequence[Value]) -> Tuple[Value, ...]:
    labels_tuple = tuple(labels)
    if START in labels_tuple:
        raise ValueError("START sentinel must not be a label")
    if not labels_tuple:
        raise ValueError("labels must be nonempty")
    return labels_tuple


def augmented_mode_order(m: int) -> Tuple[Mode, ...]:
    if m <= 0:
        raise ValueError("m must be positive")
    if m == 1:
        return ("q", "j", "qp")
    pair_modes = tuple(f"c{i}_cp{i}" for i in range(1, m))
    return ("q",) + pair_modes + ("j", "qp")


def transfer_mode_order(m: int) -> Tuple[Mode, ...]:
    if m <= 0:
        raise ValueError("m must be positive")
    if m == 1:
        return ("q", "qp")
    pair_modes = tuple(f"c{i}_cp{i}" for i in range(1, m))
    return ("q",) + pair_modes + ("qp",)


def shift_mode_order(m: int) -> Tuple[Mode, ...]:
    if m <= 0:
        raise ValueError("m must be positive")
    if m == 1:
        return ("j",)
    return tuple(f"c{i}_cp{i}" for i in range(1, m)) + ("j",)


def score_mode_order(m: int) -> Tuple[Mode, ...]:
    if m <= 0:
        raise ValueError("m must be positive")
    if m == 1:
        return ("j",)
    return tuple(f"c{i}" for i in range(1, m)) + ("j",)


def shift_mode_values(labels: Sequence[Value], m: int) -> dict[Mode, Tuple[Value, ...]]:
    labels_tuple = _guard_labels(labels)
    values: dict[Mode, Tuple[Value, ...]] = {}
    if m == 1:
        values["j"] = labels_tuple
        return values
    omega = (START,) + labels_tuple
    for i in range(1, m):
        values[f"c{i}_cp{i}"] = tuple(product(omega, omega))
    values["j"] = labels_tuple
    return values


def direct_shift_tensor(labels: Sequence[Value], m: int) -> tuple[Tuple[Mode, ...], dict[Mode, Tuple[Value, ...]], Tensor]:
    labels_tuple = _guard_labels(labels)
    order = shift_mode_order(m)
    values = shift_mode_values(labels_tuple, m)
    tensor: Tensor = {}
    for key in all_keys(order, values):
        if m == 1:
            tensor[key] = 1.0
            continue
        pairs = key[:-1]
        label = key[-1]
        context = tuple(pair[0] for pair in pairs)
        next_context = tuple(pair[1] for pair in pairs)
        tensor[key] = 1.0 if update_context(context, label, m) == next_context else 0.0
    return order, values, tensor


def shift_register_mpo(labels: Sequence[Value], m: int) -> MPO:
    labels_tuple = _guard_labels(labels)
    order = shift_mode_order(m)
    values = shift_mode_values(labels_tuple, m)
    if m == 1:
        entries = {(0, label, 0): 1.0 for label in labels_tuple}
        core = _make_core("j", 1, 1, entries)
        return MPO("shift-register", order, values, (core,), 1)

    omega = (START,) + labels_tuple
    omega_index = {value: idx for idx, value in enumerate(omega)}
    cores: list[MPOCore] = []
    first_mode = order[0]
    first_entries = {
        (0, pair, omega_index[pair[1]]): 1.0
        for pair in values[first_mode]
    }
    cores.append(_make_core(first_mode, 1, len(omega), first_entries))
    for mode in order[1:-1]:
        entries = {}
        for pair in values[mode]:
            c_value, cp_value = pair
            entries[(omega_index[c_value], pair, omega_index[cp_value])] = 1.0
        cores.append(_make_core(mode, len(omega), len(omega), entries))
    final_entries = {
        (omega_index[label], label, 0): 1.0
        for label in labels_tuple
    }
    cores.append(_make_core("j", len(omega), 1, final_entries))
    return MPO("shift-register", order, values, tuple(cores), len(omega))


def score_table_mpo_rank1(labels: Sequence[Value], m: int) -> MPO:
    labels_tuple = _guard_labels(labels)
    order = score_mode_order(m)
    values: dict[Mode, Tuple[Value, ...]] = {}
    if m >= 2:
        omega = (START,) + labels_tuple
        for i in range(1, m):
            values[f"c{i}"] = omega
    values["j"] = labels_tuple

    label_factor = {label: 1.0 + 0.2 * idx for idx, label in enumerate(labels_tuple)}
    cores: list[MPOCore] = []
    for mode in order:
        entries = {}
        for value in values[mode]:
            if mode == "j":
                coeff = label_factor[value]
            else:
                pos = int(mode[1:])
                coeff = 1.0 if value == START else 1.0 + 0.05 * pos
            entries[(0, value, 0)] = coeff
        cores.append(_make_core(mode, 1, 1, entries))
    return MPO("rank-one-score", order, values, tuple(cores), 1)


def dfa_transition_mpo(dfa: DFA, rank_bound: int | None = None, name: str = "dfa-transition") -> MPO:
    dfa.validate_complete()
    order = ("q", "j", "qp")
    values = {"q": tuple(dfa.states), "j": tuple(dfa.alphabet), "qp": tuple(dfa.states)}
    witnesses = tuple(product(values["q"], values["j"]))
    witness_index = {witness: idx for idx, witness in enumerate(witnesses)}
    first = {
        (0, q, witness_index[(q, label)]): 1.0
        for q in values["q"]
        for label in values["j"]
    }
    middle = {
        (idx, label, idx): 1.0
        for (q, label), idx in witness_index.items()
    }
    final = {
        (idx, dfa.step(q, label), 0): 1.0
        for (q, label), idx in witness_index.items()
    }
    cores = (
        _make_core("q", 1, len(witnesses), first),
        _make_core("j", len(witnesses), len(witnesses), middle),
        _make_core("qp", len(witnesses), 1, final),
    )
    actual_rank = max(1, len(witnesses))
    if rank_bound is not None and rank_bound < actual_rank:
        raise ValueError("rank_bound is smaller than the explicit DFA enumeration cores")
    return MPO(name, order, values, cores, rank_bound or actual_rank)


def parity_transition_mpo(labels: Sequence[Value], symbol: Value = 1) -> tuple[DFA, MPO]:
    labels_tuple = _guard_labels(labels)
    dfa = make_parity_monitor(labels_tuple, symbol=symbol, target_parity=0)
    states = tuple(dfa.states)
    if set(states) != {0, 1}:
        raise ValueError("parity sanity constructor expects states {0,1}")
    order = ("q", "j", "qp")
    values = {"q": states, "j": labels_tuple, "qp": states}
    first = {(0, q, q): 1.0 for q in states}
    middle = {
        (q, label, dfa.step(q, label)): 1.0
        for q in states
        for label in labels_tuple
    }
    final = {(q, q, 0): 1.0 for q in states}
    cores = (
        _make_core("q", 1, 2, first),
        _make_core("j", 2, 2, middle),
        _make_core("qp", 2, 1, final),
    )
    return dfa, MPO("parity-transition", order, values, cores, 2)


def augmented_mode_values(labels: Sequence[Value], m: int, dfa: DFA) -> dict[Mode, Tuple[Value, ...]]:
    labels_tuple = _guard_labels(labels)
    values: dict[Mode, Tuple[Value, ...]] = {
        "q": tuple(dfa.states),
        "j": labels_tuple,
        "qp": tuple(dfa.states),
    }
    if m >= 2:
        omega = (START,) + labels_tuple
        for i in range(1, m):
            values[f"c{i}_cp{i}"] = tuple(product(omega, omega))
    return values


def lift_mpo(
    mpo: MPO,
    target_order: Sequence[Mode],
    target_values: Mapping[Mode, Tuple[Value, ...]],
    extractors: Mapping[Mode, Callable[[Value], Value]] | None = None,
    name: str | None = None,
) -> MPO:
    extractors = extractors or {}
    order = tuple(target_order)
    source_to_target: dict[Mode, tuple[Mode, Callable[[Value], Value]]] = {}
    for source_mode in mpo.mode_order:
        if source_mode in order:
            source_to_target[source_mode] = (source_mode, lambda value: value)
            continue
        extractor = extractors.get(source_mode)
        if not isinstance(extractor, LocalExtractor):
            raise ValueError(f"no local extractor for source mode {source_mode!r}")
        source_to_target[source_mode] = (extractor.target_mode, extractor)

    target_to_source: dict[Mode, tuple[Mode, Callable[[Value], Value]]] = {}
    for source_mode, (target_mode, extractor) in source_to_target.items():
        if target_mode in target_to_source:
            raise ValueError(f"target mode {target_mode!r} maps to multiple source modes")
        target_to_source[target_mode] = (source_mode, extractor)

    source_idx = 0
    current_dim = 1
    lifted_cores: list[MPOCore] = []
    for target_mode in order:
        if target_mode not in target_values:
            raise ValueError(f"missing target values for mode {target_mode!r}")
        if target_mode not in target_to_source:
            lifted_cores.append(_identity_core(target_mode, target_values[target_mode], current_dim))
            continue

        source_mode, extractor = target_to_source[target_mode]
        source_core = mpo.cores[source_idx]
        if source_core.mode != source_mode:
            raise ValueError("source modes are not order-compatible with target modes")
        if source_core.left_dim != current_dim:
            raise ValueError("lift would break bond-dimension compatibility")
        entries: dict[CoreEntry, float] = {}
        for target_value in target_values[target_mode]:
            source_value = extractor(target_value)
            for (left, core_value, right), coeff in source_core.entries.items():
                if core_value == source_value:
                    entries[(left, target_value, right)] = coeff
        lifted_cores.append(_make_core(target_mode, source_core.left_dim, source_core.right_dim, entries))
        current_dim = source_core.right_dim
        source_idx += 1
    if source_idx != len(mpo.cores):
        raise ValueError("not all source cores were lifted")
    return MPO(name or f"lift-{mpo.name}", order, dict(target_values), tuple(lifted_cores), mpo.rank_bound)


def context_extractors(m: int) -> dict[Mode, LocalExtractor]:
    extractors: dict[Mode, LocalExtractor] = {}
    for i in range(1, m):
        pair_mode = f"c{i}_cp{i}"
        c_mode = f"c{i}"
        extractors[c_mode] = LocalExtractor(pair_mode, lambda pair: pair[0])
    return extractors


def pointwise_core_product(mpo_a: MPO, mpo_b: MPO, name: str = "core-product") -> MPO:
    if tuple(mpo_a.mode_order) != tuple(mpo_b.mode_order):
        raise ValueError("mode orders must match for pointwise product")
    for mode in mpo_a.mode_order:
        if tuple(mpo_a.mode_values[mode]) != tuple(mpo_b.mode_values[mode]):
            raise ValueError(f"mode values differ for {mode!r}")

    cores: list[MPOCore] = []
    for core_a, core_b in zip(mpo_a.cores, mpo_b.cores):
        entries: dict[CoreEntry, float] = {}
        for (left_a, value_a, right_a), coeff_a in core_a.entries.items():
            for (left_b, value_b, right_b), coeff_b in core_b.entries.items():
                if value_a != value_b:
                    continue
                left = left_a * core_b.left_dim + left_b
                right = right_a * core_b.right_dim + right_b
                entries[(left, value_a, right)] = entries.get((left, value_a, right), 0.0) + coeff_a * coeff_b
        cores.append(
            _make_core(
                core_a.mode,
                core_a.left_dim * core_b.left_dim,
                core_a.right_dim * core_b.right_dim,
                entries,
            )
        )
    return MPO(
        name,
        mpo_a.mode_order,
        dict(mpo_a.mode_values),
        tuple(cores),
        mpo_a.rank_bound * mpo_b.rank_bound,
    )


def label_contract(mpo: MPO, label_mode: Mode = "j", name: str = "label-contract") -> MPO:
    if label_mode not in mpo.mode_order:
        raise ValueError(f"label mode {label_mode!r} not in mode order")
    label_pos = mpo.mode_order.index(label_mode)
    order = tuple(mode for mode in mpo.mode_order if mode != label_mode)
    values = {mode: tuple(mpo.mode_values[mode]) for mode in order}
    label_values = tuple(mpo.mode_values[label_mode])

    if label_pos + 1 < len(mpo.cores):
        label_core = mpo.cores[label_pos]
        next_core = mpo.cores[label_pos + 1]
        entries: dict[CoreEntry, float] = {}
        for (left, label_value, mid), label_coeff in label_core.entries.items():
            if label_value not in label_values:
                continue
            for (mid2, next_value, right), next_coeff in next_core.entries.items():
                if mid != mid2:
                    continue
                key = (left, next_value, right)
                entries[key] = entries.get(key, 0.0) + label_coeff * next_coeff
        combined = _make_core(next_core.mode, label_core.left_dim, next_core.right_dim, entries)
        cores = mpo.cores[:label_pos] + (combined,) + mpo.cores[label_pos + 2 :]
    else:
        prev_core = mpo.cores[label_pos - 1]
        label_core = mpo.cores[label_pos]
        entries = {}
        for (left, prev_value, mid), prev_coeff in prev_core.entries.items():
            for (mid2, label_value, right), label_coeff in label_core.entries.items():
                if mid != mid2 or label_value not in label_values:
                    continue
                key = (left, prev_value, right)
                entries[key] = entries.get(key, 0.0) + prev_coeff * label_coeff
        combined = _make_core(prev_core.mode, prev_core.left_dim, label_core.right_dim, entries)
        cores = mpo.cores[: label_pos - 1] + (combined,)
    return MPO(name, order, values, cores, mpo.rank_bound)


def direct_event_transfer_from_augmented(H_aug: MPO, label_mode: Mode = "j") -> Tensor:
    return label_contract(H_aug, label_mode=label_mode, name="direct-transfer").tensor


def terminal_vector_for_accepting(
    labels: Sequence[Value],
    m: int,
    dfa: DFA,
    accepting: Iterable[Value],
) -> dict[tuple[object, Value], int]:
    _guard_labels(labels)
    accepting_set = set(accepting)
    contexts = context_states(labels, m)
    return {
        (context, q): 1 if q in accepting_set else 0
        for context in contexts
        for q in dfa.states
    }


def compare_tensors(a: Tensor, b: Tensor, tolerance: float = 1e-12) -> tuple[bool, float]:
    keys = set(a) | set(b)
    max_abs = 0.0
    for key in keys:
        max_abs = max(max_abs, abs(a.get(key, 0.0) - b.get(key, 0.0)))
    return max_abs <= tolerance, max_abs
