"""Audit local experiment run bundles for the pre-paper gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_BUNDLE_FILES = (
    "resolved_config.yaml",
    "run_metadata.json",
    "summary.md",
)


def audit_bundle(path: Path) -> list[str]:
    errors: list[str] = []
    for filename in REQUIRED_BUNDLE_FILES:
        if not (path / filename).is_file():
            errors.append(f"{path}: missing {filename}")

    metadata_path = path / "run_metadata.json"
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("returncode") != 0:
            errors.append(f"{path}: returncode is {metadata.get('returncode')}")
        for key in ("command", "started_at_utc", "ended_at_utc", "duration_seconds", "git_commit"):
            if key not in metadata:
                errors.append(f"{path}: metadata missing {key}")

    result_files = [
        candidate
        for candidate in path.iterdir()
        if candidate.is_file()
        and candidate.name not in REQUIRED_BUNDLE_FILES
        and candidate.suffix in {".json", ".csv", ".md"}
    ]
    has_runs = any("runs" in file.stem or "cases" in file.stem for file in result_files)
    has_summary = any("summary" in file.stem for file in result_files)
    if not has_runs:
        errors.append(f"{path}: missing runner-produced runs/cases file")
    if not has_summary:
        errors.append(f"{path}: missing runner-produced summary file")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", default="experiments/runs/local_checks")
    parser.add_argument("--require", nargs="*", default=[])
    args = parser.parse_args()

    runs_dir = Path(args.runs_dir)
    errors: list[str] = []
    for name in args.require:
        bundle = runs_dir / name
        if not bundle.is_dir():
            errors.append(f"{bundle}: missing required run bundle")
            continue
        errors.extend(audit_bundle(bundle))

    if not args.require:
        for bundle in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
            errors.extend(audit_bundle(bundle))

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        raise SystemExit(1)

    checked = args.require or [path.name for path in sorted(runs_dir.iterdir()) if path.is_dir()]
    for name in checked:
        print(f"PASS {runs_dir / name}")


if __name__ == "__main__":
    main()
