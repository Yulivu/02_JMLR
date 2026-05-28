# Fresh Proof / Theory Consistency Audit

Generated: 2026-05-28

This is a local consistency audit before paper drafting. It is not a substitute for final theorem writing or external proof review.

## Verdict

```text
theory_spine_status = usable_with_guardrails
main_theory_scope = T0 + T1 + event-loss/diagnostic object
appendix_scope = T2/T3 conditional support
proof_writing_status = not yet final
```

## Main Theory Spine

| Item | Status | Evidence | Remaining Work |
|---|---|---|---|
| finite posterior setup | pass | `posterior_algebra.py`; accept-all/empty/singleton tests | write clean theorem statement |
| `P_theta(L|x)` definition | pass | brute-force event probability tests, zero-event handling | specify finite `Y,T` and complete DFA |
| product automaton transfer exactness | pass | `test_product_transfer.py` matches brute force for context-order and first-order cases | write proof with one-to-one path/sequence mapping |
| boundary conventions | pass | `test_indexing_boundaries.py`, `test_order_m_context.py` | state indexing convention once in paper |
| event loss as trainable signal | empirical/mechanism pass | event CRF tests and formal runs | avoid theorem-style optimization claim |
| diagnostic object | empirical pass | R5a and R6a | keep diagnostic as empirical claim |

## Proof Checks

### T0 finite setup

The finite setup is coherent if:

```text
Y is finite
T is finite
S_theta(x,y) is finite for all y in Y^T
L_T = L cap Y^T
```

Then `Z_theta(x)` is a finite positive sum and `Z_{theta,L}(x)` is finite and nonnegative. If `L_T` is empty, `P_theta(L|x)=0`.

Status:

```text
PASS
```

### T1 exact product transfer

The product state combines:

```text
CRF context c_t
DFA state q_t
```

For each label sequence, the deterministic context update and deterministic DFA transition define one product path. Conversely, every nonzero product path selects a label at each step and therefore corresponds to one label sequence. The path weight is the product of local CRF weights, equal to `exp(S_theta(x,y))`. The terminal vector selects exactly accepted DFA states.

Status:

```text
PASS for finite deterministic complete DFA setup
```

Required paper boundary:

```text
The proof assumes a complete deterministic automaton and fixed finite sequence length.
```

### T2 conditional MPO/rank membership

The current rank/MPO material is a construction sanity check. It supports a conditional appendix statement only:

```text
If score, shift, and DFA transition indicators each have nonnegative MPO constructions under a common mode order, then their product/label contraction yields a nonnegative MPO construction for the event transfer with multiplicative rank bound.
```

Status:

```text
PASS as appendix-only conditional membership
FAIL as main low-rank theorem
```

Required boundary:

```text
Do not claim arbitrary low-rank advantage.
Do not make tensor rank the paper identity.
```

### T3 positive-cone approximation

The elementwise nonnegative multiplicative bound is coherent for event mass if:

```text
0 <= (1-rho_t) M_t <= hat M_t <= (1+rho_t) M_t
```

and all transfers/boundary vectors are nonnegative. Posterior and log versions need denominator control and positivity.

Status:

```text
PASS as appendix-only approximation support
```

Required boundary:

```text
No posterior/log corollary without denominator and strict positivity assumptions.
```

## Code/Test Mapping

| Claim | Code/Test |
|---|---|
| finite posterior and zero-event handling | `test_posterior_algebra.py` |
| product transfer exactness | `test_product_transfer.py` |
| order-m context convention | `test_order_m_context.py` |
| indexing boundaries | `test_indexing_boundaries.py` |
| complete DFA utilities | `test_dfa.py` |
| conditional MPO sanity | `test_mpo_sanity.py` |

Current validation command:

```text
python -m pytest
47 passed
```

## Required Guardrails For Paper Draft

Allowed in main text:

- finite posterior event definition;
- exact product automaton event transfer;
- event loss as a computable training signal;
- posterior event mass as an audit/diagnostic statistic.

Move to appendix or keep optional:

- conditional MPO/rank membership;
- positive-cone approximation bounds;
- implementation-level scaling sanity.

Forbidden:

- arbitrary low-rank theorem;
- optimized runtime claim;
- benchmark superiority;
- hard constraints are useless;
- formula tests prove theory.

## Final Theory Decision

```text
Proceed to paper-outline planning only if the main theorem spine remains T0/T1.
Do not expand the theory section around rank/MPO.
Before final writing, convert this audit into formal theorem/proof prose and, ideally, get an external proof check.
```
