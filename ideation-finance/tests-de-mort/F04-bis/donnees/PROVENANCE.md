# F04-bis — provenance des fichiers bruts

Tous les fichiers de ce dossier sont conservés tels que reçus ou copiés, sans aucune modification.

## Fichier téléchargé pour ce test

| Fichier | URL | Téléchargé (UTC) | Réponse | Octets | Lignes | sha256 |
|---|---|---|---|---|---|---|
| `fy2021-mc-vs-hs-combined.csv` (fichier B, les deux méthodes) | `https://home.treasury.gov/system/files/221/fy2021-mc-vs-hs-combined.csv` | 2026-11-12T17:31:28Z (requête lancée) ; fichier écrit à 17:31:39Z | HTTP 200 à la première tentative, `curl -sS -L`, agent utilisateur par défaut de curl | 47 599 | 252 lignes = 1 en-tête + 251 lignes de données (35 colonnes chacune) | `d1111ffb985ea76a3291f0f006cca652c8f8126811e932182b507e2ce86f695d` |

Le scellement de la préinscription porte l'heure 2026-11-12T17:31:07Z (date de modification de `preenregistrement.md`,
`preenregistrement.md.sha256` et `scellement.md`) : le téléchargement a eu lieu après.

Forme constatée : marque d'ordre d'octets UTF-8 au début, 252 fins de ligne toutes CRLF, séparateur virgule, dates
`M/J/AAAA` sans zéro initial du `10/1/2020` au `9/30/2021`, taux à deux décimales au plus (zéros finaux supprimés),
aucune cellule vide, aucun espace en trop.

## Fichiers repris du premier test F04 (aucun retéléchargement, comme le prévoit la préinscription)

| Fichier ici | Origine | Copié (UTC) | Octets | Lignes | sha256 (identique à l'origine) |
|---|---|---|---|---|---|
| `F04_analyse.csv` (fichier A) | `tests-de-mort/F04/F04_analyse.csv`, fichier d'analyse du premier test (construit le 2026-11-12T15:58Z) | 2026-11-12T17:32Z, `cp -p` | 285 608 | 1 607 lignes = 1 en-tête + 1 606 lignes de données | `90d2cabe769dad36e56e3d5011d2ce11a8e351e86c6056049f9c8eecad98cac9` |
| `DGS10.csv` (calendrier C) | `tests-de-mort/F04/donnees/DGS10.csv` ; d'après la provenance de F04 : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10`, téléchargé le 2026-11-12T15:53:11Z | 2026-11-12T17:32Z, `cp -p` | 269 347 | 16 921 lignes = 1 en-tête + 16 920 lignes de données | `0a19145416475025a3db81f1d24cddde626211cc098ccba2c22c4baf426c5bb4` |

`DGS10.csv` ne sert qu'à compter les jours du calendrier C dans l'exercice (251) et à les comparer aux dates du fichier B ;
aucun taux n'en est tiré. Les taux FRED et ceux de la courbe ajustée viennent du fichier A, comme l'écrit la préinscription.

`construire.py` vérifie à chaque exécution que la copie du fichier A a le même sha256 que l'original, et écrit les trois
sha256 dans `construire_journal.json`.

## Fichier produit

| Fichier | Octets | Lignes | sha256 |
|---|---|---|---|
| `../F04-bis_analyse.csv` | 4 578 | 25 lignes = 1 en-tête + 24 adjudications | `86ecfc2a26d714272a58cc463c3e0fd9b090f2e9940c71d44aadfe8c3e18b5b1` |
