# Data Manifest

AutoDL/HPC runs are offline by default. Required data must already be present
after cloning from GitHub or must be uploaded manually with FileZilla/SFTP.

| Path | Required For | SHA256 | Source | Policy |
|---|---|---|---|---|
| `data/raw/online_retail.xlsx` | `retail_fields_v1`, `r0_real_source_smoke` | `ef60e854dd93a8a60932a547ebd8c0dca63e33251f2dbbdcb8f2abb2aff3e272` | UCI Online Retail local copy | tracked in Git because it is small and required for smoke |

Do not rely on external dataset downloads on AutoDL. If a future dataset is too
large for GitHub, upload it manually into `data/raw/` and add a manifest row
before running formal experiments.
