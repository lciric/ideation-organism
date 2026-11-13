# Does forecasters' under-reaction grow with the size of news?

**Evidence from 58 years of the US Survey of Professional Forecasters.**

When the consensus of professional forecasters revises a forecast up, does the outcome end up even higher
than the revised forecast? A positive slope of the forecast error (outturn − forecast) on the forecast
revision (new − older forecast, same target) means the consensus **under-reacts** to news (Coibion and
Gorodnichenko 2015). This project asks whether that under-reaction is **stronger after large news**: is
the slope steeper in quarters that follow a large surprise in the data?

The answer rests on one test, **K20**, preregistered and sealed before any statistic was computed, then run
by an experimenter and an independent verifier (see [`audit/`](audit/README.md)). This project recomputes
that test from the raw public data, checks every sealed number, and adds descriptive analyses, each marked
*descriptive, not preregistered*.

## Run it

```
python run_all.py
```

Python 3.13 with numpy, pandas, scipy, statsmodels, matplotlib and openpyxl (pytest for the tests). The
first run downloads the ten raw files into `data/raw/` (curl's user agent, retries with growing waits:
FRED sometimes returns empty bodies, the Philadelphia Fed site can be slow); later runs reuse that cache.
A full run on a warm cache takes about 30 seconds. Tests: `python -m pytest`.

`python run_all.py --seed <path to tests-de-mort/K20/donnees>` fills empty cache slots by copying the raw
files the sealed test downloaded on 2026-11-12 (recorded as such in `data/raw/PROVENANCE.md`), which
guarantees the same data vintage as the sealed verdict. The cache in this folder was seeded that way. Check
made on 2026-11-13: with an empty cache (`SNU_RAW_DIR` pointing elsewhere) the code downloaded all ten
files again, each on the first attempt, and all ten were byte-identical to the seeded ones.

## What each file does

| file | role |
|---|---|
| `run_all.py` | checks the seal of the preregistration, gets the data, builds the analysis dataset, computes the 53 preregistered fields and the verdict the sealed rule gives, runs the descriptive analyses and the simulation, writes `results/` |
| `src/snu/data.py` | download with on-disk cache and retries; catalogue of the source URLs, grouped by test; seeding from the sealed test; `PROVENANCE.md` (URL, origin, date, sha256, rows) |
| `src/snu/measures.py` | quarter numbers, sign conventions (error, revision, surprise), first releases from the real-time data set, FRED quarterly means; `build_k20()` returns the 1 038-row analysis dataset |
| `src/snu/stats.py` | OLS, Driscoll-Kraay / Newey-West covariances (Bartlett weights, lags in calendar time), classical covariance, linear combinations — written from their formulas |
| `src/snu/k20.py` | the preregistered test: 12 schema checks, standardisation, the regression, the 53 fields |
| `src/snu/descriptive.py` | descriptive analyses (not preregistered): base slope by variable, pooled, before 2020 and by decade; slopes after small and large surprises; c by episode removed; c under other definitions of "large" |
| `src/snu/simulation.py` | simulated panels with no true size effect but noisy consensus forecasts: sorting on the revision vs on the lagged surprise |
| `src/snu/figures.py` | the four figures |
| `tests/` | estimators against statsmodels and hand computations; sign conventions and definitions; acceptance (all 53 sealed numbers, the sealed verdict, the single schema failure and its irrelevance to the estimate); the simulation test |
| `audit/` | byte-for-byte copies of K20's preregistration, seal, verdict and after-verdict reading, and an English explanation |
| `data/raw/` | raw-data cache (not tracked by git; `PROVENANCE.md` is) |
| `data/processed/K20_analysis.csv` | the analysis dataset (re-created by `run_all.py`, not tracked) |
| `results/` | `results.json` (all numbers), `RESULTS.md` (results and descriptive analyses), `reproduction.md` (sealed vs pipeline, field by field), `figures/` |

The analysis dataset uses English column names; the docstring of `build_k20` gives the French names of the
preregistration. Result fields keep the preregistered (French) names, so that they compare one to one with
the sealed verdict.

