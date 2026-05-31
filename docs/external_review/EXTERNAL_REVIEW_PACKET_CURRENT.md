# External Review Packet Current

Updated: 2026-05-30

This packet is for a new external review. It is intended to be descriptive, not persuasive. The reviewer should judge whether the project has a coherent contribution, whether the evidence supports the stated claims, and whether any claims should be removed or downgraded before manuscript writing.

## Provenance

```text
Review the repository HEAD that contains this file.
R6a uncertainty-baseline result first committed in: 9ef3eb3.
JMLR CPU-upgrade formal run bundle was produced at commit: a10517d.
R7 derisk negative-boundary wrapped formal run uses config experiments/configs/exp7/r7_sensitivity_formal.yaml, returncode 0, duration 28.276712 seconds.
Paper-table provenance is recorded in experiments/results/paper_tables/PAPER_TABLES_INDEX.md.
```

## Recommended Review Order

1. `docs/external_review/EXTERNAL_REVIEW_PACKET_CURRENT.md`
2. `docs/external_review/CLOSEST_PRIOR_ATTACK_MEMO.md`
3. `docs/manuscript/FINAL_CLAIM_TABLE.md`
4. `docs/manuscript/RELATED_WORK_DRAFT.md`
5. `docs/manuscript/THEORY_PROOF_PROSE.md`
6. `experiments/results/paper_tables/PAPER_TABLES_INDEX.md`
7. `docs/protocols/B7_WFST_DESIGN_NOTE.md`
8. `experiments/results/event_training/formal_pre_paper/JMLR_CPU_UPGRADE_RESULT_AUDIT.md`
9. `experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_FORMAL_AUDIT.md`
10. `experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_MULTISEED_TINY_SMOKE_AUDIT.md`
11. `experiments/results/event_training/formal_pre_paper/b7_constrained_product/B7_CONSTRAINED_PRODUCT_FORMAL_AUDIT.md`
12. `experiments/results/event_training/formal_pre_paper/r7_sensitivity/R7_SENSITIVITY_FORMAL_AUDIT.md`
13. `experiments/results/event_training/formal_pre_paper/r7_sensitivity/R7_SENSITIVITY_DERISK_AUDIT.md`
14. `experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/R6A_UNCERTAINTY_BASELINE_REANALYSIS.md`
15. `docs/manuscript/REPRODUCIBILITY_PACKAGE_CHECKLIST.md`

## Review Tasks

Please evaluate the following without assuming the proposed framing is correct:

| Question | Evaluation target |
|---|---|
| Is `P_theta(L|x)` more than a restatement of known CRF x automaton marginal inference? | novelty / significance |
| Is the distinction from constrained decoding, WFST inference, RegCCRF, and constrained CRFs technically clear? | related-work boundary |
| Is the distinction from Posterior Regularization, Generalized Expectation, and Semantic Loss technically clear? | related-work boundary |
| Are the theorem assumptions complete and stated at the right level of generality? | theory soundness |
| Do R5a/R5b support the empirical claims assigned to them? | empirical framing |
| Does R6a support only a rule-specific signal, or more than that? | diagnostic claim strength |
| Does the uncertainty-baseline result require downgrading any claim? | empirical boundary |
| Is the implemented B7 constrained-product baseline faithful and sufficient for the paper boundary? | baseline sufficiency |
| Does the CoNLL2000 public case strengthen the empirical story without implying benchmark superiority? | public case-study framing |
| Does R7 sensitivity adequately show lambda/rule boundaries, including unhelpful cases? | sensitivity / boundary evidence |
| Which current claim is most likely to be rejected by a reviewer? | claim discipline |
| Which experiment, if any, is required before writing begins? | remaining work |

## Object Under Review

The project defines the following quantity for a CRF posterior and a regular-language label event:

```text
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x)
```

where `Z_{theta,L}(x)` sums CRF sequence weights over label sequences in the event `L`, and `Z_theta(x)` sums over all label sequences in `Y^T`.

