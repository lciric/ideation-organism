# T0.3 — preregistered simulation of the additivity lemma and the negative theorem (control programme): result

*Result page of a preregistered simulation of the AI-control programme that hosts this repository. Its name in the programme is T0.3, "simulation of the additivity lemma and of the negative theorem"; this page sits in the folder `controle-simulation-defenses`. It was run once, on 4 October 2026, and the frozen reading was applied by the frozen code. Published on 3 November 2026 on the director's decision. Last updated: 3 November 2026, 05:50 UTC.*

## Result

**Frozen reading of 4 October 2026**, computed by the frozen code at the end of the single decisive run (`20261004-080257-t03`, 706 s).

- **31 of 31 predictions confirmed**: 342 statistical cells and 544 trajectory cells, all conforming; 0 contrary cell, so no replication; 0 trajectory violation.
- **Symmetry audit ("too good = reservation"): not triggered.** Variance of the standardised deviations from theory: 0.955 over 63 comparisons with closed forms, 0.853 over 104 equalities, within the frozen bounds [0.3, 3]. The deviations behave like ordinary Monte Carlo noise, neither too clean nor too noisy.
- **Reservation written with the result.** That everything is confirmed was expected: most predictions are **instrument checks**, which could fail only through an error of code or of statement. The confirmation establishes three things: the aggregators and calibrations are correct; the arithmetic of the proofs is right; the informative predictions have the announced magnitudes. **It proves neither the lemma nor the theorem on real activations.**
- **No fresh-reader verdict.** The outcome is the mechanical application of the frozen criteria by the frozen code; the run crossed no gate, and no fresh reader has given a verdict on it. The results note that records the reading is copied below.

### The informative result: Ville's threshold outside its assumptions (P8)

No attack is played, so every alarm is a false alarm. The statistic is the maximum over the horizon of a one-sided normal-mixture e-process; Ville's rule raises an alarm when the e-process reaches 1/α, with α = 0.05. 20,000 episodes per setting.

| situation | false-alarm rate of Ville's rule | sealed count |
|---|---|---|
| well specified (Gaussian scores; 1 × 200, 1 × 1000 and 5 × 40) | 0.017 to 0.019 | 333, 387 and 337 of 20,000 |
| episode effect τ = 0.2, n₀ = 200 | 0.21 | 4,210 of 20,000 |
| episode effect τ = 0.2, n₀ = 1000 | 0.35 | 7,029 of 20,000 |
| episode effect τ = 0.1, n₀ = 1000 | 0.24 | 4,723 of 20,000 |
| equicorrelation between agents, c = 0.4 (5 agents × 40 steps; the stronger of the two correlations of the grid; c = 0.2 gives 0.083, 1,655 of 20,000) | 0.17 | 3,312 of 20,000 |
| σ underestimated by 20 % | 0.066 | 1,322 of 20,000 |
| AR(1), φ = 0.2 | 0.057 | 1,136 of 20,000 |

The rates are those of the results note; the counts are read in the sealed output `bloc-P8.json` (key `resultat.reglages[i].alarmes.e_unilat_ville`, out of `R` = 20,000).

**Calibrating on whole honest episodes holds the rate.** A conformal threshold calibrated on K = 1,000 whole honest episodes, drawn from the same law as the test, gives 0.046 to 0.055 in all 17 settings, for both statistics read (the e-process and the sum), against 0.04995 predicted (1 − 951/1001).

How the frozen reading reads the programme's statement "the false-positive rate of always-valid aggregators is checked empirically on honest episodes" (translated): **"Decisive: Ville's rule exceeds its well-specified rate under episode effect, correlation between agents, temporal dependence or underestimated σ, and exceeds α at the strongest levels of episode effect, correlation between agents and underestimation of σ. Conformal calibration on whole honest episodes holds its rate when calibration and deployment episodes are exchangeable (instrument check); its robustness to a shift between them is not tested in T0.3."**

Definitions: n₀ is the number of actions in an episode (agents × steps). An episode effect τ is a shift shared by all the scores of an episode, of standard deviation τ, the total variance staying 1 (each score remains N(0, 1)). Equicorrelation c is a correlation c between the agents' scores at the same step.

### The programme's statements, as the frozen reading reads them

Table E of the frozen reading, translated (prediction numbers omitted). Class C: the attacker only rearranges the honest scores, so their multiset is preserved. Class K: each score keeps its marginal law and the attacker changes their dependence (copula).

