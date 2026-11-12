# J02 — Préinscription du test de mort : les projections d'inflation de la BCE sous-réagissent-elles aux nouvelles ?

Rédigé le 2026-11-12 par le rédacteur de préinscription de J02. Le rédacteur n'a lancé aucune analyse : aucune erreur, aucune
révision, aucune moyenne, aucune régression et aucune statistique n'a été calculée sur les données. Les seuls calculs faits
sont des calculs de puissance théoriques (loi normale), sans donnée.

**Ce que le rédacteur a lu.** La fiche J02 et les failles des quatre juges ; la note de nouveauté `generation-2/nouveaute/J02.md` ;
`tests-de-mort/protocole.md` et `tests-de-mort/verdict.py` ; dans le dossier `tests-de-mort/H03-v2`, **seulement**
`preenregistrement.md` et `verdict.json`. Rien d'autre de ce dossier (ni fichier d'analyse, ni données, ni scripts, ni
rapports, ni témoin).

**Ce que le rédacteur a vu des données.**
- MPD, une seule série, `MPD.Q.U2.HIC.A.W99.0000` (délai dépassé à 90 s au premier essai, HTTP 200 au deuxième) : les noms
  de colonnes, le nombre de lignes (12), le premier trimestre de statut `F` (1999-Q1), le dernier trimestre (2000-Q4), le
  contenu de `TITLE_COMPL` (« … HICP overall index - Annual growth rate - March 1999 staff macroeconomic projections »).
  **Aucune valeur de `OBS_VALUE` n'a été affichée.**
- Eurostat `prc_hicp_minr`, série mensuelle `M.I15.TOTAL.EA` (HTTP 200 au premier essai) : la ligne d'en-tête, les quatre
  premières lignes (indices de janvier à avril 1996), le nombre de mois (369), le premier et le dernier mois (1996-01,
  2026-09), l'absence de valeur vide et de drapeau ; les libellés des dimensions (mise à jour du 2026-11-04). Aucune valeur
  postérieure à avril 1996 n'a été affichée.
- BCE `ICP`, série `M.U2.N.000000.4.INX` (HTTP 200) : en-tête et couverture seulement (1996-01 à 2025-12, base 2015 = 100,
  statut `A`). Elle n'est pas retenue (section 4).
- Les chiffres publiés de H03-v2, recopiés en section 2.

---

## 1. Question, hypothèse et prédiction chiffrée

**Question.** Quand les services de la BCE et de l'Eurosystème révisent à la hausse leur projection d'inflation pour un
trimestre donné, l'inflation de ce trimestre finit-elle, en moyenne, encore au-dessus de la projection révisée ?

