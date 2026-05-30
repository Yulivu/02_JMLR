# R7 Sensitivity De-Risk Audit

This audit adds an explicit negative boundary to R7. The `product_code_swapped_rule` data are generated as product codes, but the event rule audits the swapped pattern `DD-LLL`. This rule is intentionally weakly related to task correctness.

## Provenance

- raw bundle: `experiments/runs/local_checks/r7_sensitivity_derisk_formal_wrapped`
- git commit: `a10517d`
- curation repo state: `a10517d+dirty`
- config: `experiments\configs\exp7\r7_sensitivity_formal.yaml`
- returncode: `0`
- duration_seconds: `28.276712`
- started_at_utc: `2026-05-30T04:35:22.878145+00:00`
- ended_at_utc: `2026-05-30T04:35:51.154857+00:00`

Wrapper command:

```text
python scripts/exp1/run_event_training_task.py --config experiments\configs\exp7\r7_sensitivity_formal.yaml --out-dir experiments\runs\local_checks\r7_sensitivity_derisk_formal_wrapped
```

Executed module command:

```text
C:\Users\debuf\AppData\Local\Programs\Python\Python312\python.exe -m tensor_crf_jmlr.event_training.sensitivity_probe --seed-count 10 --difficulty-levels easy_saturated medium hard irrelevant_rule --workers 0 --output-dir experiments\runs\local_checks\r7_sensitivity_derisk_formal_wrapped
```

## Key Rows

| task | variant | runs | P(event) | delta P | delta legal rate | delta char acc | delta exact acc | boundary |
|---|---|---:|---:|---:|---:|---:|---:|---|
| date | B0_unconstrained | 10 | 0.7136 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | ordinary |
| date | B4_semi_event_1.0 | 10 | 0.9738 | +0.2603 | +0.1948 | +0.0306 | +0.1996 | ordinary |
| product_code | B0_unconstrained | 10 | 0.7765 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | ordinary |
| product_code | B4_semi_event_1.0 | 10 | 0.9844 | +0.2079 | +0.0328 | +0.0097 | +0.0248 | ordinary |
| product_code_swapped_rule | B0_unconstrained | 10 | 0.0000 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | event/task tradeoff |
| product_code_swapped_rule | B4_semi_event_0.1 | 10 | 0.6083 | +0.6083 | +0.6752 | -0.4352 | -0.0668 | event/task tradeoff |
| product_code_swapped_rule | B4_semi_event_1.0 | 10 | 0.9486 | +0.9485 | +0.9716 | -0.5524 | -0.0816 | event/task tradeoff |
| stock_like_digits | B0_unconstrained | 10 | 0.9192 | +0.0000 | +0.0000 | +0.0000 | +0.0000 | legal-rate-not-useful |
| stock_like_digits | B4_semi_event_1.0 | 10 | 0.9961 | +0.0769 | +0.0000 | +0.0331 | +0.0868 | legal-rate-not-useful |

## Interpretation

Allowed: event loss can move posterior event mass, but if the rule is weakly related or misleading for the task, task metrics can degrade sharply.

Boundary: this directly rules out any claim that event loss is a general accuracy method. It also shows why the paper must treat rule choice as an audit-design assumption.
