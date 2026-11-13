# K20 — Rapport du vérificateur

J'ai lu seulement `preenregistrement.md` et `K20_analyse.csv`. Je n'ai ouvert aucun autre fichier du dossier ni d'un autre
test, et je n'ai pas listé leur contenu. Mon code est dans `verification.py` (`python3 verification.py --detail` affiche le
détail). Les chiffres sont dans `verification.json`. Je n'écris pas de verdict.

## Contrôles de schéma : 1 contrôle violé sur 12

- **Contrôle 9 (niveaux), 1 ligne : `CPI` 2026-Q1.** `niveau_cible` est présent (328,1137), mais `niveau_avant` est vide.
  Selon la section 4.2, `niveau_avant` est la moyenne des trois mois de 2025T4. Octobre 2025 est vide dans `CPIAUCSL`, donc
  cette moyenne manque, et la ligne est juste. Le texte prévoit d'ailleurs que a(t) manque pour `CPI` 2026T1. C'est donc
  **une ligne correcte que le libellé du contrôle n'a pas prévue**. Ce n'est ni une erreur de données ni une information
  venue du futur. `realise`, `erreur` et `complete` y sont vides ou nuls, et la ligne n'entre dans aucune régression
  (principale, épisodes, S1 à S7). La ligne voisine (`CPI` 2025-Q4) montre le cas symétrique : `niveau_cible` vide et
  `niveau_avant` présent. Celle-là ne viole rien, car le contrôle n'exige la présence de `niveau_avant` que si le niveau
  est présent.
- Lecture littérale : « présents … quand le niveau correspondant l'est ». Le niveau correspondant à `niveau_avant` est
  `niveau_cible`, donc le contrôle est violé, et `n_violations_schema` = 1 dans `verification.json`. Une lecture moins
  littérale (« présent quand la source le fournit ») donnerait 0.
- Les contrôles 1 à 8 et 10 à 12 passent. En particulier :
  - comptes `complete` et `principal` : 1 020 et 1 004 ;
  - lignes principales par épisode, toutes égales aux attentes : 15, 27, 60, 35, 40, 55, 69 ;
  - les millésimes en t + 2 tombent bien sur les cibles prévues ;
  - `grande_nouvelle` est identique au L que j'ai recalculé.

## Points ambigus et lecture retenue

1. **Contrôle 5.** J'ai appliqué « `FRED` pour les autres variables » aux lignes où `realise` (ou `realise_q4`) est
   présent. J'ai aussi vérifié que le millésime est vide quand le réalisé l'est (définition de la colonne 12) : aucun cas
   ne s'écarte.
2. **Échantillon et L.** J'ai pris la colonne `principal` du fichier, identique à ma propre reconstruction. J'ai recalculé
   L à partir de `surprise` et de Q_v (lignes principales, `numpy.quantile`, méthode linéaire).
3. **a et A.** J'ai pris une moyenne simple, avec pour diviseur le nombre de lignes, sur toutes les lignes principales de
   la classe, toutes variables confondues, en centrant chaque variable sur sa moyenne m_{v,ℓ}. Deux autres lectures :
   - moyenne des cinq variances par variable : rapport 3,085 au lieu de 3,064, biais 0,0816 au lieu de 0,0807 ;
   - diviseur n − 5 : écart du même ordre.
   Le plancher reste 0,10 dans tous les cas.
4. **Driscoll-Kraay.**
   - Le calendrier va du plus petit au plus grand `t_cible`, avec un vecteur nul pour chaque trimestre vide. L'échantillon
     principal a 5 trimestres vides à l'intérieur : 1970T1-T3, 1971T1 et 1975T3.
   - Pour les exclusions d'épisode, la borne du calendrier ne change rien, puisque les vecteurs nuls ne contribuent pas.
   - Pour 8 retards, j'ai pris les poids de Bartlett 1 − j/9, prolongement de 1 − j/5 : le texte ne les écrit pas.
   - Contrôle croisé : à 0 retard, mon calcul égale l'écart-type groupé par trimestre de statsmodels sans correction, à
     10⁻¹⁵ près.
