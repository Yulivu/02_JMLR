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

Uncertainty baselines should be added only after the public case emits per-case uncertainty fields; until then mark them pending.

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
python scripts/exp1/run_event_training_task.py --config experiments/configs/exp7/public_conll2000_chunking_formal.yaml --out-dir experiments/runs/autodl_jmlr_block/public_sequence_labeling/conll2000_chunking
```

## Claim Boundary

Allowed after audited results:

```text
The public BIO/chunking case provides an additional structured-prediction audit of original posterior event mass, constrained decoded legality, B4 event-mass movement, and B7 constrained-product behavior.
```

Forbidden:

```text
SOTA, benchmark superiority, B4 improves all task metrics, or constrained methods are replaced.
```
