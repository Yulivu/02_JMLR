# JMLR Methods Paper Outline

Generated: 2026-05-28

Working title:

```text
Posterior Regular-Language Event Mass for Conditional Random Fields
```

Paper identity:

```text
Decoded output legality is not posterior consistency.
```

## Abstract

Draft content:

Structured prediction systems often use hard constraints to ensure that decoded outputs satisfy known rules. This repairs the final prediction but does not reveal how much posterior probability the model assigns to rule-consistent structures. We define `P_theta(L|x)`, the posterior mass that a CRF assigns to a regular-language event `L`, and compute it exactly using a product construction between the CRF state and a deterministic finite automaton. The resulting scalar is a posterior-level semantic object: it can be audited, trained through an event loss, and used as a diagnostic signal. In diagnostic and field-style settings, posterior event mass exposes hidden inconsistency that constrained decoding can mask. The paper is positioned around posterior-event semantics and auditability, not benchmark superiority.

## 1. Introduction

Opening problem:

```text
Legal decoded outputs can hide inconsistent posteriors.
```

Concrete example:

- A BIO constrained decoder can always return a legal BIO sequence.
- The original CRF posterior may still assign most probability mass to illegal BIO sequences.
- A legal final sequence alone cannot answer whether the model believes the rule.

Proposed object:

```text
P_theta(L|x) = posterior mass assigned to regular-language event L.
```

### 1.1 What This Is And Is Not

2x2 distinction table:

| Nearby Method | Primary Object | Intervention Point | What It Cannot Directly Answer |
|---|---|---|---|
| Constrained decoding / WFST | legal decoded output | decode time | how much original posterior mass satisfies the rule |
| Posterior regularization | constrained expectation or projected posterior family | training/inference objective | explicit regular-language event probability as an audit scalar |
| Confidence calibration | confidence of selected prediction or class probabilities | probability calibration layer | whether a structured rule receives posterior mass |
| Lagrangian relaxation | optimization of constrained objective | inference/training optimization | posterior semantic consistency of the unconstrained model |

This work:

| Object | Intervention Point | Answer |
|---|---|---|
| `P_theta(L|x)` | posterior event algebra | how much probability the CRF assigns to rule-satisfying structures |

### 1.2 Preemptive Rebuttal: Is This Just Standard Marginal Inference?

Draft paragraph:

One might object that `P_theta(L|x)` is merely standard marginal inference after adding an auxiliary constraint. That description misses the object of interest. We do not ask for the best legal sequence, nor do we replace the model with a constrained decoder or projected posterior. We evaluate a global regular-language event under the original CRF posterior. This produces a scalar audit statistic that can be low even when constrained Viterbi decoding returns a legal output. R5a demonstrates this for BIO legality, and R6a shows that low event mass identifies high-risk field-style examples. Theoretically, the object is the ratio `Z_{theta,L}(x)/Z_theta(x)`, where the numerator is computed by a CRF x DFA product transfer and the denominator remains the original CRF normalizer. This posterior-event probability is therefore distinct from a constrained Viterbi result, from decoding repair, and from optimizing an auxiliary constrained objective.

### 1.3 Contributions

1. Define regular-language posterior event mass for CRFs.
2. Prove exact finite product-transfer computation.
3. Introduce event loss for posterior event training.
4. Show hidden posterior conflict that hard decoding masks.
5. Provide diagnostic evidence that low event mass predicts risk.
6. Provide conservative reference complexity scaling.

Explicit non-contributions:

- no benchmark superiority claim;
- no claim that hard constraints are useless;
- no arbitrary low-rank theorem.

## 2. Related Work

### 2.1 Constrained Decoding And WFST Methods

Position:

```text
They ensure legal outputs. We measure posterior mass of legal events.
```

Required boundary:

- do not claim automata-constrained inference is new;
- do not claim constrained decoding is bad;
- emphasize the difference between decoded legality and posterior consistency.

### 2.2 Posterior Regularization And Ganchev et al. 2010

Ganchev et al. 2010 introduced posterior regularization as a framework for incorporating indirect supervision through constraints on posterior distributions. The boundary argument should be explicit:

| Ganchev et al. 2010 / Posterior Regularization | This Work |
|---|---|
| constrains or projects posteriors according to expectation-style constraint sets | defines an explicit regular-language event probability under the original CRF posterior |
| primarily an optimization framework for posterior constraints | an algebraic posterior-event object with audit semantics |
| constraints influence training/inference objectives | `P_theta(L|x)` can be reported as a scalar diagnostic even without changing decoding |
| does not center the distinction between legal decoded output and low original posterior event mass | this distinction is the main empirical and conceptual object |

Text to include:

```text
Posterior regularization is the closest conceptual neighbor, but our object is not a projected posterior or a constraint penalty by itself. It is the event probability assigned by the model's original posterior to a regular language. This makes it directly auditable: hard-constrained decoding can return a legal output while `P_theta(L|x)` remains low.
```

