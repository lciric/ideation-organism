# K20-ZE — écarts et ambiguïtés (expérimentateur)

Scellé vérifié avant tout : sha256 de `preenregistrement.md` = `91c3f919…e63a`, identique à `preenregistrement.md.sha256`.

## A. Écarts à la préinscription

Aucun écart de données : l'archive de la BCE (`49348fa3…51f4`) et les trois fichiers Eurostat (`43ef7b6b…`, `0b8e98ab…`,
`7842067c…`, mises à jour 17/09/26, 11/11/26, 05/11/26) sont identiques à ceux décrits en 3.1-3.2. Aucun fichier manquant,
1 essai par téléchargement. Aucun échantillon sous 50 lignes, aucune matrice singulière (`analyse_detail.json`, `incidents` vide).
Comptes de 4.3 retrouvés exactement (624 / 618 / 578 ; 296 / 282 ; épisodes 54-72-98-354 et 54-72-138-360 ; 107 tours ; 26 années).

Ajouts mineurs, sans effet sur un chiffre :
1. `telecharger.py` télécharge aussi, en facultatif, les deux constats du comité de datation cités en 6.8 (HTTP 200, sha256
   identiques à ceux de la préinscription). Ils ne servent à aucun calcul.
2. Fichiers non demandés écrits dans le dossier : `controles_schema.json`, `analyse_detail.json`, `lecture_alternative.py/.json`,
   `test_controles.py`, `controle_croise.py`.

## B. Aveuglement

- Je n'ai ouvert aucun fichier d'un autre dossier de `tests-de-mort/`, ni rien sous `projects/`, ni `simulation_decision*` de K20-ZE.
- Hors consigne stricte, j'ai lu `/home/user/ideation-organism/.gitignore` et `ideation-finance/.gitignore` (pour savoir si
  `PROVENANCE.md` est versionné) et fait un `ls` de K20-ZE (qui montre les noms `simulation_decision*`, non ouverts) et
  un `git status`/`git check-ignore` limités à K20-ZE.

## C. Ambiguïtés de la préinscription et lecture retenue

### C1. Égalités dans la coupure de la grande nouvelle (6.2) — **la seule qui change des chiffres**
Le texte demande `numpy.quantile` sur |`surprise`| « en double précision, sans arrondi intermédiaire », et justifie aussi la
coupure par les « beaucoup d'égalités » des valeurs à une décimale (« on ne coupe jamais à l'intérieur d'un groupe de valeurs
égales »). Mais `surprise` = `ref` − `ref_prec` en double donne par exemple 0,2000000000000011 pour une paire et 0,19999999999999929
pour une autre : les égalités décimales n'en sont pas dans le fichier, et la coupure peut tomber au milieu d'un groupe.
- **Lecture A (retenue, plus proche de la lettre)** : doubles du fichier, sans arrondi. `grande_nouvelle` du fichier est
  celle-ci (le contrôle 12 la retrouve). Q_HICP = 0,4667 (stricte, 36/107), Q_RGDP = 0,5 (stricte, 30/99), Q_UNEM = 0,200000000000001
  (large, 35/99 ; 30 en stricte).
- **Lecture B (intention affichée)** : |`surprise`| arrondi à 6 décimales avant Q_v et la coupure. Q_UNEM = 0,2 exactement, coupure
  stricte (30/99 ; la coupure large donnerait 52/99), RGDP strict 29/99. 14 lignes changent de L (12 principales).
  Chiffres complets dans `lecture_alternative.json` (script `lecture_alternative.py`, ne touche pas `temoin.json`).

| champ | A (temoin.json) | B (arrondie) |
|---|---|---|
| n_grands / n_tours_grands | 196 / 71 | 184 / 67 |
| c | −0,10596 | −0,09928 |
| et_c_dk8 | 0,08977 | 0,08562 |
| t_c | −1,180 | −1,160 |
| borne_basse_ic90 / borne_haute_ic90 | −0,2593 / +0,0474 | −0,2455 / +0,0470 |
| b_moyen | 0,4468 | 0,4406 |
| controle_positif_ok | 1 | 1 |
| rapport_variance_revision | 8,415 | 8,914 |
| seuil_survie_bas | 0,4251 | 0,4281 |
| borne_basse_moins_seuil | −0,6844 | −0,6736 |
| marge_indecision | −0,3526 | −0,3530 |
| pertinence_manquante | 0 | 0 |
| c_sans_E1 / E2 / E3 | −0,0643 / −0,1854 / −0,1669 | −0,0514 / −0,1717 / −0,1601 |
| t_sans_E1 / E2 / E3 | −0,733 / −2,000 / −1,247 | −0,638 / −1,899 / −1,232 |
| t_min_sans_episode (épisode) | −2,000 (E2) | −1,899 (E2) |
| c_min_sans_episode | −0,1854 | −0,1717 |
| conflit_robustesse | 0 | 0 |
| n_effectif | 735 | 800 |

