Vous êtes juge dans une course d'idéation de recherche, génération 2. Vous n'avez écrit aucune des fiches. Lisez d'abord le brief que les proposeurs ont reçu (il contient le registre des résultats déjà mesurés et les deux parents), puis votre grille, puis les 20 fiches ; jugez à partir des fiches et de ce que vous savez, sans rien rechercher ni calculer. Soyez sévère : pour chaque fiche, cherchez d'abord pourquoi elle échoue (test qui ne peut pas tuer l'idée, trop peu d'observations indépendantes pour l'effet prédit, identification qui n'identifie pas, résultat déjà connu ou déjà mesuré dans le registre). Votre réponse est UNIQUEMENT le tableau JSON décrit dans la grille (20 objets, identifiants J01 à J20), sans texte avant ni après, sans bloc de code.

===== BRIEF REÇU PAR LES PROPOSEURS =====

# Brief d'idéation — projet de recherche en économie ou finance quantitative, mené avec des agents d'IA

## But
Trouver un projet de recherche empirique **ambitieux mais faisable**, qu'un étudiant de niveau licence (maths/économie,
Python ou R) mène **ouvertement avec des agents d'IA**, et qu'il présentera dans une candidature à un master de recherche
en économie et finance quantitatives (micro, macro, économétrie, séries temporelles ; débouché doctorat ou poste quantitatif).
Le projet doit montrer deux choses à la fois :
1. un vrai résultat empirique (positif ou négatif) sur une question d'économie ou de finance ;
2. une **manière rigoureuse de se servir de l'IA** : l'IA propose et exécute, mais ne note jamais son propre travail.

## Critère de choix (fixé par le commanditaire)
On retient ce qui **parle le plus au jury d'admission** (économistes universitaires : rigueur d'identification, honnêteté
statistique, question claire) **et aux recruteurs de stage** (banque d'investissement, gestion d'actifs, recherche quantitative,
banque centrale, recherche économique, conseil : sujet reconnaissable, résultat qu'on explique en deux phrases, un graphique,
un dépôt de code propre). Une idée brillante mais illisible pour un recruteur, ou vendeuse mais fragile devant un économètre, perd.

## Règle de méthode (reprise de l'organisme d'idéation de ce dépôt)
- Le rôle qui produit un artefact ne détient jamais la clé qui l'évalue.
- Toute prédiction est écrite et scellée (sha256) **avant** que les données qui la jugent soient lues.
- Le verdict d'un test est calculé par un code séparé à partir du fichier brut, jamais par l'agent qui a fait l'expérience.
- Un résultat nul proprement obtenu est un résultat. Une idée qu'on ne peut pas tuer n'est pas une idée.

## Contraintes dures
- **Données publiques et gratuites uniquement**, téléchargeables sans compte. Joignables depuis cette machine (vérifié) :
  FRED (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>`), bibliothèque Ken French (Dartmouth),
  portail de données de la BCE (`https://data.ecb.europa.eu/`, API `https://data-api.ecb.europa.eu/service/data/...`), arXiv.
  Non joignables ou limités : Yahoo Finance (429), Stooq (injoignable). Toute autre source doit être **testée par vous avec curl**
  (code HTTP et premières lignes) avant d'être citée dans une fiche. Pas de CRSP, Compustat, Bloomberg, Refinitiv.
- Calcul : un portable, processeur seul. Appels de modèles de langage permis si la fiche chiffre le coût (viser < 30 USD).
- Durée : 4 à 6 semaines à temps partiel pour l'étudiant.
- Méthodes défendables en 30 minutes d'entretien devant des économistes : MCO, panel à effets fixes, projections locales,
  études d'événement, Fama-MacBeth, évaluation de prévisions hors échantillon (Diebold-Mariano, Clark-West), bootstrap,
  correction de tests multiples. Pas d'apprentissage profond opaque comme cœur du résultat.
- À éviter : le « backtest » naïf d'une stratégie qui bat le marché ; une simple réplication sans question nouvelle ;
  un sujet dont le résultat est connu d'avance.

## Format d'une fiche (champs fermés, tous obligatoires, en français)
```
### <ID> — <titre court>
- **Question** : une phrase.
- **Hypothèse falsifiable** : une phrase, avec le sens de l'effet.
- **Prédiction chiffrée** : signe et ordre de grandeur attendus, écrits sans avoir regardé le résultat.
- **Test de mort** : statistique exacte, seuil, échantillon ou fenêtre hors échantillon ; ce qui élimine l'idée.
- **Données** : séries ou fichiers exacts, URL, et le code HTTP que vous avez obtenu en les testant.
- **Méthode** : 3 à 5 lignes.
- **Ce qui serait nouveau** : en quoi cela dépasse ce qui est connu ; travaux les plus proches dont vous vous souvenez,
  chacun marqué « à vérifier » (n'inventez aucune référence : dans le doute, écrivez « référence incertaine »).
- **Rôle de l'IA** : ce que les agents font ; ce que l'humain décide ; la garde qui empêche l'IA de se noter elle-même.
- **Coût et durée** : calcul, appels de modèles en USD, semaines.
- **Risques** : ce qui rendrait le projet sans intérêt même exécuté proprement.
- **Valeur si l'hypothèse meurt** : ce qu'on peut encore écrire.
- **Ce que ça dit au jury et aux recruteurs** : la ligne de CV (une phrase, au passé, sans enjoliver), le graphique unique
  qui résume le projet, et quels métiers de stage y reconnaissent leur travail.
```

---

# Complément pour la génération 2 — 12 novembre 2026

Une première génération d'idées a été proposée, jugée puis **testée sur données réelles**, chaque test étant préinscrit et
scellé avant lecture des données, exécuté par un agent, recalculé par un autre, et jugé par un code séparé. Vous êtes proposeur
de la **génération 2** : vous construisez sur ce qui a survécu.

## Profil et centres d'intérêt de l'étudiant
- Centres d'intérêt, par ordre : **économie monétaire, banque centrale, macroéconomie**, puis finance de marché.
- Il sait : Python (pandas, numpy, statsmodels), mathématiques de classes préparatoires, cours de titres à revenu fixe et
  d'économie monétaire. Ses projets existants portent sur les actions.

## Registre des résultats (faits mesurés ; « pb » = point de base)
- **Pression de prix aux adjudications du Trésor américain** — verdict : *survit*. sur 321 réouvertures à 10, 20 et 30 ans (2010-2026), pression moyenne de 0.91 pb (erreur type 0.16, t = 5.6) ; placebo à J+10 : |t| = 0.27.
- **Adjudications : la disparition de l'effet après 2021 vient-elle de la méthode de la courbe du Trésor ?** — verdict : *non concluant*. sur 23 réouvertures de l'exercice 2021, pression de 1.64 pb avec l'ancienne méthode du Trésor et de 0.85 pb avec la nouvelle ; différence 0.78 pb, intervalle à 95 % [0.45 ; 1.12], qui contient le seuil préinscrit de 0,9.
- **Instrument de protection de la transmission de la BCE et écarts souverains** — verdict : *non concluant*. pente écart souverain / surprise de taux : 0.56 avant juillet 2022 (87 réunions), 0.21 après (26) ; variation -0.35, erreur type 0.32 ; sans la réunion du 12 mars 2020 la variation tombe à -0.13.
- **Anomalies boursières publiées : effet de la publication ou tendance commune ?** — verdict : *non concluant*. effet propre de la publication : -0.06 du rendement d'origine (erreur type 0.12), intervalle [-0.32 ; 0.19] ; 185 anomalies.
- **Les surprises de la BCE sont-elles prévisibles hors échantillon avec des données publiques ?** — verdict : *éliminée*. sur 147 réunions (2010-2025), cinq prédicteurs publics réestimés avant chaque réunion : R² hors échantillon de -0.5 %, statistique de Clark-West 0.59 (seuil 1,645).
- **Emploi américain : le taux à 2 ans réagit-il à la part du chiffre qui sera révisée ?** — verdict : *survit*. sur 309 publications (1990-2025), 2.32 pb par tranche de 100 000 emplois surestimés (erreur type 0.94, t = 2.45) ; placebo la veille : |t| = 1.00.
- **Les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel ?** — *test annulé, à refaire* : la préinscription rangeait à l'envers les exercices de juin et de septembre ; aucun résultat valide.

## Les parents : les 2 idées qui ont survécu
### Parent A — Pression de prix aux adjudications du Trésor américain

**Mesure.** V = 100 × [2·E(J) − E(J−5) − E(J+5)], en points de base, où E = rendement à échéance constante du Trésor (FRED `DGS10`, `DGS20`, `DGS30`) moins rendement au pair de la courbe ajustée de la Fed (`SVENPY10/20/30` de `feds200628.csv`) ; J = jour de l'adjudication, en jours ouvrés. Seules les réouvertures sont gardées (le titre de référence n'y change pas). Erreur type groupée par mois (134 mois).
**Dispersion mesurée, utile pour vos calculs de puissance.** Écart-type de V : 2,57 pb par adjudication.
**Lectures exploratoires, faites après le verdict (questions, pas résultats).** Par échéance : 1,17 pb à 10 ans, 1,04 à 30 ans, −0,13 à 20 ans. Par année : de 1,0 à 2,2 pb de 2011 à 2021, puis 0,30 ; −0,03 ; 0,23 ; −0,54 ; 0,39 de 2022 à 2026.
**Fait de mesure établi.** Le 6 décembre 2021 le Trésor a remplacé la méthode de sa courbe (spline d'Hermite, puis méthode « monotone convexe »). Sur l'exercice 2021, où il publie les deux méthodes côte à côte (fichier à deux décimales, soit 1 pb de résolution), l'écart ancienne moins nouvelle méthode vaut en moyenne 0,26 pb à J−5, 0,70 pb à J et 0,35 pb à J+5 : l'ancienne méthode gonfle le taux le jour même de l'adjudication.
**Littérature la plus proche (vérifiée).** Fleming, Liu et Nguyen (2026, Fed de New York) : pression mesurée sur données intrajournalières et CRSP de 1991 à juillet 2024, qui « faiblit nettement » en 2015-2024 ; le montant offert ne l'explique pas. Lou, Yan et Zhang (2013) : article d'origine, 1980-2008.
**Ce qui reste ouvert.** La disparition après 2021 vient-elle du marché ou de la mesure ? Les échéances de 2 à 7 ans, l'effet de taille et les autres émetteurs souverains n'ont pas été testés. Aucune mesure indépendante de la courbe du Trésor n'a été essayée.

### Parent B — Emploi américain : le taux à 2 ans réagit-il à la part du chiffre qui sera révisée ?

**Mesure.** Régression MCO, par publication mensuelle de l'emploi, de la variation du taux à 2 ans (FRED `DGS2`, en pb) le jour de la publication sur N = première estimation moins troisième estimation de la variation mensuelle de l'emploi (`PAYEMS`, millésimes ALFRED, en centaines de milliers), avec en contrôle les révisions des deux mois précédents publiées le même jour, la variation publiée du taux de chômage et la médiane des douze dernières variations connues la veille. Erreurs types robustes (HC3). Hors révisions annuelles larges, publication double et extrêmes de 2020.
**Dispersion mesurée, utile pour vos calculs de puissance.** Écart-type de la variation du taux à 2 ans un jour d'emploi : 9,43 pb.
**Fragilité mesurée (descriptif).** Aucune décennie n'est significative seule ; les années 2010 donnent −0,45 pb (t = −0,39) ; sans les années 2020 (47 publications), t tombe à 1,75.
**Limite de fond.** Il n'existe pas de source gratuite de la prévision de consensus : la vraie surprise du jour manque. Un coefficient positif est attendu même d'un marché rationnel qui ne peut pas voir l'erreur le jour même ; le test ne montre donc pas un défaut de filtrage.
**Littérature la plus proche (vérifiée).** Gilbert (2011) : sur les actions, les prix bougent dans le sens de la révision future (signe contraire) ; seul son résumé a été lu. Krueger et Fortson (2003) ; Gilbert, Scotti, Strasser et Vega (2017).
**Ce qui reste ouvert.** Le taux revient-il en arrière quand la révision est publiée ? L'effet existe-t-il pour d'autres statistiques révisées (ventes au détail, production industrielle, PIB), d'autres échéances, d'autres marchés ? Pourquoi est-il absent dans les années 2010 ? La syntaxe qui marche pour les millésimes : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<SERIE>&vintage_date=AAAA-MM-JJ`.

## Ce que vous rendez
Exactement **cinq fiches**, en français, au format de fiche du brief, avec deux champs en plus :
- **Parent et différence** (obligatoire) : `Parent A`, `Parent B` ou `libre`. Pour une fiche fille, dites lequel de ces quatre
  éléments vous changez par rapport au parent — la statistique, l'échantillon ou le marché, la source de données,
  l'identification — et pourquoi ce changement peut donner une réponse que le parent n'a pas. Une fiche qui reformule son parent
  sans changer l'un de ces quatre éléments est refusée avant le jugement. Pour une fiche libre, citez le résultat du registre
  qui la motive.
- **Arithmétique de puissance** (obligatoire) : nombre d'observations réellement indépendantes, erreur type attendue (servez-vous
  des dispersions mesurées ci-dessus), effet prédit ; dites si le test peut trancher. Plusieurs tests de la génération 1 ont fini
  « non concluants » faute d'observations : un test qui ne peut pas trancher est une mauvaise fiche.

Au moins **trois fiches filles** (réparties comme vous voulez entre les parents) et au plus **deux fiches libres**.
Cinq questions et cinq méthodes différentes. Les meilleures fiches filles tranchent une question que le parent a laissée ouverte.

## Vous n'avez aucun outil
Vous ne pouvez rien télécharger ni tester. Le champ « Données » ne cite que des sources de la liste ci-dessous, dont l'accès a
été vérifié. Toute autre source porte la mention « source non vérifiée » et ne peut pas être indispensable au test de mort.

Sources vérifiées (publiques, sans compte) :
- FRED, séries en CSV (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>`) et millésimes ALFRED (`alfredgraph.csv`).
- Bibliothèque Ken French (facteurs et portefeuilles, quotidiens et mensuels).
- API de données de la BCE (`https://data-api.ecb.europa.eu/service/data/...`, intermittente) : courbes de rendements (YC),
  taux d'intérêt bancaires (MIR), enquête sur la distribution du crédit (BLS), base des projections macroéconomiques (MPD,
  111 millésimes), taux à long terme par pays (IRS).
- Base EA-MPD de la BCE (`Dataset_EA-MPD.xlsx`) : variations de marché autour de 315 réunions de 1999 à 2025
  (OIS, rendements souverains DE, FR, IT, ES, actions, change).
- Enquête de la BCE auprès des prévisionnistes professionnels, prévisions individuelles (archive zip).
- Trésor américain : API des adjudications depuis 1979 (`api.fiscaldata.treasury.gov ... auctions_query`) ; courbe ajustée
  de la Fed (Gürkaynak, Sack et Wright, `feds200628.csv`, quotidienne).
- Fed de Philadelphie : enquête auprès des prévisionnistes professionnels (niveaux médians, dispersion). Fed de New York :
  enquête sur les anticipations des consommateurs (classeur).
- Textes de la Fed sur federalreserve.gov (communiqués du FOMC, Livre beige).
- Eurostat (API), BRI (téléchargements en bloc `data.bis.org`), Open Source Asset Pricing (Hugging Face).
Injoignables : Yahoo Finance, Stooq, FMI, API de la Banque mondiale, texte des dépôts SEC, tout fournisseur payant.

