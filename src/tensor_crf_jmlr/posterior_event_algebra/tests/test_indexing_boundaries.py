from __future__ import annotations

import unittest

from tensor_crf_jmlr.posterior_event_algebra.indexing import (
    CONTEXT_ORDER_M,
    FIRST_ORDER_REDUCED,
    identity_matrix,
    transfer_index_set,
    validate_convention,
)


class IndexingBoundaryTests(unittest.TestCase):
    def test_transfer_index_sets(self):
        self.assertEqual(transfer_index_set(CONTEXT_ORDER_M, 1), (1,))
        self.assertEqual(transfer_index_set(CONTEXT_ORDER_M, 3), (1, 2, 3))
        self.assertEqual(transfer_index_set(FIRST_ORDER_REDUCED, 1), ())
        self.assertEqual(transfer_index_set(FIRST_ORDER_REDUCED, 4), (2, 3, 4))

    def test_context_order_m_rejects_scored_initial_or_missing_M1(self):
        with self.assertRaises(ValueError):
            validate_convention(CONTEXT_ORDER_M, 2, uses_scored_initial=True, includes_M1=True)
        with self.assertRaises(ValueError):
            validate_convention(CONTEXT_ORDER_M, 2, uses_scored_initial=False, includes_M1=False)

    def test_first_order_reduced_rejects_missing_scored_initial_or_M1(self):
        with self.assertRaises(ValueError):
            validate_convention(FIRST_ORDER_REDUCED, 2, uses_scored_initial=False, includes_M1=False)
        with self.assertRaises(ValueError):
            validate_convention(FIRST_ORDER_REDUCED, 2, uses_scored_initial=True, includes_M1=True)

    def test_empty_product_identity_dimension(self):
        self.assertEqual(identity_matrix(3), [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])


if __name__ == "__main__":
    unittest.main()

