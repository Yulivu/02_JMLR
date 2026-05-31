# Related Work Draft

Generated: 2026-05-30

This draft is written for submission-risk control. It deliberately concedes close prior art and avoids positioning the paper as a new automata-inference, constrained-decoding, weak-supervision, or uncertainty method.

## Constrained Decoding And Automata-Based Inference

Constrained decoding and WFST-style methods are a direct neighbor. Linear-chain CRFs, finite-state sequence models, and WFST methods already combine statistical sequence scores with automata-like structure. These methods are appropriate when the goal is to search over legal paths, repair invalid outputs, or enforce a regular constraint at decode time.

This paper does not claim that automata-constrained inference is new. It uses the familiar CRF x automaton computational neighborhood to make a different quantity explicit: the probability mass assigned by the original CRF posterior to a regular-language event. A constrained decoder answers:

```text
What is the best legal output?
```

The audit object answers:

```text
How much probability does the original posterior assign to legal outputs?
```

These can disagree. A constrained-product decoder can return a legal BIO sequence while the unconstrained posterior assigns low mass to BIO-legal sequences. The paper uses constrained decoding baselines to expose this distinction, not to argue that constrained decoding is unimportant.

## Regular-Constrained CRFs

Regular-constrained CRFs, including RegCCRF-style models and work on constraining linear-chain CRFs to regular languages, are among the closest prior systems. They can enforce regular-language support restrictions and train/infer under a constrained CRF distribution. A constrained CRF is often the right modeling choice when illegal structures should receive zero probability by design.

The boundary is the denominator and the object under audit. In a constrained-support CRF, the posterior is normalized over legal structures. In this project, the reported scalar is:

```text
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x),
```

where `Z_theta(x)` is the original CRF normalizer over all length-`T` label sequences. We therefore do not replace the original model with a constrained-support model before asking the audit question. This distinction is useful precisely when decoded legality or constrained support would hide the fact that the original model placed substantial mass outside the rule.

Allowed wording:

```text
We audit the original posterior rather than replacing it with a constrained-support posterior.
```

Forbidden wording:

```text
We replace RegCCRF or show that constrained CRFs are unnecessary.
```

## Posterior Regularization

Posterior Regularization, especially Ganchev et al. (2010), is a close conceptual prior. PR can express posterior constraints, weak structural supervision, and training objectives that encourage model posteriors to satisfy desired properties. The paper should not imply otherwise.

The distinction is narrower. PR is primarily a framework for constraining, projecting, or regularizing posterior distributions during learning or inference. This project centers a reportable event probability under the original posterior. The scalar can be computed and audited before deciding whether to regularize, project, constrain decoding, or change the model:

```text
original-posterior event mass first; training objective second.
```

The event loss `-log P_theta(L|x)` is one computable use of the object. It should not be presented as a new weak-supervision family or as a claim that PR cannot express related constraints.

## Generalized Expectation

Generalized Expectation criteria use weak supervision by matching model expectations to target expectations. This is relevant because event loss also uses weak structural information. The safe distinction is that GE is an expectation-matching training criterion, while the main object here is the auditable regular-language event probability under the original posterior.

Event loss should be framed as a secondary training signal derived from the audit object. The paper should avoid suggesting that it introduces a broadly new semi-supervised or weak-supervision framework.

## Semantic Loss

Semantic Loss is especially important to handle directly. It penalizes low probability assigned to assignments that satisfy a logical constraint. Therefore:

```text
-log P_theta(L|x)
```

is conceptually close to semantic loss or to the negative log probability of satisfying a constraint. This must be conceded.

The defensible distinction is not that the loss form is unrelated. The distinction is that this paper studies a finite CRF posterior, regular-language label events, exact CRF x DFA event-mass computation, and an audit protocol separating decoded legality from original posterior consistency. In other words, semantic-loss-like training is not the paper identity; the original-posterior event mass and its audit semantics are.

Allowed wording:

```text
The event loss is semantic-loss-like; our emphasis is the CRF posterior audit object and regular-language diagnostic protocol.
```

Forbidden wording:

