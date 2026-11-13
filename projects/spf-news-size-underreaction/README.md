# Does forecasters' under-reaction grow with the size of news?

**Evidence from two surveys of professional forecasters: the US (1969-2026) and the euro area (2000-2025).**

When the consensus of professional forecasters revises a forecast up, does the outcome end up even higher
than the revised forecast? A positive slope of the forecast error (outturn − forecast) on the forecast
revision (new − older forecast, same target) means the consensus **under-reacts** to news (Coibion and
Gorodnichenko 2015). This project asks whether that under-reaction is **stronger after large news**: is
the slope steeper after a large surprise in the data?

The answer rests on two tests, each preregistered and sealed before any statistic was computed, then run
by an experimenter and an independent verifier (see [`audit/`](audit/README.md)):

- **K20**, on the Philadelphia Fed Survey of Professional Forecasters: five variables, quarterly targets
  1969-2026;
- **K20-ZE**, a blind replication on the ECB Survey of Professional Forecasters: three variables, annual
  targets 2000-2025, written after K20's result but before any euro-area statistic.

This project recomputes both tests from the raw public data, checks every sealed number, and adds
descriptive analyses, each marked *descriptive, not preregistered*.

## What the project establishes

Two surveys, two continents, the same answer. **The consensus under-reacts on average, and the
under-reaction does not grow after large news.**

- US: base slope 0.19 (90% interval [0.11, 0.27]); extra slope after large surprises c = −0.03
  ([−0.15, 0.09]). The sealed verdict is "non concluant" only because a schema check failed on one row
  that enters no regression; under the same rule the numbers would have given "éliminée".
- Euro area: base slope 0.37 ([0.27, 0.46]; the preregistered positive control passes); c = −0.11
  ([−0.26, 0.05]). Verdict: **éliminée**: the predicted +0.40 is excluded.
- In neither survey does a variable or the removal of an episode give a clear positive c. One exception
  is shown plainly: in the euro area, putting back the 2020-2021 GDP and unemployment rows, which the
  preregistration excluded, gives c = +0.18 (se 0.08), driven by unemployment. That is still far below
  +0.40.
- Sorting "large" on the revision itself, as the original card did, mixes in consensus noise. The
  simulation shows this sort creates a positive c when the true slope does not depend on news size.

## Run it

```
python run_all.py
```

Python 3.13 with numpy, pandas, scipy, statsmodels, matplotlib and openpyxl (pytest for the tests). The
first run downloads the 14 raw files into `data/raw/` (curl's user agent, retries with growing waits:
FRED sometimes returns empty bodies, the Philadelphia Fed site can be slow); later runs reuse that cache.
A full run on a warm cache takes about 35 seconds. Tests: `python -m pytest`.

`python run_all.py --seed <path to tests-de-mort>` fills empty cache slots by copying the raw files the
sealed tests downloaded (`<ID>/donnees/`; recorded as such in `data/raw/PROVENANCE.md`). Checks made on
2026-11-13:
- K20's ten files were seeded that way. With an empty cache (`SNU_RAW_DIR` pointing elsewhere), the code
  downloaded all ten again, each on the first attempt, and all ten were byte-identical to the seeded files.
- K20-ZE's four files were downloaded by the code. Each is byte-identical to the sealed test's copy.
- `data/raw/PROVENANCE.md` has a "same as sealed" column, recomputed at every run.

## What each file does

