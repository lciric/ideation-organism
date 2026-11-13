# Does forecasters' under-reaction grow with the size of news?

**Evidence from three surveys of professional forecasters on two continents, 1947-2026: the US Survey of
Professional Forecasters, the ECB Survey of Professional Forecasters and the US Livingston Survey.**

When the consensus of professional forecasters revises a forecast up, does the outcome end up even higher
than the revised forecast? A positive slope of the forecast error (outturn − forecast) on the forecast
revision (new − older forecast, same target) means the consensus **under-reacts** to news (Coibion and
Gorodnichenko 2015). This project asks whether that under-reaction is **stronger after large news**: is
the slope steeper after a large surprise in the data?

The answer rests on three tests. Each was preregistered and sealed before any statistic was computed, then
run by an experimenter and an independent verifier (see [`audit/`](audit/README.md)):

- **K20**, on the Philadelphia Fed Survey of Professional Forecasters (US SPF): five variables, quarterly
  targets 1969-2026;
- **K20-ZE**, a blind replication on the ECB Survey of Professional Forecasters (ECB SPF): three variables,
  annual targets 2000-2025;
- **K20-LIV**, a blind replication on the Livingston Survey (Philadelphia Fed): five variables, June and
  December targets 1947-2026.

This project recomputes the three tests from the raw public data, checks every sealed number, and adds
descriptive analyses, each marked *descriptive, not preregistered*.

## What the project establishes

Three surveys, two continents, 1947-2026, the same answer: **under-reaction yes, size-dependence no.**

- **Under-reaction yes.** Every consensus under-reacts on average: the base slope of error on revision is
  0.19 (US SPF), 0.37 (ECB SPF) and 0.37 (Livingston), in standard deviations of error per standard
  deviation of revision. The two replications included a preregistered positive control, and both passed.
- **Size-dependence no.** The extra slope after large news is c = −0.03 (US SPF), −0.11 (ECB SPF) and
  −0.12 (Livingston). Every 90% interval contains 0. The predicted +0.40 is excluded in both conclusive
  tests, which are eliminated.
- **Robustness.** No episode removed and no variable gives a clear positive c, with one lead noted below.

Honest notes:
- **K20 itself is inconclusive by its own rule.** A schema check failed on one row (CPI 2026-Q1) that enters
  no regression. Under the same rule, its numbers would have given "éliminée".
- **The ECB SPF floor was higher than simulated.** The mechanical-bias floor came out at 0.43, against the
  0.10 that the preregistration's decisiveness simulation assumed. That would have blocked a survival; the
  elimination comes from the upper bound of c, which the floor does not enter.
- **The Livingston dispersions were the writer's scenario S-b.** Level targets gave k ≈ 1 and a variance
  ratio of 10, not K20's 0.3 and 3. In that scenario the preregistration expected to eliminate a null effect
  only 78% of the time. The positive control passed and the test decided. Its floor was measured from the
  individual answers (noise share 0.016, doubled), not assumed.
- **A lead, not a result.** In the euro area, putting back the 2020-2021 GDP and unemployment rows, which
  the preregistration excluded, gives c = +0.18 (se 0.08), driven by unemployment. In the Livingston Survey,
  unemployment is the only variable with a positive c (+0.38, se 0.29). This pattern was noticed after the
  verdicts, on one variable.
- **The sort matters.** Sorting "large" on the revision itself, as the original card did, mixes in consensus
  noise. The simulation shows this sort creates a positive c when the true slope does not depend on news
  size.

## Run it

```
python run_all.py
```

Python 3.13 with numpy, pandas, scipy, statsmodels, matplotlib and openpyxl (pytest for the tests).
- **Data.** The first run downloads the 24 raw files into `data/raw/` with curl's user agent and retries
  with growing waits: FRED sometimes returns empty bodies, and the Philadelphia Fed site can be slow. Later
  runs reuse that cache.
- **Time.** A full run on a warm cache takes about 35 seconds.
- **Tests.** `python -m pytest`.

`python run_all.py --seed <path to tests-de-mort>` fills empty cache slots by copying the raw files the
sealed tests downloaded (`<ID>/donnees/`); `data/raw/PROVENANCE.md` records each copy. Checks made on
2026-11-13:
- K20's ten files were seeded that way. A re-download into an empty cache gave ten byte-identical files.
- K20-ZE's four files and K20-LIV's ten other files were downloaded by the code. All are byte-identical
  (sha256) to the sealed tests' copies.
- The two FRED files K20-LIV shares with K20 (CPIAUCSL, UNRATE) are identical to K20-LIV's copies as well.
- `data/raw/PROVENANCE.md` has a "same as sealed" column, recomputed at every run.

## What each file does

