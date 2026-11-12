# J02 — Rapport du vérificateur

Le vérificateur n'a lu que `preenregistrement.md` et `J02_analyse.csv`. Il n'a ouvert aucun autre fichier de `J02` ni d'un
autre test (ni scripts, ni `temoin.json`, ni journaux, ni données brutes). Code : `verification.py` (écrit à partir du
texte de la préinscription) ; sortie : `verification.json`. Aucun verdict n'est écrit ici.

## Contrôles de schéma

Les 11 contrôles de la section 5 ont été exécutés sur le fichier : **aucune violation** (`n_violations_schema` = 0).
Tous se font à partir du seul fichier d'analyse ; aucun n'a dû être omis. Ce que le fichier ne permet pas de vérifier :
que les valeurs recopiées (projections, statuts, titres, indices) sont bien celles des fichiers bruts MPD et Eurostat.

Contrôles complémentaires (hors des 11, non comptés) : tous passés.
- `realise` écrit avec 12 décimales, `revision` avec 10, `erreur` avec 12 (minimum demandé : 8, 6, 6).
- Le millésime h2 de la cible t est toujours le millésime h3 de la cible t + 1 ; les deux exercices d'une ligne sont
  consécutifs (numéros t − 2 et t − 3).

## Cohérence des millésimes

Cohérente sur les 216 couples (ligne, millésime) : la lettre correspond au mois du titre (`W` = 3, `G` = 6, `S` = 9,
`A` = 12) et l'année du titre à celle du code ; le numéro tiré du code vaut `t_cible` − 2 (resp. − 3) ; le premier
trimestre `F` est le trimestre de l'exercice ; chaque projection retenue a le statut `F` et est faite 2 (resp. 3)
trimestres avant la cible ; la révision est prise entre deux exercices consécutifs pour la même cible et le même
horizon. Les indices « un an avant » recopient exactement les indices de la ligne t − 4 (contrôle 11).

## Lecture des points ambigus

1. **Couples de Newey-West dans un sous-échantillon (S3).** L'étape 5 forme les couples par écart de `t_cible`. Retirer
   2021-2023 crée un trou de 12 trimestres : en lecture littérale (écart de `t_cible`), aucun couple ne franchit le trou ;
   en lecture « série mise bout à bout » (écart de position, comme `statsmodels`), 2020 et 2024 deviennent voisins.
   `et_beta_z_hors_2021_2023_nw4` = 0,065409 (littérale, retenue) contre 0,064628 (positions). Écart 0,0008, sous la
   tolérance de 0,005. Sur l'échantillon complet et sur S1 (sans trou), les deux lectures coïncident ; l'écart-type
   complet est identique à celui de `statsmodels` HAC sans correction (0,195502).
2. **« Au plus une décimale »** (contrôle 8) : vérifié à la fois sur le texte écrit et sur la valeur (multiple de 0,1).
3. **Contrôle 7** : appliqué seulement quand la projection est présente (texte littéral) ; complété par la vérification
   que le trimestre de l'exercice est antérieur à la cible.
4. **Variables r et e** : prises dans les colonnes `revision` et `erreur` du fichier (section 6), non recalculées ;
   l'écart avec la différence recalculée est de l'ordre de 10⁻¹⁶.
5. **Bootstrap** : `rng.integers(0, n − 7, size = k)` une fois par tirage, k = 14, blocs tronqués à 108 lignes ; un tirage
   dégénéré serait sauté en consommant le générateur — il n'y en a eu aucun sur 9 999.
6. **Années de la garde** : Y = 1999 retire la seule cible de 1999 et les quatre de 2000 ; Y = 2025 retire 2025 et 2026.

## Ce qui ressort / points à signaler

- **Dépendance à 2021-2022.** La pente complète vaut 0,443. Sans 2021-2022, elle tombe à **0,050** (c'est le minimum de
  la garde, `annee_debut_min` = 2021) ; sans 2022-2023 : 0,187. Toutes les autres paires d'années donnent 0,43 à 0,47.
  Sans 2021-2023 : **0,144** (écart-type NW4 0,065). La garde reste positive, mais de très peu.
- **Pente sans chaque année seule** : 0,436 à 0,454 pour toutes les années, sauf **2022 : 0,084** et **2023 : 0,572**
  (2023, avec des révisions positives et des erreurs négatives, joue contre la pente).
- **Avant 2020** (n = 81) : pente brute 0,192, proche des 0,20 de Granziera et coauteurs, mais avec un écart-type NW4 de
  0,111 contre 0,21 publié ; pente réduite 0,134.
- **Inférence** : l'écart-type NW8 (0,162) est plus petit que NW4 (0,196), ce qui est inhabituel. Le bootstrap par blocs
  donne [0,051 ; 0,592] : borne basse plus proche de 0 et borne haute bien plus basse que l'intervalle de Newey-West
  [0,122 ; 0,765]. La position de 0,40 dans l'intervalle n'en dépend pas, mais la largeur de l'intervalle NW4 est portée par
  quelques trimestres de 2021-2023.
- 11 révisions sur 108 valent exactement 0 (arrondi à 0,1 point, limite 6).
- Rien d'implausible relevé dans les ordres de grandeur (réalisations de −0,4 à 10,0 %, pic en 2022-T4) ; les valeurs
  elles-mêmes n'ont pas pu être confrontées aux sources brutes.
