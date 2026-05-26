"""Tiny CPU-only linear-chain CRF with BIO event posterior mass."""

from __future__ import annotations

from itertools import product
from math import exp, log
from typing import Sequence

import torch
from torch import nn

from .bio_event import NEG_INF, bio_sequence_allowed, make_bio_masks


def _as_bool_tensor(values: Sequence[bool], device: torch.device) -> torch.Tensor:
    return torch.tensor(values, dtype=torch.bool, device=device)


class TinyLinearChainCRF(nn.Module):
    """Minimal linear-chain CRF for local event-training probes."""

    def __init__(self, vocab_size: int, label_names: Sequence[str]):
        super().__init__()
        self.label_names = tuple(label_names)
        self.num_labels = len(self.label_names)
        self.emissions = nn.Embedding(vocab_size, self.num_labels)
        self.start = nn.Parameter(torch.zeros(self.num_labels))
        self.transitions = nn.Parameter(torch.zeros(self.num_labels, self.num_labels))
        try:
            start_allowed, transition_allowed = make_bio_masks(self.label_names)
        except ValueError:
            start_allowed = [True] * self.num_labels
            transition_allowed = [[True] * self.num_labels for _ in range(self.num_labels)]
        self.register_buffer("_bio_start_allowed", torch.tensor(start_allowed, dtype=torch.bool))
        self.register_buffer(
            "_bio_transition_allowed", torch.tensor(transition_allowed, dtype=torch.bool)
        )
        self.reset_parameters()

    def reset_parameters(self) -> None:
        nn.init.normal_(self.emissions.weight, mean=0.0, std=0.05)
        nn.init.normal_(self.start, mean=0.0, std=0.02)
        nn.init.normal_(self.transitions, mean=0.0, std=0.02)

    def assert_cpu_only(self) -> None:
        devices = {param.device.type for param in self.parameters()}
        if devices != {"cpu"}:
            raise RuntimeError(f"probe must remain CPU-only, got devices={devices}")

    def emission_scores(self, word_ids: Sequence[int] | torch.Tensor) -> torch.Tensor:
        if not isinstance(word_ids, torch.Tensor):
            word_ids = torch.tensor(word_ids, dtype=torch.long)
        return self.emissions(word_ids.to(self.emissions.weight.device))

    def path_score(self, emissions: torch.Tensor, label_ids: Sequence[int] | torch.Tensor) -> torch.Tensor:
        if not isinstance(label_ids, torch.Tensor):
            label_ids = torch.tensor(label_ids, dtype=torch.long, device=emissions.device)
        labels = label_ids.to(emissions.device)
        if labels.numel() == 0:
            return torch.tensor(0.0, device=emissions.device)
        score = self.start[labels[0]] + emissions[0, labels[0]]
        for pos in range(1, labels.numel()):
            score = score + self.transitions[labels[pos - 1], labels[pos]] + emissions[pos, labels[pos]]
        return score

    def log_partition(self, emissions: torch.Tensor) -> torch.Tensor:
        if emissions.shape[0] == 0:
            return torch.tensor(0.0, device=emissions.device)
        alpha = self.start + emissions[0]
        for pos in range(1, emissions.shape[0]):
            scores = alpha[:, None] + self.transitions + emissions[pos][None, :]
            alpha = torch.logsumexp(scores, dim=0)
        return torch.logsumexp(alpha, dim=0)

    def log_event_partition_bio(self, emissions: torch.Tensor) -> torch.Tensor:
        if emissions.shape[0] == 0:
            return torch.tensor(0.0, device=emissions.device)
        start_mask = self._bio_start_allowed.to(emissions.device)
        transition_mask = self._bio_transition_allowed.to(emissions.device)
        alpha = self.start + emissions[0]
        alpha = torch.where(start_mask, alpha, torch.full_like(alpha, NEG_INF))
        for pos in range(1, emissions.shape[0]):
            scores = alpha[:, None] + self.transitions + emissions[pos][None, :]
            scores = torch.where(transition_mask, scores, torch.full_like(scores, NEG_INF))
            alpha = torch.logsumexp(scores, dim=0)
        return torch.logsumexp(alpha, dim=0)

    def log_event_probability_bio(self, word_ids: Sequence[int] | torch.Tensor) -> torch.Tensor:
        emissions = self.emission_scores(word_ids)
        return self.log_event_partition_bio(emissions) - self.log_partition(emissions)

    def neg_log_likelihood(self, word_ids: Sequence[int], label_ids: Sequence[int]) -> torch.Tensor:
        emissions = self.emission_scores(word_ids)
        return self.log_partition(emissions) - self.path_score(emissions, label_ids)

    def log_path_probability(
        self,
        word_ids: Sequence[int],
        label_ids: Sequence[int],
    ) -> torch.Tensor:
        emissions = self.emission_scores(word_ids)
        return self.path_score(emissions, label_ids) - self.log_partition(emissions)

    def event_regularized_loss(
        self,
        word_ids: Sequence[int],
        label_ids: Sequence[int],
        lam: float,
    ) -> torch.Tensor:
        nll = self.neg_log_likelihood(word_ids, label_ids)
        log_p_event = self.log_event_probability_bio(word_ids)
        return nll - lam * log_p_event

    def viterbi(self, word_ids: Sequence[int], *, constrained: bool = False) -> tuple[list[int], float]:
        emissions = self.emission_scores(word_ids)
        if emissions.shape[0] == 0:
            return [], 0.0
        start = self.start
        transitions = self.transitions
        if constrained:
            start_mask = self._bio_start_allowed.to(emissions.device)
            transition_mask = self._bio_transition_allowed.to(emissions.device)
            alpha = torch.where(start_mask, start + emissions[0], torch.full_like(start, NEG_INF))
        else:
            transition_mask = None
            alpha = start + emissions[0]
        backpointers: list[list[int]] = []
        for pos in range(1, emissions.shape[0]):
            scores = alpha[:, None] + transitions + emissions[pos][None, :]
            if constrained:
                scores = torch.where(transition_mask, scores, torch.full_like(scores, NEG_INF))
            best_scores, best_prev = torch.max(scores, dim=0)
            alpha = best_scores
            backpointers.append(best_prev.tolist())
        best_last = int(torch.argmax(alpha).item())
        best_score = float(alpha[best_last].detach().cpu().item())
        path = [best_last]
        for prev_for_next in reversed(backpointers):
            path.append(prev_for_next[path[-1]])
        path.reverse()
        return path, best_score

    def brute_force_log_event_partition_bio(self, emissions: torch.Tensor) -> float:
        total = 0.0
        for path in product(range(self.num_labels), repeat=emissions.shape[0]):
            label_names = [self.label_names[idx] for idx in path]
            if bio_sequence_allowed(label_names):
                total += exp(float(self.path_score(emissions, path).detach().cpu().item()))
        return log(total)

    def legal_path_distribution(
        self,
        word_ids: Sequence[int],
        *,
        top_k: int | None = None,
    ) -> list[tuple[tuple[str, ...], float]]:
        emissions = self.emission_scores(word_ids)
        log_z = float(self.log_partition(emissions).detach().cpu().item())
        paths: list[tuple[tuple[str, ...], float]] = []
        for path in product(range(self.num_labels), repeat=emissions.shape[0]):
            label_names = tuple(self.label_names[idx] for idx in path)
            if not bio_sequence_allowed(label_names):
                continue
            score = float(self.path_score(emissions, path).detach().cpu().item())
            paths.append((label_names, exp(score - log_z)))
        paths.sort(key=lambda item: item[1], reverse=True)
        return paths[:top_k] if top_k is not None else paths

