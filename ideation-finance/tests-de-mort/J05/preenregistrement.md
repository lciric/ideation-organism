# J05 — Préinscription du test de mort : la concession d'adjudication, mesurée sans courbe du Trésor, a-t-elle baissé après 2021 ?

Rédigé le 2026-11-12 par le rédacteur de préinscription. Le rédacteur n'a lancé aucune analyse : aucun rendement GSW, aucune
concession, aucune moyenne n'a été calculé. Ce qu'il a vu des données est listé à la fin de la section 4. Ce texte est figé
une fois scellé (sha256) ; toute déviation ira dans `tests-de-mort/J05/ecarts.md`.

## 1. D'où vient la question

- **Parent (F04, scellé, « survit »).** Autour de 321 réouvertures des titres à 10, 20 et 30 ans (2010-01 à 2026-09),
  V = 2·E(J) − E(J−5) − E(J+5), avec E = taux à échéance constante du Trésor (FRED `DGS`) moins rendement au pair de la
  courbe GSW de la Fed. Moyenne 0,906 pb, erreur type 0,161 pb (groupée par mois, 134 mois), t = 5,6.
- **Découpes faites après ce verdict (exploratoires).** V vaut 1,0 à 2,2 pb par an de 2011 à 2021, puis 0,30 ; −0,03 ;
  0,23 ; −0,54 ; 0,39 de 2022 à 2026. Écart-type de V : 2,57 pb.
- **F04-bis (« non concluant »).** Sur les 23 réouvertures de l'exercice 2021, passer de l'ancienne méthode de courbe du
  Trésor (HS) à la nouvelle (MC, en service le 6 décembre 2021) fait baisser V de D = 0,78 pb, IC à 95 % [0,45 ; 1,12].
  La méthode explique donc une partie de la cassure, peut-être pas tout.
- **Question restée ouverte.** La pression a-t-elle disparu après 2021 **sur le marché**, ou seulement **dans la courbe du
  Trésor** dont la méthode a changé ? Pour répondre, il faut une mesure de la pression qui ne passe pas du tout par la
  courbe du Trésor. C'est ce que fait J05 : le rendement auquel le Trésor a réellement vendu le titre (rendement limite de
  l'adjudication, `high_yield`) comparé au rendement du même titre évalué sur la courbe GSW des titres anciens.

## 2. Question, hypothèses rivales et prédiction chiffrée

**Question.** Aux réouvertures des titres nominaux à 10, 20 et 30 ans, la concession d'adjudication mesurée sans aucune
courbe du Trésor est-elle plus faible en 2022-2026 qu'en 2010-2021 ?

**La mesure (définie exactement en section 6).** Pour chaque réouverture i :

K_i = 100 × { [ rendement limite_i − g_i(J) ] − [ f_i(J−5) − g_i(J−5) ] }, en points de base,

où g_i(x) est le rendement du titre i évalué sur la courbe GSW du jour x, et f_i(x) le rendement du titre i tiré de son prix
de marché de fin de journée du jour x (prix FedInvest, section 4). Lecture équivalente, plus parlante :
K_i = [hausse du rendement du titre entre J−5 et l'adjudication] − [hausse de la courbe des titres anciens, aux mêmes flux,
entre J−5 et J]. Le titre est comparé à lui-même une semaine plus tôt : sa prime de titre courant s'annule (section 3, A1).

**Statistique.** Δ = baisse moyenne de K entre 2010-2021 et 2022-2026, à échéance égale (Δ > 0 : la concession a baissé).

**Hypothèse de la fiche, mise à mort ici.** « La disparition de la pression après 2021 est un phénomène de marché » : Δ est
positif et de la taille qu'implique la cassure du parent. « Survit » veut dire que cette hypothèse tient ; « éliminée »
qu'elle tombe.

**Trois lectures et ce que chacune prédit pour Δ** (écrit sans avoir vu une seule valeur de K) :

| Lecture | Ce qu'elle dit | Δ prédit |
|---|---|---|
| **Marché** | La pression a disparu sur le marché ; la courbe du Trésor l'a seulement enregistré | **+0,9 pb** (0,66 à 1,15) |
| **Mesure** | La pression existe toujours ; c'est la nouvelle méthode du Trésor qui l'efface de V | **0** (−0,3 à +0,3) |
| **Mixte** | Le changement de méthode explique une partie, comme le suggère F04-bis | +0,3 pb (0,1 à 0,9) |

**D'où viennent ces chiffres.**
- La cassure du parent, sur la même fenêtre que ce test : V moyen 2010-2021 ≈ 1,38 pb, V moyen 2022-2026 ≈ 0,05 pb (calcul :
  la moyenne globale 0,906 sur 321 réouvertures, moins les cinq moyennes annuelles 2022-2026 pondérées par 24, 24, 24, 24 et
  18 réouvertures). Cassure ≈ 1,32 pb sur V.
- K ne mesure que la **montée** entre J−5 et l'adjudication, pas la redescente qui suit. V = montée + redescente. Si les deux
  moitiés sont égales (forme en V inversé décrite par Lou, Yan et Zhang 2013 et Fleming, Liu et Nguyen 2026), la montée
  porte la moitié de la cassure : 0,66 pb. C'est le bas de la fourchette « marché ».
- K contient en plus, entre 13 h et la clôture, une partie de la détente qui suit l'adjudication, et la décote propre à
  l'adjudication (0,1 à 0,7 pb selon Goldreich 2007 et la note 8 de Fleming, Liu et Nguyen). Si la pression disparaît, ces
  morceaux baissent aussi, de 0 à 0,5 pb. D'où le haut de la fourchette, 1,15 pb, et le centre, 0,9 pb.
- « Mixte » : si le changement de méthode retire de V entre 0,45 et 1,12 pb (F04-bis), la part « marché » de la cassure de
  1,32 pb est de 0,20 à 0,87 pb sur V, soit 0,10 à 0,44 pb sur la montée, plus 0 à 0,5 pb d'après-midi et de décote.

**Avis du rédacteur, sans effet sur la règle.** F04-bis rend « mixte » la lecture la plus plausible. Dans ce cas, avec la
dispersion attendue (section 7), le verdict le plus probable est « non concluant ».

## 3. Amendements déclarés

