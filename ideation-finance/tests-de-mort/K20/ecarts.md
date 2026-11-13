# K20 — écarts à la préinscription (expérimentateur)

## ⚠ En tête : un énoncé de la préinscription est faux sur les données (contrôle de schéma n° 9)

**Ce que dit la préinscription.** Contrôle 9 : « `niveau_avant` et `niveau_avant_q4` […] présents pour `PGDP`, `RGDP` et
`CPI` quand le niveau correspondant l'est », avec la mention « vérifié avant scellement : oui (structure des sources) ».

**Ce que donnent les données, définitions de la section 4.2 appliquées telles quelles.** Pour la ligne `CPI` × `2026-Q1` :
- `niveau_cible` = moyenne de janvier, février et mars 2026 de `CPIAUCSL` : les trois mois sont présents, donc la valeur
  est présente (section 4.2 : « manquante si l'un des trois mois est vide ») ;
- `niveau_avant` = la même moyenne pour 2025T4 : octobre 2025 est vide, donc la valeur est vide ;
- `realise` est donc vide, ce que la préinscription annonce elle-même (« a(t) manque pour […] `CPI` 2026T1 »).

Le contrôle 9, lu littéralement (« le niveau correspondant » de `niveau_avant` = `niveau_cible` ; de `niveau_avant_q4` =
`niveau_q4`), échoue donc sur cette ligne. C'est la seule ligne et le seul contrôle en échec. La « structure des sources »
invoquée avant le scellement ne garantit pas la propriété pour `CPI`, dont les deux niveaux sont calculés séparément sur
deux trimestres de `CPIAUCSL` ; le trou d'octobre 2025 la rompt.

**Ce que j'ai fait.** J'ai exécuté la préinscription telle qu'écrite : `niveau_cible` présent, `niveau_avant` vide, et
`n_violations_schema` = **1** dans `temoin.json`. Je n'ai pas modifié le fichier pour faire passer le contrôle (vider
`niveau_cible` contredirait la définition de la section 4.2).

**Autre lecture, signalée seulement.** Si « le niveau correspondant » désignait le niveau du trimestre précédent lui-même
(ce que `niveau_avant` représente), la ligne ne serait pas en défaut et le compte serait 0 (`construire.py` imprime les
deux comptes). Je ne retiens pas cette lecture pour le témoin. Aucune autre statistique n'en dépend : la ligne
`CPI 2026-Q1` n'est ni `complete` ni `principal`, si bien que c, ses écarts-types et toutes les analyses secondaires sont
identiques sous les deux lectures.

## Autres écarts et précisions, du plus au moins important

1. **Égalités exactes au quantile Q_v (fragilité, pas un écart).** Pour `PGDP` (223 lignes), `UNEMP` (214) et `CPI` (175),
   (n_v − 1) × 2/3 est entier : `numpy.quantile(…, 2/3)` tombe exactement sur une valeur observée de |surprise|
   (`PGDP 2026-Q2`, `UNEMP 2018-Q1`, `CPI 1987-Q1`). La règle stricte « |s| > Q_v » leur donne L = 0, comme écrit. Avec
   « ≥ », `n_grands` passerait de 334 à 337. Un vérificateur qui calcule Q_v autrement que par la méthode linéaire de numpy,
   ou dont l'arithmétique place Q_v un ulp plus bas, obtiendrait L = 1 sur ces lignes. J'applique la règle écrite ; je n'ai
   pas calculé c sous la variante « ≥ ».
2. **Script de téléchargement séparé.** La section 4 demande le journal des téléchargements dans `construire_journal.json`.
   Il y est, mais il est écrit par `telecharger.py`, pas par `construire.py` : la consigne de l'orchestrateur veut que
   `construire.py` reconstruise le fichier d'analyse à partir de `donnees/` seulement. Le journal contient en plus le numéro
   d'essai et la taille en octets. Le même contenu est repris dans `donnees/PROVENANCE.md`.
3. **Fichier téléchargé en plus : FRED `USRECQP`.** Il n'entre pas dans le fichier d'analyse ; il sert seulement à
   vérifier les fenêtres E1-E7. Résultat : les fenêtres de la section 6 sont exactement « pic NBER à creux NBER + 4
   trimestres » (le creux étant le trimestre qui suit le dernier 1 de `USRECQP`), E7 étant prolongée à 2023T4 comme écrit.
4. **Précision d'écriture.** Tous les décimaux du fichier sont écrits avec 12 décimales (`%.12f`). Les différences
   (`revision`, `erreur`, `surprise`, …) sont calculées à partir des valeurs déjà arrondies à 12 décimales, et L est calculé
   sur la `surprise` telle qu'écrite, pour que le vérificateur retrouve exactement L à partir du fichier. L'arrondi est
   inférieur à 10⁻¹², très en dessous des tolérances (10⁻⁶ dans les contrôles).
5. **`episode_t_min`** est écrit comme l'entier k (2 pour E2), puisque le témoin ne contient que des nombres.
6. **`n_effectif`** est écrit tel que donné par la formule, sans arrondi (819,78).
7. **Écart-type de Driscoll-Kraay dans les exclusions.** Quand la fenêtre retirée est au bord de l'échantillon (E1, au
   début), la plage des trimestres commence au plus petit `t_cible` restant. Comme un trimestre sans ligne a un score nul,
   cela donne exactement le même Ω que si l'on gardait les trimestres retirés comme trimestres vides.
8. **Contrôle 5 pour les variables FRED.** J'ai lu « `FRED` pour les autres variables » avec la définition de la colonne 12 :
   `FRED` quand `realise` (resp. `realise_q4`) est présent, vide sinon. Aucun échec sous cette lecture.
9. **Contournement openpyxl.** Appliqué, comme préinscrit, à la lecture de tous les classeurs (pas seulement `pQvQd.xlsx` et
   `routputQvQd.xlsx`). Sans effet sur les valeurs lues. openpyxl émet aussi des avertissements sur les en-têtes et pieds
   de page des classeurs de l'enquête ; ils sont sans effet sur les cellules.
10. **Contrôle de l'implémentation, pas un écart.** Sur l'échantillon S4 (aucun trimestre vide), mon écart-type de
    Driscoll-Kraay à 4 retards coïncide avec `statsmodels` `hac-groupsum` sans correction (0,0833461 des deux côtés). Le
    verdict n'utilise pas `statsmodels`, comme demandé.
11. **Règle d'aveuglement.** Je n'ai ouvert aucun fichier d'un autre dossier de `tests-de-mort/` en dehors de
    `protocole.md` (je n'ai pas non plus ouvert `verdict.py`).
