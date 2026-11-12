# K11 — Préinscription du test de mort : la pression d'adjudication est-elle encore là après 2021, mesurée sur le titre rouvert contre des titres témoins, sans aucune courbe ?

Rédigé le 2026-11-12 par le rédacteur de préinscription. Le rédacteur n'a lancé aucune analyse : aucune pression, aucun écart
au témoin, aucune moyenne, aucune régression n'a été calculé. Ce qu'il a vu des données est listé en section 4.6. Ce texte est
figé une fois scellé (sha256) ; toute déviation ira dans `tests-de-mort/K11/ecarts.md`.

## 1. D'où vient la question

- **F04 (« survit »).** Autour de 321 réouvertures à 10, 20 et 30 ans (2010-2026), la pression mesurée dans la courbe du
  Trésor, V = 2·E(J) − E(J−5) − E(J+5) avec E = taux à échéance constante (CMT) moins courbe GSW de la Fed, vaut 0,91 pb en
  moyenne (t = 5,6). Découpe faite après le verdict : environ 1,38 pb en 2010-2021 et environ 0,05 pb en 2022-2026.
- **F04-bis (« non concluant »).** Sur l'exercice 2021, passer de l'ancienne méthode de courbe du Trésor à la nouvelle
  (décembre 2021) fait baisser V de 0,78 pb (IC à 95 % : 0,45 à 1,12). La méthode explique donc au moins une partie de la
  cassure.
- **J05 (« non concluant » pour une garde de calendrier mal libellée).** Concession mesurée sur le prix de marché du titre
  rouvert à J−5 et le rendement limite de l'adjudication, nette de la courbe GSW : 0,68 pb avant 2022, 1,10 pb après ; pas de
  baisse. Mais 2023 pèse lourd (3,34 pb en moyenne), et sans le 30 ans la différence devient incertaine.
- **Question restée ouverte : « marché ou mesure ? ».** La pression a-t-elle disparu du marché après 2021, ou seulement de la
  courbe du Trésor, dont la méthode a changé ? K11 répond sans **aucune** courbe ajustée ni interpolée, ni celle du Trésor ni
  celle de la Fed : on compare le titre rouvert à des titres témoins de la même famille, tous évalués au même prix de fin de
  journée, les mêmes jours.

## 2. Question, hypothèses rivales et prédiction chiffrée

**Question.** Aux réouvertures des titres nominaux à 10, 20 et 30 ans de 2022-01-01 à 2026-10-31, le rendement du titre
rouvert monte-t-il encore avant l'adjudication et redescend-il après, plus que celui de titres témoins appariés qui ne sont pas
adjugés ?

