# Claim Summary

| claim_id | claim | level | evidence | boundary |
| --- | --- | --- | --- | --- |
| C1 | `P_theta(L|x)` is a well-defined CRF posterior event probability for finite `Y,T` and regular language `L` | Main | `docs/audits/THEORY_AND_GUARDRAILS.md`; posterior algebra tests | requires finite sequence length and finite label set |
| C2 | Product automaton transfer computes `Z_{theta,L}(x)` exactly | Main | product transfer tests match brute force for accept-all, empty, exact-pattern, parity, low-probability events | reference implementation is finite/sanity scale |
| C3 | Hard-constrained decoding and posterior consistency are different objects | Main | R5a: constrained legality can be 1 while B0 `P(BIO|x)=0.0566`; B1 does not alter posterior mass | do not say hard constraints are useless |
| C4 | Event loss has a finite expectation-difference gradient when `Z_{theta,L}(x)>0` | Main-with-boundary | `docs/paper/THEORY_PROOF_PROSE.md` event-loss gradient proposition | training-signal statement only; no task-improvement theorem |
| C5 | Semi-event training can raise posterior event mass | Main-with-boundary | R5a, R1, R2, R4 all show positive B4 event-mass movement | secondary empirical evidence; not always task-metric dominant; not benchmark superiority |
| C6 | WNUT17 exposes hidden posterior BIO conflict under diagnostic stress | Main-with-boundary | R5a B0 hidden conflict near 1 with entity F1 0; B4 raises BIO event mass | diagnostic stress only; no NER usefulness claim |
| C7 | WNUT17 is learnable by the local CRF setup | Main-with-boundary | R5b B0 entity F1 `0.1660` over 10 seeds | modest F1; no B4 NER improvement claim |
| C8 | Low `P_theta(L|x)` is a field-style rule-specific posterior-consistency signal with positive risk-ranking value | Main-with-boundary | R6a bottom/top gaps plus reanalysis: AUROC `0.7088`, AUPRC `0.8470`; uncertainty baselines are stronger and complementarity is not robust | field-style tasks only; not calibration, not all structured prediction, not uncertainty-baseline superiority, not robust residual predictiveness |
| C9 | Hidden conflict concentrates at low event mass in semi-real diagnostics | Main-with-boundary | R6a hidden-conflict gaps strongest on amount/date/product_code; R5a supports WNUT hidden conflict | real-source fields mostly saturated |
| C10 | Reference product-transfer scaling can be discussed via product-state count | Main-with-boundary | R8 varies sequence length, label count, DFA states, context order | reference CPU sanity only; no speed superiority |
