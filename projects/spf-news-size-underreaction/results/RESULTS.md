# Results

Does forecasters' under-reaction grow with the size of news? Two preregistered tests answer it on two
surveys: K20 on the US Survey of Professional Forecasters (1969-2026) and K20-ZE, a blind replication
on the ECB Survey of Professional Forecasters (2000-2025). For each, the primary statistic, its
interval and the guards are computed exactly as sealed (see `../audit/`); only they enter the verdict.
Every section marked *Descriptive, not preregistered* was added for this project and describes the
data; none of it can change a verdict.

| test | survey | extra slope after large news, c | 90% interval | verdict (sealed rule) |
|---|---|---|---|---|
| K20 | US SPF, 1969-2026 | -0.030 | [-0.146, 0.086] | non concluant |
| K20-ZE | ECB SPF, 2000-2025 | -0.106 | [-0.259, 0.047] | éliminée |

## K20 — US Survey of Professional Forecasters, five variables, targets 1969-2026

### The preregistered test

- Sample: 1004 variable-quarter rows (223 target quarters), 334 of them after a large surprise (top third of |surprise| of the variable).
- **Extra slope after large surprises c = -0.030** (Driscoll-Kraay 4-lag se 0.071, t = -0.42); 90% interval [-0.146, 0.086]. The card predicted +0.40.
- Base slope after small surprises (mean of the five b_v) 0.194; after large surprises 0.164. Revision variance ratio large/small 3.06 (relevance condition: at least 1.25). Mechanical-bias floor 0.10 (computed bias with 20% noise: 0.081). Effective observations 820.
- **Verdict from the sealed rule applied to this pipeline's numbers: non concluant** (sealed verdict: non concluant). The only condition that holds is `n_violations_schema` = 1 > 0: schema check 9 fails on one row, CPI 2026-Q1 (October 2025 is missing in FRED, so the previous-quarter CPI level is missing although the 2026-Q1 level exists). That row is not complete, so it enters no regression; every number above is the same whether or not it is in the file.
- For information only (not the verdict): with that check set aside, the same rule gives **éliminée** (upper bound 0.086 < 0.40). See `audit/README.md`.

Preregistered secondary analyses (computed by the rule, outside the verdict):

| analysis | c | se |
|---|---|---|
| S2: 8 lags / 0 lags | -0.030 | 0.068 / 0.073 |
| S3: with RGDP and UNEMP 2020-2021 | -0.095 | 0.074 |
| S4: targets from 1985 | -0.067 | 0.083 |
| S5: targets to 2019Q4 | -0.037 | 0.079 |
| S6: median consensus | 0.075 | 0.069 |
| S7: card's cut, \|revision\| > 1 s.d. | -0.003 | 0.086 |

### 1. Base under-reaction slope, by variable and pooled

*Descriptive, not preregistered.*

