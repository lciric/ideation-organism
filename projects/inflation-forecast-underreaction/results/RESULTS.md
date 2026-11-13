# Results

Do inflation forecasters under-react to news? Four preregistered tests, recomputed from raw data.
Primary statistics are computed exactly as preregistered (see `audit/`). Only the primary statistic,
its interval and the preregistered guards enter a verdict; every other number below is descriptive.

| test | question | primary statistic | 90% interval | verdict (sealed rule) |
|---|---|---|---|---|
| H03-v2 | Could a recursive real-time correction rule based on revisions reduce ECB staff inflation projection errors? | mean block correlation R = 0.016 (se 0.049) | [-0.074, 0.105] | éliminée |
| J02 | Is the full-sample error-on-revision slope of ECB staff projections (2 quarters ahead) positive and as large as 0.40? | standardised slope 0.443 (NW4 se 0.196, t = 2.27) | [0.122, 0.765] | survit |
| K01 | Do individual ECB SPF forecasters over-react to their own news (2SLS slope < 0)? | 2SLS slope 1.151 (DK8 se 0.463; first-stage F 514) | [0.357, 1.945] | éliminée |
| K20 | Does the US SPF consensus under-react more after large surprises (extra slope c > 0)? | extra slope c = -0.030 (DK4 se 0.071) | [-0.146, 0.086] | non concluant (schema guard: n_violations_schema = 1) |

## H03-v2 — real-time correction rule (ECB staff, horizons 1-4, targets 2004-2025)

- 352 evaluated rows in 11 valid blocks. Without blocks 2020-2023: R = -0.030. Geometric mean of block MSE ratios (corrected / published): 1.097 (above 1: the correction makes errors larger in a typical block).
- Descriptive: overall MSE ratio 0.970, without 2021-2022 targets 1.096; share of rows improved 0.448; share of positive real-time slopes 0.599; by horizon R = 0.145, 0.128, 0.111, -0.087 (h = 1..4); placebo (two-year-old revision) R = 0.075 (se 0.062); the card's own test (h = 4, vintages from 2020): MSE ratio 1.010, DM-HLN p = 0.911.

| block (target years) | rows | R_k | MSE ratio Q_k |
|---|---|---|---|
| 2004-2005 | 32 | -0.225 | 1.219 |
| 2006-2007 | 32 | 0.110 | 1.021 |
| 2008-2009 | 32 | 0.026 | 1.015 |
| 2010-2011 | 32 | -0.062 | 1.114 |
| 2012-2013 | 32 | 0.003 | 1.040 |
| 2014-2015 | 32 | 0.229 | 0.961 |
| 2016-2017 | 32 | -0.041 | 1.062 |
| 2018-2019 | 32 | -0.130 | 1.118 |
| 2020-2021 | 32 | 0.196 | 0.971 |
| 2022-2023 | 32 | 0.246 | 0.945 |
| 2024-2025 | 32 | -0.182 | 1.812 |

## J02 — full-sample error-on-revision slope (ECB staff, 2 quarters ahead, targets 1999Q4-2026Q3)

- 108 targets; raw slope 0.678 points per point (se 0.299); NW8 se 0.162; moving-block bootstrap 90% interval [0.051, 0.592].
- Survival guard: the smallest correlation after removing two consecutive years is 0.050 (removing 2021-2022); after removing one year, 0.084.
- Descriptive: before 2020 (targets 1999Q4-2019Q4, n = 81) the standardised slope is 0.134, raw 0.192 (se 0.111), to compare with 0.20 (0.21) in Granziera, Jalasjoki and Paloviita (2021); without 2021-2023 targets (n = 96) 0.144 (se 0.065).

