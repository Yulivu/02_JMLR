# Theory Proof Prose

Generated: 2026-05-28

This document converts `docs/audits/FRESH_PROOF_THEORY_AUDIT.md` into formal prose suitable for a methods/theory paper draft. It keeps the main theorem spine limited to finite posterior event mass and exact product transfer. Conditional rank/MPO material remains appendix-only.

## 1. Finite Posterior Event Setup

Let `Y` be a finite label alphabet and let `T` be a fixed finite sequence length. For a fixed input `x`, consider a CRF-style scoring function

```text
S_theta(x,y)
```

defined for every sequence `y = (y_1,...,y_T) in Y^T`. Assume all scores are finite real numbers. The ordinary CRF normalizer is

```text
Z_theta(x) = sum_{y in Y^T} exp(S_theta(x,y)).
```

Because `Y^T` is finite and every summand is positive and finite, `Z_theta(x)` is finite and strictly positive.

Let `L subseteq Y^*` be a regular language. Since the CRF is defined at length `T`, the relevant event is the finite slice

```text
L_T = L cap Y^T.
```

Define the event-restricted normalizer

```text
Z_{theta,L}(x) = sum_{y in L_T} exp(S_theta(x,y)).
```

This quantity is finite and nonnegative. It is zero exactly when no positive-mass length-`T` sequence lies in the event. The posterior event probability is

```text
P_theta(L | x) = Z_{theta,L}(x) / Z_theta(x).
```

Thus `P_theta(L|x)` is always well-defined in `[0,1]` under the finite setup.

## 2. Regular-Language Monitor

Let the regular language `L` be recognized by a complete deterministic finite automaton

```text
A_L = (Q, q_start, F, delta),
```

where `Q` is a finite state set, `q_start in Q` is the start state, `F subseteq Q` is the accepting set, and

```text
delta: Q x Y -> Q
```

is a total transition map. Completeness is used only to ensure that every label sequence in `Y^T` has a unique DFA trajectory. If a rule is originally specified by an incomplete automaton, it can be completed by adding a rejecting sink state.

For any sequence `y`, define the DFA trajectory:

```text
q_0 = q_start,
q_t = delta(q_{t-1}, y_t),  t = 1,...,T.
```

Then `y in L_T` if and only if `q_T in F`.

## 3. Local CRF Factorization

Assume the score admits a finite-context local factorization. Let `C` be a finite context state space, let `c_0 in C` be the fixed initial context, and let

```text
U: C x Y -> C
```

be a deterministic context update. For a sequence `y`, define

```text
c_t = U(c_{t-1}, y_t).
```

Assume the score can be written as

```text
S_theta(x,y) = sum_{t=1}^T phi_t(x, c_{t-1}, y_t),
```

where each local potential is finite. Define the corresponding positive local weight

```text
G_t(c,j) = exp(phi_t(x,c,j)).
```

The finite-context assumption covers the standard first-order linear-chain case and fixed higher-order Markov contexts. It is not a claim about arbitrary unbounded-memory models.

## 4. Product Event Transfer

Define the product state space

```text
C x Q.
```

For each time `t`, define a nonnegative transfer matrix `M_t^L` indexed by product states:

```text
M_t^L[(c,q),(c',q')]
= sum_{j in Y} G_t(c,j) 1[c' = U(c,j)] 1[q' = delta(q,j)].
```

Let `u_0` be the row vector that is one at `(c_0,q_start)` and zero elsewhere. Let `b_L` be the terminal column vector

```text
b_L(c,q) = 1[q in F].
```

The candidate product-transfer event mass is

```text
u_0 M_1^L M_2^L ... M_T^L b_L.
```

## 5. Exact Event Transfer Theorem

**Theorem.** Under the finite setup above,

```text
u_0 M_1^L M_2^L ... M_T^L b_L = Z_{theta,L}(x).
```

Consequently,

```text
P_theta(L | x)
= (u_0 M_1^L M_2^L ... M_T^L b_L) / Z_theta(x).
```

**Proof.** Fix a label sequence `y = (y_1,...,y_T) in Y^T`. Because the CRF context update `U` is deterministic and the initial context `c_0` is fixed, the sequence `y` induces a unique context trajectory:

```text
c_t = U(c_{t-1}, y_t).
```

Because the DFA transition `delta` is deterministic and complete, the same sequence induces a unique automaton trajectory:

```text
q_0 = q_start,
q_t = delta(q_{t-1}, y_t).
```

Thus `y` induces a unique product trajectory

```text
(c_0,q_0), (c_1,q_1), ..., (c_T,q_T).
```

At time `t`, the transfer entry from `(c_{t-1},q_{t-1})` to `(c_t,q_t)` contains the term

```text
G_t(c_{t-1}, y_t),
```

because `c_t = U(c_{t-1},y_t)` and `q_t = delta(q_{t-1},y_t)`. Therefore the weight of the product path induced by `y` is

```text
prod_{t=1}^T G_t(c_{t-1},y_t)
= prod_{t=1}^T exp(phi_t(x,c_{t-1},y_t))
= exp(sum_{t=1}^T phi_t(x,c_{t-1},y_t))
= exp(S_theta(x,y)).
```

Conversely, consider any nonzero product path contributing to

```text
u_0 M_1^L ... M_T^L b_L.
```

At each time step, a nonzero transfer contribution must arise from at least one label `j in Y` satisfying the deterministic updates

```text
c' = U(c,j),
q' = delta(q,j).
```

