# Puissance du juge sur la banque réelle — v1 (2026-11-01 19:58 UTC)

## Lecture fixée avant l'exécution

Écrite : 2026-11-01, 19:55 UTC, avant toute course. Lecture principale : e-BH, m = 17 (témoin vrai hors famille au seuil log(m/α)), juge gelé (taille_plan = 120).

- **P1** : à force 0,5 et N = 144 épisodes d'épreuve, taux de promotion des témoins vrais ≥ 0,8 (réplique la couche 1 bis v2 : force 0,5 promue à 144 épisodes d'épreuve, plan de 120, m = 17).
- **P2** : à force ≤ 0,2 et N ≤ 180, taux de promotion des témoins vrais < 0,5 dans chaque cellule.
- **P3** : taux de promotion des témoins faux ≤ 0,05 dans chaque cellule, pour les deux sortes de témoins faux (bruit, même forme permutée) et les trois lectures (par fiche, e-BH m = 17, e-BH m = m₀), juge gelé ; la borne haute de Clopper-Pearson est rapportée, non décisive.
- **L4** : lue, sans seuil : gain de puissance de N = 120 à N = 600, juge gelé (plan de 120) contre la variante taille_plan = N.

## Ce qu'on mesure

Juge : réglages de `demo_couche1_proposeur_v7.py` (juge v1 sans urne, nul informé, nul d'archive — sans effet sur un témoin —, règle e-BH, α = 0,05, taille_plan = 120). Seuils en log W : par fiche 3,00 ; e-BH m = 17 : 5,83 ; e-BH m = 83 : 7,41. Banque : structure de `banque-t05-v2.json` (120 épisodes, 60 tâches) ; N/2 tâches d'épreuve, N/4 de calibrage ; tirage par tâche, sans remise si 3N/4 ≤ 60, avec remise au-delà. Répétitions par cellule : 500 ; durée 920,7 s sur 2 processus (2 cœurs).

## Puissance — lecture principale (e-BH, m = 17), juge gelé

Taux de promotion des témoins vrais [intervalle exact à 95 %] ; N = épisodes d'épreuve ; plan = min(N, 120).

| force | N = 60 | N = 120 (remise) | N = 144 (remise) | N = 180 (remise) | N = 288 (remise) | N = 600 (remise) |
|---|---|---|---|---|---|---|
| 0,1 | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] |
| 0,2 | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] | 0,01 [0,00 ; 0,03] | 0,02 [0,01 ; 0,03] | 0,05 [0,04 ; 0,08] | 0,19 [0,15 ; 0,22] |
| 0,3 | 0,00 [0,00 ; 0,01] | 0,11 [0,08 ; 0,14] | 0,15 [0,12 ; 0,18] | 0,24 [0,21 ; 0,28] | 0,39 [0,34 ; 0,43] | 0,54 [0,50 ; 0,59] |
| 0,5 | 0,16 [0,13 ; 0,20] | 0,65 [0,60 ; 0,69] | 0,71 [0,66 ; 0,75] | 0,73 [0,69 ; 0,77] | 0,73 [0,69 ; 0,77] | 0,69 [0,65 ; 0,73] |
| 0,8 | 0,69 [0,65 ; 0,73] | 0,95 [0,92 ; 0,97] | 0,95 [0,92 ; 0,97] | 0,95 [0,93 ; 0,97] | 0,87 [0,83 ; 0,89] | 0,81 [0,77 ; 0,84] |

### Autre lecture : par fiche (log W ≥ log(1/α)), juge gelé

| force | N = 60 | N = 120 | N = 144 | N = 180 | N = 288 | N = 600 |
|---|---|---|---|---|---|---|
| 0,1 | 0,00 | 0,00 | 0,00 | 0,00 | 0,01 | 0,05 |
| 0,2 | 0,01 | 0,14 | 0,20 | 0,22 | 0,27 | 0,48 |
| 0,3 | 0,12 | 0,42 | 0,53 | 0,59 | 0,64 | 0,68 |
| 0,5 | 0,58 | 0,85 | 0,90 | 0,90 | 0,86 | 0,77 |
| 0,8 | 0,90 | 0,98 | 0,99 | 0,98 | 0,94 | 0,84 |

