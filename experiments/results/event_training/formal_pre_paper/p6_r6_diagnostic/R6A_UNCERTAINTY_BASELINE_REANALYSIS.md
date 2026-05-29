# R6a Uncertainty Baseline Reanalysis

This report compares event risk against available uncertainty baselines on exact-error ranking.

| baseline | AUROC | AUPRC | Spearman char error | top20 risk error | bottom20 risk error | risk gap |
|---|---:|---:|---:|---:|---:|---:|
| event_risk_1_minus_p | 0.7088 | 0.8470 | 0.2869 | 0.8586 | 0.4233 | 0.4352 |
| token_marginal_entropy | 0.8036 | 0.8984 | 0.4953 | 0.9319 | 0.2836 | 0.6483 |
| sequence_entropy | 0.7799 | 0.8783 | 0.4382 | 0.9048 | 0.3071 | 0.5976 |
| viterbi_margin_inverse | 0.8105 | 0.8942 | 0.4535 | 0.9152 | 0.2405 | 0.6748 |
| max_sequence_probability_inverse | 0.8083 | 0.8987 | 0.5153 | 0.9357 | 0.2319 | 0.7038 |
| neg_log_viterbi_probability | 0.8083 | 0.8987 | 0.5153 | 0.9357 | 0.2319 | 0.7038 |

## Complementarity Check

Within each generic-uncertainty decile, cases are split by event risk `1 - P_theta(L|x)`.
A positive weighted gap means high event risk still has higher exact-error rate after controlling coarsely for the generic baseline.

| controlled generic baseline | weighted within-bin event-risk error gap |
|---|---:|
| token_marginal_entropy | -0.0769 |
| sequence_entropy | -0.0464 |
| viterbi_margin_inverse | 0.0368 |
| max_sequence_probability_inverse | -0.0314 |
| neg_log_viterbi_probability | -0.0314 |

## Interpretation

The event-risk score has positive exact-error ranking signal, but standard uncertainty baselines are stronger overall in this rerun.
Therefore the paper should not claim diagnostic superiority over entropy, margin, or max-probability uncertainty.
The complementarity check asks only whether event risk carries some rule-specific residual signal within coarse uncertainty strata; it is not a causal or calibration result.
The safe claim is narrower: `1 - P_theta(L|x)` is an interpretable rule-specific posterior-consistency signal with positive risk-ranking value, not a universal or dominant uncertainty score.

Boundary: this is ranking evidence only, not calibration and not benchmark superiority.