| statement | frozen reading |
|---|---|
| Lemma: "power depends only on B and on the variance, not on how the sabotage is spread over agents or time steps" (B: the total sabotage budget) | Established by proof, checked in simulation: exact for the terminal statistic at fixed n₀, the "variance" being that of the statistic (n₀σ²), for any spread (agents, steps, values, adaptive choice of positions). False at fixed per-action variance when n₀ = NT varies: power decreases in n₀. False for the always-valid sequential reading as to timing (spread over steps): bringing the sabotage forward helps the defender, postponing it brings it back towards the terminal bound, the only invariant. Invariance between agents at the same step (L4) is not tested in T0.3. |
| Execution brief: "the power of the per-action max collapses as fragmentation grows" | Established by proof, checked in simulation: exact, with a floor strictly above α at fixed n₀. |
| Negative theorem: "any statistic based on the marginals (max, mean, cumulative sum) has power equal to the false-positive rate" (damage in the correlation, marginals preserved) | True in class C for symmetric statistics, path by path, and for any statistic under uniform reshuffling; the permutation group matters. False in class K: the sum and the e-process go above their rate under the honest law for a positive dependence and below it for a negative one; under positive dependence, the max stays at its rate or below (Slepian); this is the case of the construction of arXiv 2606.10456 (sum 0.07 to 0.25 at α = 0.05). |
| Theorem: "an autocorrelation aggregator (over time) or a co-elevation aggregator (across agents) is needed" | In class K, under positive dependence, autocorrelation and co-elevation detect; under negative dependence, the sum and the e-process fall below their rate under the honest law and the absolute autocorrelation detects; under positive dependence, the sum is not blind. Against an adaptive class-C attacker, autocorrelation and runs can be neutralised; only local statistics (scan, Page, co-elevation) keep a path-wise guarantee. |
| Execution brief: "the cumulative sum fails" (marginal-preserving attack) | Exact for the terminal sum in class C; exact in the adversarial sense for the one-sided sequential sum under arrangements with dominated partial sums, from which the two-sided rule escapes; inexact in class K: the sum is not blind (Φ̄(z_α·√(v₀/v₁)), 0.07 to 0.25 in the construction of 2606.10456 at α = 0.05), but it stays weak. |
| Guard of gate G1: "the false-positive rate of always-valid aggregators is checked empirically on honest episodes" | Decisive (quoted above). |

## The question

Before any real activation, are the programme's statistical instruments correct, and what do its two founding statements really say? The simulation checks them on synthetic scores, in the form corrected by the programme's mathematical note: an additivity lemma (at a fixed horizon, the power of the terminal sum depends only on the total sabotage budget, not on how it is spread) and a negative theorem by invariance (against an attacker who only rearranges the multiset of scores, a permutation-invariant statistic keeps its value path by path, so its power equals its false-alarm rate). It fixes in advance how each sentence of the programme will be read, and asks whether the always-valid thresholds the programme relies on stay valid outside their assumptions.

## Design (frozen in the sealed preregistration)

- **Synthetic scores only.** An episode is a matrix of monitor scores X_{i,t}, agent i ≤ N, step t ≤ T, n₀ = NT; scores standardised (mean 0, σ = 1, known, except in P8 where σ is misestimated); honest reference law: independent N(0, 1); α = 0.05 for every rule; sequential reading time first.
- **Statements tested**: the additivity lemma (L1), the collapse of the max (L2), the always-valid sequential reading (L3), the negative theorem in class C (T1 to T4), dependence attacks with preserved marginals (class K), and the validity of Ville's rule outside its assumptions (P8).
- **31 signed predictions (P1.1 to P8.4)**, each labelled by origin (proof, closed form, heuristic, or "exploratory seen" when its magnitude had been observed before sealing) and by nature (instrument check, or informative), read mechanically on 886 cells under frozen criteria (Z = 4). Any contrary cell would have triggered a replication with fresh seeds.
- **Seeds and code.** The decisive grid was sealed with fresh entropy; seeds derived by `numpy.random.SeedSequence` for 3,280 tasks; code frozen at commit `d73ac46`, the launcher refusing any other code or grid; a single decisive run (Python 3.11.15, numpy 2.4.6, scipy 1.17.1).
- **Counter-reading.** Three counter-readings by three distinct fresh sub-agents before sealing, each "sealable after corrections". Every remark was treated before sealing; one minor code fix (a refusal path not reached by the decisive command) was deferred until after the run, the code being frozen.

## Sealed before the run

The sealed preregistration, outputs and reading live in the private working repository; their hashes are listed here. There is no separate verdict: the frozen reading is the outcome.

