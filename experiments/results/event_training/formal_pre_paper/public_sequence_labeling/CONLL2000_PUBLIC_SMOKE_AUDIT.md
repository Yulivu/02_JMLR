# CoNLL2000 Public Sequence Labeling Smoke Audit

Updated: 2026-05-30

This is a local smoke run for the optional public BIO/chunking case. It is not a formal benchmark result and must not be used for superiority claims.

## Provenance

Data:

```text
data/raw/conll2000_chunking/train.txt
data/raw/conll2000_chunking/test.txt
```

The downloader attempted the historical official CoNLL2000 URLs first. They returned 404/502 locally on 2026-05-30, so the local files were fetched from the GitHub mirror configured in `scripts/data/fetch_conll2000_chunking.py` and checked against MD5 hashes.

Command:

```powershell
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_smoke.yaml --out-dir experiments/runs/local_checks/public_conll2000_chunking_smoke
```

Run metadata:

```text
train_sentences = 80
unlabeled_sentences = 80
dev_sentences = 80
max_len = 40
epochs = 1
use_features = true
```

## Smoke Table

| variant | P(BIO\|x) | hidden conflict | unconstrained legal | constrained legal | B7 legal | token acc | B7 token acc | span F1 | B7 span F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B0 unconstrained | 0.7303 | 0.4125 | 1.0000 | 1.0000 | 1.0000 | 0.8715 | 0.8715 | 0.7345 | 0.7345 |
| B4 semi-event 0.1 | 0.8078 | 0.2125 | 0.9750 | 1.0000 | 1.0000 | 0.8630 | 0.8627 | 0.7219 | 0.7211 |

## Interpretation

Allowed:

```text
The public BIO/chunking smoke provides a cleaner public structured-prediction case where B4 moves posterior event mass upward and reduces hidden posterior conflict.
```

Required boundary:

```text
Task metrics decrease slightly in this smoke. Do not claim benchmark superiority, B4 task improvement, or replacement of constrained decoding/B7.
```

## Status

```text
public_case_smoke = passed
public_case_full_run = pending
uncertainty_fields_for_public_case = implemented in runner and present in smoke raw bundle
```

The raw smoke bundle now includes `public_case_details.csv` with event risk, token marginal entropy, sequence entropy, Viterbi margin, max sequence probability, and negative log Viterbi probability fields.
