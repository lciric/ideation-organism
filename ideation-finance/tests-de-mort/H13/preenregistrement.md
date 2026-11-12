# H13 — Préinscription du test de mort

Rédigé le 2026-11-12 par le rédacteur de préinscription. Ce texte est figé une fois scellé. Le rédacteur n'a lancé aucune
analyse ; ce qu'il a vu des données est listé à la fin de la section 4.

## 1. Ce que ce test peut dire, et ce qu'il ne peut pas dire

La fiche demande si, le jour de la publication de l'emploi américain, le taux à 2 ans réagit à la partie du chiffre qui sera
effacée par les révisions des deux mois suivants. Elle lit un coefficient positif comme le « signe que le marché ne filtre pas
le bruit ». Les trois juges et la note de nouveauté rejettent cette lecture, et ce texte la retire (amendement A1).

Ce que le test mesure : **le sens et la taille du lien, le jour même, entre la variation du taux à 2 ans et la partie du premier
chiffre révisée ensuite.** Rien de plus. Il ne sépare pas « le marché filtre mal » de « le marché filtre au mieux mais ne peut
pas voir l'erreur ce jour-là ». Il ne dit rien du retour du taux les jours suivants.

Ce qui le rend utile quand même : la fiche et le travail publié le plus proche (Gilbert, 2011, sur les actions) prédisent des
signes opposés pour ce même coefficient. Aucune régression de ce type sur un taux du Trésor n'a été trouvée par la note de
nouveauté. Le signe n'est donc pas connu d'avance.

## 2. Question, hypothèses rivales et prédiction chiffrée

### Notations

Pour une publication donnée, qui annonce pour la première fois l'emploi du mois m :

- A1 : première estimation de la variation mensuelle de l'emploi salarié (celle que le marché lit à 8 h 30) ;
- A3 : troisième estimation de la même variation, publiée deux mois plus tard ;
- **N = (A1 − A3) / 100 000** : la partie du premier chiffre qui sera révisée. N > 0 : le premier chiffre était trop haut ;
- Δy : variation du taux à 2 ans entre la clôture de la veille et la clôture du jour, en points de base (pb) ;
- μ : ce que le marché attendait la veille (le consensus). **Non observé ici** : aucune source gratuite ne remonte à 1990.

**β** est le coefficient de N dans la régression de Δy sur N et quatre contrôles (section 6), en pb par 100 000 emplois.

### Ce que β contient

Écrivons la réaction du taux comme : Δy = κ × (A1 − μ) + δ × N + autres nouvelles du jour. κ est la sensibilité du taux au
chiffre publié. δ dit si, à chiffre publié donné, le taux penche déjà vers la valeur future. Alors, si les contrôles font leur
travail :

**β ≈ κ × p + δ**, où p est la pente de la surprise du jour (A1 − μ) sur N.

p dépend de la nature des révisions, pas du marché :
- **révisions de type « bruit »** : A1 = A3 + erreur, l'erreur étant sans lien avec A3. Alors N est cette erreur, elle est tout
  entière dans le chiffre publié, et p = 1 ;
- **révisions de type « information nouvelle »** : A3 = A1 + correction imprévisible le jour même. Alors N est sans lien avec
  le chiffre publié, et p = 0.

Raisonnement du rédacteur, non vérifié : la troisième estimation ajoute les réponses tardives des entreprises à celles déjà
comptées dans la première. Si les retardataires ressemblent aux premiers répondants, la correction est sans lien avec A3 et
liée à A1 : c'est le type « bruit », p proche de 1. L'analyse S1 mesure p avec une attente grossière.

### Les trois lectures et ce qu'elles prédisent

| Lecture | Ce qu'elle suppose | Prédiction pour β (pb par 100 000) |
|---|---|---|
| **Fiche H13** | Le chiffre publié contient une erreur (p > 0) et le taux suit le chiffre publié, erreur comprise (δ = 0) | **+1 à +3**, soit un tiers à la moitié d'une sensibilité κ de 4 à 6 |
| **Lecture rivale, tirée de Gilbert (2011)** | Le jour même, les prix vont dans le sens de la révision à venir : le marché en sait plus que le chiffre publié (δ < 0) | **négatif ou nul** : entre −κ (environ −4 à −6, si la révision est une information que le marché a déjà) et 0 (si la révision corrige une erreur que le marché voit entièrement). Aucun chiffre publié pour le taux à 2 ans |
| **Manuel** | Première estimation efficace (p = 0), marché sans information privée (δ = 0) | **0** |

Chiffres de la note de nouveauté sur κ : 3,8 à 8 pb par 100 000 selon l'échéance et la période ; aucun ne couvre le 2 ans
sur 1990-2025. La fourchette de la fiche (4 à 6) est plausible, non vérifiée.

### L'objection principale des juges, traitée de front

Un marché parfaitement rationnel qui reçoit un chiffre entaché d'une erreur invisible réagit au chiffre entier, donc aussi à
l'erreur. Il réagit seulement moins fort que si le chiffre était exact : κ est atténué (c'est ce que montrent Hautsch et Hess,
2007, d'après la note). Dans ce cas β = κ atténué × p > 0, exactement comme dans la lecture de la fiche. **Un β positif est
donc ce qu'on attend d'un marché rationnel dès que les révisions sont du type « bruit ».** Il ne prouve aucun défaut.

Pour montrer un défaut de filtrage, il faudrait comparer κ observé au κ qu'un marché rationnel devrait avoir compte tenu de la
précision du chiffre. Il faut pour cela le consensus et un modèle de la précision. Ce test n'a ni l'un ni l'autre.

Ce que chaque résultat voudra dire :

