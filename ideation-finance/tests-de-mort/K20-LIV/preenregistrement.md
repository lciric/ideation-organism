# K20-LIV — Préinscription : la sous-réaction du consensus grandit-elle avec la taille des nouvelles ? Réplication aveugle sur l'enquête Livingston

Rédigé le 2026-11-13 par le rédacteur de préinscription de K20-LIV. Le rédacteur écrit le texte figé ; il ne lance pas le
test. Il n'a calculé aucune erreur, aucune révision, aucune surprise, aucune moyenne de prévision ou de réalisation, aucune
régression et aucune statistique sur les données de l'enquête Livingston ou sur les séries réalisées. Les seuls calculs faits
sont : des comptes de cellules présentes ou absentes ; des comptes de cellules hors de plages larges (le nombre seulement,
jamais les valeurs) ; une simulation sans aucune donnée (section 8, script `simulation_decision.py`).

**Ce que le rédacteur a lu.**
- Le brief de l'orchestrateur, `tests-de-mort/protocole.md`, `tests-de-mort/verdict.py`, `generation-3/regle-generation-3.md`.
- En entier, dans `tests-de-mort/K20/` : `preenregistrement.md`, `verdict.json`, `lecture-apres-coup.md`. Aucun autre fichier de ce
  dossier : ni fichier d'analyse, ni données, ni scripts, ni rapports.
