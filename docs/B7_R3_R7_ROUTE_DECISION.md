# B7 / R3 / R7 Route Decision

Generated: 2026-05-28

## Decision

```text
run_more_hpc_now = no
B7_status = design_required_before_paper, not immediate HPC
R3_status = optional, defer
R7_status = optional, defer
```

The current formal package is strong enough to pause AutoDL and continue local route review. The next risk is not missing compute; it is overclaiming.

## B7 WFST-Style Baseline

| Question | Decision |
|---|---|
| Is B7 needed before the next HPC run? | no |
| Is B7 needed before paper submission? | likely needs design discussion; implementation depends on positioning |
| Why not run now? | B7 is a baseline-design problem, not a compute problem |
| Current mitigation | B1/B3 hard-constrained decoding already separate output repair from posterior mass |

Recommended handling:

```text
Write a B7 design note before implementing anything.
If the paper claims superiority over constrained structured methods, implement B7.
If the paper claims posterior-event auditability, B7 can be scoped as related-work pressure with a clear distinction.
```

Risk:

```text
Reviewers may ask whether this is only constrained decoding in another form.
```

Response:

```text
The paper should emphasize that constrained decoding changes the selected output, while `P_theta(L|x)` measures posterior mass. R5a is the cleanest empirical evidence for this distinction.
```

## R3 Low-Label / Unlabeled Sensitivity

| Question | Decision |
|---|---|
| Is R3 needed now? | no |
| When would R3 become necessary? | if the paper wants a strong semi-supervised learning claim |
| Current evidence | R2 and R4 already show B4 raises event mass; existing learning-curve outputs exist inside semi-real/real-source runners |
| Main risk | without R3, do not claim a broad low-label advantage |

Current allowed claim without R3:

```text
Semi-event training can raise posterior event mass under the tested labeled/unlabeled settings.
```

Not allowed without R3:

```text
Semi-event training is robustly better across low-label and unlabeled-size regimes.
```

## R7 Lambda / Rule Sensitivity

| Question | Decision |
|---|---|
| Is R7 needed now? | no |
| When would R7 become necessary? | if reviewers need robustness around lambda, unlabeled size, or rule complexity |
| Current evidence | R1/R2/R4 include multiple B4 lambda rows; R8 covers complexity scaling |
| Main risk | high lambda can trade task accuracy for event mass |

Current allowed claim without R7:

```text
The tested default and nearby event-loss settings move posterior event mass upward.
```

Not allowed without R7:

```text
The method is insensitive to lambda or rule complexity.
```

## Next Action

```text
Do not run B7/R3/R7 now.
Write proof/claim-consistency audit and then decide paper positioning.
```

If another HPC round is later approved, the priority order should be:

1. B7 only if claiming against constrained structured methods.
2. R3 only if claiming semi-supervised/low-label robustness.
3. R7 only if claiming sensitivity robustness.
