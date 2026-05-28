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
Do this locally before paper writing if diagnostic becomes a main contribution.
No AutoDL run is required.
```
