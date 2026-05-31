"""Lightweight checks for the draft LaTeX paper skeleton."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def cite_keys(tex: str) -> set[str]:
    keys: set[str] = set()
    for match in re.finditer(r"\\cite[a-zA-Z]*\{([^}]+)\}", tex):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def bib_keys(bib: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,\s]+)", bib))


def input_paths(tex: str) -> list[Path]:
    paths = []
    for match in re.finditer(r"\\input\{([^}]+)\}", tex):
        paths.append(PAPER / f"{match.group(1)}.tex")
    return paths


def main() -> None:
    main_tex = read(PAPER / "main.tex")
    missing_inputs = [path for path in input_paths(main_tex) if not path.is_file()]
    if missing_inputs:
        raise AssertionError(f"missing input files: {missing_inputs}")

    all_tex = main_tex + "\n" + "\n".join(read(path) for path in (PAPER / "sections").glob("*.tex"))
    table_inputs = [path for path in input_paths(all_tex) if "tables" in path.parts]
    missing_tables = [path for path in table_inputs if not path.is_file()]
    if missing_tables:
        raise AssertionError(f"missing generated table files: {missing_tables}")

    cited = cite_keys(all_tex)
    available = bib_keys(read(PAPER / "references.bib"))
    missing_cites = sorted(cited - available)
    unused_bib = sorted(available - cited)
    if missing_cites:
        raise AssertionError(f"missing bib entries: {missing_cites}")

    print("PASS paper skeleton check")
    print(f"cited_keys={len(cited)}")
    print(f"unused_bib={unused_bib}")


if __name__ == "__main__":
    main()
