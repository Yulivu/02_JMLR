"""Complete deterministic finite monitors for tiny formula checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Hashable, Iterable, Sequence, Tuple


State = Hashable
Label = Hashable


@dataclass(frozen=True)
class DFA:
    name: str
    states: Tuple[State, ...]
    alphabet: Tuple[Label, ...]
    start: State
    accepting: frozenset[State]
    delta: Dict[Tuple[State, Label], State]

    def validate_complete(self) -> None:
        if self.start not in self.states:
            raise ValueError("DFA start state is not in states")
        missing = [
            (q, a)
            for q in self.states
            for a in self.alphabet
            if (q, a) not in self.delta
        ]
        if missing:
            raise ValueError(f"DFA transition function is incomplete: {missing[:3]}")
        state_set = set(self.states)
        if not self.accepting.issubset(state_set):
            raise ValueError("DFA accepting set is not a subset of states")
        for key, value in self.delta.items():
            q, a = key
            if q not in state_set or a not in self.alphabet or value not in state_set:
                raise ValueError(f"invalid transition {key!r}->{value!r}")

    def step(self, state: State, label: Label) -> State:
        return self.delta[(state, label)]

    def run(self, labels: Sequence[Label]) -> State:
        q = self.start
        for label in labels:
            q = self.step(q, label)
        return q

    def accepts(self, labels: Sequence[Label]) -> bool:
        return self.run(labels) in self.accepting

    def with_accepting(self, accepting: Iterable[State], name: str | None = None) -> "DFA":
        return DFA(
            name=name or self.name,
            states=self.states,
            alphabet=self.alphabet,
            start=self.start,
            accepting=frozenset(accepting),
            delta=dict(self.delta),
        )

    def terminal_vector(self, product_states: Sequence[Tuple[object, State]]) -> list[int]:
        return [1 if q in self.accepting else 0 for _, q in product_states]


def make_empty_language_dfa(labels: Sequence[Label]) -> DFA:
    alphabet = tuple(labels)
    delta = {(0, a): 0 for a in alphabet}
    dfa = DFA("empty-language", (0,), alphabet, 0, frozenset(), delta)
    dfa.validate_complete()
    return dfa


def make_accept_all_dfa(labels: Sequence[Label]) -> DFA:
    alphabet = tuple(labels)
    delta = {(0, a): 0 for a in alphabet}
    dfa = DFA("accept-all", (0,), alphabet, 0, frozenset({0}), delta)
    dfa.validate_complete()
    return dfa


def make_exact_pattern_dfa(labels: Sequence[Label], pattern: Sequence[Label]) -> DFA:
    alphabet = tuple(labels)
    pattern_tuple = tuple(pattern)
    dead = len(pattern_tuple) + 1
    states = tuple(range(dead + 1))
    delta: Dict[Tuple[int, Label], int] = {}
    for q in states:
        for a in alphabet:
            if q < len(pattern_tuple) and a == pattern_tuple[q]:
                delta[(q, a)] = q + 1
            else:
                delta[(q, a)] = dead
    for a in alphabet:
        delta[(dead, a)] = dead
    dfa = DFA(
        f"exact-pattern-{pattern_tuple}",
        states,
        alphabet,
        0,
        frozenset({len(pattern_tuple)}),
        delta,
    )
    dfa.validate_complete()
    return dfa


def make_parity_monitor(
    labels: Sequence[Label],
    symbol: Label = 1,
    target_parity: int = 0,
) -> DFA:
    alphabet = tuple(labels)
    states = (0, 1)
    delta = {}
    for q in states:
        for a in alphabet:
            delta[(q, a)] = 1 - q if a == symbol else q
    dfa = DFA(
        f"parity-{symbol}-{target_parity}",
        states,
        alphabet,
        0,
        frozenset({target_parity}),
        delta,
    )
    dfa.validate_complete()
    return dfa


def make_mod_count_monitor(
    labels: Sequence[Label],
    symbol: Label,
    modulus: int,
    accepting_residues: Iterable[int],
) -> DFA:
    if modulus <= 0:
        raise ValueError("modulus must be positive")
    alphabet = tuple(labels)
    states = tuple(range(modulus))
    delta = {}
    for q in states:
        for a in alphabet:
            delta[(q, a)] = (q + 1) % modulus if a == symbol else q
    accepting = frozenset(r % modulus for r in accepting_residues)
    dfa = DFA(
        f"mod-count-{symbol}-mod-{modulus}",
        states,
        alphabet,
        0,
        accepting,
        delta,
    )
    dfa.validate_complete()
    return dfa

