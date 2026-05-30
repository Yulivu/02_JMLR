# Closest Prior Attack Memo

Updated: 2026-05-30

This memo is intentionally adversarial. It is written to find the strongest JMLR-main rejection arguments before manuscript drafting. It does not try to make the project look safer than the evidence supports.

## Summary Verdict

The project can still be novel/significant enough only if the paper is framed as a posterior-semantics and auditability contribution, not as an inference-algorithm contribution. The computational primitive is familiar. The defensible object is the original-posterior event mass `Z_{theta,L}(x) / Z_theta(x)` and the empirical protocol around decoded legality, event loss, and diagnostic boundaries.

The single most dangerous related-work objection is:

```text
This is standard CRF x automaton marginal inference with a new name, plus a semantic-loss-style penalty.
```

The introduction should preempt it with:

```text
Known product-automaton marginal inference is the computational neighborhood; our focus is the original-posterior regular-language event mass as an auditable semantic object, separated from constrained decoding and constrained-support normalization.
```

The following sentence must never appear:

```text
We introduce a new product-automaton inference algorithm for CRFs.
```

## CRF x DFA / Product Automaton Marginal Inference

| Question | Attack memo |
|---|---|
| prior already does what? | Combines a sequence model with a finite-state monitor/product state and computes constrained sums or marginals by dynamic programming. |
| reviewer attack against us | `P_theta(L|x)` is just a regular constrained marginal; the algorithmic step is old. |
| our defensible distinction | We report the mass of `L` under the original CRF posterior and use it as an audit scalar; we do not claim the product DP is new. |
| what we must concede | Exact computation by product construction is known computational territory. |
| claim wording allowed | "We formalize and operationalize original-posterior regular-language event mass, computed with known product-automaton marginal-inference machinery." |
| claim wording forbidden | "We propose a new CRF-DFA product inference algorithm." |
| residual risk level | high |

## Constrained Decoding / WFST

| Question | Attack memo |
|---|---|
| prior already does what? | Enforces symbolic constraints at decode time and returns legal high-scoring outputs, often using finite-state representations. |
| reviewer attack against us | If users need legal outputs, constrained decoding already solves the practical problem. |
| our defensible distinction | Decoded legality and original posterior consistency answer different questions; B7 returns legal outputs without using event mass. |
| what we must concede | Constrained decoding is the right tool when the target is legal output repair. |
| claim wording allowed | "Constrained decoding returns a legal sequence; event mass audits how much original posterior probability is legal." |
| claim wording forbidden | "Constrained decoding is ineffective" or "B7 replaces WFST methods." |
| residual risk level | medium |

## RegCCRF / Constrained CRF

| Question | Attack memo |
|---|---|
| prior already does what? | Restricts CRF support to regular languages and trains/infer under constrained support. |
| reviewer attack against us | Regular-language CRF constraints already exist and are closer to the claimed object than the draft admits. |
| our defensible distinction | RegCCRF-style normalization changes the model support; our denominator remains the original `Z_theta(x)`. |
| what we must concede | Regular-constrained CRFs are a close prior and may be preferable when the goal is constrained prediction. |
| claim wording allowed | "We audit the original posterior rather than replacing it by a constrained-support posterior." |
| claim wording forbidden | "Regular-constrained CRFs cannot model these rules" or "we replace RegCCRF." |
| residual risk level | high |

## Posterior Regularization / Ganchev et al.

| Question | Attack memo |
|---|---|
| prior already does what? | Expresses posterior constraints and weak structural supervision through constraint sets and projection/regularization objectives. |
| reviewer attack against us | The event loss is just posterior regularization or a posterior constraint penalty. |
| our defensible distinction | The central object is a reportable event probability under the original posterior; event loss is one use, not the identity. |
| what we must concede | PR can express rich posterior constraints and weak structural supervision. |
| claim wording allowed | "Unlike a projected posterior objective, this audit can be reported without changing decoding or support." |
| claim wording forbidden | "Posterior regularization cannot express structural constraints." |
| residual risk level | high |

