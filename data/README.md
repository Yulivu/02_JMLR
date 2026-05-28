# Data

Dataset staging area.

Current retained local data:

```text
raw/online_retail.xlsx
raw/wnut17/train.conll
raw/wnut17/dev.conll
raw/wnut17/test.conll
```

`online_retail.xlsx` is used by the real-source small-field event-training experiment. It is a local research artifact, not a benchmark release.

`raw/wnut17/*.conll` is the frozen WNUT17 BIO/NER slice for the future R5 canonical structured prediction block. See `docs/protocols/BIO_NER_SLICE_PROTOCOL.md`.

AutoDL/HPC runs are offline by default. See `data/DATA_MANIFEST.md` and verify
before running:

```powershell
python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
```
