# F04 — Préinscription du test de mort

Rédigé le 2026-11-12 par le rédacteur de préinscription. Ce texte est figé une fois scellé. Le rédacteur n'a lancé aucune
analyse ; ce qu'il a vu des données est listé à la fin de la section « Données ».

## 1. Ce qui reste à tester

La note de nouveauté classe la fiche comme variante mince, et ce test ne prétend pas davantage. Point par point :

- **Existence du V inversé sur le rendement brut, 2010 à juillet 2024.** Déjà publié par Fleming, Liu et Nguyen (2026), avec la
  même statistique sur dix jours et des prix de titres individuels. On ne le reteste pas.
- **Les 26 mois d'après leur échantillon (août 2024 à septembre 2026), sur le rendement brut.** C'est le test hors échantillon
  strict de leur chiffre, mais il n'a pas de puissance : l'erreur type attendue est d'environ 2 pb (section 6) pour un effet
  publié de 1,2 pb (10 ans) à 2,6 pb (5 ans). Il ne peut ni confirmer ni réfuter. Il est rapporté à titre descriptif (S1), sans
  effet sur le verdict.
- **L'effet de taille sur dix jours.** C'est le seul point où la note voit une réponse connue pouvoir changer. Il n'est pas
  testable proprement ici : le montant offert change par paliers, à quelques annonces trimestrielles près sur seize ans, donc
  la pente compare en réalité une poignée de sous-périodes. Rapporté à titre descriptif (S2).
- **Ce qui reste et qu'on peut tester avec puissance.** La composante de la pression propre au titre adjugé, c'est-à-dire
  l'écart entre le rendement de l'échéance adjugée et la courbe ajustée sur les titres anciens. C'est la mesure de la fiche.
  D'après la note, les travaux cités rapportent le rendement brut des titres courants et précédents, pas cet écart. La mesure
  n'est propre que là où le titre de référence ne change pas à l'adjudication : les **réouvertures** des titres à 10, 20 et
  30 ans. Le test porte sur elles seules.

Ce que le test ajoute s'il aboutit : une mesure, sur données publiques et quotidiennes, de la pression locale autour de
321 réouvertures de 2010 à 2026, dont 51 postérieures à l'échantillon publié. Ce qu'il n'ajoute pas : rien sur les échéances de
2 à 7 ans, rien sur les nouvelles émissions, rien de concluant sur la taille.

## 2. Question, hypothèse et prédiction chiffrée

**Question.** Autour des réouvertures de titres du Trésor américain à 10, 20 et 30 ans, le rendement à échéance constante de
l'échéance adjugée monte-t-il par rapport à la courbe des titres anciens dans les cinq jours qui précèdent l'adjudication, puis
redescend-il dans les cinq jours qui suivent ?

**Hypothèse falsifiable.** Oui : la moyenne de V (définie en section 5) est strictement positive.

**Prédiction chiffrée (reprise de la fiche, sans changement).** Moyenne de V comprise entre **+0,5 et +1,5 point de base** sur
2010-01 à 2026-09. La borne basse, 0,5 pb, sert de seuil d'élimination.

Position par rapport aux travaux les plus proches (chiffres lus dans la note de nouveauté, pas dans les articles) :

| Travail | Mesure | Période | Chiffre |
|---|---|---|---|
| Fleming, Liu et Nguyen (2026), tableau A2 | rendement brut du titre courant, V sur dix jours | 2007-2014 | 4,4 pb (10 ans) |
| idem | idem | 2015-2024 | 1,2 pb non significatif (10 ans) ; 2,6 pb (5 ans) |
| Somogyi, Wallen et Xu (2025) | rendement brut à 10 ans | 2011-avril 2025 | pas de baisse après l'adjudication |
| Ce test | écart à la courbe des titres anciens, réouvertures seules | 2010-2026 | prédit : 0,5 à 1,5 pb |

Ces chiffres publiés portent sur le niveau des rendements. L'écart à la courbe retranche ce niveau. Un résultat nul ici ne
contredit donc pas ces travaux, et un résultat positif ne les reproduit pas : il dit que le titre adjugé décote en plus du
reste de la courbe.

