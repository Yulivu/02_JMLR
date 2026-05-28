# External Review README

Generated: 2026-05-28

Use this file as the entry point for an external AI/researcher review. The goal is to stress-test the project before manuscript writing, not to polish prose.

Current review commit:

```text
ffdb667
```

## One-Sentence Thesis

Decoded output legality is not posterior consistency. This project defines and computes the posterior mass assigned by the original CRF posterior to a regular-language event, then studies that scalar as an audit, training, and diagnostic object.

## Recommended Review Order

1. `docs/EXTERNAL_REVIEW_PACKET_V2.md`
2. `docs/FINAL_CLAIM_TABLE.md`
3. `docs/RELATED_WORK_DRAFT.md`
4. `docs/THEORY_PROOF_PROSE.md`
5. `experiments/results/paper_tables/PAPER_TABLES_INDEX.md`
6. `docs/B7_WFST_DESIGN_NOTE.md`
7. `docs/REPRODUCIBILITY_PACKAGE_CHECKLIST.md`

## What To Judge

| Question | Why it matters |
|---|---|
| Is the contribution defensible if CRF x automaton marginal inference is acknowledged as known? | main novelty risk |
| Is the boundary against posterior regularization, especially Ganchev et al. (2010), clear enough? | closest related-work risk |
| Is R5a acceptable as diagnostic-stress evidence despite zero entity F1? | empirical framing risk |
| Is R6a strong enough as risk-ranking evidence after accounting for base exact-error rate? | diagnostic claim strength |
| Can B7 remain design-only if the paper avoids superiority claims against WFST/constrained methods? | baseline risk |
| Are the theorem assumptions and proof prose complete enough for a methods/theory paper draft? | theory risk |

## Safe Positioning

```text
We define and compute the posterior mass assigned by the original CRF posterior to a regular-language event, and show that this scalar can reveal posterior inconsistency hidden by legal decoded outputs.
```

## Claims Not Allowed

- benchmark superiority;
- NER F1 improvement;
- WFST/constrained-method replacement;
- hard constraints are useless;
- posterior event mass is calibrated confidence;
- optimized runtime or low-rank superiority;
- tensor rank / MPO as the main paper identity.

## Evidence Snapshot

| Block | Use | Boundary |
|---|---|---|
| Theory | finite posterior event mass and exact product transfer | fixed finite label set, sequence length, complete DFA |
| R5a | BIO diagnostic-stress evidence that legal decoding can hide low posterior event mass | entity F1 is zero; not NER usefulness |
| R5b | nonzero local WNUT17 viability check | no B4 F1 improvement |
| R1/R2/R4 | event training can move posterior event mass | not uniformly task-metric dominant |
| R6a | low event mass is a field-style risk-ranking signal | not calibration; Spearman is moderate |
| R8 | reference product-state scaling evidence | not optimized runtime |

## Desired Reviewer Output

Please return:

1. verdict on whether this is a viable narrower JMLR methods/auditability paper;
2. strongest safe abstract framing;
3. weakest claim to delete or downgrade;
4. whether B7 must be implemented before submission;
5. missing citations or related-work risks;
6. theorem/proof gaps;
7. any experiment that is necessary before writing begins.

## Current Decision Rule

Do not run more HPC by default. Run new experiments only if external review identifies a specific claim that cannot be defended with the current R5/R1/R2/R4/R6a/R8 evidence package.