| N° | Test de la fiche | Test préinscrit | Raison |
|---|---|---|---|
| A1 | Concession en **niveau** C = 100·(rendement limite − g(J)) | **K** = C moins l'écart du **même titre** à la courbe GSW à J−5, mesuré sur son prix de marché (FedInvest) | Faille des quatre juges et de la note de nouveauté. Le titre rouvert est le titre courant ; GSW exclut les deux titres les plus récents de chaque échéance. C contient donc la prime du titre courant (−7 à −14 pb à 10 ans selon TBAC 2021, variable de plusieurs pb d'une année à l'autre). Cette prime suit la « spécialité » en repo, bornée par le niveau des taux, passés de près de zéro (2020-2021) à 4-5 % (2022-2026) : elle a pu se creuser après 2021 et faire baisser C sans aucun changement de pression, c'est-à-dire produire un faux « survit ». Les effets fixes d'échéance ne la retirent pas, puisqu'elle varie dans le temps. Dans K, la prime figure deux fois avec des signes opposés et s'annule, quel que soit son niveau dans chaque période. C'est le contrôle « variation de la concession de J−5 à J plutôt que niveau ». J−5 et non J−10 : c'est la date de départ du V du parent, et elle précède l'annonce de la réouverture (le jeudi précédent, vers J−4). |
| A2 | Avant = 1991-2021 | Avant = **2010-2021** pour le verdict ; 1991-2021 garde sa place en analyse secondaire S1 | (a) Les prix FedInvest, nécessaires à A1, n'existent qu'à partir de 2008 (section 4). (b) La cassure du parent est mesurée contre 2010-2021. (c) De 1991 à 2009, la pression était plus forte (Fleming, Liu et Nguyen : baisse après 2014) ; inclure ces années mélangerait une baisse lente sur trente ans avec une rupture en 2021 et pousserait vers « survit ». |
| A3 | Δ prédit = +1,2 pb (0,9 à 1,5) | Δ prédit = **+0,9 pb (0,66 à 1,15)** sous « marché », 0 sous « mesure » | Le chiffre de la fiche n'était pas dérivé. Celui-ci part de la cassure mesurée du parent et du fait que K ne porte que la montée (section 2). |
| A4 | Éliminée si la borne haute de l'IC à 90 % est < 1,0 pb ; aucune règle de survie écrite | **Deux tests unilatéraux à 5 %** : survit si la borne basse de l'IC à 90 % est > 0 (et la borne haute ≥ 0,5) ; éliminée si la borne haute est < 0,5 pb ; non concluant sinon | Sans règle de survie, la fiche « survivait » dès qu'elle n'était pas éliminée, même si Δ = 0. Un seuil d'élimination à 1,0 pb éliminerait l'hypothèse « marché » alors qu'elle prédit 0,66 pb au bas de sa fourchette. Justification des seuils en section 8. |
| A5 | « Au moins 400 réouvertures avant 2022 et 100 après » | 207 réouvertures en 2010-2021 (96 mois), 116 en 2022-2026 (39 mois) | Note de nouveauté et comptage du rédacteur sur les métadonnées de l'API (section 4). |
| A6 | API `v2`, champ `interest_rate`, adresse GSW `/pubs/feds/2006/200628/...`, colonnes `SVENY01`–`SVENY30` | API `v1`, champ `int_rate`, adresse `/data/yield-curve-tables/feds200628.csv`, paramètres `BETA0`–`BETA3`, `TAU1`, `TAU2` | Corrections de la note de nouveauté (404 et 400 sur les adresses et champs de la fiche ; `SVENY` ne donne que les échéances entières, il faut les paramètres pour actualiser des flux à dates quelconques). |
| A7 | Flux « à la date de règlement », convention de rendement non écrite | Prix **à terme** pour règlement à `issue_date`, conventions écrites (section 5) | `high_yield` est un rendement pour règlement à `issue_date`, 1 à 15 jours après l'adjudication. Un rendement « au comptant » diffère du rendement à terme d'environ (pente de la courbe) × (délai) / (durée), jusqu'à environ 1 pb ; la pente a changé de signe en 2023-2024. Ne pas corriger biaiserait Δ d'une quantité de la taille de l'effet cherché. |
| A8 | Rien sur l'heure | Courbe GSW **du jour J** (clôture), sans correction ; traitement déclaré ci-dessous | Faille des juges : `high_yield` est fixé à 13 h, la courbe GSW et FedInvest sont des fins de journée. Aucune courbe publique n'existe à 13 h. La clôture de la veille ajouterait la nuit et la matinée de J (statistiques de 8 h 30), donc plus de bruit. |
| A9 | Un second agent « réimplémente le rendement GSW » | Le fichier d'analyse contient toutes les entrées brutes (prix, paramètres GSW, coupon, dates) ; le vérificateur recalcule chaque rendement avec son propre code | Rend la vérification indépendante de l'implémentation de l'expérimentateur, avec un écart maximal préinscrit. |
| A10 | Réplication secondaire 10 et 30 ans | Non retenue ; trois analyses secondaires descriptives (section 6) | Les effets fixes d'échéance traitent la composition, et K retire déjà le niveau propre à chaque titre (y compris la cherté particulière du 20 ans). |

**Traitement de l'heure (A8), en détail.** K se décompose exactement en trois morceaux :
K = [rendement limite − rendement du titre sur le marché à 13 h] (décote d'adjudication)
  + [rendement du titre à 13 h − à la clôture de J] (après-midi)
  + [écart du titre à la courbe à la clôture de J − même écart à J−5] (montée de la pression).
- *Sur le niveau de K.* L'après-midi ajoute en moyenne la détente qui suit l'adjudication (positive si les rendements
  redescendent après 13 h), plus une dérive moyenne de l'après-midi, à peu près nulle hors tendance.
- *Sur la différence avant/après.* Deux choses peuvent changer. (1) La détente d'après 13 h : c'est un comportement du
  marché, compté du côté « marché » dans la prédiction. (2) La dérive moyenne de l'après-midi, qui n'est pas nulle en
  période de forte tendance : en 2022, le 10 ans a monté d'environ 240 pb, soit environ 1 pb par jour ouvré, dont environ
  0,3 pb l'après-midi ; cela abaisse K en 2022 d'environ 0,3 pb, donc la moyenne 2022-2026 d'environ 0,3 × 24/116 ≈ 0,06 pb.
  Biais d'environ +0,06 pb sur Δ, en faveur de « survit » ; négligeable devant les seuils. Les autres années n'ont pas de
  tendance comparable.
- *Sur le bruit.* Le mouvement de l'après-midi a un écart-type de l'ordre de 2,5 pb (2010-2021) à 3,5-4 pb (2022-2026).
  C'est la première source de bruit de K ; elle est dans l'arithmétique de puissance (section 7).
- L'analyse secondaire S2 sépare la montée mesurée à la clôture (sans décalage d'heure) du reste (décote et après-midi).

