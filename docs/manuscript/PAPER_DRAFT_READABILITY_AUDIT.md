# Paper Draft Readability / Compile Audit

Date: 2026-05-31

## Verdict

```text
latex_structure_status = pass
pdf_compile_status = pending_no_local_tex_distribution
readability_status = draft_readable_with_table_width_risk
```

The current paper skeleton has a coherent claim-safe narrative and passes local
structure checks. PDF compilation is still pending because the local Windows
environment does not provide `latexmk`, `pdflatex`, `tectonic`, or `chktex`.

## Local Tool Availability

Checked commands:

```text
latexmk: unavailable
pdflatex: unavailable
tectonic: unavailable
chktex: unavailable
```

## Checks Run

```powershell
python scripts/analysis/check_paper_skeleton.py
python scripts/analysis/verify_jmlr_claim_evidence.py
python -m ruff check src scripts
python -m pytest src/tensor_crf_jmlr/posterior_event_algebra -q
python -m pytest src/tensor_crf_jmlr/event_training/tests -q
```

Current results:

```text
PASS paper skeleton check
PASS jmlr claim evidence verification
ruff: All checks passed
posterior_event_algebra: 29 passed, 14 subtests passed
event_training tests: 20 passed
```

Pytest emitted only cache-write permission warnings.

## Readability Notes

The draft now has:

- introduction with a closest-prior rebuttal and object-comparison table;
- related work that concedes CRF/automaton inference, RegCCRF, PR, GE,
  Semantic Loss, constrained optimization, uncertainty, and tensor-network
  neighbors;
- theory section with finite-context assumptions and proof text;
- methods section separating event mass, unconstrained legality, B7 constrained
  decoding, and task metrics;
- experiments section with narrative boundaries for WNUT17, R1/R2/R4, R6a,
  CoNLL2000, B7, and R7;
- limitations section with theory, empirical, uncertainty, and tensor-boundary
  limitations.

Main readability risk:

```text
Generated tables are structurally valid but may be too wide under the final JMLR
style. A later PDF compile pass should split or rotate wide tables if needed.
```

## Claim Wording Gate

`check_paper_skeleton.py` now checks for high-risk positive wording patterns.
It caught a potentially ambiguous "replace those interventions" phrase in the
introduction; the phrase was changed to "stand in for those interventions."

The paper still contains terms such as "replacement", "calibration", and
"benchmark superiority" only in negative or boundary contexts.

## Next Required Compile Step

Run on a machine with LaTeX:

```bash
cd paper
latexmk -pdf main.tex
```

Then inspect:

1. overfull/underfull boxes;
2. table width and page breaks;
3. undefined citations or references;
4. bibliography formatting;
5. theorem/proof readability under the final style.