**La mesure (définie exactement en section 5).** Pour chaque réouverture i, au jour x ∈ {J−5, J, J+5} (J = jour de
l'adjudication, jours ouvrés fédéraux) :

E_i(x) = 100 × [ y_A(x) − (y_T1(x) + y_T2(x) + y_T3(x)) / 3 ], en points de base,

où y_A est le rendement du titre rouvert et y_T1, y_T2, y_T3 ceux de ses trois témoins, tous tirés du prix FedInvest
`END OF DAY` du même jour. Puis

**V_i = 2·E_i(J) − E_i(J−5) − E_i(J+5)** = [montée de l'écart entre J−5 et J] + [redescente entre J et J+5].

C'est **exactement la forme du V de F04**, avec une seule différence : l'écart E n'est plus « courbe du Trésor moins courbe de
la Fed », mais « titre rouvert moins ses témoins », sur des prix de marché. V > 0 : le titre rouvert s'est déprécié par rapport
à ses voisins avant l'adjudication et a rattrapé ensuite, ce qui est la signature d'une pression d'offre temporaire.

Pourquoi cette forme (plus de détails en section 3) :
- le niveau propre du titre (prime du titre courant, coupon) s'annule (poids 2 − 1 − 1 = 0) ;
- une dérive linéaire de cette prime sur les dix jours (le titre courant perd lentement sa cherté au fil du cycle) s'annule
  aussi ;
- le mouvement général des taux s'annule, puisque titre et témoins sont pris **à la même clôture les mêmes jours** ;
- le rendement limite de 13 h n'entre pas dans la mesure principale, ce qui supprime le décalage 13 h / clôture relevé par les
  juges (section 3, A1) et la question du règlement à terme.

**Statistique principale.** μ_après = moyenne de V sur les réouvertures de 2022-2026, avec une erreur type groupée par mois.

**Hypothèse mise à mort ici.** « La pression est encore présente sur le marché après 2021 » (donc la disparition vue dans la
courbe du Trésor par F04 vient de la mesure). « Survit » veut dire qu'elle tient ; « éliminée » qu'elle tombe.

**Trois lectures et leurs prédictions** (écrites sans avoir vu une seule valeur de V) :

| Lecture | Ce qu'elle dit | μ_après prédit | Baisse avant → après (10 et 30 ans) |
|---|---|---|---|
| **Mesure** | La pression existe toujours sur le marché ; seule la nouvelle méthode du Trésor l'efface de F04 | **+0,8 pb** (0,3 à 1,4) | **0** (−0,4 à +0,4) |
| **Marché** | La pression a disparu sur le marché ; la courbe du Trésor l'a seulement enregistré | **0** (−0,3 à +0,3) | ≈ le niveau d'avant, **+0,8 pb** |
| **Mixte** | La méthode explique une partie de la cassure (F04-bis), le marché le reste | +0,4 pb (0,2 à 0,7) | +0,4 pb |

**D'où viennent ces chiffres.**
- *Le niveau d'avant 2022 de V avec ces témoins.* Deux bornes publiées l'encadrent. En haut, le V de F04 avant 2022, environ
  1,38 pb : il compare le titre courant (que la courbe CMT suivait avant décembre 2021) à une courbe GSW lisse ajustée sur les
  titres anciens ; une courbe lisse absorbe peu la pression locale. En bas, Fleming, Liu et Nguyen (2026, annexe, tableaux A2 et
  A3) : sur 2015-2024, le V du **premier ancien** vaut presque celui du titre courant (1,04 contre 1,17 pb à 10 ans ; 1,55
  contre 1,61 pb à 30 ans). Si nos témoins (deuxième à quatrième anciens) bougeaient comme le premier ancien, V ne vaudrait que
  0,1 pb environ. Les témoins excluent le premier ancien (A2) ; ils devraient donc absorber moins que lui. Prédiction : 0,8 pb,
  fourchette large de 0,3 à 1,4 pb. **Cette incertitude est la principale du test** ; la règle la traite par une condition
  d'instrument (section 8).
- *« Mesure »* : la pression n'a pas changé ; μ_après ≈ niveau d'avant.
- *« Marché »* : la courbe du Trésor a enregistré une vraie disparition : μ_après ≈ 0, comme le V de F04 après 2021
  (0,05 pb).
- *« Mixte »* : la moitié de la cassure de F04 vient de la méthode (F04-bis : 0,78 pb sur environ 1,6) : μ_après ≈ la moitié
  du niveau d'avant.

**Avis du rédacteur, sans effet sur la règle.** J05 (la montée jusqu'à l'adjudication, nette de la courbe GSW, n'a pas baissé)
et F04-bis rendent « mesure » ou « mixte » plus plausibles que « marché ». Le verdict le plus probable est « survit » si V
avant 2022 vaut au moins 0,7 pb ; « non concluant » si les témoins absorbent la plus grande partie de la pression.

## 3. Amendements déclarés à la fiche

| N° | Test de la fiche | Test préinscrit | Raison |
|---|---|---|---|
| A1 | P = (rendement limite − rendement du titre à J−5) − médiane des variations des témoins entre J−5 et J | **V = 2E(J) − E(J−5) − E(J+5)**, E = titre rouvert moins moyenne de trois témoins, **tous en prix de fin de journée FedInvest, les mêmes jours**. La mesure de la fiche est gardée en analyse secondaire S1 | **Faille principale des juges (Astra, Claude)** : le rendement limite est fixé à 13 h, les témoins à la clôture ; le mouvement de l'après-midi (écart-type de 2,5 à 4 pb, J05 section 7) entre alors dans P et peut noyer un effet de moins de 1 pb. En prenant titre et témoins à la même clôture, ce mouvement commun s'annule. Deuxième raison : V a la forme du V de F04 ; on compare donc le même objet, avec et sans courbe. Troisième : le rendement limite est un rendement pour règlement à `issue_date` (1 à 15 jours plus tard) ; le comparer à des rendements au comptant introduit un écart allant jusqu'à environ 1 pb dont le signe suit la pente (J05, amendement A7 ; note de nouveauté, point 3). V n'utilise que des rendements au comptant de même convention. Quatrième : J05 a déjà publié la première jambe de la fiche (rendement limite − rendement à J−5) ; V n'est pas encore vu. Ce qui reste du décalage horaire : section 3.1. |
| A2 | Trois témoins « de même échéance d'origine, de maturité proche, sans adjudication dans les dix séances voisines » | Famille de même échéance d'origine ; on **exclut le titre courant (le titre rouvert) et le premier ancien** ; témoins = les trois titres suivants par échéance décroissante, à au plus **18 mois** d'écart d'échéance, sans aucune adjudication dans [J−5 ; J+5], remplacés par le suivant si leur prix manque ou est figé | Note de nouveauté : le premier ancien porte presque toute la pression (Fleming, Liu et Nguyen 2026, tableau A3) ; le prendre comme témoin absorberait l'effet. « Un témoin de chaque côté » est impossible : le titre rouvert est toujours **le plus long** de sa famille (vérifié sur les 324 réouvertures). De l'autre côté, il n'y a que des titres d'autres familles, absents ou épars (l'émission à 30 ans a été suspendue de 2001 à 2006 : presque aucune échéance entre 2031 et 2036 face au 10 ans d'après 2021). Une règle uniforme exige donc des témoins tous plus courts : 6, 9 et 12 mois pour toutes les réouvertures qui ont trois candidats, sauf une (30 ans du 2010-01-14 : 6, 9 et 18 mois). La règle d'adjudication voisine n'exclut aucun candidat (vérifié) : un ancien n'est jamais rouvert. |
| A3 | Médiane des témoins | **Moyenne** des trois | Avec la moyenne, V = V du titre − moyenne des V des témoins : linéaire, recalculable, décomposable en montée et redescente. La médiane de trois jette deux témoins sur trois. Les prix aberrants sont traités par les gardes (section 5.3), pas par la médiane. |
| A4 | « Dates = observations de marché », sans définition | **Calendrier C** : du lundi au vendredi, moins les jours fériés fédéraux (5 U.S.C. 6103, avec report du samedi au vendredi et du dimanche au lundi ; Juneteenth à partir de 2021), moins **deux jours sans tableau FedInvest vérifiés** : 2012-10-30 (ouragan Sandy) et 2018-12-05 (deuil national). J−5 et J+5 = cinquième date de C avant et après J. Le contrôle porte sur le rang exact dans C, et non sur un nombre de jours civils | Demande du commanditaire, et l'échec de J05 (garde « 7 à 9 jours civils » cassée par trois lundis qui suivent un lundi férié, où l'écart vaut 10 jours). Vérifié sur pages réelles (section 4.5) : FedInvest publie les veilles et lendemains de Noël où l'administration a pu être fermée par décret (2020-12-24, 2024-12-24, 2025-12-24, 2025-12-26), le jour de deuil national du 2025-01-09, les Vendredis saints (2021-04-02, 2023-04-07) et pendant les fermetures budgétaires (octobre 2013 et 2025) ; il ne publie rien le 2012-10-30, le 2018-12-05 et un lundi férié (2016-09-05). Le 2018-12-05 tombait exactement à J−5 de la réouverture à 10 ans du 2018-12-12 : sans cette exception, la ligne serait perdue. |
| A5 | t = (μ_post − 0,25)/ET, erreur type HAC à trois adjudications ; meurt si μ_post < 0,50 ou t ≤ 1,645 | μ_après, erreur type **groupée par mois** ; IC à 90 %. **Survit** : borne basse > 0, borne haute ≥ 0,5 et robustesse ; **éliminée** : borne haute < 0,5 pb **et** baisse significative entre avant et après (condition d'instrument) ; **non concluant** sinon | Un HAC à trois retards sur une suite d'événements irréguliers (10 et 30 ans deux jours de suite, 20 ans la semaine suivante, puis un mois de vide) est difficile à défendre ; le groupement par mois est celui de F04 et J05, et il traite exactement cette dépendance. Les seuils de la fiche (0,25 et 0,50) étaient posés sur l'échelle de la mesure de J05, rendement limite compris ; ils sont refondés sur l'échelle de V en section 8. Surtout, la règle de la fiche « éliminait » l'idée dès que μ_post < 0,5, même si l'intervalle contenait 0,5 et plus : elle confondait « pas prouvé » et « absent ». |
| A6 | Meurt « comme résultat général » si la moyenne devient négative sans 2023 ou sans le 30 ans | La même condition (moyenne > 0 sans 2023 et sans le 30 ans) est requise pour **survivre** ; si elle seule manque, le verdict est **non concluant**, pas « éliminée » | 2023 et le 30 ans portaient le résultat de J05 ; une survie qui n'existerait que par eux ne serait pas une pression persistante. Mais une moyenne globale significativement positive n'est pas une preuve d'absence : tuer l'idée sur la moyenne ponctuelle d'un sous-échantillon de 78 à 93 réouvertures (erreur type d'environ 0,33 à 0,36 pb au cas central de la section 7) serait tuer sur du bruit. |
| A7 | Rien | **Condition d'instrument** : on ne conclut « éliminée » que si l'instrument voit une baisse significative entre 2010-2021 et 2022-2026 sur les 10 et 30 ans | Note de nouveauté et quatrième juge : les témoins peuvent absorber la pression. Si l'instrument ne voit déjà rien avant 2022, un zéro après 2021 ne dit rien sur « marché ou mesure ». La comparaison est faite sur les 10 et 30 ans seulement, présents à égalité dans les deux périodes (le 20 ans n'existe qu'à partir de 2020). |
| A8 | « Les réouvertures post-2021 de l'échantillon J05 » (116) ; 20 ans « moins nombreux avant 2020 » | 117 réouvertures après 2021 (39 par échéance), y compris le 20 ans du 2026-10-21, dont le rendement limite est absent de l'API mais dont V n'a pas besoin. Avant 2022 : on écarte l'opération hors calendrier du 2019-06-21 (exclue aussi par Fleming, Liu et Nguyen, note 10), les **8 réouvertures à 20 ans de 2020-06-17 à 2021-04-21 qui n'ont pas trois témoins**, et celle du 2021-12-02, dont le titre n'était pas encore émis à J−5 | Il n'existe **aucun 20 ans avant le 2020-05-20** (correction 4 de la note de nouveauté) : le doute des juges porte sur 2020-2021. Comptes refaits sur les métadonnées (section 4.4) et vérifiés sur pages réelles : le 2021-12-02, le titre 912810TC2 (émis le 2021-11-30) est absent de la page du 2021-11-24. Les 5 réouvertures à 20 ans d'avant 2022 qui restent ne servent qu'au descriptif. |
| A9 | Dispersion « d'environ 2,3 pb » | 3,2 pb par réouverture en cas central (section 7) | Correction 5 de la note de nouveauté : l'erreur type de J05 implique 3,2 pb. |
| A10 | « Rendements quotidiens par CUSIP » FedInvest | FedInvest donne des **prix** ; le rendement est recalculé (conventions de J05, reprises en 5.2) ; l'échéance d'origine vient de l'API des adjudications | Correction 3 de la note de nouveauté. |

### 3.1 Ce qui reste du décalage 13 h / clôture

- **Ce qui s'annule.** Le mouvement général des taux entre 13 h et la clôture touche le titre et ses témoins ; pris à la même
  clôture, il disparaît de E. C'était la principale source de bruit de J05.
- **Ce qui reste (1) : la pression atteint son sommet vers 13 h**, puis commence à se résorber. E(J) est mesuré à la clôture,
  après une partie de cette détente. V à la clôture sous-estime donc le V « au sommet » de deux fois la détente relative du
  titre entre 13 h et la clôture. Ce biais va vers zéro dans les deux périodes. F04 (CMT et GSW de fin de journée) et
  Fleming, Liu et Nguyen (rendements CRSP de clôture) font de même : la comparaison avec F04 reste à convention égale.
- **Ce qui reste (2) : un changement de vitesse de résorption** après 2021 (par exemple si l'après-midi effaçait plus vite la
  pression) ferait baisser V sans changement du sommet. On ne peut pas le mesurer sans données intrajournalières ; l'analyse
  S1 (rendement limite de 13 h) en donne une idée, bruitée.
- **Ce qui reste (3) : l'heure de « fin de journée » de FedInvest n'est pas documentée.** Elle est la même pour tous les titres
  d'une page, donc elle s'annule dans E, sauf si le fournisseur évalue le titre courant sur des cotations et les anciens par un
  modèle (limite 3, section 9).

## 4. Données

Toutes publiques, sans compte. L'expérimentateur enregistre chaque fichier brut (réponse JSON de l'API, chaque page HTML de
FedInvest) dans `tests-de-mort/K11/donnees/`, avec la date de téléchargement et le sha256. Aucune source de remplacement n'est
permise.

### 4.1 D1. Adjudications (Fiscal Data, API v1)

Une seule requête, testée le 2026-11-12 (HTTP 200, 2 793 lignes, une page) :

```
https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?fields=cusip,auction_date,issue_date,maturity_date,security_type,security_term,original_security_term,reopening,inflation_index_security,floating_rate,closing_time_comp,int_rate,high_yield,high_price&filter=security_type:in:(Note,Bond),auction_date:lte:2026-10-31&sort=auction_date&page%5Bsize%5D=10000
```

Valeur manquante : la chaîne `null`. Lignes nominales : `inflation_index_security` ≠ "Yes" et `floating_rate` ≠ "Yes".

**Réouvertures étudiées.** Lignes nominales avec `reopening` = "Yes", `auction_date` entre 2010-01-01 et 2026-10-31, et
`security_term` qui commence par « 9-Year » (échéance 10), « 19-Year » (20) ou « 29-Year » (30). Comptes constatés : 324.

| Période | Dates | 10 ans | 20 ans | 30 ans | Total |
|---|---|---|---|---|---|
| `avant` | 2010-01-01 à 2021-12-31 | 97 | 14 | 96 | 207 |
| `apres` | 2022-01-01 à 2026-10-31 | 39 | 39 | 39 | 117 |

**Familles** (pour les témoins). Pour chaque CUSIP nominal, sa **première** adjudication (ligne avec `reopening` = "No") donne
son échéance d'origine (`original_security_term`), sa date d'émission d'origine (`issue_date`), son coupon (`int_rate`) et son
échéance (`maturity_date`). Famille 10 : `original_security_term` = "10-Year". Famille 20 : "20-Year". Famille 30 :
"30-Year", "29-Year 9-Month" ou "30-Year 3-Month" (quatre obligations à 30 ans émises avec un terme légèrement décalé, dont
912810PX0, échéance 2038-05-15, témoin du 30 ans du 2010-01-14). Toutes les échéances des titres rouverts et des témoins
retenus tombent le 15 du mois (vérifié).

Champs de S1 seulement : `high_yield` (rendement limite, pour cent) et `high_price` (prix limite, pour 100). Une seule
réouverture étudiée a ces deux champs à `null` : le 20 ans du 2026-10-21. `closing_time_comp` vaut « 01:00 PM » sauf trois
lignes (2012-09-13 et 2012-12-12 à 11 h 30 ; 2019-06-21 à 11 h, écartée) ; on les garde (même convention de clôture pour V).

### 4.2 D2. Prix de fin de journée par titre (FedInvest, Bureau of the Fiscal Service)

Procédure, testée le 2026-11-12 sur 80 dates, une date par session, client par défaut, pause d'une seconde :
1. `GET https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate` : HTTP 200 ; garder le témoin de session et
   le champ caché `_csrf` (96 caractères).
2. `POST` à la même adresse, corps `priceDate=AAAA-MM-JJ&submit=Show+Prices&_csrf=<jeton>`, avec le témoin : HTTP 302 (ne pas
   suivre la redirection automatiquement : J05 a obtenu 403 avec `curl -L`).
3. `GET https://www.treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail` avec le témoin : HTTP 200, page HTML avec
   « Prices For: <Mois jour, année> » et un tableau d'en-tête exact `CUSIP, SECURITY TYPE, RATE, MATURITY DATE, CALL DATE,
   BUY, SELL, END OF DAY` (vérifié sur les 80 pages).

Champs utilisés : `CUSIP`, `SECURITY TYPE` (« MARKET BASED NOTE » ou « MARKET BASED BOND »), `RATE` (forme « 2.375% »),
`MATURITY DATE` (forme « MM/JJ/AAAA ») et `END OF DAY` (prix pied de coupon pour 100 de nominal ; J05 l'a vérifié autour du
coupon du 15 mai 2016). Une page dont la date affichée diffère de la date demandée, ou dont le tableau est vide, est traitée
comme absente.

Dates à télécharger : J−5, J et J+5 de chaque réouverture non écartée par les métadonnées (section 4.4), soit **905 dates
distinctes**, dont 316 pour 2022-2026 (environ 45 minutes de téléchargement, une fois, mises en cache). Tous les témoins se
lisent sur les mêmes pages.

### 4.3 Calendrier C

C = jours du lundi au vendredi de 2009-06-01 à 2026-12-31, moins :
- les jours fériés fédéraux observés : 1er janvier, troisième lundi de janvier, troisième lundi de février, dernier lundi de
  mai, 19 juin (à partir de 2021), 4 juillet, premier lundi de septembre, deuxième lundi d'octobre, 11 novembre, quatrième
  jeudi de novembre, 25 décembre ; un férié tombant un samedi est observé le vendredi précédent (le 1er janvier 2011 et le
  1er janvier 2022 sont donc observés les 2010-12-31 et 2021-12-31), un dimanche le lundi suivant ;
- deux jours sans tableau FedInvest, vérifiés : **2012-10-30** et **2018-12-05**.

J = `auction_date` (doit appartenir à C : vrai pour les 324 lignes) ; J−5 = la date de C de rang rang(J) − 5 ; J+5 = rang
rang(J) + 5. Les autres jours de fermeture fédérale exceptionnelle (veilles de Noël, deuil du 2025-01-09, fermetures budgétaires) restent dans C : FedInvest y publie (vérifié, A4). Une autre page
vide rencontrée par l'expérimentateur à J−5, J ou J+5 rend la ligne incomplète (`prix_manquant`) ; elle ne modifie pas C.

### 4.4 Sélection des témoins (sur D1 seulement, avant de lire un prix)

Pour la réouverture i (titre A, échéance M, jour J) :
1. **Membres de la famille en circulation** : CUSIP de la famille de A, dont la première adjudication est au plus tard J et
   dont l'échéance est postérieure à J+5.
2. **Ordre** : échéance décroissante ; à échéance égale, première adjudication la plus récente d'abord ; puis CUSIP dans
   l'ordre alphabétique inverse. Rang 0 = **A lui-même** (vérifié sur les 324 lignes : le titre rouvert est toujours le plus
   long de sa famille). Rang 1 = le **premier ancien**, exclu.
3. **Candidats** : rangs 2, 3, 4, … ; on garde ceux dont l'écart d'échéance avec A, en mois entiers
   (12 × différence d'années + différence de mois), est au plus 18, et qui n'ont **aucune** ligne dans D1 (adjudication ou
   réouverture) datée de J−5 à J+5 inclus.
4. **Témoins** : les trois premiers candidats qui ont, aux trois dates J−5, J et J+5, un prix `END OF DAY` présent et > 0
   (sinon le candidat est sauté et compté dans `n_candidats_absents`), et qui ne sont pas **figés** : un témoin dont le prix
   `END OF DAY` est identique à J−5 et à J, ou à J et à J+5, est sauté et compté dans `n_temoins_figes`.

**Comptes constatés sur les métadonnées** (2026-11-12), avant toute lecture de prix :
- 10 et 30 ans, toutes périodes : au moins trois candidats à 18 mois ou moins ; écarts 6, 9 et 12 mois, sauf le 30 ans du
  2010-01-14 (6, 9 et 18 mois).
- 20 ans après 2021 : trois candidats à 6, 9 et 12 mois pour les 39 réouvertures.
- 20 ans avant 2022 : le nombre de candidats est 0, 0, 0, 0, 1, 1, 2, 2 pour les huit réouvertures du 2020-06-17 au
  2021-04-21, puis 3 à partir du 2021-06-15. **Les huit premières sont écartées** (`temoins_insuffisants`). Aucun repli sur
  d'anciennes obligations à 30 ans n'est prévu : il mélangerait deux familles dans le seul sous-groupe où le 20 ans est rare,
  pour 8 lignes qui ne comptent pas dans la règle.
- La règle d'adjudication voisine n'écarte aucun candidat.
- Le 20 ans du 2021-12-02 : le titre 912810TC2, adjugé le 2021-11-17 et émis le 2021-11-30, n'existe pas encore sur FedInvest
  à J−5 = 2021-11-24 (vérifié). Règle générale : si l'`issue_date` de la première adjudication de A est postérieure à J−5, la
  ligne est écartée (`titre_non_emis_a_jm5`). C'est le seul cas.

Échantillon attendu : 117 réouvertures après 2021 (39 mois) ; 192 réouvertures à 10 et 30 ans avant 2022 (96 mois) ; plus 5
réouvertures à 20 ans avant 2022, descriptives.

### 4.5 Vérifications faites sur données réelles (2026-11-12)

**Pages FedInvest téléchargées** (80 dates) : 2010-01-06, 07, 13, 14, 21, 22 ; 2012-10-29, 30 ; 2013-10-02, 03, 09, 10, 17,
18 ; 2016-09-02, 05, 12, 19 ; 2018-12-04, 05, 11, 12, 13, 19 ; 2019-01-02, 03, 09, 10, 16, 17 ; 2020-03-05, 12, 19 ;
2020-12-24 ; 2021-04-02 ; 2021-06-08, 15, 23 ; 2021-07-02, 12, 19 ; 2021-11-24 ; 2021-12-02, 09 ; 2022-09-02, 12, 19 ;
2023-04-07 ; 2024-12-10, 17, 24, 30, 31 ; 2025-01-07, 08, 09, 14, 15 ; 2025-10-01, 02, 08, 09, 15, 16, 17, 22, 29 ;
2025-12-10, 17, 24, 26 ; 2026-09-30 ; 2026-10-01, 07, 08, 14, 15, 16, 21, 28. Les 80 ont répondu 200 / 302 / 200, avec la date
affichée égale à la date demandée et l'en-tête exact. Tableau vide : 2012-10-30, 2016-09-05 (Labor Day), 2018-12-05. Tableau
rempli (193 à 353 notes et obligations) partout ailleurs.

**Réouvertures vérifiées sur les trois pages (J−5, J, J+5), titre rouvert et trois témoins** : pour chacun des 4 titres et
chacune des 3 dates, présence du CUSIP, `SECURITY TYPE` de note ou d'obligation, `RATE` et `MATURITY DATE` égaux au coupon et à
l'échéance de D1, `END OF DAY` > 0, et absence de prix figé.

| Échéance | Réouverture (J) | Cas de calendrier ou de données testé | Résultat |
|---|---|---|---|
| 10 ans | 2010-01-13 | début de l'échantillon | 12/12 |
| 10 ans | 2013-10-09 | fermeture budgétaire d'octobre 2013 | 12/12 |
| 10 ans | 2016-09-12 | lundi après Labor Day : J−5 = 2016-09-02, 10 jours civils | 12/12 |
| 10 ans | 2018-12-12 | J−5 tombait le 2018-12-05 (page vide) ; avec C, J−5 = 2018-12-04 | 12/12 avec C (4 absences sur la page du 05) |
| 10 ans | 2019-01-09 | fermeture budgétaire 2018-2019 | 12/12 |
| 10 ans | 2021-07-12 | lundi après le 4 juillet observé le 5 : J−5 = 2021-07-02, 10 jours | 12/12 |
| 10 ans | 2022-09-12 | lundi après Labor Day : J−5 = 2022-09-02, 10 jours | 12/12 |
| 10 ans | 2025-01-07 | J−5 = 2024-12-30 (Noël et 1er janvier) ; 2025-01-09 (deuil) dans la fenêtre | 12/12 ; page du 09 remplie |
| 10 ans | 2025-10-08 | fermeture budgétaire d'octobre 2025 | 12/12 |
| 10 ans | 2026-10-07 | fin de l'échantillon | 12/12 |
| 20 ans | 2021-06-15 | premier 20 ans avec trois témoins ; J+5 franchit Juneteenth observé le 2021-06-18 | 12/12 |
| 20 ans | 2021-12-02 | titre émis le 2021-11-30, après J−5 | titre absent à J−5 → règle `titre_non_emis_a_jm5` |
| 20 ans | 2024-12-17 | J+5 = 2024-12-24, veille de Noël | 12/12 ; page du 24 remplie |
| 20 ans | 2025-10-22 | J−5 = 2025-10-15, après Columbus Day | 12/12 |
| 20 ans | 2025-12-17 | J+5 = 2025-12-24, veille de Noël | 12/12 |
| 20 ans | 2026-10-21 | dernière ligne ; `high_yield` nul | 12/12 |
| 30 ans | 2010-01-14 | témoin à 18 mois (912810PX0, famille « 29-Year 9-Month ») | 12/12 |
| 30 ans | 2013-10-10 | fermeture budgétaire d'octobre 2013 | 12/12 |
| 30 ans | 2019-01-10 | fermeture budgétaire 2018-2019 | 12/12 |
| 30 ans | 2020-03-12 | mars 2020 | 12/12 |
| 30 ans | 2025-01-08 | J−5 = 2024-12-31 | 12/12 |
| 30 ans | 2025-10-09 | J+5 = 2025-10-17, franchit Columbus Day | 12/12 |
| 30 ans | 2026-10-08 | fin de l'échantillon | 12/12 |

Aucun prix figé parmi les 83 titres présents aux trois dates (20 titres rouverts, 63 témoins). Aux dates J−5 de 24 réouvertures (les précédentes, plus 2021-12-09 et
2025-01-22, dont la page J−5 était en cache), un calcul en mémoire, dont seuls des booléens ont été imprimés, a confirmé : prix
dans [30 ; 200], rendements dans [−1 ; 20] et écart de rendement entre chaque témoin et le titre rouvert d'au plus 0,60 point.

**Calendrier, sur les 324 lignes (métadonnées)** : J ∈ C pour toutes ; écart J − (J−5) = 7 jours civils (261 lignes), 8 (60)
ou 10 (3 : les lundis 2016-09-12, 2021-07-12 et 2022-09-12) ; écart (J+5) − J = 7 (272) ou 8 (52). Aucune extrémité de
fenêtre ne tombe un Vendredi saint. 15 réouvertures ont lieu un lundi.

### 4.6 Ce que le rédacteur a vu

- Les verdicts et chiffres du vérificateur de F04, F04-bis et J05, la lecture après coup de J05 et la note de nouveauté de
  K11. Ils ont servi à la prédiction et aux seuils : ce n'est pas un regard aveugle, c'est déclaré.
- D1 : la liste des champs, et pour les 2 793 lignes les identifiants, dates, termes, coupons et heures de clôture. Pour
  `high_yield` et `high_price`, seulement le nombre de valeurs nulles (aucune valeur affichée).
- D2 : pour 80 dates, la date affichée, l'en-tête, le nombre de lignes, et pour les titres listés en 4.5 : présence, type,
  coupon, échéance, et des booléens (prix > 0 ; prix identique ou non entre deux dates ; gardes de plage et d'appariement à
  J−5). **Aucun prix ni aucun rendement n'a été affiché. Des rendements n'ont été calculés, en mémoire, qu'à J−5 et pour les seules
  gardes. Aucun E, aucun V, aucune différence entre deux dates n'a été calculé (hors le test d'égalité des prix pour les prix
  figés).**

## 5. Fichier d'analyse

Nom : `tests-de-mort/K11/K11_analyse.csv`. UTF-8, virgule, point décimal, une ligne d'en-tête, champ vide pour une valeur
manquante, nombres écrits sans arrondi (au moins 10 chiffres significatifs). **Une ligne par réouverture** sélectionnée en 4.1
(324), triée par `date_adjudication` puis `echeance`. Pas d'autre ligne.

### 5.1 Colonnes

Notation : A = titre rouvert ; T1, T2, T3 = témoins dans l'ordre de la section 4.4 ; PA = premier ancien (exclu des témoins,
suivi seulement pour l'analyse S2).

| N° | Colonne | Type | Unité, contenu |
|---|---|---|---|
| 1 | `id_ligne` | texte | `<cusip>_<date_adjudication>`, unique |
| 2 | `cusip` | texte | 9 caractères, CUSIP de A |
| 3 | `terme_api` | texte | `security_term` de D1, recopié |
| 4 | `echeance` | entier | 10, 20 ou 30, selon le préfixe de `terme_api` |
| 5 | `date_adjudication` | date AAAA-MM-JJ | J |
| 6 | `mois` | texte AAAA-MM | 7 premiers caractères de J |
| 7 | `annee` | entier | année de J |
| 8 | `periode` | texte | `avant` ou `apres` (tableau 4.1) |
| 9 | `heure_cloture` | texte | `closing_time_comp`, recopié |
| 10 | `date_emission_origine` | date | `issue_date` de la première adjudication de A |
| 11 | `date_reglement` | date | `issue_date` de cette réouverture (S1 seulement) |
| 12 | `date_echeance` | date | `maturity_date` de A |
| 13 | `taux_coupon_pct` | décimal | `int_rate` de A, pour cent par an |
| 14 | `date_jm5` | date | J−5 dans C |
| 15 | `date_jp5` | date | J+5 dans C |
| 16 | `ecart_jm5_jours` | entier | J − J−5, jours civils |
| 17 | `ecart_jp5_jours` | entier | J+5 − J, jours civils |
| 18 | `cusip_premier_ancien` | texte | CUSIP de rang 1 |
| 19 | `echeance_pa` | date | échéance de PA |
| 20 | `coupon_pa_pct` | décimal | coupon de PA |
| 21-23 | `cusip_t1`, `cusip_t2`, `cusip_t3` | texte | témoins |
| 24-26 | `rang_t1`, `rang_t2`, `rang_t3` | entier | rang dans l'ordre de 4.4 (≥ 2) |
| 27-29 | `echeance_t1`, `echeance_t2`, `echeance_t3` | date | `maturity_date` des témoins |
| 30-32 | `coupon_t1_pct`, `coupon_t2_pct`, `coupon_t3_pct` | décimal | `int_rate` des témoins |
| 33-35 | `ecart_mois_t1`, `ecart_mois_t2`, `ecart_mois_t3` | entier | écart d'échéance avec A, mois entiers |
| 36 | `n_temoins_figes` | entier | candidats sautés car figés (4.4, étape 4) |
| 37 | `n_candidats_absents` | entier | candidats sautés car prix absent ou nul |
| 38-40 | `prix_a_jm5`, `prix_a_j`, `prix_a_jp5` | décimal | `END OF DAY` de A, pour 100 |
| 41-49 | `prix_t1_jm5`, `prix_t1_j`, `prix_t1_jp5`, `prix_t2_jm5`, `prix_t2_j`, `prix_t2_jp5`, `prix_t3_jm5`, `prix_t3_j`, `prix_t3_jp5` | décimal | `END OF DAY` des témoins |
| 50-52 | `prix_pa_jm5`, `prix_pa_j`, `prix_pa_jp5` | décimal | `END OF DAY` de PA (vides si absents) |
| 53 | `identite_fi_ok` | entier | 1 si, pour A et les trois témoins aux trois dates, `RATE` et `MATURITY DATE` de FedInvest égalent coupon et échéance de D1 et `SECURITY TYPE` est une note ou une obligation ; sinon 0 |
| 54 | `rdt_limite_pct` | décimal | `high_yield` (S1 seulement) |
| 55 | `prix_limite` | décimal | `high_price` (S1 seulement) |
| 56-58 | `rdt_a_jm5_pct`, `rdt_a_j_pct`, `rdt_a_jp5_pct` | décimal | Y(prix de A, date), section 5.2 |
| 59-67 | `rdt_t1_jm5_pct`, …, `rdt_t3_jp5_pct` (même ordre que 41-49) | décimal | Y(prix du témoin, date) |
| 68-70 | `rdt_pa_jm5_pct`, `rdt_pa_j_pct`, `rdt_pa_jp5_pct` | décimal | Y(prix de PA, date) |
| 71-73 | `e_jm5_pb`, `e_j_pb`, `e_jp5_pb` | décimal | E(x) = 100 × [`rdt_a_x` − (`rdt_t1_x` + `rdt_t2_x` + `rdt_t3_x`)/3] |
| 74 | `v_pb` | décimal | 2 × `e_j_pb` − `e_jm5_pb` − `e_jp5_pb` |
| 75 | `montee_pb` | décimal | `e_j_pb` − `e_jm5_pb` |
| 76 | `detente_pb` | décimal | `e_j_pb` − `e_jp5_pb` |
| 77 | `v_pa_pb` | décimal | même formule que V avec PA à la place de A |
| 78 | `p_carte_pb` | décimal | 100 × [(`rdt_limite_pct` − `rdt_a_jm5_pct`) − moyenne sur k de (`rdt_tk_j_pct` − `rdt_tk_jm5_pct`)] |
| 79 | `motif_exclusion` | texte | vide, ou dans l'ordre de priorité : `hors_calendrier` (2019-06-21), `temoins_insuffisants` (moins de trois candidats sur D1), `titre_non_emis_a_jm5`, `prix_manquant` (page absente ou vide, prix de A absent ou nul, ou moins de trois témoins valides après remplacements), `prix_fige` (prix de A identique à J−5 et J ou à J et J+5) |
| 80 | `complet` | entier | 1 si les 12 prix de A et des témoins sont présents et > 0 et `identite_fi_ok` = 1 ; sinon 0 |
| 81 | `dans_p` | entier | 1 si `motif_exclusion` est vide et `complet` = 1 ; sinon 0 |

Une valeur dérivée (colonnes 56-78) est vide si l'une de ses entrées l'est. Pour les lignes écartées par les métadonnées
(trois premiers motifs), les colonnes 18 à 78 peuvent rester vides.

### 5.2 Conventions de calcul (identiques pour l'expérimentateur et le vérificateur ; reprises de J05, section 5.2)

Notations : c = coupon (pour cent) ; M = échéance (toujours le 15 du mois ici) ; d = date de règlement.
- **Dates de coupon.** T_k = M reculée de 6·k mois (k = 0, 1, 2, …), même jour du mois. Dates nominales, sans report.
- **Coupon couru.** L(d) = dernier T_k ≤ d ; N(d) = premier T_k > d ; AI(d) = (c/2) × (d − L)/(N − L), en jours civils.
- **Rendement d'un prix pied de coupon P pour règlement d**, Y(P, d) (31 CFR partie 356, annexe B, plus d'un coupon restant) :
  y, en pour cent, est l'unique solution de P + AI(d) = Σ_{j=1..n} F_j × (1 + y/200)^−[(j − 1) + (N − d)/(N − L)], où n est le
  nombre de T_k > d et F_j = c/2 pour j < n, c/2 + 100 pour j = n. Résolution numérique à 10⁻⁹ point de pourcentage près.
- **Rendements de marché.** Pour tout titre et toute date x ∈ {J−5, J, J+5} : Y(`END OF DAY` du jour x, x). Le titre rouvert
  et ses témoins ont la même convention de règlement le même jour ; E ne dépend donc pas de la convention de règlement propre
  à FedInvest, et aucune courbe n'intervient.
- `p_carte_pb` (S1) compare `high_yield`, rendement pour règlement à `date_reglement`, à des rendements au comptant ; l'écart de
  règlement (jusqu'à environ 1 pb selon J05, amendement A7, de signe lié à la pente) **n'est pas corrigé**, puisque le corriger demanderait une
  courbe. S1 est descriptive.

### 5.3 Contrôles de schéma

Le vérificateur les exécute et rapporte `schema_ok` = 1 si tous passent, 0 sinon. Chacun a été vérifié sur des lignes ou des
dates réelles (colonne de droite).

| N° | Contrôle | Vérifié sur |
|---|---|---|
| 1 | Les 81 colonnes ci-dessus, dans cet ordre, et aucune autre | — (format) |
| 2 | `id_ligne` unique et égal à `<cusip>_<date_adjudication>` ; `cusip` de 9 caractères ; `echeance` = 10, 20 ou 30 selon que `terme_api` commence par « 9-Year », « 19-Year » ou « 29-Year » ; `mois`, `annee` et `periode` conformes à `date_adjudication` ; colonnes 53, 80, 81 dans {0, 1} | les 324 lignes de D1 |
| 3 | 324 lignes ; `avant` : 97, 14 et 96 lignes à 10, 20 et 30 ans ; `apres` : 39, 39 et 39 ; `hors_calendrier` sur la seule ligne 9128286T2_2019-06-21 ; `temoins_insuffisants` sur exactement les huit lignes à 20 ans du 2020-06-17 au 2021-04-21 ; `titre_non_emis_a_jm5` sur la seule ligne 912810TC2_2021-12-02 | les 324 lignes de D1 |
| 4 | **Calendrier, au rang exact** : `date_adjudication` ∈ C ; `date_jm5` = la date de C de rang rang(J) − 5 et `date_jp5` = rang(J) + 5, C étant reconstruit par le vérificateur selon 4.3 ; `ecart_jm5_jours` et `ecart_jp5_jours` égaux aux différences de dates et compris entre 7 et 11 | les 324 lignes (écarts constatés 7, 8, 10 et 7, 8) ; pages réelles des cas limites de 4.5 (trois lundis après un lundi férié, 2018-12-05, veilles de Noël, deuil national, fermetures budgétaires, Juneteenth, Columbus Day) |
| 5 | **Témoins** (lignes non écartées par les métadonnées) : trois CUSIP distincts, différents de `cusip` et de `cusip_premier_ancien` ; `rang_t1` < `rang_t2` < `rang_t3`, tous ≥ 2 ; `echeance_t1` ≥ `echeance_t2` ≥ `echeance_t3`, toutes antérieures à `date_echeance` ; `ecart_mois_tk` = 12 × (année de `date_echeance` − année de `echeance_tk`) + (mois de `date_echeance` − mois de `echeance_tk`), entre 1 et 18. Le vérificateur télécharge D1 (une requête) et refait les étapes 1 à 3 de 4.4 : `cusip_premier_ancien` doit être le rang 1 ; les trois témoins doivent être, dans l'ordre, des candidats de la liste obtenue, et figurer parmi ses 3 + s premiers, avec s = `n_temoins_figes` + `n_candidats_absents` (les trois premiers si s = 0) | les 324 lignes de D1 (rang 0 = titre rouvert partout ; témoins aux rangs 2, 3, 4, écarts 6, 9, 12 mois, une fois 18) ; 22 réouvertures sur pages réelles, sans remplacement nécessaire |
| 6 | **Dates des prix** : aucun prix n'est daté hors de {`date_jm5`, `date_adjudication`, `date_jp5`} (par construction des colonnes) ; `date_emission_origine` ≤ `date_jm5` sur les lignes `dans_p` = 1 | 2021-12-02 (seul cas contraire, écarté) |
| 7 | **Plages**, sur les lignes `dans_p` = 1 : prix (colonnes 38-49) entre 30 et 200 ; rendements (56-67) entre −1 et 20 ; coupons entre 0 et 15 | booléens à J−5 sur 24 réouvertures |
| 8 | **Garde contre un mauvais appariement de titre ou de colonne**, sur les lignes `dans_p` = 1 et aux trois dates : \|`rdt_tk_x_pct` − `rdt_a_x_pct`\| ≤ 0,60 point de pourcentage pour k = 1, 2, 3 | booléens à J−5 sur 24 réouvertures |
| 9 | **Pas de prix figé retenu** : pour A et chaque témoin des lignes `dans_p` = 1, le prix de J diffère de celui de J−5 et de celui de J+5 | 83 titres présents aux trois dates : aucun figé |
| 10 | `identite_fi_ok` = 1 sur toutes les lignes `dans_p` = 1 | 264 consultations (22 réouvertures × 4 titres × 3 dates) : 259 présentes, toutes conformes ; les 5 absences sont la page vide du 2018-12-05 (4) et le titre non émis du 2021-11-24 (1) |
| 11 | Colonnes 71 à 78 égales à leur formule appliquée aux colonnes du fichier, à 10⁻⁶ pb près ; colonnes 80 et 81 conformes à leur définition | — (arithmétique) |

Les plages des contrôles 7 et 8 sont larges exprès : un des prix les plus bas attendus pour un témoin (coupon de 1,875 % avec
29 ans restants, rendement de 4,2 % fin 2022) est d'environ 61 ; à 18 mois d'écart d'échéance au plus, l'écart de rendement
entre deux titres de la même famille est de l'ordre de la pente de la courbe sur un an (quelques points de base à une vingtaine),
loin de 0,60 point. La leçon de J05 est appliquée : aucune garde n'est plus étroite que ce que les cas réels vérifiés
permettent.

## 6. Statistique

**Échantillons.** P = lignes avec `dans_p` = 1.
- P_après = lignes de P avec `periode` = `apres` (attendu 117 ; 39 mois).
- P_avant,10/30 = lignes de P avec `periode` = `avant` et `echeance` ∈ {10, 30} (attendu 192 ; 96 mois).
- P_après,10/30 = lignes de P_après avec `echeance` ∈ {10, 30} (attendu 78 ; 39 mois).

**Moyenne et erreur type groupée par mois**, pour un ensemble S de N lignes réparties en G mois (`mois`) :
V̄_S = moyenne de `v_pb` sur S ; ET_S = (1/N) × racine[ G/(G − 1) × Σ_g ( Σ_{i ∈ S, mois g} (V_i − V̄_S) )² ].
(C'est l'erreur type groupée par mois d'une régression de V sur une constante, avec le seul facteur G/(G − 1).)

**Recalcul.** Le vérificateur recalcule avec son propre code, selon 5.2, les 12 rendements (colonnes 56-67) de chaque ligne de
P à partir des prix, coupons, échéances et dates du fichier, puis E et V. Il rapporte `ecart_max_rdt_pb` = 100 × le plus grand
écart absolu entre ses rendements et ceux du fichier. L'expérimentateur rapporte le même champ avec un second code à lui
(attendu 0). Chacun calcule ensuite les statistiques avec ses propres V, sur l'échantillon P défini par les colonnes du
fichier. Les deux rapportent aussi `n_temoins_figes` = somme de la colonne 36 sur P.

**Statistique principale (une seule) : la pression moyenne après 2021.**
- `v_moyen_apres_pb` = V̄ sur P_après ; `erreur_type_apres_pb` = ET sur P_après.
- `borne_inf_90_apres_pb` : L = V̄ − 1,645 × ET ; `borne_sup_90_apres_pb` : U = V̄ + 1,645 × ET (1,645 exactement).
- `marge_zone_grise` = min(−L, U − 0,5). Mz ≥ 0 veut dire : L ≤ 0 et U ≥ 0,5, c'est-à-dire que les données n'excluent ni
  « marché » (μ = 0) ni « mesure » (μ ≥ 0,5).

**Robustesse (2023 et 30 ans), dans la règle.**
- `v_moyen_apres_sans_2023_pb` = V̄ sur P_après privé des lignes de `annee` = 2023 (attendu 93 lignes) ;
  `v_moyen_apres_sans_30_pb` = V̄ sur P_après privé des 30 ans (attendu 78) ; `min_robustesse_pb` = le plus petit des deux.
- `alerte_robustesse` = 1 si L > 0 et U ≥ 0,5 et `min_robustesse_pb` ≤ 0 ; sinon 0.

**Avant / après, dans la règle (condition d'instrument), sur les 10 et 30 ans.**
- `v_moyen_avant_1030_pb`, `erreur_type_avant_1030_pb` sur P_avant,10/30 ; `v_moyen_apres_1030_pb`,
  `erreur_type_apres_1030_pb` sur P_après,10/30 (chacun avec son propre G).
- `baisse_1030_pb` = `v_moyen_avant_1030_pb` − `v_moyen_apres_1030_pb` (positif : la pression a baissé) ;
  `erreur_type_baisse_pb` = racine(ET_avant² + ET_après²) (les deux périodes n'ont aucun mois commun, donc aucune covariance
  groupée) ; `borne_inf_90_baisse_pb` = baisse − 1,645 × ET_baisse.
- `alerte_instrument` = 1 si U < 0,5 et `borne_inf_90_baisse_pb` ≤ 0 ; sinon 0.

Pourquoi le groupement par mois : les réouvertures à 10 et 30 ans ont lieu deux jours de suite, celle à 20 ans la semaine
suivante ; leurs fenêtres se chevauchent et partagent les mêmes nouvelles. Pas de bootstrap, pas de tirage : le calcul est
déterministe. On garde la moyenne, sans écrêtage, pour rester comparable à F04 et J05.

**Analyses secondaires, descriptives, sans effet sur le verdict** (dans `verification.json` sous la clé `descriptif`) :
- **S1. La mesure de la fiche, au rendement limite de 13 h.** Moyenne et ET groupée de `p_carte_pb` sur P_après (lignes où il
  est présent) et sur P_avant,10/30. Montre ce que donnait la mesure avec le décalage horaire (et l'écart de règlement non
  corrigé), à côté de V.
- **S2. Forme et absorption.** Moyenne et ET de `montee_pb` et `detente_pb` sur P_après et P_avant,10/30 (la montée et la
  redescente sont-elles symétriques, et laquelle a changé ?) ; moyenne et ET de `v_pa_pb` sur les mêmes ensembles (lignes où il
  est présent) : si le premier ancien a lui aussi un V positif contre les mêmes témoins, la pression déborde sur les voisins, et
  V sous-estime la pression totale.
- **S3. 2023, le 30 ans et le reste.** V̄ par année (2022 à 2026) et par échéance sur P_après ; V̄ sur P_après sans 2023 **et**
  sans le 30 ans ; V̄ des 5 réouvertures à 20 ans d'avant 2022 ; V̄ par échéance sur P_avant,10/30 ; écart-type de V
  (dénominateur n − 1) sur P_après et sur P_avant,10/30, pour le comparer aux hypothèses de la section 7.

## 7. Arithmétique de puissance

Aucune valeur de V n'a été vue : sa dispersion est une supposition, déclarée comme telle.

**Ce que disent les chiffres du registre.**
- J05 : erreur type groupée de Δ = 0,3733 pb avec 206 et 116 réouvertures. La dispersion « efficace » par réouverture (qui
  inclut déjà l'effet du groupement par mois) vaut 0,3733 / racine(1/206 + 1/116) = **3,2 pb** (note de nouveauté, correction 5).
- F04 : V (même forme 2E(J) − E(J−5) − E(J+5), sur des écarts de courbes) a un écart-type de 2,57 pb et un facteur de
  groupement de 1,12, soit 2,9 pb efficaces.

**Ce qui change pour V.** Le mouvement de l'après-midi, première source de bruit de J05 (2,5 à 4 pb), disparaît (A1). S'ajoutent
la seconde jambe (J à J+5), le bruit d'évaluation de douze prix FedInvest (arrondi au 1/32 de point de prix dans les années
anciennes : environ 0,3 pb sur V au total), les variations de pente entre le titre et ses témoins (6 à 12 mois plus courts) et
les variations de cherté propres au titre courant en pension (repo). D'où trois hypothèses :

| Cas | σ efficace de V | ET de μ_après (117) | ET avant, 10/30 (192) | ET de la baisse (192 et 78) | Effet détectable à 80 % (L > 0) |
|---|---|---|---|---|---|
| Favorable (bruit de prix seulement) | 2,0 pb | 0,18 | 0,14 | 0,27 | 0,46 pb |
| **Central (dispersion de J05)** | **3,2 pb** | **0,30** | **0,23** | **0,43** | **0,74 pb** |
| Défavorable (√2 × J05 : deux jambes aussi bruitées que J05) | 4,5 pb | 0,42 | 0,32 | 0,60 | 1,03 pb |

(ET ≈ σ/√N ; effet détectable = (1,645 + 0,84) × ET.)

**Probabilité de chaque verdict**, par simulation de lois normales sous ces hypothèses (4 000 tirages, 117 réouvertures en 39
mois dont 24 en 2023, 192 avant 2022 en 96 mois ; la règle complète de la section 8, gardes de données mises à part) :

| σ | Niveau avant (10/30) | Vrai μ_après | Lecture | survit | éliminée | non concluant |
|---|---|---|---|---|---|---|
| 2,0 | 1,0 | 1,0 | mesure | 100 % | 0 % | 0 % |
| 2,0 | 1,0 | 0,5 | mixte | 85 % | 5 % | 9 % |
| 2,0 | 1,0 | 0 | marché | 6 % | 84 % | 10 % |
| **3,2** | 1,0 | 1,0 | mesure | **95 %** | 0 % | 5 % |
| **3,2** | 1,0 | 0,5 | mixte | 53 % | 5 % | 42 % |
| **3,2** | 1,0 | 0 | marché | 5 % | **49 %** | 46 % |
| 3,2 | 0,5 | 0,5 | mesure, instrument faible | 51 % | 2 % | 47 % |
| 3,2 | 0,5 | 0 | marché, instrument faible | 5 % | 26 % | 68 % |
| 3,2 | 0 | 0 | instrument aveugle | 5 % | 5 % | 90 % |
| 4,5 | 1,0 | 1,0 | mesure | 75 % | 0 % | 25 % |
| 4,5 | 1,0 | 0 | marché | 5 % | 28 % | 67 % |

**Lecture, sans enjoliver.**
- Un verdict à tort est rare : « survit » quand la pression a vraiment disparu arrive 5 à 6 % du temps ; « éliminée » quand la
  pression est restée entière, jamais (0 %), et environ 5 % quand elle a été divisée par deux.
- Le test est **plus apte à confirmer « mesure » qu'à l'éliminer**. Au cas central, il confirme une pression restée à 1 pb
  95 fois sur 100, mais n'élimine une pression disparue qu'une fois sur deux, et rend « non concluant » l'autre fois.
- **Si les témoins absorbent la pression** (instrument aveugle), le test ne dit pas « marché » à tort : il rend « non
  concluant » neuf fois sur dix. C'est le rôle de la condition d'instrument.
- Le bruit n'a pas de remède raisonnable au-delà de ce qui est fait : les réouvertures sont ce qu'elles sont (117 après 2021),
  et les données intrajournalières ne sont pas publiques. L'écart-type de V rapporté en S3 dira, après coup, quel cas était le
  bon.

**Coût.** Une requête D1 (1 Mo), 905 pages FedInvest (environ 45 minutes, une fois, en cache) ; calcul de quelques secondes
sur un portable.

## 8. Règle de verdict

Le verdict s'applique aux nombres du vérificateur. La règle est écrite pour que l'ordre d'évaluation ne change rien.

**En mots.**
- **Survit** = la pression est encore présente après 2021 : la borne basse de l'IC à 90 % de μ_après est au-dessus de 0
  (rejet unilatéral à 5 % de « marché »), la borne haute n'exclut pas une pression de 0,5 pb, et la moyenne reste positive sans
  2023 comme sans le 30 ans. Donc la disparition vue par F04 dans la courbe du Trésor ne se retrouve pas sur les prix du marché.
- **Éliminée** = la borne haute de l'IC à 90 % de μ_après est sous 0,5 pb (une pression de la taille que prédit « mesure » est
  exclue à 5 % unilatéral), **et** l'instrument voit, sur les 10 et 30 ans, une baisse significative entre 2010-2021 et
  2022-2026 (borne basse à 90 % de la baisse au-dessus de 0). Si en même temps la borne basse de μ_après est au-dessus de 0, il
  reste une petite pression : c'est aussi « éliminée », car elle est trop faible pour que la mesure explique la disparition de
  F04.
- **Non concluant** = l'IC de μ_après contient à la fois 0 et 0,5 ; ou la pression est significativement positive mais
  disparaît sans 2023 ou sans le 30 ans ; ou μ_après est petit mais l'instrument ne voit pas de baisse depuis 2010-2021 (les
  témoins ont pu absorber la pression) ; ou une garde de données se déclenche.

**Non concluant** si l'une de ces conditions tient :
- `schema_ok` < 1 ;
- `n_apres` < 105, `n_grappes_apres` < 35, `n_avant_1030` < 175 ou `n_grappes_avant_1030` < 88 ;
- `n_temoins_figes` > 47 ;
- `ecart_max_rdt_pb` > 0,05 ;
- `marge_zone_grise` ≥ 0 ;
- `alerte_robustesse` ≥ 1 ;
- `alerte_instrument` ≥ 1 ;
- (protocole) une donnée nommée manque, ou l'expérimentateur et le vérificateur diffèrent de plus que la tolérance.

**Survit** si toutes ces conditions tiennent : `borne_inf_90_apres_pb` > 0 ; `borne_sup_90_apres_pb` ≥ 0,5 ;
`min_robustesse_pb` > 0 ; `schema_ok` ≥ 1 ; `n_apres` ≥ 105 ; `n_grappes_apres` ≥ 35 ; `n_avant_1030` ≥ 175 ;
`n_grappes_avant_1030` ≥ 88 ; `n_temoins_figes` ≤ 47 ; `ecart_max_rdt_pb` ≤ 0,05.

**Éliminée** sinon, c'est-à-dire : gardes passées, `borne_sup_90_apres_pb` < 0,5 et `borne_inf_90_baisse_pb` > 0.
(Vérification des cas : si L ≤ 0 et U ≥ 0,5, la marge est ≥ 0 → non concluant ; si L > 0, U ≥ 0,5 et la robustesse manque →
alerte → non concluant ; si U < 0,5 et la baisse n'est pas significative → alerte → non concluant ; si U < 0,5 et la baisse est
significative → éliminée ; si L > 0, U ≥ 0,5 et robustesse tenue → survit.)

**Justification de chaque seuil.**
- **0 (borne basse de μ_après).** « Marché » prédit μ_après = 0, comme le V de F04 après 2021 (0,05 pb). Survivre, c'est
  rejeter cette lecture.
- **0,5 pb (borne haute de μ_après).** La plus petite pression qu'implique encore « mesure » d'après F04-bis. Dans F04, V passe
  d'environ 1,38 à 0,05 pb (baisse de 1,33). F04-bis attribue au moins 0,45 pb de V au seul changement de méthode (borne basse
  de son IC à 95 %). La part « marché » de la baisse vaut donc au plus 1,33 − 0,45 = 0,88 pb, et la pression de marché après
  2021 au moins 1,38 − 0,88 = **0,50 pb**. Une borne haute sous 0,5 exclut même la version la plus faible de « mesure ». Ce
  seuil suppose que V avec témoins et V de F04 ont la même échelle ; la condition d'instrument protège en partie contre une
  échelle plus basse. C'est aussi le seuil de J05, ce qui garde les deux tests comparables.
- **Condition d'instrument (borne basse de la baisse > 0).** Sans elle, des témoins qui absorbent la pression donneraient
  μ_après ≈ 0 et un faux « marché ». Elle est faite sur les 10 et 30 ans, de même composition avant et après (le 20 ans pèse un
  tiers après 2021 et n'a que 5 lignes avant). Elle ne conditionne pas la survie : une pression significativement positive après
  2021 est présente, quel que soit son niveau d'avant.
- **Robustesse (moyenne > 0 sans 2023 et sans 30 ans).** Reprise de la fiche ; 2023 (3,34 pb dans J05) et le 30 ans portaient le
  résultat de J05. Le seuil de 0 sur une moyenne ponctuelle est volontairement simple : il ne bloque qu'une survie entièrement
  portée par une année ou une échéance.
- **90 % et 1,645.** Deux tests unilatéraux à 5 %, un contre chaque lecture, comme J05. Avec 39 mois après 2021, la valeur de
  Student à 38 degrés de liberté (1,686) déplacerait les bornes d'environ 0,01 pb pour ET = 0,3 : négligeable, et la loi normale
  reste plus simple à défendre.
- **105, 35, 175, 88.** Comptes attendus : 117 réouvertures en 39 mois après 2021 ; 192 en 96 mois avant (10 et 30 ans). On
  tolère la perte d'environ 10 % des lignes (pages absentes, prix figés) et de quelques mois. Au-delà, la perte ne serait plus
  accidentelle et l'arithmétique de puissance ne vaudrait plus.
- **47 témoins figés.** 5 % des quelque 940 places de témoins de P. Aucun figé sur 63 témoins vérifiés ; au-delà de 5 %, FedInvest ne
  donnerait plus des prix de marché pour les anciens, et V comparerait un prix à une évaluation gelée.
- **0,05 pb d'écart de recalcul.** Deux implémentations correctes de 5.2 s'accordent à 10⁻⁴ pb près ; 0,05 pb reste dix fois
  sous le seuil de 0,5 pb.

**Tolérances entre expérimentateur et vérificateur.** 0 sur les comptes, `schema_ok`, `n_temoins_figes` et les deux alertes ;
0,005 pb sur les moyennes, les erreurs types, la baisse et `min_robustesse_pb` ; 0,01 pb sur les bornes et la marge ; 0,05 pb
sur `ecart_max_rdt_pb`.

## 9. Limites

1. **Les témoins absorbent une partie de la pression** (Fleming, Liu et Nguyen 2026, section 4.3 et tableau A3 ; Sigaux 2018 ;
   Krishnamurthy 2002). V mesure la pression **propre au titre rouvert, au-delà de ses voisins** (deuxième à quatrième anciens),
   pas la pression totale du secteur. Le biais va vers zéro dans les deux périodes : un « survit » est donc prudent ; un
   « éliminée » exige que l'instrument ait vu la pression avant 2022 (condition d'instrument). Un « non concluant » par
   `alerte_instrument` voudra dire : « cet instrument ne sait pas voir la pression », pas « la pression a disparu ».
   **C'est la limite la plus sérieuse du test.**
2. **V avec témoins n'est pas V de F04.** Le pont « présent ici ⇒ la disparition de F04 vient de la mesure » suppose que les deux
   mesurent la même pression, l'un contre une courbe lisse, l'autre contre des voisins. Le seuil de 0,5 pb repose sur cette
   équivalence d'échelle.
3. **FedInvest donne des évaluations de fin de journée, pas des transactions**, sans source ni heure documentées. Si les anciens
   étaient évalués par un modèle ancré sur une courbe, une courbe reviendrait par la porte de derrière. La garde des prix figés
   n'attrape que les prix gelés. L'accès demande un témoin de session ; un blocage durable rend le test non concluant.
4. **Le sommet de 13 h n'est pas mesuré** (section 3.1) : V à la clôture le sous-estime, et un changement de vitesse de
   résorption après 2021 se confondrait avec une baisse de pression. S1 en donne une idée bruitée.
5. **Un effet d'offre permanent compte comme pression** dans la première jambe : si le titre rouvert reste plus cher ou moins cher
   après la réouverture (sa cherté en pension baisse quand l'encours augmente), V le compte à moitié, comme F04 et Fleming, Liu
   et Nguyen. Une dérive linéaire de la prime, elle, s'annule.
6. **Composition.** Le 20 ans pèse un tiers de μ_après mais n'existe presque pas avant 2022 ; la comparaison avant/après ne
   porte que sur les 10 et 30 ans. Les 8 premières réouvertures à 20 ans sont perdues faute de témoins.
7. **Puissance asymétrique.** Au cas central, le test confirme bien « mesure » mais n'élimine une pression disparue qu'une fois
   sur deux (section 7).
8. **Données déjà en partie regardées.** La coupure de 2022, la prédiction et les seuils viennent de F04, F04-bis et J05. Les
   valeurs de V, elles, n'ont jamais été vues ; la première jambe de la fiche (rendement limite moins rendement à J−5), déjà
   publiée par J05, n'entre que dans S1.
9. **Moyenne sensible aux valeurs extrêmes.** Mars 2020 (avant) et mars 2023 (la réouverture à 10 ans du 2023-03-08 a sa
   fenêtre sur la faillite de SVB) peuvent peser ; la condition « sans 2023 » couvre la seconde.
10. **Champ.** Réouvertures nominales à 10, 20 et 30 ans seulement ; rien sur les nouvelles émissions ni sur les échéances de
    2 à 7 ans.

## 10. Ce qu'on écrira dans chaque cas

- **Survit.** « Mesurée sans aucune courbe — rendement du titre rouvert contre la moyenne de trois titres témoins de la même
  famille (hors titre courant et premier ancien), tous à la même clôture FedInvest — la pression des réouvertures à 10, 20 et
  30 ans vaut encore X pb en 2022-2026 (IC à 90 % : Y à Z pb, au-dessus de 0, et positive sans 2023 comme sans le 30 ans), donc
  la disparition vue après 2021 dans la courbe du Trésor (F04) vient de la mesure et non du marché, au moins en partie, sans que
  ce test dise quelle part de la pression d'avant 2022 subsiste. »
- **Éliminée.** « Mesurée de la même façon, la pression après 2021 ne dépasse pas Z pb (borne haute de l'IC à 90 %, sous les
  0,5 pb qu'impliquerait encore une explication par la mesure), alors que le même instrument voit une baisse significative
  depuis 2010-2021 sur les 10 et 30 ans, donc la disparition vue dans la courbe du Trésor est d'abord un phénomène de marché
  [si Y > 0 : une petite pression subsiste, trop faible pour que le changement de méthode explique la cassure de F04], ce qui
  laisse à expliquer pourquoi F04-bis trouvait un effet de méthode. »
- **Non concluant.** « Le test ne tranche pas, pour la raison suivante : [IC à 90 % de Y à Z pb, qui contient à la fois 0 et
  0,5 pb / pression positive mais portée par 2023 ou par le 30 ans / pression faible après 2021 mais aucune baisse visible
  depuis 2010-2021, les témoins ayant pu absorber la pression / échantillon sous le minimum / prix FedInvest inaccessibles ou
  figés / schéma violé / désaccord entre expérimentateur et vérificateur] ; on ne conclut ni que la pression a disparu du marché,
  ni qu'elle n'a disparu que de la courbe du Trésor. »

## 11. Règle lisible par machine

```json
{
  "id": "K11",
  "fichier_analyse": "K11_analyse.csv",
  "champs_verification": [
    "schema_ok",
    "n_apres",
    "n_grappes_apres",
    "n_avant_1030",
    "n_grappes_avant_1030",
    "n_temoins_figes",
    "ecart_max_rdt_pb",
    "v_moyen_apres_pb",
    "erreur_type_apres_pb",
    "borne_inf_90_apres_pb",
    "borne_sup_90_apres_pb",
    "marge_zone_grise",
    "v_moyen_apres_sans_2023_pb",
    "v_moyen_apres_sans_30_pb",
    "min_robustesse_pb",
    "alerte_robustesse",
    "v_moyen_avant_1030_pb",
    "erreur_type_avant_1030_pb",
    "v_moyen_apres_1030_pb",
    "erreur_type_apres_1030_pb",
    "baisse_1030_pb",
    "erreur_type_baisse_pb",
    "borne_inf_90_baisse_pb",
    "alerte_instrument"
  ],
  "survit_si": [
    {"champ": "borne_inf_90_apres_pb", "operateur": ">", "seuil": 0},
    {"champ": "borne_sup_90_apres_pb", "operateur": ">=", "seuil": 0.5},
    {"champ": "min_robustesse_pb", "operateur": ">", "seuil": 0},
    {"champ": "schema_ok", "operateur": ">=", "seuil": 1},
    {"champ": "n_apres", "operateur": ">=", "seuil": 105},
    {"champ": "n_grappes_apres", "operateur": ">=", "seuil": 35},
    {"champ": "n_avant_1030", "operateur": ">=", "seuil": 175},
    {"champ": "n_grappes_avant_1030", "operateur": ">=", "seuil": 88},
    {"champ": "n_temoins_figes", "operateur": "<=", "seuil": 47},
    {"champ": "ecart_max_rdt_pb", "operateur": "<=", "seuil": 0.05}
  ],
  "non_concluant_si": [
    {"champ": "schema_ok", "operateur": "<", "seuil": 1},
    {"champ": "n_apres", "operateur": "<", "seuil": 105},
    {"champ": "n_grappes_apres", "operateur": "<", "seuil": 35},
    {"champ": "n_avant_1030", "operateur": "<", "seuil": 175},
    {"champ": "n_grappes_avant_1030", "operateur": "<", "seuil": 88},
    {"champ": "n_temoins_figes", "operateur": ">", "seuil": 47},
    {"champ": "ecart_max_rdt_pb", "operateur": ">", "seuil": 0.05},
    {"champ": "marge_zone_grise", "operateur": ">=", "seuil": 0},
    {"champ": "alerte_robustesse", "operateur": ">=", "seuil": 1},
    {"champ": "alerte_instrument", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "schema_ok": 0,
    "n_apres": 0,
    "n_grappes_apres": 0,
    "n_avant_1030": 0,
    "n_grappes_avant_1030": 0,
    "n_temoins_figes": 0,
    "ecart_max_rdt_pb": 0.05,
    "v_moyen_apres_pb": 0.005,
    "erreur_type_apres_pb": 0.005,
    "borne_inf_90_apres_pb": 0.01,
    "borne_sup_90_apres_pb": 0.01,
    "marge_zone_grise": 0.01,
    "v_moyen_apres_sans_2023_pb": 0.005,
    "v_moyen_apres_sans_30_pb": 0.005,
    "min_robustesse_pb": 0.005,
    "alerte_robustesse": 0,
    "v_moyen_avant_1030_pb": 0.005,
    "erreur_type_avant_1030_pb": 0.005,
    "v_moyen_apres_1030_pb": 0.005,
    "erreur_type_apres_1030_pb": 0.005,
    "baisse_1030_pb": 0.005,
    "erreur_type_baisse_pb": 0.005,
    "borne_inf_90_baisse_pb": 0.01,
    "alerte_instrument": 0
  }
}
```
