# Diagnostic Reanalysis Plan

Generated: 2026-05-28

## Motivation

R6a bottom/top quantile evidence is strong, but a JMLR reviewer may want more than quantile gaps if diagnostic value is a main contribution.

Current R6a supports:

```text
low event mass is associated with higher error in field-style tasks
```

It does not yet fully support:

```text
calibration or complete diagnostic ranking evaluation
```

## Recommended Local Reanalysis

No new HPC is needed. Use the existing R6a `diagnostic_cases.csv`.

Add metrics:

| Metric | Purpose |
|---|---|
| AUROC | ranking quality for predicting exact error |
| AUPRC | performance under high-error imbalance |
| Spearman correlation | monotonic relation between event mass and char error |
| risk curve | error rate by event-mass decile |
| hidden-conflict precision | how often low event mass identifies constrained-legal but posterior-low cases |

## Required Input

```text
experiments/runs/autodl_jmlr_block/p6_r6_diagnostic/r6a_field_diagnostic_formal/diagnostic_cases.csv
```

## Output Target

```text
experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/
```

Suggested files:

```text
diagnostic_ranking_metrics.csv
diagnostic_risk_curve.csv
P6_R6A_DIAGNOSTIC_REANALYSIS.md
```

## Claim Boundary

Allowed after successful reanalysis:

```text
P_theta(L|x) provides a useful ranking/risk signal for audited field-style tasks.
```

Not allowed:

```text
P_theta(L|x) is calibrated.
P_theta(L|x) universally predicts errors.
```

## Decision

```text
DONE locally.
No AutoDL run was required.
```

## Completed Reanalysis

Output files:

```text
experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/diagnostic_ranking_metrics.csv
experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/diagnostic_risk_curve.csv
experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/P6_R6A_DIAGNOSTIC_REANALYSIS.md
```

Key results:

| Metric | Value |
|---|---:|
| cases | 21000 |
| overall AUROC for exact error | 0.7088 |
| overall AUPRC for exact error | 0.8470 |
| Spearman risk vs char error | 0.2869 |
| bottom risk decile exact error | 0.8862 |
| top risk decile exact error | 0.2624 |

Updated claim:

```text
P_theta(L|x) provides a useful ranking/risk signal for the audited field-style tasks.
```

Still not allowed:

```text
P_theta(L|x) is calibrated.
P_theta(L|x) universally predicts errors.
P_theta(L|x) establishes benchmark superiority.
```
