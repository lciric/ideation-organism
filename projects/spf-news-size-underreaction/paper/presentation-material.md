# Presentation material: "Does consensus under-reaction grow with the size of the news?"

All numbers below come from `results/results.json`, `results/RESULTS.md` and the sealed verdicts in `audit/`.
Verdict words are those of the sealed rules: *survives*, *eliminated*, *inconclusive*. Slopes are in standard
deviations of forecast error per standard deviation of forecast revision. Anything added after the verdicts is
called descriptive.

## 1. Two-minute oral version (about 320 words)

"When professional forecasters revise their consensus forecast, does the outcome end up even further in the same
direction? If so, the consensus under-reacts to news. That is well documented. My question was narrower: is the
under-reaction stronger after *large* news? After 2021 and 2022, when inflation kept beating forecasts, it is the
obvious question.

I tested it on three surveys: the US Survey of Professional Forecasters, the ECB's survey, and the Livingston
Survey, which goes back to 1947. The tool is the standard regression of the forecast error on the forecast revision,
with an extra slope after large news. The prediction was an extra slope of plus 0.40.

One design point matters. You cannot define 'large news' as a large revision. The published consensus contains
noise, and that noise enters the revision and the error with opposite signs. Sorting on the revision creates the
effect even when it does not exist; I show this on simulated panels. So 'large news' is the top third of the data
surprise released *before* the survey.

Each test was preregistered and sealed with a hash before any number was computed. A verifier on another model
recomputed everything, and code applied the verdict.

The result: under-reaction yes, size-dependence no. The base slope is 0.19, 0.37 and 0.37. The extra slope after
large news is minus 0.03, minus 0.11 and minus 0.12. In the euro-area and Livingston tests the predicted plus 0.40
is excluded, and both are eliminated. The first US test is formally inconclusive: a data check failed on one row
that enters no regression, and I did not rewrite the check after seeing the numbers.

So the consensus is sticky, but in proportion: after big news it moves much more, and leaves the same share of the
news on the table. That rules out 'reluctance to make large revisions'. It fits constant information rigidity, or
attention that rises a little with shocks. Every number can be rebuilt from public data with one command."

## 2. Five likely questions, with short answers

**1. Why not simply sort on the size of the revision, as the original idea did?**
Because the consensus is a noisy average: the panel changes and answers are rounded. The noise of the evaluated
survey enters the revision with a plus sign and the error with a minus sign. Sorting on large revisions also sorts
on that noise, which pushes the extra slope up even when the true slope is constant. In simulated panels with no
size effect, the revision sort gave +0.046 on average (+0.120 with fixed-size noise), the surprise sort −0.003
(+0.050). The surprise is measured on data released before the survey, so it does not contain that noise. A
remaining bias is covered by a floor that a survival must clear.

**2. Your US test is "inconclusive" because of one row. Why not fix the check?**
Because changing a guard after seeing the numbers is exactly what the seal is meant to prevent. October 2025 is
missing in FRED, so one CPI row (2026-Q1) failed a schema check that the preregistration had called guaranteed.
That row has no outturn and enters no regression. The estimate is c = −0.030, interval [−0.146, 0.086]; with the
check set aside the rule would say "eliminated", but I report that as a reading, not a verdict. The lesson went into
the next two tests: checks count only on rows used in the computation, and both replications were conclusive.

**3. Does "eliminated" mean there is no size effect at all?**
No. It means the predicted +0.40 is excluded at the one-sided 5% level: the upper bounds are 0.047 (ECB) and 0.107
(Livingston). A small effect is not excluded by design; in the Livingston simulation a true +0.20 was eliminated
about 7 times in 10. By variable, intervals are wide, and unemployment is the one variable with a positive sign
(+0.38 in Livingston, se 0.29; positive in the ECB survey once the 2020–21 rows are put back). I noticed that after
the verdicts, on one variable, so it is a lead for a new sealed test, not a result.

**4. Could these tests actually have said "yes"?**
That was checked before sealing: the replications had to show, in simulation, that the rule decides at least 80% of
the time both when the true effect is 0 and when it is +0.40. Two honest caveats. In the ECB test the noise floor
came out at 0.43, far above the 0.10 simulated, so a true +0.40 would mostly have ended inconclusive; the
elimination does not depend on the floor, which only enters survival. In Livingston the dispersions matched the
writer's less favourable scenario, where a null effect is eliminated 78% of the time; but its floor was measured
from individual answers (0.12), so a real +0.40 had a fair chance.

**5. What did the AI do, what did you do, and why trust the numbers?**
Agents from four model families proposed and blind-ranked ideas, checked novelty, wrote the preregistrations, ran
the experiments and verified them. No agent graded its own work: each plan was sealed by hash before data were
read, a verifier on another model recomputed every number, and code applied the verdict. A separate pipeline
rebuilds all three tests from raw public files and reproduces every sealed number (53/53, 65/65, 63/63). No
economist has reviewed it yet. [Author: state here what you personally decided, checked or re-derived.]

## 3. One-slide summary

**Does consensus under-reaction grow with the size of the news?**
*Three preregistered tests: US SPF (1969–2026), ECB SPF (2000–2025), Livingston Survey (1947–2026)*

- **Question.** Is the slope of forecast error on forecast revision steeper after large news? Prediction: extra
  slope +0.40.
- **Design.** "Large news" = top third of the data surprise released before the survey, not the revision (which
  creates the effect through survey noise). Variable-specific slopes, Driscoll-Kraay errors, episode guard, noise
  floor, positive control.
- **Protocol.** Sealed by SHA-256 before any statistic; independent verifier on another model; verdict by code;
  full rebuild from raw public data.

| | US SPF | ECB SPF | Livingston |
|---|---|---|---|
| Base slope (under-reaction) | 0.19 | 0.37 | 0.37 |
| Extra slope after large news | −0.03 | −0.11 | −0.12 |
| 90% interval | [−0.15, 0.09] | [−0.26, 0.05] | [−0.35, 0.11] |
| Verdict | inconclusive (data guard) | eliminated | eliminated |

- **Answer.** Under-reaction yes, size-dependence no: sticky but proportional updating.
- **Caveats.** "Eliminated" = +0.40 excluded, not "no effect"; unemployment lead found after the fact.
- **Figure.** `results/figures/fig6_base_slope_vs_c_three_surveys.png` (base slope beside extra slope, three
  surveys). Say: "Blue is the under-reaction everyone finds; orange is the extra after big news: zero or below, far
  from the dotted +0.40."