Inchangés : la population (réouvertures nominales à taux fixe des titres à 10, 20 et 30 ans), la coupure au 1er janvier
2022, la régression sur une indicatrice « après » avec effets fixes d'échéance, les erreurs types groupées par mois,
l'intervalle à 90 %.

## 4. Données

Toutes publiques, sans compte. L'expérimentateur enregistre chaque fichier brut dans `tests-de-mort/J05/donnees/`, avec la
date de téléchargement et le sha256. Aucune source de remplacement n'est permise.

**D1. Adjudications (Fiscal Data, API v1).** Une seule requête, testée le 2026-11-12 (HTTP 200, 2 375 lignes, une page) :

```
https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?fields=cusip,auction_date,issue_date,maturity_date,dated_date,first_int_payment_date,first_int_period,security_type,security_term,reopening,inflation_index_security,floating_rate,closing_time_comp,auction_format,int_rate,high_yield,high_price,accrued_int_per1000&filter=auction_date:gte:1991-01-01,auction_date:lte:2026-10-31,security_type:in:(Note,Bond)&sort=auction_date&page%5Bsize%5D=10000
```

Valeur manquante : la chaîne `null`. Sélection : `reopening` = "Yes", `inflation_index_security` ≠ "Yes",
`floating_rate` ≠ "Yes", et `security_term` qui commence par « 9-Year » (échéance 10), « 19-Year » (20) ou « 29-Year » (30).
Comptes attendus (métadonnées, 2026-11-12) :

| Période | Dates d'adjudication | Réouvertures | Mois |
|---|---|---|---|
| `ancien` | 1991-01-01 à 2009-12-31 | 65 | — |
| `avant` | 2010-01-01 à 2021-12-31 | 207 (10 ans : 97 ; 20 ans : 14 ; 30 ans : 96) | 96 |
| `apres` | 2022-01-01 à 2026-10-31 | 117 (39 ; 39 ; 39), dont une sans `high_yield` (20 ans du 2026-10-21) | 39 |

Faits constatés sur ces 389 lignes : `first_int_period` = "Normal" partout ; toutes les échéances tombent le 15 du mois ;
`auction_format` = "Single-Price" partout sauf 13 lignes de 1992 à 1998 ("Multi-Price") ; `closing_time_comp` vaut
« 01:00 PM » sauf 5 lignes (11:00 ou 11:30) et 45 lignes anciennes vides ; `high_price` manque sur une seule ligne (la même
que `high_yield`) ; `accrued_int_per1000` ne manque sur aucune. Toute ligne future avec `first_int_period` ≠ "Normal" est
écartée et notée dans `ecarts.md`.

**D2. Courbe GSW (Réserve fédérale).** `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` (HTTP 200,
16,7 Mo selon la note de nouveauté ; en-tête relu le 2026-11-12). Neuf lignes de préambule, en-tête à la ligne 10.
Colonnes utilisées : `Date`, `BETA0`, `BETA1`, `BETA2`, `BETA3`, `TAU1`, `TAU2`. Valeur manquante : `NA`. Dernière date
attendue : 2026-11-06.

**D3. Prix de fin de journée par titre (FedInvest, Bureau of the Fiscal Service).** Ce sont des prix de marché de chaque
titre, publiés pour les placements des comptes fédéraux ; ils ne passent par aucune méthode de courbe, et le changement du
6 décembre 2021 ne les concerne pas. Procédure, testée le 2026-11-12, une date à la fois, client par défaut, pause d'une
seconde entre deux dates :
1. `GET https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate` : HTTP 200 ; garder le témoin de session et
   le champ caché `_csrf`.
2. `POST` à la même adresse, corps `priceDate=AAAA-MM-JJ&submit=Show+Prices&_csrf=<jeton>`, avec le témoin : HTTP 302.
3. `GET https://www.treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail` avec le témoin : HTTP 200, page HTML avec
   « Prices For: <mois jour, année> » et un tableau `CUSIP, SECURITY TYPE, RATE, MATURITY DATE, CALL DATE, BUY, SELL,
   END OF DAY`. (Suivre automatiquement la redirection de l'étape 2 avec `curl -L` a donné 403 ; l'export CSV a donné 403 :
   on lit le tableau HTML.)

Colonne utilisée : `END OF DAY` (prix pour 100 de nominal). Couverture constatée : tableau rempli le 2008-09-15 (226 titres),
2008-12-15, 2009-03-16, 2010-01-04, 2010-03-15, 2012-03-14, 2016-06-15, 2021-12-06 et 2026-11-06 (464 titres) ; tableau vide
le 1995-03-14, 2000-03-14, 2004-03-15, 2006-03-14 et 2008-03-14. D'où A2. **Prix pied de coupon (sans coupon couru)** : vérifié
sur trois obligations à fort coupon (7,5 %, 8,75 %, 9,125 %) de part et d'autre du coupon du 15 mai 2016 : `END OF DAY` a
varié de 0,00 à 0,09 entre le 13 et le 16 mai 2016, alors qu'un prix coupon couru inclus aurait chuté de 3,75 à 4,56. Ces
prix étaient des multiples de 1/32, soit un arrondi d'au plus 0,2 pb de rendement sur un 10 ans.

Dates à télécharger : J et J−5 de chaque réouverture `avant` et `apres` (environ 640 dates distinctes ; environ une
demi-heure de téléchargement, une seule fois). Une page dont la date affichée diffère de la date demandée est traitée comme
manquante.

**Calendrier.** C est la liste triée des dates du fichier D2 où les six paramètres sont présents. J = `auction_date` ; « J−5 »
est la date située 5 rangs avant J dans C.

**Ce qui compte comme manquant.**
- J absent de C, un des six paramètres GSW absent à J ou à J−5, `high_yield` ou `high_price` nul, page FedInvest vide ou
  absente à J−5, titre (CUSIP) absent du tableau, ou `END OF DAY` vide ou nul : K manquant (`complet_k` = 0), ligne hors de
  l'échantillon principal, comptée.
- Même règle pour le prix FedInvest à J, qui ne sert qu'à l'analyse S2 (`complet_r`).
- D1, D2 ou D3 injoignable, ou colonnes différentes : le fichier d'analyse n'est pas construit ; test non concluant. Si
  FedInvest refuse l'accès (403) de façon durable, l'expérimentateur ne cherche aucun contournement : non concluant pour
  raison de données.
- Échantillon sous les minimums de la section 8 : non concluant.

**Ce que le rédacteur a vu.**
- Les résultats du parent cités en section 1 (verdicts de F04 et F04-bis, contrôle de l'orchestrateur, moyennes annuelles
  du projet F04-bis). Ils ont servi à fixer la prédiction et les seuils : ce n'est pas un regard aveugle, c'est déclaré.
