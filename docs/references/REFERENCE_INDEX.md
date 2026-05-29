# Reference Index

Updated: 2026-05-29

This directory keeps reference papers and retained reading notes. It is not the current project entrypoint.

Current project entrypoints:

```text
docs/PROJECT_OVERVIEW.md
docs/README.md
docs/manuscript/FINAL_CLAIM_TABLE.md
docs/external_review/EXTERNAL_REVIEW_README.md
```

## Papers

| File | Paper | Why Here |
|---|---|---|
| `papers/2018_Han_PRX_Unsupervised_Generative_Modeling_Using_Matrix_Product_States.pdf` | Han et al., *Unsupervised Generative Modeling Using Matrix Product States*, Phys. Rev. X 2018 | tensor-network generative modeling background |

## Reading Notes

| File / Folder | Content |
|---|---|
| `reading_notes/2021_uMPS_AISTATS_detailed_reading_CN.md` | uMPS AISTATS 2021 detailed Chinese reading note |
| `reading_notes/rankseg/` | RankSEG reading notes retained as theory-writing reference material |

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