The proposed interpretation is:

```text
the probability mass assigned by the original CRF posterior to label sequences satisfying rule L.
```

The review should evaluate whether this object and its empirical treatment are sufficient for a methods/auditability manuscript.
The packet intentionally does not ask the reviewer to treat CRF-DFA product
automaton marginal inference as new. Known product automaton marginal inference
is the computational neighborhood; the proposed contribution is object
semantics, audit protocol, event-loss use, and empirical boundaries.

## Object Distinctions

| Object | Formula / Procedure | Denominator / Search Space | Question Answered |
|---|---|---|---|
| Unconstrained CRF posterior | `p_theta(y|x)=exp S_theta(x,y)/Z_theta(x)` | all `y in Y^T` | What distribution does the CRF assign? |
| Constrained decoding / WFST decoding | `argmax_{y in L} S_theta(x,y)` | search restricted to legal outputs | What is the best legal output? |
| Constrained CRF / RegCCRF-style support restriction | `p_theta(y|x,y in L)=exp S_theta(x,y)/Z_{theta,L}(x)` for `y in L` | legal set `L` only | What is the posterior after support restriction? |
| This project object | `P_theta(L|x)=Z_{theta,L}(x)/Z_theta(x)` | numerator over `L`, denominator over all `Y^T` | What mass does the original posterior assign to the event? |

Review task: judge whether this distinction is enough to separate the project from existing constrained inference and posterior-constraint literature.

## Claimed Contribution Components

The repository currently presents these components:

1. posterior regular-language event mass object;
2. exact finite CRF-DFA product-transfer computation as theorem foundation;
3. distinction from constrained decoding and constrained CRFs;
4. event-loss gradient as a computable training signal;
5. rule-specific diagnostic evidence;
6. conservative product-state scaling discussion.

Event training is currently positioned as a secondary use of the object, not as an accuracy method.

## Related-Work Risks

| Neighbor | Possible objection | Current distinction in repo |
|---|---|---|
| CRF x DFA / product automaton inference | The computation is standard marginal inference. | The repo claims the contribution is the reported posterior-event object and audit use, not the DP primitive itself. |
| RegCCRF / constrained CRF | Regular-language CRF constraints already exist. | RegCCRF-style models condition or restrict support; this project reports `Z_{theta,L}/Z_theta` under the original posterior. |
| constrained decoding / WFST | The object may be viewed as another constrained-decoding variant. | Constrained decoding returns a legal path; the event mass reports posterior mass over the event. |
| Posterior Regularization / Ganchev et al. 2010 | Posterior constraints are already a known framework. | The repo distinguishes a reportable regular-language event probability from a projection/regularization framework. |
| Generalized Expectation | Weak supervision via expectations is already known. | The repo distinguishes explicit event mass from feature-expectation matching. |
| Semantic Loss | `-log P(L)` is close to semantic loss. | The repo distinguishes CRF structured posterior, regular-language label events, and constrained-decoding contrast. |
| uncertainty / calibration | Event mass may be an uncertainty score. | R6a shows signal, but generic uncertainty baselines are stronger; the repo limits the claim to rule-specific posterior consistency. |

Review task: identify whether these distinctions are accurate, sufficient, or overstated.

## Evidence Snapshot

