# B7 Constrained-Product Formal Audit

B7 is a constrained-product Viterbi decoding baseline over CRF state x strict-BIO DFA state. It is not a full WFST system and does not use original posterior event mass for decoding.

## Provenance

- raw bundle: `experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/b7_constrained_product_formal`
- git commit: `a10517d`
- config: `experiments/configs/exp7/b7_constrained_product_formal.yaml`
- returncode: `0`
- duration_seconds: `89.849893`

## Rows

| source model | legal rate | token accuracy | entity F1 | event training | uses event mass for decoding |
|---|---:|---:|---:|---|---|
| B0_unconstrained | 1.0000 | 0.8841 | 0.1486 | False | False |
| B4_semi_event_0.1 | 1.0000 | 0.8838 | 0.1688 | True | False |

## Interpretation

Allowed: B7 verifies that a faithful constrained-product decoder can be reported separately from posterior event mass, with legal rate and task metrics.

Boundary: do not present this as a WFST replacement, constrained-CRF replacement, or evidence that event-mass training defeats constrained decoding.
