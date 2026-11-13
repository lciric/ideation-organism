# Presentation material: "Auction pressure in U.S. Treasury yields after 2021: did the market change, or the measure?"

All numbers below come from `results/results.json` and the sealed verdicts in `audit/`. Verdict words are those of
the sealed rules: *survives*, *eliminated*, *inconclusive*. Anything chosen after seeing the data is called
descriptive.

## 1. CV bullets (pick one)

**Variant A (rates and markets first)**
- Measured price pressure around 321 U.S. Treasury reopenings (2010–2026) on public data: 0.91 bp against the
  Treasury curve (t = 5.6), and showed that the December 2021 curve-method change alone removes 0.78 bp of it
  (95% CI [0.45, 1.12]) on fiscal 2021.

**Variant B (data and econometrics first)**
- Rebuilt auction concessions from 921 days of TreasuryDirect security prices and the Fed's fitted (GSW) curve,
  with Treasury yield conventions and month-clustered errors; found no fall after 2021 (−0.66 bp, 90% CI
  [−1.27, −0.04]), under a sealed verdict that stayed inconclusive.

**Variant C (AI method)**
- Ran an AI-agent research pipeline with SHA-256-sealed preregistrations, an independent verifier on another
  model and verdicts applied by code: four Treasury-auction tests (one survived, three inconclusive), all 60
  verified numbers rebuilt from raw data.

*Check before use:* Variant C says "ran". Keep the verb only if it matches what you did; Section 9 of the paper
leaves your exact role to you. Do not shorten Variant B to "showed the concession did not fall": the verdict
was inconclusive.

## 2. Two-minute oral pitch (about 320 words)

"When the U.S. Treasury sells a bond, dealers have to absorb the supply, so the bond tends to cheapen in the days
before the auction and recover after. This is well documented. I asked whether it still holds, using only public
data.

I measured it around 321 reopenings of 10-, 20- and 30-year securities, as the move of the Treasury's
constant-maturity yield relative to the Fed's fitted curve. Over 2010 to 2026 the pressure averaged 0.91 basis
points, with a t-statistic of 5.6, and the preregistered test survived. But when I cut it by year, after the
verdict, it was about 1.4 basis points until 2021 and almost zero from 2022.

So I read the Treasury's methodology notes. On 6 December 2021 the Treasury changed the method that builds that
curve. For fiscal 2021 it publishes both versions side by side. On the same 23 auctions, the new method alone
lowers the measured pressure by 0.78 basis points out of 1.64. The interval is 0.45 to 1.12: clearly not zero,
but the sealed rule asked whether it was above 0.9, so the verdict is inconclusive.

Then I measured the concession without the Treasury curve at all: the auction's own yield and end-of-day security
prices against the Fed's curve. It did not fall after 2021: 0.68 basis points before, 1.10 after. That test is
formally inconclusive too, because a calendar check I had sealed did not foresee Monday holidays, and I did not
rewrite it after seeing the numbers.

My conclusion: the pressure exists, and its disappearance after 2021 is at least partly an artefact of the public
constant-maturity series. Free end-of-day data cannot fully settle it. For anyone using those series around
auctions, or across December 2021, the lesson is to check the measure before reading a change in the market.

Every hypothesis was sealed with a hash before the data were read, a separate verifier recomputed every number,
and the whole pipeline rebuilds from raw data."

## 3. Ten questions a sharp interviewer would ask, with honest answers

**1. Why should a market as liquid as Treasuries concede at all around a scheduled auction?**
Because the supply is large relative to what dealers and investors can hold at short notice. Someone has to
warehouse the new duration until end investors buy it, and that risk is paid for with a cheaper price around the
auction. Lou, Yan and Zhang (2013) found it to 2008; Fleming, Liu and Nguyen (2026) find it weaker after 2014;
Fleming, Nguyen and Rosenberg (2024) show that issuance drives dealer inventories. My measure is a spread to a
fitted curve, so it captures only the part specific to the auctioned maturity, not a move of the whole curve.

**2. Why reopenings only, and why a spread to the Fed's curve rather than the raw yield?**
The constant-maturity yield is read on the most recently auctioned security. At a new issue that security
changes, and the spread jumps by the new issue's premium; at a reopening it does not. The spread removes the level
of rates, which moves several basis points a day and would drown a 1 bp effect. The cost is that any pressure
shared by the whole curve is removed too, so a zero would have meant "no pressure specific to this maturity", not
"no pressure".