| Block | Setting | Reported result | Intended use | Boundary |
|---|---|---|---|---|
| Theory | finite `Y,T`, finite scores, complete DFA, finite-context/local factorization for product transfer | exact event mass and product transfer | theorem spine / formal foundation | arbitrary finite score tables require huge context/table representation; no efficiency claim |
| Gradient | `Z_{theta,L}(x)>0`, finite differentiable scores | event-loss gradient is posterior expectation minus event-conditioned expectation | training-signal interpretation | no accuracy theorem |
| R5a WNUT17 diagnostic stress | 10 seeds, word-id tiny CRF, low-data stress | B0 `P(BIO|x)=0.0566`, constrained legality 1; B4 raises event mass to `0.3389` | hidden-posterior-conflict diagnostic | entity F1 is 0; not NER usefulness |
| R5b WNUT17 feature nonzero-F1 check | 10 seeds, feature CRF | B0 entity F1 `0.1660`; event mass saturated near 0.98 | WNUT slice nonzero-F1 check | no B4 F1 improvement |
| R1/R2/R4 | controlled, semi-real, real-source small-field tasks | B4 generally raises posterior event mass | event-training movement evidence | not task-metric dominance |
| R6a diagnostic | 21,000 field-style cases | event risk AUROC `0.7088`, AUPRC `0.8470` | rule-specific posterior-consistency signal | not calibration; generic uncertainty baselines are stronger |
| R6a uncertainty baselines | same 21,000 cases | entropy/margin/max-probability AUROC about `0.78-0.81` | boundary on diagnostic claim | no uncertainty-superiority or complementarity claim |
| R8 complexity | reference CPU transfer scaling | product-state scaling measured | complexity discussion | not optimized runtime |
| Public CoNLL2000 multiseed formal | 1000/1000/1000 public BIO/chunking case, seeds 0/1/2 | B4 raises mean `P(BIO|x)` from `0.9837` to `0.9885`, hidden conflict drops from `0.0133` to `0.0123`, while token acc drops from `0.8731` to `0.8697` and span F1 drops from `0.7973` to `0.7918`; B7 legality `1.0000` | public structured-prediction audit case | not SOTA, benchmark superiority, or general task-improvement claim |
| Public CoNLL2000 uncertainty | same 2,000 variant/case detail rows | event risk has positive exact-error ranking signal, but entropy/max-probability baselines are stronger | public-case uncertainty boundary | no uncertainty-superiority or calibration claim |
| B7 constrained-product formal | WNUT17 BIO, 500/500/500, B0 and B4 source models | legal rate `1.0000`; `uses_event_mass_for_decoding=False` | faithful constrained decoding comparison object | not full WFST, constrained CRF, or replacement claim |
| R7 sensitivity formal | 3 rule difficulties x 10 seeds x lambda sweep | event mass moves with lambda; stock-like digits has legal-rate-not-useful boundary | lambda/rule boundary evidence | not an accuracy-method or benchmark claim |
| R7 derisk boundary | wrapped formal run, 10 seeds, config `experiments/configs/exp7/r7_sensitivity_formal.yaml`, includes intentionally swapped rule | `product_code_swapped_rule` B4 lambda 1.0 raises `P(event)` by `+0.9485`, while char accuracy drops `-0.5524` and exact accuracy drops `-0.0816` | explicit event/task tradeoff boundary | shows rule choice can make event loss harmful for task metrics |
| CoNLL2000 multiseed tiny smoke | wrapped smoke run, 30/30/30 examples, 3 seeds, 1 epoch | B4 raises mean `P(BIO|x)` from `0.3487` to `0.5187`, while mean span F1 drops from `0.6894` to `0.6647` | plumbing check only | separate smoke provenance table; not formal evidence |

## Key Numbers

### R5 WNUT17

| Block | Variant | Seeds | P_event | Hidden Conflict | Entity F1 | Reported use |
|---|---|---:|---:|---:|---:|---|
| R5a diagnostic stress | B0 | 10 | 0.0566 | 1.0000 | 0.0000 | hidden conflict evidence |
| R5a diagnostic stress | B4 | 10 | 0.3389 | 0.9963 | 0.0000 | event-mass movement |
| R5b feature nonzero-F1 check | B0 | 10 | 0.9824 | 0.0088 | 0.1660 | nonzero NER check |
| R5b feature nonzero-F1 check | B4 | 10 | 0.9865 | 0.0074 | 0.1522 | no F1 improvement |

### R6a Diagnostic And Uncertainty

