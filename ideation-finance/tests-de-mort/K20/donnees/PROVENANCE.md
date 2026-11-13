# K20 — provenance des données brutes

Fichiers téléchargés par `telecharger.py` (agent HTTP par défaut de Python, délai 120 s, jusqu'à 5 essais ; tous obtenus au
premier essai), écrits sans aucune modification. Le même journal, au format JSON, est dans `../construire_journal.json`
(section 4 de la préinscription). Date et heure en UTC. « Lignes » = lignes de données hors en-tête (par feuille utilisée
pour les classeurs Excel).

| Fichier | URL | Date et heure (UTC) | HTTP | Octets | sha256 | Lignes |
|---|---|---|---|---|---|---|
| `meanGrowth.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/meanGrowth.xlsx | 2026-11-12T23:56:01Z | 200 | 146159 | `4888e773cb4d577970dd24227bca5c7feb2ff79d931de7d0fb70b5bf628ea517` | PGDP : 232 ; RGDP : 232 |
| `meanLevel.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/meanLevel.xlsx | 2026-11-12T23:56:05Z | 200 | 599838 | `f2b53e0cb911c71348eddf367eb3bfada1dd9dfcb728c4199efa8846fdfcbee4` | UNEMP : 232 ; CPI : 232 ; TBILL : 232 |
| `medianGrowth.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/medianGrowth.xlsx | 2026-11-12T23:56:08Z | 200 | 144611 | `fdcf9ca0299de022c58f8fc35fd20761d8e52b45e038781ae3c4826d1a3cbb5c` | PGDP : 232 ; RGDP : 232 |
| `medianLevel.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/medianLevel.xlsx | 2026-11-12T23:56:12Z | 200 | 554444 | `d296e737331c406f7680414504a0d005472743709387f8fda6d969a1d2200977` | UNEMP : 232 ; CPI : 232 ; TBILL : 232 |
| `pQvQd.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/pQvQd.xlsx | 2026-11-12T23:56:16Z | 200 | 247472 | `9726209d1cd370bd44bc22f18a1c715405e4e8f329d9779229ae8914203a11c6` | P : 319 (245 millésimes P65Q4-P26Q4) |
| `routputQvQd.xlsx` | https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/routputQvQd.xlsx | 2026-11-12T23:56:19Z | 200 | 244845 | `6a7971b31b7336551705465de8a0855826f3652abe112406f52b2c2ed0994c0c` | ROUTPUT : 319 (245 millésimes) |
| `UNRATE.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE | 2026-11-12T23:56:22Z | 200 | 14226 | `fb669461abc34e00324b940be6bad1c7f89117652f28587196a7b8bf4a9f56a1` | 946 (1948-01 à 2026-10 ; 2025-10 vide) |
| `CPIAUCSL.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL | 2026-11-12T23:56:25Z | 200 | 17782 | `c9be2d4909ffd28d91f07df5d113151b0fe7ba602144ee6fd453d3bc8426efde` | 958 (1947-01 à 2026-10 ; 2025-10 vide) |
| `TB3MS.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS | 2026-11-12T23:56:29Z | 200 | 17881 | `33fae406051a658c316580f8e8b5e461157e6663bc03b35648cc7cd3e89ee26b` | 1114 (1934-01 à 2026-10 ; aucun vide) |
| `USRECQP.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=USRECQP | 2026-11-12T23:56:32Z | 200 | 8969 | `fae37d07129f12682fde3584a8511408eeaef1554b33141f15c6e7886fea627e` | 688 (1854T4 à 2026T3) — sert seulement à vérifier les fenêtres d'épisodes, n'entre pas dans le fichier d'analyse |