- Ajouts vérifiés depuis : fichier du Trésor donnant ses deux méthodes de courbe côte à côte pour l'exercice 2021
  (`https://home.treasury.gov/system/files/221/fy2021-mc-vs-hs-combined.csv`) ; millésimes ALFRED par
  `alfredgraph.csv?id=<SERIE>&vintage_date=AAAA-MM-JJ` ; hypothèses individuelles de taux directeur dans l'enquête de la BCE auprès
  des prévisionnistes (2002-2026) ; facteurs quotidiens Europe de la bibliothèque Ken French.

## Idées déjà proposées — ne pas les reprendre telles quelles (une fille d'un parent doit s'en distinguer comme dit plus haut)
- Anomalies publiées : l'érosion après publication est-elle un effet de la publication ou une tendance commune du calendrier ?
- Les banques prévoient-elles bien leur propre politique de crédit ? Rationalité des anticipations dans l'enquête BLS
- Liens entre secteurs : un modèle de langage choisit-il mieux que le hasard, sur des rendements postérieurs au gel de ses poids ?
- Adjudications du Trésor américain : la pression de prix existe-t-elle encore et croît-elle avec la taille des émissions ?
- Les a priori d'un modèle sur l'exposition des industries au pétrole, aux taux et au dollar
- Corrélation actions-obligations et inflation : un modèle figé en 2019 prédit-il la bascule de 2021-2025 pays par pays ?
- Le canal des dépôts à l'épreuve de 2022-2023 : re-test scellé d'une prédiction publiée, banque par banque
- Les booms de crédit prédisent-ils les crises hors des pays riches ? Multivers et transport hors échantillon
- Livre beige : le texte régional dit-il quelque chose que l'emploi passé ne dit pas ?
- Contexte ou mémoire ? Prévoir l'inflation à un mois avec des chiffres nommés ou anonymes
- Hausse des « frais de notaire » de 2025 : anticipation et recul des ventes, département par département
- L'instrument de protection de la transmission a-t-il coupé le lien entre surprises de la BCE et écarts souverains ?
- Les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel ?
- Ménages synthétiques et prix de l'essence : une expérience par vignettes
- Le choc d'énergie passe-t-il dans l'inflation sous-jacente plus que proportionnellement ?
- Jours d'annonces macroéconomiques : la prime de risque y est-elle toujours gagnée après la publication du résultat ?
- Le modèle lit-il la BCE, ou se souvient-il de la suite ?
- Le ton des communiqués du FOMC, lu avec et sans date
- Salaire minimum et emploi dans la restauration : multivers sur les paires de comtés frontaliers, 2014-2025
- Bêta des dépôts : les taux servis aux ménages baissent-ils plus vite qu'ils n'ont monté ?
- Surprises de la BCE et surcoût du crédit aux PME
- L'euro réagit-il symétriquement aux surprises de la BCE ?
- Les chocs d'inflation s'éteignent-ils dans les projections de la BCE ?
- Les dissidents du FOMC annoncent-ils les décisions suivantes ?
- Pétrole et ancrage des anticipations d'inflation
- Asymétrie de la transmission des surprises de la BCE aux taux bancaires par maturité
- Rigidité de l'information à terme et pente des taux : un test de Coibion-Gorodnichenko dans la zone euro
- L'ancrage des anticipations protège-t-il l'extrémité longue de la courbe des taux américaine des surprises d'inflation ?
- La prime de terme macroéconomique : évaluation de modèles de prévision à fréquences mixtes des excès de rendement obligataires
- Dissidence implicite dans le Livre beige et dispersion des anticipations de taux à court terme
- Les surprises de la BCE sont-elles vraiment des surprises ?
- La règle de Taylor de la BCE vue par les prévisionnistes
- Emploi américain : le taux à 2 ans réagit-il au bruit ?
- L'inflation à 5 ans dans 5 ans suit-elle encore le pétrole ?
- TVA des restaurants allemands : hausse 2024, baisse 2026

## Sortie attendue
Cinq fiches, chacune sous un titre `### <ID> — <titre court>`, identifiants `{ID}1` à `{ID}5`. Rien d'autre : pas d'introduction,
pas de conclusion, pas de classement de vos propres fiches.


===== VOTRE GRILLE =====

# Génération 2 — grille des juges et règle d'agrégation, figées avant la lecture de toute fiche de la génération 2

## Ce qui est jugé
Un lot anonyme de vingt fiches (cinq par proposeur : Kimi, Gemini, Astra, Claude), sous identifiants opaques J01…J20, dans un ordre
tiré par une graine dérivée du sha256 des fichiers de fiches. Le juge ne sait pas quelle famille a écrit une fiche. Il reçoit
aussi le **registre des résultats** que les proposeurs ont reçu (faits mesurés sur les fiches déjà testées), pour pouvoir juger
ce qu'une fiche ajoute. Il ne reçoit aucun classement ni aucune note d'un juge précédent.

## Les juges
Quatre juges de familles différentes — Kimi, Gemini, Astra, Claude — reçoivent exactement la même consigne. Aucun ne voit les autres.

## Critère de choix
Ce qui parle le plus au jury d'admission d'un master de recherche en économie et finance quantitatives **et** aux recruteurs de
stage, pour un étudiant dont les centres d'intérêt sont, par ordre : économie monétaire, banque centrale, macroéconomie, puis
finance de marché, et dont les projets existants portent sur les actions.

## Axes (note entière de 1 à 5)
1. **jury** — question claire, identification honnête.
2. **recruteurs** — sujet reconnaissable, résultat en deux phrases.
3. **tuable** — le test peut vraiment éliminer l'idée, avec assez d'observations indépendantes pour trancher.
4. **interet** — adéquation aux centres d'intérêt et apport au profil.
5. **nouveaute** — d'après ce que le juge sait de la littérature.
6. **apport** — ce que la fiche ajoute à ce qui est déjà mesuré dans le registre. 1 = redite d'un résultat du registre ;
   3 = prolongement utile ; 5 = tranche une question qu'un résultat du registre a ouverte.

## Contraintes de forme
- Classement complet du rang 1 au rang 20, sans ex æquo.
- Mention : au plus **5** « à retenir », au moins **8** « à écarter », le reste « possible ».
- Pour chaque fiche, la **faille la plus grave** en une phrase.

## Sortie
Uniquement un tableau JSON de 20 objets, sans texte autour :
`{"id": "J07", "rang": 1, "mention": "à retenir", "jury": 5, "recruteurs": 4, "tuable": 5, "interet": 4, "nouveaute": 3, "apport": 4, "faille": "..."}`

## Agrégation (code de l'orchestrateur, `jugements/agreger_generation_2.py`)
Somme des rangs des quatre juges (Borda), départage par jury + recruteurs puis identifiant. Une fiche « à écarter » pour deux
juges ou plus sort des retenues. Les **cinq** premières sont retenues. Sont rapportés : le classement, l'accord entre juges, le
rang moyen par famille de proposeur, et le rang que chaque juge donne aux fiches de sa propre famille et à celles des autres.


===== LES 20 FICHES =====

# Fiches anonymes de la génération 2 (20 fiches, J01 à J20)