Les écarts entre A et B dépassent la tolérance de 0,005 sur c (0,0067), sur b_moyen (0,0062) et sur plusieurs bornes/t, et valent
11 sur `n_grands`. **Un vérificateur qui arrondirait la surprise et un autre qui ne l'arrondirait pas ne s'accorderaient donc pas.**
Je n'ai pas choisi d'après les résultats : A a été fixé avant de calculer B. Les champs d'indicateurs (controle_positif_ok,
pertinence_manquante, conflit_robustesse, episode_t_min) sont les mêmes dans les deux lectures. Les conditions de la règle
(signe de `borne_basse_moins_seuil`, `borne_haute_ic90` < 0,40, `marge_indecision` < 0) tombent du même côté dans les deux.

### C2. Autres lectures, sans effet connu sur un chiffre
- **Contrôles de schéma** : « n_anomalies_hors_principal » compté comme nombre de couples (contrôle, ligne) en échec sur les lignes
  `principal` ≠ 1, un couple par contrôle et par ligne. Les contrôles 1, 2 et 10 comptent toujours pour le verdict. J'ai ajouté deux
  vérifications implicites au contrôle 5 (ref et ref_periode vides avant 1999T1, périodes comparées à la règle de 3.1 y compris
  exceptions) et au contrôle 7 (valeur de `prev_glissante_t4` égale à la moyenne brute à 10⁻⁹ près). Résultat : 0 échec, 0 anomalie.
- **6.7** : `a` et `A` calculés sur les lignes principales (« toutes les lignes L = 0 / 1 » lu comme tout l'échantillon principal,
  moyennes m_{g,ℓ} par série). `z_p` réduit par série (moyenne et écart-type n−1 sur les lignes principales).
- **6.8** : `episode_t_min` écrit en entier k (1, 2 ou 3).
- **6.11** : pour S1, S3, S4, S5, S6, S7, les z viennent de l'échantillon principal (moyennes/écarts-types des lignes principales),
  même quand le sous-échantillon est plus grand (S3) ou plus petit. Pour S6, médianes réduites par série sur les lignes principales.
  S8 : T_v = tours distincts des lignes principales de v où `surprise_consensus` est présente. `et_c_grappes_annee` : scores
  sommés par `annee_cible`, Ω = Σ H_y H_y', sans retard ni correction.
- Les tours sans ligne en début ou fin de sous-échantillon n'influent pas sur Ω (vecteur nul) ; la fenêtre va du plus petit au plus
  grand `t_tour` du sous-échantillon.
- `n_violations_schema` et `n_anomalies_hors_principal` viennent des contrôles de `construire.py` relancés sur le fichier
  (ils lisent aussi les fichiers bruts, ce que la préinscription demande pour les contrôles 5, 7 et 9) ; tout le reste de
  `temoin.json` vient du seul fichier d'analyse.

## D. Incident de contrôle croisé (sans effet sur temoin.json)
`statsmodels.stats.sandwich_covariance.cov_nw_groupsum` ré-étiquette les dates par ordre d'apparition (`pd.factorize`) dès que
`max(date) > 2 × nobs`, ce qui casse l'ordre des dates quand les lignes ne sont pas triées par tour ; et il compte les dates par
position si on lui passe des dates à trous. `controle_croise.py` lui passe donc `t_tour − t_min` : les 35 champs comparés
(c, écarts-types à 0/4/8/12 retards, grappes, b, épisodes, S1-S7) coïncident avec `temoin.json` à 2·10⁻¹⁴ près. Ceci confirme
la remarque de 6.4 sur statsmodels.