Slope of the standardised error on the standardised revision, one constant per variable, no split by surprise size (the Coibion-Gorodnichenko regression in K20's units: s.d. of error per s.d. of revision). Positive = under-reaction. 'Before 2020' = targets to 2019Q4, with the full-sample standardisation. Raw units = points of error per point of revision.

| variable | full sample: slope (se) | 90% interval | rows | before 2020: slope (se) | 90% interval | rows | raw units, full sample |
|---|---|---|---|---|---|---|---|
| PGDP | 0.258 (0.096) | [0.10, 0.42] | 223 | 0.249 (0.108) | [0.07, 0.43] | 196 | 1.11 (0.41) |
| RGDP | -0.119 (0.078) | [-0.25, 0.01] | 215 | -0.093 (0.084) | [-0.23, 0.04] | 196 | -0.57 (0.37) |
| UNEMP | 0.352 (0.100) | [0.19, 0.52] | 214 | 0.357 (0.101) | [0.19, 0.52] | 196 | 0.80 (0.23) |
| CPI | 0.118 (0.095) | [-0.04, 0.28] | 175 | 0.074 (0.098) | [-0.09, 0.24] | 150 | 0.87 (0.70) |
| TBILL | 0.359 (0.093) | [0.21, 0.51] | 177 | 0.278 (0.081) | [0.15, 0.41] | 150 | 0.80 (0.21) |
| pooled | 0.191 (0.047) | [0.11, 0.27] | 1004 | 0.171 (0.047) | [0.09, 0.25] | 888 | – |

### 2. Extra slope c by variable and with each episode removed

*Descriptive, not preregistered.*
The point estimates are preregistered fields (secondary S1 and the episode guard); the intervals and this presentation are added here.

| variable | slope after small surprises (se) | slope after large surprises (se) | c_v (se) | 90% interval of c_v |
|---|---|---|---|---|
| PGDP | 0.148 (0.091) | 0.321 (0.143) | 0.173 (0.183) | [-0.13, 0.47] |
| RGDP | -0.100 (0.115) | -0.153 (0.109) | -0.053 (0.158) | [-0.31, 0.21] |
| UNEMP | 0.418 (0.150) | 0.314 (0.104) | -0.103 (0.149) | [-0.35, 0.14] |
| CPI | 0.090 (0.059) | 0.137 (0.147) | 0.047 (0.151) | [-0.20, 0.29] |
| TBILL | 0.496 (0.153) | 0.185 (0.105) | -0.311 (0.180) | [-0.61, -0.01] |
| pooled | 0.194 (0.056) | 0.164 (0.048) | -0.030 (0.071) | [-0.15, 0.09] |

| episode removed | target window | main rows removed | c (se) | t | 90% interval |
|---|---|---|---|---|---|
| E1 | 1969Q4-1971Q4 | 15 | -0.033 (0.072) | -0.45 | [-0.15, 0.09] |
| E2 | 1973Q4-1976Q1 | 27 | -0.084 (0.055) | -1.52 | [-0.17, 0.01] |
| E3 | 1980Q1-1983Q4 | 60 | 0.014 (0.092) | 0.15 | [-0.14, 0.16] |
| E4 | 1990Q3-1992Q1 | 35 | -0.021 (0.072) | -0.28 | [-0.14, 0.10] |
| E5 | 2001Q1-2002Q4 | 40 | -0.028 (0.071) | -0.39 | [-0.14, 0.09] |
| E6 | 2007Q4-2010Q2 | 55 | -0.007 (0.068) | -0.11 | [-0.12, 0.10] |
| E7 | 2019Q4-2023Q4 | 69 | -0.027 (0.078) | -0.34 | [-0.15, 0.10] |

### 3. Sorting on the size of the revision instead of the surprise

*Descriptive, not preregistered.*
Same regression, three definitions of 'large'. Sorting on the revision also sorts on the consensus noise that the revision shares (with the opposite sign) with the error, which pushes c up even when the true slope does not depend on size (preregistration, section 7). The variance ratio is the variance of the standardised revision after large news over that after small news.

| definition of 'large' | share of rows | variance ratio | c (se) | 90% interval |
|---|---|---|---|---|
| top third of \|surprise\| (preregistered) | 0.33 | 3.1 | -0.030 (0.071) | [-0.15, 0.09] |
| \|revision\| > 1 s.d. (card; S7) | 0.22 | 17.2 | -0.003 (0.086) | [-0.14, 0.14] |
| top third of \|revision\| | 0.33 | 20.9 | 0.116 (0.116) | [-0.07, 0.31] |

Simulation (`src/snu/simulation.py`, also run as a test): panels with **no true size effect** (constant true slope), fat-tailed news (Student t, 3 degrees of freedom), consensus noise in both surveys (noise s.d. 0.25 x the quarter's volatility: 11% of the variance of the revision with scaled noise, 11% with fixed noise), and a lagged surprise that reveals the quarter's volatility but not the noise of the survey being evaluated. 'Scaled' noise grows with turbulence (forecast disagreement does); 'fixed' noise has the same size in every quarter.

| noise model | sort | mean c, 300 panels of 1 000 rows | 5-95% range | c in one panel of 200 000 rows (se) |
|---|---|---|---|---|
| scaled | lagged \|surprise\|, top third (K20) | -0.003 | [-0.16, +0.16] | +0.013 (0.009) |
| scaled | \|revision\| > 1 s.d. (card) | +0.046 | [-0.11, +0.21] | +0.067 (0.008) |
| fixed | lagged \|surprise\|, top third (K20) | +0.050 | [-0.10, +0.21] | +0.063 (0.008) |
| fixed | \|revision\| > 1 s.d. (card) | +0.120 | [-0.03, +0.27] | +0.148 (0.007) |

With scaled noise the surprise sort is unbiased and the revision sort is not. With fixed noise the surprise sort keeps a smaller positive residual (differential attenuation, section 7 of the preregistration), which the preregistered floor max(0.10, computed bias) is meant to absorb.

### 4. Base under-reaction slope by decade

*Descriptive, not preregistered.*
Pooled slope (one constant per variable, one common slope, no size split) by decade of the target quarter; CPI and T-bill targets start in 1982Q3.

| decade | rows | quarters | variables | slope (se) | 90% interval |
|---|---|---|---|---|---|
| 1969-1979 | 108 | 36 | PGDP, RGDP, UNEMP | 0.063 (0.073) | [-0.06, 0.18] |
| 1980-1989 | 180 | 40 | PGDP, RGDP, UNEMP, CPI, TBILL | 0.058 (0.060) | [-0.04, 0.16] |
| 1990-1999 | 200 | 40 | PGDP, RGDP, UNEMP, CPI, TBILL | 0.154 (0.072) | [0.03, 0.27] |
| 2000-2009 | 200 | 40 | PGDP, RGDP, UNEMP, CPI, TBILL | 0.317 (0.077) | [0.19, 0.44] |
| 2010-2019 | 200 | 40 | PGDP, RGDP, UNEMP, CPI, TBILL | 0.013 (0.080) | [-0.12, 0.14] |
| 2020-2026 | 116 | 27 | PGDP, RGDP, UNEMP, CPI, TBILL | 0.160 (0.104) | [-0.01, 0.33] |

## K20-ZE — ECB Survey of Professional Forecasters, three variables, target years 2000-2025

A blind replication of K20, preregistered and sealed on 2026-11-13 before any statistic was computed (see `../audit/README.md`). Annual targets (calendar-year averages), eight survey rounds per target, six series (variable x horizon); the news is the change in the latest published figure that the ECB sends to the forecasters between two rounds, so it contains no survey noise.

### The preregistered test

- Sample: 578 variable x target-year x round rows (107 rounds, 26 target years), 196 after large news. Schema: `n_violations_schema` = 0, `n_anomalies_hors_principal` = 0.
- **Extra slope after large news c = -0.106** (Driscoll-Kraay 8-lag se 0.090, t = -1.18); 90% interval (critical value 1.708) [-0.259, 0.047]. The prediction was +0.40.
- **Positive control passed** (`controle_positif_ok` = 1): common slope b_commun = 0.366 (se 0.057, lower 90% bound 0.268); slope after small news 0.447 (lower bound 0.298); after large news 0.341. The consensus under-reacts, so a null c is not the silence of a blind instrument.
- Revision variance ratio large/small 8.42; computed mechanical bias 0.425, so the survival floor is 0.425. Without each episode c = -0.064 (E1), -0.185 (E2), -0.167 (E3). Effective observations 735.
- **Verdict from the sealed rule applied to this pipeline's numbers: éliminée** (sealed verdict: éliminée); no non-conclusion condition holds. Elimination case (a): the upper bound 0.047 is below 0.40.
- The floor (0.43) turned out far above the 0.10 assumed in the preregistration's decisiveness simulation (calibrated on K20's variance ratio of about 3; here it is 8.4): had c been near +0.40, the test would mostly have ended 'non concluant'. The elimination does not depend on the floor: it comes from the upper bound, which the floor does not enter, and the mechanical bias pushes c up, not down.
- Surprises are taken in double precision without rounding, as the letter of the preregistration says and as both the experimenter and the verifier did (`audit/K20-ZE/ecarts.md`, C1); the rounded reading gives c = -0.099 and the same verdict.

Preregistered secondary analyses (computed by the rule, outside the verdict):

| analysis | c | se |
|---|---|---|
| S2: 4 / 12 / 0 lags; clustered by target year | -0.106 | 0.087 / 0.094 / 0.099; 0.079 |
| S3: with GDP and unemployment 2020-2021 | 0.177 | 0.077 |
| S4: target years to 2019 | -0.149 | 0.134 |
| S5: current year / next year | -0.011 / -0.198 | 0.130 / 0.151 |
| S6: median consensus | -0.031 | 0.102 |
| S7: card's cut, \|revision\| > 1 s.d. | -0.229 | 0.131 |
| S8: surprise relative to the consensus (554 rows) | -0.271 | 0.113 |

### 1. Extra slope c by variable

*Descriptive, not preregistered.*
The point estimates are the preregistered secondary S1; the intervals (critical value 1.708) are added here.

| variable | c_v (se) | 90% interval |
|---|---|---|
| HICP | 0.127 (0.171) | [-0.17, 0.42] |
| RGDP | -0.217 (0.163) | [-0.49, 0.06] |
| UNEM | -0.151 (0.209) | [-0.51, 0.21] |

### 2. c with and without the pandemic rows

*Descriptive, not preregistered.*
The first two rows are preregistered (the main test and S3); the rows by variable are added here. Putting back the 2020-2021 GDP and unemployment rows (40 rows) turns c positive, and the change comes from unemployment. The preregistration excluded these rows before seeing any data, because a handful of targets that moved by several points in one round outweigh two decades; even with them, c stays well below +0.40.

| sample | rows | c (se) | 90% interval |
|---|---|---|---|
| all variables, main sample (pandemic rows excluded; preregistered test) | 578 | -0.106 (0.090) | [-0.26, 0.05] |
| all variables, with the pandemic rows (preregistered S3) | 618 | +0.177 (0.077) | [0.04, 0.31] |
| HICP, with the pandemic rows | 206 | +0.127 (0.171) | [-0.17, 0.42] |
| RGDP, with the pandemic rows | 206 | -0.039 (0.145) | [-0.29, 0.21] |
| UNEM, with the pandemic rows | 206 | +0.577 (0.205) | [0.23, 0.93] |

### 3. Base under-reaction slope by variable and by period

*Descriptive, not preregistered.*
One constant per series (variable x horizon), no split by news size; 'pooled' is the preregistered positive control b_commun. Periods are of the target year (10, 10 and 6 target years).

| variable or period | rows | slope (se) | 90% interval |
|---|---|---|---|
| HICP | 206 | 0.374 (0.111) | [0.18, 0.56] |
| RGDP | 186 | 0.333 (0.137) | [0.10, 0.57] |
| UNEM | 186 | 0.389 (0.092) | [0.23, 0.55] |
| pooled | 578 | 0.366 (0.057) | [0.27, 0.46] |
| target years 2000-2009 (43 rounds) | 234 | 0.404 (0.085) | [0.26, 0.55] |
| target years 2010-2019 (44 rounds) | 240 | 0.318 (0.123) | [0.11, 0.53] |
| target years 2020-2025 (28 rounds) | 104 | 0.232 (0.096) | [0.07, 0.40] |

## Two surveys, two continents, the same answer

*Descriptive, not preregistered.*
Side by side, the quantities that decide or frame the two preregistered tests. Both consensus forecasts under-react on average (positive base slope; in the euro area the preregistered positive control passes), and in neither does the under-reaction grow after large news: both intervals for c contain 0 and exclude the predicted +0.40. The euro-area floor for the mechanical bias (0.43) is far above the 0.10 that the decisiveness simulation of its preregistration assumed (the variance ratio of revisions is 8.4, not about 3); that would have mattered for a survival, not for the elimination, which rests on the upper bound of c alone.

| quantity | US SPF (K20) | ECB SPF (K20-ZE) |
|---|---|---|
| rows in the main sample | 1004 | 578 |
| survey dates (clusters for the standard error) | 223 target quarters | 107 rounds, 26 target years |
| standard error; critical value of the 90% interval | Driscoll-Kraay, 4 lags; 1.645 | Driscoll-Kraay, 8 lags; 1.708 |
| base slope, no size split (one constant per series, one common slope) | 0.191 (se 0.047) | 0.366 (se 0.057) |
| base slope after small news (mean of the series' b) | 0.194 | 0.447 (se 0.087) |
| slope after large news (mean b + c) | 0.164 | 0.341 |
| **extra slope after large news, c (se)** | **-0.030** (0.071) | **-0.106** (0.090) |
| 90% interval of c | [-0.146, 0.086] | [-0.259, 0.047] |
| variance ratio of revisions, large / small news | 3.06 | 8.42 |
| k = s.d. revision / s.d. error (mean) | 0.294 | 0.427 |
| mechanical bias with 20% noise | 0.081 | 0.425 |
| mechanical-bias floor max(0.10, bias) | 0.100 | 0.425 |
| c without each episode (range) | -0.084 to 0.014 | -0.185 to -0.064 |
| effective observations | 820 | 735 |

The US base slope is the descriptive pooled slope of section K20.1; the euro-area one is the preregistered b_commun. Both have one constant per series and one common slope, in standardised units.

## Figures

1. `figures/fig1_slopes_small_vs_large_surprises.png`
2. `figures/fig2_c_without_each_episode.png`
3. `figures/fig3_sort_on_revision_vs_surprise.png`
4. `figures/fig4_base_slope_by_decade.png`
5. `figures/fig5_forest_c_us_vs_euro_area.png`
6. `figures/fig6_base_slope_vs_c_two_surveys.png`