| Item (private working repository) | Role | SHA-256 | When |
|---|---|---|---|
| `prereg/T0.3-simulation-lemme-theoreme-v1.md` | preregistration: hypotheses, 31 signed predictions, metric, thresholds, analysis plan, frozen reading criteria and table E, stop list, transparency on what was seen before sealing | `7474743a0fa2a9db5da85bcedb0087ea57114fcca0fbb3415c7a97bf1b78d1fb` | sealed 4 Oct 2026, before the run; **copied here** |
| `prereg/T0.3-grille-v2.json` | decisive grid (sizes, settings, entropy), cited by the preregistration | `5609f920c0d606a192e92b2c2172416dad740b158940aac1ee049de8b8affe23` | sealed 4 Oct 2026; **copied here** |
| `prereg/contre-lectures/T0.3-rapport-contre-lecture-1-v1.md`, `-2-v1.md`, `-3-v1.md` | the three counter-readings | `92007a7ca203a226dcdbb323b9368d32780a0e013f668bebbda4136af2b92173`; `b5a7c6ac13e3a69f08ea3435a82318f4e6e39435e6682e35f4552a3d2dc0835c`; `129eadabc31f4404ee797a04e7f5c508f9d72f8ba3f824ac2939963d2ac607f8` | 4 Oct 2026, before sealing |
| run `20261004-080257-t03`, manifest | the single decisive run; cites the sealed preregistration by its hash | `c9bba5e1f5f8dbf268e47023db8fac56c2cfd011721c6f89ba8ecad413e1a8ea` | created 4 Oct 2026, 08:02:57 UTC |
| `lecture.json` | frozen reading, computed by the frozen code | `c5aa62b42feed399e8626e3f681830023dc2dd124663d138e3a0c8170f1a7bbb` | same run; **copied here** |
| `lecture.md` | its table | `650ef86bef453104784fa7237187aa2d211be3169f25ffa9bba854d0b2f5722d` | same run; **copied here** |
| `bloc-P8.json` | sealed output of block P8 (the counts above) | `9af85122e168279f2c6a6407b136b08dca1d1caf491b23fdc9c5edf372bb7dad` | same run; **copied here** |
| `calibrage.json`; `equivalence.json` | outputs of the calibration and equivalence guards | `cb72b41d4dff5ee547037e700aeec963dbf5762a0727ccf6f615fbcad178f383`; `4bdfd2fc5c1e6ea32e624d98c7c29d2925a4a081f6d21de3102b46f5c6b37320` | same run |
| `docs/notes/resultats-T0.3-v1.md` | results note: pronouncement of the frozen reading, informative magnitudes | `9ab618edae17e757ab83d5de7a346ebf08bebf89aef61e4337cb5c067e5fd545` | 4 Oct 2026; **copied here** |

## What this does not show

- Anything about real models or real activations: the scores are synthetic (Gaussian, plus the departures listed), and most predictions check the instruments (reservation above).
- A blind prediction of the strongest cells. The cells where Ville's rule exceeds α (P8.3) were selected after exploratory runs had shown values of 0.214, 0.364, 0.164 and 0.067; the decisive run confirms them on fresh seeds, it does not predict them blind. The grid was fixed before any decisive execution, but not independently of all the values seen; the preregistration says so.
- That every episode effect breaks Ville's rule by that much. 0.21 to 0.35 are the three strongest episode-effect settings of the grid. In the same sealed output, the weaker settings give 0.034 (τ = 0.05, n₀ = 200: 676 of 20,000), 0.089 (τ = 0.1, n₀ = 200: 1,773) and 0.107 (τ = 0.05, n₀ = 1000: 2,146): above the well-specified rate, as predicted in all eleven cells of P8.2, but the first is below α.
- That conformal calibration survives a shift between calibration and deployment episodes: not tested. The calibrated rate holds when they are exchangeable, and that part is an instrument check.
- Novelty. Neither the failure nor the fix is claimed as new: Ville's rule fails here because one of its assumptions is broken (an episode effect, a correlation between agents, a temporal dependence, a misestimated σ), and calibrating a threshold on whole honest episodes is a conformal construction. The simulation measures how large the failure is in the programme's own settings, and checks that the programme's code implements the calibration correctly.
- What was declared out of scope before the run: the invariance between agents at the same step (L4), the covered adversary of arXiv 2601.20022, a data-dependent compensation steered by the agent, the variant of T3 just above a quantile.
- A fresh-reader verdict, or any criterion of the programme's gate G0: neither has been pronounced on this run.

## Files

Copied here, each with its seal recomputed and equal to the original (the texts are in French): [`pieces/T0.3-simulation-lemme-theoreme-v1.md`](pieces/T0.3-simulation-lemme-theoreme-v1.md) (preregistration), [`pieces/T0.3-grille-v2.json`](pieces/T0.3-grille-v2.json) (grid), [`pieces/lecture.md`](pieces/lecture.md) and [`pieces/lecture.json`](pieces/lecture.json) (frozen reading), [`pieces/bloc-P8.json`](pieces/bloc-P8.json) (block P8), [`pieces/resultats-T0.3-v1.md`](pieces/resultats-T0.3-v1.md) (results note), and their `.sha256` companions. Check: `cd pieces && sha256sum -c *.sha256`.

The simulation code (commit `d73ac46`), the run manifest, the other blocks and the counter-readings stay in the private working repository.

Published on 3 November 2026 on the director's decision.

Back to the [main README](../../README.md).
