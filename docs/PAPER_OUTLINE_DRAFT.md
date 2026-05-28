# Paper Outline Draft

Generated: 2026-05-28

Working title:

```text
Tensorized Regular-Language Posterior Algebra for Conditional Random Fields
```

Short identity:

```text
Decoded output legality is not posterior consistency.
```

## Abstract Shape

Structured prediction systems often use hard constraints to ensure that decoded outputs satisfy known rules. This repairs the final prediction but does not reveal how much posterior probability the model assigns to rule-consistent structures. We define `P_theta(L|x)`, the posterior mass that a CRF assigns to a regular-language event `L`, and compute it exactly using a product construction between the CRF state and a DFA monitor. This object supports three uses: auditing hidden posterior conflict, training with an event loss, and diagnosing high-risk examples. Experiments on BIO/NER, controlled format tasks, semi-real fields, and real-source small fields show that posterior event mass can expose inconsistency hidden by constrained decoding and can be moved by semi-event training. The strongest claim is posterior-event semantics and auditability, not benchmark superiority.

## 1. Introduction

Core problem:

```text
Hard-constrained decoding can make an output legal, but it cannot say whether the model posterior believes the rule.
```

Example narrative:

- BIO constrained decoding produces legal BIO tags.
- Baseline CRF posterior still assigns most mass to illegal BIO sequences.
- `P_theta(BIO-legal|x)` exposes that hidden conflict.

Contribution list:

1. Define CRF posterior regular-language event mass `P_theta(L|x)`.
2. Give an exact CRF x DFA product transfer computation.
3. Use event mass as a training signal via `-log P_theta(L|x)`.
4. Use low event mass as an audit/diagnostic signal.
5. Provide formal pre-paper evidence across WNUT17 BIO/NER, controlled formats, semi-real fields, real-source small fields, diagnostics, and scaling.

Explicit non-claim:

```text
We do not claim benchmark superiority or that hard constraints are useless.
```

## 2. Related Work Positioning

Required distinctions:

| Area | Their Main Object | Our Main Object |
|---|---|---|
| constrained decoding / WFST | legal decoded output | posterior mass of legal event |
| rule-feature CRF | local rule-correlated features | explicit global event probability |
| posterior regularization | expectation-style constraints | regular-language event probability |
| uMPS / tensor events | generative regular-language events | conditional CRF posterior events |

Main sentence:

```text
This paper is about posterior-level semantics, not another decoding algorithm.
```

## 3. Posterior Event Algebra

Definitions:

- finite label set `Y`;
- fixed sequence length `T`;
- CRF score `S_theta(x,y)`;
- regular language `L`;
- complete DFA `A_L`;
- event mass `Z_{theta,L}(x)`;
- event probability `P_theta(L|x)`.

Main theorem:

```text
The CRF x DFA product transfer computes Z_{theta,L}(x) exactly.
```

Proof idea:

- each label sequence defines one product path;
- each nonzero product path defines one label sequence;
- path weight equals CRF sequence weight;
- accepting DFA states select exactly `L cap Y^T`.

Appendix-only:

- conditional MPO/rank membership;
- positive-cone approximation bounds.

## 4. Event Training And Diagnostics

Training signal:

```text
loss = supervised CRF NLL + lambda * [-log P_theta(L|x)]
```

Semi-event setting:

- labeled data uses NLL plus optional event term;
- unlabeled inputs can use event term only;
- claim is posterior mass movement, not universal accuracy improvement.

Diagnostic signal:

```text
low P_theta(L|x) = high risk / possible hidden conflict
```

## 5. Experimental Design

Blocks:

| Block | Role |
|---|---|
| R5 WNUT17 BIO/NER | canonical hidden posterior conflict and task viability |
| R1 controlled | mechanism stability across controlled regular formats |
| R2 semi-real | field-like structured tasks |
| R4 real-source small | auxiliary real-source field evidence |
| R6a diagnostic | bottom/top event-mass risk signal |
| R8 complexity | product-transfer scaling sanity |

Baselines:

- B0 unconstrained CRF;
- B1 hard-constrained decoding;
- B2 labeled event training;
- B3 event + hard decoding;
- B4 semi-event training;
- B5 rule-feature CRF;
- B6 posterior-regularization-style baseline;
- B7 design-only unless superiority against constrained methods is claimed.

## 6. Results

### R5 WNUT17

Main result:

```text
R5a: B0 P(BIO|x)=0.0566 while constrained legality is 1.
B4 raises P(BIO|x) to 0.3389.
```

Boundary:

```text
R5a has entity F1 = 0, so it is diagnostic only.
R5b has nonzero B0 entity F1, but B4 does not improve NER F1.
```

### R1/R2/R4 Training Signal

Main result:

```text
B4 raises posterior event mass across controlled, semi-real, and real-source field tasks.
```

Boundary:

```text
Task accuracy is not uniformly dominant; B5/B6 are competitive.
```

### R6a Diagnostic

Main result:

```text
bottom event-mass quantile has higher exact and char error than top quantile on every audited field-style task.
```

Boundary:

```text
Diagnostic evidence is not task-improvement evidence.
```

### R8 Complexity

Main result:

```text
Reference CPU product-transfer runtime scales with sequence length, label count, DFA states, and product-state count.
```

Boundary:

```text
No optimized speed, GPU, or low-rank superiority claim.
```

## 7. Discussion

Defensible paper thesis:

```text
Posterior event mass is a useful semantic object for structured prediction: it can be computed, trained, and audited.
```

Downgrade route:

```text
If reviewers reject empirical strength, the paper remains a posterior-event algebra and diagnostic/auditability contribution.
```

## 8. Limitations

- no benchmark superiority;
- WNUT hidden-conflict stress is diagnostic, not useful NER performance;
- B7 is not implemented as a faithful WFST baseline;
- reference implementation is CPU-first and not optimized;
- rank/MPO result is conditional appendix support only;
- final theorem prose still needs external proof review.

## 9. Appendix Plan

- full theorem proofs;
- conditional MPO/rank membership;
- positive-cone approximation bound;
- full run configs and audit tables;
- additional case studies;
- repository/reproducibility details.