- **β positif.** Le taux à 2 ans a bougé, le jour même, dans le sens de la partie du chiffre effacée ensuite. Il faut à la
  fois que le premier chiffre contienne une erreur (p > 0) et que le marché n'ait pas su la corriger d'avance (κ × p > −δ).
  Cela contredit la lecture rivale dans sa forme forte. Cela ne dit pas si le marché filtre bien ou mal.
- **β nul, mesuré avec précision** (intervalle à 95 % tout entier entre −1 et +1). Le taux ne porte pas la partie révisée.
  Trois explications que le test ne sépare pas : les révisions sont de l'information nouvelle (p = 0) ; le marché voit
  l'erreur et l'écarte (δ = −κ × p) ; les deux forces existent et se compensent. S1 aide à trier : si p mesuré est proche de 1,
  la première explication tombe.
- **β négatif.** Le taux a bougé dans le sens de la valeur future, contre l'erreur du jour. Deux explications non séparées :
  le marché en sait plus que le chiffre publié (lecture rivale) ; ou les premières estimations sous-réagissent, la révision
  prolonge la surprise au lieu de la corriger (p < 0), et le taux suit simplement la surprise.
- **β nul, mesuré sans précision.** On ne sait pas.

### La règle ne favorise aucune lecture

- Le test est bilatéral (|t| ≥ 1,96), alors que la fiche prévoyait un test unilatéral en sa faveur.
- Les seuils sont en miroir : la fiche survit si t ≥ +1,96 ; la lecture rivale est dite « appuyée » si t ≤ −1,96 ; l'effet
  de la fiche est dit « exclu » si la borne haute de l'intervalle à 95 % est ≤ +1 ; un effet rival d'au moins 1 pb est dit
  « exclu » si la borne basse est ≥ −1.
- Une asymétrie demeure, et elle vient des prédictions, pas de la règle : la fiche s'engage sur un signe strict, la lecture
  rivale admet zéro. Un zéro précis élimine donc la fiche sans éliminer la lecture rivale.

Le verdict machine ne connaît que la fiche (« survit », « éliminée », « non concluant »). La phrase de conclusion
(section 10) distingue quatre cas.

Avis du rédacteur, sans effet sur la règle : p proche de 1 lui paraît probable, donc un β positif aussi ; la puissance
(section 7) rend « non concluant » l'issue la plus probable si l'effet vrai est de 1 pb ou moins.

## 3. Amendements déclarés

| N° | Test de la fiche | Test préinscrit | Raison |
|---|---|---|---|
| A1 | β > 0 est le « signe que le marché ne filtre pas le bruit » | β > 0 veut dire : le taux a porté, le jour même, la partie du chiffre révisée ensuite. Aucune conclusion sur la qualité du filtrage | Faille principale des juges (section 2) : un marché rationnel qui ne voit pas l'erreur donne le même signe |
| A2 | Seuil unilatéral, p < 0,05 | Seuil bilatéral, t ≥ 1,96 | Note de nouveauté : Gilbert (2011) prédit le signe contraire. Un test unilatéral suppose le signe connu ; il ne l'est pas |
| A3 | L'idée meurt si β ≤ 0 ou si p > 0,05 | Éliminée seulement si la borne haute de l'intervalle à 95 % est ≤ 1 pb. Si t < 1,96 mais que la borne haute dépasse 1 : non concluant | Ne pas rejeter zéro n'est pas montrer zéro. La fiche reconnaît elle-même que le test « devient non concluant si l'effet vrai est ≤ 1 » |
| A4 | N = première estimation − troisième estimation, « lue deux millésimes plus tard » | Même définition, rendue mécanique : A1 est lue dans le premier millésime qui contient le mois m ; A3 dans le premier millésime de publication dont le dernier mois est ≥ m + 2. Chaque variation est calculée à l'intérieur d'un seul millésime | Les publications retardées (1996, 2013, 2025) cassent la règle « deux millésimes plus tard ». On garde la troisième estimation et non la valeur finale : la valeur finale mêle des révisions de référence et de méthode publiées jusqu'à des années après, et la question de la fiche porte sur les deux mois suivants |
| A5 | « Exclusions (mois de révision annuelle) » fixées par l'humain | Détection mécanique des millésimes de révision large (section 4, étape 5). Une publication sort de l'échantillon si l'un des millésimes qui servent à la construire, du sien à celui de la troisième estimation, est de révision large | Note de nouveauté : la révision de référence change aussi les variations mensuelles et les coefficients saisonniers ; N ne serait plus la révision d'échantillon. Le jour d'une révision large, les révisions des mois précédents (les contrôles) sont elles aussi d'une autre nature. Une règle mécanique évite une liste faite à la main, et ne dépend pas du mois où tombait la révision avant 2004 (juin, de mémoire, non vérifié) |
| A6 | Rien sur les millésimes qui ne sont pas des publications, ni sur les publications doubles | Un millésime n'est une publication que s'il apporte au moins un mois nouveau. La publication du 2025-12-16, qui en apporte deux, sort de l'échantillon | Note de nouveauté : trois millésimes de correction (2002-12-09, 2003-10-10, 2020-05-11) ; octobre et novembre 2025 publiés ensemble, donc deux premiers chiffres le même jour |
| A7 | Rien sur 2020 | Sort de l'échantillon toute publication dont \|A1\| > 1 000 000 emplois ou \|A1 − A3\| > 500 000 emplois | Au printemps et à l'été 2020, les variations de l'emploi valent 10 à 200 fois la normale et le taux à 2 ans est collé à zéro. Ces quelques points pèseraient plus que tous les autres et mesureraient le plancher des taux. La règle porte sur le régresseur seul, jamais sur le taux : elle ne biaise pas la pente. De mémoire, non vérifié, elle écarte environ six publications, toutes en 2020. S3 les remet |
| A8 | Rien sur les mois de grève ou d'ouragan | Aucune liste, aucune exclusion à ce titre | (i) Une grève déplace A1 et A3 de la même quantité : elle s'annule dans N. (ii) Un ouragan fait baisser le taux de réponse et grossit N : c'est le phénomène étudié, pas une anomalie. (iii) Aucune donnée gratuite ne permet de dater ces mois mécaniquement ; une liste faite à la main serait un choix libre de plus. Les cas extrêmes sont pris par A7, et la tendance de A9 est une médiane, insensible à un mois aberrant |
| A9 | Contrôles : révisions des deux mois précédents, variation du taux de chômage | Les mêmes, définis exactement (section 5), plus la médiane des douze dernières variations mensuelles connues la veille. Pas de contrôle pour les salaires | Faille des juges : si l'erreur de première estimation suit le cycle, β est biaisé. La tendance connue la veille capte le cycle et ne peut pas être causée par le chiffre du jour. Les salaires horaires ne sont pas ajoutés : sans consensus, leur niveau mesure mal leur surprise, et leurs millésimes anciens n'ont pas été vérifiés |
| A10 | « L'identification n'exige pas le consensus » | Le consensus manque et cela a trois effets, écrits ici. (1) κ n'est pas mesuré : on ne peut pas dire quelle part de la réaction normale β représente. (2) La vraie surprise du jour reste dans le résidu : plus de bruit, mais pas de biais si elle est sans lien avec N. (3) Si N est lié à la vraie surprise, β est biaisé du signe de ce lien : vers le négatif si les premières estimations sous-réagissent, vers le positif si elles sur-réagissent. S1 et S2 donnent une mesure grossière de p et de κ avec une attente naïve | Failles des trois juges et point (5) de la note : Aruoba (2008) trouve des révisions prévisibles, l'orthogonalité n'est pas acquise |
| A11 | Taux zéro-coupon ajusté `SVENY02` ; `DGS2` en recoupement | `DGS2` pour la statistique ; `SVENY02` dans le fichier pour contrôler l'alignement des dates | Note de nouveauté : `SVENY02` manque quatre jours de publication, `DGS2` un seul. `DGS2` est un taux coté, pas le produit d'un ajustement de courbe. Son arrondi au point de base ajoute environ 0,4 pb de bruit, négligeable devant 6 à 9 pb |
| A12 | « Erreurs robustes » | Erreurs robustes HC3, formule écrite (section 6) | Deux personnes doivent obtenir le même nombre. HC3 est la variante prudente quand quelques points du régresseur sont loin de la moyenne |
| A13 | Placebo : coefficient sur la variation de la veille « nul » | Même placebo, avec un seuil : si \|t\| ≥ 1,96, le test est non concluant | La veille, le chiffre n'est pas publié. Un lien entre N et le taux de la veille voudrait dire que N est lié à quelque chose de déjà connu (cycle, inscriptions au chômage du jeudi) : β ne serait plus lisible |
| A14 | Projections locales à 1, 5, 10, 21 et 42 jours | Retirées du test | Faille des juges, et la fiche le dit : erreur type d'environ 2,4 pb à 21 jours, aucune puissance. Peut être fait après, hors verdict, annoncé comme exploratoire |
| A15 | « L'agent qui construit N n'a pas accès aux taux » | L'expérimentateur construit et enregistre les colonnes d'emploi, avec leur sha256, avant de télécharger les taux | Le protocole n'a qu'un expérimentateur ; l'ordre de construction, journalisé, remplace la séparation des agents |

