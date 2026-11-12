# F12 — Provenance des fichiers bruts

Téléchargés le 2026-11-12 par l'expérimentateur, avec `curl` (agent par défaut), sans modification après écriture.
Heures en temps universel (UTC). Tous les téléchargements ont réussi au premier essai (HTTP 200).

| Fichier | URL | Date et heure (UTC) | Octets | sha256 | Lignes |
|---|---|---|---|---|---|
| `Dataset_EA-MPD.xlsx` | `https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx` | 2026-11-12 15:55:46 | 377 116 | `f417fb861a305e3cbb871a7571c4899ba6bca003d9e087024d2f3f0744426cef` | feuille `Monetary Event Window` : 1 ligne d'en-têtes + 315 réunions datées (1999-01-07 à 2025-10-30), 46 colonnes nommées ; autres feuilles, non lues pour l'analyse : `Notes` (60 lignes non vides en colonne A), `Press Release Window` (1 + 315), `Press Conference Window` (1 + 315) |
| `riksbank_DEGVB10Y.json` | `https://api.riksbank.se/swea/v1/Observations/DEGVB10Y/2009-12-01/2025-11-30` | 2026-11-12 15:55:52 | 145 126 | `9e304697b22d94649ca0df099f4a3b457633b7c2a099afdb20d210b3a034de91` | 4 018 observations (2009-12-01 à 2025-11-28) |
| `riksbank_NLGVB10Y.json` | `https://api.riksbank.se/swea/v1/Observations/NLGVB10Y/2009-12-01/2025-11-30` | 2026-11-12 15:55:56 | 145 020 | `ac06ac06cc8300df35b260e9685179d5176f98c0f749a3946124daf5fad9c066` | 4 016 observations (2009-12-02 à 2025-11-28) |
| `riksbank_FIGVB10Y.json` | `https://api.riksbank.se/swea/v1/Observations/FIGVB10Y/2009-12-01/2025-11-30` | 2026-11-12 15:56:00 | 144 709 | `a890a95477ec35c48d410871bd404ea397abbda61dbc82f2d9dd0c264f451a01` | 4 016 observations (2009-12-02 à 2025-11-28) |
| `riksbank_FRGVB10Y.json` | `https://api.riksbank.se/swea/v1/Observations/FRGVB10Y/2009-12-01/2025-11-30` | 2026-11-12 15:56:05 | 145 746 | `ad80c1001faabf3529d6dfb3959367cdff0f4b72b20c85f1b4e201816d097531` | 4 016 observations (2009-12-02 à 2025-11-28) |

Remarques :
- L'empreinte de `Dataset_EA-MPD.xlsx` est **identique** à celle notée dans la préinscription (§ 4.1), ainsi que sa taille.
- Les fichiers Riksbank sont des listes JSON d'objets `{"date": "AAAA-MM-JJ", "value": <rendement en %>}`, sur une seule
  ligne physique ; la colonne « Lignes » donne le nombre d'observations. Aucune valeur non numérique.
- Pause de trois secondes entre les appels à l'interface de la Riksbank.
- `brut/` (nom de dossier de la préinscription, § 5) est un lien symbolique vers ce dossier `donnees/` (voir `ecarts.md`).
