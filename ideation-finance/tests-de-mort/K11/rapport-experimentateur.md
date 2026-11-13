# K11 — rapport de l'expérimentateur

Rôle : exécuter la préinscription scellée (`preenregistrement.md`, sha256 `3f4e97b4…5597`, inchangée, vérifiée avant et après
le travail). Ce rapport donne des chiffres ; il ne contient pas de verdict. Les nombres de `temoin.json` ne sont qu'un témoin :
le verdict s'appliquera aux nombres du vérificateur.

## 1. Ce qui a été fait

1. **D1** : la requête exacte de la section 4.1, faite le 2026-11-12 à 23:49:56 UTC (HTTP 200, 2 793 lignes, une page) →
   `donnees/auctions_query.json`. La réponse conservée par J05 n'a pas été reprise (autre liste de champs, sans
   `original_security_term`).
2. **Calendrier, réouvertures, témoins sur métadonnées** (`construire.py --dates`) : 324 réouvertures, 905 dates
   FedInvest requises (J−5, J, J+5 des 314 lignes non écartées par les métadonnées), dont 316 en 2022-2026 — exactement
   les comptes de la préinscription.
3. **D2** : 614 des 905 pages copiées sans modification depuis les pages brutes de J05 ; 291 téléchargées par K11
   (`telecharger.py`, procédure 4.2 : GET avec témoin de session et `_csrf`, POST sans suivre la redirection, GET de
   `securityPriceDetail`, une session par date, pause d'une seconde, 5 essais au plus). Contrôle de la reprise : 17 dates
   copiées (une par année, 2010-2026) retéléchargées dans `donnees/fedinvest_controle/` ; aucune identique octet par octet,
   la seule différence étant le jeton `_csrf` aléatoire de la session (deux lignes du formulaire) ; tableau de prix extrait
   identique sur les 17 (`comparaison_controle.txt`). Tout est dans `donnees/PROVENANCE.md` (un tableau : fichier, origine,
   URL ou motif, date et heure UTC, sha256, lignes) ; les codes HTTP et essais des téléchargements K11 sont dans
   `donnees/journal_fedinvest.csv` et `donnees/journal_controle.csv`.
4. **Fichier d'analyse** : `construire.py` lit `donnees/` seulement et écrit `K11_analyse.csv` (324 lignes, 81 colonnes),
   puis exécute les 11 contrôles de la section 5.3 (`construire_sortie.txt`).
5. **Statistiques** : `analyse.py` recalcule les rendements avec un second code (Newton, dates de coupon générées
   autrement), puis E, V et toutes les statistiques de la section 6 ; écrit `temoin.json` et `figure.png`
   (`analyse_sortie.txt`).

## 2. Échantillon à chaque filtre

| Étape | Total | Après 2021 (10/20/30) | Avant 2022, 10 et 30 ans | Avant 2022, 20 ans |
|---|---|---|---|---|
| Réouvertures sélectionnées (4.1) | 324 | 117 (39/39/39) | 193 (97/96) | 14 |
| − `hors_calendrier` (2019-06-21) | 323 | 117 | 192 | 14 |
| − `temoins_insuffisants` | 315 | 117 | 192 | 6 |
| − `titre_non_emis_a_jm5` | 314 | 117 | 192 | 5 |
| − `prix_manquant` (aucune page absente ; candidats épuisés par des témoins figés) | 306 | 115 | 186 | 5 |
| − `prix_fige` (titre rouvert) | **302** | **113** (37/37/39) | **184** (88/96) | 5 |

- Les 905 pages ont la date demandée et un tableau rempli ; `n_candidats_absents` = 0 partout ; `identite_fi_ok` = 1 sur
  les 306 lignes qui ont trois témoins.
- Témoins figés sautés : 42 sur les 314 lignes, **7 sur P** (`n_temoins_figes`). Les 8 lignes `prix_manquant` : 2013-04-10,
  2013-12-11, 2016-04-13, 2017-10-11, 2017-12-11, 2019-07-10 (10 ans), 2023-06-21 (20 ans), 2023-09-12 (10 ans). Les 4 lignes
  `prix_fige` : 2018-12-12, 2020-07-08, 2023-06-12 (10 ans), 2023-03-21 (20 ans). Les quatre exclusions d'après 2021 sont
  toutes en 2023.
- Grappes : 39 mois après 2021 ; 96 mois avant (10 et 30 ans). P_après,10/30 : 76 lignes en 39 mois.
- Témoins retenus sur P : écarts d'échéance 6/9/12 mois (295 lignes), 6/9/15 (4), 6/9/18 (2), 9/12/15 (1).

## 3. Les nombres (témoin)

| Champ | Valeur |
|---|---|
| `schema_ok` (lecture littérale du contrôle 5 ; voir ci-dessous) | **0** (autre lecture : 1) |
| `n_apres` / `n_grappes_apres` | 113 / 39 |
| `n_avant_1030` / `n_grappes_avant_1030` | 184 / 96 |
| `n_temoins_figes` | 7 |
| `ecart_max_rdt_pb` | 4,2 × 10⁻¹¹ |
| **`v_moyen_apres_pb`** (μ_après) | **−0,0107** |
| `erreur_type_apres_pb` | 0,0631 |
| `borne_inf_90_apres_pb` / `borne_sup_90_apres_pb` | −0,1146 / 0,0932 |
| `marge_zone_grise` | −0,4068 |
| `v_moyen_apres_sans_2023_pb` / `v_moyen_apres_sans_30_pb` | −0,0524 / −0,0403 |
| `min_robustesse_pb` / `alerte_robustesse` | −0,0524 / 0 |
| `v_moyen_avant_1030_pb` (ET) | −0,0264 (0,0799) |
| `v_moyen_apres_1030_pb` (ET) | 0,0407 (0,0716) |
| `baisse_1030_pb` (ET) | −0,0671 (0,1073) |
| `borne_inf_90_baisse_pb` | −0,2437 |
| `alerte_instrument` | 1 |

Valeurs complètes (sans arrondi) dans `temoin.json`.

**Contrôles de schéma** : 1, 2, 3, 4, 6, 7, 8, 9, 10, 11 passent. Le contrôle 5, lu à la lettre (« trois CUSIP distincts »
sur toute ligne non écartée par les métadonnées), échoue sur les 8 lignes `prix_manquant` qui n'ont pas trois témoins
valides — ce que la règle 4.4 elle-même prévoit. Tout le reste du contrôle 5 passe (lecture « 5bis »). D'où `schema_ok` = 0
en lecture littérale, 1 en lecture alternative ; c'est le premier point de `ecarts.md`.

## 4. Analyses secondaires — descriptives, sans effet sur la règle

**S1. Mesure de la fiche au rendement limite de 13 h** (`p_carte_pb`, écart de règlement non corrigé) :
P_après 0,557 pb (ET 0,225 ; n = 112, 39 mois ; le 20 ans du 2026-10-21 n'a pas de `high_yield`) ; P_avant,10/30 0,875 pb
(ET 0,222 ; n = 184, 96 mois).

**S2. Forme et absorption** (moyenne, ET groupée par mois) :

| | P_après (113) | P_avant,10/30 (184) |
|---|---|---|
| `montee_pb` = E(J) − E(J−5) | 0,107 (0,053) | 0,120 (0,087) |
| `detente_pb` = E(J) − E(J+5) | −0,117 (0,040) | −0,146 (0,044) |
| `v_pa_pb` (premier ancien contre les mêmes témoins) | 0,019 (0,061) | −0,076 (0,075) |

Descriptivement : l'écart du titre rouvert à ses témoins monte d'environ 0,1 pb entre J−5 et J et continue de monter d'autant
entre J et J+5 (détente négative), dans les deux périodes ; V, qui en est la somme, est donc proche de zéro.

**S3. 2023, le 30 ans et le reste** (V̄, ET groupée, n) :
- par année sur P_après : 2022 0,002 (0,189 ; 24) ; 2023 0,183 (0,133 ; 20) ; 2024 −0,043 (0,140 ; 24) ; 2025 −0,180
  (0,125 ; 24) ; 2026 0,021 (0,085 ; 21) ;
- par échéance sur P_après : 10 ans 0,036 (0,126 ; 37) ; 20 ans −0,116 (0,158 ; 37) ; 30 ans 0,045 (0,096 ; 39) ;
- P_après sans 2023 et sans 30 ans : −0,086 (0,110 ; 62) ;
- les 5 réouvertures à 20 ans d'avant 2022 : −0,032 (0,275 ; 5) ;
- par échéance sur P_avant,10/30 : 10 ans −0,007 (0,137 ; 88) ; 30 ans −0,044 (0,042 ; 96) ;
- écart-type de V (n − 1) : **0,785 pb** sur P_après, **0,936 pb** sur P_avant,10/30 — contre 2,0 / 3,2 / 4,5 pb supposés
  en section 7. Les erreurs types obtenues (0,06 à 0,08 pb) sont donc 4 à 5 fois plus petites que celles du cas central.

## 5. Figure

`figure.png` : V̄ par année (toutes échéances de P), avec IC à 90 % groupé par mois (± 1,645 ET) ; coupure de 2022 marquée
(trait vertical) ; bandes : moyenne 2010-2021 des 10 et 30 ans avec son IC à 90 % (bleu) et μ_après avec son IC à 90 %
(orange, la statistique principale) ; repères à 0 et 0,5 pb. Les points annuels de 2010-2021 incluent les 5 réouvertures à
20 ans de 2021 (descriptif hors préinscription). Les années 2010, 2013 et 2020 (mars 2020) ont les moyennes les plus basses
et, pour 2010 et 2020, les intervalles les plus larges.

## 6. Difficultés rencontrées

1. **Prix « figés » fréquents, et pourquoi.** Tous les prix `END OF DAY` des titres de P sont des multiples de 1/32. Sur une
   page FedInvest typique, environ 6,6 % des notes et obligations (médiane ; jusqu'à 40 %) ont le même prix à J−5 et à J :
   quand le marché revient à peu près au même niveau en cinq séances, la grille de 1/32 rend des prix identiques sans que le
   prix soit gelé. La règle des prix figés (préinscrite) a ainsi sauté 42 témoins, épuisé les candidats de 8 lignes
   (`prix_manquant`) et écarté 4 titres rouverts (`prix_fige`), dont le 10 ans du 2018-12-12 pour lequel la préinscription
   avait prévu l'exception de calendrier du 2018-12-05. Cette règle exclut donc de préférence des fenêtres où les taux ont peu
   bougé ; l'effet sur V n'a pas été mesuré (ce serait une analyse non préinscrite).
2. **Contrôle 5 intenable à la lettre** (ci-dessus et `ecarts.md`).
3. **Réseau** : une seule coupure (2010-03-17, connexion réinitialisée), réussie au deuxième essai. FedInvest est resté
   disponible ; aucune source de remplacement n'a été utilisée.
4. **Pages non identiques octet par octet** à la reprise : uniquement le jeton `_csrf` de session (voir 1.3).
5. **Contrôle de vraisemblance** fait en cours de route : le rendement du titre rouvert à la clôture de J est à −0,65 pb en
   moyenne (écart-type 2,5 pb) du rendement limite ; E(J−5) vaut 1,4 pb en moyenne (écart-type 4,5 pb) ; le rendement du
   titre bouge de 7,7 pb en médiane entre J−5 et J. Les deux codes de rendement s'accordent à 4 × 10⁻¹¹ pb.

## 7. Fichiers

`donnees/` (D1, 905 pages, 17 pages de contrôle, deux journaux, `PROVENANCE.md`) ; `construire.py`, `telecharger.py`,
`comparer_controle.py`, `provenance.py`, `analyse.py` ; `K11_analyse.csv` ; `temoin.json` ; `figure.png` ;
`construire_sortie.txt`, `analyse_sortie.txt`, `comparaison_controle.txt`, `dates_requises.txt` ; `ecarts.md`.
