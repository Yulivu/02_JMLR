"""Run or inspect a reproducible experiment suite."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Suite must be a YAML mapping: {path}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="experiments/suites/current_repro.yaml")
    parser.add_argument("--task")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    suite_path = Path(args.suite)
    suite = load_yaml(suite_path)
    tasks = suite.get("tasks", [])
    if not isinstance(tasks, list):
        raise ValueError("Suite field 'tasks' must be a list.")

    selected = []
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each suite task must be a mapping.")
        if args.task and task.get("id") != args.task:
            continue
        if not args.task and not task.get("enabled", False):
            continue
        selected.append(task)

    if args.task and not selected:
        raise ValueError(f"Task not found: {args.task}")

    for task in selected:
        command = [
            sys.executable,
            str(task["script"]),
            "--config",
            str(task["config"]),
            "--out-dir",
            str(Path("experiments/runs") / str(task["output_subdir"])),
        ]
        print(" ".join(command))
        if not args.dry_run:
            subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
