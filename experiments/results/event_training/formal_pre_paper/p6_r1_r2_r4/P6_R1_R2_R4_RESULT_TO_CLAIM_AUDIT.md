# P6 R1/R2/R4 Result-to-Claim Audit

This audit summarizes downloaded AutoDL P6 R1/R2/R4 outputs. It is an evidence audit, not a paper section.

## Block Summary

| block | family | rows | mean delta P | positive P rate | mean delta legal | mean delta char | mean delta exact |
|---|---|---:|---:|---:|---:|---:|---:|
| r1_controlled_formal | B2 | 8 | -0.0002 | 0.6250 | -0.0043 | -0.0034 | -0.0081 |
| r1_controlled_formal | B4 | 8 | 0.1883 | 1 | 0.1639 | 0.0048 | 0.0032 |
| r2_semi_real_formal | B2 | 8 | -0.0146 | 0 | -0.0406 | -0.0049 | -0.0205 |
| r2_semi_real_formal | B4 | 8 | 0.1584 | 1 | 0.0854 | 0.0188 | 0.0775 |
| r2_semi_real_formal | B5 | 4 | 0.0740 | 1 | 0.0671 | 0.0119 | 0.0449 |
| r2_semi_real_formal | B6 | 4 | 0.0968 | 1 | 0.0772 | 0.0210 | 0.0723 |
| r4_real_source_formal | B2 | 6 | 0.0141 | 0.5000 | 0.0006 | 0.0082 | 0.0294 |
| r4_real_source_formal | B4 | 6 | 0.0722 | 1 | 0.0018 | 0.0289 | 0.1127 |
| r4_real_source_formal | B5 | 3 | 0.0314 | 1 | 0.0013 | 0.0187 | 0.0678 |
| r4_real_source_formal | B6 | 3 | 0.0219 | 1 | 0.0009 | 0.0190 | 0.0743 |

## r1_controlled_formal

| task | variant | runs | P(L|x) | delta P | legal rate | char acc | exact acc |
|---|---|---:|---:|---:|---:|---:|---:|
| DATE | B0_unconstrained | 20 | 0.9203 | 0.0000 | 0.9955 | 0.9995 | 0.9953 |
| DATE | B4_semi_event_0.1 | 20 | 0.9726 | 0.0522 | 1.0000 | 1.0000 | 1.0000 |
| DATE | B4_semi_event_0.5 | 20 | 0.9848 | 0.0644 | 1.0000 | 1.0000 | 1.0000 |
| DDDLL | B0_unconstrained | 20 | 0.1765 | 0.0000 | 0.1855 | 0.7203 | 0.1640 |
| DDDLL | B4_semi_event_0.1 | 20 | 0.2718 | 0.0953 | 0.2937 | 0.7633 | 0.1947 |
| DDDLL | B4_semi_event_0.5 | 20 | 0.5723 | 0.3958 | 0.6538 | 0.6953 | 0.1028 |
| LL-DDD | B0_unconstrained | 20 | 0.8229 | 0.0000 | 0.9738 | 0.9736 | 0.8648 |
| LL-DDD | B4_semi_event_0.1 | 20 | 0.9650 | 0.1421 | 1.0000 | 0.9886 | 0.9333 |
| LL-DDD | B4_semi_event_0.5 | 20 | 0.9868 | 0.1640 | 1.0000 | 0.9876 | 0.9282 |
| LLDDD | B0_unconstrained | 20 | 0.2259 | 0.0000 | 0.2388 | 0.7683 | 0.2117 |
| LLDDD | B4_semi_event_0.1 | 20 | 0.3569 | 0.1310 | 0.3897 | 0.7924 | 0.2125 |
| LLDDD | B4_semi_event_0.5 | 20 | 0.6872 | 0.4613 | 0.7613 | 0.7347 | 0.1257 |

## r2_semi_real_formal

