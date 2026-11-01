# Écart à la section 13 du préenregistrement de la validation du nul v8 — v2

Remplace la v1 (`ecart-section13-v1.md`, gardée telle quelle), dont les deux dates étaient fausses d’un jour. Écrit par la session qui a lancé la course (conv-audit), le 1er novembre 2026 vers 23:40 UTC (2 novembre, 00:40 à Paris), après le verdict du lecteur neuf (réserve R2 de `verdict-R13-validation-nul-v8-v1.md`).

- **Ce que demandait le texte scellé** (section 13) : après la poussée du commit de scellement, rejouer sur l'arbre scellé les 35 essais (`essais/test_v58_nul_v8.py`) et le banc de mutations (`essais/mutations_v58.py`), puis lancer la commande de la section 4.
- **Ce qui a été fait** : la poussée de `1bad95f` est datée de 22:25:07 UTC, la course est partie à 22:25:14 UTC, **sans ce rejeu**. Les mêmes essais et le même banc avaient été joués avant le scellement, sur un code identique à l'octet (contre-lecteur, pièce L12ab de `resultats/prelectures-nul-v8-2026-11-01/`).
- **Rejeu a posteriori** (`rejeu-section13-a-posteriori-v1.txt`) : au commit `2cfb940`, dont l'arbre `orchestrator/` est identique à celui de `1bad95f` (`git diff --quiet 1bad95f HEAD -- orchestrator` : vide), le 1er novembre 2026, 23:34 à 23:37 UTC : **35 essais réussis** (51 sous-essais) ; **34 mutations sur 34 tuées pour la raison attendue**, aucune survivante, témoin à 0 échec avant et après.
- **Conséquence** : aucune sur l'issue (le code de la course est celui que ces essais éprouvent) ; l'écart est consigné ici et au README.