Avis du rédacteur, sans effet sur la règle : les juges estiment le saut mécanique de changement de titre à 0,5 à 1,5 pb, soit
la taille de la prédiction. Une fois ce saut retiré par construction, la moitié basse de la fourchette est la plus plausible.

## 3. Amendements déclarés

| N° | Test de la fiche | Test préinscrit | Raison |
|---|---|---|---|
| A1 | Toutes les adjudications à 2, 3, 5, 7, 10, 20, 30 ans (environ 1 000 annoncées, 1 285 dans l'API) | Réouvertures des titres à 10, 20 et 30 ans seulement (321) | Faille principale des juges. Le rendement à échéance constante repose sur le titre le plus récemment adjugé. À une nouvelle émission, ce titre change et l'écart saute de la prime du titre neuf. À une réouverture, le Trésor revend le même titre : la référence ne change pas. Les titres à 2, 3, 5 et 7 ans n'ont pas de réouverture ; ils sortent du verdict. |
| A2 | Rien sur la dérive de la prime | V est une différence seconde | La prime du titre courant s'use lentement entre deux émissions. Une dérive linéaire sur la fenêtre s'annule exactement dans V = 2·E(J) − E(J−5) − E(J+5). |
| A3 | Placebo : dates fictives, même jour de semaine, semaines sans adjudication de l'échéance ; \|t\| < 2 | Placebo fixé : J + 10 jours ouvrés, même échéance, même titre de référence, fenêtre sans adjudication de cette échéance ; \|t\| < 2 | Même idée, rendue reproductible. Le placebo porte le même titre de référence que l'adjudication, donc aucun des deux ne porte de saut. |
| A4 | Meurt si moyenne ≤ 0 ou t < 2 | Meurt si t < 2 **et** si la borne haute de l'intervalle à 95 % est ≤ 0,5 pb. Si t < 2 mais que la borne haute dépasse 0,5 pb : non concluant | Deuxième faille des juges (effet noyé dans le bruit). Un t < 2 obtenu avec une estimation trop imprécise pour exclure l'effet prédit n'est pas une élimination. La survie reste aussi exigeante que dans la fiche. |
| A5 | Second verdict sur la pente « dose » | Pente rapportée à titre descriptif (S2) | Un seul verdict par fiche. Le montant offert bouge par paliers : puissance faible et confusion avec la période. |
| A6 | Choix fixés et scellés sur 1980-2009 | Choix fixés ici, sans lire aucun rendement | Plus strict : aucune donnée de rendement n'a servi à choisir la fenêtre, la mesure ou les filtres. |
| A7 | Régression avec part des spécialistes, annonces macroéconomiques, fin de mois | Moyenne simple de V, sans contrôle | L'écart à la courbe retire déjà les mouvements de niveau. Moins de choix libres. Les pages ALFRED ne sont plus utilisées. |
| A8 | Erreurs groupées par mois, formule non écrite | Même groupement, formule écrite (section 5) | Deux personnes doivent obtenir le même nombre. |
| A9 | « Test hors échantillon après publication » présenté comme la nouveauté | Mois d'après juillet 2024 et échéance à 20 ans rapportés en S1 et S3, descriptifs | Note de nouveauté : la période est publiée jusqu'en juillet 2024, et les 26 mois restants ne donnent pas de puissance sur le rendement brut. |

Inchangés : la fenêtre de cinq jours ouvrés de part et d'autre, la courbe ajustée de la Réserve fédérale en rendement au pair,
le seuil t ≥ 2, la période 2010-01 à 2026-09.

## 4. Données

Toutes publiques, sans compte. L'expérimentateur enregistre chaque fichier brut dans `tests-de-mort/F04/brut/`, avec la date de
téléchargement et le sha256.

**D1. Adjudications.** Une seule requête, testée le 2026-11-12 (HTTP 200, 1 639 lignes, une page) :

```
https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?fields=auction_date,security_type,security_term,original_security_term,reopening,inflation_index_security,floating_rate,offering_amt,cusip,issue_date,maturity_date&filter=auction_date:gte:2010-01-01,auction_date:lte:2026-09-30,security_type:in:(Note,Bond)&sort=auction_date&page%5Bsize%5D=10000
```

Filtres : `inflation_index_security` = "No" et `floating_rate` = "No". Il reste 1 285 lignes. L'échéance se lit dans
`security_term`, pas dans `original_security_term` (ce dernier vaut parfois « 7-Year » pour un titre à 2 ans émis sous un
ancien code) :

| `security_term` | `echeance` | `reouverture` | lignes attendues |
|---|---|---|---|
| 2-Year, 3-Year, 5-Year, 7-Year | 2, 3, 5, 7 | 0 | 201 chacune |
| 10-Year / 20-Year / 30-Year | 10 / 20 / 30 | 0 | 67 / 26 / 67 |
| 9-Year 10-Month, 9-Year 11-Month | 10 | 1 | 67 + 68 |
| 19-Year 10-Month, 19-Year 11-Month | 20 | 1 | 25 + 27 |
| 29-Year 10-Month, 29-Year 11-Month | 30 | 1 | 67 + 67 |

Toute autre valeur de `security_term` : ligne écartée et notée dans `ecarts.md`. Contrôle de construction : les 321 lignes de
réouverture ont `reopening` = "Yes" dans l'API.

**D2. Rendements à échéance constante (Trésor, via FRED).** `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>` pour
DGS2, DGS3, DGS5, DGS7, DGS10, DGS20, DGS30. Chacune testée : HTTP 200, colonnes `observation_date,<SERIE>`, dernière date
2026-11-09. Unité : pour cent par an, deux décimales. Valeur manquante : champ vide (jours fériés).

**D3. Courbe ajustée sur les titres anciens (Gürkaynak, Sack et Wright).**
`https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` : HTTP 200, 16,7 Mo, modifié le 2026-11-10. Neuf lignes
de préambule, puis l'en-tête qui commence par `Date`. Colonnes utilisées : `Date`, `SVENPY02`, `SVENPY03`, `SVENPY05`,
`SVENPY07`, `SVENPY10`, `SVENPY20`, `SVENPY30` (rendement au pair, pour cent, quatre décimales). Valeur manquante : `NA`.

**Calendrier.** C est la liste triée des dates où DGS10 a une valeur non vide. Pour une date d de C, « d + k » est la date
située k rangs plus loin dans C.

**Ce qui compte comme manquant.**
- Une ligne dont l'une des six valeurs de rendement (D2 et D3 en J − 5, J, J + 5) est vide, ou dont la date d'adjudication
  n'est pas dans C : `complet` = 0, exclue des calculs, comptée.
- Une source D1, D2 ou D3 injoignable ou de colonnes différentes : pas de source de remplacement. Le fichier d'analyse n'est
  pas construit et le test est non concluant.
- Moins de 290 réouvertures utilisables, ou moins de 120 mois : non concluant (section 7).

**Sources testées et non retenues.**
- Méthode du Trésor, `https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology`
  (HTTP 200) : les entrées sont les cotations « for the most recently auctioned » titres. Le texte ne dit pas quel jour le
  titre neuf entre dans la courbe. C'est la raison de A1 : on ne cherche pas à dater le saut, on ne garde que les jours où il
  n'y en a pas.
- Prix par titre, FedInvest, `https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate` : la page répond 200 ;
  l'envoi d'une date avec le témoin de session et le jeton du formulaire renvoie 200 et un tableau `CUSIP, SECURITY TYPE, RATE,
  MATURITY DATE, CALL DATE, BUY, SELL, END OF DAY` (testé pour le 2012-03-14) ; sans session, 403. Non retenue : près de
  1 000 dates à demander une par une, et une conversion prix-rendement que le vérificateur ne pourrait pas refaire à partir du
  fichier d'analyse. C'est la suite naturelle si l'idée survit.

**Ce que le rédacteur a vu.** Les en-têtes des fichiers ; le nombre de lignes et les dates extrêmes des séries FRED (fichiers
téléchargés en entier pour ce seul comptage, puis supprimés sans lecture des valeurs) ; les métadonnées d'adjudication (dates, échéances, montants, indicateur de réouverture), qui ont servi à compter les lignes
ci-dessus. Deux valeurs de DGS10 (1er et 2 juillet 2024) et deux lignes de 1961 du fichier D3 se sont affichées pendant le
contrôle des colonnes. Aucune moyenne, aucun écart, aucune statistique n'a été calculé.

## 5. Fichier d'analyse

Nom : `tests-de-mort/F04/F04_analyse.csv`. UTF-8, virgule, point décimal, une ligne d'en-tête, champ vide pour une valeur
manquante. Trié par `date_adjudication`, `echeance`, `type_ligne`.

**Une ligne par adjudication et par type.** Type `reelle` : chacune des 1 285 adjudications de D1 après filtres. Type
`placebo` : une ligne pour chacune des 321 réouvertures à 10, 20 et 30 ans. Attendu : 1 606 lignes.

| Colonne | Type | Unité, contenu |
|---|---|---|
| `id_ligne` | texte | `<cusip>_<date_adjudication>_<type_ligne>`, unique |
| `type_ligne` | texte | `reelle` ou `placebo` |
| `cusip` | texte | 9 caractères, champ `cusip` de D1 |
| `terme_api` | texte | `security_term` de D1, recopié |
| `echeance` | entier | 2, 3, 5, 7, 10, 20 ou 30 (ans) |
| `reouverture` | entier | 1 si `terme_api` est l'une des six valeurs « x-Year y-Month » du tableau D1, sinon 0 |
| `principal` | entier | 1 si `reouverture` = 1 et `echeance` ∈ {10, 20, 30}, sinon 0 |
| `date_adjudication` | date AAAA-MM-JJ | `auction_date` de D1 (pour un placebo : celle de l'adjudication dont il dérive) |
| `mois` | texte AAAA-MM | sept premiers caractères de `date_adjudication` |
| `montant_offert_mds` | décimal | `offering_amt` / 10⁹, milliards de dollars |
| `date_j` | date | `reelle` : `date_adjudication`. `placebo` : `date_adjudication` + 10 dans C |
| `date_jm5` | date | `date_j` − 5 dans C |
| `date_jp5` | date | `date_j` + 5 dans C |
| `cmt_jm5`, `cmt_j`, `cmt_jp5` | décimal | pour cent ; série DGS de l'`echeance` aux trois dates, recopiée sans arrondi |
| `gsw_jm5`, `gsw_j`, `gsw_jp5` | décimal | pour cent ; colonne SVENPY de l'`echeance` aux trois dates, recopiée sans arrondi |
| `complet` | entier | 1 si les six rendements sont présents, sinon 0 |
| `fenetre_propre` | entier | 1 si aucune **autre** adjudication `reelle` de même `echeance` n'a sa `date_adjudication` dans [`date_jm5`, `date_jp5`], sinon 0 |

**Contrôles de schéma** (le vérificateur les exécute et rapporte `schema_ok` = 1 si tous passent, 0 sinon) :
1. Les 21 colonnes ci-dessus, dans cet ordre, et aucune autre.
2. `id_ligne` unique ; `type_ligne`, `echeance`, `reouverture`, `principal`, `complet`, `fenetre_propre` dans leurs valeurs permises.
3. `date_jm5` < `date_j` < `date_jp5`. Pour `reelle` : `date_j` = `date_adjudication`. Pour `placebo` : `date_j` > `date_adjudication`.
4. `date_adjudication` entre 2010-01-01 et 2026-09-30 ; `mois` = ses sept premiers caractères ; `montant_offert_mds` > 0.
5. `principal` = 1 si et seulement si `reouverture` = 1 et `echeance` ∈ {10, 20, 30}. Toute ligne `placebo` a `principal` = 1 et
   partage `cusip` et `date_adjudication` avec exactement une ligne `reelle`.
6. `complet` = 1 si et seulement si les six rendements sont non vides.
7. Tout rendement non vide est entre −1 et 20 ; pour chaque date, |cmt − gsw| ≤ 1 (garde contre une colonne mal appariée).
8. Le nombre de lignes `reelle` avec `principal` = 1 est entre 300 et 330.

## 6. Statistique

**Mesure.** Pour une ligne i et une date x ∈ {J − 5, J, J + 5} : E_i(x) = `cmt_x` − `gsw_x`, en points de pourcentage.

V_i = 100 × [ (E_i(J) − E_i(J − 5)) − (E_i(J + 5) − E_i(J)) ] = 100 × [ 2·E_i(J) − E_i(J − 5) − E_i(J + 5) ], en points de base.

V_i > 0 : l'écart monte avant l'adjudication et redescend après. Le rendement en J est relevé vers 15 h 30, après la clôture
de l'adjudication à 13 h : une partie du retour a déjà eu lieu, ce qui joue contre l'hypothèse.

**Échantillon principal P.** Lignes avec `type_ligne` = `reelle`, `principal` = 1, `complet` = 1, `fenetre_propre` = 1.
N = nombre de lignes de P (`n_adjudications`). G = nombre de valeurs distinctes de `mois` dans P (`n_grappes`).

**Statistique principale (une seule).** La moyenne simple, avec erreur type groupée par mois :

- `v_moyen_pb` : V̄ = (1/N) Σ_i V_i.
- Pour chaque mois g : S_g = Σ_{i dans g} (V_i − V̄).
- `erreur_type_pb` : ET = (1/N) × racine( G/(G − 1) × Σ_g S_g² ). Aucun autre facteur de correction.
- `t_stat` : t = V̄ / ET.
- `borne_sup_95_pb` : B = V̄ + 1,96 × ET.
- `marge_zone_grise` : M = min( 2 − t , B − 0,5 ). M > 0 veut dire : t < 2 et pourtant l'effet prédit de 0,5 pb n'est pas exclu.

Pas de bootstrap, pas de tirage aléatoire : le calcul est déterministe.

**Garde de validité (placebo).** Mêmes formules sur les lignes `type_ligne` = `placebo`, `complet` = 1, `fenetre_propre` = 1,
groupées par `mois`. `n_placebo` = nombre de lignes ; `t_placebo_abs` = |V̄_placebo / ET_placebo|. Si `t_placebo_abs` ≥ 2, la
statistique s'écarte de zéro là où il n'y a pas d'adjudication : le plan est invalide et le test non concluant. Cette garde se
déclenche à tort dans environ 5 % des cas.

**Analyses secondaires, descriptives, sans effet sur le verdict.**
- **S1. Hors échantillon strict, rendement brut.** Lignes `reelle`, toutes échéances, `date_adjudication` ≥ 2024-08-01, trois
  valeurs `gsw` présentes (attendu : 182 lignes, 26 mois). V brut_i = 100 × [2·`gsw_j` − `gsw_jm5` − `gsw_jp5`]. Moyenne et
  erreur type groupée par mois, mêmes formules ; moyenne par échéance sans erreur type. À lire à côté des 1,2 pb et 2,6 pb
  publiés, avec l'erreur type attendue d'environ 2 pb. La courbe des titres anciens ne porte pas de saut de titre.
- **S2. Taille.** Sur P : r_i = `montant_offert_mds`_i divisé par la moyenne de `montant_offert_mds` des lignes `reelle` de même
  `echeance` dont la `date_adjudication` est dans les 1 096 jours civils strictement avant celle de i (au moins 12 lignes, sinon
  r_i manquant). z_i = (r_i − moyenne) / écart-type (dénominateur n − 1), sur les lignes où r_i existe. MCO de V_i sur z_i et
  trois indicatrices d'échéance, sans constante. Rapporter la pente et son erreur type groupée par mois (formule sandwich,
  facteur G/(G − 1) seul).
- **S3. Sous-périodes.** V̄, ET, N et G de la statistique principale sur 2010-01-01 à 2014-12-31 (attendu : 80 lignes, 40 mois),
  2015-01-01 à 2024-07-31 (190 ; 77) et 2024-08-01 à 2026-09-30 (51 ; 17).

L'expérimentateur rapporte aussi l'écart-type de V_i sur P, pour le comparer à l'hypothèse de la section suivante.

## 7. Arithmétique de puissance

Aucune donnée de rendement n'a été lue : l'écart-type de V est une supposition, déclarée comme telle.

- **Observations.** 321 réouvertures dans 134 mois. Les deux ou trois réouvertures d'un mois (10 et 30 ans la même semaine,
  20 ans la suivante) partagent la même courbe ajustée. Nombre d'observations effectivement indépendantes : entre 134 et 321.
