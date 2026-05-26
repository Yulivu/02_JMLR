from __future__ import annotations

import unittest

from tensor_crf_jmlr.posterior_event_algebra.dfa import make_parity_monitor
from tensor_crf_jmlr.posterior_event_algebra.posterior_algebra import enumerate_label_sequences, event_partition_bruteforce
from tensor_crf_jmlr.posterior_event_algebra.product_transfer import (
    START,
    context_order_m_score,
    event_partition_transfer_context_order_m,
    initial_context,
    update_context,
)
from tensor_crf_jmlr.posterior_event_algebra.synthetic_cases import make_context_phi_fns, phi_to_G


class OrderMContextTests(unittest.TestCase):
    def test_context_update_boundaries(self):
        self.assertEqual(initial_context(1), ())
        self.assertEqual(update_context((), 1, 1), ())
        self.assertEqual(initial_context(2), (START,))
        self.assertEqual(update_context((START,), 1, 2), (1,))
        self.assertEqual(initial_context(3), (START, START))
        self.assertEqual(update_context((START, 0), 1, 3), (0, 1))

    def test_order_m_matches_bruteforce_for_m_1_2_3_and_m_greater_than_T(self):
        labels = (0, 1)
        cases = [(1, 4), (2, 4), (3, 4), (4, 2)]
        for m, T in cases:
            with self.subTest(m=m, T=T):
                phi_fns = make_context_phi_fns(T, labels)
                G_fns = phi_to_G(phi_fns)
                dfa = make_parity_monitor(labels)

                def score(seq):
                    return context_order_m_score(seq, m, phi_fns)

                brute = event_partition_bruteforce(labels, T, score, dfa.accepts)
                transfer = event_partition_transfer_context_order_m(labels, T, m, G_fns, dfa)
                self.assertAlmostEqual(transfer, brute)

    def test_context_path_score_factorization(self):
        labels = (0, 1)
        T = 3
        m = 3
        phi_fns = make_context_phi_fns(T, labels)
        G_fns = phi_to_G(phi_fns)
        for seq in enumerate_label_sequences(labels, T):
            score = context_order_m_score(seq, m, phi_fns)
            context = initial_context(m)
            product_value = 1.0
            for label, G_t in zip(seq, G_fns):
                product_value *= G_t(context, label)
                context = update_context(context, label, m)
            self.assertAlmostEqual(product_value, __import__("math").exp(score))


if __name__ == "__main__":
    unittest.main()

