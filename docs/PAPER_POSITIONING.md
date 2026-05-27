# Paper Positioning

生成时间：2026-05-27

## 1. Core Identity

这篇论文的主身份不是：

```text
another constrained decoder
another posterior regularization variant
tensor rank / MPO complexity paper
```

主身份应该是：

```text
posterior-level regular-language event semantics for CRFs
```

最短说法：

```text
Hard-constrained decoding can make the final output legal.
It cannot tell whether the model posterior still places large mass on illegal structures.
We define and compute P_theta(L|x), the posterior probability that the model truly assigns to a regular-language rule.
```

中文说法：

```text
hard constraint 只能修最终答案；
P_theta(L|x) 问模型心里有多少概率真的相信这条规则。
```

## 2. Reviewer-Facing Problem Definition

Reviewer 必须在 5 分钟内理解的问题：

```text
Legality of the decoded output is not the same as posterior consistency.
```

例子：

```text
BIO constrained decoding 可以把输出修成合法 BIO。
但原始 CRF 后验可能仍然把大量概率质量放在非法 BIO 序列上。
```

本项目解决的是：

```text
How can we compute, train, and audit the posterior probability that a CRF assigns to a regular-language structural event?
```

## 3. Relationship To Nearby Work

| Nearby Area | What It Usually Answers | What This Project Answers |
|---|---|---|
| constrained decoding / WFST | final decoded output legality | posterior mass assigned to legal structures |
| hard legality repair | how to force a valid output | whether the model internally believes validity |
| rule-feature CRF | add local rule-correlated features | measure explicit global event probability |
| posterior regularization | enforce expectation-style constraints | compute explicit regular-language event probability |
| automata inference | implement rule-constrained paths | expose posterior semantic consistency |

The paper should proactively define this distinction. Do not let reviewers define it as a decoding variant.

## 4. Paper Spine

Main paper spine:

| Part | Role |
|---|---|
| Exact posterior event algebra | define `P_theta(L|x)` and compute it via CRF x DFA product transfer |
| Event training | use `-log P_theta(L|x)` to move posterior mass toward legal structures |
| Hidden conflict diagnostic | show low `P_theta(L|x)` exposes risk even when decoded output is legal |
| Canonical BIO/NER benchmark | demonstrate the problem in a standard structured prediction setting |

Secondary / appendix spine:

| Part | Role |
|---|---|
| conditional MPO/rank membership | optional theoretical extension, not paper identity |
| positive-cone approximation bound | optional approximation theory support |
| retail field slice | auxiliary real-source small-field evidence |

## 5. Required Narrative Discipline

All theory, experiments, baselines, and case studies should answer one of:

1. Can we compute posterior event mass?
2. Can event training increase posterior event mass?
3. Can posterior event mass reveal hidden conflict that final decoding hides?

If a section does not support one of these, move it to appendix or remove it from the main paper route.

## 6. Empirical Priority Revision

Highest priority before P6 formal runs:

```text
Add a canonical BIO/NER structured benchmark slice.
```

Reason:

```text
BIO legality is a natural regular-language constraint.
Constrained decoding can make outputs legal.
The hidden-conflict question is immediately understandable:
does the posterior still assign large mass to illegal BIO sequences?
```

Retail fields remain useful, but only as auxiliary evidence:

```text
retail_fields_v1 = real-source small-field auxiliary block
BIO/NER = canonical reviewer-facing structured prediction block
```

## 7. Success Criteria

Strong result:

```text
After constrained decoding, outputs are legal, but baseline posterior illegal mass remains high.
Event training raises P_theta(BIO-legal|x), reduces hidden conflict, and preserves or improves task metrics.
Low P_theta(BIO-legal|x) predicts structured errors.
```

Acceptable result:

```text
B4 is not dominant on accuracy, but P_theta(L|x) is a stable audit/diagnostic signal that hard decoding and rule features do not expose.
```

Downgrade route:

```text
If B5/B6 dominate accuracy, position contribution as posterior-event semantics and hidden-conflict auditing rather than empirical superiority.
```

## 8. Main-Theory Boundary

Main text should emphasize:

```text
definition -> exact product transfer -> event loss -> diagnostic
```

MPO/rank membership should be appendix-only unless it becomes directly necessary for the empirical story.

Do not let rank theory become the reviewer’s main attack surface.