**3. Is 0.9 bp economically meaningful?**
It is small relative to daily noise: the standard deviation of V across auctions was 2.57 bp. But it is
systematic, it applies to every reopening, and the Treasury pays it on the amount sold. It is the same order as
the published 10-day figure for the 10-year in 2015–2024 (1.2 bp, not significant). I would not claim more than
"about a basis point, measured precisely".

**4. Your observations overlap and cluster. How did you handle inference?**
The 10- and 30-year reopenings fall in the same week and the 20-year a week later, so their windows share news.
Standard errors are clustered by month, with the formula written in the preregistration: 134 months in F04, 96
and 39 in J05. The fiscal-2021 test has only 8 months, so it uses a Student critical value with 7 degrees of
freedom (2.365) instead of 1.96, and it relies on pairing: the same auction is measured twice, so market noise and
the fitted curve cancel in the difference.

**5. The fiscal-2021 test was inconclusive. Why do you still say "at least partly measurement"?**
Because the question it was built to answer was "more than half or less than half?", and the interval [0.45,
1.12] straddles 0.9. It does not straddle zero. The preregistration said in advance that if the interval's
half-width was below 0.45 bp the reading would be "in part"; it was 0.33. Add that a measure without the Treasury
curve shows no fall after 2021. I do not claim the method explains all of it: under the new method fiscal-2021 V
was still 0.85 bp, against 0.05 bp in 2022–2026.

**6. Maybe the new method is right and the old one created the pressure. How do you know which?**
I do not, and the tests cannot say. Before 2022 most of V sat on the auction day itself, and the two methods
differ most on auction days (0.70 bp on average, against 0.26 and 0.35 bp five days either side), so the old
method may have amplified the move. On the other side, the concession measured on security prices against the
Fed's curve is positive in both periods (0.68 and 1.10 bp), and the published work finds pressure with other
data. The safe statement is that the measured pressure depends on the measure by about half its size.

**7. Auctions close at 1 pm and your prices are end-of-day. What does that do?**
Three things. It understates the peak, because part of the reversal happens in the afternoon. It adds noise to the
auction-yield measure, since the afternoon's market move enters it; that was its main source of noise. And a
change in how fast the pressure unwinds after 1 pm would look like a change in the pressure itself. Fixing that
needs intraday data, which are not free.

**8. Your matched-control test saw nothing even before 2022. Was it badly designed?**
It was designed to fail safely. The controls were the 2nd to 4th off-the-run securities of the same original
maturity, and they move with the reopened security; Fleming, Liu and Nguyen show the same for the first off-the-run,
and Sigaux (2018) rejects domestic controls for this reason. The preregistration included an instrument check: if
the measure showed no decline from 2010–2021, the verdict could not be "eliminated". It fired, so the test returned
inconclusive instead of a false "the market changed". The lesson is that controls must come from another maturity
sector, or the data must be intraday.

**9. One test failed a calendar check on three correct rows. Why not just fix the check?**
Because fixing a guard after seeing the numbers is exactly what sealing is meant to prevent. The rows were
Mondays after Monday holidays, where five business days span 10 calendar days; both the experimenter and the
verifier found them correct. I report both facts: the verdict is inconclusive, and the written reading after the
verdict says the numbers would have eliminated the "market change" reading. I also report the weak point of that
test: its rise after 2021 comes mostly from 2023 (3.34 bp); without 2023 the change is −0.04 bp, which shows no
fall but no rise either.

**10. What did the AI do, what did you do, and why should I trust the numbers?**
Agents from several model families proposed and ranked ideas blind, checked novelty, wrote the preregistrations,
ran the experiments and verified them. No agent graded its own work: each preregistration was sealed by hash
before data were read, a verifier on another model recomputed every number from the analysis file, and code
applied the verdict rule. A separate pipeline rebuilds all four analyses from raw public files and reproduces all
60 sealed numbers. References are limited to those the novelty checks actually opened. [Author: state here what
you personally decided, checked or re-derived.]

## 4. The one figure

If only one figure is allowed, show **Figure 3** (`results/figures/fig3_fy2021_old_vs_new_method.png`): the same 23
fiscal-2021 auctions, V under the old and the new Treasury method, mean 1.64 bp against 0.85 bp.

Why this one: it is the only figure that answers the question rather than describing the puzzle, and it needs no
econometrics to read. Each line is one auction measured twice, so the drop cannot come from the market. Say in one
sentence what it does not show: it covers one fiscal year, and the sealed verdict is inconclusive because the
interval of the drop, [0.45, 1.12] bp, contains the 0.9 bp threshold.

If a second figure is allowed, add **Figure 1** (`results/figures/fig2_v_by_year_treasury_curve.png`), the yearly
means with the December 2021 line, as the puzzle that Figure 3 answers; say that the year split was made after the
verdict.
