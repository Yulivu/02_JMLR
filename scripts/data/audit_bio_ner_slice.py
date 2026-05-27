"""Audit the frozen BIO/NER slice before formal experiment implementation."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from tensor_crf_jmlr.event_training.bio_event import bio_sequence_allowed
from tensor_crf_jmlr.event_training.data_utils import read_conll


@dataclass(frozen=True)
class SplitAudit:
    split: str
    path: str
    sentences: int
    tokens: int
    min_len: int
    max_len: int
    mean_len: float
    raw_labels: list[str]
    normalized_labels: list[str]
    raw_illegal_gold_sequences: int
    normalized_illegal_gold_sequences: int
    top_raw_labels: list[tuple[str, int]]


def normalize_label(label: str) -> str:
    if label == "O":
        return label
    prefix, sep, label_type = label.partition("-")
    if sep != "-" or prefix not in {"B", "I"}:
        raise ValueError(f"unexpected BIO label: {label!r}")
    return f"{prefix}-{label_type.upper()}"


def audit_split(split: str, path: Path) -> SplitAudit:
    dataset = read_conll(path)
    lengths = [len(tokens) for tokens in dataset.tokens]
    raw_counter = Counter(label for labels in dataset.labels for label in labels)
    normalized_labels = [[normalize_label(label) for label in labels] for labels in dataset.labels]
    normalized_counter = Counter(label for labels in normalized_labels for label in labels)
    raw_illegal = sum(not bio_sequence_allowed(labels) for labels in dataset.labels)
    normalized_illegal = sum(not bio_sequence_allowed(labels) for labels in normalized_labels)
    return SplitAudit(
        split=split,
        path=str(path),
        sentences=len(dataset.tokens),
        tokens=sum(lengths),
        min_len=min(lengths) if lengths else 0,
        max_len=max(lengths) if lengths else 0,
        mean_len=sum(lengths) / max(1, len(lengths)),
        raw_labels=sorted(raw_counter),
        normalized_labels=sorted(normalized_counter),
        raw_illegal_gold_sequences=raw_illegal,
        normalized_illegal_gold_sequences=normalized_illegal,
        top_raw_labels=raw_counter.most_common(20),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/raw/wnut17")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    required = {
        "train": data_dir / "train.conll",
        "dev": data_dir / "dev.conll",
        "test": data_dir / "test.conll",
    }
    missing = [str(path) for path in required.values() if not path.is_file()]
    if missing:
        raise SystemExit("Missing WNUT17 files: " + ", ".join(missing))

    audits = [audit_split(split, path) for split, path in required.items()]
    payload = [asdict(audit) for audit in audits]
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    print(text)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")

    illegal = sum(audit.normalized_illegal_gold_sequences for audit in audits)
    if illegal:
        raise SystemExit(f"BIO audit failed: {illegal} normalized gold sequences are illegal")


if __name__ == "__main__":
    main()
