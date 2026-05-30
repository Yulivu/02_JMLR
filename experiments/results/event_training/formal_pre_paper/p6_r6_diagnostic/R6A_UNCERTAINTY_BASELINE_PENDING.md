# R6a Uncertainty Baseline Reanalysis Pending

The requested R6a cases file is not available locally, so no new uncertainty table was generated.

Missing cases file:

- `experiments\runs\autodl_jmlr_block\p6_r6_diagnostic\r6a_field_diagnostic_formal\diagnostic_cases.csv`

Expected source:

```text
experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/r6a_field_diagnostic_formal/diagnostic_cases.csv
```

This raw run folder is intentionally not committed. Restore it from the audited run bundle, then rerun:

```powershell
python scripts/analysis/reanalyze_r6a_uncertainty_baselines.py --cases experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/r6a_field_diagnostic_formal/diagnostic_cases.csv --output-dir experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic
```

Until then, use the committed `R6A_UNCERTAINTY_BASELINE_REANALYSIS.md` and mark the event-risk/generic-uncertainty correlation table pending.
