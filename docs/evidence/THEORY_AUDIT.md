# Theory Audit

Updated: 2026-05-29

This document is the single theory-audit entrypoint. It consolidates the earlier guardrail and fresh proof-check notes. Future theory-status updates should be made here, while paper-ready theorem prose should stay in `docs/manuscript/THEORY_PROOF_PROSE.md`.

## Verdict

```text
theory_spine_status = usable_with_guardrails
main_theory_scope = finite posterior event mass + exact product transfer + event-loss gradient
appendix_scope = conditional MPO/rank membership and positive-cone approximation support
proof_writing_status = paper-draft prose exists, final external proof review still recommended
```

## Core Object

Fix a finite label set `Y`, finite length `T`, input `x`, finite differentiable CRF-style score `S_theta(x,y)`, regular language `L`, and a complete DFA recognizing `L`.

The project object is:

```text
Z_theta(x) = sum_{y in Y^T} exp(S_theta(x,y))
L_T = L cap Y^T
Z_{theta,L}(x) = sum_{y in L_T} exp(S_theta(x,y))
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x)
```

The paper must stay tied to this object. Claims that do not involve `Z_{theta,L}(x)`, `P_theta(L|x)`, or the product event transfer are outside the main route.

## Main Theory Spine

| ID | Statement | Status | Scope |
|---|---|---|---|
| T0 | Finite posterior setup is well-defined. | Main | finite `Y,T`, finite scores |
| T1 | Product automaton transfer computes `Z_{theta,L}(x)` exactly. | Main | complete deterministic DFA, fixed sequence length |
| T2 | Event loss has a finite expectation-difference gradient when `Z_{theta,L}(x)>0`. | Main-with-boundary | computable training signal only |
| T3 | Conditional nonnegative MPO/rank membership. | Appendix only | explicit construction assumptions required |
| T4 | Positive-cone transfer approximation controls event mass multiplicatively. | Appendix only | nonnegative matrices; posterior/log versions need denominator and positivity assumptions |

## Exact Event Transfer

For order-`m` local factors:

```text
S_theta(x,y) = sum_t phi_t(x, c_{t-1}, y_t)
G_t(c,j) = exp(phi_t(x,c,j))
```

The product transfer is:

```text
M_t^L[(c,q),(c',q')]
= sum_{j in Y} G_t(c,j) 1[c'=U(c,j)] 1[q'=delta(q,j)]
```

The product state combines the CRF context and DFA state. Every label sequence maps to one product path. Every nonzero product path selects one label per step and maps back to one label sequence. The terminal vector accepts exactly paths whose DFA state is accepting. Therefore the accepted path-weight sum equals `Z_{theta,L}(x)`.

Required boundary:

```text
The exactness statement assumes finite labels, finite length, finite scores, and a complete deterministic DFA.
```

## Event-Loss Gradient

For `Z_{theta,L}(x)>0`, finite sums allow exchanging differentiation and summation:

```text
grad[-log P_theta(L|x)]
= E_{p_theta(y|x)}[grad S_theta(x,y)]
  - E_{p_theta(y|x, y in L)}[grad S_theta(x,y)]
```

Interpretation:

```text
The event loss pulls unconstrained posterior sufficient-statistic expectations toward event-conditioned posterior expectations.
```

Boundary:

```text
This is a computable training signal. It does not prove task accuracy improvement.
```

## Appendix-Only Theory

### Conditional MPO / Rank Membership

This can be stated only as a conditional construction result. Under a fixed mode order, if score factors, context-shift indicators, and DFA-transition indicators each have nonnegative MPO constructions under compatible modes, then the event transfer has a nonnegative MPO construction with a multiplicative rank bound.

Boundary:

```text
Do not claim arbitrary low-rank advantage.
Do not make tensor rank the paper identity.
```

### Positive-Cone Event-Mass Error

If transfers and approximations are nonnegative and:

```text
0 <= rho_t < 1
(1-rho_t) M_t^L <= hat M_t^L <= (1+rho_t) M_t^L
```

then the event numerator is bounded multiplicatively by the product of per-step error factors.

Boundary:

```text
Posterior and log-event bounds require denominator control and strict positivity.
Zero-event cases do not support relative/log event error.
```

## Code And Test Mapping

| Theory object | Code/Test |
|---|---|
| finite posterior and zero-event handling | `src/tensor_crf_jmlr/posterior_event_algebra/posterior_algebra.py`; `test_posterior_algebra.py` |
| complete DFA utilities | `src/tensor_crf_jmlr/posterior_event_algebra/dfa.py`; `test_dfa.py` |
| product transfer exactness | `src/tensor_crf_jmlr/posterior_event_algebra/product_transfer.py`; `test_product_transfer.py` |
| indexing and boundary conventions | `src/tensor_crf_jmlr/posterior_event_algebra/indexing.py`; `test_indexing_boundaries.py` |
| order-`m` context convention | `test_order_m_context.py` |
| conditional MPO sanity | `src/tensor_crf_jmlr/posterior_event_algebra/mpo_sanity.py`; `test_mpo_sanity.py` |
| event-loss behavior | `src/tensor_crf_jmlr/event_training/`; `test_event_crf.py` |

Current validation command:

```text
python -m pytest
47 passed
```

## Guardrails

Allowed in the main paper:

- posterior event identity;
- exact product automaton event transfer;
- event loss as a computable training signal;
- posterior event mass as an audit/diagnostic statistic.

Appendix only:

- conditional MPO/rank membership;
- positive-cone approximation bounds;
- implementation-level scaling sanity.

Forbidden:

- benchmark superiority;
- speed or memory superiority;
- arbitrary low-rank event transfer;
- arbitrary DFA low-rank transition;
- arbitrary regular-language shared rank;
- claim that automata product inference is new;
- claim that CRF regular constraints are new;
- claim that tests prove theory;
- claim that event loss guarantees task accuracy improvement.
