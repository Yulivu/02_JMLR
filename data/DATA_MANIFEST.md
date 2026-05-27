# Data Manifest

AutoDL/HPC runs are offline by default. Required data must already be present
after cloning from GitHub or must be uploaded manually with FileZilla/SFTP.

| Path | Required For | SHA256 | Source | Policy |
|---|---|---|---|---|
| `data/raw/online_retail.xlsx` | `retail_fields_v1`, `r0_real_source_smoke` | `ef60e854dd93a8a60932a547ebd8c0dca63e33251f2dbbdcb8f2abb2aff3e272` | UCI Online Retail local copy | tracked in Git because it is small and required for smoke |
| `data/raw/wnut17/train.conll` | `wnut17_bio`, future R5 BIO/NER slice | `731820e13f71af324c6b55a1575ec2ce59fbaa2a0806f8f0400b98d56cd6a7a5` | WNUT17 `wnut17train.conll` from `leondz/emerging_entities_17` | tracked in Git; CC-BY 4.0 per upstream README |
| `data/raw/wnut17/dev.conll` | `wnut17_bio`, future R5 BIO/NER slice | `e053b752b8155113ca66e7db08af5f2f5f43ab993694e4774f1ec5bad42312d8` | WNUT17 `emerging.dev.conll` from `leondz/emerging_entities_17` | tracked in Git; CC-BY 4.0 per upstream README |
| `data/raw/wnut17/test.conll` | `wnut17_bio`, future R5 BIO/NER slice | `2aa79b764e56ec9264a1b30fdd9b70195bd00ff400b62edd8f399d5f13c178f0` | WNUT17 `emerging.test.annotated` from `leondz/emerging_entities_17` | tracked in Git; do not replace with multi-label `emerging.test.conll` |

Do not rely on external dataset downloads on AutoDL. If a future dataset is too
large for GitHub, upload it manually into `data/raw/` and add a manifest row
before running formal experiments.

WNUT17 can be refreshed from GitHub with:

```powershell
python scripts/data/fetch_wnut17.py
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
```
