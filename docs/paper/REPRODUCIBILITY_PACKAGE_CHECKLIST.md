# Reproducibility Package Checklist

Generated: 2026-05-28

## Purpose

Before paper submission, the repository should expose exact code, configs, data notes, run provenance, and table-generation scripts for every claim.

## Required Items

| Item | Status | Notes |
|---|---|---|
| source package under `src/` | done | `tensor_crf_jmlr` |
| experiment configs | mostly done | R5, R1/R2/R4, R6a, R8 frozen |
| suite files | mostly done | formal suites exist |
| raw run ignore policy | done | `experiments/runs/` ignored |
| curated results | mostly done | formal_pre_paper audits exist |
| run metadata | done | `run_metadata.json` in bundles |
| data notes | partial | WNUT and retail notes exist; final paper citation notes need checking |
| exact commit references | partial | commits in run metadata; final table should list them |
| table-generation scripts | done-for-review | `scripts/analysis/generate_paper_tables.py` regenerates `experiments/results/paper_tables/` from curated audit CSVs and `docs/paper/FINAL_CLAIM_TABLE.md` |
| external proof/claim review | pending | next step |

## Paper-Ready Requirements

Before writing final experimental section:

1. Re-run `python scripts/analysis/generate_paper_tables.py` after any curated-result change.
2. Record the final submission commit hash for every table.
3. Ensure data licenses/citations are listed.
4. Ensure no raw `experiments/runs/` output is required for paper readers unless archived separately.
5. Export appendix tables from curated result files, not hand-copied numbers.
6. Freeze an external review packet response and mark any required changes before manuscript writing.

## Current Decision

```text
The repo is reproducible enough for pre-paper review.
It is not yet packaged as a final submission artifact.
```

## Current Table Pipeline

The current review-stage table pipeline is:

```text
curated audit CSVs + docs/paper/FINAL_CLAIM_TABLE.md -> scripts/analysis/generate_paper_tables.py -> experiments/results/paper_tables/
```

Generated outputs:

- `experiments/results/paper_tables/table_1_claim_summary.*`
- `experiments/results/paper_tables/table_2_r5_wnut17.*`
- `experiments/results/paper_tables/table_3_event_training_signal.*`
- `experiments/results/paper_tables/table_4_diagnostic_ranking.*`
- `experiments/results/paper_tables/table_5_complexity_scaling.*`

These tables are ready for external review and paper outlining. They are not yet final camera-ready tables because final provenance, citations, and external proof/claim review are still pending.