| year(s) removed | correlation, one year removed | correlation, years Y and Y+1 removed |
|---|---|---|
| 1999 | 0.443 | 0.448 |
| 2000 | 0.448 | 0.459 |
| 2001 | 0.454 | 0.462 |
| 2002 | 0.451 | 0.452 |
| 2003 | 0.444 | 0.448 |
| 2004 | 0.446 | 0.448 |
| 2005 | 0.445 | 0.449 |
| 2006 | 0.448 | 0.455 |
| 2007 | 0.450 | 0.462 |
| 2008 | 0.454 | 0.466 |
| 2009 | 0.452 | 0.457 |
| 2010 | 0.447 | 0.449 |
| 2011 | 0.445 | 0.446 |
| 2012 | 0.444 | 0.441 |
| 2013 | 0.440 | 0.432 |
| 2014 | 0.436 | 0.443 |
| 2015 | 0.451 | 0.450 |
| 2016 | 0.442 | 0.449 |
| 2017 | 0.449 | 0.454 |
| 2018 | 0.447 | 0.446 |
| 2019 | 0.442 | 0.443 |
| 2020 | 0.445 | 0.445 |
| 2021 | 0.443 | 0.050 |
| 2022 | 0.084 | 0.187 |
| 2023 | 0.572 | 0.585 |
| 2024 | 0.450 | 0.450 |
| 2025 | 0.443 | 0.444 |
| 2026 | 0.444 | – |

## K01 — individual ECB SPF forecasters (target years 2002-2025)

- 8595 revisions, 94 forecasters, 96 rounds. First stage 0.496 (F = 514); reduced-form t = 2.59; se clustered by round 0.460, by target year 0.293.
- Without target years 2021-2023: 2SLS 0.168 (se 0.466, F = 315); largest 2SLS slope when one target year is removed 1.320; with forecaster fixed effects 1.099 (se 0.434); before 2020 0.134 (se 0.604), OLS with fixed effects before 2020 0.043 (se 0.095; Broer and Kohlhas: -0.169 (0.182)).
- The naive within-round slope -0.452 (se 0.066) measures the change in the dispersion of forecasts, not their accuracy (it is -1/2 by construction when dispersion is stable). Noise bounds: both 0, because the pooled OLS and 2SLS slopes are positive (there is no negative slope for reporting noise to explain).
- Consensus slope 0.918 (se 0.238), ECB staff 0.774 (se 0.294), difference ECB - consensus -0.143 (se 0.146); without 2021-2023: consensus 0.515, ECB 0.162.

| estimate | sample | slope | se |
|---|---|---|---|
| Individuals, 2SLS (preregistered) | full sample | 1.151 | 0.463 |
| Individuals, naive pooled OLS | full sample | 0.419 | 0.188 |
| Individuals, naive within-round | full sample | -0.452 | 0.066 |
| SPF consensus | full sample | 0.918 | 0.238 |
| ECB staff | full sample | 0.774 | 0.294 |
| Individuals, 2SLS (preregistered) | excluding 2021-2023 | 0.168 | 0.466 |
| Individuals, naive pooled OLS | excluding 2021-2023 | 0.017 | 0.096 |
| Individuals, naive within-round | excluding 2021-2023 | -0.394 | 0.056 |
| SPF consensus | excluding 2021-2023 | 0.515 | 0.207 |
| ECB staff | excluding 2021-2023 | 0.162 | 0.119 |

## K20 — US SPF consensus, five variables, large vs small surprises (targets 1969-2026)

- 1004 variable-quarter rows (223 quarters; 334 after large surprises); base slope (mean of b_v) 0.194, slope after large surprises 0.164; revision variance ratio large/small 3.06; mechanical-bias floor 0.10; effective observations 820.
- The sealed verdict is 'non concluant' because schema check 9 fails on one row (CPI 2026-Q1: October 2025 is missing in FRED, so the previous-quarter CPI level is missing). That row enters no regression. With the check passed the rule would have given 'éliminée' (upper bound 0.086 < 0.40).
- Without each episode window, c ranges from -0.084 to 0.014; NW8 se 0.068, no-lag se 0.073; with the pandemic quarters -0.095; since 1985 -0.067; before 2020 -0.037; medians 0.075; the card's own cut on |revision| > 1 s.d. -0.003.

| variable | slope after small surprises | slope after large surprises | c_v (se) |
|---|---|---|---|
| PGDP | 0.148 | 0.321 | 0.173 (0.183) |
| RGDP | -0.100 | -0.153 | -0.053 (0.158) |
| UNEMP | 0.418 | 0.314 | -0.103 (0.149) |
| CPI | 0.090 | 0.137 | 0.047 (0.151) |
| TBILL | 0.496 | 0.185 | -0.311 (0.180) |

## Figures

1. `figures/fig1_ecb_error_vs_revision.png`
2. `figures/fig2_j02_leave_years_out.png`
3. `figures/fig3_h03v2_blocks.png`
4. `figures/fig4_k01_slopes.png`
5. `figures/fig5_k20_by_variable.png`