Inchangés : la variable N, le taux à 2 ans, la fenêtre d'un jour, la période (publications du 1990-01-01 au 2025-12-31), la
régression par moindres carrés, les trois contrôles de la fiche.

## 4. Données

Toutes publiques, sans compte. L'expérimentateur enregistre chaque fichier brut dans `tests-de-mort/H13/brut/`, avec la date de
téléchargement et le sha256. Toutes les adresses ci-dessous ont répondu 200 le 2026-11-12.

**D1. Liste des dates de millésime de l'emploi salarié (`PAYEMS`).**
`https://alfred.stlouisfed.org/series/downloaddata?seid=PAYEMS` (HTML, environ 100 ko). Les dates sont les balises
`<option value="AAAA-MM-JJ">` du menu `form[selected_vintage_dates][]`. 861 dates, de 1955-05-06 à 2026-11-06. On garde les
dates du 1989-12-01 au 2026-03-31 : **438 attendues**, la première étant 1989-12-08.

**D2. Niveaux de `PAYEMS` par millésime.** Syntaxe vérifiée par la note de nouveauté, par lots de **12 millésimes au plus** :

```
https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS,PAYEMS,…(n fois)&vintage_date=AAAA-MM-JJ,AAAA-MM-JJ,…(n dates)
```

Réponse : une ligne par mois depuis 1939 (`observation_date` = premier jour du mois), une colonne `PAYEMS_AAAAMMJJ` par
millésime, en milliers d'emplois, entiers, corrigés des variations saisonnières ; champ vide pour un mois pas encore publié.
Trois pièges, à contrôler à chaque lot :
- au-delà de 12 millésimes, la réponse est tronquée sans message : vérifier que l'en-tête compte exactement n colonnes, dans
  l'ordre demandé ;
- la même requête sur `fred.stlouisfed.org/graph/fredgraph.csv` ignore `vintage_date` et rend le millésime courant : ne
  jamais l'utiliser pour D2 ou D3 ;
- une date qui n'est pas un millésime ne produit pas d'erreur (testé sur `UNRATE` : la colonne porte la date demandée) : ne
  demander que des dates de D1.

37 lots pour 438 dates. Si cette adresse cesse de répondre, le téléchargement groupé de la même page D1 (`POST`, décrit dans
la note de nouveauté) est admis, à noter dans `ecarts.md`. Aucune autre source ne remplace ALFRED.

