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

Structured prediction systems often use hard constraints to ensure that decoded outputs satisfy known rules. This repairs the final prediction but does not reveal how much posterior probability the original model assigns to rule-consistent structures. We formalize and operationalize posterior regular-language event mass as an audit statistic for CRF posteriors, using known product-automaton marginal-inference machinery as the computational foundation. The resulting scalar measures posterior-level rule consistency: it can be audited directly, used in an event loss, and studied as a diagnostic signal. In evaluated diagnostic and field-style settings, posterior event mass exposes cases where legal decoded outputs coexist with low original posterior event mass. The paper is positioned around posterior-event semantics and auditability, not new automata inference or benchmark superiority.

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

Four-object formula table:

| Object | Formula / Procedure | Denominator / Search Space | What It Answers |
|---|---|---|---|
| Unconstrained CRF posterior | `p_theta(y|x)=exp S_theta(x,y)/Z_theta(x)` | all `y in Y^T` | original model distribution |
| Constrained decoding / WFST decoding | `argmax_{y in L} S_theta(x,y)` | legal outputs only | best legal output |
| Constrained CRF / RegCCRF-style restriction | `p_theta(y|x, y in L)=exp S_theta(x,y)/Z_{theta,L}(x)` for `y in L` | legal set `L` only | posterior after support restriction |
| This work | `P_theta(L|x)=Z_{theta,L}(x)/Z_theta(x)` | numerator over `L`, denominator over all `Y^T` | original posterior mass satisfying the rule |

### 1.2 Preemptive Rebuttal: Is This Just Standard Marginal Inference?

Draft paragraph:

One might object that `P_theta(L|x)` is merely standard marginal inference after adding an auxiliary constraint. That description misses the object of interest. We do not ask for the best legal sequence, nor do we replace the model with a constrained decoder or projected posterior. We evaluate a global regular-language event under the original CRF posterior. This produces a scalar audit statistic that can be low even when constrained Viterbi decoding returns a legal output. R5a demonstrates this for BIO legality, and R6a shows that low event mass identifies high-risk field-style examples. Theoretically, the object is the ratio `Z_{theta,L}(x)/Z_theta(x)`, where the numerator is computed by a CRF x DFA product transfer and the denominator remains the original CRF normalizer. This posterior-event probability is therefore distinct from a constrained Viterbi result, from decoding repair, and from optimizing an auxiliary constrained objective.

### 1.3 Contributions

1. Formalize posterior regular-language event mass as an audit object for CRF posterior semantics.
2. Use exact finite product-transfer computation as the theorem foundation, while acknowledging known product automaton marginal inference as the computational neighborhood.
3. Distinguish posterior event mass from constrained decoding, WFST-style decoding, constrained CRFs, and RegCCRF-style support restriction.
4. Derive event-loss gradient as a computable expectation-difference training signal.
5. Provide a diagnostic protocol and empirical boundaries for evaluated field-style settings.
6. Provide scaling sanity for the finite product-state implementation.

Event training is a secondary contribution. It shows the event object can be used as a training signal and can move posterior event mass; it is not framed as an accuracy method.

Explicit non-contributions:

- no benchmark superiority claim;
- no WFST replacement claim;
- no claim that product automaton inference itself is new;
- no NER F1 improvement claim;
- no calibration claim;
- no claim that hard constraints are useless;
- no arbitrary low-rank theorem;
- no tensor-rank/MPO main identity.

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

### 2.2 Regular-Constrained CRFs / RegCCRF

RegCCRF and "Constraining Linear-chain CRFs to Regular Languages" should be discussed directly.

Boundary:

| RegCCRF / constrained CRF | This Work |
|---|---|
| changes the model support so illegal sequences receive zero probability | keeps the original CRF posterior and measures its mass on `L` |
| answers how to train/infer under regular-language constraints | answers how much unconstrained posterior mass satisfies a rule |
| can improve constrained structured prediction performance | does not claim constrained-method superiority |
| denominator is the constrained model normalizer | denominator remains `Z_theta(x)` from the original model |

### 2.3 Posterior Regularization And Ganchev et al. 2010

Ganchev et al. 2010 introduced posterior regularization as a framework for incorporating indirect supervision through constraints on posterior distributions. The boundary argument should be explicit:

| Ganchev et al. 2010 / Posterior Regularization | This Work |
|---|---|
| constrains or projects posteriors according to expectation-style constraint sets | formalizes and studies a reportable regular-language event probability under the original CRF posterior |
| primarily an optimization framework for posterior constraints | an algebraic posterior-event object with audit semantics |
| constraints influence training/inference objectives | `P_theta(L|x)` can be reported as a scalar diagnostic even without changing decoding |
| does not center the distinction between legal decoded output and low original posterior event mass | this distinction is the main empirical and conceptual object |

Text to include:

```text
Posterior regularization is the closest conceptual neighbor, but our object is not a projected posterior or a constraint penalty by itself. It is the event probability assigned by the model's original posterior to a regular language. This makes it directly auditable: hard-constrained decoding can return a legal output while `P_theta(L|x)` remains low.
```

### 2.4 Generalized Expectation Criteria

