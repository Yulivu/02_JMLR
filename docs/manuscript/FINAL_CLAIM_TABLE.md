# Final Claim Table

Generated: 2026-05-30

This table defines what the project can currently claim before paper drafting. It is intentionally conservative.

## Claim Levels

| Level | Meaning |
|---|---|
| Main | safe for main paper positioning if proof prose is checked |
| Main-with-boundary | safe only with explicit scope limitation |
| Formal foundation | theorem or setup support for the main object, not the main novelty claim |
| Sanity / Appendix | useful as a viability or boundary check, not paper identity |
| Appendix | usable as support, not paper identity |
| Not supported | must not be claimed |

## Final Claims

| Claim ID | Claim | Level | Evidence | Boundary |
|---|---|---|---|---|
| C1 | `P_theta(L|x)` is a well-defined CRF posterior event probability for finite `Y,T` and regular language `L` | Formal foundation | `docs/evidence/THEORY_AUDIT.md`; posterior algebra tests | supports the audit object; not a standalone novelty claim |
| C2 | Product automaton transfer computes `Z_{theta,L}(x)` exactly under explicit finite-context/local-factor assumptions | Formal foundation | product transfer tests match brute force for accept-all, empty, exact-pattern, parity, low-probability events | product-automaton marginal inference is the known computational neighborhood; reference implementation is finite/sanity scale |
| C3 | Hard-constrained decoding and posterior consistency are different objects | Main | R5a: constrained legality can be 1 while B0 `P(BIO|x)=0.0566`; B1 does not alter posterior mass; B7 reports legal decoding without using event mass | do not say hard constraints are useless |
| C4 | Event loss has a finite expectation-difference gradient when `Z_{theta,L}(x)>0` | Main-with-boundary | `docs/manuscript/THEORY_PROOF_PROSE.md` event-loss gradient proposition | training-signal statement only; no task-improvement theorem |
| C5 | Semi-event training can raise posterior event mass | Main-with-boundary | R5a, R1, R2, R4, public CoNLL2000 formal, and R7 sensitivity all show positive B4/event-loss event-mass movement | secondary empirical evidence; not always task-metric dominant; not benchmark superiority |
| C6 | WNUT17 exposes hidden posterior BIO conflict under diagnostic stress | Main-with-boundary | R5a B0 hidden conflict near 1 with entity F1 0; B4 raises BIO event mass | diagnostic stress only; no NER usefulness claim |
| C7 | WNUT17 is learnable by the local CRF setup | Sanity / Appendix | R5b B0 entity F1 `0.1660` over 10 seeds | modest viability check only; no B4 NER improvement claim; not a main paper claim |
| C8 | In the evaluated field-style diagnostics, low `P_theta(L|x)` has positive ranking signal for exact error | Main-with-boundary | R6a bottom/top gaps plus reanalysis: AUROC `0.7088`, AUPRC `0.8470`; uncertainty baselines are stronger and complementarity is not robust | evaluated field-style tasks only; not calibration, not all structured prediction, not uncertainty-baseline superiority, not robust residual predictiveness |
| C9 | Hidden conflict can concentrate at low event mass in semi-real diagnostics, while real-source hidden conflict is often saturated or near zero | Main-with-boundary | R6a hidden-conflict gaps strongest on amount/date/product_code; R5a supports WNUT hidden conflict | real-source fields mostly saturated; do not generalize hidden-conflict concentration beyond evaluated diagnostics |
| C10 | Reference product-transfer scaling can be discussed via product-state count | Main-with-boundary | R8 varies sequence length, label count, DFA states, context order | reference CPU sanity only; no speed superiority |
| C11 | Conditional nonnegative MPO/rank membership can be stated under explicit assumptions | Appendix | MPO sanity tests; `docs/evidence/THEORY_AUDIT.md` T3 | not arbitrary low-rank advantage |
| C12 | Positive-cone approximation bounds can be stated under nonnegativity and positivity assumptions | Appendix | `docs/evidence/THEORY_AUDIT.md` T4 | posterior/log versions need denominator and strict positivity control |
| C13 | The public CoNLL2000 BIO/chunking case provides a structured-prediction audit case with event-mass movement, hidden-conflict reduction, and legal constrained decoding | Main-with-boundary | full CPU run `a10517d`: B0 `P(BIO|x)=0.9762`, hidden conflict `0.0240`, span F1 `0.7773`; B4 `P(BIO|x)=0.9953`, hidden conflict `0.0040`, span F1 `0.7936`; B7 legality `1.0000` | one frozen case-study configuration; three-seed full run is pending; not SOTA, benchmark superiority, or proof that event training generally improves task metrics |
| C14 | A faithful constrained-product decoding baseline can be reported separately from event-mass auditing | Main-with-boundary | B7 formal: legal rate `1.0000` for B0 and B4 source models; `uses_event_mass_for_decoding=False` | constrained-product Viterbi baseline only; not a full WFST toolkit and not a replacement claim |
| C15 | Lambda/rule sensitivity changes event-mass movement and exposes boundary cases where event loss is unhelpful or harmful for task metrics | Main-with-boundary | R7 wrapped formal derisk run `experiments/runs/local_checks/r7_sensitivity_derisk_formal_wrapped`, config `experiments/configs/exp7/r7_sensitivity_formal.yaml`, returncode `0`, duration `28.276712`: stock-like digits has `legal_rate_not_useful=True`; `product_code_swapped_rule` B4 lambda 1.0 raises `P(event)` by `+0.9485` while char accuracy drops `-0.5524` and exact accuracy drops `-0.0816` | sensitivity/boundary study only; rule choice matters; event loss is not a general accuracy method or benchmark claim |

## Not Supported Claims

| Forbidden Claim | Reason |
|---|---|
| The project is submission-ready now | final proof audit, final route synthesis, and paper package are not done |
| Product automaton inference itself is new | CRF x automaton/product marginal inference is the known computational neighborhood; contribution must be object semantics, audit protocol, and empirical boundaries |
| B4 is benchmark-superior | B5/B6 are competitive and task metrics vary |
| B4 improves WNUT17 NER F1 | R5b does not support this |
| Event training always improves accuracy | some high-lambda settings trade accuracy for event mass |
| Hard constraints are useless | hard constraints repair decoded outputs; they answer a different question |
| WFST/constrained methods are beaten or replaced | B7/related constrained baselines are comparison objects, not defeated systems |
| Event risk dominates or robustly complements generic uncertainty | R6a uncertainty baselines are stronger overall and complementarity gaps are mixed |
| Arbitrary CRF/DFA/regular languages have low-rank event transfers | only conditional appendix membership is supported |
| R8 establishes optimized runtime | R8 is reference CPU scaling only |

## Required Wording

Use this sentence or a close variant in the introduction/related-work boundary:

```text
Known product automaton marginal inference is the computational neighborhood; this paper studies the posterior regular-language event mass as a semantics/audit object under the original CRF posterior.
```

## Recommended Paper Position

```text
This is a posterior-event semantics and auditability paper, with training and diagnostic evidence.
It should not be positioned as a benchmark-superiority paper.
```
