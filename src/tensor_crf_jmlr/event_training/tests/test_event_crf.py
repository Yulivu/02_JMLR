from __future__ import annotations

import unittest

import torch

from tensor_crf_jmlr.event_training.bio_event import (
    bio_sequence_allowed,
    bio_start_allowed,
    bio_transition_allowed,
    extract_strict_bio_spans,
)
from tensor_crf_jmlr.event_training.constrained_product_baseline import (
    constrained_product_viterbi_model,
    make_bio_dfa,
)
from tensor_crf_jmlr.event_training.data_utils import SequenceDataset, filter_dataset_by_length, normalize_bio_dataset
from tensor_crf_jmlr.event_training.event_crf import TinyLinearChainCRF
from tensor_crf_jmlr.event_training.formal_validation_runner import (
    FormatTask,
    constrained_viterbi_format as constrained_viterbi_pattern,
    labels_follow_pattern,
    log_event_probability_format,
    log_event_partition_format,
    make_format_dataset,
)
from tensor_crf_jmlr.event_training.semi_real_format_probe import (
    TASKS as SEMI_REAL_TASKS,
    VariantConfig,
    labels_follow_pattern as semi_real_labels_follow_pattern,
    log_event_probability as semi_real_log_event_probability,
    make_dataset as make_semi_real_dataset,
    train_model as train_semi_real_model,
    viterbi as semi_real_viterbi,
)
from tensor_crf_jmlr.event_training.wnut17_bio_probe import (
    entity_counts,
    f1_from_counts,
    log_event_probability_bio as wnut_log_event_probability_bio,
    viterbi as wnut_viterbi,
)