Boundary:

```text
Generalized expectation criteria match model expectations to weak supervision targets. This work reports an explicit regular-language event mass under the original posterior; event loss is only one use of that object.
```

### 2.5 Semantic Loss

Boundary:

```text
Semantic Loss is a broad logic-based differentiable loss. This work is narrower: finite CRF posterior event semantics for regular-language label events, with exact CRF x DFA transfer and an audit interpretation.
```

### 2.6 Confidence Calibration

Boundary:

```text
Calibration usually concerns whether reported probabilities match empirical correctness. Here the question is whether a structured rule receives posterior mass.
```

R6a can be mentioned only as diagnostic evidence, not calibration evidence.

### 2.7 Lagrangian Relaxation

Boundary:

```text
Lagrangian relaxation optimizes constrained objectives. Our object measures an event under the CRF posterior and can be computed without changing the decoder.
```

### 2.8 Tensor Networks / uMPS

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

Required assumption boundary:

```text
The exact product-transfer theorem assumes finite label set, fixed finite length,
finite scores, complete deterministic DFA, and a finite-context/local
factorization of the CRF score. Arbitrary finite score tables can be represented
by a sufficiently large finite context/table construction, but that is an
expressive construction, not an efficiency claim.
```

Main theorem:

```text
u_0 M_1^L ... M_T^L b_L = Z_{theta,L}(x).
```

Proof source:

```text
docs/manuscript/THEORY_PROOF_PROSE.md
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

Gradient proposition:

```text
grad[-log P_theta(L|x)]
= E_{p_theta(y|x)}[grad S_theta(x,y)]
  - E_{p_theta(y|x, y in L)}[grad S_theta(x,y)].
```

Interpretation:

- event loss pulls the unconstrained posterior expectation toward the event-conditioned posterior expectation;
- this is a training-signal statement, not an accuracy guarantee.

### 4.3 Diagnostic Use

Use `P_theta(L|x)` to audit and rank examples:

- low event mass;
- bottom/top quantile errors;
- hidden conflict cases where constrained decoding is legal but posterior mass is low.
- compare against uncertainty baselines where available;
- do not claim event risk dominates entropy, margin, or max-probability uncertainty.
- do not claim robust residual predictive power after controlling for generic uncertainty.

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
Low event mass is a rule-specific posterior-consistency signal with positive exact-error ranking value in the evaluated field-style diagnostics.
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
Diagnostic evidence, not task-improvement evidence, calibration evidence, uncertainty superiority, or robust complementarity evidence.
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

### 5.8 Public CoNLL2000 BIO/Chunking Formal Case

Claim:

```text
The public BIO/chunking formal case provides an additional structured-prediction
audit case: B4 moves posterior BIO event mass upward, B7 constrained-product
decoding produces legal outputs, and the original posterior event mass remains
separate from decoded legality.
```

Key formal run:

```text
B0 mean P(BIO|x)=0.9837 +/- 0.0011, hidden conflict=0.0133, span F1=0.7973
B4 mean P(BIO|x)=0.9885 +/- 0.0063, hidden conflict=0.0123, span F1=0.7918
B7 constrained-product legality=1.0000
```

Boundary:

```text
Full local three-seed public case-study configuration, not SOTA, benchmark
superiority, or proof that event training generally improves task metrics.
B4 raises event mass and slightly reduces hidden conflict on average, while
mean token accuracy and span F1 decrease.
```

Public-case uncertainty boundary:

```text
Event risk has positive exact-error ranking signal in the public multiseed case
(B0 AUROC 0.7384; B4 AUROC 0.6895), but sequence entropy is stronger by AUROC
for both variants. Do not claim uncertainty dominance.
```

### 5.9 R7 Lambda / Rule Sensitivity And Negative Boundary

Claim:

```text
Event loss can move posterior event mass, but its task effect depends on the
rule and lambda. A rule that is weakly related or misleading for the task can
raise event mass while degrading task metrics.
```

Key derisk row:

```text
product_code_swapped_rule, B4 lambda 1.0:
delta P(event)=+0.9485
delta legal rate=+0.9716
delta char accuracy=-0.5524
delta exact accuracy=-0.0816
```

Provenance:

```text
wrapped formal run:
experiments/runs/local_checks/r7_sensitivity_derisk_formal_wrapped
config: experiments/configs/exp7/r7_sensitivity_formal.yaml
returncode: 0
duration_seconds: 28.276712
```

Boundary:

```text
This is evidence against an accuracy-method reading of event loss. It supports
only a training-signal and audit-design interpretation.
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
- not a new automata-inference algorithm;
- not a replacement for constrained decoding, WFST methods, constrained CRFs, or RegCCRF;
- not an uncertainty replacement; R6a shows generic uncertainty baselines are stronger overall;
- B7 is a constrained-product decoding baseline, not a full WFST toolkit;
- public CoNLL2000 is a full local three-seed case study, not broad benchmark evidence;
- R7 sensitivity includes negative/event-task tradeoff boundary evidence and is not benchmark-superiority evidence;
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
7. B7 constrained-product design and scoped baseline discussion.