### Autre lecture : e-BH, m = 83, juge gelé

| force | N = 60 | N = 120 | N = 144 | N = 180 | N = 288 | N = 600 |
|---|---|---|---|---|---|---|
| 0,1 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 | 0,00 |
| 0,2 | 0,00 | 0,00 | 0,00 | 0,00 | 0,02 | 0,08 |
| 0,3 | 0,00 | 0,03 | 0,05 | 0,11 | 0,24 | 0,42 |
| 0,5 | 0,06 | 0,45 | 0,57 | 0,64 | 0,66 | 0,66 |
| 0,8 | 0,51 | 0,89 | 0,91 | 0,92 | 0,83 | 0,78 |

### Richesse des témoins vrais : log W maximal, médiane [décile 1 ; décile 9], juge gelé

| force | N = 60 | N = 120 | N = 144 | N = 180 | N = 288 | N = 600 |
|---|---|---|---|---|---|---|
| 0,1 | 0,1 [-0,5 ; 0,7] | 0,3 [-0,5 ; 1,2] | 0,3 [-0,4 ; 1,3] | 0,4 [-0,3 ; 1,5] | 0,4 [-0,3 ; 1,7] | 0,5 [-0,3 ; 2,6] |
| 0,2 | 0,5 [-0,5 ; 2,0] | 1,2 [-0,2 ; 3,3] | 1,5 [-0,2 ; 3,8] | 1,6 [-0,2 ; 4,1] | 1,6 [-0,1 ; 4,7] | 2,8 [-0,1 ; 6,9] |
| 0,3 | 1,3 [-0,3 ; 3,1] | 2,6 [0,2 ; 6,0] | 3,2 [0,2 ; 6,7] | 3,6 [0,7 ; 7,6] | 4,5 [0,3 ; 9,4] | 6,4 [0,0 ; 13,7] |
| 0,5 | 3,5 [0,8 ; 6,8] | 7,1 [2,5 ; 11,7] | 8,3 [3,0 ; 14,4] | 9,7 [3,0 ; 16,1] | 12,1 [2,1 ; 19,5] | 17,1 [0,2 ; 27,0] |
| 0,8 | 7,6 [3,0 ; 12,0] | 15,4 [7,2 ; 22,6] | 16,8 [7,9 ; 26,2] | 19,2 [8,3 ; 29,9] | 23,6 [4,7 ; 36,4] | 34,9 [0,7 ; 45,6] |

## Variante hors juge gelé : taille_plan = N (lecture principale)

| force | N = 144 | N = 180 | N = 288 | N = 600 |
|---|---|---|---|---|
| 0,1 | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] | 0,00 [0,00 ; 0,01] | 0,01 [0,00 ; 0,02] |
| 0,2 | 0,01 [0,01 ; 0,03] | 0,03 [0,02 ; 0,05] | 0,12 [0,09 ; 0,15] | 0,55 [0,51 ; 0,60] |
| 0,3 | 0,16 [0,13 ; 0,19] | 0,31 [0,27 ; 0,35] | 0,61 [0,57 ; 0,65] | 0,94 [0,91 ; 0,96] |
| 0,5 | 0,73 [0,69 ; 0,77] | 0,84 [0,80 ; 0,87] | 0,96 [0,94 ; 0,98] | 1,00 [0,99 ; 1,00] |
| 0,8 | 0,97 [0,95 ; 0,98] | 0,99 [0,97 ; 1,00] | 1,00 [0,99 ; 1,00] | 1,00 [0,99 ; 1,00] |

## Témoins faux (juge gelé)

