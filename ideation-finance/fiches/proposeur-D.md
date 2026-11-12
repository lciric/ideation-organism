# Fiches du proposeur D — banque, microéconométrie appliquée sur données publiques, crédibilité de l'économie empirique

Tests d'accès faits avec `curl` depuis cette machine le 2026-11-12. Aucun test d'hypothèse n'a été exécuté. Pour vérifier
qu'un fichier existe, seuls des en-têtes, des listes de clés de séries et, dans deux cas, 3 lignes de données ont été lus
(agrégat zone euro du BLS 2025T3-2026T1 ; trois trimestres d'une seule banque dans l'API FDIC). Ces lignes ne permettent
de juger aucune des prédictions ci-dessous. Toutes les références sont citées de mémoire et marquées « à vérifier ».

Deux remarques d'accès qui valent pour plusieurs fiches :
- l'API de la BCE et FRED répondent, mais par intermittence (503, délais dépassés ou réponse vide sur certains essais, 200 au
  réessai) : tout script de collecte doit réessayer et mettre les fichiers bruts en cache avec leur sha256 ;
- `github.com` et `api.github.com` renvoient 403 depuis cette session (restriction du mandataire de session) ;
  `raw.githubusercontent.com` répond 200.

---

### D1 — Les banques prévoient-elles bien leur propre politique de crédit ? Rationalité des anticipations dans l'enquête BLS

- **Question** : dans l'enquête de la BCE sur la distribution du crédit (BLS), le durcissement des critères d'octroi que les
  banques annoncent pour les trois mois à venir est-il une prévision efficace de ce qu'elles déclarent avoir fait le trimestre suivant ?
- **Hypothèse falsifiable** : les banques sous-réagissent ; l'erreur de prévision (réalisé au tour t+1 moins anticipé au tour t)
  est positivement autocorrélée, donc prévisible à partir de l'erreur précédente.
- **Prédiction chiffrée** : dans un panel de pays à effets fixes, le coefficient ρ de l'erreur passée sur l'erreur courante est
  compris entre +0,15 et +0,45 pour les critères d'octroi aux entreprises. Prédictions secondaires : la question prospective
  bat la prévision naïve « même valeur qu'au dernier tour » avec un rapport d'erreurs quadratiques moyennes entre 0,80 et 0,95 ;
  pour la demande de crédit, les banques sont trop optimistes, avec une erreur moyenne entre −3 et −8 points de solde net.
- **Test de mort** : fenêtre de test 2020T1 à 2026T3, jamais lue avant le scellement ; pays ayant au moins 20 trimestres
  dans la fenêtre (15 pays au moins attendus). Régression de l'erreur sur l'erreur retardée, effets fixes pays,
  écarts-types de Driscoll-Kraay (4 retards). L'idée meurt si ρ estimé ≤ 0,10 ou si le test unilatéral de ρ > 0 donne p > 0,05.
  Elle meurt aussi si le signe s'inverse entre 2003-2019 et 2020-2026.
- **Données** : API BCE, jeu `BLS`. Agrégat zone euro, critères d'octroi aux entreprises, rétrospectif et prospectif :
  `https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.O.E.Z.B3.ST.S.WFNET?format=csvdata` → **200** ;
  `.../BLS/Q.U2.ALL.O.E.Z.F3.ST.S.WFNET?format=csvdata` → **200** (après deux 503 et un délai dépassé).
  Liste des pays : `.../BLS/Q..ALL.O.E.Z.F3.ST.S.?format=csvdata&detail=serieskeysonly` → **200**, 21 pays (solde `FNET` ;
  `BFNET` pour BG, MT, SK). Clés par pays vérifiées sur la France (`.../BLS/Q.FR.ALL....F3...FNET?...serieskeysonly` → **200**) :
  critères (`ST.S`) et demande (`ZZ.D`) pour entreprises (`O.E.Z`), prêts au logement (`Z.H.H`), crédit à la consommation (`Z.H.C`),
  en `B3` (trois mois passés) et `F3` (trois mois à venir). Les clés `...BWFNET` et `...F3.ST.S.FNET` pour `U2` renvoient 404 : ne pas les utiliser.
