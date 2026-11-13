# Audit trail

This folder holds byte-for-byte copies of the records of the four tests this project is built on.
They are in French, as they were written. Nothing here was edited.

## What these files are

- **`<ID>/preenregistrement.md` — the preregistration.** Each one was written and sealed *before* anyone
  computed an error, a revision or a regression on the data. Its author could look only at file
  headers, column names and counts of present cells (each preregistration lists exactly what was seen).
  It fixes in advance the data, the sample, the statistic, the thresholds, the guards, the tolerances and
  the verdict rule, and it says what would be written in each case.
- **`<ID>/preenregistrement.md.sha256` — the seal.** The sha256 of the preregistration, taken when it was
  sealed. `run_all.py` recomputes the hash of each copy here and stops if it differs from the seal or from
  `sceau_preenregistrement` in `verdict.json`.
- **`<ID>/verdict.json` — the verdict.** Two people worked on each test separately: an experimenter built
  the analysis file and computed the statistics; an independent verifier, who had only the preregistration
  and the analysis file, rewrote all the computations with separate code. The verdict was then computed
  mechanically, by a separate script, from the **verifier's** numbers (`chiffres_verificateur`) and the
  machine-readable rule copied from the preregistration (`regle`). Nobody chose the verdict by hand.
- **`K20/lecture-apres-coup.md` — a reading written after the verdict.** It explains the verdict and what
  the numbers show, and it says explicitly that it does not change the verdict.
- **`H03/annulation.md` — an honesty record.** The first run of H03 was voided: its preregistration had the
  vintage letters for June and September swapped (`S` and `G`), and the schema check that should have
  caught it read an empty column (`TITLE` instead of `TITLE_COMPL`). The test was re-preregistered as
  H03-v2 with the corrected mapping (W = March, G = June, S = September, A = December) before any statistic
  was computed under the correct mapping. Only H03-v2 is used in this project.

Each verdict has three possible values: **survit** (survives), **éliminée** (eliminated),
**non concluant** (inconclusive: a data or schema guard failed, or the 90% interval cannot choose
between "no effect" and "the predicted effect").

## The four tests

| ID | Question | Primary statistic and rule (summary) | Verdict |
|---|---|---|---|
| H03-v2 | Could a recursive real-time rule, correcting each ECB/Eurosystem staff inflation projection by a slope of error on revision estimated only on errors already known, have predicted the projection errors (targets 2004-2025, horizons 1-4)? | Mean over 11 two-year blocks of the uncentred correlation between the announced correction and the realised error, with a 90% interval (Student, neighbour-block correction). Survives if the lower bound > 0, the mean outside 2020-2023 > 0 and the geometric mean of block MSE ratios < 1; eliminated if the upper bound < 0.22 (the smallest effect predicted). | **éliminée** — R = 0.016, 90% interval [−0.074, 0.105]; the corrected projection does worse in a typical block (MSE ratio 1.10). |
| J02 | Is the full-sample slope of ECB staff projection errors on revisions, two quarters ahead, positive and of the predicted size (0.40)? 108 targets 1999Q4-2026Q3. | Standardised slope (= Pearson correlation) with a Newey-West (4 lags) 90% interval. Survives if the lower bound > 0, the upper bound ≥ 0.40 and the correlation stays positive when any two consecutive years are removed. | **survit** — 0.44, t = 2.27, interval [0.12, 0.76]; but only 0.05 without 2021-2022 and 0.14 without 2021-2023. |
| K01 | Do individual ECB SPF forecasters over-react to their own news (negative slope), while the consensus and the ECB under-react? | Pooled 2SLS slope of error on revision, the revision instrumented by the same forecaster's revision of the other target year in the same round; Driscoll-Kraay (8 lags) 90% interval with critical value 1.714. Survives if the upper bound < 0 and the slope without 2021-2023 < 0; eliminated if the whole interval lies above −0.15 (the predicted over-reaction is excluded). | **éliminée** — +1.15, interval [0.36, 1.94]: the predicted over-reaction is excluded. The naive within-round slope (−0.45) is mechanical. Descriptive: consensus 0.92, ECB staff 0.77. |
| K20 | Does the under-reaction of the Philadelphia Fed SPF consensus (five variables) grow after large surprises? | Extra slope c of the standardised error on the standardised revision after the top third of surprises; Driscoll-Kraay (4 lags) 90% interval. Survives if the lower bound is above a mechanical-bias floor, the upper bound ≥ 0.40 and t ≥ 1 without each of seven episodes. | **non concluant** — by a schema guard: check 9 fails on one row (CPI 2026Q1, October 2025 missing at the source). The numbers show no extra under-reaction: c = −0.03, interval [−0.15, 0.09]; base slope 0.19. |

`../results/reproduction.md` shows that the pipeline of this project, written from the raw data,
reproduces every verifier number within the preregistered tolerances.
