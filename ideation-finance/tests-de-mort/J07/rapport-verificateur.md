# J07 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `J07_analyse.csv`, rien d'autre. Code : `verification.py` (écrit d'après le texte de la
préinscription) ; sortie : `verification.json`. Je ne rends pas de verdict.

## Nombres (verification.json)

| champ | valeur |
|---|---|
| schema_ok | 1 |
| n_admissibles | 309 |
| n_previsions | 248 |
| premiere_prevision_aaaammjj | 19970207 |
| cw_stat | 1,871964 |
| r2_hors_echantillon | 0,02156752 |
| reqm_reference_k | 57,922097 |
| reqm_modele_k | 57,294074 |

Contrôle croisé : `statsmodels` (HAC, 4 retards, `use_correction=False`) redonne exactement 1,871964 ; l'identité
f = 2(ŷ1 − ŷ0)(y − ŷ0) tient à 1e-11 près. Taille d'apprentissage : 60 à la première prévision, 307 à la dernière.

## Lecture des points ambigus

- **Ensemble d'apprentissage** : S_i = { j ∈ A : d3_j ≤ d_i }, jour même compris (lecture littérale de la section 6 et de B5).
  231 paires (j, i) ont d3_j = d_i. Variante non littérale, à titre de sensibilité seulement (d3_j < d_i strict) :
  P = 247, première prévision 1997-03-07, CW = 1,72, R² = 0,0185.
- **Première prévision** : la première ligne de A dont |S_i| ≥ 60 ; |S_i| croît avec i, donc E est un suffixe de A.
- **Autocovariances** : divisées par P (pas par P − l), comme écrit ; poids de Bartlett 1 − l/5.
- **Types** : « entier » lu comme un champ sans partie décimale ; tous les champs entiers du fichier le sont. `tendance_12m_k`
  et `pred_ecart_tendance_k` sont écrits avec « .0 » ou « .5 » (décimaux, conformes).
- **Contrôle 6, égalité « exacte »** : comparaison en virgule flottante sans tolérance ; exacte ici puisque T est un multiple
  de 0,5.
- **« Cinq publications les plus influentes »** : non défini dans la préinscription. Je prends les cinq plus grands |f_i|, et
  je retire chacune soit de l'évaluation seule, soit de A entier (apprentissage et évaluation, tout recalculé). Je donne aussi
  le classement par baisse de CW.

## Contrôles de schéma

Les huit contrôles passent sur le fichier tel quel (431 lignes, 18 colonnes dans l'ordre). Contrôles supplémentaires, tous
passés : `date_millesime_precedent` = date de la ligne précédente ; `n_mois_nouveaux` = écart de mois avec la ligne précédente ;
`date_millesime_3e` = première publication du fichier dont le mois est ≥ m + 2 ; `date_info_predicteurs` = `date_publication`
partout ; A1(v) + R1(v+1) + R2(v+2) = A3(v) sur toutes les lignes où c'est calculable (cohérence interne forte des révisions).

Non vérifiables à partir du fichier seul : la valeur de `revision_large` (demande les niveaux de 10 mois par millésime) ; la
conformité de A1, A3, R1, R2, T aux millésimes ALFRED (seule la ligne du 1990-02-02 est fixée par la préinscription) ;
l'exactitude de `date_info_predicteurs`, qui est une déclaration ; les décomptes attendus de la section 4 (438, 3 corrections).

Filtres : complet = 0 : 0 ; publication double : 1 ; `revision_large` = 1 : 119 lignes ; `extreme` = 1 : 6 lignes
(2020-04-03 à 2020-09-04). 119 révisions larges, c'est beaucoup (28 % des lignes) mais cohérent avec la limite 3 (« environ un
quart ») et avec n = 309 du parent.

## Information future

Aucune trouvée. Chaque S_i ne contient que des lignes antérieures à i dont la troisième estimation est datée au plus tard du
jour de i (vérifié par assertion) ; toute `date_millesime_3e` correspond à une publication réelle du fichier de mois ≥ m + 2,
donc les dates d3 ne sont pas avancées ; tous les prédicteurs sont datés du jour de publication. Reste la sélection par
`revision_large`/`extreme` (limite 3, déclarée).

## Plausibilité

Moyenne de N = −8,7 milliers, écart-type 58,5. Coefficients de la dernière prévision : constante −6,4, x1 +0,035, x2 −0,20
(x2 de signe négatif comme attendu). Dans l'échantillon (S3) : x2 = −0,202 (erreur type NW 0,088), x1 = 0,034 (0,028), R² = 4,3 %.
R² hors échantillon de 2,2 % et CW de 1,87 tombent au centre de la prédiction du rédacteur. Rien d'implausible.

## Fragilité

- **S1** : x1 seul CW = −1,15, R² = −0,009 ; x2 seul CW = 2,12, R² = +0,025. Toute la prévisibilité vient de x2.
- **Par période (prévisions inchangées)** : années 1990 (P = 26) CW = 0,50, R² = +0,008 ; années 2000 (P = 86) CW = −1,47,
  R² = −0,032 ; années 2010 (P = 89) CW = −0,52, R² = −0,022 ; années 2020 (P = 47) CW = 3,72, R² = +0,092. S2 : avant 2008
  CW = −0,75 ; 2008-2019 CW = −1,10 ; à partir de 2020 CW = 3,72. Sans 2020-2025 : CW = −1,28, R² = −0,025. **Le résultat
  repose entièrement sur 2020-2025.**
- **Cinq plus grands |f_i|, chacun retiré à son tour** (évaluation seule / A entier) : 2025-06-06 : 1,75 / 1,75 ;
  2023-07-07 : 1,67 / 1,65 ; 2024-07-05 : 1,74 / 1,73 ; 2021-11-05 : 1,77 / 1,66 ; 2025-04-04 : 1,80 / 1,79. Aucun retrait
  isolé ne fait passer CW sous 1,645 (sur les 248 retraits un à un dans l'évaluation, le minimum est 1,668, pour 2023-07-07),
  mais l'avance est mince : 2023-07-07 retiré de A entier donne 1,649.
- **Retraits cumulés** (évaluation) : 1 → 1,75 ; 2 → 1,52 ; 3 → 1,36 ; 4 → 1,22 ; 5 → 1,01 (R² −0,003). Deux publications
  suffisent à passer sous 1,645, cinq à rendre le R² négatif.
- La règle stricte d3_j < d_i (non littérale) donne CW = 1,72 : au-dessus du seuil, mais avec moins de marge.
