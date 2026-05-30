# R6a Uncertainty Boundary Audit

Updated: 2026-05-30

## Required Table Columns

The paper-ready uncertainty table must include:

| Required column | Current source |
|---|---|
| event risk `1 - P_theta(L|x)` | `baseline_p_event` in R6a cases; `event_risk_1_minus_p` row in `r6a_uncertainty_baseline_metrics.csv` |
| token marginal entropy | `baseline_token_marginal_entropy` |
| sequence entropy | `baseline_sequence_entropy` |
| Viterbi margin inverse | `baseline_viterbi_margin` transformed by inverse sign |
| max sequence probability inverse | `baseline_max_sequence_prob` transformed by inverse sign |
| negative log Viterbi probability | `baseline_neg_log_viterbi_prob` |
| AUROC | `auroc_exact_error` |
| AUPRC | `auprc_exact_error` |
| Spearman char error | `spearman_char_error` |
| top/bottom quantile risk | `top20_risk_exact_error`, `bottom20_risk_exact_error`, `risk_gap` |
| correlation between event risk and generic uncertainty | `r6a_event_uncertainty_correlations.csv` after rerun of analysis script |
| within-bin residual / complementarity check | `r6a_uncertainty_complementarity.csv` |

## Interpretation Boundary

Allowed:

```text
In the evaluated field-style diagnostics, event risk has positive exact-error ranking signal and is interpretable as rule-specific posterior consistency.
```

Required boundary:

```text
Generic uncertainty baselines are stronger overall in the current R6a reanalysis, and within-bin complementarity is mixed. Do not claim uncertainty replacement, calibration, dominance, or robust residual predictive power.
```

## Refresh Command

```powershell
python scripts/analysis/reanalyze_r6a_uncertainty_baselines.py --cases experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/r6a_field_diagnostic_formal/diagnostic_cases.csv --output-dir experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic
```

If the cases file is unavailable locally, use the committed `R6A_UNCERTAINTY_BASELINE_REANALYSIS.md` and mark the new correlation table pending rather than inventing values.
