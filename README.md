# 2_Tensor_CRF_JMLR

Working paper direction:

```text
Posterior Regular-Language Event Mass for Conditional Random Fields
```

Core identity:

```text
decoded output legality != posterior consistency
```

This repository studies `P_theta(L|x)`: the posterior probability that a CRF assigns to a regular-language event `L`. The goal is posterior-event semantics, auditability, event training, and diagnostic analysis. It is not a benchmark-superiority project, not a constrained-decoding replacement project, and not a tensor-rank paper.

## Current Status

```text
HPC paused.
Formal pre-paper evidence blocks completed and audited.
Claim-boundary cleanup, B7 smoke, public CoNLL2000 smoke, and sensitivity smoke are local-only additions.
Next step: external review plus full B7/public/sensitivity decisions, not broad AutoDL runs.
```

Completed audited blocks:

| Block | Role |
|---|---|
| R5 WNUT17 BIO/NER | hidden posterior conflict diagnostic evidence and task viability boundary |
| R1 controlled | controlled format robustness |
| R2 semi-real | field-like semi-real tasks |
| R4 real-source small | invoice/stock auxiliary small-field evidence |
| R6a diagnostic | field-style risk diagnostic |
| R8 complexity | reference CPU product-transfer scaling |
| B7 constrained-product smoke | local constrained decoding baseline smoke; full run pending |
| Public CoNLL2000 chunking smoke | public BIO/chunking boundary case; full run pending |
| R7 sensitivity smoke | local lambda/rule boundary smoke; full run pending |

Supported at current scope:

- `P_theta(L|x)` is a well-defined finite CRF posterior event object and formal foundation.
- Product automaton transfer computes event mass exactly under finite-context/local-factor assumptions; known product automaton marginal inference is the computational neighborhood, not the novelty claim.
- Semi-event training can raise posterior event mass in audited settings.
- Hard-constrained decoding and posterior consistency are different objects.
- In the evaluated field-style diagnostics, low event mass has positive risk-ranking signal.
- R8 supports conservative product-state complexity discussion.

Not supported:

- benchmark superiority;
- B4 improves WNUT17 NER F1;
- B4 dominates B5/B6 overall;
- hard constraints are useless;
- arbitrary low-rank advantage;
- optimized runtime superiority;
- product automaton inference itself is new;
- JMLR main draft-ready or submission-ready status.

## Repository Structure

```text
docs/
  README.md
  PROJECT_OVERVIEW.md
  manuscript/       manuscript planning: claims, outline, theory prose, related work
  external_review/  one-file external review packet
  protocols/        experiment, diagnostic, and baseline protocols
  evidence/         result evidence and theory audits
  runbooks/         AutoDL and FileZilla operational notes
  references/       retained papers and reading notes

data/
  raw retained datasets and manifests

experiments/
  configs/      hand-written experiment configs
  suites/       reproducible suite definitions
  runs/         raw machine outputs, ignored by Git
  results/      curated audit outputs

scripts/
  exp1/         thin experiment entrypoints
  analysis/     audit/export scripts
  data/         data checks
  hpc/          AutoDL/HPC helpers

src/tensor_crf_jmlr/
  posterior_event_algebra/
  event_training/
```

## Setup And Checks

```powershell
python -m pip install -e ".[dev]"
python -c "import tensor_crf_jmlr; print('tensor_crf_jmlr import ok')"
python -m pytest
python -m ruff check src scripts
```

Current expected check status:

```text
pytest: 49 passed
ruff: All checks passed
```

## Recommended Reading Order

For paper-writing handoff, start here:

1. `docs/HANDOFF_FOR_PAPER_WRITING.md`
2. `docs/EXPERIMENT_INVENTORY.md`
3. `docs/external_review/EXTERNAL_REVIEW_PACKET_CURRENT.md`
4. `docs/manuscript/FINAL_CLAIM_TABLE.md`
5. `docs/manuscript/RELATED_WORK_DRAFT.md`
6. `docs/manuscript/THEORY_PROOF_PROSE.md`
7. `experiments/results/paper_tables/PAPER_TABLES_INDEX.md`

For internal project orientation:

1. `docs/PROJECT_OVERVIEW.md`
2. `docs/manuscript/PAPER_POSITIONING.md`
3. `docs/manuscript/JMLR_METHODS_OUTLINE.md`
4. `docs/evidence/EVIDENCE_AND_AUDIT.md`

## AutoDL/HPC

Do not start new HPC jobs by default. Use AutoDL only if a post-review decision explicitly requires more experiments.

Runbook:

```text
docs/runbooks/AUTODL_HPC_RUNBOOK.md
```

Raw run outputs should stay under:

```text
experiments/runs/
```

Curated, reviewed outputs should go under:

```text
experiments/results/
```
