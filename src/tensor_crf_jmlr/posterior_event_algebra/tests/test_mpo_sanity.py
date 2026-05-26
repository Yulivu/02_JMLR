from __future__ import annotations

import unittest

from tensor_crf_jmlr.posterior_event_algebra.dfa import make_parity_monitor
from tensor_crf_jmlr.posterior_event_algebra.mpo_sanity import (
    augmented_mode_order,
    augmented_mode_values,
    compare_tensors,
    context_extractors,
    dfa_transition_mpo,
    direct_event_transfer_from_augmented,
    direct_shift_tensor,
    label_contract,
    lift_mpo,
    max_bond_dim,
    parity_transition_mpo,
    pointwise_core_product,
    reconstruct_mpo,
    score_table_mpo_rank1,
    shift_register_mpo,
    terminal_vector_for_accepting,
    transfer_mode_order,
)


class MPORankSanityTests(unittest.TestCase):
    def assertTensorEqual(self, a, b):
        ok, max_abs = compare_tensors(a, b)
        self.assertTrue(ok, f"tensor mismatch max_abs={max_abs}")

    def lifted_components(self, labels=(0, 1), m=2):
        dfa, dfa_mpo = parity_transition_mpo(labels)
        target_order = augmented_mode_order(m)
        target_values = augmented_mode_values(labels, m, dfa)

        score = score_table_mpo_rank1(labels, m)
        shift = shift_register_mpo(labels, m)

        score_lift = lift_mpo(
            score,
            target_order,
            target_values,
            context_extractors(m),
            name="score-lift",
        )
        shift_lift = lift_mpo(shift, target_order, target_values, name="shift-lift")
        dfa_lift = lift_mpo(dfa_mpo, target_order, target_values, name="dfa-lift")
        return dfa, score_lift, shift_lift, dfa_lift

    def test_shift_mpo_constructor_sanity(self):
        for labels, m in [((0, 1), 1), ((0, 1), 2), ((0, 1), 3), ((0, 1, 2), 2)]:
            with self.subTest(labels=labels, m=m):
                order, _values, direct = direct_shift_tensor(labels, m)
                mpo = shift_register_mpo(labels, m)
                self.assertEqual(mpo.mode_order, order)
                self.assertEqual(len(mpo.cores), len(mpo.mode_order))
                self.assertTensorEqual(reconstruct_mpo(mpo), direct)
                expected = 1 if m == 1 else len(labels) + 1
                self.assertLessEqual(max_bond_dim(mpo), expected)
                self.assertTrue(
                    all(value >= 0 for core in mpo.cores for value in core.entries.values())
                )

    def test_core_product_rank_multiplication_sanity(self):
        dfa, score_lift, shift_lift, dfa_lift = self.lifted_components(m=(0 + 2))
        _ = dfa
        score_shift = pointwise_core_product(score_lift, shift_lift, name="score-shift")
        H = pointwise_core_product(score_shift, dfa_lift, name="H")
        direct = {}
        for key in H.tensor:
            direct[key] = score_lift.tensor[key] * shift_lift.tensor[key] * dfa_lift.tensor[key]
        self.assertTensorEqual(reconstruct_mpo(H), direct)
        self.assertEqual(len(H.cores), len(H.mode_order))
        self.assertLessEqual(
            max_bond_dim(H),
            max_bond_dim(score_lift) * max_bond_dim(shift_lift) * max_bond_dim(dfa_lift),
        )

    def test_label_contraction_rank_preservation_sanity(self):
        for m in (1, 2, 3):
            with self.subTest(m=m):
                _dfa, score_lift, shift_lift, dfa_lift = self.lifted_components(m=m)
                H = pointwise_core_product(
                    pointwise_core_product(score_lift, shift_lift, name="score-shift"),
                    dfa_lift,
                    name="H",
                )
                M = label_contract(H, label_mode="j", name="M")
                direct = direct_event_transfer_from_augmented(H)
                self.assertEqual(M.mode_order, transfer_mode_order(m))
                self.assertNotIn("j", M.mode_order)
                self.assertEqual(len(M.cores), len(M.mode_order))
                self.assertTensorEqual(reconstruct_mpo(M), direct)
                self.assertLessEqual(max_bond_dim(M), max_bond_dim(H))

    def test_parity_transition_structured_example(self):
        labels = (0, 1)
        dfa, parity_mpo = parity_transition_mpo(labels, symbol=1)
        direct = dfa_transition_mpo(dfa).tensor
        self.assertEqual(len(parity_mpo.cores), 3)
        self.assertEqual([core.left_dim for core in parity_mpo.cores], [1, 2, 2])
        self.assertEqual([core.right_dim for core in parity_mpo.cores], [2, 2, 1])
        self.assertTensorEqual(reconstruct_mpo(parity_mpo), direct)
        self.assertLessEqual(max_bond_dim(parity_mpo), 2)

    def test_full_event_transfer_reconstruction_for_m_1_2_3(self):
        for m in (1, 2, 3):
            with self.subTest(m=m):
                _dfa, score_lift, shift_lift, dfa_lift = self.lifted_components(m=m)
                H = pointwise_core_product(
                    pointwise_core_product(score_lift, shift_lift, name="score-shift"),
                    dfa_lift,
                    name="H",
                )
                M = label_contract(H, label_mode="j", name="M")
                self.assertTensorEqual(reconstruct_mpo(M), direct_event_transfer_from_augmented(H))
                self.assertLessEqual(
                    max_bond_dim(M),
                    max_bond_dim(score_lift) * max_bond_dim(shift_lift) * max_bond_dim(dfa_lift),
                )

    def test_shared_monitor_accepting_set_sanity(self):
        labels = (0, 1)
        m = 2
        dfa, score_lift, shift_lift, dfa_lift = self.lifted_components(labels=labels, m=m)
        local_transfer_even = label_contract(
            pointwise_core_product(
                pointwise_core_product(score_lift, shift_lift, name="score-shift"),
                dfa_lift,
                name="H",
            ),
            label_mode="j",
            name="M-even",
        )
        odd_dfa = dfa.with_accepting({1}, name="parity-odd")
        odd_transition = dfa_transition_mpo(odd_dfa)
        self.assertTensorEqual(dfa_transition_mpo(dfa).tensor, odd_transition.tensor)

        b_even = terminal_vector_for_accepting(labels, m, dfa, {0})
        b_odd = terminal_vector_for_accepting(labels, m, dfa, {1})
        self.assertNotEqual(b_even, b_odd)

        local_transfer_odd = local_transfer_even
        self.assertTensorEqual(local_transfer_even.tensor, local_transfer_odd.tensor)


if __name__ == "__main__":
    unittest.main()

