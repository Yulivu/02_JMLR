# Citation / Related-Work Audit

Date: 2026-05-31

## Verdict

```text
related_work_anchor_status = PASS_WITH_FIXES
final_bibtex_audit_status = pending_until_latex_and_bib_exist
```

This is a pre-submission source-level audit, not the final citation audit. The
repository currently has no paper `.tex` files and no `.bib` file, so a true
per-citation context audit cannot yet be run. The goal here is to lock the
closest-prior spine and prevent strawman positioning before manuscript writing.

## Anchor Citation Checks

| Area | Anchor | Status | Use allowed |
|---|---|---|---|
| CRFs | Lafferty, McCallum, and Pereira, "Conditional Random Fields: Probabilistic Models for Segmenting and Labeling Sequence Data", ICML 2001 | keep | base CRF sequence model and dynamic-programming neighborhood |
| WFST / finite-state methods | Mohri, Pereira, and Riley, "Weighted Finite-State Transducers in Speech Recognition", Computer Speech & Language 2002 | keep | finite-state composition/product-style constrained decoding neighborhood |
| regular-constrained CRFs | Papay, Klinger, and Padó, "Constraining Linear-chain CRFs to Regular Languages", ICLR 2022 | fix year/venue if written as 2021 | closest constrained-support CRF neighbor |
| Posterior Regularization | Ganchev, Graca, Gillenwater, and Taskar, "Posterior Regularization for Structured Latent Variable Models", JMLR 2010 | keep | posterior constraints and weak structural supervision |
| Generalized Expectation | Mann and McCallum, "Generalized Expectation Criteria for Semi-Supervised Learning with Weakly Labeled Data", JMLR 2010 | keep | weak-supervision expectation-matching boundary |
| Semantic Loss | Xu, Zhang, Friedman, Liang, and Van den Broeck, "A Semantic Loss Function for Deep Learning with Symbolic Knowledge", ICML 2018 | keep | closest loss-form neighbor for `-log P_theta(L|x)` |
| calibration | Platt 1999; Guo et al., "On Calibration of Modern Neural Networks", ICML 2017 | keep as boundary only | calibration is not the paper claim |
| dual decomposition | Rush, Sontag, Collins, and Jaakkola, "On Dual Decomposition and Linear Programming Relaxations for Natural Language Processing", EMNLP 2010 | keep | constrained optimization neighbor |

## Source URLs To Use When Building BibTeX

- CRF: https://repository.upenn.edu/cis_papers/159/
- WFST: https://www.sciencedirect.com/science/article/pii/S0885230801000204
- RegCCRF / regular-language CRFs: https://openreview.net/forum?id=T-QC2p1mduO
- Posterior Regularization: https://www.jmlr.org/papers/v11/ganchev10a.html
- Generalized Expectation: https://www.jmlr.org/papers/v11/mann10a.html
- Semantic Loss: https://proceedings.mlr.press/v80/xu18h.html
- Calibration: https://proceedings.mlr.press/v70/guo17a.html
- Dual decomposition: https://aclanthology.org/D10-1001/

## Required Wording

Use:

```text
Known product-automaton marginal inference is the computational neighborhood;
our focus is original-posterior regular-language event mass as an auditable
semantic object, separated from constrained decoding and constrained-support
normalization.
```

Use:

```text
The event loss is semantic-loss-like; the paper's emphasis is not a new weak
supervision family but the CRF posterior audit object and diagnostics.
```

Do not use:

```text
We introduce a new CRF-DFA product inference algorithm.
```

Do not use:

```text
Semantic Loss, Posterior Regularization, or regular-constrained CRFs cannot
express related constraints.
```

## Residual Risk

The most dangerous objection remains:

```text
This is standard CRF x automaton marginal inference with a new name, plus a
semantic-loss-style penalty.
```

The draft can survive this only if related work concedes the computation and
loss-form neighborhood directly, then argues for the narrower audit object:
original-posterior event mass, decoded legality separation, and empirical
boundaries.

## Final Submission Gate

When the LaTeX manuscript and BibTeX exist, run a true citation audit over every
`\cite{...}` occurrence. This document does not verify final cite contexts,
author order, DOI fields, or venue formatting.
