from __future__ import annotations

import unittest

from tensor_crf_jmlr.posterior_event_algebra.dfa import (
    DFA,
    make_accept_all_dfa,
    make_empty_language_dfa,
    make_exact_pattern_dfa,
    make_mod_count_monitor,
    make_parity_monitor,
)
from tensor_crf_jmlr.posterior_event_algebra.posterior_algebra import enumerate_label_sequences


class DFATests(unittest.TestCase):
    def test_incomplete_dfa_rejected(self):
        dfa = DFA("bad", (0,), (0, 1), 0, frozenset({0}), {(0, 0): 0})
        with self.assertRaises(ValueError):
            dfa.validate_complete()

    def test_empty_and_accept_all(self):
        labels = (0, 1)
        empty = make_empty_language_dfa(labels)
        all_dfa = make_accept_all_dfa(labels)
        for seq in enumerate_label_sequences(labels, 3):
            self.assertFalse(empty.accepts(seq))
            self.assertTrue(all_dfa.accepts(seq))

    def test_exact_pattern(self):
        labels = (0, 1)
        pattern = (1, 0, 1)
        dfa = make_exact_pattern_dfa(labels, pattern)
        for seq in enumerate_label_sequences(labels, 3):
            self.assertEqual(dfa.accepts(seq), seq == pattern)

    def test_parity_monitor(self):
        labels = (0, 1)
        dfa = make_parity_monitor(labels, symbol=1, target_parity=0)
        for seq in enumerate_label_sequences(labels, 4):
            self.assertEqual(dfa.run(seq), sum(1 for label in seq if label == 1) % 2)
            self.assertEqual(dfa.accepts(seq), sum(1 for label in seq if label == 1) % 2 == 0)

    def test_shared_monitor_accepting_sets(self):
        labels = (0, 1)
        monitor = make_mod_count_monitor(labels, symbol=1, modulus=3, accepting_residues={0})
        accept_one = monitor.with_accepting({1}, name="mod-count-accept-one")
        self.assertEqual(monitor.delta, accept_one.delta)
        self.assertNotEqual(monitor.accepting, accept_one.accepting)
        self.assertTrue(accept_one.accepts((1,)))
        self.assertFalse(monitor.accepts((1,)))


if __name__ == "__main__":
    unittest.main()

