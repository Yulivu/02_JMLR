from __future__ import annotations

import unittest

from tensor_crf_jmlr.posterior_event_algebra.dfa import (
    make_accept_all_dfa,
    make_empty_language_dfa,
    make_exact_pattern_dfa,
    make_parity_monitor,
)
from tensor_crf_jmlr.posterior_event_algebra.posterior_algebra import event_partition_bruteforce, partition_bruteforce
from tensor_crf_jmlr.posterior_event_algebra.product_transfer import (
    context_order_m_score,
    event_partition_transfer_context_order_m,
    event_partition_transfer_first_order_reduced,
    first_order_reduced_score,
)
from tensor_crf_jmlr.posterior_event_algebra.synthetic_cases import make_context_phi_fns, make_first_order_factors, phi_to_G


class ProductTransferTests(unittest.TestCase):
    def test_context_order_m_T1_empty_and_accept_all(self):
        labels = (0, 1)
        T = 1
        m = 2
        phi_fns = make_context_phi_fns(T, labels)
        G_fns = phi_to_G(phi_fns)

        def score(seq):
            return context_order_m_score(seq, m, phi_fns)

        empty = make_empty_language_dfa(labels)
        all_dfa = make_accept_all_dfa(labels)
        self.assertAlmostEqual(
            event_partition_transfer_context_order_m(labels, T, m, G_fns, empty),
            0.0,
        )
        self.assertAlmostEqual(
            event_partition_transfer_context_order_m(labels, T, m, G_fns, all_dfa),
            partition_bruteforce(labels, T, score),
        )

    def test_context_order_m_T_greater_than_1_pattern_and_parity(self):
        labels = (0, 1)
        T = 4
        m = 2
        phi_fns = make_context_phi_fns(T, labels)
        G_fns = phi_to_G(phi_fns)

        def score(seq):
            return context_order_m_score(seq, m, phi_fns)

        for dfa in (make_exact_pattern_dfa(labels, (1, 0, 1, 0)), make_parity_monitor(labels)):
            brute = event_partition_bruteforce(labels, T, score, dfa.accepts)
            transfer = event_partition_transfer_context_order_m(labels, T, m, G_fns, dfa)
            self.assertAlmostEqual(transfer, brute)

    def test_first_order_reduced_T1_uses_scored_v1_only(self):
        labels = (0, 1)
        T = 1
        e_fns, a_fns = make_first_order_factors(T, labels)
        dfa = make_exact_pattern_dfa(labels, (1,))

        def score(seq):
            return first_order_reduced_score(seq, e_fns, a_fns)

        brute = event_partition_bruteforce(labels, T, score, dfa.accepts)
        transfer = event_partition_transfer_first_order_reduced(labels, T, e_fns, a_fns, dfa)
        self.assertAlmostEqual(transfer, brute)

    def test_first_order_reduced_T_greater_than_1(self):
        labels = (0, 1)
        T = 4
        e_fns, a_fns = make_first_order_factors(T, labels)
        dfa = make_parity_monitor(labels)

        def score(seq):
            return first_order_reduced_score(seq, e_fns, a_fns)

        brute = event_partition_bruteforce(labels, T, score, dfa.accepts)
        transfer = event_partition_transfer_first_order_reduced(labels, T, e_fns, a_fns, dfa)
        self.assertAlmostEqual(transfer, brute)

    def test_low_probability_event(self):
        labels = (0, 1)
        T = 4
        e_fns, a_fns = make_first_order_factors(T, labels, low_prob_symbol=1)
        dfa = make_exact_pattern_dfa(labels, (0, 0, 0, 1))

        def score(seq):
            return first_order_reduced_score(seq, e_fns, a_fns)

        brute = event_partition_bruteforce(labels, T, score, dfa.accepts)
        transfer = event_partition_transfer_first_order_reduced(labels, T, e_fns, a_fns, dfa)
        self.assertGreater(brute, 0.0)
        self.assertLess(brute / partition_bruteforce(labels, T, score), 1e-6)
        self.assertAlmostEqual(transfer, brute)


if __name__ == "__main__":
    unittest.main()

