Vous êtes un proposeur dans une course d'idéation de recherche. Lisez le brief ci-dessous en entier et suivez-le à la lettre. Vos identifiants de fiches commencent par « 2K ».

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

# Complément pour la course 2 (proposeurs de familles différentes) — 12 novembre 2026

## Profil et centres d'intérêt de l'étudiant
- Centres d'intérêt, par ordre : **économie monétaire, banque centrale, macroéconomie**, puis finance de marché.
  Au moins **quatre fiches sur cinq** doivent relever des trois premiers.
- Il sait : Python (pandas, numpy, statsmodels), mathématiques de classes préparatoires, cours de titres à revenu fixe et
  d'économie monétaire. Ses projets existants portent sur les actions (frais des fonds indiciels, signaux quantitatifs) :
  un projet de taux, monétaire ou macroéconomique lui apporte le plus.

## Vous n'avez aucun outil
Vous ne pouvez rien télécharger ni tester. Le champ « Données » ne cite donc que des sources de la liste ci-dessous, dont l'accès
a été vérifié depuis la machine du projet. Toute autre source doit porter la mention « source non vérifiée » et ne peut pas
être indispensable au test de mort.

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

## Champ ajouté à la fiche (obligatoire)
- **Arithmétique de puissance** : nombre d'observations réellement indépendantes, erreur type attendue, effet prédit ;
  dire en une phrase si le test peut trancher ou s'il risque de finir « non concluant ».

## Idées déjà proposées dans la course 1 — ne pas les reprendre, même habillées autrement
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

## Sortie attendue
Exactement **cinq fiches**, en français, au format de fiche ci-dessus (tous les champs, plus « Arithmétique de puissance »),
chacune sous un titre `### <ID> — <titre court>`, avec les identifiants `2K1` à `2K5`. Rien d'autre : pas d'introduction,
pas de conclusion, pas de classement de vos propres fiches. Cinq questions **et** cinq méthodes différentes.
