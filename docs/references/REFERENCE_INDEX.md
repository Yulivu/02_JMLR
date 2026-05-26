# Reference Index

生成时间：2026-05-26

本目录只放参考论文、展示备份和阅读笔记，不作为当前执行入口。当前主线入口仍是：

```text
docs/PROJECT_OVERVIEW.md
docs/THEORY_AND_GUARDRAILS.md
docs/EVIDENCE_AND_AUDIT.md
docs/EXPERIMENT_PLAN.md
```

## Papers

| File | Paper | Why Here |
|---|---|---|
| `papers/2018_Han_PRX_Unsupervised_Generative_Modeling_Using_Matrix_Product_States.pdf` | Han et al., *Unsupervised Generative Modeling Using Matrix Product States*, Phys. Rev. X 2018 | tensor-network generative modeling background; copied from `C:\Users\debuf\Desktop\02\PhysRevX.8.031012.pdf` |

## Reading Notes

| File / Folder | Content |
|---|---|
| `reading_notes/2021_uMPS_AISTATS_detailed_reading_CN.md` | uMPS AISTATS 2021 detailed Chinese reading note |
| `reading_notes/rankseg/` | RankSEG reading notes kept as theory-writing reference material |

## Presentation

Current project HTML presentation:

```text
docs/presentation/project_value_presentation_cn.html
```

Previous HTML source copy:

```text
docs/presentation/project_value_presentation_previous_source_cn.html
```

This presentation is for explaining project value to non-specialists. It is not a formal paper and should be synced after major evidence/gate changes.

## Relation To Current Project

uMPS gives the conceptual bridge:

```text
regular language as a probabilistic event
```

This project applies that idea to CRF conditional posteriors:

```text
P_theta(y in L | x)
```

The PhysRevX MPS paper is broader tensor-network generative modeling background, not the direct main prior for the CRF posterior-event contribution.
