# F12 — Préinscription du test de mort

Fiche : « L'instrument de protection de la transmission (TPI) a-t-il coupé le lien entre surprises de la BCE et écarts souverains ? »
Rédigée le 2026-11-12 par le rédacteur de préinscription. Aucune analyse n'a été lancée. Ce que j'ai lu des données :
les noms de feuilles et de colonnes de la base EA-MPD, sa feuille `Notes`, sa colonne de dates, la présence ou l'absence de
valeur dans les cellules utiles (jamais les valeurs), l'empreinte du fichier ; pour la Riksbank, la liste des séries et les
dates disponibles. En confirmant que les séries existent, j'ai vu quelques niveaux de rendement : Riksbank du 4 au 15 janvier
2010 (période `crise`, hors du test principal et de S1), et les dernières valeurs de 2026 de séries de la Bundesbank et de la
BCE (hors échantillon). Aucune moyenne, pente ou variation un jour de réunion n'a été calculée ni regardée ; le § 7 ne
contient qu'une simulation sur des paramètres supposés.

Convention : dans le texte, la virgule est décimale ; dans les formules, le fichier et le bloc JSON, c'est le point.

---

## 1. Ce qui reste à tester

Peu de chose, et il faut le dire avant le reste.

- **La question n'est pas neuve.** Le rapport de l'Eurosystème (ECB Occasional Paper n° 372, 2025, graphique 10) montre déjà
  la réponse d'un écart « pays très endettés moins pays peu endettés » à une surprise d'un point de base, avant et après le TPI,
  et conclut que l'instrument a « en partie isolé » les écarts des chocs restrictifs. Le résultat qualitatif que la fiche attend
  est donc déjà affirmé, par l'institution qui a créé l'instrument.
- **Ce que ce graphique ne règle pas** : il ne donne ni les coefficients, ni la période, ni la mesure de la surprise, ni surtout
  un test de la *différence* entre les deux régimes (deux bandes à 90 % qui se chevauchent ou non ne disent pas si la différence
  est distinguable de zéro). Il porte sur des projections locales journalières à dix jours pour six pays, pas sur la fenêtre de
  la réunion. Grosse-Steffen, Lewis et Lhuissier (2026) et Ferrara et Szczerbowicz (2026) ne comparent pas l'avant et l'après juillet 2022.
- **Ce que ce test peut donc ajouter, et rien de plus** : un nombre — la variation de la pente intrajournalière de l'écart
  Italie/Espagne-Allemagne sur la surprise OIS à 2 ans, avec son erreur type — calculé sur données publiques, selon un plan
  scellé, par quelqu'un qui n'a pas intérêt au résultat, et la réponse à une question étroite : *cette baisse est-elle
  distinguable de zéro avec les 26 réunions disponibles ?* C'est une contre-épreuve chiffrée d'une affirmation publiée, pas une découverte.
- **Ce que ce test n'ajoute pas** : l'attribution au TPI. Une comparaison avant-après à une seule date ne sépare pas le TPI du
  cycle de resserrement, de la réduction du bilan, de la souplesse des réinvestissements du programme pandémie ni des nouvelles
  budgétaires nationales. Le rapport de l'Eurosystème a la même limite (sa note 29). Aucune donnée publique gratuite ne permet de la lever (voir § 9).

Conséquence pour la suite du projet : même si la fiche « survit », sa nouveauté est celle d'une réplication indépendante avec
une incertitude honnête. Si elle est « éliminée » ou « non concluante », le résultat utile est que les données publiques ne
suffisent pas à étayer, au jour des réunions, la phrase de l'Eurosystème.

## 2. Question, hypothèse, prédiction chiffrée

**Question.** Dans la fenêtre intrajournalière des réunions de la BCE, la réponse de l'écart de rendement à 10 ans
Italie/Espagne-Allemagne à une surprise sur le taux OIS à 2 ans est-elle plus faible depuis l'annonce du TPI (21 juillet 2022)
qu'entre l'annonce des opérations monétaires sur titres (OMT, 6 septembre 2012) et le TPI ?

**Hypothèse falsifiable.** Avant le TPI, une surprise à la hausse de l'OIS à 2 ans élargit l'écart moyen Italie/Espagne-Allemagne
(pente `b_avant` > 0) ; après le TPI, la pente est plus faible (`d = b_apres − b_avant` < 0).

