# P6 R8 Complexity Result-to-Claim Audit

This audit summarizes downloaded AutoDL R8 complexity outputs. It is an evidence audit, not a paper section.

## Key Numbers

- max_mean_seconds: `0.616036` at setting `vary_label_count`
- max_product_state_count: `256` at setting `vary_label_count`

## Detailed Rows

| setting | T | labels | DFA states | context order | product states | mean seconds |
|---|---:|---:|---:|---:|---:|---:|
| vary_length_dfa | 10 | 8 | 2 | 1 | 16 | 0.001858 |
| vary_length_dfa | 10 | 8 | 4 | 1 | 32 | 0.003969 |
| vary_length_dfa | 10 | 8 | 8 | 1 | 64 | 0.009504 |
| vary_length_dfa | 10 | 8 | 16 | 1 | 128 | 0.022598 |
| vary_length_dfa | 20 | 8 | 2 | 1 | 16 | 0.003829 |
| vary_length_dfa | 20 | 8 | 4 | 1 | 32 | 0.008535 |
| vary_length_dfa | 20 | 8 | 8 | 1 | 64 | 0.022315 |
| vary_length_dfa | 20 | 8 | 16 | 1 | 128 | 0.060741 |
| vary_length_dfa | 40 | 8 | 2 | 1 | 16 | 0.007845 |
| vary_length_dfa | 40 | 8 | 4 | 1 | 32 | 0.017804 |
| vary_length_dfa | 40 | 8 | 8 | 1 | 64 | 0.048074 |
| vary_length_dfa | 40 | 8 | 16 | 1 | 128 | 0.143605 |
| vary_length_dfa | 80 | 8 | 2 | 1 | 16 | 0.015927 |
| vary_length_dfa | 80 | 8 | 4 | 1 | 32 | 0.036593 |
| vary_length_dfa | 80 | 8 | 8 | 1 | 64 | 0.099471 |
| vary_length_dfa | 80 | 8 | 16 | 1 | 128 | 0.220599 |
| vary_label_count | 40 | 4 | 8 | 1 | 32 | 0.007231 |
| vary_label_count | 40 | 8 | 8 | 1 | 64 | 0.027294 |
| vary_label_count | 40 | 16 | 8 | 1 | 128 | 0.108981 |
| vary_label_count | 40 | 32 | 8 | 1 | 256 | 0.616036 |
| context_order_sanity | 30 | 6 | 4 | 1 | 24 | 0.004366 |
| context_order_sanity | 30 | 6 | 4 | 2 | 28 | 0.005613 |

## Claim Audit

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| Reference product-transfer scaling was measured | supported | R8 varies sequence length, label count, DFA states, and context order | reference CPU implementation only |
| Complexity story can report product-state dependence | supported | runtime increases with larger product-state configurations | report as sanity/scaling, not optimized benchmark |
| Optimized runtime superiority | not supported | no optimized implementation or competing systems measured | do not claim speed advantage |
| Arbitrary low-rank advantage | not supported | R8 does not test low-rank approximation | keep rank/MPO in appendix scope |

## Decision

```text
R8 supports a conservative complexity/scaling discussion.
R8 does not support speed, GPU, low-rank, or superiority claims.
```
