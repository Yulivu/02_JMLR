# R7 Lambda / Rule Sensitivity Formal Audit

This formal run studies how event-mass movement and task metrics vary with lambda and rule difficulty. It is a boundary study, not an accuracy benchmark.

## Provenance

- raw bundle: `experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/r7_sensitivity_formal`
- git commit: `a10517d`
- config: `experiments/configs/exp7/r7_sensitivity_formal.yaml`
- returncode: `0`
- duration_seconds: `13.726078`

## Key Rows

| task | variant | runs | P(event) | delta P | delta legal rate | delta exact acc | boundary |
|---|---|---:|---:|---:|---:|---:|---|
| date | B0_unconstrained | 10 | 0.7136 | +0.0000 | +0.0000 | +0.0000 | ordinary |
| date | B4_semi_event_1.0 | 10 | 0.9738 | +0.2603 | +0.1948 | +0.1996 | ordinary |
| product_code | B0_unconstrained | 10 | 0.7765 | +0.0000 | +0.0000 | +0.0000 | ordinary |
| product_code | B4_semi_event_1.0 | 10 | 0.9844 | +0.2079 | +0.0328 | +0.0248 | ordinary |
| stock_like_digits | B0_unconstrained | 10 | 0.9192 | +0.0000 | +0.0000 | +0.0000 | legal-rate-not-useful |
| stock_like_digits | B4_semi_event_1.0 | 10 | 0.9961 | +0.0769 | +0.0000 | +0.0872 | legal-rate-not-useful |

## Boundary Rows

| task | legal-rate not useful | best event variant | best delta P | best exact variant | best delta exact | tradeoff observed |
|---|---|---|---:|---|---:|---|
| date | False | B4_semi_event_1.0 | 0.2602620032727718 | B4_semi_event_1.0 | 0.1996 | False |
| product_code | False | B4_semi_event_1.0 | 0.20787990701198578 | B4_semi_event_0.05 | 0.044800000000000006 | False |
| stock_like_digits | True | B4_semi_event_1.0 | 0.07686075954437258 | B4_semi_event_1.0 | 0.0872 | False |

## Interpretation

Allowed: event loss can move posterior event mass, and the movement depends on lambda and rule difficulty. The `stock_like_digits` row is a useful boundary because legal-rate movement is not informative there.

Boundary: do not claim event training always improves task metrics or that this sensitivity probe is benchmark evidence.
