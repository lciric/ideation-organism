# J02 — Rapport de l'expérimentateur

Rédigé le 2026-11-12. L'expérimentateur exécute la préinscription scellée (`preenregistrement.md`, sha256
`6cbe19ea…441ed0`, vérifié identique au fichier `.sha256` avant et après le travail). Les chiffres ci-dessous ne sont qu'un
**témoin** : le verdict est calculé par `verdict.py` à partir des chiffres du vérificateur. Ce rapport ne conclut pas.

## 1. Ce qui a été fait

1. **Lecture** : `tests-de-mort/protocole.md`, puis la préinscription en entier. Aucune fiche, aucun jugement, aucun fichier
   d'un autre test n'a été ouvert. Aucun fichier de `tests-de-mort/H03-v2/` n'a été ouvert ni copié (voir `ecarts.md`, É3).
2. **Téléchargement** (`telecharger.py`) : les 109 millésimes MPD `W99` … `W26` (liste figée, section 4) et la série Eurostat
   `prc_hicp_minr` `M.I15.TOTAL.EA`, avec la règle d'essai préinscrite (10 essais, 120 s, 10 s d'attente, HTTP 200 et
   en-tête contrôlé). **Les 110 fichiers sont arrivés au premier essai.** La liste des clés MPD (`detail=serieskeysonly`) a
   aussi été téléchargée pour contrôle : elle contient 111 millésimes `Q.U2.HIC.A` (les 109 de la liste, plus `G26` et
   `S26`, non utilisés), comme l'annonçait la note de nouveauté. Contrôle de stabilité : 12 millésimes répartis sur les
   années et les lettres (W99, A01, G05, S08, W12, A15, G18, S21, W23, A24, G25, W26) et le fichier Eurostat ont été
   retéléchargés quelques minutes plus tard : identiques octet pour octet. Tout est dans `donnees/PROVENANCE.md`.
3. **Construction** (`construire.py`, à partir de `donnees/` seul) : `J02_analyse.csv`, 108 lignes × 26 colonnes, dans le
   schéma de la section 5 (sha256 `33b69a67ca010ec7c896944a9a7b1f3a463df329b318cfa5fb45b26e17875e58`). Le script écrit
   `construire_journal.json` (sha256 et nombre de lignes de chaque fichier brut, date et code HTTP recopiés du journal de
   téléchargement, drapeaux Eurostat, comptes, contrôles).
4. **Contrôles de schéma** (`controles_schema.py`, appelé par `construire.py` et par `analyse.py`) : les 11 contrôles de la
   section 5, appliqués au seul fichier d'analyse. **0 violation.** En particulier :
   - contrôle 5 (lettre et titre) : sur les 216 couples (ligne, millésime), le dernier nom de mois anglais de `TITLE_COMPL`
     vaut 3 × trimestre de la lettre et l'année du titre vaut l'année du code. Vérifié aussi, hors schéma, sur les 109
     millésimes : chacun a un seul `TITLE_COMPL`, une seule année à quatre chiffres, le bon mois ;
   - contrôle 6 : le premier trimestre de statut `F` est, dans chacun des 109 millésimes, le trimestre de l'exercice
     (h = 0) ;
   - contrôle 7 (la projection précède la réalisation) : les 216 projections retenues sont toutes lues sur des lignes de
     statut `F`, dans un exercice daté 2 (f₂) ou 3 (f₃) trimestres avant la cible ;
   - contrôles 9 à 11 : réalisé, révision et erreur recalculés à 10⁻⁶ ; indices « un an avant » identiques aux indices de
     la ligne t − 4.
