# R7 Lambda / Rule Sensitivity

| task | variant | runs | P_event | delta_P_event | delta_legal_rate | delta_char_acc | delta_exact_acc | boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| date | B0_unconstrained | 10 | 0.7136 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | ordinary |
| date | B4_semi_event_1.0 | 10 | 0.9738 | 0.2603 | 0.1948 | 0.0306 | 0.1996 | ordinary |
| product_code | B0_unconstrained | 10 | 0.7765 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | ordinary |
| product_code | B4_semi_event_1.0 | 10 | 0.9844 | 0.2079 | 0.0328 | 0.0097 | 0.0248 | ordinary |
| product_code_swapped_rule | B0_unconstrained | 10 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | event/task tradeoff |
| product_code_swapped_rule | B4_semi_event_0.1 | 10 | 0.6083 | 0.6083 | 0.6752 | -0.4352 | -0.0668 | event/task tradeoff |
| product_code_swapped_rule | B4_semi_event_1.0 | 10 | 0.9486 | 0.9485 | 0.9716 | -0.5524 | -0.0816 | event/task tradeoff |
| stock_like_digits | B0_unconstrained | 10 | 0.9192 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | legal-rate-not-useful |
| stock_like_digits | B4_semi_event_1.0 | 10 | 0.9961 | 0.0769 | 0.0000 | 0.0331 | 0.0868 | legal-rate-not-useful |