- **Méthode** : erreur e(c,t+1) = solde rétrospectif du tour t+1 moins solde prospectif du tour t. Trois tests classiques :
  biais (moyenne nulle), régression de Mincer-Zarnowitz (constante 0, pente 1), prévisibilité de l'erreur par l'erreur passée
  et par la révision d'anticipation (à la Coibion-Gorodnichenko). Comparaison hors échantillon à la prévision naïve par un test
  de Diebold-Mariano. Six séries par pays ; correction de Holm sur les six.
- **Ce qui serait nouveau** : les tests de rigidité d'information portent surtout sur les prévisionnistes professionnels et les
  ménages ; je ne me souviens d'aucun test systématique sur les anticipations des responsables du crédit du BLS par pays.
  Travaux proches : Coibion et Gorodnichenko (2015, American Economic Review) sur la rigidité d'information — à vérifier ;
  Bordalo, Gennaioli, Ma et Shleifer (2020, American Economic Review) sur la sur-réaction — à vérifier ; de Bondt, Maddaloni,
  Peydró et Scopel (2010, document de travail BCE) sur le contenu prédictif du BLS pour le crédit — à vérifier ; un document
  occasionnel de la BCE sur le BLS par Köhler-Ulbrich, Hempell et Scopel (vers 2016) — à vérifier. Existence d'un test
  identique déjà publié : référence incertaine, à chercher avant de lancer.
- **Rôle de l'IA** : un agent écrit le collecteur (avec réessais) et les régressions sur données simulées ; un second agent
  propose les variantes (segments, pays exclus, retards). L'humain choisit la spécification de référence et scelle la
  prédiction (sha256) avant tout téléchargement de la fenêtre 2020-2026. Garde : le verdict est calculé par un script séparé
  qui lit le fichier brut de la BCE et le fichier scellé ; l'agent exécutant ne voit que « passe » ou « meurt ».
- **Coût et durée** : calcul négligeable (environ 130 séries trimestrielles) ; appels de modèles < 10 USD ; 4 semaines.
- **Risques** : soldes nets bruités dans les petits pays (peu de banques interrogées), ce qui crée une autocorrélation
  mécanique faible ou nulle ; le solde de la zone euro est pondéré, ceux des pays ne le sont pas ; le calendrier de l'enquête
  ne recouvre pas exactement le trimestre civil ; panel court (une vingtaine de pays, grappes peu nombreuses).
- **Valeur si l'hypothèse meurt** : « les anticipations des banques sur leur propre offre de crédit sont efficaces, à la
  différence de celles des prévisionnistes » est un résultat net, utile à qui lit le BLS chaque trimestre ; le rapport
  d'erreurs face à la prévision naïve reste publiable tel quel.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai testé sur 21 pays et 2020-2026 si les anticipations de
  durcissement du crédit déclarées par les banques dans l'enquête BLS de la BCE étaient des prévisions efficaces, avec une
  prédiction scellée avant lecture des données. » Graphique : nuage anticipé contre réalisé par pays, droite à 45 degrés et
  droite estimée, avant et après 2020. Métiers : banque centrale, recherche économique de banque, analyse crédit, stratégie taux.

---

### D2 — Hausse des « frais de notaire » de 2025 : anticipation et recul des ventes, département par département

- **Question** : la hausse de 4,5 % à 5 % des droits de mutation, votée à des dates différentes selon les départements
  en 2025, a-t-elle déplacé les signatures de ventes immobilières avant la date d'effet, et de combien ?
- **Hypothèse falsifiable** : dans les départements qui relèvent le taux, le nombre de ventes de logements anciens augmente
  le mois qui précède la date d'effet puis baisse le mois qui suit, par rapport aux départements qui n'ont pas encore relevé.
- **Prédiction chiffrée** : excès de ventes de +10 % à +30 % le dernier mois avant la hausse ; creux de −10 % à −25 % le
  premier mois après ; effet net cumulé sur les mois −2 à +6 compris entre −1 % et −5 %. Aucun effet sur les ventes en
  l'état futur d'achèvement, taxées à un taux réduit non concerné (|effet| < 5 %).
- **Test de mort** : le code est mis au point sur les seuls départements du 1er avril 2025. Échantillon de test fixé d'avance :
  départements à date d'effet au 1er mai et au 1er juin 2025 (57 environ), comparés aux départements sans hausse ou non encore
  traités. Étude d'événement empilée sur le logarithme du nombre mensuel de ventes, effets fixes département et mois,
  grappes par département. L'idée meurt si le coefficient du mois −1 est inférieur à +5 % ou si son intervalle à 95 %
  contient 0, ou si le coefficient du mois 0 n'est pas négatif. Le plan est déclaré contaminé si le placebo sur le neuf dépasse 5 % en valeur absolue.
  Second échantillon, rapporté sans seuil car petit : départements à date d'effet au 1er janvier 2026, avec les ventes du premier semestre 2026.
