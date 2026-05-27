# Data

Dataset staging area.

Current retained local data:

```text
raw/online_retail.xlsx
```

This file is used by the real-source small-field event-training experiment. It is a local research artifact, not a benchmark release.

AutoDL/HPC runs are offline by default. See `data/DATA_MANIFEST.md` and verify
before running:

```powershell
python scripts/data/verify_data.py --strict
```
