from __future__ import annotations

import math
import unittest

from tensor_crf_jmlr.posterior_event_algebra.dfa import make_accept_all_dfa, make_empty_language_dfa, make_exact_pattern_dfa
from tensor_crf_jmlr.posterior_event_algebra.posterior_algebra import (
    event_partition_bruteforce,
    event_probability_bruteforce,
    partition_bruteforce,
    restricted_distribution,
)


class PosteriorAlgebraTests(unittest.TestCase):
    def setUp(self):
        self.labels = (0, 1)
        self.T = 3

        def score(seq):
            return sum(0.2 * (pos + 1) * (label + 1) for pos, label in enumerate(seq))

        self.score = score

    def test_partition_is_finite_positive(self):
        Z = partition_bruteforce(self.labels, self.T, self.score)
        self.assertTrue(math.isfinite(Z))
        self.assertGreater(Z, 0.0)

    def test_empty_language_has_zero_event_mass(self):
        dfa = make_empty_language_dfa(self.labels)
        Z_L = event_partition_bruteforce(self.labels, self.T, self.score, dfa.accepts)
        result = event_probability_bruteforce(self.labels, self.T, self.score, dfa.accepts)
        self.assertEqual(Z_L, 0.0)
        self.assertEqual(result["Z_L"], 0.0)
        self.assertEqual(result["P_L"], 0.0)
        self.assertEqual(result["status"], "zero_event")
        self.assertEqual(restricted_distribution(self.labels, self.T, self.score, dfa.accepts), {"status": "zero_event"})

    def test_accept_all_recovers_partition(self):
        dfa = make_accept_all_dfa(self.labels)
        Z = partition_bruteforce(self.labels, self.T, self.score)
        result = event_probability_bruteforce(self.labels, self.T, self.score, dfa.accepts)
        self.assertAlmostEqual(result["Z_L"], Z)
        self.assertAlmostEqual(result["P_L"], 1.0)

    def test_singleton_event_matches_manual_weight(self):
        pattern = (1, 0, 1)
        dfa = make_exact_pattern_dfa(self.labels, pattern)
        Z_L = event_partition_bruteforce(self.labels, self.T, self.score, dfa.accepts)
        self.assertAlmostEqual(Z_L, math.exp(self.score(pattern)))

    def test_restricted_distribution_normalizes_when_positive(self):
        dfa = make_exact_pattern_dfa(self.labels, (1, 0, 1))
        dist = restricted_distribution(self.labels, self.T, self.score, dfa.accepts)
        self.assertNotIn("status", dist)
        self.assertAlmostEqual(sum(dist.values()), 1.0)

    def test_low_probability_positive_event_has_positive_mass(self):
        T = 4

        def low_score(seq):
            return sum(-18.0 if label == 1 else 0.0 for label in seq)

        dfa = make_exact_pattern_dfa(self.labels, (0, 0, 0, 1))
        result = event_probability_bruteforce(self.labels, T, low_score, dfa.accepts)
        self.assertGreater(result["Z_L"], 0.0)
        self.assertGreater(result["P_L"], 0.0)
        self.assertLess(result["P_L"], 1e-6)


if __name__ == "__main__":
    unittest.main()

