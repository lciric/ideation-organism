# Smallest real run of the full loop, third attempt (organism v67, configuration v8) — verdict of 12 November 2026

**Verdict (fresh reader, rule R13): the rendered outcome is confirmed — C1, "the chain holds (covered class, this world, this size)":** the class covered by the v8 null, toy world S-V1, one and a half generations. **Nothing** about the uncovered class, real data, or the quality of the ideas. Seven reservations, none of which changes the outcome (below). The phrase rendered by the frozen reading program, copied as it came:

> Issue C1 : « la chaîne garde (classe couverte, ce monde, cette taille) » — course reel (decisif) (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte).

The verdict file in this folder is the reference (French, byte for byte); this page summarises it and adds nothing to it.

## Three attempts under this design, reported together

Text v2 requires the third attempt to be reported with the first two (rule R4). The first two (code v66, text v1) are on the [status page of 12 November](../boucle-reelle-v66/).

| attempt | relay record, sha256 | launcher | laws judged | outcome | cause |
|---|---|---|---|---|---|
| 1 (v66, 12 Nov 2026) | `c9c6212bfe16b148e5df42c27a1f631eeafbd79ca9c7b82ac048fabce69c3069` ([file](../boucle-reelle-v66/poste-local-v1/boucle-reelle-v66.json)) | exit 3 | 0 card, 0 planted law | C5 "not judgeable (stop)" | Kimi upstream HTTP 429 |
| 2 (v66, 12 Nov 2026) | `5a7fc27c7dfb1c7e0911cf9df3aa0b1c785e386bfa32de0294625c5709d52b9b` ([file](../boucle-reelle-v66/poste-local-v2/boucle-reelle-v66.json)) | exit 3 | 0 card, 0 planted law | C5 "not judgeable (stop)" | proposer reply cut by its output bound (46,714 output tokens) |
| 3 (v67, 12 Nov 2026, 14:21:52 → 15:07:32 UTC) | `21bc75f4d81825695b30b2b32f21feaa91322293f6c2c3161a28dc179ec6df71` ([file](poste-local-v1/boucle-reelle-v66.json)) | exit 0 | 23 cards, 18 planted laws, two generations | C1 | — |

Frozen readings: attempts 1 and 2, `7de89198…` and `edae8c4f…` (C5, nothing hidden behind the stop); attempt 3, `d0ef1ee7667bdc665747c2822dcb031abfea3b38b3094782ad72ae593c016086` ([file](poste-local-v1/lecture-course-reelle.json)). The verdict notes that nothing had been judged before deviation 1, that the reading criteria were unchanged, and that the third attempt used fresh seeds (root = the hash of text v2): it is not a draw chosen among three results. It also notes that the two long Kimi calls of attempt 3 (31,891 and 38,343 output tokens) would have fitted under the v1 bounds: success owes as much to the variable length of the model's reasoning as to the deviation.

## What the verdict checked

- The frozen reading, replayed by the reader: same code C1, same phrase; every field equal to the filed reading except the clock time and the path the program writes (reservation R-7).
- Checks V-1 to V-8 of the sealed text on the raw record: all hold; V-8 does not apply (11 real cards retained in generation 1).
- Symmetry audit (A1 "too good", triggered by C1): the 40 judgements of the record replayed offline with the frozen code, **40 of 40 equal**; planted laws equal to the sealed planted set; planted false laws F1 to F4 refused in both generations; V1 and V2 promoted and surviving their death tests; T-ELIM promoted then eliminated; T-MAL refused at the gate. Generation 2 was served and judged with generation 1's selection; as a counter-check (outside the criteria), the four copies refused in the run are all promoted when judged without that selection. Fourteen `gains.csv` files recomputed outside the sandbox, byte-equal to the sealed copies. Relay journals: Kimi and Argon only, no Claude-family model.
- Spend under GO-2026-11-12-06: 1.99431 USD of model calls (46 relayed calls) and about 0.27 USD of machine, about 2.26 USD against a cap of 45.

## Scope, as the verdict states it

