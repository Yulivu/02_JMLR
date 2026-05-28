# External Review Brief

Generated: 2026-05-28

Use this document when asking an outside AI/researcher to critique the project.

## Review Request

Please review whether this project is ready to proceed from pre-paper evidence into paper outlining. Focus on claim discipline, novelty positioning, and whether the empirical package is strong enough for a JMLR-style methods paper.

## Core Idea

```text
Decoded output legality is not posterior consistency.
```

The project defines:

```text
P_theta(L|x)
```

the posterior probability that a CRF assigns to a regular-language event `L`.

The intended contribution is not a new constrained decoder. The intended contribution is a posterior-level semantic object that can be computed, trained, and audited.

## Current Evidence

| Block | Result | Boundary |
|---|---|---|
| Theory | finite posterior event mass and exact product transfer are coherent | final proof prose still needed |
| R5a WNUT17 | hidden posterior BIO conflict is strong | diagnostic stress only; entity F1 is 0 |
| R5b WNUT17 | local feature CRF gets nonzero entity F1 | no B4 NER F1 improvement |
| R1 controlled | B4 raises event mass across controlled formats | controlled evidence only |
| R2 semi-real | B4 raises event mass across field-like tasks | task metrics not uniformly dominant |
| R4 real-source small | B4 raises event mass on invoice/stock fields | auxiliary small-field evidence |
| R6a diagnostic | low event mass predicts higher error on field-style tasks | not a task-improvement claim |
| R8 complexity | conservative product-transfer scaling measured | not optimized runtime or low-rank claim |

## Current Intended Claims

Allowed:

- `P_theta(L|x)` is a well-defined CRF posterior event object.
- Product automaton transfer computes event mass exactly.
- Semi-event training can raise posterior event mass.
- Hard-constrained decoding and posterior consistency are different.
- Low event mass is a useful diagnostic/risk signal in the audited field-style tasks.
- WNUT17 R5a demonstrates hidden posterior BIO conflict.

Not allowed:

- benchmark superiority;
- B4 improves WNUT NER F1;
- B4 dominates B5/B6 overall;
- hard constraints are useless;
- arbitrary low-rank advantage;
- optimized runtime superiority.

## Questions For Reviewer

1. Is the core object sufficiently distinct from constrained decoding and posterior regularization?
2. Is the paper better positioned as methods/theory, diagnostic/auditability, or empirical structured prediction?
3. Does the current evidence support a JMLR route if the claims are conservative?
4. Is B7 WFST-style baseline mandatory before paper submission?
5. Are R3/R7 sensitivity runs necessary, or can they be omitted with clear limitations?
6. Should rank/MPO material be appendix-only or removed entirely?
7. Is WNUT17 R5a acceptable as diagnostic evidence despite zero entity F1?
8. What is the sharpest reviewer objection?

## Files To Read

```text
docs/FINAL_CLAIM_TABLE.md
docs/PAPER_OUTLINE_DRAFT.md
docs/FRESH_PROOF_THEORY_AUDIT.md
docs/B7_R3_R7_ROUTE_DECISION.md
docs/PRE_PAPER_EVIDENCE_GATE.md
docs/AI_REVIEW_PACKET.md
```

## Desired Reviewer Output

Please provide:

1. strongest version of the paper thesis;
2. claims that are too strong;
3. missing baseline or experiment risks;
4. whether B7/R3/R7 should be run before drafting;
5. whether this should target JMLR or a narrower venue/positioning.
