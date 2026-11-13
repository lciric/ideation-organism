# K20-ZE — Préinscription : la sous-réaction du consensus grandit-elle avec la taille des nouvelles ? Réplication sur l'enquête de la BCE

Rédigé le 2026-11-13 par le rédacteur de préinscription de K20-ZE. Le rédacteur n'a lancé aucune analyse. Il n'a calculé
aucune erreur, aucune révision, aucune surprise, aucune moyenne de prévisions, aucune régression et aucune statistique sur
les prévisions comparées aux réalisations. Les seuls calculs faits sur les fichiers réels sont des **comptes** : présence
de cellules, nombre de répondants, formats, nombre de décimales, nombre de valeurs hors d'une plage. Les calculs de puissance
sont théoriques (loi normale) ou simulés sans aucune donnée de résultat (section 8).

**Pourquoi ce test.** K20 a posé la question sur l'enquête américaine de la Fed de Philadelphie et a trouvé un supplément de
pente proche de zéro. Son verdict est « non concluant » pour une raison de construction : un contrôle de schéma a échoué sur
une ligne qui n'entrait dans aucune régression. K20-ZE pose la même question, à l'aveugle, sur une deuxième enquête (celle de
la BCE, zone euro, 1999-2026). Il garde les règles de K20 partout où elles se transportent, et corrige la garde fautive.

---

## 0. Ce qui a déjà été vu

**Ce que le rédacteur a lu, en entier.**
- `tests-de-mort/protocole.md` et `tests-de-mort/verdict.py`.
- `tests-de-mort/K20/preenregistrement.md`, `K20/verdict.json`, `K20/lecture-apres-coup.md`. Rien d'autre du dossier K20.
- `tests-de-mort/K01/preenregistrement.md`, pour reprendre ses conventions de données sur la même archive. **Rien d'autre du
  dossier K01** : ni fichier d'analyse, ni dossier de données, ni scripts, ni rapports, ni `temoin.json`, ni `verdict.json`.
- `generation-3/nouveaute/K20.md` (littérature).
- Deux demandes du chef de projet, reçues pendant la rédaction : un contrôle positif (section 6.6) et une vérification par
  simulation que la règle tranche (section 8).

**Résultat de K20 (enquête américaine, 1969-2026, 1 004 lignes, cinq variables).**
- Supplément de pente après une grande surprise : **c = −0,030**, écart-type de Driscoll-Kraay 0,071, intervalle à 90 %
  **[−0,146 ; +0,086]**.
- Pente de base (petites nouvelles), moyenne des cinq variables : **b = 0,194** ; pente après une grande surprise : 0,164.
- k = écart-type des révisions / écart-type des erreurs : 0,294. Rapport des variances de révision (grandes / petites) :
  3,06. Biais mécanique calculé : 0,081. Écart-type « comme si indépendant » : 0,064, soit 820 observations effectives
  pour 1 004 lignes.
- Sans chaque épisode, c va de −0,084 à +0,014 ; par variable, de −0,31 à +0,17.
- Sous sa propre règle, ces chiffres auraient donné « éliminée ». Le verdict est « non concluant » seulement parce que le
  contrôle n° 9 a échoué sur une ligne (IPC, 2026T1) hors de toute régression : le contrôle portait sur tout le fichier et non
  sur les lignes du calcul.

**Ce que K01 a publié sur le consensus de l'enquête de la BCE** (chiffres connus par le brief, `verdict.json` de K01 non
ouvert) : pente erreur sur révision du consensus d'inflation, cibles annuelles, **0,92** sur tout l'échantillon et **0,51**
hors des années cibles 2021-2023. Ces pentes sont en points d'erreur par point de révision, non réduites, et portent sur
l'inflation seule. Elles disent que le consensus de la BCE sous-réagit en moyenne, et que 2021-2023 pèse lourd. Elles ne
disent rien du supplément selon la taille des nouvelles. **Le plan n'est pas réglé sur elles** : aucun seuil n'en vient. Le
contrôle positif (section 6.6) a été demandé par le chef de projet ; pour l'inflation, il n'est pas aveugle (limite 2).

**Ce que le rédacteur a vu des données** (téléchargées le 2026-11-13 dans un dossier temporaire, hors du dépôt ; aucune
valeur affichée).
- Archive de la BCE (`SPF_microdata_by_variable.zip`, HTTP 200, même sha256 que pour K01 la veille) : liste des fichiers,
  en-têtes, texte de `README_SPF_microdata.pdf`, et des comptes : types de cible présents par tour, décalage année cible −
  année du tour, nombre de répondants par cellule, doublons, nombre de décimales, nombre de valeurs hors plage, **périodes**
  (pas valeurs) des valeurs de référence de chaque tour, et périodes des cibles glissantes.
- Un compte sur les valeurs de référence du PIB, pour en vérifier l'unité : 54 des 104 tours hors 2020-2021 ont une valeur
  de référence supérieure à 1,5 en valeur absolue. Cela n'est compatible qu'avec un taux sur un an (un taux trimestriel
  dépasse rarement 1 %). Aucune valeur n'a été affichée.
- Eurostat (`prc_hicp_ainr`, `nama_10_gdp`, `une_rt_m`, `une_rt_a`) : en-têtes, zones disponibles, périodes présentes,
  drapeaux, date de mise à jour, nombre de décimales, nombre de valeurs hors plage.
- Comité de datation de la zone euro (CEPR-EABCN) : deux documents de constat téléchargés et lus (section 6.8).
- Les résultats des simulations de la section 8, qui n'utilisent aucune donnée de résultat.

**Règle d'aveuglement pour la suite.** L'expérimentateur et le vérificateur de K20-ZE n'ouvrent aucun fichier d'un autre
dossier de `tests-de-mort/`, sauf `protocole.md` et `verdict.py`. Tout ce qu'il faut savoir de K20 et de K01 est écrit ici.
S'ils ouvrent autre chose, ils l'écrivent dans `ecarts.md`.

---

## 1. Question, définitions, hypothèses rivales et prédiction chiffrée

**Question.** Dans l'enquête de la BCE auprès des prévisionnistes professionnels (années cibles 2000-2025, inflation IPCH,
croissance du PIB réel, taux de chômage), la sous-réaction du consensus est-elle plus forte après une grande nouvelle sur les
données ? Et cela tient-il sans chacun des grands épisodes ? La sous-réaction se mesure, comme dans K20, par la pente positive
de l'erreur sur la révision.

