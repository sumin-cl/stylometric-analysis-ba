# Aggregate Significance Report

Primary inferential statistic: Mann-Whitney U with rank-biserial effect size.
Complementary statistics: Levene (variance), Kolmogorov-Smirnov (distribution shape),
Cohen's d (parametric effect size).

## Compact view (effect sizes)

| metric | comparison | abs_r_rb | rrb_effect | abs_cohens_d | cohen_effect | p_levene | p_ks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MTLD | A vs B (filtered) | 0.3331 | medium | 0.5981 | medium | 0.0000 | 0.0000 |
| MTLD | B vs C (LLM) | 0.6140 | large | 1.0386 | large | 0.0000 | 0.0000 |
| Shannon WORD | A vs B (filtered) | 0.1503 | small | 0.2791 | small | 0.0000 | 0.0000 |
| Shannon WORD | B vs C (LLM) | 0.3398 | medium | 0.6257 | medium | 0.0000 | 0.0000 |
| Shannon POS | A vs B (filtered) | 0.0207 | negligible | 0.0176 | negligible | 0.6736 | 0.0493 |
| Shannon POS | B vs C (LLM) | 0.0538 | negligible | 0.2203 | small | 0.0000 | 0.0000 |
| PTD | A vs B (filtered) | 0.0224 | negligible | 0.0482 | negligible | 0.0002 | 0.0205 |
| PTD | B vs C (LLM) | 0.4640 | medium | 0.7341 | medium | 0.0000 | 0.0000 |
| FWR tagged | A vs B (filtered) | 0.0943 | negligible | 0.1563 | negligible | 0.0000 | 0.0000 |
| FWR tagged | B vs C (LLM) | 0.4565 | medium | 0.7589 | medium | 0.0000 | 0.0000 |
| FWR untagged | A vs B (filtered) | 0.1181 | small | 0.2057 | small | — | — |
| FWR untagged | B vs C (LLM) | 0.4301 | medium | 0.8386 | large | — | — |

## Full table

| metric | comparison | n1 | n2 | mean_1 | mean_2 | diff | U | p_mwu | r_rb | abs_r_rb | rrb_effect | levene_W | p_levene | ks_D | p_ks | cohens_d | abs_cohens_d | cohen_effect |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MTLD | A vs B (filtered) | 3110 | 3251 | 122.8 | 150.6 | 27.75 | 3.371e+06 | 4.381e-117 | 0.3331 | 0.3331 | medium | 110.9 | 1.002e-25 | 0.2508 | 2.867e-88 | -0.5981 | 0.5981 | medium |
| MTLD | B vs C (LLM) | 441 | 476 | 151.6 | 204.7 | 53.13 | 4.051e+04 | 3.441e-58 | 0.614 | 0.614 | large | 58.53 | 5.068e-14 | 0.5658 | 3.653e-68 | -1.039 | 1.039 | large |
| Shannon WORD | A vs B (filtered) | 8848 | 8848 | 10.83 | 11.04 | 0.2051 | 3.326e+07 | 3.77e-67 | 0.1503 | 0.1503 | small | 98.05 | 4.682e-23 | 0.1103 | 2.833e-47 | -0.2791 | 0.2791 | small |
| Shannon WORD | B vs C (LLM) | 1196 | 1196 | 10.8 | 10.04 | -0.7588 | 4.722e+05 | 6.042e-47 | 0.3398 | 0.3398 | medium | 32.96 | 1.059e-08 | 0.2751 | 3.177e-40 | -0.6257 | 0.6257 | medium |
| Shannon POS | A vs B (filtered) | 8848 | 8848 | 3.571 | 3.549 | -0.02157 | 3.995e+07 | 0.01704 | -0.02071 | 0.02071 | negligible | 0.1775 | 0.6736 | 0.02046 | 0.04931 | 0.01755 | 0.01755 | negligible |
| Shannon POS | B vs C (LLM) | 1196 | 1196 | 3.556 | 3.514 | -0.04249 | 6.767e+05 | 0.02262 | 0.05384 | 0.05384 | negligible | 250.3 | 1.096e-53 | 0.1798 | 2.699e-17 | -0.2203 | 0.2203 | small |
| PTD | A vs B (filtered) | 8848 | 8848 | 5.494 | 5.438 | -0.05593 | 4.002e+07 | 0.00996 | -0.02237 | 0.02237 | negligible | 14.19 | 0.000166 | 0.02204 | 0.02048 | 0.04821 | 0.04821 | negligible |
| PTD | B vs C (LLM) | 1196 | 1196 | 5.423 | 4.602 | -0.8213 | 1.047e+06 | 5.83e-86 | -0.464 | 0.464 | medium | 234.6 | 1.991e-52 | 0.3676 | 5.179e-130 | 0.7341 | 0.7341 | medium |
| FWR tagged | A vs B (filtered) | 8848 | 8848 | 0.3242 | 0.3149 | -0.009283 | 4.284e+07 | 1.7e-27 | -0.09431 | 0.09431 | negligible | 27.06 | 1.99e-07 | 0.07755 | 4.914e-25 | 0.1563 | 0.1563 | negligible |
| FWR tagged | B vs C (LLM) | 1196 | 1196 | 0.3176 | 0.359 | 0.04142 | 3.887e+05 | 2.862e-83 | 0.4565 | 0.4565 | medium | 611.4 | 1.741e-131 | 0.4347 | 3.402e-184 | -0.7589 | 0.7589 | medium |
| FWR untagged | A vs B (filtered) | 8848 | 8848 | 0.8473 | 0.7975 | -0.04986 | 4.377e+07 | 3.876e-42 | -0.1181 | 0.1181 | small | — | — | — | — | 0.2057 | 0.2057 | small |
| FWR untagged | B vs C (LLM) | 1196 | 1196 | 0.8144 | 0.9771 | 0.1628 | 4.076e+05 | 4.179e-74 | 0.4301 | 0.4301 | medium | — | — | — | — | -0.8386 | 0.8386 | large |

## Vocabulary-alignment diagnostics

One-sided vocabulary alignment (diagnostic, not an effect-size measure). `raw_ref` = reference corpus raw value; `raw_other` = comparison corpus raw value; `other_aligned` = comparison corpus restricted to reference vocabulary (min_freq>=3 for WORD). A near-zero or negative `diff_aligned` indicates the raw difference is driven by vocabulary novelty (topic shift) rather than by distributional structure.

| metric | comparison | raw_ref | raw_other | other_aligned | diff_aligned |
| --- | --- | --- | --- | --- | --- |
| MTLD | A vs B (filtered) | 122.8 | 150.6 | 122.8 | 0.007755 |
| MTLD | B vs C (LLM) | 151.6 | 204.7 | 138.4 | -13.25 |
| Shannon WORD | A vs B (filtered) | 10.83 | 11.04 | 10.29 | -0.5414 |
| Shannon WORD | B vs C (LLM) | 10.8 | 10.04 | 9.079 | -1.72 |