| Score | AUROC | AUPRC | Spearman char error | Risk Gap |
|---|---:|---:|---:|---:|
| `1 - P_theta(L|x)` | 0.7088 | 0.8470 | 0.2869 | 0.4352 |
| token marginal entropy | 0.8036 | 0.8984 | 0.4953 | 0.6483 |
| sequence entropy | 0.7799 | 0.8783 | 0.4382 | 0.5976 |
| Viterbi margin inverse | 0.8105 | 0.8942 | 0.4535 | 0.6748 |
| max sequence probability inverse | 0.8083 | 0.8987 | 0.5153 | 0.7038 |

Complementarity check:

```text
Within generic-uncertainty deciles, event-risk residual gaps are not consistently positive.
Weighted within-bin gaps:
token entropy -0.0769, sequence entropy -0.0464, Viterbi margin +0.0368,
max sequence probability -0.0314, negative log Viterbi probability -0.0314.
```

Review task: determine what diagnostic claim, if any, these numbers support.

### Public CoNLL2000 Multiseed Formal Case

| Variant | Seeds | P(BIO\|x) mean | P(BIO\|x) std | Hidden Conflict | B7 Legal | Token Acc | Span F1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| B0 | 3 | 0.9837 | 0.0011 | 0.0133 | 1.0000 | 0.8731 | 0.7973 |
| B4 | 3 | 0.9885 | 0.0063 | 0.0123 | 1.0000 | 0.8697 | 0.7918 |

Public-case uncertainty:

| Variant | Score | AUROC exact | AUPRC exact | Spearman token error | Exact risk gap |
|---|---|---:|---:|---:|---:|
| B0 | event risk | 0.7384 | 0.8829 | 0.3117 | 0.4450 |
| B0 | strongest generic: sequence entropy | 0.8339 | 0.9405 | 0.4346 | not reported here |
| B4 | event risk | 0.6895 | 0.8865 | 0.2886 | 0.2650 |
| B4 | strongest generic: sequence entropy | 0.8178 | 0.9394 | 0.3785 | not reported here |

Review task: decide whether this is enough as a public structured-prediction case study, and whether any wording implies benchmark superiority.

Full three-seed CoNLL2000 was completed locally in
`experiments/runs/local_checks/public_conll2000_chunking_multiseed_full`
at git commit `002ecbb` with returncode `0` and duration `3076.544701`
seconds. The tiny three-seed run remains a wrapped smoke/provenance check and
appears only in `table_6a_public_conll2000_smoke`; it is not C13 evidence.

### B7 And R7 Formal Additions

| Block | Key result | Boundary |
|---|---|---|
| B7 constrained-product | B0-source legal rate `1.0000`, token accuracy `0.8841`, entity F1 `0.1486`; B4-source legal rate `1.0000`, token accuracy `0.8838`, entity F1 `0.1688` | decoding baseline only; does not use event mass for decoding |
| R7 date | B4 lambda 1.0: delta `P(event)=+0.2603`, delta exact accuracy `+0.1996` | sensitivity evidence, not accuracy theorem |
| R7 product_code | B4 lambda 1.0: delta `P(event)=+0.2079`, delta legal rate `+0.0328` | sensitivity evidence, not benchmark |
| R7 stock_like_digits | B4 lambda 1.0: delta `P(event)=+0.0769`, delta legal rate `+0.0000` | legal-rate-not-useful boundary |
| R7 product_code_swapped_rule | B4 lambda 1.0: delta `P(event)=+0.9485`, delta legal rate `+0.9716`, delta char accuracy `-0.5524`, delta exact accuracy `-0.0816` | wrapped-formal event/task tradeoff; event loss is not a general accuracy method |

## Current Claim Table Summary

The repository currently allows these claims, subject to boundaries in `docs/manuscript/FINAL_CLAIM_TABLE.md`:

