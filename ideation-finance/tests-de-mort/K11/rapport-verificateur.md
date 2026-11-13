# K11 — Rapport du vérificateur

Fichiers lus : `preenregistrement.md` et `K11_analyse.csv`, rien d'autre (aucun code, json, log ni rapport de
l'expérimentateur ouvert). Code : `verification.py` (calendrier C, rendement 31 CFR 356 de 5.2, contrôles 1 à 11, moyennes
et ET groupées par mois selon la formule de la section 6, alertes). Sortie : `verification.json`. Pas de verdict ici.

## Nombres recalculés

Les 12 rendements de chaque ligne de P, recalculés à partir des prix : écart maximal au fichier 7,8·10⁻¹¹ pb ; V recalculé
contre `v_pb` du fichier : 1,6·10⁻¹⁰ pb. P = 302 lignes ; `n_apres` = 113 (39 mois), `n_avant_1030` = 184 (96 mois),
`n_temoins_figes` = 7. μ_après = −0,011 pb (ET 0,063 ; IC à 90 % −0,115 à 0,093) ; sans 2023 −0,052, sans 30 ans −0,040.
Avant 10/30 : −0,026 (ET 0,080) ; après 10/30 : 0,041 (ET 0,072) ; baisse −0,067 (ET 0,107 ; borne basse −0,244).
`alerte_robustesse` = 0, `alerte_instrument` = 1, `marge_zone_grise` = −0,407. `schema_ok` = 0 (voir plus bas).

## Lectures des points ambigus

1. **Portée du contrôle 5.** Il s'applique aux « lignes non écartées par les métadonnées », donc aussi aux lignes
   `prix_manquant` et `prix_fige`. Lecture littérale retenue : oui, toutes ces lignes. (Voir violation ci-dessous.)
2. **Partie D1 du contrôle 5** (refaire les étapes 1 à 3 de 4.4 sur D1 téléchargé) : non exécutée, puisque la consigne limite
   la vérification au fichier d'analyse. Seule la partie lisible dans le fichier a été contrôlée : CUSIP distincts, différents de
   A et du premier ancien, rangs croissants ≥ 2, échéances décroissantes et antérieures à celle de A, écarts en mois recalculés
   et dans [1 ; 18]. Cohérence locale des remplacements : rangs (2,3,5) ou (2,3,6) seulement sur les 6 lignes de P où
   s = 1 ou 2, et rang (3,4,5) sur une ligne où s = 1 ; témoins à 15 ou 18 mois seulement dans ces cas (et pour le 30 ans du
   2010-01-14).
3. **Coupons du contrôle 7** : pris sur A et les trois témoins (colonnes 13, 30-32). Le coupon du premier ancien est aussi
   dans [0 ; 15] : aucune différence.
4. **Contrôle 8** : sur les rendements du fichier (identiques aux miens à 10⁻¹⁰ pb près) ; aucune différence.
5. **`ecart_max_rdt_pb`** : sur les 12 rendements de A et des témoins (colonnes 56-67), sans le premier ancien.
6. **Clé `descriptif`** : la section 6 la place dans `verification.json`, mais la consigne demande un objet plat limité à
   `champs_verification`. Le descriptif est donc donné ici, pas dans le json.
7. **Calendrier** : bornes 7 à 11 inclusives ; fériés du samedi reportés au vendredi, y compris le 1er janvier d'une année
   suivante. Le contrôle 4 passe sur les 324 lignes.

## Violations de schéma

- **Contrôle 5, échoue sur 8 lignes** : 912828UN8_2013-04-10, 912828WE6_2013-12-11, 912828P46_2016-04-13,
  9128282R0_2017-10-11, 9128283F5_2017-12-11, 9128286T2_2019-07-10, 912810TS7_2023-06-21, 91282CHT1_2023-09-12. Toutes
  sont `prix_manquant`, `complet` = 0, `dans_p` = 0 : **elles n'entrent dans aucune statistique**. Elles ont 0, 1 ou 2 témoins
  (les autres colonnes de témoin sont vides) parce que 3 à 5 candidats ont été sautés comme figés et que la liste à 18 mois
  s'est épuisée. Par définition, `prix_manquant` couvre « moins de trois témoins valides après remplacements ». Nature : **des
  lignes correctes que le libellé du contrôle n'a pas prévues**. Ce n'est ni une erreur de données ni une anticipation.
  Restreint aux lignes `dans_p` = 1, le contrôle 5 (partie lisible dans le fichier) passe. La lecture littérale donne quand
  même `schema_ok` = 0.
- Contrôles 1, 2, 3, 4, 6, 7, 8, 9, 10 et 11 : passent. Le tri (date puis échéance) est conforme.
- **Témoins adjugés dans la fenêtre / titre courant / premier ancien** : aucun témoin n'est égal à A ni au premier ancien, et
  aucun n'apparaît dans le fichier comme titre adjugé dans [J−5 ; J+5]. Les premières adjudications (reopening = No) ne sont
  pas dans le fichier : cette partie repose sur la construction. Un titre émis dans la fenêtre serait plus long que A et
  prendrait le rang 0, or le rang 0 est toujours A.

