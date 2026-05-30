# B7 Constrained-Product Decoding Baseline Audit Template

Updated: 2026-05-30

This template records the intended paper row schema for B7. Formal B7 evidence is now curated in `experiments/results/event_training/formal_pre_paper/b7_constrained_product/B7_CONSTRAINED_PRODUCT_FORMAL_AUDIT.md`; this file remains a schema for future reruns.

## Paper Table Row Schema

| block | variant | source model | legal rate | token accuracy | entity/span F1 | uses event training | uses event mass for decoding | notes |
|---|---|---|---:|---:|---:|---|---|---|
| `b7_constrained_product_decode` | `B7_constrained_product_decode` | `B0_unconstrained` or trained source | pending | pending | pending | source-dependent | false | constrained-product Viterbi over CRF x DFA; decoding baseline only |

## What It Answers

- Whether a faithful constrained-product decoder using the same language `L` can produce legal outputs.
- What task metrics that legal decoder obtains under the chosen source CRF.
- How decoded legality differs from original posterior event mass.

## What It Does Not Answer

- It is not a full WFST toolkit.
- It is not constrained-CRF or RegCCRF training.
- It does not show B4 superiority over constrained structured methods.
- It must not use original `P_theta(L|x)` as a B7 advantage, except as a separate audit diagnostic.

## Full Run Status

```text
status = pending
smoke_command = python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/b7_constrained_product_smoke.yaml --out-dir experiments/runs/local_checks/b7_constrained_product_smoke
formal_command = python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/b7_constrained_product_formal.yaml --out-dir experiments/runs/autodl_jmlr_block/b7_constrained_product/wnut17_feature
```