**Prédiction chiffrée** (reprise de la fiche, transposée telle quelle à l'objet amendé, sans regarder les données) :
- `b_avant` : +0,15 à +0,50 point de base d'écart par point de base de surprise ;
- `b_apres` : −0,10 à +0,10 ;
- `d` : **−0,15 à −0,50**, centre −0,30.
- Placebo pays peu endettés (Pays-Bas, Finlande, données journalières) : variation de pente entre −0,05 et +0,05.

Position par rapport aux travaux proches : même signe que le graphique 10 de l'Eurosystème ; la taille n'y est pas lisible,
donc la fourchette ci-dessus est celle de la fiche, pas une valeur empruntée.

## 3. Amendements déclarés

Le test de la fiche était : MCO Italie seule, réunions de 2010-01 à 2025-10, `Δécart = a + b·ΔOIS2Y + c·Après + d·(Après × ΔOIS2Y)` ;
mort si `b ≤ 0` (unilatéral 5 %, HC3) ou si la valeur p de `d < 0` par rééchantillonnage sauvage dépasse 0,10 ; rang de `d`
parmi des ruptures factices ; comparaison hors échantillon d'erreurs quadratiques. Changements, chacun avec sa raison :

| n° | Changement | Raison |
|---|---|---|
| A1 | Variable expliquée : **moyenne des écarts Italie-Allemagne et Espagne-Allemagne** par réunion, au lieu de l'Italie seule. | L'hypothèse porte sur les pays très endettés, pas sur les nouvelles propres à l'Italie. La surprise ne varie que par réunion : le MCO empilé à deux pays avec effets fixes pays × période et erreurs groupées par réunion donne exactement la même pente que la régression sur la moyenne par réunion ; je définis donc l'estimateur sur cette moyenne. **Gain de précision faible** (les deux écarts bougent ensemble) : l'empilement ne répond pas à la faille de puissance, il la laisse presque entière. |
| A2 | Période d'avant : **2012-10-04 à 2022-06-09 (87 réunions)** au lieu de 2010-01 à 2022-06 (120). La réunion du 2012-09-06 (détails de l'OMT) est exclue comme l'est celle du 2022-07-21. | Appariement sur le régime : des deux côtés de la rupture il existe déjà un filet (l'OMT) et pas de crise existentielle. Comparer à 2010-2012 attribuerait au TPI ce que l'OMT a fait, et ajoute du bruit sans rapport avec les surprises de taux. Coût : 33 réunions de moins ; l'ère des achats nets (2015-2022) reste non appariée (limite, § 9). Les 33 réunions de 2010-2012 restent dans le fichier pour l'analyse secondaire S2. |
| A3 | Inférence : **erreur type HC3 en formule fermée et valeurs critiques de Student fixées** (1,32 et 1,66) ; plus de rééchantillonnage sauvage. | Deux personnes doivent obtenir le même nombre à la troisième décimale ; un rééchantillonnage dépend du générateur aléatoire du logiciel. HC3 est la variante prudente quand quelques observations ont un fort levier, ce qui est le cas ici. |
| A4 | Ajout d'un **seuil de taille** : `d_hat ≤ −0,15` (bas de la fourchette prédite). | Une prédiction chiffrée doit pouvoir échouer sur sa taille, pas seulement sur son signe. |
| A5 | Ajout d'une condition de **robustesse au retrait d'une réunion** : `d` doit rester négatif quelle que soit la réunion retirée. | Avec 26 réunions, deux ou trois grosses surprises portent l'essentiel de la variance du régresseur ; une survie due à une seule journée ne vaut rien. |
| A6 | Ruptures factices : de condition de mort à **analyse descriptive** (S2, fenêtres glissantes de 26 réunions). | Les fenêtres se recouvrent : il n'y a que quatre ou cinq fenêtres indépendantes avant le TPI, donc aucun « rang dans les 10 % » n'a un niveau de test défendable. Les montrer reste utile pour voir si une pente aussi basse existait déjà avant l'instrument. |
| A7 | Comparaison hors échantillon des erreurs quadratiques : **supprimée**. | Redondante avec `d` (si la pente d'après est nulle, le modèle « réponse nulle » gagne), et dominée par une ou deux réunions. |
| A8 | Séparation politique/information par le co-mouvement taux-actions : **supprimée** ; remplacée par S3 (surprises restrictives seulement). | Trois analyses secondaires au plus ; le signe de la surprise répond plus directement à la confusion avec le cycle de resserrement. |
| A9 | Ajout d'un **placebo pays peu endettés** (Pays-Bas, Finlande ; S1), en données journalières. Descriptif. | Le TPI vise les pays vulnérables ; si la pente baisse autant pour des pays que l'instrument ne concerne pas, la baisse n'est pas propre au risque souverain. Descriptif seulement, car la mesure n'est pas la même (journalière, plus bruitée) que la statistique principale : voir § 4. |
| A10 | Clause de **précision** : si `se_d > 0,16` et que l'intervalle contient à la fois 0 et −0,15, le verdict est « non concluant » au lieu de « éliminée ». | Faille des juges : une erreur type du même ordre que l'effet. Au-delà de 0,16, ne pas détecter un effet vrai de −0,30 arrive plus d'une fois sur trois, puis une fois sur deux : l'absence de détection ne tue alors rien honnêtement (§ 7). |
| A11 | La simulation de puissance « scellée avant lecture », qui décidait d'empiler ou non, est remplacée par l'empilement décidé ici (A1) et l'arithmétique du § 7. | Aucune décision ne doit dépendre d'un calcul fait après le scellement. |
| A12 | La prédiction « France trois à cinq fois plus petite » **n'entre pas dans le verdict** ; la France ne sert que de pont entre mesures intrajournalière et journalière (S1). | Une seule statistique principale ; la France a ses propres nouvelles budgétaires en 2024-2025. |
| A13 | Courbes de la BCE (tous émetteurs / AAA), rendements mensuels IRS et FRED : **non utilisés**. | Mensuels, ou agrégats dont la composition change ; ils ne permettent ni placebo par pays ni fenêtre de réunion. |
| A14 | Échantillon **figé au 2025-10-30**, même si le fichier est mis à jour plus tard. | Le fichier en ligne le 2026-11-12 s'arrête à cette date (dernière mise à jour : 4 novembre 2025) ; il n'y a donc pas plus de 26 réunions après le TPI. |

## 4. Données

### 4.1 Source principale — base EA-MPD (Altavilla, Brugnolini, Gürkaynak, Motto et Ragusa)

- URL : `https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx`
- Testée le 2026-11-12 avec curl (agent par défaut) : HTTP 200, 377 116 octets, `Last-Modified: Thu, 20 Nov 2025`.
- sha256 du fichier lu : `f417fb861a305e3cbb871a7571c4899ba6bca003d9e087024d2f3f0744426cef`. Si l'empreinte diffère, l'écrire dans
  `ecarts.md` et continuer : l'échantillon est défini par les dates ci-dessous, pas par l'empreinte.
- Feuille : **`Monetary Event Window`** (variation entre la médiane des cotations avant le communiqué et la médiane après la
  conférence de presse ; 13:25-13:35 → 15:40-15:50 jusqu'en juin 2022, 13:55-14:05 → 15:55-16:05 à partir de juillet 2022, d'après la feuille `Notes`).
- Colonnes utilisées (ligne 1 = en-têtes) : `date`, `OIS_2Y`, `DE10Y`, `IT10Y`, `ES10Y`, `FR10Y`. Unité : points de base.
- Pièges vérifiés : (i) la colonne `date` est une date Excel jusqu'au 2023-10-26, puis **du texte au format `jj/mm/aaaa`** du
  2023-12-14 au 2025-10-30 ; (ii) la feuille a plus de mille colonnes vides à droite ; (iii) 315 lignes, de 1999-01-07 à 2025-10-30.
- Échantillon : les **147 réunions** du 2010-01-14 au 2025-10-30 inclus, réparties par la seule date :

| `periode` | Dates | Réunions | Usage |
|---|---|---|---|
| `crise` | 2010-01-14 à 2012-09-06 inclus | 33 | S2 seulement |
| `avant` | 2012-10-04 à 2022-06-09 inclus | 87 | principal |
| `annonce` | 2022-07-21 | 1 | exclue partout |
| `apres` | 2022-09-08 à 2025-10-30 inclus | 26 | principal |

- Présence vérifiée (sans lire les valeurs) : les six colonnes sont renseignées pour les 147 réunions.
- **Donnée manquante** : une cellule vide ou non numérique dans `OIS_2Y`, `DE10Y`, `IT10Y` ou `ES10Y` pour une réunion `avant`
  ou `apres`. La réunion sort alors de l'échantillon principal, et comme le minimum préinscrit est l'échantillon complet
  (87 et 26), le verdict devient « non concluant ». Aucune imputation.

### 4.2 Source secondaire — rendements journaliers à 10 ans, Sveriges Riksbank (pour S1 seulement)

- URL : `https://api.riksbank.se/swea/v1/Observations/<SERIE>/2009-12-01/2025-11-30` avec `<SERIE>` ∈
  `DEGVB10Y` (Allemagne), `NLGVB10Y` (Pays-Bas), `FIGVB10Y` (Finlande), `FRGVB10Y` (France).
- Testées le 2026-11-12 avec curl (agent par défaut, deux secondes entre les appels) : HTTP 200 pour les quatre ; réponse JSON,
  liste d'objets `{"date": "AAAA-MM-JJ", "value": <rendement en %>}` ; 4 016 à 4 018 observations journalières du 2009-12-01 au 2025-11-28.
  Liste des séries : `https://api.riksbank.se/swea/v1/Series` (HTTP 200). Source indiquée par la Riksbank : Refinitiv.
- Trous connus : pas de cotation les jours fériés suédois. Quatre jours de réunion manquent dans les quatre séries :
  **2012-06-06, 2013-06-06, 2019-06-06, 2024-06-06**. La veille de la réunion du 2013-05-02 manque aussi (1er mai).
- Variation journalière un jour de réunion `t` : `100 × (valeur(t) − valeur(s))`, où `s` est la dernière date cotée strictement
  avant `t`, à condition que `t − s ≤ 5` jours calendaires. Sinon, ou si `t` n'est pas coté : **manquant** (cellule vide).
  Attendu : 85 réunions `avant` et 25 `apres` utilisables pour S1.
- L'heure de cotation n'est pas documentée par l'interface : limite traitée par le contrôle de calage de S1.
- Si l'interface de la Riksbank ne répond pas après cinq essais espacés d'une minute : S1 n'est pas faite, les lignes
  `RIKSBANK` sont écrites avec des cellules vides, c'est noté dans `ecarts.md`, et **le verdict n'en dépend pas**.

### 4.3 Ce qui n'existe pas, et la conséquence pour le plan

Je n'ai trouvé **aucune source publique, gratuite et sans compte de rendements journaliers à 10 ans pour l'Italie, l'Espagne,
le Portugal, la Grèce ou la Belgique** couvrant 2010-2025. Testé le 2026-11-12 : Eurostat `irt_lt_mcby_d` (HTTP 404, « not
available for dissemination ») ; BCE `IRS/D.IT.L.L40.CI.0000.EUR.N.Z` (404 ; la série n'existe qu'en mensuel, `IRS/M.IT...` : 200) ;
BCE `FM/D.IT.EUR.4F.BB.IT10YT_RR.YLD` (404) ; Banque de Grèce (403) ; Banco de Portugal BPstat (réponse vide). La Banque
d'Espagne (`https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv`, 200) ne couvre que l'Espagne ; la
Bundesbank (`BBSIS.D.I.ZAR.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A`, 200) que l'Allemagne. Ni l'une ni l'autre n'est utilisée.

Conséquence : on ne peut pas refaire à l'identique le panel journalier à six pays de l'Eurosystème. Le plan est donc bâti sur
ce qui existe : (i) pour les pays très endettés, les variations **intrajournalières** de l'Italie et de l'Espagne dans EA-MPD,
qui portent la statistique principale ; (ii) pour le placebo, les variations **journalières** des Pays-Bas et de la Finlande
(Riksbank), descriptives parce que la mesure diffère ; (iii) la France, présente dans les deux sources, sert de pont entre les deux mesures.

## 5. Fichier d'analyse

Nom : **`analyse_F12.csv`**, dans `tests-de-mort/F12/`. CSV UTF-8, séparateur virgule, point décimal, une ligne d'en-têtes,
cellule vide pour un manquant, nombres écrits avec au moins quatre décimales. Fichiers bruts conservés dans `tests-de-mort/F12/brut/`.

**Une ligne par (réunion, pays, source).** 147 réunions × 6 = **882 lignes** : pour chaque réunion, trois lignes
`EAMPD` (pays `IT`, `ES`, `FR`) et trois lignes `RIKSBANK` (pays `FR`, `NL`, `FI`).

| Colonne | Type | Unité | Contenu |
|---|---|---|---|
| `date_reunion` | texte `AAAA-MM-JJ` | — | date de la réunion (colonne `date` d'EA-MPD) |
| `pays` | texte | — | `IT`, `ES`, `FR`, `NL` ou `FI` |
| `source` | texte | — | `EAMPD` (fenêtre intrajournalière) ou `RIKSBANK` (variation journalière) |
| `periode` | texte | — | `crise`, `avant`, `annonce` ou `apres`, selon le tableau du § 4.1 |
| `d_ois2y_pb` | réel | point de base | `OIS_2Y` de la feuille `Monetary Event Window`, répété sur les six lignes de la réunion |
| `d_rdt_pays_pb` | réel ou vide | point de base | `EAMPD` : `IT10Y`, `ES10Y` ou `FR10Y` ; `RIKSBANK` : variation journalière du pays (§ 4.2) |
| `d_rdt_de_pb` | réel ou vide | point de base | `EAMPD` : `DE10Y` ; `RIKSBANK` : variation journalière de `DEGVB10Y` |
| `d_ecart_pb` | réel ou vide | point de base | `d_rdt_pays_pb − d_rdt_de_pb` |
| `surprise_restrictive` | entier 0/1 | — | 1 si `d_ois2y_pb > 0`, sinon 0 |

**Contrôles de schéma** (le vérificateur les refait tous et compte ceux qui échouent dans `violations_schema`) :
1. exactement 882 lignes et les 9 colonnes ci-dessus, dans cet ordre ;
2. clé (`date_reunion`, `pays`, `source`) unique ; pour chaque date, exactement les six couples (pays, source) attendus ;
3. 147 dates distinctes, la première 2010-01-14, la dernière 2025-10-30 ; par `periode` : 33, 87, 1, 26 dates ;
4. `periode` cohérente avec les bornes de dates du § 4.1 ;
5. `d_ois2y_pb` jamais vide et identique sur les six lignes d'une même date ;
6. lignes `EAMPD` : aucune cellule vide ; `d_rdt_de_pb` identique sur les trois lignes `EAMPD` d'une même date ;
7. lignes `RIKSBANK` : `d_rdt_pays_pb`, `d_rdt_de_pb` et `d_ecart_pb` sont vides ensemble ou renseignés ensemble ; `d_rdt_de_pb` identique sur les lignes `RIKSBANK` renseignées d'une même date ;
8. `|d_ecart_pb − (d_rdt_pays_pb − d_rdt_de_pb)| ≤ 1e-6` partout où ces cellules sont renseignées ;
9. `surprise_restrictive` vaut 1 si et seulement si `d_ois2y_pb > 0` ;
10. toutes les valeurs numériques renseignées sont finies et de valeur absolue inférieure à 300.

## 6. Statistique

### 6.1 Statistique principale

Lignes utilisées : `source = EAMPD`, `pays ∈ {IT, ES}`, `periode ∈ {avant, apres}`.

Pour chaque réunion `t` : `x_t = d_ois2y_pb` et `y_t = (d_ecart_pb[IT, t] + d_ecart_pb[ES, t]) / 2`.

Pour chaque régime `r ∈ {avant, apres}`, avec `n_r` réunions, moyennes `x̄_r`, `ȳ_r`, et `S_r = Σ (x_t − x̄_r)²` :

```
b_r   = Σ (x_t − x̄_r)(y_t − ȳ_r) / S_r                       (MCO avec constante, par régime)
e_t   = (y_t − ȳ_r) − b_r (x_t − x̄_r)                         (résidu)
h_t   = 1/n_r + (x_t − x̄_r)² / S_r                            (levier)
V_r   = Σ (x_t − x̄_r)² · e_t² / (1 − h_t)²  /  S_r²           (variance HC3 de b_r, sans autre correction)
```

**Statistique principale : `d_hat = b_apres − b_avant`**, en point de base d'écart par point de base de surprise, avec
`se_d = sqrt(V_apres + V_avant)`.

C'est, à l'identique, le coefficient d'interaction `d` du MCO empilé
`d_ecart_pb[c,t] = α_c + γ_c·Après_t + b·x_t + d·(Après_t × x_t) + ε` (effets fixes pays × période), et `se_d` est son erreur
type robuste au regroupement par réunion, version HC3 calculée sur les moyennes par réunion. Pas de pondération, pas
d'écrêtage, pas de variable de contrôle, pas de rééchantillonnage.

Nombres dérivés, tous déterministes :
- `n_avant`, `n_apres` : nombre de réunions utilisées par régime ;
- `b_avant`, `b_apres` ; `se_b_avant = sqrt(V_avant)` ; `t_b_avant = b_avant / se_b_avant` ;
- `d_borne_haute = d_hat + 1.32 × se_d` et `d_borne_basse = d_hat − 1.32 × se_d` (1,32 : quantile unilatéral à 10 % d'une loi de Student à 24 degrés de liberté, soit `n_apres − 2` ; constante fixée, à ne pas recalculer) ;
- `d_max_sans_une` : pour chacune des `n_avant + n_apres` réunions, on la retire, on recalcule `b` du régime touché et donc `d` ; `d_max_sans_une` est le plus grand des `d` ainsi obtenus ;
- `non_informatif` = 1 si (`se_d > 0.16`) et (`d_borne_haute ≥ 0`) et (`d_borne_basse ≤ −0.15`), sinon 0 ;
- `violations_schema` : nombre de contrôles du § 5 qui échouent (0 à 10).

Le seuil 1,66 appliqué à `t_b_avant` est le quantile unilatéral à 5 % d'une loi de Student à 85 degrés de liberté (constante fixée).

### 6.2 Analyses secondaires — descriptives, elles ne changent pas le verdict

Elles sont rapportées par l'expérimentateur dans son compte rendu ; le vérificateur n'a pas à les refaire. Même estimateur
que le § 6.1 (pentes par régime, HC3), seul l'échantillon change.

**S1 — Placebo pays peu endettés (journalier).** Lignes `RIKSBANK` renseignées, `periode ∈ {avant, apres}`.
(a) *Calage* : pente `kappa` du MCO avec constante de `d_rdt_de_pb` (`RIKSBANK`) sur `d_rdt_de_pb` (`EAMPD`), par date ; si
`kappa < 0,5`, la variation journalière ne capte pas la réunion et le placebo est déclaré **non informatif**, sans autre commentaire.
(b) *Placebo* : `y_t` = moyenne des `d_ecart_pb` de `NL` et `FI` ; on rapporte `d_placebo`, `se_placebo` et `d_placebo ± 1,32 × se_placebo`.
(c) *Pont* : `d` pour `FR` en journalier (`RIKSBANK`) et `d` pour `FR` en intrajournalier (`EAMPD`), côte à côte, pour mesurer ce que le changement de mesure fait à l'estimation.
Lecture fixée : si `d_placebo + 1,32 × se_placebo < 0`, on écrit que la baisse de pente **s'observe aussi** pour des pays que le TPI ne vise pas ; sinon, que le placebo **ne la montre pas**, en rappelant qu'il est plus bruité que la mesure principale.

**S2 — Stabilité de la pente avant le TPI (ruptures factices).** Lignes `EAMPD`, `IT` et `ES`, les 120 réunions `crise` + `avant`
dans l'ordre des dates. Pour chacune des 95 fenêtres de 26 réunions consécutives, pente `b_w` de `y` sur `x` avec constante.
On rapporte le minimum, la médiane, le maximum des `b_w`, et `part_fenetres_basses` = part des fenêtres où `b_w ≤ b_apres`.
Graphique : `b_w` selon la date de fin de fenêtre, avec `b_apres` en trait horizontal.
Lecture fixée : si `part_fenetres_basses > 0,10`, on écrit qu'une pente aussi basse que celle d'après TPI **existait déjà** avant l'instrument.

**S3 — Surprises restrictives seulement.** Échantillon principal restreint à `surprise_restrictive = 1` dans les deux régimes.
On rapporte `d_restrictif`, son erreur type et les deux effectifs. Lecture fixée : nombre donné tel quel, sans conclusion, l'effectif d'après TPI étant de l'ordre de la moitié de 26.

## 7. Arithmétique de puissance

Les ordres de grandeur ci-dessous sont **supposés** (souvenir de la littérature sur les fenêtres de réunion), pas lus dans le fichier.

- **Observations effectivement indépendantes** : 113 réunions (87 + 26), pas 226 lignes. Pour une pente, le nombre effectif
  est plus petit encore — de l'ordre de `(Σx²)² / Σx⁴` — parce que quelques grosses surprises portent l'essentiel de `Σx²` ;
  après le TPI il peut tomber sous dix. C'est la raison de HC3 et de la condition de retrait d'une réunion.
- **Erreur type attendue** d'une pente : `σ_e / (σ_x √n)`.
  - Avant : `σ_x` ≈ 3 à 4 pb, `σ_e` ≈ 3,5 à 5 pb, `n` = 87 → `se_b_avant` ≈ 0,11 à 0,18.
  - Après : `σ_x` ≈ 5 à 7 pb (cycle de hausses), `σ_e` ≈ 2,5 à 3,5 pb, `n` = 26 → erreur type ≈ 0,08 à 0,14.
  - Donc `se_d` ≈ **0,13 à 0,22**. La valeur avancée par un juge (0,2) est dans cette fourchette ; la moitié du bruit vient de la période d'avant, pas seulement des 26 réunions.
- **Effet prédit** : −0,15 à −0,50, centre −0,30.
- **Probabilités de verdict** (simulation normale à deux millions de tirages, graine fixe, sur ces erreurs types supposées ; la
  condition de retrait d'une réunion n'est pas simulée et retire encore quelques points à la survie) :

| `se_b_avant` / après → `se_d` | Vérité (`b_avant`, `b_apres`) | survit | non concluant | éliminée |
|---|---|---|---|---|
| 0,10 / 0,08 → 0,13 | effet haut (0,50 ; 0) | 0,99 | 0 | 0,01 |
| | effet central (0,30 ; 0) | 0,82 | 0 | 0,18 |
| | effet bas (0,15 ; 0) | 0,33 | 0 | 0,67 |
| | faux : lien non coupé (0,30 ; 0,30) | 0,09 | 0 | 0,91 |
| | faux : jamais de lien (0 ; 0) | 0,03 | 0 | 0,97 |
| 0,12 / 0,10 → 0,156 | effet haut | 0,97 | 0 | 0,03 |
| | effet central | 0,67 | 0 | 0,33 |
| | effet bas | 0,25 | 0 | 0,75 |
| | faux : lien non coupé | 0,09 | 0 | 0,91 |
| 0,155 / 0,125 → 0,20 | effet haut | 0,87 | 0,12 | 0,02 |
| | effet central | 0,49 | 0,41 | 0,11 |
| | effet bas | 0,18 | 0,62 | 0,20 |
| | faux : lien non coupé | 0,09 | 0,62 | 0,29 |
| 0,19 / 0,15 → 0,24 | effet central | 0,36 | 0,51 | 0,13 |
| | faux : lien non coupé | 0,09 | 0,66 | 0,24 |

**Ce que cela dit, sans fard.**
- Si `se_d ≤ 0,16`, le test fait son travail pour le centre et le haut de la fourchette : une hypothèse fausse est tuée neuf
  fois sur dix, un effet vrai de −0,30 survit deux fois sur trois à quatre fois sur cinq, un effet de −0,50 presque toujours.
- Dans tous les cas, **le bas de la fourchette prédite (−0,15) n'est pas testable** : un effet vrai de cette taille ne
  survit qu'une fois sur trois au mieux. La fiche prédisait une fourchette dont la moitié basse est hors de portée de 26 réunions.
- Si `se_d > 0,16` — ce qui est à peu près aussi probable que l'inverse d'après la fourchette supposée — le test est
  **faible** : il ne peut plus tuer une hypothèse fausse que dans un quart à un tiers des cas, et rend le plus souvent
  « non concluant ». C'est la faille relevée par les juges ; aucun choix de méthode sur données publiques ne la répare, parce
  qu'il n'existe pas d'autres réunions après le TPI dans la base et que l'empilement de pays corrélés n'ajoute presque rien.
  La clause A10 ne fait que l'écrire dans le verdict au lieu de la cacher dans une élimination ou une survie de hasard.
- Faux positifs : une survie arrive au plus une fois sur dix quand rien n'a changé. Le niveau de 10 % unilatéral est celui de la fiche ; il est indulgent.

Temps de calcul : quelques secondes sur un portable (trois téléchargements, des MCO sur 113 points).

## 8. Règle de verdict

Appliquée par le code de l'orchestrateur aux nombres du vérificateur.

1. **Non concluant** si l'une de ces conditions est vraie :
   - `n_apres < 26` ou `n_avant < 87` (une donnée nommée manque) ;
   - `violations_schema > 0` ;
   - `non_informatif ≥ 1`, c'est-à-dire : `se_d > 0,16`, et l'intervalle `[d_borne_basse ; d_borne_haute]` contient à la fois 0 et −0,15 (le test est trop imprécis et sa réponse n'est décisive dans aucun sens) ;
   - l'expérimentateur et le vérificateur diffèrent de plus que la tolérance sur l'un des champs.
2. Sinon, **survit** si les quatre conditions sont toutes vraies :
   - `d_hat ≤ −0,15` (la taille prédite est atteinte) ;
   - `d_borne_haute < 0` (baisse distinguable de zéro, unilatéral 10 %, HC3) ;
   - `t_b_avant ≥ 1,66` (il existait un lien à couper : `b_avant > 0`, unilatéral 5 %, HC3) ;
   - `d_max_sans_une < 0` (le signe ne tient pas à une seule réunion).
3. Sinon, **éliminée**.

Cas particuliers voulus : quand `se_d > 0,16`, la fiche survit encore si la baisse est assez forte pour être significative, et
elle est encore éliminée si `d_borne_basse > −0,15` (le plus petit effet prédit est rejeté). Un « non concluant » par
imprécision est une raison **statistique**, pas une raison de données au sens du protocole.

**Ce que « survit » voudrait dire, et ne voudrait pas dire.** Cela voudrait dire que, dans la fenêtre des réunions, la
sensibilité des écarts italien et espagnol aux surprises de taux a été plus faible sur les 26 réunions qui suivent juillet
2022 que sur les 87 qui séparent l'OMT du TPI, de plus que le bruit d'échantillonnage. Cela **ne voudrait pas dire** que le TPI
en est la cause : la même baisse est attendue si les surprises d'après 2022 sont d'une autre nature (taux directeurs plutôt
qu'achats d'actifs), si la fin des achats nets, la réduction du bilan ou la souplesse des réinvestissements ont joué, ou si
les nouvelles budgétaires ont été plus calmes. Les analyses S1 à S3 éclairent ces lectures sans les départager.
**Ce que « éliminée » voudrait dire** : la baisse prédite n'est pas visible dans cette mesure ; pas que le TPI est sans effet
(il peut agir sur le niveau des écarts ou sur leur queue de distribution plutôt que sur la pente au jour des réunions).

## 9. Limites que le plan ne répare pas

1. **Attribution (la plus grave).** Une rupture unique, datée, sans groupe témoin mesuré de la même façon : le TPI coïncide
   avec la première hausse de taux depuis 2011, la fin des achats nets, la souplesse des réinvestissements du programme
   pandémie, puis la réduction du bilan, des élections et des budgets nationaux. Aucune donnée publique intrajournalière
   n'existe pour des pays témoins ; le placebo journalier (S1) n'est pas comparable terme à terme.
2. **Vingt-six réunions**, dont quelques-unes portent l'essentiel de la variance de la surprise.
3. **Nature des surprises** : avant 2022, taux au plancher et annonces d'achats ; après, décisions de taux. La même variation
   de l'OIS à 2 ans ne porte pas la même nouvelle. La période d'avant n'est appariée que sur l'existence d'un filet (OMT).
4. **La fenêtre d'EA-MPD change d'horaire en juillet 2022**, exactement à la rupture (les horaires de la BCE ont changé).
5. **Deux pays** seulement (Italie, Espagne) ; ni Portugal, ni Grèce, ni Belgique, faute de données publiques.
6. **Effet d'impact seulement** : rien sur la persistance à quelques jours, que le rapport de l'Eurosystème regarde.
7. **Choix de la période d'avant** (après l'OMT) : c'est un jugement ; S2 montre ce que donnent les autres fenêtres, 2010-2012 comprise.
8. **Riksbank** : heure de cotation non documentée, quatre jours de réunion manquants.
9. **Niveau de 10 % unilatéral** et quatre conditions conjointes : le test est indulgent sur le faux positif et sévère sur les petits effets.

## 10. Ce qu'on écrira dans chaque cas

Phrases fixées maintenant ; seuls les nombres entre crochets seront remplis, avec les valeurs du vérificateur (S1, S2 : valeurs de l'expérimentateur).

- **Survit** : « Sur données publiques et selon un plan scellé, la réponse intrajournalière de l'écart moyen
  Italie/Espagne-Allemagne à 10 ans à une surprise d'un point de base sur l'OIS à 2 ans passe de [b_avant] (87 réunions,
  octobre 2012 à juin 2022) à [b_apres] (26 réunions, septembre 2022 à octobre 2025), soit une variation de [d_hat]
  (erreur type [se_d]) ; cette baisse, déjà affirmée par l'Eurosystème, est distinguable de zéro au seuil unilatéral de 10 %,
  mais une comparaison avant-après ne permet pas de l'attribuer au TPI plutôt qu'au changement de régime monétaire ou
  budgétaire (placebo Pays-Bas/Finlande : [d_placebo] ; part des fenêtres d'avant TPI à pente aussi basse : [part_fenetres_basses]). »
- **Éliminée** : « Sur données publiques et selon un plan scellé, la baisse prédite (−0,15 à −0,50) de la réponse
  intrajournalière de l'écart moyen Italie/Espagne-Allemagne aux surprises sur l'OIS à 2 ans après juillet 2022 n'est pas
  établie (pente avant [b_avant], après [b_apres], variation [d_hat], erreur type [se_d] ; condition non remplie : [liste]) ;
  l'hypothèse de la fiche F12 est éliminée telle que préinscrite, ce qui ne montre pas que le TPI est sans effet mais que la
  sensibilité des écarts au jour des réunions ne permet pas de le voir. »
- **Non concluant** : « Le test préinscrit de F12 ne conclut pas ([raison : donnée manquante / schéma violé / écart entre
  expérimentateur et vérificateur / imprécision, avec se_d = [se_d] et un intervalle de [d_borne_basse] à [d_borne_haute] qui
  contient à la fois 0 et −0,15]) : avec 26 réunions après le TPI, les données publiques ne permettent ni de confirmer ni
  d'écarter une baisse de la réponse des écarts, et rien n'est écrit sur l'effet de l'instrument. »

## 11. Règle de verdict lisible par machine

```json
{
  "id": "F12",
  "fichier_analyse": "analyse_F12.csv",
  "champs_verification": [
    "n_avant",
    "n_apres",
    "b_avant",
    "b_apres",
    "d_hat",
    "se_d",
    "d_borne_haute",
    "d_borne_basse",
    "t_b_avant",
    "d_max_sans_une",
    "non_informatif",
    "violations_schema"
  ],
  "survit_si": [
    {"champ": "d_hat", "operateur": "<=", "seuil": -0.15},
    {"champ": "d_borne_haute", "operateur": "<", "seuil": 0},
    {"champ": "t_b_avant", "operateur": ">=", "seuil": 1.66},
    {"champ": "d_max_sans_une", "operateur": "<", "seuil": 0}
  ],
  "non_concluant_si": [
    {"champ": "n_apres", "operateur": "<", "seuil": 26},
    {"champ": "n_avant", "operateur": "<", "seuil": 87},
    {"champ": "violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "non_informatif", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "n_avant": 0,
    "n_apres": 0,
    "b_avant": 0.001,
    "b_apres": 0.001,
    "d_hat": 0.001,
    "se_d": 0.001,
    "d_borne_haute": 0.002,
    "d_borne_basse": 0.002,
    "t_b_avant": 0.01,
    "d_max_sans_une": 0.001,
    "non_informatif": 0,
    "violations_schema": 0
  }
}
```