**Définitions.** Pour une variable v, une année cible y (moyenne de l'année civile) et un tour d'enquête t (trimestriel) :
- **Consensus** P(t, y) : moyenne simple des prévisions ponctuelles individuelles du tour t pour l'année y (section 3.1).
- **Révision** r = P(t, y) − P(t − 1, y) : ce que le consensus a changé entre deux tours successifs, pour la même année.
- **Erreur** e = a(y) − P(t, y), où a(y) est la valeur réalisée de l'année y (Eurostat, section 3.2).
- **Surprise** s = R(t) − R(t − 1), où R(t) est la **valeur de référence** que la BCE donne aux prévisionnistes au début du
  tour t : la dernière donnée publiée de la variable (inflation du dernier mois connu, croissance sur un an du dernier
  trimestre connu, chômage du dernier mois connu). s est donc la nouvelle publiée entre les deux tours, telle que les
  prévisionnistes l'ont reçue. La révision r répond en partie à cette nouvelle.
- **Grande nouvelle** : L = 1 si |s| est dans le tiers supérieur des |s| de la variable (règle exacte en section 6.2) ;
  sinon L = 0. L ne dépend jamais de la révision.

**Hypothèses** (c = supplément de pente de l'erreur réduite sur la révision réduite quand L = 1, section 6.3).

| Hypothèse | Ce qu'elle dit | Signe de c |
|---|---|---|
| H1 — fiche K20 | les prévisionnistes révisent trop peu quand il faudrait réviser beaucoup (réticence aux grandes révisions, lissage) | **c > 0** |
| H0 — rigidité de taille fixe | information rigide ou bruitée à degré constant (Coibion et Gorodnichenko 2012) | c = 0 |
| H2 — l'attention monte avec les chocs | moins de rigidité en période agitée et après les grands chocs visibles (Coibion et Gorodnichenko 2015 ; Baker, McElroy et Sheng 2020) | c < 0 |
| H3 — sur-réaction aux nouvelles extrêmes | règle linéaire face à des chocs à queues épaisses (de Silva, Larsen-Hallock, Rej et Thesmar 2025, sur des ventes d'entreprises) | c < 0, pente des grandes nouvelles b + c parfois négative |
| H4 — artefact de mesure | le bruit du consensus atténue davantage la pente là où les révisions varient peu | c > 0, petit (section 7) |
| H5 — persistance | plus de sous-réaction quand l'inflation est élevée (Kučinskas et Peters 2024) | c > 0 surtout pour l'inflation ; c par variable, descriptif |

**Prédiction chiffrée de l'hypothèse, reprise de K20 sans changement** : pente de base ≈ +0,3 ; supplément **c ≈ +0,40**,
plage +0,2 à +0,6 ; unités : écart-type d'erreur par écart-type de révision, variables regroupées. L'enjeu chiffré reste
**0,40**.

**Attente du rédacteur, pour mémoire et hors verdict.** K20 a trouvé c ≈ −0,03 sur l'enquête américaine, et la littérature
penche contre H1. Le rédacteur s'attend à un c entre −0,2 et +0,1, donc plutôt à une élimination. Il ne sait pas de quel côté
des seuils le résultat tombera sur la zone euro.

**Ce qu'une réplication ajoute.** Une deuxième enquête, un autre continent, d'autres chocs (crise des dettes souveraines, choc
énergétique de 2022), des cibles annuelles au lieu de trimestrielles, et une surprise mesurée sur la donnée réellement
envoyée aux prévisionnistes.

---

## 2. Ce qui est repris de K20 et ce qui est adapté

### 2.1 Repris sans changement

| Élément de K20 | Pourquoi il se transporte tel quel |
|---|---|
| La statistique : supplément de pente c commun, en variables réduites, après une grande nouvelle | c'est la question ; la réplication doit mesurer la même chose |
| Grande nouvelle = tiers supérieur de \|surprise\| **dans chaque variable**, surprise tirée d'une donnée publiée entre les deux enquêtes, **jamais de la révision** | trier sur la révision crée l'interaction par le bruit (K20, amendement A1) |
| Constante, effet propre de la classe et pente de base **propres à chaque série** ; c commun | sinon la non-linéarité se confond avec des différences entre séries (K20, A3) |
| Réduction par l'écart-type de chaque série sur l'échantillon principal | même raison que K20 (A12) |
| Consensus = moyenne des réponses (médiane en secondaire) | la moyenne réduit l'arrondi individuel (K20, A4) |
| Écart-type de Driscoll-Kraay : scores sommés par date d'enquête, poids de Bartlett, trimestres vides comptés, sans correction de petit échantillon, code propre et non `statsmodels` | même idée, même écriture exacte (K20, étape 4) |
| Plancher de survie = max(0,10 ; biais mécanique calculé avec 20 % de bruit), même formule | le tri par la surprise laisse l'atténuation différentielle (section 7) |
| Survie : borne basse à 90 % au-dessus du plancher, borne haute ≥ 0,40, t ≥ 1 sans chaque épisode | ce sont les seuils de K20 ; 0,40 est la prédiction |
| Élimination : borne haute < 0,40, ou c ≤ 0 sans un épisode alors que le test principal passe | idem |
| Non concluant : indécision (l'intervalle contient le plancher et 0,40), conflit de robustesse | idem |
| Seuil de pertinence 1,25 sur le rapport des variances de révision | idem, mais son **usage** change (2.2, ligne 9) |
| Exclusion pandémique pour les variables d'activité, analyse avec la pandémie en secondaire | même raison : une poignée de cibles pèserait plus que deux décennies |
| Analyses secondaires : par variable, autres retards, avec la pandémie, avant 2020, médiane, coupure de la fiche sur la révision | idem |
| Tolérances entre expérimentateur et vérificateur | idem |

### 2.2 Adapté, avec la raison

| N° | K20 faisait | K20-ZE fait | Raison |
|---|---|---|---|
| 1 | cible trimestrielle ; une révision par cible (enquête q − 4 → q − 3) | **cibles annuelles** « année en cours » et « année suivante » ; une ligne par variable × année cible × tour, soit 8 tours par cible | l'enquête de la BCE ne demande pas de trajectoire trimestrielle sur toute la période (le fichier trimestriel du PIB ne commence qu'en 2021T2) ; les cibles glissantes changent de date à chaque tour, donc on ne peut pas y former une révision « même cible, tours successifs ». Les cibles annuelles existent à **tous** les tours (vérifié, section 3.1) |
| 2 | surprise = donnée publiée − prévision du trimestre courant par le consensus (« nowcast ») | surprise = **valeur de référence du tour t − valeur de référence du tour t − 1** | l'enquête de la BCE n'a pas de prévision du trimestre courant sur toute la période. La valeur de référence est la donnée que la BCE envoie aux prévisionnistes au début du tour : c'est exactement « la donnée publiée entre les deux enquêtes ». Le point de comparaison devient la donnée précédente (sans changement) au lieu du consensus. Conséquence : la surprise ne contient **aucun** bruit d'enquête (section 7). Une surprise relative au consensus, plus proche de K20, est en analyse secondaire S8 |
| 3 | 5 variables, pentes propres à chaque variable | 3 variables × 2 horizons = **6 séries** ; constantes, effets de classe et pentes propres à chaque série | une même variable a, selon l'horizon, des erreurs et des révisions d'échelles différentes. 6 + 6 + 6 + 1 = 19 paramètres |
| 4 | Driscoll-Kraay à 4 retards | **8 retards** (4 et 12 en secondaire) | l'erreur d'une prévision annuelle faite au premier tour de l'année précédente contient les nouvelles de 8 tours. Les scores de deux tours distants de 1 à 7 partagent des chocs : il faut au moins 7 retards. 8 retards = deux ans, comme K01 |
| 5 | valeur critique 1,645 (loi normale) | **1,708** (loi de Student à 25 degrés de liberté) | l'information indépendante vient d'environ 26 années cibles, pas de 223 trimestres. C'est la correction de K01 sur la même archive |
| 6 | épisodes : récessions NBER, du pic au creux + 4 trimestres | récessions de la **zone euro** datées par le comité CEPR-EABCN, jointes à la poussée d'inflation 2021-2023 ; une ligne appartient à un épisode si son intervalle d'information le croise | même principe (une ligne est touchée si une information qu'elle contient date de l'épisode), traduit pour des cibles annuelles (section 6.8) |
| 7 | réalisé : première publication (comptes nationaux) ou dernier millésime FRED | **dernier millésime Eurostat**, téléchargé le jour du calcul | Eurostat ne publie pas de millésimes (section 3.2) |
| 8 | exclusion pandémique : cibles trimestrielles 2020T1-2021T4 de `RGDP` et `UNEMP` | lignes PIB et chômage dont l'année cible est 2020 ou 2021, ou dont le tour est entre 2020T1 et 2021T4 | même règle (toute ligne dont le réalisé, la surprise ou les deux tours tombent dans la pandémie), traduite en années |
| 9 | non concluant si rapport des variances de révision < 1,25 | non concluant si ce rapport est < 1,25 **et** si la survie n'est pas acquise (`pertinence_manquante`) | la simulation (section 8) montre un défaut de la garde de K20 : sous H1 à la taille prédite, le consensus révise **moins** que la nouvelle ne l'exige après les grandes surprises, et le rapport tombe sous 1 (0,6 en moyenne). La garde de K20 aurait rendu « non concluant » presque chaque fois que l'hypothèse est vraie. Or un tri sans rapport avec les nouvelles ne peut pas produire un c significativement au-dessus du plancher, sauf par hasard : la garde ne sert qu'à empêcher d'**éliminer** sur un tri vide de sens |
| 10 | — | **contrôle positif** : la sous-réaction de base doit être visible (`controle_positif_ok`) | demande du chef de projet : si le consensus ne montre aucune sous-réaction, un c nul ne dit rien de sa dépendance à la taille (section 6.6) |
| 11 | contrôles de schéma sur tout le fichier | **contrôles sur les lignes qui entrent dans le calcul** ; anomalies des autres lignes comptées à part, hors verdict | c'est le défaut qui a rendu K20 non concluant (section 4.4) |
| 12 | coupure stricte \|s\| > Q | coupure stricte ou large, celle qui approche le mieux le tiers | les valeurs de référence ont une décimale : beaucoup d'égalités. Une coupure stricte pourrait ne garder que 20 % des tours (section 6.2) |
| 13 | minimum 1 000 lignes sur 1 004 | minimum **570** lignes sur 578 | perdre plus d'un tour entier (6 lignes) et deux lignes signalerait un défaut de construction |

---

## 3. Données

Toutes les sources sont publiques, sans compte. Les fichiers bruts vont dans `tests-de-mort/K20-ZE/donnees/`. Le sha256, la
date, le code HTTP et, pour Eurostat, la colonne `LAST UPDATE` de chaque fichier vont dans
`tests-de-mort/K20-ZE/construire_journal.json`. Chaque téléchargement a jusqu'à 10 essais, 120 s par essai, 10 s entre deux
essais. **Si un fichier manque, l'expérimentateur s'arrête** : non concluant, pour une raison de données.

### 3.1 Prévisions — enquête de la BCE auprès des prévisionnistes professionnels

```
https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip
```

- Testé le 2026-11-13 : HTTP 200, 12 035 888 octets, sha256
  `49348fa33c5e5d58aa3e05aac56cf5df23ab29439862ab6e3ccafe68797b51f4` (identique à celui relevé par K01 le 2026-11-12).
- L'archive contient deux copies de chaque fichier : à la racine et sous `D:/spf-disc-casper/output_files/`. Les copies sont
  identiques (sha256 vérifiés). **On lit la copie à la racine** :
  - `1_HICP.csv` (sha256 `a8e99246…85aa7`), `3_RGDP.csv` (`755f49aa…478438`), `5_UNEM.csv` (`d522f43c…26d394`) ;
  - `0_Round_dates.csv` (`c960dcc2…142eae`) : dates des tours, recopié dans `donnees/`, non utilisé dans le calcul.
- Si l'archive du jour a un autre sha256 (mise à jour), on continue avec elle et on l'écrit dans `ecarts.md`. La fenêtre
  (tours jusqu'à 2025T4, années cibles 2000-2025) est fixée ici : des tours ajoutés après 2025T4 ne changent rien.
- Colonnes : `ref_round, fct_topic, forecaster_id, target_period_type, target_period, table_name, prob_interval, value`.
  Lecture en texte (`dtype=str`, `keep_default_na=False`) : les identifiants ont des zéros en tête.

**Lignes utilisées.**
- Prévisions individuelles : `table_name` = `Point` ; `forecaster_id` = trois chiffres (`AGG`, moyenne publiée, et `ECB`,
  valeurs de référence, exclus) ; `target_period_type` ∈ {`A_YEAR_0_AHEAD`, `A_YEAR_1_AHEAD`, `A_YEAR_2_AHEAD`} (moyenne de
  l'année du tour, de l'année suivante, de la deuxième année suivante, selon le README).
- Valeurs de référence : `forecaster_id` = `ECB`, `table_name` = `Point`, `target_period_type` = `M_REFERENCE` (inflation,
  chômage) ou `Q_REFERENCE` (PIB). `target_period` donne la période de la donnée (forme `2007Jun` ou `2007Q1`).
- Prévisions glissantes à un an (analyse secondaire S8 seulement) : individuelles, `M_YEAR_1_AHEAD` (inflation, chômage) ou
  `Q_YEAR_1_AHEAD` (PIB).

**Ce qui a été vérifié sur les fichiers réels (comptes seulement).**
- 112 tours, de 1999T1 à 2026T4, tous au format `AAAAQn`, dans les trois fichiers.
- `A_YEAR_0_AHEAD` et `A_YEAR_1_AHEAD` existent aux **112 tours**. `A_YEAR_2_AHEAD` existe à tous les tours T3 et T4 de 2000T3
  à 2026T4 (et aux tours T1 et T2 depuis 2013), **mais pas en 1999T4**.
- Année cible − année du tour = 0, 1, 2 pour 100 % des lignes de ces trois types.
- Aucun doublon (tour, identifiant, type, cible) ; aucune valeur `NA` ni non numérique parmi les prévisions ponctuelles.
- Répondants par cellule utilisée par l'échantillon principal : **au moins 44** au tour évalué, **au moins 39** au tour
  précédent (cellules `A_YEAR_2_AHEAD`). Le minimum de 20 fixé en 3.3 ne mord donc jamais sur l'archive actuelle.
- Une seule ligne `ECB` de référence par tour et par fichier (112 sur 112).
- **Période de la valeur de référence**, vérifiée aux 112 tours (période seulement, pas valeur) :
  - inflation : dernier mois du trimestre précédent le tour (décembre pour un tour T1…), sauf 2024T2 : février 2024 ;
  - PIB : trimestre t − 2 (le tour T1 de l'année Y reçoit le taux sur un an du T3 de Y − 1) ;
  - chômage : deuxième mois avant le début du trimestre du tour (novembre pour un tour T1…), sauf six tours : 2000T1
    (décembre 1999), 2023T1 (octobre 2022), 2023T4 (juillet 2023), 2024T1 (octobre 2023), 2024T2 (janvier 2024), 2024T4
    (juillet 2024).
- Unités des valeurs de référence : inflation, taux sur un an de l'IPCH du mois (%) ; PIB, taux de croissance sur un an du
  trimestre (%), vérifié par le compte donné en section 0 ; chômage, taux du mois (% de la population active).
- Nombre de décimales des valeurs de référence : une (ou zéro) dans les trois fichiers.
- Prévisions glissantes à un an : la cible du tour t − 4 est la période de référence du tour t pour 107 tours sur 108
  (inflation), 108 sur 108 (PIB), 101 sur 108 (chômage).

### 3.2 Réalisations — Eurostat, dernier millésime

```
https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV
https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nama_10_gdp/A.CLV_PCH_PRE.B1GQ.EA?format=SDMX-CSV
https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/une_rt_m/M.NSA.TOTAL.PC_ACT.T.EA21?format=SDMX-CSV
```

| Variable | Série | Concept | a(y) | Vérifié le 2026-11-13 |
|---|---|---|---|---|
| `HICP` | `prc_hicp_ainr`, `RCH_A_AVG`, `TOTAL`, zone `EA` (composition évolutive) | taux de variation de la moyenne annuelle de l'IPCH, % | `OBS_VALUE` de l'année y | HTTP 200 ; colonnes `DATAFLOW, LAST UPDATE, freq, unit, coicop18, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS` ; 1997-2025 ; aucun vide, aucun drapeau ; une décimale ; mise à jour `17/09/26` ; sha256 `43ef7b6b…0505e` (identique à K01) |
| `RGDP` | `nama_10_gdp`, `CLV_PCH_PRE`, `B1GQ`, zone `EA` (composition évolutive) | croissance annuelle du PIB en volume chaîné, % | `OBS_VALUE` de l'année y | HTTP 200 ; colonnes `DATAFLOW, LAST UPDATE, freq, unit, na_item, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS` ; 1996-2025 ; aucun vide, aucun drapeau ; une décimale ; mise à jour `11/11/26` ; sha256 `0b8e98ab…31534` |
| `UNEM` | `une_rt_m`, non désaisonnalisé (`NSA`), `TOTAL`, `PC_ACT`, `T`, zone `EA21` | taux de chômage, % de la population active | **moyenne des 12 mois** de l'année y | HTTP 200 ; colonnes `DATAFLOW, LAST UPDATE, freq, s_adj, age, unit, sex, geo, TIME_PERIOD, OBS_VALUE, OBS_FLAG, CONF_STATUS` ; 2000-01 à 2026-09 ; 12 mois présents pour chaque année 2000-2025 ; aucun vide, aucun drapeau ; une décimale ; mise à jour `05/11/26` ; sha256 `7842067c…4beb10e` |

**Pourquoi ces séries.**
- L'enquête demande la moyenne de l'année civile : taux de variation de la moyenne annuelle de l'IPCH, croissance annuelle
  du PIB réel, taux de chômage moyen de l'année (README de l'enquête).
- Zone à composition évolutive (`EA`) quand elle existe : c'est la zone sur laquelle les prévisionnistes répondaient chaque
  année.
- Pour le chômage, Eurostat n'a pas de série à composition évolutive : la série annuelle `une_rt_a` (zone `EA21`) ne commence
  qu'en 2009 (vérifié), et la série mensuelle n'a que `EA21`, depuis 2000-01. On prend donc la moyenne des 12 mois de `EA21`
  (limite 6).

**Règle de millésime.** Eurostat ne publie pas de millésimes de ces séries. Le réalisé est celui du fichier téléchargé **le
jour du calcul** par l'expérimentateur. Son sha256 et sa date `LAST UPDATE` vont dans `construire_journal.json`. Le
vérificateur recalcule sur le fichier d'analyse, donc sur les mêmes réalisés. Si le fichier du jour diffère de celui décrit
ici (autre sha256 ou autre date), on continue et on l'écrit dans `ecarts.md`. **Limite** : le réalisé n'est pas le chiffre
que les prévisionnistes visaient au moment de la cible. Pour le PIB, les révisions de référence (SEC 2010 en 2014, 2019,
2024) déplacent la croissance annuelle de quelques dixièmes. Pour le chômage, la composition `EA21` et la refonte de
l'enquête sur les forces de travail de 2021 déplacent le niveau. Ces écarts sont dans le réalisé, donc dans l'erreur, et sont
communs aux 8 lignes d'une même année cible. Ils élargissent les intervalles ; ils ne biaisent la pente que s'ils sont
corrélés aux révisions. L'inflation n'est pas révisée.

**La surprise n'utilise pas Eurostat** : elle se lit dans les valeurs de référence de l'archive, en temps réel.

### 3.3 Construction

Numéro de tour : t = 4 × année + trimestre − 1 (1999T1 → 7996 ; 2020T1 → 8080 ; 2025T4 → 8103).

Pour chaque variable v ∈ {`HICP`, `RGDP`, `UNEM`}, chaque année cible y de 2000 à 2025 et chaque rang j de 1 à 8 :
- `t_tour` = 4 × (y − 1) + j − 1 : le rang 1 est le tour T1 de y − 1, le rang 8 le tour T4 de y ;
- `horizon` = 1 (année suivante) si j ≤ 4, 0 (année en cours) si j ≥ 5 ;
- tour précédent : `t_tour` − 1 ; son horizon vaut y − année(tour précédent), soit 2 pour le rang 1, sinon 1 ou 0 ;
- consensus `prev` = moyenne des `value` des prévisions individuelles du tour, du type `A_YEAR_<horizon>_AHEAD`, de
  `target_period` = y ; `n_rep` = leur nombre ; `prev` vide si `n_rep` < 20 ;
- `prev_prec`, `n_rep_prec` : idem au tour précédent, type `A_YEAR_<horizon_prec>_AHEAD` ; vides (et `n_rep_prec` = 0) si le
  tour précédent est avant 1999T1 ou si la cellule n'existe pas ;
- `prev_med`, `prev_prec_med` : médianes des mêmes réponses ;
- `ref`, `ref_periode` : `value` et `target_period` de la ligne `ECB` du tour ; `ref_prec`, `ref_periode_prec` : idem au tour
  précédent (vides avant 1999T1) ;
- `prev_glissante_t4` : moyenne des prévisions individuelles glissantes à un an du tour `t_tour` − 4 dont `target_period` =
  `ref_periode` ; vide s'il y en a moins de 20 ou si ce tour est avant 1999T1 ;
- `realise` : section 3.2.

**Conséquences vérifiées par la présence des cellules.**
- 624 lignes (3 × 26 × 8).
- 6 lignes sans révision : le rang 1 des cibles 2000 (tour 1999T1, premier tour de l'enquête, pas de tour précédent) et 2001
  (la prévision précédente serait `A_YEAR_2_AHEAD` au tour 1999T4, absente), pour chaque variable.
- Valeur de référence présente à tous les tours ; surprise présente dès 1999T2.

---

## 4. Fichier d'analyse

### 4.1 Format

**Nom** : `tests-de-mort/K20-ZE/K20-ZE_analyse.csv`. UTF-8, séparateur virgule, point décimal, première ligne = noms de
colonnes, cellule vide = manquant. Les décimaux sont écrits en double précision complète (représentation Python `repr`),
sans arrondi.

**Une ligne par variable × année cible × tour**, exactement **624 lignes**, y compris quand des valeurs manquent. Tri :
`variable` dans l'ordre `HICP`, `RGDP`, `UNEM`, puis `annee_cible`, puis `t_tour` croissants.

| # | Colonne | Type | Contenu, unité |
|---|---|---|---|
| 1 | `variable` | texte | `HICP`, `RGDP` ou `UNEM` |
| 2 | `annee_cible` | entier | 2000 à 2025 |
| 3 | `tour` | texte | forme `2007Q3` |
| 4 | `t_tour` | entier | 4 × année + trimestre − 1 |
| 5 | `rang` | entier | `t_tour` − 4 × (`annee_cible` − 1) + 1, de 1 à 8 |
| 6 | `horizon` | entier | `annee_cible` − année de `tour` : 1 si `rang` ≤ 4, 0 sinon |
| 7 | `tour_prec` | texte | tour `t_tour` − 1, forme `2007Q2` |
| 8 | `horizon_prec` | entier | `annee_cible` − année de `tour_prec` : 0, 1 ou 2 |
| 9 | `n_rep` | entier | nombre de prévisions individuelles de la cellule du tour |
| 10 | `n_rep_prec` | entier | idem au tour précédent ; 0 si la cellule n'existe pas |
| 11 | `prev` | décimal | consensus (moyenne) du tour, % |
| 12 | `prev_prec` | décimal | consensus du tour précédent, même année cible, % |
| 13 | `prev_med` | décimal | médiane du tour, % |
| 14 | `prev_prec_med` | décimal | médiane du tour précédent, % |
| 15 | `ref_periode` | texte | `target_period` de la valeur de référence du tour (`2007Jun`, `2007Q1`) |
| 16 | `ref` | décimal | valeur de référence du tour, % |
| 17 | `ref_periode_prec` | texte | idem au tour précédent |
| 18 | `ref_prec` | décimal | valeur de référence du tour précédent, % |
| 19 | `prev_glissante_t4` | décimal | consensus glissant à un an du tour `t_tour` − 4 pour la période `ref_periode`, % |
| 20 | `realise` | décimal | a(`annee_cible`), % (section 3.2) |
| 21 | `revision` | décimal | `prev` − `prev_prec`, points |
| 22 | `erreur` | décimal | `realise` − `prev`, points |
| 23 | `surprise` | décimal | `ref` − `ref_prec`, points |
| 24 | `surprise_consensus` | décimal | `ref` − `prev_glissante_t4`, points |
| 25 | `revision_med` | décimal | `prev_med` − `prev_prec_med` |
| 26 | `erreur_med` | décimal | `realise` − `prev_med` |
| 27 | `complete` | entier | 1 si `revision`, `erreur` et `surprise` sont toutes présentes ; sinon 0 |
| 28 | `principal` | entier | 1 si `complete` = 1 et si la ligne n'est pas exclue pour la pandémie (4.2) ; sinon 0 |
| 29 | `episode` | texte | `E1`, `E2` ou `E3` selon la règle de la section 6.8 ; sinon vide |
| 30 | `grande_nouvelle` | entier | L (section 6.2) si `surprise` est présente ; sinon vide |

Soit exactement 30 colonnes, dans cet ordre et sans aucune autre. Une différence est vide si et seulement si l'un de ses
termes est vide.

### 4.2 Échantillon principal

`principal` = 1 si `complete` = 1, **sauf** les lignes `RGDP` et `UNEM` dont `annee_cible` ∈ {2020, 2021} ou dont `t_tour`
est entre 8080 et 8087 (2020T1-2021T4).

Pourquoi : en 2020, les prévisions annuelles du PIB ont été révisées de six à huit points en un tour, contre quelques dixièmes
d'habitude. Une révision réduite de dix écarts-types pèserait plus sur c que des années entières. La règle retire toute ligne
dont le réalisé (années 2020 et 2021, rebond compris), la révision ou la surprise tombe dans la pandémie. L'inflation garde
ces lignes, comme les prix dans K20 : ses mouvements de 2020-2023 sont grands mais pas d'un autre ordre que leurs propres
variations. L'analyse S3 remet les lignes exclues. Ce choix vient de ce que tout le monde sait de 2020, pas des données de
l'enquête.

### 4.3 Comptes attendus (présence des cellules, vérifiés sur les fichiers réels)

| | `HICP` | `RGDP` | `UNEM` | Total |
|---|---|---|---|---|
| lignes | 208 | 208 | 208 | 624 |
| `complete` = 1 | 206 | 206 | 206 | 618 |
| `principal` = 1 | 206 | 186 | 186 | **578** |
| dont année en cours / année suivante | 104 / 102 | 96 / 90 | 96 / 90 | 296 / 282 |

- L'échantillon principal couvre **107 tours** (1999T2-2025T4) et **26 années cibles** ; de 2 à 6 lignes par tour (5,4 en
  moyenne).
- Lignes principales par épisode (section 6.8) : E1 54, E2 72, E3 98 ; hors épisode 354. Sur tout le fichier : 54, 72,
  138, 360.

### 4.4 Contrôles de schéma — la correction de K20

**Le défaut de K20.** Un contrôle a échoué sur une ligne (IPC, 2026T1) qui n'entrait dans aucune régression. Le contrôle
portait sur tout le fichier, et la préinscription affirmait sans l'avoir vérifié que la structure de la source le
garantissait. Le test est devenu non concluant pour un défaut sans effet sur le chiffre.

**La règle de K20-ZE.**
1. Les contrôles de **fichier** (n° 1 et 2) portent sur le fichier entier : un fichier mal formé fausse tout.
2. Les contrôles de **ligne** (n° 3 à 9, 11 et 12) sont faits sur toutes les lignes. Un échec compte pour le verdict
   **seulement s'il touche une ligne où `principal` = 1**. Les échecs sur les autres lignes sont comptés dans
   `n_anomalies_hors_principal` (nombre de couples contrôle × ligne en échec), rapporté, **sans effet sur le verdict**.
3. Le contrôle d'**appartenance** (n° 10) recalcule `complete` et `principal` sur toutes les lignes à partir de leurs propres
   colonnes. Tout désaccord compte pour le verdict, même sur une ligne marquée 0 : il change l'ensemble des lignes du calcul.

`n_violations_schema` = nombre de contrôles (de 0 à 12) qui comptent pour le verdict et qui échouent sur au moins une ligne.
0 attendu. Le vérificateur les refait sur le fichier.

**Vérification avant scellement.** La dernière colonne dit ce qui a été vérifié sur des lignes réelles de l'archive et
d'Eurostat (comptes, sans valeur). Quand un contrôle est une identité de calcul (une différence, une moyenne), on a vérifié
que ses opérandes existent et sont numériques sur toutes les lignes concernées ; l'identité elle-même ne peut échouer que par
une erreur de construction, et la calculer serait calculer un résultat.

| N° | Contrôle | Portée | Vérifié sur les lignes réelles |
|---|---|---|---|
| 1 | **Colonnes** : les 30 noms de 4.1, dans cet ordre, sans autre | fichier | colonnes sources présentes sous ces noms dans `1_HICP.csv`, `3_RGDP.csv`, `5_UNEM.csv` et les trois fichiers Eurostat (en-têtes en 3.1-3.2) ; le fichier d'analyse n'existe pas encore |
| 2 | **Grille** : exactement 624 lignes ; chaque (`variable`, `annee_cible`, `t_tour`) de la grille une seule fois ; tri conforme | fichier | grille construite sur les identifiants réels : 624 lignes, 112 tours présents dans les trois fichiers |
| 3 | **Identifiants** : `tour` de forme `AAAAQn` ; `t_tour`, `rang`, `horizon`, `tour_prec`, `horizon_prec` conformes à leurs formules ; `rang` ∈ [1 ; 8] | lignes | les 112 tours au bon format ; décalage année cible − année du tour = 0, 1, 2 pour 100 % des lignes `A_YEAR_*` des trois fichiers |
| 4 | **Effectifs et présence** : `prev` présent si et seulement si `n_rep` ≥ 20 ; `prev_prec` présent si et seulement si `n_rep_prec` ≥ 20 ; sur les lignes principales, `n_rep` ≥ 20, `n_rep_prec` ≥ 20, et `prev`, `prev_prec`, `prev_med`, `prev_prec_med` présents | lignes | répondants des cellules principales : minimum 44 (tour évalué) et 39 (tour précédent) ; 0 doublon ; 0 `NA` ; 0 valeur non numérique ; les 6 lignes sans `prev_prec` listées en 3.3 |
| 5 | **Référence** : `ref` et `ref_periode` présents à tout tour ≥ 1999T1, et égaux à la ligne `ECB` de ce tour ; `ref_periode` suit la règle de 3.1 (mois ou trimestre, avec les exceptions listées) ; idem pour `ref_prec`, `ref_periode_prec` au tour précédent | lignes | les 112 tours, une ligne `ECB` par tour et par fichier ; règle des périodes vérifiée aux 112 tours, exceptions comprises |
| 6 | **Plages** : `prev`, `prev_prec`, `prev_med`, `prev_prec_med`, `realise` dans [−3 ; 12] (`HICP`), [−10 ; 10] (`RGDP`), [3 ; 15] (`UNEM`) ; `ref`, `ref_prec` dans [−3 ; 12], [−20 ; 20], [3 ; 15] | lignes | 0 prévision individuelle hors plage parmi les 12 852 (`HICP`), 11 666 (`RGDP`) et 11 032 (`UNEM`) réponses des cellules principales (une moyenne ou une médiane de valeurs dans la plage y reste) ; 0 valeur de référence hors plage sur les 112 tours des trois fichiers ; 0 réalisé hors plage (Eurostat, 2000-2025, les 312 mois de chômage compris) |
| 7 | **Formules** : `revision`, `erreur`, `surprise`, `surprise_consensus`, `revision_med`, `erreur_med` égales à leurs différences à 10⁻⁹ près, vides si et seulement si un terme est vide ; `prev_glissante_t4` présente si et seulement s'il y a au moins 20 prévisions glissantes du tour `t_tour` − 4 pour `ref_periode` | lignes | tous les opérandes numériques là où ils existent ; prévisions glissantes ≥ 20 pour 103 des 107 tours principaux (`HICP`), 96 sur 99 (`RGDP`), 89 sur 99 (`UNEM`) ; les différences ne sont pas calculées (ce seraient des résultats) |
| 8 | **Cohérence entre lignes** : quand la ligne (v, y, `t_tour` − 1) existe, `prev_prec` et `n_rep_prec` égalent son `prev` et son `n_rep` ; toutes les lignes d'un même (v, `t_tour`) ont les mêmes `ref`, `ref_periode`, `ref_prec`, `surprise`, `grande_nouvelle` ; `ref_prec`(v, t) = `ref`(v, t − 1) | lignes | une seule valeur de référence par tour ; une seule cellule par (tour, identifiant, type, cible) |
| 9 | **Réalisé** : une seule valeur par (`variable`, `annee_cible`), présente pour 2000-2025 ; `HICP` et `RGDP` = `OBS_VALUE` de l'année ; `UNEM` = moyenne des 12 mois de l'année, à 10⁻⁹ près (recalculée sur le fichier brut) | lignes | années 2000-2025 présentes, sans drapeau, dans les deux séries annuelles ; 12 mois présents pour chaque année 2000-2025 dans `une_rt_m` `EA21` |
| 10 | **Appartenance** : `complete` et `principal` conformes à leur définition, recalculés sur **toutes** les lignes | toutes les lignes, compte pour le verdict | présence : 618 et 578 ; les 6 lignes incomplètes identifiées |
| 11 | **Épisodes** : `episode` = `Ek` si et seulement si la ligne vérifie la règle de la fenêtre k (section 6.8) ; sinon vide | lignes | comptes par épisode de 4.3, sur toutes les lignes et sur les principales |
| 12 | **Grande nouvelle** : `grande_nouvelle` présente si et seulement si `surprise` l'est ; constante dans un même (v, `t_tour`) ; vaut 1 si et seulement si \|`surprise`\| dépasse Q_v selon la coupure retenue, Q_v et la coupure recalculés comme en 6.2 | lignes | surprise présente sur toutes les lignes principales (référence présente aux 112 tours) ; le seuil Q_v n'est pas calculé avant le scellement (ce serait une statistique des nouvelles) |

---

## 5. Pourquoi cette surprise

**Ce qu'elle mesure.** Entre deux tours, la BCE envoie aux prévisionnistes la dernière donnée publiée. s = R(t) − R(t − 1)
est la variation de cette donnée en un trimestre : par exemple, l'inflation sur un an passe de 2,1 % (septembre) à 2,9 %
(décembre). C'est la nouvelle la plus visible entre les deux tours.

**Ce qu'elle ne mesure pas.** Elle ne retire pas la part prévisible de ce mouvement (effets de base, tendance). Une partie des
« grandes » surprises était donc attendue. Cela brouille le tri, ce qui affaiblit le test sans le biaiser dans un sens
connu. La surprise relative au consensus (S8) retire une partie de cette part prévisible ; elle n'existe pas pour tous les
tours (4.4, contrôle 7), d'où son statut secondaire.

**Ce qu'elle gagne sur K20.** Elle ne contient aucune prévision de l'enquête, donc aucun bruit d'enquête (section 7).

**Une même surprise pour les deux horizons.** Au tour t, la même donnée sert de nouvelle pour l'année en cours et pour
l'année suivante. L est donc défini par variable et par tour.

---

## 6. Statistique

Tout se calcule à partir du seul fichier d'analyse, en double précision, sans arrondi intermédiaire.

### 6.1 Échantillon et réduction

Échantillon principal : lignes `principal` = 1 ; n = `n_principal` (578 attendus). Une **série** g est un couple (variable,
horizon) : 6 séries.

Pour chaque série g, sur ses lignes principales :
- moyennes et écarts-types (diviseur n_g − 1) de `revision` et d'`erreur` : s_{r,g}, s_{e,g} ;
- z_r = (`revision` − moyenne) / s_{r,g} ; z_e = (`erreur` − moyenne) / s_{e,g} ;
- k_g = s_{r,g} / s_{e,g} ; `k_moyen` = moyenne des six k_g.

Toutes les lignes de g reçoivent ces constantes, y compris hors échantillon principal (pour S3). De même pour `revision_med`
et `erreur_med` (pour S6).

### 6.2 Grande nouvelle

Pour chaque variable v :
- T_v = ensemble des `t_tour` distincts des lignes principales de v ; |s_{v,t}| = valeur absolue de `surprise` de ce tour ;
- Q_v = `numpy.quantile(|s| sur T_v, 2/3)`, méthode linéaire par défaut ;
- n_> = nombre de tours de T_v avec |s| > Q_v ; n_≥ = nombre avec |s| ≥ Q_v ;
- **coupure** : stricte (L = 1 si |s| > Q_v) si |n_>/|T_v| − 1/3| ≤ |n_≥/|T_v| − 1/3| ; sinon large (L = 1 si |s| ≥ Q_v) ;
- L est appliqué à toute ligne de v dont `surprise` est présente.

Pourquoi cette coupure : les valeurs de référence ont une décimale, donc |s| prend des valeurs comme 0,1, 0,2, 0,3… avec
beaucoup d'égalités. On ne coupe jamais à l'intérieur d'un groupe de valeurs égales, et l'on prend le côté qui approche le
mieux le tiers. La règle ne dépend que de s, jamais de la révision ni de l'erreur. Q_v, la coupure et L sont calculés une
fois, puis gardés tels quels dans toutes les analyses (sauf S7 et S8).

### 6.3 Régression principale

Par MCO sur les lignes principales :

  z_e = Σ_g α_g·D_g + Σ_g δ_g·D_g·L + Σ_g b_g·D_g·z_r + **c**·z_r·L + u

- D_g = indicatrice de la série g ; 19 paramètres, dans cet ordre : 6 constantes, 6 effets de classe, 6 pentes de base, c.
- b_g = pente de l'erreur sur la révision pour les petites nouvelles de la série g ; b_g + c = pente pour ses grandes
  nouvelles.
- `c` = supplément de pente commun. `b_moyen` = moyenne des six b̂_g ; `pente_moyenne_grandes` = `b_moyen` + c.

### 6.4 Écart-type de Driscoll-Kraay à 8 retards

1. X = matrice des 19 régresseurs ; û = résidus ; h_i = X_i·û_i.
2. Pour chaque numéro de tour τ, du plus petit au plus grand `t_tour` de l'échantillon, **y compris les tours sans ligne** :
   H_τ = somme des h_i des lignes de ce tour (vecteur nul s'il n'y en a pas).
3. Ω = Σ_τ H_τ H_τ' + Σ_{j=1..8} (1 − j/9) × Σ_τ (H_τ H_{τ−j}' + H_{τ−j} H_τ').
4. V = (X'X)⁻¹ Ω (X'X)⁻¹, **sans correction de petit échantillon**.
5. `et_c_dk8` = racine de l'élément de V qui correspond à c.

On n'utilise pas `statsmodels` pour le verdict : il compte les retards par position et non par tour.

**Pourquoi 8 retards.** L'erreur d'une ligne contient les nouvelles du tour t jusqu'à la fin de l'année cible : jusqu'à 8
tours pour une prévision faite au premier tour de l'année précédente. Les scores de deux tours distants de 1 à 7 partagent
donc des chocs. Il faut au moins 7 retards ; 8 couvre deux ans. La règle de Newey et West (partie entière de
4 × (107/100)^(2/9) = 4) est trop courte pour ce chevauchement : 4 retards sont rapportés à côté (S2), avec 12 et 0.

### 6.5 Intervalle

- `t_c` = c / `et_c_dk8`.
- `borne_basse_ic90` = c − 1,708 × `et_c_dk8` ; `borne_haute_ic90` = c + 1,708 × `et_c_dk8`.
- 1,708 = quantile à 95 % de la loi de Student à 25 degrés de liberté : l'information indépendante vient d'environ 26
  années cibles (2000-2025), et l'écart-type de Driscoll-Kraay est souvent trop petit avec peu de grappes indépendantes.

### 6.6 Contrôle positif : l'instrument voit-il la sous-réaction ?

Demande du chef de projet : avant que le supplément c compte, le plan doit montrer qu'il voit l'effet sur lequel il est
bâti, la sous-réaction de base du consensus.

- **Pente commune** : MCO sur les lignes principales de z_e = Σ_g α_g·D_g + `b_commun`·z_r + u (7 paramètres, sans
  classe). Écart-type de Driscoll-Kraay à 8 retards (même calcul qu'en 6.4) : `et_b_commun_dk8` ;
  `borne_basse_b_commun_ic90` = `b_commun` − 1,708 × `et_b_commun_dk8`.
- **Pente des petites nouvelles** : `b_moyen` (6.3). Son écart-type est celui de la combinaison w'β, avec w = 1/6 sur les six
  b_g : `et_b_moyen_dk8` = racine(w'Vw), V de 6.4 ; `borne_basse_b_moyen_ic90` = `b_moyen` − 1,708 × `et_b_moyen_dk8`.
- **`controle_positif_ok`** = 1 si `borne_basse_b_commun_ic90` > 0 **ou** `borne_basse_b_moyen_ic90` > 0 ; sinon 0.

En mots : la sous-réaction de base est établie si la pente commune, ou la pente des petites nouvelles, a une borne basse à
90 % au-dessus de 0. Pourquoi les deux : sous H2 ou H3 avec un c fortement négatif, la pente commune peut tomber près de 0
alors que la pente des petites nouvelles reste positive ; ne regarder que la pente commune empêcherait alors d'éliminer. La
pente commune seule sert parce qu'elle utilise toutes les lignes : elle est plus précise que la pente des petites nouvelles.
Si `controle_positif_ok` = 0, le consensus ne montre pas de sous-réaction ; un c nul ne dit alors rien de la dépendance à
la taille, et le verdict est non concluant.

### 6.7 Pertinence et biais mécanique

Pour chaque série g et chaque classe ℓ, m_{g,ℓ} = moyenne de z_r parmi les lignes principales de g avec L = ℓ.
- a = moyenne de (z_r − m_{g,0})² sur toutes les lignes L = 0 ; A = moyenne de (z_r − m_{g,1})² sur toutes les lignes L = 1 ;
- `rapport_variance_revision` = A / a ;
- `pertinence_manquante` = 1 si `rapport_variance_revision` < 1,25 **et** `borne_basse_moins_seuil` ≤ 0 ; sinon 0 ;
- `rapport_variance_ecart_prec` (descriptif) : même calcul avec z_p à la place de z_r, où p = `erreur` + `revision` =
  `realise` − `prev_prec`, réduit par série. C'est la taille de ce qui restait à apprendre après le tour précédent ; elle ne
  dépend pas de la réaction du tour t ;
- `biais_mecanique_nu20` = (2 × `b_moyen` + `k_moyen`) × 0,10 × (1/a − 1/A) ;
- `seuil_survie_bas` = max(0,10 ; `biais_mecanique_nu20`) ;
- `borne_basse_moins_seuil` = `borne_basse_ic90` − `seuil_survie_bas`.

### 6.8 Garde de robustesse sur les épisodes (entre dans le verdict)

**Chronologie.** Comité de datation des cycles de la zone euro (CEPR-EABCN). Pics et creux trimestriels : pic 2008T1, creux
2009T2 ; pic 2011T3, creux 2013T1 ; pic 2019T4, creux 2020T2. Vérification :
- la page `https://eabcn.org/dc/chronology-euro-area-business-cycles` (et les pages de `cepr.org`) répond **HTTP 403** à
  `curl` et à la lecture automatique depuis cet environnement (blocage Cloudflare) : son existence n'a pas pu être
  confirmée par `curl` ;
- le constat du comité de septembre 2020,
  `https://eabcn.org/sites/default/files/2023-09/eabcdc_findings_september_2020_0.pdf` (HTTP 200, sha256
  `742947507455e1b0…3fce2c02`), lu : pic en 2019T4, expansion commencée après le creux de 2013T1, trajectoires de reprise
  « 2009Q2-2011Q3 » et « 2013Q1-2019Q4 » (donc creux 2009T2 et 2013T1, pics 2011T3 et 2019T4) ;
- le constat de décembre 2022, `https://eabcn.org/sites/default/files/2023-09/eabcdc_findings_december2022_0.pdf`
  (HTTP 200, sha256 `b0c779a8d10558c6…2bdd5623`), lu : « reprise commencée après le creux de 2020Q2 » ;
- le pic de 2008T1 (mois : janvier 2008) n'a été vu que dans des résumés de recherche web (page `eabcn.org/node/450`,
  bloquée en lecture directe). C'est la date publiée par le comité ; la fenêtre est fixée ici quoi qu'il arrive.

Aucune récession postérieure à 2020T2 n'apparaît dans les documents lus. Si le comité en a daté une depuis, la liste ne
change pas : elle est fixée maintenant.

**Fenêtres**, en numéros de trimestre, fixées maintenant :

| Code | Fenêtre [P ; T] | Numéros | Contenu |
|---|---|---|---|
| E1 | 2008T1-2009T2 | 8032-8037 | grande récession |
| E2 | 2011T3-2013T1 | 8046-8052 | crise des dettes souveraines |
| E3 | 2019T4-2023T4 | 8079-8095 | récession pandémique (2019T4-2020T2) jointe à la poussée d'inflation 2021T1-2023T4, comme l'E7 de K20 |

**Règle d'appartenance.** Une ligne (y, t) contient l'information de la période qui va du tour précédent (t − 1) à la fin de
son année cible (4y + 3). Elle appartient à Ek si cet intervalle croise la fenêtre :

  `t_tour` − 1 ≤ T_k  et  4 × `annee_cible` + 3 ≥ P_k.

C'est le principe du « + 4 » de K20 (une cible est touchée si une information qu'elle contient date de l'épisode), traduit
pour des cibles annuelles. Les trois fenêtres ne se recouvrent sur aucune ligne : une ligne de E1 a un tour ≤ 2009T3 ; une
ligne de E2 a une cible ≥ 2011, donc un tour ≥ 2010T1, et un tour ≤ 2013T2 ; une ligne de E3 a une cible ≥ 2019, donc un
tour ≥ 2018T1.

**Pour chaque k** :
- on refait 6.3 sur les lignes principales hors Ek, avec les mêmes z et le même L ;
- on calcule l'écart-type comme en 6.4 (les tours retirés deviennent des tours sans ligne) ;
- `c_sans_Ek` = c_(−k) ; `t_sans_Ek` = c_(−k) / et_(−k).

Champs : `t_min_sans_episode` = min_k `t_sans_Ek` ; `episode_t_min` = le k qui le donne (le plus petit en cas d'égalité) ;
`c_min_sans_episode` = min_k `c_sans_Ek`.

### 6.9 Champs dérivés pour la règle

- `marge_indecision` = min(`seuil_survie_bas` − `borne_basse_ic90` ; `borne_haute_ic90` − 0,40). Elle est positive ou nulle
  exactement quand l'intervalle à 90 % contient à la fois le plancher et 0,40.
- `conflit_robustesse` = 1 si les quatre conditions tiennent : `borne_basse_ic90` > `seuil_survie_bas` ;
  `borne_haute_ic90` ≥ 0,40 ; `t_min_sans_episode` < 1 ; `c_min_sans_episode` > 0. Sinon 0.

### 6.10 Comptes et observations effectives

- `n_grands` = lignes principales avec L = 1 ; `n_tours` = tours distincts de l'échantillon principal (107 attendus) ;
  `n_tours_grands` = tours avec au moins une ligne principale L = 1 ; `n_annees_cibles` = années cibles distinctes (26).
- `et_c_iid` = écart-type MCO classique de c, avec σ̂² = Σû² / (n − 19) ;
  `n_effectif` = n × (`et_c_iid` / `et_c_dk8`)². Un `n_effectif` supérieur à n signale un écart-type de Driscoll-Kraay trop
  petit, pas une information en plus (section 8).

**Convention.** Si un échantillon a moins de 50 lignes, ou si une matrice X'X est singulière, ses champs valent 0 et
l'incident va dans `ecarts.md`. Si cela touche le test principal, le verdict est non concluant (par `n_principal`, le schéma
ou le contrôle positif).

### 6.11 Analyses secondaires — descriptives, hors verdict, rapportées quoi qu'il arrive

Chacune reprend 6.3 à 6.5 (8 retards), avec les z et le L de l'échantillon principal, sauf mention contraire.
- **S1 — par variable** : c_v propre à chaque variable (18 + 3 = 21 paramètres). Champs `c_HICP`, `c_RGDP`, `c_UNEM` et
  `et_c_<v>_dk8`. Répond à H5.
- **S2 — inférence** : `et_c_dk4`, `et_c_dk12`, `et_c_dk0` (somme par tour, sans retard), `et_c_grappes_annee` (scores
  sommés par `annee_cible`, 26 grappes, Ω = Σ_y H_y H_y').
- **S3 — avec la pandémie** : lignes `complete` = 1. Champs `c_avec_pandemie`, `et_c_avec_pandemie_dk8`.
- **S4 — avant 2020** : lignes principales d'`annee_cible` ≤ 2019. Champs `c_avant_2020`, `et_c_avant_2020_dk8`.
- **S5 — par horizon** : lignes principales d'`horizon` 0 seulement (3 séries, 10 paramètres), puis d'`horizon` 1 seulement.
  Champs `c_annee_en_cours`, `et_c_annee_en_cours_dk8`, `c_annee_suivante`, `et_c_annee_suivante_dk8`.
- **S6 — médianes** : `revision_med`, `erreur_med`, réduites de la même façon sur les mêmes lignes ; L inchangé. Champs
  `c_mediane`, `et_c_mediane_dk8`.
- **S7 — coupure de la fiche** : L' = 1 si |z_r| > 1, à la place de L. Champs `c_coupure_revision`,
  `et_c_coupure_revision_dk8`. Il contient le biais de tri sur la révision : il n'est pas lu comme une preuve.
- **S8 — surprise relative au consensus** : lignes principales où `surprise_consensus` est présente ; L'' construit comme en
  6.2 sur |`surprise_consensus`|. Champs `n_surprise_consensus`, `c_surprise_consensus`, `et_c_surprise_consensus_dk8`. Plus
  proche de la surprise de K20 (donnée moins attente du consensus), mais l'attente date d'un an et manque à quelques tours.

**Fichiers.** L'expérimentateur écrit `temoin.json` et le vérificateur `verification.json`. Les deux contiennent tous les
champs de la règle (section 12), en nombres. Ni l'un ni l'autre n'écrit de verdict.

---

## 7. Le biais mécanique : ce que le plan enlève, ce qui reste

**Le problème** (K20, section 7). Le consensus publié = vraie prévision + bruit ε (composition changeante du panel,
arrondis). Le bruit de l'enquête t entre dans la révision avec le signe + et dans l'erreur avec le signe −. Deux effets :
1. **Atténuation différentielle** : la pente est d'autant plus abaissée que la vraie révision varie peu ; elle l'est plus dans
   la classe des petites nouvelles, ce qui gonfle c.
2. **Sélection sur le bruit** : trier sur |révision| trie aussi sur |ε| ; cela fabrique c > 0.

**Ce que le plan enlève.** La surprise est une variation de la donnée publiée, sans aucune prévision de l'enquête. L'effet 2
disparaît entièrement. L'effet prudent de K20 (le bruit de l'enquête q − 4 dans la surprise poussait c vers le bas) disparaît
aussi.

**Ce qui reste : l'effet 1.** Même formule que K20 : si la vraie pente vaut β partout, c_méca = (2β + k) × (ν/2) × (1/a − 1/A),
avec ν la part du bruit dans la variance des révisions. `biais_mecanique_nu20` le calcule avec ν = 0,20.

**Ordre de grandeur de ν.** Le panel compte 39 à 70 répondants par cellule utilisée. Avec une dispersion des prévisions annuelles de
l'ordre de 0,3 à 0,5 point, des entrées et sorties d'environ 10 à 20 % du panel par tour et des révisions d'écart-type 0,2 à
0,4 point, ν vaut environ 0,02 à 0,10. **ν = 0,20 est une marge de prudence**, comme dans K20. Avec β ≈ 0,19, k ≈ 0,3 et
A/a ≈ 3 (chiffres de K20), c_méca ≈ 0,08 : le plancher vaut alors 0,10. Sous H1 à la taille prédite, A/a tombe sous 1 et le
biais calculé devient négatif : le plancher reste 0,10.

**Non couvert.** Si ν dépasse 0,20 (panel réduit certains tours), le plancher est trop bas (limite 3).

---

## 8. Puissance et capacité de décision

### 8.1 Ordre de grandeur de l'écart-type de c

Trois estimations indépendantes, toutes sans donnée de résultat :
- **Comme si indépendant** : n = 578, un tiers de grandes nouvelles, rapport de variances 3, variance résiduelle plus grande
  après les grandes nouvelles : ET_iid(c) ≈ **0,085** (moyenne de l'écart-type MCO classique dans la simulation de 8.2).
- **K20 transporté** : K20 avait un écart-type de 0,071 pour 1 004 lignes et un effet de plan de 1,22 (820 observations
  effectives). Avec le même effet de plan, 578 lignes donnent 0,071 × √(1 004 / 578) ≈ **0,093**.
- **Simulation** (8.2) : dispersion réelle de ĉ sur 2 000 tirages, scénario central : **0,093** ; écart-type de
  Driscoll-Kraay estimé en moyenne : 0,081.

Le chevauchement des cibles annuelles gonfle peu la variance de c : les révisions de deux tours successifs sont presque
indépendantes, donc les produits révision × résidu le sont aussi, même si les erreurs se ressemblent. Les 578 lignes valent
environ 400 à 500 observations indépendantes, dont 130 à 170 de grandes nouvelles.

**Ce que fait la règle selon l'écart-type estimé (et).** Survie si ĉ > 0,10 + 1,708 × et ; élimination si ĉ < 0,40 −
1,708 × et. Les deux seuils se croisent à et = 0,088 :
- si et < 0,088, il n'y a pas de zone d'indécision : tout ĉ donne survie ou élimination, sauf gardes ;
- si et > 0,088, la zone d'indécision a une largeur 2 × 1,708 × et − 0,30.

| et | survit si ĉ > | éliminée si ĉ < | P(décision) si vrai c = 0 | P(décision) si vrai c = 0,40 |
|---|---|---|---|---|
| 0,08 | 0,237 | 0,263 | 1,00 | 1,00 |
| 0,10 | 0,271 | 0,229 | 0,98 | 0,94 |
| 0,12 | 0,305 | 0,195 | 0,93 | 0,82 |
| 0,14 | 0,339 | 0,161 | 0,85 | 0,72 |

(Loi normale, dispersion réelle prise à 1,2 × et, gardes non comprises.) **La règle reste décisive à 80 % tant que et ne
dépasse pas environ 0,12.** Les trois estimations ci-dessus le placent entre 0,08 et 0,10.

### 8.2 Simulation de la règle complète

**But** (demande du chef de projet) : vérifier, avant le scellement, que la règle aboutit à « survit » ou « éliminée » avec une
probabilité d'au moins 0,80 quand le vrai c vaut 0 et quand il vaut la taille prédite (0,40).

**Ce qui est simulé.** Rien n'est tiré des données de l'enquête de la BCE au-delà de sa **grille** (comptes de présence).
- **Grille réelle** : 3 variables, années cibles 2000-2025, rangs 1 à 8 (et le rang 0, tour T4 de y − 2, pour la première
  révision), les 578 lignes principales exactes de 4.3 et leurs 107 tours, l'exclusion pandémique, les trois épisodes.
- **Nouvelles** : à chaque tour et pour chaque variable, un choc w = part commune aux trois variables (corrélation ρ) + part
  propre ; lois de Student à 4 degrés de liberté (queues épaisses) ; volatilité multipliée par 2 en 2008T2-2009T2, 1,5 en
  2011T4-2013T1, 3 en 2020T1-T2, 2 en 2021-2023.
- **Nouvelle pour une année cible** au tour τ : part κ venant de w (commune aux deux horizons), le reste propre à la cible.
  Prévision rationnelle = somme des nouvelles reçues ; réalisé = prévision rationnelle au rang 8 + nouvelles publiées après
  le dernier tour (écart-type 1,6).
- **Consensus** : ajustement partiel, P_j = P_{j−1} + λ × (prévision rationnelle − P_{j−1}), avec λ = λ₀ = 0,58 après une
  petite nouvelle et λ₁ après une grande ; plus un bruit d'enquête d'écart-type 0,05. Dans ce modèle, la pente de l'erreur sur
  la révision vaut exactement (1 − λ)/λ dans chaque classe ; c = 0 si λ₁ = λ₀.
- **Surprise** = choc du tour + bruit (écart-type 0,5 × volatilité), pour qu'une partie des grandes surprises n'en soient
  pas (effets de base).
- **Calibrage sur les chiffres scellés de K20** (seuls chiffres de résultat utilisés, ceux d'une autre enquête) : avec
  λ₀ = 0,58 et c = 0, la simulation donne b = 0,19 (K20 : 0,194), k = 0,31 (0,294), rapport de variances 2,98 (3,06) et un
  écart-type de c de 0,08 à 0,09 (K20 transporté : 0,093). λ₁ = 0,285 donne un c moyen de 0,40.
- **Règle appliquée en entier** à chaque tirage : réduction, coupure, régression, Driscoll-Kraay à 8 retards, 1,708,
  plancher calculé, contrôle positif, pertinence, trois exclusions d'épisode, indécision, conflit. Le schéma et la taille
  sont supposés conformes.
- **Graine 20261113, 2 000 tirages par cas.**

**Résultats** (survit / éliminée / non concluant, en %, puis probabilité de décision) :

| Scénario | vrai c = 0 | vrai c ≈ 0,40 |
|---|---|---|
| **Central** : ρ = 0,3 ; κ = 0,6 ; Student 4 ; bruit 0,05 | 0,2 / 96,2 / 3,6 → **0,964** | 85,9 / 3,2 / 10,9 → **0,891** (ĉ moyen 0,399) |
| Chocs plus corrélés, queues plus épaisses : ρ = 0,6 ; κ = 0,8 ; Student 3 ; bruit 0,10 | 0,1 / 90,2 / 9,7 → 0,903 | 86,8 / 2,5 / 10,6 → 0,894 (0,403) |
| Surprise deux fois plus bruitée | 0,2 / 96,4 / 3,4 → 0,966 | 83,9 / 2,2 / 13,9 → 0,861 (0,404) |
| Chocs peu corrélés : ρ = 0,1 ; κ = 0,4 | 0,3 / 97,6 / 2,1 → 0,979 | 85,7 / 2,2 / 12,0 → 0,880 (0,407) |
| Épreuve : ρ = 0,8 ; κ = 0,9 ; Student 3 ; volatilité des épisodes doublée ; bruit 0,10 | 1,0 / 82,8 / 16,2 → 0,838 | 84,0 / 2,4 / 13,6 → 0,864 (0,418) |

**Les deux probabilités demandées, scénario central : 0,964 si c = 0 ; 0,891 si c = 0,40.** Les deux dépassent 0,80 dans
tous les scénarios, y compris l'épreuve.

D'où viennent les non-conclusions :
- c = 0 : le contrôle positif échoue 3,5 % du temps (b = 0,19 est petit) ;
- c = 0,40 : la zone d'indécision (5 %) et la pertinence manquante (10 %, quand le rapport des révisions tombe sous 1,25
  et que la borne basse ne passe pas le plancher).

**Ce que la simulation a changé dans le plan.** Une première version reprenait la garde de pertinence de K20 telle quelle
(non concluant dès que le rapport des variances de révision est < 1,25). Sous H1, ce rapport tombe sous 1 (0,6 en moyenne
à c = 0,40) : dans un premier essai à c ≈ 0,34, la règle finissait « non concluant » dans 150 tirages sur 150. D'où
l'amendement 2.2-9.

### 8.3 Ce que le test peut et ne peut pas détecter

Scénario central, mêmes réglages :

| Vrai c | survit | éliminée | non concluant |
|---|---|---|---|
| −0,29 (H2 ou H3 fort) | 0 % | 74 % | 26 % |
| 0 (H0) | 0,2 % | 96 % | 4 % |
| ≈ 0,07 (biais mécanique seul) | 1 % | 96 % | 3 % |
| **≈ 0,19** | **15 %** | **51 %** | **34 %** |
| ≈ 0,40 (prédiction) | 86 % | 3 % | 11 % |

**Lecture.**
- **Le test ne peut pas décider à un effet de 0,20.** Il ne survit qu'une fois sur sept. Il est le plus souvent éliminé, mais
  cette élimination dit « 0,40 est exclu », pas « il n'y a pas d'effet de 0,20 ». Un tiers du temps il ne conclut pas.
- **L'effet qui survit 8 fois sur 10 vaut environ 0,33 à 0,35.** En dessous, une survie est peu probable.
- Le test ne survit pas au seul biais mécanique (1 %).
- Sous H2 ou H3 fort, le test élimine trois fois sur quatre ; le reste du temps, la pente commune tombe près de 0 et le
  contrôle positif échoue (non concluant).
- **Écart-type de Driscoll-Kraay trop petit.** Dans la simulation, il sous-estime la dispersion réelle de ĉ de 10 à 20 %
  (0,081 contre 0,093 au centre). La valeur 1,708 au lieu de 1,645 n'en corrige qu'une partie : si le vrai c vaut 0,10 (le
  plancher), la survie arrive environ 7 % du temps au lieu de 5 % (calcul en loi normale avec la dispersion simulée). Le `n_effectif` publié dépassera souvent n pour cette
  raison.
- Ces chiffres valent pour le modèle simulé (ajustement partiel, une seule source de dépendance à la taille). Un mécanisme
  différent changerait les probabilités, pas la logique.

**Minimum d'échantillon.** 578 lignes principales attendues. Sous **570**, la construction a perdu plus d'un tour entier :
non concluant.

---

## 9. Règle de verdict

Le verdict est calculé par `verdict.py` à partir des chiffres du vérificateur. « Survit » veut dire : dans l'enquête de la
BCE, années cibles 2000-2025, la pente de l'erreur sur la révision du consensus est plus forte après une grande nouvelle sur
les données ; ce supplément dépasse le biais mécanique plausible, est compatible avec la taille prédite (0,40) et ne tient à
aucun épisode isolé ; et le consensus montre une sous-réaction de base.

**Non concluant** si l'une de ces conditions est vraie :
1. `n_violations_schema` > 0 : une ligne qui entre dans le calcul, ou l'ensemble de ces lignes, est hors schéma. On ne juge
   pas une idée sur un fichier douteux. Les anomalies des autres lignes (`n_anomalies_hors_principal`) sont publiées et ne
   comptent pas.
2. `n_principal` < 570 : voir 8.3.
3. `controle_positif_ok` < 1 : ni la pente commune ni la pente des petites nouvelles n'a de borne basse à 90 % au-dessus de 0.
   Si le consensus ne montre aucune sous-réaction de base, une interaction nulle ne dit rien de sa dépendance à la taille.
   Seuil 0 : c'est la frontière entre sous-réaction et absence de sous-réaction.
4. `pertinence_manquante` ≥ 1 : la classe des grandes surprises n'a pas des révisions nettement plus variables (rapport
   < 1,25, comme dans K20 : un tri au hasard donne environ 1, et 1,25 = 12 % d'écart-type en plus), **et** la survie n'est pas
   acquise. Le tri ne montre pas qu'il sépare de grandes nouvelles ; un c faible ne peut donc pas éliminer l'idée. Si en
   revanche la borne basse dépasse le plancher, le tri a manifestement un sens (un tri vide de sens ne produit pas cela, sauf
   par hasard), et le rapport bas est ce que H1 prédit.
5. `marge_indecision` ≥ 0 : l'intervalle à 90 % contient à la fois le plancher et 0,40. Les données ne choisissent pas.
6. `conflit_robustesse` ≥ 1 : l'intervalle est au-dessus du plancher et contient 0,40, mais sans un épisode t tombe sous 1
   sans que c change de signe. La preuve est fragile sans être contredite.
7. Écart entre expérimentateur et vérificateur au-delà de la tolérance sur un champ, ou champ absent (protocole).

**Survit** si aucune condition ci-dessus n'est vraie et si les trois suivantes le sont :
- `borne_basse_moins_seuil` > 0 : tout l'intervalle à 90 % est au-dessus de max(0,10 ; biais calculé). C'est un test
  unilatéral à 5 % (H1 a un sens, c > 0) contre le plancher de biais plutôt que contre 0 (section 7). Seuil repris de K20.
- `borne_haute_ic90` ≥ 0,40 : 0,40 est la prédiction ponctuelle de la fiche, reprise sans changement.
- `t_min_sans_episode` ≥ 1,0 : sans n'importe lequel des trois épisodes, l'interaction reste au moins à un écart-type
  au-dessus de 0. Repris de K20 : le seuil 1,708 dans chaque exclusion coûterait trop de puissance, le signe seul laisserait
  passer un effet porté par un épisode une fois sur deux.

**Éliminée** dans tous les autres cas. Avec les conditions de non-conclusion, cela arrive exactement dans deux cas :
- **(a)** `borne_haute_ic90` < 0,40 : les données excluent, au seuil unilatéral de 5 %, le supplément de 0,40 prédit. Cela
  vaut si c est nul, négatif (H2 ou H3), ou positif mais nettement plus petit que prévu.
- **(b)** le test principal passe, mais `c_min_sans_episode` ≤ 0 : sans un épisode, l'interaction disparaît ou change de
  signe. La réponse à « cela tient-il sans un grand choc ? » est non.

**Tolérances** (écart maximal entre expérimentateur et vérificateur, qui calculent sur le même fichier) : 0 sur les champs
entiers et les indicatrices ; 0,005 sur les coefficients, écarts-types, moyennes et biais ; 0,01 sur les bornes, marges,
plancher et rapports de variances ; 0,02 sur les t ; 1 sur `n_effectif`.

---

## 10. Limites

1. **Le plan n'est pas aveugle.** Le rédacteur connaît le résultat de K20 (c ≈ −0,03), la littérature, l'histoire de la zone
   euro et l'ampleur de 2020. Aucune donnée de résultat de l'enquête de la BCE n'a été lue, mais on ne peut pas prouver que
   ces connaissances n'ont pas orienté les choix.
2. **Le contrôle positif n'est pas aveugle pour l'inflation.** K01 a publié une pente du consensus d'inflation de 0,92 (0,51
   hors 2021-2023). Le contrôle positif devrait donc passer ; il reste informatif pour le PIB et le chômage, et il a été
   demandé, pas choisi en le sachant.
3. **Le biais mécanique est borné, pas supprimé.** Le plancher suppose au plus 20 % de bruit dans la variance des révisions.
4. **La surprise est une variation de la donnée, pas une erreur d'attente.** Une partie des grandes surprises était
   prévisible (effets de base, mouvements annoncés). Le tri en est brouillé, ce qui pousse c vers 0 si l'effet existe. S8
   montre une surprise relative au consensus, sur moins de tours.
5. **Le test porte sur les grandes surprises, pas sur la non-linéarité dans la révision** (K20, limite 3). Une élimination dira
   « pas de sous-réaction plus forte après les grandes surprises », pas « aucune non-linéarité dans la révision ». S7 donne
   la coupure de la fiche, avec son biais.
6. **Réalisés du dernier millésime, chômage à composition fixe `EA21`.** Les révisions du PIB, la refonte de l'enquête sur
   les forces de travail et l'écart entre `EA21` et la zone de l'époque entrent dans l'erreur. Ils sont communs aux 8 lignes
   d'une année cible.
7. **Peu d'années indépendantes.** 26 années cibles ; trois épisodes seulement. L'écart-type de Driscoll-Kraay est trop petit
   de 10 à 20 % dans la simulation (8.3) ; la valeur 1,708 en corrige une partie. S2 (grappes par année cible) le montrera.
8. **Puissance limitée au milieu** : un effet de 0,20 n'est pas détectable (8.3).
9. **Une même surprise pour deux horizons et un modèle de simulation.** Les probabilités de décision dépendent du mécanisme
   simulé (ajustement partiel) ; elles sont robustes aux corrélations et aux queues testées, pas à tout mécanisme.
10. **Choix d'échantillon.** L'exclusion pandémique du PIB et du chômage est un choix (S3 la défait). Les cibles 2000 et 2001
    perdent leur premier rang (structure de l'archive).
11. **Une seule statistique décide.** Les analyses secondaires (une trentaine de chiffres) sont descriptives. Aucune ne peut
    sauver ni tuer l'idée, et l'on ne cherchera pas après coup celle qui « marche ».
12. **Sous-réaction ou lissage.** On écrira « les erreurs suivent davantage les révisions après les grandes surprises »,
    jamais « les prévisionnistes sont irrationnels ».

---

## 11. Ce qu'on écrira dans chaque cas

Dans tous les cas, on publie aussi : c par variable et par horizon, c avant 2020, c avec la pandémie, c avec la médiane, c
avec la coupure de la fiche, c avec la surprise relative au consensus, les écarts-types à 4, 12 et 0 retards et par année
cible, `n_effectif`, `n_anomalies_hors_principal`, et la comparaison avec K20 (c = −0,03, [−0,15 ; +0,09]).

- **Survit** : « Sur 578 couples variable × année cible × tour de l'enquête de la BCE (2000-2025, trois variables), la pente
  de l'erreur sur la révision du consensus est plus forte de c (intervalle à 90 %) dans le tiers des tours qui suivent les
  plus grandes variations de la donnée publiée. C'est plus que le biais de mesure plausible le plus haut, compatible avec le
  +0,40 prédit, et l'effet reste à au moins un écart-type de zéro quel que soit l'épisode retiré. Le résultat contredit
  celui de K20 sur l'enquête américaine ; la dépendance à la taille serait propre à la zone euro ou à ses chocs. »
- **Éliminée, interaction négative** (`borne_haute_ic90` < 0) : « Après les grandes surprises, les erreurs suivent *moins*
  les révisions ; la pente des grandes nouvelles vaut `pente_moyenne_grandes`. Cela va dans le sens des modèles où
  l'attention monte avec les chocs, ou de la sur-réaction aux nouvelles extrêmes. »
- **Éliminée, interaction indistinguable de zéro** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` ≤ 0) : « Comme dans
  l'enquête américaine (K20), la pente de l'erreur sur la révision ne dépend pas de la taille des surprises de façon
  détectable, et les données excluent au seuil de 5 % le supplément de 0,40 prédit. Un effet de 0,20 ne serait pas exclu. »
- **Éliminée, interaction positive mais plus petite que prévu** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` > 0) : « Les
  erreurs suivent un peu plus les révisions après les grandes surprises, mais nettement moins que prédit. Une partie de cet
  écart peut venir du bruit de mesure (plancher `seuil_survie_bas`). »
- **Éliminée, effet porté par un épisode** (`c_min_sans_episode` ≤ 0, test principal passé) : « L'interaction est
  significative sur toute la période, mais elle disparaît sans l'épisode `episode_t_min`. Elle tient à ce seul choc. »
- **Non concluant, par le contrôle positif** (`controle_positif_ok` = 0) : « Le consensus de la BCE ne montre pas de
  sous-réaction de base mesurable sur ces cibles. Une interaction nulle ne dirait rien de sa dépendance à la taille ; on ne
  conclut pas. »
- **Non concluant, par pertinence** (`pertinence_manquante` = 1) : « Les grandes variations de la donnée publiée
  n'entraînent pas de révisions nettement plus grandes, et l'interaction n'est pas établie. Le tri ne montre pas qu'il sépare
  les grandes nouvelles des petites ; la question reste ouverte. »
- **Non concluant, par indécision** (`marge_indecision` ≥ 0) : « L'intervalle à 90 % de c contient à la fois le biais de mesure
  plausible et le +0,40 prédit. On publie l'intervalle et on ne conclut pas. »
- **Non concluant, par conflit** (`conflit_robustesse` = 1) : « L'interaction est au-dessus du plancher sur toute la période et
  reste positive sans chaque épisode, mais à moins d'un écart-type de zéro sans `episode_t_min`. On ne conclut pas. »
- **Non concluant, par les données** (schéma, moins de 570 lignes, fichier manquant, écart entre expérimentateur et
  vérificateur) : « Le test n'a pas pu être mené comme préinscrit. La raison exacte est dans `ecarts.md`, et aucune
  conclusion n'est tirée sur l'hypothèse. »

---

## 12. Règle lisible par machine

```json
{
  "id": "K20-ZE",
  "fichier_analyse": "K20-ZE_analyse.csv",
  "champs_verification": [
    "n_violations_schema",
    "n_anomalies_hors_principal",
    "n_principal",
    "n_tours",
    "n_annees_cibles",
    "n_grands",
    "n_tours_grands",
    "c",
    "et_c_dk8",
    "t_c",
    "borne_basse_ic90",
    "borne_haute_ic90",
    "b_moyen",
    "et_b_moyen_dk8",
    "borne_basse_b_moyen_ic90",
    "b_commun",
    "et_b_commun_dk8",
    "borne_basse_b_commun_ic90",
    "controle_positif_ok",
    "k_moyen",
    "pente_moyenne_grandes",
    "rapport_variance_revision",
    "rapport_variance_ecart_prec",
    "pertinence_manquante",
    "biais_mecanique_nu20",
    "seuil_survie_bas",
    "borne_basse_moins_seuil",
    "marge_indecision",
    "c_sans_E1",
    "c_sans_E2",
    "c_sans_E3",
    "t_sans_E1",
    "t_sans_E2",
    "t_sans_E3",
    "t_min_sans_episode",
    "c_min_sans_episode",
    "episode_t_min",
    "conflit_robustesse",
    "et_c_iid",
    "n_effectif",
    "et_c_dk4",
    "et_c_dk12",
    "et_c_dk0",
    "et_c_grappes_annee",
    "c_avec_pandemie",
    "et_c_avec_pandemie_dk8",
    "c_avant_2020",
    "et_c_avant_2020_dk8",
    "c_annee_en_cours",
    "et_c_annee_en_cours_dk8",
    "c_annee_suivante",
    "et_c_annee_suivante_dk8",
    "c_mediane",
    "et_c_mediane_dk8",
    "c_coupure_revision",
    "et_c_coupure_revision_dk8",
    "n_surprise_consensus",
    "c_surprise_consensus",
    "et_c_surprise_consensus_dk8",
    "c_HICP",
    "c_RGDP",
    "c_UNEM",
    "et_c_HICP_dk8",
    "et_c_RGDP_dk8",
    "et_c_UNEM_dk8"
  ],
  "survit_si": [
    {"champ": "borne_basse_moins_seuil", "operateur": ">", "seuil": 0},
    {"champ": "borne_haute_ic90", "operateur": ">=", "seuil": 0.40},
    {"champ": "t_min_sans_episode", "operateur": ">=", "seuil": 1.0}
  ],
  "non_concluant_si": [
    {"champ": "n_violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "n_principal", "operateur": "<", "seuil": 570},
    {"champ": "controle_positif_ok", "operateur": "<", "seuil": 1},
    {"champ": "pertinence_manquante", "operateur": ">=", "seuil": 1},
    {"champ": "marge_indecision", "operateur": ">=", "seuil": 0},
    {"champ": "conflit_robustesse", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "n_violations_schema": 0,
    "n_anomalies_hors_principal": 0,
    "n_principal": 0,
    "n_tours": 0,
    "n_annees_cibles": 0,
    "n_grands": 0,
    "n_tours_grands": 0,
    "c": 0.005,
    "et_c_dk8": 0.005,
    "t_c": 0.02,
    "borne_basse_ic90": 0.01,
    "borne_haute_ic90": 0.01,
    "b_moyen": 0.005,
    "et_b_moyen_dk8": 0.005,
    "borne_basse_b_moyen_ic90": 0.01,
    "b_commun": 0.005,
    "et_b_commun_dk8": 0.005,
    "borne_basse_b_commun_ic90": 0.01,
    "controle_positif_ok": 0,
    "k_moyen": 0.005,
    "pente_moyenne_grandes": 0.005,
    "rapport_variance_revision": 0.01,
    "rapport_variance_ecart_prec": 0.01,
    "pertinence_manquante": 0,
    "biais_mecanique_nu20": 0.005,
    "seuil_survie_bas": 0.01,
    "borne_basse_moins_seuil": 0.01,
    "marge_indecision": 0.01,
    "c_sans_E1": 0.005,
    "c_sans_E2": 0.005,
    "c_sans_E3": 0.005,
    "t_sans_E1": 0.02,
    "t_sans_E2": 0.02,
    "t_sans_E3": 0.02,
    "t_min_sans_episode": 0.02,
    "c_min_sans_episode": 0.005,
    "episode_t_min": 0,
    "conflit_robustesse": 0,
    "et_c_iid": 0.005,
    "n_effectif": 1,
    "et_c_dk4": 0.005,
    "et_c_dk12": 0.005,
    "et_c_dk0": 0.005,
    "et_c_grappes_annee": 0.005,
    "c_avec_pandemie": 0.005,
    "et_c_avec_pandemie_dk8": 0.005,
    "c_avant_2020": 0.005,
    "et_c_avant_2020_dk8": 0.005,
    "c_annee_en_cours": 0.005,
    "et_c_annee_en_cours_dk8": 0.005,
    "c_annee_suivante": 0.005,
    "et_c_annee_suivante_dk8": 0.005,
    "c_mediane": 0.005,
    "et_c_mediane_dk8": 0.005,
    "c_coupure_revision": 0.005,
    "et_c_coupure_revision_dk8": 0.005,
    "n_surprise_consensus": 0,
    "c_surprise_consensus": 0.005,
    "et_c_surprise_consensus_dk8": 0.005,
    "c_HICP": 0.005,
    "c_RGDP": 0.005,
    "c_UNEM": 0.005,
    "et_c_HICP_dk8": 0.005,
    "et_c_RGDP_dk8": 0.005,
    "et_c_UNEM_dk8": 0.005
  }
}
```