class EventCRFTests(unittest.TestCase):
    def test_bio_accept_reject_examples(self):
        self.assertTrue(bio_start_allowed("O"))
        self.assertTrue(bio_start_allowed("B-PER"))
        self.assertFalse(bio_start_allowed("I-PER"))
        self.assertTrue(bio_transition_allowed("B-PER", "I-PER"))
        self.assertTrue(bio_transition_allowed("I-PER", "I-PER"))
        self.assertFalse(bio_transition_allowed("O", "I-PER"))
        self.assertFalse(bio_transition_allowed("B-ORG", "I-PER"))
        self.assertTrue(bio_sequence_allowed(["B-PER", "I-PER", "O"]))
        self.assertFalse(bio_sequence_allowed(["O", "I-PER"]))

    def test_log_event_partition_matches_bruteforce(self):
        torch.manual_seed(7)
        model = TinyLinearChainCRF(vocab_size=5, label_names=("O", "B-X", "I-X")).double()
        emissions = torch.randn(3, 3, dtype=torch.double) * 0.2
        transfer = model.log_event_partition_bio(emissions)
        brute = model.brute_force_log_event_partition_bio(emissions)
        self.assertAlmostEqual(float(transfer.detach().item()), brute, places=8)

    def test_event_probability_boundary(self):
        torch.manual_seed(8)
        model = TinyLinearChainCRF(vocab_size=5, label_names=("O", "B-X", "I-X"))
        p_event = torch.exp(model.log_event_probability_bio([2, 3, 4]))
        self.assertGreaterEqual(float(p_event.item()), 0.0)
        self.assertLessEqual(float(p_event.item()), 1.0)

    def test_path_probability_boundary(self):
        torch.manual_seed(10)
        model = TinyLinearChainCRF(vocab_size=5, label_names=("O", "B-X", "I-X"))
        p_path = torch.exp(model.log_path_probability([2, 3, 4], [1, 2, 0]))
        self.assertGreaterEqual(float(p_path.item()), 0.0)
        self.assertLessEqual(float(p_path.item()), 1.0)

    def test_event_regularized_loss_has_finite_gradients(self):
        torch.manual_seed(9)
        model = TinyLinearChainCRF(vocab_size=5, label_names=("O", "B-X", "I-X"))
        loss = model.event_regularized_loss([2, 3, 4], [1, 2, 0], lam=0.5)
        self.assertTrue(torch.isfinite(loss))
        loss.backward()
        total_grad = 0.0
        for param in model.parameters():
            self.assertIsNotNone(param.grad)
            self.assertTrue(torch.all(torch.isfinite(param.grad)))
            total_grad += float(param.grad.abs().sum().item())
        self.assertGreater(total_grad, 0.0)

    def test_event_loss_gradient_penalizes_illegal_bio_features(self):
        model = TinyLinearChainCRF(
            vocab_size=8,
            label_names=("O", "B-X", "I-X", "B-Y", "I-Y"),
        ).double()
        with torch.no_grad():
            model.emissions.weight.zero_()
            model.start.zero_()
            model.transitions.zero_()

        loss = -model.log_event_probability_bio([1, 2, 3, 4])
        self.assertTrue(torch.isfinite(loss))
        loss.backward()

        start_grad = model.start.grad.detach()
        transition_grad = model.transitions.grad.detach()
        label_names = model.label_names
        illegal_start_grads = [
            float(start_grad[idx].item())
            for idx, label in enumerate(label_names)
            if not bio_start_allowed(label)
        ]
        illegal_transition_grads = [
            float(transition_grad[prev_idx, curr_idx].item())
            for prev_idx, prev_label in enumerate(label_names)
            for curr_idx, curr_label in enumerate(label_names)
            if not bio_transition_allowed(prev_label, curr_label)
        ]
        legal_transition_grads = [
            float(transition_grad[prev_idx, curr_idx].item())
            for prev_idx, prev_label in enumerate(label_names)
            for curr_idx, curr_label in enumerate(label_names)
            if bio_transition_allowed(prev_label, curr_label)
        ]

        self.assertGreater(min(illegal_start_grads), 0.0)
        self.assertGreater(min(illegal_transition_grads), 0.0)
        self.assertTrue(any(grad < 0.0 for grad in legal_transition_grads))

    def test_cpu_only_guard(self):
        model = TinyLinearChainCRF(vocab_size=5, label_names=("O", "B-X", "I-X"))
        model.assert_cpu_only()
        self.assertEqual({p.device.type for p in model.parameters()}, {"cpu"})

    def test_strict_bio_span_extraction(self):
        labels = ["O", "B-PER", "I-PER", "O", "I-ORG", "B-LOC", "I-LOC"]
        spans = extract_strict_bio_spans(labels)
        self.assertEqual(spans, {(1, 3, "PER"), (5, 7, "LOC")})

    def test_bio_dataset_normalization_and_length_filter(self):
        dataset = SequenceDataset(
            "toy",
            tokens=[["John", "Smith"], ["OpenAI", "hi", "!"]],
            labels=[["B-person", "I-person"], ["B-corporation", "O", "O"]],
        )
        normalized = normalize_bio_dataset(dataset)
        self.assertEqual(normalized.labels[0], ["B-PERSON", "I-PERSON"])
        filtered = filter_dataset_by_length(normalized, max_len=2)
        self.assertEqual(filtered.tokens, [["John", "Smith"]])

    def test_wnut_entity_count_helpers(self):
        pred = ["B-PER", "I-PER", "O", "B-LOC"]
        gold = ["B-PER", "I-PER", "O", "B-ORG"]
        true_positive, predicted, gold_total = entity_counts(pred, gold)
        self.assertEqual((true_positive, predicted, gold_total), (1, 2, 2))
        self.assertAlmostEqual(f1_from_counts(true_positive, predicted, gold_total), 0.5)

    def test_wnut_rule_bias_helpers_have_valid_boundaries(self):
        model = TinyLinearChainCRF(vocab_size=8, label_names=("O", "B-X", "I-X"))
        word_ids = [1, 2, 3]
        p_event = torch.exp(wnut_log_event_probability_bio(model, word_ids, rule_bias=0.8))
        self.assertGreaterEqual(float(p_event.item()), 0.0)
        self.assertLessEqual(float(p_event.item()), 1.0)
        path, _score = wnut_viterbi(model, word_ids, constrained=True, rule_bias=0.8)
        labels = [model.label_names[idx] for idx in path]
        self.assertTrue(bio_sequence_allowed(labels))

    def test_b7_bio_dfa_matches_bio_utility(self):
        label_names = ("O", "B-X", "I-X", "B-Y", "I-Y")
        dfa = make_bio_dfa(label_names)
        for labels in (("O", "B-X", "I-X"), ("B-Y", "O", "B-X"), ("I-X",), ("O", "I-Y")):
            ids = [label_names.index(label) for label in labels]
            self.assertEqual(dfa.accepts(ids), bio_sequence_allowed(labels))

    def test_b7_constrained_product_viterbi_returns_legal_path(self):
        model = TinyLinearChainCRF(vocab_size=4, label_names=("O", "B-X", "I-X"))
        with torch.no_grad():
            model.emissions.weight.zero_()
            model.start[:] = torch.tensor([0.0, -2.0, 3.0])
            model.transitions.zero_()
        dfa = make_bio_dfa(model.label_names)
        path, _score = constrained_product_viterbi_model(model, [1, 2], dfa)
        labels = [model.label_names[idx] for idx in path]
        self.assertTrue(bio_sequence_allowed(labels))

    def test_non_bio_format_event_helpers(self):
        torch.manual_seed(11)
        task = FormatTask("LLDDD", ("L", "L", "D", "D", "D"), "test pattern")
        model = TinyLinearChainCRF(vocab_size=8, label_names=task.label_names)
        log_p = log_event_probability_format(model, task, [1, 2, 3, 4, 5])
        p_event = torch.exp(log_p)
        self.assertGreaterEqual(float(p_event.item()), 0.0)
        self.assertLessEqual(float(p_event.item()), 1.0)
        constrained_path, _score = constrained_viterbi_pattern(model, task, [1, 2, 3, 4, 5])
        self.assertTrue(labels_follow_pattern(task, model.label_names, constrained_path))

    def test_formal_validation_dataset_follows_pattern(self):
        task = FormatTask("LL-D", ("L", "L", "-", "D"), "test pattern")
        dataset = make_format_dataset(task, "toy", 20, seed=123)
        label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
        for labels in dataset.labels:
            path = [label_to_idx[label] for label in labels]
            self.assertTrue(labels_follow_pattern(task, task.label_names, path))

    def test_formal_validation_log_event_partition_matches_bruteforce(self):
        torch.manual_seed(12)
        task = FormatTask("LD", ("L", "D"), "test pattern")
        model = TinyLinearChainCRF(vocab_size=4, label_names=task.label_names).double()
        emissions = torch.randn(task.length, len(task.label_names), dtype=torch.double) * 0.2
        transfer = log_event_partition_format(model, task, [1, 2])
        with torch.no_grad():
            model.emissions.weight[1] = emissions[0]
            model.emissions.weight[2] = emissions[1]
        transfer = log_event_partition_format(model, task, [1, 2])
        total = 0.0
        for first_idx, first_label in enumerate(model.label_names):
            for second_idx, second_label in enumerate(model.label_names):
                if first_label in {"O", "I", "B", "S", "Z", "A"} and second_label in {"0", "1", "8", "5", "2", "3"}:
                    score = model.path_score(model.emission_scores([1, 2]), [first_idx, second_idx])
                    total += float(torch.exp(score).detach().item())
        brute = torch.log(torch.tensor(total, dtype=torch.double))
        self.assertAlmostEqual(float(transfer.detach().item()), float(brute.item()), places=8)

    def test_formal_validation_constrained_viterbi_follows_pattern(self):
        torch.manual_seed(13)
        task = FormatTask("DDDLL", ("D", "D", "D", "L", "L"), "test pattern")
        model = TinyLinearChainCRF(vocab_size=8, label_names=task.label_names)
        path, _score = constrained_viterbi_pattern(model, task, [1, 2, 3, 4, 5])
        self.assertTrue(labels_follow_pattern(task, model.label_names, path))

    def test_semi_real_dataset_and_event_probability_boundary(self):
        task = next(task for task in SEMI_REAL_TASKS if task.name == "amount")
        dataset = make_semi_real_dataset(task, "toy_amount", 5, seed=21)
        self.assertEqual(len(dataset.tokens[0]), task.length)
        label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
        model = TinyLinearChainCRF(vocab_size=32, label_names=task.label_names)
        word_ids = list(range(1, task.length + 1))
        p_event = torch.exp(semi_real_log_event_probability(model, task, word_ids))
        self.assertGreaterEqual(float(p_event.item()), 0.0)
        self.assertLessEqual(float(p_event.item()), 1.0)
        path = [label_to_idx[label] for label in dataset.labels[0]]
        self.assertTrue(semi_real_labels_follow_pattern(task, task.label_names, path))

    def test_semi_real_rule_feature_constrained_viterbi(self):
        task = next(task for task in SEMI_REAL_TASKS if task.name == "dose")
        model = TinyLinearChainCRF(vocab_size=16, label_names=task.label_names)
        path, _score = semi_real_viterbi(model, task, [1, 2, 3, 4, 5], constrained=True)
        self.assertTrue(semi_real_labels_follow_pattern(task, model.label_names, path))

    def test_semi_real_training_smoke_cpu_only(self):
        task = next(task for task in SEMI_REAL_TASKS if task.name == "product_code")
        label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
        dataset = make_semi_real_dataset(task, "toy_product", 3, seed=22)
        vocab = {"<UNK>": 0}
        for seq in dataset.tokens:
            for token in seq:
                vocab.setdefault(token, len(vocab))
        labeled = [
            ([vocab[token] for token in tokens], [label_to_idx[label] for label in labels])
            for tokens, labels in zip(dataset.tokens, dataset.labels)
        ]
        model = train_semi_real_model(
            task,
            labeled,
            [],
            len(vocab),
            variant=VariantConfig("smoke", "semi_event", labeled_lam=0.1),
            seed=23,
            epochs=1,
            lr=0.01,
        )
        model.assert_cpu_only()


if __name__ == "__main__":
    unittest.main()

