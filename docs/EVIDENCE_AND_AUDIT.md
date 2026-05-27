# Evidence And Audit

生成时间：2026-05-26

本文档合并当前 evidence table、claim-evidence matrix、baseline fairness、diagnostic、code/result audit 和 gate 状态。它不是最终论文结论。

## 1. Test Status

```text
python -m pytest src/tensor_crf_jmlr/posterior_event_algebra -q
29 passed, 14 subtests passed

python -m unittest discover -s src/tensor_crf_jmlr/event_training/tests -v
15 tests OK
```

支持：

- formula / indexing / product transfer / MPO sanity；
- event probability boundary；
- finite gradients；
- formal validation helpers；
- semi-real smoke。

不支持：

- full training system；
- benchmark；
- speed/memory superiority；
- JMLR-ready。

## 2. Claim-Evidence Matrix

| Claim | Status | Evidence | Gap |
|---|---|---|---|
| `Z_{theta,L}(x)` / `P_theta(L|x)` 是 posterior event 对象 | supported | theorem package, theory tests | final proof prose |
| product automaton transfer 精确计算 event mass | supported | T1, product transfer tests | fresh proof audit |
| 条件非负 MPO rank membership | appendix-only / conditional | T2, MPO sanity | no arbitrary low-rank claim; not paper identity |
| positive-cone event-mass error | supported | T3 | posterior/log needs extra assumptions |
| `P_theta(L|x)` 可作为训练信号 | locally supported | gradient, controlled, semi-real, real-source | larger formal evidence |
| weak/semi-supervised format signal | partial | semi-real/real-source B4 positive | stronger BIO/NER public slice |
| hard constraint 与 posterior training 不同 | supported | constrained metrics, conflict cases | explicit B1/B3 rows preferred |
| risk diagnostic | partial positive | bottom/top diagnostic | expand all tasks/baselines |
| B4 empirically superior | not supported | B5/B6 competitive | stronger baseline block |
| JMLR-ready empirical package | not yet | local evidence only | AutoDL/formal block |

## 3. Evidence Summary

| Evidence | Key Positive | Key Boundary |
|---|---|---|
| Core algebra tests | `posterior_event_algebra` all green; finite posterior algebra and product transfer align | small finite sanity only |
| Event CRF smoke tests | 15 tests OK | not a benchmark |
| Gradient mechanism | zero-potential `P_theta(L|x)=0.244800`; illegal BIO gradients positive | not training evidence alone |
| Synthetic robustness | lambda 2.0 raises event mass across 30-seed paired toy configs | high lambda can hurt token accuracy |
| Controlled format | B4 0.1 raises `P_theta(L|x)` on DATE/DDDLL/LL-DDD/LLDDD | 10 seeds only, B5/B6 absent |
| Semi-real fields | amount/date/dose/product_code all positive in posterior mass | B5/B6 competitive |
| Real-source small fields | invoice/stock fields positive in posterior mass and some task metrics | local small-field, not public benchmark |
| Diagnostic | bottom 20% `P_theta(L|x)` samples have higher error than top 20% | representative tasks only |

## 4. Important Numbers

Semi-real main, B4 semi-event 0.1:

| Task | Delta `P_theta(L|x)` | Interpretation |
|---|---:|---|
| amount | +0.1422 | positive structure signal |
| date | +0.1953 | positive structure signal |
| dose | +0.0608 | smaller but positive |
| product_code | +0.1642 | positive, but B5/B6 competitive |

Real-source small-field main, B4 semi-event 0.1:

| Task | Delta `P_theta(L|x)` | Extra |
|---|---:|---|
| invoice_6d | +0.0573 | exact +0.0700 |
| invoice_c6d | +0.0661 | exact +0.0933 |
| stock_5d | +0.0543 | exact +0.0580 |

Diagnostic bottom/top:

| Task | Bottom B0 Error | Top B0 Error |
|---|---:|---:|
| invoice_6d | 0.9167 | 0.3611 |
| stock_5d | 0.9056 | 0.2389 |
| amount | 0.9833 | 0.4500 |
| product_code | 0.9889 | 0.7389 |

Interpretation:

```text
low P_theta(L|x) is a local risk signal.
```

## 5. Baseline Fairness

Overall verdict:

```text
WARN / PASS-with-scope
claim_upgrade_allowed = partial only
JMLR_empirical_strength = not yet sufficient
```

Current baseline coverage:

| Block | Coverage | Verdict |
|---|---|---|
| controlled | B0/B2/B4 plus constrained metrics | WARN |
| semi-real | B0/B2/B4/B5/B6 | PASS-with-scope |
| real-source small-field | B0/B2/B4/B5/B6 | PASS-with-scope |
| diagnostic | B0/B4 representative tasks | PASS-with-scope |

B5/B6 pressure:

```text
semi-real amount: B6 exact +0.0753 vs B4 +0.0733
semi-real dose: B6 exact +0.0420 vs B4 +0.0340
semi-real product_code: B6 exact +0.0393 vs B4 +0.0387
real-source invoice_6d: B6 exact +0.0807 vs B4 +0.0700
real-source stock_5d: B5 exact +0.0747 vs B4 +0.0580
```

Conclusion:

```text
B4 is competitive and theoretically/auditably distinctive,
but not empirically dominant under current local baselines.
```

## 6. Current Supported Claims

Current evidence can support:

1. `P_theta(L|x)` is a well-defined, computable CRF posterior event object.
2. Product automaton transfer aligns with brute-force on finite sanity cases.
3. `-log P_theta(L|x)` has local gradient mechanisms that penalize illegal structure.
4. Controlled non-saturated format tasks show posterior event mass can be trained upward.
5. Semi-real and real-source small-field probes provide partial positive evidence.
6. Hard constraint and posterior event training answer different questions.
7. Low posterior event mass is a local risk/hidden-conflict signal.

## 7. Unsupported Claims

Current evidence does not support:

- benchmark superiority;
- JMLR-ready empirical claim;
- full real-task usefulness;
- comprehensive superiority over hard constraint / WFST / posterior regularization / rule-feature;
- arbitrary CRF / DFA / regular language low-rank advantage;
- best lambda;
- full diagnostic AUC / calibration claim;
- production readiness.

## 8. Remaining Gaps

| Gap | Why It Matters | Minimal Fix |
|---|---|---|
| fresh proof-check | theory prose before paper must be externally/freshly audited | run proof-check before drafting |
| explicit B1/B3 rows | constrained metrics are currently implicit | add rows or preserve clear flags |
| B5/B6 grids | B5/B6 pressure decides empirical strength | freeze and run grids |
| canonical BIO/NER public slice | missing reviewer-facing structured benchmark | add and freeze before P6 formal runs |
| retail field slice | current slice is frozen but still small-field | keep as auxiliary evidence |
| diagnostic full coverage | current diagnostic is representative | expand all tasks/baselines |
| AutoDL formal block | JMLR needs scale and seeds | run only after smoke gate |

## 9. Gate

```text
GO: continue pre-paper formal validation planning.
GO: P3 protocol/run list revised around posterior event semantics.
GO: P4 local CPU smoke passed.
GO: P5 AutoDL/HPC smoke engineering may proceed.
GO: revise P6 around canonical BIO/NER hidden-conflict benchmark before formal runs.
HOLD: paper-writing.
HOLD: benchmark superiority.
HOLD: JMLR-ready claim.
HOLD: P6 formal AutoDL runs until P5 target-machine smoke passes.
HOLD: treating retail_fields_v1 as the primary public benchmark.
```