- La note de nouveauté `generation-3/nouveaute/K20.md`.
- Dans `generation-2/nouveaute/J02.md`, seulement les deux passages qui contiennent le mot « Livingston » (recherche faite pour
  vérifier que l'enquête n'a jamais servi dans ce projet ; elle n'a servi à aucun test).
- La documentation de l'enquête : `livingston-documentation.pdf` (version du 4 avril 2022), en entier.

**Ce que le rédacteur a vu des données** (téléchargées le 2026-11-13, toutes en HTTP 200 sauf mention).
- Fed de Philadelphie, `means.xlsx`, `medians.xlsx` : noms des 16 feuilles et des colonnes ; la colonne `Date` (161 dates) ;
  pour chaque colonne, le nombre de cellules numériques, la première et la dernière date numériques, les dates marquées
  `#N/A` à l'intérieur de cette plage.
- `individualdata.xlsx` : noms des feuilles et des colonnes ; par enquête, le **nombre** de réponses numériques des colonnes
  `_BP`, `_6M`, `_12M` des cinq variables retenues (minimum, médiane, maximum) ; le nombre de réponses hors des plages larges
  du contrôle 6 (zéro).
- `MeanGrowthRate.xlsx`, `MedianGrowthRate.xlsx`, `Alternative_Base_Values.xlsx` : téléchargés, non ouverts, non utilisés.
- FRED, séries `CPIAUCNS`, `CPIAUCSL`, `UNRATE`, `DPRIME`, `DTB3`, `HOUST`, `DGS10` : l'en-tête, la première et la dernière date,
  la liste des dates vides ; pour les séries quotidiennes, le **jour** de la dernière observation non vide de chaque mois
  d'avril, juin, octobre et décembre utile (toujours le 28 ou après).
- FRED `USRECP` et `USREC` (indicateurs de récession NBER) : les mois marqués 1 depuis 1945.
- ALFRED : le code HTTP et la plage de dates de quelques millésimes (`UNRATE` 1961, 1962, 1966, 1969, 1970 ; `CPIAUCNS` 1960 ;
  `CPIAUCSL` 1974, 2005 ; `HOUST` 1971, 1990 ; `DTB3`, `DPRIME` : 404). Aucune valeur lue.
- Des **comptes** de cellules hors de plages larges sur les 548 lignes principales : 3 052 cellules de prévision, 1 644
  cellules réalisées, 43 233 réponses individuelles. Résultat : zéro hors plage. Aucune valeur n'a été affichée.

**Aucune valeur de prévision, aucune valeur réalisée, aucune erreur, révision ou surprise de l'enquête Livingston n'a été
affichée ni calculée.**

---

## 0. Ce qui a déjà été vu

**Le résultat de K20, sur l'enquête des prévisionnistes professionnels (SPF), est connu de tous les rôles.** Chiffres du
vérificateur (`K20/verdict.json`) :
- 1 004 lignes, cinq variables, 223 trimestres cibles (1969-2026) ;
- supplément de pente après une grande surprise : **c = −0,030**, erreur type de Driscoll-Kraay 0,071, **IC à 90 %
  [−0,146 ; +0,086]** ;
- pente de base moyenne b = 0,194 ; pente après les grandes surprises 0,164 ;
- rapport des variances de la révision réduite entre grandes et petites surprises : 3,06 ; k moyen (écart-type de la révision
  sur écart-type de l'erreur) : 0,294 ; biais mécanique calculé avec 20 % de bruit : 0,081 ;
- sans chaque épisode, c va de −0,084 à +0,014 ; par variable, de −0,31 (taux à 3 mois) à +0,17 (déflateur) ;
- verdict scellé : **non concluant**, seulement parce que le contrôle de schéma n° 9 a échoué sur une ligne (IPC 2026T1,
  octobre 2025 absent) qui n'entrait dans aucune régression. Sans cet incident, la règle aurait donné « éliminée ».

Les données du SPF ont donc été vues : un nouveau test sur le SPF ne serait pas aveugle.

**De l'enquête Livingston, rien n'a été vu au-delà de la structure** (liste ci-dessus). L'enquête n'a servi à aucun test de ce
projet. Le rédacteur sait par la littérature que la pente de base erreur-sur-révision a été publiée sur cette enquête
(Coibion et Gorodnichenko 2015, d'après la note de nouveauté de J02), et, par culture générale, que des études anciennes ont
trouvé ses prévisions d'inflation lentes à s'ajuster. Il ne les a pas relues pour ce test. Personne, à sa connaissance, n'a
publié le supplément de pente selon la taille des nouvelles sur cette enquête.

**Ce qui peut avoir orienté le plan, et ce qui ne le peut pas.** Le rédacteur connaît la réponse de K20 (c ≈ 0). Les seuils de
ce test sont ceux de K20, transférés sans réglage (section 9). Les choix propres à K20-LIV (variables, cibles, surprise,
retards, épisodes, bruit) viennent de la structure des fichiers et de la documentation, chacun avec sa raison (section 2).

---

## 1. Question, hypothèses rivales et prédiction chiffrée

**Question.** Dans l'enquête Livingston (Fed de Philadelphie, deux enquêtes par an, en juin et en décembre, depuis 1946), la
sous-réaction du consensus aux nouvelles est-elle plus forte après les grandes surprises ? Et cela tient-il sur plusieurs
grands chocs, pas seulement sur 2021-2023 ? La sous-réaction se mesure, comme dans K20, par la pente positive de l'erreur sur
la révision.

**Définitions courtes** (exactes en section 4). Pour une variable v et un mois cible T (juin ou décembre) :
- l'enquête **s** (mois T − 12) donne la prévision à 12 mois du niveau de T ; l'enquête suivante **s+1** (mois T − 6) donne la
  prévision à 6 mois du **même** niveau ;
- **révision** r = prévision de s+1 − prévision de s ; **erreur** e = réalisé de T − prévision de s+1 ;
- **surprise** : la dernière donnée connue de s+1 (avril ou octobre), moins ce que la trajectoire prévue par s annonçait pour ce
  mois-là ;
- **grande nouvelle** : L = 1 si |surprise| est dans le tiers supérieur de la variable.

**Hypothèses et signe attendu de c**, le supplément de pente de l'erreur sur la révision quand L = 1 (écart-type d'erreur par
écart-type de révision) :

| Hypothèse | Ce qu'elle dit | Signe de c |
|---|---|---|
| H1 — fiche K20 | les prévisionnistes révisent trop peu quand il faudrait réviser beaucoup (réticence aux grandes révisions, lissage) | **c > 0** |
| H0 — rigidité de taille fixe | information rigide ou bruitée à degré constant (Coibion et Gorodnichenko 2012) : la pente ne dépend pas de la taille des chocs | c = 0 |
| H2 — attention qui monte avec les chocs | moins de rigidité après les grands chocs visibles (Coibion et Gorodnichenko 2015 ; Baker, McElroy et Sheng 2020) | c < 0 |
| H3 — sur-réaction aux nouvelles extrêmes | règle linéaire face à des chocs à queues épaisses (de Silva, Larsen-Hallock, Rej et Thesmar 2025) | c < 0, pente des grandes nouvelles parfois négative |
| H4 — artefact de mesure | le bruit du consensus atténue davantage la pente là où les révisions varient peu | c > 0, petit (section 7) |
| H5 — dépendance à la persistance | plus de sous-réaction quand l'inflation est élevée (Kučinskas et Peters 2024) | c > 0 surtout pour l'IPC ; descriptif (S1) |

**Prédiction chiffrée, reprise de la fiche K20 sans changement.**
- Pente de base positive (sous-réaction) : b > 0. C'est le **contrôle positif** (section 6, étape 6).
- Supplément pour les grandes nouvelles : **c ≈ +0,40**, plage +0,2 à +0,6, variables regroupées.

**Attente du rédacteur, hors verdict.** K20 a trouvé c = −0,03 sur le SPF. Les deux enquêtes interrogent des prévisionnistes
américains sur les mêmes chocs. Le rédacteur s'attend donc à c entre −0,2 et +0,15, et plutôt à une élimination. Le plan est
dimensionné pour que cette attente puisse être démentie : il fait survivre c = 0,40 près de 9 fois sur 10 (section 8).

---

## 2. Ce qui passe de K20, ce qui est adapté, et pourquoi

| N° | Élément | K20 (SPF) | K20-LIV (Livingston) | Raison |
|---|---|---|---|---|
| T1 | Statistique | c, supplément de pente commun de l'erreur réduite sur la révision réduite quand L = 1 | **identique** | même question |
| T2 | Consensus | moyenne des réponses ; médiane en secondaire | **identique** (`means.xlsx` ; `medians.xlsx` en S6) | l'arrondi d'une seule réponse pèse moins dans une moyenne |
| T3 | Réduction | par variable, sur l'échantillon principal | **identique** | — |
| T4 | Régression | constantes, effets de classe et pentes de base propres à chaque variable ; c commun | **identique** (16 paramètres) | une pente commune confondrait taille des nouvelles et différences entre variables |
| T5 | Grande nouvelle | tiers supérieur de \|surprise\| par variable ; surprise sur une donnée publiée entre les deux enquêtes | **identique dans le principe** ; surprise adaptée (A3) | trier sur la révision elle-même fabrique l'interaction (bruit, retour à la moyenne) |
| T6 | Seuils | survie : borne basse > max(0,10 ; biais) et borne haute ≥ 0,40 et t ≥ 1 sans chaque épisode ; élimination : borne haute < 0,40 | **identiques** | test de la même prédiction (0,40), avec la même prudence |
| T7 | Pertinence | rapport des variances de la révision ≥ 1,25 | **identique** | sinon le tri ne sépare pas les grandes nouvelles |
| A1 | Cadence | trimestrielle ; révision horizon 4 → horizon 3 | **semestrielle** : prévision à 12 mois de l'enquête s → prévision à 6 mois de l'enquête s+1, même mois cible | l'enquête a deux dates par an et deux horizons (6 et 12 mois) : c'est la seule paire de prévisions successives d'une même cible |
| A2 | Cible | taux de croissance (3 variables), niveaux (2) | **niveaux** ; en log ×100 pour l'IPC et les mises en chantier ; l'IPC **remis dans la base de la série réalisée** par la valeur de base du même questionnaire | l'enquête demande des niveaux. Un taux calculé dans une seule enquête pour le semestre cible exige la prévision du mois courant, qui n'existe que depuis juin 1992 : on perdrait 60 % de l'échantillon. La documentation dit que la valeur de base de l'IPC (`CPI_BP`) est exacte dans toutes les enquêtes |
| A3 | Surprise | réalisé du trimestre de la 1re enquête − sa prévision du trimestre courant | réalisé du **mois de base de s+1** (avril ou octobre) − la valeur que la **trajectoire de s** annonçait pour ce mois (aux 3/4 du chemin entre son mois de base et sa cible à 6 mois) | avant 1992, l'enquête ne prévoit pas le mois courant. Le mois de base de s+1 est la dernière donnée connue des répondants de s+1 (documentation, section 4) |
| A4 | Variables | `PGDP`, `RGDP`, `UNEMP`, `CPI`, `TBILL` | **`CPI`, `UNPR`, `PRIME`, `TBILL`, `TPHS`** | les seules variables dont la prévision et la réalisation se comparent sans conversion douteuse (section 3.2) |
| A5 | Réalisés | première publication (PIB, déflateur), dernier millésime FRED (autres) | **dernier millésime FRED pour tout** | trois des six séries ne sont jamais révisées ; deux ne le sont que par les coefficients saisonniers (section 3.4) |
| A6 | Retards de Driscoll-Kraay | 4 trimestres | **2 semestres** | même durée calendaire (un an) ; chevauchement d'ordre 1 entre erreurs successives (section 6) |
| A7 | Épisodes | 7 fenêtres : pic NBER → creux + 4 trimestres | **11 fenêtres** : pic NBER → creux + 14 mois, fusion des chevauchements, 2020 jointe à 2021-2023 | une ligne utilise des données datées de T − 14 à T ; l'échantillon commence en 1947 (quatre récessions de plus) |
| A8 | Biais mécanique | bruit supposé : 20 % de la variance de la révision | **bruit mesuré** sur les réponses individuelles, puis doublé | limite 2 de K20 : « sans les réponses individuelles, on ne mesure pas ν ». L'enquête Livingston les publie |
| A9 | Contrôle positif | — | **nouveau** : la pente regroupée erreur-sur-révision doit avoir sa borne basse à 90 % au-dessus de 0 (sauf si tout l'intervalle de c est sous 0 : section 6, étape 6) | une interaction nulle ne dit rien si l'enquête ne montre aucune sous-réaction de base |
| A10 | Contrôles de schéma | sur toutes les lignes | **sur les seules lignes principales** ; les anomalies ailleurs sont comptées et rapportées, sans effet sur le verdict | K20 est tombé en « non concluant » pour une ligne hors de toute régression |
| A11 | Pandémie | `RGDP`, `UNEMP` sans les cibles 2020T1-2021T4 | **`UNPR`** sans les 4 cibles dont une donnée ou une enquête tombe en 2020 | même raison (section 3.5) |
| A12 | Minimum | 1 000 lignes (1 004 attendues) | **540 lignes** (548 attendues) | même marge relative, à peu près |

---

## 3. Données

Toutes les sources sont publiques, sans compte. Les fichiers bruts vont dans `tests-de-mort/K20-LIV/donnees/`. Le sha256, la date
et le code HTTP de chaque fichier vont dans `tests-de-mort/K20-LIV/construire_journal.json`. Chaque téléchargement a jusqu'à 5
essais, avec 120 s de délai par essai. **Si un fichier manque, l'expérimenteur s'arrête** : verdict non concluant, pour une
raison de données.

### 3.1 Prévisions — enquête Livingston, Fed de Philadelphie

Page : `https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/livingston-historical-data` (datée du
24 juin 2026).

Préfixe des fichiers :
`https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/livingston-survey/historical-data/`

| Fichier | Rôle | Taille et sha256 au 2026-11-13 |
|---|---|---|
| `means.xlsx` | **principal** : consensus moyen | 168 566 o, `791eaa77…a1f` |
| `medians.xlsx` | secondaire S6 : consensus médian | 162 457 o, `ddb2a9f7…75df` |
| `individualdata.xlsx` | bruit du consensus (section 7) | 6 046 431 o, `fcbfc455…b6f6` |

Documentation : `https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/livingston-survey/livingston-documentation.pdf`
(version du 4 avril 2022, 423 974 o).

Les sha256 complets du rédacteur : `means.xlsx` 791eaa773a3274e8358e9ffe6a197cf814bd77997b5d398d6f7ed27c437e1a1f ;
`medians.xlsx` ddb2a9f7ed51c2964921d04efefbe3363b3d8aa223df0c7efc28723d4a8175df ; `individualdata.xlsx`
fcbfc455057afb3b8b986bc60bfc60f0b35afc5ed1819378efa7b3305534b6f6. La Fed peut ajouter l'enquête de décembre 2026 avant le
téléchargement de l'expérimentateur : cela ne change aucune ligne du test (toutes les cibles sont au plus juin 2026, toutes les
enquêtes au plus décembre 2025). Un sha256 différent est noté dans `ecarts.md` ; ce n'est pas une cause de non-conclusion.

**Structure vérifiée sur les fichiers réels.**
- `means.xlsx` et `medians.xlsx` : 16 feuilles, une par variable. Dans chaque feuille, colonne `Date` puis `<V>_BP`, `<V>_ZM`,
  `<V>_6M`, `<V>_12M`, `<V>_BY`, `<V>_ZY`, `<V>_1Y`, `<V>_2Y` (et `<V>_10Y` pour `RGDPX` et `CPI`).
- La colonne `Date` a **161 dates**, toutes au 1er juin ou au 1er décembre, de **1946-06 à 2026-06**, en demi-années consécutives
  sans trou, dans les cinq feuilles utilisées des deux fichiers. Ce sont les dates d'enquête publiées.
- Une valeur absente est écrite `#N/A` (texte). Aucun autre marqueur.
- Sens des colonnes (documentation, section 3) : `_BP` = dernière valeur historique connue à l'envoi du questionnaire (avril pour
  juin, octobre pour décembre ; dernier jour de ces mois pour les taux) ; `_6M` = prévision pour le mois six mois après le mois de
  l'enquête ; `_12M` = douze mois après. Pour les taux, la prévision vise le **dernier jour** du mois.
- `individualdata.xlsx` : mêmes feuilles ; colonnes `Date`, `ID`, `Category`, puis les mêmes colonnes de prévision ; une ligne par
  répondant et par enquête ; 7 241 lignes par feuille ; mois de `Date` : juin et décembre seulement.

| Variable (feuille) | Colonnes utilisées | Unité publiée | Cellules numériques `_6M` / `_12M` | Réponses individuelles par cellule (minimum sur les cellules utilisées ; maximum) |
|---|---|---|---|---|
| `CPI` (IPC) | `CPI_BP`, `CPI_6M`, `CPI_12M` | indice dans la base de l'époque ; non désaisonnalisé avant l'enquête de décembre 2004, désaisonnalisé ensuite | `_6M` 1946-06 → 2026-06 (161) ; `_12M` 1946-12 → 2026-06 (160) ; `_BP` 161, sans trou | 14 à 64 |
| `UNPR` (chômage) | `UNPR_6M`, `UNPR_12M` | points de %, désaisonnalisé | 1961-06 → 2026-06 (131 chacune), sans trou | 14 à 67 |
| `PRIME` (taux de base bancaire) | `PRIME_6M`, `PRIME_12M` | points, dernier jour du mois | 1981-06 → 2026-06 (91), sans trou | 12 à 62 |
| `TBILL` (bons du Trésor à 3 mois) | `TBILL_6M`, `TBILL_12M` | points, base escompte, marché secondaire, dernier jour du mois | 1992-06 → 2026-06 (69), sans trou | 13 à 59 |
| `TPHS` (mises en chantier) | `TPHS_6M`, `TPHS_12M` | millions de logements, rythme annuel, désaisonnalisé | 1968-12 → 2026-06 (115), absent en 1969-06 seulement | 12 à 65 |

### 3.2 Pourquoi ces cinq variables, et pas les autres

**Retenues** : chacune se compare à sa réalisation sans conversion douteuse.
- `CPI` : prévision en niveau d'indice, avec la valeur de base du questionnaire (`CPI_BP`), **exacte dans toutes les enquêtes**
  selon la documentation. Cela permet de remettre chaque prévision dans la base de la série réalisée (section 4). L'IPC non
  désaisonnalisé n'est jamais révisé.
- `UNPR`, `PRIME`, `TBILL` : des taux, sans année de base.
- `TPHS` : un nombre de logements, sans année de base ; c'est la seule variable d'activité réelle qui le permette.

**Écartées** :
- `RGDPX`, `GDPX`, `IP`, `PPI`, `BFIX`, `CPAT`, `WMFG`, `RTTR` : niveaux en indices ou en dollars. La documentation dit que leurs
  valeurs de base sont **douteuses avant juin 2004** (« to be used with great caution »). Les années de base changent. Les
  données sont révisées fortement (comptes nationaux, production industrielle). Les concepts changent : PNB → PIB en 1992, IPP
  SOP → FD-ID en 2014, SIC → NAICS, bénéfices avec ou sans IVA et CCAdj en 2006. Une prévision faite dans une base et une
  réalisation lue dans une autre fabriqueraient des « erreurs » que personne ne pouvait prévoir.
- `AUTODF` : le concept (ventes au détail d'automobiles, nationales et importées) n'a pas d'équivalent FRED net.
- `TBOND` : 30 ans jusqu'en juin 2002, 10 ans ensuite ; et la série FRED à 30 ans (`DGS30`) manque de février 2002 à février
  2006. Elle aurait ajouté 64 lignes avec trois règles d'exception. La simulation (section 8) montre que le plan tranche sans
  elle.
- `SPIF` (indice boursier) : hors du champ de K20, et seulement depuis 1990.

**Correspondance avec K20** : `CPI` ↔ inflation (`CPI`, `PGDP`) ; `UNPR` ↔ `UNEMP` ; `TBILL` ↔ `TBILL` ; `PRIME` = le taux court
depuis 1981, avant `TBILL` ; `TPHS` = l'activité réelle, à la place de `RGDP`.

### 3.3 Réalisations — FRED

Adresse : `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SÉRIE>`. En-tête vérifié : `observation_date,<SÉRIE>`.

| Variable | Série FRED | Fréquence, couverture vérifiée | Dates vides vérifiées | Valeur utilisée pour un mois M |
|---|---|---|---|---|
| `CPI`, lignes dont l'enquête s+1 est au plus 2004-06 | `CPIAUCNS` (IPC-U, non désaisonnalisé, 1982-84 = 100) | mensuelle, 1913-01 → 2026-10 | **2025-10** | l'observation du mois M |
| `CPI`, lignes dont l'enquête s est au moins 2004-12 | `CPIAUCSL` (désaisonnalisé) | mensuelle, 1947-01 → 2026-10 | **2025-10** | l'observation du mois M |
| `UNPR` | `UNRATE` | mensuelle, 1948-01 → 2026-10 | **2025-10** | l'observation du mois M |
| `PRIME` | `DPRIME` | jours ouvrés, 1955-08-04 → 2026-11-09 | jours fériés | la **dernière observation non vide du mois M** |
| `TBILL` | `DTB3` | jours ouvrés, 1954-01-04 → 2026-11-10 | jours fériés | la **dernière observation non vide du mois M** |
| `TPHS` | `HOUST` (milliers, rythme annuel) | mensuelle, 1959-01 → 2026-09 | aucune | l'observation du mois M, **divisée par 1 000** (millions, comme l'enquête) |

Vérifié pour tous les mois utiles (avril, juin, octobre, décembre de 1980 à 2026 pour `DPRIME`, de 1992 à 2026 pour `DTB3`) :
la dernière observation non vide du mois tombe le 28 ou après. L'enquête vise le dernier jour du mois ; on prend donc la
dernière observation disponible de ce mois.

**La ligne IPC à cheval sur le changement de saisonnalité.** Les prévisions d'IPC sont non désaisonnalisées jusqu'à l'enquête
de juin 2004 et désaisonnalisées à partir de celle de décembre 2004. La seule paire d'enquêtes à cheval est (2004-06 ;
2004-12), cible 2005-06 : sa révision mélangerait deux concepts. Elle est vide par règle (section 4) et sort de l'échantillon
principal.

