# Paper Skeleton

This directory is a claim-safe JMLR manuscript skeleton. It is not a final
submission manuscript.

## Regenerate Tables

```powershell
python scripts/analysis/generate_paper_tables.py
python scripts/analysis/generate_latex_tables.py
python scripts/analysis/verify_jmlr_claim_evidence.py
python scripts/analysis/check_paper_skeleton.py
```

## Compile

If a LaTeX distribution is installed:

```bash
cd paper
latexmk -pdf main.tex
```

The local Windows environment used to create this skeleton did not have
`latexmk` or `pdflatex` available, so PDF compilation is still pending.

## Claim Discipline

The skeleton intentionally frames the project as posterior-semantics and
auditability work. It does not claim:

- a new product automaton inference algorithm;
- benchmark superiority;
- replacement of WFST, constrained decoding, regular-constrained CRFs,
  posterior regularization, or semantic loss;
- uncertainty dominance or calibration;
- general task-accuracy improvement from event loss.
