# AI Review Packet

Generated: 2026-05-28

Purpose: one-file external review packet for the project idea, theory object, current evidence, experiment route, stage, and main risks.

Reviewer should judge:

1. whether the posterior-event object is distinct enough from constrained decoding, rule features, and posterior regularization;
2. whether current claims are too strong or too weak;
3. whether the pre-paper formal experiment route is enough for a JMLR submission path;
4. whether the BIO/NER slice, baselines, diagnostics, and complexity story still have obvious gaps;
5. how to position the paper if B4 is useful diagnostically but not empirically dominant.

## 1. One-Sentence Idea

This project studies:

```text
Tensorized Regular-Language Posterior Algebra for CRFs
```

Plain version:

```text
Do not only ask whether the final CRF output satisfies a rule.
Compute how much probability mass the whole CRF posterior assigns to rule-satisfying outputs:
P_theta(L | x).
```

Core distinction:

```text
decoded output legality != posterior consistency
```

## 2. Motivation

Hard-constrained decoding can repair the final output, but it can hide model uncertainty or internal conflict. A model may output a legal sequence after constrained decoding while most of its posterior probability still sits on illegal structures.

This project turns a rule from an output-time filter into a posterior event:

| Use | Meaning |
|---|---|
| Audit | legal top output but low `P_theta(L|x)` means the model does not strongly believe the rule |
| Training | `-log P_theta(L|x)` can be used as an event loss |
| Diagnostic | low `P_theta(L|x)` can expose hidden conflict or risk |
| Theory | product automaton transfer computes event mass exactly; rank/MPO material is appendix-only support |

## 3. Relation To uMPS

One sentence:

```text
uMPS shows that regular languages can be computable events inside probabilistic sequence models; this project connects that view to CRF conditional posteriors and studies P_theta(y in L | x).
```

| uMPS | This Project |
|---|---|
| generative sequence model | conditional CRF posterior |
| asks whether generated strings fall in a regex event | asks whether tag posteriors believe a regular-language rule |
| focuses on u-MPS tensor-network models | focuses on CRF posterior event mass |
| `P(s in R)` | `P_theta(y in L | x)` |

## 4. Theory Object

Given finite labels, fixed sequence length, input `x`, CRF-style scores, regular language `L`, and a complete DFA recognizing `L`, the core object is:

```text
Z_theta(x)       = total CRF normalizer
Z_{theta,L}(x)   = mass of sequences accepted by L
P_theta(L | x)   = Z_{theta,L}(x) / Z_theta(x)
```

Product automaton idea:

```text
CRF local context state x DFA state
```

Accepted product paths correspond to label sequences satisfying the rule, so summing those path weights gives the event mass.

## 5. Current Stage

Current status:

```text
P5 passed.
AutoDL target-machine smoke passed.
R5 WNUT17 formal AutoDL runs completed and downloaded.
R5 result-to-claim audit completed locally.
The project is still pre-paper; it is not JMLR-ready yet.
```

Roadmap:

| Phase | Goal | Status | Evidence / Artifact | Remaining |
|---|---|---|---|---|
| P0 | problem definition | done | mainline fixed | none |
| P1 | theory object closed loop | mostly done | posterior algebra, DFA/product-transfer tests | fresh proof-check |
| P2 | local mechanism validation | mostly done | controlled/semi-real/real-source probes | not benchmark evidence |
| P3 | experiment protocol freeze | done | frozen protocol, baseline table, run list, WNUT17 data gate | revise only through explicit protocol updates |
| P4 | local R0 smoke | done | controlled/semi-real/real-source smoke + schema audit | smoke only |
| P5 | AutoDL/HPC engineering | done | target-machine preflight and smoke passed | none |
| R5 | WNUT17 BIO/NER formal slice | audited | R5a/R5b 10-seed AutoDL outputs and claim audit | use only within its claim boundaries |
| P6 | full formal runs | partial / next | R5 done; R1-R4/R6-R8 still planned | controlled, semi-real, real-source, diagnostic, complexity formal blocks |
| P7 | full result-to-claim audit | not started | R5 audit exists | requires all formal blocks |
| P8 | pre-writing freeze | not started | docs/code foundation | final figures/tables/limitations/repro package |

## 6. R5 Formal Result Summary

Curated audit output:

```text
experiments/results/event_training/formal_pre_paper/r5_wnut17/R5_RESULT_TO_CLAIM_AUDIT.md
experiments/results/event_training/formal_pre_paper/r5_wnut17/r5_wnut17_audit_summary.csv
```

### R5a Diagnostic Stress

10 seeds, word-id CRF, low-resource stress.

Key audited means:

| Variant | `P(BIO|x)` | delta vs B0 | hidden conflict | entity F1 |
|---|---:|---:|---:|---:|
| B0 | 0.0566 | 0.0000 | 1.0000 | 0.0000 |
| B4 | 0.3389 | 0.2822 | 0.9963 | 0.0000 |
| B5 | 0.1608 | 0.1042 | 1.0000 | 0.0000 |
| B6 | 0.1703 | 0.1137 | 1.0000 | 0.0000 |

Interpretation:

