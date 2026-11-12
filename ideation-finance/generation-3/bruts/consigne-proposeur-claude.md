Vous êtes un proposeur dans une course d'idéation de recherche, génération 3. Lisez le brief ci-dessous en entier et suivez-le à la lettre. Vos identifiants de fiches commencent par « 4C ».

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

# Complément pour la génération 3 — 12 novembre 2026

Deux générations d'idées ont été proposées, jugées puis **testées sur données réelles** (préinscription scellée avant lecture des
données, exécution par un agent, recalcul par un autre, verdict par un code séparé). Vous êtes proposeur de la **génération 3** : vous
construisez sur ce qui a survécu et sur la question restée ouverte.

## Profil et centres d'intérêt de l'étudiant
- Centres d'intérêt, par ordre : **économie monétaire, banque centrale, macroéconomie**, puis finance de marché.
- Il sait : Python (pandas, numpy, statsmodels), mathématiques de classes préparatoires, cours de titres à revenu fixe et
  d'économie monétaire. Ses projets existants portent sur les actions.

## Registre des résultats (faits mesurés, chiffres du vérificateur ; « pb » = point de base)
- **Pression de prix aux adjudications du Trésor américain** — verdict : *survit*. sur 321 réouvertures à 10, 20 et 30 ans (2010-2026), pression moyenne de 0,91 pb mesurée contre la courbe du Trésor (t = 5,6) ; par année, de 1,0 à 2,2 pb en 2011-2021, proche de zéro en 2022-2026 (lecture exploratoire).
- **Adjudications : la disparition après 2021 vient-elle de la méthode de la courbe du Trésor ?** — verdict : *non concluant*. sur 23 réouvertures de l'exercice 2021, 1,64 pb avec l'ancienne méthode du Trésor et 0,85 pb avec la nouvelle ; différence 0,78 pb, IC à 95 % [0,45 ; 1,12], qui contient le seuil préinscrit de 0,9.
- **Instrument de protection de la transmission de la BCE et écarts souverains** — verdict : *non concluant*. variation de pente -0,35, erreur type 0,32, 26 réunions après l'instrument.
- **Anomalies boursières publiées : effet de la publication ou tendance commune ?** — verdict : *non concluant*. effet de la publication -0,06 du rendement d'origine, IC [-0,32 ; 0,19].
- **Les surprises de la BCE sont-elles prévisibles hors échantillon avec des données publiques ?** — verdict : *éliminée*. R² hors échantillon -0,5 % sur 147 réunions, Clark-West 0,59 (seuil 1,645).
- **Emploi américain : le taux à 2 ans réagit-il à la part du chiffre qui sera révisée ?** — verdict : *survit*. 2,32 pb par 100 000 emplois surestimés, sur 309 publications (t = 2,45) ; aucune décennie significative seule, les années 2010 négatives.
- **Les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel par une règle fondée sur les révisions ?** — verdict : *éliminée*. corrélation 0,02 entre correction annoncée et erreur réalisée (IC à 90 % [-0,07 ; 0,10]), 352 observations ; la projection corrigée fait moins bien que la publiée.
- **Peut-on prévoir hors échantillon la partie révisée du chiffre de l'emploi ?** — verdict : *survit*. sur 248 prévisions depuis 1997, Clark-West 1,87 (seuil 1,645), R² hors échantillon 2,2 %.
- **Les projections d'inflation de la BCE sous-réagissent-elles ?** — verdict : *survit*. pente erreur sur révision réduites 0,44 (t = 2,27) sur 108 trimestres cibles ; 0,05 sans 2021-2022 ; 0,14 hors 2021-2023.
- **Pression aux adjudications mesurée contre la courbe ajustée de la Fed, avant et après 2021** — verdict : *non concluant*. concession 0,68 pb en 2010-2021 (206 réouvertures) et 1,10 pb en 2022-2026 (116) : pas de baisse ; écart -0,66, IC à 90 % [-1,27 ; -0,04] ; non concluant parce qu'un contrôle de dates n'avait pas prévu les lundis fériés (trois lignes correctes) ; sans 2023 l'écart est nul (−0,04).

## Les parents : les 2 idées de la génération 2 qui ont survécu
### Parent A — Peut-on prévoir hors échantillon la partie révisée du chiffre de l'emploi ?

**Mesure.** Pour chaque publication mensuelle de l'emploi depuis 1990, N = première estimation moins troisième estimation de
la variation mensuelle de l'emploi (`PAYEMS`, millésimes ALFRED, en milliers). Prévision récursive à fenêtre croissante (au moins 60
publications d'apprentissage dont la troisième estimation est publiée au plus tard le jour de la prévision), MCO sur une constante,
x1 = première estimation moins la médiane des douze derniers mois connus, x2 = somme des deux révisions des mois précédents publiées
le même jour ; référence = moyenne historique de N. Clark-West avec Newey-West à 4 retards.
**Ce que la vérification a montré (descriptif).** Tout le pouvoir prédictif vient de x2 (Clark-West 2,12 seul) ; x1 n'apporte rien
(−1,15). Tout vient de 2020-2025 : sur ces prévisions, Clark-West 3,72 et R² 9,2 % ; sans elles, Clark-West −1,28. Retirer les deux
publications les plus influentes fait tomber la statistique à 1,52. Écart-type de N : environ 58 000 emplois.
**Questions ouvertes.** Pourquoi depuis 2020 (méthode du bureau des statistiques, taux de réponse, chocs de la pandémie) ? Le marché
se sert-il de cette prévisibilité le jour même (le parent de la génération 1 dit que le taux à 2 ans réagit au bruit) ? Vaut-elle pour
d'autres statistiques révisées ?