**Conséquence vérifiée d'octobre 2025** (fermeture de l'administration fédérale, aucune collecte) : la cible 2026-06 de `CPI`
perd sa révision, son erreur et sa surprise (octobre 2025 sert de base à la prévision de décembre 2025) ; la cible 2026-06 de
`UNPR` perd sa surprise. Ces deux lignes sont hors de l'échantillon principal. C'est l'incident qui a rendu K20 non concluant :
ici, il est prévu et il ne touche aucun contrôle (A10).

### 3.4 Politique de millésime : dernier millésime FRED pour tout, et sa limite

**Règle.** Toutes les réalisations (mois cible et mois de base) sont lues dans le **dernier millésime FRED** au jour du
téléchargement par l'expérimentateur, qui note la date dans le journal.

**Pourquoi c'est acceptable ici.**
- `CPIAUCNS` (IPC non désaisonnalisé) n'est **jamais révisé** ; seule la base de l'indice change, et elle s'annule dans les
  rapports (section 4). Le dernier millésime est donc la donnée en temps réel. C'est la série de 115 des 156 lignes IPC principales (cibles 1947-12 à 2004-12).
- `DPRIME` et `DTB3` ne sont jamais révisées. ALFRED n'en a aucun millésime (404, vérifié).
- `UNRATE` et `CPIAUCSL` ne sont révisés que par les coefficients saisonniers (de l'ordre du dixième de point pour le chômage,
  de quelques centièmes de point pour la croissance de l'IPC sur huit mois).
- `HOUST` est révisé (les deux mois suivants, puis les coefficients saisonniers), de quelques pour cent, à comparer à des
  erreurs de prévision semestrielles de l'ordre de 10 à 20 %.

**Ce qu'ALFRED offrirait, et pourquoi on ne le prend pas.** ALFRED a des millésimes pour `UNRATE` (vérifié dès 1961-07),
`CPIAUCNS` (dès 1960), `CPIAUCSL` (dès 1973, avec des fenêtres de 19 mois au début) et `HOUST` (dès 1971). Une règle « première
publication » demanderait un millésime par mois utile (plus de 600 requêtes) et une date de lecture fixe. Les fermetures de
2013 et 2025 ont retardé des publications de plusieurs semaines : une règle de calendrier aurait échoué sur certains mois. C'est
exactement le genre de construction fragile qui a rendu K20 non concluant. Et le gain est petit : la réalisation n'entre que
dans l'erreur (variable expliquée) et dans la surprise (le classement des lignes).

**Limite** (section 10, limite 6). Le réalisé contient des révisions que les prévisionnistes ne pouvaient pas connaître. Dans
l'erreur, c'est du bruit dans la variable expliquée : il élargit l'intervalle, sans biaiser c, sauf s'il est corrélé à la
révision. Dans la surprise, il classe mal quelques lignes près du seuil, ce qui rapproche c de 0.

### 3.5 Pourquoi une exclusion pandémique pour `UNPR` seulement

Le chômage est passé de 3,5 % à 14,7 % entre février et avril 2020. Ses surprises semestrielles habituelles se mesurent en
dixièmes de point : celle de 2020 en vaut des dizaines. Une poignée de lignes pèserait plus que des décennies. Les quatre cibles
`UNPR` dont une donnée, une enquête ou un mois de base tombe en 2020 sortent de l'échantillon principal : 2020-06 (réalisé),
2020-12 (enquête s+1 et mois de base avril 2020), 2021-06 (enquête s de juin 2020), 2021-12 (mois de base octobre 2020).
L'analyse S3 les remet. Les mises en chantier (−30 % en avril 2020), les prix et les taux de 2020 sont grands, mais du même ordre
que 1974, 1980 ou 2008 : ils restent, comme les prix et les taux dans K20. Ce choix vient de ce que tout le monde sait de 2020,
pas des données de l'enquête.

### 3.6 Dates des récessions

FRED `USRECP` (du pic au mois précédant le creux) et `USREC` (du mois suivant le pic au creux) donnent les pics et creux NBER
mensuels : 1948-11/1949-10, 1953-07/1954-05, 1957-08/1958-04, 1960-04/1961-02, 1969-12/1970-11, 1973-11/1975-03,
1980-01/1980-07, 1981-07/1982-11, 1990-07/1991-03, 2001-03/2001-11, 2007-12/2009-06, 2020-02/2020-04.

---

## 4. Définitions exactes

**Lignes.** Une ligne = une variable v × un mois cible T (juin ou décembre). À chaque cible correspond une seule paire
d'enquêtes : `enquete_1` = s, l'enquête du même mois un an avant (T − 12 mois) ; `enquete_2` = s+1, l'enquête suivante dans la
liste publiée (T − 6 mois). La ligne est donc aussi identifiée par (variable, cible, enquête s+1).

**Mois de base.** `mois_ancre_1` = avril si s est une enquête de juin, octobre si c'est une enquête de décembre (même année) ;
`mois_ancre_2` de même pour s+1. Ce sont les mois de `_BP` de la documentation.

**Valeurs lues.**
- `prev_12m_1` = `<v>_12M` de s ; `prev_6m_2` = `<v>_6M` de s+1 ; `prev_6m_1` = `<v>_6M` de s (dans `means.xlsx`).
- `bp_1` = `CPI_BP` de s ; `bp_2` = `CPI_BP` de s+1 (IPC seulement, dans `means.xlsx`, aussi pour les calculs sur médianes).
- `prev_12m_1_med`, `prev_6m_2_med` : comme `prev_12m_1` et `prev_6m_2`, dans `medians.xlsx`.
- `realise_niv`, `ancre_niv_1`, `ancre_niv_2` : la valeur réalisée (section 3.3) des mois T, `mois_ancre_1`, `mois_ancre_2`.

**Unités d'analyse.** g(x) = 100 × ln(x) pour `CPI` et `TPHS` ; g(x) = x pour `UNPR`, `PRIME`, `TBILL`.
- `y_realise` = g(`realise_niv`) ; `y_ancre_1` = g(`ancre_niv_1`) ; `y_ancre_2` = g(`ancre_niv_2`).
- Pour `CPI` (remise dans la base de la série réalisée par la valeur de base du même questionnaire) :
  - `y_prev_1` = 100 ln(`prev_12m_1`) − 100 ln(`bp_1`) + `y_ancre_1` ;
  - `y_prev_2` = 100 ln(`prev_6m_2`) − 100 ln(`bp_2`) + `y_ancre_2` ;
  - `y_prev6_1` = 100 ln(`prev_6m_1`) − 100 ln(`bp_1`) + `y_ancre_1`.
- Pour les autres : `y_prev_1` = g(`prev_12m_1`), `y_prev_2` = g(`prev_6m_2`), `y_prev6_1` = g(`prev_6m_1`).

**Pourquoi la remise en base de l'IPC.** Une prévision de niveau d'IPC est écrite dans la base de l'époque (1935-39 = 100,
1947-49, 1957-59, 1967, puis 1982-84). Ce qui ne dépend pas de la base, c'est le rapport « prévision / valeur de base du même
questionnaire ». On l'ajoute au niveau réalisé du mois de base, lu dans la série réalisée. L'erreur devient alors exactement :
croissance réalisée de l'IPC du mois de base de s+1 au mois cible, moins croissance prévue sur la même période (en log ×100).

