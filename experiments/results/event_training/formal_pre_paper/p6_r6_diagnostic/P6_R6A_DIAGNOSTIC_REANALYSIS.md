# P6 R6a Diagnostic Reanalysis

This reanalysis uses the existing R6a diagnostic cases. No new experiment or HPC run was performed.

## Overall Metrics

| cases | exact error | hidden conflict | AUROC exact error | AUPRC exact error | Spearman risk-char error |
|---:|---:|---:|---:|---:|---:|
| 21000 | 0.7359 | 0.0207 | 0.7088 | 0.8470 | 0.2869 |

## Per-Task Metrics

| source | task | cases | AUROC | AUPRC | Spearman | bottom20 exact err | bottom20 hidden conflict |
|---|---|---:|---:|---:|---:|---:|---:|
| real_source | invoice_6d | 3000 | 0.7928 | 0.8862 | 0.4949 | 0.9150 | 0 |
| real_source | invoice_c6d | 3000 | 0.7354 | 0.8116 | 0.4347 | 0.8333 | 0.0067 |
| real_source | stock_5d | 3000 | 0.8334 | 0.8979 | 0.5667 | 0.9167 | 0 |
| semi_real | amount | 3000 | 0.8046 | 0.9220 | 0.5178 | 0.9600 | 0.0750 |
| semi_real | date | 3000 | 0.7220 | 0.7918 | 0.4001 | 0.8817 | 0.4783 |
| semi_real | dose | 3000 | 0.8509 | 0.9367 | 0.5296 | 0.9400 | 0.0067 |
| semi_real | product_code | 3000 | 0.8240 | 0.9754 | 0.5165 | 0.9800 | 0.1567 |

## Overall Risk Curve

| risk decile | mean P(L|x) | exact error | char error | hidden conflict |
|---:|---:|---:|---:|---:|
| 1 | 0.5594 | 0.8862 | 0.2106 | 0.2067 |
| 2 | 0.7125 | 0.8310 | 0.2140 | 0 |
| 3 | 0.7879 | 0.8395 | 0.2152 | 0 |
| 4 | 0.8355 | 0.8267 | 0.2042 | 0 |
| 5 | 0.8678 | 0.7981 | 0.1833 | 0 |
| 6 | 0.8943 | 0.8138 | 0.1850 | 0 |
| 7 | 0.9169 | 0.7914 | 0.1695 | 0 |
| 8 | 0.9369 | 0.7257 | 0.1487 | 0 |
| 9 | 0.9560 | 0.5843 | 0.1165 | 0 |
| 10 | 0.9754 | 0.2624 | 0.0530 | 0 |

## Claim Boundary

Allowed: `P_theta(L|x)` provides a useful ranking/risk signal for the audited field-style tasks.

Not allowed: this does not prove calibration, universal error prediction, or benchmark superiority.