Promus sur jugés (bruit + même forme permutée), par lecture ; borne haute exacte à 95 % de la cellule.

| force | N | par fiche (log W ≥ log(1/α)) | e-BH, m = 17 (principale) | e-BH, m = 83 |
|---|---|---|---|---|
| 0,1 | 60 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,1 | 120 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,1 | 144 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,1 | 180 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,1 | 288 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,1 | 600 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,2 | 60 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,2 | 120 | 1/1000 (≤ 0,006) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,2 | 144 | 4/1000 (≤ 0,010) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,2 | 180 | 5/1000 (≤ 0,012) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,2 | 288 | 3/1000 (≤ 0,009) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,2 | 600 | 7/1000 (≤ 0,014) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,3 | 60 | 2/1000 (≤ 0,007) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,3 | 120 | 10/1000 (≤ 0,018) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,3 | 144 | 5/1000 (≤ 0,012) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,3 | 180 | 3/1000 (≤ 0,009) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,3 | 288 | 6/1000 (≤ 0,013) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,3 | 600 | 6/1000 (≤ 0,013) | 1/1000 (≤ 0,006) | 0/1000 (≤ 0,004) |
| 0,5 | 60 | 5/1000 (≤ 0,012) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,5 | 120 | 6/1000 (≤ 0,013) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,5 | 144 | 4/1000 (≤ 0,010) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,5 | 180 | 6/1000 (≤ 0,013) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,5 | 288 | 4/1000 (≤ 0,010) | 1/1000 (≤ 0,006) | 0/1000 (≤ 0,004) |
| 0,5 | 600 | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,8 | 60 | 4/1000 (≤ 0,010) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,8 | 120 | 3/1000 (≤ 0,009) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,8 | 144 | 8/1000 (≤ 0,016) | 1/1000 (≤ 0,006) | 0/1000 (≤ 0,004) |
| 0,8 | 180 | 4/1000 (≤ 0,010) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |
| 0,8 | 288 | 4/1000 (≤ 0,010) | 1/1000 (≤ 0,006) | 0/1000 (≤ 0,004) |
| 0,8 | 600 | 2/1000 (≤ 0,007) | 0/1000 (≤ 0,004) | 0/1000 (≤ 0,004) |

## N minimal pour une puissance de 0,9 (interpolation linéaire entre points de la grille)

| force | juge gelé (lecture principale) | variante taille_plan = N |
|---|---|---|
| 0,1 | non atteint sur la grille (N ≤ 600) | non atteint sur la grille (N ≤ 600) |
| 0,2 | non atteint sur la grille (N ≤ 600) | non atteint sur la grille (N ≤ 600) |
| 0,3 | non atteint sur la grille (N ≤ 600) | ≈ 564 (entre 288 et 600) |
| 0,5 | non atteint sur la grille (N ≤ 600) | ≈ 233 (entre 180 et 288) |
| 0,8 | ≈ 109 (entre 60 et 120) ; retombe plus loin | ≈ 109 (entre 60 et 120) |

## Ce qui a tenu

- **P1** **non tenu** : force 0,5, N = 144 : taux 0,71 [0,66 ; 0,75] (seuil ≥ 0,8).
- **P2** **tenu** : 0,1 × 60 → 0,00, 0,1 × 120 → 0,00, 0,1 × 144 → 0,00, 0,1 × 180 → 0,00, 0,2 × 60 → 0,00, 0,2 × 120 → 0,00, 0,2 × 144 → 0,01, 0,2 × 180 → 0,02 (seuil < 0,5).
- **P3** **tenu** : taux de faux le plus haut 0,018 (force 0,3, N = 120, par fiche (log W ≥ log(1/α)), faux_meme_forme) ; plus haute borne exacte à 95 % (par sorte de témoin faux, 500 jugés par cellule) : 0,034 ; cellules au-dessus du seuil : 0. Variante (lue) : 0 cellule(s) au-dessus du seuil.
- **L4** (lue) : de N = 120 à N = 600, force 0,1 : 0,00 → 0,00 (gelé), 0,01 (taille_plan = N) ; force 0,2 : 0,00 → 0,19 (gelé), 0,55 (taille_plan = N) ; force 0,3 : 0,11 → 0,54 (gelé), 0,94 (taille_plan = N) ; force 0,5 : 0,65 → 0,69 (gelé), 1,00 (taille_plan = N) ; force 0,8 : 0,95 → 0,81 (gelé), 1,00 (taille_plan = N).

