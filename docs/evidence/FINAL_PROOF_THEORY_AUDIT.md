# Final Proof / Theory Audit

Date: 2026-05-31

## Verdict

```text
internal_theory_audit = PASS_WITH_GUARDRAILS
submission_gate_status = not_final_external_review
```

The main finite theorem spine is defensible for a JMLR methods/auditability
paper if the manuscript keeps the stated assumptions visible. No current proof
text supports an arbitrary-score efficient algorithm, a new product-automaton
inference claim, an accuracy theorem, or a calibration theorem.

## Audited Files

- `docs/manuscript/THEORY_PROOF_PROSE.md`
- `docs/evidence/THEORY_AUDIT.md`
- `docs/manuscript/FINAL_CLAIM_TABLE.md`
- `src/tensor_crf_jmlr/posterior_event_algebra/`
- `src/tensor_crf_jmlr/event_training/`

## Theorem Scope Check

| Item | Status | Required paper wording |
|---|---|---|
| finite label alphabet `Y` | pass | state in theorem setup |
| fixed finite length `T` | pass | event is the finite slice `L cap Y^T` |
| finite scores | pass | all sums and gradients are finite sums |
| complete deterministic DFA | pass | incomplete rules must be completed with a rejecting sink |
| finite-context/local factorization | pass, essential | product transfer and scaling require this assumption |
| arbitrary finite score table | guarded | representable only by exponentially large context/table; not an efficiency claim |
| product-state scaling | guarded | applies only to the chosen finite-context implementation |

## Product Transfer

The product transfer theorem is sound under the finite-context/local
factorization:

```text
S_theta(x,y) = sum_t phi_t(x, c_{t-1}, y_t)
```

with deterministic context update `U` and complete DFA transition `delta`.
The proof correctly handles the case where multiple labels induce the same
product transition by summing label weights in the transfer entry.

Allowed:

```text
The event numerator can be computed exactly by a CRF-context x DFA product
transfer under finite-context/local-factor assumptions.
```

Forbidden:

```text
This is a new product-automaton inference algorithm for arbitrary CRF scores.
```

## Event-Loss Gradient

The gradient proposition is valid when:

- scores are finite and differentiable;
- the sequence space is finite;
- `Z_{theta,L}(x) > 0`.

The proof uses finite-sum differentiation and obtains:

```text
grad[-log P_theta(L|x)]
= E_p[grad S_theta] - E_{p(.|L)}[grad S_theta].
```

Boundary:

```text
This is a computable training signal. It does not prove task accuracy,
calibration, or benchmark improvement.
```

## Appendix Theory

MPO/rank membership and positive-cone approximation results remain appendix
only. They require explicit nonnegativity, mode-order, component-MPO, denominator
control, and strict-positivity assumptions. They must not become the paper's
main identity.

## Required Manuscript Gate

Before submission, run an independent proof read on the final LaTeX theorem
statements. The current repository prose is internally consistent, but it is
not a substitute for final external proof review.
