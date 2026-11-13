# Audit trail

This folder holds byte-for-byte copies of the records of the sealed test this project rests on, K20.
They are in French, as they were written. Nothing here was edited. `run_all.py` recomputes the sha256 of
`K20/preenregistrement.md` and stops if it differs from the seal.

## The sealed protocol

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

## The question and the rule

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
all 53 verifier numbers within the preregistered tolerances and that the sealed rule applied to them gives
"non concluant" again.
