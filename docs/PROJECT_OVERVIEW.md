# Project Overview

Updated: 2026-05-29

## Core Direction

```text
Posterior Regular-Language Event Mass for Conditional Random Fields
```

The project studies one object:

```text
P_theta(L|x)
```

This is the probability mass that the original CRF posterior assigns to a regular-language rule `L`. The central distinction is:

```text
decoded output legality != posterior consistency
```

Hard-constrained decoding can return a legal output, but that does not tell us whether the model posterior assigns substantial mass to legal structures. This project makes that hidden posterior consistency question computable and auditable.

## Current Stage

The project is no longer an early idea search. It is in the pre-paper review stage:

| Area | Status | Notes |
|---|---|---|
| theory object | stable | finite CRF posterior event mass and product transfer |
| source code | stable for current claims | posterior algebra and event training tests pass |
| formal evidence | audited | R5, R1/R2/R4, R6a, R8 completed |
| claim table | frozen for review | conservative main/boundary/appendix split |
| paper positioning | narrowed | methods/theory/auditability, not benchmark superiority |
| HPC | paused | no new AutoDL job unless review requires a specific experiment |
| next step | paper-writer handoff / external review | stress-test novelty, proof assumptions, related work, and empirical framing |

## Supported Claims

Safe current claims:

- `P_theta(L|x)` is a well-defined finite CRF posterior event probability.
- Product automaton transfer computes the event numerator exactly under the finite setup.
- Hard-constrained decoding and posterior consistency are different objects.
- Semi-event training can raise posterior event mass in audited settings.
- Low event mass is a rule-specific posterior-consistency signal with positive risk-ranking value, but it is not stronger than generic uncertainty baselines in R6a.
- Reference product-state scaling can be discussed conservatively.

Do not claim:

- benchmark superiority;
- WNUT17 NER F1 improvement;
- WFST/constrained-method replacement;
- hard constraints are useless;
- calibrated confidence;
- optimized runtime superiority;
- arbitrary low-rank or tensor-rank advantage.

## Main Evidence Blocks

| Block | Role | Boundary |
|---|---|---|
| R5a WNUT17 diagnostic stress | shows legal constrained outputs can hide low posterior BIO mass | entity F1 is zero; diagnostic only |
| R5b WNUT17 viability | shows local CRF setup gets nonzero entity F1 | no B4 F1 improvement claim |
| R1 controlled | controlled event-mass movement evidence | not a real benchmark |
| R2 semi-real | field-like event-mass movement evidence | not general task superiority |
| R4 real-source small | auxiliary invoice/stock evidence | small-field scope only |
| R6a diagnostic | rule-specific risk/audit evidence from event mass | not calibration; not uncertainty-baseline superiority |
| R8 complexity | product-state scaling evidence | reference CPU only |

## Directory Map

```text
docs/
  PROJECT_OVERVIEW.md          main project state
  README.md                    docs index and reading order
  manuscript/                  manuscript planning: claims, outline, theory, related work
  external_review/             one-file external review packet
  protocols/                   experiment, diagnostic, and baseline protocols
  evidence/                    result evidence, guardrails, and theory audits
  runbooks/                    AutoDL / FileZilla operational notes
  references/                  papers and reading notes

src/tensor_crf_jmlr/
  posterior_event_algebra/     reusable posterior event algebra
  event_training/              reusable event-training utilities and tests

experiments/
  configs/                     hand-written experiment configs
  suites/                      reproducible suite definitions
  runs/                        raw run bundles, ignored by Git
  results/                     curated audited outputs
  visualizations/              paper-facing visual artifacts

scripts/
  exp1/                        experiment entrypoints
  analysis/                    audit and table generation scripts
  data/                        data checks/download helpers
  hpc/                         AutoDL/HPC helpers
```

## Reading Order

For external review:

1. `docs/HANDOFF_FOR_PAPER_WRITING.md`
2. `docs/external_review/EXTERNAL_REVIEW_PACKET_CURRENT.md`
3. `docs/EXPERIMENT_INVENTORY.md`
4. `docs/manuscript/FINAL_CLAIM_TABLE.md`
5. `docs/manuscript/RELATED_WORK_DRAFT.md`
6. `docs/manuscript/THEORY_PROOF_PROSE.md`
7. `experiments/results/paper_tables/PAPER_TABLES_INDEX.md`

For internal orientation:

1. `docs/PROJECT_OVERVIEW.md`
2. `docs/manuscript/PAPER_POSITIONING.md`
3. `docs/protocols/EXPERIMENT_PLAN.md`
4. `docs/evidence/EVIDENCE_AND_AUDIT.md`
5. `docs/evidence/THEORY_AUDIT.md`

## uMPS Relation

uMPS work suggests that regular languages can be treated as probabilistic events. This project transfers that idea to conditional CRF posteriors: instead of asking whether a generated string lies in a regex event, it asks how much posterior mass a CRF assigns to a regular-language label rule.

## Immediate Next Step

External review. Do not run more HPC until review identifies a concrete missing experiment tied to a specific claim.
