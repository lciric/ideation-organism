# H13 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `H13_analyse.csv`, rien d'autre. Code : `verification.py` (MCO et HC3 écrits à la
main à partir des formules de la section 6 ; recoupés avec `statsmodels` `OLS(...).fit(cov_type="HC3")`, accord à 1e-12).

## Nombres (verification.json)

| champ | valeur |
|---|---|
| schema_ok | 1 |
| n_publications | 309 |
| beta_pb_par_100k | 2,3155 |
| erreur_type_pb | 0,9448 |
| t_stat | 2,4509 |
| borne_inf_95_pb | 0,4638 |
| borne_sup_95_pb | 4,1672 |
| marge_zone_grise | −0,4909 |
| t_placebo_abs | 0,9977 |

## Points ambigus et lecture retenue

1. **Contrôle 5 quand une date est vide** : lecture littérale, une comparaison avec une date vide échoue (sauf
   `date_millesime_3e`, explicitement conditionnelle). Sans effet : aucune de ces dates n'est vide.
2. **Contrôle 7, « tout taux présent »** : lu comme les cinq colonnes `dgs2_*` et `sveny02_*`. Les deux lectures (DGS2 seul
   ou tous) passent.
3. **Contrôle 9, « 8,1466 à 0,0001 près »** : comparé à la valeur non arrondie du fichier (8,146617 et 8,223438) ; écarts
   de 2e-5 et 4e-5, passe sous les deux lectures (valeur brute ou arrondie à 4 décimales).
4. **Placebo, « mêmes lignes, même X »** : même échantillon P de 309 lignes ; aucune ligne de P n'a `dgs2_avant_veille`
   vide, donc pas d'ambiguïté.
5. **« Les cinq publications les plus influentes »** (demande du vérificateur, pas de la préinscription) : retenu = plus
   grand |DFBETA| sur β (variation exacte de β quand on retire la ligne). Le classement par distance de Cook diffère ; les
   deux sont donnés ci-dessous.

Aucune ambiguïté ne donne deux nombres différents pour les neuf champs.

## Contrôles de schéma

Les neuf contrôles ont pu être exécutés sur le fichier tel quel ; tous passent (431 lignes, 22 colonnes dans l'ordre,
définitions de `extreme`, `complet`, `principal` reproduites exactement, ligne 1990-02-02 conforme, alignement DGS2/SVENY02
partout ≤ 0,75). Non vérifiable depuis le fichier seul : que les valeurs viennent bien d'ALFRED/FRED (D1–D5), la valeur
exacte de `rev_m*`, `tendance_12m_k`, `d_chomage_pt`, et la règle de révision large (étape 5), qui exige les niveaux des
millésimes.

## Contrôles de cohérence supplémentaires (hors schéma)

- Aucune publication dupliquée ; `date_millesime_precedent` = date de la ligne précédente partout ; `n_mois_nouveaux`
  cohérent avec l'écart de `mois_reference` ; `date_millesime_3e` = première publication suivante avec mois ≥ m + 2 sur
  toutes les lignes vérifiables.
- Identité comptable A3 = A1 + `rev_m1_k`(v+1) + `rev_m2_k`(v+2) : 428 lignes testées, 0 écart. Forte cohérence interne
  des colonnes d'emploi.
- `revision_large` : 119 lignes à 1, 3 par an (6 en 1996 et 2020, 5 en 2002 et 2003, 4 en 2010). Les publications
  susceptibles d'être « larges » compatibles avec le fichier tombent en juin jusqu'en 2003, en février depuis 2004, plus
  1990-09, 1996-10, 2003-01, 2010-03, 2020-06 : profil plausible (révisions de référence ; 2003-01 = passage au NAICS).
  Aucune contradiction trouvée. La ligne 2025-12-16 a `revision_large` = 1 avec v3 = 2026-02-11 hors fichier :
  invérifiable, sans effet (déjà exclue comme publication double).
- Exclusions : 1 double (2025-12-16), 6 extrêmes (toutes en 2020, d'avril à septembre, comme annoncé), 2 incomplètes
  (1994-04-01 Vendredi saint ; 2025-12-16 sans chômage). n = 309, dans la fourchette attendue 270–315.
- `sveny02_j` vide 4 fois (1994-04-01, 1994-07-08, 1994-10-07, 1999-04-02) : conforme à « SVENY02 manque quatre jours ».
- Valeurs extrêmes plausibles : y = +36 pb le 2009-06-05 (0,96 → 1,32), +33 pb le 1996-03-08, −28 pb le 1990-05-04.

## Anomalies ou points à vérifier

- **Jours de semaine** : 417 vendredis, 12 jeudis, 2 mardis. Expliqués : jeudis de début juillet (fête du 4), 2013-10-22
  et 2025-11-20 (fermetures de l'État fédéral), 2025-12-16 (publication double). **Non expliqué : 1998-11-05, un jeudi**,
  alors que le vendredi 1998-11-06 n'est pas férié. Si la vraie publication est le 6, la ligne porte sur le mauvais jour
  (limite 9 de la préinscription). Elle est dans P (N = −0,48, y = +4) ; la retirer donne β = 2,324, t = 2,46 : sans effet.
- Écart-type de y sur P = 9,43 pb, au-dessus de la fourchette supposée (6,5–9) ; écart-type de N = 0,585 (supposé 0,5–0,8).
  Pas une erreur, une supposition de la section 7 dépassée.
- Triplets de taux identiques sur plusieurs dates (ex. 0,25/0,27/0,25 en 2011–2012) : périodes de taux plancher, plausible.

## Fragilité

Sans chacune des cinq publications les plus influentes (|DFBETA|) :

| retirée | N | y (pb) | β | t |
|---|---|---|---|---|
| 1990-05-04 | 0,90 | −28 | 2,639 | 2,94 |
| 1996-03-08 | 0,74 | +33 | 2,030 | 2,24 |
| 1990-06-01 | −2,05 | −17 | 2,083 | 2,20 |
| 2008-10-03 | 2,44 | −2 | 2,535 | 2,59 |
| 2003-09-05 | −1,28 | −19 | 2,116 | 2,27 |
| les cinq ensemble | | | 2,127 | 2,47 |

Plus grands Cook (2009-06-05, 1990-05-04, 1996-03-08, 1995-02-03, 2025-08-01) : sans 2009-06-05, β = 2,480, t = 2,66 ;
sans 1995-02-03, 2,224 / 2,36 ; sans 2025-08-01, 2,253 / 2,39. Aucun retrait isolé ne fait passer t sous 2,2.

Par décennie (régression sur la décennie seule | sans la décennie) :

| décennie | n | β seule | t seule | β sans | t sans |
|---|---|---|---|---|---|
| 1990 | 87 | 3,15 | 1,34 | 2,10 | 2,08 |
| 2000 | 86 | 2,86 | 1,26 | 2,38 | 2,23 |
| 2010 | 89 | −0,45 | −0,39 | 2,83 | 2,51 |
| 2020 | 47 | 3,97 | 1,53 | 2,08 | 1,75 |

Lecture : le coefficient est stable au retrait d'un point, mais t ≈ 2,45 n'a qu'une faible marge au-dessus de 1,96.
Aucune décennie n'est significative seule ; la décennie 2010 (taux plancher) a un β proche de zéro et négatif ; sans les
années 2020 (47 publications), t tombe à 1,75. Le résultat repose sur l'ensemble de la période, et en partie sur 2020–2025.
