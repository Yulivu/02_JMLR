# Paper Claim / Evidence Audit

Date: 2026-05-31

## Verdict

```text
claim_table_status = PASS_WITH_SCOPE
paper_table_status = PASS_AFTER_TABLE7_FIX
final_manuscript_claim_audit = pending_until_latex_exists
```

This audit checks the current repository claim table, external-review packet,
and generated paper-prep tables against curated evidence files. It is not a
final paper-to-evidence audit because no final LaTeX manuscript exists yet.

## Verification Command

```powershell
python scripts/analysis/verify_jmlr_claim_evidence.py
```

Result:

```text
PASS jmlr claim evidence verification
```

## High-Risk Claims Checked

| Claim/table | Evidence file | Status | Boundary |
|---|---|---|---|
| C13 public CoNLL2000 multiseed | `conll2000_public_multiseed_formal_summary.csv`; `table_6_public_conll2000.csv` | pass | B4 raises event mass but lowers mean token/span metrics |
| public uncertainty table | `conll2000_public_multiseed_uncertainty_metrics.csv`; `table_7_public_uncertainty.csv` | pass after generator fix | event risk positive, generic uncertainty stronger |
| C15 R7 derisk | `r7_sensitivity_derisk_key_rows.csv`; `table_9_r7_sensitivity.csv` | pass by audited row presence | event loss can be harmful when rule is misleading |
| C8 R6a uncertainty boundary | `r6a_uncertainty_baseline_metrics.csv`; `table_4_diagnostic_ranking.csv` | pass by existing curated audit | no uncertainty dominance or calibration |
| C14 B7 constrained-product | `b7_constrained_product_formal_summary.csv`; `table_8_b7_constrained_product.csv` | pass by existing curated audit | constrained-product Viterbi only, not full WFST |

## Issue Found And Fixed

`table_7_public_uncertainty` was still generated from the older one-seed public
uncertainty CSV while `table_6_public_conll2000` and the external review packet
had moved to the full three-seed public case. The table generator now prefers:

```text
conll2000_public_multiseed_uncertainty_metrics.csv
```

when available, and falls back to the one-seed file only when the multiseed
file is absent.

## Smoke / Formal Separation

`table_6_public_conll2000` contains formal evidence only. The tiny multiseed
smoke appears only in:

```text
table_6a_public_conll2000_smoke.*
CONLL2000_PUBLIC_MULTISEED_TINY_SMOKE_AUDIT.md
```

and is labeled:

```text
plumbing smoke only; not formal evidence
```

## Final Submission Gate

After the final manuscript is written, run a zero-context paper-claim audit over
the final `.tex` files and curated CSV/JSON evidence. This repository-level
audit is sufficient for drafting and external review, but not a substitute for
the final manuscript audit.