| file | role |
|---|---|
| `run_all.py` | checks the seal of each preregistration, gets the data, builds each analysis dataset, computes every preregistered field and the verdict each sealed rule gives, runs the descriptive analyses and the simulation, compares the two surveys, writes `results/` |
| `src/snu/data.py` | download with on-disk cache and retries; catalogue of the source URLs, grouped by test; seeding from the sealed tests and sha256 comparison with their copies; `PROVENANCE.md` |
| `src/snu/measures.py` | US data: quarter numbers, sign conventions (error, revision, surprise), first releases from the real-time data set, FRED quarterly means; `build_k20()` returns the 1 038-row analysis dataset |
| `src/snu/stats.py` | OLS, Driscoll-Kraay / Newey-West covariances (Bartlett weights, lags in calendar time), clustered and classical covariances, linear combinations — written from their formulas |
| `src/snu/k20.py` | the US test: 12 schema checks, standardisation, the regression, the 53 fields |
| `src/snu/k20ze.py` | the euro-area test: reading the ECB SPF archive and Eurostat, `build_k20ze()` (624 rows), 12 schema checks scoped to the rows in the computation, the tie-aware cut, the regression with six series and 8 lags, the positive control, the 65 fields |
| `src/snu/descriptive.py` | descriptive analyses (not preregistered): base slopes by variable, period and decade; slopes after small and large news; c by episode removed, by sort variable, with and without the pandemic rows; the US / euro-area comparison table |
| `src/snu/simulation.py` | simulated panels with no true size effect but noisy consensus forecasts: sorting on the revision vs on the lagged surprise |
| `src/snu/figures.py` | the six figures |
| `tests/` | estimators against statsmodels and hand computations; sign conventions and definitions; acceptance for K20 (53 sealed numbers, sealed verdict, the single schema failure and its irrelevance to the estimate) and for K20-ZE (65 sealed numbers, sealed verdict, schema, dataset bit-identical to the sealed analysis file); unit tests of the tie-aware cut, reference periods and episode membership; the simulation test |
| `audit/` | byte-for-byte copies of both tests' sealed records, and an English explanation |
| `data/raw/` | raw-data cache (not tracked by git; `PROVENANCE.md` is) |
| `data/processed/` | the analysis datasets `K20_analysis.csv`, `K20-ZE_analysis.csv` (re-created by `run_all.py`, not tracked) |
| `results/` | `results.json` (all numbers), `RESULTS.md` (results and descriptive analyses), `reproduction.md` (sealed vs pipeline, field by field), `figures/` |

The analysis datasets use English column names; the docstrings of `build_k20` and `build_k20ze` give the
French names of the preregistrations. Result fields keep the preregistered (French) names, so that they
compare one to one with the sealed verdicts.

## Data sources

| source | URL | content | test |
|---|---|---|---|
| Philadelphia Fed, Survey of Professional Forecasters: mean and median forecasts (`meanGrowth.xlsx`, `meanLevel.xlsx`, `medianGrowth.xlsx`, `medianLevel.xlsx`) | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/ | forecasts of the current quarter and of 3 and 4 quarters ahead, surveys 1968Q4-2026Q3 | K20 |
| Philadelphia Fed, Real-Time Data Set for Macroeconomists (`pQvQd.xlsx`, `routputQvQd.xlsx`) | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/ | every vintage of the GDP (GNP) deflator and real output, for first releases | K20 |
| FRED, latest vintage: `UNRATE`, `CPIAUCSL`, `TB3MS` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE (same pattern for each series) | outturns of unemployment, CPI and the 3-month T-bill rate | K20 |
| FRED `USRECQP` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=USRECQP | NBER recession quarters, to check the episode windows only | K20 |
| ECB Survey of Professional Forecasters, individual answers (`SPF_microdata_by_variable.zip`; root copies of `1_HICP.csv`, `3_RGDP.csv`, `5_UNEM.csv`) | https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip | point forecasts for the current and next calendar years, rolling one-year-ahead forecasts, and the reference value sent to forecasters each round, 1999Q1-2026Q4 | K20-ZE |
| Eurostat, HICP annual average rate of change, euro area | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV | inflation outturns | K20-ZE |
| Eurostat, real GDP growth (chain-linked volumes), euro area | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_gdp/A.CLV_PCH_PRE.B1GQ.EA?format=SDMX-CSV | GDP outturns | K20-ZE |
| Eurostat, monthly unemployment rate, EA21 | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/une_rt_m/M.NSA.TOTAL.PC_ACT.T.EA21?format=SDMX-CSV | unemployment outturns (mean of the 12 months) | K20-ZE |

## Results

