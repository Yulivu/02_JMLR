# External Review Packet Current

Updated: 2026-05-29

Provenance:

```text
Review the repository HEAD that contains this file.
R6a uncertainty-baseline result first committed in: 9ef3eb3.
Paper-table provenance is recorded separately in experiments/results/paper_tables/PAPER_TABLES_INDEX.md.
```

Use this packet for the next external AI/researcher review. The request is not to polish wording, but to decide whether the current project is defensible as a JMLR-style methods/auditability paper.

## One-Sentence Thesis

Decoded output legality is not posterior consistency. We define and compute the posterior mass assigned by the original CRF posterior to a regular-language event.

## Core Object

```text
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x)
```

Interpretation:

```text
How much probability mass does the original CRF posterior assign to label sequences satisfying rule L?
```

This is not:

- the best legal output;
- a constrained decoder;
- a constrained CRF whose support is already restricted to `L`;
- a projected posterior;
- a calibration score;
- a tensor-rank paper.

## Four Object Formula Table

| Object | Formula / Procedure | Denominator / Search Space | What It Answers |
|---|---|---|---|
| Unconstrained CRF posterior | `p_theta(y|x)=exp S_theta(x,y)/Z_theta(x)` | all `y in Y^T` | what distribution does the CRF assign? |
| Constrained decoding / WFST decoding | `argmax_{y in L} S_theta(x,y)` | search restricted to legal outputs | what is the best legal output? |
| Constrained CRF / RegCCRF-style support restriction | `p_theta(y|x, y in L)=exp S_theta(x,y)/Z_{theta,L}(x)` for `y in L` | legal set `L` only | what is the posterior after restricting support to legal outputs? |
| This work | `P_theta(L|x)=Z_{theta,L}(x)/Z_theta(x)` | numerator over `L`, denominator over all `Y^T` | how much original posterior mass satisfies the rule? |

This table is the intended main defense against the objection that the paper is only constrained decoding or a constrained CRF.

## Intended Paper Identity

This should be reviewed as a narrower methods/theory/auditability paper:

1. posterior regular-language event mass object;
2. exact product-transfer computation;
3. distinction from constrained decoding / constrained CRFs;
4. event-loss gradient as a computable training signal;
5. rule-specific diagnostic evidence;
6. conservative product-state scaling.

Event training is secondary. It shows that the object can be used as a training signal and can move posterior event mass. It is not an accuracy method.

## Main Related-Work Risks

| Neighbor | Reviewer objection | Current defense |
|---|---|---|
| CRF x DFA / product automaton inference | this is standard marginal inference with a new name | we openly acknowledge the computational primitive; the contribution is the posterior-event object and audit semantics |
| RegCCRF / constrained CRF | constrained CRFs already handle regular-language constraints | RegCCRF changes model support; we measure event mass under the original CRF posterior with denominator `Z_theta(x)` |
| constrained decoding / WFST | this is just constrained decoding | constrained decoding returns a legal path; `P_theta(L|x)` reports how much original posterior mass is legal |
| Posterior Regularization / Ganchev et al. 2010 | PR already uses posterior constraints | PR is an optimization/projection framework; our central object is a reportable regular-language event probability |
| Generalized Expectation | weak supervision via expectations already exists | GE matches expected features to targets; our main contribution is an explicit event mass and audit protocol |
| Semantic Loss | `-log P(L)` resembles semantic loss | yes, event loss is adjacent; our narrower contribution is CRF posterior semantics for regular-language label events |
| uncertainty / calibration | event mass may just be uncertainty | R6a shows event risk has signal but is weaker than entropy/margin/max-probability; we only claim rule-specific posterior consistency |

## Evidence Snapshot

| Block | Setting | Main Result | Safe Use | Boundary |
|---|---|---|---|---|
| Theory | finite `Y,T`, finite scores, complete DFA | exact event mass and product transfer | main theorem spine | fixed finite setup |
| Gradient | `Z_{theta,L}(x)>0`, finite differentiable scores | event-loss gradient is posterior expectation minus event-conditioned expectation | training-signal interpretation | no accuracy theorem |
| R5a WNUT17 diagnostic stress | 10 seeds, word-id tiny CRF, low-data stress | B0 `P(BIO|x)=0.0566`, constrained legality 1; B4 raises event mass to `0.3389` | hidden posterior conflict diagnostic evidence | entity F1 is 0; not NER usefulness |
| R5b WNUT17 feature viability | 10 seeds, feature CRF | B0 entity F1 `0.1660`; event mass saturated near 0.98 | shows WNUT slice not pure all-O toy | no B4 F1 improvement |
| R1/R2/R4 | controlled, semi-real, real-source small-field tasks | B4 generally raises posterior event mass | event training can move the object | not task-metric dominance |
| R6a diagnostic | 21,000 field-style cases | event risk AUROC `0.7088`, AUPRC `0.8470` | rule-specific posterior-consistency signal with positive risk-ranking value | not calibration; not strongest uncertainty |
| R6a uncertainty baselines | same 21,000 cases | entropy/margin/max-probability AUROC about `0.78-0.81` | forces conservative diagnostic claim | no uncertainty-superiority or complementarity claim |
| R8 complexity | reference CPU transfer scaling | product-state scaling measured | conservative complexity discussion | not optimized runtime |

