# Paper-Writing Handoff

Updated: 2026-05-30

This document is the main handoff for a supervisor or paper writer. It summarizes what the project is, what story it can safely tell, where the experiments live, and which claims must not be made.

## Project In One Paragraph

This project studies a posterior-level audit object for linear-chain CRFs: the probability mass that the original CRF posterior assigns to a regular-language rule event, written as `P_theta(L|x)=Z_theta,L(x)/Z_theta(x)`. The central claim is not that constrained decoding is bad, and not that this is a new automata inference primitive. The central claim is that decoded output legality and posterior consistency are different objects: a constrained decoder can return a legal sequence while the original posterior still assigns substantial probability mass to illegal sequences.

## Paper Story

The safest paper identity is:

```text
Auditing CRF Posterior Consistency with Regular-Language Event Mass
```

The story should be:

1. A CRF defines a full posterior distribution over label sequences.
2. A regular-language rule defines an event over label sequences.
3. The scalar `P_theta(L|x)` measures how much the original posterior believes the rule.
4. This scalar is different from asking for the best legal decoded path.
5. The scalar can be computed exactly by the standard CRF-DFA product transfer.
6. It supports an event-loss training signal and a rule-specific audit statistic.
7. Experiments support the auditability story, not benchmark superiority.

## Four Objects To Keep Distinct

| Object | Question answered | Typical form | Paper boundary |
|---|---|---|---|
| Unconstrained CRF | What is the original posterior? | `p_theta(y|x)=exp S_theta(x,y)/Z_theta(x)` | Baseline distribution being audited. |
| Constrained decoding / WFST decoding | What is the best legal output? | `argmax_{y in L} S_theta(x,y)` | Produces a legal path; does not report original posterior mass on `L`. |
| Constrained CRF / RegCCRF-style conditional model | What is the posterior after conditioning on legality? | `p_theta(y|x,y in L)=exp S_theta(x,y)/Z_theta,L(x)` | Changes the normalized distribution to the legal subset. |
| This work | How much mass did the original posterior assign to the rule event? | `P_theta(L|x)=Z_theta,L(x)/Z_theta(x)` | Audit scalar for posterior consistency under the original CRF posterior. |

## Supported Claims

| Claim | Current support | Main evidence |
|---|---|---|
| `P_theta(L|x)` is a well-defined finite CRF posterior event object. | Strong. | `docs/manuscript/THEORY_PROOF_PROSE.md`; unit tests. |
| Product transfer computes event mass exactly in the finite setup. | Strong. | `src/tensor_crf_jmlr/posterior_event_algebra/`; proof prose; tests. |
| Decoded legality and posterior consistency differ. | Supported. | R5a diagnostic stress: legal constrained output can coexist with low `P(BIO|x)`. |
| Event training can raise posterior event mass in audited settings. | Supported but narrow. | R5a, R1/R2/R4, public CoNLL2000, and R7 audits; R7 derisk shows this can harm task metrics when the rule is misleading. |
| Event mass is a rule-specific posterior-consistency signal with positive risk-ranking value. | Supported but not dominant. | R6a AUROC/AUPRC and uncertainty-baseline comparison. |
| Product-state scaling is discussable conservatively. | Supported as reference scaling, not optimized runtime superiority. | R8 complexity audit. |

## Forbidden Claims

Do not write the paper as any of the following:

- benchmark-superiority paper;
- NER F1 improvement paper;
- WFST or constrained-decoding replacement paper;
- claim that hard constraints are useless;
- claim that event risk beats generic uncertainty;
- calibration paper;
- tensor-rank or MPO main-contribution paper;
- low-rank advantage paper.
- submission-ready package without final proof/related-work/reproducibility review.

## Experimental Evidence Snapshot

