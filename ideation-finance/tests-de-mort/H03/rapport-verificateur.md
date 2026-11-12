# H03 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `H03_analyse.csv`, rien d'autre. Code : `verification.py` (écrit d'après le texte
de la préinscription), sortie : `verification.json`. Aucun chiffre ni code de l'expérimentateur n'a été vu.

## Contrôles de schéma

Les 11 contrôles de la section 5 ont tous pu être faits sur le fichier seul ; **aucun n'est violé** (`n_violations_schema` = 0).
444 lignes, 111 millésimes de la liste figée, tri respecté, aucun couple (millésime, cible) en double, `t_lecture` = `t_cible` + 2
partout. Les seules valeurs manquantes sont attendues : `projection_precedente` vide pour `W99` (4 lignes), `realise` vide pour
les cibles 2026-Q2 et après (18 lignes). Les contrôles ne peuvent pas vérifier que les valeurs sont bien celles des fichiers
bruts (statuts `A`/`F`, valeurs) : cela demande `donnees/`, que je n'ai pas ouvert.

## Anomalies

1. **Les lettres `S` et `G` semblent inversées (anomalie majeure, non détectée par le schéma).** Indices tirés du fichier seul :
   - `t_premier_F` − `t_millesime` vaut 0 pour tous les `W` et `A`, **+1 pour tous les `S`** et **−1 pour tous les `G`** ; un
     exercice de juin a normalement son premier trimestre projeté en T2, un exercice de septembre en T3 : le motif est celui
     d'un `S` = septembre et d'un `G` = juin.
   - À l'horizon 1, l'erreur absolue moyenne des `S` est 0,05 point (54 % d'erreurs exactement nulles) contre 0,40 à 0,47 pour
     `W`, `G`, `A` : les « projections à 1 trimestre » des `S` sont en fait des estimations du trimestre en cours.
   - Exemple : `S22` projette 9,1 pour 2022-Q3, `G22` (censé être postérieur) projette 6,4 pour 2022-Q4 ; les révisions des `G`
     sont donc « juin moins septembre » (−2,8 à −3,3 en 2022), c'est-à-dire de signe opposé à une vraie révision.
   Conséquence si c'est bien le cas : la moitié des révisions est mal datée ou de signe inversé, les horizons des lignes `S`/`G`
   sont décalés d'un trimestre, et l'ensemble d'apprentissage d'une ligne `G` peut contenir une erreur lue dans un millésime
   réellement postérieur (un trimestre d'anticipation). La préinscription signalait cette correspondance comme non vérifiée
   et comptait sur les contrôles 4 et 5 ; le contrôle 5 l'admet (tolérance −2 à +1) et le contrôle 4 ne peut pas jouer (point 2).
   Les chiffres de `verification.json` sont calculés **sur le fichier tel qu'il est**, sans correction.
2. **`mois_titre` est vide sur les 444 lignes.** La préinscription dit que le titre de `W21` contient « March 2021 », donc
   `mois_titre` devrait valoir 3 au moins pour `W21`. Ce n'est pas une violation (le contrôle 4 ne porte que sur les cellules
   non vides), mais cela neutralise le contrôle prévu pour détecter l'anomalie 1.
3. Aucune valeur réalisée n'est lue dans un millésime où la cible serait déjà projetée (`t_premier_F` du millésime de lecture
   toujours > cible) ; aucune valeur impossible (projections −0,3 à 9,2 ; réalisé −0,4 à 10,0) ; aucun millésime manquant.

## Lecture des points ambigus (lecture littérale retenue)

- Apprentissage A(i) : toutes les lignes complètes de même horizon avec `t_lecture` ≤ `t_millesime`(i), y compris des cibles
  hors 2004-2025 (ex. cibles 1999-2003). La ligne i est exclue d'office (elle l'est déjà par la condition de date).
- g1 : paires de blocs valides d'indices k et k+1 dans la numérotation d'origine ; divisé par K − 1 comme g0.
- Quantile : valeur du tableau (K = 11 → 1,8125).
- S1 : γ_j = (1/n) Σ_{i=j+1..n} ; ordre par `t_millesime` (une ligne par millésime à h = 4) ; p = P(t_{n−1} > DM*).
- S2 par horizon : la pente b_i est celle de la règle principale ; blocs retenus avec ≥ 4 lignes et sommes de carrés > 10⁻¹².
- S3 : révision décalée = `revision` de la ligne (t_millesime − 8, même horizon) ; mêmes seuils (8 points, 16 lignes par bloc).
- Contrôle 6 : « au plus une décimale » vérifié sur l'écriture texte. Contrôle 10 : deux cellules vides sont égales.
  Contrôle 11 : `W99` n'a pas de ligne précédente, traité comme « les deux vides ».
Aucune de ces lectures n'a d'alternative littérale qui changerait les chiffres de façon visible ici (toutes les lignes cibles
2004-2025 sont évaluées, les 11 blocs sont valides et pleins).

## Statistique bloc par bloc (règle principale)

K = 11, 352 lignes évaluées (32 par bloc). R̄ = −0,056, ET = 0,063 (g0 = 0,0385, g1 = 0,0029), IC 90 % [−0,171 ; 0,059].

| Bloc | Cibles | R_k | Q_k | Σe² | b moyen | R_k placebo |
|---|---|---|---|---|---|---|
| 0 | 2004-2005 | +0,127 | 1,040 | 5,5 | −0,40 | −0,114 (20 lignes) |
| 1 | 2006-2007 | +0,304 | 0,914 | 6,9 | −0,42 | +0,009 |
| 2 | 2008-2009 | −0,139 | 1,101 | 52,6 | −0,44 | −0,001 |
| 3 | 2010-2011 | −0,126 | 1,102 | 13,0 | −0,25 | −0,192 |
| 4 | 2012-2013 | −0,146 | 1,029 | 6,8 | −0,09 | +0,290 |
| 5 | 2014-2015 | −0,105 | 1,012 | 17,4 | −0,06 | +0,233 |
| 6 | 2016-2017 | −0,214 | 1,055 | 13,9 | +0,08 | −0,225 |
| 7 | 2018-2019 | −0,254 | 1,062 | 4,5 | +0,11 | +0,350 |
| 8 | 2020-2021 | +0,257 | 0,979 | 45,6 | +0,08 | +0,130 |
| 9 | 2022-2023 | −0,066 | 1,047 | 460,9 | +0,19 | +0,104 |
| 10 | 2024-2025 | −0,251 | 1,398 | 3,7 | +0,24 | +0,254 |

Seuls les blocs 0, 1 et 8 ont un R_k positif ; huit blocs sur onze sont négatifs, de 2008 à 2019 sans interruption. Aucun bloc
ne domine R̄ (blocs à poids égal) ; le bloc 2022-2023 concentre 73 % de Σe² mais pèse 1/11. Par horizon, seul h = 2 est positif
en moyenne (+0,146) ; h = 1 est le plus négatif (−0,164), ce qui est cohérent avec l'anomalie 1 (les lignes `S` à h = 1 sont
des estimations du trimestre courant et les révisions `G` ont un signe inversé).