5. **`n_trimestres_grands`.** Je l'ai compté sur les lignes principales : 184. Sur toutes les lignes avec L = 1, on
   trouverait 188, et 185 sur les lignes `complete`.
6. **Analyses secondaires.**
   - S3 garde les z et Q_v de l'échantillon principal pour les 16 lignes pandémiques.
   - S6 réduit `revision_med` et `erreur_med` par leurs propres moyennes et écarts-types, sur les lignes principales.
   - S7 remplace L par 1{|z_r| > 1} dans les quatre blocs où L intervient.
7. **`episode_t_min`.** Il vaut 2 (E2), sans égalité.

## Ce qui paraît peu plausible, sans violer le schéma

- **`PGDP` 1969-Q4.** `prev_h3_med` vaut exactement 0, alors que la moyenne vaut 2,618. Cela donne `revision_med` = −3,21
  et z = −5,5 dans S6. C'est cohérent avec des niveaux médians entiers dans les premières enquêtes (amendement A4) : c'est
  probablement un arrondi, pas une erreur. Cette ligne n'entre que dans S6.
- **`PGDP` 1987-Q1.** `prev_h4` (moyenne) vaut 4,81 contre 2,76 pour la médiane, ce qui laisse penser à une réponse
  aberrante dans l'enquête 1986T1, colonne 6 (limite 8). Cette ligne entre dans la régression principale.
- **`PGDP` 1975-Q2.** z de la révision médiane = 6,2 (S6 seulement).
- **Pente de base de `RGDP` négative** (b = −0,11). Les quatre autres variables vont de +0,14 à +0,37.
- **Écart-type de Driscoll-Kraay proche de celui des MCO.** On a 0,0707 contre 0,0639 en MCO, d'où `n_effectif` ≈ 820. La
  section 8 attendait environ 230 au centre. L'écart-type à 8 retards (0,0682) est même plus petit qu'à 4 retards. Si
  l'erreur-type est trop petite (limite 7), cela ne change pas le signe de c.

## Fragilité

- **Estimation principale :**
  - c = −0,030 (é.-t. 0,071), intervalle à 90 % [−0,146 ; +0,086] ;
  - la borne haute est loin de 0,40 ;
  - le rapport de variances (3,06) dépasse largement 1,25.
- **Par épisode retiré :**
  - c va de −0,084 (sans E2) à +0,014 (sans E3) ;
  - t va de −1,52 (sans E2) à +0,15 (sans E3) ;
  - aucun retrait ne rapproche c de 0,40.
- **Par variable (S1) :**

  | Variable | c | é.-t. |
  |---|---|---|
  | `PGDP` | +0,17 | 0,18 |
  | `CPI` | +0,05 | 0,15 |
  | `RGDP` | −0,05 | 0,16 |
  | `UNEMP` | −0,10 | 0,15 |
  | `TBILL` | −0,31 | 0,18 |

  Aucun |t| ne dépasse 1,75. En retirant une variable entière (calcul descriptif à moi, hors champs) :
  - c vaut −0,093 sans `PGDP` et +0,020 sans `TBILL` ;
  - le signe tient donc à `TBILL` d'un côté et à `PGDP` de l'autre ;
  - l'ordre de grandeur, proche de 0, ne change pas.
- **Variantes secondaires :**
  - médianes : c = +0,075 ;
  - avec la pandémie : −0,095 ;
  - depuis 1985 : −0,067 ;
  - avant 2020 : −0,037 ;
  - coupure de la fiche : −0,003.
- **Ce qui fait bouger le résultat.** Le seul point qui change un champ de la règle est la violation de schéma du
  contrôle 9. Elle tient à la lecture littérale d'une ligne correcte, hors de toute régression.
