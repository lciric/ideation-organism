# K20-ZE — Rapport du vérificateur

Rédigé le 2026-11-13 par le vérificateur de K20-ZE. Ce rapport ne contient pas de verdict et `verdict.py` n'a pas été
exécuté. Les chiffres complets, en double précision, sont dans `verification.json`. Dans ce rapport, ils sont arrondis
pour la lecture.

## 1. Ce que j'ai lu

J'ai lu quatre fichiers et aucun autre :
- `K20-ZE/preenregistrement.md`, en entier ;
- `K20-ZE/K20-ZE_analyse.csv` ;
- `tests-de-mort/protocole.md` ;
- `tests-de-mort/verdict.py`.

Je n'ai ouvert aucun autre fichier : ni les scripts de l'expérimentateur, ni `temoin.json`, ni ses rapports, ni `ecarts.md`,
ni les fichiers de détail, de lecture alternative, de contrôle, de journal ou de simulation, ni la figure, ni le dossier
`donnees/`, ni un autre dossier de test. La liste du dossier (`ls`) m'a montré les noms des fichiers, pas leur contenu.

**Sceau.** sha256 de `preenregistrement.md` =
`91c3f919cbf571abfeee2e087b387b4962960e183f832a7e4983de7bb802e63a`. C'est la valeur de `preenregistrement.md.sha256` :
**le sceau est conforme**. sha256 du fichier d'analyse vérifié :
`6964ed68b6f4dae1a6eced333879d0750370d6bb162e0dc16db14b97bb8dfbb6`.

## 2. Code

- `verification.py` : mon code, écrit sans rien reprendre d'ailleurs. Il lit le CSV en texte, refait les 12 contrôles de
  schéma, calcule tous les champs de `champs_verification` (numpy pour les moindres carrés et pour Driscoll-Kraay) et écrit
  `verification.json`. Les 65 champs y sont, en nombres, avec des entiers pour les comptes et les indicatrices.
- `verification_controle.py` : une seconde implémentation, indépendante de la première. La lecture passe par pandas, la
  réduction par `groupby`, et le quantile est écrit à la main. Les régressions passent par `statsmodels.OLS`, Driscoll-Kraay
  par `statsmodels` (`cov_nw_groupsum`, avec un temps codé t_tour − min : les tours vides y comptent, puisque la somme passe
  par `bincount`), les grappes par année aussi par `statsmodels` (`cov_cluster` sans correction), et c avec son écart-type
  de Driscoll-Kraay par `linearmodels` (`PanelOLS`, noyau de Bartlett de largeur 8).
  **Résultat** : 45 champs sont recalculés de cette façon. Le plus grand écart est 4·10⁻¹⁵ sur les coefficients,
  écarts-types, bornes et t, et 3·10⁻¹² sur `n_effectif`. Avec `linearmodels` : c = −0,105963, et_DK = 0,089770, comme
  dans `verification.py`.

## 3. Contrôles de schéma (section 4.4)

Portée appliquée à la lettre :
- les contrôles 1 et 2 portent sur le fichier entier ;
- les contrôles de ligne (3 à 9, 11 et 12) sont faits sur toutes les lignes, mais ne comptent pour `n_violations_schema` que
  s'ils échouent sur une ligne où `principal` = 1. Leurs échecs ailleurs vont dans `n_anomalies_hors_principal` ;
- le contrôle 10 compte sur toutes les lignes.

Pour un contrôle entre lignes (n° 8), l'échec est attribué à la ligne vérifiée. Pour la constance dans un même
(v, `t_tour`), il est attribué à toutes les lignes du groupe.

