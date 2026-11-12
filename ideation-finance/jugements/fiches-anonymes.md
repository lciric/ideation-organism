# Fiches anonymes — ordre tiré par la graine sha256(fiches/SCEAUX.sha256)

### F01 — Anomalies publiées : l'érosion après publication est-elle un effet de la publication ou une tendance commune du calendrier ?

- **Question** : la baisse des rendements des anomalies après leur publication est-elle causée par la publication, ou reflète-t-elle un déclin général dans le temps qui toucherait aussi les anomalies pas encore publiées ?
- **Hypothèse falsifiable** : comparé, aux mêmes mois, à celui d'anomalies pas encore publiées, le rendement long-court d'une anomalie baisse dans les cinq ans qui suivent sa publication.
- **Prédiction chiffrée** : effet de la publication, avec effets fixes de mois et d'anomalie, de −20 % à −40 % du rendement moyen en échantillon d'origine ; baisse supplémentaire de −10 % à −25 % entre la fin de l'échantillon d'origine et la publication (part attribuable au biais de sélection statistique) ; aucune tendance préalable dans les cinq ans avant la fin de l'échantillon d'origine.
- **Test de mort** : étude d'événement empilée ; variable = rendement mensuel long-court divisé par sa moyenne sur l'échantillon d'origine. Choix de plan fixés sur les anomalies publiées jusqu'en 2000, scellés ; verdict sur les **cohortes publiées de 2001 à 2011**, témoins = anomalies publiées au moins cinq ans plus tard (jusqu'en 2016). Statistique : coefficient moyen des mois +1 à +60 moins celui des mois −60 à −1 autour de la publication, erreurs groupées par mois et par anomalie. **L'idée meurt si l'intervalle à 95 % contient 0 ou si l'estimation est plus faible que −10 % en valeur absolue** (dans ce cas : l'érosion est une tendance du calendrier). Garde : si les coefficients d'avance sont conjointement significatifs à 5 %, le plan est déclaré invalide plutôt que l'hypothèse confirmée.
- **Données** (Open Source Asset Pricing, Chen et Zimmermann, version 2026.10, hébergée sur Hugging Face, sans compte) :
  - Table des signaux (auteurs, année de publication, début et fin de l'échantillon d'origine, statistique t) : `https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/Data-Release-2026.10/SignalDoc.csv` → **200** (183 Ko, environ 330 lignes, prédicteurs et placebos confondus).
  - Rendements mensuels long-court par signal : `.../resolve/Data-Release-2026.10/Portfolios/Full%20Sets%20OP/PredictorLSretWide.parquet` → **206** sur une requête partielle (en-tête Parquet lu ; 1,4 Mo).
  - Signaux « placebo » pour la falsification : `.../Portfolios/Full%20Sets%20OP/PlaceboPortsFull.parquet` (présent dans l'arborescence, API → **200**).
  - Page du projet : `https://www.openassetpricing.com/data/` → **200**. L'ancien chemin GitHub `https://github.com/OpenSourceAP/CrossSection/raw/master/SignalDoc.csv` → **403** : ne pas l'utiliser.
- **Méthode** : pour chaque anomalie traitée, on empile ses rendements et ceux des témoins pas encore publiés sur la fenêtre [−120, +60] mois. Régression avec effets fixes pile×mois et pile×anomalie, coefficients par temps d'événement, deux ruptures distinguées (fin de l'échantillon d'origine, publication). Robustesse : estimateur pour traitements échelonnés à effets hétérogènes ; mêmes calculs sur les placebos, où aucun effet n'est attendu.
- **Ce qui serait nouveau** : l'érosion après publication est connue ; ce qui est neuf est de la traiter comme un traitement échelonné avec les estimateurs récents, des témoins propres, un graphique de tendance préalable, dix ans de données en plus et des cohortes de verdict postérieures à la conception. Travaux proches : McLean et Pontiff (2016), environ −26 % hors échantillon et −58 % après publication — chiffres à vérifier ; Chen et Zimmermann, biais de publication et jeu de données ouvert — à vérifier ; Jacobs et Müller (2020), anomalies à l'international — à vérifier ; Jensen, Kelly et Pedersen, crise de réplication en finance — à vérifier ; Harvey, Liu et Zhu, seuils de tests multiples — à vérifier. McLean et Pontiff contrôlent déjà en partie le temps : à vérifier, c'est le principal risque de redondance.
- **Rôle de l'IA** : les agents lisent la table des signaux, construisent les piles, codent les estimateurs et les placebos. L'humain décide des fenêtres, de la définition des témoins et de la règle de mort sur les cohortes d'avant 2001. Garde : le fichier des cohortes 2001-2011 est mis de côté par un script avant toute exploration ; le verdict est produit par un code séparé exécuté une fois ; l'agent qui a exploré les cohortes anciennes n'a pas accès au fichier de verdict.
- **Coût et durée** : calcul en secondes sur un portable. Agents : 5 à 10 USD. 5 semaines (une semaine pour comprendre les estimateurs échelonnés).
- **Risques** : la table ne donne que l'année de publication (incertitude de plusieurs mois, biais vers zéro) ; les témoins se raréfient pour les cohortes tardives ; les anomalies se ressemblent, donc le nombre effectif d'observations est inférieur à 200 ; le résultat peut seulement confirmer McLean et Pontiff.
- **Valeur si l'hypothèse meurt** : « l'érosion des anomalies est une tendance commune du calendrier, pas un effet de la publication » contredit une lecture courante de la littérature et se défend avec un graphique ; un plan invalide (tendance préalable) est aussi un résultat de méthode.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai réestimé l'effet de la publication sur les rendements d'environ 200 anomalies boursières par une étude d'événement empilée avec témoins pas encore publiés, sur des cohortes de verdict fixées d'avance. » Graphique unique : coefficients par temps d'événement de −120 à +60 mois, avec deux traits verticaux (fin d'échantillon d'origine, publication) et la courbe des placebos. Métiers : recherche quantitative actions, gestion factorielle, recherche académique en finance.

---

---

### F02 — Les banques prévoient-elles bien leur propre politique de crédit ? Rationalité des anticipations dans l'enquête BLS

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
  `https://data-api.ecb.europa.eu/service/data/BLS/Q.U2.ALL.O.E.Z.F06.ST.S.WFNET?format=csvdata` → **200** ;
  `.../BLS/Q.U2.ALL.O.E.Z.F3.ST.S.WFNET?format=csvdata` → **200** (après deux 503 et un délai dépassé).
  Liste des pays : `.../BLS/Q..ALL.O.E.Z.F3.ST.S.?format=csvdata&detail=serieskeysonly` → **200**, 21 pays (solde `FNET` ;
  `BFNET` pour BG, MT, SK). Clés par pays vérifiées sur la France (`.../BLS/Q.FR.ALL....F3...FNET?...serieskeysonly` → **200**) :
  critères (`ST.S`) et demande (`ZZ.D`) pour entreprises (`O.E.Z`), prêts au logement (`Z.H.H`), crédit à la consommation (`Z.H.C`),
  en `F06` (trois mois passés) et `F3` (trois mois à venir). Les clés `...BWFNET` et `...F3.ST.S.FNET` pour `U2` renvoient 404 : ne pas les utiliser.
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

---

### F03 — Liens entre secteurs : un modèle de langage choisit-il mieux que le hasard, sur des rendements postérieurs au gel de ses poids ?

- **Question** : les liens économiques orientés entre secteurs (« le secteur i précède le secteur j ») proposés par un modèle de langage prédisent-ils les rendements sectoriels mieux que des liens tirés au hasard ou choisis par fouille statistique, quand on juge sur des données que le modèle ne peut matériellement pas contenir ?
- **Hypothèse falsifiable** : sur la fenêtre postérieure au gel des poids, la liste de 100 liens proposée par le modèle donne une prévisibilité croisée signée plus forte que celle de listes aléatoires de même taille, et elle conserve une plus grande part de son avantage en échantillon que la liste choisie par fouille statistique.
- **Prédiction chiffrée** : en échantillon (1963-07 à 2023-12), la liste du modèle se place au-dessus du 95e centile des listes aléatoires. Sur la fenêtre de jugement (2024-01-03 à 2026-09-30, environ 143 semaines), son rendement signé moyen est positif, de l'ordre de +1 à +3 points de base par semaine et par unité de signal, soit un rang attendu vers le 85e-95e centile. Taux de conservation (avantage hors échantillon / avantage en échantillon) : 0,3 à 0,7 pour la liste du modèle, 0 à 0,3 pour la liste par fouille. Probabilité subjective que l'hypothèse survive au test de mort : environ 35 %.
- **Test de mort** : statistique R(liste) = moyenne sur les semaines de la fenêtre de jugement de (1/100) Σ s·z(i,t)·[r(j,t+1) − r(marché,t+1)], où s est le signe scellé et z(i,t) le rendement hebdomadaire du secteur i net du marché, divisé par son écart-type glissant sur 52 semaines. Valeur p par permutation = part de 10 000 listes aléatoires (mêmes proportions de signes) dont R ≥ R(liste du modèle). **L'idée meurt si p > 0,05.** Critère secondaire écrit d'avance : R(modèle) − R(fouille) avec intervalle à 90 % par bootstrap par blocs de 4 semaines ; si la borne haute est < 0, la fouille statistique domine et on l'écrit.
- **Données** :
  - Rendements quotidiens de 49 secteurs, Ken French : `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/49_Industry_Portfolios_daily_CSV.zip` → **200** (4,2 Mo ; dernière date lue : 2026-09-30).
  - Marché et taux sans risque quotidiens : `.../ftp/F-F_Research_Data_Factors_daily_CSV.zip` → **200**.
  - Poids gelés du modèle : `https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF` (API `https://huggingface.co/api/models/TheBloke/Mistral-7B-Instruct-v0.2-GGUF` → **200**, non restreint, sans compte ; journal des commits → **200**, dernier dépôt de poids le 2023-12-11 ; fichier `mistral-7b-instruct-v0.2.Q4_K_M.gguf` → **302 puis 200**, 4,37 Go, empreinte sha256 exposée `3e0039fd…ccf9`).
  - Second modèle optionnel pour la robustesse : `bartowski/Meta-Llama-3.1-8B-Instruct-GGUF` (API → **200**, créé le 2024-07-23 ; fenêtre de jugement alors 2024-08 à 2026-09).
- **Méthode** : (1) Le modèle gelé reçoit seulement les 49 noms de secteurs et leur définition, sans aucune donnée ; il liste des liens orientés i→j avec signe et mécanisme en une ligne ; 20 tirages, on garde les 100 liens les plus souvent cités. (2) Liste concurrente « fouille » : les 100 liens au plus fort |t| dans la régression prédictive hebdomadaire sur 1963-2023. (3) Listes aléatoires : 10 000 tirages parmi les 49×48 liens. (4) Les trois listes sont scellées (sha256) avant toute lecture des lignes postérieures au 2023-12-29. (5) Un code de verdict séparé calcule R, la valeur p par permutation et le bootstrap. Variante quotidienne déclarée d'avance comme secondaire.
- **Ce qui serait nouveau** : la comparaison de trois sources d'hypothèses (savoir économique d'un modèle, fouille statistique, hasard) avec une garantie matérielle contre la mémorisation, et la mesure du « taux de conservation » qui sépare ce que le modèle sait de ce qu'il récite. Travaux proches : Hong, Torous et Valkanov (2007), secteurs qui précèdent le marché — à vérifier ; Cohen et Frazzini (2008), liens clients-fournisseurs — à vérifier ; Menzly et Ozbas (2010), diffusion entre secteurs liés — à vérifier ; Chen, Lopez-Lira et Zimmermann, théorie publiée contre fouille de données — à vérifier ; Novy-Marx et Velikov, production automatisée d'hypothèses en finance — référence incertaine ; Lopez-Lira et Tang, modèles de langage et rendements, avec le problème de la date de coupure — à vérifier.
- **Rôle de l'IA** : le modèle gelé propose les liens ; un agent de code (modèle récent) écrit la chaîne de traitement mais **n'a aucun rôle éditorial** sur la liste (transmission mot pour mot, vérifiée par empreinte). L'humain fixe la grammaire des hypothèses, le nombre de liens, la statistique et le seuil avant le scellé. Gardes : (a) **garantie contre la mémorisation** = le fichier de poids a été déposé publiquement le 2023-12-11 avec une empreinte sha256 ; un fichier figé à cette date ne peut pas contenir des rendements de 2024-2026 ; on vérifie l'empreinte du fichier téléchargé avant usage ; (b) le modèle récent, qui a pu voir 2024-2026, ne touche jamais à la liste ; (c) test témoin : 50 questions factuelles sur les marchés de 2024-2025 posées au modèle gelé, taux de réussite attendu au niveau du hasard, publié ; (d) volet prospectif : les mêmes listes sont renotées sur les mois publiés par Ken French après la date du scellé.
- **Coût et durée** : inférence locale sur processeur (7 milliards de paramètres, quantifié 4 bits, quelques jetons par seconde : 20 tirages en une nuit) : 0 USD. Agent de code : 5 à 10 USD. 4 à 5 semaines.
- **Risques** : la prévisibilité croisée hebdomadaire entre secteurs peut être nulle pour toutes les listes après 2024, ce qui tue l'hypothèse sans distinguer « le modèle ne sait rien » de « il n'y a rien à savoir » (parade : rapporter aussi l'avantage en échantillon) ; 143 semaines donnent une puissance modeste ; un petit modèle peut produire des liens banals ; les portefeuilles sectoriels pondérés par la valeur réduisent l'effet des cotations non synchrones mais ne l'annulent pas.
- **Valeur si l'hypothèse meurt** : on écrit que le savoir économique d'un modèle de langage, propre de toute mémorisation, ne sélectionne pas mieux que le hasard des relations prédictives entre secteurs ; l'écart entre son avantage en échantillon et son avantage hors échantillon devient une mesure chiffrée de la part de récitation, utile à toute étude qui utilise ces modèles en finance. Le protocole (poids datés, scellé, test témoin) reste réutilisable.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai comparé, sur des rendements postérieurs au gel des poids d'un modèle de langage, des relations prédictives entre secteurs proposées par ce modèle, par fouille statistique et par tirage au hasard, avec prédictions scellées et test par permutation. » Graphique unique : histogramme des 10 000 listes aléatoires sur la fenêtre de jugement, avec deux traits verticaux (liste du modèle, liste par fouille), et le même graphique en échantillon à côté. Métiers : recherche quantitative, gestion d'actifs systématique, équipes de données et d'IA en banque.

---

---

### F04 — Adjudications du Trésor américain : la pression de prix existe-t-elle encore et croît-elle avec la taille des émissions ?

- **Question** : le rendement de l'échéance mise en adjudication monte-t-il dans les jours qui précèdent l'adjudication puis redescend-il après, et l'amplitude augmente-t-elle avec le montant émis ?
- **Hypothèse falsifiable** : autour de chaque adjudication de titres à 2, 3, 5, 7, 10, 20 et 30 ans, l'écart entre le rendement de l'échéance adjugée et la courbe ajustée sur les titres anciens dessine un V inversé (hausse avant, baisse après), plus marqué quand le montant offert est grand.
- **Prédiction chiffrée** : sur 2010-2026, amplitude du V inversé (hausse de J−5 à J plus baisse de J à J+5) positive, de l'ordre de 2 à 4 points de base sur le rendement brut à 10 ans et de 0,5 à 1,5 point de base sur l'écart à la courbe ; un écart-type de montant offert en plus ajoute environ +0,3 à +0,8 point de base.
- **Test de mort** : statistique V = (y(J) − y(J−5)) − (y(J+5) − y(J)), calculée sur l'écart « rendement à échéance constante FRED − rendement au pair de la courbe ajustée de la Réserve fédérale » à l'échéance adjugée. Tous les choix (fenêtre, mesure, filtres) sont fixés et scellés sur 1980-2009 ; verdict sur **2010-01 à 2026-09** (environ 1 000 adjudications). **L'idée meurt si la moyenne de V ≤ 0 ou si t < 2** (erreurs groupées par mois). Garde de validité : sur des dates fictives (même jour de semaine, semaines sans adjudication de cette échéance), |t| doit rester < 2, sinon le plan est déclaré invalide. Second verdict : pente de V sur le montant offert normalisé ≤ 0 ou p unilatérale > 0,05 → la partie « dose » meurt.
- **Données** :
  - Adjudications depuis 1979 (date, échéance, montant offert, part des spécialistes en valeurs du Trésor, réouverture) : `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query` → **200** (11 154 lignes ; première note lue : 1979-10-31). Recoupement : `https://www.treasurydirect.gov/TA_WS/securities/search?...&format=json` → **200**.
  - Rendements quotidiens à échéance constante, FRED : DGS1, DGS2, DGS3, DGS5, DGS7, DGS10, DGS20, DGS30 (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10`, etc.) → **200** chacun (jusqu'au 2026-11-09).
  - Courbe ajustée quotidienne (Gürkaynak, Sack et Wright) : `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` → **200** (16,7 Mo, depuis 1961, dernière date 2026-11-06).
  - Dates de publication de l'indice des prix et de l'emploi (pour contrôler les annonces) : pages ALFRED `https://alfred.stlouisfed.org/series/downloaddata?seid=CPIAUCSL` et `...seid=PAYEMS` → **200** (dates de millésime présentes dans la page).
- **Méthode** : étude d'événement sur la fenêtre [−10, +10] jours ouvrés autour de chaque adjudication. Variable : écart du rendement adjugé à la courbe ajustée, ce qui retire les mouvements généraux de taux. Régression de V sur le montant offert (rapporté à sa moyenne glissante sur 3 ans), la part absorbée par les spécialistes, des indicatrices d'annonces macroéconomiques et de fin de mois. Erreurs groupées par mois ; test placebo sur dates fictives et sur échéances non adjugées.
- **Ce qui serait nouveau** : un test hors échantillon, après publication, d'un effet de pression de prix sur le marché le plus liquide du monde, avec une relation dose-effet sur la période d'émissions records et de réduction du bilan de la Réserve fédérale. Travaux proches : Lou, Yan et Zhang (2013), chocs d'offre anticipés et répétés sur les titres du Trésor, échantillon s'arrêtant vers 2008 — à vérifier ; Fleming et Rosenberg, gestion des positions des spécialistes autour des adjudications — à vérifier ; travaux sur les contraintes de bilan des intermédiaires (He, Kelly et Manela ; Duffie) — à vérifier. Je ne sais pas si une mise à jour jusqu'en 2026 a été publiée : référence incertaine.
- **Rôle de l'IA** : les agents écrivent le chargement de l'API, l'appariement échéance-adjudication et l'étude d'événement ; un agent propose les spécifications sur 1980-2009 seulement. L'humain choisit la mesure et scelle le plan. Garde : le code de verdict est écrit par un autre agent, testé sur données simulées, et lit pour la première fois les lignes postérieures à 2009 lors d'une exécution unique ; l'agent qui a conçu le plan ne lance pas le verdict.
- **Coût et durée** : calcul négligeable. Agents : 5 à 10 USD. 4 à 5 semaines.
- **Risques** : les rendements à échéance constante sont interpolés et ne mesurent le titre adjugé qu'approximativement ; le calendrier d'adjudication coïncide avec des publications macroéconomiques (d'où l'écart à la courbe et les placebos) ; l'effet peut être trop petit pour ces données ; une étude récente peut déjà couvrir la période.
- **Valeur si l'hypothèse meurt** : un effet documenté sur 1980-2008 qui disparaît après publication malgré des émissions bien plus grosses est un résultat sur l'arbitrage dans un marché liquide ; on écrit la borne supérieure de l'effet compatible avec les données.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai mesuré par étude d'événement, sur environ 1 000 adjudications du Trésor américain de 2010 à 2026, la variation du rendement de l'échéance adjugée autour de la date d'adjudication, selon un plan fixé sur 1980-2009. » Graphique unique : trajectoire moyenne de l'écart à la courbe de J−10 à J+10 avec bande de confiance, pour les gros et les petits montants. Métiers : salle de marché de taux, agence de la dette, banque centrale, recherche économique.

---

---

### F05 — Les a priori d'un modèle sur l'exposition des industries au pétrole, aux taux et au dollar

- **Question** : l'exposition des 49 industries américaines aux chocs de pétrole, de taux longs et de dollar est-elle connaissable
  a priori, par raisonnement économique écrit avant de voir les rendements ?
- **Hypothèse falsifiable** : les bêtas annoncés par le modèle, scellés avant lecture des données, classent correctement les
  industries selon leurs bêtas réalisés après la date de coupure (corrélation de rang positive), mais n'ajoutent rien à un bêta
  historique estimé sur cinq ans.
- **Prédiction chiffrée** : corrélation de Spearman entre a priori et bêtas réalisés en fenêtre propre : pétrole 0,4 à 0,7 ; taux
  à 10 ans 0,2 à 0,5 ; dollar 0,0 à 0,3. Bêta historique sur 5 ans : 0,6 à 0,8 pour le pétrole. Corrélation partielle de l'a
  priori une fois le bêta historique pris en compte : inférieure à 0,2. En revanche, contracter un bêta estimé sur 60 jours vers
  l'a priori du modèle réduit l'erreur quadratique de 5 à 20 % par rapport à une contraction vers zéro.
- **Test de mort** : fenêtre propre = jours de bourse de T_c + 3 mois au 2026-09-30 (au moins 240 jours). L'idée meurt si la
  valeur p de permutation (10 000 permutations des étiquettes d'industrie) du Spearman est ≥ 0,05 pour le pétrole (seuil d'environ
  0,24 avec 49 industries) **et** pour la mesure empilée des trois chocs. Seconde branche, jugée séparément : la contraction vers
  l'a priori meurt si elle ne réduit pas l'erreur quadratique face à la contraction vers zéro (valeur p ≥ 0,05, bootstrap par
  blocs de jours). Un plafond de bruit (corrélation entre bêtas réalisés des jours pairs et impairs) est rapporté à côté.
- **Données** :
  - 49 industries, rendements quotidiens : `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/49_Industry_Portfolios_daily_CSV.zip`
    → **200** (4,2 Mo ; « created using the 202609 CRSP database » ; dernière ligne 20260930).
  - Facteur de marché et taux sans risque quotidiens : `.../ftp/F-F_Research_Data_Factors_daily_CSV.zip` → **200** (jusqu'au 20260930).
  - Pétrole WTI quotidien : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO` → **200** (jusqu'au 2026-11-03).
  - Taux à 10 ans : `...id=DGS10` → **200** (jusqu'au 2026-11-09). Indice large du dollar : `...id=DTWEXBGS` → **200** (2006-01-02 au 2026-11-06).
- **Méthode** : (1) Le modèle donne, pour chaque industrie et chaque choc (pétrole +1 %, taux à 10 ans +10 pb, dollar +1 %), la
  réaction attendue du rendement en excès du marché, en points de base, avec une phrase de justification ; cinq passages avec
  l'ordre des industries mélangé, moyenne par industrie. (2) Scellement. (3) Bêtas réalisés par MCO quotidien du rendement en excès
  sur le marché et les trois chocs, en fenêtre propre. (4) Spearman avec test de permutation ; régression transversale du bêta
  réalisé sur le bêta historique et l'a priori ; comparaison de trois contractions d'un bêta de 60 jours (vers zéro, vers
  l'historique, vers l'a priori). **Garde contre la connaissance du futur** : aucune donnée n'est fournie au modèle ; les bêtas
  réalisés ne sont estimés que sur des rendements postérieurs à T_c + 3 mois ; en placebo, on compare le Spearman obtenu sur les
  cinq années d'avant coupure à celui de la fenêtre propre : l'écart mesure ce qui relève du souvenir de l'historique.
- **Ce qui serait nouveau** : on sait que les bêtas d'industrie estimés sont bruités et instables et qu'on les contracte vers une
  cible statistique ; utiliser comme cible un **a priori économique écrit et scellé**, puis le juger sur une période que le modèle
  n'a pas pu lire, est à ma connaissance peu fait. Travaux proches : Fama et French (1997), « Industry costs of equity »
  (à vérifier) ; Vasicek (1973) sur la contraction bayésienne des bêtas (à vérifier) ; Ludwig et Mullainathan, « Machine learning
  as a tool for hypothesis generation » (à vérifier) ; pour l'élicitation d'a priori par modèle de langage en finance : référence
  incertaine.
- **Rôle de l'IA** : le modèle joue le rôle de générateur d'hypothèses (147 signes et grandeurs) ; un agent distinct écrit
  l'estimation des bêtas et le verdict. L'humain choisit les trois chocs, la fenêtre de 60 jours et les seuils. Garde : le fichier
  des a priori est scellé (sha256) avant tout téléchargement de rendements postérieurs à T_c ; la règle statistique est écrite hors
  du modèle et exécutée par un rôle qui n'a pas produit les a priori.
- **Coût et durée** : 3 chocs × 5 passages × 7 lots de 7 industries = 105 appels, plus 45 appels de reformulation de contrôle :
  **150 appels** d'environ 800 jetons en entrée et 400 en sortie, soit **≈ 1,5 USD**. Calcul : quelques secondes. 4 semaines.
- **Risques** : 12 mois de fenêtre propre donnent des bêtas réalisés bruités pour les industries peu exposées (d'où le plafond de
  bruit) ; un Spearman positif pour le pétrole peut paraître évident (les pétrolières aiment le pétrole cher) : l'intérêt repose
  alors sur les taux, le dollar et la branche « contraction » ; les trois chocs sont corrélés entre eux certains jours.
- **Valeur si l'hypothèse meurt** : si l'a priori ne classe rien, c'est un résultat net sur les limites du « raisonnement
  économique » d'un modèle face à une statistique simple ; si seule la contraction échoue, on documente que l'historique sur 5 ans
  suffit, ce qui intéresse un constructeur de modèles de risque.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai fait écrire et sceller par un modèle de langage 147 hypothèses
  d'exposition sectorielle au pétrole, aux taux et au dollar, puis je les ai jugées sur des rendements postérieurs à sa date de
  coupure. » Graphique : nuage des 49 industries, bêta pétrole annoncé en abscisse, bêta réalisé en ordonnée, noms des industries
  affichés. Métiers : modèles de risque et gestion d'actifs, recherche quantitative actions, stratégie sectorielle en banque
  d'investissement.

---

---

### F06 — Corrélation actions-obligations et inflation : un modèle figé en 2019 prédit-il la bascule de 2021-2025 pays par pays ?

- **Question** : la corrélation entre rendements des actions et des obligations d'État dépend-elle du niveau d'inflation au point de prédire, pays par pays, son changement pendant la poussée d'inflation de 2021-2025 ?
- **Hypothèse falsifiable** : la corrélation actions-obligations augmente avec l'inflation moyenne ; les pays où l'inflation a le plus monté en 2021-2025 sont ceux où la corrélation a le plus augmenté.
- **Prédiction chiffrée** : dans le panel 1960-2019 (fenêtres de 5 ans sans chevauchement, effets fixes pays), pente de +0,04 à +0,10 de corrélation par point d'inflation annuelle. Sur 2021-2025, pente entre pays de la variation de corrélation sur la variation d'inflation moyenne : positive, +0,03 à +0,10 par point ; le modèle figé réduit l'erreur quadratique moyenne d'au moins 10 % par rapport à la simple persistance.
- **Test de mort** : coefficients estimés sur les fenêtres finissant au plus tard en 2019-12, scellés. Fenêtre de jugement : **2021-01 à 2025-12**, environ 20 pays. (1) Rapport des erreurs quadratiques moyennes (modèle figé / persistance de la corrélation 2015-2019) ≥ 1 → mort. (2) Pente entre pays de Δcorrélation sur Δinflation ≤ 0, ou valeur p unilatérale par permutation des pays > 0,05 → mort. **Un seul échec suffit.**
- **Données** (FRED, toutes testées sur `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>`) :
  - Taux longs mensuels `IRLTLT01<PP>M156N` pour US, CA, GB, DE, FR, IT, ES, NL, BE, AT, FI, IE, PT, SE, NO, DK, CH, JP, AU, NZ, KR → **200** pour les 21 (jusqu'en 2026-08 ou 2026-09).
  - Indices boursiers mensuels `SPASTT01<PP>M661N`, mêmes 21 pays → **200** (jusqu'en 2026-09).
  - Inflation annuelle `FPCPITOTLZG<ISO3>` : testés USA, DEU, GBR, AUS, NZL, KOR, CHE, SWE, CAN, JPN → **200** (jusqu'en 2025, États-Unis jusqu'en 2024) ; les 11 autres codes suivent le même schéma et restent à tester. Série mensuelle `CPALTT01<PP>M659N` → **200** mais arrêtée en 2025-03 (Japon 2021-06, Corée 2023-11 ; Australie et Nouvelle-Zélande **404**) : utilisée seulement en robustesse.
  - Robustesse quotidienne : États-Unis DGS10 → **200** et marché Ken French quotidien → **200** ; zone euro, taux à 10 ans de la BCE `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?format=csvdata` → **200**, et facteurs Europe quotidiens Ken French `.../ftp/Europe_5_Factors_Daily_CSV.zip` → **200**.
- **Méthode** : rendement obligataire mensuel approché par r = y/12 − D·Δy (duration D = 8) ; rendement des actions par variation logarithmique de l'indice. Corrélation par pays et par fenêtre de 5 ans. Panel à effets fixes pays de la corrélation sur l'inflation moyenne de la fenêtre, erreurs groupées par pays. Prévision 2021-2025 à coefficients figés, comparée à la persistance ; régression entre pays de la variation de corrélation sur la variation d'inflation, avec test par permutation.
- **Ce qui serait nouveau** : la bascule américaine de 2022 est connue ; ce qui ne l'est pas, à ma connaissance, est un test de dose-effet entre une vingtaine de pays, avec coefficients figés avant l'épisode et comparaison explicite à la persistance. Travaux proches : Campbell, Pflueger et Viceira, régimes macroéconomiques et bêta des obligations — à vérifier ; Campbell, Sunderam et Viceira, inflation et covariance actions-obligations — à vérifier ; Li (2002), inflation et corrélation actions-obligations dans les pays du G7 — à vérifier ; notes de sociétés de gestion parues après 2022 — référence incertaine.
- **Rôle de l'IA** : les agents assemblent le panel de 60 séries, vérifient les ruptures, codent le panel et les prévisions. L'humain fixe la duration, la longueur des fenêtres et la liste des pays avant le scellé. Garde : coefficients et prévisions par pays scellés (sha256) à partir d'un fichier tronqué à 2019-12 ; le verdict est calculé par un code séparé qui seul lit 2021-2025 ; aucune respécification après lecture.
- **Coût et durée** : calcul négligeable. Agents : 3 à 8 USD. 4 semaines.
- **Risques** : le résultat pour les États-Unis est attendu, tout l'intérêt repose sur la variation entre pays, qui peut être trop faible (choc mondial commun) ; les séries OCDE sont des moyennes mensuelles, ce qui lisse les corrélations ; une vingtaine de pays donne peu de puissance ; la duration fixe est une approximation.
- **Valeur si l'hypothèse meurt** : si la corrélation monte partout sans lien avec l'inflation locale, la bascule tient à un facteur mondial (taux américains, politique monétaire commune) et non à l'inflation nationale : résultat utile pour qui construit un portefeuille diversifié hors des États-Unis.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai estimé sur 21 pays et 1960-2019 le lien entre inflation et corrélation actions-obligations, puis jugé ses prévisions figées sur 2021-2025 contre une référence de persistance. » Graphique unique : nuage de points par pays, variation de l'inflation en abscisse, variation de la corrélation en ordonnée, avec la droite prédite en 2019 et la droite observée. Métiers : allocation d'actifs, gestion multi-actifs, stratégie de taux, banque centrale.

---

---

### F07 — Le canal des dépôts à l'épreuve de 2022-2023 : re-test scellé d'une prédiction publiée, banque par banque

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

---

### F08 — Les booms de crédit prédisent-ils les crises hors des pays riches ? Multivers et transport hors échantillon

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

---

### F09 — Livre beige : le texte régional dit-il quelque chose que l'emploi passé ne dit pas ?

- **Question** : le ton du rapport de chaque district de la Réserve fédérale dans le Livre beige prédit-il la croissance de
  l'emploi de ce district sur les trois mois suivants, une fois retirés la conjoncture nationale, le niveau moyen du district et
  l'emploi passé ?
- **Hypothèse falsifiable** : à date donnée, les districts dont le rapport est noté plus favorable connaissent ensuite une
  croissance de l'emploi plus forte que les autres (coefficient positif), y compris quand le texte est anonymisé et sur les
  rapports postérieurs à la date de coupure.
- **Prédiction chiffrée** : un point de ton (échelle −2 à +2) ↔ +0,05 à +0,15 point de croissance de l'emploi sur trois mois (non
  annualisée) par rapport aux autres districts à la même date ; gain de R² intra-groupe ≤ 0,02 ; écart entre bras daté et bras
  anonymisé inférieur à 30 % du coefficient.
- **Test de mort** : bras anonymisé, 12 districts × environ 150 rapports (2008 – mi-2026), soit environ 1 800 observations. L'idée
  meurt si le coefficient de ton est ≤ 0 ou si sa valeur p est ≥ 0,05 selon un test de permutation qui réattribue les notes entre
  districts **à l'intérieur de chaque date** (5 000 tirages) ; ou si, sur les rapports de la fenêtre propre (environ 6 livraisons
  dont la cible à trois mois est déjà publiée, soit environ 72 observations), le coefficient est négatif avec un intervalle à 95 %
  qui exclut l'estimation d'avant coupure.
- **Données** :
  - Rapports par district, archive de la Fed de Minneapolis, adresse régulière `https://www.minneapolisfed.org/beige-book-reports/<AAAA>/<AAAA>-<MM>-<code>` :
    `.../1985/1985-03-ch` → **200** ; `.../2024/2024-10-at` → **200** ; `.../2026/2026-10-at` → **200** ; les dix autres codes
    (bo, cl, da, kc, mi, ny, ph, ri, sf, sl) testés sur 2015-06 → **200** chacun ; synthèse nationale `.../2024/2024-10-su` → **200**.
  - Mêmes textes à la source : `https://www.federalreserve.gov/monetarypolicy/beigebook202410.htm` → **200** ;
    `.../beigebook202410-atlanta.htm` (lien présent dans la page) ; `.../beigebook202610-atlanta.htm` → **200** ; liste
    `https://www.federalreserve.gov/monetarypolicy/publications/beige-book-default.htm` → **200** ; archive
    `.../beige-book-archive.htm` → **200**. (Une adresse devinée, `beigebook202609.htm`, a rendu 404 : il n'y a pas de livraison ce mois-là.)
  - Emploi salarié non agricole par État, mensuel : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=CANA` → **200** (1990-01 à
    2026-09) ; `...id=TXNA` → **200**. Chômage par État : `...id=CAUR` → **200**. Les 48 autres États suivent le même schéma de nom
    (`<ÉTAT>NA`), non testés un par un.
  - Millésimes pour les contrôles en temps réel : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=CANA&vintage_date=2024-06-30` → **200**.
- **Méthode** : panel district × livraison. Le modèle note de −2 à +2 l'emploi et l'activité décrits par chaque rapport. Emploi du
  district = somme des États rattachés à titre principal (table de correspondance fixée d'avance). Régression :
  croissance_{d, t→t+3} = α_d + γ_t + β·Ton_{d,t} + deux retards de croissance + ε, effets fixes de district et de date, inférence
  par permutation intra-date et, en contrôle, erreurs groupées par date. Bras anonymisé (noms de district, de villes, d'États,
  d'entreprises et dates masqués par un script) sur tout l'échantillon ; bras daté sur un quart tiré au hasard, pour mesurer
  l'écart. **Garde contre la connaissance du futur** : (i) les effets fixes de date absorbent tout ce que le modèle sait de la
  conjoncture nationale future ; l'identification ne vient que des écarts entre districts à la même date ; (ii) anonymisation ;
  (iii) sous-échantillon postérieur à T_c + 3 mois ; (iv) écart daté − anonymisé rapporté comme mesure de fuite.
- **Ce qui serait nouveau** : les travaux que je connais relient le Livre beige à l'activité nationale ou notent le texte par
  dictionnaire ; ici l'identification est **intra-date, entre districts**, avec un test propre de fuite d'information et une
  fenêtre postérieure à la coupure. Travaux proches : Balke et Petersen (2002), « How well does the Beige Book reflect economic
  activity? » (à vérifier) ; Armesto, Hernández-Murillo, Owyang et Piger (2009) sur le contenu informatif du Livre beige
  (à vérifier) ; Shi et Hollifield, « Predictive Power of LLMs in Financial Markets », arXiv 2411.16569 (titre vérifié sur arXiv,
  ressorti d'une recherche « Beige Book », contenu non relu) ; notes récentes de la Réserve fédérale utilisant des modèles de
  langage sur le Livre beige : référence incertaine.
- **Rôle de l'IA** : un agent collecte et anonymise les rapports, un autre lance la notation, un troisième construit le panel
  d'emploi sans voir les notes. L'humain fixe la table États → districts, l'horizon de trois mois, l'échelle et les seuils. Garde :
  notes scellées (sha256) avant la construction de la variable expliquée ; régression et permutation dans un script figé d'avance,
  exécuté par un rôle qui n'a pas noté les textes.
- **Coût et durée** : 1 800 appels (bras anonymisé) + 450 appels (bras daté) = **2 250 appels** d'environ 2 300 jetons en entrée
  et 40 en sortie : ≈ 5,2 M de jetons en entrée, soit **≈ 17 USD**. Calcul : moins d'une minute. 6 semaines (collecte et table de
  correspondance : deux semaines).
- **Risques** : les districts ne suivent pas les frontières des États (la Pennsylvanie, par exemple, est partagée), d'où une
  erreur de mesure qui tire le coefficient vers zéro ; l'emploi par État est révisé chaque année, donc les retards utilisés en
  contrôle doivent venir des millésimes d'ALFRED ; le ton peut ne résumer que l'emploi déjà publié ; 12 districts donnent peu de
  variation transversale par date.
- **Valeur si l'hypothèse meurt** : un résultat nul bien identifié dit que l'information qualitative régionale n'ajoute rien aux
  chiffres d'emploi à trois mois, ce qui nuance l'usage courant du Livre beige ; le jeu de notes district × date, publié, reste
  réutilisable.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai construit un panel de 12 districts sur 18 ans à partir du
  texte du Livre beige noté par un modèle de langage et testé, avec effets fixes de date et de district, s'il prédit l'emploi
  régional à trois mois. » Graphique : nuage par classes de la croissance résiduelle de l'emploi contre le ton résiduel, en deux
  couleurs (avant et après la date de coupure). Métiers : recherche économique et banque centrale, études régionales, conseil
  économique, recherche macro en gestion d'actifs.

---

---

### F10 — Contexte ou mémoire ? Prévoir l'inflation à un mois avec des chiffres nommés ou anonymes

- **Question** : dire à un modèle « voici l'inflation de tel pays à telle date » améliore-t-il sa prévision à un mois par rapport
  aux mêmes chiffres rendus anonymes, et quelle part de ce gain disparaît après sa date de coupure ?
- **Hypothèse falsifiable** : le gain de précision apporté par le contexte (nom du pays, variable, dates) est nettement plus fort
  avant la date de coupure qu'après : l'essentiel du gain mesuré en rétro-test est de la mémoire, et la valeur du contexte en
  conditions propres est proche de zéro.
- **Prédiction chiffrée** : avant T_c, l'erreur quadratique moyenne du bras nommé est inférieure de 15 à 40 % à celle du bras
  anonyme ; après T_c + 3 mois, l'écart est compris entre −5 % et +10 %. Coefficient de différence de différences δ > 0,
  représentant au moins 70 % du gain d'avant coupure. En fenêtre propre, le bras nommé ne bat pas un AR(1) : |statistique de
  Diebold-Mariano| < 1,96.
- **Test de mort** : deux modèles dont les dates de coupure diffèrent d'au moins 9 mois ; 11 pays × 36 mois × 2 bras × 2 modèles.
  On régresse d = (perte anonyme − perte nommée) sur un effet fixe de modèle, un effet fixe de mois et l'indicatrice « mois
  antérieur à la coupure de ce modèle ». L'idée meurt si δ ≤ 0 ou si sa valeur p unilatérale (bootstrap sauvage groupé par mois)
  est ≥ 0,05. Condition de validité écrite d'avance : la perte du bras anonyme rapportée à celle de l'AR(1) doit rester stable à
  ± 25 % entre les périodes, sinon le verdict est « non concluant » et non « confirmé ».
- **Données** :
  - Indices des prix harmonisés mensuels par pays, sur FRED : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=CP0000DEM086NEST`
    → **200** (1996-01 à 2026-09) ; mêmes séries pour FR, IT, ES, NL, AT, BE, FI, IE, PT, GR (`CP0000<PAYS>M086NEST`) → **200**
    chacune, toutes jusqu'à 2026-09.
  - Source d'origine, en secours : `https://data-api.ecb.europa.eu/service/data/ICP/M.DE+FR+IT.N.000000.4.ANR?startPeriod=2025-01&format=csvdata`
    → **200** une fois, puis délai dépassé (code 000) sur la même requête avec `startPeriod=2026-01` : source instable ce jour-là,
    donc non retenue comme source principale.
  - Millésimes en temps réel (robustesse) : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=UNRATE&vintage_date=2025-03-07`
    → **200** (colonne `UNRATE_20250307`). Le paramètre `vintage_date` de `fredgraph.csv` est en revanche ignoré (200, mais données
    courantes).
- **Méthode** : cible = glissement annuel de l'indice, prévu à un mois à partir des 24 mois précédents. Bras nommé : pays, variable,
  dates, valeurs vraies. Bras anonyme : « série A, mois 1 à 24 », valeurs décalées d'une constante tirée au hasard, prévision
  ramenée ensuite à l'échelle. Références : marche aléatoire et AR(1) à fenêtre croissante. Différence de différences modèle × période
  avec effets fixes de mois (les mois situés entre les deux coupures sont « avant » pour un modèle et « après » pour l'autre),
  erreurs groupées par mois. Graphique en temps d'événement autour de chaque coupure. **Garde contre la connaissance du futur** :
  c'est l'objet même du plan : l'écart nommé − anonyme n'est interprété comme valeur économique que sur les mois postérieurs à
  T_c + 3 mois ; la sonde de récitation vérifie la fenêtre ; le second modèle sert de placebo (la cassure doit se déplacer avec la
  date de coupure et non rester à une date de calendrier).
- **Ce qui serait nouveau** : plusieurs travaux affirment qu'un modèle prévoit l'inflation aussi bien ou mieux que les
  prévisionnistes, d'autres montrent que les modèles récitent le passé ; je ne connais pas de plan qui **sépare la valeur du
  contexte économique de la mémoire** par un croisement nommé/anonyme × avant/après coupure sur un panel de pays. Travaux proches :
  Faria-e-Castro et Leibovici, « Artificial Intelligence and Inflation Forecasts » (à vérifier) ; Lopez-Lira, Tang et Zhu, « The
  Memorization Problem: Can We Trust LLMs' Economic Forecasts? », arXiv 2504.14765 (titre vérifié sur arXiv) ; He, Lv, Manela et
  Wu, « Chronologically Consistent Large Language Models », arXiv 2502.21206 (titre vérifié sur arXiv) ; Faust et Wright (2013),
  « Forecasting inflation » (à vérifier) ; Atkeson et Ohanian (2001) pour la marche aléatoire comme référence (à vérifier).
- **Rôle de l'IA** : un agent construit les invites des deux bras et lance les appels ; un autre code l'AR(1) et le script de
  verdict. L'humain choisit les deux modèles, relève leurs dates de coupure, fixe les fenêtres et la condition de validité. Garde :
  les prévisions sont écrites dans un fichier scellé (sha256) avant que le script de verdict ne lise les valeurs réalisées ;
  l'agent prévisionniste ne reçoit jamais les mois cibles.
- **Coût et durée** : 11 × 36 × 2 × 2 = **1 584 appels** de prévision + 792 appels de sonde de récitation = **2 376 appels**
  d'environ 500 jetons en entrée et 40 en sortie : ≈ 1,2 M de jetons en entrée, soit **≈ 5 USD**. Calcul négligeable. 4 semaines.
- **Risques** : si le modèle ne mémorise pas l'inflation mensuelle de petits pays, δ sera faible même si le problème existe
  ailleurs ; 36 mois ne font que 36 grappes ; la période d'avant coupure peut être plus agitée que celle d'après, d'où la condition
  de validité et le second modèle ; sans économie dans la question, la fiche tomberait dans le simple banc d'essai : l'accent doit
  rester sur « que vaut le contexte pour prévoir l'inflation ».
- **Valeur si l'hypothèse meurt** : si δ ≈ 0, les rétro-tests d'inflation par modèle de langage sont moins contaminés qu'on le
  craint sur ce type de données, ce qui est publiable ; si le contexte aide encore après coupure, on a une estimation propre de
  la valeur du jugement économique à un mois.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai séparé, sur 11 pays de la zone euro et deux modèles, ce qui
  relève de la mémoire et ce qui relève de l'information économique dans les prévisions d'inflation à un mois d'un modèle de
  langage. » Graphique : gain du bras nommé sur le bras anonyme, mois par mois, en temps relatif à la date de coupure, une courbe
  par modèle. Métiers : recherche quantitative (tout métier qui fait des rétro-tests), prévision macroéconomique, banque centrale.

---

---

### F11 — Hausse des « frais de notaire » de 2025 : anticipation et recul des ventes, département par département

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

---

### F12 — L'instrument de protection de la transmission a-t-il coupé le lien entre surprises de la BCE et écarts souverains ?

- **Question** : depuis l'annonce de l'instrument de protection de la transmission (TPI) le 21 juillet 2022, une surprise restrictive de la BCE écarte-t-elle encore le rendement italien du rendement allemand ?
- **Hypothèse falsifiable** : avant le TPI, une surprise à la hausse du taux OIS à 2 ans élargit l'écart Italie-Allemagne à 10 ans dans la fenêtre de la réunion ; après le TPI, cette réponse est plus faible.
- **Prédiction chiffrée** : réunions de 2010-01 à 2022-06 (environ 110) : +0,15 à +0,50 point de base d'écart par point de base de surprise. Réunions de 2022-09 à 2025-10 (environ 26) : entre −0,10 et +0,10. Différence : −0,15 à −0,50. Pour l'écart France-Allemagne, réponses trois à cinq fois plus petites dans les deux périodes.
- **Test de mort** : MCO sur la feuille « Monetary Event Window » : Δ(IT10Y − DE10Y) = a + b·ΔOIS2Y + c·Après + d·(Après × ΔOIS2Y), la réunion du 2022-07-21 étant exclue. L'hypothèse meurt si b ≤ 0 (test unilatéral à 5 %, écarts-types robustes HC3) ou si la valeur p unilatérale de d < 0 par rééchantillonnage sauvage dépasse 0,10. Contrôle par dates factices : d doit se trouver dans les 10 % les plus bas de la distribution obtenue en plaçant la rupture à chaque réunion de 2012 à 2019. Hors échantillon : sur les réunions d'après TPI, l'erreur quadratique d'une réponse nulle doit être plus petite que celle du modèle estimé avant le TPI.
- **Données** : base EA-MPD `https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx` : HTTP 200, 315 réunions de 1999-01-07 à 2025-10-30, colonnes OIS_2Y, DE10Y, IT10Y, ES10Y, FR10Y, STOXX50, EURUSD (en-têtes lus, valeurs non regardées). Contrôle journalier : courbes de la BCE, tous émetteurs souverains `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_C.SV_C_YM.SR_10Y?format=csvdata` et émetteurs AAA `...G_N_A.SV_C_YM.SR_10Y` : HTTP 200. Rendements mensuels à long terme par pays `.../IRS/M.FR.L.L40.CI.0000.EUR.N.Z` : HTTP 200 ; FRED `IRLTLT01FRM156N` et `IRLTLT01DEM156N` : HTTP 200. Écarté : un dépôt GitHub de chocs « information contre politique » essayé de mémoire a répondu 404.
- **Méthode** : étude d'événement à haute fréquence avec rupture de régime. Variable expliquée : variation de l'écart à 10 ans dans la fenêtre de la réunion ; choc : variation du taux OIS à 2 ans. Séparation des surprises de politique et d'information par le signe du co-mouvement taux-actions, fixée d'avance comme analyse secondaire. Espagne et France en comparaison. Avant toute lecture des réponses, une simulation scellée donne la puissance du test pour d = −0,3 avec 26 réunions ; si elle est sous 50 %, l'Italie et l'Espagne sont empilées, décision prise avant de voir les écarts.
- **Ce qui serait nouveau** : les effets d'annonce des programmes d'achats (2010-2015) sont très étudiés ; je ne connais pas de test du changement de sensibilité des écarts aux surprises ordinaires de taux depuis le TPI avec la base publique mise à jour jusqu'en 2025. Travaux proches : Altavilla et coauteurs (2019, JME) (à vérifier) ; Leombroni, Vedolin, Venter et Whelan (2021, JFE), « Central bank communication and the yield curve » (à vérifier) ; Krishnamurthy, Nagel et Vissing-Jorgensen (2018, RFS) sur les achats d'obligations de la BCE (à vérifier) ; Altavilla, Giannone et Lenza (2016, IJCB) sur les annonces OMT (à vérifier) ; De Grauwe et Ji (2013) sur les crises auto-réalisatrices en zone euro (à vérifier) ; Jarociński et Karadi (2020, AEJ Macro) (à vérifier) ; travaux sur le TPI lui-même : référence incertaine.
- **Rôle de l'IA** : les agents écrivent le code, la simulation de puissance et les contrôles par dates factices. L'humain fixe les dates de rupture, la fenêtre et la règle d'empilement. Garde : l'agent de préparation ne reçoit que la colonne des surprises OIS ; les colonnes de rendements souverains sont lues pour la première fois par le script de verdict, après le scellement de la spécification et de la prédiction.
- **Coût et durée** : calcul négligeable ; 0 USD d'appels de modèle dans la chaîne de résultat ; agents de code : moins de 10 USD. 4 semaines.
- **Risques** : 26 réunions après le TPI, donc peu de puissance ; un intervalle large autour de zéro ne dit rien. La période d'après 2022 diffère aussi par le resserrement, la réduction du bilan, la souplesse des réinvestissements du programme pandémie et la situation budgétaire italienne : une baisse de d ne peut pas être attribuée au seul TPI. Le signe de b avant 2022 peut changer entre la crise de 2010-2012 et la période d'achats.
- **Valeur si l'hypothèse meurt** : si b ≤ 0, on documente que les surprises de taux n'ont jamais écarté les rendements en moyenne, contre le récit courant ; si d n'est pas distinguable de zéro, on publie la borne que 26 réunions permettent d'exclure et la puissance du test, ce qui est une réponse honnête à « le TPI a-t-il marché ? ».
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai testé, sur les réunions de la BCE de 2010 à 2025, si la réponse de l'écart Italie-Allemagne aux surprises de taux a changé après l'annonce du TPI, avec une spécification et une analyse de puissance scellées avant lecture des rendements. » Graphique unique : nuage de points surprise OIS à 2 ans contre variation de l'écart, deux couleurs et deux droites (avant et après juillet 2022). Métiers : stratégie taux et dette souveraine en banque d'investissement, gestion obligataire, banque centrale (opérations de marché), recherche économique.

---

---

### F13 — Les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel ?

- **Question** : les erreurs des projections d'inflation des services de la BCE et de l'Eurosystème pouvaient-elles être réduites, au moment de leur publication, par une règle simple fondée sur la révision de la projection précédente ?
- **Hypothèse falsifiable** : les projections sous-réagissent : une révision à la hausse est suivie d'une erreur de même signe (inflation réalisée au-dessus de la projection), et la correction estimée en temps réel réduit l'erreur hors échantillon.
- **Prédiction chiffrée** : inflation IPCH trimestrielle en glissement annuel, horizon de 4 trimestres. Coefficient de l'erreur sur la révision, millésimes de 2001 à 2019 : +0,2 à +0,6. Hors échantillon, millésimes 2020T1 et suivants : la projection corrigée a une erreur quadratique moyenne de 5 à 15 % plus basse que la projection publiée (rapport de 0,85 à 0,95). Aucun gain à l'horizon d'un trimestre (rapport entre 0,97 et 1,03).
- **Test de mort** : horizon principal fixé à 4 trimestres. Coefficient estimé de façon récursive avec les seules données disponibles à chaque millésime. Test de Diebold-Mariano avec correction de Harvey-Leybourne-Newbold, unilatéral, sur la différence des pertes quadratiques entre projection publiée et projection corrigée, millésimes 2020T1 jusqu'au dernier évaluable (environ 23). L'hypothèse meurt si le rapport des erreurs quadratiques est ≥ 0,95 ou si p > 0,10. Horizons secondaires (1, 2, 6, 8 trimestres) avec correction de Holm.
- **Données** : base des projections macroéconomiques de la BCE (MPD), un millésime par exercice. Liste des 6 206 séries `https://data-api.ecb.europa.eu/service/data/MPD?detail=serieskeysonly&format=csvdata` : HTTP 200. Inflation IPCH zone euro, `MPD.Q.U2.HIC.A.<MILLÉSIME>.0000` (111 millésimes trimestriels, codes W, S, G, A pour mars, juin, septembre, décembre) et `MPD.A.U2.HIC.A.<MILLÉSIME>.0000` (111 millésimes annuels, de A00 à G26) ; essai sur `MPD/A.U2.HIC.A.W21.0000` : HTTP 200. Hypothèse de prix du pétrole `MPD.A.F17.POU.U.<MILLÉSIME>.0000` (101 millésimes annuels) : 503 au premier essai, HTTP 200 au second. France : 49 séries `MPD.A.FR.HIC...`. Enquête auprès des prévisionnistes professionnels : `https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_individual_forecasts.zip` : HTTP 200, 111 fichiers de 1999Q1 à 2026Q3 ; la même enquête par l'API (`.../data/SPF`) a répondu 503, puis expiré, puis 200 : préférer l'archive. Brent `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU` : HTTP 200. Vu en testant : les valeurs historiques 1995-2001 d'un millésime et le dernier cours du Brent ; aucune erreur de projection calculée.
- **Méthode** : erreur = réalisation en temps réel (valeur du trimestre lue dans le millésime publié deux trimestres plus tard) moins projection. Régression de l'erreur sur la révision entre deux millésimes successifs pour la même date cible, écarts-types robustes à l'autocorrélation. Évaluation hors échantillon de la règle de correction récursive. Références de comparaison : marche aléatoire et moyenne de l'enquête auprès des prévisionnistes. Analyse secondaire : part de l'erreur expliquée par l'erreur sur l'hypothèse de prix du pétrole.
- **Ce qui serait nouveau** : les évaluations publiées s'arrêtent pour la plupart avant ou pendant la poussée de 2021-2023 et sont faites après coup ; ici, une règle de correction en temps réel est jugée sur la poussée, la désinflation et 2026. Le millésime de décembre 2026 sera publié pendant le projet : la prédiction de la règle pour ce millésime peut être scellée avant, à titre d'illustration (une observation, hors test de mort). Travaux proches : Coibion et Gorodnichenko (2015, AER), « Information rigidity and the expectations formation process » (à vérifier) ; Kontogeorgos et Lambrias (2019, document de travail de la BCE) sur vingt ans de projections (à vérifier) ; Chahad et coauteurs (2022, Bulletin économique de la BCE) sur les erreurs récentes (à vérifier) ; Granziera, Jalasjoki et Paloviita (2021, Banque de Finlande) sur le biais des projections selon l'état (à vérifier) ; Bordalo, Gennaioli, Ma et Shleifer (2020, AER) (à vérifier) ; Nordhaus (1987) sur l'efficience des révisions (à vérifier).
- **Rôle de l'IA** : les agents reconstruisent le panel millésime × date cible, écrivent la règle récursive et les tests. L'humain fixe l'horizon principal, la définition de la réalisation en temps réel et la fenêtre hors échantillon. Garde : l'agent d'estimation reçoit les millésimes jusqu'à 2019T4 seulement et livre un code de règle figé (sha256) ; le script de verdict, écrit à part, applique ce code aux millésimes suivants. Aucun agent ne retouche la règle après avoir vu 2020 et après.
- **Coût et durée** : calcul négligeable ; 0 USD d'appels de modèle dans la chaîne de résultat ; agents de code : moins de 10 USD. 5 semaines (le montage du panel de millésimes prend la moitié du temps).
- **Risques** : environ 23 millésimes hors échantillon et des erreurs autocorrélées : la puissance est limitée. La période 2021-2022 domine la perte quadratique ; le résultat sans ces deux années doit être montré. Les projections sont conditionnelles à des hypothèses techniques (pétrole, taux) : une partie de l'erreur n'est pas une erreur de jugement. La couverture trimestrielle des premiers millésimes est à vérifier.
- **Valeur si l'hypothèse meurt** : on écrit que les projections de la BCE ne laissaient pas de gain exploitable par cette règle, même pendant la poussée d'inflation, et on publie la décomposition des erreurs entre hypothèse pétrolière et reste. C'est un résultat net en faveur de l'efficience des projections.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai reconstitué 111 millésimes des projections d'inflation de la BCE et testé hors échantillon, par un test de Diebold-Mariano, si une correction en temps réel fondée sur les révisions réduisait leurs erreurs depuis 2020. » Graphique unique : inflation réalisée en trait plein et, en éventail, la trajectoire projetée à chaque millésime, projections corrigées en pointillé. Métiers : banque centrale (prévision), recherche économique en banque ou en gestion d'actifs, institut de conjoncture, conseil économique.

---

---

### F14 — Ménages synthétiques et prix de l'essence : une expérience par vignettes

- **Question** : des ménages simulés par un modèle de langage révisent-ils leur anticipation d'inflation à un an, après une hausse
  du prix de l'essence, avec la même ampleur que les ménages de l'enquête du Michigan ?
- **Hypothèse falsifiable** : la révision des ménages synthétiques est positive, propre à l'essence (plus forte que pour un prix
  placebo hors panier), et du même ordre que l'élasticité observée dans l'enquête, avec une tendance à l'exagérer (rapport
  synthétique / réel supérieur à 1).
- **Prédiction chiffrée** : élasticité réelle b_réel ≈ +0,02 point d'anticipation pour +1 % de prix de l'essence dans le mois
  (plage 0,01 à 0,04) ; élasticité synthétique nette (essence moins placebo) entre +0,02 et +0,06 ; rapport R = b_synth / b_réel
  entre 1 et 3, valeur centrale 2. Écart d'anticipation « revenu < 50 k$ » moins « revenu > 100 k$ » positif chez les synthétiques,
  entre +0,5 et +2 points, contre environ +0,5 point dans l'enquête de la Fed de New York (ordre de grandeur de mémoire, à calculer).
- **Test de mort** : calculé par un code séparé sur les fichiers bruts. L'idée meurt si l'un des trois cas se produit :
  (a) l'intervalle de confiance à 95 % de (b_essence − b_placebo), erreurs groupées par répondant synthétique, contient 0 ou est
  négatif ; (b) R estimé sort de [1/3 ; 3] ; (c) l'écart par revenu chez les synthétiques est de signe opposé à l'écart moyen de
  l'enquête de la Fed de New York sur juin 2013 – T_c. Échantillon : 400 répondants synthétiques × 3 vignettes ; régression réelle
  sur 1990-10 à T_c (environ 415 mois).
- **Données** :
  - Anticipation médiane à un an, Michigan : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=MICH` → **200** (1978-01 à 2026-09).
  - Même série à la source : `https://www.sca.isr.umich.edu/files/tbmpx1px5.csv` → **200** (colonnes Month, YYYY, PX_MD, PX5_MD ; jusqu'à octobre 2026).
  - Prix de l'essence ordinaire, mensuel : `...fredgraph.csv?id=GASREGM` → **200** (1990-09 à 2026-10). Indice des prix : `...id=CPIAUCSL` → **200**.
  - Enquête de la Fed de New York, anticipations par âge, diplôme, revenu, région :
    `https://www.newyorkfed.org/medialibrary/interactives/sce/sce/downloads/data/frbny-sce-data.xlsx` → **200** (1,27 Mo ; feuille
    « Inflation expectations Demo », 2013-06 à 2026-10).
  - Tableaux démographiques du Michigan (`https://data.sca.isr.umich.edu/data-archive/mine.php`) → **200** mais c'est un formulaire :
    non retenu, la ventilation vient de la Fed de New York.
- **Méthode** : (1) Régression réelle : ΔMICH_t sur 100·Δln(GASREGM_t) et la variation retardée de l'inflation sur 12 mois, MCO,
  erreurs de Newey-West. (2) Expérience : 400 personas tirés dans 54 cellules (âge × diplôme × revenu × sexe) répondent à la question
  de l'enquête sur un scénario de base, puis à trois vignettes où l'on tire au hasard une dose (−20 % à +30 %) pour l'essence,
  l'alimentation et un bien hors panier (placebo qui mesure la complaisance du modèle envers tout chiffre qu'on lui montre).
  (3) MCO de la révision sur les trois doses avec effet fixe de répondant ; comparaison de b_essence − b_placebo avec b_réel par
  bootstrap. (4) En complément descriptif : les mêmes personas reçoivent les vraies conditions de chaque mois de la fenêtre propre.
  **Garde contre la connaissance du futur** : les vignettes sont fictives, sans année ni niveau de prix réel, donc aucune valeur
  mémorisée ne peut y répondre ; le complément (4) ne porte que sur des mois postérieurs à T_c + 3 mois.
- **Ce qui serait nouveau** : les travaux que je connais comparent des niveaux moyens d'anticipations simulées à ceux des enquêtes ;
  ici on compare une **réponse causale** (dose-réponse randomisée) à une élasticité observée, avec un bras placebo pour l'effet de
  complaisance. Travaux proches : Horton, Filippas et Manning, « Large Language Models as Simulated Economic Agents », arXiv
  2301.07543 (titre vérifié sur arXiv) ; Bybee, « Surveying Generative AI's Economic Expectations », arXiv 2305.02823 (titre vérifié
  sur arXiv) ; Iadisernia et Camassa, « Prompting for Policy: Forecasting Macroeconomic Scenarios with Synthetic LLM Personas »,
  arXiv 2511.02458 (titre vérifié sur arXiv) ; Coibion et Gorodnichenko (2015) sur le pétrole et les anticipations des ménages
  (à vérifier) ; Binder (2018), « Inflation expectations and the price at the pump » (à vérifier) ; D'Acunto, Malmendier, Ospina
  et Weber sur les prix d'épicerie (à vérifier) ; une étude expérimentale de Zarifhonarvar sur les anticipations d'inflation de
  modèles de langage (référence incertaine).
- **Rôle de l'IA** : un agent écrit le générateur de vignettes et lance les appels ; un second agent écrit la régression réelle
  sans voir les réponses synthétiques. L'humain fixe les doses, les cellules, la bande [1/3 ; 3] et le texte exact de la question.
  Garde : prédiction et seuils scellés (sha256) avant tout appel ; le verdict sort d'un script figé qui lit les réponses brutes et
  les CSV ; l'agent qui a produit les réponses n'a ni les séries réelles ni le script de verdict.
- **Coût et durée** : 400 bases + 1 200 vignettes + 1 400 appels « conditions réelles » (100 personas × 14 mois) = **3 000 appels**
  d'environ 500 jetons en entrée et 60 en sortie, soit environ 1,5 M de jetons en entrée et 0,2 M en sortie : **≈ 8 USD**.
  Calcul négligeable. 4 semaines.
- **Risques** : la régression réelle est observationnelle (l'essence bouge avec d'autres nouvelles) alors que la vignette est
  « toutes choses égales » : les deux élasticités ne mesurent pas exactement le même objet. Le modèle a lu la littérature et peut
  réciter le fait stylisé plutôt que le simuler. Le résultat peut dépendre fortement de la formulation du prompt (à mesurer avec
  deux formulations figées d'avance).
- **Valeur si l'hypothèse meurt** : une mesure propre de l'écart entre répondants synthétiques et réels sur une réponse causale,
  avec l'effet de complaisance chiffré par le placebo ; c'est une mise en garde utilisable contre le remplacement d'enquêtes par
  des simulations.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai mesuré, par une expérience randomisée sur 400 répondants
  simulés, la réaction des anticipations d'inflation au prix de l'essence et je l'ai comparée à l'élasticité estimée sur l'enquête
  du Michigan. » Graphique : courbes dose-réponse (essence, alimentation, placebo) avec, superposée, la droite de l'élasticité
  réelle et son intervalle. Métiers : recherche économique en banque centrale, études macroéconomiques, conseil économique.

---

---

### F15 — Le choc d'énergie passe-t-il dans l'inflation sous-jacente plus que proportionnellement ?

- **Question** : à exposition donnée, la hausse des prix de l'énergie de 2021-2022 s'est-elle transmise aux prix hors énergie et alimentation des pays européens plus fortement que ne le prévoyait la relation estimée de 2000 à 2019 ?
- **Hypothèse falsifiable** : la transmission est non linéaire : par unité d'exposition, la réponse de l'inflation sous-jacente en 2021-2023 est au moins deux fois celle que prédit le coefficient estimé avant 2020.
- **Prédiction chiffrée** : de 2000 à 2019, un choc qui ajoute mécaniquement 1 point à l'inflation totale par l'énergie (poids de l'énergie × hausse du prix commun) relève l'indice sous-jacent de 0,05 à 0,20 point après 12 à 18 mois. En 2021-2023, la pente entre pays vaut 0,2 à 0,5, soit un rapport de 2 à 4. Corrélation de rang entre l'inflation sous-jacente cumulée prédite et réalisée par pays : 0,4 à 0,7.
- **Test de mort** : coupe de 27 pays de l'UE, de 2021-01 à 2023-06, variables centrées sur la moyenne des pays. (1) Corrélation de rang de Spearman entre réalisé et prédit (coefficients de 2000-2019) : si elle est inférieure à 0,32 (seuil unilatéral à 5 % pour 27 pays), le dispositif est vide et l'idée meurt. (2) Rapport entre la pente de 2021-2023 et le coefficient d'avant 2020 : si la borne basse de l'intervalle à 90 % (rééchantillonnage par pays, incertitude du coefficient d'avant 2020 comprise) est ≤ 1, ou si l'estimation ponctuelle sans les trois pays baltes est ≤ 1, l'hypothèse de non-linéarité meurt.
- **Données** : Eurostat, format SDMX-CSV. Indices IPCH mensuels `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_midx/M.I15.TOT_X_NRG_FOOD.<PAYS>?format=SDMX-CSV` (sous-jacent) et `...M.I15.NRG.<PAYS>` (énergie) : HTTP 200, depuis 1996-01, série figée à 2025-12. Poids annuels `.../prc_hicp_inw/A.NRG.<PAYS>` : HTTP 200, 44 zones dont les 27 pays de l'UE pour 2019. Nouvelle base qui remplace les précédentes depuis 2026, `.../statistics/1.0/data/prc_hicp_minr?format=JSON&geo=FR` : HTTP 200, mise à jour le 2026-11-04. Prix du gaz en Europe `https://fred.stlouisfed.org/graph/fredgraph.csv?id=PNGASEUUSDM` : HTTP 200, depuis 1992 ; Brent `...id=DCOILBRENTEU` : HTTP 200 ; dollar par euro `...id=DEXUSEU` et `https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A` : HTTP 200. Écarté : les séries IPCH de l'API de la BCE (`ICP`), énergie en 404 et sous-jacent arrêté à 2025-11. Vu en testant : quelques valeurs isolées (poids de l'énergie 2019 de deux pays, deux taux annuels français de fin 2025, dernier cours du Brent à 107 USD au 2026-11-03) ; aucune coupe de pays.
- **Méthode** : exposition = poids de l'énergie dans l'IPCH du pays l'année précédente × variation sur 12 mois d'un prix commun de l'énergie en euros (moitié Brent, moitié gaz, pondération fixée d'avance). Projections locales en panel de l'indice sous-jacent sur l'exposition, avec effets fixes pays et effets fixes de date : la date absorbe tout choc commun, et l'effet est identifié par la différence d'exposition entre pays. Première étape montrée : l'exposition prédit la contribution effective de l'énergie à l'inflation du pays. Estimation de 2000 à 2019, puis prévision de la coupe 2021-2023.
- **Ce qui serait nouveau** : la non-linéarité est discutée surtout sur séries agrégées ou sur prix individuels ; ici elle est testée par un dispositif d'exposition entre pays, avec des coefficients figés avant 2020 et une prévision scellée de la coupe. Si 2026 contient un nouveau choc, la nouvelle base Eurostat permet un second test scellé, cette fois vraiment prospectif. Travaux proches : Cavallo, Lippi et Miyahara (2024), « Large shocks travel fast » (à vérifier) ; Benigno et Eggertsson (2023), « It's baaack » (à vérifier) ; Bernanke et Blanchard (2023) et son application à la zone euro (à vérifier) ; Baba, Duval, Lan et Topalova (2023, FMI) sur l'inflation en Europe (à vérifier) ; Corsello et Tagliabracci (2023, Banque d'Italie) sur la transmission de l'énergie (à vérifier) ; Borusyak, Hull et Jaravel (2022, REStud) et Goldsmith-Pinkham, Sorkin et Swift (2020, AER) pour la méthode d'exposition (à vérifier).
- **Rôle de l'IA** : les agents assemblent le panel, écrivent les projections locales et la prévision de coupe. L'humain fixe la pondération du prix commun, la liste des pays, la fenêtre 2021-2023 et le traitement des pays baltes avant toute estimation. Garde : l'agent d'estimation ne reçoit que les données jusqu'à 2019-12 ; les coefficients et la prévision par pays sont scellés (sha256) ; un script de verdict séparé lit ensuite les indices de 2021-2023 dans le fichier brut.
- **Coût et durée** : calcul négligeable ; 0 USD d'appels de modèle dans la chaîne de résultat ; agents de code : moins de 10 USD. 5 semaines.
- **Risques** : 27 pays, c'est peu, et les pays baltes peuvent porter tout le résultat. Les pays les plus exposés sont aussi les plus proches de la guerre et ceux où les salaires ont le plus monté : l'exposition n'est pas tirée au hasard. Les boucliers tarifaires (France, Espagne) coupent le lien entre prix commun et prix payé ; c'est pourquoi la première étape est montrée. Hors zone euro, le change s'ajoute. Le sujet est très travaillé depuis 2022 : l'apport tient au dispositif scellé, pas au thème.
- **Valeur si l'hypothèse meurt** : si le rapport n'est pas distinguable de 1, on écrit qu'entre pays la relation d'avant 2020 suffit à expliquer 2021-2023, donc que la poussée sous-jacente tient à la taille du choc et non à un changement de mécanisme ; si le rang n'est pas prédit, on écrit que l'exposition énergétique n'ordonne pas les pays, ce qui renvoie vers la demande et les salaires.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai estimé sur 27 pays de l'UE la transmission des prix de l'énergie à l'inflation sous-jacente par un dispositif d'exposition, puis comparé la coupe 2021-2023 à une prévision scellée issue des coefficients de 2000-2019. » Graphique unique : nuage de 27 points, inflation sous-jacente cumulée prédite en abscisse et réalisée en ordonnée, avec la diagonale et la droite ajustée. Métiers : recherche économique et stratégie inflation en banque, banque centrale, gestion d'actifs (obligations indexées), conseil en énergie et en économie.

---

### F16 — Jours d'annonces macroéconomiques : la prime de risque y est-elle toujours gagnée après la publication du résultat ?

- **Question** : la relation entre bêta et rendement, forte les jours d'annonces macroéconomiques et nulle les autres jours, a-t-elle persisté depuis 2012, comme on l'attend d'une prime de risque et non d'une anomalie ?
- **Hypothèse falsifiable** : sur 2012-2026, la pente de la droite de marché (rendement en fonction du bêta) est plus forte les jours de publication de l'inflation, de l'emploi et des décisions de la Réserve fédérale que les autres jours.
- **Prédiction chiffrée** : différence de pente (jours d'annonce − autres jours) positive, de +4 à +8 points de base par unité de bêta et par jour ; rendement excédentaire du marché de 6 à 10 points de base les jours d'annonce contre 2 à 4 les autres jours. Ordres de grandeur d'origine, de mémoire : environ 10 points de base de pente les jours d'annonce, environ 11 contre 1 pour le marché — à vérifier.
- **Test de mort** : fenêtre de jugement **2012-01-03 à 2026-09-30** (postérieure à l'échantillon d'origine), environ 460 jours d'annonce et 3 250 autres jours. Régressions transversales quotidiennes de Fama-MacBeth sur 99 portefeuilles ; statistique = moyenne des pentes les jours d'annonce moins moyenne les autres jours. **L'idée meurt si le t unilatéral est < 1,645.** Verdict d'érosion écrit d'avance : si la borne haute de l'intervalle à 90 % est < 5 points de base (la moitié de l'effet d'origine), on conclut que l'effet a diminué même s'il reste positif. Puissance annoncée : erreur type attendue d'environ 3 points de base sur la différence de pente, 5 sur le rendement du marché.
- **Données** :
  - Portefeuilles quotidiens Ken French : 49 secteurs `.../ftp/49_Industry_Portfolios_daily_CSV.zip` → **200** ; 25 taille × valeur `.../ftp/25_Portfolios_5x5_Daily_CSV.zip` → **200** ; 25 taille × momentum `.../ftp/25_Portfolios_ME_Prior_12_2_Daily_CSV.zip` → **200** ; marché et taux sans risque `.../ftp/F-F_Research_Data_Factors_daily_CSV.zip` → **200**. Le fichier quotidien trié par bêta `.../ftp/Portfolios_Formed_on_BETA_Daily_CSV.zip` → **404** : les bêtas sont donc estimés par l'étudiant.
  - Dates de publication : millésimes ALFRED de l'indice des prix `https://alfred.stlouisfed.org/series/downloaddata?seid=CPIAUCSL` → **200** (673 dates depuis 1972, dernière 2026-11-10) et de l'emploi `...seid=PAYEMS` → **200** (863 dates depuis 1955, dernière 2026-11-06) ; contrôle d'un millésime : `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=CPIAUCSL&vintage_date=2015-03-24` → **200**.
  - Réunions de la Réserve fédérale : `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` → **200** et pages historiques `.../monetarypolicy/fomchistorical2015.htm` → **200**.
  - Sources écartées : calendrier du Bureau of Labor Statistics `https://www.bls.gov/schedule/news_release/cpi.htm` → **403** ; `https://alfred.stlouisfed.org/release/downloaddates?rid=10` → 200 mais formulaire sans données.
- **Méthode** : calendrier des jours d'annonce construit à partir des millésimes (premier millésime de chaque mois) et des réunions programmées. Bêtas glissants sur 252 jours, estimés jusqu'à la veille. Chaque jour, régression transversale du rendement excédentaire sur le bêta ; moyennes des pentes par type de jour, test de différence. Le plan (portefeuilles, fenêtre des bêtas, calendrier) est d'abord reproduit sur 1964-2011 et scellé, puis appliqué tel quel à 2012-2026. Robustesse : chaque type d'annonce séparément ; facteurs Europe quotidiens.
- **Ce qui serait nouveau** : un test hors échantillon, sur près de quinze ans postérieurs à l'échantillon d'origine, d'un des résultats les plus cités sur la prime de risque, lu comme test discriminant : une prime de risque doit persister, une anomalie fouillée doit s'éroder (voir F01). Travaux proches : Savor et Wilson (2013, 2014), prime des jours d'annonce et droite de marché — à vérifier ; Lucca et Moench (2015), dérive avant les réunions de la Réserve fédérale — à vérifier ; Kurov et coauteurs, disparition de cette dérive — référence incertaine ; Ai et Bansal (2018), théorie de la prime d'annonce — à vérifier. Une mise à jour récente peut exister : référence incertaine.
- **Rôle de l'IA** : les agents extraient les dates des pages ALFRED et de la Réserve fédérale, construisent les bêtas et les régressions quotidiennes ; un agent distinct vérifie le calendrier contre un échantillon de dates contrôlées à la main par l'humain. L'humain valide le calendrier et scelle le plan après la reproduction 1964-2011. Garde : l'agent qui construit le plan ne voit que les rendements jusqu'à 2011-12 ; le code de verdict, séparé, lit 2012-2026 une seule fois et écrit le verdict dans un fichier horodaté.
- **Coût et durée** : environ 15 000 régressions transversales de 99 points, quelques secondes. Agents : 5 à 10 USD. 4 à 5 semaines.
- **Risques** : les millésimes ALFRED contiennent aussi des révisions, d'où un calendrier à nettoyer ; la puissance est limite pour le rendement du marché (effet attendu d'environ deux erreurs types) ; sans portefeuilles triés par bêta, la dispersion des bêtas est plus faible que dans l'article d'origine ; une étude récente a pu déjà faire ce test.
- **Valeur si l'hypothèse meurt** : un résultat phare présenté comme une prime de risque qui ne survit pas hors échantillon rejoint le constat d'érosion des anomalies et interroge sa lecture par le risque ; on publie l'intervalle de confiance et la comparaison avec l'effet d'origine.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai testé sur 2012-2026, selon un plan reproduit puis scellé sur 1964-2011, si la relation entre bêta et rendement reste plus forte les jours d'annonces macroéconomiques, par régressions de Fama-MacBeth quotidiennes sur 99 portefeuilles. » Graphique unique : rendement moyen en fonction du bêta pour les 99 portefeuilles, deux nuages et deux droites (jours d'annonce, autres jours), période d'origine à gauche et 2012-2026 à droite. Métiers : recherche quantitative, stratégie actions, gestion d'actifs, banque centrale.

---

### F17 — Le modèle lit-il la BCE, ou se souvient-il de la suite ?

- **Question** : quand un modèle de langage « explique » le sens de la réaction des taux à une conférence de presse de la BCE, quelle part vient du texte qu'on lui donne et quelle part vient de sa mémoire de ce qui s'est passé ce jour-là ?
- **Hypothèse falsifiable** : avec la seule date de la réunion et sans aucun texte, le modèle devine le signe de la surprise de taux mieux que le hasard pour les réunions antérieures à sa date de coupure, et pas mieux que le hasard pour les réunions postérieures.
- **Prédiction chiffrée** : bras « date seule », réunions d'avant coupure dont la surprise dépasse 2 points de base en valeur absolue : 56 à 62 % de bons signes (hasard : 50 %), et au moins 70 % sur le cinquième des plus grosses surprises. Après coupure : 50 % au bruit près. Bras « texte masqué » (dates, années, noms et niveaux chiffrés retirés) : 58 à 64 %, sans différence avant et après coupure. Écart « texte daté » moins « texte masqué » : +2 à +6 points avant coupure, nul après.
- **Test de mort** : test binomial unilatéral du taux de bons signes du bras « date seule » contre 50 %, par modèle, sur les réunions de 2002-01 à (coupure − 6 mois) dont |ΔOIS 2 ans| ≥ 2 pb dans la feuille « Press Conference Window ». Seuil p < 0,0125 (Bonferroni sur 4 modèles) et taux ≥ 55 % pour au moins un modèle. Si aucun modèle ne passe, l'hypothèse de fuite meurt. Contre-épreuve hors échantillon : sur les réunions postérieures à la coupure (jugées par la variation du jour du taux AAA à 2 ans, série YC), un taux de bons signes du bras « date seule » supérieur à 65 % tue aussi l'idée, parce que le bras ne mesurerait alors pas la mémoire. Le substitut journalier n'est admis que s'il a le même signe que la surprise intrajournalière dans au moins 75 % des réunions communes ; sinon la contre-épreuve est déclarée non concluante.
- **Données** :
  - Déclarations de politique monétaire de la BCE, index par année `https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/<AAAA>/html/index_include.en.html` : HTTP 200 pour 1999, 2003, 2024 et 2026 (7 déclarations listées pour 2026, la dernière du 2026-10-29). Page d'une déclaration (`.../2024/html/ecb.is241212~ce143b3bc8.en.html`) : HTTP 200.
  - Surprises intrajournalières, base EA-MPD `https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx` : HTTP 200, 377 Ko, trois feuilles (communiqué, conférence de presse, événement entier), 315 réunions du 1999-01-07 au 2025-10-30, colonnes OIS de 1 semaine à 20 ans, rendements DE, FR, IT, ES, STOXX50, EURUSD.
  - Taux AAA à 2 ans, journalier `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y?format=csvdata` : HTTP 200. Taux de la facilité de dépôt `.../FM/D.U2.EUR.4F.KR.DFR.LEV` : HTTP 200.
  - Extension États-Unis (facultative) : communiqués du FOMC `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` (HTTP 200, 95 liens de communiqués) et `.../fomchistorical2015.htm` (HTTP 200) ; `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2` (HTTP 200) ; surprises de la Fed de San Francisco `https://www.frbsf.org/wp-content/uploads/monetary-policy-surprises-data.xlsx` (HTTP 200, contenu non ouvert).
  - Extension discours (facultative) : `https://www.ecb.europa.eu/press/key/shared/data/all_ECB_speeches.csv` : HTTP 200, 58,7 Mo, 3 086 discours du 1997-02-07 au 2026-10-30.
- **Méthode** : pour chaque réunion et chaque modèle, trois questions fermées (réponse « hausse » ou « baisse » des taux à 2 ans pendant la conférence, plus une probabilité) : (D) la date seule ; (T) le texte masqué ; (T+D) le texte daté. Une quatrième question demande de deviner l'année du texte masqué, pour mesurer ce que le masquage laisse passer. Quatre modèles de dates de coupure différentes, deux répétitions par appel. Comparaisons appariées (McNemar) entre bras ; régression du score de Brier sur une indicatrice « réunion antérieure à la coupure du modèle » avec effets fixes réunion et modèle, écarts-types groupés par réunion. Référence sans mémoire : un compte de mots « restrictifs » moins « accommodants » fixé d'avance.
- **Ce qui serait nouveau** : la fuite du futur est documentée pour les actions et les titres de presse, mais je ne connais pas de mesure faite sur le texte d'une banque centrale avec un bras « date seule » et des surprises intrajournalières publiques. Le produit utile est une règle d'emploi : sur quelles réunions un score de ton produit par un modèle est-il propre ? Travaux proches : Sarkar et Vafa (2024), « Lookahead bias in pretrained language models » (à vérifier) ; Glasserman et Lin (2023), « Assessing look-ahead bias in stock return predictions generated by GPT sentiment analysis » (à vérifier) ; Hansen et Kazinnik (2023), « Can ChatGPT decipher Fedspeak? » (à vérifier) ; Altavilla, Brugnolini, Gürkaynak, Motto et Ragusa (2019, JME), « Measuring euro area monetary policy » (à vérifier) ; Ludwig, Mullainathan et Rambachan (2025), « Large language models: an applied econometric framework » (à vérifier) ; des modèles « chronologiquement cohérents » ont été proposés vers 2025 (référence incertaine).
- **Rôle de l'IA** : le modèle est ici l'objet mesuré. Les agents écrivent le code de collecte, de masquage et d'interrogation. L'humain choisit les quatre modèles, relit 30 textes masqués tirés au hasard et fixe les seuils. Garde : l'agent qui interroge les modèles ne reçoit jamais le fichier EA-MPD ni les séries de taux ; les réponses sont figées dans un fichier dont le sha256 est publié avant le téléchargement des surprises ; le verdict est un script séparé qui lit le fichier de réponses et le fichier brut. Aucun modèle ne note une réponse de modèle.
- **Coût et durée** : calcul négligeable. Environ 275 déclarations de 2 500 jetons, deux bras avec texte, deux répétitions, soit 3,4 millions de jetons d'entrée par modèle. Aux tarifs lus le 2026-11-12 dans la documentation de l'API (par million de jetons, entrée/sortie : claude-haiku-4-5 1/5 USD, claude-sonnet-4-6 3/15, claude-sonnet-5-5 2/10, claude-haiku-5-5 0,10/0,50 ; traitement par lots à moitié prix) : environ 15 USD par lots, plafond fixé à 30 USD. Les dates de coupure officielles sont à lire dans la documentation de chaque modèle (à vérifier ; je ne les cite pas de mémoire). 5 semaines.
- **Risques** : après coupure il reste peu de réunions (8 par an), donc la contre-épreuve hors échantillon a peu de puissance ; le test principal est le bras « date seule » avant coupure. Les modèles récents n'acceptent plus de réglage de température : la répétition remplace le réglage. Un modèle peut refuser de répondre sans texte : le taux de refus est rapporté et compté comme une erreur. Un modèle ancien peut être retiré de l'API pendant le projet.
- **Valeur si l'hypothèse meurt** : si le bras « date seule » reste à 50 %, on écrit que la mémoire de ces modèles ne porte pas sur le signe des surprises de la BCE, ce qui autorise leur emploi comme instrument de mesure sur tout l'historique, et on publie la précision du bras « texte masqué » face au compte de mots.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai mesuré, sur 27 ans de conférences de presse de la BCE et quatre modèles de langage, la part de la réussite d'un modèle qui vient de sa mémoire du futur plutôt que du texte, avec des réponses scellées avant lecture des surprises de marché. » Graphique unique : taux de bons signes par année de réunion pour les trois bras, avec une ligne verticale à la date de coupure de chaque modèle. Métiers : recherche quantitative et gestion d'actifs (signaux textuels sans biais d'anticipation), banque centrale (analyse de la communication), recherche économique.

---

---

### F18 — Le ton des communiqués du FOMC, lu avec et sans date

- **Question** : le ton du communiqué du FOMC, noté par un modèle de langage, explique-t-il la variation du taux à 2 ans le jour de
  l'annonce au-delà de la décision de taux, et cette relation tient-elle quand le modèle ne peut pas connaître la suite ?
- **Hypothèse falsifiable** : un communiqué noté plus restrictif que le précédent s'accompagne d'une hausse du taux à 2 ans le
  jour même, à décision de taux donnée ; la note tirée du texte anonymisé ne prédit pas la dérive des 20 jours suivants, alors que
  la note tirée du texte daté la prédit davantage (fuite d'information future).
- **Prédiction chiffrée** : un point de ton (échelle −2 à +2) ↔ +2 à +5 points de base sur le 2 ans le jour J, gain de R² de 0,05
  à 0,15 par rapport à la seule décision. Régression placebo sur la dérive de J+1 à J+20 : coefficient du bras anonymisé entre
  −2 et +2 pb avec |t| < 2 ; coefficient du bras daté supérieur de 0 à 5 pb à celui du bras anonymisé avant T_c, et écart nul
  (|t| < 2) après T_c.
- **Test de mort** : sur le bras anonymisé, environ 220 communiqués (mai 1999 – octobre 2026) : l'idée meurt si le t de Student
  robuste du coefficient de ton est < 2 ; ou si, dans la régression placebo (dérive J+1 à J+20), le coefficient du bras anonymisé a
  |t| > 2 (la mesure est alors contaminée ou capte autre chose que l'annonce) ; ou si, sur les réunions de la fenêtre propre
  (environ 9, d'octobre 2025 à octobre 2026), le coefficient est de signe opposé à celui d'avant T_c (rapporté avec sa valeur p de
  permutation exacte).
- **Données** :
  - Communiqués récents : `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` → **200** (liens jusqu'à
    `monetary20261028a.htm`) ; exemple `https://www.federalreserve.gov/newsevents/pressreleases/monetary20240131a.htm` → **200** ;
    `.../monetary20261028a.htm` → **200**.
  - Communiqués anciens : `https://www.federalreserve.gov/monetarypolicy/fomchistorical2015.htm` → **200** ;
    `.../fomchistorical2003.htm` → **200** ; exemple ancien `https://www.federalreserve.gov/boarddocs/press/monetary/2003/20030129/default.htm` → **200**.
  - Taux à 2 ans quotidien : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2` → **200** (jusqu'au 2026-11-09).
  - Cible des fonds fédéraux : `...id=DFEDTAR` → **200** (1982 – 2008-12-15) ; `...id=DFEDTARU` → **200** ; `...id=DFEDTARL` → **200**.
  - Attention : FRED a renvoyé une erreur HTTP/2 (code 000) quand curl se présentait avec un agent utilisateur de navigateur ;
    avec l'agent par défaut, 200.
- **Méthode** : étude d'événement quotidienne. Pour chaque réunion, le modèle reçoit le communiqué et le précédent et rend une
  note entière de −2 à +2, trois fois (pour mesurer son bruit). Deux bras : texte daté ; texte anonymisé par un script déterministe
  (dates, noms, niveaux de taux et chiffres remplacés par des marques, la décision réduite à « inchangé / hausse / baisse »).
  MCO : ΔDGS2_J = a + b·Ton + c·ΔCible + d·ΔDGS2_{J−1} + e, erreurs robustes. Régression placebo : même membre de droite, variable
  expliquée = DGS2_{J+20} − DGS2_J. **Garde contre la connaissance du futur** : (i) bras anonymisé, avec un test de datation (on
  demande au modèle l'année du texte anonymisé ; on rapporte l'erreur absolue médiane) ; (ii) régression placebo sur la dérive
  future, qui doit être nulle ; (iii) sous-échantillon postérieur à T_c + 3 mois.
- **Ce qui serait nouveau** : le ton des communiqués noté par un modèle a déjà été étudié ; ce qui manque, à ma connaissance, est
  une **mesure chiffrée de la fuite d'information future** dans ce cadre monétaire, par l'écart daté − anonymisé d'une régression
  placebo. Travaux proches : Hansen et Kazinnik, « Can ChatGPT Decipher Fedspeak? » (à vérifier) ; Peskoff, Visokay, Schulhoff et
  Wachspress, « GPT Deciphering Fedspeak », arXiv 2407.19110 (titre vérifié sur arXiv) ; Glasserman et Lin, « Assessing Look-Ahead
  Bias in Stock Return Predictions Generated By GPT Sentiment Analysis », arXiv 2309.17322 (titre vérifié sur arXiv) ; Sarkar et
  Vafa, « Lookahead bias in pretrained language models » (à vérifier) ; Gürkaynak, Sack et Swanson (2005) sur les deux facteurs
  des annonces (à vérifier) ; Lucca et Trebbi (2009) sur la mesure automatique des communiqués (à vérifier).
- **Rôle de l'IA** : un agent collecte et anonymise les textes ; un autre lance la notation ; aucun des deux ne lit les séries de
  taux. L'humain fixe l'échelle, la fenêtre de 20 jours, les contrôles et les seuils. Garde : notes scellées (sha256) avant le
  téléchargement de DGS2 ; régressions et verdict par un script figé d'avance, exécuté par un rôle distinct.
- **Coût et durée** : 220 communiqués × 2 bras × 3 répétitions = 1 320 appels + 220 appels de datation = **1 540 appels**
  d'environ 2 500 jetons en entrée (deux communiqués) et 30 en sortie : ≈ 3,9 M de jetons en entrée, soit **≈ 12 à 13 USD**.
  5 semaines (la collecte des pages anciennes prend une semaine).
- **Risques** : données quotidiennes seulement (pas de fenêtre de 30 minutes, pas de contrats à terme sur fonds fédéraux gratuits),
  donc la surprise de taux est mal contrôlée et d'autres nouvelles du jour polluent ; les communiqués sont reconnaissables à leurs
  formules même anonymisés (le test de datation le dira) ; 9 réunions propres ne donnent qu'une vérification de signe.
- **Valeur si l'hypothèse meurt** : si le ton n'explique rien au-delà de la décision en données quotidiennes, c'est une borne
  utile sur ce qu'on peut tirer du texte sans données intrajournalières ; si le placebo échoue, on a une mesure directe de la
  contamination des études de ce type.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai mesuré l'effet du ton des communiqués du FOMC sur le taux à
  2 ans sur environ 220 réunions, et chiffré par une régression placebo la part due à la connaissance du futur par le modèle. »
  Graphique : quatre coefficients avec intervalles (jour J et dérive J+1…J+20, texte daté et anonymisé), avant et après T_c.
  Métiers : stratégie taux, recherche en banque centrale, gestion obligataire, recherche quantitative macro.

---

---

### F19 — Salaire minimum et emploi dans la restauration : multivers sur les paires de comtés frontaliers, 2014-2025

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

---

### F20 — Bêta des dépôts : les taux servis aux ménages baissent-ils plus vite qu'ils n'ont monté ?

- **Question** : dans les pays de la zone euro, la transmission du taux directeur aux taux des dépôts des ménages a-t-elle été plus forte pendant la baisse commencée en 2024 que pendant la hausse de 2022-2023 ?
- **Hypothèse falsifiable** : pour les dépôts à terme de moins d'un an des ménages (nouveaux contrats), la part de la variation du taux directeur transmise au taux servi est plus élevée à la baisse qu'à la hausse.
- **Prédiction chiffrée** : moyenne des pays, dépôts à terme ≤ 1 an : bêta à la hausse 0,60 à 0,75 ; bêta à la baisse 0,80 à 0,95 ; asymétrie de +0,10 à +0,25. Dépôts à vue : bêta à la hausse de 0,05 à 0,15. Hors échantillon : un modèle à correction d'erreur symétrique estimé jusqu'à 2023-09 surestime le taux des dépôts à terme de 15 à 40 points de base douze mois après la première baisse.
- **Test de mort** : deux conditions, toutes deux nécessaires. (1) Asymétrie par pays A = bêta(baisse) − bêta(hausse), chaque bêta étant la variation du taux bancaire entre le mois qui précède le premier mouvement et le troisième mois après le dernier, divisée par celle du taux de la facilité de dépôt ; les phases sont découpées mécaniquement à partir de la série DFR. Il faut A > 0 dans au moins 14 des 19 pays membres sur toute la fenêtre (test du signe, p ≈ 0,03) et une moyenne ≥ 0,05 dont l'intervalle à 90 % par rééchantillonnage des pays exclut 0. (2) Hors échantillon : erreur de prévision moyenne du modèle symétrique sur 2024-06 et après, à l'horizon 12 mois, négative avec t de Driscoll-Kraay < −1,65. Si l'une échoue, l'hypothèse meurt.
- **Données** : statistiques de taux d'intérêt bancaires de la BCE (MIR), mensuelles, par pays. `https://data-api.ecb.europa.eu/service/data/MIR/M.<PAYS>.B.L21.A.R.A.2250.EUR.N?format=csvdata` (dépôts à vue des ménages), `...L22.F.R.A.2250.EUR.N` (dépôts à terme ≤ 1 an, nouveaux contrats), `...A2C.A.R.A.2250.EUR.N` (crédits à l'habitat), `...A2A.A.R.A.2240.EUR.N` (crédits aux entreprises) : HTTP 200 pour chacune, 21 pays plus l'agrégat U2 présents (AT BE BG CY DE EE ES FI FR GR HR IE IT LT LU LV MT NL PT SI SK), série italienne à terme depuis 2000-01, dernières observations 2026-07. Taux de la facilité de dépôt `.../FM/D.U2.EUR.4F.KR.DFR.LEV` : HTTP 200. Euribor 3 mois `.../FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA` : HTTP 200 (jusqu'à 2026-10). €STR `.../EST/B.EU000A2X2A25.WT` : HTTP 200. Vu en testant : les trois dernières valeurs françaises (2026-07), une valeur italienne de 2000 et les derniers niveaux de l'Euribor et de l'€STR ; aucune trajectoire. La base d'indicateurs de structure bancaire (SSI) n'a pas répondu en 120 s : elle n'est pas utilisée.
- **Méthode** : panel pays × mois, 2003 à aujourd'hui. Projections locales du taux bancaire sur la variation de l'Euribor 3 mois, avec effets fixes pays et interaction « phase de baisse », écarts-types de Driscoll-Kraay. Bêtas de cycle par pays pour le graphique. Prévision scellée : modèle à correction d'erreur symétrique par pays, estimé sur un fichier tronqué à 2023-09, projeté sur la trajectoire réalisée du taux de marché. Rééchantillonnage par pays, car il y a peu de grappes.
- **Ce qui serait nouveau** : la rigidité à la hausse des taux de dépôts est connue ; le cycle complet hausse puis baisse à partir de taux négatifs n'est observable en entier que depuis peu, et la prévision scellée d'un modèle symétrique donne un test que la description du cycle ne donne pas. Travaux proches : Hannan et Berger (1991, AER), « The rigidity of prices: evidence from the banking industry » (à vérifier) ; Neumark et Sharpe (1992, QJE) (à vérifier) ; Driscoll et Judson (2013), « Sticky deposit rates » (à vérifier) ; Drechsler, Savov et Schnabl (2017, QJE), « The deposits channel of monetary policy » (à vérifier) ; de Bondt (2005), sur la transmission des taux en zone euro (à vérifier) ; Messer et Niepmann (2023, note de la Fed sur les dépôts en zone euro) (à vérifier) ; articles du Bulletin économique de la BCE de 2023-2025 sur ce sujet (référence incertaine).
- **Rôle de l'IA** : les agents téléchargent les séries, écrivent les projections locales et proposent des spécifications. L'humain fixe la règle de découpage des phases, la liste des pays et l'horizon avant toute estimation. Garde : l'agent d'estimation ne reçoit qu'un fichier tronqué à 2023-09 ; ses prévisions sont scellées (sha256) ; un script de verdict écrit à part lit ensuite le fichier brut complet. Aucun agent ne choisit après coup la phase ou l'horizon.
- **Coût et durée** : quelques secondes de calcul. Aucun appel de modèle dans la chaîne de résultat (0 USD) ; agents de code : moins de 10 USD. 4 semaines.
- **Risques** : le résultat peut déjà figurer dans une publication de la BCE (à vérifier avant de lancer). Le taux directeur est commun à tous les pays : l'asymétrie est un fait descriptif bien mesuré, pas un effet causal d'un choc exogène. La composition des nouveaux contrats change au cours du cycle. En France, l'épargne réglementée pèse sur les taux sans figurer dans ces séries. Si la BCE a de nouveau changé de direction en 2026, les phases se multiplient et il faut s'en tenir à la règle mécanique.
- **Valeur si l'hypothèse meurt** : une transmission symétrique est un résultat contre l'idée reçue du pouvoir de marché des banques sur les déposants ; on publie alors les bêtas par pays et par produit et l'erreur de prévision du modèle symétrique, utiles tels quels à une trésorerie bancaire.
- **Ce que ça dit au jury et aux recruteurs** : ligne de CV : « J'ai estimé pour 19 pays de la zone euro la transmission du taux directeur aux taux des dépôts des ménages à la hausse et à la baisse, et j'ai testé l'asymétrie avec une prévision scellée avant lecture des données de la phase de baisse. » Graphique unique : nuage de points, un point par pays, bêta à la hausse en abscisse et bêta à la baisse en ordonnée, avec la diagonale. Métiers : gestion actif-passif et trésorerie de banque, analyse des banques en banque d'investissement, banque centrale (transmission), conseil en risque de taux.

---

---
