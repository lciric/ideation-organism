# Price pressure around U.S. Treasury auctions: did it disappear after 2021, or did the measure change?

When the Treasury reopens a 10-, 20- or 30-year bond, dealers must absorb new supply: the bond's yield tends to
rise in the days before the auction and fall back after it (an inverted V). Measured against the Treasury's own
yield curve, this pattern is clear in 2010-2021 and gone in 2022-2026. But the Treasury changed the method behind
that curve on 6 December 2021. This project asks whether the pressure disappeared from the market or only from
the measure, through four tests whose rules were sealed before their data were read (see `audit/README.md`).

This repository is a clean, reproducible pipeline: from raw public data it rebuilds the four analysis datasets,
recomputes each preregistered statistic, and checks every number against the sealed verifier values.

## Run it

```
python run_all.py          # about 30 s with the cache; about 1 h from an empty cache (921 FedInvest pages)
python -m pytest tests     # unit tests
```

Requirements: Python 3.13 with numpy, pandas, scipy, statsmodels, matplotlib (pytest for the tests). Network
access is needed only for files missing from `data/raw/`. `run_all.py` exits with status 1 if a preregistration
fails its sha256 check or a verifier number does not reproduce within its preregistered tolerance.

## Results

| Test | Measure | Primary statistic (bp) | Sealed verdict | Reproduced |
|---|---|---|---|---|
| F04 | V against the Treasury curve: E = CMT yield - Fed GSW par yield, 321 reopenings 2010-2026 | mean V = 0.91, SE 0.16, t = 5.6 | survives | 10/10 fields |
| F04-bis | Same V on the 23 fiscal-2021 reopenings, old (HS) vs new (MC) Treasury method | D = V_HS - V_MC = 0.78, 95% CI [0.45, 1.12] | inconclusive | 12/12 fields |
| J05 | Concession K: auction yield vs the bond on the GSW curve, net of its own J-5 spread (FedInvest prices) | K 0.68 (2010-21) -> 1.10 (2022-26); decline -0.66, 90% CI [-1.27, -0.04] | inconclusive (schema guard) | 14/14 fields |
| K11 | V against three matched off-the-run control bonds, FedInvest prices, no curve | V after 2021 = -0.01, 90% CI [-0.11, 0.09]; before = -0.03 | inconclusive (instrument mute) | 24/24 fields |

In short: the Treasury-curve pressure (1.38 bp before 2022, 0.05 bp after; descriptive split) is about half
explained, on the one year where both are available, by the curve-method change alone (0.78 bp); measured on
market prices against the Fed's curve, the concession did not fall after 2021; the control-bond instrument sees
nothing in either period. Full tables: `results/RESULTS.md`; number-by-number check: `results/reproduction.md`.

## What each file does

| Path | Role |
|---|---|
| `run_all.py` | Checks the sealed preregistrations' sha256, downloads or reuses the data, builds the four datasets, runs the schema checks and the primary statistics exactly as preregistered, applies the sealed verdict rules, computes the descriptive breakdowns, writes `results/` and the figures, and refreshes `data/raw/PROVENANCE.md`. |
| `src/tap/data.py` | Downloads with an on-disk cache and up to 5 retries with backoff; curl's default user agent on every request (FRED drops browser agents and sometimes sends empty bodies, which are retried; federalreserve.gov refuses Python's default agent); the FedInvest form procedure (session cookie, `_csrf` token, POST without following the 302, one fresh session per date, 1 s pause); readers for each source; the provenance table. |
| `src/tap/calendar.py` | Rank-based J±5 windows; U.S. federal business-day calendar (5 U.S.C. 6103 with weekend rule and Juneteenth from 2021). |
| `src/tap/bonds.py` | Coupon dates, accrued interest, yield from price (the preregistered convention and the exact 31 CFR 356 Appendix B one), Svensson (GSW) zero and par yields and bond values from BETA/TAU. |
| `src/tap/measures.py` | The four analysis datasets (F04, F04-bis, J05, K11) and their primary statistics. |
| `src/tap/schema.py` | Each preregistration's schema checks, applied literally. |
| `src/tap/stats.py` | Means and OLS with month-clustered standard errors written from the formula; intervals. |
| `src/tap/figures.py` | The five figures. |
| `tests/` | J±5 windows across holidays (incl. 2016-09-12, 2021-07-12, 2022-09-12), the yield convention on a known auction, GSW pricing against the published SVENY/SVENPY columns, clustered SE against statsmodels. |
| `audit/` | Byte-for-byte copies of the sealed preregistrations, seals and verdicts (see `audit/README.md`). |
| `results/` | `results.json` (everything), `RESULTS.md` (tables), `reproduction.md` (sealed vs pipeline), `datasets/*.csv` (the four analysis files), `figures/*.png`. |