5. **Analyse** (`analyse.py`, à partir du seul fichier d'analyse) : statistique principale, garde de robustesse, champs
   dérivés, analyses secondaires S1 à S3, `temoin.json` (les 26 champs de `champs_verification`, nombres seulement),
   `analyse_detail.json` (détails descriptifs) et `figure.png`.

## 2. Échantillon à chaque filtre

| Étape | Cibles |
|---|---|
| Liste figée des cibles 1999T4-2026T3 (lignes du fichier) | 108 |
| f₂ présente (ligne existante, statut `F`, valeur non vide) | 108 |
| f₃ présente | 108 |
| a(q) présente (six indices Eurostat présents) | 108 |
| révision présente | 108 |
| **complètes (révision et erreur présentes) = `n_cibles`** | **108** |
| S1 : `t_cible` ≤ 8079 (1999T4-2019T4) | 81 |
| S3 : hors 8084-8095 (2021T1-2023T4) | 96 |

Aucune valeur manquante. Eurostat : 369 mois de 1996-01 à 2026-09 (mise à jour du 04/11/26), aucun vide, **aucun
drapeau** (`OBS_FLAG` vide partout) ; mois utilisés 1998-10 à 2026-09 (336 mois) ; aucun mois postérieur à 2026-09 n'était
présent ; le repli `I25` n'a pas servi.

Description des variables (108 cibles) : révision moyenne 0,135 point (min −1,4 ; max 3,3 ; 11 révisions nulles sur 108,
soit 10,2 %) ; erreur moyenne 0,218 point (min −2,24 ; max 4,35).

## 3. Statistique principale (témoin)

| Champ | Valeur |
|---|---|
| `n_violations_schema` | 0 |
| `n_cibles` | 108 |
| `beta_z` (corrélation de Pearson révision–erreur) | 0,44312 |
| `et_beta_z_nw4` (Newey-West, L = 4, Bartlett, sans correction) | 0,19550 |
| `t_nw4` | 2,2666 |
| `borne_basse_ic90` | 0,12152 |
| `borne_haute_ic90` | 0,76472 |
| `marge_indecision` | −0,12152 |
| `beta_z_min_sans_deux_ans` | 0,05033 |
| `annee_debut_min` | 2021 (cibles 2021 et 2022 retirées) |
| `conflit_robustesse` | 0 |
| `beta_brut` (points d'erreur par point de révision) | 0,67826 |
| `et_beta_brut_nw4` | 0,29925 |
| `ecart_type_revision` | 0,61997 |
| `ecart_type_erreur` | 0,94895 |

Contrôle croisé : `statsmodels` `OLS(y, add_constant(z)).fit(cov_type="HAC", cov_kwds={"maxlags": 4,
"use_correction": False})` donne la même pente (0,4431206) et le même écart-type (0,1955020) ; les 108 cibles sont
contiguës, l'équivalence annoncée à l'étape 7 s'applique donc.

**Garde (27 retraits de deux années consécutives).** 24 des 27 corrélations sont entre 0,432 et 0,466. Les trois autres :
retrait de 2021-2022 → **0,050** (le minimum) ; retrait de 2022-2023 → 0,187 ; retrait de 2023-2024 → 0,585. Le détail
est dans `analyse_detail.json`.

## 4. Analyses secondaires — descriptives, hors verdict

**S1 — Avant 2020 (1999T4-2019T4, comparaison avec Granziera, Jalasjoki et Paloviita, 2021).** n = 81 ;
`beta_z_avant_2020` = 0,1342 (écart-type NW4 0,0777, t = 1,73) ; `beta_brut_avant_2020` = 0,1924 ;
`et_beta_brut_avant_2020_nw4` = 0,1114. Pour mémoire, le chiffre publié est 0,20 (écart-type 0,21) ; l'écart-type obtenu
ici est environ moitié plus petit (sources et réalisations différentes : MPD actuelle et IPCH Eurostat ECOICOP v2 de
dernier millésime). Le rapport s_r / s_e sur ce sous-échantillon vaut 0,386 / 0,554 = 0,70, un peu au-dessus de la plage
1/3 à 2/3 supposée en section 1.

**S2 — Sensibilité de l'inférence (échantillon complet).**
- `et_beta_z_nw8` = 0,1616 (t = 2,74 ; intervalle à 90 % correspondant, indicatif : [0,177 ; 0,709]). L'écart-type à 8
  retards est plus petit qu'à 4 retards.
- Bootstrap par blocs mobiles (blocs de 8, k = 14 blocs, B = 9 999 tirages, `default_rng(20261112)`, débuts par
  `rng.integers(0, 101, size=14)`) : `bb_borne_basse_ic90` = 0,0507 ; `bb_borne_haute_ic90` = 0,5921. Aucun tirage rejeté
  pour variable constante. Moyenne des tirages 0,376, médiane 0,432 : la distribution est étirée vers le bas (tirages qui
  omettent les blocs de 2022).

**S3 — Poids de l'épisode 2021-2023.**
- Sans les cibles 2021T1-2023T4 : `n_hors_2021_2023` = 96 ; `beta_z_hors_2021_2023` = 0,1436 ;
  `et_beta_z_hors_2021_2023_nw4` = 0,0654 (t = 2,20 ; intervalle à 90 % indicatif [0,036 ; 0,251]).
- Retrait d'une seule année civile (28 valeurs) : `beta_z_min_sans_une_annee` = 0,0842, obtenu en retirant **2022** ;
  retirer 2023 donne 0,572 ; les 26 autres retraits donnent entre 0,436 et 0,454.

En résumé descriptif : la corrélation sur tout l'échantillon (0,443) est portée en grande partie par les cibles de 2022
(révisions et erreurs positives et grandes, voir la figure) ; les cibles de 2023 vont en sens inverse (révisions encore
positives ou grandes en début d'année, erreurs nulles ou négatives) ; hors 2021-2023, la corrélation est 0,144.

## 5. Figure

`figure.png` : nuage de l'erreur réduite y contre la révision réduite z pour les 108 cibles ; droite de pente β_z = 0,443
passant par l'origine (la constante est nulle par construction) ; zone ombrée = droites de pentes `borne_basse_ic90` et
`borne_haute_ic90` (intervalle à 90 %, Newey-West 4 retards) ; droite pointillée de pente 0,40 (prédiction de la fiche) ;
les 12 cibles 2021T1-2023T4 en losanges orange, étiquetées. Aucun bruit n'a été ajouté : les révisions étant des multiples
de 0,1 point, beaucoup de points se superposent près de l'origine (11 révisions nulles). La figure montre les points
extrêmes de 2022 (z ≈ 0,6 à 3,7, y ≈ 3,5 à 4,4) et 2023T1 (z ≈ 5,1, y ≈ −0,2).

## 6. Difficultés et choix

- **Réseau** : aucune difficulté ; les 110 fichiers (plus la liste des clés) ont été reçus au premier essai, avec HTTP 200.
- **Réutilisation des fichiers de H03-v2** : l'orchestrateur l'autorisait sous conditions, mais la préinscription
  (section 2, « Règle d'aveuglement ») interdit d'ouvrir **aucun** fichier du dossier `H03-v2`. J'ai suivi la
  préinscription : tout a été retéléchargé, rien n'a été copié ni ouvert (le seul contact avec ce dossier est un listage
  des noms de fichiers, voir `ecarts.md`, É3).
- **Règle d'essai Eurostat** : la préinscription n'en fixe pas ; la règle MPD a été reprise (É1). Sans effet : premier
  essai réussi.
- **Lecture de `TITLE_COMPL`** : chaque fichier a un seul titre, de la forme « Euro area - Price and cost developments -
  HICP overall index - Annual growth rate - <Mois> <Année> staff macroeconomic projections » pour 105 millésimes ; les
  quatre derniers (G25, S25, A25, W26) portent en plus un nom de saison : « Spring/June 2025 », « Summer/September 2025 »,
  « Autumn/December 2025 », « Winter/March 2026 ». Les noms de saison ne sont pas des noms de mois ; chaque titre contient
  un seul nom de mois anglais complet et une seule année à quatre chiffres : la règle « dernier nom de mois » et la lecture
  de l'année n'ont aucune ambiguïté sur ces données (le mois lu concorde avec la lettre pour les 109 millésimes).
- **Écriture des nombres** : projections et indices recopiés tels que publiés (chaîne du fichier brut, par exemple
  `75.60`) ; `realise` et `erreur` écrits avec 12 décimales, `revision` avec 10 décimales (calculées en double précision ;
  la différence de deux nombres à une décimale peut porter un résidu de l'ordre de 10⁻¹⁶, invisible à 10 décimales).
- **Bootstrap** : lecture littérale, un appel `rng.integers(0, n − 7, size=k)` par tirage, blocs mis bout à bout et tronqués
  à n = 108 lignes, centiles par `numpy.percentile` (méthode linéaire).
- **Fichiers produits en plus** de ceux que nomme la préinscription : `telecharger.py`, `telecharger_journal.json`,
  `controles_schema.py`, `analyse_detail.json`, `donnees/MPD_cles_serieskeysonly.csv`. Ils ne changent rien aux calculs.

## 7. Reproduire

```
python3 -I telecharger.py      # facultatif : réutilise donnees/ si les fichiers y sont
python3 -I construire.py       # écrit J02_analyse.csv et construire_journal.json
python3 -I analyse.py          # écrit temoin.json, analyse_detail.json, figure.png
```
