# Audit trail

This folder holds byte-for-byte copies of the records of the two sealed tests this project rests on:
K20 (US Survey of Professional Forecasters) and K20-ZE (its blind replication on the ECB Survey of
Professional Forecasters). They are in French, as they were written. Nothing here was edited.
`run_all.py` recomputes the sha256 of each `<ID>/preenregistrement.md` and stops if it differs from the
seal.

A third replication, K20-LIV (US Livingston Survey), is being preregistered; its records will go in
`K20-LIV/` once it is sealed and judged.

## The sealed protocol

Described here for K20; K20-ZE follows the same protocol (its differences are listed in its section below).

- **`K20/preenregistrement.md` — the preregistration.** Written and sealed on 2026-11-12, *before* anyone
  computed an error, a revision, a surprise or a regression on the data. Its author could look only at file
  headers, column names, counts of present cells and the precision with which numbers are written (the
  first page lists exactly what was seen). It fixes in advance the data sources, the sample (1 004 rows
  expected), the 28 columns of the analysis file and 12 schema checks on it, the statistic, the standard
  errors, the thresholds, the episode guard, the secondary analyses, the tolerances and the verdict rule,
  and it says what would be written in each case.
- **`K20/preenregistrement.md.sha256` — the seal**:
  `2c34e6f5ff86721f1ae903f2dce8f91d79324d94a909cff19aee569a16451ad7`. The same value is recorded as
  `sceau_preenregistrement` in `verdict.json`.
- **`K20/verdict.json` — the verdict.** Two people worked separately. An experimenter downloaded the data,
  built the analysis file and computed the statistics. An independent verifier, who had only the
  preregistration and the analysis file, rewrote every computation, including the 12 schema checks, with
  separate code. The verdict was then computed mechanically, by a separate script, from the **verifier's**
  numbers (`chiffres_verificateur`, 53 fields) and the machine-readable rule copied from the preregistration
  (`regle`). Nobody chose the verdict by hand.
- **`K20/lecture-apres-coup.md` — a reading written after the verdict.** It explains the verdict and what
  the numbers show, and states that it does not change the verdict.

A verdict has three possible values: **survit** (survives), **éliminée** (eliminated) and
**non concluant** (inconclusive: a data or schema guard failed, or the 90% interval cannot choose between
"no effect" and "the predicted effect").

## K20: the question and the rule

Does the under-reaction of the Philadelphia Fed SPF consensus grow after large surprises? For five
variables (GDP deflator inflation, real GDP growth, unemployment, CPI inflation, 3-month T-bill rate;
targets 1969-2026), the standardised forecast error is regressed on the standardised forecast revision,
with one constant, one class effect and one base slope per variable, and a common extra slope **c** after a
large surprise (the top third of |surprise| of the variable, where the surprise is the gap between the
data for quarter t-4, published between the two surveys, and what the consensus expected for it). The
card that motivated the test predicted c = +0.40.

- **Survives** if the lower 90% bound of c is above a floor for the mechanical bias that consensus noise
  can create (max(0.10, bias computed with 20% noise)), the upper bound reaches 0.40, and t ≥ 1 without
  each of seven episode windows.
- **Inconclusive** if the analysis file breaks any schema check, the sample has fewer than 1 000 rows, the
  sort does not separate large from small revisions (variance ratio below 1.25), the interval contains both
  the floor and 0.40, or the episode guard conflicts.
- **Eliminated** otherwise.