- `P_theta(L|x)` is a well-defined finite CRF posterior event probability, used as a formal foundation.
- CRF x DFA product transfer computes `Z_{theta,L}(x)` exactly under finite-context/local-factor assumptions; this is the known computational neighborhood, not the novelty claim.
- Hard-constrained decoding and posterior consistency are different objects.
- Event loss has an expectation-difference gradient under explicit finite assumptions.
- Semi-event training can raise posterior event mass in audited settings.
- In the evaluated field-style diagnostics, low event mass has positive risk-ranking signal.
- Public CoNLL2000 provides a structured-prediction multiseed audit case with event-mass movement, hidden-conflict accounting, legal constrained decoding, and task-metric boundary behavior.
- B7 constrained-product decoding can be reported as a decoding comparison object that does not use event mass for decoding.
- R7 sensitivity shows lambda/rule-dependent movement and includes legal-rate-not-useful and wrapped-formal event/task tradeoff boundary cases.
- Product-state scaling can be discussed conservatively.

The repository currently forbids these claims:

- benchmark superiority;
- WNUT17 NER F1 improvement by B4;
- replacement or defeat of WFST / constrained CRF / RegCCRF;
- hard constraints are useless;
- calibration;
- event risk dominates entropy/margin/max-probability uncertainty;
- event risk adds robust residual predictive power after controlling for generic uncertainty;
- optimized runtime superiority;
- tensor rank / MPO as the main paper identity.
- product automaton inference itself is new.

## Current Readiness Boundary

```text
The project is not JMLR-main submission-ready and should not be described as
submission-ready. Manuscript drafting can proceed with conservative boundaries now
that B7, public CoNLL2000, and R7 sensitivity formal runs are audited, but
submission still requires final proof review, final related-work citations,
table/figure integration, and reproducibility packaging.
```

Review task: check whether the allowed list is still too broad, and whether any forbidden claim is implied elsewhere.

## Files To Review

```text
docs/manuscript/FINAL_CLAIM_TABLE.md
docs/manuscript/JMLR_METHODS_OUTLINE.md
docs/manuscript/PAPER_POSITIONING.md
docs/manuscript/RELATED_WORK_DRAFT.md
docs/manuscript/THEORY_PROOF_PROSE.md
docs/evidence/THEORY_AUDIT.md
docs/protocols/B7_WFST_DESIGN_NOTE.md
experiments/results/paper_tables/PAPER_TABLES_INDEX.md
experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/R6A_UNCERTAINTY_BASELINE_REANALYSIS.md
experiments/results/event_training/formal_pre_paper/JMLR_CPU_UPGRADE_RESULT_AUDIT.md
experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_FORMAL_AUDIT.md
experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_MULTISEED_TINY_SMOKE_AUDIT.md
experiments/results/event_training/formal_pre_paper/b7_constrained_product/B7_CONSTRAINED_PRODUCT_FORMAL_AUDIT.md
experiments/results/event_training/formal_pre_paper/r7_sensitivity/R7_SENSITIVITY_FORMAL_AUDIT.md
experiments/results/event_training/formal_pre_paper/r7_sensitivity/R7_SENSITIVITY_DERISK_AUDIT.md
```

## Review Questions

1. Is the project contribution novel enough if product automaton inference is treated as known?
2. Is the boundary against RegCCRF / constrained CRF technically valid?
3. Is the boundary against Posterior Regularization, Generalized Expectation, and Semantic Loss technically valid?
4. What does R5a support, given that entity F1 is zero?
5. What does R6a support, given that generic uncertainty baselines outperform event risk?
6. Is the B7 constrained-product implementation a faithful enough baseline for the manuscript boundary?
7. Which claim should be deleted or downgraded?
8. What theorem/proof wording is most vulnerable?
9. Are more experiments necessary before submission, or is the remaining work mainly proof/related-work/reproducibility integration?
10. Is there a coherent manuscript if event mass is weaker than generic uncertainty but rule-specific and interpretable?

## Requested Reviewer Output

Please return:

- overall assessment of contribution and venue fit;
- main objection;
- claim most likely to be overstated or unsupported;
- related-work gaps;
- theory/proof gaps;
- experiment gaps;
- whether B7 is faithful and sufficiently scoped;
- whether to proceed to writing, run additional experiments first, or reframe the project.
