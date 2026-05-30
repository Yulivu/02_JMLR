# JMLR Main Upgrade Plan

Updated: 2026-05-30

This plan turns the current draftable Tensor-CRF posterior-event project into a more defensible JMLR main-track package. It is not a submission-readiness claim.

## Current Audit

| Question | Status | Evidence / Files |
|---|---|---|
| B1/B3 hard-constrained decoding baseline exists? | yes | `src/tensor_crf_jmlr/event_training/wnut17_bio_probe.py`, `formal_validation_runner.py`, `semi_real_format_probe.py` report constrained decoding metrics |
| WFST-style / constrained structured baseline code exists? | partial | design note only before this plan; implement as constrained-product decoding baseline, not a full WFST system |
| Reusable DFA/rule infrastructure exists? | yes | `bio_event.py`, product-transfer DFA utilities, pattern-mask utilities in controlled/semi-real runners |
| Public BIO / sequence-labeling dataset configs exist? | local smoke passed; full pending | WNUT17 configs/data are present; CoNLL2000 chunking public smoke is audited in `experiments/results/event_training/formal_pre_paper/public_sequence_labeling/` |
| Uncertainty baseline computation pipeline exists? | yes | `posterior_event_diagnostic.py` writes entropy/margin/probability fields; `reanalyze_r6a_uncertainty_baselines.py` writes ranking tables |
| Lambda/rule sensitivity configs exist? | partial | semi-real and real-source runners contain lambda sweeps; no JMLR-facing sensitivity protocol/table yet |

## Mandatory Before JMLR Submission

| Item | Exact files/configs/scripts to create or update | Expected tables/figures | Acceptance criteria | Risk if omitted |
|---|---|---|---|---|
| Faithful constrained baseline B7 | `src/tensor_crf_jmlr/event_training/constrained_product_baseline.py`; `experiments/configs/exp7/b7_*`; `docs/protocols/B7_WFST_DESIGN_NOTE.md`; tests | B7 row with task metric, legal rate, constrained score, and clear notes | Uses same `L`/rule as event mass, returns legal decoded sequence, reports task metrics/legal rate, does not claim superiority | Reviewer says the constrained-decoding boundary is only asserted, not tested |
| Stronger public structured-prediction case or explicit scoped fallback | CoNLL2000 chunking downloader/protocol/configs/runner are present; full run still pending | Public-case table: `P(L|x)`, constrained legality, task metric, hidden conflict, B4 event movement, B7 behavior, uncertainty if available | Local smoke passed with audited provenance; full run command is exact; no fabricated result | WNUT17 remains too weak: R5a F1 is zero and R5b event mass saturates |
| Sensitivity evidence | `src/tensor_crf_jmlr/event_training/sensitivity_probe.py` or runner configs reusing R2/R4; `experiments/configs/exp7/r7_*` | Lambda/rule difficulty table and event-mass/task-metric tradeoff plot/table | Includes multiple lambda values, multiple rules/difficulty levels, and at least one saturated or unhelpful boundary case | Event-loss claim appears cherry-picked |
| Claim-table and paper-outline discipline | `FINAL_CLAIM_TABLE.md`, `JMLR_METHODS_OUTLINE.md`, `PAPER_POSITIONING.md` | Claim-to-evidence table | Product inference is explicitly known; C1/C2 are formal foundation; C7 appendix/sanity | Reviewer rejects novelty framing |
| Theory assumption audit | `THEORY_PROOF_PROSE.md`, `THEORY_AUDIT.md` | Theorem assumptions box | finite `Y,T`, complete DFA, finite-context/local factorization; arbitrary finite scores only via huge context/table | The theorem appears over-general |

## Strongly Recommended

| Item | Files/scripts | Expected output | Acceptance criteria | Risk if omitted |
|---|---|---|---|---|
| Paper-ready R6a uncertainty boundary | `R6A_UNCERTAINTY_BASELINE_REANALYSIS.md`; `r6a_uncertainty_baseline_metrics.csv`; `r6a_uncertainty_complementarity.csv` | Table with event risk and generic uncertainty baselines | AUROC, AUPRC, Spearman char error, top/bottom quantile risk, correlations, within-bin residual checks | Event risk may be oversold as uncertainty replacement |
| Correlation table for event risk vs uncertainty | update `reanalyze_r6a_uncertainty_baselines.py` | Correlation CSV/Markdown | Spearman/Pearson event-risk correlation with entropy/margin/max-probability scores | Boundary against generic uncertainty is incomplete |
| Result audit templates for new B7/public/sensitivity runs | `docs/templates/` or protocol docs; result README in `experiments/results/...` | Explicit pending/completed states | Every result row has provenance and claim boundary | Hard to distinguish smoke from evidence |
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

## Readiness Gate

```text
JMLR main draft-ready: closer, because B7 smoke + public-case smoke + R7 sensitivity smoke are present and claim docs remain conservative. Still treat as draft-ready-with-caveats until full-run decisions are made.
JMLR submission-ready: no. Submission requires full audited runs or explicit reviewer-facing downgrades, final proof review, final related-work citations, and reproducibility packaging.
```