- **What it says:** with real agents (Kimi `kimi-k3.1-pro` and Argon `gemini-4-argon`), a real sandbox and the planted laws of the text, the chain let V1 and V2 through to survival, refused F1 to F4 in both generations, and judged generation 2 with generation 1's selection on real content.
- **Bounds:** class covered by the v8 null; toy world S-V1 (3 outcomes, 2 traits); starting archive of one law; two providers; one full generation and a second up to its selection; a single judged run.
- **Nothing** about the uncovered class (piecewise recombinations, products, compositions) — some real cards retained here have such forms and are classed true by the oracle, which C1 does not guarantee in general; power at the weak effects of real data; the quality of the ideas; universality on unseen families; the composition of the proposers.
- Under section 14 of the text, this outcome is always reported **with A1-v3** (the out-of-class breach, [status page](../attaque-goodhart-v2/)).
- Under a correct chain the outcome was nearly certain by construction (simulation: 1,000 of 1,000): it establishes the absence of an observed plumbing defect at this size, not a performance. What it opens (several generations) is a proposal; the decision, and any spend, remain the project lead's.

## The seven reservations (none changes the outcome)

1. **R-1** — two "two-decimal" hits of the planted-law search in the proposers' generation-2 contexts, not mentioned by the run report; read by hand as a coincidence (the value 1.3 is a weight of a retained real card, at another position than the planted law's parameter), not a leak.
2. **R-2** — two raw pieces of the audit are missing: the proposers' session folders are empty (the proposers' raw replies are not kept, so the cards cannot be checked against what the models returned), and no per-run `bwrap` witness file is filed (the machine is destroyed). The recomputation outside the sandbox covers the value of the verdicts, not the isolation itself.
3. **R-3** — the run manifest says the tree was modified while the report says "clean tree", unexplained (probably the untracked copy of the sealed text); the 99 code hashes were checked by the launcher and by the reader.
4. **R-4** — one card fewer: Kimi returned 5 laws in generation 1 (23 real cards, not 24); allowed by the text ("at most 6").
5. **R-5** — generation 2 exercised neither the sandbox nor the selection on content: no real card promoted, no death test, empty final selection. The 11 retained cards of generation 1 are close variants of one finding (the effect of trait z1): the count says nothing about the quality or diversity of the ideas.
6. **R-6** — the frozen reading counts Argon's 16 calls "without usage" while the record holds their usage under other field names; a measure with no bearing on the outcome; the cost is right.
7. **R-7** — byte equality of the replayed reading is reached only after restoring the clock time and path of the filed reading (two lines); every substantive field is equal without it.

## Files in this folder

Copied byte for byte from the private working repository, each with its `.sha256` companion:

| file | sha256 |
|---|---|
| `verdict-course-v67-v1.md` — the fresh reader's verdict (French) | `d79024328157aafc5c801b5b0a4a621a5c009f367d88b96bbbfaeaeef3753459` |
| `rapport-course-v67-poste-local-v1.md` — the run report of the operating session (French) | `8a98f2f67b8c442e65dc700c081c270ec0a025bac09e89fe03961cf424b09f65` |
| `poste-local-v1/boucle-reelle-v66.json` — the launcher's record (the launcher still names it after v66; in the reports: `course-reelle/boucle-reelle-v66.json`) | `21bc75f4d81825695b30b2b32f21feaa91322293f6c2c3161a28dc179ec6df71` |
| `poste-local-v1/lecture-course-reelle.json` — the frozen reading of that record | `d0ef1ee7667bdc665747c2822dcb031abfea3b38b3094782ad72ae593c016086` |

The code that ran is commit `ab53b7f` on `main` (99 of 99 hashes equal to the sealed text v2). To replay the reading: from `orchestrator/`, `python -I -B demonstrations/lire_boucle_reelle_v66.py <folder holding boucle-reelle-v66.json> <out.json> --releve-sha256 21bc75f4d81825695b30b2b32f21feaa91322293f6c2c3161a28dc179ec6df71`.

Not here (private, hashes in the working repository): the raw journals of the provider relays and the machine logs (provider logs are not published); the run manifest, spending register, machine sheets and dry-run outputs (work records); the per-generation folders (cards, stage traces, death-test scripts and outputs); the run instruction and the registers.
