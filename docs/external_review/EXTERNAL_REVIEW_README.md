# External Review README

Updated: 2026-05-30

Use this file as the entry point for an external AI/researcher review. The purpose is to evaluate the project state before manuscript writing. The reviewer should identify strengths, weaknesses, overclaims, missing citations, proof gaps, and missing experiments.

Review target:

```text
Review the repository HEAD that contains this file.
```

## Project Claim Under Review

The project defines and computes the posterior mass assigned by the original CRF posterior to a regular-language event:

```text
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x)
```

The repository currently positions this object as separate from constrained decoding and constrained CRF normalization. The review should test whether that distinction is sufficient for a manuscript contribution.

## Recommended Review Order

1. `docs/external_review/EXTERNAL_REVIEW_PACKET_CURRENT.md`
2. `docs/manuscript/FINAL_CLAIM_TABLE.md`
3. `docs/manuscript/RELATED_WORK_DRAFT.md`
4. `docs/manuscript/THEORY_PROOF_PROSE.md`
5. `experiments/results/paper_tables/PAPER_TABLES_INDEX.md`
6. `docs/protocols/B7_WFST_DESIGN_NOTE.md`
7. `docs/manuscript/REPRODUCIBILITY_PACKAGE_CHECKLIST.md`
8. `experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/R6A_UNCERTAINTY_BASELINE_REANALYSIS.md`

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
| Is B7 necessary before manuscript writing or only before stronger baseline claims? | baseline sufficiency |
| Which current claim is most likely to be rejected by a reviewer? | claim discipline |
| Which experiment, if any, is required before writing begins? | remaining work |

## Claims To Check For Overstatement

The current repository says these claims should not be made. Please verify whether any remaining document still implies them:

- benchmark superiority;
- WNUT17 NER F1 improvement by B4;
- replacement or defeat of WFST / constrained CRF / RegCCRF;
- hard constraints are useless;
- calibration;
- event risk dominates entropy, margin, or max-probability uncertainty;
- event risk adds robust residual predictive power after controlling for generic uncertainty;
- optimized runtime superiority;
- tensor rank / MPO as the main paper identity.

## Evidence Snapshot

| Block | Reported use | Reported boundary |
|---|---|---|
| Theory | finite posterior event mass and exact product transfer | fixed finite label set, sequence length, complete DFA |
| R5a | BIO diagnostic-stress evidence | entity F1 is zero; not NER usefulness |
| R5b | local WNUT17 feature-CRF nonzero-F1 check | no B4 F1 improvement |
| R1/R2/R4 | event training moves posterior event mass in audited settings | not uniform task-metric dominance |
| R6a | rule-specific risk-ranking signal | not calibration; generic uncertainty baselines are stronger |
| R8 | reference product-state scaling | not optimized runtime |

## Requested Review Output

Please return:

1. overall assessment of manuscript readiness and likely venue fit;
2. main objection to the contribution;
3. claim most likely to be overstated or unsupported;
4. related-work gaps and specific citation needs;
5. theory/proof gaps;
6. experiment gaps;
7. whether B7 should be implemented before writing;
8. whether the current project should proceed to drafting, run more experiments first, or be reframed.