**D3. Taux de chômage par millésime (`UNRATE`).** Même syntaxe avec `id=UNRATE,…` et, comme dates, les dates de publication
de l'étape 2 ci-dessous. Pour cent, une décimale. Vérifié sur les menus : toutes les dates de publication de la fenêtre sont
des millésimes de `UNRATE`.

**D4. Taux à 2 ans.** `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2` : colonnes `observation_date,DGS2`, quotidien
depuis 1976-06-01, pour cent par an, deux décimales, champ vide les jours fériés. Taux à échéance constante du Trésor, relevé
en fin de séance.

**D5. Taux zéro-coupon à 2 ans (contrôle d'alignement seulement).**
`https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` (16,7 Mo). Neuf lignes de préambule, puis l'en-tête
qui commence par `Date`. Colonnes utilisées : `Date`, `SVENY02` (pour cent, quatre décimales). Valeur manquante : `NA`.

### Procédure de reconstruction

Notations : L(j ; v) est le niveau du mois j lu dans le millésime v ; Δ(j ; v) = L(j ; v) − L(j−1 ; v), variation mensuelle
calculée **à l'intérieur du seul millésime v** ; fin(v) est le dernier mois dont la valeur n'est pas vide dans v.

1. **Millésimes.** Télécharger D1, puis D2 pour les 438 dates.
2. **Publications.** Parcourir les 438 millésimes dans l'ordre. Le premier (1989-12-08) est une publication. Ensuite, un
   millésime v est une publication si fin(v) est postérieur à fin du millésime qui le précède dans la liste complète ; sinon
   c'est une correction, écartée. Attendu : 3 corrections (2002-12-09, 2003-10-10, 2020-05-11), **435 publications**, dont
   **431** datées du 1990-01-01 au 2025-12-31. Recoupement : les trois corrections sont les seules dates absentes du menu de
   `UNRATE`. Tout autre décompte est écrit dans `ecarts.md` ; le fichier est construit tel que la règle le donne.
   La date de publication est la date du millésime. prec(v) désigne la publication qui précède v.
3. **Pour chaque publication v datée du 1990-01-01 au 2025-12-31**, avec m = fin(v) et m′ = fin(prec(v)) :
   - nombre de mois nouveaux : nombre de mois de m′ + 1 à m (1 en temps normal) ;
   - **première estimation** : A1 = Δ(m ; v) ;
   - **millésime de la troisième estimation** : v3 = la première publication w postérieure à v telle que fin(w) ≥ m + 2 ;
   - **troisième estimation** : A3 = Δ(m ; v3) ;
   - **révision du mois précédent publiée ce jour** : Δ(m′ ; v) − Δ(m′ ; prec(v)) ;
   - **révision du mois d'avant publiée ce jour** : Δ(m′ − 1 ; v) − Δ(m′ − 1 ; prec(v)) ;
   - **tendance connue la veille** : médiane des douze valeurs Δ(j ; prec(v)), j = m′ − 11, …, m′ (moyenne de la 6ᵉ et de
     la 7ᵉ valeur triée).
4. **Taux de chômage du jour.** U(j) lu dans `UNRATE` au millésime daté du jour de publication. Variation publiée :
   U(m) − U(m − 1), dans ce même millésime.
5. **Millésimes de révision large.** Une publication w est « de révision large » si, pour au moins un des dix mois
   j = m′ − 11, …, m′ − 2 (m′ = fin(prec(w))), L(j ; w) ≠ L(j ; prec(w)). En temps normal une publication ne retouche que les
   deux derniers mois déjà publiés (m′ et m′ − 1) ; toute retouche plus ancienne signale une révision de référence, de
   coefficients saisonniers, ou une correction. La publication v reçoit `revision_large` = 1 si une publication w de
   révision large vérifie date(v) ≤ date(w) ≤ date(v3).
6. **Enregistrer** les colonnes d'emploi et de chômage dans un fichier intermédiaire, noter son sha256 dans le journal.
   **Ensuite seulement** télécharger D4 et D5.
7. **Calendrier des taux.** C est la liste triée des dates où `DGS2` a une valeur. Pour une date de publication d : la veille
   est la dernière date de C strictement avant d ; l'avant-veille est la date de C qui précède la veille. Si d n'est pas dans
   C, le taux du jour est manquant.

Exemple de contrôle, tiré de la note de nouveauté : publication du 1990-02-02, mois de janvier 1990. A1 = 109 823 − 109 548 =
+275 milliers. v3 = 1990-04-06, A3 = 109 931 − 109 570 = +361 milliers. N = (275 − 361) / 100 = −0,86.

**Ce qui compte comme manquant.**
- Une publication dont une valeur nécessaire manque (taux du jour, de la veille ou de l'avant-veille ; chômage ; troisième
  estimation) : `complet` = 0, hors calcul, comptée. Attendu : au moins 1994-04-01 (Vendredi saint, `DGS2` vide).
- D1, D2, D3 ou D4 injoignable ou de colonnes différentes : le fichier n'est pas construit, le test est non concluant.
- D5 injoignable : colonnes `sveny02_*` vides, noté dans `ecarts.md` ; le contrôle de schéma n° 9 ne porte alors sur rien.
- Moins de 250 publications dans l'échantillon principal : non concluant (section 8).

**Sources non retenues.** Tableau du BLS des trois estimations (`https://www.bls.gov/web/empsit/cesnaicsrev.htm`) : 403 avec
curl d'après la note. Fichier en temps réel de la Fed de Philadelphie : millésimes mensuels sans date de publication.
Consensus des économistes : aucune source gratuite depuis 1990.

**Ce que le rédacteur a vu.** Les deux menus de dates de millésime (`PAYEMS`, `UNRATE`), comparés entre eux et comptés ;
l'en-tête d'un lot de 12 millésimes de `PAYEMS` et le début de sa dernière ligne (`1990-10-01,,`) ; l'en-tête d'une requête
`UNRATE` ; l'en-tête et les deux premières lignes de `DGS2` (juin 1976) ; le préambule, l'en-tête et le début de la première
ligne (1961) de D5. Les seules valeurs d'emploi et de taux de la période étudiée qu'il connaît sont celles citées dans la note
de nouveauté (janvier-février 1990). Les seuils de A7 viennent de sa mémoire des chiffres d'emploi de 2020, pas des taux.
Aucune moyenne, aucune régression, aucune statistique n'a été calculée sur des données ; le tableau de la section 7 est
calculé sur des ordres de grandeur supposés.

## 5. Fichier d'analyse

Nom : `tests-de-mort/H13/H13_analyse.csv`. UTF-8, virgule, point décimal, une ligne d'en-tête, champ vide pour une valeur
manquante, dates au format AAAA-MM-JJ. **Une ligne par publication** datée du 1990-01-01 au 2025-12-31, triée par
`date_publication`. Attendu : 431 lignes.

| Colonne | Type | Unité, contenu |
|---|---|---|
| `date_publication` | date | date du millésime de publication v ; unique |
| `mois_reference` | texte AAAA-MM | m = fin(v), dernier mois publié ce jour |
| `n_mois_nouveaux` | entier | nombre de mois de m′ + 1 à m ; 1 ou 2 |
| `date_millesime_precedent` | date | date de prec(v) |
| `date_millesime_3e` | date | date de v3 ; vide si v3 n'existe pas dans D2 |
| `emploi_1re_k` | entier | A1, milliers d'emplois |
| `emploi_3e_k` | entier | A3, milliers d'emplois ; vide si `date_millesime_3e` est vide |
| `rev_m1_k` | entier | révision, publiée ce jour, de la variation du mois m′, milliers |
| `rev_m2_k` | entier | révision, publiée ce jour, de la variation du mois m′ − 1, milliers |
| `tendance_12m_k` | décimal | médiane des douze dernières variations mensuelles lues dans prec(v), milliers par mois |
| `d_chomage_pt` | décimal | variation publiée du taux de chômage, points de pourcentage |
| `revision_large` | entier | 0 ou 1 (étape 5) |
| `extreme` | entier | 1 si \|`emploi_1re_k`\| > 1000, ou si `emploi_3e_k` est présent et \|`emploi_1re_k` − `emploi_3e_k`\| > 500 ; sinon 0 |
| `date_veille` | date | dernière date de C avant `date_publication` |
| `date_avant_veille` | date | date de C qui précède `date_veille` |
| `dgs2_j` | décimal | `DGS2` à `date_publication`, pour cent, recopié sans arrondi ; vide si absent |
| `dgs2_veille` | décimal | `DGS2` à `date_veille` |
| `dgs2_avant_veille` | décimal | `DGS2` à `date_avant_veille` |
| `sveny02_j` | décimal | `SVENY02` à `date_publication`, pour cent ; vide si `NA` ou absent |
| `sveny02_veille` | décimal | `SVENY02` à `date_veille` ; vide si `NA` ou absent |
| `complet` | entier | 1 si `emploi_3e_k`, `rev_m1_k`, `rev_m2_k`, `tendance_12m_k`, `d_chomage_pt`, `dgs2_j`, `dgs2_veille`, `dgs2_avant_veille` sont tous présents ; sinon 0 |
| `principal` | entier | 1 si `complet` = 1, `n_mois_nouveaux` = 1, `revision_large` = 0 et `extreme` = 0 ; sinon 0 |

**Contrôles de schéma** (le vérificateur les exécute et rapporte `schema_ok` = 1 si tous passent, 0 sinon) :
1. Les 22 colonnes ci-dessus, dans cet ordre, et aucune autre.
2. Entre 425 et 435 lignes ; `date_publication` unique, strictement croissante, entre 1990-01-01 et 2025-12-31.
3. `mois_reference` strictement croissant ; l'écart entre `date_publication` et le premier jour de `mois_reference` est de
   28 à 110 jours civils.
4. `n_mois_nouveaux` ∈ {1, 2} ; `revision_large`, `extreme`, `complet`, `principal` ∈ {0, 1}.
5. `date_millesime_precedent` < `date_publication` ; si elle est présente, `date_millesime_3e` > `date_publication` ;
   `date_avant_veille` < `date_veille` < `date_publication`.
6. `extreme`, `complet` et `principal` valent exactement ce que leur définition donne à partir des autres colonnes.
7. Bornes : \|`emploi_1re_k`\| ≤ 25 000 ; \|`d_chomage_pt`\| ≤ 11 ; tout taux présent est entre 0 et 12.
8. Ligne du 1990-02-02 : `mois_reference` = 1990-01, `emploi_1re_k` = 275, `date_millesime_3e` = 1990-04-06,
   `emploi_3e_k` = 361.
9. Alignement des dates : là où les deux sont présents, \|`dgs2_j` − `sveny02_j`\| ≤ 0,75 et \|`dgs2_veille` −
   `sveny02_veille`\| ≤ 0,75. Si elles sont présentes à la ligne du 1990-02-02 : `sveny02_veille` = 8,1466 et `sveny02_j` =
   8,2234 à 0,0001 près.

## 6. Statistique

**Échantillon principal P** : les lignes où `principal` = 1. n = nombre de ces lignes (`n_publications`).

**Variables**, calculées en double précision, sans arrondi intermédiaire :

- y = 100 × (`dgs2_j` − `dgs2_veille`) : variation du taux à 2 ans le jour de la publication, en pb ;
- N = (`emploi_1re_k` − `emploi_3e_k`) / 100 : partie révisée, en centaines de milliers d'emplois ;
- R1 = `rev_m1_k` / 100 et R2 = `rev_m2_k` / 100 : révisions des deux mois précédents publiées ce jour ;
- U = `d_chomage_pt` : variation publiée du taux de chômage ;
- T = `tendance_12m_k` / 100 : tendance de l'emploi connue la veille.

**Statistique principale (une seule).** Moindres carrés ordinaires sur P :

y = a + β·N + c1·R1 + c2·R2 + c3·U + c4·T + résidu.

Soit X la matrice n × 6 dont la ligne i est (1, N, R1, R2, U, T), dans cet ordre.

- Coefficients : b = (X′X)⁻¹ X′y. `beta_pb_par_100k` est le deuxième élément de b.
- Résidus : e_i = y_i − x_i′b. Levier : h_i = x_i′ (X′X)⁻¹ x_i.
- Variance robuste HC3 : V = (X′X)⁻¹ [ Σ_i (e_i / (1 − h_i))² x_i x_i′ ] (X′X)⁻¹. Aucun autre facteur de correction.
- `erreur_type_pb` : ET = racine du deuxième élément diagonal de V.
- `t_stat` : t = β / ET. Comparé à la loi normale (1,96), pas à une loi de Student.
- `borne_inf_95_pb` = β − 1,96 × ET ; `borne_sup_95_pb` = β + 1,96 × ET.
- `marge_zone_grise` : M = min( 1,96 − t , `borne_sup_95_pb` − 1 ). M > 0 veut dire : β n'est pas significativement positif,
  et pourtant l'effet de 1 pb prédit par la fiche n'est pas exclu.

Avec `statsmodels`, c'est `OLS(y, X).fit(cov_type="HC3")`. Le calcul est déterministe : pas de tirage aléatoire.

Pourquoi ces choix. Les publications sont espacées d'un mois et y est une variation sur un jour : pas d'autocorrélation à
corriger. La volatilité du taux change beaucoup d'une époque à l'autre (années 1990, taux plancher de 2009-2015 et 2020-2021) :
il faut des erreurs robustes à l'hétéroscédasticité. HC3 divise chaque résidu par (1 − h_i) : les points qui tirent le plus
la droite comptent davantage dans l'incertitude.

**Garde de validité (placebo).** Même régression, mêmes lignes, même X, avec pour variable expliquée
y_veille = 100 × (`dgs2_veille` − `dgs2_avant_veille`). `t_placebo_abs` = |coefficient de N / son erreur type HC3|. Si
`t_placebo_abs` ≥ 1,96, le test est non concluant. Cette garde se déclenche à tort dans environ 5 % des cas.

**Analyses secondaires, descriptives, sans effet sur le verdict.**

- **S1. Nature des révisions (emploi seul, aucun taux).** Sur P, surprise naïve : Sn = `emploi_1re_k` / 100 − T. Régression
  de Sn sur N avec constante ; rapporter la pente p̂ et son erreur type HC3. Lecture : p̂ proche de 1, révisions de type
  « bruit » ; proche de 0, de type « information nouvelle » ; négative, premières estimations qui sous-réagissent. Si
  p̂ ≥ 0,3, rapporter aussi β / p̂, sans erreur type : ordre de grandeur de la sensibilité au chiffre publié, à comparer aux
  4 à 6 pb de la littérature. T est une attente grossière : S1 ne remplace pas le consensus.
- **S2. À chiffre publié donné.** Régression principale avec Sn ajoutée comme septième colonne. Rapporter le coefficient de
  Sn (sensibilité au chiffre publié, sous-estimée parce que Sn mesure mal la surprise) et celui de N (δ), avec leurs erreurs
  types HC3. Lecture de δ : négatif, le taux penche vers la valeur future à chiffre publié donné, ce qui est la forme la plus
  proche de la régression de Gilbert ; nul, le marché traite la partie révisée comme le reste du chiffre.
- **S3. Sensibilité à la règle A7.** Régression principale sur les lignes où `complet` = 1, `n_mois_nouveaux` = 1 et
  `revision_large` = 0, que `extreme` vaille 0 ou 1. Rapporter β, ET, n, et la liste des dates où `extreme` = 1.

L'expérimentateur rapporte aussi, sur P, l'écart-type de N, l'écart-type de y, et le nombre de lignes écartées par chaque
filtre, pour les comparer aux suppositions de la section 7.

## 7. Arithmétique de puissance

Aucune donnée n'a été lue pour cette section. Les ordres de grandeur viennent de la note de nouveauté et de la fiche ; ils
sont **non vérifiés** sur l'échantillon.

**Nombre de publications.** 431 jours de publication. À retirer : la publication double (1) ; les extrêmes de A7 (environ 6,
de mémoire) ; le jour sans taux (1) ; les révisions larges. Une révision large par an fait sortir trois publications par an
(celle du jour et les deux précédentes), soit 108 sur 36 ans. S'il y en avait deux par an avant 2004 (possible, non vérifié),
il en sortirait une quarantaine de plus. **n attendu : entre 270 et 315.**

**Écart-type de N.** Le BLS publie une révision absolue moyenne (troisième moins première estimation) de 56 000 emplois sur
1979-2026, 51 000 depuis 2003 (note de nouveauté). Pour une loi normale, écart-type = 1,25 × écart absolu moyen, soit environ
65 000 ; avec des queues épaisses (rapport de 1,55 lu chez Krueger et Fortson pour une autre révision), environ 85 000. Les
extrêmes et les mois de révision large sont retirés, et les contrôles absorbent une partie de N. **Supposition : 0,5 à 0,8 en
centaines de milliers, 0,6 au centre.** La fiche supposait 0,6.

**Écart-type de y un jour d'emploi.** Gilbert, Scotti, Strasser et Vega : 4,2 pb sur le 2 ans par écart-type de surprise, R²
de 0,27 (1997-2015), d'où un écart-type total d'environ 4,2 / √0,27 ≈ 8 pb, si leur fenêtre est bien la journée (non vérifié).
La fiche supposait 8,5. Les années de taux plancher tirent vers le bas, les années 1990 vers le haut. **Supposition : 6,5 à
9 pb, 8 au centre.**

**Erreur type attendue de β** ≈ écart-type de y / (écart-type de N × √n) :

| Cas | Écart-type de y | Écart-type de N | n | Erreur type | La fiche survit si β̂ ≥ | Éliminée si β̂ ≤ |
|---|---|---|---|---|---|---|
| Favorable | 6,5 | 0,8 | 315 | 0,46 | 0,90 | 0,10 |
| Central | 8,0 | 0,6 | 300 | 0,77 | 1,51 | −0,51 |
| Défavorable | 9,0 | 0,5 | 270 | 1,10 | 2,15 | −1,15 |

La formule suppose des résidus de même variance. Avec des queues épaisses dans N, l'erreur type HC3 peut être plus grande.

**Probabilité de chaque verdict** (loi normale, garde placebo mise à part) :

| Cas | Vrai β | survit | éliminée | non concluant |
|---|---|---|---|---|
| Favorable (0,46) | −2 | 0 % | 100 % | 0 % |
| Favorable | 0 | 2,5 % | 59 % | 39 % |
| Favorable | +1 | 59 % | 2,5 % | 39 % |
| Favorable | +2 | 99 % | 0 % | 1 % |
| Central (0,77) | −2 | 0 % | 97 % | 3 % |
| Central | 0 | 2,5 % | 25 % | 72 % |
| Central | +1 | 25 % | 2,5 % | 72 % |
| Central | +2 | 74 % | 0,1 % | 26 % |
| Central | +3 | 97 % | 0 % | 3 % |
| Défavorable (1,10) | −2 | 0 % | 78 % | 22 % |
| Défavorable | 0 | 2,5 % | 15 % | 83 % |
| Défavorable | +1 | 15 % | 2,5 % | 83 % |
| Défavorable | +2 | 45 % | 0,2 % | 55 % |
| Défavorable | +3 | 78 % | 0 % | 22 % |

**Ce que le test peut détecter.** Au centre, un effet d'au moins 2,2 pb par 100 000 est détecté quatre fois sur cinq
(2,8 × 0,77) ; un effet rival de −2 est reconnu presque toujours. Le milieu et le haut de la fourchette de la fiche (2 à 3)
sont donc à portée, ainsi qu'un signe contraire net.

**Ce qu'il ne peut pas détecter.** Le bas de la fourchette : entre 0 et 1 pb, le test rend « non concluant » environ sept
fois sur dix au centre. Il ne peut pas non plus mesurer le retour du taux les jours suivants, ni un changement après 2020
(une cinquantaine de publications, erreur type proche de 2), ni la qualité du filtrage.

Dans tous les cas, un verdict à tort ne dépasse pas 2,5 % : survie alors que β = 0, ou élimination alors que β = +1.

Coût : environ 75 requêtes légères et deux fichiers (17 Mo en tout), six paramètres estimés sur 300 lignes. Quelques
minutes sur un portable, téléchargement compris.

## 8. Règle de verdict

Le verdict s'applique aux nombres du vérificateur. On regarde d'abord « non concluant », puis « survit ».

**Non concluant** si l'une de ces conditions tient :
- `schema_ok` < 1 ;
- `n_publications` < 250 ;
- `t_placebo_abs` ≥ 1,96 ;
- `marge_zone_grise` > 0, c'est-à-dire t < 1,96 alors que la borne haute à 95 % dépasse 1 pb ;
- (protocole) une donnée nommée manque, un champ n'est pas calculable, ou l'expérimentateur et le vérificateur diffèrent de
  plus que la tolérance.

**Survit** si toutes ces conditions tiennent : `t_stat` ≥ 1,96 ; `beta_pb_par_100k` > 0 ; `t_placebo_abs` < 1,96 ;
`schema_ok` ≥ 1 ; `n_publications` ≥ 250.

**Éliminée** sinon : échantillon et placebo valides, t < 1,96 et borne haute à 95 % ≤ 1 pb. Cela couvre deux situations que
la phrase de conclusion distingue : un coefficient significativement négatif (t ≤ −1,96), et un zéro précis.

**Justification des seuils.**
- **1,96** : seuil bilatéral à 5 %. Bilatéral parce qu'un travail publié prédit le signe contraire (A2). Le même seuil, en
  miroir, sert à dire que la lecture rivale est appuyée.
- **1 pb par 100 000** : borne basse de la prédiction de la fiche. Une borne haute à 95 % sous 1 exclut toute la fourchette
  prédite. Choisir 2 (le centre) éliminerait à tort une fiche vraie à +1 une fois sur quatre au centre ; avec 1, ce risque
  reste à 2,5 %. Le prix : beaucoup de « non concluant » si l'effet vrai est petit.
- **250 publications** : 20 sous le bas de la fourchette attendue (270 à 315). En dessous, la construction ne s'est pas
  passée comme prévu (plus de révisions larges ou de données manquantes qu'annoncé) et ce n'est plus le test décrit ici.
- **Placebo à 1,96** : seuil usuel, dit « nul » dans la fiche ; 5 % de fausses alertes, acceptées.

La survie porte sur le signe. La taille est jugée dans la phrase de conclusion, qui doit dire si l'intervalle à 95 % recoupe
la fourchette de +1 à +3.

**Tolérances** entre expérimentateur et vérificateur : 0,005 pb sur le coefficient et l'erreur type ; 0,01 pb sur les deux
bornes ; 0,02 sur t, sur la marge et sur le t du placebo ; 0 sur `n_publications` et `schema_ok`. Les deux calculent sur le
même fichier avec une formule fermée : un écart plus grand signale une erreur, pas un arrondi.

`temoin.json` et `verification.json` sont des objets JSON plats qui portent les neuf champs de la règle. S1 à S3 peuvent y
figurer sous une clé `descriptif` ; elles ne sont ni comparées ni lues par le verdict.

## 9. Limites

1. **Un β positif ne montre pas un défaut de filtrage.** Un marché rationnel qui ne voit pas l'erreur donne le même signe.
   Le test établit au mieux que le taux a porté l'erreur le jour même.
2. **β est une forme réduite : β ≈ κ × p + δ.** Chaque signe a au moins deux lectures (section 2). Sans consensus, on ne
   sépare pas ce qui vient du marché (κ, δ) de ce qui vient de la nature des révisions (p). S1 et S2 n'utilisent qu'une
   attente naïve.
3. **Biais possible si N est lié à la vraie surprise.** Les contrôles (tendance, révisions du jour, chômage) et le placebo
   réduisent ce risque sans l'écarter.
4. **Puissance faible sous 2 pb.** Si l'effet vrai est entre 0 et 1, l'issue la plus probable est « non concluant ».
5. **Fenêtre d'un jour.** La variation de clôture à clôture contient toutes les autres nouvelles : salaires horaires (non
   contrôlés), durée du travail, autres publications, banques centrales. C'est du bruit si elles sont sans lien avec N, ce
   qui n'est pas testé. Des cotations intrajournalières feraient mieux ; elles ne sont pas gratuites.
6. **N n'est pas toute l'erreur.** La troisième estimation garde une erreur d'échantillonnage et sera encore révisée par les
   révisions de référence. N ne mesure que ce que les réponses tardives corrigent en deux mois.
7. **Taux plancher.** De 2009 à 2015 et en 2020-2021, le taux à 2 ans réagit peu aux nouvelles. Ces publications tirent β
   vers zéro. Aucune sous-période n'est testée.
8. **Environ un quart des publications sort par A5** (décembre, janvier et février depuis 2004). Le résultat ne vaut pas
   pour elles.
9. **Qualité des millésimes anciens.** Les dates de publication sont déduites des dates de millésime d'ALFRED, sans
   recoupement avec le calendrier du BLS. Une erreur de date d'un jour ferait porter le test sur le mauvais jour.
10. **Les écarts-types de la section 7 sont supposés** : la puissance réelle n'est connue qu'après le test.

## 10. Ce qu'on écrira dans chaque cas

- **Survit.** « Sur n publications de l'emploi américain de 1990 à 2025, hors révisions de référence et hors 2020, le taux à
  2 ans monte le jour même de X pb (erreur type Y) par tranche de 100 000 emplois de surestimation initiale ; l'intervalle à
  95 % recoupe / ne recoupe pas la fourchette prédite de 1 à 3 pb : le taux porte la partie du chiffre effacée ensuite,
  contre la lecture tirée de Gilbert (2011), sans que cela montre un défaut de filtrage, puisqu'un marché rationnel qui ne
  voit pas l'erreur réagit de la même façon. »
- **Éliminée, coefficient significativement négatif (t ≤ −1,96).** « Sur les mêmes publications, le taux à 2 ans bouge le
  jour même dans le sens de la valeur révisée et non de l'erreur initiale (X pb par 100 000, erreur type Y) : la fiche est
  éliminée et le résultat de Gilbert (2011) sur les actions s'étend au taux à 2 ans, sans qu'on puisse dire si le marché
  anticipe la révision ou si les premières estimations sous-réagissent. »
- **Éliminée, zéro précis (intervalle à 95 % sous +1, t > −1,96).** « Sur les mêmes publications, le taux à 2 ans ne réagit
  pas à la partie du chiffre révisée ensuite (X pb par 100 000, borne haute à 95 % de Y, sous le 1 pb prédit) : la fiche est
  éliminée ; ce zéro est compatible avec des révisions qui sont de l'information nouvelle comme avec un marché qui écarte
  l'erreur, et S1 (p̂ = Z) dit laquelle des deux explications est la plus plausible. »
- **Non concluant.** « Le test ne tranche pas, pour la raison suivante : [estimation trop imprécise pour exclure 1 pb /
  placebo différent de zéro / échantillon sous 250 / schéma violé / désaccord entre expérimentateur et vérificateur] ; on ne
  conclut ni à la réaction du taux à la partie révisée ni à son absence. »

## 11. Règle lisible par machine

```json
{
  "id": "H13",
  "fichier_analyse": "H13_analyse.csv",
  "champs_verification": [
    "schema_ok",
    "n_publications",
    "beta_pb_par_100k",
    "erreur_type_pb",
    "t_stat",
    "borne_inf_95_pb",
    "borne_sup_95_pb",
    "marge_zone_grise",
    "t_placebo_abs"
  ],
  "survit_si": [
    {"champ": "t_stat", "operateur": ">=", "seuil": 1.96},
    {"champ": "beta_pb_par_100k", "operateur": ">", "seuil": 0},
    {"champ": "t_placebo_abs", "operateur": "<", "seuil": 1.96},
    {"champ": "schema_ok", "operateur": ">=", "seuil": 1},
    {"champ": "n_publications", "operateur": ">=", "seuil": 250}
  ],
  "non_concluant_si": [
    {"champ": "schema_ok", "operateur": "<", "seuil": 1},
    {"champ": "n_publications", "operateur": "<", "seuil": 250},
    {"champ": "t_placebo_abs", "operateur": ">=", "seuil": 1.96},
    {"champ": "marge_zone_grise", "operateur": ">", "seuil": 0}
  ],
  "tolerance": {
    "schema_ok": 0,
    "n_publications": 0,
    "beta_pb_par_100k": 0.005,
    "erreur_type_pb": 0.005,
    "t_stat": 0.02,
    "borne_inf_95_pb": 0.01,
    "borne_sup_95_pb": 0.01,
    "marge_zone_grise": 0.02,
    "t_placebo_abs": 0.02
  }
}
```
