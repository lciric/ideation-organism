# Audit trail: the four sealed tests

This folder holds byte-for-byte copies of the documents that fixed each test **before any of its data were
read**. They are in French, as written. Nothing here is edited; `run_all.py` recomputes the sha256 of every
`preenregistrement.md` and stops with an error if it differs from the sealed value.

## How the tests were run

1. **Preregistration first.** For each test a writer fixed, in `preenregistrement.md`, the question, the data
   sources, the exact construction of the analysis file, the single primary statistic, the minimum sample, the
   tolerances and a machine-readable verdict rule (the `json` block at the end). The writer had not computed any
   statistic on the data the test uses; what they had seen is listed in the text.
2. **Seal.** The file's sha256 was recorded in `preenregistrement.md.sha256` before the data were downloaded.
   For F04-bis the seal is documented in `scellement.md` (the draft was sealed unchanged, including its first
   line that still reads "PROJET NON SCELLÉ").
3. **Two independent computations.** An experimenter built the analysis file and computed the statistic. A
   separate verifier, working from the preregistration text and the analysis file only, recomputed every number
   with independent code.
4. **Verdict by rule.** The verdict was computed mechanically by separate code, from the **verifier's** numbers
   (`chiffres_verificateur` in `verdict.json`), by applying the sealed rule: first "non concluant"
   (inconclusive), then "survit" (survives), otherwise "éliminée" (eliminated).
5. **Reading afterwards.** `lecture-apres-coup.md` (J05, K11) is a plain-language reading written after the
   verdict. It does not change the verdict.

This project's pipeline re-derives every verifier number from the raw data with its own code; the comparison is
in `../results/reproduction.md`.

## The four tests

| Test | Question | Rule (in short) | Verdict |
|---|---|---|---|
| **F04** | Around 10-, 20- and 30-year reopenings (2010-2026), does the Treasury constant-maturity yield rise relative to the Fed's GSW curve in the 5 days before the auction and fall back in the 5 days after? V = 100[2E(J) - E(J-5) - E(J+5)], E = CMT - GSW par yield. | Survives if mean V > 0 with t >= 2 (SE clustered by month), placebo \|t\| < 2 and enough data; eliminated if t < 2 and the 95% upper bound <= 0.5 bp; otherwise inconclusive. | **Survives**: 0.91 bp, t = 5.6, 321 reopenings. |
| **F04-bis** | On the 23 reopenings of fiscal 2021, how much lower is V when computed with the Treasury's new curve method (MC) instead of the old one (HS)? D = V_HS - V_MC. | Survives ("the method change explains the post-2021 break") if the whole 95% interval of D (Student, 7 df) is above 0.9 bp; eliminated if it is all below 0.9; inconclusive otherwise or if a guard fails. | **Inconclusive**: D = 0.78 bp, 95% CI [0.45, 1.12] contains 0.9. |
| **J05** | Measured without any Treasury curve (auction high yield vs the same bond on the GSW curve, net of its own spread at J-5 from FedInvest prices), did the concession K fall from 2010-2021 to 2022-2026? | Survives if the 90% CI of the decline is above 0 and reaches 0.5 bp; eliminated if its upper bound is below 0.5 bp; inconclusive otherwise or if a guard fails. | **Inconclusive**: schema check 5 ("J-5 is 7 to 9 calendar days before J") fails on three Mondays after a Monday holiday (10 days). The numbers show no decline: 0.68 -> 1.10 bp (decline -0.66, 90% CI [-1.27, -0.04]). |
| **K11** | Against three matched control securities of the same family (2nd-4th off-the-run), all at FedInvest end-of-day prices and with no curve at all, is V still positive after 2021? | Survives if the 90% CI of mean V after 2021 is above 0, reaches 0.5 bp and is robust without 2023 and without the 30-year; eliminated if the upper bound is below 0.5 bp **and** the same instrument sees a significant decline since 2010-2021; inconclusive otherwise. | **Inconclusive**: the instrument alert fires (V is -0.03 bp before 2022 as well, so the measure cannot see the pressure), and schema check 5 fails on 8 rows without three usable controls. |

## Files

| Folder | Files |
|---|---|
| `F04/` | `preenregistrement.md`, `preenregistrement.md.sha256`, `verdict.json` |
| `F04-bis/` | the same, plus `scellement.md` |
| `J05/` | the same, plus `lecture-apres-coup.md` |
| `K11/` | the same, plus `lecture-apres-coup.md` |
