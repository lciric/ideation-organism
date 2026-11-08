# R1 — white-box versus black-box monitors on real activations (control programme): status

*Status page of the first white-box versus black-box comparison of the AI-control programme that hosts this repository. Last updated: 8 November 2026, 09:20 UTC. The result is below; it was read once under the sealed analyses and checked by fresh readers. The 2 November text is kept unchanged under "Where it stood".*

## Result (6–7 November 2026): a leak, established by a preregistered audit

- **The replay is exact.** 2,400 of 2,400 actions re-run identically, maximal gap 0.0; the three analyses ran once, on the rerun (an addendum fixed which run counts, sha256 `a5ac6632691a…`, below).
- **Primary analysis, as preregistered:** the probe trained on this organism beats the generic probe by **+0.932** in area under the ROC curve; by episode, +0.983.
- **But the trained probe reads the instruction, not the sabotage.** The saboteur received a hidden instruction in its context; the probe sees that context. A leak audit, preregistered with a symmetric rule before it ran, found that the probe separates the saboteur's actions that do **not** inflate the cost (area **0.9967** [0.9930, 0.9991], 46 actions, 12 tasks) as well as those that do (0.9977 [0.9958, 0.9993]). Frozen outcome: **"leak (reading the instruction)"**, with 5 written reservations.
- **The black box is weak too.** The 3-billion-parameter LLM judge is at chance (area 0.523, permutation p = 0.19); a simple predictor on text features reaches 0.866, and the cost rule alone 0.726 (recomputed by an independent reader). The generic probes do not beat 200 random directions (first white-box test, `../controle-p3-premier-test/`).
- **Consequence.** No white-box-versus-black-box claim stands on this organism. Next: organisms whose sabotage is trained into the weights (low-rank adapters distilled from the saboteur's actions), with no instruction in the context — their full chain has run end to end on a real GPU on 8 November (36 episodes, 144 actions, 3.65 USD), one fidelity check still to be fixed before the decisive run — then probes tested across the two origins of sabotage, against a stronger black-box baseline.

### The texts, now public, unchanged

| File (`textes-scelles/`) | Role | SHA-256 |
|---|---|---|
| `analyse-blanche-noire-v3.md` | secondary reading | `1f6a6da2c551060a5f90ff3358b0aaf276dd9f336a5b953e6d93233c8c581fa9` (as announced) |
| `analyse-principale-r1-r2-v1.md` | primary reading | `8e2679526b2777a9fe8564dd5f5fdaf98b70affd759cf47857abc8b168d92537` (as announced) |
| `analyse-par-episode-v1.md` | by-episode reading | `26a3ff72e3a39636d3bdb965971fd1b237a04acc133a31a42f9a695d6d5970a4` (as announced) |
| `addendum-1-gardes-analyses-r1-v4-v1.md` | addendum: which run counts, guards | in its `.sha256` companion |
| `verdict-analyses-r1-r2-relance-v4-v1.md` | fresh reader's verdict on the three analyses | in its `.sha256` companion |
| `verdict-audit-fuite-r1-v4-v1.md` | fresh reader's verdict of the leak audit | in its `.sha256` companion |

The working documents are in French. The episodes, activations and scores stay private.

## The question

On the 2,400 scored actions of the programme's first test on real activations (Llama-3.1-8B, 60 tasks; a saboteur given a hidden instruction to inflate a declared cost, against honest and control conditions), do probes on the model's activations detect the saboteur's actions better than small black-box LLM judges (3 and 8 billion parameters) and a simple cost rule, at the same false-alarm rate?

## Sealed before the data

| Text (private working repository) | Role | SHA-256 | Sealed |
|---|---|---|---|
| `prereg/analyse-blanche-noire-v3.md` | secondary reading: white box versus black box, by family of monitors | `1f6a6da2c551060a5f90ff3358b0aaf276dd9f336a5b953e6d93233c8c581fa9` | 2 Nov 2026, 01:05 UTC (commit `7a238666`) |
| `prereg/analyse-principale-r1-r2-v1.md` | primary reading, action by action | `8e2679526b2777a9fe8564dd5f5fdaf98b70affd759cf47857abc8b168d92537` | 2 Nov 2026, 01:24 UTC (commit `83ce7a91`) |
| `prereg/analyse-par-episode-v1.md` | complementary reading, episode by episode | `26a3ff72e3a39636d3bdb965971fd1b237a04acc133a31a42f9a695d6d5970a4` | 2 Nov 2026, 07:40 UTC (commit `52eb34c8`), before any output of the run was retrieved |

The three texts will be made public with the result, unchanged, so that anyone can check them against these hashes.

## Where it stood (2 November 2026)

- **The activation replay stopped on its own fidelity guard.** To read the activations, the model is re-run on the recorded episodes. For some actions, the recorded text could not be re-tokenised into exactly the tokens that were generated, and the guard stopped the replay rather than let it read approximate activations. Nothing of the white-box arm has been read.
- **Next, each step preregistered, counter-read by a fresh reviewer and sealed before it runs:** a seeded replay that regenerates the exact tokens of the episodes concerned from their recorded seeds, then a single rerun of R1 on the complete table.
- **Then:** the output is sealed before any reading; the three analyses run once; a fresh reader checks each verdict; the result is posted here, null or not. If a step stops on a guard again, this page says so.

Back to the [main README](../../README.md).
