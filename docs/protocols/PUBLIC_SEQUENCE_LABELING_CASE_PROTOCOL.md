# Public Sequence Labeling Case Protocol

Updated: 2026-05-30

## Purpose

WNUT17 is useful for the hidden-posterior-conflict story but too weak to carry the public structured-prediction case by itself: R5a has entity F1 equal to zero, and R5b has saturated BIO event mass with no B4 F1 improvement. This protocol adds a cleaner public BIO-style case if data provenance and licensing are acceptable.

## Preferred Case

```text
CoNLL-2000 chunking
```

Reason:

- public sequence labeling dataset;
- chunk labels use BIO-style structure;
- task metric can be token accuracy and strict chunk-span F1;
- event `L_BIO` is the same strict BIO language used by WNUT17 and B7.

Local paths after download:

```text
data/raw/conll2000_chunking/train.txt
data/raw/conll2000_chunking/test.txt
```

Prepare command:

```powershell
python scripts/data/fetch_conll2000_chunking.py
```

The downloader first attempts the historical official CoNLL2000 hosts and then
falls back to the GitHub mirror used in local smoke because the official hosts
returned 404/502 on 2026-05-30. It verifies the downloaded text MD5 hashes and
records resolved source URLs in `data/raw/conll2000_chunking/PROVENANCE.md`.
Review redistribution/licensing before tracking downloaded files.

Current local hashes:

| file | SHA256 | MD5 |
|---|---|---|
| `train.txt` | `82033cd7a72b209923a98007793e8f9de3abc1c8b79d646c50648eb949b87cea` | `2e2f24e90e20fcb910ab2251b5ed8cd0` |
| `test.txt` | `73b7b1e565fa75a1e22fe52ecdf41b6624d6f59dacb591d44252bf4d692b1628` | `56944df34be553b72a2a634e539a0951` |

## Required Metrics

| Metric | Meaning |
|---|---|
| `mean_p_event` | unconstrained posterior event mass `P_theta(L_BIO|x)` |
| `unconstrained_legal_rate` | legality of unconstrained Viterbi |
| `constrained_decoded_legal_rate` | legality of hard constrained decode |
| `b7_legal_rate` | legality of constrained-product decoding baseline |
| `token_accuracy` | unconstrained task metric |
| `span_f1` | strict BIO span metric |
| `hidden_conflict_rate` | constrained legal but original posterior event mass below threshold |
| `B4 delta` | event-mass movement relative to B0 |

The formal public run emits per-case uncertainty fields and the curated analysis compares event risk against entropy, margin, and max-probability uncertainty baselines.

## Smoke Command

```powershell
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_smoke.yaml --out-dir experiments/runs/local_checks/public_conll2000_chunking_smoke
```

If data are absent, the runner writes `PUBLIC_CASE_PENDING.md` and exits without fabricating results.

## Local Smoke Result

Completed on 2026-05-30 with:

```powershell
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_smoke.yaml --out-dir experiments/runs/local_checks/public_conll2000_chunking_smoke
```

Curated smoke audit:

```text
experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_SMOKE_AUDIT.md
```

Smoke interpretation:

```text
B4 moved posterior BIO event mass upward and reduced hidden conflict, while
token/span metrics decreased slightly. This is useful boundary evidence, not a
superiority result.
```

## Full-Run Command

```powershell
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_formal.yaml --out-dir experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/public_conll2000_chunking_formal
```

Formal result:

```text
raw bundle: experiments/runs/autodl_jmlr_block/jmlr_cpu_upgrade/public_conll2000_chunking_formal
curated audit: experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_FORMAL_AUDIT.md
```

Key formal numbers:

```text
B0 P(BIO|x)=0.9762, hidden conflict=0.0240, span F1=0.7773
B4 P(BIO|x)=0.9953, hidden conflict=0.0040, span F1=0.7936
B7 legality=1.0000
```

## Multiseed Status

The runner supports explicit seeds and a three-seed full config:

```text
experiments/configs/exp7/public_conll2000_chunking_multiseed.yaml
experiments/configs/exp7/public_conll2000_chunking_multiseed_smoke.yaml
```

Completed local tiny smoke:

```powershell
python -m tensor_crf_jmlr.event_training.public_sequence_labeling_case --output-dir experiments/runs/local_checks/public_conll2000_multiseed_tiny_smoke --seeds 0 1 2 --train-size 30 --unlabeled-size 30 --dev-size 30 --max-len 40 --epochs 1 --lr 0.05 --use-features
```

Curated tiny-smoke audit:

```text
experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_MULTISEED_TINY_SMOKE_AUDIT.md
```

The tiny smoke validates plumbing only and is not formal evidence. The full
three-seed run was completed locally with 1000/1000/1000 train/unlabeled/dev
examples:

```bash
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_multiseed.yaml --out-dir experiments/runs/local_checks/public_conll2000_chunking_multiseed_full
```

Provenance: git commit `002ecbb`, returncode `0`, duration `3076.544701`
seconds. Curated audit:

```text
experiments/results/event_training/formal_pre_paper/public_sequence_labeling/CONLL2000_PUBLIC_MULTISEED_FORMAL_AUDIT.md
```

## Claim Boundary

Allowed after audited results:

```text
The public BIO/chunking case provides an additional structured-prediction audit of original posterior event mass, constrained decoded legality, B4 event-mass movement, and B7 constrained-product behavior under a full local three-seed case-study configuration.
```

Forbidden:

```text
SOTA, benchmark superiority, B4 improves all task metrics, or constrained methods are replaced.
```
