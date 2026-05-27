# Route Review Checklist

生成时间：2026-05-27

用途：在进入 P6 formal runs 前重新审核路线，避免项目重新扩张或 claim 过强。

## 1. Paper Identity Check

| Question | Required Answer Before P6 |
|---|---|
| 论文主问题是否能一句话说清？ | `decoded output legality != posterior consistency` |
| 主贡献是否围绕 `P_theta(L|x)`？ | yes |
| 是否避免把 rank/MPO 当主贡献？ | yes, appendix only |
| 是否主动区分 constrained decoding / posterior regularization / rule features？ | yes |

## 2. Canonical Benchmark Check

| Question | Required Answer Before P6 |
|---|---|
| 是否冻结 BIO/NER public dataset？ | yes: WNUT17 Emerging Entities |
| 是否冻结 BIO/BIOES legality DFA？ | yes: strict BIO legality |
| 是否能展示 hidden posterior conflict？ | required |
| 是否报告 constrained decoded legality 与 posterior legal mass 的差异？ | required |
| retail_fields_v1 是否只作为辅助证据？ | yes |

## 3. Baseline Check

| Baseline | Required Before P6 |
|---|---|
| B0 unconstrained CRF | yes |
| B1 hard-constrained decoding | yes |
| B2 labeled event training | yes |
| B3 event training + hard constraint | yes |
| B4 semi-event training | yes |
| B5 rule-feature CRF | yes |
| B6 posterior-regularization-style | yes |
| B7 WFST-style | design-if-feasible; justify if omitted |

## 4. Complexity Check

Reviewer will ask about:

| Topic | Required Story |
|---|---|
| CRF x DFA product state size | explicit complexity in sequence length, labels, context, DFA states |
| memory scaling | reported or bounded |
| rule complexity scaling | vary DFA states / rule patterns |
| batching behavior | document whether implementation is CPU-first / small-scale |

## 5. Claim Gate

| Result Pattern | Paper Position |
|---|---|
| B4 improves event mass and diagnostic, not always accuracy | posterior event semantics + auditability |
| B4 beats B5/B6 on many tasks | cautiously claim training advantage |
| B5/B6 dominate accuracy | drop superiority, keep audit/diagnostic contribution |
| BIO/NER hidden conflict absent | downgrade JMLR empirical route |
| diagnostic weak | remove diagnostic claim |

## 6. Go / Hold

GO to P6 only if:

- P5 target-machine smoke passes;
- BIO/NER slice is frozen and local data audit passes;
- B0-B6 are implementable for BIO/NER;
- hidden-conflict metric is defined;
- complexity story is written;
- output schema and audit scripts are ready.

HOLD P6 if:

- WNUT17 BIO/NER implementation or smoke is not ready;
- retail_fields_v1 is still the only public-looking slice;
- baseline definitions are still moving;
- rank/MPO starts dominating main narrative;
- result-to-claim mapping is unclear.

Current BIO/NER data gate:

```text
WNUT17 data source, split, local files, manifest hashes, and strict BIO audit are frozen.
R5 implementation and hidden-conflict dev smoke are still pending.
```