**Définitions** (un trimestre cible q ; les projections sont des glissements annuels de l'IPCH de la zone euro, en %) :
- f₂(q) = projection publiée dans l'exercice du trimestre q − 2 (horizon 2) ;
- f₃(q) = projection publiée dans l'exercice précédent, celui du trimestre q − 3 (horizon 3) ;
- **révision** r(q) = f₂(q) − f₃(q) ;
- **erreur** e(q) = valeur réalisée a(q) − f₂(q).

**Hypothèse falsifiable (sens de l'effet).** Les projections sous-réagissent : une révision positive est suivie, en moyenne,
d'une erreur positive. La pente de l'erreur sur la révision est donc **positive**. Si les projections utilisaient toute
l'information disponible, l'erreur ne serait pas prévisible par la révision, et la pente serait nulle.

**Statistique.** β_z : pente de la régression de l'erreur réduite (centrée, divisée par son écart-type) sur la révision
réduite. Avec une constante, cette pente est exactement le **coefficient de corrélation de Pearson** entre révision et
erreur. Elle est sans unité, entre −1 et 1.

**Prédiction chiffrée de la fiche, reprise telle quelle.** β_z = +0,40, plage plausible +0,30 à +0,55.

**Où se place cette prédiction.**
- **Granziera, Jalasjoki et Paloviita (2021)** ont fait la même régression, une observation par trimestre cible, écarts-types
  de Newey-West, sur les cibles 1999T4-2019T4. À h = 2 : pente **0,20 (écart-type 0,21)**, en points par point de révision,
  non réduite, positive mais non significative. Pour passer à une pente réduite, il faut multiplier par le rapport
  écart-type des révisions / écart-type des erreurs, qui n'est pas publié. **Hypothèse d'ordre de grandeur, non mesurée** :
  si ce rapport est entre 1/3 et 2/3, leur 0,20 vaut 0,07 à 0,13 en pente réduite, et la borne haute de leur intervalle à
  90 % vaut 0,18 à 0,36. Autrement dit, sur 1999-2019, une pente réduite de 0,40 était probablement déjà exclue. **La
  prédiction de la fiche ne peut donc tenir que si l'ajout de 2020-2026 (la poussée d'inflation de 2021-2023 et la
  désinflation) relève nettement la pente.**
- **Chahad et coauteurs (2024, Bulletin économique de la BCE n° 5/2024)** rejettent à 1 % l'absence de « sur-lissage » à Q+2,
  avec des projections jusqu'à 2024T1. Mais leur test porte sur des fenêtres glissantes de 32 trimestres : il suffit
  qu'**une** fenêtre franchisse la valeur critique. Le test est bilatéral et ils ne publient **ni coefficient ni signe**. Le pic
  tombe sur la fenêtre 2014T3-2022T2. Après ajustement des erreurs pour les hypothèses techniques (pétrole, taux), le rejet
  disparaît à Q+2.

**Ce que ce test peut ajouter.** Une seule pente, avec son signe et sa taille, sur toutes les cibles de 1999T4 à 2026T3
(108 trimestres, dont toute la poussée de 2021-2023), sur des données publiques, avec un seuil de taille écrit à l'avance
(0,40) et pas seulement un test de nullité. Personne ne l'a publiée : Granziera et coauteurs s'arrêtent en 2019, et la BCE ne
donne pas de coefficient.

---

## 2. Ce qui est déjà connu avant le scellement, et la différence avec H03-v2

**H03-v2 a déjà été jugé « éliminée ».** Il posait une autre question : une règle de correction **réestimée en temps réel**
à chaque exercice (pente estimée sur les seules erreurs déjà connues ce jour-là, puis appliquée à la révision du jour)
aurait-elle annoncé les erreurs ? Statistique : moyenne, sur 11 blocs de deux ans (cibles 2004T1-2025T4), de la corrélation
**non centrée** entre la correction annoncée et l'erreur, horizons 1 à 4 regroupés, réalisations lues en temps réel dans la
MPD. Résultat publié (`verdict.json`) : R̄ = 0,016, intervalle à 90 % [−0,074 ; 0,105].

| Point | H03-v2 | J02 |
|---|---|---|
| Pente | réestimée à chaque exercice, avec le passé seulement (temps réel, hors échantillon) | une seule pente estimée après coup sur tout l'échantillon (en échantillon) |
| Statistique | corrélation non centrée, moyenne de 11 blocs à poids égaux | corrélation de Pearson centrée, une observation par trimestre cible à poids égaux |
| Horizons | 1 à 4 regroupés | 2 seulement |
| Réalisations | lues en temps réel dans la MPD, deux trimestres après la cible | dernier millésime Eurostat (`prc_hicp_minr`) |
| Cibles | 2004T1-2025T4 (88) | 1999T4-2026T3 (108) |
| Question | la révision était-elle **exploitable** à l'époque ? | la pente erreur-révision, mesurée après coup, atteint-elle la taille prédite ? |

Les deux réponses peuvent diverger : une pente positive en échantillon peut coexister avec l'échec d'une règle en temps
réel (Eva et Winkler, 2023), surtout quand la règle est estimée sur peu de points au début.

**Chiffres de H03-v2 connus du rédacteur** (champs descriptifs de `verdict.json`) : `r_moyen_h2` = 0,128 (même statistique de
blocs, restreinte à h = 2, non centrée, en temps réel) ; `part_b_positif` = 0,60 (60 % des pentes réestimées en temps réel
sont positives) ; `rapport_eqm_global` = 0,970 mais `rapport_eqm_hors_2021_2022` = 1,096 ; `r_hors_episode` = −0,030.

**Ce que ces chiffres changent aux chances de J02.** Ils rendent **plus probable** une pente positive sur tout l'échantillon :
à h = 2, la correction et l'erreur vont plutôt dans le même sens, et le seul endroit où la règle réduisait l'erreur est
2021-2022, période qu'une régression sur tout l'échantillon pèse fortement (les révisions et les erreurs y sont les plus
grandes). Ils rendent **moins probable** une pente à la fois grande (0,40) et répartie sur toute la période : hors 2021-2022,
la règle aggravait l'erreur. Le rédacteur s'attend, pour mémoire (hors verdict), à une pente réduite positive, plutôt entre
0,15 et 0,40, portée en bonne partie par 2021-2023 ; il ne sait pas de quel côté des seuils elle tombera.

**Le plan n'a pas été réglé sur ces chiffres.** L'horizon (2), la statistique (pente réduite), le retard de Newey-West (4),
le seuil de taille (0,40) et le seuil de significativité (1,645) sont ceux de la fiche, inchangés. Chaque amendement
(section 3) répond à une faille nommée par un juge ou à une correction de la note de nouveauté. Le seuil de mort n'a pas été
abaissé à 0,30 (bas de la plage de la fiche), ce qui aurait protégé l'idée.

**Règle d'aveuglement pour la suite.** L'expérimentateur et le vérificateur de J02 n'ouvrent **aucun** fichier du dossier
`tests-de-mort/H03-v2` (en particulier pas `H03-v2_analyse.csv`, qui contient des révisions et erreurs à h = 2). Ils
construisent tout à partir des sources brutes de la section 4. S'ils l'ont fait, ils l'écrivent dans `ecarts.md`.

---

## 3. Amendements déclarés à la fiche

| N° | La fiche disait | Ce test fait | Raison |
|---|---|---|---|
| A1 | « 90 à 100 trimestres cibles appariés » ; non concluant sous 90 | liste figée de **108 cibles, 1999T4 à 2026T3** ; non concluant sous **100** cibles complètes | la note de nouveauté compte 110 cibles appariables à h = 2 dans la MPD, dont 108 déjà réalisées (jusqu'à 2026T3) ; le minimum suit ce compte (juges : nombre de cibles) |
| A2 | tri par « horodatage des millésimes » | identification d'un exercice par sa lettre (`W` = mars, `G` = juin, `S` = septembre, `A` = décembre), contrôlée par le mois et l'année écrits dans `TITLE_COMPL` et par le premier trimestre de statut `F` | la MPD n'a pas d'horodatage de publication (note de nouveauté, correction 4) ; c'est la convention vérifiée dans H03-v2 |
| A3 | réalisations : Eurostat `prc_hicp_midx` | Eurostat **`prc_hicp_minr`**, indice `I15`, `TOTAL`, `EA`, une seule série de 1996-01 à 2026-09 | `prc_hicp_midx` est gelé à 2025-12 et archivé (passage à l'ECOICOP v2) ; une seule série évite de raccorder deux sources ; la série `ICP` de la BCE s'arrête aussi en 2025-12 |
| A4 | réalisation : non précisé | moyenne trimestrielle de l'indice mensuel, puis glissement sur un an : a(q) = 100 × (somme des 3 mois de q / somme des 3 mois de q − 4 − 1) | la MPD projette des glissements annuels trimestriels ; c'est leur définition |
| A5 | deux conditions (morte si tout l'IC à 90 % < 0,40 ; étayée si t > 1,645), sans dire ce qui se passe entre les deux | trois issues : survit, éliminée, non concluant ; la zone entre les deux conditions est « non concluant » | le protocole demande une règle complète ; un intervalle qui contient à la fois 0 et 0,40 ne tranche rien |
| A6 | rien sur la robustesse | garde de survie : la pente reste positive quand on retire **n'importe quelles deux années civiles consécutives** de cibles | juges : « les erreurs de 2021-2022 peuvent porter seules la pente » ; la garde vise ce cas sans choisir les années à la main |
| A7 | Newey-West à 4 retards, puissance avec +40 % sur l'écart-type | 4 retards maintenus et justifiés (section 6) ; Newey-West à 8 retards et bootstrap par blocs rapportés à titre descriptif ; puissance refaite avec trois scénarios explicites | juge : la majoration de 40 % n'était pas justifiée face au chevauchement et aux chocs persistants |
| A8 | rien | sous-échantillon fixe des cibles 1999T4-2019T4, descriptif : la pente non réduite y est directement comparable au 0,20 (0,21) de Granziera et coauteurs | juges : domination de 2021-2022 ; c'est aussi la réplication du résultat publié sur données publiques |
| A9 | rôle de l'IA : deux agents d'appariement, vérification manuelle | rôles du protocole (expérimentateur, vérificateur, verdict par `verdict.py`) ; contrôles de schéma automatiques | le protocole remplace ce dispositif |
| A10 | « référence incertaine » ; lissage optimal cité dans les risques | positionnement face à Granziera et coauteurs et Chahad et coauteurs (section 1) ; le lissage optimal et les hypothèses techniques sont des limites (section 9) | note de nouveauté, corrections 1 et 2 ; juge : une pente positive peut refléter un lissage optimal |

---

## 4. Données

**Source 1 — projections : base MPD de la BCE**, par l'API du portail de données de la BCE, sans compte.

```
https://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.<MILLÉSIME>.0000?format=csvdata
```

Clé : `MPD.Q.U2.HIC.A.<MILLÉSIME>.0000` (trimestriel, zone euro `U2`, IPCH total `HIC`, taux de croissance annuel `A`).
Liste des clés pour contrôle : `https://data-api.ecb.europa.eu/service/data/MPD?detail=serieskeysonly&format=csvdata`.
Colonnes utilisées : `KEY`, `TIME_PERIOD` (forme `1999-Q1`), `OBS_VALUE`, `OBS_STATUS` (`A` = observé, `F` = projeté),
`TITLE_COMPL` (nom de l'exercice ; la colonne `TITLE` est vide).

**Liste figée des 109 millésimes utilisés** : de `W99` à `W26` dans l'ordre de publication, soit `W`, `G`, `S`, `A` pour
chaque année de 1999 à 2025 (108 codes) plus `W26`. `G26` et `S26` ne servent pas (ils projettent des cibles non réalisées à
horizon 2 ou 3) ; tout autre code est ignoré.

**Numéro de trimestre** : t = 4 × année + (numéro du trimestre − 1). Exemples : 1999-Q4 → 7999 ; 2019-Q4 → 8079 ; 2021-Q1 →
8084 ; 2023-Q4 → 8095 ; 2026-Q3 → 8106. Le numéro d'un millésime est celui de son trimestre (lettre `W` → trimestre 1,
`G` → 2, `S` → 3, `A` → 4) : `W99` → 7996, `W26` → 8104.

**Téléchargement MPD.** Pour chaque millésime : jusqu'à 10 essais, délai maximal de 120 s par essai, 10 s entre deux essais ;
on garde le premier fichier reçu avec HTTP 200 et une ligne d'en-tête contenant les colonnes ci-dessus. Fichiers bruts :
`tests-de-mort/J02/donnees/MPD_Q_U2_HIC_A_<MILLÉSIME>.csv`, avec sha256, date et code HTTP dans
`tests-de-mort/J02/construire_journal.json`. **Si un seul des 109 fichiers manque, l'expérimentateur s'arrête** : non concluant
pour une raison de données.

**Source 2 — réalisations : Eurostat, `prc_hicp_minr`** (IPCH, ECOICOP v2), sans compte.

```
https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_minr/M.I15.TOTAL.EA?format=SDMX-CSV
```

Testé le 2026-11-12 : HTTP 200 au premier essai ; colonnes `DATAFLOW, LAST UPDATE, freq, unit, coicop18, geo, TIME_PERIOD,
OBS_VALUE, OBS_FLAG, CONF_STATUS` ; 369 mois de 1996-01 à 2026-09, aucun vide ; mise à jour du 2026-11-04. `EA` = zone euro à
composition évolutive (EA11-1999 … EA21-2026), même concept que `U2` dans la MPD. Indice `I15` (2015 = 100). Mois utilisés :
1998-10 à 2026-09 ; les mois postérieurs à 2026-09, s'il y en a au téléchargement, sont ignorés. Repli unique : si un mois
nécessaire manque dans `I15`, on prend **toute** la série `I25` du même jeu (même URL avec `I25`) ; un glissement annuel ne
dépend pas de la base, aux arrondis près ; le repli est écrit dans `ecarts.md`. Fichier brut :
`tests-de-mort/J02/donnees/prc_hicp_minr_M_I15_TOTAL_EA.csv`, avec sha256, date et code HTTP dans le journal.

**Lecture de la projection f₂(q).** Dans le fichier du millésime de numéro t_q − 2, ligne `TIME_PERIOD` = q : `OBS_VALUE`,
**à condition que `OBS_STATUS` = `F`**. **f₃(q)** : même règle dans le millésime de numéro t_q − 3. Manquante si la ligne
n'existe pas, si la valeur est vide ou si le statut n'est pas `F`.

**Lecture de la réalisation a(q).** Les trois mois du trimestre q (m1, m2, m3) et les trois mêmes mois un an plus tôt
(a1, a2, a3), dans la série Eurostat. a(q) = 100 × ((m1 + m2 + m3) / (a1 + a2 + a3) − 1), sans arrondi. Manquante si l'un des
six indices est vide ou non numérique. Les drapeaux (`OBS_FLAG`, par exemple `p` provisoire) n'excluent pas une valeur ;
ils sont recopiés dans le journal.

**Ce qui compte comme manquant.** Une cible est **complète** si f₂, f₃ et a sont présentes toutes les trois. On ne remplace
jamais une valeur manquante par une autre source, une interpolation ou un autre horizon.

**Coût.** 110 requêtes (10 à 15 s chacune d'après la note de nouveauté), puis un calcul de quelques secondes : quelques
minutes sur un portable.

---

## 5. Fichier d'analyse

**Nom** : `tests-de-mort/J02/J02_analyse.csv`. UTF-8, séparateur virgule, point décimal, première ligne = noms de colonnes,
cellule vide = manquant. **Une ligne par trimestre cible**, exactement **108 lignes** (1999-Q4 à 2026-Q3), y compris quand
des valeurs manquent. Tri : `t_cible` croissant.

| Colonne | Type | Unité, contenu |
|---|---|---|
| `cible` | texte | trimestre cible, forme `2022-Q1` |
| `t_cible` | entier | numéro du trimestre cible |
| `annee_cible` | entier | année civile de la cible |
| `millesime_h2` | texte | code du millésime de numéro `t_cible` − 2, par exemple `S21` |
| `t_millesime_h2` | entier | son numéro |
| `mois_titre_h2` | entier | mois lu dans `TITLE_COMPL` de ce millésime : le dernier nom de mois anglais complet (January … December) du texte → 1 à 12 ; vide si aucun |
| `annee_titre_h2` | entier | année à quatre chiffres lue dans `TITLE_COMPL` ; vide si aucune |
| `t_premier_F_h2` | entier | numéro du premier trimestre de statut `F` dans ce millésime ; vide s'il n'y en a pas |
| `statut_h2` | texte | `OBS_STATUS` de la ligne `TIME_PERIOD` = cible dans ce millésime ; vide si la ligne n'existe pas |
| `projection_h2` | décimal | f₂, % en glissement annuel, tel que publié (une décimale) ; vide si manquante |
| `millesime_h3`, `t_millesime_h3`, `mois_titre_h3`, `annee_titre_h3`, `t_premier_F_h3`, `statut_h3`, `projection_h3` | idem | mêmes définitions pour le millésime de numéro `t_cible` − 3 et f₃ |
| `indice_m1`, `indice_m2`, `indice_m3` | décimal | indice IPCH (2015 = 100) des trois mois du trimestre cible, tel que publié |
| `indice_an_avant_m1`, `indice_an_avant_m2`, `indice_an_avant_m3` | décimal | mêmes mois, un an plus tôt |
| `realise` | décimal | a(q), % en glissement annuel, non arrondi (au moins 8 décimales écrites) |
| `revision` | décimal | `projection_h2` − `projection_h3`, en points de pourcentage (au moins 6 décimales écrites) |
| `erreur` | décimal | `realise` − `projection_h2`, en points de pourcentage (au moins 6 décimales écrites) |

Soit exactement 26 colonnes, dans cet ordre et sans aucune autre : `cible, t_cible, annee_cible, millesime_h2,
t_millesime_h2, mois_titre_h2, annee_titre_h2, t_premier_F_h2, statut_h2, projection_h2, millesime_h3, t_millesime_h3,
mois_titre_h3, annee_titre_h3, t_premier_F_h3, statut_h3, projection_h3, indice_m1, indice_m2, indice_m3,
indice_an_avant_m1, indice_an_avant_m2, indice_an_avant_m3, realise, revision, erreur`.

**Contrôles de schéma.** Le vérificateur les refait sur le fichier. `n_violations_schema` = nombre de contrôles violés
(0 attendu, 11 au plus). Un contrôle est violé s'il échoue sur une seule ligne.
1. **Colonnes** : les 26 noms ci-dessus, dans cet ordre, sans autre colonne.
2. **Lignes** : exactement 108 ; `t_cible` prend chaque valeur de 7999 à 8106 une fois, en ordre croissant.
3. **Cible** : `cible` et `annee_cible` sont cohérents avec `t_cible` (formule de la section 4).
4. **Millésimes** : `t_millesime_h2` = `t_cible` − 2 et `t_millesime_h3` = `t_cible` − 3 ; chaque code est dans la liste figée
   des 109 et son numéro, tiré de la lettre et de l'année, est égal à la colonne `t_millesime_…` correspondante.
5. **Lettre et titre** : sur les 216 couples (ligne, millésime), `mois_titre` n'est **pas vide** et vaut 3 × (trimestre tiré
   de la lettre : `W` → 1, `G` → 2, `S` → 3, `A` → 4) ; `annee_titre` n'est pas vide et vaut l'année du code.
6. **Premier trimestre projeté** : `t_premier_F_h2` = `t_millesime_h2` et `t_premier_F_h3` = `t_millesime_h3` (la note de
   nouveauté l'a constaté sur les 111 millésimes : chaque exercice commence à h = 0).
7. **La projection précède la réalisation** : quand `projection_h2` (resp. `projection_h3`) n'est pas vide, `statut_h2`
   (resp. `statut_h3`) vaut `F` ; avec le contrôle 4, chaque valeur retenue est une prévision faite 2 (resp. 3) trimestres
   avant la cible, dont les trois mois sont tous postérieurs au trimestre de l'exercice. Aucune projection n'est lue sur une
   ligne de statut `A`.
8. **Valeurs** : `projection_h2`, `projection_h3` vides ou entre −5 et 15, avec au plus une décimale ; les six indices vides
   ou entre 20 et 300 ; `realise` vide ou entre −5 et 15.
9. **Réalisation** : `realise` est vide si et seulement si l'un des six indices est vide ; sinon elle vaut
   100 × ((m1 + m2 + m3) / (a1 + a2 + a3) − 1) à 10⁻⁶ près.
10. **Révision et erreur** : `revision` est vide si et seulement si `projection_h2` ou `projection_h3` est vide, sinon elle
    vaut leur différence à 10⁻⁶ près ; `erreur` est vide si et seulement si `realise` ou `projection_h2` est vide, sinon elle
    vaut leur différence à 10⁻⁶ près.
11. **Cohérence entre lignes** : pour toute ligne t dont la ligne t − 4 existe, `indice_an_avant_mk`(t) = `indice_mk`(t − 4)
    pour k = 1, 2, 3, quand les deux sont présents (même série, mêmes mois).

---

## 6. Statistique

Tout se calcule à partir du seul fichier d'analyse, en double précision, sans arrondi intermédiaire.

**Échantillon.** Les lignes **complètes** : `revision` et `erreur` toutes deux présentes. n = leur nombre (`n_cibles`).
Elles sont rangées par `t_cible` croissant ; r_i = `revision`, e_i = `erreur`.

**Statistique principale : β_z, pente réduite, avec écart-type de Newey-West à 4 retards.**
1. r̄, ē = moyennes ; s_r, s_e = écarts-types avec diviseur n − 1 (`ecart_type_revision`, `ecart_type_erreur`).
2. Variables réduites : z_i = (r_i − r̄) / s_r et y_i = (e_i − ē) / s_e.
3. Régression par MCO de y sur une constante et z. La constante vaut 0 ; la pente vaut
   **β_z = Σ z_i y_i / Σ z_i²**, c'est-à-dire la corrélation de Pearson entre r et e (champ `beta_z`).
4. Résidus u_i = y_i − β_z z_i ; produits v_i = z_i u_i.
5. Pour j = 0 à L : Γ_j = somme de v_a × v_b sur les couples de lignes complètes (a, b) tels que `t_cible`(a) − `t_cible`(b)
   = j (Γ_0 = Σ v_i²). Une cible absente ne crée aucun couple.
6. S = Γ_0 + 2 × Σ_{j=1..L} (1 − j/(L + 1)) × Γ_j (poids de Bartlett), avec **L = 4**.
7. **Écart-type** : `et_beta_z_nw4` = racine(S) / Σ z_i². **Aucune correction de petit échantillon** (pas de facteur
   n/(n − 2)). Équivalent, quand aucune cible ne manque : `statsmodels` `OLS(y, add_constant(z)).fit(cov_type="HAC",
   cov_kwds={"maxlags": 4, "use_correction": False})`.
8. `t_nw4` = β_z / `et_beta_z_nw4`. Intervalle à 90 % : `borne_basse_ic90` = β_z − 1,645 × et ; `borne_haute_ic90` = β_z +
   1,645 × et.
9. Pente non réduite, pour comparaison avec Granziera et coauteurs : `beta_brut` = β_z × s_e / s_r (points d'erreur par point
   de révision) ; `et_beta_brut_nw4` = `et_beta_z_nw4` × s_e / s_r. Le t est le même.

**Pourquoi 4 retards.** (a) Sous l'hypothèse d'efficience, l'erreur d'une projection à deux trimestres d'un glissement annuel
contient les nouvelles des trimestres q − 2 (en partie), q − 1 et q : deux erreurs de cibles distantes de 1 ou 2 trimestres
partagent des chocs (moyenne mobile d'ordre 2, au plus 3 si la date d'arrêt de l'exercice tombe tôt). Il faut donc au moins
3 retards. (b) La règle usuelle de Newey et West (1994), partie entière de 4 × (n/100)^(2/9), donne 4 pour n ≈ 108. (c) C'est
le choix de la fiche. Les poids de Bartlett sous-pondèrent les retards 2 et 3 ; c'est pourquoi 8 retards et un bootstrap par
blocs sont rapportés à côté (S2), sans entrer dans le verdict.

**Pourquoi 1,645.** Test unilatéral à 5 % de β_z > 0 : l'hypothèse a un sens (pente positive). La loi de Student à 106
degrés de liberté donnerait 1,659 ; l'écart est négligeable devant l'incertitude sur l'écart-type lui-même.

**Garde de robustesse (entre dans le verdict).** Pour chaque année Y de 1999 à 2025, on retire toutes les cibles des années
Y et Y + 1 et on recalcule la corrélation de Pearson entre r et e sur les cibles complètes restantes (27 valeurs).
`beta_z_min_sans_deux_ans` = la plus petite ; `annee_debut_min` = l'année Y qui la donne (la plus petite en cas d'égalité).

**Champs dérivés pour la règle.**
- `marge_indecision` = le plus petit des deux nombres (− `borne_basse_ic90`) et (`borne_haute_ic90` − 0,40). Il est positif ou
  nul exactement quand l'intervalle à 90 % contient à la fois 0 et 0,40.
- `conflit_robustesse` = 1 si `borne_basse_ic90` > 0 et `borne_haute_ic90` ≥ 0,40 et `beta_z_min_sans_deux_ans` ≤ 0 ;
  0 sinon. (Quand `borne_haute_ic90` < 0,40, l'hypothèse chiffrée est exclue de toute façon : la garde n'a rien à protéger.)

**Convention.** Si n < 10 ou si s_r ou s_e est nul, tous les champs numériques de cette section et des analyses secondaires
valent 0 (le verdict est de toute façon « non concluant », n étant sous 100). Un sous-échantillon secondaire de moins de 10
cibles ou de variance nulle donne 0 pour ses champs.

**Analyses secondaires — trois, descriptives, hors verdict.** Calculées et rapportées quoi qu'il arrive.

*S1 — Avant 2020 (comparaison avec Granziera et coauteurs).* Cibles complètes avec `t_cible` ≤ 8079 (1999T4-2019T4, le même
échantillon que leur article). Mêmes étapes 1 à 9 sur ce seul sous-échantillon (réduction faite dans le sous-échantillon) :
`n_avant_2020`, `beta_z_avant_2020`, `beta_brut_avant_2020`, `et_beta_brut_avant_2020_nw4`. Lecture prévue : on compare
`beta_brut_avant_2020` à 0,20 (0,21). Pas de seuil : le résultat de cette période est déjà publié, il ne peut donc pas départager.

*S2 — Sensibilité de l'inférence.*
- `et_beta_z_nw8` : étapes 5 à 7 avec L = 8.
- Bootstrap par blocs mobiles, sur les n cibles complètes rangées par `t_cible` : blocs de 8 positions consécutives (deux
  ans) ; k = arrondi supérieur de n / 8 blocs par tirage ; débuts tirés uniformément parmi les positions 0 à n − 8 ; blocs
  mis bout à bout puis tronqués à n lignes ; on calcule la corrélation de Pearson entre r et e. B = 9 999 tirages ; générateur
  `numpy.random.default_rng(20261112)`, débuts tirés par `rng.integers(0, n − 7, size=k)` tirage après tirage ; un tirage
  dont r ou e est constant est remplacé par le tirage suivant. `bb_borne_basse_ic90` et `bb_borne_haute_ic90` = centiles 5 et
  95 (`numpy.percentile`, méthode linéaire par défaut). Blocs de 8 : ils couvrent le chevauchement (2 à 3 trimestres) et la
  persistance d'un épisode d'environ deux ans, tout en gardant 13 à 14 blocs par tirage.

*S3 — Poids de l'épisode 2021-2023.*
- `n_hors_2021_2023`, `beta_z_hors_2021_2023`, `et_beta_z_hors_2021_2023_nw4` : étapes 1 à 7 sans les cibles de 8084 à 8095
  (2021T1-2023T4).
- `beta_z_min_sans_une_annee` : la plus petite des 28 corrélations obtenues en retirant une seule année civile de cibles
  (1999 à 2026).

**Fichiers.** L'expérimentateur écrit `temoin.json`, le vérificateur `verification.json` ; les deux contiennent tous les
champs de la règle (section 11), en nombres. Ni l'un ni l'autre n'écrit de verdict.

---

## 7. Arithmétique de puissance

Calculs sans donnée, en loi normale, l'écart-type étant traité comme connu.

**Écart-type attendu de β_z.** Pour une corrélation sur n = 108 observations indépendantes, l'écart-type vaut environ
1/√108 = 0,096. Deux raisons de l'augmenter :
- **Dépendance dans le temps.** Sous l'hypothèse nulle, la variance est multipliée par environ 1 + 2 × Σ_j ρ_r(j) ρ_e(j), où
  ρ_r et ρ_e sont les autocorrélations des révisions et des erreurs. Erreurs en moyenne mobile d'ordre 2 (ρ_e ≈ 0,6 ; 0,3 ;
  0,1) et révisions un peu persistantes (ρ_r ≈ 0,2 à 0,4 au premier retard) : facteur 1,14 à 1,27 sur l'écart-type. Avec des
  chocs plus persistants (ρ_e jusqu'à 0,7 ; 0,5 ; 0,3 ; 0,2 et ρ_r jusqu'à 0,5 ; 0,3 ; 0,2 ; 0,1) : 1,47.
- **Volatilité commune.** Si 8 trimestres sur 108 (la poussée de 2021-2022) ont des révisions et des erreurs 2 fois plus
  dispersées que les autres, l'écart-type est multiplié par 1,19 ; 3 fois plus dispersées : 1,65.

D'où trois scénarios : **optimiste** 0,10 (facteur 1,05) ; **central** 0,14 (facteur 1,45, proche des +40 % de la fiche, mais
cette fois décomposé) ; **pessimiste** 0,19 (facteur 2).

**Ce que la règle demande** (section 8). Survie : β̂_z > max(1,645 × ET ; 0,40 − 1,645 × ET). Élimination : β̂_z < 0,40 −
1,645 × ET. Entre les deux : non concluant.

| ET | survit si β̂_z > | éliminée si β̂_z < | effet détecté 8 fois sur 10 |
|---|---|---|---|
| 0,10 | 0,236 | 0,236 | 0,32 |
| 0,14 | 0,230 | 0,170 | 0,35 |
| 0,19 | 0,313 | 0,087 | 0,47 |

**Probabilités des trois issues** (survit / éliminée / non concluant), avant la garde de robustesse :

| Vraie pente β_z | ET = 0,10 | ET = 0,14 (central) | ET = 0,19 |
|---|---|---|---|
| 0 | 1 / 99 / 0 % | 5 / 89 / 6 % | 5 / 68 / 27 % |
| 0,10 (ordre de grandeur de Granziera et coauteurs, réduit) | 9 / 91 / 0 % | 18 / 69 / 13 % | 13 / 47 / 39 % |
| 0,20 | 36 / 64 / 0 % | 41 / 41 / 17 % | 28 / 28 / 45 % |
| 0,30 (bas de la plage de la fiche) | 74 / 26 / 0 % | 69 / 18 / 13 % | 47 / 13 / 39 % |
| 0,40 (prédiction) | 95 / 5 / 0 % | 89 / 5 / 6 % | 68 / 5 / 27 % |
| 0,55 (haut de la plage) | 100 / 0 / 0 % | 99 / 0 / 1 % | 89 / 1 / 10 % |

**Lecture.** Dans le scénario central, le test tranche bien aux deux bouts : une pente nulle est éliminée 9 fois sur 10, la
pente prédite (0,40) survit 9 fois sur 10. Il tranche mal au milieu : une vraie pente de 0,20 donne autant de chances de
survie que d'élimination. C'est voulu : 0,20 est à mi-chemin entre « pas d'effet » et l'effet prédit, et la règle reprend le
seuil de 0,40 de la fiche. Une erreur de première espèce de 5 % au plus (survie quand β_z = 0) suppose que l'écart-type de
Newey-West est juste ; avec 108 points et des queues épaisses, il est souvent trop petit (limite 4).

**Ce sont des plafonds pour « survit »** : la garde de robustesse peut changer une survie en « non concluant » si la pente
tient à deux années consécutives ; les projections arrondies à 0,1 point ajoutent du bruit aux révisions, ce qui tire la pente
vers zéro.

**Minimum d'échantillon.** 108 cibles attendues. Sous 100 (plus de 8 cibles, deux ans, manquantes), la base ne contient pas
ce que la note de nouveauté a compté : c'est un signe de problème de construction, et l'écart-type grandit d'au moins 4 %, ce
qui déplace les seuils du tableau ; le verdict est alors « non concluant ».

---

## 8. Règle de verdict

Le verdict est calculé par `verdict.py` à partir des chiffres du vérificateur. « Survit » veut dire : sur 1999T4-2026T3, la
pente de l'erreur sur la révision à horizon 2 est significativement positive, compatible avec la taille prédite (0,40), et ne
tient pas à deux années consécutives.

**Non concluant** si l'une de ces conditions est vraie :
1. `n_violations_schema` > 0 — fichier d'analyse hors schéma ; on ne juge pas une idée sur un fichier douteux.
2. `n_cibles` < 100 — voir « Minimum d'échantillon » (section 7).
3. `marge_indecision` ≥ 0 — l'intervalle à 90 % contient à la fois 0 (pas de sous-réaction) et 0,40 (la prédiction) : les
   données ne choisissent pas.
4. `conflit_robustesse` ≥ 1 — l'intervalle est entièrement positif et contient 0,40, mais la pente devient nulle ou négative
   quand on retire deux années consécutives : la preuve repose sur un épisode, et les indices se contredisent.
5. Écart entre expérimentateur et vérificateur au-delà de la tolérance sur un champ, ou champ absent (protocole).

**Survit** si aucune condition ci-dessus n'est vraie et si les trois suivantes le sont :
- `borne_basse_ic90` > 0. Seuil 0 : pente nulle = projections efficientes au sens de ce test. Équivaut à t > 1,645, la
  condition « positivement étayée » de la fiche.
- `borne_haute_ic90` ≥ 0,40. Seuil 0,40 : la prédiction ponctuelle de la fiche ; la fiche déclare morte la sous-réaction forte
  si tout l'intervalle est en dessous. Repris sans changement.
- `beta_z_min_sans_deux_ans` > 0. Seuil 0 : on demande un signe, pas un test (100 cibles restantes ne donnent pas la
  puissance d'un second test) ; un signe nul ou négatif voudrait dire que deux années portent seules la pente.

**Éliminée** dans tous les autres cas. Compte tenu des conditions de non-conclusion, cela arrive exactement quand
`borne_haute_ic90` < 0,40 : les données excluent, au seuil unilatéral de 5 %, la sous-réaction de l'ordre de 0,40 prédite par
la fiche. C'est vrai même si la borne basse est positive : une sous-réaction **faible** mais significative élimine quand même
l'hypothèse telle qu'elle a été chiffrée ; on l'écrira (section 10).

**Tolérances** (écart maximal entre expérimentateur et vérificateur, qui calculent sur le même fichier d'analyse) : 0 sur les
champs entiers ; 0,005 sur les pentes, corrélations et écarts-types ; 0,01 sur les bornes et la marge ; 0,02 sur `t_nw4` et
sur les bornes du bootstrap (le vérificateur peut utiliser un autre générateur aléatoire).

---

## 9. Limites

1. **Le plan n'est pas aveugle.** Il est écrit en 2026 par quelqu'un qui connaît la poussée d'inflation de 2021-2023, les
   résultats de Granziera et coauteurs et de la BCE, et le verdict de H03-v2 avec ses chiffres à h = 2 (section 2). Aucune
   donnée n'est postérieure au plan. Les choix principaux viennent de la fiche, pas de ces chiffres, mais on ne peut pas le
   prouver.
2. **Un épisode peut encore porter la pente.** Une régression sur toute la période pèse beaucoup les trimestres où révisions
   et erreurs sont grandes. La garde retire deux années consécutives, pas trois : si 2021, 2022 et 2023 vont toutes dans le
   même sens, la pente peut survivre grâce à elles. S3 (`beta_z_hors_2021_2023`) le montrera, sans entrer dans le verdict ;
   la phrase de survie devra le citer.
3. **Sous-réaction ou lissage optimal : le test ne les sépare pas.** Une pente positive est compatible avec (a) une institution
   qui, sous incertitude, révise volontairement par petits pas parce que des révisions brusques ont un coût (communication,
   crédibilité) ; (b) un produit agrégé : les exercices de juin et de décembre combinent les projections des banques
   centrales nationales, et une moyenne de prévisionnistes rationnels mais mal informés donne une pente positive (Coibion et
   Gorodnichenko, 2015) ; (c) des hypothèses techniques imposées (pétrole tiré des contrats à terme, taux de marché) : la BCE
   montre qu'à Q+2 la rigidité disparaît une fois les erreurs ajustées de ces hypothèses. On écrira « les erreurs suivent les
   révisions », jamais « les services sont irrationnels ».
4. **Écart-type de Newey-West en petit échantillon.** Avec 108 points, des erreurs autocorrélées et une volatilité concentrée
   en 2021-2022, l'écart-type de Newey-West est souvent trop petit, ce qui rend la survie un peu trop facile. Le bootstrap par
   blocs et 8 retards (S2) le diront, sans corriger le verdict.
5. **Réalisations du dernier millésime**, en ECOICOP v2, et non celles que les services voyaient à l'époque. Les révisions de
   l'IPCH sont petites, mais pas nulles.
6. **Projections arrondies à 0,1 point.** Les révisions sont des multiples de 0,1 ; beaucoup peuvent valoir 0. Cet arrondi
   agit comme une erreur de mesure sur la variable explicative et tire la pente vers zéro.
7. **Millésimes anciens reconstitués.** Les exercices de 1999-2000 n'étaient pas publiés à l'époque avec ce détail
   trimestriel. Cela ne gêne pas un test en échantillon, mais ces cibles ne sont pas des projections « publiques » du moment.
8. **Un seul horizon.** h = 2 est le choix de la fiche ; Granziera et coauteurs trouvent des pentes positives jusqu'à h = 3 et
   négatives au-delà. Un résultat à h = 2 ne dit rien des autres horizons.
9. **En échantillon seulement.** Même si J02 survit, cela ne veut pas dire qu'on aurait pu corriger les projections en temps
   réel : H03-v2 a été éliminée sur cette question.

---

## 10. Ce qu'on écrira dans chaque cas

- **Survit** : « Sur les 108 trimestres cibles de 1999T4 à 2026T3, les erreurs des projections d'inflation de la BCE à deux
  trimestres suivaient leurs révisions (corrélation β_z avec son intervalle à 90 %, compatible avec la sous-réaction de
  0,40 prédite et positive quelles que soient les deux années retirées) ; on donne la pente sans 2021-2023 et avant 2020 à
  côté, et le test ne dit pas si cela vient d'une sous-réaction, d'un lissage voulu ou des hypothèses techniques. »
- **Éliminée, sans pente significative** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` ≤ 0) : « Sur 1999T4-2026T3, la pente de
  l'erreur sur la révision à deux trimestres n'est pas distinguable de zéro et les données excluent, au seuil de 5 %, la
  sous-réaction de 0,40 écart-type prédite ; l'ajout de la période 2020-2026 ne change pas la conclusion de Granziera et
  coauteurs sur 1999-2019. »
- **Éliminée, avec une pente faible mais significative** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` > 0) : « Les erreurs
  suivent les révisions, mais nettement moins que prédit : la pente est positive et significative, et pourtant les données
  excluent, au seuil de 5 %, la sous-réaction de 0,40 écart-type que la fiche avait chiffrée. »
- **Non concluant, par indécision** (`marge_indecision` ≥ 0) : « Avec 108 trimestres cibles, l'intervalle à 90 % de la pente
  contient à la fois 0 et 0,40 : on publie l'intervalle et on ne conclut pas. »
- **Non concluant, par conflit** (`conflit_robustesse` = 1) : « La pente est significativement positive sur toute la période,
  mais elle disparaît quand on retire deux années consécutives (lesquelles : `annee_debut_min`) ; la preuve tient à un épisode
  et l'on ne conclut pas. »
- **Non concluant, par les données** (schéma, moins de 100 cibles, fichier manquant, écart entre expérimentateur et
  vérificateur) : « Le test n'a pas pu être mené comme préinscrit ; la raison exacte est dans `ecarts.md` et aucune conclusion
  n'est tirée sur l'hypothèse. »

---

## 11. Règle lisible par machine

```json
{
  "id": "J02",
  "fichier_analyse": "J02_analyse.csv",
  "champs_verification": [
    "n_violations_schema",
    "n_cibles",
    "beta_z",
    "et_beta_z_nw4",
    "t_nw4",
    "borne_basse_ic90",
    "borne_haute_ic90",
    "marge_indecision",
    "beta_z_min_sans_deux_ans",
    "annee_debut_min",
    "conflit_robustesse",
    "beta_brut",
    "et_beta_brut_nw4",
    "ecart_type_revision",
    "ecart_type_erreur",
    "n_avant_2020",
    "beta_z_avant_2020",
    "beta_brut_avant_2020",
    "et_beta_brut_avant_2020_nw4",
    "et_beta_z_nw8",
    "bb_borne_basse_ic90",
    "bb_borne_haute_ic90",
    "n_hors_2021_2023",
    "beta_z_hors_2021_2023",
    "et_beta_z_hors_2021_2023_nw4",
    "beta_z_min_sans_une_annee"
  ],
  "survit_si": [
    {"champ": "borne_basse_ic90", "operateur": ">", "seuil": 0},
    {"champ": "borne_haute_ic90", "operateur": ">=", "seuil": 0.40},
    {"champ": "beta_z_min_sans_deux_ans", "operateur": ">", "seuil": 0}
  ],
  "non_concluant_si": [
    {"champ": "n_violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "n_cibles", "operateur": "<", "seuil": 100},
    {"champ": "marge_indecision", "operateur": ">=", "seuil": 0},
    {"champ": "conflit_robustesse", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "n_violations_schema": 0,
    "n_cibles": 0,
    "beta_z": 0.005,
    "et_beta_z_nw4": 0.005,
    "t_nw4": 0.02,
    "borne_basse_ic90": 0.01,
    "borne_haute_ic90": 0.01,
    "marge_indecision": 0.01,
    "beta_z_min_sans_deux_ans": 0.005,
    "annee_debut_min": 0,
    "conflit_robustesse": 0,
    "beta_brut": 0.005,
    "et_beta_brut_nw4": 0.005,
    "ecart_type_revision": 0.005,
    "ecart_type_erreur": 0.005,
    "n_avant_2020": 0,
    "beta_z_avant_2020": 0.005,
    "beta_brut_avant_2020": 0.005,
    "et_beta_brut_avant_2020_nw4": 0.005,
    "et_beta_z_nw8": 0.005,
    "bb_borne_basse_ic90": 0.02,
    "bb_borne_haute_ic90": 0.02,
    "n_hors_2021_2023": 0,
    "beta_z_hors_2021_2023": 0.005,
    "et_beta_z_hors_2021_2023_nw4": 0.005,
    "beta_z_min_sans_une_annee": 0.005
  }
}
```
