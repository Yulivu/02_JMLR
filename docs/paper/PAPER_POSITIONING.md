# Paper Positioning

Generated: 2026-05-28

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
We define and compute P_theta(L|x), the posterior mass assigned to a regular-language event.
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

## 4. Relationship To Nearby Work

| Nearby Area | What It Usually Answers | What This Project Answers |
|---|---|---|
| constrained decoding / WFST | what is the best legal output? | how much original posterior mass is legal? |
| hard legality repair | how do we force valid output? | does the model distribution believe validity? |
| rule-feature CRF | can local rule-correlated features help? | what is the explicit global event probability? |
| posterior regularization | how do we train/project with constraints? | what event mass does the original posterior assign? |
| confidence calibration | are predicted probabilities calibrated? | does a structured rule receive posterior mass? |
| Lagrangian relaxation | how do we optimize a constrained objective? | how do we audit posterior consistency without replacing the posterior? |

The paper should proactively acknowledge that the computational primitive is adjacent to CRF x automaton marginal inference. The novelty claim should be the object and audit semantics, not that product inference itself is new.

## 5. Boundary Against Ganchev et al. 2010 / Posterior Regularization

Posterior regularization is the closest conceptual neighbor. The safe boundary is:

```text
Posterior regularization constrains or projects posterior distributions during learning/inference.
This work defines an explicit regular-language event probability under the original CRF posterior and uses it as an audit scalar.
```

Do not say posterior regularization cannot express constraints. Say instead:

```text
Our central object is not a projected posterior or constraint penalty. It is Z_{theta,L}(x)/Z_theta(x), a reportable event probability under the model's original posterior.
```

## 6. Paper Spine

Main paper spine:

| Part | Role |
|---|---|
| Exact posterior event algebra | define `P_theta(L|x)` and compute it via CRF x DFA product transfer |
| Event training | use `-log P_theta(L|x)` as a computable event signal |
| Hidden conflict diagnostic | show legal decoded output can coexist with low posterior event mass |
| Field-style risk diagnostic | show low event mass predicts higher errors in audited field-style tasks |
| Complexity sanity | report conservative product-state scaling |

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
field-style risk diagnostic evidence
not calibration or universal error theorem
```

R8:

```text
reference CPU complexity sanity
not optimized speed or low-rank evidence
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
- B4 improves WNUT17 NER F1;
- B4 dominates B5/B6 overall;
- hard constraints are useless;
- event training generally preserves or improves task metrics;
- arbitrary low-rank advantage;
- optimized runtime superiority;
- JMLR-ready without external proof/positioning review.

## 10. Most Dangerous Objection

```text
This is just CRF marginal inference on a product automaton, with a new name.
```

Response:

```text
Yes, the computation is adjacent to standard product automaton marginal inference.
The contribution is the posterior-event object and audit protocol: measuring the original CRF posterior's mass on a regular-language rule, and showing that legal decoded outputs can coexist with low original posterior event mass.
```
