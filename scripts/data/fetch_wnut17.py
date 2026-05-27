"""Fetch the frozen WNUT17 BIO/NER slice from GitHub.

This script only downloads small public dataset files used for the canonical
BIO/NER protocol. It does not run experiments.
"""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve


FILES = {
    "train.conll": "https://raw.githubusercontent.com/leondz/emerging_entities_17/master/wnut17train.conll",
    "dev.conll": "https://raw.githubusercontent.com/leondz/emerging_entities_17/master/emerging.dev.conll",
    "test.conll": "https://raw.githubusercontent.com/leondz/emerging_entities_17/master/emerging.test.annotated",
}


def main() -> None:
    output_dir = Path("data/raw/wnut17")
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, url in FILES.items():
        path = output_dir / filename
        print(f"FETCH {url} -> {path}")
        urlretrieve(url, path)


if __name__ == "__main__":
    main()
