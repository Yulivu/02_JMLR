# block_D_semi_real Formal Pre-Paper Export Audit

This directory is generated from existing local probe CSV files.
No new experiment was run by the export step.

## Scope

- task_family: `semi_real_field`
- runs rows: `84`
- summary rows: `42`

## Known Warnings

- B1/B3 hard-constrained variants are represented through constrained metric fields, not independent rows.
- B5/B6 are local-style baselines unless a future implementation reproduces a specific related-work method.
- These exports preserve local-probe scope and do not create benchmark evidence.
