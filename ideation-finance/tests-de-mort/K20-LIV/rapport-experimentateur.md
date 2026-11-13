# K20-LIV — rapport de l'expérimentateur

Je ne calcule ni n'écris de verdict, et je n'ai pas lancé `verdict.py`. Les chiffres ci-dessous sont un témoin ; le vérificateur recalcule.

## 1. Contrôle du sceau
`sha256(preenregistrement.md)` = e3afba764025ed5cd33b3caa8959d742f1d7d4e7616e28b4edaf153be811e505, identique au fichier `.sha256`. Lu en entier : préinscription, `protocole.md`, `verdict.py`.

## 2. Ce qui a été fait
1. `telecharger.py` : 12 fichiers, tous en HTTP 200, au premier essai (Fed : `means`, `medians`, `individualdata`, documentation ; FRED : `CPIAUCNS`, `CPIAUCSL`, `UNRATE`, `DPRIME`, `DTB3`, `HOUST`, `USRECP`, `USREC`). URL, date, code, sha256, taille, lignes dans `donnees/PROVENANCE.md` (et `construire_journal.json`). Les sha256 des trois fichiers de la Fed sont ceux de la préinscription.
2. `construire.py` → `K20-LIV_analyse.csv` : 555 lignes, 40 colonnes dans l'ordre, tri variable puis cible. Contrôles dans `controles.py`, relus sur le fichier écrit.
3. `test_alterations.py` : chaque contrôle 1 à 11 détecte une altération délibérée faite sur une copie en mémoire (sortie dans `test_alterations_sortie.txt`) ; trois altérations hors lignes principales (contrôles 6, 3, 8) sont comptées comme anomalies et non comme violations. Certaines altérations déclenchent aussi des contrôles voisins (une cible fausse viole aussi 3 et 5), ce qui est normal.
4. `analyse.py` → `temoin.json`, `figure.png`, `analyse_diagnostics.json`, depuis le seul fichier d'analyse. `controle_croise.py` (statsmodels) retrouve c, et_c_dk2, b_regroupe, et_b_regroupe_dk2, et_c_iid à 6 décimales.

## 3. Échantillon à chaque filtre
| Variable | lignes | complètes | principales | grandes nouvelles (L = 1) |
|---|---|---|---|---|
| CPI | 158 | 156 | 156 | 52 |
| UNPR | 129 | 128 | 124 | 41 |
| PRIME | 89 | 89 | 89 | 30 |
| TBILL | 67 | 67 | 67 | 22 |
| TPHS | 112 | 112 | 112 | 37 |
| **Total** | **555** | **552** | **548** | **182** |

Lignes incomplètes : CPI 2005-06 (par règle), CPI 2026-06 et UNPR 2026-06 (octobre 2025 absent). Complètes hors principal : UNPR 2020-06, 2020-12, 2021-06, 2021-12. 158 semestres cibles distincts, 110 avec au moins une grande nouvelle. Comptes par épisode (principal) : E1 5, E2 4, E3 4, E4 4, E5 13, E6 15, E7 28, E8 12, E9 20, E10 30, E11 36, hors épisode 377 : conformes.
Contrôles de schéma : `n_violations_schema` = 0 ; anomalies hors lignes principales : 0.

## 4. Chiffres de `temoin.json`
Statistique principale (Driscoll-Kraay, 2 semestres) :
- c = −0,12219 ; et_c_dk2 = 0,13909 ; t_c = −0,879 ; IC à 90 % [−0,35099 ; +0,10661]
- b_moyen = 0,44305 ; pente_moyenne_grandes = 0,32086 ; k_moyen = 1,01517
- n_principal = 548 ; n_violations_schema = 0 ; n_grands = 182 ; n_dates = 158 ; n_dates_grands = 110
- et_c_iid = 0,11483 ; n_effectif = 373,5 ; et_c_dk4 = 0,14060 ; et_c_dk0 = 0,14137

Contrôle positif : b_regroupe = 0,37277 ; et = 0,06681 ; borne basse à 90 % = 0,26287 ; `controle_positif_ok` = 1.

Pertinence et biais : rapport_variance_revision = 10,100 ; nu_mesure = 0,015558 (ν_v : CPI 0,00984, UNPR 0,01862, PRIME 0,01173, TBILL 0,01285, TPHS 0,02476) ; biais_mecanique_mesure = 0,12198 ; biais_mecanique_nu20 = 0,78399 ; seuil_survie_bas = 0,12198 ; borne_basse_moins_seuil = −0,47297 ; marge_indecision = −0,29339.

Épisodes : c sans E1…E11 = −0,0564 ; −0,1233 ; −0,1185 ; −0,1247 ; −0,1306 ; −0,1288 ; −0,0693 ; −0,1026 ; −0,0919 ; −0,1114 ; −0,1124. t_min_sans_episode = −0,920 (episode_t_min = 6) ; c_min_sans_episode = −0,13062 ; conflit_robustesse = 0.

Secondaires (c ; écart-type) : par variable CPI −0,2235 ; 0,3923 | UNPR +0,3784 ; 0,2861 | PRIME −0,4421 ; 0,2553 | TBILL −0,0258 ; 0,2700 | TPHS −0,4690 ; 0,2931. Avec la pandémie −0,3199 ; 0,1490. Depuis 1985 −0,0394 ; 0,1527. Avant 2020 −0,1612 ; 0,1544. Médianes −0,0948 ; 0,1234. Coupure de la fiche (|z_r| > 1) −0,1841 ; 0,1126.

Hors règle : pentes de base par variable CPI 0,558, UNPR 0,427, PRIME 0,231, TBILL 0,594, TPHS 0,405. IPC, lignes principales dont la base du questionnaire s'écarte de plus de 0,005 en log des mois de base (hors changements de base d'indice) : 2 sur 152.

## 5. Ambiguïtés
Voir `ecarts.md` : lectures de a et A (groupée retenue ; rapport 10,100 contre 11,325 par variable ; biais 0,1220 contre 0,1273), ancrage CPI 2005-06, facteur 0,10 de `biais_mecanique_nu20`, journal JSON et PROVENANCE.md. Aucun écart à la préinscription.

## 6. Fichiers
`telecharger.py`, `construire.py`, `controles.py`, `test_alterations.py`, `analyse.py`, `controle_croise.py`, `K20-LIV_analyse.csv`, `temoin.json`, `figure.png`, `analyse_diagnostics.json`, `controles_resultat.json`, `ecarts.md`, `donnees/PROVENANCE.md` (données brutes non versionnées, `.gitignore`).
