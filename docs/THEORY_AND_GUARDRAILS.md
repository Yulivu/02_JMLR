# Theory And Guardrails

生成时间：2026-05-26

## 1. 不可变核心对象

固定有限标签集 `Y`、有限长度 `T`、输入 `x`、有限 CRF-style score `S_theta(x,y)`、正则语言 `L`，以及识别 `L` 的 complete DFA：

```text
A_L = (Q, q_start, F, delta)
```

核心对象：

```text
Z_theta(x) = sum_{y in Y^T} exp(S_theta(x,y))
L_T = L cap Y^T
Z_{theta,L}(x) = sum_{y in L_T} exp(S_theta(x,y))
P_theta(L|x) = Z_{theta,L}(x) / Z_theta(x)
```

order-`m` local factor：

```text
S_theta(x,y) = sum_t phi_t(x, c_{t-1}, y_t)
G_t(c,j) = exp(phi_t(x,c,j))
```

product event transfer：

```text
M_t^L[(c,q),(c',q')]
= sum_{j in Y} G_t(c,j) 1[c'=U(c,j)] 1[q'=delta(q,j)]
```

任何 claim 如果不绑定 `Z_{theta,L}(x)`、`P_theta(L|x)` 或 `M_t^L`，都视为偏离主线。

## 2. Theorem Package

Main-paper theorem spine:

```text
finite setup -> exact product transfer -> event loss / diagnostic object
```

Appendix-only theory support:

```text
conditional MPO/rank membership and positive-cone approximation bounds
```

This distinction is intentional. The paper identity is posterior event semantics, not tensor complexity theory.

| ID | Statement | Status | Scope |
|---|---|---|---|
| T0 | finite posterior setup is well-defined | main | finite `Y,T`, finite score |
| T1 | product automaton transfer computes `Z_{theta,L}(x)` exactly | main | complete DFA, fixed convention |
| T2 | event transfer has conditional nonnegative MPO rank membership | appendix / optional | needs explicit `r_g/r_shift/r_A` assumptions |
| T3 | positive-cone transfer approximation controls event mass multiplicatively | appendix / optional | nonnegative matrices and boundary vectors |
| C1 | posterior probability control | appendix / conditional | needs numerator and denominator control |
| C2 | log event/posterior control | appendix / conditional | needs strict positivity |

## 3. Exact Event Algebra

The product automaton starts at `(c_0,q_start)`. For any label sequence `y_1:T`:

```text
c_t = U(c_{t-1}, y_t)
q_t = delta(q_{t-1}, y_t)
```

Each label sequence corresponds to one product path, and each nonzero product path corresponds to one label sequence. The path weight is:

```text
prod_t G_t(c_{t-1}, y_t)
= exp(sum_t phi_t(x,c_{t-1},y_t))
= exp(S_theta(x,y))
```

The terminal vector accepts exactly paths whose DFA state is in `F`, so summing accepted path weights gives:

```text
Z_{theta,L}(x) = sum_{y in L cap Y^T} exp(S_theta(x,y))
```

Then:

```text
P_theta(L|x)=Z_{theta,L}(x)/Z_theta(x)
```

## 4. Conditional Nonnegative MPO Rank Membership

Placement:

```text
appendix only unless needed for a specific approximation/scaling argument.
```

Reviewer-risk note:

```text
Do not let this theorem become the paper identity.
It is weaker and more conditional than the posterior-event semantics contribution.
```

Under a fixed mode order, suppose:

1. score factor `G_t(c,j)` has a nonnegative MPO construction with rank `r_g`;
2. context shift indicator `1[c'=U(c,j)]` has rank `r_shift`;
3. DFA transition indicator `1[q'=delta(q,j)]` has rank `r_A`;
4. all constructions lift to a common augmented mode order;
5. label contraction is performed on the explicit constructed cores.

Then:

```text
rank_MPO^+(M_t^L) <= r_g r_shift r_A
```

This is a membership result, not a universal low-rank theorem.

Useful boundaries:

- for `m=1`, current shift rank can be 1;
- for `m>=2`, explicit shift-register construction gives order `|Y|+1`;
- worst-case DFA bookkeeping gives `r_A <= |Q||Y|`;
- structured monitors may be smaller, but that is an example, not a general theorem.

## 5. Positive-Cone Event-Mass Error

If event transfers and approximations are nonnegative and:

```text
0 <= rho_t < 1
(1-rho_t) M_t^L <= hat M_t^L <= (1+rho_t) M_t^L
```

elementwise, then:

```text
prod_t(1-rho_t) Z_{theta,L}(x)
<= hat Z_{theta,L}(x)
<= prod_t(1+rho_t) Z_{theta,L}(x)
```

Posterior/log versions need extra assumptions:

- `Z_theta(x)` or its approximation must also be controlled;
- log bounds require `Z_{theta,L}(x)>0`;
- zero-event cases do not support relative/log event error.

## 6. Code Sanity Mapping

| Theory object | Code |
|---|---|
| finite posterior sums | `src/tensor_crf_jmlr/posterior_event_algebra/posterior_algebra.py` |
| complete DFA identity | `src/tensor_crf_jmlr/posterior_event_algebra/dfa.py` |
| product transfer exactness | `src/tensor_crf_jmlr/posterior_event_algebra/product_transfer.py` |
| indexing and boundary conventions | `src/tensor_crf_jmlr/posterior_event_algebra/indexing.py` |
| order-`m` context | `src/tensor_crf_jmlr/posterior_event_algebra/tests/test_order_m_context.py` |
| tiny nonnegative MPO sanity | `src/tensor_crf_jmlr/posterior_event_algebra/mpo_sanity.py` |

Current test status:

```text
python -m pytest src/tensor_crf_jmlr/posterior_event_algebra -q
29 passed, 14 subtests passed
```

## 7. Guardrails

Allowed:

- posterior event identity;
- product automaton event-mass representation;
- conditional event-transfer rank membership as appendix support only;
- positive-cone event-mass error as appendix support only;
- posterior/log corollaries under extra positivity and denominator conditions as appendix support only;
- unit tests as sanity evidence only.

Forbidden:

- JMLR-ready claim;
- benchmark superiority;
- speed/memory advantage;
- arbitrary CRF low-rank event transfer;
- arbitrary DFA low-rank transition;
- arbitrary regular language shared rank;
- “automata product inference is new”;
- “CRF regular constraint is new”;
- “formula checks prove theorem”;
- “rank sanity proves usefulness”.

## 8. Theory Gate

```text
GO: use this package as the theory basis.
GO: keep T0/T1 in the main paper spine.
WARN: T2 is conditional membership, not low-rank superiority.
WARN: T2/T3 should not distract from posterior event semantics.
WARN: posterior/log corollaries need denominator and positivity control.
HOLD: paper theorem prose until fresh proof-check.
HOLD: arbitrary low-rank claim.
```