## Key Numbers

### R5 WNUT17

| Block | Variant | Seeds | P_event | Hidden Conflict | Entity F1 | Use |
|---|---|---:|---:|---:|---:|---|
| R5a diagnostic stress | B0 | 10 | 0.0566 | 1.0000 | 0.0000 | hidden conflict evidence |
| R5a diagnostic stress | B4 | 10 | 0.3389 | 0.9963 | 0.0000 | event-mass movement |
| R5b feature viability | B0 | 10 | 0.9824 | 0.0088 | 0.1660 | nonzero NER viability |
| R5b feature viability | B4 | 10 | 0.9865 | 0.0074 | 0.1522 | no F1 improvement |

### R6a Diagnostic And Uncertainty

| Score | AUROC | AUPRC | Spearman char error | Risk Gap |
|---|---:|---:|---:|---:|
| `1 - P_theta(L|x)` | 0.7088 | 0.8470 | 0.2869 | 0.4352 |
| token marginal entropy | 0.8036 | 0.8984 | 0.4953 | 0.6483 |
| sequence entropy | 0.7799 | 0.8783 | 0.4382 | 0.5976 |
| Viterbi margin inverse | 0.8105 | 0.8942 | 0.4535 | 0.6748 |
| max sequence probability inverse | 0.8083 | 0.8987 | 0.5153 | 0.7038 |

Reading:

```text
Event mass has diagnostic signal, but is not the strongest uncertainty score.
Its defensible value is rule-specific posterior consistency, not general uncertainty dominance.
```

Complementarity check:

```text
Within generic-uncertainty deciles, event-risk residual gaps are not consistently positive.
Weighted within-bin gaps:
token entropy -0.0769, sequence entropy -0.0464, Viterbi margin +0.0368,
max sequence probability -0.0314, negative log Viterbi probability -0.0314.
```

Reading:

```text
Do not claim event risk adds robust residual predictive power beyond generic uncertainty.
Use R6a only to support a rule-specific posterior-consistency audit signal.
```

## Claims Allowed

- `P_theta(L|x)` is a well-defined finite CRF posterior event probability.
- CRF x DFA product transfer computes `Z_{theta,L}(x)` exactly under the finite setup.
- Hard-constrained decoding and posterior consistency are different objects.
- Event loss has an expectation-difference gradient under explicit finite assumptions.
- Semi-event training can raise posterior event mass in audited settings.
- Low event mass is a rule-specific posterior-consistency signal with positive risk-ranking value in field-style diagnostics.
- Product-state scaling can be discussed conservatively.

## Claims Not Allowed

- benchmark superiority;
- WNUT17 NER F1 improvement by B4;
- replacement or defeat of WFST / constrained CRF / RegCCRF;
- hard constraints are useless;
- calibration;
- event risk dominates entropy/margin/max-probability uncertainty;
- event risk adds robust residual predictive power after controlling for generic uncertainty;
- optimized runtime superiority;
- tensor rank / MPO as the main paper identity.

## Files To Review

```text
docs/manuscript/FINAL_CLAIM_TABLE.md
docs/manuscript/JMLR_METHODS_OUTLINE.md
docs/manuscript/PAPER_POSITIONING.md
docs/manuscript/RELATED_WORK_DRAFT.md
docs/manuscript/THEORY_PROOF_PROSE.md
docs/protocols/B7_WFST_DESIGN_NOTE.md
experiments/results/paper_tables/PAPER_TABLES_INDEX.md
experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/R6A_UNCERTAINTY_BASELINE_REANALYSIS.md
```

## Review Questions

1. Is this defensible as a JMLR methods/auditability paper if product automaton inference is acknowledged as known?
2. Is the boundary against RegCCRF / constrained CRF strong enough?
3. Is the boundary against Posterior Regularization, Generalized Expectation, and Semantic Loss strong enough?
4. Does R5a remain useful as diagnostic-stress evidence despite zero entity F1?
5. Is the R6a diagnostic claim conservative enough after uncertainty baselines outperform event risk and complementarity is weak?
6. Is B7 implementation necessary if the paper avoids superiority claims?
7. Which claim should be deleted or downgraded before manuscript writing?
8. What theorem/proof wording is most likely to be attacked?
9. Are more experiments necessary before writing begins?
10. Does the paper remain valuable if event risk is weaker than generic uncertainty but more interpretable and rule-specific?

## Desired Reviewer Output

Please return:

- verdict on JMLR route;
- strongest safe abstract framing;
- weakest claim;
- required related-work changes;
- required theory changes;
- required experiments, if any;
- whether B7 must be implemented;
- whether the uncertainty-baseline result weakens the paper identity or just narrows the diagnostic claim.
