# Do inflation forecasters under-react to news?

**ECB staff projections, professional forecasters and the 2021-2023 surge.**

When a forecaster revises an inflation forecast up, does inflation end up even higher than the revised
forecast (under-reaction), or lower (over-reaction)? The standard measure is the slope of the forecast
error (outturn − forecast) on the forecast revision (new − old forecast for the same target): positive
means under-reaction. This project recomputes, from the raw public data, four tests of this question that
were preregistered, sealed and judged before this code was written (see [`audit/`](audit/README.md)):

| test | data | question |
|---|---|---|
| **J02** | ECB/Eurosystem staff projections (MPD), 2 quarters ahead, 108 targets 1999Q4-2026Q3 | Is the full-sample error-on-revision slope positive and as large as predicted (0.40)? |
| **H03-v2** | same, horizons 1-4, targets 2004-2025, real-time outturns | Could a correction rule estimated in real time on past errors have predicted the errors? |
| **K01** | ECB Survey of Professional Forecasters, individual forecasters, 2002-2025 | Do individuals over-react, once the mechanical bias is removed by an instrument? |
| **K20** | Philadelphia Fed SPF consensus, five variables, 1969-2026 | Does under-reaction grow after large surprises? |

## Run it

```
python run_all.py
```

Python 3.13 with numpy, pandas, scipy, statsmodels, matplotlib and openpyxl (pytest for the tests).
The first run downloads every raw file into `data/raw/` (about 220 requests; the ECB and Eurostat APIs are
intermittent, so each request is retried with growing waits) and later runs reuse that cache. A full run on
a warm cache takes about 15 seconds. Tests: `python -m pytest`.

`python run_all.py --seed <path to tests-de-mort>` fills empty cache slots by copying the raw files the
sealed tests downloaded (recorded as such in `data/raw/PROVENANCE.md`), which guarantees the same data
vintage as the sealed verdicts. Sources such as Eurostat are revised over time, so a fresh download may
differ slightly. Check made on 2026-11-13 with an empty cache (`IFU_RAW_DIR` pointing elsewhere): the code
re-downloaded the ECB SPF archive, both Eurostat files, the six Philadelphia Fed workbooks, the four FRED
series and the first 19 MPD vintages, all byte-identical to the seeded files; the remaining MPD requests were
slow that day (the ECB API was answering in minutes) and the check was stopped there.

## What each file does

| file | role |
|---|---|
| `run_all.py` | checks the seals of the preregistrations, gets the data, builds the four datasets, computes every preregistered field, applies each test's verdict rule, writes `results/` |
| `src/ifu/data.py` | download with on-disk cache and retries; catalogue of all source URLs; seeding from the sealed tests; `PROVENANCE.md` (URL, date, sha256, rows) |
| `src/ifu/vintages.py` | MPD vintages: letter codes (W = March, G = June, S = September, A = December, checked against `TITLE_COMPL`), quarter numbers, reading a value with a given status, real-time outturns |
| `src/ifu/measures.py` | errors and revisions; one `build_*` function per test returns its analysis dataset |
| `src/ifu/stats.py` | OLS, Newey-West / Driscoll-Kraay (Bartlett weights, lags in calendar time), just-identified 2SLS with first-stage F, block statistics, Diebold-Mariano-HLN, moving-block bootstrap — written from their formulas |
| `src/ifu/h03v2.py`, `j02.py`, `k01.py`, `k20.py` | one module per test: its schema checks, its primary statistic exactly as preregistered, its descriptive breakdowns |
| `src/ifu/figures.py` | the five figures |
| `tests/` | pytest: vintage letters against `TITLE_COMPL`, sign conventions, estimators against statsmodels and hand computations, and the acceptance test (all sealed numbers reproduce) |
| `audit/` | byte-for-byte copies of the sealed preregistrations, seals, verdicts, the K20 after-verdict reading and the record of the voided H03 run |
| `results/` | `results.json` (all fields), `RESULTS.md` (results and breakdowns), `reproduction.md` (sealed vs pipeline, field by field), `figures/` |

