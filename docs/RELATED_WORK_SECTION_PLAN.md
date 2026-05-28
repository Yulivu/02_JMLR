# Related Work Section Plan

Generated: 2026-05-28

## Purpose

This document prevents novelty overclaiming. The paper should openly acknowledge that CRF x automaton product inference is a known computational neighborhood. The contribution is the posterior-event object and audit semantics.

## Required Opening

Suggested paragraph:

```text
Our computation is closely related to classical dynamic programming for CRFs, automata-constrained sequence models, and WFST-style product constructions. We do not claim that product inference with automata is new. Our focus is instead the posterior event probability assigned by the original CRF posterior to a regular-language rule, and the use of that scalar as an audit, training, and diagnostic object.
```

## Constrained Decoding / WFST

Safe distinction:

| Existing Work | This Paper |
|---|---|
| compute legal best path or legal constrained inference | compute mass assigned by original posterior to a legal event |
| changes or restricts decoding | can audit without changing the decoder |
| answers "what legal output should I return?" | answers "how much does the model believe the rule?" |

Do not say:

```text
constrained decoding is useless
```

Say:

```text
constrained decoding solves output legality, while posterior event mass audits posterior consistency.
```

## Posterior Regularization / Ganchev et al. 2010

Closest-neighbor framing:

```text
Posterior regularization introduces constraints on posterior distributions and optimizes models under those constraints. Our object is an explicit regular-language event probability under the original CRF posterior. Event loss is one possible use of this object, but the object itself is also an audit statistic.
```

Boundary table:

| Posterior Regularization | Posterior Event Mass |
|---|---|
| constraint-driven learning framework | posterior semantic object |
| often uses expectation constraints or projected posteriors | computes `Z_{theta,L}(x)/Z_theta(x)` |
| changes training/inference objective | can be reported without changing decoding |
| asks how to impose constraints | asks how much original posterior mass satisfies a rule |

Prohibited sentence:

```text
Posterior regularization cannot handle posterior constraints.
```

Allowed sentence:

```text
Our emphasis differs: we make the regular-language event probability itself the reportable object.
```

## Confidence Calibration

Safe distinction:

```text
Calibration asks whether model probabilities match empirical correctness. We ask whether a structured regular-language event receives posterior mass. R6a is a risk diagnostic, not a calibration theorem.
```

## Lagrangian Relaxation

Safe distinction:

```text
Lagrangian relaxation optimizes constrained objectives. Our quantity evaluates an event under the original posterior and can be used even when the decoded output is repaired separately.
```

## Tensor Networks / uMPS

Safe distinction:

```text
uMPS work motivates probability of regular-language events in generative sequence models. This paper moves the event-mass view to conditional CRF posteriors.
```

Rank/MPO material should be appendix-only.

## Reviewer Risk

Most dangerous objection:

```text
This is just CRF marginal inference on a product automaton.
```

Response:

```text
We agree that the computational primitive is adjacent to product automaton marginal inference. The contribution is to define, operationalize, and empirically audit the posterior regular-language event mass under the original CRF posterior, especially where legal decoded outputs mask low event mass.
```
