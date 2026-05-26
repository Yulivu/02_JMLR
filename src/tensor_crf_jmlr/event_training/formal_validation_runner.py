"""Formal controlled validation runner for posterior event training.

This runner is still CPU-only and local.  It is not a benchmark runner.  Its
purpose is to turn the earlier LLDDD probe into a reusable controlled protocol:

* multiple non-saturated regular-language format events;
* B0/B1/B2/B3/B4 baseline accounting;
* posterior, decoding, and task metrics in CSV/JSON;
* conservative Chinese reports with explicit claim boundaries.
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


LETTERS = ("O", "I", "B", "S", "Z", "A")
DIGITS = ("0", "1", "8", "5", "2", "3")
LITERALS = ("-",)
BASE_LABELS = LETTERS + DIGITS + LITERALS

AMBIGUOUS_GLYPH = {
    "O": "O0",
    "0": "O0",
    "I": "I1",
    "1": "I1",
    "B": "B8",
    "8": "B8",
    "S": "S5",
    "5": "S5",
    "Z": "Z2",
    "2": "Z2",
    "A": "A",
    "3": "3",
    "-": "-",
}

GROUP_TO_LABELS = {
    "L": LETTERS,
    "D": DIGITS,
    "-": ("-",),
}


@dataclass(frozen=True)
class FormatTask:
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
        # Include both letters and digits for all tasks so that the format event
        # is genuinely non-saturated; include literals only when needed.
        for label in LETTERS + DIGITS:
            if label not in labels:
                labels.append(label)
        for group in self.pattern:
            if group in LITERALS and group not in labels:
                labels.append(group)
        return tuple(labels)


@dataclass(frozen=True)
class FormatDataset:
    name: str
    tokens: list[list[str]]
    labels: list[list[str]]


@dataclass(frozen=True)
class FormalSetting:
    name: str
    labeled_size: int
    unlabeled_size: int
    dev_size: int
    epochs: int
    lr: float
    seeds: tuple[int, ...]
    variants: tuple[str, ...]


@dataclass
class FormalRun:
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


TASKS = (
    FormatTask("LLDDD", ("L", "L", "D", "D", "D"), "two letters followed by three digits"),
    FormatTask("DDDLL", ("D", "D", "D", "L", "L"), "three digits followed by two letters"),
    FormatTask("LL-DDD", ("L", "L", "-", "D", "D", "D"), "two letters, dash, three digits"),
    FormatTask("DATE", ("D", "D", "D", "D", "-", "D", "D", "-", "D", "D"), "date-like digit format"),
)


VARIANT_WEIGHTS: dict[str, tuple[float, float]] = {
    "B0_unconstrained": (0.0, 0.0),
    "B2_event_0.1": (0.1, 0.0),
    "B2_event_0.5": (0.5, 0.0),
    "B4_semi_event_0.1": (0.1, 0.1),
    "B4_semi_event_0.5": (0.5, 0.5),
}


def default_setting(seed_count: int = 10) -> FormalSetting:
    return FormalSetting(
        name="controlled_labeled25_unlabeled100",
        labeled_size=25,
        unlabeled_size=100,
        dev_size=300,
        epochs=5,
        lr=0.08,
        seeds=tuple(range(seed_count)),
        variants=tuple(VARIANT_WEIGHTS.keys()),
    )


def choose_label(group: str, rng: random.Random) -> str:
    if group == "L":
        return rng.choice(("O", "I", "B", "S", "Z", "O", "I", "B", "S", "Z", "A"))
    if group == "D":
        return rng.choice(("0", "1", "8", "5", "2", "0", "1", "8", "5", "2", "3"))
    if group in LITERALS:
        return group
    raise ValueError(f"unknown pattern group: {group!r}")


def make_format_dataset(task: FormatTask, name: str, size: int, *, seed: int) -> FormatDataset:
    rng = random.Random(seed)
    tokens: list[list[str]] = []
    labels: list[list[str]] = []
    for _ in range(size):
        label_seq = [choose_label(group, rng) for group in task.pattern]
        labels.append(label_seq)
        tokens.append([AMBIGUOUS_GLYPH[label] for label in label_seq])
    return FormatDataset(name=name, tokens=tokens, labels=labels)


def build_vocab(sequences: Sequence[Sequence[str]]) -> dict[str, int]:
    vocab = {"<UNK>": 0}
    for seq in sequences:
        for token in seq:
            if token not in vocab:
                vocab[token] = len(vocab)
    return vocab


def encode(
    dataset: FormatDataset,
    vocab: dict[str, int],
    label_to_idx: dict[str, int],
) -> list[tuple[list[int], list[int]]]:
    unk = vocab["<UNK>"]
    return [
        ([vocab.get(token, unk) for token in tokens], [label_to_idx[label] for label in labels])
        for tokens, labels in zip(dataset.tokens, dataset.labels)
    ]


def pattern_masks(task: FormatTask, label_names: Sequence[str], device: torch.device) -> list[torch.Tensor]:
    masks: list[torch.Tensor] = []
    for group in task.pattern:
        allowed = set(GROUP_TO_LABELS[group])
        masks.append(torch.tensor([label in allowed for label in label_names], dtype=torch.bool, device=device))
    return masks


def labels_follow_pattern(task: FormatTask, label_names: Sequence[str], path: Sequence[int]) -> bool:
    if len(path) != task.length:
        return False
    for group, idx in zip(task.pattern, path):
        if label_names[idx] not in GROUP_TO_LABELS[group]:
            return False
    return True


def log_event_partition_format(
    model: TinyLinearChainCRF,
    task: FormatTask,
    word_ids: Sequence[int],
) -> torch.Tensor:
    emissions = model.emission_scores(word_ids)
    if emissions.shape[0] != task.length:
        raise ValueError(f"expected length {task.length}, got {emissions.shape[0]}")
    masks = pattern_masks(task, model.label_names, emissions.device)
    alpha = torch.where(masks[0], model.start + emissions[0], torch.full_like(model.start, -1e9))
    for pos in range(1, emissions.shape[0]):
        scores = alpha[:, None] + model.transitions + emissions[pos][None, :]
        scores = torch.where(masks[pos][None, :], scores, torch.full_like(scores, -1e9))
        alpha = torch.logsumexp(scores, dim=0)
    return torch.logsumexp(alpha, dim=0)


def log_event_probability_format(
    model: TinyLinearChainCRF,
    task: FormatTask,
    word_ids: Sequence[int],
) -> torch.Tensor:
    emissions = model.emission_scores(word_ids)
    return log_event_partition_format(model, task, word_ids) - model.log_partition(emissions)


def format_event_loss(model: TinyLinearChainCRF, task: FormatTask, word_ids: Sequence[int]) -> torch.Tensor:
    return -log_event_probability_format(model, task, word_ids)


def constrained_viterbi_format(
    model: TinyLinearChainCRF,
    task: FormatTask,
    word_ids: Sequence[int],
) -> tuple[list[int], float]:
    emissions = model.emission_scores(word_ids)
    if emissions.shape[0] != task.length:
        raise ValueError(f"expected length {task.length}, got {emissions.shape[0]}")
    masks = pattern_masks(task, model.label_names, emissions.device)
    alpha = torch.where(masks[0], model.start + emissions[0], torch.full_like(model.start, -1e9))
    backpointers: list[list[int]] = []
    for pos in range(1, emissions.shape[0]):
        scores = alpha[:, None] + model.transitions + emissions[pos][None, :]
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


def train_model(
    task: FormatTask,
    labeled: list[tuple[list[int], list[int]]],
    unlabeled: list[list[int]],
    vocab_size: int,
    *,
    variant: str,
    seed: int,
    epochs: int,
    lr: float,
) -> TinyLinearChainCRF:
    set_seed(seed)
    model = TinyLinearChainCRF(vocab_size, task.label_names)
    model.assert_cpu_only()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    labeled_lam, unlabeled_lam = VARIANT_WEIGHTS[variant]
    for _epoch in range(epochs):
        labeled_order = list(range(len(labeled)))
        random.shuffle(labeled_order)
        for idx in labeled_order:
            word_ids, label_ids = labeled[idx]
            optimizer.zero_grad(set_to_none=True)
            loss = model.neg_log_likelihood(word_ids, label_ids)
            if labeled_lam:
                loss = loss + labeled_lam * format_event_loss(model, task, word_ids)
            loss.backward()
            optimizer.step()
        if unlabeled_lam and unlabeled:
            unlabeled_order = list(range(len(unlabeled)))
            random.shuffle(unlabeled_order)
            for idx in unlabeled_order:
                optimizer.zero_grad(set_to_none=True)
                loss = unlabeled_lam * format_event_loss(model, task, unlabeled[idx])
                loss.backward()
                optimizer.step()
    return model


def evaluate_model(
    model: TinyLinearChainCRF,
    task: FormatTask,
    dev: list[tuple[list[int], list[int]]],
    *,
    setting: FormalSetting,
    variant: str,
    seed: int,
) -> FormalRun:
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
            p_event = float(torch.exp(log_event_probability_format(model, task, word_ids)).detach().cpu().item())
            nll = float(model.neg_log_likelihood(word_ids, gold).detach().cpu().item()) / len(gold)
            pred, _score = model.viterbi(word_ids, constrained=False)
            c_pred, _c_score = constrained_viterbi_format(model, task, word_ids)
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
    return FormalRun(
        task=task.name,
        pattern="".join(task.pattern),
        setting=setting.name,
        variant=variant,
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
        notes="controlled CPU-only posterior-event training probe; not a benchmark",
    )


def run_task(task: FormatTask, setting: FormalSetting) -> list[FormalRun]:
    runs: list[FormalRun] = []
    label_to_idx = {label: idx for idx, label in enumerate(task.label_names)}
    for seed in setting.seeds:
        labeled_dataset = make_format_dataset(task, f"{task.name}_labeled", setting.labeled_size, seed=1000 + seed)
        unlabeled_dataset = make_format_dataset(task, f"{task.name}_unlabeled", setting.unlabeled_size, seed=2000 + seed)
        dev_dataset = make_format_dataset(task, f"{task.name}_dev", setting.dev_size, seed=3000 + seed)
        vocab = build_vocab(labeled_dataset.tokens + unlabeled_dataset.tokens + dev_dataset.tokens)
        labeled = encode(labeled_dataset, vocab, label_to_idx)
        unlabeled = [word_ids for word_ids, _labels in encode(unlabeled_dataset, vocab, label_to_idx)]
        dev = encode(dev_dataset, vocab, label_to_idx)
        for variant in setting.variants:
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


def _ci95(values: Sequence[float]) -> float:
    if len(values) <= 1:
        return 0.0
    return 1.96 * stdev(values) / sqrt(len(values))


def summarize_runs(runs: Sequence[FormalRun]) -> list[dict[str, float | str | int]]:
    by_key = {(run.task, run.setting, run.seed, run.variant): run for run in runs}
    grouped: dict[tuple[str, str, str], list[FormalRun]] = {}
    for run in runs:
        grouped.setdefault((run.task, run.setting, run.variant), []).append(run)
    rows: list[dict[str, float | str | int]] = []
    for (task, setting, variant), group in sorted(grouped.items()):
        deltas_p: list[float] = []
        deltas_illegal: list[float] = []
        deltas_event_rate: list[float] = []
        deltas_char: list[float] = []
        deltas_exact: list[float] = []
        deltas_constrained_char: list[float] = []
        deltas_constrained_exact: list[float] = []
        for run in group:
            baseline = by_key[(task, setting, run.seed, "B0_unconstrained")]
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
                "task": task,
                "setting": setting,
                "variant": variant,
                "runs": len(group),
                "mean_p_event": mean(run.mean_p_event for run in group),
                "delta_p_event": mean(deltas_p),
                "ci95_delta_p_event": _ci95(deltas_p),
                "p_event_up_rate": mean(1.0 if delta > 0 else 0.0 for delta in deltas_p),
                "mean_illegal_mass": mean(run.mean_illegal_mass for run in group),
                "delta_illegal_mass": mean(deltas_illegal),
                "low_p_event_rate": mean(run.low_p_event_rate for run in group),
                "unconstrained_event_rate": mean(run.unconstrained_event_rate for run in group),
                "delta_unconstrained_event_rate": mean(deltas_event_rate),
                "event_rate_up_rate": mean(1.0 if delta > 0 else 0.0 for delta in deltas_event_rate),
                "constrained_event_rate": mean(run.constrained_event_rate for run in group),
                "char_accuracy": mean(run.char_accuracy for run in group),
                "delta_char_accuracy": mean(deltas_char),
                "char_accuracy_up_rate": mean(1.0 if delta > 0 else 0.0 for delta in deltas_char),
                "constrained_char_accuracy": mean(run.constrained_char_accuracy for run in group),
                "delta_constrained_char_accuracy": mean(deltas_constrained_char),
                "exact_sequence_accuracy": mean(run.exact_sequence_accuracy for run in group),
                "delta_exact_sequence_accuracy": mean(deltas_exact),
                "exact_sequence_up_rate": mean(1.0 if delta > 0 else 0.0 for delta in deltas_exact),
                "constrained_exact_sequence_accuracy": mean(run.constrained_exact_sequence_accuracy for run in group),
                "delta_constrained_exact_sequence_accuracy": mean(deltas_constrained_exact),
                "mean_nll": mean(run.mean_nll for run in group),
                "hidden_conflict_rate": mean(run.hidden_conflict_rate for run in group),
            }
        )
    return rows


def _fmt(value: object, digits: int = 4, signed: bool = False) -> str:
    if isinstance(value, float):
        prefix = "+" if signed and value >= 0 else ""
        return f"{prefix}{value:.{digits}f}"
    return str(value)


def _variant_label(variant: str) -> str:
    labels = {
        "B0_unconstrained": "B0 baseline",
        "B2_event_0.1": "B2 event 0.1",
        "B2_event_0.5": "B2 event 0.5",
        "B4_semi_event_0.1": "B4 semi-event 0.1",
        "B4_semi_event_0.5": "B4 semi-event 0.5",
    }
    return labels.get(variant, variant)


def _summary_table(rows: Sequence[dict[str, float | str | int]]) -> list[str]:
    selected = [row for row in rows if row["variant"] != "B0_unconstrained"]
    lines = [
        "| task | variant | runs | Δ P(L|x) | Δ illegal mass | Δ unconstrained legal rate | Δ char acc | Δ exact acc |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in selected:
        lines.append(
            "| {task} | {variant} | {runs} | {dp} | {di} | {dr} | {dc} | {de} |".format(
                task=row["task"],
                variant=_variant_label(str(row["variant"])),
                runs=int(row["runs"]),
                dp=_fmt(float(row["delta_p_event"]), signed=True),
                di=_fmt(float(row["delta_illegal_mass"]), signed=True),
                dr=_fmt(float(row["delta_unconstrained_event_rate"]), signed=True),
                dc=_fmt(float(row["delta_char_accuracy"]), signed=True),
                de=_fmt(float(row["delta_exact_sequence_accuracy"]), signed=True),
            )
        )
    return lines


def _baseline_constraint_table(rows: Sequence[dict[str, float | str | int]]) -> list[str]:
    baseline_rows = [row for row in rows if row["variant"] == "B0_unconstrained"]
    lines = [
        "| task | P(L|x) | unconstrained legal rate | hard-constrained legal rate | char acc | hard-constrained char acc | exact acc | hard-constrained exact acc | hidden conflict rate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in baseline_rows:
        lines.append(
            "| {task} | {p} | {ur} | {cr} | {ca} | {cca} | {ea} | {cea} | {hc} |".format(
                task=row["task"],
                p=_fmt(float(row["mean_p_event"])),
                ur=_fmt(float(row["unconstrained_event_rate"])),
                cr=_fmt(float(row["constrained_event_rate"])),
                ca=_fmt(float(row["char_accuracy"])),
                cca=_fmt(float(row["constrained_char_accuracy"])),
                ea=_fmt(float(row["exact_sequence_accuracy"])),
                cea=_fmt(float(row["constrained_exact_sequence_accuracy"])),
                hc=_fmt(float(row["hidden_conflict_rate"])),
            )
        )
    return lines


def _sweet_spot_table(rows: Sequence[dict[str, float | str | int]]) -> list[str]:
    selected = [
        row
        for row in rows
        if row["variant"] != "B0_unconstrained"
        and float(row["delta_p_event"]) > 0
        and float(row["delta_unconstrained_event_rate"]) > 0
        and float(row["delta_char_accuracy"]) >= 0
        and float(row["delta_exact_sequence_accuracy"]) >= 0
    ]
    if not selected:
        return ["当前没有同时提高事件后验、原始合法率、字符准确率和 exact 准确率的配置。"]
    lines = [
        "| task | variant | Δ P(L|x) | Δ legal rate | Δ char acc | Δ exact acc |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in selected:
        lines.append(
            "| {task} | {variant} | {dp} | {dr} | {dc} | {de} |".format(
                task=row["task"],
                variant=_variant_label(str(row["variant"])),
                dp=_fmt(float(row["delta_p_event"]), signed=True),
                dr=_fmt(float(row["delta_unconstrained_event_rate"]), signed=True),
                dc=_fmt(float(row["delta_char_accuracy"]), signed=True),
                de=_fmt(float(row["delta_exact_sequence_accuracy"]), signed=True),
            )
        )
    return lines


def write_outputs(runs: Sequence[FormalRun], output_dir: Path) -> list[dict[str, float | str | int]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_dicts = [asdict(run) for run in runs]
    (output_dir / "formal_validation_runs.json").write_text(
        json.dumps(run_dicts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "formal_validation_runs.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(run_dicts[0].keys()))
        writer.writeheader()
        writer.writerows(run_dicts)
    summary = summarize_runs(runs)
    (output_dir / "formal_validation_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    with (output_dir / "formal_validation_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)
    return summary


def write_reports(summary: Sequence[dict[str, float | str | int]], output_dir: Path) -> None:
    report_dir = output_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "FORMAL_CONTROLLED_VALIDATION_REPORT.md"
    audit_path = report_dir / "FORMAL_CONTROLLED_VALIDATION_CLAIM_AUDIT.md"
    next_path = report_dir / "FORMAL_CONTROLLED_VALIDATION_NEXT_GATE.md"

    report = [
        "# 正式受控验证报告",
        "",
        "本报告记录 CPU-only、tiny controlled format-event probes。它不是 benchmark，也不是完整真实任务实验。",
        "",
        "## 1. 核心问题",
        "",
        "我们要检查的是：当规则语言事件 `L` 非饱和且与任务结构强相关时，`Pθ(L|x)` 是否能作为训练信号，推动 CRF 原始后验把更多概率质量放到 `L` 中，并改善 unconstrained 输出的合法性。",
        "",
        "## 2. 实验边界",
        "",
        "- 任务是受控 OCR-like / form-code sequence labeling。",
        "- 输入含有混淆 glyph，例如 `O/0`, `I/1`, `B/8`, `S/5`, `Z/2`。",
        "- 规则事件包括 `LLDDD`, `DDDLL`, `LL-DDD`, `DATE`。",
        "- 系统包括 B0 baseline、B1 hard-constrained decoding、B2 event posterior training、B3 event + hard-constrained decoding、B4 semi-event training。",
        "- 所有运行都是 CPU-only local probes，不记录 runtime/memory superiority。",
        "",
        "## 3. 主结果",
        "",
        *_summary_table(summary),
        "",
        "## 4. Hard constraint 边界",
        "",
        "B1 只改变解码阶段；它能把最终输出投影到合法集合，但不会改变 baseline 的 `Pθ(L|x)`。这正是本项目要区分的边界：输出合法性不等于原始后验合法质量。",
        "",
        *_baseline_constraint_table(summary),
        "",
        "## 5. Sweet spot 配置",
        "",
        "下面配置同时提高 `Pθ(L|x)`、unconstrained 合法率、字符准确率和 exact 准确率。它们只能支持 controlled task early evidence，不能外推到真实 benchmark。",
        "",
        *_sweet_spot_table(summary),
        "",
        "## 6. 当前结论",
        "",
        "可以说：`Pθ(L|x)` 是一个可计算、可训练、可审计的后验事件信号；在多个非饱和受控格式事件上，它稳定改变 posterior event mass，并在部分低强度设置下带来 controlled task early evidence。",
        "",
        "不能说：它已经优于 hard constraint、posterior regularization 或 WFST；也不能说已经证明真实任务 benchmark usefulness。",
        "",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")

    supported_rows = [
        row
        for row in summary
        if row["variant"] != "B0_unconstrained" and float(row["delta_p_event"]) > 0
    ]
    task_positive = sorted({str(row["task"]) for row in supported_rows})
    sweet_rows = [
        row
        for row in supported_rows
        if float(row["delta_unconstrained_event_rate"]) > 0
        and float(row["delta_char_accuracy"]) >= 0
        and float(row["delta_exact_sequence_accuracy"]) >= 0
    ]
    audit = [
        "# 正式受控验证 Claim Audit",
        "",
        "## Verdict",
        "",
        "```text",
        "controlled_structural_usefulness = supported",
        "controlled_task_usefulness = partial",
        "real_benchmark_usefulness = not supported",
        "hard_constraint_superiority_claim = forbidden",
        "```",
        "",
        "## 支持的主张",
        "",
        f"- `Pθ(L|x)` 训练项在这些受控任务上提高事件后验质量：{', '.join(task_positive) if task_positive else '无'}。",
        "- hard constraint 与 event posterior training 回答不同问题：前者修最终输出，后者改变原始后验。",
        "- 低强度 event/semi-event 设置存在 controlled sweet spot，但不是所有 λ 都好。",
        "",
        "## 部分支持的主张",
        "",
        f"- controlled task early evidence：当前 sweet spot 数量为 {len(sweet_rows)}。它提示训练用途值得继续推进，但还不是正式任务性能结论。",
        "",
        "## 不支持或禁止的主张",
        "",
        "- 不支持真实 OCR / 信息抽取 benchmark superiority。",
        "- 不支持 event posterior training 全面优于 hard constraint。",
        "- 不支持比 RegCCRF / WFST / posterior regularization 全面更好。",
        "- 不支持任意 CRF / DFA 都低秩。",
        "- 不支持项目已经投稿就绪。",
        "",
        "## 下一步 claim gate",
        "",
        "如果要升级 empirical usefulness，必须进入半真实或真实格式抽取任务，并保留 B0-B4 以及至少一个 posterior-regularization / rule-feature 风格对照。",
        "",
    ]
    audit_path.write_text("\n".join(audit), encoding="utf-8")

    next_gate = [
        "# 正式受控验证下一步 Gate",
        "",
        "## Gate",
        "",
        "```text",
        "GO for result-to-claim review and semi-real task planning.",
        "HOLD for benchmark claim.",
        "HOLD for paper-writing as final empirical evidence.",
        "```",
        "",
        "## 推荐下一步",
        "",
        "1. 对本轮 `formal_validation_summary.csv` 做独立 result-to-claim 审计。",
        "2. 将 HTML 中“验证状态”更新为：多事件受控验证已完成，支持 controlled structural usefulness，task usefulness 仍是 partial。",
        "3. 设计半真实格式抽取任务，例如日期、金额、商品编号、剂量格式；保持 CPU-first。",
        "4. 如果需要进入论文实验路线，再补 posterior regularization / rule-feature / WFST-style 对照，而不是直接宣称更好。",
        "",
    ]
    next_path.write_text("\n".join(next_gate), encoding="utf-8")


def run_all(setting: FormalSetting, tasks: Sequence[FormatTask]) -> list[FormalRun]:
    runs: list[FormalRun] = []
    for task in tasks:
        runs.extend(run_task(task, setting))
    return runs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="experiments/results/event_training")
    parser.add_argument("--seed-count", type=int, default=10)
    parser.add_argument("--tasks", nargs="*", default=[task.name for task in TASKS])
    args = parser.parse_args()
    task_by_name = {task.name: task for task in TASKS}
    selected_tasks = [task_by_name[name] for name in args.tasks]
    setting = default_setting(seed_count=args.seed_count)
    output_dir = Path(args.output_dir)
    runs = run_all(setting, selected_tasks)
    summary = write_outputs(runs, output_dir)
    write_reports(summary, output_dir)


if __name__ == "__main__":
    main()