## Ce qui est peu plausible ou à signaler

- **La dispersion de V est bien plus faible que prévu** : écart-type 0,78 pb après 2021 et 0,94 pb avant 10/30, contre 2,0 à
  4,5 pb dans les hypothèses de la section 7. Les ET groupées (0,06 à 0,08) sont donc 3 à 5 fois plus petites que le cas
  central. Le test est beaucoup plus précis que planifié.
- **Tous les prix sont des multiples exacts de 1/32**, de 2010 à 2026. Un prix « figé » (identique à 5 séances d'écart) peut
  donc être un vrai prix arrondi au même 1/32 et non une évaluation gelée. Cela touche 7 témoins de P, 4 lignes `prix_fige`
  sur A et environ 31 candidats sautés dans les 8 lignes `prix_manquant`. La 2019-07-10 n'a aucun témoin valide (5 figés).
- Valeur extrême : V = −9,15 pb au 10 ans du 2020-03-11 (crise de mars 2020), qui pèse sur 2020. Ensuite −4,04
  (912810TK4_2022-09-20) et +3,03 (912810TL2_2022-12-13).
- Forme : la montée moyenne est positive (avant 0,12 pb, ET 0,09 ; après 0,11, ET 0,05) mais la « détente » est négative et de
  même taille (avant −0,15, après −0,12). L'écart E continue de monter après J : c'est une dérive monotone (le titre courant
  perd sa cherté), qui s'annule dans V, et non une forme en V.

## La mesure voit-elle une pression en 2010-2021 ?

**Non, ou très peu.** Sur les 10 et 30 ans d'avant 2022, V vaut −0,026 pb (ET 0,080) : la borne haute à 90 % (≈ 0,10 pb)
exclut déjà les 1,38 pb de F04 et même 0,5 pb. Médiane +0,025 ; 52 % de V positifs.

| Année | 10 ans | 30 ans | Ensemble 10/30 (ET groupée) |
|---|---|---|---|
| 2010 | −0,34 | −0,32 | −0,33 (0,40) |
| 2011 | −0,09 | 0,11 | 0,01 (0,17) |
| 2012 | 0,25 | −0,09 | 0,08 (0,11) |
| 2013 | −0,81 | −0,20 | −0,46 (0,09) |
| 2014 | 0,36 | −0,04 | 0,16 (0,10) |
| 2015 | 0,27 | −0,08 | 0,10 (0,15) |
| 2016 | 0,26 | 0,09 | 0,17 (0,18) |
| 2017 | 0,07 | 0,06 | 0,07 (0,09) |
| 2018 | 0,35 | −0,04 | 0,14 (0,14) |
| 2019 | 0,43 | 0,00 | 0,20 (0,09) |
| 2020 | −1,27 | −0,03 | −0,61 (0,77) |
| 2021 | 0,23 | 0,01 | 0,12 (0,12) |

- Par échéance, avant 2022 : 10 ans −0,007 (ET 0,137), ou +0,10 (ET 0,09) sans 2020 ; sur 2014-2019, +0,30 (ET 0,09). C'est la
  seule trace positive, et elle est 4 à 5 fois plus faible que la pression de F04. 30 ans : −0,044 (ET 0,042), −0,045 sans
  2020 : rien du tout. 20 ans d'avant 2022 (5 lignes) : −0,03.
- Après 2021, par année : 2022 0,00 ; 2023 0,18 ; 2024 −0,04 ; 2025 −0,18 ; 2026 0,02. Par échéance : 10 ans 0,04 (0,13),
  20 ans −0,12 (0,16), 30 ans 0,05 (0,10). Sans 2023 et sans le 30 ans à la fois : −0,09.
- Pour comparaison (S1, descriptif) : la mesure de la fiche au rendement limite de 13 h vaut 0,87 pb (ET 0,22) avant 10/30 et
  0,56 (ET 0,23) après. S2 : V du premier ancien contre les mêmes témoins, −0,08 (ET 0,08) avant et 0,02 (ET 0,06) après. Il
  ne montre pas non plus de pression qui déborderait sur les voisins.

En clair, l'instrument (titre rouvert contre les 2e à 4e anciens, à la clôture FedInvest) ne voit pas, en 2010-2021, la
pression que la courbe du Trésor montrait (F04 ≈ 1,38 pb). Les deux mesures n'ont pas la même échelle (limite 2 de la
section 9), ou bien les témoins et la clôture absorbent la pression (limites 1 et 4). Le zéro d'après 2021 ne peut donc pas
être lu comme une disparition de marché : c'est l'objet de `alerte_instrument` = 1.
