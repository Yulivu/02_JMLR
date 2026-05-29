# External Review Packet V2

Generated: 2026-05-28

Use this shorter packet for a second external AI/researcher review after diagnostic reanalysis and positioning cleanup.

## Core Thesis

```text
Decoded output legality is not posterior consistency.
```

We define:

```text
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x)
```

the posterior mass assigned by the original CRF posterior to a regular-language event `L`.

## Current Proposed Title

```text
Posterior Regular-Language Event Mass for Conditional Random Fields
```

## What This Paper Is

- a methods/theory/auditability paper;
- an explicit posterior-event semantics paper;
- a diagnostic paper for hidden posterior conflict and field-style risk;
- a conservative event-training evidence paper.

## What This Paper Is Not

- not a benchmark-superiority paper;
- not an NER improvement paper;
- not a WFST replacement paper;
- not a tensor-rank paper;
- not a calibration paper.

## Evidence Snapshot

| Block | Main Evidence | Boundary |
|---|---|---|
| Theory | finite posterior event mass and exact product transfer | fixed finite `Y,T`, complete DFA |
| R5a | B0 `P(BIO|x)=0.0566` while constrained legality is 1; B4 raises event mass to `0.3389` | diagnostic-stress evidence, not NER performance |
| R5b | B0 entity F1 `0.1660` | no B4 F1 improvement |
| R1/R2/R4 | B4 raises event mass across controlled, semi-real, and real-source blocks | not uniformly task-metric dominant |
| R6a | base exact-error rate `0.7359`; event-risk AUROC `0.7088`, AUPRC `0.8470`; uncertainty baselines are stronger and complementarity is mixed | rule-specific posterior-consistency signal, not calibration, uncertainty superiority, or residual predictiveness |
| R8 | reference product-transfer scaling measured | not optimized runtime or low-rank evidence |

## Files To Review

```text
docs/paper/FINAL_CLAIM_TABLE.md
docs/paper/JMLR_METHODS_OUTLINE.md
docs/paper/THEORY_PROOF_PROSE.md
docs/paper/RELATED_WORK_DRAFT.md
docs/protocols/B7_WFST_DESIGN_NOTE.md
docs/protocols/DIAGNOSTIC_REANALYSIS_PLAN.md
experiments/results/paper_tables/PAPER_TABLES_INDEX.md
experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/R6A_UNCERTAINTY_BASELINE_REANALYSIS.md
```

## Review Questions

1. Is the novelty defensible if we openly admit product automaton marginal inference is a known computational primitive?
2. Is the distinction from Ganchev et al. 2010 / posterior regularization clear enough?
3. Is R5a acceptable as diagnostic-stress evidence despite zero entity F1?
4. Does R6a make the diagnostic contribution strong enough for a methods/auditability paper?
5. Is the uncertainty-baseline and weak-complementarity result handled conservatively enough?
6. Is B7 implementation mandatory if we avoid superiority claims?
7. Are R3/R7 still optional if we do not claim robustness over label/unlabeled/lambda regimes?
8. Is the proposed title too narrow, too broad, or appropriate?
9. What exact claim would you delete before submission?

## Desired Output

Please provide:

- verdict on JMLR route;
- strongest safe abstract framing;
- weakest or most vulnerable claim;
- required experiments, if any;
- required related-work changes;
- proof gaps, if any;
- whether B7 must be implemented before submission.
