# Reproducibility Package Status

Date: 2026-05-31

## Verdict

```text
prepaper_reproducibility_status = review_ready
submission_reproducibility_status = not_final_packaged
```

The repository now has enough curated provenance for external review and
manuscript drafting. It is not yet a final submission artifact because final
LaTeX, BibTeX, final table selection, and archival raw-run packaging are not
frozen.

## Reproducibility Spine

| Layer | Status | Canonical files |
|---|---|---|
| source package | done | `src/tensor_crf_jmlr/` |
| configs | done for current evidence | `experiments/configs/exp7/`, formal suite YAMLs |
| raw runs | intentionally untracked | `experiments/runs/` ignored by Git |
| curated results | done for current evidence | `experiments/results/event_training/formal_pre_paper/` |
| generated paper-prep tables | done for review | `experiments/results/paper_tables/` |
| data provenance | mostly done | `data/DATA_MANIFEST.md`, fetch/verify scripts |
| claim/evidence verifier | added | `scripts/analysis/verify_jmlr_claim_evidence.py` |
| final manuscript citation audit | pending | requires final `.tex` and `.bib` |
| final paper-claim audit | pending | requires final `.tex` |

## Commands To Reproduce Current Curated Tables

```powershell
python scripts/analysis/curate_jmlr_cpu_upgrade_results.py --public-multiseed-run experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
python scripts/analysis/generate_paper_tables.py
python scripts/analysis/verify_jmlr_claim_evidence.py
```

The public multiseed raw bundle is local and ignored by Git:

```text
experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
```

Curated outputs are tracked:

```text
experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_MULTISEED_FORMAL_AUDIT.md
experiments/results/event_training/formal_pre_paper/public_sequence_labeling/conll2000_public_multiseed_*.csv
experiments/results/paper_tables/table_6_public_conll2000.*
experiments/results/paper_tables/table_7_public_uncertainty.*
```

## Submission Package Must Still Freeze

Before submission:

1. record the final Git commit in the paper and reproducibility notes;
2. decide whether to archive raw `experiments/runs/` bundles externally;
3. verify data license/citation text for CoNLL2000, WNUT17, and UCI retail;
4. run final proof, citation, and paper-claim audits on the actual LaTeX;
5. regenerate paper tables once after final claim edits;
6. confirm `python -m pytest` and `python -m ruff check src scripts` on the final commit.

## Explicit Non-Claims

This package does not establish benchmark superiority, optimized runtime,
calibration, general task-improvement from event loss, or a new product
automaton inference algorithm.
