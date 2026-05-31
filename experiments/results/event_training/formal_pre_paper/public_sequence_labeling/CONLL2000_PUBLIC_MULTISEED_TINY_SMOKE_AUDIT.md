# CoNLL2000 Public Multiseed Tiny Smoke Audit

This is a three-seed plumbing smoke only. It uses 30/30/30 train/unlabeled/dev examples for one epoch and must not be reported as formal evidence.

## Provenance

- raw bundle: `experiments/runs/local_checks/public_conll2000_chunking_multiseed_tiny_smoke`
- git commit: `a10517d`
- config: `experiments\configs\exp7\public_conll2000_chunking_multiseed_tiny_smoke.yaml`
- returncode: `0`
- duration_seconds: `99.700508`
- started_at_utc: `2026-05-30T04:50:30.915484+00:00`
- ended_at_utc: `2026-05-30T04:52:10.615992+00:00`

Wrapper command:

```text
python scripts/exp1/run_event_training_task.py --config experiments\configs\exp7\public_conll2000_chunking_multiseed_tiny_smoke.yaml --out-dir experiments\runs\local_checks\public_conll2000_chunking_multiseed_tiny_smoke
```

Executed module command:

```text
C:\Users\debuf\AppData\Local\Programs\Python\Python312\python.exe -m tensor_crf_jmlr.event_training.public_sequence_labeling_case --seeds 0 1 2 --train-size 30 --unlabeled-size 30 --dev-size 30 --max-len 40 --epochs 1 --lr 0.05 --use-features --output-dir experiments\runs\local_checks\public_conll2000_chunking_multiseed_tiny_smoke
```

## Aggregate Rows

| variant | seeds | P(BIO) mean | P(BIO) std | hidden conflict mean | token acc mean | span F1 mean |
|---|---:|---:|---:|---:|---:|---:|
| B0_unconstrained | 3 | 0.3487 | 0.0413 | 0.9889 | 0.8342 | 0.6894 |
| B4_semi_event_0.1 | 3 | 0.5187 | 0.1360 | 0.7222 | 0.8191 | 0.6647 |

## Formal Multiseed Status

This tiny run remains a plumbing smoke only. The full 1000/1000/1000 three-seed run is curated separately:

```bash
python scripts/analysis/curate_jmlr_cpu_upgrade_results.py --public-multiseed-run experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
```

Boundary: do not use this tiny smoke as C13 evidence even when a full multiseed run exists.
