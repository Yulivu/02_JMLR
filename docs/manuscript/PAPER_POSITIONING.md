# Paper Positioning

Generated: 2026-05-30

## 1. Recommended Title Direction

Prefer:

```text
Posterior Regular-Language Event Mass for Conditional Random Fields
```

or:

```text
Auditing CRF Posterior Consistency with Regular-Language Event Mass
```

Avoid making "tensorized" the headline unless the paper becomes a tensor-rank/scaling paper. The current defensible contribution is posterior-event semantics and auditability, not tensor-rank theory.

## 2. Core Identity

This paper is not:

```text
another constrained decoder
another posterior regularization variant
a benchmark-superiority paper
a tensor-rank paper
```

The paper identity is:

```text
posterior-level regular-language event semantics for CRFs
```

Shortest version:

```text
Hard-constrained decoding can make the final output legal.
It cannot tell whether the original CRF posterior still places large mass on illegal structures.
We formalize, operationalize, and study `P_theta(L|x)`, the original posterior mass assigned to a regular-language event.
```

## 3. Reviewer-Facing Problem Definition

The reviewer must understand this within five minutes:

```text
Legality of the decoded output is not posterior consistency.
```

Example:

```text
BIO constrained decoding can return legal BIO tags, while the original CRF posterior assigns low mass to BIO-legal sequences.
```

The paper asks:

```text
How can we compute, train, and audit the posterior probability that a CRF assigns to a regular-language structural event?
```

Reviewer-facing answer to "is this just marginal inference":

```text
Yes, the computation is familiar: known product automaton marginal inference is
the computational neighborhood. The contribution is the object semantics, audit
protocol, and empirical demonstration that legal decoded outputs can coexist
with low original posterior event mass.
```

## 4. Relationship To Nearby Work

| Nearby Area | What It Usually Answers | What This Project Answers |
|---|---|---|
| constrained decoding / WFST | what is the best legal output? | how much original posterior mass is legal? |
| hard legality repair | how do we force valid output? | does the model distribution believe validity? |
| rule-feature CRF | can local rule-correlated features help? | what is the explicit global event probability? |
| posterior regularization | how do we train/project with constraints? | what event mass does the original posterior assign? |
| confidence calibration | are predicted probabilities calibrated? | does a structured rule receive posterior mass? |
| Lagrangian relaxation | how do we optimize a constrained objective? | how do we audit posterior consistency without replacing the posterior? |

The paper should proactively acknowledge that the computational primitive is adjacent to CRF x automaton marginal inference. The contribution claim should be the object and audit semantics, not that product inference itself is new.

Formula distinction:

| Object | Formula / Procedure | Main Difference |
|---|---|---|
| unconstrained CRF | `p_theta(y|x)=exp S_theta(x,y)/Z_theta(x)` | original posterior |
| constrained decoding | `argmax_{y in L} S_theta(x,y)` | legal search, no posterior mass audit |
| constrained CRF / RegCCRF | `p_theta(y|x,y in L)=exp S_theta(x,y)/Z_{theta,L}(x)` | support already restricted to `L` |
| this work | `P_theta(L|x)=Z_{theta,L}(x)/Z_theta(x)` | audits how much original posterior mass satisfies `L` |

Important wording:

```text
Do not introduce the computation as a new CRF-DFA product automaton algorithm.
Introduce it as the exact finite computation used to evaluate a posterior
event statistic under the original CRF posterior.
```

## 5. Boundary Against Ganchev et al. 2010 / Posterior Regularization

Posterior regularization is the closest conceptual neighbor. The safe boundary is:

```text
Posterior regularization constrains or projects posterior distributions during learning/inference.
This work formalizes and studies a reportable regular-language event probability under the original CRF posterior as an audit scalar.
```

Do not say posterior regularization cannot express constraints. Say instead:

```text
Our central object is not a projected posterior or constraint penalty. It is Z_{theta,L}(x)/Z_theta(x), a reportable event probability under the model's original posterior.
```

## 6. Paper Spine

Main paper spine:

| Part | Role |
|---|---|
| Posterior regular-language event mass | formalize the audit object `P_theta(L|x)` under the original CRF posterior |
| Exact product transfer | finite theorem foundation for computing `Z_{theta,L}(x)` via known CRF x DFA product transfer |
| Distinction from constrained decoding / constrained CRF | show the object answers posterior mass, not best legal output or support restriction |
| Event-loss gradient / training signal | show `-log P_theta(L|x)` has a finite expectation-difference gradient under explicit assumptions |
| Risk diagnostic evidence | show event mass is a rule-specific posterior-consistency signal with positive risk-ranking value |
| Public structured-prediction case | report CoNLL2000 BIO/chunking as an audit case, not a benchmark-superiority case |
| Constrained-product decoding baseline | report B7 as legal decoding behavior separated from original posterior event mass |
| Lambda/rule sensitivity | show event-mass movement depends on lambda and rule difficulty, including legal-rate-not-useful and event/task tradeoff boundary cases |
| Complexity sanity | report conservative product-state scaling |

Event training should be framed as a secondary contribution. It demonstrates that the event object is trainable and can move posterior mass; it is not an accuracy method and should not be sold as the main empirical result.

Appendix-only:

| Part | Role |
|---|---|
| conditional MPO/rank membership | optional support, not paper identity |
| positive-cone approximation bound | optional support under explicit assumptions |
| full configs/audit tables | reproducibility support |

## 7. Empirical Framing

R5a:

```text
diagnostic-stress evidence of hidden posterior BIO conflict
not an NER performance result
```

R5b:

```text
task viability check
not a B4 F1 improvement claim
```

R1/R2/R4:

```text
posterior event mass movement evidence
not benchmark superiority
```

R6a:

```text
evaluated field-style rule-specific risk diagnostic evidence
not calibration, universal error theorem, stronger-than-uncertainty claim, or robust complementarity claim
```

R8:

```text
reference CPU complexity sanity
not optimized speed or low-rank evidence
```

Public CoNLL2000:

```text
public structured-prediction audit case
not SOTA, benchmark superiority, or a proof that event training generally improves task metrics
```

B7:

```text
faithful constrained-product decoding baseline
not a full WFST toolkit, constrained-CRF replacement, or event-mass advantage claim
```

R7:

```text
lambda/rule sensitivity, including an intentionally misleading-rule boundary
where event mass rises while task metrics fall
not an accuracy-method claim
```

## 8. Required Narrative Discipline

Every section should answer at least one:

1. Can we compute posterior event mass?
2. Can event training increase posterior event mass?
3. Can posterior event mass reveal hidden conflict or risk that decoded legality hides?

If a section does not serve one of these, move it to appendix or remove it.

## 9. Prohibited Claims

Do not claim:

- benchmark superiority;
- WFST replacement;
- new product automaton inference algorithm;
- B4 improves WNUT17 NER F1;
- B4 dominates B5/B6 overall;
- hard constraints are useless;
- calibration;
- event risk dominates or robustly complements generic uncertainty baselines;
- event training generally preserves or improves task metrics;
- arbitrary low-rank advantage;
- tensor rank / MPO as main paper identity;
- optimized runtime superiority;
- submission-ready without external proof/positioning review.

## 10. Most Dangerous Objection

```text
This is just CRF marginal inference on a product automaton, with a new name.
```

Response:

```text
Yes, the computation is familiar: it sits in the known product automaton marginal-inference neighborhood.
The contribution is object semantics, audit protocol, and evidence: measuring the original CRF posterior's mass on a regular-language rule, and showing that legal decoded outputs can coexist with low original posterior event mass.
```
