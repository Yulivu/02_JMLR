# Pre-Paper Evidence Gate

Generated: 2026-05-28

## Current Verdict

```text
formal_pre_paper_status = strong-but-not-paper-ready
hpc_status = pause
next_hpc_required_now = no
```

The current evidence is enough to stop running AutoDL jobs temporarily and do a local route review. The project has evidence for the posterior-event object, posterior-event training signal, diagnostic signal, and conservative complexity story. It still does not have benchmark superiority or a final paper-ready empirical package.

## Completed Formal Blocks

| Block | Status | Supports | Does Not Support |
|---|---|---|---|
| R5 WNUT17 BIO/NER | audited | hidden posterior conflict in R5a; WNUT17 viability in R5b | NER F1 superiority |
| R1 controlled | audited | B4 raises posterior event mass on controlled formats | real-task usefulness |
| R2 semi-real | audited | B4 raises event mass on field-like tasks | uniform task-metric dominance |
| R4 real-source small | audited | B4 raises event mass on invoice/stock fields | broad benchmark claim |
| R6a diagnostic | audited | low event mass predicts higher error on field-style tasks | task improvement by itself |
| R8 complexity | audited | conservative reference scaling story | optimized speed, GPU, low-rank, superiority |

## Supported Claims

1. `P_theta(L|x)` is a computable CRF posterior event object.
2. Product automaton transfer gives an exact finite event-mass computation.
3. Semi-event training can raise posterior event mass across controlled, semi-real, real-source, and WNUT diagnostic settings.
4. Hard-constrained decoding and posterior event consistency are different objects.
5. Low event mass is a useful field-style risk signal.
6. Hidden posterior conflict is demonstrated in WNUT R5a and partially in semi-real R6a diagnostics.
7. Reference product-transfer complexity can be discussed through sequence length, label count, DFA states, context order, and product-state count.

## Unsupported Claims

- benchmark superiority;
- B4 improves WNUT NER F1;
- B4 dominates B5/B6 overall;
- event training always improves task accuracy;
- optimized runtime advantage;
- arbitrary CRF/DFA/regular-language low-rank advantage;
- final JMLR-ready package without proof audit and final route review.

## Next Work Before Any New HPC

| Step | Action | HPC Needed |
|---|---|---:|
| G1 | update `AI_REVIEW_PACKET.md` with R1/R2/R4/R6/R8 audited status | no; done |
| G2 | write final claim table for paper route | no; done in `docs/FINAL_CLAIM_TABLE.md` |
| G3 | decide whether B7 WFST-style baseline is mandatory | no; done in `docs/B7_R3_R7_ROUTE_DECISION.md` |
| G4 | decide whether R3/R7 sensitivity is needed | no; done in `docs/B7_R3_R7_ROUTE_DECISION.md` |
| G5 | fresh proof-check / theory consistency audit | no; done in `docs/FRESH_PROOF_THEORY_AUDIT.md` |

## Possible Next HPC Only If Needed

| Candidate | Trigger | Priority |
|---|---|---|
| R3 low-label/unlabeled sensitivity | if reviewer route requires stronger semi-supervised story | medium |
| R7 lambda/rule sensitivity | if results need robustness around lambda/rule complexity | medium |
| B7 WFST-style baseline | if route review says constrained decoding baseline pressure is still too high | high only if feasible |

## Decision

```text
Do not start another HPC job now.
Local pre-paper route review and proof/claim audit are now complete at the document level.
Next step is paper-outline planning or external review, not HPC.
```
