"""Run a configured event-training task.

This is intentionally a thin orchestration layer. Reusable experiment logic stays
under ``tensor_crf_jmlr.event_training``; this script only resolves config,
routes output to ``experiments/runs``, and records run provenance.
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Config must be a YAML mapping: {path}")
    return payload


def parse_override(raw: str) -> tuple[list[str], Any]:
    if "=" not in raw:
        raise ValueError(f"Override must use key=value syntax: {raw}")
    key, value = raw.split("=", 1)
    parsed: Any = yaml.safe_load(value)
    return key.split("."), parsed


def apply_override(config: dict[str, Any], raw: str) -> None:
    keys, value = parse_override(raw)
    cursor = config
    for key in keys[:-1]:
        child = cursor.setdefault(key, {})
        if not isinstance(child, dict):
            raise ValueError(f"Cannot set nested override under non-mapping key: {key}")
        cursor = child
    cursor[keys[-1]] = value


def cli_args_from_mapping(mapping: dict[str, Any]) -> list[str]:
    args: list[str] = []
    for key, value in mapping.items():
        flag = f"--{key.replace('_', '-')}"
        if isinstance(value, bool):
            if value:
                args.append(flag)
            continue
        if value is None:
            continue
        if isinstance(value, list):
            args.append(flag)
            args.extend(str(item) for item in value)
            continue
        args.extend([flag, str(value)])
    return args


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--set", dest="overrides", action="append", default=[])
    args = parser.parse_args()

    config_path = Path(args.config)
    out_dir = Path(args.out_dir)
    config = load_yaml(config_path)
    for override in args.overrides:
        apply_override(config, override)

    module = config.get("module")
    if not isinstance(module, str) or not module:
        raise ValueError("Config must include non-empty 'module'.")

    module_args = config.get("args", {})
    if not isinstance(module_args, dict):
        raise ValueError("Config field 'args' must be a mapping.")
    module_args = dict(module_args)
    module_args["output_dir"] = str(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)
    resolved_config_path = out_dir / "resolved_config.yaml"
    metadata_path = out_dir / "run_metadata.json"
    summary_path = out_dir / "summary.md"

    command = [sys.executable, "-m", module, *cli_args_from_mapping(module_args)]
    resolved_config_path.write_text(
        yaml.safe_dump(config, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    started_at = datetime.now(timezone.utc)
    metadata = {
        "config": str(config_path),
        "out_dir": str(out_dir),
        "command": command,
        "started_at_utc": started_at.isoformat(),
        "platform": platform.platform(),
        "python": sys.version,
        "git_commit": git_commit(),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    completed = subprocess.run(command, text=True)
    ended_at = datetime.now(timezone.utc)
    metadata["ended_at_utc"] = ended_at.isoformat()
    metadata["duration_seconds"] = (ended_at - started_at).total_seconds()
    metadata["returncode"] = completed.returncode
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    status = "passed" if completed.returncode == 0 else "failed"
    summary_path.write_text(
        "\n".join(
            [
                f"# Event Training Task: {config.get('id', config_path.stem)}",
                "",
                f"- status: {status}",
                f"- module: `{module}`",
                f"- config: `{config_path}`",
                f"- output: `{out_dir}`",
                f"- duration_seconds: {metadata['duration_seconds']:.2f}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
