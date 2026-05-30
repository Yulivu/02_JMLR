"""Run or inspect a reproducible experiment suite."""

from __future__ import annotations

import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    parser.add_argument(
        "--jobs",
        type=int,
        default=1,
        help="Number of suite tasks to run concurrently. Each task must write to a distinct output_subdir.",
    )
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

    commands = []
    for task in selected:
        command = [
            sys.executable,
            str(task["script"]),
            "--config",
            str(task["config"]),
            "--out-dir",
            str(Path("experiments/runs") / str(task["output_subdir"])),
        ]
        commands.append((task, command))
        print(" ".join(command))

    if args.dry_run:
        return

    jobs = max(1, min(args.jobs, len(commands)))
    if jobs == 1:
        for _task, command in commands:
            subprocess.run(command, check=True)
        return

    def run_command(task: dict[str, Any], command: list[str]) -> tuple[str, int]:
        completed = subprocess.run(command, check=False)
        return str(task.get("id", command[1])), completed.returncode

    failures: list[tuple[str, int]] = []
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = [executor.submit(run_command, task, command) for task, command in commands]
        for future in as_completed(futures):
            task_id, returncode = future.result()
            if returncode != 0:
                failures.append((task_id, returncode))

    if failures:
        formatted = ", ".join(f"{task_id}={returncode}" for task_id, returncode in failures)
        raise subprocess.CalledProcessError(failures[0][1], f"suite failures: {formatted}")


if __name__ == "__main__":
    main()