| file | role |
|---|---|
| `run_all.py` | checks the seal of each preregistration, gets the data, builds each analysis dataset, computes every preregistered field and the verdict each sealed rule gives, runs the descriptive analyses and the simulation, compares the three surveys, writes `results/` |
| `src/snu/data.py` | download with on-disk cache and retries; catalogue of the source URLs, grouped by test; seeding from the sealed tests and sha256 comparison with their copies; `PROVENANCE.md` |
| `src/snu/measures.py` | US SPF data: quarter numbers, sign conventions (error, revision, surprise), first releases from the real-time data set, FRED quarterly means; `build_k20()` returns the 1 038-row analysis dataset |
| `src/snu/stats.py` | OLS, Driscoll-Kraay / Newey-West covariances (Bartlett weights, lags in calendar time), clustered and classical covariances, linear combinations — written from their formulas |
| `src/snu/k20.py` | the US SPF test: 12 schema checks, standardisation, the regression, the 53 fields |
| `src/snu/k20ze.py` | the ECB SPF test: reading the archive and Eurostat, `build_k20ze()` (624 rows), schema checks scoped to the rows in the computation, the tie-aware cut, six series and 8 lags, the positive control, the 65 fields |
| `src/snu/k20liv.py` | the Livingston test: reading the mean, median and individual answers and FRED, `build_k20liv()` (555 rows; CPI rebased with the questionnaire's base value; surprise on the expected path), schema checks on the main rows, the measured noise share and floor, the positive control, the 63 fields |
| `src/snu/descriptive.py` | descriptive analyses (not preregistered): base slopes by variable, period and decade; slopes after small and large news; c by episode removed, by sort variable, by sample; the three-survey comparison table |
| `src/snu/simulation.py` | simulated panels with no true size effect but noisy consensus forecasts: sorting on the revision vs on the lagged surprise |
| `src/snu/figures.py` | the six figures |
| `tests/` | see the list below |
| `audit/` | byte-for-byte copies of the three tests' sealed records, and an English explanation |
| `data/raw/` | raw-data cache (not tracked by git; `PROVENANCE.md` is) |
| `data/processed/` | `K20_analysis.csv`, `K20-ZE_analysis.csv`, `K20-LIV_analysis.csv` (re-created by `run_all.py`, not tracked) |
| `results/` | `results.json` (all numbers), `RESULTS.md` (results and descriptive analyses), `reproduction.md` (sealed vs pipeline, field by field), `figures/` |

The tests in `tests/` cover:
- the estimators against statsmodels and hand computations;
- sign conventions and definitions;
- acceptance for each test: every sealed number and the sealed verdict;
- for K20, the single schema failure and its irrelevance to the estimate;
- for K20-ZE and K20-LIV, the schema checks and a dataset bit-identical to the sealed analysis file;
- unit tests of the tie-aware cut, reference periods, episode membership, the Livingston surprise and the
  CPI rebasing;
- the simulation test.

The analysis datasets use English column names; the docstrings of `build_k20`, `build_k20ze` and
`build_k20liv` give the French names of the preregistrations. Result fields keep the preregistered
(French) names, so that they compare one to one with the sealed verdicts.

## Data sources

| source | URL | content | test |
|---|---|---|---|
| Philadelphia Fed, Survey of Professional Forecasters: mean and median forecasts (`meanGrowth.xlsx`, `meanLevel.xlsx`, `medianGrowth.xlsx`, `medianLevel.xlsx`) | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/ | forecasts of the current quarter and of 3 and 4 quarters ahead, surveys 1968Q4-2026Q3 | K20 |
| Philadelphia Fed, Real-Time Data Set for Macroeconomists (`pQvQd.xlsx`, `routputQvQd.xlsx`) | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/ | every vintage of the GDP (GNP) deflator and real output, for first releases | K20 |
| FRED, latest vintage: `UNRATE`, `CPIAUCSL`, `TB3MS` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE (same pattern for each FRED series) | outturns of unemployment, CPI and the 3-month T-bill rate | K20 (UNRATE and CPIAUCSL also K20-LIV) |
| FRED `USRECQP` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=USRECQP | NBER recession quarters, to check the episode windows only | K20 |
| ECB Survey of Professional Forecasters, individual answers (`SPF_microdata_by_variable.zip`; root copies of `1_HICP.csv`, `3_RGDP.csv`, `5_UNEM.csv`) | https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip | point forecasts for the current and next calendar years, rolling one-year-ahead forecasts, and the reference value sent to forecasters each round, 1999Q1-2026Q4 | K20-ZE |
| Eurostat, HICP annual average rate of change, euro area | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV | inflation outturns | K20-ZE |
| Eurostat, real GDP growth (chain-linked volumes), euro area | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_gdp/A.CLV_PCH_PRE.B1GQ.EA?format=SDMX-CSV | GDP outturns | K20-ZE |
| Eurostat, monthly unemployment rate, EA21 | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/une_rt_m/M.NSA.TOTAL.PC_ACT.T.EA21?format=SDMX-CSV | unemployment outturns (mean of the 12 months) | K20-ZE |
| Philadelphia Fed, Livingston Survey: `means.xlsx`, `medians.xlsx`, `individualdata.xlsx`, and the documentation | https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/livingston-survey/historical-data/ (documentation: `.../livingston-survey/livingston-documentation.pdf`) | mean, median and individual 6- and 12-month-ahead forecasts and base values, surveys 1946-06 to 2026-06 | K20-LIV |
| FRED, latest vintage: `CPIAUCNS`, `DPRIME`, `DTB3`, `HOUST` (and `USRECP`, `USREC` for the episode windows) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCNS (same pattern) | outturns of the CPI (not seasonally adjusted until the survey of June 2004), prime rate, 3-month bill, housing starts | K20-LIV |

## Results

Every sealed verifier number is reproduced within its preregistered tolerance: 53 of 53 for K20, 65 of 65
for K20-ZE and 63 of 63 for K20-LIV ([`results/reproduction.md`](results/reproduction.md)). Applying each
sealed rule to the pipeline's numbers gives the sealed verdicts again: "non concluant", "éliminée" and
"éliminée". Full tables: [`results/RESULTS.md`](results/RESULTS.md).

| quantity | US SPF (K20) | ECB SPF (K20-ZE) | Livingston (K20-LIV) | status |
|---|---|---|---|---|
| **extra slope after large news, c** (predicted +0.40) | **−0.030** (se 0.071) | **−0.106** (se 0.090) | **−0.122** (se 0.139) | preregistered primary statistic |
| 90% interval of c | [−0.146, 0.086] | [−0.259, 0.047] | [−0.351, 0.107] | preregistered (critical values 1.645 / 1.708 / 1.645) |
| verdict | **non concluant** (schema guard on a row outside every regression; with it set aside, "éliminée") | **éliminée** | **éliminée** | sealed rule |
| base slope, no size split | 0.191 [0.11, 0.27] | 0.366 [0.27, 0.46] | 0.373 [0.26, 0.48] | US descriptive; the replications' preregistered positive controls |
| slope after small / after large news | 0.194 / 0.164 | 0.447 / 0.341 | 0.443 / 0.321 | preregistered |
| c by variable | deflator +0.17, real GDP −0.05, unemployment −0.10, CPI +0.05, T-bill −0.31 | HICP +0.13, real GDP −0.22, unemployment −0.15 | CPI −0.22, unemployment **+0.38**, prime −0.44, T-bill −0.03, housing −0.47 | preregistered secondary S1 |
| c with each episode removed | −0.08 to +0.01 | −0.19 to −0.06 | −0.13 to −0.06 | preregistered guard |
| c with the pandemic rows put back | −0.095 (se 0.074) | **+0.177** (se 0.077), from unemployment (+0.58) | −0.320 (se 0.149) | preregistered S3; ECB breakdown descriptive |
| c since 1985 | −0.067 | — | −0.039 | preregistered S4 |
| variance ratio of revisions, large / small news | 3.06 | 8.42 | 10.10 | preregistered |
| k = s.d. revision / s.d. error | 0.29 | 0.43 | 1.02 | preregistered |
| noise share nu; mechanical-bias floor | assumed 0.20; 0.10 | assumed 0.20; 0.43 | measured 0.016 (doubled); 0.12 | preregistered |
| base slope over time | 1970s 0.06, 1980s 0.06, 1990s 0.15, 2000s 0.32, 2010s 0.01, 2020-26 0.16 | 2000-09 0.40, 2010-19 0.32, 2020-25 0.23 | — | descriptive, not preregistered |

Simulation (descriptive): in panels with no true size effect, sorting on |revision| > 1 s.d. gives a mean c
of +0.046, and sorting on the lagged surprise gives −0.003 (300 panels of 1 000 rows).

Figures (`results/figures/`):

1. `fig1_slopes_small_vs_large_surprises.png` — US SPF: slope after small vs large surprises, by variable and pooled.
2. `fig2_c_without_each_episode.png` — US SPF: c with each episode window removed.
3. `fig3_sort_on_revision_vs_surprise.png` — US SPF: c under the preregistered sort and under sorts on the revision (data), beside the simulation.
4. `fig4_base_slope_by_decade.png` — US SPF: pooled base slope by decade.
5. `fig5_forest_c_three_surveys.png` — c with 90% intervals, pooled and by variable, for the three surveys, with the 0 and +0.40 lines.
6. `fig6_base_slope_vs_c_three_surveys.png` — base under-reaction slope beside c, for each survey.

## Adding a study

A further replication is added in five steps:
- a module `src/snu/<id>.py`, with its dataset builder and preregistered statistic, reusing `stats.py`,
  `k20.regress` and `descriptive.py`;
- a group of files in `data.CATALOGUES` and `data.SEALED_NAMES`;
- a `run_<id>()` function and its entry in `run_all.STUDIES`;
- its sealed records in `audit/<ID>/`;
- a column in `descriptive.comparison` and a block in figures 5 and 6.
