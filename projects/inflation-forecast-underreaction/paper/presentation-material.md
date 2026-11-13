# Presentation material: "Do inflation forecasters under-react to news?"

All numbers below come from `results/results.json` and the sealed verdicts in `audit/`. Verdict words are those of
the sealed rules: *survives*, *eliminated*, *inconclusive*.

## 1. CV bullets (pick one)

**Variant A (economics first)**
- Tested four preregistered hypotheses on ECB staff and professional inflation forecasts (1969–2026, public data):
  staff errors follow revisions (correlation 0.44) but almost only through 2021–22 (0.05 without), and a real-time
  correction rule would not have helped.

**Variant B (econometrics first)**
- Built an instrumental-variable test on 8,595 individual ECB SPF revisions that removes the mechanical bias of
  the usual within-round slope; the predicted individual over-reaction was rejected (2SLS slope 1.15, 90% CI
  [0.36, 1.94], first-stage F 514).

**Variant C (AI method)**
- Directed an AI-agent research pipeline under strict verification (SHA-256-sealed preregistrations, independent
  verifier on another model, verdicts applied by code); four macro tests, all 149 verified numbers rebuilt from
  raw data.

*Check before use:* Variant C says "directed". Keep it only if it matches what you did; Section 8 of the paper
leaves your exact role to you.

## 2. Two-minute oral pitch (about 300 words)

"When the ECB's staff raise their inflation projection, does inflation end up even higher than the new number?
If so, forecasters under-react to news. I tested that question four ways on public data. Each hypothesis was
written down and sealed with a cryptographic hash before any data were looked at, and a verdict rule fixed in
advance decided the outcome.

First, could the ECB have used this in real time, correcting each projection with a slope learned from past
errors? No. The correction's correlation with later errors was 0.02, with an interval of minus 0.07 to 0.10, so
the test was eliminated. The correction even made errors larger in a typical two-year block.

Second, looking back over 1999 to 2026, do errors follow revisions? Yes. The correlation is 0.44 and the test
survived. But remove 2021 and 2022 and it falls to 0.05. The effect is essentially the inflation surge.

Third, is the under-reaction just an averaging artefact, with individual forecasters actually over-reacting, as
US studies find? The usual test for that is negative by construction. I instrumented each forecaster's revision
with their revision for the other target year, which carries news but not their reporting noise. Individuals
under-react too: the slope is 1.15, and the predicted over-reaction was eliminated. Again, the effect mostly
comes from 2021–2023.

Fourth, in 57 years of US survey data, does under-reaction grow after large surprises? The estimate says no,
minus 0.03. But the formal verdict is inconclusive, because one data check failed on a single row, and the rule
says a failed check means no verdict. I kept it that way.

So my answer is this. Under-reaction in euro area inflation forecasts is real over the whole sample, but it is
mostly one episode, and it was not exploitable in real time. The project was run with AI agents under a protocol
where no agent graded its own work, and every number can be rebuilt from the raw data."

## 3. Ten questions a sharp interviewer would ask, with honest answers

**1. Why does a positive error-on-revision slope mean under-reaction, and what else could produce it?**
If a forecast used all its information, the revision, which is known at forecast time, could not predict the
error, so the slope would be zero. A positive slope means forecasts moved in the right direction but not far
enough. The same pattern also comes from deliberate smoothing (an institution revising in small steps), from
averaging rational but differently informed forecasters (Coibion and Gorodnichenko, 2015), from conditioning on
market-based oil and rate assumptions, or from autocorrelated shocks. My tests cannot separate these. That is why
I say "errors follow revisions", not "forecasters are irrational".

**2. J02 "survives", yet you say it is carried by 2021–22. Isn't that a contradiction?**
No. The rule asked whether the full-sample correlation was positive, compatible with 0.40, and still positive
after removing any two consecutive years. It was: 0.44, interval [0.12, 0.76], and 0.050 at worst when 2021–22 is
removed. So it survives as a statement about 1999–2026 as a whole. The preregistration itself warned that a
guard removing two years cannot stop a three-year episode from carrying the slope. Without 2021–2023 the
correlation is 0.14, and before 2020 it is 0.13, close to Granziera et al.'s 0.20 (0.21) in raw units.

**3. How can errors be predictable in-sample but not in real time?**
The in-sample slope comes mostly from one episode that a rule estimated on earlier data could not anticipate.
After the rule had learned from 2021–22, it over-corrected the disinflation: in the 2024–25 block the corrected
projection had 81% more squared error than the published one. Over all rows the correction gained 3%; without
2021–22 it lost 10%. Eva and Winkler (2023) find the same pattern on US surveys.