- **Bruit de V.** Trois sources : l'arrondi de FRED au point de base (environ 0,7 pb sur V) ; l'écart d'heure de relevé entre
  les deux sources ; l'erreur d'ajustement de la courbe. Supposition : écart-type de V entre 2 et 5 pb, 3 pb au centre.
- **Erreur type attendue.** Favorable : 2/√321 = 0,11 pb. Centrale : 3/√200 = 0,21 pb. Défavorable : 5/√134 = 0,43 pb.

Probabilité de chaque verdict (loi normale, garde placebo mise à part) :

| Cas | Vrai effet | survit | éliminée | non concluant |
|---|---|---|---|---|
| Favorable (ET 0,11) | 0 | 2 % | 98 % | 0 % |
| Favorable | 0,5 pb | 99 % | 1 % | 0 % |
| Central (ET 0,21) | 0 | 2 % | 66 % | 32 % |
| Central | 0,5 pb | 64 % | 2,5 % | 33 % |
| Central | 1,0 pb | 99,7 % | < 0,1 % | 0,3 % |
| Défavorable (ET 0,43) | 0 | 2 % | 21 % | 77 % |
| Défavorable | 0,5 pb | 20 % | 2,5 % | 78 % |
| Défavorable | 1,0 pb | 62 % | 0,1 % | 38 % |