The analysis datasets (`data/processed/*.csv`) use English column names; each `build_*` docstring gives the
French name used in the preregistration. Result fields keep the preregistered (French) names, so that they
can be compared one to one with the sealed verdicts.

## Data sources

| source | URL | used by |
|---|---|---|
| ECB Macroeconomic Projection Database, quarterly HICP, one series per vintage | `https://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.<vintage>.0000?format=csvdata` | H03-v2, J02 |
| same, annual | `https://data-api.ecb.europa.eu/service/data/MPD/A.U2.HIC.A.<vintage>.0000?format=csvdata` | K01 |
| MPD series keys | `https://data-api.ecb.europa.eu/service/data/MPD?detail=serieskeysonly&format=csvdata` | check only |
| ECB SPF individual forecasts | `https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip` | K01 |
| Eurostat HICP monthly index (2015 = 100), euro area | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_minr/M.I15.TOTAL.EA?format=SDMX-CSV` | J02 |
| Eurostat HICP annual average rate, euro area | `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV` | K01 |
| Philadelphia Fed SPF mean and median forecasts (`meanGrowth`, `meanLevel`, `medianGrowth`, `medianLevel`.xlsx) | `https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/` | K20 |
| Philadelphia Fed real-time data set (`pQvQd.xlsx`, `routputQvQd.xlsx`) | `https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/` | K20 |
| FRED latest vintage: `UNRATE`, `CPIAUCSL`, `TB3MS` (and `USRECQP` for the episode windows) | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<series>` | K20 |
| ALFRED vintages (helper only, not used by the four tests) | `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<series>&vintage_date=<date>` | — |

## Results

All 149 sealed verifier numbers are reproduced within their preregistered tolerances
([`results/reproduction.md`](results/reproduction.md)); applying each preregistered rule to the pipeline's
numbers gives the sealed verdicts.

| test | primary statistic | 90% interval | verdict | what it means |
|---|---|---|---|---|
| J02 | standardised slope 0.44 (Newey-West se 0.20, t = 2.27) | [0.12, 0.76] | survives | ECB staff errors follow revisions over 1999-2026, but the slope is carried by 2021-2022: 0.05 without them, 0.14 without 2021-2023, 0.13 before 2020 |
| H03-v2 | mean block correlation 0.016 | [−0.074, 0.105] | eliminated | a rule estimated in real time would not have predicted the errors; the corrected projection does worse in a typical block (MSE ratio 1.10) |
| K01 | individual 2SLS slope +1.15 (Driscoll-Kraay se 0.46; first-stage F 514) | [0.36, 1.94] | eliminated | the predicted individual over-reaction (−0.15) is excluded; the naive within-round slope (−0.45) is the mechanical bias. Descriptive: consensus 0.92, ECB staff 0.77; without 2021-2023 the individual slope is 0.17 |
| K20 | extra slope after large surprises c = −0.03 (se 0.07) | [−0.15, 0.09] | inconclusive (schema guard) | one row (CPI 2026Q1) fails a schema check because October 2025 is missing at the source; the numbers show no extra under-reaction after large surprises (base slope 0.19) |

Details and descriptive breakdowns: [`results/RESULTS.md`](results/RESULTS.md). Figures:

1. `results/figures/fig1_ecb_error_vs_revision.png` — ECB staff errors against revisions, 2021-2023 marked, fits with and without them.
2. `results/figures/fig2_j02_leave_years_out.png` — the J02 correlation when each year, or each pair of consecutive years, is removed.
3. `results/figures/fig3_h03v2_blocks.png` — the H03-v2 block statistic by two-year block.
4. `results/figures/fig4_k01_slopes.png` — individual 2SLS vs naive slopes vs consensus and ECB staff, with and without 2021-2023.
5. `results/figures/fig5_k20_by_variable.png` — K20 slopes after small vs large surprises, by variable.
