# JMLR Main Upgrade Plan

Updated: 2026-05-30

This plan turns the current draftable Tensor-CRF posterior-event project into a more defensible JMLR main-track package. It is not a submission-readiness claim.

## Current Audit

| Question | Status | Evidence / Files |
|---|---|---|
| B1/B3 hard-constrained decoding baseline exists? | yes | `src/tensor_crf_jmlr/event_training/wnut17_bio_probe.py`, `formal_validation_runner.py`, `semi_real_format_probe.py` report constrained decoding metrics |
| WFST-style / constrained structured baseline code exists? | partial | design note only before this plan; implement as constrained-product decoding baseline, not a full WFST system |
| Reusable DFA/rule infrastructure exists? | yes | `bio_event.py`, product-transfer DFA utilities, pattern-mask utilities in controlled/semi-real runners |
| Public BIO / sequence-labeling dataset configs exist? | yes; formal run passed | WNUT17 configs/data are present; CoNLL2000 chunking formal audit is in `experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_FORMAL_AUDIT.md` |
| Uncertainty baseline computation pipeline exists? | yes | `posterior_event_diagnostic.py` writes entropy/margin/probability fields; `reanalyze_r6a_uncertainty_baselines.py` writes ranking tables |
| Lambda/rule sensitivity configs exist? | yes; formal run passed | `experiments/results/event_training/formal_pre_paper/r7_sensitivity/R7_SENSITIVITY_FORMAL_AUDIT.md` |

## Mandatory Before JMLR Submission

| Item | Exact files/configs/scripts to create or update | Expected tables/figures | Acceptance criteria | Risk if omitted |
|---|---|---|---|---|
| Faithful constrained baseline B7 | completed: `src/tensor_crf_jmlr/event_training/constrained_product_baseline.py`; `experiments/configs/exp7/b7_*`; `experiments/results/event_training/formal_pre_paper/b7_constrained_product/` | B7 row with task metric, legal rate, constrained score, and clear notes | Uses same `L`/rule as event mass, returns legal decoded sequence, reports task metrics/legal rate, does not claim superiority | If omitted from manuscript, reviewer may think the constrained-decoding boundary is only asserted |
| Stronger public structured-prediction case or explicit scoped fallback | completed: CoNLL2000 chunking downloader/protocol/configs/runner and formal audit | Public-case table: `P(L|x)`, constrained legality, task metric, hidden conflict, B4 event movement, B7 behavior, uncertainty fields | Formal CPU run passed at commit `a10517d`; no fabricated result; claims remain case-study scoped | Without careful wording, one public case could be overread as benchmark superiority |
| Sensitivity evidence | completed: `src/tensor_crf_jmlr/event_training/sensitivity_probe.py`; `experiments/configs/exp7/r7_*`; `experiments/results/event_training/formal_pre_paper/r7_sensitivity/` | Lambda/rule difficulty table and event-mass/task-metric boundary table | Includes multiple lambda values, multiple rules/difficulty levels, the `stock_like_digits` legal-rate-not-useful boundary, and a wrapped-formal `product_code_swapped_rule` event/task tradeoff boundary with complete run metadata | Event-loss claim appears cherry-picked if the boundary rows are not shown |
| Claim-table and paper-outline discipline | `FINAL_CLAIM_TABLE.md`, `JMLR_METHODS_OUTLINE.md`, `PAPER_POSITIONING.md` | Claim-to-evidence table | Product inference is explicitly known; C1/C2 are formal foundation; C7 appendix/sanity | Reviewer rejects novelty framing |
| Theory assumption audit | `THEORY_PROOF_PROSE.md`, `THEORY_AUDIT.md` | Theorem assumptions box | finite `Y,T`, complete DFA, finite-context/local factorization; arbitrary finite scores only via huge context/table | The theorem appears over-general |

## Strongly Recommended