| task | variant | runs | P(L|x) | delta P | legal rate | char acc | exact acc |
|---|---|---:|---:|---:|---:|---:|---:|
| amount | B0_unconstrained | 10 | 0.7825 | 0.0000 | 0.8847 | 0.8137 | 0.2190 |
| amount | B4_semi_event_0.1 | 10 | 0.9291 | 0.1466 | 0.9983 | 0.8472 | 0.3130 |
| amount | B4_semi_event_0.5 | 10 | 0.9660 | 0.1835 | 1.0000 | 0.8422 | 0.3077 |
| amount | B5_rule_feature_0.8 | 10 | 0.8614 | 0.0789 | 0.9880 | 0.8350 | 0.2773 |
| amount | B6_pr_style_tau0.8 | 10 | 0.8818 | 0.0993 | 0.9927 | 0.8448 | 0.3050 |
| date | B0_unconstrained | 10 | 0.7131 | 0.0000 | 0.8043 | 0.9240 | 0.4257 |
| date | B4_semi_event_0.1 | 10 | 0.9085 | 0.1955 | 0.9883 | 0.9469 | 0.5780 |
| date | B4_semi_event_0.5 | 10 | 0.9609 | 0.2478 | 0.9990 | 0.9495 | 0.5940 |
| date | B5_rule_feature_0.8 | 10 | 0.8130 | 0.1000 | 0.9390 | 0.9382 | 0.5163 |
| date | B6_pr_style_tau0.8 | 10 | 0.8744 | 0.1613 | 0.9773 | 0.9437 | 0.5530 |
| dose | B0_unconstrained | 10 | 0.9155 | 0.0000 | 0.9953 | 0.8051 | 0.2133 |
| dose | B4_semi_event_0.1 | 10 | 0.9735 | 0.0580 | 1.0000 | 0.8111 | 0.2427 |
| dose | B4_semi_event_0.5 | 10 | 0.9888 | 0.0733 | 1.0000 | 0.8032 | 0.2277 |
| dose | B5_rule_feature_0.8 | 10 | 0.9440 | 0.0285 | 0.9987 | 0.8121 | 0.2393 |
| dose | B6_pr_style_tau0.8 | 10 | 0.9355 | 0.0200 | 0.9967 | 0.8161 | 0.2510 |
| product_code | B0_unconstrained | 10 | 0.7751 | 0.0000 | 0.9667 | 0.7294 | 0.0800 |
| product_code | B4_semi_event_0.1 | 10 | 0.9377 | 0.1626 | 0.9997 | 0.7494 | 0.1197 |
| product_code | B4_semi_event_0.5 | 10 | 0.9750 | 0.1999 | 1.0000 | 0.7452 | 0.1137 |
| product_code | B5_rule_feature_0.8 | 10 | 0.8638 | 0.0887 | 0.9937 | 0.7344 | 0.0847 |
| product_code | B6_pr_style_tau0.8 | 10 | 0.8817 | 0.1066 | 0.9930 | 0.7516 | 0.1183 |

## r4_real_source_formal

| task | variant | runs | P(L|x) | delta P | legal rate | char acc | exact acc |
|---|---|---:|---:|---:|---:|---:|---:|
| invoice_6d | B0_unconstrained | 10 | 0.9120 | 0.0000 | 1.0000 | 0.8392 | 0.2797 |
| invoice_6d | B4_semi_event_0.1 | 10 | 0.9720 | 0.0600 | 1.0000 | 0.8592 | 0.3497 |
| invoice_6d | B4_semi_event_0.5 | 10 | 0.9917 | 0.0797 | 1.0000 | 0.8834 | 0.4383 |
| invoice_6d | B5_rule_feature_0.8 | 10 | 0.9414 | 0.0293 | 1.0000 | 0.8599 | 0.3507 |
| invoice_6d | B6_pr_style_tau0.8 | 10 | 0.9321 | 0.0201 | 1.0000 | 0.8610 | 0.3587 |
| invoice_c6d | B0_unconstrained | 10 | 0.8977 | 0.0000 | 0.9940 | 0.8795 | 0.3453 |
| invoice_c6d | B4_semi_event_0.1 | 10 | 0.9656 | 0.0679 | 0.9987 | 0.8979 | 0.4330 |
| invoice_c6d | B4_semi_event_0.5 | 10 | 0.9885 | 0.0909 | 1.0000 | 0.9117 | 0.4903 |
| invoice_c6d | B5_rule_feature_0.8 | 10 | 0.9333 | 0.0356 | 0.9980 | 0.8943 | 0.4087 |
| invoice_c6d | B6_pr_style_tau0.8 | 10 | 0.9249 | 0.0272 | 0.9967 | 0.8985 | 0.4333 |
| stock_5d | B0_unconstrained | 10 | 0.9139 | 0.0000 | 1.0000 | 0.8191 | 0.2857 |
| stock_5d | B4_semi_event_0.1 | 10 | 0.9713 | 0.0574 | 1.0000 | 0.8317 | 0.3407 |
| stock_5d | B4_semi_event_0.5 | 10 | 0.9913 | 0.0774 | 1.0000 | 0.8652 | 0.4453 |
| stock_5d | B5_rule_feature_0.8 | 10 | 0.9432 | 0.0293 | 1.0000 | 0.8398 | 0.3547 |
| stock_5d | B6_pr_style_tau0.8 | 10 | 0.9322 | 0.0183 | 1.0000 | 0.8353 | 0.3417 |

## Claim Audit

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| B4 raises posterior event mass on controlled tasks | supported | R1 B4 rows have positive delta P across controlled formats | controlled structural evidence only |
| B4 raises posterior event mass on semi-real fields | supported | R2 B4 rows have positive delta P across amount/date/dose/product_code | task accuracy is not uniformly dominant |
| B4 raises posterior event mass on real-source small fields | supported | R4 B4 rows have positive delta P across invoice/stock fields | baseline legal rate is saturated or near-saturated |
| B4 is benchmark-superior | not supported | B5/B6 are competitive and task metrics vary by block | do not claim superiority |
| R1/R2/R4 complete P6 | not supported | they cover structural/training evidence, not full diagnostics or complexity | R6/R8 still needed |

## Decision

```text
P6 R1/R2/R4 support posterior-event training as a structural signal.
They do not support benchmark superiority.
Proceed to R6 diagnostic and R8 complexity before paper-writing.
```
