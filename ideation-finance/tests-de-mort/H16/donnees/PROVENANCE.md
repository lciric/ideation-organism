# H16 — provenance des fichiers bruts

Tous les fichiers ont été téléchargés le **2026-11-12** par `telecharger.py` (curl, agent utilisateur par défaut, `-L`), chacun
au **premier essai** (HTTP 200), et sont conservés tels quels, sans aucune modification. Les heures sont en UTC (fin du
téléchargement). Le journal brut du téléchargement est `telechargements.json` (ce n'est pas une donnée).

| Fichier | URL | Date et heure (UTC) | Octets | sha256 | Lignes |
|---|---|---|---|---|---|
| `Dataset_EA-MPD.xlsx` | https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx | 2026-11-12 18:55:07 | 377 116 | `f417fb861a305e3cbb871a7571c4899ba6bca003d9e087024d2f3f0744426cef` | feuille `Monetary Event Window` : 325 lignes = 1 en-tête + 315 réunions + 9 lignes vides en fin de feuille ; 46 colonnes nommées |
| `DCOILBRENTEU.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU | 2026-11-12 18:55:07 | 170 363 | `b30cdc14ddae1f72df40bb942f6926acc9df627cb3c68844d6e18ea65b5cf6f0` | 10 296 lignes = 1 en-tête + 10 295 observations (1987-05-20 à 2026-11-03), dont 1 173 vides |
| `DEXUSEU.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXUSEU | 2026-11-12 18:55:07 | 129 109 | `2374b98f07cdfc5c0f3b5147325bfe5ddc15fc9d6cc5eb71b2c320d19c5438d3` | 7 266 lignes = 1 en-tête + 7 265 observations (1999-01-04 à 2026-11-06), dont 281 vides |
| `feds200628.csv` | https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv | 2026-11-12 18:55:08 | 16 672 370 | `dfaad994aeaf232bcc3204aec4b30c0f0bbb4db410f8985d55c15390a73ff2bd` | 17 073 lignes = 9 de préambule + 1 en-tête + 17 063 observations (1961-06-14 à 2026-11-06), dont 749 `NA` pour `SVENY02` |
| `Europe_3_Factors_Daily_CSV.zip` | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_3_Factors_Daily_CSV.zip | 2026-11-12 18:55:09 | 64 819 | `53598ec5af305d321ee93db492a32076fc882f976e67d27eba724d0266d20ad2` | un seul fichier `Europe_3_Factors_Daily.csv` : 9 465 lignes = 6 de préambule + 1 en-tête + 9 458 observations (19900702 à 20260930), aucune `-99.99` ; millésime « 202609 Bloomberg database » |

Notes.
- L'empreinte d'EA-MPD est **identique** à celle de la préinscription (§ 4.1).
- Le repli FRED `DGS2` (amendement A14) n'a pas été téléchargé : le fichier de la Réserve fédérale a répondu au premier essai.
- Les tailles d'EA-MPD (377 116 octets), de la courbe américaine (16,7 Mo) et du fichier Ken French (64 819 octets) sont celles
  relevées par la préinscription.