## Generalized Expectation

| Question | Attack memo |
|---|---|
| prior already does what? | Uses weak supervision by matching model expectations to target expectations. |
| reviewer attack against us | Event loss is another weak-supervision expectation criterion. |
| our defensible distinction | The paper centers the event probability as an audit scalar; training is secondary. |
| what we must concede | GE is a close weak-supervision family for training with indirect signals. |
| claim wording allowed | "Event loss is a computable use of the audit object." |
| claim wording forbidden | "We introduce a new weak-supervision family." |
| residual risk level | medium |

## Semantic Loss

| Question | Attack memo |
|---|---|
| prior already does what? | Penalizes low probability assigned to satisfying assignments of logical constraints. |
| reviewer attack against us | `-log P_theta(L|x)` is semantic loss for a regular-language constraint. |
| our defensible distinction | We must accept the conceptual closeness. Our narrower contribution is CRF original-posterior regular-language event auditing and decoded-legality contrast. |
| what we must concede | The loss form is not conceptually isolated from semantic loss. |
| claim wording allowed | "The event loss is semantic-loss-like; our emphasis is the CRF posterior audit object and regular-language computation/diagnostics." |
| claim wording forbidden | "Semantic Loss is unrelated" or "event loss is a wholly new objective." |
| residual risk level | high |

## Lagrangian Relaxation / Constrained Optimization

| Question | Attack memo |
|---|---|
| prior already does what? | Adds penalties or dual variables to solve constrained inference/training objectives. |
| reviewer attack against us | The method is just another constrained penalty. |
| our defensible distinction | `P_theta(L|x)` can be computed and reported before choosing any constraint-enforcement intervention. |
| what we must concede | Penalty methods are appropriate when the goal is enforcing constraints. |
| claim wording allowed | "Event mass can inform whether enforcement hides posterior conflict." |
| claim wording forbidden | "Penalty and constrained-optimization methods are unnecessary." |
| residual risk level | medium |

## Calibration / Uncertainty Ranking

| Question | Attack memo |
|---|---|
| prior already does what? | Studies confidence, uncertainty scores, error ranking, and probability calibration. |
| reviewer attack against us | Event risk is weaker than entropy/margin/max-probability baselines, so the diagnostic claim is not compelling. |
| our defensible distinction | Event risk is an interpretable rule-specific posterior-consistency audit, not a universal uncertainty score. |
| what we must concede | R6a and public CoNLL2000 both show generic uncertainty baselines are stronger for error ranking. |
| claim wording allowed | "Event risk has positive rule-specific ranking signal in evaluated diagnostics." |
| claim wording forbidden | "Event risk dominates uncertainty" or "event mass is calibrated confidence." |
| residual risk level | medium |

## Tensor-Network / uMPS / MPO Motivation

| Question | Attack memo |
|---|---|
| prior already does what? | Represents sequence distributions and regular-language events with tensor-network constructions. |
| reviewer attack against us | Tensor language distracts from a simple automaton DP and creates unsupported low-rank expectations. |
| our defensible distinction | uMPS/tensor material is motivation or appendix-only; the main paper is CRF posterior semantics. |
| what we must concede | No main low-rank or optimized tensor-runtime result is established. |
| claim wording allowed | "Tensor-network language motivates regular-language event probabilities but is not the main identity." |
| claim wording forbidden | "Tensor rank is the central contribution" or "we obtain arbitrary low-rank event transfers." |
| residual risk level | medium |

## Bottom Line

If product automaton inference is treated as known, the project is still plausible only as a methods/auditability paper about a specific posterior semantic object and its empirical protocol. The paper must make the object useful enough to justify publication: legal outputs can hide low original-posterior event mass; event loss moves this mass but is not an accuracy method; and risk diagnostics are rule-specific and weaker than generic uncertainty for broad error ranking.