## Réserves

- « Force » = coefficient a de `planter` (v3) : logit ±a·z_i sur les issues 0 et 2 d'un moniteur à 3 issues (issue 1 à 0), signe inversé selon le signe d'un autre trait z_j ; z centrés réduits. C'est une loi **non linéaire** que le nul informé (softmax linéaire ajustée sur le calibrage) ne capture pas ; un effet linéaire de même taille serait en partie absorbé par le nul informé : la courbe est une borne haute pour un tel effet.
- Le témoin vrai engage **la loi exacte du monde** (témoin oracle) : la puissance mesurée est celle d'une fiche parfaitement spécifiée ; une fiche réelle (forme, traits, coefficients approchés) en a moins.
- Les moniteurs plantés portent une issue sur **toutes** les instances ; les moniteurs réels de la banque v2 n'en portent que sur une partie (de 53 à 109 des 120 épisodes) et ont 2 ou 3 issues à coupes déséquilibrées : N épisodes réels donnent moins d'instances jugées par moniteur que N ici.
- La banque réelle n'a que 80 épisodes d'épreuve (60 tâches au total) : toutes les cellules N où 3N/4 tâches dépassent 60 sont tirées **avec remise** (mêmes traits répétés, issues plantées indépendantes). Avec un plan plafonné à 120, le sélecteur par divergence prend les instances les plus extrêmes : au-delà de N = 120, il choisit des copies des mêmes épisodes réels extrêmes ; de vrais épisodes neufs auraient des extrêmes plus extrêmes.
- Juge gelé : taille_plan = 120 ; au-delà, N n'agit que sur le choix des 120 instances, pas sur leur nombre (la variante taille_plan = N dit ce que donnerait un plan qui grandit).
- Le seuil effectif d'un témoin vrai sous e-BH est log(m/α), pas log(1/α) ≈ 3,00 : 5,83 à m = 17, 7,41 à m = 83 ; la puissance dépend donc de la taille de la génération, que ce banc ne tire pas (deux valeurs lues).
- Famille e-BH reconstituée : un témoin vrai (hors famille) et deux témoins faux, les m − 2 autres fiches à e = 0. C'est exact tant que les fiches réelles ont log W < log(1/α) (aucune promue dans la démo) ; des fiches réelles fortes abaisseraient le seuil des faux (k* plus grand).
- Les 5 forces d'une répétition partagent la même banque (mêmes traits, issues indépendantes par moniteur) : les cellules d'une même ligne N sont corrélées entre forces, pas entre répétitions.
- Le plan est trié par divergence ; les ex aequo (le trait « actions_valides » est un compte entier) sont départagés par le mélange du réservoir, dont la graine est l'empreinte de la fiche : renommer un témoin peut changer sa richesse maximale. Vérifié hors banc sur la couche 1 bis v2 : le chemin du témoin de ce script redonne exactement les log W du journal quand la fiche porte les noms du pôle, et s'en écarte un peu sous un autre nom.
- Banc exploratoire, sans préenregistrement scellé ni contre-lecture : rien d'opposable ; la lecture fixée en tête est datée dans le script, pas scellée avant la course.

Fichiers : `puissance-juge-banque-v1.json` (chiffres), ce Markdown (rendu du JSON). Script : `demonstrations/puissance_juge_banque_v1.py` (sha256 692d4134e7b8…).
