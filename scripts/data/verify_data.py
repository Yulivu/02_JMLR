"""Verify required offline data files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


REQUIRED_FILES = {
    "data/raw/online_retail.xlsx": "ef60e854dd93a8a60932a547ebd8c0dca63e33251f2dbbdcb8f2abb2aff3e272",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="Fail on missing or mismatched required data.")
    args = parser.parse_args()

    errors: list[str] = []
    for raw_path, expected_hash in REQUIRED_FILES.items():
        path = Path(raw_path)
        if not path.is_file():
            errors.append(f"missing {path}")
            continue
        actual_hash = sha256_file(path)
        if actual_hash.lower() != expected_hash:
            errors.append(f"hash mismatch {path}: expected {expected_hash}, got {actual_hash}")
            continue
        print(f"PASS {path} {actual_hash}")

    if errors:
        for error in errors:
            print(f"FAIL {error}")
        if args.strict:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