### Parent B — Les projections d'inflation de la BCE sous-réagissent-elles ?

**Mesure.** Pour chaque trimestre cible de 1999T4 à 2026T3 (108 cibles), erreur = inflation réalisée (Eurostat, glissement
annuel de l'IPCH) moins projection de la BCE à horizon 2 trimestres ; révision = projection à horizon 2 moins projection à horizon 3
pour la même cible ; pente MCO de l'erreur réduite sur la révision réduite, Newey-West à 4 retards. Lettres des millésimes vérifiées :
W = mars, G = juin, S = septembre, A = décembre (colonne `TITLE_COMPL`).
**Ce que la vérification a montré (descriptif).** Pente brute 0,68 ; avant 2020, 0,13 (proche de Granziera, Jalasjoki et Paloviita
2021 : 0,20 non significatif) ; sans 2021-2022, 0,05 ; sans 2023 seule, 0,57.
**Questions ouvertes.** La sous-réaction est-elle propre aux grands chocs ? Vient-elle des hypothèses techniques (prix de l'énergie,
change, taux, figés sur les marchés à terme et publiés dans la même base) plutôt que du jugement des économistes ? Les prévisionnistes
professionnels (enquête de la BCE) sous-réagissent-ils de la même façon ? Une règle en temps réel ne l'exploitait pas (H03-v2).

### Question ouverte prioritaire — la pression aux adjudications a-t-elle disparu du marché, ou seulement de la courbe du Trésor ?

Trois tests l'ont approchée sans la trancher selon leur règle (voir le registre : F04, F04-bis, J05). Faits établis : mesurée contre la
courbe du Trésor, la pression disparaît après 2021 ; le 6 décembre 2021 le Trésor a changé la méthode de sa courbe, et sur l'exercice 2021
la nouvelle méthode efface environ la moitié de la pression ; mesurée contre la courbe ajustée de la Fed, nette de l'écart du même titre
cinq jours avant, elle ne baisse pas (hausse portée surtout par 2023 et le 30 ans). Prix de marché par titre disponibles depuis 2008
(FedInvest, TreasuryDirect, un formulaire par date). Une fiche qui tranche cette question, avec une mesure et un contrôle que les trois
tests n'ont pas eus, compte comme fille.

## Ce que vous rendez
Exactement **cinq fiches**, en français, au format de fiche du brief, avec deux champs en plus :
- **Parent et différence** (obligatoire) : `Parent A`, `Parent B`, `Question ouverte` ou `libre`. Pour une fille, dites lequel de ces
  quatre éléments vous changez par rapport au test qui l'inspire — la statistique, l'échantillon ou le marché, la source de données,
  l'identification — et pourquoi ce changement peut donner une réponse que ce test n'a pas. Une fiche qui reformule un test déjà fait
  sans changer l'un de ces éléments est refusée avant le jugement. Pour une fiche libre, citez le résultat du registre qui la motive.
- **Arithmétique de puissance** (obligatoire) : nombre d'observations réellement indépendantes, erreur type attendue (servez-vous des
  dispersions mesurées ci-dessus), effet prédit ; dites si le test peut trancher. Plusieurs tests ont fini « non concluants » faute
  d'observations, et deux survivants reposent sur quelques années récentes : un test qui ne peut pas trancher, ou dont le résultat
  tiendrait à un seul épisode, est une mauvaise fiche.

Au moins **trois fiches filles** (d'un parent ou de la question ouverte) et au plus **deux fiches libres**. Cinq questions et cinq
méthodes différentes.

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

## Idées déjà proposées — ne pas les reprendre telles quelles
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
- La concession d’adjudication après 2021, sans courbe du Trésor
- Pression d’adjudication : bosse passagère ou saut permanent ?
- La pression d’adjudication reste-t-elle à son échéance ?
- Le résultat sur l’emploi se généralise-t-il aux autres statistiques révisées ?
- Les projections d’inflation de la BCE sous-réagissent-elles aux nouvelles informations ?
- Adjudications du Trésor : pression sur la courbure de la courbe de la Fed et échéances de 2 à 7 ans
- Révisions de l'emploi américain : pourquoi le taux à 2 ans a-t-il cessé de réagir dans les années 2010 ?
- Révisions des ventes au détail américaines et décomposition du taux à 2 ans le jour de l'annonce
- Pression des adjudications américaines et propagation dynamique aux rendements souverains européens
- Prévisibilité en temps réel des erreurs de projection d'inflation de la BCE (1999-2025)
- La pression d’adjudication existe-t-elle hors de la courbe du Trésor ?
- Le bruit de l’emploi est-il surtout un choc de taux courts ?
- La courbe corrige-t-elle le bruit quand les révisions arrivent ?
- Peut-on prévoir la partie révisée du chiffre d’emploi ?
- BCE : les surprises de taux favorisent-elles la valeur ?
- Règlements du Trésor et taux repo : la pression de quantité mesurée hors de la courbe du Trésor
- Emploi américain : la révision à venir est-elle prévisible le jour même ?
- Le taux à 2 ans réagit-il au bruit des autres statistiques ? Réplication sur des jours neufs
- Écarts souverains et taux courts en données quotidiennes : la rupture tombe-t-elle à l'été 2022 ?
- Prévoir le taux de la BCE : compétence ou chance chez les prévisionnistes ?

## Sortie attendue
Cinq fiches, chacune sous un titre `### <ID> — <titre court>`, identifiants `4C1` à `4C5`. Rien d'autre : pas d'introduction,
pas de conclusion, pas de classement de vos propres fiches.