Lecture. Si le bruit est de 3 pb ou moins, le test élimine une hypothèse fausse environ deux fois sur trois ou plus, et laisse
survivre une hypothèse vraie environ deux fois sur trois à la borne basse, presque toujours au milieu de la fourchette. Dans
tous les cas, un verdict à tort (survie d'un effet nul, élimination d'un effet de 0,5 pb) ne dépasse pas 2,5 %. Si le bruit atteint 5 pb, le test
est faible pour la moitié basse de la prédiction et rend le plus souvent « non concluant » : c'est le prix de A4.

Pour S1 (rendement brut, 26 mois) : variation quotidienne d'environ 6 pb, donc écart-type de V d'environ 6 × √10 ≈ 19 pb ;
deux à trois fenêtres indépendantes par mois ; erreur type d'environ 19/√(2,5 × 26) ≈ 2,4 pb. Sans puissance contre 1 à 3 pb.

Coût de calcul : trois téléchargements (environ 20 Mo) et quelques milliers de lignes ; moins d'une minute sur un portable.

## 8. Règle de verdict

Le verdict s'applique aux nombres du vérificateur. On regarde d'abord « non concluant », puis « survit » ; la règle est écrite
pour que l'ordre d'évaluation ne change pas le résultat.

**Non concluant** si l'une de ces conditions tient :
- `schema_ok` < 1 ;
- `n_adjudications` < 290, ou `n_grappes` < 120, ou `n_placebo` < 250 ;
- `t_placebo_abs` ≥ 2 ;
- `marge_zone_grise` > 0, c'est-à-dire t < 2 alors que la borne haute à 95 % dépasse 0,5 pb ;
- (protocole) une donnée nommée manque, ou l'expérimentateur et le vérificateur diffèrent de plus que la tolérance.

