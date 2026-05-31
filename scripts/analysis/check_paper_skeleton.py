"""Lightweight checks for the draft LaTeX paper skeleton."""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "paper"
CURATED_TABLES = ROOT / "experiments" / "results" / "paper_tables"

FORBIDDEN_POSITIVE_PATTERNS = [
    r"(?<!not )(?<!no )benchmark superiority",
    r"\bSOTA\b",
    r"\boutperform(s|ed|ing)?\b",
    r"\bdominates?\b",
    r"\breplaces?\b",
    r"\bnew product-automaton inference algorithm\b",
    r"\bwe define\b",
]


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


def labels(tex: str) -> set[str]:
    return set(re.findall(r"\\label\{([^}]+)\}", tex))


def label_list(tex: str) -> list[str]:
    return re.findall(r"\\label\{([^}]+)\}", tex)


def refs(tex: str) -> set[str]:
    found: set[str] = set()
    for command in ("ref", "eqref", "autoref"):
        for match in re.finditer(rf"\\{command}\{{([^}}]+)\}}", tex):
            found.add(match.group(1))
    return found


def tabular_column_count(spec: str) -> int:
    cleaned = re.sub(r"@\{[^}]*\}", "", spec)
    cleaned = re.sub(r"[| ]", "", cleaned)
    return sum(1 for ch in cleaned if ch in "lcrpmbX")


def check_table_fragment(path: Path) -> None:
    text = read(path)
    match = re.search(r"\\begin\{tabular\}\{([^}]*)\}", text)
    if not match:
        raise AssertionError(f"missing tabular environment in {path}")
    n_cols = tabular_column_count(match.group(1))
    if n_cols > 10:
        raise AssertionError(f"{path} has {n_cols} columns; likely too wide for the draft page")

    csv_path = CURATED_TABLES / f"{path.stem}.csv"
    if csv_path.is_file():
        with csv_path.open(newline="", encoding="utf-8") as handle:
            csv_cols = len(next(csv.reader(handle)))
        if csv_cols != n_cols:
            raise AssertionError(f"{path} has {n_cols} LaTeX columns but {csv_path} has {csv_cols}")


def check_claim_wording(tex: str) -> None:
    for pattern in FORBIDDEN_POSITIVE_PATTERNS:
        for match in re.finditer(pattern, tex, flags=re.IGNORECASE):
            start = max(0, match.start() - 80)
            end = min(len(tex), match.end() + 80)
            context = tex[start:end].replace("\n", " ")
            if any(marker in context.lower() for marker in ("not ", "no ", "does not", "do not", "cannot", "forbidden")):
                continue
            raise AssertionError(f"risky positive wording matched {pattern!r}: {context}")


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
    for table in table_inputs:
        check_table_fragment(table)

    cited = cite_keys(all_tex)
    available = bib_keys(read(PAPER / "references.bib"))
    missing_cites = sorted(cited - available)
    unused_bib = sorted(available - cited)
    if missing_cites:
        raise AssertionError(f"missing bib entries: {missing_cites}")

    all_labels = label_list(all_tex)
    duplicate_labels = sorted({label for label in all_labels if all_labels.count(label) > 1})
    if duplicate_labels:
        raise AssertionError(f"duplicate labels: {duplicate_labels}")
    missing_refs = sorted(refs(all_tex) - labels(all_tex))
    if missing_refs:
        raise AssertionError(f"missing labels for refs: {missing_refs}")
    check_claim_wording(all_tex)

    print("PASS paper skeleton check")
    print(f"cited_keys={len(cited)}")
    print(f"labels={len(labels(all_tex))}")
    print(f"table_fragments={len(table_inputs)}")
    print(f"unused_bib={unused_bib}")


if __name__ == "__main__":
    main()