**Révision, erreur, surprise.**
- `revision` = `y_prev_2` − `y_prev_1`.
- `erreur` = `y_realise` − `y_prev_2`.
- `surprise` = `y_ancre_2` − [ `y_ancre_1` + 0,75 × (`y_prev6_1` − `y_ancre_1`) ].

**Lecture de la surprise.** L'enquête s connaissait le mois `mois_ancre_1` et prévoyait le mois six mois après elle, huit mois
plus loin. Le mois de base de s+1 est six mois après celui de s, soit aux 6/8 = 3/4 du chemin. La surprise est l'écart entre la
dernière donnée connue de s+1 et le point de la trajectoire de s, supposée régulière, à cette date. Elle ne contient ni la
prévision évaluée (`y_prev_2`) ni le réalisé de la cible.

**Médianes.** `revision_med` et `erreur_med` : mêmes formules avec `prev_12m_1_med` et `prev_6m_2_med` (et, pour l'IPC, les
mêmes `bp_1`, `bp_2` et mois de base).

**Bruit du consensus** (section 7), dans `individualdata.xlsx` :
- `n_rep_1` = nombre de réponses numériques `<v>_12M` à l'enquête s ; `var_rep_1` = variance (diviseur n − 1) de g(réponse) sur
  ces réponses ;
- `n_rep_2`, `var_rep_2` : de même pour `<v>_6M` à l'enquête s+1.
Pour l'IPC, g(réponse) = 100 ln(réponse) : la base de l'indice ne change pas la variance d'un logarithme.

**Règles de vide.**
- Une cellule `#N/A`, vide ou un mois absent de FRED rend vide toute quantité qui en dépend.
- **Ligne IPC 2005-06** (paire 2004-06 / 2004-12, mélange non désaisonnalisé / désaisonnalisé) : `y_prev_1`, `y_prev6_1`,
  `revision`, `surprise` et `revision_med` sont vides par règle ; `serie_realise` = `CPIAUCSL` (celle de s+1).
- Série réalisée de l'IPC : `CPIAUCNS` si `enquete_2` ≤ 2004-06 ; `CPIAUCSL` sinon.

**Indicateurs.**
- `complete` = 1 si `revision`, `erreur` et `surprise` sont toutes présentes ; sinon 0.
- `principal` = 1 si `complete` = 1, `n_rep_1` ≥ 2, `n_rep_2` ≥ 2, `var_rep_1` et `var_rep_2` présentes, et si la ligne n'est pas
  `UNPR` avec `cible` dans {2020-06, 2020-12, 2021-06, 2021-12} ; sinon 0.

---

## 5. Fichier d'analyse

**Nom** : `tests-de-mort/K20-LIV/K20-LIV_analyse.csv`. UTF-8, séparateur virgule, point décimal, première ligne = noms de
colonnes, cellule vide = manquant. Les nombres décimaux sont écrits avec au moins 10 chiffres significatifs.

**Une ligne par variable × cible**, exactement **555 lignes**, y compris quand des valeurs manquent :

| Variable | Cibles (première → dernière) | Lignes | `complete` = 1 | `principal` = 1 |
|---|---|---|---|---|
| `CPI` | 1947-12 → 2026-06 | 158 | 156 | 156 |
| `UNPR` | 1962-06 → 2026-06 | 129 | 128 | 124 |
| `PRIME` | 1982-06 → 2026-06 | 89 | 89 | 89 |
| `TBILL` | 1993-06 → 2026-06 | 67 | 67 | 67 |
| `TPHS` | 1970-12 → 2026-06 | 112 | 112 | 112 |
| **Total** | | **555** | **552** | **548** |