**4. Why is the within-round slope negative "by construction"?**
Within a round, all forecasters face the same outturn, so a forecaster's error relative to the round mean is
exactly minus his forecast's deviation from the round mean. The outturn drops out, and the slope depends only on
how dispersion changes between rounds. With stable dispersion it is exactly −1/2. I found −0.45. It measures
dispersion, not accuracy.

**5. Why is your instrument valid, and what would break it?**
Relevance: news moves a forecaster's current-year and next-year forecasts together. The first-stage F is 514.
Exogeneity: under rationality the forecaster knows his other-year revision at forecast time, so it cannot predict
his error. Reporting noise specific to the evaluated number is not in the instrument. What breaks it is noise
common to both numbers in the same round, for example strategic shading of the whole submission. That noise
would bias the slope negative. Since the slope is positive, it cannot explain the result, and the computed noise
bound is zero.

**6. Why is the 2SLS slope (1.15) so much larger than OLS (0.42)?**
Part of the gap is what reporting noise predicts: noise pushes OLS down and the instrument removes it. Part is
weighting. The instrument puts weight on revisions that move both target years together, which is common news,
and 2021–22 dominates those. Without 2021–2023 the 2SLS slope is 0.17 with a standard error of 0.47, so I would
not lean on the 1.15 as a typical magnitude.

**7. Are your standard errors credible with so few independent observations?**
They are the weakest point. K01 has about 24 independent target years. That is why the preregistration used a
t(23) critical value of 1.714 and Driscoll-Kraay errors with 8 lags. J02 has 108 overlapping quarters. There I
also report 8 Newey-West lags (se 0.162) and a block bootstrap ([0.051, 0.592]), and neither changes the verdict.
Precision differed from the preregistered power scenarios. K01's standard error, 0.46, was worse than the
pessimistic case; it decided only because the estimate was far from −0.15.

**8. K20 is "inconclusive" because of one missing month. Why not just fix the guard?**
Because that is what sealing is for. The preregistration claimed a schema check was guaranteed by the data
structure and did not verify it on the last row. October 2025 is missing in FRED, so one CPI row fails. That row
enters no regression, and the numbers show no extra under-reaction: c = −0.03, interval [−0.15, 0.09]. Had the
check passed, the rule would have said "eliminated". But rewriting a guard after seeing results is exactly the
flexibility the protocol exists to remove. So I report the numbers, and I report the verdict as inconclusive.

**9. What did the AI do, what did you do, and why should I trust it?**
Agents proposed ideas, judged them blind, checked the literature, wrote the preregistrations, ran the analyses
and verified them. [Complete with your own role: the question and constraints you set, the decisions you took,
what you checked or re-derived yourself.] The trust comes from the structure, not the agents. Predictions were
sealed before data were read. A verifier on a different model recomputed everything without seeing the
experimenter's code. Verdicts came from code. Errors were recorded, not hidden: the first run of one test was
voided because two vintage letters were swapped, and the record is in the audit folder. The limit: the verifier
checked computations from the analysis file, not its construction. The independent rebuild from raw data, which
reproduces all 149 numbers, covers that only partly.

**10. What should a central bank take from this?**
Three modest points. Full-sample efficiency tests that include 2021–22 overstate how projections behave in a
typical year, so report leave-episode-out estimates. A simple revision-based bias correction is not a free
improvement; here it would have hurt. And claims that individual forecasters over-react depend on a statistic
with a mechanical component. What I cannot say is whether staff should have revised faster in 2021–22: smoothing
and under-reaction look the same in these data, and the ECB's own work points to energy assumptions, which I did
not test.

## 4. The one figure to show

**Figure 1, `results/figures/fig1_ecb_error_vs_revision.png`** (ECB staff errors against revisions, 2021–2023 in
orange, fits with and without them).

Why this one: it states the main finding and its main caveat in a single picture. The solid line is the
preregistered result that survived (correlation 0.44). The dashed line is the same fit without 2021–2023 (0.14).
The four 2022 points in the top right show where the slope comes from. A recruiter gets the message in ten
seconds, and an economist sees immediately that you are not overselling it.

What to say while showing it, in one sentence: "Errors do follow revisions over 1999–2026, but the slope is these
four quarters of 2022; without the surge it is a third as large, and a rule learned in real time could not have
used it."

If a second figure is allowed, use Figure 2 (`fig2_j02_leave_years_out.png`): it shows that removing any year
except 2022 leaves the correlation unchanged.
