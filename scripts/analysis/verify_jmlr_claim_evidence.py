"""Verify high-risk JMLR claim/table numbers against curated CSV evidence."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "results"
PUBLIC = RESULTS / "event_training" / "formal_pre_paper" / "public_sequence_labeling"
PAPER_TABLES = RESULTS / "paper_tables"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rounded(value: str) -> str:
    return f"{float(value):.4f}"


def require_equal(label: str, observed: str, expected: str) -> None:
    if observed != expected:
        raise AssertionError(f"{label}: observed {observed!r}, expected {expected!r}")


def row_by(rows: list[dict[str, str]], key: str, value: str) -> dict[str, str]:
    for row in rows:
        if row[key] == value:
            return row
    raise AssertionError(f"missing row where {key}={value!r}")


def verify_public_multiseed_table() -> None:
    curated = read_rows(PUBLIC / "conll2000_public_multiseed_formal_summary.csv")
    table = read_rows(PAPER_TABLES / "table_6_public_conll2000.csv")
    for variant in ("B0_unconstrained", "B4_semi_event_0.1"):
        c = row_by(curated, "variant", variant)
        t = row_by(table, "variant", variant)
        require_equal(f"{variant} seeds", t["seeds"], c["seeds"])
        require_equal(f"{variant} P_BIO_mean", t["P_BIO_mean"], rounded(c["P_BIO_mean"]))
        require_equal(f"{variant} P_BIO_std", t["P_BIO_std"], rounded(c["P_BIO_std"]))
        require_equal(
            f"{variant} hidden_conflict_mean",
            t["hidden_conflict_mean"],
            rounded(c["hidden_conflict_mean"]),
        )
        require_equal(f"{variant} B7_legal_mean", t["B7_legal_mean"], rounded(c["B7_legal_mean"]))
        require_equal(f"{variant} token_acc_mean", t["token_acc_mean"], rounded(c["token_acc_mean"]))
        require_equal(f"{variant} span_F1_mean", t["span_F1_mean"], rounded(c["span_F1_mean"]))


def verify_public_uncertainty_table() -> None:
    curated = read_rows(PUBLIC / "conll2000_public_multiseed_uncertainty_metrics.csv")
    table = read_rows(PAPER_TABLES / "table_7_public_uncertainty.csv")
    by_key = {(row["variant"], row["baseline"]): row for row in curated}
    for row in table:
        c = by_key[(row["variant"], row["score"])]
        require_equal(f"{row['variant']} {row['score']} AUROC", row["AUROC_exact"], rounded(c["auroc_exact_error"]))
        require_equal(f"{row['variant']} {row['score']} AUPRC", row["AUPRC_exact"], rounded(c["auprc_exact_error"]))
        require_equal(
            f"{row['variant']} {row['score']} Spearman",
            row["Spearman_token_error"],
            rounded(c["spearman_token_error"]),
        )
        require_equal(f"{row['variant']} {row['score']} gap", row["exact_risk_gap"], rounded(c["risk_gap_exact"]))


def verify_claim_summary_c13() -> None:
    claims = read_rows(PAPER_TABLES / "table_1_claim_summary.csv")
    c13 = row_by(claims, "claim_id", "C13")
    required_tokens = [
        "0.9837 +/- 0.0011",
        "0.0133",
        "0.7973",
        "0.9885 +/- 0.0063",
        "0.0123",
        "0.7918",
        "1.0000",
        "token/span metrics decrease",
    ]
    for token in required_tokens:
        if token not in c13["evidence"] and token not in c13["boundary"]:
            raise AssertionError(f"C13 missing expected token: {token}")


def main() -> None:
    verify_public_multiseed_table()
    verify_public_uncertainty_table()
    verify_claim_summary_c13()
    print("PASS jmlr claim evidence verification")


if __name__ == "__main__":
    main()
