# R7 Lambda / Rule Sensitivity Protocol

Updated: 2026-05-30

## Purpose

R7 tests whether event loss behavior is sensitive to lambda and rule difficulty. It is a boundary study: the goal is to report tradeoffs and negative/saturated cases, not to prove task-metric superiority.

## Implemented Runner

```text
src/tensor_crf_jmlr/event_training/sensitivity_probe.py
experiments/configs/exp7/r7_sensitivity_smoke.yaml
experiments/configs/exp7/r7_sensitivity_formal.yaml
experiments/suites/r7_sensitivity_plan.yaml
```

## Rule Difficulty Levels

| Level | Task | Role |
|---|---|---|
| `easy_saturated` | short digit field | boundary case where event mass may already be high |
| `medium` | product code `LL-DDD` | mixed-format event |
| `hard` | date-like field | longer rule with more positions |

## Lambda Values

Uses existing `LAMBDA_VARIANTS`:

```text
B0, B4 lambda 0.05, 0.1, 0.2, 0.5, 1.0
```

## Smoke Command

```powershell
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/r7_sensitivity_smoke.yaml --out-dir experiments/runs/local_checks/r7_sensitivity_smoke
```

## Formal Command

```powershell
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/r7_sensitivity_formal.yaml --out-dir experiments/runs/autodl_jmlr_block/r7_sensitivity/lambda_rule_difficulty
```

## Acceptance Criteria

- Report multiple lambda values.
- Report multiple rule difficulty levels.
- Include at least one saturated or unhelpful boundary case, such as a rule where event mass moves but decoded legal rate or task metric does not materially improve.
- Report event mass vs legal rate vs exact/task metric tradeoff.
- Do not suppress negative rows.

## Claim Boundary

Allowed:

```text
Event loss can move posterior event mass, but task effects depend on lambda and rule difficulty.
```

Forbidden:

```text
Event loss always improves accuracy or event mass is always useful.
```
