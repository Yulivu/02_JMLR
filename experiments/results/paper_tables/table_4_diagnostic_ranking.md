# R6a Diagnostic Ranking

| source | task | cases | base_exact_error | AUROC | AUPRC | Spearman | bottom20_exact_error | bottom20_hidden_conflict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | all | 21000 | 0.7359 | 0.7088 | 0.8470 | 0.2869 | 0.8586 | 0.1033 |
| real_source | invoice_6d | 3000 | 0.7203 | 0.7928 | 0.8862 | 0.4949 | 0.9150 | 0 |
| real_source | invoice_c6d | 3000 | 0.6547 | 0.7354 | 0.8116 | 0.4347 | 0.8333 | 0.0067 |
| real_source | stock_5d | 3000 | 0.7143 | 0.8334 | 0.8979 | 0.5667 | 0.9167 | 0 |
| semi_real | amount | 3000 | 0.7810 | 0.8046 | 0.9220 | 0.5178 | 0.9600 | 0.0750 |
| semi_real | date | 3000 | 0.5743 | 0.7220 | 0.7918 | 0.4001 | 0.8817 | 0.4783 |
| semi_real | dose | 3000 | 0.7867 | 0.8509 | 0.9367 | 0.5296 | 0.9400 | 0.0067 |
| semi_real | product_code | 3000 | 0.9200 | 0.8240 | 0.9754 | 0.5165 | 0.9800 | 0.1567 |
