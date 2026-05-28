# Related Work Draft

Generated: 2026-05-28

This is prose for paper drafting. It is intentionally conservative about novelty.

## Constrained Decoding And Automata-Based Inference

Constrained decoding and WFST-style methods are a natural point of comparison because they also combine sequence models with symbolic structure. This neighborhood includes linear-chain CRFs (Lafferty, McCallum, and Pereira, 2001), weighted finite-state transducer methods for sequence modeling and decoding (Mohri, Pereira, and Riley, 2002), and automata-constrained dynamic programs for structured prediction. In these methods, the central object is usually the decoded output under a constraint: the inference procedure searches over legal paths, repairs invalid outputs, or restricts the output space to satisfy a formal rule. This is the right tool when the goal is output validity.

Our object is different. We ask how much probability mass the original CRF posterior assigns to a regular-language event. A hard-constrained decoder can return a legal output while the original posterior still assigns low mass to legal structures. Thus decoded legality and posterior consistency are distinct. We use constrained decoding baselines to expose this difference rather than to claim that constrained decoding is ineffective.

We do not claim that automata product inference is new. The computational construction is adjacent to standard CRF x automaton dynamic programming. The contribution is to make the regular-language event probability under the original posterior the central semantic object, and to study it as an audit, training, and diagnostic signal.

## Posterior Regularization

Posterior regularization, especially the framework of Ganchev et al. (2010), is the closest conceptual neighbor. Posterior regularization introduces constraints on posterior distributions and optimizes models under those constraints. It provides a general training framework for using indirect supervision or structural preferences.

Our emphasis is different. We define an explicit regular-language event probability under the original CRF posterior:

```text
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x).
```

This scalar can be reported without changing the decoder or projecting the posterior. Event loss is one possible use of the object, but it is not the only use. The same quantity can audit hidden posterior conflict: a constrained decoder may return a legal sequence while `P_theta(L|x)` remains low.

Therefore, the boundary is not that posterior regularization cannot use constraints. It can. The boundary is that our paper centers the explicit event mass assigned by the original posterior to a regular language, and uses this mass to separate posterior consistency from decode-time legality.

## Confidence Calibration

Confidence calibration studies whether model probabilities correspond to empirical correctness, as in classical probability calibration for classifiers (Platt, 1999) and later neural calibration analyses (Guo et al., 2017). This is related because both calibration and posterior event mass involve probabilities attached to model behavior. However, calibration typically concerns the reliability of predicted confidence values, while our question is whether a structured rule receives posterior mass.

Our R6a diagnostic results should not be described as calibration. They show that low event mass is useful as a ranking/risk signal in audited field-style tasks. They do not prove calibrated probabilities or universal error prediction.

## Lagrangian Relaxation And Constrained Optimization

Lagrangian relaxation and constrained optimization methods introduce penalties or dual variables to solve constrained objectives. Dual-decomposition methods for structured prediction and NLP (for example, Rush et al., 2010) are representative of this line. These methods are optimization tools. They are useful when the goal is to enforce or approximately enforce constraints during inference or learning.

By contrast, `P_theta(L|x)` is an event probability under the original posterior. It can be computed before deciding whether to constrain decoding, add a penalty, or change training. This distinction matters because the event mass can reveal that a model does not internally believe a rule even when an optimization procedure returns a legal answer.

## Tensor-Network And uMPS Motivation

Prior tensor-network sequence models, including uMPS-style work, motivate the idea that regular languages can be treated as probabilistic events. This project transfers that view to conditional CRF posteriors. The tensor/rank material in our repository is therefore support for optional appendix discussion, not the paper identity.

The main paper should not be framed as a tensor-rank contribution. The safer framing is posterior regular-language event mass for CRFs.

## Summary Boundary

The safest related-work statement is:

```text
We use a familiar computational neighborhood, CRF x automaton dynamic programming, to define and audit a specific posterior event object. The novelty is not product inference alone; it is the posterior-event semantics, result-to-claim discipline, and empirical demonstration that legal decoded outputs can coexist with low original posterior event mass.
```

## Citation Spine To Resolve In BibTeX

Use this as a citation checklist during manuscript writing:

| Area | Anchor citation | Role in this paper |
|---|---|---|
| CRFs | Lafferty, McCallum, and Pereira (2001), "Conditional Random Fields" | base conditional sequence model and marginal inference neighborhood |
| WFST / finite-state methods | Mohri, Pereira, and Riley (2002), "Weighted Finite-State Transducers in Speech Recognition" | automata/product-style constrained decoding neighborhood |
| posterior regularization | Ganchev et al. (2010), "Posterior Regularization for Structured Latent Variable Models" | closest conceptual neighbor for posterior constraints |
| calibration | Platt (1999); Guo et al. (2017), "On Calibration of Modern Neural Networks" | boundary: risk ranking is not calibration |
| Lagrangian / dual decomposition | Rush et al. (2010), "On Dual Decomposition and Linear Programming Relaxations for Natural Language Processing" | boundary: constrained optimization is not the central object |

The final manuscript should replace these checklist entries with normal BibTeX citations and should avoid unsupported historical claims beyond these anchor works.