- **Données** : ventes notariées (DVF géolocalisé), date de l'acte, nature et type de bien :
  `https://files.data.gouv.fr/geo-dvf/latest/csv/2025/full.csv.gz` → **200** (98 Mo, années 2021 à 2025 disponibles) ;
  fichier par département `.../2025/departements/36.csv.gz` → **200**, en-tête lu (`date_mutation`, `nature_mutation`,
  `valeur_fonciere`, `type_local`, `code_departement`). Premier semestre 2026 :
  `https://static.data.gouv.fr/resources/demandes-de-valeurs-foncieres/20261012-171648/valeursfoncieres-2026-s1.txt.zip` → **206**
  (requête partielle, archive zip ; une réinitialisation de connexion au premier essai) ; le dossier `geo-dvf/latest/csv/2026/` est vide.
  Dates d'effet par département (table de la DGFiP, colonne « taux applicable depuis le ») :
  `https://www.impots.gouv.fr/sites/default/files/media/1_metier/3_partenaire/notaires/dmto/dmto_2026-01.pdf` → **200** ;
  comptage approximatif tiré du texte du PDF, à recompter : environ 27 départements au 1er avril 2025, 46 au 1er mai, 11 au
  1er juin, quelques-uns au 1er janvier 2026, une dizaine sans hausse. Les PDF mensuels de 2025 au même chemin renvoient 404.
  Recettes mensuelles de droits par département (variable de contrôle de cohérence) :
  `https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/dmto_attrib/records?limit=2` → **200** (après plusieurs
  réinitialisations de connexion). Écartés : `cgedd.fr` (connexion réinitialisée), `notaires.fr` (403).