Why the sort is on the lagged surprise and not on the revision (the card's original definition): the
published consensus contains noise (changing panel, rounding) that enters the revision with one sign and
the error with the other. Sorting on |revision| also sorts on that noise and creates c > 0 even when the
true slope does not depend on the size of news. The surprise does not contain the noise of the survey
being evaluated. `tests/test_simulation.py` and figure 3 show this on simulated panels.

## K20's verdict: **non concluant**, by a schema guard

The verifier's numbers: c = −0.030 (Driscoll-Kraay se 0.071), 90% interval [−0.146, 0.086]; base slope
after small surprises 0.194, after large surprises 0.164; 1 004 rows, 223 quarters, 820 effective
observations. Every condition of the rule is decided by these numbers except one: **`n_violations_schema` = 1**.

**The guard failure.** Schema check 9 says that the previous-quarter level (`niveau_avant`) must be
present for PGDP, RGDP and CPI whenever the level of the quarter is present, and the preregistration noted
it as "verified before sealing (structure of the sources)". It fails on exactly one row, **CPI 2026-Q1**:
FRED's CPI series has no value for October 2025 (no data were collected during the federal shutdown), so
the 2025-Q4 average, which is the previous level of 2026-Q1, is missing, while the three months of 2026-Q1
are present. The preregistration itself announces that the CPI outturn of 2026-Q1 is missing; it had not
noticed that this breaks check 9 on that row. The experimenter and the verifier each found the failure
independently, both judged the row correct as defined, and neither rewrote the check after the fact. Under
the sealed rule one failed check is enough for "non concluant".

**Why it does not touch the estimate.** That row has no outturn, so no error, so it is not `complete` and
not in the main sample; it enters no regression, primary or secondary. Removing it from the file changes
no estimate (`tests/test_k20.py::test_estimate_does_not_depend_on_the_failing_row`). The verdict is
therefore inconclusive for a reason that says nothing about the hypothesis. With the check set aside, the
same rule applied to the same numbers would give **éliminée** (upper bound 0.086 < 0.40): this is reported
for information only, as the after-verdict reading does, and is never used as the verdict.

`../results/reproduction.md` shows that this project's pipeline, written from the raw data, reproduces
all 53 K20 verifier numbers within the preregistered tolerances and that the sealed rule applied to them
gives "non concluant" again.

## K20-ZE: the blind euro-area replication — **éliminée**

**Files** (`K20-ZE/`): `preenregistrement.md` (sealed on 2026-11-13, seal
`91c3f919cbf571abfeee2e087b387b4962960e183f832a7e4983de7bb802e63a`), `preenregistrement.md.sha256`,
`verdict.json` (the verdict computed mechanically from the verifier's 65 numbers), `verification.json`
(the verifier's numbers), `temoin.json` (the experimenter's numbers), `ecarts.md` (the experimenter's
deviations and ambiguities), `rapport-experimentateur.md`, `rapport-verificateur.md` and
`lecture-apres-coup.md` (a reading written after the verdict, which does not change it).

**What it asks.** The same question as K20, asked blind on a second survey: does the under-reaction of the
ECB SPF consensus (HICP inflation, real GDP growth, unemployment; target years 2000-2025) grow after large
news? Its author knew K20's result and the literature but had seen no euro-area statistic.

**What it keeps and what it adapts.** The statistic, the survival and elimination thresholds and the floor
formula are K20's. Its own section 2.2 lists the adaptations:
- Annual targets with eight survey rounds each, and six series (variable × horizon).
- The news is the change in the reference value that the ECB sends to forecasters between two rounds. It
  contains no survey noise.
- A tie-aware cut for "large": values have one decimal, so ties are common.
- Driscoll-Kraay standard errors with 8 lags by survey round, and the critical value 1.708 (about 26
  independent target years).
- A positive control: the base under-reaction must be visible, or a null c says nothing.
- A relevance guard that applies only when survival is not reached.
- **K20's faulty guard is fixed.** Schema checks count for the verdict only on the rows that enter the
  computation; failures elsewhere are reported as `n_anomalies_hors_principal`.

**Verdict: éliminée.** The verifier's numbers, all reproduced here:
- **Sample.** 578 rows, 107 rounds, 26 target years; 0 schema violations and 0 anomalies.
- **Positive control: passes.** Common slope 0.366, lower 90% bound 0.268; the consensus under-reacts.
- **Primary statistic.** c = −0.106 (se 0.090), 90% interval [−0.259, +0.047].
- **Why it is eliminated.** The upper bound is below 0.40, so the predicted extra slope is excluded at the
  one-sided 5% level.
- **Episodes.** Without each of the three episodes c stays negative (−0.19 to −0.06).

**Three things the after-verdict reading states plainly, repeated here.**
1. **The survival floor was much higher than the preregistration expected.** The computed mechanical bias
   is 0.43, against the 0.10 assumed in the decisiveness simulation, because the variance ratio of
   revisions is 8.4 rather than about 3. Had the true c been near +0.40, the test would mostly have ended
   "non concluant". The elimination does not depend on the floor: it comes from the upper bound, and the
   mechanical bias pushes c up, not down.
2. **With the pandemic rows, the sign changes.** Secondary analysis S3 puts back the 2020-2021 GDP and
   unemployment rows, which were excluded before any data were seen. It gives c = +0.18 (se 0.08); this
   project's descriptive breakdown shows it is driven by unemployment. That is still far below +0.40.
3. **Ties in the cut.** The experimenter and the verifier both computed surprises in double precision
   without rounding, as the text says. The rounded reading gives c = −0.099 and the same verdict
   (`K20-ZE/ecarts.md`, C1). This project follows the letter. Its analysis dataset is bit-identical to the
   sealed `K20-ZE_analyse.csv`.

`../results/reproduction.md` shows all 65 K20-ZE verifier numbers reproduced within the preregistered
tolerances, and the sealed rule applied to them gives "éliminée" again.