| Item | Files/scripts | Expected output | Acceptance criteria | Risk if omitted |
|---|---|---|---|---|
| Paper-ready R6a uncertainty boundary | `R6A_UNCERTAINTY_BASELINE_REANALYSIS.md`; `r6a_uncertainty_baseline_metrics.csv`; `r6a_uncertainty_complementarity.csv` | Table with event risk and generic uncertainty baselines | AUROC, AUPRC, Spearman char error, top/bottom quantile risk, correlations, within-bin residual checks | Event risk may be oversold as uncertainty replacement |
| Public-case uncertainty boundary | completed for CoNLL2000 in `conll2000_public_uncertainty_metrics.csv` and related correlation/complementarity CSVs | Table comparing event risk with entropy/margin/max-probability uncertainty | Shows event risk has positive signal but generic uncertainty is stronger in this public case | Event risk may be oversold as uncertainty replacement |
| CoNLL2000 three-seed public run | `experiments/configs/exp7/public_conll2000_chunking_multiseed.yaml`; `experiments/suites/public_sequence_labeling_plan.yaml`; curation hook `scripts/analysis/curate_jmlr_cpu_upgrade_results.py --public-multiseed-run ...` | Mean/std public-case table for `P(BIO|x)`, hidden conflict, B7 legal rate, token accuracy, span F1; uncertainty fields are emitted per case for follow-up analysis | Completed locally: `experiments/runs/local_checks/public_conll2000_chunking_multiseed_full`, commit `002ecbb`, returncode `0`, duration `3076.544701`; tiny three-seed smoke remains plumbing only | Public case remains a case study and shows task-metric boundary behavior; not benchmark superiority |
| Result audit templates for new B7/public/sensitivity runs | completed in `experiments/results/event_training/formal_pre_paper/{public_sequence_labeling,b7_constrained_product,r7_sensitivity}/` | Explicit completed states | Every result row has provenance and claim boundary | Hard to distinguish smoke from evidence |
| Public data provenance | `data/DATA_MANIFEST.md`; `scripts/data/fetch_conll2000_chunking.py`; protocol doc | Source, local path, hashes, official-host failure note, mirror fallback | Local hashes recorded; redistribution/citation review still needed before tracking data | Data reproducibility objection |

## Optional / Appendix

| Item | Files/scripts | Expected output | Acceptance criteria | Risk if omitted |
|---|---|---|---|---|
| Full WFST-library implementation | separate appendix script only if cleanly integrated | comparison note | Must not be a strawman; otherwise omit | Over-engineering or misleading baseline |
| Conditional MPO/rank appendix polish | `THEORY_PROOF_PROSE.md` appendix | appendix proposition only | explicit mode order and assumptions | Tensor identity may distract from main contribution |
| Additional WNUT17 seeds/tuning | existing R5 configs | appendix robustness table | Does not claim B4 F1 gain unless proven | WNUT remains weak main evidence |

## Full-Run Commands To Freeze Later

```powershell
python scripts/run_experiment_suite.py --suite experiments/suites/r5_wnut17_formal_plan.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/p6_r1_r2_r4_formal_plan.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/p6_r6_diagnostic_formal_plan.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/p6_r8_complexity_formal_plan.yaml --dry-run
```

New suites should add:

```powershell
python scripts/run_experiment_suite.py --suite experiments/suites/b7_constrained_product_plan.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/public_sequence_labeling_plan.yaml --dry-run
python scripts/run_experiment_suite.py --suite experiments/suites/r7_sensitivity_plan.yaml --dry-run
```

Completed public multiseed full run provenance:

```bash
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_multiseed.yaml --out-dir experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
python scripts/analysis/curate_jmlr_cpu_upgrade_results.py --public-multiseed-run experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
python scripts/analysis/generate_paper_tables.py
```

## Readiness Gate

```text
JMLR main manuscript drafting can proceed with caveats: B7, public CoNLL2000, and R7 sensitivity formal runs are audited, and the R7 derisk run now gives a wrapped-formal event/task tradeoff boundary.
JMLR submission-ready: no. Submission still requires final proof review, final related-work citations, final table/figure integration, and reproducibility packaging.
```
