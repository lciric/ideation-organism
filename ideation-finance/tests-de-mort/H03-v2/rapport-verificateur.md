# H03-v2 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `H03-v2_analyse.csv`, rien d'autre (ni code, ni témoin, ni données brutes, ni le
dossier H03). Code : `verification.py` ; résultats : `verification.json`. Pas de verdict ici.

## Contrôles de schéma

Les 11 contrôles ont été refaits sur le fichier tel quel : **0 violation**. Contrôle n° 4 : 444 lignes avec `mois_titre`
rempli, 0 désaccord avec la lettre (`W`=3, `G`=6, `S`=9, `A`=12). Tri (`t_millesime` puis `horizon`, exigé en section 5 mais
hors des 11 contrôles numérotés) : conforme.

Non vérifiable à partir du fichier seul : que `projection` porte bien le statut `F` et `realise` le statut `A` dans la
source ; que `mois_titre` et `t_premier_F` ont bien été lus dans `TITLE_COMPL` et dans la colonne `OBS_STATUS` ; que le
repli q+3 / q+4 n'a été utilisé que quand q+2 manquait (ici toutes les 426 valeurs réalisées sont lues à q+2) ; l'existence
et les sha256 des 111 fichiers bruts.

## Cohérence des millésimes

- Dans chaque année, l'ordre est `W`, `G`, `S`, `A` ; `t_premier_F` = `t_millesime` pour les 111 millésimes, et il avance
  d'exactement un trimestre d'un millésime au suivant sur toute la liste (aucune exception).
- Le mois du titre concorde avec la lettre sur les 444 lignes.
- Horizon 1 : la cible est `t_millesime` + 1, strictement après le premier trimestre `F` du millésime, sur les 111
  millésimes ; ce sont donc de vraies projections, pas des estimations d'un trimestre déjà observé.
- `millesime_precedent` est toujours l'exercice publié juste avant ; contrôle n° 11 (chaînage des projections) sans écart.
- Valeurs réalisées : sondées à la main sur une trentaine de trimestres, elles correspondent aux ordres de grandeur connus
  de l'IPCH (2009-Q3 −0,4 ; 2014-Q4 0,2 ; 2022-Q4 10,0 ; 2023-Q4 2,7).

Le fichier paraît correctement construit sur ces points.

## Lecture des points ambigus

1. **Ensemble d'apprentissage** : toutes les lignes complètes de même horizon avec `t_lecture` ≤ `t_millesime`(i), y
   compris celles dont la cible est avant 2004 (la borne 8016-8103 ne porte que sur les lignes évaluées). Lecture littérale.
2. **r_i, e_i** : pris dans les colonnes `revision` et `erreur` (arrondies à 0,1), non recalculés.
3. **g1** : somme sur les paires (k, k+1) toutes deux valides, divisée par K − 1 (et non par le nombre de paires).
4. **S1** : p = P(T_{n−1} > DM*), unilatéral, comme écrit (« dépasse ») ; autocovariances γ_j sur i = j+1..n, ordre
   `t_millesime` croissant ; la ligne W25 h4 (cible 2026-Q1) est incluse puisqu'il n'y a pas de borne sur `t_cible`.
5. **S2 par horizon** : bloc retenu si ≥ 4 lignes évaluées d'horizon h et Σc² et Σe² > 10⁻¹² (les deux sommes).
6. **S3** : la ligne de même horizon décalée de 8 trimestres doit seulement avoir une `revision` présente ; l'apprentissage
   utilise la même condition `t_lecture` ≤ `t_millesime` ; même formule d'ET avec correction de voisinage pour `et_r_placebo`.

Aucune de ces lectures n'a d'alternative littérale plausible qui change les chiffres de façon visible ; je n'ai pas
trouvé deux lectures littérales concurrentes.

## Statistique bloc par bloc

352 lignes évaluées (88 par horizon), 11 blocs valides de 32 lignes. g0 = 0,0267 ; g1 = −0,0058 (négatif, donc la
correction de voisinage n'élargit rien).

| Bloc | Cibles | b > 0 (sur 32) | R_k | Q_k | Σ e² | R_k placebo |
|---|---|---|---|---|---|---|
| 0 | 2004-2005 | 9 | −0,224 | 1,219 | 5,3 | +0,055 (20 lignes) |
| 1 | 2006-2007 | 1 | +0,110 | 1,021 | 6,6 | −0,051 |
| 2 | 2008-2009 | 3 | +0,027 | 1,015 | 53,7 | +0,125 |
| 3 | 2010-2011 | 21 | −0,062 | 1,114 | 12,7 | −0,278 |
| 4 | 2012-2013 | 24 | +0,003 | 1,040 | 7,1 | +0,304 |
| 5 | 2014-2015 | 24 | +0,229 | 0,961 | 18,0 | +0,196 |
| 6 | 2016-2017 | 24 | −0,041 | 1,063 | 13,5 | −0,238 |
| 7 | 2018-2019 | 24 | −0,130 | 1,118 | 4,6 | +0,203 |
| 8 | 2020-2021 | 24 | +0,196 | 0,971 | 44,4 | −0,055 |
| 9 | 2022-2023 | 25 | +0,246 | 0,945 | 461,8 | +0,244 |
| 10 | 2024-2025 | 32 | −0,182 | 1,812 | 3,9 | +0,317 |

R̄ = 0,0156, ET = 0,0493, IC90 = [−0,074 ; 0,105]. Les seuls blocs nettement positifs sont 5 (2014-2015), 8 et 9 (2020-2023) ;
hors blocs 8-9, la moyenne est −0,030. Le bloc 10 est le plus défavorable en Q_k (1,81) : la pente apprise sur l'épisode
2021-2022 surcorrige des erreurs devenues petites.

## Remarques

- Pentes : `part_b_positif` = 0,60, mais très peu de pentes positives avant 2010 (blocs 0-2).
- S1 : 21 lignes ; les corrections à 4 trimestres sont presque nulles (|c| ≤ 0,51, la plupart < 0,1), d'où un rapport ≈ 1,01.
- Horizon 4 : `r_moyen_h4` = −0,087, alors que les horizons 1-3 sont positifs (0,11 à 0,15).
- Millésimes 1999-2000 : présents avec détail trimestriel et statut `F` ; la BCE ne publiait pas encore ses projections à
  l'époque (limite 4 de la préinscription), sans effet sur les blocs évalués autrement que par l'apprentissage.
- Millésimes 2026 (`W26`, `G26`, `S26`) : projections de 2,2 à 3,6 % pour 2026-2027, nettement au-dessus du réalisé 2026-Q1
  (2,0). Je ne peux pas les vérifier ; elles n'entrent dans aucune ligne évaluée (pas de valeur réalisée), seulement dans
  les contrôles.
