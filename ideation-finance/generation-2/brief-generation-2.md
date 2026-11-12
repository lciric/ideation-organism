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
- L’euro réagit-il symétriquement aux surprises de la BCE ?
- Les chocs d’inflation s’éteignent-ils dans les projections de la BCE ?
- Les dissidents du FOMC annoncent-ils les décisions suivantes ?
- Pétrole et ancrage des anticipations d’inflation
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
