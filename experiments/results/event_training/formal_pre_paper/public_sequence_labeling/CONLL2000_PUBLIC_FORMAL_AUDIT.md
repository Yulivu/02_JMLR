# CoNLL2000 Public Sequence Labeling Formal Audit

This is a public BIO/chunking case study. It is not a SOTA, benchmark-superiority, or constrained-method replacement experiment.

## Provenance

- raw bundle: `experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/public_conll2000_chunking_formal`
- git commit: `a10517d`
- config: `experiments/configs/exp7/public_conll2000_chunking_formal.yaml`
- returncode: `0`
- duration_seconds: `864.752525`

## Main Rows

| variant | P(BIO|x) | hidden conflict | unconstrained legal | B7 legal | token acc | B7 token acc | span F1 | B7 span F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B0_unconstrained | 0.9762 | 0.0240 | 0.9800 | 1.0000 | 0.8623 | 0.8626 | 0.7773 | 0.7776 |
| B4_semi_event_0.1 | 0.9953 | 0.0040 | 1.0000 | 1.0000 | 0.8681 | 0.8681 | 0.7936 | 0.7936 |

## B4 Movement Relative To B0

| metric | B0 | B4 | delta |
|---|---:|---:|---:|
| P_BIO | 0.9762 | 0.9953 | +0.0191 |
| hidden_conflict | 0.0240 | 0.0040 | -0.0200 |
| unconstrained_legal | 0.9800 | 1.0000 | +0.0200 |
| token_acc | 0.8623 | 0.8681 | +0.0058 |
| span_F1 | 0.7773 | 0.7936 | +0.0164 |

## Public-Case Uncertainty Boundary

| variant | event-risk AUROC exact | event-risk AUPRC exact | event-risk Spearman token error | event-risk exact risk gap |
|---|---:|---:|---:|---:|
| B0_unconstrained | 0.7202 | 0.9011 | 0.2607 | 0.3950 |
| B4_semi_event_0.1 | 0.6861 | 0.8664 | 0.2621 | 0.2450 |

Strongest generic uncertainty baselines by AUROC in the same public case:

| variant | strongest generic score | AUROC exact | AUPRC exact | Spearman token error |
|---|---|---:|---:|---:|
| B0_unconstrained | sequence_entropy | 0.8380 | 0.9495 | 0.3929 |
| B4_semi_event_0.1 | token_marginal_entropy | 0.8242 | 0.9417 | 0.4042 |

The raw detail table contains `event_risk_1_minus_p`, token marginal entropy, sequence entropy, Viterbi margin, max sequence probability, and negative log Viterbi probability for 2,000 variant/case rows.

## Interpretation

Allowed: this public case supports a structured-prediction audit story in which B4 moves posterior BIO mass upward and B7 constrained decoding gives legal sequences.

Boundary: event risk has positive signal but generic uncertainty is stronger in this public case. The full run is one frozen configuration and should not be used as benchmark superiority, SOTA evidence, uncertainty dominance, or proof that event training generally improves task metrics.