| N° | Ce que j'ai vérifié sur le fichier | Résultat |
|---|---|---|
| 1 | les 30 noms de colonnes de 4.1, dans l'ordre, sans autre | conforme |
| 2 | 624 lignes ; la grille (3 variables × 26 années × rangs 1-8) est présente, chaque (`variable`, `annee_cible`, `t_tour`) une seule fois ; le tri suit HICP, RGDP, UNEM, puis l'année, puis le tour | conforme |
| 3 | `tour` de forme `AAAAQn` ; `t_tour` = 4 × année + trimestre − 1 ; `rang` = `t_tour` − 4(`annee_cible` − 1) + 1, dans [1 ; 8] ; `horizon` = année cible − année du tour, et 1 si et seulement si `rang` ≤ 4 ; `tour_prec` est le tour `t_tour` − 1 ; `horizon_prec` = année cible − année de `tour_prec`, dans {0, 1, 2} ; entiers écrits sans décimale | 0 échec |
| 4 | `prev` présent si et seulement si `n_rep` ≥ 20, et de même pour `prev_prec` avec `n_rep_prec` ; sur les lignes principales : `n_rep` ≥ 20, `n_rep_prec` ≥ 20, et `prev`, `prev_prec`, `prev_med`, `prev_prec_med` présents. Minimum relevé sur les lignes principales : 44 et 39 (le texte annonce 44 et 39) | 0 échec |
| 5 | `ref` et `ref_periode` présents à chaque tour ; `ref_periode` suit la règle de 3.1 avec ses exceptions (HICP 2024T2 → `2024Feb` ; UNEM 2000T1, 2023T1, 2023T4, 2024T1, 2024T2, 2024T4) ; `ref_prec` et `ref_periode_prec` présents et conformes à la règle du tour précédent, vides quand le tour précédent est 1998T4 | 0 échec |
| 6 | plages de `prev`, `prev_prec`, `prev_med`, `prev_prec_med`, `realise`, `ref`, `ref_prec` par variable | 0 échec |
| 7 | les six différences égales à leurs termes à 10⁻⁹ près, vides si et seulement si un terme est vide (en fait égales **exactement** en double : 621/621 surprises, 618/618 révisions, 624/624 erreurs) ; `prev_glissante_t4` vide quand le tour `t_tour` − 4 est avant 1999T1 | 0 échec |
| 8 | `prev_prec` et `n_rep_prec` égaux (texte identique) au `prev` et au `n_rep` de la ligne (v, y, `t_tour` − 1) quand elle existe ; `ref`, `ref_periode`, `ref_prec`, `surprise`, `grande_nouvelle` constants dans chaque (v, `t_tour`) ; `ref_prec`(v, t) = `ref`(v, t − 1) | 0 échec |
| 9 | `realise` présent, une seule valeur par (`variable`, `annee_cible`), pour les 78 couples 2000-2025 | 0 échec |
| 10 | `complete` et `principal` recalculés sur les 624 lignes à partir de leurs propres colonnes (règle de 4.2) | 0 désaccord |
| 11 | `episode` recalculé par `t_tour` − 1 ≤ T_k et 4 × `annee_cible` + 3 ≥ P_k, fenêtres 8032-8037, 8046-8052 et 8079-8095 ; aucune ligne dans deux fenêtres | 0 échec |
| 12 | `grande_nouvelle` présente si et seulement si `surprise` l'est ; constante dans chaque (v, `t_tour`) ; égale au L que je recalcule par 6.2 (Q_v et coupure recalculés) | 0 échec, voir la section 6, ambiguïté 1 |

**`n_violations_schema` = 0. `n_anomalies_hors_principal` = 0.**

**Ce qu'on ne peut pas vérifier sur le fichier seul.** Certaines parties des contrôles 4, 5, 7 et 9 comparent le fichier aux
fichiers bruts. La préinscription dit que le vérificateur refait les contrôles « sur le fichier » et la règle d'aveuglement
interdit `donnees/`. Je ne les ai donc **pas** faites :
- `n_rep` égal au nombre de réponses individuelles ;
- `ref` égal à la ligne `ECB` ;
- au moins 20 prévisions glissantes quand `prev_glissante_t4` est présente ;
- `realise` égal à l'`OBS_VALUE` d'Eurostat, ou à la moyenne des 12 mois.

Je les ai remplacées par des contrôles indirects, qui ne comptent pas :
- `ref` et `ref_prec` ont au plus une décimale ;
- `realise` a au plus une décimale pour HICP et RGDP ;
- pour UNEM, 12 × `realise` est un nombre à une décimale, donc compatible avec une moyenne de 12 valeurs mensuelles à une
  décimale ;
- la présence de la médiane suit celle de la moyenne ;
- quand le tour précédent est 1998T4, `n_rep_prec` = 0 et `prev_prec` est vide ;
- `ref_periode_prec`, `prev_glissante_t4` et `surprise_consensus` sont constants dans un même tour ;
- l'échantillon S8 compte 103, 96 et 89 tours, les comptes annoncés en 4.4, contrôle 7.