### J01 — Révisions des ventes au détail américaines et décomposition du taux à 2 ans le jour de l'annonce
- **Parent et différence** : `Parent B`. Changement de **la source de données** (passage de l'emploi `PAYEMS` aux ventes au détail avancées `RSAFS` dans ALFRED, qui subissent des révisions proportionnellement deux fois plus fortes et sont publiées un jour distinct du mois) et de **la statistique** (décomposition de la réaction du taux à 2 ans entre anticipation de taux court et prime de terme via le modèle DKW de la Fed). Cela teste si l'effet du Parent B est une loi générale des statistiques macroéconomiques bruitées ou une particularité du rapport sur l'emploi.
- **Question** : Le jour de la publication des ventes au détail américaines, le taux à 2 ans — et spécifiquement sa composante d'anticipation des taux directeurs — sur-réagit-il à la part du chiffre mensuel qui sera révisée un et deux mois plus tard ?
- **Hypothèse falsifiable** : Une surestimation initiale de la croissance mensuelle des ventes au détail (`RSAFS`, 1re estimation moins 3e estimation) fait monter significativement le taux à 2 ans et sa composante d'anticipation de politique monétaire le jour de la publication.
- **Prédiction chiffrée** : Une surestimation initiale de 1 point de pourcentage de la croissance mensuelle des ventes au détail entraîne une hausse de +1,5 à +3,0 pb du taux à 2 ans le jour de l'annonce, dont au moins les deux tiers proviennent de la composante d'anticipation des taux courts.
- **Test de mort** : Sur l'échantillon mensuel 1992-2025 (~390 publications), estimation par bootstrap par blocs mobiles (pour tenir compte de l'estimation générée du proxy de surprise). L'idée meurt si le coefficient de l'erreur initiale de mesure $N_t^{\text{Retail}}$ sur $\Delta \text{DGS2}_t$ a une statistique $t$ inférieure à 1,96.
- **Arithmétique de puissance** : La série avancée des ventes au détail est disponible en temps réel dans ALFRED depuis 1992 (~390 publications mensuelles indépendantes des jours d'emploi). Les jours de ventes au détail, la volatilité de $\Delta \text{DGS2}$ est d'environ 5,5 pb (inférieure aux 9,43 pb des jours d'emploi), tandis que l'écart-type des révisions entre la 1re et la 3e lecture de la croissance mensuelle de `RSAFS` est d'environ 0,40 point de pourcentage. L'erreur type attendue est de $5,5 / (0,40 \times \sqrt{380}) \approx 0,70$ pb par point de pourcentage de révision. Pour un effet prédit de 1,8 pb, la statistique $t$ attendue est de $2,57$. Le test peut trancher.
- **Données** : Millésimes ALFRED des ventes au détail (`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=RSAFS&vintage_date=AAAA-MM-JJ`, syntaxe vérifiée) et séries FRED quotidiennes (`DGS2`, et décomposition quotidienne de Kim et Wright sur FRED : `THREEFY2` et `THREEFYTP2`, HTTP 200 vérifié).
- **Méthode** : Extraction des dates exactes de publication des millésimes d'ALFRED pour `RSAFS` de 1992 à 2025. Régression de $\Delta \text{DGS2}_t$ et de $\Delta \text{THREEFY2}_t$ (anticipation pure de taux à 2 ans) sur l'erreur initiale $N_t^{\text{Retail}} = g_{t}^{(1)} - g_{t}^{(3)}$, en contrôlant par la prévision ARMA temps réel calculée sur le millésime de la veille et les révisions de $t-1$ et $t-2$ annoncées le même jour. Inférence par bootstrap par blocs (1 000 réplications).
- **Ce qui serait nouveau** : Étend l'analyse du bruit temps réel aux données de consommation nominale (principale source d'information sur la demande entre deux réunions du FOMC) et sépare la réaction des anticipations de taux courts de celle de la prime de terme. Travaux proches : Gilbert, Scotti, Strasser et Vega (2017, *vérifié*), Kim et Wright (2005, *à vérifier*).
- **Rôle de l'IA** : L'agent télécharge la séquence des millésimes mensuels de `RSAFS` sur ALFRED et identifie les dates de sortie (généralement vers le 13-16 du mois). L'humain valide l'exclusion des mois de confinement du printemps 2020 et fige le protocole de bootstrap avant l'estimation sur `DGS2`. Un script de vérification recalcule indépendamment les taux de croissance par millésime.
- **Coût et durée** : Calcul : ~10 minutes (bootstrap compris). Appels de modèles : < 3 USD. Durée : 5 semaines.
- **Risques** : Les dates exactes de publication dans les métadonnées ALFRED avant 2000 peuvent comporter un décalage d'un jour ouvré (vérifiable par le saut de variance de `DGS2` autour de la fenêtre [-1, +1]).
- **Valeur si l'hypothèse meurt** : Un résultat nul sur 390 annonces de ventes au détail démontrerait que l'effet trouvé au Parent B est exclusif au rapport sur l'emploi (en raison du double mandat de la Fed) et que le marché obligataire filtre efficacement le bruit fort des enquêtes sur le commerce de détail.
- **Ce que ça dit au jury et aux recruteurs** : *Ligne de CV* : « Analysé la réaction de la courbe des taux américaine aux révisions en temps réel des ventes au détail (ALFRED, 1992-2025) avec décomposition prime de terme / taux attendu. » *Graphique unique* : Comparaison côte à côte des coefficients de réponse de `DGS2` (décomposé en taux attendu et prime de terme) au signal vrai versus au bruit révisé. *Métiers* : Stratégie taux (fixed income strategy), recherche économique en banque d'investissement, banque centrale.

---

### J02 — Les projections d'inflation de la BCE sous-réagissent-elles aux nouvelles informations ?
- **Parent et différence** : `libre`. Elle est motivée par le test des erreurs de projection de la BCE annulé dans le registre, mais en change la statistique et l'identification : un test révision-erreur à horizon fixe, avec une observation par trimestre cible, plutôt qu'une nouvelle recherche de prédicteurs. Le tri repose sur l'horodatage des millésimes, jamais sur les étiquettes « juin » et « septembre » à l'origine de l'annulation.
- **Question** : Les révisions des projections trimestrielles d'inflation de la BCE sont-elles suivies d'erreurs dans le même sens, signature d'une révision insuffisante ?
- **Hypothèse falsifiable** : À horizon fixe, une révision positive laisse en moyenne une erreur positive ultérieure, ce qui indique une sous-réaction plutôt qu'une révision intégrale de l'information disponible.
- **Prédiction chiffrée** : Après réduction des deux variables par leurs écarts-types, je prédis \(\beta_z=+0{,}40\) écart-type d'erreur par écart-type de révision, avec une plage plausible de +0,30 à +0,55.
- **Test de mort** : Sur les projections appariées à deux trimestres d'horizon, une par trimestre cible, régression MCO de l'erreur réduite sur la révision réduite avec Newey-West à quatre retards. La sous-réaction forte préinscrite est morte si tout l'IC à 90 % de \(\beta_z\) est inférieur à +0,40 ; elle n'est positivement étayée que si \(t>1{,}645\) contre \(\beta_z\le0\).
- **Données** : Base MPD et ses 111 millésimes via `https://data-api.ecb.europa.eu/service/data/MPD/` ; réalisations de l'indice des prix, Eurostat `prc_hicp_midx`, `coicop=CP00`, agrégat zone euro choisi d'après les métadonnées avant calcul des erreurs : `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_midx`. Accès vérifié selon le brief ; codes HTTP non retestés faute d'outil.
- **Méthode** : Pour chaque trimestre cible, retenir la projection publiée exactement deux trimestres avant et celle du millésime immédiatement précédent pour le même cible. Définir \(r=f_{h=2}-f_{h=3}\) et \(e=a-f_{h=2}\), sans utiliser de millésime postérieur dans le choix des contrôles. Estimer \(e_z=\beta_z r_z+u\), avec une seule observation par cible et sans optimisation du découpage temporel.
- **Ce qui serait nouveau** : Le test annulé demandait si des prédicteurs publics amélioraient les projections ; celui-ci teste une restriction de rationalité portant directement sur les révisions, moins exposée au choix de variables et au problème de calendrier. Coibion et Gorodnichenko (2015 ; référence et application précise à vérifier) fournissent le cadre proche ; je n'ai pas de référence certaine pour la même restriction appliquée à ces millésimes trimestriels de la BCE.
- **Rôle de l'IA** : Un agent extrait les millésimes, un second refait l'appariement cible-horizon à partir des seuls horodatages ; un troisième script calcule le verdict sans accès aux sorties d'estimation. L'humain vérifie manuellement quelques enchaînements juin-septembre avant le scellement SHA-256. Aucun agent ne peut modifier l'horizon, le retard HAC ou le seuil après calcul des erreurs.
- **Coût et durée** : Calcul négligeable ; environ 3 millions de tokens pour extraction, double appariement et revue, plafond 10 USD ; 5 semaines.
- **Risques** : Le nombre de couples appariés peut être inférieur à celui annoncé par les seuls 111 millésimes. Une pente positive peut aussi refléter un lissage optimal sous incertitude plutôt qu'une irrationalité. Enfin, des erreurs adjacentes fortement autocorrélées augmenteraient la variance effective.
- **Valeur si l'hypothèse meurt** : On pourra conclure qu'il n'y a pas de sous-réaction de l'ordre de 0,40 écart-type dans ce test transparent, tout en livrant une base appariée et un protocole corrigeant explicitement l'inversion de calendrier qui avait annulé le test précédent.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai testé la relation entre révisions et erreurs ultérieures des projections d'inflation de la BCE sur des millésimes horodatés. » Graphique unique : erreur ultérieure en fonction de la révision, en classes de révision, avec pente estimée, IC et pente préinscrite. Métiers : banque centrale, recherche macroéconomique, prévision et conseil économique quantitatif.
- **Arithmétique de puissance** : Je retiens 90 à 100 trimestres cibles appariés, chacun compté une seule fois. Pour des variables réduites, le \(SE\) iid serait 0,10–0,105 ; en le gonflant de 40 % pour l'autocorrélation et Newey-West, \(SE(\beta_z)\simeq0{,}14\)–0,15. L'effet de 0,40 donne \(t\simeq2{,}7\)–2,9 et environ 85–88 % de puissance ; l'effet minimal détectable avec 80 % de puissance est 0,35–0,37. Le test peut donc trancher, mais seulement si l'appariement conserve au moins 90 cibles, condition vérifiable sans lire les erreurs.

---

### J03 — Prévisibilité en temps réel des erreurs de projection d'inflation de la BCE (1999-2025)
- **Parent et différence** : `libre`. Motivée directement par l'entrée du registre de la génération 1 : *« Les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel ? — test annulé, à refaire : la préinscription rangeait à l'envers les exercices de juin et de septembre ; aucun résultat valide. »* Cette fiche corrige l'ordonnancement chronologique des trimestres de la base MPD de la BCE et applique une méthode d'évaluation de prévisions à horizons multiples.
- **Question** : Les erreurs des projections d'inflation HICP des services de la BCE et de l'Eurosystème à un an étaient-elles prévisibles en temps réel à partir d'indicateurs publics de prix, de taux et de révisions disponibles avant la date d'arrêt technique de chaque exercice ?
- **Hypothèse falsifiable** : Les erreurs de projection d'inflation à 4 trimestres de la BCE ($e_{t+4|t} = \pi_{t+4} - \hat{\pi}_{t+4|t}$) sont positivement corrélées en temps réel avec la révision même de la projection d'inflation de la BCE entre $t-1$ et $t$ (rigidité informationnelle au sens de Coibion-Gorodnichenko) ainsi qu'avec la pente de la courbe des taux observée avant la date de bouclage technique.
- **Prédiction chiffrée** : Le coefficient de sous-réaction de Coibion-Gorodnichenko ($\beta$ dans la régression de l'erreur finale sur la révision de la prévision du même horizon cible entre deux trimestres consécutifs : Mars $\to$ Juin $\to$ Septembre $\to$ Décembre) est compris entre +0,25 et +0,60, et un modèle linéaire récursif temps réel obtient une statistique de Clark-West hors échantillon supérieure à 1,645.
- **Test de mort** : Après tri chronologique strict des 111 millésimes trimestriels (Mars = T1, Juin = T2, Septembre = T3, Décembre = T4, vérifié par test unitaire sur les dates avant tout calcul), l'idée meurt si, sur les millésimes 2000-2024 (~96 exercices complets à horizon de 4 trimestres), la statistique $t$ de Newey-West (4 retards pour le chevauchement annuel des erreurs trimestrielles) sur le coefficient de révision $\beta$ est inférieure à 1,96 ET la statistique hors échantillon de Clark-West (fenêtre d'évaluation 2010-2024, 60 trimestres) est inférieure à 1,645.
- **Arithmétique de puissance** : La base MPD de la BCE contient 111 millésimes trimestriels. En tenant compte du chevauchement d'horizon de 4 trimestres (autocorrélation MA(3) des erreurs de prévision corrigée par Newey-West), l'échantillon de ~96 projections comporte l'équivalent d'au moins 35 à 40 observations indépendantes. L'écart-type des révisions trimestrielles de prévision d'inflation à 1 an est d'environ 0,35 point de pourcentage et celui des erreurs d'environ 1,1 point (ou ~0,6 point hors 2022). Dans la régression de Coibion-Gorodnichenko, l'erreur type attendue sur $\beta$ est d'environ 0,14. Pour un effet prédit de $\beta = 0,35$, on obtient $t \approx 2,50$. Le test peut trancher.
- **Données** : Base des projections macroéconomiques de la BCE (`MPD`, 111 millésimes trimestriels via `https://data-api.ecb.europa.eu/service/data/MPD/...`, HTTP 200 vérifié), inflation HICP réalisée via l'API de la BCE (`ICP`) ou Eurostat (vérifié), et enquête auprès des prévisionnistes professionnels de la BCE (archive zip vérifiée) pour comparaison temps réel.
- **Méthode** : Alignement temps réel d'horizons fixes et d'événements fixes entre millésimes consécutifs $(t-1, t)$ dans l'ordre calendaire strict (Mars, Juin, Septembre, Décembre). Régression d'efficience informationnelle de Nordhaus / Coibion-Gorodnichenko avec erreurs types HAC de Newey-West (et de Driscoll-Kraay en contrôle), complétée par un test de prévisibilité hors échantillon de Clark-West (2007) en temps réel récursif.
- **Ce qui serait nouveau** : Premier test propre et scellé dans ce projet sur les 111 millésimes officiels de la BCE (après l'annulation technique du test de génération 1 due à l'inversion alphabétique/numérique Juin-Septembre), et comparaison directe de la rigidité informationnelle des services de la BCE avec celle du consensus privé (SPF) publié le même trimestre. Travaux proches : Coibion et Gorodnichenko (2015, *à vérifier*), Kontogeorgos et Lambrias (2019, *à vérifier*).
- **Rôle de l'IA** : L'agent écrit le parseur des 111 millésimes MPD. Pour éviter l'erreur de la génération 1, un script d'assertion automatique vérifie que les dates des exercices suivent une suite strictement croissante de ~90 jours (Mars < Juin < Septembre < Décembre) *avant* de calculer les révisions. L'humain scelle par sha256 la table des révisions avant que l'agent n'apparie l'inflation réalisée $\pi_{t+4}$. Le verdict est calculé par un script tiers.
- **Coût et durée** : Calcul : < 2 minutes. Appels de modèles : < 2 USD. Durée : 4 semaines.
- **Risques** : Le choc inflationniste de 2021-2022 domine la variance quadratique de fin d'échantillon ; le protocole préinscrit donc un test principal sur l'échantillon complet et un sous-test pré-2020.
- **Valeur si l'hypothèse meurt** : Prouver que les projections des services de la BCE respectent l'hypothèse d'efficience informationnelle en temps réel ($\beta \approx 0$, Clark-West non significatif) malgré les critiques post-2022 constituerait une défense empirique forte du processus de prévision de l'Eurosystème.
- **Ce que ça dit au jury et aux recruteurs** : *Ligne de CV* : « Testé la rationalité en temps réel des 111 millésimes de projections d'inflation de la BCE (1999-2025) par régressions de Coibion-Gorodnichenko et test hors échantillon de Clark-West. » *Graphique unique* : Nuage de points des erreurs de prévision d'inflation à 1 an de la BCE contre la dernière révision de la prévision (droite de sous-réaction de Coibion-Gorodnichenko), distinguant 1999-2019 et 2020-2025. *Métiers* : Banque centrale (direction des études, politique monétaire), recherche macroéconomique, gestion d'actifs (inflation et taux européens).

---

### J04 — Le bruit de l'emploi est-il surtout un choc de taux courts ?
- **Question** : La composante de l'emploi ultérieurement révisée déplace-t-elle davantage le taux américain à deux ans que celui à dix ans ?
- **Hypothèse falsifiable** : Une première estimation excessivement élevée fait monter davantage le taux à deux ans que le taux à dix ans.
- **Prédiction chiffrée** : Pour 100 000 emplois surestimés, la hausse du deux ans dépassera celle du dix ans d'environ **2 pb**.
- **Test de mort** : Sur les 309 publications admissibles du parent, tester \(H_0:\beta_2-\beta_{10}\leq0\) contre une différence positive ; seuil unilatéral de 5 %, covariance tenant compte de la dépendance entre échéances et HAC de quatre publications. L'idée directionnelle est abandonnée si le test ne rejette pas. Aucun verdict séparé par décennie.
- **Données** : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2,DGS5,DGS10` ; millésimes `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS&vintage_date=AAAA-MM-JJ` et même adresse avec `UNRATE`. Accès vérifié selon le brief ; **code HTTP non communiqué, non testé personnellement**. Les premières et troisièmes estimations seront reconstruites en différenciant les niveaux dans chaque millésime, jamais en mélangeant deux millésimes.
- **Méthode** :  
  Estimer conjointement les équations de variation des taux à deux, cinq et dix ans, avec les contrôles et exclusions du parent.  
  Calculer la covariance entre équations et le contraste de Wald \(\beta_2-\beta_{10}\) ; vérifier son identité avec une régression directe de la variation de pente.  
  Le cinq ans sert uniquement à dessiner la forme de la réponse, sans troisième hypothèse principale.  
  Interpréter le contraste comme une localisation sur la courbe, pas comme une décomposition identifiée entre anticipations de taux et primes de terme.
- **Ce qui serait nouveau** : Déterminer si le résultat du parent ressemble à une révision principalement proche de la trajectoire de politique monétaire ou à un déplacement général des rendements. Gilbert (2011), Krueger et Fortson (2003), Gilbert, Scotti, Strasser et Vega (2017) — **à vérifier** pour les maturités et marchés effectivement étudiés.
- **Rôle de l'IA** : L'IA prépare les millésimes et les équations ; l'humain arrête les exclusions et le contraste unique. Le protocole et le signe attendu sont scellés avant lecture des réponses à cinq et dix ans. Un agent auditeur indépendant vérifie les unités, les dates et l'identité algébrique ; le verdict est produit par un programme séparé verrouillé par l'humain.
- **Coût et durée** : CPU seul, quelques minutes d'estimation ; **15 USD** maximum d'appels ; **4 semaines**.
- **Risques** : Le consensus de marché manque toujours. Une différence positive peut être parfaitement rationnelle et ne prouve aucune erreur de filtrage. La comparaison deux ans/dix ans ne permet pas, à elle seule, d'identifier un choc monétaire pur.
- **Valeur si l'hypothèse meurt** : Montrer que la réaction au bruit n'est pas concentrée sur le segment court, ou borner précisément cette concentration ; produire une cartographie publique et reproductible de l'annonce d'emploi.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai estimé comment les erreurs initiales de l'emploi se répartissaient sur la courbe des taux américaine. » Graphique : coefficient par maturité et intervalle de confiance, avec le contraste principal annoté. Métiers : stratégie taux, recherche macroéconomique, trading de courbe, banque centrale.
- **Parent et différence** : **Parent B** ; changement de **marché observé** et de **statistique**, avec un contraste entre maturités plutôt qu'un seul coefficient sur le deux ans. Le parent ne distingue pas déplacement parallèle et mouvement de pente.
- **Arithmétique de puissance** : **309 dates communes**, pas 927 observations indépendantes ; hypothèse prudente de **250 observations effectives** après dépendance temporelle. Le couple dispersion/erreur type du parent suggère seulement un ordre de grandeur de 0,57 pour la dispersion résiduelle du régresseur, en centaines de milliers. Si l'écart de variation deux ans–dix ans a une dispersion de 4,5 pb, l'erreur type attendue vaut \(4,5/(0,57\sqrt{250})=0,50\) pb : un effet de 2 pb est nettement détectable. Ces deux dispersions restent des hypothèses de puissance à auditer, non des faits mesurés sur ce contraste.

---

### J05 — La concession d'adjudication après 2021, sans courbe du Trésor
- **Parent et différence** : `Parent A`. Je change la source de données et la statistique : le rendement effectivement obtenu à l'adjudication est comparé à un prix théorique calculé uniquement avec la courbe zéro-coupon de la Fed. Cette concession ne dépend donc ni des `DGS` ni de la méthode de courbe du Trésor, et peut révéler une rupture que le spread entre deux courbes ne voit pas.
- **Question** : La disparition de la pression après 2021 apparaît-elle aussi dans une concession d'adjudication construite sans la courbe du Trésor ?
- **Hypothèse falsifiable** : Si la disparition est un phénomène de marché, la concession moyenne des réouvertures baisse d'au moins 1 pb après 2021 ; si elle tient surtout à la méthode de la courbe du Trésor, elle ne devrait pas connaître cette chute.
- **Prédiction chiffrée** : En notant \(C\) la concession en pb et \(\Delta=\bar C_{1991-2021}-\bar C_{2022-2026}\), je prédis \(\Delta=+1{,}2\) pb, avec une plage plausible de +0,9 à +1,5 pb ; je ne prédis pas le niveau de \(C\), qui peut contenir une prime de liquidité.
- **Test de mort** : Régression de \(C_i\) sur un indicateur post-2021 et des effets fixes d'échéance, erreurs types groupées par mois, sur les réouvertures de 1991 à octobre 2026. L'explication par une disparition réelle d'au moins 1 pb est éliminée si la borne supérieure de l'IC à 90 % de \(\Delta\) est inférieure à +1,0 pb ; une simple absence de significativité avec un intervalle large ne suffit pas.
- **Données** : API des adjudications, notamment `reopening`, `high_yield`, `interest_rate`, `auction_date`, `issue_date`, `maturity_date` et `cusip` : `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/auctions_query` ; courbe GSW, colonnes `SVENY01` à `SVENY30` : `https://www.federalreserve.gov/pubs/feds/2006/200628/feds200628.csv`. Accès vérifié selon le brief ; codes HTTP non retestés faute d'outil, donc non inventés.
- **Méthode** : Pour chaque titre, reconstruire les flux de coupon et de principal à la date de règlement. Les actualiser avec les zéro-coupons GSW interpolés, puis convertir le prix obtenu en rendement actuariel avec la même convention que `high_yield` ; \(C=100(y_{\text{adjudication}}-y_{\text{GSW}})\). Comparer les périodes à effets fixes d'échéance, avec une réplication secondaire limitée aux 10 et 30 ans pour conserver la composition.
- **Ce qui serait nouveau** : Cela apporterait une mesure publique indépendante, directement liée au résultat de l'adjudication, au débat « marché ou mesure » et prolongerait l'observation jusqu'en 2026. Lou, Yan et Zhang (2013 ; à vérifier) et Fleming, Liu et Nguyen (2026 ; référence indiquée comme vérifiée dans le registre, comparaison détaillée à vérifier) sont les travaux les plus proches.
- **Rôle de l'IA** : Un agent écrit l'extracteur et les calculs de flux, un second réimplémente le rendement GSW et le verdict sans lire les estimations du premier. L'humain valide les conventions de taux sur quelques exemples avant le gel. La préinscription, les exclusions et les seuils sont hachés en SHA-256 avant lecture des concessions ; le verdict est recalculé depuis les fichiers bruts par un script séparé.
- **Coût et durée** : Portable seul ; environ 4 millions de tokens pour développement, revue croisée et documentation, plafond 14 USD ; 5 à 6 semaines à temps partiel.
- **Risques** : \(C\) peut être dominé par les conventions de prix, la liquidité du titre ou une erreur de la courbe GSW plutôt que par la pression temporaire. Même une absence de chute ne démontrerait alors pas l'artefact du Trésor. Une dispersion supérieure à celle retenue pour la puissance rendrait également le test non concluant.
- **Valeur si l'hypothèse meurt** : On pourra encore écrire qu'une concession indépendante ne confirme pas une chute de 1 pb, donner une borne supérieure à cette chute et documenter précisément ce que les deux familles de mesures peuvent et ne peuvent pas identifier.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai construit une mesure publique de concession aux réouvertures du Trésor, indépendante de la courbe du Trésor, et testé sa rupture après 2021. » Graphique unique : concessions moyennes avant/après 2021 par échéance, avec IC et seuil préinscrit. Métiers : taux et obligataires, banque centrale, recherche quantitative, structuration et gestion de taux.
- **Arithmétique de puissance** : Je retiens au moins 400 réouvertures avant 2022 et 100 après. La dispersion de \(C\) n'étant pas mesurée, j'utilise prudemment \(\sigma_C=3{,}5\) pb, contre 2,57 pb pour le \(V\) du parent, et le facteur de regroupement mensuel observé dans le parent, \(0{,}16/(2{,}57/\sqrt{321})\simeq1{,}12\). Ainsi \(SE(\Delta)\simeq1{,}12\times3{,}5\sqrt{1/400+1/100}=0{,}44\) pb. L'effet prédit donne \(t\simeq2{,}7\), une puissance d'environ 85 % à 5 % unilatéral et un effet minimal détectable avec 80 % de puissance de 1,09 pb : le test peut trancher, mais sans sous-échantillon principal supplémentaire.

---

### J06 — Pression d'adjudication : bosse passagère ou saut permanent ?
- **Parent et différence** : `Parent A`. Je change la statistique et l'identification : au lieu du seul contraste symétrique \(V\), je sépare la concession avant l'adjudication du retournement après celle-ci. Le parent ne peut pas distinguer une pression temporaire d'un déplacement de niveau survenant le jour J.
- **Question** : La pression mesurée aux réouvertures correspond-elle à une bosse de rendement qui se résorbe, ou à un saut de niveau qui persiste après l'adjudication ?
- **Hypothèse falsifiable** : Une pression temporaire implique qu'au moins la moitié du contraste moyen du parent se résorbe entre J et J+5.
- **Prédiction chiffrée** : Avec \(C=100[E(J)-E(J-5)]\) et \(R=100[E(J)-E(J+5)]\), donc \(V=C+R\), je prédis \(C\simeq+0{,}46\) pb et \(R\simeq+0{,}45\) pb ; à J+5, le rendement serait donc presque revenu à son niveau de J−5.
- **Test de mort** : Sur les mêmes 321 réouvertures et avec des erreurs types groupées par mois, le caractère temporaire au sens préinscrit est mort si \((\widehat R-0{,}45)/SE(\widehat R)<-1{,}645\), c'est-à-dire si tout l'IC à 90 % est sous 0,45 pb. Un retournement positif n'est établi que si \(\widehat R/SE>1{,}645\) ; la zone intermédiaire est non concluante.
- **Données** : `DGS10`, `DGS20`, `DGS30`, par exemple `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10` ; `SVENPY10/20/30` dans `https://www.federalreserve.gov/pubs/feds/2006/200628/feds200628.csv` ; calendrier et réouvertures dans l'API `auctions_query` citée en J05. Sources vérifiées selon le brief ; HTTP non retesté faute d'outil.
- **Méthode** : Reconstituer exactement \(E\) du parent, puis estimer conjointement les moyennes de \(C\) et \(R\), avec effets fixes d'échéance et regroupement par mois. Tracer le profil de J−5 à J+5 sans réestimer les dates. Les sous-périodes avant/après 2021 sont secondaires ; les placebos à J−10 et J+10 vérifient qu'un événement décalé ne produit pas la même décomposition.
- **Ce qui serait nouveau** : Le test porte sur une restriction interne non exploitée du résultat survivant : \(V>0\) n'implique nullement \(R>0\). Cela distingue concession et retournement sur une période récente, plutôt que de répliquer seulement un cycle d'adjudication ancien. Lou, Yan et Zhang (2013 ; à vérifier) et Fleming, Liu et Nguyen (2026 ; détail des profils événementiels à vérifier) sont les références proches.
- **Rôle de l'IA** : Les agents produisent deux calculs indépendants des trois dates et des placebos ; l'humain choisit avant le gel la définition de « temporaire ». Le script de verdict vérifie algébriquement \(V=C+R\), recalcule les moyennes groupées depuis les observations brutes et applique les seuils sans intervention générative.
- **Coût et durée** : Calcul négligeable ; environ 2 millions de tokens, plafond 7 USD ; 4 semaines.
- **Risques** : Les annonces macroéconomiques proches peuvent rendre le profil bruité. Un retournement partiel, par exemple 0,30 pb, resterait intéressant mais ne satisferait pas l'hypothèse forte. Enfin, la décomposition ne prouve pas à elle seule un mécanisme d'inventaire.
- **Valeur si l'hypothèse meurt** : Si \(R\) est petit ou nul, le résultat du parent devra être décrit comme un déplacement persistant plutôt que comme une pression temporaire ; c'est une restriction importante sur son interprétation et sur la suite du programme de recherche.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai décomposé la pression d'adjudication en concession anticipée et retournement, avec un protocole préinscrit et vérifié indépendamment. » Graphique unique : profil moyen de \(E\) de J−5 à J+5, avec IC et les deux pentes \(C\) et \(R\). Métiers : recherche taux, banque centrale, gestion obligataire et analyse de marchés primaires.
- **Arithmétique de puissance** : Les 321 adjudications restent l'unité d'analyse, avec 134 grappes mensuelles. Même sans supposer que \(R\) est moins dispersé que \(V\), je prends \(\sigma_R=2{,}57\) pb et le \(SE\) du parent comme planification, soit \(SE(\widehat R)\simeq0{,}16\) pb. L'effet de 0,45 pb donne \(t\simeq2{,}8\), environ 88 % de puissance pour détecter un retournement positif ; l'effet minimal détectable à 80 % est \(2{,}485\times0{,}16\simeq0{,}40\) pb. Sous un saut permanent \(R=0\), le critère de mort a également environ 88 % de puissance.

---

### J07 — Peut-on prévoir la partie révisée du chiffre d'emploi ?
- **Question** : Deux indicateurs publics disponibles à la première publication permettent-ils de prévoir hors échantillon une part économiquement substantielle de sa révision future ?
- **Hypothèse falsifiable** : Une estimation initiale très éloignée de sa tendance récente et les révisions déjà publiées prédisent une partie du bruit de mesure.
- **Prédiction chiffrée** : Une correction linéaire réduira d'environ **15 %** l'erreur quadratique de prévision de la troisième estimation, relativement à une correction par le seul biais historique.
- **Test de mort** : Après 60 publications d'apprentissage, évaluer chronologiquement les publications restantes du parent ; exiger simultanément un \(R^2\) hors échantillon d'au moins **5 %** et une statistique de Clark-West supérieure à **1,645**, avec correction HAC de quatre publications. Sinon, abandon de l'hypothèse d'un bruit publiquement prévisible avec cette spécification.
- **Données** : Millésimes exacts de `PAYEMS` : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS&vintage_date=AAAA-MM-JJ`. Aucun taux de marché ni consensus propriétaire n'est nécessaire au test de mort. Accès vérifié selon le brief ; **code HTTP non communiqué et non testé personnellement**.
- **Méthode** :  
  Prévoir première moins troisième estimation avec une constante et deux variables : écart du chiffre initial à la médiane des douze variations connues auparavant ; somme des deux révisions annoncées ce jour-là.  
  Réestimer par MCO en fenêtre croissante, uniquement sur les cohortes dont la troisième estimation était déjà disponible à cette date.  
  Comparer à la moyenne historique du bruit calculée sur les mêmes cohortes admissibles ; traduire les prévisions de bruit en prévisions de troisième estimation.  
  Conserver tous les échecs et aucune recherche de variables, de transformations ou de fenêtres sur l'échantillon d'évaluation.
- **Ce qui serait nouveau** : Le parent étudie la réaction à un bruit défini ex post ; ce projet demande quelle fraction était effectivement prévisible avec une règle publique. Cela fournit une condition nécessaire, mais non suffisante, pour discuter le filtrage par les marchés. Mankiw et Shapiro, travaux sur « news versus noise » dans les révisions — **à vérifier** ; Krueger et Fortson (2003) — **à vérifier**.
- **Rôle de l'IA** : L'IA propose et implémente le pipeline sans accès à la portion d'évaluation. L'humain gèle les deux variables et scelle leur définition. Chaque prévision est écrite et hachée avant déblocage du troisième millésime correspondant ; un évaluateur séparé vérifie les dates de disponibilité et calcule les scores depuis les fichiers bruts. Il s'agit d'un rejeu historique contrôlé, pas d'une expérience prospective.
- **Coût et durée** : CPU seul ; moins de dix minutes d'estimation après constitution des millésimes ; **15 USD** maximum ; **5 semaines**.
- **Risques** : Les révisions peuvent être essentiellement de nouvelles informations. Le pouvoir prédictif peut provenir d'un régime ancien et ne pas se transporter. Une correction statistiquement utile ne prouve pas que les opérateurs ne l'effectuent pas déjà.
- **Valeur si l'hypothèse meurt** : Établir qu'une correction publique très simple ne bat pas le biais historique, ce qui renforce la prudence dans l'interprétation du parent comme erreur des marchés.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai évalué en millésimes réels une correction publique des premières estimations d'emploi américain. » Graphique : différence cumulée de pertes quadratiques hors échantillon. Métiers : nowcasting, recherche macro, banque centrale, équipes de données économiques.
- **Parent et différence** : **Parent B** ; changement d'**identification** et de **statistique**, d'une régression explicative ex post à une prévision séquentielle utilisant seulement l'information alors disponible.
- **Arithmétique de puissance** : Environ **249 prévisions**, avec hypothèse prudente de **220 observations effectives**. Pour une réduction de variance \(q=0,15\), une approximation gaussienne du différentiel de pertes donne un rapport signal/bruit \(\sqrt{220q}/2\simeq2,87\), compatible avec une puissance directionnelle proche de **89 %**. Cette approximation n'est pas une puissance exacte de Clark-West : l'évaluateur la complétera par simulations scellées, utilisant uniquement l'apprentissage. Une amélioration de 2 % serait probablement indécidable ; la cible économique est volontairement plus exigeante.

---

### J08 — Prévoir le taux de la BCE : compétence ou chance chez les prévisionnistes ?
- **Parent et différence** : libre. Motivée par le résultat « Les surprises de la BCE sont-elles prévisibles hors échantillon avec des données publiques ? », éliminé (R² hors échantillon de −0,5 %, Clark-West 0,59). Si aucun modèle public ne bat le marché, reste à savoir si certaines personnes le font durablement : je passe du prédicteur statistique au prévisionniste individuel, avec les hypothèses de taux directeur de l'enquête de la BCE (2002-2026), source ajoutée à la liste vérifiée.
- **Question** : certains prévisionnistes de l'enquête de la BCE anticipent-ils le taux directeur à un an durablement mieux que les autres, au-delà de ce que la chance produit ?
- **Hypothèse falsifiable** : oui : la dispersion des scores moyens entre prévisionnistes dépasse celle que donne un tirage au hasard des identités.
- **Prédiction chiffrée** : score = rang normalisé (0 à 1) de l'erreur absolue dans chaque vague. Variance entre prévisionnistes du score moyen : 1,5 à 2,5 fois la médiane obtenue sous permutation ; corrélation de rang des scores moyens entre 2002-2013 et 2014-2025 : +0,3.
- **Test de mort** : prévisionnistes ayant au moins 20 réponses ; hypothèse de taux à l'horizon le plus proche d'un an ; 10 000 permutations des identités par blocs de quatre vagues consécutives (pour respecter le chevauchement des horizons). L'idée meurt si la valeur p de la variance observée dépasse 0,05, ou si le résultat disparaît quand on retire les vagues où plus de la moitié des réponses sont identiques (taux plancher).
- **Données** : enquête de la BCE auprès des prévisionnistes professionnels, réponses individuelles et hypothèses de taux (archive zip ; libellé exact de la question, horizon et stabilité des identifiants anonymes : à vérifier) ; taux directeurs réalisés sur FRED (`ECBMRRFR`, `ECBDFR`, identifiants de mémoire, à vérifier). Code HTTP : non testé par moi (aucun outil) ; sources de la liste vérifiée du brief.
- **Méthode** : apparier chaque hypothèse au taux réalisé ; rang normalisé par vague, ce qui neutralise la difficulté de la période ; score moyen par prévisionniste ; distribution sous permutation par blocs ; persistance entre deux moitiés de l'échantillon. Lecture secondaire : les meilleurs sur le taux le sont-ils aussi sur l'inflation à un an ?
- **Ce qui serait nouveau** : le test compétence-chance appliqué aux hypothèses individuelles de taux directeur en zone euro. Proches, de mémoire : D'Agostino, McQuinn et Whelan (2012, enquête américaine, peu de compétence durable, à vérifier) ; Fama et French (2010, même logique pour les fonds, à vérifier) ; un document de travail de la BCE sur la performance individuelle dans son enquête (référence incertaine).
- **Rôle de l'IA** : un agent nettoie l'archive et apparie les horizons, un second vérifie vingt réponses tirées au hasard contre les fichiers bruts ; l'humain fixe l'horizon, le seuil de 20 réponses et la taille des blocs, scellés avant calcul des erreurs ; la valeur p sort d'un script séparé, avec graine publiée.
- **Coût et durée** : calcul de quelques minutes ; moins de 10 USD ; 5 semaines (le nettoyage de l'archive est le gros du travail).
- **Risques** : un biais constant (toujours trop haut) peut passer pour de la compétence sur un cycle de hausse, d'où le test sur deux moitiés ; panel non équilibré ; années de taux plancher sans information ; identifiants éventuellement réattribués.
- **Valeur si l'hypothèse meurt** : résultat cohérent avec l'élimination du registre : ni les modèles publics ni les individus ne prévoient durablement mieux le taux de la BCE ; on peut l'écrire avec une borne sur la compétence détectable.
- **Ce que ça dit au jury et aux recruteurs** : CV : « A testé par permutation, sur 24 ans de réponses individuelles à l'enquête de la BCE, si des prévisionnistes anticipent le taux directeur durablement mieux que le hasard. » Graphique : distribution des scores moyens observés superposée à l'enveloppe des permutations. Métiers : banque centrale, recherche économique, sélection de gérants et analyse de performance en gestion d'actifs, recherche quantitative.
- **Arithmétique de puissance** : environ 45 prévisionnistes avec 50 vagues chacun en moyenne, soit 12 ou 13 blocs annuels indépendants par personne. Écart-type d'échantillonnage du score moyen : 0,29 / √12,5 ≈ 0,08. Avec un écart-type de compétence vraie de 0,06, le rapport de variances attendu est de 1,5 ; l'écart-type de ce rapport sous l'hypothèse nulle est d'environ √(2/44) ≈ 0,21, soit 2,5 écarts-types et une puissance d'environ 80 %. Le test tranche si la compétence vraie atteint 0,06 en unités de rang ; à 0,04 il ne la verrait pas, et la conclusion serait alors une borne, pas une absence.

---

### J09 — Pression des adjudications américaines et propagation dynamique aux rendements souverains européens
- **Parent et différence** : `Parent A`. Changement **du marché** (passage du marché domestique américain à la transmission internationale vers les courbes souveraines de la zone euro via `Dataset_EA-MPD.xlsx` et les courbes quotidiennes de la BCE) et de **la méthode** (projections locales de Jordà de $J-5$ à $J+5$ au lieu d'une mesure ponctuelle unique). Cela tranche une question ouverte du Parent A : la pression d'adjudication est-elle une friction purement locale de tenue de marché (spécifique au CUSIP émis) ou un choc d'offre global de duration absorbé par les arbitragistes internationaux ?
- **Question** : Le cycle de pression de prix autour des adjudications du Trésor américain à 10 et 30 ans se transmet-il jour par jour aux rendements souverains de la zone euro (Bund allemand et courbe AAA de la BCE) ?
- **Hypothèse falsifiable** : Entre $J-5$ et le jour $J$ d'une réouverture américaine à 10 ou 30 ans, le rendement souverain européen à 10 ans (clôture européenne suivant l'adjudication ou lendemain matin) connaît un cycle en V inversé positif (hausse jusqu'à $J$, détente de $J$ à $J+5$), proportionnel à la pression observée simultanément sur le Trésor américain.
- **Prédiction chiffrée** : Le cycle en V européen $V^{\text{EUR}}_{10} = 2 y^{\text{EUR}}_{10}(J+1) - y^{\text{EUR}}_{10}(J-4) - y^{\text{EUR}}_{10}(J+6)$ (décalé d'un jour ouvré car l'adjudication américaine a lieu à 13h00 heure de New York, après la clôture européenne) atteint entre +0,30 pb et +0,60 pb en moyenne, soit un coefficient de transmission (pass-through) de 0,30 à 0,50 de la pression américaine.
- **Test de mort** : En projection locale à l'horizon du pic ($h = +1$ jour ouvré en Europe pour une adjudication US à $J$), l'idée meurt si la réponse moyenne $V^{\text{EUR}}_{10}$ sur 2004-2026 (~260 réouvertures US à 10 et 30 ans, hors jours de réunion de la BCE identifiés par `Dataset_EA-MPD.xlsx`) a une statistique $t$ (erreurs types de Newey-West) inférieure à 1,96.
- **Arithmétique de puissance** : De septembre 2004 à 2026, on compte ~260 réouvertures américaines à 10 et 30 ans (8 par an par échéance). En mesurant $y^{\text{EUR}}_{10}$ comme l'écart entre le taux au pair à 10 ans de la courbe AAA de la BCE et le taux court (ou sa courbure locale 5s10s30s sur la courbe YC de la BCE), l'écart-type de la combinaison en V sur 10 jours est du même ordre que sur le Parent A (~2,6 pb). Sur 260 événements (~130 mois indépendants), l'erreur type attendue est de $2,6 / \sqrt{130} \approx 0,23$ pb (et encore plus précise en contrôlant par les jours de réunion BCE). Un effet de 0,48 pb donne $t \approx 2,10$, et dans la régression de transmission directe de $\Delta y^{\text{EUR}}$ sur $V^{\text{US}}$ (ratio signal/bruit accru), $t > 2,5$. Le test peut trancher.
- **Données** : API des adjudications du Trésor américain (`auctions_query`, HTTP 200 vérifié), FRED (`DGS10`, `DGS30`) et `feds200628.csv` (vérifiés), API de la BCE pour la courbe des rendements souverains AAA quotidienne depuis 2004 (`https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y`, `SR_5Y`, `SR_30Y`, HTTP 200 vérifié), et `Dataset_EA-MPD.xlsx` (vérifié) pour exclure ou contrôler les jours de réunion de la BCE.
- **Méthode** : Projections locales de Jordà (1985/2005) estimant la trajectoire cumulée du rendement (et de la courbure 5s10s30s) AAA de la zone euro pour chaque horizon $h \in \{-5, \dots, +6\}$ jours ouvrés autour des réouvertures américaines à 10 et 30 ans. Contrôle strict du décalage horaire (13h00 EST = 19h00 CET) et neutralisation des annonces de la BCE via `Dataset_EA-MPD.xlsx`.
- **Ce qui serait nouveau** : Teste pour la première fois si le cycle d'adjudication de Lou, Yan et Zhang (2013) traverse l'Atlantique, ce qui permet de distinguer empiriquement les théories d'inventaire local des Primary Dealers américains des théories de capacité globale d'absorption du risque de duration. Travaux proches : Lou, Yan et Zhang (2013, *à vérifier*), Greenwood et Vayanos (2014, *à vérifier*).
- **Rôle de l'IA** : L'agent aligne les calendriers de jours ouvrés américains et européens (TARGET) et code l'estimateur par projections locales. L'humain vérifie le décalage horaire exact entre l'adjudication US (13h00 EST) et le fixing de la courbe BCE, et scelle la spécification avant de lire les données européennes. Un script indépendant génère le verdict statistique.
- **Coût et durée** : Calcul : < 3 minutes. Appels de modèles : < 3 USD. Durée : 5 semaines.
- **Risques** : Bruit macroéconomique transatlantique entre $J-5$ et $J+5$ si l'on n'utilise pas la mesure relative de courbure sur la courbe de la BCE.
- **Valeur si l'hypothèse meurt** : L'absence de contagion à la courbe européenne (tandis que le choc américain de 1,1 pb à 10 et 30 ans est très fort dans le Parent A) prouverait que la pression d'adjudication est une pure friction de microstructure propre aux Primary Dealers américains et non un choc macro-financier sur le prix mondial de la duration.
- **Ce que ça dit au jury et aux recruteurs** : *Ligne de CV* : « Estimé par projections locales la contagion internationale des adjudications du Trésor américain vers la courbe des taux de la zone euro (2004-2026). » *Graphique unique* : Réponse impulsionnelle (J-5 à J+6) superposant le V inversé du taux américain à 10 ans et la réponse décalée de 24h de la courbe AAA de la BCE. *Métiers* : Trading taux G10, stratégie obligataire internationale, banque centrale (stabilité financière et marchés).

---

### J10 — La courbe corrige-t-elle le bruit quand les révisions arrivent ?
- **Question** : Le mouvement de pente associé à une surestimation initiale de l'emploi s'inverse-t-il lors des deux publications qui révisent ce chiffre ?
- **Hypothèse falsifiable** : Une surestimation initiale est suivie d'une baisse cumulée du taux à deux ans relativement au dix ans lors des deux annonces de révision.
- **Prédiction chiffrée** : La correction cumulée sera d'environ **−2 pb par 100 000 emplois surestimés**, sur les deux annonces suivantes.
- **Test de mort** : Tester \(\beta_1+\beta_2<0\), où les deux coefficients portent sur les variations de pente aux deux annonces suivantes ; statistique studentisée, seuil unilatéral de 5 %, bootstrap temporel par blocs de six publications. Échantillon : cohortes du parent dont les deux révisions sont disponibles. L'absence de rejet élimine l'hypothèse de correction détectable, sans établir une absence de correction.
- **Données** : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2,DGS10` ; millésimes ALFRED `PAYEMS` et `UNRATE` via `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<SERIE>&vintage_date=AAAA-MM-JJ`. Accès vérifié selon le brief ; **code HTTP non communiqué, aucun test personnel**. Les dates de publication sont reconstruites à partir de l'apparition du nouveau mois dans les millésimes et les ambiguïtés documentées avant estimation.
- **Méthode** :  
  Construire des projections locales en temps de publication, aux horizons une et deux annonces, pour la variation de \(DGS2-DGS10\).  
  Contrôler les nouveaux chiffres d'emploi et de chômage publiés à chaque annonce, leur référence adaptative connue auparavant, et les révisions concernant les autres cohortes.  
  Ne pas contrôler la révision de la cohorte étudiée : elle constitue le mécanisme recherché. Ne pas sélectionner les observations selon la réaction initiale des prix.  
  Additionner les deux coefficients et leurs covariances ; traiter explicitement le chevauchement des observations.
- **Ce qui serait nouveau** : Passer d'une corrélation au jour de la première estimation à la recherche d'une correction aux dates où l'information devient publique. Gilbert (2011) et Krueger et Fortson (2003) — **à vérifier**, notamment pour l'étude des annonces de révision plutôt que des premières publications.
- **Rôle de l'IA** : Un agent construit la table « cohorte d'emploi–annonce de révision » ; un autre en vérifie des exemples sans consulter les rendements. L'humain scelle les horizons, les contrôles, la prédiction et les règles de chevauchement. Le code de verdict, détenu séparément, repart des millésimes et des taux bruts ; l'agent exécutant ne peut choisir une fenêtre après lecture des résultats.
- **Coût et durée** : CPU seul, bootstrap de quelques dizaines de minutes ; plafond de **20 USD** ; **5 à 6 semaines**.
- **Risques** : Les annonces de révision contiennent simultanément un nouveau chiffre d'emploi ; sans consensus, leur séparation reste imparfaite. Une correction peut intervenir entre annonces ou être anticipée. Le test ne constitue donc ni une preuve d'inefficience ni un backtest exploitable.
- **Valeur si l'hypothèse meurt** : Montrer que la réaction initiale ne s'accompagne pas d'un retour détectable aux dates naturelles de résolution ; distinguer absence de correction mesurée, anticipation et manque de puissance.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai suivi la réaction de la courbe des taux depuis une première publication d'emploi jusqu'à ses deux révisions. » Graphique : réponse initiale puis correction cumulée aux deux annonces suivantes, avec intervalles. Métiers : recherche taux, stratégies macro, analyse des annonces, banque centrale.
- **Parent et différence** : **Parent B** ; changement de **statistique**, de **fenêtre événementielle** et d'**identification temporelle** : l'information est recherchée aux dates où l'erreur devient observable, et non seulement à sa création.
- **Arithmétique de puissance** : Jusqu'à **309 cohortes**, mais deux fenêtres successives partagent des annonces ; retenir environ **150 observations effectives** pour le dimensionnement. Avec une dispersion résiduelle cumulée de 5 pb et une dispersion résiduelle du bruit de 0,57, l'erreur type attendue est \(5/(0,57\sqrt{150})=0,72\) pb ; effet de −2 pb, puissance unilatérale proche de **87 %**. Le chiffre de 5 pb est une hypothèse, pas une dispersion héritée du parent. Une erreur type auditée supérieure à 0,8 pb déclenche un verdict explicite de puissance insuffisante pour la cible.

---

### J11 — Le taux à 2 ans réagit-il au bruit des autres statistiques ? Réplication sur des jours neufs
- **Parent et différence** : Parent B. Je change l'échantillon : mêmes régression et taux, mais sur des jours que le parent n'a jamais lus, soit les publications des ventes au détail, de l'estimation avancée du PIB, de la production industrielle et des commandes de biens durables, plus l'emploi de 1976 à 1989. Le parent tient à t = 2,45 et tombe à 1,75 sans les années 2020 ; seule une réplication sur données indépendantes dit si l'effet est une propriété générale des statistiques révisées ou un accident de l'emploi récent.
- **Question** : le jour d'une publication, le taux à 2 ans bouge-t-il dans le sens de la part du chiffre qui sera révisée, pour d'autres statistiques que l'emploi de 1990-2025 ?
- **Hypothèse falsifiable** : oui, avec un effet positif, proportionnel à la sensibilité habituelle du taux à chaque statistique.
- **Prédiction chiffrée** : par écart-type de N (première moins troisième estimation), en pb de taux à 2 ans : ventes au détail +0,45 ; PIB avancé +0,45 ; production industrielle +0,15 ; biens durables +0,2 ; emploi 1976-1989 +2,4 (taux alors deux fois plus volatil). Référence : +1,25 pour l'emploi du parent. Ces ordres de grandeur sont des estimations de mémoire.
- **Test de mort** : pour chaque bloc, MCO de la variation de `DGS2` le jour de la publication sur N standardisé, avec la médiane des douze dernières valeurs connues en contrôle, erreurs HC3, exclusions du parent. Statistique : Z de Stouffer = somme des cinq t divisée par √5. L'idée survit si Z > 1,645 ; elle meurt si Z < 0,45 (la généralisation proportionnelle est alors rejetée à 5 %) ou si le Z placebo de la veille dépasse 2 en valeur absolue. Correction de Holm pour les lectures bloc par bloc.
- **Données** : millésimes ALFRED de `RSAFS`, `GDPC1`, `INDPRO`, `DGORDER`, `PAYEMS` (dates de début des millésimes : à vérifier, de mémoire 1991 pour le PIB, vers 2001 pour les ventes au détail) ; FRED `DGS2` (depuis juin 1976). Code HTTP : non testé par moi (aucun outil) ; sources de la liste vérifiée du brief.
- **Méthode** : reprendre le code du parent sans le modifier, en changeant seulement la série ; reconstruire première et troisième estimations par millésime ; un coefficient par bloc ; combinaison de Stouffer ; placebo à J−1 ; graphique en forêt.
- **Ce qui serait nouveau** : la même mesure de réaction au bruit sur cinq statistiques, avec une règle de combinaison écrite avant lecture. Proches (cités par le brief) : Gilbert (2011) ; Gilbert, Scotti, Strasser et Vega (2017). De mémoire : Mankiw et Shapiro (1986), à vérifier.
- **Rôle de l'IA** : un agent adapte le chargement des millésimes ; un autre vérifie que le code de régression est identique à celui du parent (comparaison de fichiers) ; l'humain fixe les blocs, les prédictions et la règle de Stouffer, scellés avant lecture ; verdict par script séparé.
- **Coût et durée** : calcul négligeable ; moins de 10 USD ; 4 à 5 semaines (le calendrier exact des publications anciennes demande du soin).
- **Risques** : même limite de fond que le parent (pas de consensus gratuit) ; jours de publication partagés avec d'autres statistiques ; millésimes trop courts pour un bloc.
- **Valeur si l'hypothèse meurt** : l'effet du parent serait propre à l'emploi, ou fragile ; avec le résultat décennal du parent, cela conduit à le déclasser, ce qui est un résultat net.
- **Ce que ça dit au jury et aux recruteurs** : CV : « A répliqué sur cinq blocs de publications indépendantes (environ 1 300 jours) un effet de réaction des taux au bruit statistique, avec une règle de décision scellée. » Graphique : forêt des cinq coefficients avec intervalles, et celui du parent. Métiers : recherche économique, stratégie taux, banque centrale.
- **Arithmétique de puissance** : environ 285, 135, 425, 300 et 160 publications, sur des jours distincts donc quasi indépendants. Écart-type du taux ces jours-là supposé de 6,5, 7, 6, 6 et 18 pb ; erreurs types de 0,39, 0,60, 0,29, 0,35 et 1,42 pb par écart-type de N ; t attendus de 1,2, 0,75, 0,5, 0,6 et 1,7 ; Z attendu d'environ 2,1. Puissance d'environ 70 % à 5 % unilatéral ; zone grise (0,45 à 1,645) dans environ un cas sur quatre. Le test tranche le plus souvent, pas toujours : c'est la fiche la moins puissante des cinq, et je le dis.

---

### J12 — Adjudications du Trésor : pression sur la courbure de la courbe de la Fed et échéances de 2 à 7 ans
- **Parent et différence** : `Parent A`. Changement de **la statistique** (mesure de la pression par la courbure locale sur la seule courbe de la Fed GSW, sans utiliser la série `DGS` du Trésor) et de **l'échantillon** (extension aux échéances de 2, 3, 5 et 7 ans sur 1980-2026). Cela tranche la question ouverte par le parent : la disparition de l'effet après 2021 vient-elle du changement de méthode de la courbe du Trésor le 6 décembre 2021, ou d'une vraie évolution de la liquidité du marché ?
- **Question** : La pression de prix aux adjudications du Trésor américain et son affaiblissement après 2021 subsistent-ils lorsqu'on les mesure par la déformation locale de la seule courbe ajustée de la Fed sur les échéances de 2, 3, 5 et 7 ans ?
- **Hypothèse falsifiable** : Lors d'une adjudication à l'échéance $m \in \{2, 3, 5, 7\}$ ans, l'écart de courbure locale $C_m(t) = \text{SVENPY}_m(t) - \frac{1}{2}[\text{SVENPY}_{m-1}(t) + \text{SVENPY}_{m+1}(t)]$ forme un pic positif temporaire $V_m = 2 C_m(J) - C_m(J-5) - C_m(J+5) > 0$, et ce pic reste strictement positif après le 6 décembre 2021.
- **Prédiction chiffrée** : Sur l'échantillon complet (1980-2026), la pression de courbure moyenne $V_m$ est comprise entre +0,30 pb et +0,80 pb ; sur le sous-échantillon post-décembre 2021, elle reste d'au moins +0,25 pb (contre un effondrement proche de 0 sur l'ancienne mesure du Parent A).
- **Test de mort** : Test $t$ d'étude d'événement avec erreurs types groupées par date d'adjudication (pour corriger la corrélation des émissions simultanées). L'idée meurt si, sur 1980-2026, $t < 2,5$ sur la moyenne de $V_m$, ou si sur le sous-échantillon post-décembre 2021 (environ 200 adjudications à 2, 3, 5 et 7 ans) la moyenne de $V_m$ n'est pas significativement positive au seuil de 5 % ($t < 1,645$, test unilatéral).
- **Arithmétique de puissance** : Les adjudications à 2, 3, 5 et 7 ans sont mensuelles : 48 par an, soit ~2 000 adjudications de 1980 à 2026 (et ~760 de 2010 à 2026, groupées en ~190 dates indépendantes). Comme $C_m$ neutralise le niveau et la pente de la courbe GSW, l'écart-type de $V_m$ est inférieur ou égal aux 2,57 pb du Parent A (attendu autour de 1,5 pb). Sur 2010-2026, l'erreur type attendue est $\le 1,5 / \sqrt{190} \approx 0,11$ pb. Sur l'après-2021 (~200 adjudications, ~100 dates), l'erreur type est $\le 1,5 / \sqrt{100} = 0,15$ pb : un effet de 0,30 pb donne $t \ge 2,0$. Le test peut nettement trancher.
- **Données** : API des adjudications du Trésor américain (`https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query`, HTTP 200 vérifié) et courbe quotidienne ajustée de la Fed Gürkaynak, Sack et Wright (`https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv`, séries `SVENPY01` à `SVENPY08`, HTTP 200 vérifié).
- **Méthode** : Étude d'événement sur la double différence de courbure $V_m = 100 \times [2 C_m(J) - C_m(J-5) - C_m(J+5)]$ autour du jour d'adjudication $J$. Estimation par MCO avec effets fixes d'échéance et erreurs types groupées par date calendaire. Test de rupture structurelle de Chow à la date exacte du changement méthodologique du Trésor (6 décembre 2021).
- **Ce qui serait nouveau** : Sépare pour la première fois l'artefact statistique de la spline d'Hermite du Trésor (documenté sur l'exercice 2021 par le Parent A) de la vraie pression d'offre sur le segment intermédiaire (2-7 ans). Travaux proches : Lou, Yan et Zhang (2013, *à vérifier*), Fleming, Liu et Nguyen (2026, *vérifié*).
- **Rôle de l'IA** : Un premier agent code l'extraction de l'API du Trésor et l'alignement calendaire avec `feds200628.csv`. L'humain vérifie la définition algébrique des papillons de courbure $C_m$ et scelle par sha256 le script de test avant l'exécution sur la période post-2021. Un second agent indépendant exécute le script de verdict sur le fichier brut sans que le premier agent puisse modifier ses filtres.
- **Coût et durée** : Calcul sur processeur : moins de 2 minutes. Appels de modèles : < 3 USD. Durée : 4 semaines.
- **Risques** : Le lissage paramétrique de Nelson-Siegel-Svensson dans `feds200628.csv` pourrait trop atténuer les déformations très locales entre $m-1$, $m$ et $m+1$ ans.
- **Valeur si l'hypothèse meurt** : Si $V_m$ est significatif avant 2021 mais nul après, cela prouve rigoureusement que la disparition de la pression d'adjudication n'est pas un artefact de la courbe du Trésor mais une mutation structurelle de l'intermédiation obligataire américaine.
- **Ce que ça dit au jury et aux recruteurs** : *Ligne de CV* : « Isolé l'effet réel des adjudications du Trésor américain (1980-2026) d'un biais méthodologique de la courbe officielle par une étude d'événement sur la courbure de Nelson-Siegel-Svensson. » *Graphique unique* : Trajectoire annuelle comparée de la pression mesurée avec la courbe du Trésor (qui chute en décembre 2021) et par courbure pure GSW. *Métiers* : Trading de taux (desk Treasuries), recherche quantitative obligataire, banque centrale (marchés).

---

### J13 — Règlements du Trésor et taux repo : la pression de quantité mesurée hors de la courbe du Trésor
- **Parent et différence** : Parent A. Je change le marché et la source de données. Le parent mesure la pression sur un rendement qui dépend de la courbe du Trésor, dont la méthode a changé le 6 décembre 2021 ; je la mesure le jour du règlement des adjudications sur le taux repo au jour le jour SOFR, que la Fed de New York calcule à partir de transactions. Cette mesure ne doit rien à la courbe du Trésor et couvre surtout l'après-2021 : elle dit si l'offre de titres déplace encore un prix après 2021, ce que le parent ne peut pas séparer d'un artefact de mesure.
- **Question** : quand le Trésor encaisse le règlement net de ses titres à coupons, le SOFR monte-t-il par rapport au taux servi sur les réserves, en proportion du montant, et seulement quand les réserves ne sont plus abondantes ?
- **Hypothèse falsifiable** : hors période de réserves abondantes, le pic du SOFR au jour de règlement croît avec le règlement net ; en période abondante, la pente est nulle.
- **Prédiction chiffrée** : P = (SOFR − taux des réserves) au jour de règlement moins sa médiane de J−5 à J−1. Périodes non abondantes fixées d'avance (avril 2018–février 2020 ; juillet 2024–octobre 2026) : pente de +0,3 à +0,5 pb par 10 Md USD de règlement net, pic moyen d'environ +2 pb. Période abondante (mars 2020–juin 2024) : pente entre −0,1 et +0,1.
- **Test de mort** : MCO de P sur le règlement net, avec effets fixes de type de date (mi-mois, fin de mois, fin de trimestre) et indicatrice d'échéance d'impôt sur les sociétés, erreurs robustes, 16-18 septembre 2019 exclus d'avance et rapportés à part. L'idée meurt si la pente des périodes non abondantes a t < 2, ou si elle ne dépasse pas celle de la période abondante (t de la différence < 1,645), ou si le placebo calculé à J−1 a |t| > 2.
- **Données** : FRED `SOFR`, `IORB`, `IOER` (avant juillet 2021), `RRPONTSYD`, `WRESBAL` (identifiants de mémoire, à vérifier) ; API des adjudications du Trésor (date d'émission, montant accepté, part de la Fed ; champ du montant arrivant à échéance détenu par le public : à vérifier, sinon recalcul à partir des adjudications passées). Code HTTP : non testé par moi (aucun outil) ; sources de la liste vérifiée du brief.
- **Méthode** : construire le calendrier des règlements de coupons depuis avril 2018 et le règlement net (émissions au public moins tombées) ; calculer P ; estimer la pente par période ; placebo à J−1 ; contrôle par le règlement net de bons. Lecture secondaire, hors test de mort : à niveau égal de réserves rapportées aux actifs bancaires, le pic est-il plus fort en 2024-2026 qu'en 2018 ?
- **Ce qui serait nouveau** : une élasticité « points de base par milliard réglé » tirée du seul calendrier du Trésor, annoncé des semaines à l'avance, avec une prédiction scellée sur 2024-2026. Proches, de mémoire : Afonso, Giannone, La Spada et Williams (courbe de demande de réserves, vers 2022, à vérifier) ; Copeland, Duffie et Yang (« Reserves were not so ample after all », vers 2021, à vérifier) ; notes de la Fed sur septembre 2019 (référence incertaine).
- **Rôle de l'IA** : un agent construit le calendrier et P, un second recalcule le règlement net à partir du fichier brut ; l'humain fixe les périodes, les exclusions et les seuils, scellés (sha256) avant tout téléchargement du SOFR ; le verdict sort d'un script séparé.
- **Coût et durée** : calcul négligeable ; appels de modèles pour le code, moins de 10 USD ; 4 semaines.
- **Risques** : le fait est connu des opérateurs, donc l'intérêt tient à la pente et à la prédiction scellée ; fins de mois contaminées par les bilans des banques (d'où les effets fixes) ; règlement net mal mesuré si le champ des tombées manque.
- **Valeur si l'hypothèse meurt** : une pente nulle après 2024 dirait que les pics du repo viennent du calendrier bancaire et non du Trésor, ce qui contredit la lecture courante.
- **Ce que ça dit au jury et aux recruteurs** : CV : « A estimé, sur 200 dates de règlement du Trésor (2018-2026), la sensibilité du taux repo SOFR au montant réglé selon le niveau des réserves, avec prédiction scellée avant lecture des données. » Graphique : nuage de P contre le règlement net, deux couleurs (réserves abondantes ou non), deux droites. Métiers : banque centrale (mise en œuvre de la politique monétaire), trésorerie et repo en banque, stratégie taux.
- **Arithmétique de puissance** : environ 100 dates non abondantes (46 + 54), indépendantes (deux par mois) ; écart-type de P supposé de 3 pb (non mesuré), écart-type du règlement net d'environ 30 Md USD ; erreur type de la pente = 3 / (10 × 3) = 0,10 pb par 10 Md ; effet prédit 0,3 à 0,5, soit t de 3 à 5. Période abondante : 104 dates, écart-type 1 pb, erreur type 0,03. Le test peut trancher ; il ne le peut plus si l'écart-type de P dépasse 5 pb.

---

### J14 — Emploi américain : la révision à venir est-elle prévisible le jour même ?
- **Parent et différence** : Parent B. Je change la statistique : la variable expliquée n'est plus le taux à 2 ans mais la révision elle-même (N = première moins troisième estimation), prévue hors échantillon avec ce qui est public à 8 h 30 le jour de la publication. Le parent ne peut pas dire si son coefficient positif est un défaut de filtrage, parce qu'un marché rationnel réagit aussi à une erreur qu'il ne peut pas voir. Ici la question devient : pouvait-il la voir ? Si N est imprévisible, le résultat du parent est compatible avec un marché rationnel ; si N est prévisible, il ne l'est plus tout à fait.
- **Question** : la part du chiffre de l'emploi qui sera révisée est-elle prévisible hors échantillon à partir de l'information publique du jour ?
- **Hypothèse falsifiable** : oui, faiblement : un premier chiffre très au-dessus de la tendance récente est ensuite révisé à la baisse, et les révisions se suivent d'un mois à l'autre.
- **Prédiction chiffrée** : R² hors échantillon de +3 % (entre +1 % et +6 %) contre la prévision « révision nulle » ; coefficient de N sur l'écart du premier chiffre à la médiane des douze derniers mois : +0,05 à +0,15.
- **Test de mort** : quatre prédicteurs fixés d'avance (écart du premier chiffre à la médiane des douze dernières variations connues ; révisions des deux mois précédents publiées le même jour ; écart entre l'emploi de l'enquête auprès des ménages et l'emploi salarié ; N du même mois un an plus tôt), MCO réestimés avant chaque publication sur fenêtre croissante. Fenêtre hors échantillon : 2000-2025, mêmes exclusions que le parent. L'idée meurt si la statistique de Clark-West est inférieure à 1,645 ou si le R² hors échantillon est négatif ou nul, contre « révision nulle » et contre la moyenne récursive.
- **Données** : millésimes ALFRED de `PAYEMS`, `CE16OV` et `UNRATE` par `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<SERIE>&vintage_date=AAAA-MM-JJ` (profondeur des millésimes avant 1990 : à vérifier). Code HTTP : non testé par moi (aucun outil) ; source de la liste vérifiée du brief.
- **Méthode** : reconstruire pour chaque publication le premier chiffre et tout ce qui était connu ce jour-là ; prévisions récursives ; R² hors échantillon, Clark-West, intervalle par bootstrap par blocs. Seconde étape descriptive, hors test de mort : couper N en part prévue et part imprévue dans la régression du parent.
- **Ce qui serait nouveau** : un test hors échantillon, scellé, de la prévisibilité des révisions de l'emploi, utilisé pour qualifier un résultat de prix. Proches, de mémoire : Mankiw et Shapiro (1986, « news or noise », à vérifier) ; Aruoba (2008, révisions prévisibles en échantillon, à vérifier) ; Neumark et Wascher (vers 1991, révisions de l'emploi, référence incertaine).
- **Rôle de l'IA** : un agent reconstruit les millésimes, un autre refait dix dates tirées au hasard à la main depuis ALFRED ; l'humain fixe la liste des prédicteurs et la fenêtre, scellées avant tout calcul de N ; le verdict (Clark-West) sort d'un script séparé qui lit le fichier brut des prévisions.
- **Coût et durée** : calcul négligeable (quelques centaines de téléchargements) ; moins de 10 USD ; 4 semaines.
- **Risques** : résultat proche de travaux anciens en échantillon ; un R² de 1 à 2 % serait vrai mais sans portée ; la seconde étape manque de puissance (voir plus bas).
- **Valeur si l'hypothèse meurt** : la limite de fond du parent est confirmée par un test direct : le jour même, l'erreur n'était pas prévisible, donc le taux à 2 ans réagit au bruit sans faute de filtrage. C'est la phrase qui manquait au parent.
- **Ce que ça dit au jury et aux recruteurs** : CV : « A testé hors échantillon, sur 26 ans de publications de l'emploi américain reconstituées en temps réel, si la révision future du chiffre était prévisible le jour même. » Graphique : somme cumulée des écarts d'erreur quadratique entre « révision nulle » et le modèle, 2000-2025. Métiers : recherche économique de banque, banque centrale (données en temps réel), stratégie taux.
- **Arithmétique de puissance** : environ 220 publications hors échantillon après exclusions (400 si les millésimes d'avant 1990 permettent de démarrer en 1990). Avec un R² vrai de 4 %, le t en échantillon vaut √(220 × 0,04 / 0,96) ≈ 3,0 et la statistique de Clark-West environ 2,1 ; avec 400 publications, environ 2,8. Le test tranche si le R² vrai atteint 3 à 4 % ; en dessous de 2 % il rendra « imprévisible », ce qui est alors la bonne réponse pratique. Seconde étape : écart-type de la part prévue d'environ 11 000 emplois, erreur type d'environ 4,5 pb par 100 000 contre un effet de 2,3 : elle ne peut pas trancher et n'entre pas dans le verdict.

---

### J15 — Révisions de l'emploi américain : pourquoi le taux à 2 ans a-t-il cessé de réagir dans les années 2010 ?
- **Parent et différence** : `Parent B`. Changement de **l'identification** : passage d'une régression linéaire inconditionnelle à un modèle à interaction avec la contrainte de taux plancher (Zero Lower Bound, ZLB) et l'écart de chômage, complété par le test de retour en arrière aux dates $t+1$ et $t+2$ de publication des révisions. Cela résout les deux énigmes laissées ouvertes par le Parent B : l'absence totale d'effet dans les années 2010 ($t = -0,39$) et la rationalité du marché.
- **Question** : La réaction du taux à 2 ans à la part révisée des créations d'emplois s'éteint-elle lorsque les taux courts sont bloqués au plancher effectif (ZLB), et s'inverse-t-elle le jour où la révision est effectivement publiée ?
- **Hypothèse falsifiable** : La sensibilité du taux à 2 ans à l'erreur initiale de mesure $N_t$ (1re moins 3e estimation de `PAYEMS`) est strictement plus forte hors ZLB qu'en régime de ZLB (`DFEDTARU` $\le 0,50\%$), et la révision publiée un ou deux mois plus tard provoque une correction de signe opposé.
- **Prédiction chiffrée** : Hors ZLB, le taux à 2 ans monte de +3,5 à +4,5 pb par tranche de 100 000 emplois surestimés, contre un effet proche de 0 pb en régime ZLB (différence d'au moins +3,0 pb) ; à $t+1$ et $t+2$, la publication de la révision entraîne une correction de $-1,5$ à $-3,0$ pb par 100 000 emplois révisés.
- **Test de mort** : Dans la régression avec interaction $\Delta \text{DGS2}_t = \alpha + \beta_1 N_t + \beta_2 (N_t \times \text{HorsZLB}_t) + \gamma X_t + \varepsilon_t$ sur 1990-2025, l'idée meurt si le coefficient d'interaction $\beta_2$ a une statistique $t$ (HC3) inférieure à 1,96 ET que la somme des coefficients des révisions passées publiées le jour $t$ n'est pas significativement négative ($t > -1,645$).
- **Arithmétique de puissance** : Même base de 309 publications (1990-2025) que le Parent B, où l'erreur type globale sur $N_t$ a été mesurée à 0,94 pb. L'échantillon compte ~95 mois en ZLB (décembre 2008 à décembre 2015, mars 2020 à mars 2022) et ~214 mois hors ZLB. Hors ZLB, la volatilité de `DGS2` n'est pas écrasée et l'erreur type sur la différence de pente $\beta_2$ est d'environ $0,94 \times \sqrt{309/214 + 309/95} \approx 1,9$ pb (voire plus faible car la variance résiduelle au ZLB est quasi nulle, ce qui réduit fortement l'erreur type HC3 du segment ZLB vers 0,4 pb, donnant une erreur type sur $\beta_2$ autour de 1,15 pb). Un écart de pente de 3,5 pb donne $t \approx 3,0$. Le test peut trancher.
- **Données** : FRED (`DGS2`, `DFEDTARU`, `DFEDTAR`, `UNRATE`, HTTP 200 vérifié) et millésimes temps réel ALFRED (`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=PAYEMS&vintage_date=AAAA-MM-JJ`, syntaxe vérifiée).
- **Méthode** : Moindres carrés ordinaires à variables d'interaction (régime ZLB vs Hors-ZLB, et interaction continue avec la pente préalable 2s10s `DGS10` - `DGS2` comme mesure continue d'espace de politique monétaire) et test de Wald joint sur les coefficients de retour à la moyenne lors des publications des 2e et 3e estimations à $t+1$ et $t+2$. Erreurs types robustes HC3.
- **Ce qui serait nouveau** : Montre que l'anomalie apparente des années 2010 relevée dans le Parent B s'explique par la censure de la fonction de réaction de la Fed au ZLB, et teste directement l'hypothèse d'apprentissage bayésien par le retour en arrière à $t+1$ et $t+2$. Travaux proches : Swanson et Williams (2014, *à vérifier*), Gilbert (2011, *vérifié*).
- **Rôle de l'IA** : L'agent construit la matrice exacte des millésimes ALFRED (1re, 2e et 3e lectures pour chaque mois) et les indicatrices de régime monétaire. L'humain préinscrit la définition exacte du ZLB avant d'observer les régressions par sous-période. Le verdict est rendu par un script de test séparé sur la table assemblée.
- **Coût et durée** : Calcul : < 5 minutes (requêtes ALFRED mises en cache). Appels de modèles : < 2 USD. Durée : 4 semaines.
- **Risques** : Colinéarité entre l'indicatrice ZLB et d'autres transformations structurelles du marché du travail dans les années 2010 (d'où le contrôle par la pente 2s10s la veille de l'annonce).
- **Valeur si l'hypothèse meurt** : Si l'effet reste absent dans les années 2010 même après prise en compte de la contrainte ZLB et qu'il n'y a aucun retour en arrière à $t+1$, cela démontre que le résultat du Parent B est entièrement tiré par la volatilité post-Covid (2022-2025) et met en garde contre les régressions sur données révisées non stationnaires.
- **Ce que ça dit au jury et aux recruteurs** : *Ligne de CV* : « Évalué l'effet du plancher effectif des taux (ZLB) sur la sensibilité du marché obligataire américain au bruit de mesure des créations d'emplois (ALFRED, 1990-2025). » *Graphique unique* : Nuage de points et droites de régression de $\Delta \text{DGS2}$ contre la révision future $N_t$, séparés en deux couleurs (régime ZLB plat vs hors-ZLB pentu). *Métiers* : Recherche macroéconomique, banque centrale, gestion d'actifs (macro global).

---

### J16 — La pression d'adjudication existe-t-elle hors de la courbe du Trésor ?
- **Question** : Les réouvertures créent-elles une déformation locale des rendements mesurée avec la seule courbe ajustée de la Fed, indépendamment de la courbe à échéance constante du Trésor ?
- **Hypothèse falsifiable** : Le rendement ajusté autour de l'échéance adjugée augmente temporairement relativement aux échéances voisines.
- **Prédiction chiffrée** : La déformation événementielle moyenne sera positive, de l'ordre de **0,6 pb**.
- **Test de mort** : Sur les réouvertures de 2010 à 2026 du parent, tester la moyenne du contraste défini ci-dessous par bootstrap sauvage studentisé, groupé par mois, 9 999 tirages ; abandon de l'hypothèse positive si la borne inférieure unilatérale à 95 % n'est pas supérieure à zéro. Une non-significativité ne démontrera pas que l'effet du parent était artificiel.
- **Données** : Adjudications, champ `auctions_query`, source vérifiée du Trésor : `https://api.fiscaldata.treasury.gov/` ; fichier quotidien exact de la Fed : `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv`, colonnes `SVENY07`, `SVENY10`, `SVENY13`, `SVENY17`, `SVENY20`, `SVENY23`, `SVENY24`, `SVENY27`, `SVENY30`. Accès vérifié selon le brief ; **code HTTP non communiqué et aucun test personnel possible sans outils**. Le chemin complet d'`auctions_query` devra être consigné lors du téléchargement.
- **Méthode** :  
  Construire \(B_{10}=y_{10}-(y_7+y_{13})/2\), \(B_{20}=y_{20}-(y_{17}+y_{23})/2\), et \(B_{30}=y_{30}-2y_{27}+y_{24}\).  
  Calculer \(W=100[2B(J)-B(J-5)-B(J+5)]\), puis sa moyenne à poids égaux par adjudication.  
  Ces contrastes éliminent les déplacements parallèles et les variations linéaires de pente ; ils ne nécessitent aucune série CMT du Trésor.  
  Présenter les résultats par échéance et avant/après décembre 2021 comme décompositions descriptives, sans multiplier les verdicts.
- **Ce qui serait nouveau** : Tester une déformation de la courbe ajustée, plutôt que l'écart entre deux fabricants de courbes. Lou, Yan et Zhang (2013), et Fleming, Liu et Nguyen (2026), sont les travaux proches — **à vérifier** pour leur traitement précis des titres utilisés dans l'ajustement. La documentation GSW doit également préciser quels titres sont exclus : indépendance de méthode ne signifie pas indépendance des prix sous-jacents.
- **Rôle de l'IA** : Un agent construit les contrastes et le pipeline ; un autre produit les tests unitaires de pondération et de calendrier. L'humain choisit les définitions avant lecture des rendements événementiels et scelle protocole, prédiction et code par SHA256. Un évaluateur séparé, sous contrôle humain, recalcule le verdict depuis les fichiers bruts ; le producteur ne peut modifier son code d'évaluation.
- **Coût et durée** : CPU seul, moins d'une heure de calcul hors téléchargements ; plafond d'appels de modèles de **15 USD** ; **5 semaines**.
- **Risques** : La courbe ajustée peut lisser précisément la perturbation recherchée ; le contraste à 30 ans est moins symétrique. Un résultat nul peut donc réfuter une propagation aux obligations voisines sans réfuter une concession propre au titre adjugé.
- **Valeur si l'hypothèse meurt** : Quantifier la limite d'une mesure publique indépendante de la méthode CMT et circonscrire le résultat du parent à un phénomène relatif au titre de référence ou à sa mesure.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai testé la robustesse d'une pression d'adjudication à un changement indépendant de mesure des rendements. » Graphique : profil événementiel du contraste de courbure avec intervalle de confiance. Métiers : recherche taux, gestion obligataire, stratégie souveraine, banque centrale.
- **Parent et différence** : **Parent A** ; changement de **source de données pour la mesure du prix** et de **statistique** : aucune série CMT n'entre dans le résultat. Cela distingue une déformation présente dans les obligations servant à ajuster la courbe d'un artefact propre à la méthode du Trésor.
- **Arithmétique de puissance** : Au maximum **321 adjudications, mais 134 grappes mensuelles**, et non 321 observations pleinement indépendantes. En utilisant conservativement 2,57 pb comme dispersion des moyennes mensuelles, l'erreur type de planification est \(2,57/\sqrt{134}=0,22\) pb : effet de 0,6 pb, rapport signal/bruit de 2,7, puissance unilatérale voisine de **85 %**. Cette dispersion n'est pas mesurée pour le nouveau contraste : elle sera auditée séparément ; une erreur type supérieure à 0,24 pb fera classer le test comme insuffisamment puissant pour la cible annoncée.

---

### J17 — Écarts souverains et taux courts en données quotidiennes : la rupture tombe-t-elle à l'été 2022 ?
- **Parent et différence** : libre. Motivée par le résultat « Instrument de protection de la transmission de la BCE et écarts souverains », non concluant faute d'observations (26 réunions après juillet 2022, variation de pente −0,35 avec une erreur type de 0,32). Je remplace les jours de réunion par tous les jours ouvrés et la comparaison avant/après par une date de rupture estimée, que l'on confronte au calendrier.
- **Question** : la sensibilité quotidienne de l'écart souverain moyen de la zone euro aux mouvements du taux sans risque à 2 ans s'est-elle rompue, et la date estimée de la rupture tombe-t-elle entre l'annonce du 15 juin et celle du 21 juillet 2022 ?
- **Hypothèse falsifiable** : la pente est positive au premier semestre 2022 (les écarts s'ouvrent quand les taux montent) et chute d'au moins moitié à une date estimée dans l'été 2022.
- **Prédiction chiffrée** : écart = taux au comptant à 10 ans de la courbe « tous émetteurs souverains » moins celui de la courbe « AAA ». Pente de sa variation quotidienne sur celle du taux AAA à 2 ans : +0,10 à +0,20 avant la rupture, entre −0,03 et +0,05 après ; date de rupture estimée entre le 1er juin et le 31 août 2022.
- **Test de mort** : fenêtre du 3 janvier 2022 au 29 décembre 2023, rognée de 15 % à chaque bout. L'idée meurt si l'un des trois points échoue : (1) test sup-F d'Andrews sur la pente, p < 0,05 par bootstrap sauvage ; (2) date de rupture par moindres carrés entre le 1er juin et le 31 août 2022 ; (3) baisse de pente d'au moins 50 %. Garde-fou : la même procédure sur huit fenêtres placebo de deux ans tirées de 2005-2021 ne doit jamais donner une baisse aussi forte.
- **Données** : API de la BCE, courbes de rendements `YC`, quotidiennes depuis septembre 2004 (clés de mémoire, à vérifier : `YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y`, `...G_N_C...SR_10Y`, `...G_N_A...SR_2Y`) ; base EA-MPD pour un contrôle sur les seuls jours de réunion. Code HTTP : non testé par moi (aucun outil) ; sources de la liste vérifiée du brief (API notée intermittente).
- **Méthode** : construire l'écart et ses variations quotidiennes ; régression à rupture unique de date inconnue ; intervalle de confiance de la date (Bai) ; bootstrap sauvage pour la volatilité variable ; fenêtres placebo ; vérification de cohérence sur les jours de réunion de la base EA-MPD.
- **Ce qui serait nouveau** : dater la rupture au lieu de la supposer, avec 500 jours au lieu de 26 réunions. Proches : le test de génération 1 du registre ; études de la BCE sur l'instrument (référence incertaine) ; Andrews (1993) et Bai (1997) pour la méthode, à vérifier.
- **Rôle de l'IA** : un agent télécharge et construit les séries, un second recode le test de rupture indépendamment ; l'humain choisit la fenêtre, le rognage et les fenêtres placebo, scellés avant lecture ; un script séparé rend la date et le verdict.
- **Coût et durée** : calcul de quelques minutes (bootstrap) ; moins de 10 USD ; 4 semaines.
- **Risques** : une variation quotidienne de taux n'est pas une surprise monétaire (les jours de fuite vers la qualité donnent une pente négative) ; la courbe « tous émetteurs » change de composition ; la démission du gouvernement italien le 21 juillet 2022 tombe le même jour ; une date ne prouve pas une cause.
- **Valeur si l'hypothèse meurt** : une rupture datée ailleurs (fin 2022, ou aucune) dit que le calme des écarts ne coïncide pas avec l'annonce, ce qui pèse contre la lecture usuelle de l'instrument.
- **Ce que ça dit au jury et aux recruteurs** : CV : « A daté par un test de rupture, sur 500 jours de courbes de la BCE, le changement de sensibilité des écarts souverains aux taux courts en 2022, avec fenêtres placebo. » Graphique : pente glissante sur 60 jours, date estimée et son intervalle, traits verticaux au 15 juin et au 21 juillet 2022. Métiers : banque centrale, stratégie taux et dette souveraine, recherche économique, gestion obligataire.
- **Arithmétique de puissance** : environ 110 jours avant et 390 après, quasi indépendants en moyenne (volatilité groupée, d'où le bootstrap). Écart-type supposé de la variation de l'écart 1,5 pb, du taux à 2 ans 6 à 7 pb : erreurs types de pente 0,024 et 0,013, soit 0,027 sur la différence ; baisse prédite 0,12 à 0,15, t d'environ 5. Précision de la date : environ ±35 jours ouvrés à 95 %. Le test tranche sur l'existence de la rupture et la situe à six ou sept semaines près ; il ne sépare pas le 15 juin du 21 juillet.

---

### J18 — Le résultat sur l'emploi se généralise-t-il aux autres statistiques révisées ?
- **Parent et différence** : `Parent B`. Je change l'échantillon et les statistiques macroéconomiques : ventes au détail, production industrielle et PIB remplacent `PAYEMS`. J'agrège en outre par jour de publication pour ne pas compter deux fois la même variation du taux lorsque deux statistiques paraissent ensemble.
- **Question** : Le taux à 2 ans réagit-il aussi à la composante finalement révisée des ventes au détail, de la production industrielle et du PIB, ou le résultat est-il propre à l'emploi ?
- **Hypothèse falsifiable** : La relation réduite est commune et, hors emploi, un écart-type de révision future est associé à une réaction positive du même ordre de grandeur que dans le parent.
- **Prédiction chiffrée** : Coefficient groupé \(\beta=+1{,}2\) pb du taux à 2 ans par écart-type de révision future, avec des coefficients individuels attendus entre +0,8 et +1,5 pb ; le consensus manquant interdit toujours d'en déduire une irrationalité du marché.
- **Test de mort** : Sur les jours de publication de janvier 1992 à décembre 2025, après exclusions figées des millésimes incomplets et des publications de mars à décembre 2020, la généralisation au même ordre de grandeur est morte si tout l'IC à 90 % de \(\beta\) est inférieur à +1,2 pb/σ. Un effet positif n'est retenu que si le \(t\) unilatéral contre \(\beta\le0\) dépasse 1,645 ; les trois coefficients individuels sont secondaires avec correction de Holm.
- **Données** : Millésimes `RSAFS`, `INDPRO` et `GDPC1`, par exemple `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=RSAFS&vintage_date=AAAA-MM-JJ`, avec les mêmes URL pour `INDPRO` et `GDPC1` ; taux `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2`. Les dates J sont reconstruites comme premières dates de millésime où apparaît la nouvelle période. Sources vérifiées selon le brief ; HTTP non retesté faute d'outil.
- **Méthode** : Pour chaque série, calculer la croissance publiée puis \(N=\) première estimation moins troisième estimation, et réduire \(N\) par son écart-type propre. Lorsque plusieurs statistiques paraissent le même jour, former une seule ligne avec la moyenne de leurs \(N\) réduits. Régresser \(\Delta DGS2\) sur cette moyenne, avec effets fixes du type de combinaison de publications, premiers chiffres publiés, révisions antérieures disponibles ce jour et médiane des douze dernières variations connues ; erreurs HC3 et bootstrap par année en robustesse.
- **Ce qui serait nouveau** : Le parent laisse ouverte la généralité du phénomène ; cette fiche teste trois statistiques avec une unité d'observation qui évite la pseudo-réplication des jours communs. Krueger et Fortson (2003 ; à vérifier), Gilbert (2011 ; à vérifier) et Gilbert, Scotti, Strasser et Vega (2017 ; à vérifier) sont les travaux proches rappelés par le registre.
- **Rôle de l'IA** : Les agents automatisent la recherche des millésimes et deux extractions indépendantes des dates, mais ne choisissent ni les exclusions ni les contrôles après avoir vu \(\beta\). L'humain vérifie un échantillon aléatoire de publications avant le hachage. Le verdict et les tests de Holm sont calculés par un script séparé depuis les fichiers ALFRED/FRED bruts.
- **Coût et durée** : Calcul léger mais extraction de millésimes importante ; environ 4 millions de tokens, plafond 13 USD ; 5 à 6 semaines.
- **Risques** : Les dates inférées des changements de millésime peuvent être décalées d'un jour ou mélanger révisions et nouvelles publications. Une forte hétérogénéité rendrait le coefficient groupé peu parlant. Surtout, même un résultat positif propre resterait une relation réduite, faute de consensus gratuit.
- **Valeur si l'hypothèse meurt** : On pourra écrire que le résultat de l'emploi ne se transporte pas au même ordre de grandeur à trois autres statistiques, avec une borne supérieure quantitative ; cela orientera la recherche vers les particularités des révisions de `PAYEMS` ou de la période récente.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai testé sur trois statistiques macroéconomiques la réaction du taux à 2 ans à leur composante finalement révisée, à partir de millésimes en temps réel. » Graphique unique : coefficient groupé et coefficients par statistique, avec IC et ligne à +1,2 pb/σ. Métiers : recherche macro, banque centrale, stratégie taux et analyse de conjoncture quantitative.
- **Arithmétique de puissance** : Le parent implique, avec \(SE(\beta)=0{,}94\), \(n=309\) et \(\sigma_{\Delta y}=9{,}43\) pb, un écart-type de \(N\) d'environ \(9{,}43/(0{,}94\sqrt{309})=0{,}57\), soit un effet d'environ \(2{,}32\times0{,}57=1{,}32\) pb par écart-type. Après fusion des jours communs, je retiens prudemment 400 à 450 jours indépendants ; avec le même \(\sigma_{\Delta y}\), \(SE(\beta)\simeq0{,}44\) à 0,47 pb/σ. L'effet prédit donne \(t\simeq2{,}6\)–2,7 et environ 83–85 % de puissance ; l'effet minimal détectable à 80 % est 1,10–1,17 pb/σ, juste sous la prédiction.

---

### J19 — BCE : les surprises de taux favorisent-elles la valeur ?
- **Question** : Les annonces de la BCE associant hausse des taux anticipés et baisse du marché actions favorisent-elles davantage les actions européennes « value » que les annonces associant hausse des taux et hausse des actions ?
- **Hypothèse falsifiable** : La surperformance relative de la valeur après une hausse inattendue des taux est plus forte lorsque l'annonce ressemble à un durcissement monétaire que lorsqu'elle contient une information favorable sur l'économie.
- **Prédiction chiffrée** : Pour une hausse de **10 pb** de l'OIS à un an, l'écart de réaction du facteur HML entre les deux catégories sera d'environ **+0,30 point de pourcentage**.
- **Test de mort** : Sur les réunions de 1999 à 2025 ayant toutes les données, tester que la différence des deux pentes est positive, seuil unilatéral de 5 %, bootstrap sauvage par réunion. Utiliser une seule fenêtre intrajournalière EA-MPD, fixée avant estimation. Abandon si le test échoue ; aucune substitution postérieure d'horizon OIS, de facteur ou de fenêtre.
- **Données** : BCE, fichier `https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx` : variations intrajournalières OIS un an et indice actions européen, dates des réunions ; Ken French, `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_5_Factors_Daily_CSV.zip`, colonnes `HML` et `Mkt-RF`. Sources vérifiées selon le brief ; **code HTTP non communiqué, aucun téléchargement personnel**. Les unités, fenêtres et libellés exacts seront consignés depuis la documentation avant déblocage des rendements HML.
- **Méthode** :  
  Classer les annonces selon le signe du produit des variations intrajournalières de l'OIS et des actions : négatif pour la catégorie « monétaire », positif pour la catégorie « information ».  
  Estimer deux pentes de réaction du HML quotidien aux variations d'OIS, dans une même équation avec constantes propres aux catégories.  
  Retirer au préalable l'exposition au marché estimée sur les 250 séances antérieures, hors réunions BCE, afin de limiter une sélection mécanique par le marché actions.  
  Interpréter les catégories comme une décomposition descriptive par signes, non comme des chocs structurels identifiés sans hypothèses supplémentaires.
- **Ce qui serait nouveau** : Tester si une distinction d'information monétaire change la lecture de l'exposition « value–growth » en Europe avec des données entièrement publiques. Jarociński et Karadi (2020), sur information de banque centrale et chocs monétaires — **à vérifier** ; littérature sur duration des actions et valeur — **référence incertaine**. L'existence d'un résultat identique sur HML Europe doit être vérifiée avant lancement.
- **Rôle de l'IA** : L'IA assemble les données et produit la neutralisation de marché ; l'humain choisit la fenêtre et valide les hypothèses interprétatives. Prédiction, classification et équation sont scellées avant lecture des réactions HML aux réunions. Un programme séparé, administré par l'humain, contrôle la neutralisation sans fuite temporelle et calcule le verdict depuis les deux fichiers bruts.
- **Coût et durée** : CPU seul, moins d'une heure avec bootstrap ; plafond de **20 USD** ; **4 à 5 semaines**.
- **Risques** : La classification utilise un prix d'action et peut encore induire une sélection liée aux styles ; HML reflète aussi des compositions sectorielles. Les rendements quotidiens contiennent des nouvelles étrangères à la BCE. Le projet ne doit donc pas vendre une estimation causale pure de la duration des actions.
- **Valeur si l'hypothèse meurt** : Montrer qu'une distinction centrale en identification monétaire ne se traduit pas par une différence détectable de performance relative des styles européens ; borner cette différence.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai confronté l'exposition des styles actions européens aux différentes composantes des annonces de la BCE. » Graphique : réaction HML à une hausse de 10 pb dans chaque catégorie, avec intervalle du contraste. Métiers : recherche multi-actifs, gestion factorielle, stratégie européenne, recherche monétaire.
- **Parent et différence** : **Libre** ; motivée par l'élimination de la prévision publique des surprises BCE et par la fragilité du résultat TPI. Plutôt que prévoir ces surprises ou isoler seulement l'après-2022, le projet utilise l'ensemble des réunions pour étudier leur contenu et leur transmission à un autre marché.
- **Arithmétique de puissance** : Au maximum **315 réunions indépendantes approximativement**, et non le nombre de titres des portefeuilles ; scénario de 150 observations par catégorie. Avec un écart-type résiduel HML de 0,5 point de pourcentage et un écart-type OIS de 5 pb, chaque pente normalisée à 10 pb aurait une erreur type d'environ \(0,5/(\sqrt{150}\times0,5)=0,082\) point ; celle du contraste serait de **0,116 point**. L'effet de 0,30 point donne une puissance unilatérale proche de **83 %**. Ces dispersions sont des hypothèses de dimensionnement : une catégorie trop petite ou une erreur type supérieure à 0,12 point ferait conclure à une faisabilité statistique insuffisante.

---

### J20 — La pression d'adjudication reste-t-elle à son échéance ?
- **Parent et différence** : `Parent A`. Je change la statistique et l'identification transversale : l'événement est une adjudication à l'échéance \(m\), mais le résultat est mesuré à une autre échéance \(n\), sans adjudication propre dans la fenêtre. Cela teste une propagation que la moyenne des seuls \(V_m\) ne peut pas identifier.
- **Question** : La pression d'une réouverture reste-t-elle localisée à l'échéance adjugée ou se propage-t-elle aux autres parties de la courbe ?
- **Hypothèse falsifiable** : Si une composante commune d'inventaire ou de financement domine, la pression observée aux échéances non adjugées vaut au moins la moitié de la pression propre moyenne.
- **Prédiction chiffrée** : Pour une pression propre proche de 0,91 pb, je prédis une pression propagée moyenne \(S=+0{,}45\) à +0,55 pb ; une valeur proche de zéro indiquerait au contraire un phénomène très localisé.
- **Test de mort** : Pour chaque événement, moyenne des \(V_n\) aux échéances éligibles, avec effets fixes de paire d'échéances et erreurs types groupées par événement et par mois. L'hypothèse d'une propagation d'au moins 0,45 pb est morte si \((\widehat S-0{,}45)/SE<-1{,}645\) ; une propagation positive n'est affirmée que si \(\widehat S/SE>1{,}645\).
- **Données** : Mêmes fichiers FRED `DGS10/20/30`, GSW `SVENPY10/20/30` et API Treasury `auctions_query` qu'en J06 ; les pseudo-dates J+10 utilisent les mêmes séries. Accès vérifié selon le brief ; codes HTTP non retestés faute d'outil.
- **Méthode** : Constituer une ligne par adjudication et échéance témoin, en excluant toute échéance ayant sa propre adjudication entre J−5 et J+5. Estimer \(S\) après retrait des moyennes de paire et contrôler l'indicateur post-2021 sans en faire le test principal. Comparer aux mêmes calculs autour de pseudo-adjudications et vérifier que les fenêtres qui se chevauchent ne créent pas de double comptage indépendant.
- **Ce qui serait nouveau** : Le parent établit une moyenne propre, mais pas sa portée sur la courbe ; une forte propagation orienterait vers un choc commun, tandis qu'une borne proche de zéro renforcerait l'interprétation par une pression locale. Les travaux de Lou, Yan et Zhang (2013 ; à vérifier) et Fleming, Liu et Nguyen (2026 ; présence d'une analyse transversale équivalente à vérifier) sont les plus proches.
- **Rôle de l'IA** : Un agent construit le calendrier d'exclusion des échéances témoins, un autre le reconstruit sans voir le premier code. L'humain arbitre uniquement les erreurs de données documentées avant scellement. Les estimations, le regroupement des erreurs types et le verdict sont recalculés par un programme déterministe distinct.
- **Coût et durée** : Portable seul ; environ 2,5 millions de tokens, plafond 8 USD ; 4 à 5 semaines.
- **Risques** : Le lissage de la courbe GSW peut transmettre mécaniquement une perturbation d'une échéance aux autres ; une propagation ne serait alors pas une preuve de mécanisme commun. Le 20 ans, récent, et les fenêtres sans témoin propre réduisent aussi le nombre d'événements exploitables.
- **Valeur si l'hypothèse meurt** : Une borne supérieure précise sur la propagation montrerait que la pression est principalement locale et fournirait un fait utile pour choisir entre explications par inventaire spécifique et par ajustement global de la courbe.
- **Ce que ça dit au jury et aux recruteurs** : Ligne de CV : « J'ai estimé la propagation de la pression d'adjudication entre échéances en excluant les adjudications propres des fenêtres témoins. » Graphique unique : pression propre contre pression aux autres échéances, avec IC et seuil de 0,45 pb. Métiers : recherche obligataire, stratégie de courbe, banque centrale et gestion de taux.
- **Arithmétique de puissance** : Je retiens 300 événements indépendants après exclusions, plutôt que de compter chaque échéance témoin comme une observation nouvelle. Avec \(\sigma=2{,}57\) pb et le facteur mensuel de 1,12, \(SE(\widehat S)\simeq1{,}12\times2{,}57/\sqrt{300}=0{,}166\) pb. L'effet prédit de 0,45 pb donne \(t\simeq2{,}7\), environ 85 % de puissance ; l'effet minimal détectable à 80 % est 0,41 pb. Le test peut donc trancher l'alternative « propagation nulle » contre « moitié de la pression propre ».
