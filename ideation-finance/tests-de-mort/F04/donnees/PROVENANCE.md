# F04 — Provenance des fichiers bruts

Tous les fichiers ont été téléchargés le 2026-11-12 avec `curl` (agent utilisateur par défaut, option `-L`), enregistrés tels
quels, sans modification. Chaque téléchargement a répondu HTTP 200 au premier essai. Les heures sont en UTC.

« Lignes » = nombre de fins de ligne (`wc -l`). « Enregistrements » = lignes de données, hors en-tête et préambule.

| Fichier | URL | Heure (UTC) | Octets | Lignes | Enregistrements | sha256 |
|---|---|---|---|---|---|---|
| `auctions_query.json` | voir ci-dessous (D1) | 2026-11-12T15:53:02Z | 476 748 | 0 (JSON sur une ligne) | 1 639 objets dans `data` (`meta.total-count` = 1639, `total-pages` = 1) | `a71982759673d5ea02371b6023c131e78eb5fd1a1c522271754f0c6603f50e5b` |
| `DGS2.csv` | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2` | 2026-11-12T15:53:02Z | 209 520 | 13 161 | 13 160 (dernière date 2026-11-09) | `4d4ee579aa22639298cb3667a693b402b1c3e6e13869d9de9bbf3f71cf937128` |
| `DGS3.csv` | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS3` | 2026-11-12T15:53:04Z | 269 068 | 16 921 | 16 920 (2026-11-09) | `b024016eb765f3fe43ef5c7ab99ce56799b55efe694e74628e342a266a6eabba` |
| `DGS5.csv` | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS5` | 2026-11-12T15:53:07Z | 269 173 | 16 921 | 16 920 (2026-11-09) | `5af5c01a8e0c1af3aecaa77cdd0895933966e0d03c5fbbc6e59d0dfdffd16698` |
| `DGS7.csv` | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS7` | 2026-11-12T15:53:09Z | 238 367 | 14 966 | 14 965 (2026-11-09) | `87f454d8453a91aa9146159348ade1df429dbdb9e74dc78cdd17d4f1ba844d8b` |
| `DGS10.csv` | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10` | 2026-11-12T15:53:11Z | 269 347 | 16 921 | 16 920 (2026-11-09), dont 16 199 non vides (calendrier C) | `0a19145416475025a3db81f1d24cddde626211cc098ccba2c22c4baf426c5bb4` |
| `DGS20.csv` | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS20` | 2026-11-12T15:53:13Z | 262 616 | 16 921 | 16 920 (2026-11-09) | `6a634a74ad00687645c39e3ec4352663eca5269187120632307e4c9d9e9f8b8e` |
| `DGS30.csv` | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS30` | 2026-11-12T15:53:15Z | 206 941 | 12 976 | 12 975 (2026-11-09) | `1b017c37afd6e51664634815c2fadad2cecef2f5bc2cd5bbdf113ca2d54559be` |
| `feds200628.csv` | `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` | 2026-11-12T15:53:18Z | 16 672 370 | 17 073 | 17 063 (9 lignes de préambule, 1 en-tête ; dates 1961-06-14 à 2026-11-06) | `dfaad994aeaf232bcc3204aec4b30c0f0bbb4db410f8985d55c15390a73ff2bd` |

URL de D1 (requête unique de la préinscription, recopiée à l'identique) :

```
https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?fields=auction_date,security_type,security_term,original_security_term,reopening,inflation_index_security,floating_rate,offering_amt,cusip,issue_date,maturity_date&filter=auction_date:gte:2010-01-01,auction_date:lte:2026-09-30,security_type:in:(Note,Bond)&sort=auction_date&page%5Bsize%5D=10000
```

Contrôles de forme à la réception :
- FRED : en-tête `observation_date,<SERIE>` pour les sept séries ; valeur manquante = champ vide.
- D3 : neuf lignes de préambule puis l'en-tête commençant par `Date` ; colonnes `SVENPY02`, `SVENPY03`, `SVENPY05`, `SVENPY07`,
  `SVENPY10`, `SVENPY20`, `SVENPY30` présentes ; valeur manquante = `NA`.
- D1 : les onze champs demandés, pour chaque objet.

Le dossier s'appelle `donnees/` (consigne de l'orchestrateur) et non `brut/` (préinscription, section 4) : voir `ecarts.md`.