- **Méthode** : agrégation de DVF en nombre de ventes par département, mois et type (ancien, neuf). Étude d'événement
  à adoption échelonnée avec un estimateur robuste aux effets hétérogènes (comparaison aux non encore traités, type
  Callaway-Sant'Anna ou empilement). Mesure de l'excès et du creux, puis de l'effet net. Placebo sur le neuf ; test de
  tendances préalables sur les mois −12 à −3.
- **Ce qui serait nouveau** : la réforme de 2025 est plus petite que celle de 2014 (+0,5 point contre +0,7), étalée sur
  trois dates et assortie d'une exonération pour les primo-accédants ; c'est un re-test hors échantillon des effets estimés sur 2014.
  Travaux proches : Bérard et Trannoy (2018, European Economic Review) sur la hausse de 2014 — à vérifier, y compris leurs
  ordres de grandeur ; Best et Kleven (2018, Review of Economic Studies) sur le droit de timbre britannique — à vérifier ;
  Kopczuk et Munroe (2015) sur la taxe new-yorkaise — à vérifier. Étude publiée sur la hausse de 2025 : référence incertaine.
- **Rôle de l'IA** : des agents écrivent le pipeline DVF, extraient la table des dates du PDF et la recopient en double
  aveugle (deux agents indépendants, écarts tranchés par l'humain). L'humain fixe l'échantillon de test et scelle les
  prédictions avant toute agrégation des mois de mai à juillet 2025. Garde : un script de verdict distinct relit les fichiers
  bruts ; l'agent qui a codé l'estimateur n'a accès qu'aux départements d'avril.
- **Coût et durée** : fichiers de 100 Mo par an, un portable suffit ; appels de modèles < 15 USD ; 5 semaines.
- **Risques** : les primo-accédants exonérés ne sont pas repérables dans DVF, ce qui atténue l'effet mesuré ; DVF ne couvre
  ni l'Alsace-Moselle ni Mayotte ; les départements sans hausse sont peu nombreux et peut-être atypiques ; reprise du marché
  en 2025 commune à tous ; délai entre promesse et acte, qui limite la capacité à avancer une signature.
- **Valeur si l'hypothèse meurt** : une absence d'anticipation mesurée avec 57 départements est informative : elle borne
  l'élasticité de court terme des transactions à une taxe de 0,5 point et contredit l'extrapolation de 2014.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai mesuré sur les ventes notariées de 2025 l'effet
  d'anticipation de la hausse des droits de mutation, en exploitant les dates d'adoption différentes selon les départements,
  avec un échantillon de test fixé à l'avance. » Graphique : coefficients de l'étude d'événement mois par mois, pic avant
  la date d'effet et creux après, ancien contre neuf. Métiers : recherche économique, banque centrale, conseil en politiques
  publiques, financement immobilier, direction du Trésor.

---

### D3 — Le canal des dépôts à l'épreuve de 2022-2023 : re-test scellé d'une prédiction publiée, banque par banque

- **Question** : la prédiction publiée avant 2022 selon laquelle les banques des marchés de dépôts concentrés répercutent
  moins les hausses de taux et perdent plus de dépôts s'est-elle vérifiée pendant le cycle de hausse de 2022-2023 ?
- **Hypothèse falsifiable** : à taille égale, une banque américaine dont les agences sont dans des comtés plus concentrés
  a eu un bêta de dépôts plus faible et une croissance des dépôts plus faible entre fin 2021 et fin 2023.
- **Prédiction chiffrée** : bêta cumulé moyen du coût des dépôts (variation du coût annualisé des dépôts domestiques
  rapportée à la variation du taux des fonds fédéraux, 2021T4 à 2023T4) entre 0,30 et 0,45. Un écart-type de concentration
  en plus abaisse le bêta de 1 à 3 points de pourcentage et la croissance des dépôts de 0,5 à 2 points.
- **Test de mort** : échantillon fixé d'avance : banques assurées présentes de 2021T4 à 2023T4, actif > 100 millions USD,
  sans fusion sur la période. Régression en coupe du bêta sur l'indice de concentration de la banque, avec le logarithme de
  l'actif et son carré, grappes par État. L'idée meurt si le coefficient n'est pas négatif à p < 0,05 (unilatéral), ou si,
  sur une liste d'au moins 200 spécifications figée avant lecture, moins de 75 % ont le signe attendu. Second test scellé
  à part : même signe sur la baisse des taux de 2024T3 à 2025T4.
- **Données** : comptes trimestriels par banque (API FDIC) :
  `https://banks.data.fdic.gov/api/financials?filters=CERT:3511&fields=CERT,REPDTE,DEP,DEPDOM,EDEPDOM,ASSET&limit=3&format=csv`
  → **200** (même réponse sur `https://api.fdic.gov/banks/financials`) ; la charge d'intérêts `EDEPDOM` est cumulée depuis
  le début de l'année et doit être décumulée. Dépôts par agence et par comté pour l'indice de concentration :
  `https://banks.data.fdic.gov/api/sod?filters=YEAR:2021 AND CERT:3511&fields=CERT,YEAR,STCNTYBR,DEPSUMBR,BRNUM&limit=3&format=csv`
  → **200**. Taux directeur : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS` → **200** au second essai
  (réponse vide au premier).
- **Méthode** : indice de Herfindahl par comté à partir des dépôts par agence de juin 2021 ; concentration d'une banque =
  moyenne de ces indices pondérée par ses dépôts. Bêta cumulé et croissance des dépôts par banque. Régressions en coupe,
  puis courbe de spécification : pondérations, seuils de taille, définition du bêta, contrôles, traitement des valeurs extrêmes.
  La course de chevaux concentration contre taille est le cœur du test.
- **Ce qui serait nouveau** : re-test prédéclaré, sur un cycle postérieur à la publication, d'un résultat dont la
  robustesse à la taille des banques est contestée. Travaux proches : Drechsler, Savov et Schnabl (2017, Quarterly Journal
  of Economics), « The deposits channel of monetary policy » — à vérifier ; Begenau et Stafford, sur la fixation uniforme des
  taux et la fragilité du lien avec la concentration — à vérifier, titre et date incertains ; d'Avernas, Eisfeldt, Huang,
  Stanton et Wallace sur les dépôts des grandes et petites banques — à vérifier ; Koont, Santos et Zingales sur la banque
  numérique et la fuite des dépôts — à vérifier. Plusieurs de ces travaux couvrent déjà 2022-2023 : la nouveauté est le
  protocole scellé et la courbe de spécification, pas la période.
- **Rôle de l'IA** : un agent énumère les spécifications défendables et la liste est figée par sha256 ; un autre exécute.
  L'humain décide de la spécification de référence et du seuil de 75 % avant collecte des comptes de 2022-2023. Garde : le
  script de verdict lit les sorties brutes et la liste figée ; aucune spécification ajoutée après coup n'entre dans le compte.
- **Coût et durée** : environ 4 500 banques sur 20 trimestres, quelques minutes de calcul ; appels de modèles < 15 USD ; 5 semaines.
- **Risques** : résultat jugé déjà connu par un spécialiste ; l'indice de concentration par comté mesure mal le pouvoir de
  marché depuis la banque en ligne ; la faillite de banques régionales en mars 2023 perturbe la croissance des dépôts ;
  le coût moyen des dépôts mélange effet de taux et effet de composition (dépôts à terme).
- **Valeur si l'hypothèse meurt** : « la concentration locale n'explique plus la répercussion des taux une fois la taille
  prise en compte » est une conclusion claire sur un mécanisme enseigné partout, avec la courbe de spécification à l'appui.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai re-testé sur environ 4 500 banques américaines et le
  cycle de taux de 2022-2023 la prédiction du canal des dépôts, avec une liste de 200 spécifications figée avant lecture
  des données. » Graphique : bêta de dépôts contre concentration par quantiles, avec et sans contrôle de taille. Métiers :
  gestion actif-passif et trésorerie bancaire, banque centrale, supervision, analyse crédit sur les banques, recherche quantitative.

---

### D4 — Les booms de crédit prédisent-ils les crises hors des pays riches ? Multivers et transport hors échantillon

- **Question** : la relation entre accélération du crédit et crise bancaire, estimée sur 18 économies avancées, prédit-elle
  les crises d'une vingtaine de pays absents de l'échantillon d'origine, et résiste-t-elle aux choix défendables de mesure ?
- **Hypothèse falsifiable** : un modèle estimé sur la base Jordà-Schularick-Taylor classe mieux que le hasard les
  années de crise des pays hors base, et le signe positif du crédit résiste à la grande majorité des spécifications.
- **Prédiction chiffrée** : aire sous la courbe ROC hors échantillon entre 0,58 et 0,68 (contre 0,65 à 0,72 dans
  l'échantillon). Signe positif et significatif à 5 % dans au moins 85 % des spécifications. L'écart d'aire entre chronologies
  de crises dépasse 0,05 et dépasse l'écart entre estimateurs.
- **Test de mort** : spécification de référence et coefficients gelés sur les 18 pays, années jusqu'à 2016. Échantillon de
  test fixé d'avance : pays présents dans les séries de crédit de la BRI et dans la chronologie de crises, absents de la base
  d'origine (20 pays attendus : Argentine, Autriche, Brésil, Chili, Chine, Colombie, Grèce, Hongrie, Inde, Indonésie, Corée,
  Malaisie, Mexique, Nouvelle-Zélande, Pologne, Russie, Singapour, Thaïlande, Turquie, Afrique du Sud), 1970-2016. L'idée
  meurt si l'aire hors échantillon est inférieure à 0,58 ou si la borne basse de son intervalle à 95 % (bootstrap par blocs
  de pays) est ≤ 0,50. Le volet robustesse meurt si moins de 85 % des spécifications ont le signe attendu à 5 %.
- **Données** : base macrohistorique : `https://www.macrohistory.net/app/download/9834512569/JSTdatasetR6.xlsx` → **200**
  (1,4 Mo, en-tête lu). Crédit au secteur privé non financier (BRI, téléchargement en bloc) :
  `https://data.bis.org/static/bulk/WS_TC_csv_flat.zip` → **200** (48 zones dont 25 pays hors base d'origine).
  Chronologie de crises sur 70 pays, 1800-2016 (fichier « global crisis data » hébergé par Harvard Business School) :
  `https://www.hbs.edu/behavioral-finance-and-financial-stability/Documents/ChartData/MapCharts/20160923_global_crisis_data.xlsx`
  → **200**. Chronologie européenne (CERS) : `https://www.esrb.europa.eu/pub/fcdb/esrb.fcdb20220120.en.xlsx` → **200**.
  Écartés : base de Laeven et Valencia sur `imf.org` (403) ; API de la Banque mondiale (délai dépassé, trois essais) ;
  API SDMX de la BRI `stats.bis.org/api/v2` (404 avec la clé essayée).
- **Méthode** : modèle logit de crise sur la croissance du crédit réel retardée, estimé sur les 18 pays. Multivers
  d'environ 900 spécifications : chronologie de crises, mesure du crédit (croissance réelle, variation du ratio au PIB sur
  3 ou 5 ans, écart à la tendance), retards, estimateur, effets fixes, période. Règle de lecture écrite avant exécution.
  Transport hors échantillon avec coefficients gelés ; intervalle par bootstrap par blocs de pays.
- **Ce qui serait nouveau** : la validation hors échantillon par pays avec coefficients gelés et la mesure de ce que le
  désaccord entre chronologies de crises coûte au résultat. Travaux proches : Schularick et Taylor (2012, American Economic
  Review), « Credit booms gone bust » — à vérifier ; Gourinchas et Obstfeld (2012, AEJ Macroeconomics), qui couvrent déjà les
  émergents — à vérifier ; Drehmann et Juselius (2014) sur les indicateurs avancés — à vérifier ; Greenwood, Hanson, Shleifer
  et Sørensen (2022, Journal of Finance), « Predictable financial crises » — à vérifier ; Baron, Verner et Xiong (2021,
  Quarterly Journal of Economics) sur les crises sans panique — à vérifier.
- **Rôle de l'IA** : un agent énumère le multivers, un humain raye les spécifications indéfendables, la liste est scellée.
  Un autre agent exécute. L'humain fixe la spécification de référence et les seuils. Garde : les données des 20 pays de test
  ne sont téléchargées par le script de verdict qu'après scellement des coefficients ; l'agent exécutant n'y a pas accès.
- **Coût et durée** : 900 logits sur 2 500 observations, quelques minutes ; appels de modèles < 10 USD ; 5 semaines.
- **Risques** : peu de crises dans l'échantillon de test (quelques dizaines), intervalle large ; chronologie de test arrêtée
  en 2016 ; séries de crédit de la BRI courtes pour certains émergents ; résultat qualitatif attendu par beaucoup de lecteurs.
- **Valeur si l'hypothèse meurt** : si le modèle ne se transporte pas, on documente une limite d'un des faits stylisés les
  plus cités depuis 2008, et l'on montre quelle part du résultat tient au choix de la chronologie de crises.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai estimé sur 18 pays avancés un modèle de prédiction des
  crises bancaires par le crédit, puis je l'ai évalué coefficients gelés sur 20 pays hors échantillon, avec 900
  spécifications énumérées à l'avance. » Graphique : courbe de spécification des 900 coefficients triés, avec en regard
  l'aire ROC dans et hors échantillon. Métiers : stabilité financière en banque centrale, risque pays, risque de crédit,
  recherche macroéconomique, gestion d'actifs sur dette émergente.

---

### D5 — Salaire minimum et emploi dans la restauration : multivers sur les paires de comtés frontaliers, 2014-2025

- **Question** : le résultat publié en 2010 d'un effet nul du salaire minimum sur l'emploi de la restauration, mesuré entre
  comtés voisins de part et d'autre d'une frontière d'État, tient-il sur les hausses bien plus fortes de 2014-2025 ?
- **Hypothèse falsifiable** : sur 2014-2025, l'élasticité de l'emploi de la restauration au salaire minimum, estimée entre
  paires de comtés contigus, reste proche de zéro, alors que l'élasticité des salaires moyens est nettement positive.
- **Prédiction chiffrée** : élasticité des salaires hebdomadaires moyens entre +0,12 et +0,25 ; élasticité de l'emploi
  entre −0,08 et +0,05 dans le plan par paires frontalières ; l'estimateur à effets fixes comté et période sans contrôle
  local donne une élasticité plus négative de 0,05 à 0,20.
- **Test de mort** : fenêtre entièrement postérieure à la publication : 2014T1 à 2019T4 et 2022T1 à 2025T4 (la pandémie
  est exclue d'avance). Comtés contigus à une frontière d'État, données non masquées sur toute la fenêtre, sans salaire
  minimum local. L'idée meurt si l'élasticité de l'emploi par paires est inférieure à −0,10 avec un intervalle à 95 % qui
  exclut 0 (grappes par État et par segment de frontière). Le test est déclaré non concluant, et le projet échoue sur ce
  point, si l'intervalle est plus large que 0,30 ou si l'élasticité des salaires n'est pas positive à 5 %. Lecture du
  multivers : part des spécifications donnant une élasticité inférieure à −0,10 et significative, seuil de mort à 50 %.
- **Données** : emploi et salaires par comté, restauration (code 722), API ouverte du recensement trimestriel de l'emploi :
  `https://data.bls.gov/cew/data/api/2014/1/industry/722.csv` → **200** ; `.../2019/1/...` → **200** ; `.../2025/1/...` et `.../2025/4/...` → **200** ;
  les années 1990 et 2007 par cette API → 404 (archives annuelles `https://data.bls.gov/cew/data/files/2007/csv/2007_qtrly_by_industry.zip`
  → **206**, 480 Mo par an, utiles seulement pour refaire la période d'origine). Contiguïté des comtés :
  `https://www2.census.gov/geo/docs/reference/county_adjacency.txt` → **200**. Salaires minimums d'État datés, jusqu'à fin 2022 :
  `https://raw.githubusercontent.com/benzipperer/historicalminwage/master/rawdata/StateMinimumWage_Changes.xlsx` → **200** ;
  salaires minimums locaux (pour exclure les comtés concernés) : `.../rawdata/SubstateMinimumWage_Changes.xlsx` → **200**.
  Années 2023-2025 : séries annuelles FRED par État, `https://fred.stlouisfed.org/graph/fredgraph.csv?id=STTMINWGCA` → **200**
  (au réessai). Écartés : page des versions sur `github.com` (403 depuis cette session), table historique du ministère du Travail `dol.gov` (403).
- **Méthode** : panel trimestriel de comtés. Deux plans de base : effets fixes comté et période ; effets fixes paire de
  comtés croisés avec la période. Multivers : code d'activité (722, restauration rapide), pondération, tendances d'État,
  seuil de population, traitement des trimestres masqués, grappes. Élasticité des salaires comme condition de pertinence.
  Test de tendances préalables par retards et avances du salaire minimum.
- **Ce qui serait nouveau** : la fenêtre 2014-2025 contient des salaires minimums beaucoup plus élevés par rapport au
  salaire médian que ceux de l'échantillon d'origine ; c'est un test d'extrapolation, avec règle de lecture fixée avant
  exécution sur un débat où le choix de spécification décide du signe. Travaux proches : Dube, Lester et Reich (2010, Review
  of Economics and Statistics), « Minimum wage effects across state borders » — à vérifier ; Neumark, Salas et Wascher (2014,
  ILR Review) — à vérifier ; Allegretto, Dube, Reich et Zipperer (2017, ILR Review) — à vérifier ; Cengiz, Dube, Lindner et
  Zipperer (2019, Quarterly Journal of Economics) — à vérifier ; Vaghul et Zipperer (2016) pour les données — à vérifier ;
  un réexamen du plan frontalier par Jha, Neumark et Rodriguez-Lopez — référence incertaine.
- **Rôle de l'IA** : un agent écrit la collecte et les deux plans ; un autre énumère les spécifications, liste scellée.
  L'humain arbitre les spécifications défendables et fixe les seuils (−0,10 ; 0,30 ; 50 %) avant toute estimation.
  Garde : un script de verdict indépendant recalcule les élasticités à partir des fichiers bruts ; un agent relecteur,
  sans accès aux résultats, vérifie la table des salaires minimums contre les sources.
- **Coût et durée** : 40 fichiers trimestriels de 240 ko, panel d'environ 1 000 comtés frontaliers, calcul en minutes ;
  appels de modèles < 20 USD ; 6 semaines (le nettoyage des salaires minimums est le poste le plus long).
- **Risques** : données masquées dans les petits comtés, ce qui réduit l'échantillon ; salaires minimums de 2023-2025 connus
  seulement à la date annuelle ; sujet très étudié, le jury peut juger la contribution modeste ; la pandémie laisse des
  traces après 2022 ; les comtés frontaliers ne sont pas représentatifs.
- **Valeur si l'hypothèse meurt** : montrer que le résultat de 2010 ne s'étend pas aux hausses récentes, avec une règle
  fixée d'avance, est une contribution nette ; s'il est non concluant, la courbe de spécification montre honnêtement
  pourquoi ce débat ne se tranche pas avec ces données.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai re-testé sur 2014-2025 l'effet du salaire minimum sur
  l'emploi de la restauration entre comtés américains voisins, avec des spécifications et une règle de lecture fixées avant
  l'estimation. » Graphique : courbe de spécification des élasticités de l'emploi, les deux plans en deux couleurs, bande
  de −0,10 à +0,10. Métiers : recherche économique, conseil en politiques publiques, banque centrale, instituts d'études, analyse de données.
