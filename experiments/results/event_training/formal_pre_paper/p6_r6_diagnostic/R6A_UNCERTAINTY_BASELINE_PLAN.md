# R6a Uncertainty Baseline Reanalysis Plan

The existing downloaded R6a `diagnostic_cases.csv` does not contain all uncertainty baseline fields needed for a fair comparison.

Missing fields:

- `baseline_token_marginal_entropy`
- `baseline_sequence_entropy`
- `baseline_viterbi_margin`
- `baseline_max_sequence_prob`
- `baseline_neg_log_viterbi_prob`

Implemented preparation:

- `src/tensor_crf_jmlr/event_training/posterior_event_diagnostic.py` now writes Viterbi probability, Viterbi margin, token marginal entropy, and sequence entropy fields on rerun.
- This script will produce AUROC/AUPRC/Spearman/quantile-gap tables once those enriched cases are available.

Rerun command:

```powershell
python -m tensor_crf_jmlr.event_training.posterior_event_diagnostic --output-dir experiments/runs/local_checks/r6a_uncertainty_enriched --seed-count 10 --semi-tasks product_code amount date dose --real-tasks stock_5d invoice_6d invoice_c6d
python scripts/analysis/reanalyze_r6a_uncertainty_baselines.py --cases experiments/runs/local_checks/r6a_uncertainty_enriched/diagnostic_cases.csv --output-dir experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic
```

Claim boundary: do not report uncertainty-baseline superiority until the enriched rerun is produced and audited.
