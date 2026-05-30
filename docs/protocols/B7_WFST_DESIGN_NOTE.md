# B7 WFST-Style Design Note

Generated: 2026-05-30

## Decision

```text
B7 should be represented as a faithful constrained-product decoding baseline
when included in the JMLR package. It is not a full WFST system and must not be
used for superiority claims.
```

## Why B7 Matters

A reviewer may ask whether this paper is only constrained decoding in another form. B1/B3 already test hard-constrained decoding; B7 now adds a faithful constrained-product decoding baseline while keeping the claim scoped away from full WFST-system replacement.

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
experiments/configs/exp7/b7_constrained_product_formal.yaml
experiments/suites/b7_constrained_product_plan.yaml
experiments/results/event_training/formal_pre_paper/b7_constrained_product/B7_CONSTRAINED_PRODUCT_FORMAL_AUDIT.md
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

## Current Paper Strategy

Safe claim:

```text
The paper distinguishes posterior event mass from constrained decoding through
B1/B3, R5a, and the B7 constrained-product formal run. B7 reports legal output
behavior and task metrics without using original posterior event mass for
decoding.
```

Unsafe claim:

```text
The method outperforms WFST/constrained structured methods.
```

## Formal Run Status

Completed in the CPU upgrade block:

```text
raw bundle: experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/b7_constrained_product_formal
curated audit: experiments/results/event_training/formal_pre_paper/b7_constrained_product/B7_CONSTRAINED_PRODUCT_FORMAL_AUDIT.md
```

Observed rows:

```text
B0 source: legal rate 1.0000, token accuracy 0.8841, entity F1 0.1486
B4 source: legal rate 1.0000, token accuracy 0.8838, entity F1 0.1688
```

## Recommended Text If Full WFST Systems Are Omitted

```text
We include hard-constrained and constrained-product decoding baselines to
separate output legality from posterior consistency. A faithful comparison to
full WFST-style constrained training systems is outside the present scope
because our contribution is not a replacement decoder; it is an event
probability under the original posterior. We therefore avoid claims of
superiority over constrained structured methods.
```
