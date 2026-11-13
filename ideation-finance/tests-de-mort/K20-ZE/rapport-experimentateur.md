# K20-ZE — rapport de l'expérimentateur

Aucun verdict n'est calculé ni écrit ici ; `verdict.py` n'a pas été exécuté. Scellé : sha256 de `preenregistrement.md` conforme
(`91c3f919…e63a`).

## 1. Ce qui a été fait
1. `telecharger.py` : archive de la BCE, trois fichiers Eurostat (et, en facultatif, deux constats du comité de datation).
   HTTP 200 du premier coup ; sha256 identiques à ceux de la préinscription ; `donnees/PROVENANCE.md` (URL, date, HTTP, sha256,
   octets, lignes). Les quatre fichiers lus de l'archive sont extraits tels quels (copie de la racine).
2. `construire.py` : `K20-ZE_analyse.csv` (624 lignes, 30 colonnes dans l'ordre, tri variable/année cible/tour, décimaux en `repr`),
   `construire_journal.json` (sha256, date, HTTP, LAST UPDATE), 12 contrôles de schéma lus sur le fichier écrit
   (`controles_schema.json`).
3. `test_controles.py` : chaque contrôle détecte une altération faite sur une copie (15 altérations : colonne renommée ou
   retirée, ligne retirée, deux lignes permutées, rang = 9, n_rep = 10, ref modifié, prev = 99, révision + 0,01, prev_prec incohérent,
   réalisé d'une année changé partout, principal = 0 sur une ligne principale, principal = 1 sur une ligne incomplète, épisode
   effacé, grande nouvelle forcée à 0 pour un tour) : 15 sur 15 détectées. Deux altérations de lignes hors échantillon principal
   sont comptées dans `n_anomalies_hors_principal` sans compter pour `n_violations_schema` (sauf quand elles touchent aussi des
   lignes principales, ex. réalisé d'une année commun à plusieurs lignes). Le vrai fichier est resté inchangé (octets comparés).
4. `analyse.py` : `temoin.json` (65 champs, entiers pour les comptes et indicatrices) et `figure.png`.
5. `controle_croise.py` (statsmodels) : 35 champs recalculés, écart maximal 2·10⁻¹⁴. `lecture_alternative.py` : voir `ecarts.md` C1.

## 2. Échantillon à chaque filtre
| filtre | HICP | RGDP | UNEM | total |
|---|---|---|---|---|
| grille | 208 | 208 | 208 | 624 |
| `complete` = 1 (6 lignes sans révision : rangs 1 des cibles 2000 et 2001) | 206 | 206 | 206 | 618 |
| `principal` = 1 (exclusion pandémique : 20 lignes RGDP, 20 UNEM) | 206 | 186 | 186 | **578** |
| année en cours / suivante | 104 / 102 | 96 / 90 | 96 / 90 | 296 / 282 |
| grandes nouvelles (L = 1), lignes principales | 70 | 59 | 67 | 196 |
| tours distincts : 107 ; années cibles : 26 ; tours avec au moins une grande nouvelle : 71 | | | | |
Épisodes (lignes principales) : E1 54, E2 72, E3 98, hors épisode 354. Répondants minimum : 44 (tour évalué), 39 (tour précédent).
Seuils de la grande nouvelle : Q_HICP 0,4667 (coupure stricte), Q_RGDP 0,5 (stricte), Q_UNEM 0,2 (large, voir ambiguïté C1).

## 3. Nombres de `temoin.json`
Schéma : `n_violations_schema` 0 ; `n_anomalies_hors_principal` 0. Comptes : `n_principal` 578 ; `n_tours` 107 ;
`n_annees_cibles` 26 ; `n_grands` 196 ; `n_tours_grands` 71.

Test principal : `c` −0,1060 ; `et_c_dk8` 0,0898 ; `t_c` −1,180 ; IC 90 % [−0,2593 ; +0,0474] (valeur critique 1,708).
`b_moyen` 0,4468 (ET 0,0868, borne basse 0,2985) ; `pente_moyenne_grandes` 0,3408 ; `k_moyen` 0,4269.
Contrôle positif : `b_commun` 0,3657 (ET 0,0570, borne basse 0,2684) ; `controle_positif_ok` 1.
Pertinence : `rapport_variance_revision` 8,415 (a = 0,2737, A = 2,3035) ; `rapport_variance_ecart_prec` 2,662 ;
`pertinence_manquante` 0 ; `biais_mecanique_nu20` 0,4251 ; `seuil_survie_bas` 0,4251 ;
`borne_basse_moins_seuil` −0,6844 ; `marge_indecision` −0,3526.
Épisodes : c sans E1/E2/E3 = −0,0643 / −0,1854 / −0,1669 ; t = −0,733 / −2,000 / −1,247 ;
`t_min_sans_episode` −2,000 ; `episode_t_min` 2 ; `c_min_sans_episode` −0,1854 ; `conflit_robustesse` 0.
Effectifs : `et_c_iid` 0,1013 ; `n_effectif` 735 (supérieur à n = 578 : l'écart-type de Driscoll-Kraay est plus petit que l'iid).
Secondaires : ET à 4 / 12 / 0 retards 0,0868 / 0,0941 / 0,0986 ; par année cible 0,0791 ;
avec pandémie c = +0,1767 (ET 0,0773) ; avant 2020 −0,1491 (0,1343) ; année en cours −0,0112 (0,1299) ; année suivante
−0,1977 (0,1506) ; médiane −0,0314 (0,1023) ; coupure de la fiche −0,2293 (0,1315) ; surprise relative au consensus
(554 lignes) −0,2707 (0,1131) ; par variable HICP +0,1270 (0,1714), RGDP −0,2165 (0,1626), UNEM −0,1511 (0,2086).
Pentes de base par série : HICP h0 0,664, h1 0,222 ; RGDP h0 0,547, h1 0,277 ; UNEM h0 0,504, h1 0,467.

## 4. Remarques de lecture (sans verdict)
- Le plancher de survie (0,425) est bien au-dessus de 0,10 parce que le rapport A/a vaut 8,4 ici, contre 3 dans la simulation
  de la préinscription ; la formule de 6.7 est appliquée telle quelle.
- La seule analyse secondaire de signe positif franc est celle avec la pandémie (+0,177) ; les autres sont négatives ou proches de 0.
- Ambiguïté de 6.2 sur les égalités de |surprise| : deux lectures, mêmes indicateurs, chiffres différents au-delà de la tolérance
  (`ecarts.md` C1). `temoin.json` suit la lettre (doubles sans arrondi).

## 5. Fichiers
`telecharger.py`, `construire.py`, `test_controles.py`, `analyse.py`, `controle_croise.py`, `lecture_alternative.py`,
`K20-ZE_analyse.csv`, `construire_journal.json`, `controles_schema.json`, `analyse_detail.json`, `lecture_alternative.json`,
`temoin.json`, `figure.png`, `ecarts.md`, `donnees/PROVENANCE.md`. Exécution : `python3 -I <script>` depuis le dossier ;
ordre : telecharger, construire, test_controles, analyse, controle_croise.