All 53 K20 and all 65 K20-ZE sealed verifier numbers are reproduced within their preregistered tolerances
([`results/reproduction.md`](results/reproduction.md)). Applying each sealed rule to the pipeline's
numbers gives the sealed verdicts again: "non concluant" for K20 and "éliminée" for K20-ZE. Full tables:
[`results/RESULTS.md`](results/RESULTS.md).

| quantity | US SPF (K20) | ECB SPF (K20-ZE) | status |
|---|---|---|---|
| **extra slope after large news, c** (predicted +0.40) | **−0.030** (se 0.071) | **−0.106** (se 0.090) | preregistered primary statistic |
| 90% interval of c | [−0.146, 0.086] | [−0.259, 0.047] | preregistered (critical values 1.645 / 1.708) |
| verdict | **non concluant** (a schema check fails on one row that enters no regression; with it set aside: "éliminée") | **éliminée** (upper bound < 0.40) | sealed rule |
| base slope, no size split | 0.191 [0.11, 0.27] | 0.366 [0.27, 0.46] | US descriptive; euro area preregistered positive control |
| slope after small / after large news | 0.194 / 0.164 | 0.447 / 0.341 | preregistered |
| c by variable | deflator +0.17, real GDP −0.05, unemployment −0.10, CPI +0.05, T-bill −0.31 | HICP +0.13, real GDP −0.22, unemployment −0.15 | preregistered secondary S1 |
| c with each episode removed | −0.08 to +0.01 | −0.19 to −0.06 | preregistered guard |
| c with the pandemic rows put back | −0.095 (se 0.074) | **+0.177** (se 0.077), driven by unemployment (+0.58) | preregistered S3; by variable descriptive |
| variance ratio of revisions, large / small news | 3.06 | 8.42 | preregistered |
| mechanical-bias floor | 0.10 | 0.43 | preregistered |
| c when "large" = \|revision\| > 1 s.d. (the card's sort) | −0.003 | −0.229 | preregistered secondary S7 |
| base slope by period | 1970s 0.06, 1980s 0.06, 1990s 0.15, 2000s 0.32, 2010s 0.01, 2020-26 0.16 | 2000-09 0.40, 2010-19 0.32, 2020-25 0.23 | descriptive, not preregistered |

The euro-area floor (0.43) is far above the 0.10 that the decisiveness simulation of its preregistration
assumed. That simulation was calibrated on K20's variance ratio of about 3; the observed ratio is 8.4. A
high floor would have prevented a survival. It does not touch the elimination, which comes from the upper
bound of c alone.

Simulation (descriptive): in panels with no true size effect, sorting on |revision| > 1 s.d. gives a mean c
of +0.046, and sorting on the lagged surprise gives −0.003 (300 panels of 1 000 rows).

Figures (`results/figures/`):

1. `fig1_slopes_small_vs_large_surprises.png` — US: slope after small vs large surprises, by variable and pooled.
2. `fig2_c_without_each_episode.png` — US: c with each episode window removed.
3. `fig3_sort_on_revision_vs_surprise.png` — US: c under the preregistered sort and under sorts on the revision (data), beside the simulation.
4. `fig4_base_slope_by_decade.png` — US: pooled base slope by decade.
5. `fig5_forest_c_us_vs_euro_area.png` — c with 90% intervals, pooled and by variable, for both surveys, with the 0 and +0.40 lines.
6. `fig6_base_slope_vs_c_two_surveys.png` — base under-reaction slope beside c, for both surveys.

## Next study

A third replication, **K20-LIV** on the US Livingston Survey, is being preregistered. It is not run here
and none of its numbers appear anywhere in this project. Adding it means:
- a new module `src/snu/k20liv.py`, with its dataset builder and preregistered statistic, reusing `stats.py`
  and `descriptive.py`;
- a new group of files in `data.CATALOGUES` and `data.SEALED_NAMES`;
- a `run_k20liv()` function, set in the commented `STUDIES` entry of `run_all.py`;
- its sealed records in `audit/K20-LIV/`;
- a new section in `results/RESULTS.md` and `results/reproduction.md`, and a third column in the comparison.
