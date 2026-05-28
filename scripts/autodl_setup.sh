#!/usr/bin/env bash
set -euo pipefail

python -m pip install -U pip
python -m pip install -e ".[dev]"

python -c "import tensor_crf_jmlr; print('tensor_crf_jmlr import ok')"
python -c "import torch; print(torch.__version__); print('cuda_available=', torch.cuda.is_available())"

python scripts/data/verify_data.py --strict
python scripts/data/audit_bio_ner_slice.py --data-dir data/raw/wnut17
