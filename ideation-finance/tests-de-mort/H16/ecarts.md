# H16 — écarts à la préinscription

Rédigé par l'expérimentateur le 2026-11-12. La préinscription (`preenregistrement.md`, sha256
`6862049133ba2826e17247ed7bdf04b100f2012a08bc5696d2a044898277c38c`) n'a pas été modifiée.

**Aucun écart ne touche les données, l'échantillon, la cible, les prédicteurs, la statistique ou les seuils.** Les sept
points ci-dessous sont des lectures d'un passage ambigu, des choix de présentation ou des ajouts. Pour chacun, les neuf
champs de `temoin.json` sont **identiques** sous l'une et l'autre lecture (vérifié ou évident par construction, comme
indiqué).

| n° | Point de la préinscription | Ce qui a été fait | Raison | Effet sur les neuf champs |
|---|---|---|---|---|
| E1 | § 5 : « nombres écrits avec au moins huit chiffres significatifs ». Ambigu : précision minimale, ou nombre de chiffres réellement écrits (un `0.5` n'en montre qu'un). | Lecture la plus littérale : tous les réels de `analyse_H16.csv` sont écrits en notation scientifique à 17 chiffres significatifs (`-2.5000000000003902e-01`), donc toujours plus de huit chiffres écrits, et la valeur binaire est restituée exactement à la relecture. `rang` reste un entier. | Satisfaire les deux lectures à la fois. | Aucun : les valeurs lues sont les mêmes qu'avec une écriture décimale courte. |
| E2 | § 4.3, règles (i) et (ii), contre la description de `date_fin_*` au § 5 (« dernière observation **utilisée** ») : faut-il écrire la date de `v[i]` quand le prédicteur est manquant ? | Lecture littérale de la règle (i) : la date de `v[i]` est écrite dès que `v[i]` existe, même si le prédicteur est manquant. Cela ne se produit que pour `date_fin_eurusd` aux **rangs 1 à 5** (rodage) : l'euro-dollar commence le 1999-01-04, il n'y a pas 60 observations d'historique, `eurusd_60j_pct` est vide et `date_fin_eurusd` est renseignée. | La règle (i) est énoncée sans condition ; le § 5 autorise « vides ou renseignés » pour les rangs 1 à 17. | Aucun : lignes `rodage`, qui ne servent à rien. Le contrôle 8 réussit dans les deux lectures (ces dates précèdent la réunion de 1 jour). |
| E3 | § 4.3, règle (ii) : « si `i−60` n'existe pas, le prédicteur est manquant », alors que `act_eu_60j_pct` n'utilise que les rendements `i−59 … i`. | Règle appliquée littéralement aux quatre séries, actions comprises (il faut 61 observations valides jusqu'à `i`). | Lecture littérale. | Aucun : la série d'actions commence en 1990 ; aucune réunion n'est concernée sous l'une ou l'autre lecture. |
| E4 | § 6.3, graphique unique : « **en encart**, `p_t − m_t` contre `y_t − m_t` ». | Le nuage de points est un panneau placé **à droite** du graphique principal, dans la même image `figure.png`, et non un encart superposé aux courbes. Le contenu fixé est entier : sommes cumulées de `e0² − e1²` et de `f_t` selon la date, trois sous-périodes en fond, nuage `p − m` contre `y − m`. | Un encart superposé aurait masqué une partie des courbes cumulées, qui occupent toute la hauteur du cadre. | Aucun (présentation). |
| E5 | § 6.2-6.3 : la liste des nombres à rapporter est fermée. | Nombres descriptifs **ajoutés**, signalés « hors préinscription » dans le compte rendu : la plus grande valeur de `cw_t` quand on retire une réunion (la préinscription ne demande que la plus petite) ; le tableau des huit réunions aux plus grands `|f_t|` ; la corrélation entre `p − m` et `y − m` inscrite sur la figure ; quelques statistiques de dispersion de la cible. | La préinscription ne retient que le retrait qui abaisse le plus la statistique ; taire que le retrait d'une autre réunion la relève aurait donné une image partielle de la sensibilité à une réunion. Ces nombres n'entrent dans aucun champ ni dans aucune règle. | Aucun. |
| E6 | § 4.3-5 : précisions que la préinscription ne fixe pas. | (a) Tirage des trois réunions citées dans le compte rendu : `numpy.random.default_rng(16).choice` sans remise parmi les 298 lignes utilisables, graine (le numéro de la fiche) fixée avant d'exécuter. (b) Codes de valeur manquante reconnus un peu plus largement que ceux nommés : cellule vide, `.` ou `NA` pour FRED ; `NA` ou vide pour `SVENY02` ; toute valeur ≤ −99 dans `Mkt-RF` ou `RF` pour Ken French. (c) Formulation de la lecture S1 pour `cible_prec_norm` : la préinscription dit « même règle, comparée au signe négatif de Worms » ; j'ai écrit « signe négatif (celui de Worms) » si `b + 1,645 × se < 0`, « signe positif (opposé à Worms) » si `b − 1,645 × se > 0`, « signe non établi » sinon. | Il fallait une règle exécutable. | Aucun : (b) aucun code élargi n'apparaît dans les fichiers (FRED n'a que des cellules vides, Ken French aucune valeur manquante) ; (c) le résultat est « signe non établi » quelle que soit la formulation. |
| E7 | Liste des livrables. | Fichiers ajoutés dans `H16/` : `telecharger.py` (téléchargement avec reprises), `donnees/telechargements.json` (journal du téléchargement, pas une donnée), `construire.log`, `analyse.log`, `previsions_H16.csv` (une ligne par réunion d'évaluation : `y`, `m`, `p`, `e0`, `e1`, `d`, `f`), `resultats_analyse.json` (analyses secondaires). | Traçabilité. Le vérificateur n'a pas à les lire ; son recalcul part de `analyse_H16.csv` seul. | Aucun. |

## Points de la préinscription vérifiés sans écart

- Empreinte d'EA-MPD : identique à celle du § 4.1.
- Taux américain à 2 ans : `SVENY02` du fichier de la Réserve fédérale, obtenu au premier essai ; le repli `DGS2` (A14) n'a pas servi.
- Millésime Ken French : « 202609 Bloomberg database », celui lu par le rédacteur.
- Effectifs : 17 `rodage`, 151 `estimation`, 147 `evaluation`, 0 `exclue`, comme attendu.

## Constat qui n'est pas un écart mais contredit une attente de la préinscription

- L'amendement A7 justifie le plancher de 0,25 point de base par les cotations figées de 1999-2001. **Le plancher ne joue à
  aucune réunion** (0 sur les 299 réunions de rang ≥ 17) : le plus petit écart-type des 16 surprises précédentes est de
  0,2802 point de base (réunion du 2019-04-10). Le nombre de réunions où il joue, que la préinscription demande de
  rapporter, est donc zéro.