**Aucun de ces contrôles indirects n'échoue.**

## 4. Échantillon

Tous les comptes de 4.3 sont retrouvés exactement :

| | HICP | RGDP | UNEM | Total |
|---|---|---|---|---|
| lignes | 208 | 208 | 208 | 624 |
| `complete` = 1 | 206 | 206 | 206 | 618 |
| `principal` = 1 | 206 | 186 | 186 | **578** |
| année en cours / année suivante | 104 / 102 | 96 / 90 | 96 / 90 | 296 / 282 |

- 107 tours, de 1999T2 (7997) à 2025T4 (8103), sans trou.
- 26 années cibles.
- De 2 à 6 lignes par tour, 5,40 en moyenne.
- Lignes par épisode (E1, E2, E3, hors épisode) : 54, 72, 98 et 354 parmi les principales ; 54, 72, 138 et 360 sur tout le
  fichier.

## 5. Chiffres

### Grande nouvelle (6.2)

| Variable | \|T_v\| | Q_v (double) | n_> | n_≥ | Coupure | Tours L = 1 | Lignes principales L = 1 |
|---|---|---|---|---|---|---|---|
| HICP | 107 | 0,4666666666666657 | 36 | 36 | stricte | 36 | 70 |
| RGDP | 99 | 0,5 | 30 | 40 | stricte | 30 | 59 |
| UNEM | 99 | 0,20000000000000107 | 30 | 35 | large | 35 | 67 |

`n_grands` = 196 ; `n_tours_grands` = 71.

### Test principal (6.1-6.5, 6.10)

| Champ | Valeur |
|---|---|
| `n_principal` | 578 |
| `c` | **−0,105963** |
| `et_c_dk8` | 0,089770 |
| `t_c` | −1,1804 |
| `borne_basse_ic90` ; `borne_haute_ic90` | **−0,259290 ; +0,047364** |
| `et_c_iid` ; `n_effectif` | 0,101260 ; 735,43 (supérieur à n, ce que la section 8.3 annonce possible) |
| k_g (HICP h0, h1 ; RGDP h0, h1 ; UNEM h0, h1) | 0,6532 ; 0,1776 ; 0,5985 ; 0,1835 ; 0,5936 ; 0,3551 |
| `k_moyen` | 0,426927 |
| b_g (même ordre) | 0,6640 ; 0,2221 ; 0,5473 ; 0,2769 ; 0,5038 ; 0,4665 |
| `b_moyen` ; `et_b_moyen_dk8` ; `borne_basse_b_moyen_ic90` | 0,446776 ; 0,086833 ; 0,298465 |
| `pente_moyenne_grandes` | 0,340812 |

### Contrôle positif (6.6)

| Champ | Valeur |
|---|---|
| `b_commun` ; `et_b_commun_dk8` | **0,365654** ; 0,056960 |
| `borne_basse_b_commun_ic90` | 0,268367 |
| `controle_positif_ok` | **1** (les deux bornes basses sont au-dessus de 0) |

### Pertinence et biais mécanique (6.7)

| Champ | Valeur |
|---|---|
| a ; A (révisions) | 0,273738 ; 2,303548 |
| `rapport_variance_revision` | 8,415145 |
| `rapport_variance_ecart_prec` (a = 0,622138 ; A = 1,656109) | 2,661965 |
| `pertinence_manquante` | 0 |
| `biais_mecanique_nu20` | 0,425063 |
| `seuil_survie_bas` | 0,425063 |
| `borne_basse_moins_seuil` | −0,684354 |
| `marge_indecision` | −0,352636 |

### Épisodes (6.8, 6.9)

| | c sans Ek | t sans Ek |
|---|---|---|
| E1 | −0,064332 | −0,7326 |
| E2 | −0,185351 | −1,9999 |
| E3 | −0,166932 | −1,2467 |

- `t_min_sans_episode` = −1,999928, atteint pour `episode_t_min` = 2.
- `c_min_sans_episode` = −0,185351.
- `conflit_robustesse` = 0.

### Analyses secondaires (6.11)

