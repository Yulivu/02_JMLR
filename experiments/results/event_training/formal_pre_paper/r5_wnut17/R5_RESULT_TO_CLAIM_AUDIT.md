# R5 WNUT17 Result-to-Claim Audit

This audit summarizes downloaded AutoDL R5 outputs. It is an evidence audit, not a paper section.

## r5a_diagnostic_stress

| variant | seeds | P(BIO|x) | delta P | up-rate | hidden conflict | token acc | entity F1 | NLL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0_unconstrained | 10 | 0.0566 | 0.0000 | 0 | 1.0000 | 0.8711 | 0.0000 | 1.3770 |
| B1_hard_constrained_decode | 10 | 0.0566 | 0.0000 | 0 | 1.0000 | 0.8711 | 0.0000 | 1.3770 |
| B2_labeled_event_0.1 | 10 | 0.0576 | 0.0010 | 1 | 1.0000 | 0.8711 | 0.0000 | 1.3778 |
| B3_labeled_event_0.1_hard_decode | 10 | 0.0576 | 0.0010 | 1 | 1.0000 | 0.8711 | 0.0000 | 1.3778 |
| B4_semi_event_0.1 | 10 | 0.3389 | 0.2822 | 1 | 0.9963 | 0.8711 | 0.0000 | 0.9400 |
| B5_rule_feature_0.8 | 10 | 0.1608 | 0.1042 | 1 | 1.0000 | 0.8711 | 0.0000 | 1.1725 |
| B6_pr_style_tau0.7 | 10 | 0.1703 | 0.1137 | 1 | 1.0000 | 0.8711 | 0.0000 | 0.9348 |

## r5b_feature_viability

| variant | seeds | P(BIO|x) | delta P | up-rate | hidden conflict | token acc | entity F1 | NLL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0_unconstrained | 10 | 0.9824 | 0.0000 | 0 | 0.0088 | 0.8859 | 0.1660 | 0.6508 |
| B1_hard_constrained_decode | 10 | 0.9824 | 0.0000 | 0 | 0.0088 | 0.8860 | 0.1665 | 0.6508 |
| B2_labeled_event_0.1 | 10 | 0.9832 | 0.0007 | 1 | 0.0078 | 0.8860 | 0.1652 | 0.6521 |
| B3_labeled_event_0.1_hard_decode | 10 | 0.9832 | 0.0007 | 1 | 0.0078 | 0.8861 | 0.1657 | 0.6521 |
| B4_semi_event_0.1 | 10 | 0.9865 | 0.0041 | 0.8000 | 0.0074 | 0.8819 | 0.1522 | 0.7636 |
| B5_rule_feature_0.8 | 10 | 0.9864 | 0.0040 | 1 | 0.0058 | 0.8859 | 0.1645 | 0.6424 |
| B6_pr_style_tau0.7 | 10 | 0.9868 | 0.0044 | 0.8000 | 0.0060 | 0.8804 | 0.1463 | 0.7493 |

## Claim Audit

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| Hidden posterior conflict exists | supported in R5a | B0 has very low `P(BIO|x)` and hidden conflict near 1 while constrained legality is 1 | R5a has entity F1 = 0, so it is diagnostic only |
| Semi-event training raises posterior BIO mass | supported in R5a | B4 has the largest positive delta P over B0 among B2/B4/B5/B6 | In R5b, event mass is already saturated |
| WNUT17 is not pure all-O toy | supported in R5b | B0 entity F1 is nonzero over 10 seeds | F1 remains modest; no benchmark superiority claim |
| B4 improves NER F1 | not supported | B4 entity F1 is not consistently above B0 in R5b | Do not claim task-performance improvement |
| B5/B6 dominate B4 | not supported overall | B5/B6 are competitive in R5b but weaker than B4 for R5a posterior mass | Keep baseline discussion nuanced |

## Decision

```text
R5 supports the paper's posterior-event diagnostic story.
R5 does not support NER benchmark superiority.
Use R5a for hidden conflict and R5b for task viability.
```