```text
Semantic Loss is unrelated, or event loss is a wholly new objective family.
```

## Lagrangian Relaxation And Constrained Optimization

Lagrangian relaxation, dual decomposition, and other constrained-optimization methods introduce penalties, dual variables, or relaxations to solve constrained inference and training problems. These methods are relevant because they also connect symbolic constraints with structured prediction.

The paper's central object is not an optimizer for a constrained objective. `P_theta(L|x)` can be evaluated under the original CRF posterior without changing the decoder. This makes it useful as an audit scalar: it can reveal whether a legal answer produced by an optimization procedure is supported by the model distribution.

The paper should not claim that penalty or constrained-optimization methods are ineffective. It should say that they answer a different intervention question.

## Calibration And Uncertainty

Calibration and uncertainty-ranking work studies whether model probabilities match empirical correctness, or whether uncertainty scores rank likely errors. This project is not a calibration paper. R6a and the public CoNLL2000 case both show that generic uncertainty baselines such as entropy, margin, and max-sequence-probability scores are stronger than event risk for broad error ranking.

The narrower defensible claim is:

```text
In the evaluated diagnostics, event risk is a positive rule-specific posterior-consistency signal.
```

It is not:

```text
Event risk dominates generic uncertainty, is calibrated confidence, or has robust residual predictive power after controlling for uncertainty.
```

## Tensor-Network And uMPS Motivation

Tensor-network and uMPS work motivates the idea that regular languages can be treated as events in probabilistic sequence models. That motivation is useful, but it should not define the main paper. The current evidence does not establish arbitrary low-rank event transfers, optimized tensor runtime, or a tensor-rank identity for the method.

The main text should keep tensor-network material as motivation or appendix-only support. The main contribution is posterior regular-language event mass for CRF posteriors.

## Closest Prior Risk Summary

The closest-prior attack memo is:

```text
docs/external_review/CLOSEST_PRIOR_ATTACK_MEMO.md
```

Its core conclusion is that the paper remains plausible only if it treats product automaton inference as known and makes the contribution about object semantics, audit protocol, and empirical boundaries. The most dangerous objection is:

```text
This is standard CRF x automaton marginal inference with a new name, plus a semantic-loss-style penalty.
```

The introduction should preempt that objection with:

```text
Known product-automaton marginal inference is the computational neighborhood; our focus is the original-posterior regular-language event mass as an auditable semantic object, separated from constrained decoding and constrained-support normalization.
```

The manuscript must never say:

```text
We introduce a new product-automaton inference algorithm for CRFs.
```

## Citation Spine To Resolve In BibTeX

| Area | Anchor citation | Role in this paper |
|---|---|---|
| CRFs | Lafferty, McCallum, and Pereira (2001), "Conditional Random Fields" | base conditional sequence model and marginal inference neighborhood |
| WFST / finite-state methods | Mohri, Pereira, and Riley (2002), "Weighted Finite-State Transducers in Speech Recognition" | automata/product-style constrained decoding neighborhood |
| regular-constrained CRFs | Papay, Klinger, and Padó (2022), "Constraining Linear-chain CRFs to Regular Languages" | closest constrained-CRF neighbor; support restriction vs original-posterior event mass |
| posterior regularization | Ganchev et al. (2010), "Posterior Regularization for Structured Latent Variable Models" | closest conceptual neighbor for posterior constraints |
| generalized expectation | Mann and McCallum (2010), "Generalized Expectation Criteria for Semi-Supervised Learning with Weakly Labeled Data" | weak-supervision expectation criterion boundary |
| semantic loss | Xu et al. (2018), "A Semantic Loss Function for Deep Learning with Symbolic Knowledge" | logic/event loss boundary |
| calibration | Platt (1999); Guo et al. (2017), "On Calibration of Modern Neural Networks" | boundary: risk ranking is not calibration |
| Lagrangian / dual decomposition | Rush et al. (2010), "On Dual Decomposition and Linear Programming Relaxations for Natural Language Processing" | boundary: constrained optimization is not the central object |

The final manuscript should replace these checklist entries with normal BibTeX citations and should avoid unsupported historical claims beyond these anchor works.