| Analyse | c | Écart-type |
|---|---|---|
| S2, même c, à 4 / 12 / 0 retards | | 0,086778 / 0,094052 / 0,098567 |
| S2, grappes par année cible (26) | | 0,079064 |
| S3, avec la pandémie (618 lignes) | +0,176700 | 0,077342 |
| S4, années cibles ≤ 2019 | −0,149141 | 0,134322 |
| S5, année en cours | −0,011219 | 0,129866 |
| S5, année suivante | −0,197682 | 0,150563 |
| S6, médianes | −0,031433 | 0,102284 |
| S7, coupure de la fiche, \|z_r\| > 1 | −0,229342 | 0,131479 |
| S8, surprise relative au consensus (`n_surprise_consensus` = 554) | −0,270698 | 0,113137 |
| S1, HICP | +0,126985 | 0,171377 |
| S1, RGDP | −0,216518 | 0,162617 |
| S1, UNEM | −0,151139 | 0,208634 |

En S8, les seuils Q''_v valent 0,92366 (HICP), 0,86949 (RGDP) et 0,61207 (UNEM). La coupure est stricte partout, avec 34,
32 et 30 tours classés grands.

## 6. Ambiguïtés du texte et lecture retenue

1. **Égalités de |surprise| en double précision (6.2), le point principal.** Les valeurs de référence ont une décimale,
   mais `surprise` = `ref` − `ref_prec` est calculée en double. Des surprises égales en décimal diffèrent donc au 16ᵉ chiffre
   (par exemple 8,7 − 8,9 = −0,20000000000000107 ; 9,0 − 9,2 = −0,1999999999999993 ; −0,6 − (−1,1) = 0,5000000000000001).
   - **Lecture retenue : la lettre.** C'est `numpy.quantile` sur la colonne `surprise` telle qu'écrite, et les comparaisons
     > ou ≥ sur ces doubles, conformément à la section 6 (« en double précision, sans arrondi intermédiaire ») et à 4.1
     (décimaux en `repr`, sans arrondi). Cette lecture est cohérente avec elle-même : elle ne coupe aucun groupe de doubles
     égaux. Elle s'écarte seulement de l'intention écrite en 6.2 (« on ne coupe jamais à l'intérieur d'un groupe de valeurs
     égales »), si l'on entend « égales » au sens décimal.
   - **Conséquence.** Pour RGDP, un tour du groupe |s| = 0,5 est classé grand : 2013T4, avec 0,5000000000000001. Les 12
     autres ne le sont pas. Pour UNEM, la coupure est large au seuil 0,20000000000000107 : les cinq tours valant exactement
     ce double sont classés grands (2001T2, 2005T4, 2015T3, 2016T3, 2017T4), les 17 autres « 0,2 » ne le sont pas.
   - **Le `grande_nouvelle` du fichier suit exactement cette lecture** : contrôle 12, 0 échec.
   - **Sensibilité, hors `verification.json`** (dans `verification_controle.py`). J'ai refait le calcul en arrondissant
     |s| à une décimale. Ces 6 tours, soit 12 lignes principales, passent à L = 0 ; la coupure UNEM devient stricte
     (30 tours) et `n_grands` tombe à 184. On obtient alors :
     - c = −0,0993, écart-type 0,0856, intervalle [−0,2455 ; +0,0470] ;
     - `b_moyen` = 0,4406, rapport des variances 8,914, plancher 0,4281 ;
     - c sans E1, E2, E3 = −0,051, −0,172, −0,160, avec t = −0,64, −1,90, −1,23.

     L'écart sur c (0,0066) dépasse la tolérance de 0,005. Sous cette autre lecture, le contrôle 12 échouerait aussi sur 12
     lignes principales. Le choix de lecture compte donc pour la comparaison avec l'expérimentateur, même s'il déplace peu
     les bornes.
2. **Poids de Bartlett à 4 et 12 retards (S2).** Le texte n'écrit les poids que pour 8 retards (1 − j/9). J'ai pris
   1 − j/(m + 1) pour m retards, soit 1 − j/5 et 1 − j/13, la forme dont 1 − j/9 est le cas m = 8. À 0 retard : Ω = Σ H_τ H_τ'.
