# Experiment Inventory

Updated: 2026-05-29

This inventory maps each retained experiment block to its purpose, config, runner, curated result, and paper claim boundary. It is intended for the paper writer.

## Execution Pattern

All formal blocks use the same pattern:

```powershell
python scripts/run_experiment_suite.py --suite <suite.yaml> --dry-run
python scripts/run_experiment_suite.py --suite <suite.yaml>
```

Single tasks can be run through:

```powershell
python scripts/exp1/run_event_training_task.py --config <config.yaml> --out-dir experiments/runs/<run_name>
```

Raw run bundles belong under `experiments/runs/` and are ignored by Git. Curated paper-facing results belong under `experiments/results/`.

## Formal Blocks

| Block | Purpose | Configs | Suite | Main runner | Curated result / analysis | Safe claim |
|---|---|---|---|---|---|---|
| R5a WNUT17 diagnostic stress | Test hidden BIO posterior conflict under diagnostic stress. | `experiments/configs/exp5/wnut17_r5a_diagnostic_formal.yaml` | `experiments/suites/r5_wnut17_formal_plan.yaml` | `scripts/exp1/run_event_training_task.py` | `experiments/results/event_training/formal_pre_paper/r5_wnut17/R5_RESULT_TO_CLAIM_AUDIT.md` | Existence-style hidden conflict diagnostic. Not NER usefulness. |
| R5b WNUT17 feature viability | Check nonzero-F1 BIO/NER slice and event-mass behavior. | `experiments/configs/exp5/wnut17_r5b_feature_formal.yaml` | `experiments/suites/r5_wnut17_formal_plan.yaml` | `scripts/exp1/run_event_training_task.py` | `experiments/results/event_training/formal_pre_paper/r5_wnut17/R5_RESULT_TO_CLAIM_AUDIT.md` | Public-slice viability; no F1 superiority. |
| R1 controlled | Controlled format validation. | `experiments/configs/exp1/r1_controlled_formal.yaml` | `experiments/suites/p6_r1_r2_r4_formal_plan.yaml` | `scripts/exp1/run_event_training_task.py` | `experiments/results/event_training/formal_pre_paper/p6_r1_r2_r4/P6_R1_R2_R4_RESULT_TO_CLAIM_AUDIT.md` | Controlled evidence for event-mass and event-training behavior. |
| R2 semi-real | Field-like semi-real rule/event validation. | `experiments/configs/exp2/r2_semi_real_formal.yaml` | `experiments/suites/p6_r1_r2_r4_formal_plan.yaml` | `scripts/exp1/run_event_training_task.py` | `experiments/results/event_training/formal_pre_paper/p6_r1_r2_r4/P6_R1_R2_R4_RESULT_TO_CLAIM_AUDIT.md` | Field-like support; not benchmark superiority. |
| R4 real-source small | Small real-source auxiliary validation. | `experiments/configs/exp3/r4_real_source_formal.yaml` | `experiments/suites/p6_r1_r2_r4_formal_plan.yaml` | `scripts/exp1/run_event_training_task.py` | `experiments/results/event_training/formal_pre_paper/p6_r1_r2_r4/P6_R1_R2_R4_RESULT_TO_CLAIM_AUDIT.md` | Small real-source applicability boundary. |
| R6a field diagnostic | Evaluate event mass as risk/audit statistic. | `experiments/configs/exp6/r6a_field_diagnostic_formal.yaml` | `experiments/suites/p6_r6_diagnostic_formal_plan.yaml` | `scripts/exp1/run_event_training_task.py` | `experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/` | Positive rule-specific signal; generic uncertainty baselines are stronger. |
| R8 complexity scaling | Measure reference product-transfer scaling. | `experiments/configs/exp8/r8_complexity_scaling_formal.yaml` | `experiments/suites/p6_r8_complexity_formal_plan.yaml` | `scripts/exp1/run_event_training_task.py` | `experiments/results/event_training/formal_pre_paper/p6_r8_complexity/P6_R8_COMPLEXITY_RESULT_TO_CLAIM_AUDIT.md` | Conservative complexity discussion only. |

## Analysis And Table Scripts

| Script | Purpose | Output |
|---|---|---|
| `scripts/analysis/audit_r5_wnut17_results.py` | Audit R5 run bundles into claim table rows. | `experiments/results/event_training/formal_pre_paper/r5_wnut17/` |
| `scripts/analysis/audit_p6_r1_r2_r4_results.py` | Audit R1/R2/R4 run bundles. | `experiments/results/event_training/formal_pre_paper/p6_r1_r2_r4/` |
| `scripts/analysis/audit_p6_r6_diagnostic_results.py` | Audit R6a run bundle. | `experiments/results/event_training/formal_pre_paper/p6_r6_diagnostic/` |
| `scripts/analysis/reanalyze_p6_r6_diagnostic.py` | Compute diagnostic ranking metrics and risk curves. | `diagnostic_ranking_metrics.csv`, `diagnostic_risk_curve.csv` |
| `scripts/analysis/reanalyze_r6a_uncertainty_baselines.py` | Compare event risk against entropy, margin, max-probability baselines. | `R6A_UNCERTAINTY_BASELINE_REANALYSIS.md` |
| `scripts/analysis/audit_p6_r8_complexity_results.py` | Audit R8 complexity output. | `experiments/results/event_training/formal_pre_paper/p6_r8_complexity/` |
| `scripts/analysis/generate_paper_tables.py` | Generate paper-facing table bundle from curated results. | `experiments/results/paper_tables/` |

## Paper Tables

The paper-facing table bundle is:

```text
experiments/results/paper_tables/
```

Start with:

```text
experiments/results/paper_tables/PAPER_TABLES_INDEX.md
```

This table bundle is the safest entrypoint for writing the empirical section because it is already curated around claim boundaries.

## Raw Runs Policy

Raw machine outputs are useful for provenance but should not be treated as the paper-facing source of truth. They should stay local or be regenerated from configs. The repo keeps:

- configs under `experiments/configs/`;
- suites under `experiments/suites/`;
- curated audits under `experiments/results/`;
- raw run outputs ignored under `experiments/runs/`.
