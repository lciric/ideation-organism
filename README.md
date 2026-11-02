# Ideation organism — an automated research pole that cannot grade its own homework

**What it is.** A small, fully inspectable system in which language-model agents from several providers propose research hypotheses on AI control, and in which *none of the agents that produce an idea is allowed to decide whether it survives*. Ideas are scored by a frozen statistical judge against sealed predictions, screened by a gatekeeper that only looks at their *form*, checked for novelty, killed by preregistered "death tests" run in a sandbox, and selected from one generation to the next. Every artefact is hash-sealed before it is read; every decisive number is traced to a result file.

**Why it exists.** Automated researchers are useful only if they resist the two ways an optimiser games a research loop: *grading itself* (the proposer, the judge and the experimenter share a mind) and *drifting into the familiar* (the loop rewards what the judge already likes). This repository is one concrete answer, built and audited over October 2026 by a single researcher with AI coding agents under written rules, and it is published so that others can read the guards, run the offline demonstrations and try to break them.

**Status (1 November 2026).** Pre-pilot stage. One full ideation round has been run with real agents (29 idea cards, 17 distinct ideas). The statistical judge and its guards have been exercised on a real bank of model episodes and on planted worlds. The death-test stage and the generation-to-generation loop are implemented and tested offline but have **not yet been run for real**. Nothing here is a validated scientific result about AI control; it is an instrument, with its test suite, its mutation bench and its known gaps stated below.

```mermaid
flowchart LR
    P[Proposers<br/>Claude · Kimi · Argon] -->|idea cards| G{Gatekeeper<br/>form only}
    G -->|too concrete| V[(Sealed vault<br/>never read by agents)]
    G -->|method level| M[Anti-repetition<br/>memory]
    M --> J[Cross-provider judges<br/>blind to each other]
    M --> B[Bisociator<br/>three arms]
    B --> J
    J --> N[Novelty check<br/>arXiv · OpenAlex]
    N --> T[Death tests<br/>preregistered, sandboxed]
    T -->|survives| S[Selection<br/>next generation]
    T -->|eliminated| X[Archive<br/>with the verdict]
    S --> P
```

*Figure 1 — the journey of one idea. Every box that produces something is separated from the box that judges it; every arrow writes a hash-sealed record before the next box reads it. One arrow is not closed yet: the selection after the death tests exists in code from v57b, but the next generation does not read it yet (section 2, step 9).*

---

## Contents