## Data sources

| source | URL | content |
|---|---|---|
| Philadelphia Fed, Survey of Professional Forecasters: mean and median forecasts (`meanGrowth.xlsx`, `meanLevel.xlsx`, `medianGrowth.xlsx`, `medianLevel.xlsx`) | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/ | forecasts of the current quarter and of 3 and 4 quarters ahead, surveys 1968Q4-2026Q3 |
| Philadelphia Fed, Real-Time Data Set for Macroeconomists (`pQvQd.xlsx`, `routputQvQd.xlsx`) | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/ | every vintage of the GDP (GNP) deflator and real output, for first releases |
| FRED, latest vintage: `UNRATE`, `CPIAUCSL`, `TB3MS` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE (same pattern for each series) | outturns of unemployment, CPI and the 3-month T-bill rate |
| FRED `USRECQP` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=USRECQP | NBER recession quarters, to check the episode windows only |

## Results

All 53 sealed verifier numbers are reproduced within their preregistered tolerances
([`results/reproduction.md`](results/reproduction.md)); the sealed rule applied to the pipeline's numbers
gives "non concluant" again, as sealed. Full tables: [`results/RESULTS.md`](results/RESULTS.md).

| quantity | estimate | 90% interval | status |
|---|---|---|---|
| **extra slope after large surprises, c** (K20 primary statistic; predicted +0.40) | **−0.030** (se 0.071) | [−0.146, 0.086] | preregistered |
| K20 verdict | **non concluant** | — | one schema check fails on a row (CPI 2026-Q1) that enters no regression; with that check set aside the rule would give "éliminée" |
| base slope after small surprises (mean of five) / after large surprises | 0.194 / 0.164 | [0.10, 0.29] / [0.09, 0.24] | preregistered fields; intervals descriptive |
| base under-reaction slope, pooled, no size split: full sample / before 2020 | 0.191 / 0.171 | [0.11, 0.27] / [0.09, 0.25] | descriptive, not preregistered |
| c by variable: GDP deflator, real GDP, unemployment, CPI, T-bill | +0.17, −0.05, −0.10, +0.05, −0.31 | se 0.15-0.18 each | preregistered secondary S1 |
| c with each episode window removed | −0.08 to +0.01 | — | preregistered guard |
| c when "large" = top third of \|revision\| / \|revision\| > 1 s.d. | +0.116 / −0.003 | [−0.07, 0.31] / [−0.14, 0.14] | descriptive / preregistered secondary S7 |
| simulated panels with no size effect: c with the revision sort / the surprise sort | +0.046 / −0.003 (mean of 300 panels of 1 000 rows) | 5-95%: [−0.11, 0.21] / [−0.16, 0.16] | descriptive (simulation) |
| pooled base slope by decade: 1970s, 1980s, 1990s, 2000s, 2010s, 2020-26 | 0.06, 0.06, 0.15, 0.32, 0.01, 0.16 | only 1990s and 2000s exclude 0 | descriptive, not preregistered |

In words: the US consensus under-reacts on average (slope about 0.19 s.d. of error per s.d. of revision),
but not more after large surprises: the extra slope is close to zero, and no episode or variable shows a
clear positive one. The base under-reaction itself is not stable over time.

Figures (`results/figures/`):

1. `fig1_slopes_small_vs_large_surprises.png` — slope after small vs large surprises, by variable and pooled.
2. `fig2_c_without_each_episode.png` — c with each episode window removed.
3. `fig3_sort_on_revision_vs_surprise.png` — c under the preregistered sort and under sorts on the revision (data), beside the simulation.
4. `fig4_base_slope_by_decade.png` — pooled base slope by decade.

## Planned extension

A blind euro-area replication (test **K20-ZE**) is being preregistered and will be added: a new module in
`src/snu/` (its dataset builder and preregistered statistic, reusing `stats.py` and `descriptive.py`), a
new group of files in `data.CATALOGUES`, a new entry in `run_all.STUDIES`, its sealed records in
`audit/K20-ZE/`, and a new section in `results/RESULTS.md` and `results/reproduction.md`.
