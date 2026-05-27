"""Preflight checks before running the AutoDL/HPC smoke suite.

This script does not launch experiments. It verifies that the frozen local
protocol can be executed on a fresh machine and that outputs will be routed to
``experiments/runs`` rather than curated result directories.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


REQUIRED_MODULES = (
    "tensor_crf_jmlr",
    "torch",
    "pandas",
    "openpyxl",
    "yaml",
)


DATA_SHA256 = {
    "data/raw/online_retail.xlsx": "ef60e854dd93a8a60932a547ebd8c0dca63e33251f2dbbdcb8f2abb2aff3e272",
    "data/raw/wnut17/train.conll": "731820e13f71af324c6b55a1575ec2ce59fbaa2a0806f8f0400b98d56cd6a7a5",
    "data/raw/wnut17/dev.conll": "e053b752b8155113ca66e7db08af5f2f5f43ab993694e4774f1ec5bad42312d8",
    "data/raw/wnut17/test.conll": "2aa79b764e56ec9264a1b30fdd9b70195bd00ff400b62edd8f399d5f13c178f0",
}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"YAML file must be a mapping: {path}")
    return payload


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def check_module(name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(name)
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"name": name, "ok": False, "error": repr(exc)}
    return {"name": name, "ok": True, "version": getattr(module, "__version__", None)}


def check_suite(suite_path: Path) -> list[str]:
    errors: list[str] = []
    suite = load_yaml(suite_path)
    tasks = suite.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return [f"{suite_path}: tasks must be a non-empty list"]
    for task in tasks:
        if not isinstance(task, dict):
            errors.append(f"{suite_path}: task must be a mapping")
            continue
        for key in ("id", "script", "config", "output_subdir", "enabled"):
            if key not in task:
                errors.append(f"{suite_path}: task missing {key}")
        script = Path(str(task.get("script", "")))
        config = Path(str(task.get("config", "")))
        output_subdir = str(task.get("output_subdir", ""))
        if not script.is_file():
            errors.append(f"{suite_path}: missing script {script}")
        if not config.is_file():
            errors.append(f"{suite_path}: missing config {config}")
        if output_subdir.startswith("results") or "experiments/results" in output_subdir.replace("\\", "/"):
            errors.append(f"{suite_path}: output_subdir must not target curated results: {output_subdir}")
    return errors


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="experiments/suites/autodl_smoke.yaml")
    parser.add_argument("--data-file", default="", help="Optional extra data file to hash in the report.")
    parser.add_argument("--report", default="experiments/runs/preflight/autodl_preflight.json")
    parser.add_argument("--strict-cuda", action="store_true")
    args = parser.parse_args()

    suite_path = Path(args.suite)
    data_file = Path(args.data_file) if args.data_file else None
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    modules = [check_module(name) for name in REQUIRED_MODULES]
    errors = [f"module import failed: {item['name']} {item.get('error')}" for item in modules if not item["ok"]]
    if sys.version_info < (3, 10):
        errors.append(f"Python >= 3.10 required, got {sys.version}")
    data_hashes: dict[str, str | None] = {}
    for raw_path, expected_hash in DATA_SHA256.items():
        path = Path(raw_path)
        if not path.is_file():
            errors.append(f"missing required data file: {path}")
            data_hashes[raw_path] = None
            continue
        actual_hash = sha256_file(path).lower()
        data_hashes[raw_path] = actual_hash
        if actual_hash != expected_hash:
            errors.append(f"data hash mismatch for {path}: expected {expected_hash}, got {actual_hash}")
    extra_data_hash = None
    if data_file is not None:
        if not data_file.is_file():
            errors.append(f"missing extra data file: {data_file}")
        else:
            extra_data_hash = sha256_file(data_file)
    if not suite_path.is_file():
        errors.append(f"missing suite file: {suite_path}")
    else:
        errors.extend(check_suite(suite_path))

    torch_info: dict[str, Any] = {}
    try:
        import torch

        torch_info = {
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_count": int(torch.cuda.device_count()),
        }
        if args.strict_cuda and not torch.cuda.is_available():
            errors.append("strict CUDA requested but torch.cuda.is_available() is false")
    except Exception as exc:  # pragma: no cover - diagnostic path
        errors.append(f"torch diagnostic failed: {exc!r}")

    payload = {
        "status": "PASS" if not errors else "FAIL",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "git_commit": git_commit(),
        "suite": str(suite_path),
        "data_file": str(data_file) if data_file is not None else None,
        "data_sha256": extra_data_hash,
        "required_data_sha256": data_hashes,
        "modules": modules,
        "torch": torch_info,
        "errors": errors,
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