**Survit** si toutes ces conditions tiennent : `v_moyen_pb` > 0 ; `t_stat` ≥ 2 ; `t_placebo_abs` < 2 ; `schema_ok` ≥ 1 ;
`n_adjudications` ≥ 290 ; `n_grappes` ≥ 120 ; `n_placebo` ≥ 250.

**Éliminée** sinon : échantillon et placebo valides, t < 2 et borne haute à 95 % ≤ 0,5 pb. La pression locale prédite est
alors exclue par les données.

La survie porte sur le signe. La taille est jugée dans la phrase de conclusion, qui doit dire si l'intervalle à 95 % recoupe la
fourchette prédite.

Tolérances entre expérimentateur et vérificateur : 0,005 pb sur la moyenne et l'erreur type, 0,01 pb sur la borne haute,
0,02 sur les rapports t et la marge, 0 sur les comptes et sur `schema_ok`. Les analyses S1 à S3 peuvent figurer dans
`verification.json` sous une clé `descriptif` ; elles ne sont ni comparées ni lues par le verdict.

## 9. Limites connues

1. **L'écart à la courbe ne mesure qu'une partie de la pression.** Si tous les titres voisins décotent ensemble, la courbe
   ajustée monte avec eux et l'écart ne bouge pas. « Éliminée » veut dire : pas de pression propre au titre adjugé, pas :
   pas de pression.