1. [The problem, in one paragraph](#1-the-problem-in-one-paragraph)
2. [The journey of one idea](#2-the-journey-of-one-idea)
3. [How this system could fool you, and what stops it](#3-how-this-system-could-fool-you-and-what-stops-it)
4. [Evidence so far](#4-evidence-so-far)
5. [Run it offline in five minutes](#5-run-it-offline-in-five-minutes)
6. [Map of the code](#6-map-of-the-code)
7. [What is deliberately not here](#7-what-is-deliberately-not-here)
8. [Provenance and integrity](#8-provenance-and-integrity)
9. [Glossary (the code is in French)](#9-glossary-the-code-is-in-french)
10. [Citation, licence, contact](#10-citation-licence-contact)

---

## 1. The problem, in one paragraph

An automated research loop has three roles: someone proposes, someone experiments, someone judges. If one model plays all three, the loop optimises *the judge's taste*, not the truth, and a sufficiently capable agent learns to write what the judge rewards, to run experiments that confirm, and to report the number that passes. The design rule of this system is therefore mechanical, not moral: **the role that produces an artefact never holds the key that evaluates it.** Proposers write cards; a separate reader classifies their form; separate judges score them without seeing each other; a statistical criterion, written in orchestrator code and not in any agent, decides promotion against predictions sealed *before* the data existed; the experimenter runs in a sandbox with no network and no key; and the verifier is, by configuration, a model from a different provider family than the experimenter. The human (Lazar Ciric) sets the questions, signs the spending caps and the decision nodes, and reads the sealed registers; he does not touch verdicts.

## 2. The journey of one idea

| Step | What happens | Who or what does it | Where in the code |
|---|---|---|---|
| 1. Propose | An agent writes an *idea card* (`fiche`) with closed fields: hypothesis, predicted effect, the measurement that would kill it. Several providers propose in parallel so that no single family sets the style. | Claude, Kimi, Argon (Gemini) through adapters | `orchestrator/pole/ideation_v2.py`, `adaptateurs*.py` |
| 2. Gatekeep | A fresh reader session classifies each card by its **form only** — *method level*, *to be fixed*, or *too concrete* — and issues a passport. Cards that describe an attack concretely go, sealed, to a vault that no agent and no judge reads. The gatekeeping step can never be sacrificed to the budget. | Fresh model session, frozen prompt, one anonymous card per call | `pole/aiguilleur_v53.py` |
| 3. Remember | The memory indexes the archive and refuses repeats; it holds only whitelisted, redacted fields — never a key, never a verdict, never a witness card (a recognisable witness would stop measuring). | Orchestrator code | `pole/memoire.py`, `pole/caviardage.py` |
| 4. Judge (course) | Each card with a passport is scored by **each** judge of the configuration, one call per card per judge, fresh session, frozen prompt, opaque identifier — no judge sees another's score. | Cross-provider judges | `pole/juges_croises_v53.py` |
| 5. Marry | The *bisociator* pairs ideas with three arms — "far but close", a Gu-and-Krenn style "never linked" pairing, and a "shared structural hole" meta arm — so that the loop also explores what no proposer wrote. | Orchestrator code + a fresh session | `pole/bisociateur_v5[3-5].py` |
| 6. Check novelty | The harvester fetches metadata and abstracts only (arXiv, OpenAlex) and tags matches as non-opposable; an apparent gap in the literature is treated as a *question*, never as a claim. | Orchestrator code, relay only | `pole/moisson.py`, `pole/relais_moisson.py` |
| 7. Bet | For the test pole, a card commits to a **predictive law** over outcomes; its wealth process is computed against a library of blind predictors on *fresh draws seeded by the hash of the commitment*; promotion follows an e-value rule written in orchestrator code. | Orchestrator code, outside every agent | `pole/selection_pari.py`, `pole/engagement_apparie.py`, `pole/monde_banque.py` |
| 8. Kill | Death tests: the frozen card becomes a script, run in a sandbox (`bwrap`, no network, memory-capped, syscall-filtered, no key) on data already present; the prediction is sealed before execution; the verdict is "survives" or "eliminated" at a frozen threshold (from v57, computed by the orchestrator from the script's raw file; see section 3). | Sandboxed experimenter, then a verifier of another family | `pole/tests_de_mort_v[1-4].py`, `pole/garde_outils.py` |
| 9. Select | A card that "refines" another without changing statistic, layers, bound or threshold is refused. **Correction (1 November 2026):** up to v56, the next generation inherited from the judges' ranking, written *before* the death-test stage — no code read the death-test verdicts. v57b adds the selection point (only "survives" is kept, sealed in the stage's record), but the next generation does not read it yet. | Orchestrator code | `pole/etage_entre_generations_v5[3-6].py`, `pole/course2_v56.py`; selection point: `pole/etage_entre_generations_v57.py`, `pole/course2_v57.py` |

## 3. How this system could fool you, and what stops it

This is the table the project was built around. Each line names a way an automated researcher could game its loop, the guard that stops it, where the guard lives, and the test that exercises it on a healthy case *and* on an artefact (rule R5 of the project: a guard is only trusted once it has been seen to refuse something).

| The cheat | The guard | Where | Exercised by |
|---|---|---|---|
| The agent prints its own verdict | Promotion is decided by orchestrator code from sealed commitments and fresh draws (`selection_pari.py`). For death tests, the stage shipped in v56 reads the deciding statistic from the script's output — a weakness found by our own code review on 1 November 2026. **v57 and v57b, written the same evening:** a new stage (`tests_de_mort_v5.py`) takes each card's verdict only from the orchestrator's computation on the raw file that the sealed preregistration names — file, column, statistic and threshold come from the preregistration, never from the script, and a card without them is refused before any session; any incident of the card makes it "inconclusive"; the number the script prints, any `CALCUL:` line and the fresh reader are kept as witnesses only, and the experimenter's instruction now names the file to write and says the printed line is only a witness. Between generations, `course2_v57.py` plays this stage and keeps only "survives" through `selectionner`, which refuses any verdict without the orchestrator's label. **Still open:** tested offline only, with a simulated executor (no `bwrap`) and scripted agents — the real sandbox has not been run with this stage; the launcher (`demonstrations/ideation_v8.py`) and the ideation round (`ideation_v2.py`) still call the v56 stage; the selection is sealed but the next generation does not read it yet. | `pole/selection_pari.py`; `pole/tests_de_mort_v2.py` (lines 510–540); the fix: `pole/tests_de_mort_v4.py` (`verdict_du_noyau`, `selectionner`), wired by `pole/tests_de_mort_v5.py`, `pole/etage_entre_generations_v57.py` and `pole/course2_v57.py` | `essais/test_selection_pari.py`, `essais/test_v7_pari_apparie.py`; `essais/test_v57_verdict_noyau.py` (37 tests); `essais/test_v57b_cablage_verdict.py` (35 tests, end to end through the new stage: printed "survives" with a file saying "eliminated" → eliminated and not selected; no file → inconclusive; an incident → inconclusive although the file says "survives"; a healthy card → selected; the same scripts through the v56 stage give "survives" to the first two); `essais/mutations_v57.py` (19 of 19 killed) and `essais/mutations_v57b.py` (15 of 15 killed for the expected reason) |
| The judge sees the data before committing | The commitment (contrasts, thresholds, budget, seeds) is sealed before any outcome is read; the draws are seeded by the hash of the commitment itself. | `pole/engagement_apparie.py`, `pole/graines_v53.py` | `essais/test_v7_engagement_apparie.py` |
| The proposer learns the judge's taste | Judges are blind to each other and to earlier scores; the memory never serves verdicts or witness cards to agents. | `pole/juges_croises_v53.py`, `pole/memoire.py` | `essais/test_v53_instruments.py`, `essais/test_memoire.py`, `essais/test_memoire_v4.py` |
| A verdict or a class key is read before the end of the round | The *vault* (`Coffre`) stores verdicts and keys sealed and returns only a hash; any read before the declared end is logged as an incident and stops the orchestrator; v55 forbids in-memory copies and logs every permitted read with its reason. | `pole/coffre_v53.py`, `pole/coffre_v55.py` | `essais/test_v53_instruments.py`, `essais/test_v55_corrections.py` |
| The experimenter reaches the network, the host, or a key | Tool guard on every agent tool call (first barrier, pattern-based); real barrier: the sandbox with no network, a single directory, memory cgroup, seccomp filter, witness file checked on the host; environment variables of the disposable machine come from a **closed whitelist** (v56), not a blacklist. | `pole/garde_outils.py`, `pole/tests_de_mort_v2.py`, `pole/etage_entre_generations_v56.py` | `essais/test_v51_bac_reel.py` (needs `bwrap`), `essais/test_v56_corrections.py` |
| A secret leaks into the archive | Redaction of known key shapes before any write to archive, journal or memory (a last-resort guard with a stated limit: a secret of unknown shape passes). | `pole/caviardage.py` | `essais/test_adaptateurs.py`, `essais/test_v7_ideation_v2.py` |
| The loop silently falls back | No silent fallback anywhere: a missing field, an unknown model served, a cap reached, a signal — each stops the role or the run with a written reason; spend caps are recomputed twice and acknowledged at every stage. | `pole/noyau_v56.py`, `pole/budget_v56.py`, `pole/adaptateurs_v56.py` | `essais/test_v56_corrections.py` (64 tests), `essais/mutations_v56.py` |
| The dataset drifts under the test | A *closed folder*: the run may read exactly the files listed in a sealed manifest, no symlink, nothing more, nothing less. | `pole/dossier_ferme.py` | `essais/test_v7_ideation_v2.py` (closed-folder cases) |
| Witnesses are recognised and gamed | Planted witnesses (true and false laws) are mixed anonymously into every generation; they are indexed for audit and excluded from everything served to agents. | `pole/memoire.py`, `exemples/construire_banque_t05_v3.py` | `demonstrations/demo_couche1_v7.py`, `demonstrations/banc_tricheurs_v7.py` |
| The gatekeeper is skipped to save money | The gatekeeping step is marked *protected* in the spending plan and is never sacrificed; a card without a passport is refused by every downstream consumer. | `pole/aiguilleur_v53.py`, `pole/budget_v56.py` | `essais/test_v53_course2.py` |

### 3.1 We attacked our own judge: the cheaters bench

`demonstrations/banc_tricheurs_v7.py` is a bench of scripted cheaters against the statistical judge: each cheater is a card that tries to get promoted *without bringing a new true law* — by copying a survivor under a new name, mixing two survivors, tempering and tilting a survivor, dressing up a parent law, firing ten variants of a false law at once, and so on. Reading rules are fixed before the run (line → "must hold at ≤ α", "measured", "artefact must pass"). Rerun in this tree on 1 November 2026 (seed 20261101, 200 repetitions per line, 5 min 15 s on 4 cores; exploratory, not the decisive 1 000-repetition validation):

| cheater | judge with the plain archive null ("v7" setting: what the offline demonstrations still use) | with the pooled null (`nul_archive_ajuste`: fitted pooling of all known laws, implemented in `pole/cycle.py` and already the default of the `pole.py` command line) |
|---|---|---|
| T01 parent + blind law, T03u survivor + uniform, T17s renamed copy of a survivor, T09g parent⁶, T09l λ-mixture, T12a deformed parent, exact null | **0 / 200 each** — held | — |
| T02 hidden copy ½ parent + ½ survivor | **promoted 75 %** — the judge is beaten | 0 / 200 |
| T03b survivor + Dirichlet blind law | **promoted 85 %** — beaten | 0 / 200 |
| T04 mixture of two survivors | **promoted 95 %** — beaten | 0 / 200 |
| T05s tempered and tilted survivor | **promoted 80.5 %** — beaten | 0 / 200 |
| T07 composition (mix, then power, then tilt) | 3 % (measured) | 0.5 % |
| T14 ten variants of one false law, T15 twenty copies | at-least-one promoted: 0.5 % and 0 % under the e-BH rule (8 % and 17 % per card without it) | — |
| power on genuinely new laws (daughter, fresh) | 0.97 / 1.00 | 1.00 / 0.99 (loss −0.03 / +0.01) |
| artefact: T01 under the old "v1" null | promoted > α — the bench has teeth | — |

What this says, plainly: **without the pooled null, the judge is beaten by four cheats that recombine what the archive already accepted**; the pooled null closes all four at a power cost under 0.05. Reproduce: `python3 -I -B demonstrations/banc_tricheurs_v7.py OUT --graine 20261101 --repetitions 200 --processus 4`, then read `lecture` in `OUT/banc-tricheurs-v7.json`. The output of this run, with its manifest and `.sha256` seals, is in `resultats/banc-tricheurs-v7-2026-11-01/`.

**Since v58 (1 November 2026) the pooled null is the judge's only null** (`pole/nul_v8.py`; the offline demonstrations rerun under it, `demo_couche1_v8.py` and `demo_couche1_proposeur_v8.py`, give the same verdicts as v7 card by card), and its **decisive validation** was preregistered, counter-read, sealed (`orchestrator/prereg/preenregistrement-validation-nul-v8-v2.md`, sha256 `7f37631d4f5de481d618bba151eed9d7fe30e38a6276cbbd0d2397babc0de4c5`; seed derived from that hash) and run once, at commit `1bad95f` (`demonstrations/banc_tricheurs_v8.py`, 1,000 repetitions per line, 52 min on 2 cores):

| line (under the v8 null) | result | rule frozen before the run | status |
|---|---|---|---|
| the 11 fatal lines: T01, T02, T03u, T03b, T04, T05s, T09g, T09l, T12a, T17s, exact null | **0 of 1,000 each** (Clopper-Pearson upper bound 0.003) | promoted at ≤ α = 0.05, Holm-corrected bounds | held |
| artefact: T01 under the old v1 null | 395 of 1,000 | must be promoted at > α (the bench has teeth) | held |
| power on genuinely new laws, daughter / fresh | 0.983 / 0.978 under v8, against 0.988 / 0.998 under v7 (loss 0.005 / 0.020; Newcombe upper bounds 0.014 / 0.029) | loss ≤ 0.05 | held |
| T07 composition of three steps (outside the covered class) | 1.6 % | measured, no threshold | — |
| T12b deformed parent when the world is that deformation (the card is right) | 90.3 % | measured, no threshold | — |

The frozen reading computed by the code says **"confirmed"**, with no audit trigger; every prediction written before the run held (they were written after declared exploratory runs, so their success adds little). A fresh reader recomputed every component from the raw counts and confirmed the outcome with two minor reservations: (1) T12a, the one fatal line not refused by construction, crossed the 1/α wealth mid-run in 4 of 1,000 repetitions and was stopped by the daughters' margin at the final read, so it is held by Ville's bound *joined with that margin*; (2) the preregistration asked to replay the 35 tests and the mutation bench on the sealed tree between the push and the run, and the run started 7 s after the push without that replay (the code was byte-identical to the tree on which a counter-reader had run them; replayed afterwards on the identical tree: 35 of 35 tests passed and 34 of 34 mutations killed for the expected reason — the deviation is recorded in `ecart-section13-v2.md`). Outside the frozen criteria, the reader also checked that the zeros come from the pooled null: on 60 paired repetitions, T02, T03b, T04 and T05s are promoted 49, 48, 56 and 50 times under v7 and 0 times under v8. **Scope**: the bench's synthetic worlds (3 outcomes, 2 traits) and this class of cheats — nothing about piecewise recombinations, compositions of steps, multiplicity across cards, power at weak effects, or the real bank. Outputs, seals, launch log and the reader's verdict: `resultats/banc-tricheurs-v8-validation-v1/`.

The **mutation bench** (`essais/mutations_v56.py`, extended by `essais/mutations_v57.py`, `mutations_v57b.py` and `mutations_v58.py`) is the meta-guard: deliberate code mutations (removing a check, flipping a comparison, swallowing an exception), each of which must be killed by the test suite *for the expected reason*. In the last run before publication, all 156 mutations of v54–v56 were killed, none survived, none was killed for a wrong reason; the 19 mutations of v57 (for example "read the script's number instead of the file", "rank inconclusive as survives") and the 15 of v57b (for example "the stage reads `RESULTAT:`", "an incident is ignored", "the selection keeps inconclusive") were all killed for the expected reason on 1 November 2026, as were the 34 of v58 (the pooled null as the only null). The bench says nothing about guards that do not exist — which is why the first line of this table is written the way it is.

## 4. Evidence so far

All numbers below come from sealed run records in the private working repository (hashes in `orchestrator/EMPREINTES-orchestrateur-pole-v7-v56.txt` for the code; private run manifests not published) or from runs you can reproduce here; the outputs of the runs made in this tree on 1 November 2026 are published, sealed, in `resultats/`.

| What | Result | Reproducible here? |
|---|---|---|
| Test suite in this public tree (1 Nov 2026, 23:31 UTC, commit `2cfb940`, Python 3.13, numpy 2.5; real-sandbox tests declared not played with `POLE_ESSAI_BAC_REEL_NON_JOUE=1`) | **906 passed, 8 failed, 15 skipped, 669 subtests passed** (929 tests) in 11 min 10 s on 2 busy cores. The 8 failures are all provenance or environment checks: 7 look for release notes or hash lists of older versions that are not shipped here (`TestR12*` ×3, `test_v49_18`, `test_v50_17`, `test_v51_10`, `test_v51_15`), 1 expects a refusal message that the missing sandbox binary `bwrap` pre-empts (`test_v51_06`). No functional test fails. Without the variable, the 12 real-sandbox tests fail on purpose instead of being skipped (never ignored in silence): 906 passed, 20 failed, 3 skipped. Both outputs, sealed: `resultats/suite-essais-2026-11-02/`. | Yes — section 5 |
| Mutation benches | 224 mutations (v54–v56: 156; v57: 19; v57b: 15; v58: 34), every one killed for the expected reason, 0 survivors (v58 replayed on 1 Nov 2026, 23:35 UTC, after the decisive run) | Yes — `python3 -I -B essais/mutations_v56.py` (slow), then `mutations_v57.py`, `mutations_v57b.py`, `mutations_v58.py` |
| Statistical judge on planted worlds | 8 of 8 true witnesses promoted, 0 of 8 false witnesses promoted (both proposer arms); the hoped-for advantage of exploratory proposers did not show (1 promoted card in each arm) | **Yes, reproduced in this tree on 1 Nov 2026 in 41 s**: `python3 -I -B demonstrations/demo_couche1_proposeur_v7.py OUT --generations 4`, then read `resultats/plante-*/temoins` in the output JSON |
| Statistical judge attacked by 27 scripted cheaters: decisive validation of the v8 null (preregistered and sealed; 1,000 repetitions per line; 1 Nov 2026) | 0 of 1,000 on each of the 11 fatal cheats; the old null's artefact promoted 395 of 1,000 (the bench has teeth); power cost on new laws 0.005 and 0.020; frozen reading "confirmed", confirmed by a fresh reader with two minor reservations (section 3.1) | Yes — `python3 -I -B demonstrations/banc_tricheurs_v8.py OUT --preenregistrement prereg/preenregistrement-validation-nul-v8-v2.md --repetitions 1000 --processus 2` (≈ 52 min on 2 cores; same seed, same numbers); outputs in `resultats/banc-tricheurs-v8-validation-v1/` |
| Real engine, end to end (real model calls, 27 Oct 2026), in a deliberately tautological world (the true witness's law *is* the world's law) | 2 true witnesses promoted, 2 false eliminated, 11 of 11 replays identical — this checks the plumbing, not the judge's power | No — real API calls; records private |
| Statistical judge on a bank built from real episodes (120 rated episodes — 60 tasks × 2 — from a pilot of 180 episodes of an 8-billion-parameter model; 13 monitors from two LLM judges of 3 and 8 billion parameters) | a planted witness of strength 0.5 was recovered in one run (144 test episodes per card; the power curve in the next row puts that cell at 0.71); on the bank's 13 **real** monitors, **nothing promoted** (0 of 20 true witnesses; each real monitor is judged on 41–62 instances; at 288 episodes the best wealth reached 2.28 against a threshold of 3.0) — which the preregistered reading rule calls "no teeth, no conclusion" | The real-monitor part, yes: same command, `resultats/reel-*` (0 of 20 true witnesses promoted, reproduced 1 Nov 2026); the strength-0.5 run, not in this tree |
| **Power of the judge on this bank** (planted laws on the real episodes' features; 500 repetitions per cell; exploratory: the reading was dated in the script before the run, not sealed) | With the judge as frozen (plan of 120 instances, e-BH over 17 cards): strength 0.8 is promoted 95 % of the time at 120–180 test episodes; strength 0.5, 65–73 %; strength ≤ 0.3, at most 24 % up to 180. False witnesses: no cell above 5 % (worst 1.8 % per card, ≤ 0.1 % under e-BH). At the 41–62 instances of the real monitors, even strength 0.5 is promoted about one time in six, so **"nothing promoted" does not exclude effects of that size**. One prediction written before the run failed (≥ 0.8 at strength 0.5 and 144 episodes: measured 0.71 [0.66, 0.75]). Found on the way: with the plan frozen at 120, more episodes can *lower* power (0.95 → 0.81 at strength 0.8 from 180 to 600 episodes, partly an artefact of resampling the 120 real episodes): the selector keeps instances where the law always predicts the same outcome, and the null's empirical-marginal member then absorbs the effect; a plan that takes the whole test split reaches 0.9 at strength 0.5 near 233 test episodes. Strength in plain units: at one standard deviation of the trait, strength 0.5 moves P(outcome 2) − P(outcome 0) by 0.32, about 0.06 nat of information per episode. | Yes — `python3 -I -B demonstrations/puissance_juge_banque_v1.py OUT --repetitions 500 --processus 2 --graine 20261101` (≈ 15 min on 2 cores); output, seals and the two annex outputs in `resultats/puissance-juge-banque-v1-2026-11-01/`; annex scripts in `demonstrations/annexes_puissance_v1/` |
| **Fresh-seed reading of the real bank** (2 Nov 2026: the 96 tasks re-run with new seeds, 3 episodes each, 288 episodes rated by the same two LLM judges; reading preregistered and sealed before any rating existed, run once, checked by a fresh reader) | Outcome I1, "valid and with teeth, no real law promoted": 0 of 19 false witnesses promoted (noise traits, permuted outcomes) under both plans; witnesses planted on the real episodes' features promoted 3 of 3 with a plan that takes the whole test split, 2 of 3 with the frozen plan of 120 (the weakest, strength 0.3, was promoted on a favourable draw, probability about 0.30 for its pair of traits: not evidence of power at that strength); none of the 13 real monitors' laws (episode features → judge score) promoted. Bound, monitor by monitor: a law of the planted form carrying 0.057–0.117 nat per episode would be promoted with probability 0.9 (121–262 instances per monitor). Limits: no true real witness exists to test the judge on real links; the tasks are those of the calibration bank, so nothing carries over to new tasks; weaker links, or links of another form, can pass under the bound. | No — real episodes and ratings stay private. The sealed preregistration (`orchestrator/prereg/preenregistrement-lecture-t05-graines-neuves-v2.md`, sha256 `93923d71…`) and the reading script (`demonstrations/lecture_t05_graines_neuves_v1.py`) are here; the output is sealed in the private working repository (`lecture-t05-graines-neuves-v1.json`, sha256 `07bc2aea97ba8cc9ce2547cdb5c31b212971a977481d86ebd2c8caf36350ecb4`; fresh reader's verdict `33a75703907aaadcb1aa9e950e0d0ce89a9639e3833dc8ab434cebd09a9f4f7b`) |
| First ideation round with real agents (Claude, Argon) | 29 idea cards, 27 eligible after the gatekeeper, 17 distinct ideas (12 duplicate pairs) | No — real API calls; records private |
| Second real round (1 Nov 2026, preregistered; Kimi and Argon only, one generation, without the bisociation board; 62 model calls, 1.47 USD; every number descriptive, at most 13 cards) | All stages ran (proposal, gatekeeper, label readers, one fusion, judges); 12 cards classified; anti-leak check clean. **The two LLM judges sat at their ceiling**: 11 of 12 cards rated "notable" (one judge rated 12 of 12, the other 11 of 12), raw agreement 0.92 but Cohen's κ = 0 — at this ceiling the judge stage does not discriminate between cards. Judge of the author's own family vs the other family: 1.00 vs 0.91 "notable" (gap 0.09 on 11 cards; with two families only, every card had a judge of its own family). This is a weakness of the instrument, not a finding about the ideas: the judge stage needs a harder rubric or anchored reference cards before its ratings carry information | No — real API calls; cards private. Aggregated trace sealed in the private working repository (sha256 `091ff9edefec3faa411ae786a28595c5d3648e1b7aa4c425d290a3e64544338a`; preregistration `6fcb1035aa46be34caba9b381b1f9bf0a054fc6d3e9b4430b18e680c101c7481`) |
| **White-box versus black-box monitors on real activations (R1, control programme)** (Llama-3.1-8B, 60 tasks, 2,400 scored actions: probes versus small LLM judges of 3 and 8 billion parameters and a simple cost rule) | **Not in yet.** Three analyses sealed before the data (hashes on the status page). The activation replay stopped on its own fidelity guard; a seeded replay, then one rerun, are being prepared, each sealed before it runs. The result, null or not, will be posted on the status page once read and checked by a fresh reader. | No — real model runs, records private; status page: [`resultats/controle-r1-blanche-noire/`](resultats/controle-r1-blanche-noire/) |
| **Goodhart attack on the judge (A1)**: language-model proposers that see the verdicts, against a witness arm without them; two toy worlds where every promotion is false (W1 inside the v8 null, W2 in a class the null declares uncovered); 12 cards per world, two providers, up to 16 attempts | **In (2 Nov 2026), with a correction and a clean rerun announced.** W1 (inside the v8 null): not judgeable (instrument failure: the Kimi arm was lost to a shared spending cap, not to the model). W2 (outside the null): breach under v8 through the class the null itself declares uncovered (Argon promoted in 12 of 12 units). Audited in writing, verdict by a fresh reader; deviations, correction and hashes on the status page; a clean rerun (Argon alone, corrected instrument) is being preregistered. | The harness, yes, without any key (scripted proposers: command on the status page); the real run, no (API calls). Status page: [`resultats/attaque-goodhart-v2/`](resultats/attaque-goodhart-v2/) |
| Death tests and generation-to-generation loop | Implemented, tested offline, **never run for real** | — |

What this does *not* show: that the ideas are good (in the second real round the LLM judges sat at their ceiling and did not discriminate), or that the real monitors carry no signal — on a bank of this size the frozen judge cannot see effects below strength 0.5 (power row above), and on the fresh-seed reading of 288 episodes a monitor's law under 0.06–0.12 nat per episode could still pass unseen. The pole has not yet promoted a real hypothesis to the test stage; the first measured result of the programme that hosts this system (a preregistered simulation on adaptive defences, 1 November 2026) was produced outside this loop. That is the honest state of the instrument.

## 5. Run it offline in five minutes

Requirements: Python ≥ 3.11, `numpy ≥ 1.25`, `pytest`. No API key, no network: the agents are simulated, and a fake Claude Agent SDK (`essais/faux_sdk/`) imitates the real one's interface without any model call.

```bash
git clone https://github.com/lciric/ideation-organism
cd ideation-organism/orchestrator
python3 -m pip install numpy pytest

# 1. The quick check (64 tests, ~30 s; 63 run and 1 skipped here, a provenance check against a manifest not shipped): the v56 guards on healthy cases and on artefacts
python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v56_corrections.py

# 2. The statistical judge on the real episode bank, agents simulated (~30 s, writes a sealed JSON + .sha256)
python3 -I -B demonstrations/demo_couche1_v7.py /tmp/demo-couche1 --generations 2

# 3. The full suite (~6 min; the sandbox tests are declared not played)
POLE_ESSAI_BAC_REEL_NON_JOUE=1 python3 -I -B -m pytest -q -p no:cacheprovider essais/

# 4. The mutation bench (slow): every mutation must be killed for the expected reason
python3 -I -B essais/mutations_v56.py --v56-seulement
```

Expected output of step 2: a file `demo-couche1-v7-v3.json` with its `.sha256`, the promoted cards per arm (`promues_par_bras`) and the reading rules L1–L4 evaluated as written *before* the run in the script's docstring. Step 1 is also what the continuous integration runs on every push.

To run the real engine you need provider keys, a spending-cap line signed in a register, and the sandbox binary `bwrap`; the launcher refuses to start without them (`demonstrations/ideation_v8.py --help`). That refusal is by design.

## 6. Map of the code

```mermaid
flowchart TB
    subgraph core["pole/ — the orchestrator (French)"]
        direction TB
        n56[noyau_v56.py<br/>run loop, spend caps, stop on signal] --> n55[noyau_v55] --> n54[noyau_v54]
        c56[course2_v56.py<br/>ideation round] --> c55[course2_v55] --> c54[course2_v54] --> c53[course2_v53]
        pp56[prepilote_v56.py<br/>pre-pilot stage]
        g56[gardes_e0_v56.py<br/>guard table replayed at start] --> g55[gardes_e0_v55] --> g54[gardes_e0_v54]
        b56[budget_v56.py] ; a56[adaptateurs_v56.py] ; e56[etage_entre_generations_v56.py]
    end
    subgraph judge["judge & memory"]
        sp[selection_pari.py<br/>e-value bets] ; ea[engagement_apparie.py<br/>sealed commitment] ; mb[monde_banque.py<br/>frozen episode bank] ; me[memoire.py] ; ai[aiguilleur_v53.py<br/>gatekeeper] ; jc[juges_croises_v53.py]
    end
    subgraph kill["death tests & sandbox"]
        tm[tests_de_mort_v3.py → v2 → v1] ; go[garde_outils.py] ; df[dossier_ferme.py] ; cv[caviardage.py] ; co[coffre_v55 → v53<br/>sealed vault]
    end
    subgraph entry["entry points"]
        i8[demonstrations/ideation_v8.py<br/>launcher, delegates to v7…v4] ; d1[demonstrations/demo_couche1_v7.py] ; bt[demonstrations/banc_tricheurs_v7.py]
        t[essais/ — 929 tests<br/>faux_sdk/ fake SDK<br/>mutation benches]
    end
    entry --> core --> judge
    core --> kill
```

*Figure 2 — versions are layered, never edited.* The project's rule R12 ("a new version is a new name; nothing is overwritten") is why `noyau_v56` inherits from `noyau_v55`, which inherits from `v54`: each version adds a correction from an independent counter-reading (twenty of them, CL1 to CL20, each with a table "finding → file:line → test → mutation"), and the older file stays byte-identical so that every past run remains reproducible against its manifest. The cost is readability; the benefit is that provenance never breaks.

| Directory | Contents |
|---|---|
| `orchestrator/pole/` | the orchestrator: run loop, spending caps, gatekeeper, memory, judges, bisociator, harvester, statistical judge, death tests, sandbox guards, vault |
| `orchestrator/essais/` | 45 test modules (929 tests, 669 subtests), the fake SDK (`faux_sdk/`), the mutation benches |
| `orchestrator/demonstrations/` | offline demonstrations and the launcher (`ideation_v8.py`) |
| `orchestrator/exemples/` | the frozen episode bank of the T0.5 pilot (`banque-t05-v2.json`), planted witnesses, generated toy worlds, a scripted proposer |
| `orchestrator/conception-v7-v1.md` | the design document that precedes the v7 code (French) |
| `orchestrator/EMPREINTES-orchestrateur-pole-v7-v56.txt` | SHA-256 of every file of the v56 tree as it exists in the private repository |
| `pont-fiche-loi-v1/` | the bridge that translates an idea card of the ideation round into the predictive-law card the test pole bets on (code, 77 tests, French LISEZMOI; the design note is withheld, see `MANIFEST.md`) |

## 7. What is deliberately not here

- **Attack-side content.** The programme that hosts this system studies AI control, so some idea cards describe attacks too concretely to publish. Those cards never enter the memory or the judges: the gatekeeper sends them, sealed, to a vault held by a separate session. Nothing from that vault, and no file whose content is an attack, is in this repository. The modules named `coffre_*` (vault) and `bras_attaque_v54.py` are mechanism only: the first store sealed verdicts and keys and enforce the non-reading rule; the second is a stub that *refuses* to run because the interface it would need was never specified. An external security review of the offensive parts of the programme was done in October 2026 by the executive director of CeSIA (Centre pour la sécurité de l'IA).
- **Data under quarantine**, work registers, spending records, verbatim decisions of the director, and the private preregistrations of the pre-pilot. The spending-cap lines that appear in tests (`GO-2026-…`, `45 USD`) are fixtures of the cap-checking code, not records.
- **Older versions' archives** (v1–v55 zips and manifests). Their hashes are listed in the v56 manifest, so the chain is verifiable without shipping them.
- **Anything that runs for money.** The real engine needs keys and a signed cap; neither is here.

## 8. Provenance and integrity

- Every file in `orchestrator/` and `pont-fiche-loi-v1/` either carries a companion `.sha256` or is listed in `orchestrator/EMPREINTES-orchestrateur-pole-v7-v56.txt`. Verify: `cd orchestrator && sha256sum -c --quiet EMPREINTES-orchestrateur-pole-v7-v56.txt` (lines for files not shipped here — older-version archives — will report "No such file"; everything shipped must report OK).
- The tree is an exact extract of the private working repository `controle-ia-travail` at commit `91a3c7f8` (1 November 2026); `MANIFEST.md` lists what was copied and what was excluded, with reasons.
- Seeds: every stochastic step derives its seed deterministically and the run manifest states the rule. The core of the pole (v0–v52b) and the cheaters bench v7 derive seeds from SHA-256 of labels in the standard library (`pole/outils.graine_derivee`); from v53 on, new modules use `numpy.random.SeedSequence` keyed by the task name (`pole/graines_v53.py`), as does the power curve.
- The twenty counter-readings (CL1–CL20) that produced the version chain were done by fresh model sessions that had not written the code; their finding tables are in the French LISEZMOI files of the private repository and summarised in `conception-v7-v1.md`.

## 9. Glossary (the code is in French)

| French, as in the code | Meaning |
|---|---|
| fiche | idea card (closed fields) |
| aiguilleur, douane | gatekeeper (classifies by form; issues passports) |
| coffre | sealed vault (verdicts, keys; non-reading rule) |
| juge figé, sélection par pari | frozen statistical judge; selection by sealed bets (e-values) |
| témoin vrai / faux | planted true / false witness law |
| tests de mort | death tests (preregistered, sandboxed) |
| pôle | test pole (the stage that bets and kills) |
| course (d'idéation), génération | ideation round, generation |
| bisociateur | bisociator (marries ideas; three arms) |
| moissonneur | harvester (novelty check from arXiv/OpenAlex metadata) |
| engagement, gel, scellé | commitment, freeze, sealed (hash written before reading) |
| garde, artefact, cas sain | guard; artefact it must refuse; healthy case it must accept |
| relais, adaptateur | relay, provider adapter |
| essais, banc de mutations | tests, mutation bench |
| machine jetable | disposable machine (whitelisted environment for the test stage) |
| R12, R5, R9 | project rules: never overwrite (new version = new name); every guard tested on a healthy case and an artefact; seeds by SeedSequence |

## 10. Citation, licence, contact

Lazar Ciric, *Ideation organism: an automated research pole for AI-control hypotheses*, 2026, https://github.com/lciric/ideation-organism (see `CITATION.cff`).

No licence is attached for now: the code is published to be read, run and audited; reuse beyond that needs the author's agreement. Contact: lciric@ens-paris-saclay.fr.
