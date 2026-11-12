# Smallest real run of the full loop (organism v66, then v67) — status of 12 November 2026

**Outcome so far: "not judgeable (stop)", twice.** Two real runs under the sealed text v1, on 12 November 2026, both stopped at the first proposer call, before any generation was played. The frozen reading of both relays returns outcome C5, *non jugeable (arrêt)*. Nothing about the loop's behaviour with real agents can be read from them. No fresh reader's verdict has been given yet; the phrase below is the output of the frozen reading program, copied as it came.

> Issue C5 : « non jugeable (arrêt) » — course reel (decisif) (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte).

## What the run is meant to test

Whether the full loop (proposers, sealed commitments, the frozen statistical judge with the v8 null, death-test stage, selection read by the next generation) keeps its offline properties with real agents: on the toy world S-V1, inside the class the v8 null covers, it must let at least one planted true law survive, promote no planted false law, and have generation 2 judge with generation 1's selection. Real arm only, one and a half generations, proposers Kimi (`kimi-k3.1-pro`) and Argon (`gemini-4-argon`), the experimenter Kimi and a verifier of the other family (Argon, witness only), all behind local relays with their own spending caps (33 and 7 USD). The design, predictions, frozen reading (outcomes C1 to C7, checks V-1 to V-8) and every hash are in the sealed texts:

| text | file | sha256 |
|---|---|---|
| v1 (runs of 12 Nov, code v66, configuration v6) | [`orchestrator/prereg/preenregistrement-boucle-reelle-organisme-v1-v1.md`](../../orchestrator/prereg/preenregistrement-boucle-reelle-organisme-v1-v1.md) | `46d7545b489a2037ede235d843ef8a0c504461a0a2d697af5db40de2400fd89d` |
| v2 (deviation 1: code v67, configuration v8) | [`orchestrator/prereg/preenregistrement-boucle-reelle-organisme-v1-v2.md`](../../orchestrator/prereg/preenregistrement-boucle-reelle-organisme-v1-v2.md) | `80fe4f03b4905b2376b8cd16873c9ab93da3b97e4e01a9a2932be329bab0954d` |

Both are copied byte for byte from the private working repository (French). The planted laws of this run are written in the sealed text, as the text itself requires; they are never served to the proposers during a run (guard 23 of the text checks the served view before each call).

## The code, now on `main`

The commits the runs name are on `main` with their original hashes (merged, not rewritten): `cef5ea6` (v65), `838fa68`, `3ba4727`, `7e415cb` (v66, the code of both runs), `ab53b7f` (v67). Before this merge, `cef5ea6` and `7e415cb` existed only in the private repository, which stopped one attempt before any machine was rented (see below).

## The runs

| | run 1 | run 2 |
|---|---|---|
| time (UTC) | 12 Nov 2026, 00:20:25 → 00:20:27 | 12 Nov 2026, 08:09:02 → 08:34:56 |
| code, configuration, text | `7e415cba`, configuration v6, text v1 | same |
| preliminaries of section 12.3, on a fresh disposable machine | tests 322 passed, 5 skipped; 133 of 133 mutations killed for the expected reason; offline dry run in the real sandbox, reading C1 | same |
| launcher | exit code 3 at the first proposer call | exit code 3 at the first proposer call |
| cause | the Kimi relay's upstream answered HTTP 429 | the upstream answered 200 after 1,553 s, but the proposer's reply was cut by its output bound: 46,714 output tokens, 46,711 of them reasoning; the Kimi command exits in code 5 ("truncated or empty"), which the text treats as a stop for a proposer |
| Argon calls | 0 | 0 |
| model spend (relay's count) | 0.499998 USD, counted at the worst-case reserve (no usage returned) | 0.481706 USD |
| frozen reading | C5, "not judgeable (stop)" | C5, "not judgeable (stop)" |
| relay record, sha256 | `c9c6212bfe16b148e5df42c27a1f631eeafbd79ca9c7b82ac048fabce69c3069` | `5a7fc27c7dfb1c7e0911cf9df3aa0b1c785e386bfa32de0294625c5709d52b9b` |
| reading, sha256 | `7de89198c7ec7838ec66ff256cb3c729c81fea3bf6a3410635c9bc18c2333d82` | `edae8c4f4cdaac2aec90079ff0c55637c2750d3d5d8c01337ed8a53237fd5323` |

**Deviation, stated by the run report itself:** section 10 of text v1 asks for a new counter-read text before any resumption after a relay outage. Run 2 was resumed without one, on the project lead's direct authorisation in the session; code, configuration, text and spending line were unchanged, and the preliminaries were replayed in full on a new machine. A further request to lift the output bound and rerun was **not** executed, because the bound is part of the frozen configuration: that change went through a new text instead (below).

Two earlier attempts stopped before any model call: on the night of 10 to 11 November, from a cloud session whose network closes outbound port 22 (machine created and destroyed after 3 min 55 s); and on 11 November at 23:49 UTC, from the project lead's own computer, because commit `cef5ea6` was not reachable outside the private repository (no machine rented).

Spend under the run's spending line, as reported: about 0.21 USD of machines (three disposable machines) and at most about 0.98 USD of model calls, about 1.19 USD at most, against a cap of 45 USD.

## Deviation 1 and the third attempt

The second stop showed that lifting the output bound was not enough: the v66 code stopped every external command at 1,800 s whatever the configuration said. Text v2 (sealed on 12 November after a counter-reading and a short verification of the difference, both by fresh readers, Claude Fable 5.2) changes only:

1. **code v67** (`ab53b7f`, parent `7e415cb`): two new files, `pole/adaptateur_commande_v67.py` (each external command's adapter receives the configured delay; guard 24: finite, positive, at most 7,200 s, and the command's own `--delai-s` at least 30 s below it) and `demonstrations/boucle_reelle_v67.py` (the v66 launcher with that wiring), with their tests and mutation bench; no v66 or older file is modified;
2. **configuration v8** ([`orchestrator/exemples/configuration-boucle-reelle-v8.json`](../../orchestrator/exemples/configuration-boucle-reelle-v8.json), sha256 `eb6262890927bfc351bf2a32c21d0dcf121445256a5ebe6c4eaee70b9265b31d`): proposer session cap 0.5 → 1.5 USD; Kimi's maximum proposer output 65,536 → 131,072 tokens, command delay 1,750 → 7,150 s, adapter delay 1,800 → 7,200 s; Argon unchanged;
3. the Kimi relay's upstream and silence delays raised (7,200 s and 1,800 s);
4. in the frozen plan, only the configuration hash and the spending line.

The reading criteria are unchanged; the text says the next report must call it the third attempt under this design and report the three records together. That attempt has been authorised; no result of it is reported here.

## Files in this folder

Copied byte for byte from the private working repository, each with its `.sha256` companion:

- `rapport-course-v66-poste-local-v1.md`, `rapport-course-v66-poste-local-v2.md` — the two run reports (French), as written by the operating session;
- `poste-local-v1/`, `poste-local-v2/` — for each run, the relay record written by the launcher (`boucle-reelle-v66.json`) and the frozen reading of it (`lecture-course-reelle.json`). In the reports, the record is named `course-reelle/boucle-reelle-v66.json`.

Not here: the raw journals of the provider relays and the console logs of the machines (provider logs are not published), the run manifests and spending registers, the machine sheets, and the two earlier stop reports (one names the address of a destroyed machine). Their hashes are in the private repository.