2. **Le verdict ne couvre que 10, 20 et 30 ans, et que les réouvertures.** Pour 2, 3, 5 et 7 ans, chaque adjudication change
   le titre de référence ; aucune donnée publique quotidienne ne sépare alors la pression du saut.
3. **Interpolation.** Le rendement à 10 ans exact est lu sur une courbe interpolée entre le titre courant (9 ans et 10 ou
   11 mois) et le suivant. Le changement d'un titre voisin dans la fenêtre peut déplacer ce point ; par raisonnement, de
   quelques centièmes de point de base, non vérifié. Avant décembre 2021 la méthode du Trésor était différente et moins
   documentée.
4. **Le placebo** contrôle une moyenne non nulle hors adjudication, pas un effet lié à la position dans le mois.
5. **L'écart-type de V est supposé**, pas mesuré : la puissance réelle n'est connue qu'après le test.

## 10. Ce qu'on écrira dans chaque cas

- **Survit.** « Autour des réouvertures de titres du Trésor à 10, 20 et 30 ans de 2010 à 2026, où le titre de référence ne
  change pas, l'écart entre le rendement à échéance constante et la courbe des titres anciens monte puis redescend de X pb
  (erreur type Y pb ; l'intervalle à 95 % recoupe / ne recoupe pas la fourchette prédite de 0,5 à 1,5 pb) : une pression propre
  au titre adjugé survit à ce test, qui ne dit rien des échéances de 2 à 7 ans ni de l'effet de taille. »
- **Éliminée.** « Autour des mêmes réouvertures, cet écart ne dessine pas de V inversé (X pb, borne haute à 95 % de Y pb, sous
  les 0,5 pb prédits) : la pression propre au titre adjugé prédite par la fiche est éliminée, sans contredire la pression sur
  le niveau des rendements publiée par Fleming, Liu et Nguyen, que cet écart retranche par construction. »
- **Non concluant.** « Le test ne tranche pas, pour la raison suivante : [échantillon sous le minimum / placebo différent de
  zéro / schéma violé / estimation trop imprécise pour exclure 0,5 pb / désaccord entre expérimentateur et vérificateur] ; on
  ne conclut ni à l'existence ni à l'absence de l'effet. »

## 11. Règle lisible par machine

```json
{
  "id": "F04",
  "fichier_analyse": "F04_analyse.csv",
  "champs_verification": [
    "schema_ok",
    "n_adjudications",
    "n_grappes",
    "v_moyen_pb",
    "erreur_type_pb",
    "t_stat",
    "borne_sup_95_pb",
    "marge_zone_grise",
    "n_placebo",
    "t_placebo_abs"
  ],
  "survit_si": [
    {"champ": "v_moyen_pb", "operateur": ">", "seuil": 0},
    {"champ": "t_stat", "operateur": ">=", "seuil": 2},
    {"champ": "t_placebo_abs", "operateur": "<", "seuil": 2},
    {"champ": "schema_ok", "operateur": ">=", "seuil": 1},
    {"champ": "n_adjudications", "operateur": ">=", "seuil": 290},
    {"champ": "n_grappes", "operateur": ">=", "seuil": 120},
    {"champ": "n_placebo", "operateur": ">=", "seuil": 250}
  ],
  "non_concluant_si": [
    {"champ": "schema_ok", "operateur": "<", "seuil": 1},
    {"champ": "n_adjudications", "operateur": "<", "seuil": 290},
    {"champ": "n_grappes", "operateur": "<", "seuil": 120},
    {"champ": "n_placebo", "operateur": "<", "seuil": 250},
    {"champ": "t_placebo_abs", "operateur": ">=", "seuil": 2},
    {"champ": "marge_zone_grise", "operateur": ">", "seuil": 0}
  ],
  "tolerance": {
    "schema_ok": 0,
    "n_adjudications": 0,
    "n_grappes": 0,
    "n_placebo": 0,
    "v_moyen_pb": 0.005,
    "erreur_type_pb": 0.005,
    "t_stat": 0.02,
    "borne_sup_95_pb": 0.01,
    "marge_zone_grise": 0.02,
    "t_placebo_abs": 0.02
  }
}
```