Chaque variable commence à la première cible dont l'enquête s a une prévision à 12 mois et l'enquête s+1 une prévision à 6 mois
(`TPHS` : 6M et 12M manquent en 1969-06, d'où la première cible 1970-12). Toutes s'arrêtent à la cible 2026-06 (enquêtes
2025-06 et 2025-12) : la cible 2026-12 n'est pas encore réalisée.

Tri : variable dans l'ordre `CPI`, `UNPR`, `PRIME`, `TBILL`, `TPHS`, puis `cible` croissante.

**Les trois lignes incomplètes** : `CPI` 2005-06 (mélange, par règle), `CPI` 2026-06 (octobre 2025 absent : révision, erreur et
surprise vides), `UNPR` 2026-06 (octobre 2025 absent : surprise vide). **Les quatre lignes complètes hors échantillon
principal** : `UNPR` 2020-06, 2020-12, 2021-06, 2021-12.

**Lignes principales par épisode** (fenêtres en section 6) : E1 5, E2 4, E3 4, E4 4, E5 13, E6 15, E7 28, E8 12, E9 20,
E10 30, E11 36 ; hors épisode 377. **Dates** : les 548 lignes couvrent 158 semestres cibles distincts (1947-12 à 2026-06, sans
trou).

**Colonnes** (exactement 40, dans cet ordre, aucune autre) :

| # | Colonne | Type | Contenu, unité |
|---|---|---|---|
| 1 | `variable` | texte | `CPI`, `UNPR`, `PRIME`, `TBILL` ou `TPHS` |
| 2 | `cible` | texte | mois cible, forme `AAAA-MM`, MM = 06 ou 12 |
| 3 | `semestre` | entier | 2 × année de la cible + 0 (juin) ou 1 (décembre) |
| 4 | `enquete_1` | texte | enquête s, `AAAA-MM` (date publiée de l'enquête) |
| 5 | `enquete_2` | texte | enquête s+1, `AAAA-MM` |
| 6 | `mois_ancre_1` | texte | mois de base de s, `AAAA-04` ou `AAAA-10` |
| 7 | `mois_ancre_2` | texte | mois de base de s+1 |
| 8 | `prev_12m_1` | décimal | `<v>_12M` de s, moyenne, unité publiée |
| 9 | `prev_6m_2` | décimal | `<v>_6M` de s+1, moyenne |
| 10 | `prev_6m_1` | décimal | `<v>_6M` de s, moyenne |
| 11 | `bp_1` | décimal | `CPI_BP` de s (IPC) ; vide sinon |
| 12 | `bp_2` | décimal | `CPI_BP` de s+1 (IPC) ; vide sinon |
| 13 | `prev_12m_1_med` | décimal | `<v>_12M` de s, médiane |
| 14 | `prev_6m_2_med` | décimal | `<v>_6M` de s+1, médiane |
| 15 | `serie_realise` | texte | `CPIAUCNS`, `CPIAUCSL`, `UNRATE`, `DPRIME`, `DTB3` ou `HOUST` |
| 16 | `jour_realise` | texte | date `AAAA-MM-JJ` de l'observation FRED lue pour la cible |
| 17 | `realise_niv` | décimal | valeur réalisée de la cible (indice ; % ; millions pour `TPHS`) |
| 18 | `jour_ancre_1` | texte | date de l'observation lue pour `mois_ancre_1` |
| 19 | `ancre_niv_1` | décimal | valeur réalisée de `mois_ancre_1` |
| 20 | `jour_ancre_2` | texte | date de l'observation lue pour `mois_ancre_2` |
| 21 | `ancre_niv_2` | décimal | valeur réalisée de `mois_ancre_2` |
| 22 | `y_prev_1` | décimal | section 4 |
| 23 | `y_prev_2` | décimal | section 4 |
| 24 | `y_prev6_1` | décimal | section 4 |
| 25 | `y_realise` | décimal | section 4 |
| 26 | `y_ancre_1` | décimal | section 4 |
| 27 | `y_ancre_2` | décimal | section 4 |
| 28 | `revision` | décimal | `y_prev_2` − `y_prev_1` |
| 29 | `erreur` | décimal | `y_realise` − `y_prev_2` |
| 30 | `surprise` | décimal | section 4 |
| 31 | `revision_med` | décimal | section 4 |
| 32 | `erreur_med` | décimal | section 4 |
| 33 | `n_rep_1` | entier | réponses individuelles `<v>_12M` de s |
| 34 | `var_rep_1` | décimal | leur variance, en unités d'analyse |
| 35 | `n_rep_2` | entier | réponses individuelles `<v>_6M` de s+1 |
| 36 | `var_rep_2` | décimal | leur variance |
| 37 | `complete` | entier | section 4 |
| 38 | `principal` | entier | section 4 |
| 39 | `episode` | texte | `E1` … `E11` si `cible` tombe dans la fenêtre (section 6) ; sinon vide |
| 40 | `grande_nouvelle` | entier | L (section 6) si `surprise` est présente ; sinon vide |

**Contrôles de schéma.** Le vérificateur les refait sur le fichier. **Ils ne portent que sur les lignes principales** : les
lignes où `principal` = 1, et toute ligne que la définition de `principal`, recalculée à partir des colonnes du fichier, met à 1.
`n_violations_schema` = nombre de contrôles violés (0 attendu, 11 au plus) ; un contrôle est violé s'il échoue sur une seule de
ces lignes.

**Anomalies hors des lignes principales.** L'expérimentateur et le vérificateur appliquent aussi les contrôles 3 à 8 aux autres
lignes, sur les cellules présentes, et **listent** les échecs dans leurs rapports. Ce décompte n'est pas un champ de la règle :
il ne peut ni changer le verdict ni créer un écart de tolérance.

**Les dates se contrôlent sur les dates publiées de l'enquête, en année-mois, jamais par un nombre de jours.**

| N° | Contrôle (sur les lignes principales) | Vérifié avant scellement, sur des lignes réelles |
|---|---|---|
| 1 | **Colonnes** : les 40 noms ci-dessus, dans cet ordre, sans autre | noms des colonnes sources vérifiés (section 3) ; le fichier n'existe pas encore |
| 2 | **Clés** : `variable` parmi les cinq codes ; couple (`variable`, `cible`) unique ; `cible` de mois 06 ou 12, dans la plage de la variable (tableau ci-dessus) | oui : grille construite sur la colonne `Date` réelle ; 548 couples distincts |
| 3 | **Dates d'enquête** : `enquete_1` et `enquete_2` figurent parmi les 161 dates publiées de la colonne `Date` (forme `AAAA-06` ou `AAAA-12`) ; `enquete_2` est la date qui suit `enquete_1` dans cette liste ; `cible` est le mois de juin ou de décembre qui suit `enquete_2` dans la suite juin-décembre ; `enquete_1` a le mois de `cible` et l'année précédente ; `mois_ancre_k` = avril (enquête de juin) ou octobre (enquête de décembre) de l'année de `enquete_k` ; `semestre` conforme | oui, sur les 548 lignes : les 161 dates sont au 1er juin ou au 1er décembre, en demi-années consécutives de 1946-06 à 2026-06, dans les cinq feuilles des deux fichiers |
| 4 | **Présence** : présentes `prev_12m_1`, `prev_6m_2`, `prev_6m_1`, `serie_realise`, les trois `jour_*`, les trois `*_niv`, les six `y_*`, `revision`, `erreur`, `surprise`, `n_rep_1`, `var_rep_1`, `n_rep_2`, `var_rep_2`, `grande_nouvelle` ; `bp_1`, `bp_2` présentes si et seulement si `variable` = `CPI` | oui, sur les 548 lignes (présence des cellules sources) |
| 5 | **Séries et jours** : `serie_realise` conforme (section 3.3 ; IPC selon `enquete_2` ≤ 2004-06) ; l'année-mois de `jour_realise`, `jour_ancre_1`, `jour_ancre_2` est `cible`, `mois_ancre_1`, `mois_ancre_2` ; le jour est 01 pour les séries mensuelles | oui, sur les 1 644 observations réalisées des 548 lignes |
| 6 | **Plages des entrées** : `prev_12m_1`, `prev_6m_2`, `prev_6m_1` (et `bp_1`, `bp_2`) dans [50 ; 500] (`CPI`), [1 ; 20] (`UNPR`), [1 ; 25] (`PRIME`), [−1 ; 20] (`TBILL`), [0,2 ; 3,5] (`TPHS`) ; `realise_niv`, `ancre_niv_1`, `ancre_niv_2` dans [15 ; 500] (`CPI`), [1 ; 20], [1 ; 25], [−1 ; 20], [0,2 ; 3,5] | oui, sur les 548 lignes : 3 052 cellules de prévision (dont 1 096 médianes) et 1 644 cellules réalisées, **zéro hors plage** (compte seulement) |
| 7 | **Formules** : les six `y_*`, `revision`, `erreur`, `surprise`, `revision_med`, `erreur_med` égales à leur formule (section 4) à 10⁻⁶ près | présence des opérandes vérifiée ; les valeurs ne sont pas calculées (ce seraient des résultats) |
| 8 | **Bruit** : `n_rep_1`, `n_rep_2` entiers ≥ 2 ; `var_rep_1`, `var_rep_2` ≥ 0 | oui : au moins 12 réponses par cellule utilisée ; 43 233 réponses individuelles, zéro hors des plages du contrôle 6 |
| 9 | **Indicateurs** : sur ces lignes, `complete` = 1 et `principal` = la définition recalculée | oui (présence : 552 et 548) |
| 10 | **Épisodes** : `episode` = `Ek` si et seulement si `cible` est dans la fenêtre k (section 6) ; sinon vide | oui (comptes par épisode ci-dessus) |
| 11 | **Grande nouvelle** : `grande_nouvelle` vaut 0 ou 1, et 1 si et seulement si \|`surprise`\| > Q_v (section 6) | non : la surprise est un résultat, elle n'a pas été calculée |

**Lignes réelles vérifiées.** Les 548 lignes principales sont exactement : `CPI` cibles 1947-12 à 2025-12 sauf 2005-06 ; `UNPR`
1962-06 à 2025-12 sauf 2020-06, 2020-12, 2021-06, 2021-12 ; `PRIME` 1982-06 à 2026-06 ; `TBILL` 1993-06 à 2026-06 ; `TPHS`
1970-12 à 2026-06. Les contrôles 2 à 6, 8, 9 et 10 ont été passés sur chacune, y compris les premières et les dernières lignes
de chaque variable (`CPI` 1947-12 et 2025-12, `UNPR` 1962-06 et 2025-12, `PRIME` 1982-06 et 2026-06, `TBILL` 1993-06 et 2026-06,
`TPHS` 1970-12 et 2026-06), les lignes voisines des exclusions (`CPI` 2004-12 et 2005-12 ; `UNPR` 2019-12 et 2022-06) et les
lignes dont le mois de base est octobre 2025 ou avril 2025 (`PRIME`, `TBILL`, `TPHS` 2026-06 ; toutes les variables 2025-12).

---

## 6. Statistique

Tout se calcule à partir du seul fichier d'analyse, en double précision, sans arrondi intermédiaire. On n'utilise pas
`statsmodels` pour le verdict (il compte les retards par position, pas par semestre).

**Étape 0 — échantillon principal.** Les lignes principales (section 5). n = `n_principal`, 548 attendues.

**Étape 1 — réduction**, pour chaque variable v, sur ses lignes principales :
- moyennes et écarts-types (diviseur n_v − 1) de `revision` et de `erreur` : s_{r,v}, s_{e,v} ;
- z_r = (`revision` − moyenne) / s_{r,v} ; z_e = (`erreur` − moyenne) / s_{e,v} ;
- k_v = s_{r,v} / s_{e,v} ; `k_moyen` = moyenne des cinq k_v.
Toutes les lignes de v reçoivent ces constantes, y compris hors échantillon principal (pour S3).

**Étape 2 — grande nouvelle**, pour chaque variable v :
- Q_v = `numpy.quantile(|surprise|, 2/3)` (méthode linéaire par défaut), sur les lignes principales de v, à partir de la colonne
  `surprise` du fichier ;
- sur toute ligne où `surprise` est présente : L = 1 si |`surprise`| > Q_v (strictement), sinon 0.
Q_v et L sont calculés une fois et gardés dans toutes les analyses.

**Étape 3 — régression principale**, par MCO sur les lignes principales :

  z_e = Σ_v α_v·D_v + Σ_v δ_v·D_v·L + Σ_v b_v·D_v·z_r + **c**·z_r·L + u

- D_v = indicatrice de la variable v ; 16 paramètres, dans cet ordre : 5 constantes, 5 effets de classe, 5 pentes de base, puis
  c ; variables dans l'ordre `CPI`, `UNPR`, `PRIME`, `TBILL`, `TPHS`.
- b_v = pente de l'erreur sur la révision pour les petites nouvelles de v ; b_v + c = pente pour ses grandes nouvelles.
- `b_moyen` = moyenne des cinq b̂_v ; `pente_moyenne_grandes` = `b_moyen` + c.

**Étape 4 — écart-type de Driscoll-Kraay à 2 retards** (groupement par date, puis Newey-West en temps calendaire) :
1. X = matrice des 16 régresseurs ; û = résidus ; h_i = X_i·û_i.
2. Pour chaque semestre τ, du plus petit au plus grand `semestre` de l'échantillon utilisé, **y compris les semestres sans
   ligne** : H_τ = Σ des h_i des lignes de ce semestre (vecteur nul s'il n'y en a pas).
3. Ω = Σ_τ H_τ H_τ' + Σ_{j=1,2} (1 − j/3) × Σ_τ (H_τ H_{τ−j}' + H_{τ−j} H_τ').
4. V = (X'X)⁻¹ Ω (X'X)⁻¹, sans correction de petit échantillon.
5. `et_c_dk2` = racine de l'élément de V qui correspond à c.

Le semestre de la cible et la date de l'enquête s+1 se correspondent un à un : grouper par semestre cible, c'est grouper par date
d'enquête.

**Pourquoi 2 retards.**
- L'erreur de la cible T couvre les nouvelles de la date de l'enquête s+1 (données jusqu'à T − 8) jusqu'à T. Celle de la cible
  suivante, T + 6, couvre les nouvelles depuis l'enquête de T (données jusqu'à T − 2). Elles partagent les nouvelles des deux
  derniers mois avant T : c'est une moyenne mobile d'ordre 1 en semestres. Il faut au moins 1 retard ; avec 2, le poids de
  Bartlett du premier retard vaut 2/3.
- 2 semestres = un an, la même durée que les 4 trimestres de K20.
- Les révisions de deux cibles successives ne se chevauchent pas (deux intervalles d'enquêtes disjoints).
- 4 retards et 0 retard sont rapportés (S2).

**Étape 5.** `t_c` = c / `et_c_dk2` ; `borne_basse_ic90` = c − 1,645 × `et_c_dk2` ; `borne_haute_ic90` = c + 1,645 × `et_c_dk2`.

**Étape 6 — contrôle positif (validation de l'instrument).** Régression de Coibion et Gorodnichenko regroupée, par MCO sur les
lignes principales :

  z_e = Σ_v α_v·D_v + **b**·z_r + u   (6 paramètres)

- `b_regroupe` = b̂ ; `et_b_regroupe_dk2` = son écart-type de Driscoll-Kraay à 2 retards (étape 4, avec cette matrice X) ;
- `borne_basse_b_ic90` = `b_regroupe` − 1,645 × `et_b_regroupe_dk2` ;
- `controle_positif_ok` = 1 si `borne_basse_b_ic90` > 0, **ou** si `borne_haute_ic90` < 0 ; sinon 0.

Pourquoi : une interaction nulle ne dit rien si l'enquête ne montre aucune sous-réaction de base. Pourquoi la pente sur toutes
les lignes : quand c = 0, elle est égale à la pente de base et c'est l'estimation la plus précise (la pente des seules petites
nouvelles, estimée sur des révisions peu dispersées, ne passerait le contrôle qu'environ 8 fois sur 10 même si b = 0,19 ;
section 8). Pourquoi la seconde branche : quand c est très négatif (H2, H3), la pente sur toutes les lignes baisse avec c et
peut passer sous 0 ; sans cette branche, une interaction **nettement négative**, qui contredit H1 sans ambiguïté, deviendrait
« non concluant » (100 % des cas simulés pour c = −0,40). Une interaction dont tout l'intervalle est sous 0 n'est pas une
interaction nulle : la raison d'être du contrôle ne s'y applique pas. Dans tous les autres cas, le contrôle exige bien que la
borne basse à 90 % de la pente regroupée dépasse 0.

**Étape 7 — biais mécanique et plancher** (section 7) :
- m_{v,ℓ} = moyenne de z_r parmi les lignes principales de v avec L = ℓ ;
- a = moyenne de (z_r − m_{v,0})² sur les lignes principales L = 0 ; A = moyenne de (z_r − m_{v,1})² sur les lignes L = 1 ;
- `rapport_variance_revision` = A / a ;
- pour chaque ligne principale i de la variable v : ν_i = (`var_rep_1`/`n_rep_1` + `var_rep_2`/`n_rep_2`) / s_{r,v}² ; c'est la
  part de la variance de la révision due au bruit d'échantillonnage du consensus ;
- ν_v = médiane (`numpy.median`) des ν_i de v ; `nu_mesure` = moyenne des cinq ν_v ;
- `biais_mecanique_mesure` = (2 × `b_moyen` + `k_moyen`) × `nu_mesure` × (1/a − 1/A) ;
- `biais_mecanique_nu20` = (2 × `b_moyen` + `k_moyen`) × 0,10 × (1/a − 1/A) (formule de K20, descriptif) ;
- `seuil_survie_bas` = max(0,10 ; `biais_mecanique_mesure`) ;
- `borne_basse_moins_seuil` = `borne_basse_ic90` − `seuil_survie_bas`.

**Étape 8 — garde de robustesse sur les épisodes (entre dans le verdict).** Fenêtres en mois cibles, bornes comprises, fixées
maintenant. Chacune va du pic NBER au creux NBER + 14 mois ; les fenêtres qui se chevauchent sont fusionnées.

| Code | Fenêtre de cibles | Cibles (juin, décembre) | Contenu |
|---|---|---|---|
| E1 | 1948-11 → 1950-12 | 1948-12 … 1950-12 (5) | récession 1948-49 |
| E2 | 1953-07 → 1955-07 | 1953-12 … 1955-06 (4) | récession 1953-54 |
| E3 | 1957-08 → 1959-06 | 1957-12 … 1959-06 (4) | récession 1957-58 |
| E4 | 1960-04 → 1962-04 | 1960-06 … 1961-12 (4) | récession 1960-61 |
| E5 | 1969-12 → 1972-01 | 1969-12 … 1971-12 (5) | récession 1969-70 |
| E6 | 1973-11 → 1976-05 | 1973-12 … 1975-12 (5) | choc pétrolier, récession 1973-75 |
| E7 | 1980-01 → 1984-01 | 1980-06 … 1983-12 (8) | récessions 1980 et 1981-82 (désinflation de Volcker), fusionnées |
| E8 | 1990-07 → 1992-05 | 1990-12 … 1991-12 (3) | récession 1990-91 |
| E9 | 2001-03 → 2003-01 | 2001-06 … 2002-12 (4) | récession 2001 |
| E10 | 2007-12 → 2010-08 | 2007-12 … 2010-06 (6) | grande récession |
| E11 | 2020-02 → 2023-12 | 2020-06 … 2023-12 (8) | récession 2020 (2020-02 → 2021-06) jointe aux cibles 2021-2023, la poussée d'inflation |

Le « + 14 mois » : une ligne de cible T utilise des données datées de T − 14 (mois de base de s) à T (réalisé). Elle est touchée
par un épisode [P ; C] si T est entre P et C + 14. C'est la règle de K20 (« + 4 trimestres »), transposée à la fenêtre
d'information d'une ligne Livingston.

Pour chaque k = 1 à 11 :
- on refait l'étape 3 sur les lignes principales hors fenêtre k, avec les mêmes z et le même L ;
- écart-type comme à l'étape 4, du plus petit au plus grand semestre restant (les semestres retirés deviennent des semestres sans
  ligne) ;
- `c_sans_Ek` = ĉ_(−k) et t_(−k) = ĉ_(−k) / et_(−k).

Champs : `t_min_sans_episode` = min_k t_(−k) ; `episode_t_min` = le k qui le donne (le plus petit en cas d'égalité) ;
`c_min_sans_episode` = min_k ĉ_(−k).

**Étape 9 — champs dérivés pour la règle.**
- `marge_indecision` = min(`seuil_survie_bas` − `borne_basse_ic90` ; `borne_haute_ic90` − 0,40). Elle est positive ou nulle
  exactement quand l'intervalle à 90 % contient à la fois le plancher et 0,40.
- `conflit_robustesse` = 1 si `borne_basse_ic90` > `seuil_survie_bas`, `borne_haute_ic90` ≥ 0,40, `t_min_sans_episode` < 1 et
  `c_min_sans_episode` > 0, toutes les quatre ; sinon 0.

**Étape 10 — description de la précision.**
- `et_c_iid` = écart-type MCO classique de c, σ̂² = Σû² / (n − 16) ;
- `n_effectif` = n × (`et_c_iid` / `et_c_dk2`)² ;
- `n_grands` = lignes principales avec L = 1 ; `n_dates` = semestres distincts de l'échantillon principal (158 attendus) ;
  `n_dates_grands` = semestres avec au moins une ligne L = 1.

**Convention.** Si n < 50 ou si une matrice X'X est singulière, tous les champs numériques concernés valent 0 et l'incident est
écrit dans `ecarts.md`. Si cela touche le test principal, le verdict est de toute façon non concluant.

**Analyses secondaires — descriptives, hors verdict, calculées et rapportées quoi qu'il arrive.** Chacune reprend les étapes 3
à 5 (Driscoll-Kraay à 2 retards), avec les z et le L de l'échantillon principal, sauf mention contraire.
- **S1 — par variable** : c_v propre à chaque variable (20 paramètres : α_v, δ_v, b_v, c_v). Champs `c_CPI`, `c_UNPR`,
  `c_PRIME`, `c_TBILL`, `c_TPHS` et `et_c_<v>_dk2`. Répond à H5.
- **S2 — inférence** : `et_c_dk4` (4 retards, poids 1 − j/5) et `et_c_dk0` (groupement par semestre seul).
- **S3 — avec la pandémie** : lignes principales plus les quatre lignes `UNPR` 2020-06 à 2021-12 (complètes). Champs
  `c_avec_pandemie`, `et_c_avec_pandemie_dk2`.
- **S4 — depuis 1985** : lignes principales avec `cible` ≥ 1985-06. Champs `c_depuis_1985`, `et_c_depuis_1985_dk2`. Sépare la
  taille des nouvelles de l'époque (grandes surprises concentrées dans les années 1970 et au début des années 1980).
- **S5 — avant 2020** : lignes principales avec `cible` ≤ 2019-12. Champs `c_avant_2020`, `et_c_avant_2020_dk2`.
- **S6 — médianes** : `revision_med` et `erreur_med` à la place de `revision` et `erreur`, réduites de la même façon sur les
  mêmes lignes ; L inchangé. Champs `c_mediane`, `et_c_mediane_dk2`.
- **S7 — coupure de la fiche** : L' = 1 si |z_r| > 1, à la place de L partout dans l'étape 3. Champs `c_coupure_revision`,
  `et_c_coupure_revision_dk2`. Lu avec son biais (section 7), pas comme une preuve.

Rapportés dans les textes des rapports, **hors règle** : les cinq ν_v ; la liste des anomalies hors lignes principales ; pour
l'IPC, le nombre de lignes principales où |ln(`ancre_niv_2`/`bp_2`) − ln(`ancre_niv_1`/`bp_1`)| > 0,005, hors des paires à
cheval sur un changement de base de l'indice (`enquete_2` = 1953-06, 1962-06, 1971-06, 1988-06). Ce dernier chiffre dit si les
valeurs de base du questionnaire sont bien celles d'avril et d'octobre.

**Fichiers.** L'expérimentateur écrit `temoin.json` et le vérificateur `verification.json`. Les deux contiennent tous les champs
de la règle (section 12), en nombres. Ni l'un ni l'autre n'écrit de verdict.

---

## 7. Le biais mécanique : ce que le plan enlève, ce qui reste, et la mesure du bruit

**Le problème** (repris de K20). Le consensus publié est la vraie prévision moyenne plus un bruit ε : l'échantillon de répondants
change, les réponses sont arrondies. Le bruit ε_{s+1} de l'enquête s+1 entre dans la révision avec le signe + et dans l'erreur
avec le signe −. D'où deux effets :
1. **Atténuation différentielle.** La pente erreur-sur-révision est tirée vers le bas d'autant plus que la vraie révision varie
   peu. Dans la classe des petites nouvelles, le bruit pèse une plus grande part : la pente y est plus abaissée, donc c est
   gonflé.
2. **Sélection sur le bruit**, si l'on triait sur la révision : le tri prendrait les grandes valeurs de ε.

**Ce que le plan enlève.** La classe dépend de la surprise, qui ne contient pas le bruit de l'enquête s+1 : l'effet 2 disparaît.
La surprise contient le bruit de l'enquête s (via `y_prev6_1`, avec le poids −0,75). Ce bruit entre dans la révision (signe −)
mais pas dans l'erreur : trier sur |surprise| ajoute un peu de bruit à la révision dans la classe L = 1, ce qui pousse c **vers
le bas**, contre l'hypothèse. Sens prudent.

**Ce qui reste : l'effet 1.** En variables réduites, si la vraie pente vaut β partout, la pente mesurée dans la classe C vaut
β − (2β + k)(ν/2)/var(z_r | C), où ν est la part du bruit (des deux enquêtes) dans la variance de la révision et k = s_r/s_e.
D'où un c purement mécanique : c_méca = (2β + k)(ν/2)(1/a − 1/A).

**Ce qui change par rapport à K20 : ν est mesuré.** K20 supposait ν = 0,20, « une marge de prudence d'environ deux fois la valeur
centrale », faute de réponses individuelles (limite 2 de K20). L'enquête Livingston publie ces réponses. La variance
d'échantillonnage d'une moyenne de N réponses est σ²/N. Pour chaque ligne, la part du bruit des deux enquêtes dans la variance
de la révision est ν_i = (σ²_s/N_s + σ²_{s+1}/N_{s+1}) / s_r². On prend la médiane par variable (robuste aux enquêtes atypiques),
la moyenne des cinq (`nu_mesure`), puis on **double** : ν_LIV = 2 × `nu_mesure`, d'où le facteur `nu_mesure` = ν_LIV/2 dans
`biais_mecanique_mesure`. Le doublement reprend la prudence de K20 et couvre ce que l'échantillonnage ne mesure pas (arrondis
communs, base d'IPC arrondie par Livingston de 1985 à 1988).

**Pourquoi la mesure surestime plutôt le biais.** Elle traite les bruits de deux enquêtes successives comme indépendants. Or ce
sont en bonne partie les mêmes répondants : leurs écarts persistants à la moyenne se retrouvent dans les deux consensus et
s'annulent dans la covariance erreur-révision. Le biais vrai est donc plus petit que la mesure.

**Le plancher** reste celui de K20 : **max(0,10 ; `biais_mecanique_mesure`)**. La survie exige que tout l'intervalle à 90 % soit
au-dessus du biais mécanique plausible le plus haut, et au moins à 0,10.

**Ordre de grandeur attendu, sans donnée.** Avec 40 à 50 réponses et des dispersions de l'ordre d'un point (IPC sur 8 à
14 mois, en log ×100) ou de quelques dixièmes de point (chômage), ν est de l'ordre de 0,02 à 0,08, comme dans K20. Avec les
dispersions de K20 (rapport 3,06, k = 0,29, b = 0,19) et ν_LIV = 0,10 à 0,16, le biais vaut 0,04 à 0,06 : le plancher sera 0,10.
Si les cibles en niveau donnent k ≈ 1 et un rapport ≈ 5, il vaut environ 0,13 : le plancher monte d'autant (section 8, S-b).

**Ce qui n'est pas couvert.** Vers le bas : la dispersion des prévisions monte en période agitée, donc le bruit est plus grand
dans la classe L = 1, ce qui réduit c_méca (plancher prudent). Vers le haut : un bruit commun à tous les répondants d'une
enquête (une base mal imprimée sur le questionnaire) n'apparaît pas dans la dispersion ; le doublement est censé le couvrir,
sans preuve (limite 3).

---

## 8. Puissance et simulation de décision

**Méthode.** Script `tests-de-mort/K20-LIV/simulation_decision.py`, graine fixe 20261113, **4 000 tirages par valeur de c**.
Il n'ouvre aucun fichier de données. Il applique la règle de la section 9, étape par étape (réduction, tiers supérieur, 16
paramètres, Driscoll-Kraay à 2 retards par semestre, plancher, onze exclusions d'épisode, contrôle positif, conditions de
non-conclusion), à des panels simulés de **mêmes dimensions que l'échantillon principal réel** : 548 lignes, 5 variables
(156, 124, 89, 67, 112 lignes), 158 semestres, les mêmes lignes dans chaque épisode. Ces dimensions viennent de la seule
présence des cellules.

**Processus simulé.**
- Surprise vraie s* par ligne : une part commune aux variables d'un même semestre (corrélation ρ) et une part propre.
- Révision vraie r* = s* + η : η est réglée pour que le rapport des variances de la révision entre grandes et petites
  nouvelles vaille celui de K20.
- Bruit du consensus de chaque enquête, de variance telle que ν = 0,05 (milieu de la plage 0,02-0,12 de K20) ; la révision
  publiée contient ε_{s+1} − ε_s, l'erreur publiée −ε_{s+1}, la surprise −0,75 ε_s.
- Erreur : pente b sur r*, plus c sur r* quand L = 1, plus un aléa avec la même part commune ρ et une moyenne mobile d'ordre 1
  (θ = 0,3, le chevauchement).
- Volatilité groupée : une échelle par semestre, log-AR(1) de persistance 0,7 et d'écart-type 0,3, qui multiplie surprise,
  révision et aléa.
- ρ est réglé pour que la moyenne de (et_dk2 / et_iid)² égale l'effet de plan scellé de K20.

**Dispersions prises dans les chiffres scellés de K20** (`K20/verdict.json`) : b = 0,1936 (`b_moyen`) ; k = 0,2943
(`k_moyen`) ; rapport des variances 3,0635 ; effet de plan (0,070685 / 0,063872)² = 1,2247.

**Résultats du scénario principal** (4 000 tirages par ligne ; survit / éliminée / non concluant) :

RESULTATS_PRINCIPAL

**Les deux probabilités exigées : P(éliminée | c = 0) = P_ELIM ; P(survit | c = 0,40) = P_SURV.** Les deux dépassent 0,80.

**Seuils implicites** (écart-type ≈ ET_MOYEN, plancher 0,10) : survit si ĉ > SEUIL_SURV environ ; éliminée si
ĉ < SEUIL_ELIM environ. La bande d'indécision est étroite : le plan tranche presque toujours. Un effet vrai survit 8 fois
sur 10 à partir de c ≈ EFFET_80.

**Sensibilités** (4 000 tirages, hors exigence) :

RESULTATS_SENSIBILITE

**Lecture.**
LECTURE_SIMULATION

**Minimum d'échantillon.** 548 lignes principales sont attendues, comptées sur les fichiers réels. Sous **540** (plus de 8
lignes perdues de façon imprévue), la construction a un problème : verdict non concluant.

---

## 9. Règle de verdict

Le verdict est calculé par `verdict.py` à partir des chiffres du vérificateur. « Survit » veut dire : dans l'enquête Livingston,
1947-2026, cinq variables, la pente de l'erreur sur la révision du consensus est plus forte après une grande surprise ; ce
supplément dépasse nettement le biais mécanique plausible, est compatible avec la taille prédite (0,40), et ne tient à aucun
épisode isolé.

**Non concluant** si l'une de ces conditions est vraie :
1. `n_violations_schema` > 0 : un contrôle échoue sur une ligne principale. On ne juge pas une idée sur un fichier douteux. Les
   anomalies hors des lignes principales ne comptent pas (A10).
2. `n_principal` < 540 (section 8).
3. `rapport_variance_revision` < 1,25 : la classe des grandes surprises n'a pas des révisions nettement plus grandes ; le tri ne
   sépare pas les grandes nouvelles des petites. Avec un tri au hasard, le rapport vaudrait environ 1 ; on demande 25 % de
   variance en plus (12 % d'écart-type), comme K20.
4. `controle_positif_ok` < 1 : l'enquête ne montre pas de sous-réaction de base (borne basse à 90 % de la pente regroupée ≤ 0),
   et l'interaction n'est pas nettement négative. Une interaction nulle ne dirait alors rien.
5. `marge_indecision` ≥ 0 : l'intervalle à 90 % contient à la fois le plancher et 0,40. Les données ne choisissent pas.
6. `conflit_robustesse` ≥ 1 : l'intervalle est au-dessus du plancher et contient 0,40, mais retirer un épisode fait tomber t
   sous 1 sans changer le signe. La preuve est fragile sans être contredite.
7. Écart entre expérimentateur et vérificateur au-delà de la tolérance, ou champ absent (protocole).

**Survit** si aucune condition ci-dessus n'est vraie et si les trois suivantes le sont :
- `borne_basse_moins_seuil` > 0 : tout l'intervalle à 90 % est au-dessus de max(0,10 ; biais mesuré). Test unilatéral à 5 % ;
  le plancher remplace 0 parce qu'une partie de c peut être mécanique (section 7). Le 0,10 est le plancher absolu de K20 :
  un supplément plus petit que 0,1 écart-type n'aurait pas d'intérêt économique et serait à portée du biais.
- `borne_haute_ic90` ≥ 0,40 : 0,40 est la prédiction ponctuelle de la fiche, inchangée. Une borne haute sous 0,40 veut dire que
  les données excluent, au seuil unilatéral de 5 %, la taille prédite.
- `t_min_sans_episode` ≥ 1,0 : sans n'importe lequel des onze épisodes, l'interaction reste à au moins un écart-type au-dessus
  de 0. Seuil de K20 : il bloque la plupart des effets portés par un seul épisode pour un coût de puissance presque nul ; 1,645
  dans chaque exclusion coûterait trop, le signe seul ne bloquerait qu'une fois sur deux.

**Éliminée** dans tous les autres cas, soit :
- **(a)** `borne_haute_ic90` < 0,40 : les données excluent le supplément de 0,40 prédit. Cela vaut si c est nul, négatif (H2,
  H3), ou positif mais nettement plus petit que prévu ;
- **(b)** le test principal passe, mais `t_min_sans_episode` < 1 avec `c_min_sans_episode` ≤ 0 : sans un épisode,
  l'interaction disparaît ou change de signe.

**Tolérances** (écart maximal entre expérimentateur et vérificateur, qui calculent sur le même fichier) : 0 sur les champs
entiers ; 0,001 sur `nu_mesure` ; 0,005 sur les coefficients, écarts-types, moyennes et biais ; 0,01 sur les bornes, marges,
plancher et rapport de variances ; 0,02 sur les t ; 1 sur `n_effectif`.

---

## 10. Limites

1. **La décision repose sur les dispersions de K20.** Les cibles de Livingston sont des niveaux : la révision contient la
   surprise réalisée, donc elle varie sans doute plus entre les classes (rapport ≈ 5 plutôt que 3) et plus près de l'erreur
   (k ≈ 1 plutôt que 0,3). Dans ce cas (S-b), LIMITE_SB
2. **La surprise est interpolée.** L'enquête s ne prévoit pas le mois de base de s+1 ; on suppose une trajectoire régulière
   entre son mois de base et sa cible à 6 mois. Si les prévisionnistes attendaient une trajectoire courbe, une partie de la
   « surprise » est cette courbure. Cela classe mal certaines lignes et rapproche c de 0 : l'erreur joue contre H1, pas pour
   elle.
3. **Le biais mécanique est mesuré, pas éliminé.** La mesure ne voit que le bruit d'échantillonnage et les arrondis
   individuels. Un bruit commun à tous les répondants d'une enquête n'y est pas ; le doublement est censé le couvrir.
4. **Données anciennes.** Les données d'avant 1990 viennent des fichiers de Joseph Livingston : arrondis forts des niveaux,
   mois de la valeur de base de l'IPC incertain (mars ou avril, septembre ou octobre selon la documentation), base arrondie de
   1985 à 1988. Le diagnostic hors règle de la section 6 dira combien de lignes IPC ont une base instable.
5. **Cibles en niveau.** Dans K20, trois variables sur cinq avaient des cibles de croissance, sans donnée réalisée entre les
   deux enquêtes. Ici, la révision d'un niveau contient la donnée réalisée entre les deux enquêtes. Le signe de c se compare à
   K20 ; sa taille exacte, pas tout à fait.
6. **Réalisés au dernier millésime** (section 3.4) : un peu de bruit dans l'erreur et dans le classement.
7. **Écart-type de Driscoll-Kraay.** Avec 158 semestres, des grandes nouvelles groupées et des queues épaisses, il est souvent un
   peu trop petit, ce qui rend la survie un peu trop facile. S2 (4 retards, 0 retard) le dira, sans corriger le verdict.
8. **Époque et composition.** De 1947 à 1961, seul l'IPC est dans le panel ; les grandes surprises se concentrent dans les
   années 1970 et au début des années 1980, quand la rigidité était plus faible selon Coibion et Gorodnichenko (2015). S4 sépare
   en partie la taille de l'époque.
9. **Indépendance partielle vis-à-vis du SPF.** Certains prévisionnistes répondent aux deux enquêtes, et les chocs sont les
   mêmes. Une élimination ici et un c nul dans K20 sont deux mesures concordantes, pas deux expériences indépendantes.
10. **Le plan n'est pas aveugle sur la question.** Le rédacteur connaît le c de K20. Aucune donnée de résultat de Livingston n'a
    été lue, et les seuils sont ceux de K20 ; on ne peut pas prouver que cette connaissance n'a orienté aucun choix.
11. **Une seule statistique décide.** Les analyses secondaires sont descriptives ; aucune ne peut sauver ni tuer l'idée.
12. **Sous-réaction ou lissage.** Une pente positive peut venir de prévisionnistes rationnels mais mal informés, ou d'un
    lissage voulu. On écrira « les erreurs suivent davantage les révisions », jamais « les prévisionnistes sont irrationnels ».

---

## 11. Ce qu'on écrira dans chaque cas

- **Survit** : « Dans l'enquête Livingston (548 couples variable × cible, 1947-2026, cinq variables), la pente de l'erreur sur
  la révision du consensus est plus forte de c (intervalle à 90 %) dans le tiers des cas qui suivent les plus grandes surprises.
  C'est plus que le biais de mesure plausible le plus haut, compatible avec le +0,40 prédit, et l'effet reste à au moins un
  écart-type de zéro quel que soit l'épisode retiré. Le résultat contredit K20 (c = −0,03 sur le SPF) : la différence entre les
  deux enquêtes devient la question. » On donne à côté : `n_effectif`, c par variable, depuis 1985, avec la médiane, avec la
  coupure de la fiche.
- **Éliminée, interaction négative** (`borne_haute_ic90` < 0) : « Après les grandes surprises, les erreurs suivent *moins* les
  révisions ; la pente des grandes nouvelles vaut `pente_moyenne_grandes`. Cela va dans le sens de l'attention qui monte avec les
  chocs (Coibion et Gorodnichenko 2015) ou de la sur-réaction aux nouvelles extrêmes (de Silva et coauteurs 2025). Avec K20,
  deux enquêtes américaines disent non à H1. »
- **Éliminée, interaction indistinguable de zéro** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` ≤ 0) : « La pente de
  l'erreur sur la révision ne dépend pas de la taille des surprises de façon détectable ; les données excluent au seuil de 5 %
  le supplément de 0,40 prédit. Avec K20 (c = −0,03 sur le SPF), la réponse américaine est non. »
- **Éliminée, interaction positive mais plus petite que prévu** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` > 0) : « Les
  erreurs suivent un peu plus les révisions après les grandes surprises, mais nettement moins que prédit ; une partie de cet
  écart peut venir du bruit de mesure (plancher `seuil_survie_bas`). »
- **Éliminée, effet porté par un épisode** (`c_min_sans_episode` ≤ 0, test principal passé) : « L'interaction est
  significative sur toute la période, mais disparaît sans l'épisode `episode_t_min`. La plus forte sous-réaction aux grandes
  nouvelles tient à ce seul choc. »
- **Non concluant, par indécision** (`marge_indecision` ≥ 0) : « Avec environ `n_effectif` observations effectives,
  l'intervalle à 90 % de c contient à la fois le biais plausible et le +0,40 prédit. On publie l'intervalle et on ne conclut
  pas. »
- **Non concluant, par conflit** (`conflit_robustesse` = 1) : « L'interaction est au-dessus du plancher sur toute la période et
  reste positive sans chaque épisode, mais à moins d'un écart-type de zéro sans `episode_t_min`. On ne conclut pas. »
- **Non concluant, par le contrôle positif** (`controle_positif_ok` = 0) : « L'enquête ne montre pas de sous-réaction de base
  (borne basse de la pente regroupée `borne_basse_b_ic90`) ; un supplément nul ne dirait rien. L'instrument ne permet pas de
  répondre. »
- **Non concluant, par pertinence** (`rapport_variance_revision` < 1,25) : « Les grandes surprises n'entraînent pas de
  révisions nettement plus grandes ; le tri ne sépare pas les grandes nouvelles des petites. »
- **Non concluant, par les données** (schéma sur une ligne principale, moins de 540 lignes, fichier manquant, écart entre
  expérimentateur et vérificateur) : « Le test n'a pas pu être mené comme préinscrit. La raison exacte est dans `ecarts.md`, et
  aucune conclusion n'est tirée sur l'hypothèse. »

**Règle d'aveuglement pour la suite.** L'expérimentateur et le vérificateur de K20-LIV n'ouvrent aucun fichier d'un autre
dossier de `tests-de-mort/`, sauf `protocole.md` et `verdict.py`. S'ils l'ont fait, ils l'écrivent dans `ecarts.md`.

---

## 12. Règle lisible par machine

JSON_BLOCK
