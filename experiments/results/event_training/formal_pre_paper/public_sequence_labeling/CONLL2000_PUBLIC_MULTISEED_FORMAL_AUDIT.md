# CoNLL2000 Public Sequence Labeling Multiseed Formal Audit

This audit is for a full three-seed public BIO/chunking run. It remains a case study, not a benchmark-superiority result.

## Provenance

- raw bundle: `experiments/runs/local_checks/public_conll2000_chunking_multiseed_full`
- git commit: `002ecbb`
- config: `experiments\configs\exp7\public_conll2000_chunking_multiseed.yaml`
- returncode: `0`
- duration_seconds: `3076.544701`

## Mean / Std Rows

| variant | seeds | P(BIO) mean | P(BIO) std | hidden conflict mean | B7 legal mean | token acc mean | span F1 mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| B0_unconstrained | 3 | 0.9837 | 0.0011 | 0.0133 | 1.0000 | 0.8731 | 0.7973 |
| B4_semi_event_0.1 | 3 | 0.9885 | 0.0063 | 0.0123 | 1.0000 | 0.8697 | 0.7918 |

## B4 Movement Relative To B0

| metric | B0 mean | B4 mean | delta mean |
|---|---:|---:|---:|
| P_BIO | 0.9837 | 0.9885 | +0.0048 |
| hidden_conflict | 0.0133 | 0.0123 | -0.0010 |
| unconstrained_legal | 0.9910 | 0.9900 | -0.0010 |
| token_acc | 0.8731 | 0.8697 | -0.0034 |
| span_F1 | 0.7973 | 0.7918 | -0.0055 |

## Multiseed Uncertainty Boundary

| variant | event-risk AUROC exact | event-risk AUPRC exact | event-risk Spearman token error | event-risk exact risk gap |
|---|---:|---:|---:|---:|
| B0_unconstrained | 0.7384 | 0.8829 | 0.3117 | 0.4450 |
| B4_semi_event_0.1 | 0.6895 | 0.8865 | 0.2886 | 0.2650 |

Strongest generic uncertainty baselines by AUROC:

| variant | strongest generic score | AUROC exact | AUPRC exact | Spearman token error |
|---|---|---:|---:|---:|
| B0_unconstrained | sequence_entropy | 0.8339 | 0.9405 | 0.4346 |
| B4_semi_event_0.1 | sequence_entropy | 0.8178 | 0.9394 | 0.3785 |

## Interpretation

Allowed: multiseed aggregation strengthens the public case-study provenance if this run exists.

Boundary: this remains a public case study, not SOTA, benchmark superiority, or a general task-improvement claim.
