# B7 WFST-Style Design Note

Generated: 2026-05-28

## Decision

```text
B7 implementation is not required before the next local drafting step.
B7 design discussion is required before submission.
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

## What B7 Should Not Be

Do not implement a weak strawman. A weak B7 would be worse than omitting it.

Avoid:

- a duplicate of B1 with a different name;
- a hand-coded rule repairer;
- a baseline that changes data splits or label vocabulary;
- a baseline used to claim superiority without faithful implementation.

## Current Paper Strategy Without B7 Implementation

Safe claim:

```text
The paper distinguishes posterior event mass from constrained decoding through B1/B3 and R5a.
```

Unsafe claim:

```text
The method outperforms WFST/constrained structured methods.
```

## Trigger For Implementing B7

Implement B7 only if the final paper claims:

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
