"""Semi-real format extraction probes for posterior event training.

This file intentionally stays small and CPU-only.  The data are generated from
realistic form-field formats with OCR-like ambiguity, but they are still local
controlled probes, not benchmarks.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import asdict, dataclass
from math import sqrt
from pathlib import Path
from statistics import mean, stdev
from typing import Sequence

import torch

from .event_crf import TinyLinearChainCRF
from .run_probe import set_seed


LETTERS = ("O", "I", "B", "S", "Z", "A", "C", "D")
DIGITS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
ALL_LITERALS = ("-", ".", "$", "/", "m", "g")
ALL_LABELS = LETTERS + DIGITS + ALL_LITERALS

GROUP_TO_LABELS = {
    "L": LETTERS,
    "D": DIGITS,
    "-": ("-",),
    ".": (".",),
    "$": ("$",),
    "/": ("/",),
    "m": ("m",),
    "g": ("g",),
}

OBSERVATION_ALIASES = {
    "O": ("O0", "O", "0"),
    "0": ("O0", "0", "O"),
    "I": ("I1", "I", "1"),
    "1": ("I1", "1", "I"),
    "B": ("B8", "B", "8"),
    "8": ("B8", "8", "B"),
    "S": ("S5", "S", "5"),
    "5": ("S5", "5", "S"),
    "Z": ("Z2", "Z", "2"),
    "2": ("Z2", "2", "Z"),
    "3": ("3", "8"),
    "4": ("4A", "4"),
    "6": ("6G", "6"),
    "7": ("7T", "7"),
    "9": ("9g", "9"),
    "A": ("A4", "A"),
    "C": ("C", "G"),
    "D": ("D0", "D"),
    "-": ("-", "dash", "_"),
    ".": (".", "dot", ","),
    "$": ("$", "S$", "5$"),
    "/": ("/", "slash"),
    "m": ("m", "rn", "n"),
    "g": ("g", "9g", "q"),
}


@dataclass(frozen=True)
class SemiRealTask:
    name: str
    pattern: tuple[str, ...]
    description: str

    @property
    def length(self) -> int:
        return len(self.pattern)

    @property
    def label_names(self) -> tuple[str, ...]:
        labels: list[str] = []
        for group in self.pattern:
            for label in GROUP_TO_LABELS[group]:
                if label not in labels:
                    labels.append(label)
        for label in ALL_LABELS:
            if label not in labels:
                labels.append(label)
        return tuple(labels)

    @property
    def pattern_string(self) -> str:
        return "".join(self.pattern)


@dataclass(frozen=True)
class SequenceDataset:
    name: str
    tokens: list[list[str]]
    labels: list[list[str]]


@dataclass(frozen=True)
class ProbeSetting:
    block: str
    name: str
    labeled_size: int
    unlabeled_size: int
    dev_size: int
    epochs: int
    lr: float
    seeds: tuple[int, ...]
    variants: tuple[str, ...]


@dataclass(frozen=True)
class VariantConfig:
    name: str
    kind: str
    labeled_lam: float = 0.0
    unlabeled_lam: float = 0.0
    pr_eta: float = 0.0
    pr_tau: float = 0.8
    rule_bias: float = 0.0


@dataclass
class ProbeRun:
    block: str
    task: str
    pattern: str
    setting: str
    variant: str
    seed: int
    labeled_size: int
    unlabeled_size: int
    dev_size: int
    epochs: int
    lr: float
    mean_p_event: float
    mean_illegal_mass: float
    low_p_event_rate: float
    unconstrained_event_rate: float
    constrained_event_rate: float
    char_accuracy: float
    constrained_char_accuracy: float
    exact_sequence_accuracy: float
    constrained_exact_sequence_accuracy: float
    mean_nll: float
    hidden_conflict_rate: float
    notes: str


@dataclass
class CaseStudy:
    task: str
    seed: int
    tokens: str
    gold: str
    baseline_pred: str
    baseline_constrained_pred: str
    event_pred: str
    event_constrained_pred: str
    baseline_p_event: float
    event_p_event: float
    comment: str


TASKS = (
    SemiRealTask("product_code", ("L", "L", "-", "D", "D", "D"), "product or invoice code"),
    SemiRealTask("amount", ("$", "D", "D", ".", "D", "D"), "currency amount field"),
    SemiRealTask("date", ("D", "D", "D", "D", "-", "D", "D", "-", "D", "D"), "date-like field"),
    SemiRealTask("dose", ("D", "D", "D", "m", "g"), "medicine dosage-like field"),
)

VARIANTS: dict[str, VariantConfig] = {
    "B0_unconstrained": VariantConfig("B0_unconstrained", "baseline"),
    "B2_event_0.1": VariantConfig("B2_event_0.1", "event", labeled_lam=0.1),
    "B2_event_0.5": VariantConfig("B2_event_0.5", "event", labeled_lam=0.5),
    "B4_semi_event_0.1": VariantConfig("B4_semi_event_0.1", "semi_event", labeled_lam=0.1, unlabeled_lam=0.1),
    "B4_semi_event_0.5": VariantConfig("B4_semi_event_0.5", "semi_event", labeled_lam=0.5, unlabeled_lam=0.5),
    "B5_rule_feature_0.8": VariantConfig("B5_rule_feature_0.8", "rule_feature", rule_bias=0.8),
    "B6_pr_style_tau0.8": VariantConfig(
        "B6_pr_style_tau0.8",
        "posterior_regularization_style",
        pr_eta=1.0,
        pr_tau=0.8,
    ),
}

LAMBDA_VARIANTS: dict[str, VariantConfig] = {
    "B0_unconstrained": VARIANTS["B0_unconstrained"],
    "B4_semi_event_0.05": VariantConfig("B4_semi_event_0.05", "semi_event", labeled_lam=0.05, unlabeled_lam=0.05),
    "B4_semi_event_0.1": VARIANTS["B4_semi_event_0.1"],
    "B4_semi_event_0.2": VariantConfig("B4_semi_event_0.2", "semi_event", labeled_lam=0.2, unlabeled_lam=0.2),
    "B4_semi_event_0.5": VARIANTS["B4_semi_event_0.5"],
    "B4_semi_event_1.0": VariantConfig("B4_semi_event_1.0", "semi_event", labeled_lam=1.0, unlabeled_lam=1.0),
}


def choose_label(group: str, rng: random.Random) -> str:
    if group == "L":
        return rng.choice(("O", "I", "B", "S", "Z", "A", "C", "D", "O", "I", "B", "S", "Z"))
    if group == "D":
        return rng.choice(("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "1", "2", "5", "8"))
    labels = GROUP_TO_LABELS[group]
    return labels[0]


def observe_label(label: str, rng: random.Random) -> str:
    aliases = OBSERVATION_ALIASES[label]
    return rng.choice(aliases)


def make_dataset(task: SemiRealTask, name: str, size: int, *, seed: int) -> SequenceDataset:
    rng = random.Random(seed)
    tokens: list[list[str]] = []
    labels: list[list[str]] = []
    for _ in range(size):
        label_seq = [choose_label(group, rng) for group in task.pattern]
        labels.append(label_seq)
        tokens.append([observe_label(label, rng) for label in label_seq])
    return SequenceDataset(name, tokens, labels)


def build_vocab(sequences: Sequence[Sequence[str]]) -> dict[str, int]:
    vocab = {"<UNK>": 0}
    for seq in sequences:
        for token in seq:
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab


def encode(
    dataset: SequenceDataset,
    vocab: dict[str, int],
    label_to_idx: dict[str, int],
) -> list[tuple[list[int], list[int]]]:
    unk = vocab["<UNK>"]
    return [
        ([vocab.get(token, unk) for token in tokens], [label_to_idx[label] for label in labels])
        for tokens, labels in zip(dataset.tokens, dataset.labels)
    ]


def pattern_masks(task: SemiRealTask, label_names: Sequence[str], device: torch.device) -> list[torch.Tensor]:
    masks: list[torch.Tensor] = []
    for group in task.pattern:
        allowed = set(GROUP_TO_LABELS[group])
        masks.append(torch.tensor([label in allowed for label in label_names], dtype=torch.bool, device=device))
    return masks


def labels_follow_pattern(task: SemiRealTask, label_names: Sequence[str], path: Sequence[int]) -> bool:
    if len(path) != task.length:
        return False
    return all(label_names[idx] in GROUP_TO_LABELS[group] for group, idx in zip(task.pattern, path))


def emission_scores(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    word_ids: Sequence[int],
    *,
    rule_bias: float = 0.0,
) -> torch.Tensor:
    emissions = model.emission_scores(word_ids)
    if rule_bias == 0.0:
        return emissions
    masks = pattern_masks(task, model.label_names, emissions.device)
    bias = torch.stack([mask.to(dtype=emissions.dtype) * rule_bias for mask in masks])
    return emissions + bias


def path_score_from_emissions(
    model: TinyLinearChainCRF,
    emissions: torch.Tensor,
    label_ids: Sequence[int],
) -> torch.Tensor:
    labels = torch.tensor(label_ids, dtype=torch.long, device=emissions.device)
    score = model.start[labels[0]] + emissions[0, labels[0]]
    for pos in range(1, labels.numel()):
        score = score + model.transitions[labels[pos - 1], labels[pos]] + emissions[pos, labels[pos]]
    return score


def log_partition_from_emissions(model: TinyLinearChainCRF, emissions: torch.Tensor) -> torch.Tensor:
    alpha = model.start + emissions[0]
    for pos in range(1, emissions.shape[0]):
        scores = alpha[:, None] + model.transitions + emissions[pos][None, :]
        alpha = torch.logsumexp(scores, dim=0)
    return torch.logsumexp(alpha, dim=0)


def log_event_partition_from_emissions(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    emissions: torch.Tensor,
) -> torch.Tensor:
    masks = pattern_masks(task, model.label_names, emissions.device)
    alpha = torch.where(masks[0], model.start + emissions[0], torch.full_like(model.start, -1e9))
    for pos in range(1, emissions.shape[0]):
        scores = alpha[:, None] + model.transitions + emissions[pos][None, :]
        scores = torch.where(masks[pos][None, :], scores, torch.full_like(scores, -1e9))
        alpha = torch.logsumexp(scores, dim=0)
    return torch.logsumexp(alpha, dim=0)


def log_event_probability(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    word_ids: Sequence[int],
    *,
    rule_bias: float = 0.0,
) -> torch.Tensor:
    emissions = emission_scores(model, task, word_ids, rule_bias=rule_bias)
    return log_event_partition_from_emissions(model, task, emissions) - log_partition_from_emissions(model, emissions)


def nll_loss(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    word_ids: Sequence[int],
    label_ids: Sequence[int],
    *,
    rule_bias: float = 0.0,
) -> torch.Tensor:
    emissions = emission_scores(model, task, word_ids, rule_bias=rule_bias)
    return log_partition_from_emissions(model, emissions) - path_score_from_emissions(model, emissions, label_ids)


def viterbi(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    word_ids: Sequence[int],
    *,
    constrained: bool = False,
    rule_bias: float = 0.0,
) -> tuple[list[int], float]:
    emissions = emission_scores(model, task, word_ids, rule_bias=rule_bias)
    masks = pattern_masks(task, model.label_names, emissions.device)
    if constrained:
        alpha = torch.where(masks[0], model.start + emissions[0], torch.full_like(model.start, -1e9))
    else:
        alpha = model.start + emissions[0]
    backpointers: list[list[int]] = []
    for pos in range(1, emissions.shape[0]):
        scores = alpha[:, None] + model.transitions + emissions[pos][None, :]
        if constrained:
            scores = torch.where(masks[pos][None, :], scores, torch.full_like(scores, -1e9))
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


def event_loss(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    word_ids: Sequence[int],
    *,
    rule_bias: float = 0.0,
) -> torch.Tensor:
    return -log_event_probability(model, task, word_ids, rule_bias=rule_bias)


def pr_style_loss(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    word_ids: Sequence[int],
    *,
    tau: float,
    rule_bias: float = 0.0,
) -> torch.Tensor:
    p_event = torch.exp(log_event_probability(model, task, word_ids, rule_bias=rule_bias))
    return torch.relu(torch.tensor(tau, dtype=p_event.dtype, device=p_event.device) - p_event).pow(2)


def train_model(
    task: SemiRealTask,
    labeled: list[tuple[list[int], list[int]]],
    unlabeled: list[list[int]],
    vocab_size: int,
    *,
    variant: VariantConfig,
    seed: int,
    epochs: int,
    lr: float,
) -> TinyLinearChainCRF:
    set_seed(seed)
    model = TinyLinearChainCRF(vocab_size, task.label_names)
    model.assert_cpu_only()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for _epoch in range(epochs):
        labeled_order = list(range(len(labeled)))
        random.shuffle(labeled_order)
        for idx in labeled_order:
            word_ids, label_ids = labeled[idx]
            optimizer.zero_grad(set_to_none=True)
            loss = nll_loss(model, task, word_ids, label_ids, rule_bias=variant.rule_bias)
            if variant.labeled_lam:
                loss = loss + variant.labeled_lam * event_loss(model, task, word_ids, rule_bias=variant.rule_bias)
            if variant.pr_eta:
                loss = loss + variant.pr_eta * pr_style_loss(
                    model,
                    task,
                    word_ids,
                    tau=variant.pr_tau,
                    rule_bias=variant.rule_bias,
                )
            loss.backward()
            optimizer.step()
        if unlabeled and (variant.unlabeled_lam or variant.pr_eta):
            unlabeled_order = list(range(len(unlabeled)))
            random.shuffle(unlabeled_order)
            for idx in unlabeled_order:
                optimizer.zero_grad(set_to_none=True)
                loss = torch.tensor(0.0)
                if variant.unlabeled_lam:
                    loss = loss + variant.unlabeled_lam * event_loss(
                        model,
                        task,
                        unlabeled[idx],
                        rule_bias=variant.rule_bias,
                    )
                if variant.pr_eta:
                    loss = loss + variant.pr_eta * pr_style_loss(
                        model,
                        task,
                        unlabeled[idx],
                        tau=variant.pr_tau,
                        rule_bias=variant.rule_bias,
                    )
                loss.backward()
                optimizer.step()
    return model


def evaluate_model(
    model: TinyLinearChainCRF,
    task: SemiRealTask,
    dev: list[tuple[list[int], list[int]]],
    *,
    setting: ProbeSetting,
    variant: VariantConfig,
    seed: int,
) -> ProbeRun:
    p_values: list[float] = []
    nlls: list[float] = []
    unconstrained_event = 0
    constrained_event = 0
    hidden_conflict = 0
    total_chars = 0
    correct_chars = 0
    constrained_correct_chars = 0
    exact_sequences = 0
    constrained_exact_sequences = 0
    for word_ids, gold in dev:
        with torch.no_grad():
            p_event = float(torch.exp(log_event_probability(model, task, word_ids, rule_bias=variant.rule_bias)).item())
            nll = float(nll_loss(model, task, word_ids, gold, rule_bias=variant.rule_bias).item()) / len(gold)
            pred, _score = viterbi(model, task, word_ids, constrained=False, rule_bias=variant.rule_bias)
            c_pred, _c_score = viterbi(model, task, word_ids, constrained=True, rule_bias=variant.rule_bias)
        p_values.append(p_event)
        nlls.append(nll)
        pred_is_event = labels_follow_pattern(task, model.label_names, pred)
        c_pred_is_event = labels_follow_pattern(task, model.label_names, c_pred)
        unconstrained_event += int(pred_is_event)
        constrained_event += int(c_pred_is_event)
        hidden_conflict += int(c_pred_is_event and p_event < 0.5)
        exact_sequences += int(tuple(pred) == tuple(gold))
        constrained_exact_sequences += int(tuple(c_pred) == tuple(gold))
        for pred_idx, c_pred_idx, gold_idx in zip(pred, c_pred, gold):
            total_chars += 1
            correct_chars += int(pred_idx == gold_idx)
            constrained_correct_chars += int(c_pred_idx == gold_idx)
    return ProbeRun(
        block=setting.block,
        task=task.name,
        pattern=task.pattern_string,
        setting=setting.name,
        variant=variant.name,
        seed=seed,
        labeled_size=setting.labeled_size,
        unlabeled_size=setting.unlabeled_size,
        dev_size=setting.dev_size,
        epochs=setting.epochs,
        lr=setting.lr,
        mean_p_event=mean(p_values),
        mean_illegal_mass=1.0 - mean(p_values),
        low_p_event_rate=mean(1.0 if p < 0.5 else 0.0 for p in p_values),
        unconstrained_event_rate=unconstrained_event / len(dev),
        constrained_event_rate=constrained_event / len(dev),
        char_accuracy=correct_chars / total_chars,
        constrained_char_accuracy=constrained_correct_chars / total_chars,
        exact_sequence_accuracy=exact_sequences / len(dev),
        constrained_exact_sequence_accuracy=constrained_exact_sequences / len(dev),
        mean_nll=mean(nlls),
        hidden_conflict_rate=hidden_conflict / len(dev),
        notes="semi-real CPU-only local probe; not benchmark evidence",
    )


def run_task(task: SemiRealTask, setting: ProbeSetting, variants: dict[str, VariantConfig]) -> list[ProbeRun]:
    runs: list[ProbeRun] = []
    label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
    for seed in setting.seeds:
        labeled_ds = make_dataset(task, f"{task.name}_labeled", setting.labeled_size, seed=1100 + seed)
        unlabeled_ds = make_dataset(task, f"{task.name}_unlabeled", setting.unlabeled_size, seed=2200 + seed)
        dev_ds = make_dataset(task, f"{task.name}_dev", setting.dev_size, seed=3300 + seed)
        vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens + dev_ds.tokens)
        labeled = encode(labeled_ds, vocab, label_to_idx)
        unlabeled = [word_ids for word_ids, _labels in encode(unlabeled_ds, vocab, label_to_idx)]
        dev = encode(dev_ds, vocab, label_to_idx)
        for variant_name in setting.variants:
            variant = variants[variant_name]
            model = train_model(
                task,
                labeled,
                unlabeled,
                len(vocab),
                variant=variant,
                seed=seed,
                epochs=setting.epochs,
                lr=setting.lr,
            )
            runs.append(evaluate_model(model, task, dev, setting=setting, variant=variant, seed=seed))
    return runs


def run_settings(
    tasks: Sequence[SemiRealTask],
    settings: Sequence[ProbeSetting],
    variants: dict[str, VariantConfig],
) -> list[ProbeRun]:
    runs: list[ProbeRun] = []
    for setting in settings:
        for task in tasks:
            runs.extend(run_task(task, setting, variants))
    return runs


def _ci95(values: Sequence[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return 1.96 * stdev(values) / sqrt(len(values))


def summarize_runs(runs: Sequence[ProbeRun]) -> list[dict[str, float | str | int]]:
    by_key = {(run.block, run.task, run.setting, run.seed, run.variant): run for run in runs}
    grouped: dict[tuple[str, str, str, str], list[ProbeRun]] = {}
    for run in runs:
        grouped.setdefault((run.block, run.task, run.setting, run.variant), []).append(run)
    rows: list[dict[str, float | str | int]] = []
    for (block, task, setting, variant), group in sorted(grouped.items()):
        deltas_p: list[float] = []
        deltas_illegal: list[float] = []
        deltas_event_rate: list[float] = []
        deltas_char: list[float] = []
        deltas_exact: list[float] = []
        deltas_constrained_char: list[float] = []
        deltas_constrained_exact: list[float] = []
        for run in group:
            baseline = by_key[(block, task, setting, run.seed, "B0_unconstrained")]
            deltas_p.append(run.mean_p_event - baseline.mean_p_event)
            deltas_illegal.append(run.mean_illegal_mass - baseline.mean_illegal_mass)
            deltas_event_rate.append(run.unconstrained_event_rate - baseline.unconstrained_event_rate)
            deltas_char.append(run.char_accuracy - baseline.char_accuracy)
            deltas_exact.append(run.exact_sequence_accuracy - baseline.exact_sequence_accuracy)
            deltas_constrained_char.append(run.constrained_char_accuracy - baseline.constrained_char_accuracy)
            deltas_constrained_exact.append(
                run.constrained_exact_sequence_accuracy - baseline.constrained_exact_sequence_accuracy
            )
        rows.append(
            {
                "block": block,
                "task": task,
                "setting": setting,
                "variant": variant,
                "runs": len(group),
                "mean_p_event": mean(run.mean_p_event for run in group),
                "delta_p_event": mean(deltas_p),
                "ci95_delta_p_event": _ci95(deltas_p),
                "mean_illegal_mass": mean(run.mean_illegal_mass for run in group),
                "delta_illegal_mass": mean(deltas_illegal),
                "low_p_event_rate": mean(run.low_p_event_rate for run in group),
                "unconstrained_event_rate": mean(run.unconstrained_event_rate for run in group),
                "delta_unconstrained_event_rate": mean(deltas_event_rate),
                "constrained_event_rate": mean(run.constrained_event_rate for run in group),
                "char_accuracy": mean(run.char_accuracy for run in group),
                "delta_char_accuracy": mean(deltas_char),
                "constrained_char_accuracy": mean(run.constrained_char_accuracy for run in group),
                "delta_constrained_char_accuracy": mean(deltas_constrained_char),
                "exact_sequence_accuracy": mean(run.exact_sequence_accuracy for run in group),
                "delta_exact_sequence_accuracy": mean(deltas_exact),
                "constrained_exact_sequence_accuracy": mean(run.constrained_exact_sequence_accuracy for run in group),
                "delta_constrained_exact_sequence_accuracy": mean(deltas_constrained_exact),
                "mean_nll": mean(run.mean_nll for run in group),
                "hidden_conflict_rate": mean(run.hidden_conflict_rate for run in group),
            }
        )
    return rows


def write_table(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(prefix: str, runs: Sequence[ProbeRun], output_dir: Path) -> list[dict[str, float | str | int]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dicts = [asdict(run) for run in runs]
    summary = summarize_runs(runs)
    (output_dir / f"{prefix}_runs.json").write_text(json.dumps(run_dicts, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / f"{prefix}_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_table(output_dir / f"{prefix}_runs.csv", run_dicts)
    write_table(output_dir / f"{prefix}_summary.csv", summary)
    return summary


def make_case_studies(output_dir: Path, seeds: Sequence[int] = (0, 1, 2)) -> list[CaseStudy]:
    task = next(task for task in TASKS if task.name == "product_code")
    setting = ProbeSetting(
        block="case_study",
        name="case_labeled25_unlabeled100",
        labeled_size=25,
        unlabeled_size=100,
        dev_size=200,
        epochs=5,
        lr=0.08,
        seeds=tuple(seeds),
        variants=("B0_unconstrained", "B4_semi_event_0.1"),
    )
    label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
    case_rows: list[CaseStudy] = []
    for seed in setting.seeds:
        labeled_ds = make_dataset(task, f"{task.name}_labeled", setting.labeled_size, seed=1100 + seed)
        unlabeled_ds = make_dataset(task, f"{task.name}_unlabeled", setting.unlabeled_size, seed=2200 + seed)
        dev_ds = make_dataset(task, f"{task.name}_dev", setting.dev_size, seed=3300 + seed)
        vocab = build_vocab(labeled_ds.tokens + unlabeled_ds.tokens + dev_ds.tokens)
        inv_vocab = {idx: token for token, idx in vocab.items()}
        labeled = encode(labeled_ds, vocab, label_to_idx)
        unlabeled = [word_ids for word_ids, _labels in encode(unlabeled_ds, vocab, label_to_idx)]
        dev = encode(dev_ds, vocab, label_to_idx)
        baseline = train_model(
            task,
            labeled,
            unlabeled,
            len(vocab),
            variant=VARIANTS["B0_unconstrained"],
            seed=seed,
            epochs=setting.epochs,
            lr=setting.lr,
        )
        event_model = train_model(
            task,
            labeled,
            unlabeled,
            len(vocab),
            variant=VARIANTS["B4_semi_event_0.1"],
            seed=seed,
            epochs=setting.epochs,
            lr=setting.lr,
        )
        candidates: list[CaseStudy] = []
        for word_ids, gold in dev:
            with torch.no_grad():
                base_p = float(torch.exp(log_event_probability(baseline, task, word_ids)).item())
                event_p = float(torch.exp(log_event_probability(event_model, task, word_ids)).item())
                base_pred, _ = viterbi(baseline, task, word_ids)
                base_c_pred, _ = viterbi(baseline, task, word_ids, constrained=True)
                event_pred, _ = viterbi(event_model, task, word_ids)
                event_c_pred, _ = viterbi(event_model, task, word_ids, constrained=True)
            if labels_follow_pattern(task, baseline.label_names, base_c_pred) and base_p < 0.5:
                candidates.append(
                    CaseStudy(
                        task=task.name,
                        seed=seed,
                        tokens=" ".join(inv_vocab[idx] for idx in word_ids),
                        gold="".join(task.label_names[idx] for idx in gold),
                        baseline_pred="".join(task.label_names[idx] for idx in base_pred),
                        baseline_constrained_pred="".join(task.label_names[idx] for idx in base_c_pred),
                        event_pred="".join(task.label_names[idx] for idx in event_pred),
                        event_constrained_pred="".join(task.label_names[idx] for idx in event_c_pred),
                        baseline_p_event=base_p,
                        event_p_event=event_p,
                        comment="hard constraint gives a legal output, but baseline posterior event mass is low",
                    )
                )
        candidates.sort(key=lambda row: (row.baseline_p_event, -row.event_p_event))
        case_rows.extend(candidates[:3])
    case_dicts = [asdict(row) for row in case_rows]
    (output_dir / "semi_real_case_studies.json").write_text(
        json.dumps(case_dicts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_table(output_dir / "semi_real_case_studies.csv", case_dicts)
    return case_rows


def fmt(value: object, *, signed: bool = False) -> str:
    if isinstance(value, float):
        prefix = "+" if signed and value >= 0 else ""
        return f"{prefix}{value:.4f}"
    return str(value)


def markdown_result_table(rows: Sequence[dict[str, float | str | int]], *, block: str) -> list[str]:
    selected = [row for row in rows if row["block"] == block and row["variant"] != "B0_unconstrained"]
    lines = [
        "| task | setting | variant | runs | Δ P(L|x) | Δ legal rate | Δ char acc | Δ exact acc |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in selected:
        lines.append(
            "| {task} | {setting} | {variant} | {runs} | {dp} | {dr} | {dc} | {de} |".format(
                task=row["task"],
                setting=row["setting"],
                variant=row["variant"],
                runs=int(row["runs"]),
                dp=fmt(float(row["delta_p_event"]), signed=True),
                dr=fmt(float(row["delta_unconstrained_event_rate"]), signed=True),
                dc=fmt(float(row["delta_char_accuracy"]), signed=True),
                de=fmt(float(row["delta_exact_sequence_accuracy"]), signed=True),
            )
        )
    return lines


def markdown_case_table(cases: Sequence[CaseStudy]) -> list[str]:
    lines = [
        "| tokens | gold | baseline | constrained | event-trained | P_base(L|x) | P_event(L|x) |",
        "|---|---|---|---|---|---:|---:|",
    ]
    for row in cases[:8]:
        lines.append(
            f"| `{row.tokens}` | `{row.gold}` | `{row.baseline_pred}` | `{row.baseline_constrained_pred}` | `{row.event_pred}` | {row.baseline_p_event:.4f} | {row.event_p_event:.4f} |"
        )
    return lines


def write_plan(output_dir: Path) -> None:
    report_dir = output_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    plan = [
        "# 半真实格式抽取验证计划",
        "",
        "本轮目标是把 controlled format probe 往更真实的表单字段靠近，但仍保持 CPU-only、本地、可审计。",
        "",
        "## 1. 任务",
        "",
        "- `product_code`: `LL-DDD`，类似商品编号或票据编号。",
        "- `amount`: `$DD.DD`，类似金额字段。",
        "- `date`: `DDDD-DD-DD`，类似日期字段。",
        "- `dose`: `DDDmg`，类似剂量字段。",
        "",
        "输入使用 OCR-like 混淆 token，例如 `O/0`, `I/1`, `B/8`, `S/5`, `Z/2`, `$ / S`, `m / rn`。",
        "",
        "## 2. 系统",
        "",
        "- B0: 普通 CRF。",
        "- B1: B0 + hard-constrained decoding，仅作为评估对照。",
        "- B2: labeled event posterior training。",
        "- B3: event posterior training + hard-constrained decoding，仅作为评估对照。",
        "- B4: semi-event training，在未标注输入上也使用 `Pθ(L|x)`。",
        "- B5: rule-feature baseline，把位置合法性作为固定局部 bias。",
        "- B6: posterior-regularization-style baseline，用 `max(0, τ-Pθ(L|x))²` 约束事件后验。",
        "",
        "## 3. 边界",
        "",
        "这不是 benchmark，不支持真实任务 superiority。B5/B6 是本地压力测试 baseline，不是完整文献复现。",
        "",
    ]
    (report_dir / "SEMI_REAL_FORMAT_EXPERIMENT_PLAN_CN.md").write_text("\n".join(plan), encoding="utf-8")


def write_reports(
    main_summary: Sequence[dict[str, float | str | int]],
    learning_summary: Sequence[dict[str, float | str | int]],
    lambda_summary: Sequence[dict[str, float | str | int]],
    cases: Sequence[CaseStudy],
    output_dir: Path,
) -> None:
    report_dir = output_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report = [
        "# 半真实格式抽取验证报告",
        "",
        "本报告是 CPU-only local probe，不是正式 benchmark。",
        "",
        "## 1. 主结果：半真实格式字段",
        "",
        *_markdown_trim(markdown_result_table(main_summary, block="semi_real_main"), max_rows=40),
        "",
        "## 2. Learning Curve：少标注/弱监督方向",
        "",
        *_markdown_trim(markdown_result_table(learning_summary, block="learning_curve"), max_rows=32),
        "",
        "## 3. Lambda Tradeoff",
        "",
        *_markdown_trim(markdown_result_table(lambda_summary, block="lambda_tradeoff"), max_rows=36),
        "",
        "## 4. Conflict Case Study",
        "",
        "下面样本说明：hard constraint 可以给出合法输出，但 baseline 的原始后验事件质量仍然低。",
        "",
        *markdown_case_table(cases),
        "",
        "## 5. 当前解释",
        "",
        "如果 B4 在多个半真实任务上提高 `Pθ(L|x)` 和原始合法率，则支持 structural usefulness 从 controlled task 往 semi-real task 推进。",
        "",
        "如果 task accuracy 只在部分任务或部分 λ 下上升，则只能说 controlled/semi-real task usefulness 是 partial evidence。",
        "",
        "B5/B6 如果很强，不能视为坏事；它们说明后续论文必须诚实比较“规则作为局部特征 / 后验约束 / 后验事件训练”的边界。",
        "",
    ]
    (report_dir / "SEMI_REAL_FORMAT_VALIDATION_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    sweet_main = [
        row
        for row in main_summary
        if row["variant"] != "B0_unconstrained"
        and float(row["delta_p_event"]) > 0
        and float(row["delta_unconstrained_event_rate"]) > 0
        and float(row["delta_char_accuracy"]) >= 0
    ]
    b4_positive = [
        row
        for row in main_summary
        if str(row["variant"]).startswith("B4")
        and float(row["delta_p_event"]) > 0
        and float(row["delta_unconstrained_event_rate"]) > 0
    ]
    audit = [
        "# 半真实格式抽取 Result-to-Claim 审计",
        "",
        "## Verdict",
        "",
        "```text",
        "claim_supported = partial",
        "confidence = medium",
        "```",
        "",
        "## 支持",
        "",
        f"- B4 semi-event 在主实验中出现 posterior/event-rate 正向结果的配置数：{len(b4_positive)}。",
        f"- 同时满足 `Pθ(L|x)`、原始合法率、char accuracy 不下降的 sweet spot 数：{len(sweet_main)}。",
        "- case study 支持 hard constraint 与 posterior event mass 的边界区别。",
        "",
        "## 不支持",
        "",
        "- 仍不支持真实 benchmark superiority。",
        "- 仍不支持 event posterior training 全面优于 hard constraint。",
        "- B5/B6 只是本地对照，不代表完整相关工作复现。",
        "",
        "## 建议 claim",
        "",
        "```text",
        "在半真实格式字段的本地验证中，Pθ(L|x) 作为 semi-event 训练信号能继续稳定改变后验事件质量；",
        "任务准确率收益依赖任务和 λ，当前只能作为 partial semi-real evidence。",
        "```",
        "",
    ]
    (report_dir / "SEMI_REAL_FORMAT_RESULT_TO_CLAIM_AUDIT.md").write_text("\n".join(audit), encoding="utf-8")

    gate = [
        "# 半真实格式抽取下一步 Gate",
        "",
        "```text",
        "GO: update proposal/HTML with semi-real evidence.",
        "GO: if continuing experiments, add stronger faithful baselines and one public/real small dataset.",
        "HOLD: benchmark superiority claim.",
        "HOLD: paper-writing as final empirical story.",
        "```",
        "",
        "下一阶段如果要继续推进，应优先做真实小数据或公开格式抽取数据，并把 B5/B6 做成更 faithful 的相关工作 baseline。",
        "",
    ]
    (report_dir / "SEMI_REAL_FORMAT_NEXT_GATE.md").write_text("\n".join(gate), encoding="utf-8")


def _markdown_trim(lines: list[str], *, max_rows: int) -> list[str]:
    header = lines[:2]
    rows = lines[2:]
    if len(rows) <= max_rows:
        return lines
    return header + rows[:max_rows] + ["| ... | ... | ... | ... | ... | ... | ... | ... |"]


def main_settings(seed_count: int) -> tuple[list[ProbeSetting], list[ProbeSetting], list[ProbeSetting]]:
    seeds = tuple(range(seed_count))
    main = [
        ProbeSetting(
            block="semi_real_main",
            name="labeled25_unlabeled100",
            labeled_size=25,
            unlabeled_size=100,
            dev_size=300,
            epochs=5,
            lr=0.08,
            seeds=seeds,
            variants=tuple(VARIANTS.keys()),
        )
    ]
    learning = [
        ProbeSetting(
            block="learning_curve",
            name=f"labeled{labeled}_unlabeled100",
            labeled_size=labeled,
            unlabeled_size=100,
            dev_size=250,
            epochs=5,
            lr=0.08,
            seeds=seeds,
            variants=("B0_unconstrained", "B4_semi_event_0.1"),
        )
        for labeled in (5, 10, 25, 50)
    ]
    lambda_sweep = [
        ProbeSetting(
            block="lambda_tradeoff",
            name="labeled25_unlabeled100",
            labeled_size=25,
            unlabeled_size=100,
            dev_size=250,
            epochs=5,
            lr=0.08,
            seeds=seeds,
            variants=tuple(LAMBDA_VARIANTS.keys()),
        )
    ]
    return main, learning, lambda_sweep


def parse_task_names(names: Sequence[str]) -> list[SemiRealTask]:
    by_name = {task.name: task for task in TASKS}
    return [by_name[name] for name in names]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/results/event_training")
    parser.add_argument("--seed-count", type=int, default=5)
    parser.add_argument("--tasks", nargs="*", default=[task.name for task in TASKS])
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_plan(output_dir)

    seed_count = min(args.seed_count, 2) if args.quick else args.seed_count
    tasks = parse_task_names(args.tasks)
    main_settings_list, learning_settings_list, lambda_settings_list = main_settings(seed_count)

    main_runs = run_settings(tasks, main_settings_list, VARIANTS)
    main_summary = write_outputs("semi_real_main", main_runs, output_dir)

    learning_tasks = [task for task in tasks if task.name in {"product_code", "amount"}]
    learning_runs = run_settings(learning_tasks, learning_settings_list, VARIANTS)
    learning_summary = write_outputs("semi_real_learning_curve", learning_runs, output_dir)

    lambda_tasks = [task for task in tasks if task.name in {"product_code", "amount"}]
    lambda_runs = run_settings(lambda_tasks, lambda_settings_list, LAMBDA_VARIANTS)
    lambda_summary = write_outputs("semi_real_lambda_tradeoff", lambda_runs, output_dir)

    case_seed_count = min(3, seed_count)
    cases = make_case_studies(output_dir, seeds=tuple(range(case_seed_count)))
    write_reports(main_summary, learning_summary, lambda_summary, cases, output_dir)


if __name__ == "__main__":
    main()