### 2.3 Confidence Calibration

Boundary:

```text
Calibration usually concerns whether reported probabilities match empirical correctness. Here the question is whether a structured rule receives posterior mass.
```

R6a can be mentioned only as diagnostic evidence, not calibration evidence.

### 2.4 Lagrangian Relaxation

Boundary:

```text
Lagrangian relaxation optimizes constrained objectives. Our object measures an event under the CRF posterior and can be computed without changing the decoder.
```

### 2.5 Tensor Networks / uMPS

Boundary:

```text
uMPS motivates regular-language events inside probabilistic sequence models. We move the event-probability view to conditional CRF posteriors.
```

Rank/MPO material remains appendix-only.

## 3. Posterior Event Algebra

Sections:

1. finite setup and notation;
2. regular-language event slice `L cap Y^T`;
3. CRF x DFA product state;
4. exact event transfer theorem;
5. posterior event probability;
6. event loss and diagnostic statistic.

Main theorem:

```text
u_0 M_1^L ... M_T^L b_L = Z_{theta,L}(x).
```

Proof source:

```text
docs/paper/THEORY_PROOF_PROSE.md
```

## 4. Method

### 4.1 Event-Mass Computation

Describe:

- product state construction;
- numerator and denominator;
- finite sequence-length boundary;
- implementation conventions.

### 4.2 Event Training

Objective:

```text
NLL + lambda * (-log P_theta(L|x))
```

Semi-event setup:

- labeled examples use supervised NLL;
- unlabeled inputs can supply rule-event pressure;
- no theorem that this improves task accuracy.

### 4.3 Diagnostic Use

Use `P_theta(L|x)` to rank examples:

- low event mass;
- bottom/top quantile errors;
- hidden conflict cases where constrained decoding is legal but posterior mass is low.

## 5. Experiments

### 5.1 Experimental Principles

Report:

- event mass;
- delta event mass;
- legal rate;
- hard-constrained metrics;
- task metrics;
- bottom/top diagnostic gaps;
- claim boundary for each block.

### 5.2 R5 WNUT17 BIO/NER

Frame R5a as diagnostic-stress evidence:

```text
R5a provides diagnostic-stress evidence of hidden posterior conflict, not a performance result.
```

Include:

- B0 `P(BIO|x)=0.0566`;
- constrained legality is 1;
- B4 raises `P(BIO|x)` to 0.3389;
- entity F1 is 0, so no NER usefulness claim.

R5b:

- B0 entity F1 0.1660;
- WNUT is not all-O toy;
- B4 does not improve NER F1.

### 5.3 R1 Controlled Robustness

Claim:

```text
B4 raises posterior event mass across controlled regular formats.
```

Boundary:

```text
Controlled structural evidence only.
```

### 5.4 R2 Semi-Real Fields

Claim:

```text
B4 raises event mass on amount/date/dose/product_code.
```

Boundary:

```text
Task accuracy varies; B5/B6 are competitive.
```

### 5.5 R4 Real-Source Small Fields

Claim:

```text
B4 raises event mass on invoice/stock fields.
```

Boundary:

```text
Small-field auxiliary evidence; legal rate often saturated.
```

### 5.6 R6a Diagnostic

Claim:

```text
Low event mass predicts higher exact and char error across field-style tasks.
```

Key reanalysis:

```text
AUROC exact error = 0.7088
AUPRC exact error = 0.8470
lowest event-mass decile exact error = 0.8862
highest event-mass decile exact error = 0.2624
```

Boundary:

```text
Diagnostic evidence, not task-improvement evidence.
```

### 5.7 R8 Complexity

Claim:

```text
Reference product-transfer scaling is measured over sequence length, label count, DFA states, and context order.
```

Boundary:

```text
Not optimized runtime, GPU, or low-rank evidence.
```

## 6. Discussion

Main interpretation:

```text
Posterior event mass is a semantic audit object.
```

Use:

- distinguishes posterior belief from decoded legality;
- provides training signal;
- provides risk signal;
- supports conservative complexity accounting.

## 7. Limitations

Must include:

- missing R3 low-label/unlabeled sensitivity;
- missing R7 broader lambda/rule sensitivity;
- pending B7 faithful WFST-style baseline;
- no benchmark superiority;
- WNUT R5a is diagnostic-stress evidence, not a performance result;
- R8 is reference CPU scaling only;
- rank/MPO appendix only;
- final proof prose needs external review.

## 8. Conclusion

Close with:

```text
Rules should not only repair decoded outputs; they can also define posterior events that reveal what the model distribution actually believes.
```

## Appendix

Appendix contents:

1. full proof of exact product transfer;
2. conditional MPO/rank membership;
3. positive-cone approximation bound;
4. full configs and run manifests;
5. result-to-claim audit tables;
6. additional diagnostic cases;
7. B7 design discussion if not implemented.
