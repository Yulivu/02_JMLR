# P6 R6a Diagnostic Result-to-Claim Audit

This audit summarizes downloaded AutoDL R6a diagnostic outputs. It is an evidence audit, not a paper section.

## Summary

- risk_signal_supported_rate: `1.0000`
- hidden_conflict_supported_rate: `0.7143`

| source | task | cases | bottom P | top P | exact error gap | char error gap | hidden gap | risk supported | hidden supported |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| real_source | invoice_6d | 3000 | 0.8190 | 0.9728 | 0.5783 | 0.1683 | 0.0000 | True | False |
| real_source | invoice_c6d | 3000 | 0.7916 | 0.9683 | 0.5467 | 0.1321 | 0.0067 | True | True |
| real_source | stock_5d | 3000 | 0.8232 | 0.9772 | 0.6717 | 0.2220 | 0.0000 | True | False |
| semi_real | amount | 3000 | 0.5936 | 0.9293 | 0.5433 | 0.1831 | 0.0750 | True | True |
| semi_real | date | 3000 | 0.4853 | 0.8896 | 0.5550 | 0.0883 | 0.4783 | True | True |
| semi_real | dose | 3000 | 0.8287 | 0.9757 | 0.6483 | 0.2023 | 0.0067 | True | True |
| semi_real | product_code | 3000 | 0.5881 | 0.9181 | 0.2567 | 0.2086 | 0.1567 | True | True |

## Claim Audit

| Claim | Status | Evidence | Boundary |
|---|---|---|---|
| Low `P_theta(L|x)` is a risk signal | supported in R6a | bottom event-mass quantile has higher exact and char error than top quantile on all audited field tasks | field-style diagnostic, not all structured prediction |
| Hidden conflict concentrates at low event mass | partially supported | semi-real tasks show clear hidden-conflict gaps; real-source tasks are mostly saturated | keep separate from R5a WNUT hidden-conflict evidence |
| Diagnostic proves task improvement | not supported | diagnostic and training improvement are different claims | do not claim benchmark superiority |

## Decision

```text
R6a supports the diagnostic/risk-signal claim for field-style tasks.
R6a partially supports hidden-conflict concentration; strongest in semi-real tasks.
Proceed to R8 complexity before paper-writing.
```
