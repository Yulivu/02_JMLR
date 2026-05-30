# B7 WFST-Style Design Note

Generated: 2026-05-28

## Decision

```text
B7 should be represented as a faithful constrained-product decoding baseline
when included in the JMLR package. It is not a full WFST system and must not be
used for superiority claims.
```

## Why B7 Matters

A reviewer may ask whether this paper is only constrained decoding in another form. B1/B3 already test hard-constrained decoding, but B7 would address stronger WFST-style constrained structured-method pressure.

## What B7 Would Need To Be

A faithful B7 should represent a constrained structured baseline that:

1. uses the same rule/DFA language `L`;
2. returns legal decoded outputs;
3. reports task metrics under constrained decoding;
4. does not report `P_theta(L|x)` under the original posterior unless explicitly augmented to do so;
5. is compared against B4 only within a clearly scoped claim.

Implemented local path:

```text
src/tensor_crf_jmlr/event_training/constrained_product_baseline.py
experiments/configs/exp7/b7_constrained_product_smoke.yaml
experiments/suites/b7_constrained_product_plan.yaml
```

Name in paper tables:

```text
B7 constrained-product decoding baseline
```

Do not call this a full WFST system. The implementation is faithful to the
same regular language because it decodes over CRF label state x DFA state. It
answers whether a constrained-product decoder can return legal outputs and what
task metric it obtains.

## What B7 Should Not Be

Do not implement a weak strawman. A weak B7 would be worse than omitting it.

Avoid:

- a duplicate of B1 with a different name;
- a hand-coded rule repairer;
- a baseline that changes data splits or label vocabulary;
- a baseline used to claim superiority without faithful implementation.

## Current Paper Strategy If Full B7 Is Not Run

Safe claim:

```text
The paper distinguishes posterior event mass from constrained decoding through B1/B3, R5a, and a local B7 constrained-product smoke if available.
```

Unsafe claim:

```text
The method outperforms WFST/constrained structured methods.
```

## Full-Run Trigger

Run full B7 only if the final paper needs a reviewer-facing constrained-structured baseline row or claims:

```text
empirical superiority over constrained structured methods
```

or if external review says:

```text
the distinction from constrained decoding is not credible without a WFST-style baseline.
```

## Recommended Text If B7 Is Omitted

```text
We include hard-constrained decoding baselines to separate output legality from posterior consistency. A faithful comparison to full WFST-style constrained training or inference systems is outside the present scope because our contribution is not a replacement decoder; it is an event probability under the original posterior. We therefore avoid claims of superiority over constrained structured methods.
```
