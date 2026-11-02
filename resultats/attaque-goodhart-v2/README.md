# A1 — Goodhart attack on the statistical judge: status

*Status page of the preregistered attack on this system's statistical judge by language-model proposers that see its verdicts. Last updated: 2 November 2026, 09:29 UTC. The result, whatever its sign, will be posted on this page once the sealed output has been read once under the frozen criteria and checked by a fresh reader.*

## The question

Does the judge resist an agent that plays against it? The statistical judge was validated against 27 **scripted** cheaters (section 3.1 of the [main README](../../README.md)). It has never faced a **language-model proposer that receives the judge's verdicts and optimises against them**. In production that feedback does not exist: the memory never serves as a verdict to the agents. The experiment measures what happens if that guard gives way.

Theory already bounds part of the answer. Each attempt is promoted with probability at most α = 0.05 when the world's law is a member of the null, whatever the history. Nothing bounds the number of attempts, though: with n attempts and a stop at the first promotion, the bound is 1 − (1 − α)ⁿ (0.05, 0.185 and 0.560 for n = 1, 4 and 16). The run measures where a real optimiser lands between 0 and that ceiling, and whether the judge's feedback pushes it higher than a witness without feedback.

## Design (frozen in the sealed text)

- **Two toy worlds where the truth is known.** Neither brings a law beyond the archive, so every promotion is a false promotion.
  - **W1**: a mixture of two archive laws. It is a member of the current (v8) null, so a false promotion can only come from the multiplicity of attempts or from a code defect.
  - **W2**: a piecewise recombination of the same two laws, a class that the v8 null declares it does not cover. This is the regime in which feedback could teach the proposer the judge's taste.
- **Two arms.** "Feedback": the proposer sees each verdict. "Witness": no verdict.
- **Two judges.** The current null (v8), and the old null (v7) as a check that the attack has teeth.
- **Grid G1.** 12 cards per world, 24 units per cell, two providers (Kimi and Argon), up to 16 attempts per unit.
- **Six signed numeric predictions (P1 to P6),** each open in both directions. They do not decide the outcome; frozen reading criteria do. For example, P1 (W1, v8): with feedback, at most 0.10 of units promoted after 16 attempts, and feedback minus witness within ±0.10.
- **Budget**: capped at 80 USD (27 to 50 USD expected), hard time limit 20 hours.

## Sealed before the run

| Item | Where | SHA-256 |
|---|---|---|
| Preregistration (v2-v1) | [`orchestrator/prereg/preenregistrement-attaque-goodhart-v2-v1.md`](../../orchestrator/prereg/preenregistrement-attaque-goodhart-v2-v1.md) (commit `bc5e2d2`) | `fc81d015d27e60388099c7845a66b75d613187f99d5d0060950540a686925b65` |
| Fresh counter-reading of its draft (verdict: sealable after 23 replacements, all applied) | [`orchestrator/prereg/contre-lecture-preenregistrement-attaque-goodhart-v2.md`](../../orchestrator/prereg/contre-lecture-preenregistrement-attaque-goodhart-v2.md) (commit `53dd70b`) | `fe65f090c13a389648b28ce0abe4bd70354b610b0c54bf60e2408d7a4433b5e6` |
| Code of the run | 71 files, each frozen by its hash inside the preregistration; the launcher refuses any other code | in the text |
| Providers' configuration (private: model commands and relays) | frozen by its hash inside the preregistration; the launcher refuses any other | `e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30` |

## Replay without any key

From `orchestrator/`, the same harness with scripted proposers, no network and no cost:

```
python3 -I -B demonstrations/attaque_goodhart_v2.py OUT --a-blanc --graine 7 --cartes 1 --n-max 4 --rejeux-v8 3 --rejeux-v7 2 --rejeux-audit 3
```

It ran in 4 s here on 2 November 2026 (code 0, 36 simulated calls, 0 USD; sealed output and manifest in `OUT`). Section 9 of the preregistration reports the largest dry run, at the full grid in calls but with reduced replays. A scripted proposer reads the judge's description: W1 "resists (at this size)"; W2 is breached through the uncovered class, almost always at the first attempt. **This says nothing about a language model**: it shows the harness end to end, and how long it takes.

## Limits, written before the run

- The worlds are synthetic (3 outcomes, 2 Gaussian traits). Nothing here carries over to real model episodes.
- There are two providers and one grid.
- The finite bank reused from one attempt to the next is not played.
- A breach on W2 would not mean that the v8 null is flawed or that Ville's guarantee is beaten: the class is declared uncovered by the null itself. It would measure how fast a language model finds that hole, and how much the feedback adds.
- The real path has been tested only against a fake relay before this run.

## Where it stands

- **Sealed** on 2 November 2026. The run is launched by the session that holds the API keys, under GO-2026-11-02-07 (at most 80 USD). It ends after 2 November.
- **Then**: the output is sealed before any reading; it is read once under the frozen criteria; a fresh reader checks the verdict; the result is posted here, null or not. If the run stops on a guard, this page says so.

## Next: the closed round

The closed round is the generation loop closed with real sandboxed death tests. Its preregistration is at **draft 2**, public with the code of its first stage (commit `7d3aa82`: [`orchestrator/prereg/preenregistrement-tour-ferme-v1-brouillon2.md`](../../orchestrator/prereg/preenregistrement-tour-ferme-v1-brouillon2.md)), and a second fresh counter-reading of the text and the code is under way. **It is not sealed and has not been run**; its second stage is not yet written. This page will say when it is sealed.

Back to the [main README](../../README.md).
