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
| table-generation scripts | partial | audit scripts exist; final paper table script still needed |
| external proof/claim review | pending | next step |

## Paper-Ready Requirements

Before writing final experimental section:

1. Create a single script or Make target that regenerates final paper tables from curated CSVs.
2. Record the final commit hash for every table.
3. Ensure data licenses/citations are listed.
4. Ensure no raw `experiments/runs/` output is required for paper readers unless archived separately.
5. Export appendix tables from curated result files, not hand-copied numbers.

## Current Decision

```text
The repo is reproducible enough for pre-paper review.
It is not yet packaged as a final submission artifact.
```