```text
R5a supports hidden posterior conflict and shows semi-event training can raise posterior BIO mass.
R5a does not support NER task usefulness because entity F1 is zero.
```

### R5b Feature Viability

10 seeds, feature CRF, larger train/unlabeled/dev setting.

Key audited means:

| Variant | `P(BIO|x)` | delta vs B0 | hidden conflict | entity F1 |
|---|---:|---:|---:|---:|
| B0 | 0.9824 | 0.0000 | 0.0088 | 0.1660 |
| B4 | 0.9865 | 0.0041 | 0.0074 | 0.1522 |
| B5 | 0.9864 | 0.0040 | 0.0058 | 0.1645 |
| B6 | 0.9868 | 0.0044 | 0.0060 | 0.1463 |

Interpretation:

```text
R5b shows WNUT17 is not an all-O toy because B0 gets nonzero entity F1.
R5b does not support a B4 NER F1 improvement claim.
Posterior BIO mass is already saturated, so hidden-conflict conclusions belong to R5a.
```

## 7. Supported And Unsupported Claims

Currently supported:

1. `P_theta(L|x)` is a computable CRF posterior event signal.
2. Product automaton transfer computes event mass in finite sanity tests.
3. Event loss has meaningful local gradients.
4. Controlled/semi-real/real-source probes support posterior event training as a route.
5. R5a supports the hidden posterior conflict narrative on a canonical BIO/NER slice.
6. R5b supports WNUT17 task viability but not method superiority.

Currently unsupported:

- JMLR-ready empirical package;
- benchmark superiority;
- B4 improving NER F1;
- B4 dominating B5/B6 overall;
- hard constraints being useless;
- arbitrary low-rank advantage for all CRF/DFA/regular-language cases;
- full diagnostic/calibration claim.

## 8. Baselines

| ID | Name | Purpose | Required |
|---|---|---|---|
| B0 | unconstrained CRF | original baseline | yes |
| B1 | B0 + hard-constrained decoding | distinguish output repair from posterior training | yes |
| B2 | labeled event training | event term on labeled samples | yes |
| B3 | event training + hard constraint | check complementarity with hard decoding | yes |
| B4 | semi-event training | main method | yes |
| B5 | rule-feature CRF | rule-as-feature baseline | yes |
| B6 | posterior-regularization-style | posterior constraint baseline | yes |
| B7 | WFST-style constrained objective/eval | reviewer pressure baseline | design if feasible |

Reviewer pressure point:

```text
If B5/B6 are competitive or stronger, the paper should not claim empirical dominance.
The defensible positioning becomes posterior-event algebra, auditability, and diagnostic value.
```

## 9. Next Formal Work

The next work should not expand concepts. It should complete the evidence package:

| Block | Purpose | Priority |
|---|---|---|
| R1 controlled robustness | show mechanism stability across synthetic regular languages | high |
| R2 semi-real main | test B0-B6 under field-like formats | high |
| R3 low-label/unlabeled sensitivity | show when event training helps | medium |
| R4 real-source small auxiliary | keep retail fields as auxiliary evidence | medium |
| R6 diagnostic full | test whether low event mass predicts error/conflict | high |
| R8 complexity scaling | answer DFA x CRF cost questions | high |
| B7 design | handle WFST/constrained-method reviewer pressure | medium |

## 10. Key Risks

| Risk | Impact | Mitigation |
|---|---|---|
| reviewer sees this as constrained decoding variant | paper identity weakens | emphasize posterior event mass, not decode-time repair |
| B4 does not improve task F1 | no superiority claim | position around posterior consistency and diagnostics |
| B5/B6 are competitive | empirical novelty weaker | compare what each baseline can and cannot audit |
| diagnostic fails outside R5a | remove or narrow diagnostic claim | run R6 before writing |
| complexity story missing | reviewer will question scalability | run R8 and write CRF x DFA product complexity clearly |
| proof-check fails | theory section blocked | repair before paper drafting |

## 11. Minimal Repository Pointers

```text
docs/PROJECT_OVERVIEW.md
docs/PAPER_POSITIONING.md
docs/ROUTE_REVIEW_CHECKLIST.md
docs/EXPERIMENT_PLAN.md
docs/EVIDENCE_AND_AUDIT.md
docs/THEORY_AND_GUARDRAILS.md
docs/R5_WNUT17_FORMAL_PROTOCOL.md
experiments/results/event_training/formal_pre_paper/r5_wnut17/R5_RESULT_TO_CLAIM_AUDIT.md
src/tensor_crf_jmlr/posterior_event_algebra/
src/tensor_crf_jmlr/event_training/
```

## 12. Current Bottom Line

The project is no longer only an idea. It has a clear research object, theory/code sanity, local mechanism evidence, an organized repo, AutoDL workflow, and one audited canonical BIO/NER formal block.

It is still not ready for paper writing. The next decision is how to complete P6 without overclaiming: use R5 as evidence for posterior conflict and task viability, then run controlled/semi-real/real-source/diagnostic/complexity blocks to decide whether the final paper is a JMLR-strength methods paper or a narrower posterior-event algebra and auditability paper.