- D1 : la liste des champs ; les métadonnées des 389 réouvertures (dates, échéances, formats, heures de clôture, nombre de
  valeurs nulles, jour d'échéance, délai de règlement). En vérifiant les formats, une ligne s'est affichée : réouverture à
  30 ans du 2026-10-08, `high_yield` 5.6180, `high_price` 92.889131, `int_rate` 5.125. Aucun rendement GSW n'a été calculé
  pour elle ni pour aucune autre.
- D2 : la ligne d'en-tête.
- D3 : le nombre de lignes du tableau pour 16 dates ; les premières lignes (des bons à court terme) du 2010-03-15, du
  2016-06-15 et du 2026-11-06 ; les prix des trois vieilles obligations ci-dessus le 13 et le 16 mai 2016. Aucun prix d'un titre rouvert,
  à aucune date.
- Aucune moyenne, aucun écart, aucune statistique.

## 5. Fichier d'analyse

Nom : `tests-de-mort/J05/J05_analyse.csv`. UTF-8, virgule, point décimal, une ligne d'en-tête, champ vide pour une valeur
manquante, nombres écrits sans arrondi (au moins 10 chiffres significatifs). **Une ligne par réouverture** sélectionnée en D1
(389 attendues), triée par `date_adjudication` puis `echeance`. Pas de ligne placebo.

### 5.1 Colonnes

| N° | Colonne | Type | Unité, contenu |
|---|---|---|---|
| 1 | `id_ligne` | texte | `<cusip>_<date_adjudication>`, unique |
| 2 | `cusip` | texte | 9 caractères, `cusip` de D1 |
| 3 | `terme_api` | texte | `security_term` de D1, recopié |
| 4 | `echeance` | entier | 10, 20 ou 30 (ans), selon le préfixe de `terme_api` |
| 5 | `date_adjudication` | date AAAA-MM-JJ | `auction_date` (= J) |
| 6 | `mois` | texte AAAA-MM | sept premiers caractères de `date_adjudication` |
| 7 | `periode` | texte | `ancien`, `avant` ou `apres` selon le tableau de D1 |
| 8 | `heure_cloture` | texte | `closing_time_comp`, recopié (vide si `null`) |
| 9 | `format_adjudication` | texte | `auction_format`, recopié |
| 10 | `date_reglement` | date | `issue_date` (= s) |
| 11 | `date_echeance` | date | `maturity_date` |
| 12 | `taux_coupon_pct` | décimal | `int_rate`, pour cent par an |
| 13 | `rdt_limite_pct` | décimal | `high_yield`, pour cent |
| 14 | `prix_limite` | décimal | `high_price`, pour 100 |
| 15 | `coupon_couru_api` | décimal | `accrued_int_per1000` / 10, pour 100 |
| 16 | `coupon_couru_calc` | décimal | AI(s) calculé (section 5.2), pour 100 |
| 17 | `date_gsw_j` | date | date de la ligne D2 utilisée pour J |
| 18-23 | `beta0_j`, `beta1_j`, `beta2_j`, `beta3_j`, `tau1_j`, `tau2_j` | décimal | paramètres D2 de `date_gsw_j`, recopiés |
| 24 | `date_jm5` | date | J−5 dans C (vide pour `ancien`) |
| 25-30 | `beta0_jm5`, `beta1_jm5`, `beta2_jm5`, `beta3_jm5`, `tau1_jm5`, `tau2_jm5` | décimal | paramètres D2 de `date_jm5` (vides pour `ancien`) |
| 31 | `prix_fi_jm5` | décimal | `END OF DAY` du CUSIP à `date_jm5`, pour 100 (vide pour `ancien`) |
| 32 | `prix_fi_j` | décimal | `END OF DAY` du CUSIP à `date_adjudication`, pour 100 (vide pour `ancien`) |
| 33 | `rdt_prix_limite_pct` | décimal | Y(`prix_limite`, s), pour cent |
| 34 | `rdt_gsw_j_terme_pct` | décimal | g_terme(J), pour cent |
| 35 | `rdt_gsw_j_pct` | décimal | g(J) au comptant, pour cent (vide pour `ancien`) |
| 36 | `rdt_gsw_jm5_pct` | décimal | g(J−5), pour cent (vide pour `ancien`) |
| 37 | `rdt_fi_jm5_pct` | décimal | f(J−5), pour cent |
| 38 | `rdt_fi_j_pct` | décimal | f(J), pour cent |
| 39 | `c_pb` | décimal | 100 × (`rdt_limite_pct` − `rdt_gsw_j_terme_pct`) |
| 40 | `k_pb` | décimal | `c_pb` − 100 × (`rdt_fi_jm5_pct` − `rdt_gsw_jm5_pct`) |
| 41 | `r_fi_pb` | décimal | 100 × [(`rdt_fi_j_pct` − `rdt_gsw_j_pct`) − (`rdt_fi_jm5_pct` − `rdt_gsw_jm5_pct`)] |
| 42 | `convention_ok` | entier | 1 si \|`rdt_prix_limite_pct` − `rdt_limite_pct`\| ≤ 0,001 et \|`coupon_couru_calc` − `coupon_couru_api`\| ≤ 0,001 ; sinon 0 |
| 43 | `complet_k` | entier | 1 si les entrées de K sont toutes présentes (colonnes 13, 14, 18-23, 25-31) et `date_gsw_j` = `date_adjudication` ; sinon 0 |
| 44 | `complet_r` | entier | 1 si `complet_k` = 1 et `prix_fi_j` présent ; sinon 0 |
| 45 | `dans_p` | entier | 1 si `periode` ∈ {`avant`, `apres`}, `complet_k` = 1 et `convention_ok` = 1 ; sinon 0 |

Une valeur dérivée (colonnes 16, 33-41) est vide si l'une de ses entrées l'est.

### 5.2 Conventions de calcul (à appliquer à l'identique par l'expérimentateur et le vérificateur)

Notations : c = `taux_coupon_pct` ; M = `date_echeance` ; s = `date_reglement`. Toutes les durées en jours civils.

- **Dates de coupon.** T_k = M reculée de 6·k mois (k = 0, 1, 2, …), même jour du mois que M (le jour 15 dans tout
  l'échantillon ; si ce jour n'existe pas dans le mois, dernier jour du mois). Dates nominales, sans report au jour ouvré.
- **Flux après une date de règlement d.** c/2 à chaque T_k strictement postérieur à d, plus 100 à M. Un coupon qui tombe
  le jour d n'est pas reçu.
- **Coupon couru.** L(d) = dernier T_k ≤ d ; N(d) = premier T_k > d. AI(d) = (c/2) × (d − L) / (N − L).
- **Rendement d'un prix pied de coupon P pour règlement d**, Y(P, d) (31 CFR partie 356, annexe B, titre ayant plus d'un
  coupon restant) : y, en pour cent, est l'unique solution de
  P + AI(d) = Σ_{j=1..n} F_j × (1 + y/200)^−[(j − 1) + (N − d)/(N − L)],
  où n est le nombre de T_k > d et F_j = c/2 pour j < n, c/2 + 100 pour j = n. Résolution numérique à 10⁻⁹ point de
  pourcentage près.