3. **Étendue des tours pour Driscoll-Kraay.** Les tours vont du plus petit au plus grand `t_tour` de chaque échantillon. Les
   tours vides valent un vecteur nul et les retards se comptent en numéros de tour. Dans l'échantillon principal, aucun
   tour ne manque entre 7997 et 8103. Dans les exclusions d'épisode, les tours retirés deviennent des tours vides. Les tours
   vides aux bords ne changent rien.
4. **S3, S8 et la réduction.** Pour S3, les constantes de réduction et le L de l'échantillon principal sont appliqués aux
   lignes `complete` = 1 (6.1 et 6.2 le disent). Pour S8, les z restent ceux de l'échantillon principal. L'' est construit
   comme en 6.2 sur |`surprise_consensus`|, avec T_v = tours distincts des lignes principales où elle est présente.
5. **S7 et S8.** L' et L'' remplacent L partout dans l'équation de 6.3 : effets de classe et interaction.
6. **S1.** Il y a 6 constantes, 6 effets de classe, 6 pentes de base, puis z_r·L·D_v pour HICP, RGDP et UNEM, soit 21
   paramètres.
7. **`episode_t_min`.** Il est écrit sous forme de l'entier k (2 pour E2), puisque les champs sont numériques.
8. **p (6.7).** J'ai pris p = `erreur` + `revision`, la première écriture du texte. L'autre écriture, `realise` −
   `prev_prec`, en diffère d'au plus 8,9·10⁻¹⁶ (602 lignes sur 618 identiques). C'est sans effet visible sur le rapport.
9. **Valeur critique.** J'ai pris 1,708 tel qu'écrit, et non le quantile exact de Student à 25 degrés de liberté
   (1,70814).
10. **Exclusion pandémique.** J'ai appliqué la règle opératoire de 4.2 (`t_tour` entre 8080 et 8087, ou année cible 2020
    ou 2021). Les justifications de 2.2-8 et 4.2 parlent de retirer toute ligne dont « la révision ou la surprise tombe
    dans la pandémie ». Les lignes RGDP et UNEM du tour 2022T1 sont pourtant gardées par la lettre, alors que leur révision
    part du tour 2021T4 et que leur surprise compare deux données de 2021. La plus grande surprise de l'échantillon
    principal en fait partie : RGDP 2022T1, −10,4 (de 14,3 % pour 2021T2 à 3,9 % pour 2021T3), un effet de base du rebond.
    Comme L est binaire, sa taille ne pèse que par le classement : ce tour est classé grand de toute façon. Je le signale ;
    ce n'est pas une anomalie du fichier par rapport à la lettre.

## 7. Ce qui paraît anormal ou mérite d'être noté

- **Le fichier : rien d'anormal.** Les 12 contrôles passent sur toutes les lignes, principales ou non. Les différences sont
  exactes en double. Les comptes de 4.3 sont retrouvés au chiffre près. Le `grande_nouvelle` du fichier est celui de la
  lettre.
- **Le plancher calculé dépasse la prédiction.** `rapport_variance_revision` vaut 8,4, contre environ 3 envisagé en
  section 7 (chiffre de K20). Avec a = 0,27, le biais mécanique calculé vaut 0,425. `seuil_survie_bas` est donc
  au-dessus de 0,40, alors que la section 7 attendait un plancher de 0,10. Je le note sans l'interpréter.
- **Driscoll-Kraay plus petit que l'iid** (0,0898 contre 0,1013, `n_effectif` = 735 > 578). La section 8.3 l'annonce comme
  possible. L'écart-type par grappes d'année (0,079) est plus petit encore.
- **Valeurs extrêmes de z_r dans l'échantillon principal** : HICP 2023 au tour 2022T4 (+7,3), HICP 2022 au tour 2022T2
  (+6,6), RGDP 2009 au tour 2009T1 (−4,9). Toutes sont classées L = 1 et appartiennent à E1 ou E3.
- **L'ambiguïté 1 (section 6) est le seul point de lecture qui déplace un chiffre au-delà d'une tolérance.**

## 8. Fichiers écrits par le vérificateur

- `K20-ZE/verification.py`
- `K20-ZE/verification.json`
- `K20-ZE/verification_controle.py`
- `K20-ZE/rapport-verificateur.md`

Aucun fichier existant n'a été modifié.
