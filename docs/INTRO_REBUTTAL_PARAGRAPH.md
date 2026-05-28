# Introduction Rebuttal Paragraph

Generated: 2026-05-28

Use this paragraph in the introduction after introducing `P_theta(L|x)`.

## Paragraph

One might object that `P_theta(L|x)` is merely standard marginal inference after adding an auxiliary constraint. That description misses the object of interest. We do not ask for the best legal sequence, nor do we replace the model with a constrained decoder, projected posterior, or Lagrangian-relaxed objective. We evaluate a global regular-language event under the original CRF posterior. This produces a scalar audit statistic that can be low even when constrained Viterbi decoding returns a legal output. R5a demonstrates this for BIO legality, and R6a shows that low event mass identifies high-risk field-style examples. Theoretically, the object is the ratio `Z_{theta,L}(x)/Z_theta(x)`: the numerator is computed by a CRF x DFA product transfer, while the denominator remains the original CRF normalizer. This posterior-event probability is therefore distinct from a constrained Viterbi result, from decode-time legality repair, and from training-time constrained optimization.

## Shorter Version

`P_theta(L|x)` is not a constrained Viterbi score. It is the probability assigned by the original CRF posterior to an entire regular-language event. This distinction matters because constrained decoding can return a legal output while the unconstrained posterior still assigns low mass to legal structures, as shown in R5a and diagnosed at sample level in R6a.