- **Courbe GSW du jour x.** Pour m > 0 (années) :
  z_x(m) = β0 + β1·(1 − e^(−m/τ1))/(m/τ1) + β2·[(1 − e^(−m/τ1))/(m/τ1) − e^(−m/τ1)] + β3·[(1 − e^(−m/τ2))/(m/τ2) − e^(−m/τ2)],
  en pour cent, composition continue ; facteur d'actualisation D_x(m) = exp(−z_x(m)·m/100), avec m = (date − x)/365,25.
  (La note de nouveauté a vérifié que cette formule redonne `SVENY01`, `SVENY10` et `SVENY30` à 10⁻⁶ près.)
- **g_terme(J)** (colonne 34), pour comparer à `high_yield` qui est un rendement pour règlement à s :
  prix plein à terme = Σ flux après s × D_J(m_flux) / D_J(m_s) ; P = prix plein − AI(s) ; g_terme(J) = Y(P, s).
  (s est toujours postérieur à J dans l'échantillon : délai de 1 à 15 jours.)
- **g(x) au comptant** (colonnes 35, 36), pour x = J ou J−5 : prix plein = Σ flux après x × D_x(m_flux) ;
  P = prix plein − AI(x) ; g(x) = Y(P, x).
- **f(x)** (colonnes 37, 38) = Y(`END OF DAY` du jour x, x). Le prix FedInvest et la courbe GSW d'une même date x sont
  traités avec le même règlement x ; l'écart f(x) − g(x) ne dépend donc pas de la convention de règlement de FedInvest.
- `rdt_prix_limite_pct` (colonne 33) = Y(`prix_limite`, s). Il doit redonner `high_yield` : c'est le contrôle que la
  convention de rendement est bien celle du Trésor.

### 5.3 Contrôles de schéma

Le vérificateur les exécute et rapporte `schema_ok` = 1 si tous passent, 0 sinon.
1. Les 45 colonnes ci-dessus, dans cet ordre, et aucune autre.
2. `id_ligne` unique et égal à `<cusip>_<date_adjudication>` ; `cusip` de 9 caractères ; `echeance` = 10, 20 ou 30 selon
   que `terme_api` commence par « 9-Year », « 19-Year » ou « 29-Year » ; `mois` = sept premiers caractères de
   `date_adjudication` ; `periode` conforme aux dates du tableau D1 ; colonnes 42 à 45 dans {0, 1}.
3. `date_adjudication` entre 1991-01-01 et 2026-10-31 ; nombre de lignes par période : `ancien` entre 60 et 70, `avant`
   entre 200 et 214, `apres` entre 112 et 120.
4. `date_reglement` postérieure à `date_adjudication` d'au plus 20 jours ; `date_echeance` postérieure à `date_reglement`.
5. **Pas de regard vers l'avenir.** Tout paramètre GSW du fichier est daté `date_gsw_j` ou `date_jm5`, et ces deux dates
   sont **antérieures ou égales au jour de l'adjudication** : `date_gsw_j` = `date_adjudication` quand elle est remplie ;
   `date_jm5` < `date_adjudication`, avec un écart de 7 à 9 jours civils (cinq jours ouvrés, au plus deux fériés) et un jour
   du lundi au vendredi. Aucun prix FedInvest n'est postérieur à J.
6. Plages : rendements (colonnes 13, 33-38) entre −1 et 20 ; prix (14, 31, 32) entre 50 et 200 ; `tau1_*`, `tau2_*` > 0 ;
   `taux_coupon_pct` entre 0 et 15.
7. Garde contre un mauvais appariement de titre ou de colonne : \|`rdt_fi_jm5_pct` − `rdt_gsw_jm5_pct`\| ≤ 0,60 et
   \|`rdt_fi_j_pct` − `rdt_limite_pct`\| ≤ 0,40 (points de pourcentage) quand les deux sont présents.
8. Colonnes 39 à 41 égales à leur formule appliquée aux colonnes du fichier, à 10⁻⁶ pb près ; colonnes 42 à 45 conformes
   à leur définition appliquée aux colonnes du fichier.

## 6. Statistique

**Mesure.** K_i = `k_pb` (section 5). En mots : de combien le rendement du titre a monté entre J−5 et l'adjudication, au-delà
de ce qu'a monté la courbe des titres anciens aux mêmes flux, en points de base.

**Échantillon principal P.** Lignes avec `dans_p` = 1. N_avant, N_apres = nombre de lignes de P de chaque période
(`n_avant`, `n_apres`) ; G_avant, G_apres = nombre de mois distincts de chaque période dans P (`n_grappes_avant`,
`n_grappes_apres`) ; G = G_avant + G_apres.

**Recalcul par le vérificateur.** Le vérificateur recalcule, avec son propre code et les conventions de 5.2, les colonnes 16
et 33 à 38 de chaque ligne `avant` ou `apres` à partir des colonnes brutes du fichier, puis K. Il rapporte
`ecart_max_rdt_pb` = 100 × le plus grand écart absolu entre ses valeurs et celles des colonnes 33 à 38 du fichier.
L'expérimentateur rapporte le même champ en recalculant avec son propre code (attendu : 0). Les deux rapportent
`n_echec_convention` = nombre de lignes `avant` ou `apres` ayant `rdt_limite_pct` et `prix_limite` présents mais
`convention_ok` = 0 selon leur propre calcul. Chacun calcule la statistique avec ses propres rendements, sur l'échantillon P
défini par les colonnes du fichier.

**Statistique principale (une seule) : la baisse de K à échéance égale.** Moindres carrés ordinaires sur P :

K_i = b·apres_i + a10·d10_i + a20·d20_i + a30·d30_i + u_i, sans constante,

où apres_i = 1 si `periode` = `apres`, et d10, d20, d30 sont les indicatrices d'échéance.
- `delta_k_pb` : Δ̂ = −b̂ (Δ̂ > 0 : la concession a baissé après 2021).
- Erreur type groupée par mois : X = matrice N × 4 [apres, d10, d20, d30] ; û = résidus ; pour chaque mois g,
  s_g = X_gᵀ û_g ; V = G/(G − 1) × (XᵀX)⁻¹ (Σ_g s_g s_gᵀ) (XᵀX)⁻¹. `erreur_type_pb` = ET = racine de l'élément (1,1) de V.
  Aucun autre facteur de correction (en particulier pas de (N − 1)/(N − 4)).
- `borne_inf_90_pb` : L = Δ̂ − 1,645 × ET. `borne_sup_90_pb` : U = Δ̂ + 1,645 × ET. (1,645 exactement.)
- `marge_zone_grise` : Mz = min( −L , U − 0,5 ). Mz ≥ 0 veut dire : L ≤ 0 et U ≥ 0,5, c'est-à-dire que les données
  n'excluent ni « mesure » (Δ = 0) ni « marché » (Δ ≥ 0,5).
- Moyennes simples d'accompagnement : `k_moyen_avant_pb`, `k_moyen_apres_pb` (moyenne de K sur P dans chaque période).

Pourquoi un groupement par mois : les réouvertures à 10 et 30 ans ont lieu deux jours de suite et celle à 20 ans la semaine
suivante ; elles partagent la même courbe et les mêmes nouvelles. Pourquoi des effets fixes d'échéance : le 20 ans pèse
6,8 % de l'échantillon avant (14 sur 207) et 34 % après (39 sur 116). Pas de bootstrap, pas de tirage : le calcul est
déterministe.

**Analyses secondaires, descriptives, sans effet sur le verdict** (au plus trois ; dans `verification.json` sous la clé
`descriptif`, ni comparées ni lues par le verdict) :
- **S1. La concession en niveau de la fiche, sans contrôle de la prime.** Même régression avec `c_pb` à la place de `k_pb`,
  (a) sur les lignes `ancien`, `avant` et `apres` ayant `c_pb` présent et `convention_ok` = 1, « après » contre « ancien +
  avant » (la comparaison 1991-2021 contre 2022-2026 de la fiche) ; (b) sur P seulement. Rapporter Δ et ET. Sert à montrer
  ce que la comparaison en niveau aurait conclu, prime comprise.
- **S2. Montée à la clôture et reste.** Sur les lignes de P avec `complet_r` = 1 : même régression avec R = `r_fi_pb`
  (montée de l'écart du titre à la courbe entre J−5 et la clôture de J, sans décalage d'heure ; c'est la moitié « montée »
  du V du parent, mesurée sur le prix du titre au lieu de la courbe du Trésor) puis avec A = `k_pb` − `r_fi_pb` (décote
  d'adjudication et après-midi). Rapporter Δ et ET de chacune.
- **S3. La prime du titre courant.** Π = 100 × (`rdt_fi_jm5_pct` − `rdt_gsw_jm5_pct`) : moyenne par période et par
  échéance sur P (sans erreur type), et Δ_Π par la même régression. Mesure directement le déplacement de prime que redoutent
  les juges, donc le biais qu'aurait porté une comparaison en niveau.

L'expérimentateur et le vérificateur rapportent aussi, dans `descriptif`, l'écart-type de K sur P dans chaque période
(dénominateur n − 1), pour le comparer aux hypothèses de la section 7.

## 7. Arithmétique de puissance

Aucune valeur de K n'a été vue : sa dispersion est une supposition, déclarée comme telle.

**Sources de bruit de K, par ligne.**
- Mouvement du rendement du titre entre 13 h et la clôture (A8) : l'écart-type quotidien des rendements à 10 et 30 ans est de
  l'ordre de 5 à 6 pb en 2010-2021 et de 7 à 8 pb en 2022-2026 (ordre de grandeur connu, non calculé ici) ; l'après-midi en
  porte environ un quart à un tiers de la variance, d'où environ 2,5 pb avant et 3,5 à 4 pb après.
- Montée de l'écart du titre à la courbe entre J−5 et J : environ 1,8 pb (écart-type de V du parent, 2,57 pb, divisé par √2,
  puisque V est la somme d'une montée et d'une redescente).
- Décote d'adjudication : environ 0,8 pb.
- Arrondi des prix FedInvest au 1/32 : au plus 0,1 pb d'écart-type. Négligeable.

**Hypothèses.** Centrale : σ_avant = 3,2 pb, σ_apres = 4,2 pb, facteur de groupement 1,12 (celui observé dans le parent :
0,161 / (2,57/√321)). Favorable : 2,5 et 3,0 pb, facteur 1,0. Défavorable : 4,5 et 6,0 pb, facteur 1,3.

**Erreur type attendue.** ET ≈ facteur × racine(σ_avant²/207 + σ_apres²/116) :
favorable 0,33 pb ; centrale 0,50 pb ; défavorable 0,83 pb. Avec les hypothèses de la fiche (σ = 3,5 pb, facteur 1,12) et
les vrais comptes, 0,45 pb (la fiche annonçait 0,44 pb avec 400 et 100 réouvertures, comptes erronés). Les 116 réouvertures
d'après 2021, plus volatiles, pèsent les trois quarts de la variance de Δ̂ : c'est la contrainte.

**Probabilité de chaque verdict** (loi normale, règle de la section 8, gardes mises à part) :

| ET | Vrai Δ | survit | éliminée | non concluant |
|---|---|---|---|---|
| 0,33 (favorable) | 0 (« mesure ») | 5 % | 45 % | 50 % |
| 0,33 | 0,35 (« mixte ») | 28 % | 12 % | 60 % |
| 0,33 | 0,66 (bas de « marché ») | 64 % | 2 % | 34 % |
| 0,33 | 0,9 (« marché ») | 86 % | 0 % | 13 % |
| 0,50 (central) | 0 | 5 % | 26 % | 69 % |
| 0,50 | 0,35 | 17 % | 9 % | 74 % |
| 0,50 | 0,66 | 37 % | 2 % | 61 % |
| 0,50 | 0,9 | 56 % | 1 % | 44 % |
| 0,50 | 1,15 (haut de « marché ») | 74 % | 0 % | 26 % |
| 0,83 (défavorable) | 0 | 5 % | 15 % | 80 % |
| 0,83 | 0,9 | 29 % | 2 % | 70 % |

**Lecture, sans enjoliver.**
- Un verdict à tort est rare : « survit » quand la mesure explique tout (Δ = 0) arrive 5 % du temps ; « éliminée » quand la
  baisse est de la taille prédite par « marché » (0,66 pb ou plus), 2 % au plus.
- Le test est **plus apte à confirmer « marché » qu'à l'éliminer**. Dans le cas central, il confirme une baisse de 0,9 pb un
  peu plus d'une fois sur deux ; l'effet minimal détectable à 80 % contre Δ = 0 est 2,49 × 0,50 ≈ 1,25 pb. Si la mesure
  explique tout, il n'élimine la fiche qu'une fois sur quatre et rend « non concluant » sept fois sur dix.
- **Si la dispersion est plus grande que supposé** (cas défavorable, ET ≈ 0,83 pb), « non concluant » devient le verdict le
  plus probable dans tous les cas (70 à 80 %) ; les erreurs à tort restent sous 5 %. Le test ne devient pas trompeur, il
  devient muet. L'écart-type de K rapporté en `descriptif` dira, après coup, lequel des trois cas était le bon.
- Rien de raisonnable ne réduit le bruit principal : il vient du décalage 13 h / clôture, et aucune courbe publique n'existe
  à 13 h. L'analyse S2 (montée à la clôture, sans décalage) est moins bruitée mais ne mesure pas le prix d'adjudication.

Coût : environ 640 pages FedInvest (une demi-heure de téléchargement, une fois), deux fichiers de 1 et 17 Mo ; calcul de
quelques secondes sur un portable.

## 8. Règle de verdict

Le verdict s'applique aux nombres du vérificateur. La règle est écrite pour que l'ordre d'évaluation ne change rien.

**En mots.**
- **Survit** = l'hypothèse « marché » tient : la borne basse de l'IC à 90 % de Δ est au-dessus de 0 (la baisse est
  significative au seuil unilatéral de 5 %) et la borne haute n'exclut pas une baisse de 0,5 pb. Mesurée sans aucune courbe
  du Trésor, la concession a baissé après 2021, dans une proportion compatible avec la cassure du parent.
- **Éliminée** = la borne haute de l'IC à 90 % est sous 0,5 pb : la baisse prédite par « marché » est exclue au seuil
  unilatéral de 5 %. Si en même temps la borne basse est au-dessus de 0, la concession a baissé, mais moins que ne
  l'implique une disparition de marché (lecture « mixte ») : c'est aussi « éliminée », puisque l'hypothèse de la fiche est
  une baisse de cette taille.
- **Non concluant** = la borne basse est ≤ 0 et la borne haute ≥ 0,5 (les données n'excluent ni l'une ni l'autre lecture),
  ou une garde ci-dessous se déclenche.

**Non concluant** si l'une de ces conditions tient :
- `schema_ok` < 1 ;
- `n_avant` < 190, `n_apres` < 105, `n_grappes_avant` < 88 ou `n_grappes_apres` < 35 ;
- `n_echec_convention` > 5 ;
- `ecart_max_rdt_pb` > 0,05 ;
- `marge_zone_grise` ≥ 0 ;
- (protocole) une donnée nommée manque, ou l'expérimentateur et le vérificateur diffèrent de plus que la tolérance.

**Survit** si toutes ces conditions tiennent : `borne_inf_90_pb` > 0 ; `borne_sup_90_pb` ≥ 0,5 ; `schema_ok` ≥ 1 ;
`n_avant` ≥ 190 ; `n_apres` ≥ 105 ; `n_grappes_avant` ≥ 88 ; `n_grappes_apres` ≥ 35 ; `n_echec_convention` ≤ 5 ;
`ecart_max_rdt_pb` ≤ 0,05.

**Éliminée** sinon, c'est-à-dire : gardes passées et `borne_sup_90_pb` < 0,5.

**Justification de chaque seuil.**
- **0 (borne basse).** La lecture « mesure » prédit Δ = 0 : la pression existe toujours, seule la courbe du Trésor l'a
  effacée, et K ne passe pas par cette courbe. Survivre, c'est rejeter cette lecture.
- **0,5 pb (borne haute).** La plus petite baisse compatible avec « marché ». Si la montée porte la moitié de la cassure de V
  (1,32 pb), elle vaut 0,66 pb ; on descend à 0,5 pb pour laisser de la place à une montée un peu plus courte que la
  redescente (part de 38 % au lieu de 50 %), hypothèse que ce test ne peut pas vérifier. Le 1,0 pb de la fiche aurait
  éliminé « marché » alors que cette lecture prédit 0,66 pb au bas de sa fourchette.
- **90 % et 1,645.** Niveau de la fiche ; il revient à deux tests unilatéraux à 5 %, un contre chaque lecture. Avec 135
  mois, dont 39 après 2021, la loi normale suffit (la valeur de Student à 134 degrés de liberté, 1,656, changerait les
  bornes de 0,005 pb environ pour ET = 0,5).
- **190, 105, 88, 35.** Comptes attendus : 207 et 116 réouvertures, 96 et 39 mois. On tolère la perte d'environ 8 à 10 %
  des lignes (pages FedInvest manquantes, conventions en échec) et de quelques mois. Au-delà, la perte ne serait plus
  accidentelle (par exemple une année entière sans FedInvest) et l'arithmétique de puissance ne vaudrait plus.
- **5 échecs de convention.** Tolère quelques coquilles dans l'API. Au-delà, la formule de rendement n'est pas celle du
  Trésor, et K mélangerait deux conventions.
- **0,05 pb d'écart de recalcul.** Deux implémentations correctes des conventions de 5.2 doivent s'accorder à 10⁻⁴ pb près ;
  0,05 pb laisse une marge large, tout en restant dix fois sous le seuil de 0,5 pb.

**Tolérances entre expérimentateur et vérificateur.** 0 sur les comptes et sur `schema_ok` ; 0,005 pb sur les moyennes, Δ et
l'erreur type ; 0,01 pb sur les deux bornes et sur la marge ; 0,05 pb sur `ecart_max_rdt_pb` (l'expérimentateur rapporte 0
par construction ; le vérificateur rapporte son vrai écart).

## 9. Limites

1. **Le décalage 13 h / clôture** n'est pas corrigé, seulement déclaré (A8). Il ne biaise presque pas Δ (environ +0,06 pb à
   cause de la tendance de 2022) mais il domine le bruit : c'est lui qui rend « non concluant » probable.