Reading these labels along the path gives a sequence `y in Y^T`. Since `U` and `delta` are deterministic and the path starts at `(c_0,q_start)`, this sequence reconstructs the same context and automaton trajectory. Thus the nonzero product paths are in weight-preserving correspondence with length-`T` label sequences, up to the standard aggregation over labels that lead to identical product transitions.

If two labels can induce the same product transition from a product state, the matrix entry sums their weights. Expanding the matrix product distributes over this finite sum, so each label sequence still contributes exactly its own product of local weights. No sequence weight is omitted or counted twice.

Finally, multiplication by `b_L` keeps exactly those paths with `q_T in F`. By correctness of the DFA, this is equivalent to `y in L_T`. Therefore the product transfer sums exactly the weights

```text
exp(S_theta(x,y))
```

over `y in L_T`, which is precisely `Z_{theta,L}(x)`. This proves the theorem.

## 6. Event Loss Corollary

If `Z_{theta,L}(x)>0`, then `P_theta(L|x)>0` and the event loss

```text
ell_event(x) = -log P_theta(L|x)
```

is finite and computable by the product-transfer expression above.

If `Z_{theta,L}(x)=0`, the event probability is zero and the log loss is infinite. Practical implementations may clamp or smooth this quantity, but such engineering choices are outside the exact finite theorem.

This corollary is only a computability statement. It is not a theorem that optimizing the event loss improves task accuracy.

## 7. Event-Loss Gradient Proposition

Assume the finite setup above, finite differentiable scores `S_theta(x,y)`, and `Z_{theta,L}(x)>0`. Because `Y^T` is finite, sums over sequences are finite and differentiation may be exchanged with summation. Define

```text
ell_event(theta; x) = -log P_theta(L|x)
                    = log Z_theta(x) - log Z_{theta,L}(x).
```

Then

```text
grad_theta ell_event(theta; x)
= E_{p_theta(y|x)}[grad_theta S_theta(x,y)]
  - E_{p_theta(y|x, y in L)}[grad_theta S_theta(x,y)].
```

Here

```text
p_theta(y|x) = exp(S_theta(x,y)) / Z_theta(x)
```

is the original CRF posterior, and

```text
p_theta(y|x, y in L)
= exp(S_theta(x,y)) 1[y in L_T] / Z_{theta,L}(x)
```

is the event-conditioned posterior.

**Proof.** Since the sequence space is finite,

```text
grad_theta log Z_theta(x)
= (1 / Z_theta(x)) sum_{y in Y^T} exp(S_theta(x,y)) grad_theta S_theta(x,y)
= E_{p_theta(y|x)}[grad_theta S_theta(x,y)].
```

Similarly, using `Z_{theta,L}(x)>0`,

```text
grad_theta log Z_{theta,L}(x)
= (1 / Z_{theta,L}(x)) sum_{y in L_T} exp(S_theta(x,y)) grad_theta S_theta(x,y)
= E_{p_theta(y|x, y in L)}[grad_theta S_theta(x,y)].
```

Subtracting these two identities gives the proposition.

This proposition explains the training signal: event loss pulls the unconstrained posterior sufficient-statistic expectation toward the event-conditioned posterior expectation. It is still only a computable training signal. It does not imply that task accuracy, benchmark F1, calibration, or constrained-decoding performance must improve.

## 8. Diagnostic Corollary

The scalar `P_theta(L|x)` is a posterior-level statistic attached to the model distribution itself. It can be evaluated independently of the decoded output. Therefore it can distinguish cases where constrained decoding returns a legal output but the original posterior assigns low mass to the legal event.

This is a semantic distinction, not a universal error theorem. Empirical diagnostics are required to test whether low event mass correlates with task error or hidden conflict.

## 9. Appendix-Only Conditional MPO Statement

The product transfer `M_t^L` is a nonnegative finite tensor under a fixed mode order. Suppose the following objects admit nonnegative MPO representations under a compatible augmented mode order:

1. the score table `G_t(c,j)`;
2. the context-shift indicator `1[c'=U(c,j)]`;
3. the DFA transition indicator `1[q'=delta(q,j)]`.

Then their pointwise product has an MPO representation whose bond dimension is bounded by the product of the component bond dimensions. Contracting the shared label mode yields an MPO representation of the event transfer.

This is a conditional membership statement. It does not imply that arbitrary CRFs, arbitrary DFAs, or arbitrary regular languages admit useful low-rank event transfers. It should remain appendix-only.

## 10. Appendix-Only Positive-Cone Approximation Bound

Let `M_t` be the exact nonnegative event transfer and let `hat M_t` be a nonnegative approximation. If for each `t`

```text
(1-rho_t) M_t <= hat M_t <= (1+rho_t) M_t
```

elementwise with `0 <= rho_t < 1`, then by monotonicity of multiplication by nonnegative matrices and nonnegative boundary vectors,

```text
prod_t(1-rho_t) Z_{theta,L}(x)
<= hat Z_{theta,L}(x)
<= prod_t(1+rho_t) Z_{theta,L}(x).
```

Posterior probability and log-probability versions require additional control of the denominator `Z_theta(x)` and strict positivity of the event mass. Without those assumptions, no posterior/log corollary should be stated.

## 11. Remaining Proof Gaps

No unclosable gap is currently identified in the main finite theorem spine.

Potential paper-writing gaps to handle carefully:

- `[GAP]` The appendix MPO statement still needs polished notation for the exact mode order if included.
- `[GAP]` Any posterior/log approximation corollary requires explicit denominator-control assumptions.
- `[GAP]` If the paper later expands beyond fixed finite `T`, the theorem statement must be revised.
