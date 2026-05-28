# Main Theorem Proof Draft

Generated: 2026-05-28

This is a draft for paper-outline planning. It is not final polished theorem prose.

## Setup

Let `Y` be a finite label set and let `T` be a fixed finite sequence length. For a fixed input `x`, let a CRF-style model assign a finite score:

```text
S_theta(x,y)
```

to each sequence `y in Y^T`.

Let `L` be a regular language over `Y`, recognized by a complete deterministic finite automaton:

```text
A_L = (Q, q_start, F, delta)
```

where:

- `Q` is a finite state set;
- `q_start in Q`;
- `F subset Q`;
- `delta: Q x Y -> Q` is total.

Define:

```text
Z_theta(x) = sum_{y in Y^T} exp(S_theta(x,y))
Z_{theta,L}(x) = sum_{y in L cap Y^T} exp(S_theta(x,y))
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x)
```

Since `Y^T` is finite and all scores are finite, `Z_theta(x)` is finite and positive, and `Z_{theta,L}(x)` is finite and nonnegative.

## Local Factor Form

Assume the score decomposes with finite local context:

```text
S_theta(x,y) = sum_{t=1}^T phi_t(x, c_{t-1}, y_t)
```

where `c_t = U(c_{t-1}, y_t)` is a deterministic context update and `c_0` is fixed.

Define nonnegative local weights:

```text
G_t(c,j) = exp(phi_t(x,c,j)).
```

## Product Transfer

Define product states:

```text
(c,q)
```

where `c` is a CRF context and `q` is a DFA state.

For each time `t`, define the event transfer:

```text
M_t^L[(c,q),(c',q')]
= sum_{j in Y} G_t(c,j) 1[c'=U(c,j)] 1[q'=delta(q,j)].
```

Let `u_0` be the one-hot row vector at `(c_0,q_start)`.

Let `b_L` be the terminal vector:

```text
b_L(c,q) = 1[q in F].
```

## Theorem

For the finite CRF and complete DFA setup above:

```text
u_0 M_1^L M_2^L ... M_T^L b_L = Z_{theta,L}(x).
```

Therefore:

```text
P_theta(L|x) = (u_0 M_1^L ... M_T^L b_L) / Z_theta(x).
```

## Proof

Fix any label sequence:

```text
y = (y_1,...,y_T) in Y^T.
```

The CRF context update gives a unique context trajectory:

```text
c_t = U(c_{t-1}, y_t).
```

The DFA transition gives a unique automaton trajectory:

```text
q_t = delta(q_{t-1}, y_t),
q_0 = q_start.
```

Thus `y` defines a unique product path:

```text
(c_0,q_0), (c_1,q_1), ..., (c_T,q_T).
```

At step `t`, the transfer entry corresponding to this transition contains the term:

```text
G_t(c_{t-1}, y_t).
```

Because both `U` and `delta` are deterministic, this term contributes to exactly the transition selected by `y_t`.

The product-path weight is therefore:

```text
prod_{t=1}^T G_t(c_{t-1}, y_t)
= prod_{t=1}^T exp(phi_t(x,c_{t-1},y_t))
= exp(sum_{t=1}^T phi_t(x,c_{t-1},y_t))
= exp(S_theta(x,y)).
```

Conversely, any nonzero product path through the transfer sequence must choose at least one label `j in Y` at each time step. Reading these labels gives a sequence `y in Y^T`. Determinism of `U` and `delta` ensures that this sequence reconstructs the same product path. Thus nonzero product paths are in one-to-one correspondence with label sequences.

The terminal vector `b_L` keeps exactly those paths whose final DFA state satisfies:

```text
q_T in F.
```

By definition of the DFA, this is equivalent to:

```text
y in L.
```

Therefore summing all accepted product-path weights gives:

```text
sum_{y in L cap Y^T} exp(S_theta(x,y)) = Z_{theta,L}(x).
```

This proves the identity.

## Boundary Conditions

The theorem requires:

- finite `Y`;
- finite fixed `T`;
- finite CRF scores;
- deterministic complete DFA;
- fixed context update convention.

The theorem does not claim:

- optimized inference speed;
- arbitrary low-rank structure;
- superiority over constrained decoding;
- benchmark usefulness.

## Event Loss

When `Z_{theta,L}(x)>0`, one may define:

```text
ell_event(x) = -log P_theta(L|x).
```

This is a computable training signal under the same finite product-transfer setup.

This is not an optimization theorem. It only states that the loss is well-defined and computable when the event probability is positive.

## Diagnostic Object

The scalar:

```text
P_theta(L|x)
```

can be used as a diagnostic statistic for posterior consistency. This is an empirical use of the theory object, not a theorem that low event mass always implies error.