2. **La moitié « montée » seulement.** Pour respecter la règle « aucune courbe datée après le jour de l'adjudication », K
   s'arrête à J. Sa prédiction suppose que la montée porte à peu près la moitié du V du parent. Si la pression se forme
   surtout après J−5 et se résorbe lentement, ou l'inverse, la traduction de la cassure en pb de K est fausse ; le seuil de
   0,5 pb n'en protège qu'en partie.
3. **La prime n'est neutralisée que dans son niveau.** Ce qui bouge entre J−5 et J pour une raison liée à la réouverture
   (la spécialité en repo du titre baisse quand l'offre augmente) reste dans K. C'est un effet de marché ; avec des taux à
   4-5 % il pourrait être plus fort après 2021, ce qui jouerait contre « survit ».
4. **FedInvest** ne documente ni sa source ni l'heure de sa « fin de journée ». Pour un titre courant, très liquide, passer
   d'un prix acheteur à un prix milieu change le rendement de moins de 0,1 pb ; un changement d'heure de relevé ajouterait
   du bruit, pas un biais systématique, sauf s'il avait lieu exactement fin 2021. L'accès demande un témoin de session ; un
   blocage durable rend le test non concluant.
5. **K n'est pas V.** « Éliminée » ne contredit pas le verdict de F04 et ne prouve pas que la méthode du Trésor fabriquait
   V ; elle dit que, sur les prix de marché et au prix d'adjudication, la baisse n'a pas la taille qu'impliquerait une
   disparition de marché. Il resterait trois lectures : la mesure, une différence entre ce que mesurent V et K (heure,
   montée seule), ou le hasard d'une coupure en 2021 choisie après avoir vu les moyennes annuelles du parent.
6. **« Survit » ne dit pas que la méthode n'a rien fait.** F04-bis montre qu'elle retire une partie de V en 2021 ; un
   « survit » dit seulement qu'une baisse se voit aussi sans elle.
7. **Données déjà en partie regardées.** La coupure, la prédiction et le seuil viennent de découpes exploratoires du parent.
   Les valeurs de K, elles, n'ont jamais été vues.
8. **Champ.** Réouvertures à 10, 20 et 30 ans seulement ; rien sur les nouvelles émissions ni sur les échéances de 2 à 7 ans.
   Le 20 ans n'a que 14 réouvertures avant 2022, toutes en 2020-2021.
9. **Moyenne sensible aux valeurs extrêmes.** Un après-midi exceptionnel (mars 2020, par exemple) pèse sur Δ̂ ; on garde la
   moyenne pour rester comparable au parent et défendable simplement.

## 10. Ce qu'on écrira dans chaque cas

- **Survit.** « Mesurée sans aucune courbe du Trésor — hausse du rendement du titre rouvert entre J−5 et le prix
  d'adjudication, au-delà de celle de la courbe GSW des titres anciens — la concession des réouvertures à 10, 20 et 30 ans
  baisse de X pb entre 2010-2021 et 2022-2026 (IC à 90 % : Y à Z pb, au-dessus de 0), donc la disparition de la pression
  après 2021 se voit aussi sur les prix de marché et n'est pas seulement un effet du changement de méthode de la courbe du
  Trésor, sans que ce test dise quelle part de la cassure de V revient malgré tout à la méthode. »
- **Éliminée.** « Mesurée de la même façon, la concession ne baisse que de X pb entre 2010-2021 et 2022-2026 (IC à 90 % : Y à
  Z pb, sous les 0,5 pb qu'implique une disparition de marché), donc la cassure du V du parent ne se retrouve pas à cette
  taille sur les prix de marché [si Y > 0 : la concession a baissé, mais moins qu'une disparition de marché ne l'exige,
  ce qui va dans le sens d'une explication en partie par la mesure], sans que ce test sépare la méthode du Trésor d'une
  différence entre ce que mesurent V et cette concession. »
- **Non concluant.** « Le test ne tranche pas, pour la raison suivante : [IC à 90 % de Y à Z pb, qui contient à la fois 0 et
  0,5 pb / échantillon sous le minimum / prix FedInvest inaccessibles / conventions de rendement en échec / schéma violé /
  désaccord entre expérimentateur et vérificateur] ; on ne conclut ni que la pression a disparu sur le marché, ni qu'elle n'a
  disparu que dans la courbe du Trésor. »

## 11. Règle lisible par machine

```json
{
  "id": "J05",
  "fichier_analyse": "J05_analyse.csv",
  "champs_verification": [
    "schema_ok",
    "n_avant",
    "n_apres",
    "n_grappes_avant",
    "n_grappes_apres",
    "n_echec_convention",
    "ecart_max_rdt_pb",
    "k_moyen_avant_pb",
    "k_moyen_apres_pb",
    "delta_k_pb",
    "erreur_type_pb",
    "borne_inf_90_pb",
    "borne_sup_90_pb",
    "marge_zone_grise"
  ],
  "survit_si": [
    {"champ": "borne_inf_90_pb", "operateur": ">", "seuil": 0},
    {"champ": "borne_sup_90_pb", "operateur": ">=", "seuil": 0.5},
    {"champ": "schema_ok", "operateur": ">=", "seuil": 1},
    {"champ": "n_avant", "operateur": ">=", "seuil": 190},
    {"champ": "n_apres", "operateur": ">=", "seuil": 105},
    {"champ": "n_grappes_avant", "operateur": ">=", "seuil": 88},
    {"champ": "n_grappes_apres", "operateur": ">=", "seuil": 35},
    {"champ": "n_echec_convention", "operateur": "<=", "seuil": 5},
    {"champ": "ecart_max_rdt_pb", "operateur": "<=", "seuil": 0.05}
  ],
  "non_concluant_si": [
    {"champ": "schema_ok", "operateur": "<", "seuil": 1},
    {"champ": "n_avant", "operateur": "<", "seuil": 190},
    {"champ": "n_apres", "operateur": "<", "seuil": 105},
    {"champ": "n_grappes_avant", "operateur": "<", "seuil": 88},
    {"champ": "n_grappes_apres", "operateur": "<", "seuil": 35},
    {"champ": "n_echec_convention", "operateur": ">", "seuil": 5},
    {"champ": "ecart_max_rdt_pb", "operateur": ">", "seuil": 0.05},
    {"champ": "marge_zone_grise", "operateur": ">=", "seuil": 0}
  ],
  "tolerance": {
    "schema_ok": 0,
    "n_avant": 0,
    "n_apres": 0,
    "n_grappes_avant": 0,
    "n_grappes_apres": 0,
    "n_echec_convention": 0,
    "ecart_max_rdt_pb": 0.05,
    "k_moyen_avant_pb": 0.005,
    "k_moyen_apres_pb": 0.005,
    "delta_k_pb": 0.005,
    "erreur_type_pb": 0.005,
    "borne_inf_90_pb": 0.01,
    "borne_sup_90_pb": 0.01,
    "marge_zone_grise": 0.01
  }
}
```
