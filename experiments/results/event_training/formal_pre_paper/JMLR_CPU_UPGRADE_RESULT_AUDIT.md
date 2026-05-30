# JMLR CPU Upgrade Result Audit

This document summarizes the formal CPU upgrade runs imported from the raw run bundle.

| block | raw bundle | status | intended use | claim boundary |
|---|---|---|---|---|
| public CoNLL2000 | `public_conll2000_chunking_formal` | passed | public BIO/chunking case study | not benchmark superiority or SOTA |
| B7 constrained-product | `b7_constrained_product_formal` | passed | faithful constrained decoding comparison object | not full WFST or replacement claim |
| R7 sensitivity | `r7_sensitivity_formal` | passed | lambda/rule boundary study | not accuracy-method claim |

Raw bundles remain under ignored `experiments/runs/`; curated review artifacts are retained under `experiments/results/event_training/formal_pre_paper/`.

Primary raw root:

```text
experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade
```

The safe status after these runs is: manuscript drafting can proceed with conservative boundaries; submission readiness still requires final proof/related-work/reproducibility review.
