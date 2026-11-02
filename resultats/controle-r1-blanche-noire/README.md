# R1 — white-box versus black-box monitors on real activations (control programme): status

*Status page of the first white-box versus black-box comparison of the AI-control programme that hosts this repository. Last updated: 2 November 2026, 08:54 UTC. The result, whatever its sign, will be posted on this page once it has been read once under the sealed analyses below and checked by a fresh reader.*

## The question

On the 2,400 scored actions of the programme's first test on real activations (Llama-3.1-8B, 60 tasks; a saboteur given a hidden instruction to inflate a declared cost, against honest and control conditions), do probes on the model's activations detect the saboteur's actions better than small black-box LLM judges (3 and 8 billion parameters) and a simple cost rule, at the same false-alarm rate?

## Sealed before the data

| Text (private working repository) | Role | SHA-256 | Sealed |
|---|---|---|---|
| `prereg/analyse-blanche-noire-v3.md` | secondary reading: white box versus black box, by family of monitors | `1f6a6da2c551060a5f90ff3358b0aaf276dd9f336a5b953e6d93233c8c581fa9` | 2 Nov 2026, 01:05 UTC (commit `7a238666`) |
| `prereg/analyse-principale-r1-r2-v1.md` | primary reading, action by action | `8e2679526b2777a9fe8564dd5f5fdaf98b70affd759cf47857abc8b168d92537` | 2 Nov 2026, 01:24 UTC (commit `83ce7a91`) |
| `prereg/analyse-par-episode-v1.md` | complementary reading, episode by episode | `26a3ff72e3a39636d3bdb965971fd1b237a04acc133a31a42f9a695d6d5970a4` | 2 Nov 2026, 07:40 UTC (commit `52eb34c8`), before any output of the run was retrieved |

The three texts will be made public with the result, unchanged, so that anyone can check them against these hashes.

## Where it stands

- **The activation replay stopped on its own fidelity guard.** To read the activations, the model is re-run on the recorded episodes. For some actions, the recorded text could not be re-tokenised into exactly the tokens that were generated, and the guard stopped the replay rather than let it read approximate activations. Nothing of the white-box arm has been read.
- **Next, each step preregistered, counter-read by a fresh reviewer and sealed before it runs:** a seeded replay that regenerates the exact tokens of the episodes concerned from their recorded seeds, then a single rerun of R1 on the complete table.
- **Then:** the output is sealed before any reading; the three analyses run once; a fresh reader checks each verdict; the result is posted here, null or not. If a step stops on a guard again, this page says so.

Back to the [main README](../../README.md).