## Data sources (all public, no account)

| Data | URL | Used by |
|---|---|---|
| Treasury constant-maturity yields DGS2, 3, 5, 7, 10, 20, 30 (FRED) | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10` (one per series) | F04, F04-bis |
| Fed GSW fitted curve: par yields SVENPY and parameters BETA0-3, TAU1-2 | `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` | F04, F04-bis, J05 |
| Treasury auction results (Fiscal Data API, three queries copied from the preregistrations) | `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query` | all |
| Treasury par curve under both methods (HS and MC), fiscal 2021 | `https://home.treasury.gov/system/files/221/fy2021-mc-vs-hs-combined.csv` | F04-bis |
| FedInvest end-of-day prices per security, one page per date | `https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate` (form) then `.../securityPriceDetail` | J05, K11 |

The cache `data/raw/` is not versioned. It was seeded by copying the raw files (API responses, CSV downloads and
FedInvest pages, never analysis files) from the sealed test folders; `data/raw/PROVENANCE.md` lists every file
with its URL, date, sha256 and row count, and whether it was seeded or downloaded. Deleting `data/raw/` makes
`run_all.py` download everything again; a from-scratch run was used to check this.

## Definitions in brief

- **J, J±5.** J is the auction date; J±5 is five ranks away in the test's calendar: dates with a DGS10 value
  (F04, F04-bis), dates with all six GSW parameters (J05), federal business days minus 2012-10-30 and 2018-12-05
  (K11).
- **V** (bp) = 100 [2E(J) - E(J-5) - E(J+5)]: positive if the spread E rises before the auction and falls after.
- **K** (bp) = 100 {[high yield - g(J)] - [f(J-5) - g(J-5)]}, g = the bond priced on the GSW curve (forward to
  settlement for the auction yield), f = its yield from the FedInvest price.
- **Standard errors** are clustered by month: SE = (1/N) sqrt(G/(G-1) Σ_g S_g²) for means, the sandwich with
  the single factor G/(G-1) for OLS.

Column names in `results/datasets/` are those of the preregistrations (French), so each file can be read against
the text that defines it. Main ones: `date_adjudication` auction date; `echeance` maturity (years); `mois` month
(cluster); `cmt_*`, `gsw_*`, `hs_*`, `mc_*` yields in percent at J-5 / J / J+5 (`jm5`, `j`, `jp5`); `complet`
complete; `fenetre_propre` no other same-maturity auction in the window; `periode` `ancien`/`avant`/`apres` =
1991-2009 / 2010-2021 / 2022-2026; `rdt_*_pct` yields; `prix_*` prices; `k_pb`, `v_pb` the measures;
`dans_p` in the primary sample; `motif_exclusion` reason for exclusion; `temoin` = control security.

## Known departures and caveats (all reported, none corrected)

- J05 and K11 have `schema_ok = 0` under their own sealed checks (a calendar range that missed Mondays after
  Monday holidays; a "three controls on every row" check that eight rows cannot meet). The pipeline reproduces
  these failures rather than fixing the checks.
- The preregistered yield formula compounds the fractional first period, whereas the exact Treasury formula
  uses simple interest; the primary J05/K11 numbers use the preregistered formula, and `results/RESULTS.md`
  reports a labelled descriptive J05 variant with the exact formula (decline -0.68 instead of -0.66 bp).
- Year-by-year splits and the 2010-2021 / 2022-2026 split of F04 were chosen after seeing the data: they are
  descriptive.