| Block | Role in paper | Safe conclusion |
|---|---|---|
| R5a WNUT17 diagnostic stress | Existence-style diagnostic evidence. | Low `P(BIO|x)` can coexist with legal constrained decoding. Entity F1 is 0, so this is not NER usefulness evidence. |
| R5b WNUT17 feature viability | Public BIO/NER viability boundary. | Nonzero F1 confirms the slice is not purely all-O, but no F1 superiority claim is supported. |
| R1 controlled | Controlled rule/event validation. | Event mass and event-training behavior are coherent in controlled settings. |
| R2 semi-real | Field-like semi-real validation. | Event training can raise rule mass in field-like settings. |
| R4 real-source small | Small real-source auxiliary evidence. | Supports field-style applicability, not broad benchmark claims. |
| R6a diagnostic | Risk/audit analysis. | Event mass has positive rule-specific ranking signal, but generic uncertainty baselines are stronger. |
| R8 complexity | Scaling reference. | Product-state scaling should be described conservatively. |
| B7 constrained-product | Decoding comparison object. | Legal decoding can be reported without using original posterior event mass. |
| Public CoNLL2000 | Public BIO/chunking audit case. | Full local three-seed case study strengthens provenance, but B4 lowers mean token/span metrics while raising event mass. |
| R7 sensitivity | Lambda/rule boundary study. | Includes a wrapped-formal irrelevant-rule derisk run: B4 lambda 1.0 raises `P(event)` by `+0.9485` while char accuracy drops `-0.5524` and exact accuracy drops `-0.0816`. |

## Where Things Are

| Need | Path |
|---|---|
| Project overview | `docs/PROJECT_OVERVIEW.md` |
| External review packet | `docs/external_review/EXTERNAL_REVIEW_PACKET_CURRENT.md` |
| Claim table | `docs/manuscript/FINAL_CLAIM_TABLE.md` |
| Paper positioning | `docs/manuscript/PAPER_POSITIONING.md` |
| JMLR methods outline | `docs/manuscript/JMLR_METHODS_OUTLINE.md` |
| Related work draft | `docs/manuscript/RELATED_WORK_DRAFT.md` |
| Theory proof prose | `docs/manuscript/THEORY_PROOF_PROSE.md` |
| Experiment inventory | `docs/EXPERIMENT_INVENTORY.md` |
| Formal plan | `docs/protocols/EXPERIMENT_PLAN.md` |
| Curated paper tables | `experiments/results/paper_tables/PAPER_TABLES_INDEX.md` |
| Curated result audits | `experiments/results/event_training/formal_pre_paper/` |
| Experiment configs | `experiments/configs/` |
| Experiment suites | `experiments/suites/` |
| Experiment runner | `scripts/exp1/run_event_training_task.py` |
| Suite runner | `scripts/run_experiment_suite.py` |
| Analysis scripts | `scripts/analysis/` |
| Reusable source code | `src/tensor_crf_jmlr/` |

## Recommended Reading Order

1. `docs/HANDOFF_FOR_PAPER_WRITING.md`
2. `docs/external_review/EXTERNAL_REVIEW_PACKET_CURRENT.md`
3. `docs/EXPERIMENT_INVENTORY.md`
4. `docs/manuscript/FINAL_CLAIM_TABLE.md`
5. `docs/manuscript/PAPER_POSITIONING.md`
6. `docs/manuscript/THEORY_PROOF_PROSE.md`
7. `experiments/results/paper_tables/PAPER_TABLES_INDEX.md`

## Remaining Risks For The Writer

The largest JMLR risk is significance: a reviewer may say the computation is standard CRF-DFA marginal inference. The defense is to avoid novelty claims about the dynamic program and emphasize the paper object: original-posterior event mass as a rule-specific audit scalar distinct from decode-time legality and constrained CRF normalization.

The second risk is empirical strength. R6a shows positive signal but generic uncertainty baselines are stronger. The paper should present this as a boundary result: event mass is interpretable and rule-specific, not a universal uncertainty replacement.

The third risk is overclaiming event training. Event loss is a computable training signal, but the current evidence does not justify a general task-accuracy improvement claim.

The CoNLL2000 three-seed full public case is now completed locally:

```bash
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_multiseed.yaml --out-dir experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
python scripts/analysis/curate_jmlr_cpu_upgrade_results.py --public-multiseed-run experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
python scripts/analysis/generate_paper_tables.py
```

Use it as case-study evidence only. The tiny three-seed run remains a wrapped
plumbing smoke and should not be cited as formal evidence.
