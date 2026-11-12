# H16 — Préinscription du test de mort

Fiche : « Les surprises de la BCE sont-elles vraiment des surprises ? »
Rédigée le 2026-11-12 par le rédacteur de préinscription. **Aucune analyse n'a été lancée.**

Ce que j'ai lu des données, et rien d'autre : les noms de feuilles et de colonnes de la base EA-MPD, sa feuille `Notes`, sa
colonne de dates (pas la colonne `OIS_1Y`) ; les premières et dernières lignes des fichiers FRED, de la courbe américaine et
du fichier Ken French, pour en fixer la disposition ; pour chaque réunion, la date de la dernière observation disponible de
chaque série (pour vérifier qu'aucun prédicteur ne manquera). Aucune moyenne, régression ni statistique n'a été calculée sur
des données réelles ; aucune valeur de la cible n'a été regardée. Le § 7 repose sur une simulation à données **synthétiques**
(tirages aléatoires, paramètres supposés), qui ne lit aucun fichier.

Convention : dans le texte, la virgule est décimale ; dans les formules, le fichier et le bloc JSON, c'est le point.

---

## 1. Ce que ce test ajoute, et ce qu'il n'ajoute pas

- **La prévisibilité dans l'échantillon est déjà publiée, trois fois.** Sur la base EA-MPD et l'OIS à 1 an : R² de 20 % avec dix
  prédicteurs dont des données payantes (Worms 2025, 187 annonces) ; R² de 3,66 % avec quatre prédicteurs proches de ceux de la
  fiche (Altavilla, Gürkaynak, Kind et Laeven 2025) ; R² ajusté de 8 à 13 % sur le rendement à 2 ans (Kerssenfischer et
  Schmeling 2024). La fiche donnait ce point pour « incertain » : il ne l'est pas.
- **Ce qui manque** dans ces trois travaux : un test **hors échantillon**. Tous estiment une seule régression sur toute la
  période, donc avec des coefficients que personne ne connaissait au moment des réunions. Kerssenfischer et Schmeling
  l'écartent explicitement (leur note 22).
- **Ce que ce test ajoute, et rien de plus** : une prévision faite réunion par réunion, avec les seules données publiques et
  gratuites datées d'avant la réunion et des coefficients estimés sur le seul passé, comparée à la prévision la plus simple
  (la moyenne passée). La question est donc étroite : *un observateur muni de cinq séries gratuites et d'une régression linéaire
  aurait-il prévu les surprises de la BCE mieux que leur moyenne passée, de 2010 à 2025 ?*
- **Ce que ce test n'ajoute pas** : il ne dit pas *pourquoi* une surprise serait prévisible (erreur d'anticipation ou prime
  de risque, § 9) ; il ne compare pas la BCE à la Fed (aucun test hors échantillon équivalent n'a été trouvé pour la Fed, la
  phrase de la fiche « celles de la BCE passent un test que celles de la Fed ne passent pas » est retirée) ; et un échec ne
  contredit pas les trois résultats publiés, parce que Bauer et Swanson attendent précisément une prévisibilité « ex post »
  (dans l'échantillon) sans prévisibilité « ex ante ».

## 2. Question, hypothèse, prédiction chiffrée

**Question.** La variation de l'OIS à 1 an dans la fenêtre « événement monétaire » des réunions de la BCE, rapportée à sa
volatilité récente, est-elle prévisible hors échantillon, sur les 147 réunions du 14 janvier 2010 au 30 octobre 2025, à
partir de cinq variables publiques datées strictement d'avant la réunion ?

**Hypothèse falsifiable (amendée).** Oui : la prévision récursive bat la moyenne passée (R² hors échantillon > 0), et
l'écart est distinguable du hasard (test de Clark-West, unilatéral 5 %).

**Le signe : deux lectures rivales, aucune n'entre dans le verdict.**
- *Lecture A (celle de la fiche, d'après Bauer et Swanson pour la Fed)* : la banque centrale réagit aux nouvelles plus que le
  marché ne le croit ; de bonnes nouvelles (actions en hausse) annoncent une surprise restrictive : coefficient **positif**
  sur les actions.
- *Lecture B (Altavilla et coauteurs 2025)* : le marché surestime la réactivité de la BCE ; coefficient **négatif** sur les
  actions (−0,443 sur l'OIS 1 an, significatif à 5 %). Worms (2025) trouve un coefficient non significatif sur les actions et
  un coefficient négatif sur la surprise de la réunion précédente.

La fiche prédisait le signe de la lecture A ; le seul chiffre publié sur ce point va dans l'autre sens. La statistique
principale ne dépend d'aucun signe : à chaque réunion, la prévision utilise les coefficients que le passé donne, quels qu'ils
soient. Les signes sont rapportés à part (analyse S1), avec une règle de lecture écrite ici. On ne pourra donc pas choisir
après coup la lecture qui arrange.

**Prédiction chiffrée.**
- *Celle de la fiche* (reprise telle quelle, écrite sans voir les données) : R² de 5 à 10 % dans l'échantillon, R² hors
  échantillon de 2 à 6 %.
- *Celle du rédacteur, corrigée par la note de nouveauté* (écrite sans voir les données) : R² dans l'échantillon de 2 à 6 %
  sur les 298 réunions utilisables ; `r2_oos` entre −3 % et +3 %, centre 0 ; `cw_t` entre 0,5 et 2,5, centre 1,5. Autrement dit, je
  m'attends à un résultat près des seuils, et je tiens l'élimination pour au moins aussi probable que la survie (§ 7).
- La fiche ne meurt pas si sa fourchette de taille est fausse : elle meurt si la prévisibilité hors échantillon n'est pas
  établie (§ 8).

## 3. Amendements déclarés

Le test de la fiche était : cible normalisée par l'écart-type des 16 réunions précédentes ; cinq prédicteurs ; coefficients
estimés une seule fois sur 1999-2009 puis gelés ; évaluation sur 2010-2025 contre la prévision « zéro » ; mort si le R² hors
échantillon est ≤ 0 ou si Clark-West donne p > 0,10 ; analyses secondaires par fenêtre et placebo un jour sans réunion.

| n° | Changement | Raison |
|---|---|---|
| A1 | **Coefficients réestimés avant chaque réunion sur tout le passé disponible** (fenêtre croissante, § 6), au lieu d'une estimation unique gelée fin 2009. | Faille principale des trois juges : des coefficients de 1999-2009 appliqués à quinze ans de taux plancher, d'achats d'actifs puis de resserrement biaisent le test vers le nul. La fenêtre croissante fait entrer chaque régime dans l'estimation dès qu'il est observé. Elle n'a aucun paramètre à régler, donc rien à ajuster après coup. Dans la simulation du § 7, elle fait aussi bien que le gel ou mieux (à l'erreur de simulation près), et beaucoup mieux quand la prévisibilité n'apparaît qu'après 2010 (survie 0,41 contre 0,18). Une fenêtre glissante de 100 réunions a été envisagée et écartée comme statistique principale : elle coûte environ 5 points de R² en bruit d'estimation contre 2 pour la fenêtre croissante, et ne fait mieux que si les coefficients changent de signe ; elle est rapportée en S2. |
| A2 | **Référence : la moyenne passée de la cible, estimée sur la même fenêtre**, au lieu de la prévision « zéro ». | Les deux modèles doivent être emboîtés et estimés avec la même information : la question devient « les cinq prédicteurs ajoutent-ils quelque chose à une constante ? ». Sinon une surprise moyenne non nulle (par exemple une prime de risque constante) compterait comme de la prévisibilité. C'est le R² hors échantillon de Campbell et Thompson, avec le test de Clark et West fait pour ce cas. La référence « zéro » de la fiche est rapportée en S2. |
| A3 | **Seuil de Clark-West : 5 % unilatéral (1,645)** pour survivre, au lieu de 10 %. | Dire que les surprises de la BCE sont prévisibles en temps réel va contre leur usage comme instrument dans des dizaines d'articles ; une chance sur dix de le dire à tort est trop. Le rédacteur a aussi fait plusieurs choix (plancher, fenêtre) : un seuil strict les compense. |
| A4 | **Zone grise → « non concluant »** : si `cw_t ≥ 1,282` (le seuil de la fiche) sans que les conditions de survie soient toutes remplies. | Faille des juges : zone non concluante large pour un R² vrai de 1 à 4 %, que la règle binaire de la fiche cachait. Conséquence voulue : aucun résultat que la fiche aurait compté comme une survie ne devient une élimination. |
| A5 | Ajout d'une condition : **la statistique de Clark-West reste ≥ 1,282 quand on retire n'importe quelle réunion** de l'évaluation. | Une cible divisée par une volatilité glissante a des valeurs extrêmes aux changements de régime (2015, 2022). Une survie due à une seule réunion ne vaut rien. |
| A6 | **Le signe sort du verdict** ; deux lectures rivales (§ 2) ; signes rapportés en S1. | Note de nouveauté : le signe publié sur les actions est opposé à celui de la fiche. La règle doit juger la prévisibilité, pas un signe choisi après coup. |
| A7 | **Normalisation de la cible conservée et définie exactement** : écart-type (dénominateur 15) des 16 surprises précédentes, **plancher à 0,25 point de base**. Aucune année n'est retirée, aucune réunion n'est pondérée autrement. | C'est le traitement des années de taux plancher, fixé avant de voir les données : chaque réunion pèse en unités de sa volatilité récente, connue avant la réunion. Le plancher évite de diviser par presque zéro quand les cotations sont figées (la note de nouveauté compte 17 zéros exacts en 1999-2001) ; en dessous d'un quart de point de base, l'écart-type mesure la grille de cotation, pas des nouvelles. Le nombre de réunions où le plancher joue est rapporté. La version en points de base bruts et le découpage par régime sont en S3. |
| A8 | **Liste des prédicteurs figée** (§ 4.3) : rendement des actions européennes, Brent, euro-dollar, taux américain à 2 ans, tous sur 60 observations ; cible normalisée de la réunion précédente. Ce sont les cinq de la fiche ; aucun n'est ajouté ni retiré. | La fiche les avait fixés ; les changer maintenant serait construire une autre idée. Précisions ajoutées : rendements en logarithmes ; rendement total (`Mkt-RF` + `RF`) ; pas de conversion du dollar à l'euro, parce que le rendement en dollars et la variation de l'euro-dollar entrent tous deux dans la régression, qui peut donc former elle-même le rendement en euros (en logarithmes, c'est leur différence). |
| A9 | **Datation** : chaque prédicteur s'arrête à la dernière observation datée strictement avant le jour de la réunion ; pas de retard supplémentaire. | La fiche demandait « un jour de retard » pour les clôtures américaines. Une clôture américaine datée de la veille tombe vers 22 h, heure de Francfort, la veille ; la fenêtre de la réunion s'ouvre à 13 h 25 (13 h 55 depuis juillet 2022). « Strictement avant le jour de la réunion » suffit donc. |
| A10 | **Échantillon d'évaluation inchangé** : les 147 réunions du 2010-01-14 au 2025-10-30 ; base figée à cette dernière date. | Avec une estimation récursive, on aurait pu commencer l'évaluation plus tôt et gagner une soixantaine de réunions. Je ne le fais pas : ce serait un choix d'échantillon du rédacteur, le gain de puissance est faible, et garder la fenêtre de la fiche permet de comparer avec son test d'origine (S2). |
| A11 | **Placebo un jour sans réunion : supprimé. Lecture séparée communiqué / conférence de presse : supprimée de ce test.** | Le placebo demande l'OIS quotidien hors réunions, absent des sources publiques vérifiées. La lecture par fenêtre est reportée au projet si la fiche survit : trois analyses secondaires au plus, et 43 dates n'ont pas de conférence de presse. |
| A12 | **Affirmations corrigées** : le R² publié pour la Fed est d'environ 16 % (et non 10 %) ; « la BCE passe un test que la Fed ne passe pas » est retiré. | Note de nouveauté, points 3 et 5. |
| A13 | La garde de la fiche (« l'agent d'estimation ne reçoit que les lignes jusqu'en 2009 ») est remplacée par les trois rôles du protocole. | Une estimation récursive a besoin de toutes les lignes. La protection vient d'ailleurs : spécification scellée, statistique sans aucun choix restant, recalcul par un vérificateur indépendant. |
| A14 | Taux américain à 2 ans : `SVENY02` (fiche) ; **repli sur FRED `DGS2`** si le fichier de la Réserve fédérale est injoignable après cinq essais. | Éviter un « non concluant » pour une panne de serveur ; le repli est noté dans `ecarts.md`. |

## 4. Données

Toutes les adresses ont été testées le 2026-11-12 avec curl depuis cette machine. Les fichiers bruts sont conservés dans
`tests-de-mort/H16/donnees/`, avec leur empreinte sha256 dans le compte rendu de l'expérimentateur.

### 4.1 Cible — base EA-MPD (Altavilla, Brugnolini, Gürkaynak, Motto et Ragusa)

- URL : `https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx` — HTTP 200, 377 116 octets, `Last-Modified: Thu, 20 Nov 2025`.
- sha256 du fichier lu : `f417fb861a305e3cbb871a7571c4899ba6bca003d9e087024d2f3f0744426cef`. Si l'empreinte diffère, l'écrire
  dans `ecarts.md` et continuer : l'échantillon est défini par les dates, pas par l'empreinte.
- Feuille : **`Monetary Event Window`**. D'après la feuille `Notes` : variation entre la médiane des cotations de 13:25-13:35
  (avant le communiqué) et celle de 15:40-15:50 (après la conférence de presse) jusqu'en juin 2022 ; 13:55-14:05 et
  15:55-16:05 à partir de juillet 2022.
- Colonnes utilisées (ligne 1 = en-têtes) : **`date`** (colonne 1) et **`OIS_1Y`** (colonne 6). Unité : points de base.
- Pièges vérifiés : (i) `date` est une date Excel pour les rangs 1 à 299, puis **du texte `jj/mm/aaaa`** du rang 300
  (14/12/2023) au rang 315 ; (ii) 46 colonnes nommées, puis environ mille colonnes vides à droite.
- **315 réunions**, triées, sans doublon, du 1999-01-07 (rang 1) au 2025-10-30 (rang 315). Repères : rang 17 = 1999-09-23 ;
  rang 18 = 1999-10-07 ; rang 168 = 2009-12-03 ; rang 169 = 2010-01-14. Les réunions postérieures au 2025-10-30, si le
  fichier est mis à jour, ne sont pas utilisées.
- D'après la note de nouveauté, `OIS_1Y` est numérique pour les 315 dates. Une cellule vide ou non numérique est une
  **donnée manquante** : la réunion est marquée `exclue`, sans imputation.

### 4.2 Séries des prédicteurs

| Série | URL | Disposition vérifiée | Valeur manquante |
|---|---|---|---|
| Brent, dollars le baril | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU` (200) | en-tête `observation_date,DCOILBRENTEU` ; dates `AAAA-MM-JJ` ; depuis 1987-05-20 | cellule vide après la virgule |
| Euro-dollar, dollars pour un euro | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXUSEU` (200) | en-tête `observation_date,DEXUSEU` ; depuis 1999-01-04 | cellule vide |
| Taux américain à 2 ans, en % | `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv` (200, 16,7 Mo) | 9 lignes de préambule ; **en-tête à la ligne 10** (`Date,BETA0,…`) ; colonne **`SVENY02`** (70ᵉ) ; dates `AAAA-MM-JJ` ; depuis 1961-06-14 | `NA` |
| Repli (A14) | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2` (200) | en-tête `observation_date,DGS2` | cellule vide |
| Actions Europe, % par jour, en dollars | `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_3_Factors_Daily_CSV.zip` (200, 64 819 octets) | un seul fichier `Europe_3_Factors_Daily.csv` ; 6 lignes de préambule ; **en-tête à la ligne 7** (`,Mkt-RF,SMB,HML,RF`, première colonne sans nom = date `AAAAMMJJ`) ; cellules entourées d'espaces ; depuis 19900702 ; pas de pied de page ; millésime lu : « 202609 Bloomberg database » | `-99.99` (aucune dans ce millésime) |

Colonnes utilisées dans le fichier Ken French : `Mkt-RF` et `RF`. Rendement de marché du jour : `r = Mkt-RF + RF` (en %).

### 4.3 Construction des cinq prédicteurs (fixée maintenant)

Pour une réunion de date `D` et une série donnée, on ne garde que les observations **valides** (non manquantes), dans l'ordre
des dates ; chaque série a son propre calendrier, on ne reporte aucune valeur. Soit `i` la position de la dernière observation
valide de date **strictement inférieure à `D`**, et `v[i]` sa valeur.

| Colonne | Définition | Unité |
|---|---|---|
| `act_eu_60j_pct` | `100 × Σ ln(1 + r[j]/100)` sur les 60 rendements valides `j = i−59 … i` | % (log) |
| `brent_60j_pct` | `100 × ln(v[i] / v[i−60])` | % (log) |
| `eurusd_60j_pct` | `100 × ln(v[i] / v[i−60])` | % (log) |
| `us2a_60j_pp` | `v[i] − v[i−60]` | point de pourcentage |
| `cible_prec_norm` | cible normalisée (§ 5) de la réunion de rang précédent dans EA-MPD | écart-type |

Règles : (i) la date de `v[i]` est écrite dans la colonne `date_fin_*` correspondante ; (ii) si cette date précède `D` de
plus de 10 jours calendaires, ou si `i−60` n'existe pas, le prédicteur est **manquant** (cellule vide) ; (iii) une réunion de
rang ≥ 18 dont un prédicteur manque est marquée `exclue`.

Vérifié sur les seules dates : pour les 298 réunions de rang 18 à 315, chaque série a une observation valide dans les 7 jours
(Brent) ou les 3 jours (les autres) qui précèdent, et 60 observations d'historique. **Attendu : aucune réunion `exclue`.**

Pourquoi ces dates sont connues à temps : le Brent, le change (cours de midi à New York), le taux américain (clôture) et les
actions (clôture) datés de la veille ou d'avant sont tous fixés avant 13 h 25, heure de Francfort, le jour de la réunion.

## 5. Fichier d'analyse

Nom : **`analyse_H16.csv`**, dans `tests-de-mort/H16/`. CSV UTF-8, séparateur virgule, point décimal, une ligne d'en-têtes,
cellule vide pour un manquant, nombres écrits avec au moins huit chiffres significatifs.
**Une ligne par réunion : 315 lignes**, triées par date. Seize colonnes, dans cet ordre :

| Colonne | Type | Unité | Contenu |
|---|---|---|---|
| `rang` | entier | — | 1 à 315, dans l'ordre des dates |
| `date_reunion` | texte `AAAA-MM-JJ` | — | colonne `date` d'EA-MPD |
| `date_reunion_prec` | texte ou vide | — | `date_reunion` du rang précédent (vide au rang 1) |
| `d_ois1y_pb` | réel | point de base | `OIS_1Y`, feuille `Monetary Event Window` |
| `sigma16_pb` | réel ou vide | point de base | `max(s, 0.25)`, où `s` est l'écart-type (dénominateur 15) des `d_ois1y_pb` des 16 rangs précédents ; vide si `rang ≤ 16` |
| `cible_norm` | réel ou vide | écart-type | `d_ois1y_pb / sigma16_pb` ; vide si `rang ≤ 16` |
| `cible_prec_norm` | réel ou vide | écart-type | `cible_norm` du rang précédent ; vide si `rang ≤ 17` |
| `act_eu_60j_pct` | réel ou vide | % | § 4.3 |
| `brent_60j_pct` | réel ou vide | % | § 4.3 |
| `eurusd_60j_pct` | réel ou vide | % | § 4.3 |
| `us2a_60j_pp` | réel ou vide | point de % | § 4.3 |
| `date_fin_act` | texte ou vide | — | date de la dernière observation utilisée pour `act_eu_60j_pct` |
| `date_fin_brent` | texte ou vide | — | idem pour `brent_60j_pct` |
| `date_fin_eurusd` | texte ou vide | — | idem pour `eurusd_60j_pct` |
| `date_fin_us2a` | texte ou vide | — | idem pour `us2a_60j_pp` |
| `echantillon` | texte | — | `rodage` si `rang ≤ 17` ; sinon `exclue` si un des cinq prédicteurs ou la cible manque ; sinon `estimation` si `date_reunion ≤ 2009-12-03` ; sinon `evaluation` |

Pour les rangs 1 à 17, les quatre prédicteurs de marché et leurs dates peuvent être vides ou renseignés ; ils ne servent pas.
Effectifs attendus : 17 `rodage`, **151 `estimation`**, **147 `evaluation`**, 0 `exclue`.

**Contrôles de schéma.** Le vérificateur les refait tous à partir du fichier et rapporte dans `violations_schema` le nombre
de contrôles qui échouent (0 à 10).
1. Exactement 315 lignes et les 16 colonnes ci-dessus, dans cet ordre.
2. `rang` vaut 1, 2, …, 315 ; `date_reunion` est strictement croissante ; rang 1 = 1999-01-07, rang 168 = 2009-12-03,
   rang 169 = 2010-01-14, rang 315 = 2025-10-30.
3. `date_reunion_prec` est vide au rang 1 et égale ailleurs à la `date_reunion` de la ligne précédente.
4. `d_ois1y_pb` n'est jamais vide, est fini et de valeur absolue inférieure à 100.
5. `sigma16_pb` est vide si `rang ≤ 16` ; sinon il égale, à 1e-6 près, `max(s, 0.25)` recalculé depuis les 16 lignes précédentes.
6. `cible_norm` est vide si `rang ≤ 16` ; sinon `|cible_norm − d_ois1y_pb / sigma16_pb| ≤ 1e-6`.
7. `cible_prec_norm` est vide si `rang ≤ 17` ; sinon elle égale, à 1e-6 près, la `cible_norm` de la ligne précédente.
8. **Antériorité (aucune donnée du jour de la réunion ou d'après).** Partout où une colonne `date_fin_*` est renseignée,
   sa date est strictement inférieure à `date_reunion` et ne la précède pas de plus de 10 jours calendaires ; sur les
   lignes `estimation` et `evaluation`, les quatre `date_fin_*` sont renseignées. (Le prédicteur `cible_prec_norm` est couvert
   par les contrôles 3 et 7 : il vient de la ligne précédente, de date strictement antérieure.)
9. Sur les lignes `estimation` et `evaluation`, les cinq prédicteurs et `cible_norm` sont renseignés et finis, avec
   `|act_eu_60j_pct| < 100`, `|brent_60j_pct| < 300`, `|eurusd_60j_pct| < 50`, `|us2a_60j_pp| < 5`.
10. `echantillon` suit exactement la règle du tableau.

Le contrôle 8 vérifie ce que le fichier déclare ; il ne prouve pas que la construction est juste. C'est le rôle du compte
rendu de l'expérimentateur, qui cite pour trois réunions tirées au sort les lignes brutes utilisées.

## 6. Statistique

### 6.1 Prévisions récursives

Lignes utilisables : `echantillon ∈ {estimation, evaluation}`. Notations : `y` = `cible_norm` ; `x` = le vecteur
`(1, act_eu_60j_pct, brent_60j_pct, eurusd_60j_pct, us2a_60j_pp, cible_prec_norm)` (une constante et cinq prédicteurs, non
centrés, non réduits).

Pour chaque réunion `t` de l'échantillon `evaluation`, prise dans l'ordre des dates :
1. `A_t` = toutes les lignes utilisables de **date strictement antérieure** à celle de `t` (les lignes `estimation` et les
   réunions `evaluation` déjà passées). Il y en a 151 pour la première, 297 pour la dernière.
2. Référence : `m_t` = moyenne arithmétique de `y` sur `A_t`.
3. Modèle : `b_t` = coefficients des moindres carrés ordinaires de `y` sur `x`, estimés sur `A_t` ; prévision `p_t = x_t · b_t`.
4. Erreurs : `e0_t = y_t − m_t` ; `e1_t = y_t − p_t` ; écart des prévisions `d_t = p_t − m_t`.

Pas de pondération, pas d'écrêtage, pas de contrainte de signe, pas de sélection de variables. `P` = nombre de réunions
`evaluation` (attendu : 147).

### 6.2 Statistique principale et nombres dérivés

```
r2_oos  = 1 − Σ e1_t² / Σ e0_t²                       (sommes sur les P réunions d'évaluation)
f_t     = e0_t² − e1_t² + d_t²                         (terme de Clark-West ; identité : f_t = 2 · e0_t · d_t)
cw_fbar = (1/P) Σ f_t
s_f     = sqrt( Σ (f_t − cw_fbar)² / (P − 1) )
cw_se   = s_f / sqrt(P)
cw_t    = cw_fbar / cw_se
```

**Statistique principale : `cw_t`**, la statistique de Clark et West (2007) pour deux modèles emboîtés, comparée aux
quantiles de la loi normale (1,645 à 5 % unilatéral ; 1,282 à 10 %). `r2_oos` est le R² hors échantillon de Campbell et
Thompson ; il donne la taille, `cw_t` donne la preuve.

Pourquoi ces choix, en trois phrases :
- *Pourquoi pas une simple différence d'erreurs quadratiques ?* Si les prédicteurs ne servent à rien, le grand modèle estime
  cinq coefficients nuls avec du bruit, et ce bruit gonfle son erreur : la différence `e0² − e1²` est alors négative en
  moyenne (ici d'environ 2 points de R², § 7). Clark et West rajoutent `d_t²`, qui est exactement ce gonflement.
- *Que teste-t-on au juste ?* Comme `f_t = 2 · e0_t · d_t`, `cw_t` teste si la prévision en temps réel (son écart à la
  moyenne) varie dans le même sens que la surprise réalisée.
- *Pourquoi un écart-type simple, sans correction d'autocorrélation ?* Chaque prévision porte sur une seule réunion, et les
  cibles ne se chevauchent pas : si la surprise est imprévisible, `f_t` est imprévisible aussi, donc non autocorrélé. Les
  fenêtres de 60 jours des prédicteurs se chevauchent, ce qui autocorrèle `d_t` mais pas `f_t` sous l'hypothèse nulle.

Nombres dérivés, tous déterministes :
- `n_eval` = `P` ; `n_estim_init` = nombre de lignes `estimation` ;
- `cw_t_min_sans_une` : pour chacune des `P` réunions d'évaluation, on retire son `f_t` (les prévisions ne sont pas
  refaites), on recalcule `cw_t` sur les `P − 1` restantes avec les mêmes formules ; on garde le plus petit des `P` résultats ;
- `zone_grise` = 1 si `cw_t ≥ 1.282` et que l'une au moins des trois conditions de survie (`r2_oos > 0`, `cw_t ≥ 1.645`,
  `cw_t_min_sans_une ≥ 1.282`) n'est pas remplie ; sinon 0 ;
- `violations_schema` : nombre de contrôles du § 5 qui échouent.

Les seuils s'appliquent aux nombres non arrondis. L'expérimentateur écrit ces neuf champs dans `temoin.json`, le vérificateur
dans `verification.json`.

### 6.3 Analyses secondaires — descriptives, elles ne changent pas le verdict

Rapportées par l'expérimentateur ; le vérificateur n'a pas à les refaire.

**S1 — Signes (les deux lectures).** Une seule régression par moindres carrés de `y` sur `x` sur les 298 lignes utilisables
(c'est l'exercice « dans l'échantillon » des travaux publiés). On rapporte les six coefficients, leurs erreurs types
robustes HC3, le R² et le R² ajusté. Lecture fixée, avec `b` et `se` le coefficient des actions et son erreur type : si
`b − 1,645 × se > 0`, on écrit « signe de la lecture A » ; si `b + 1,645 × se < 0`, « signe de la lecture B » ; sinon « signe
non établi ». Même règle pour `cible_prec_norm`, comparée au signe négatif de Worms. Si le R² dans l'échantillon dépasse 3 %
alors que `r2_oos ≤ 0`, on écrit que le résultat a la forme « prévisible après coup, pas en temps réel ».

**S2 — Autres schémas de prévision, sur les mêmes réunions d'évaluation.** On rapporte `r2_oos` et `cw_t` pour : (a) le test
d'origine de la fiche — coefficients estimés une fois sur les lignes `estimation`, gelés, référence « zéro »
(`m_t = 0`) ; (b) une fenêtre glissante — modèle et moyenne estimés sur les 100 lignes utilisables qui précèdent `t` ;
(c) le schéma principal avec la référence « zéro ». Lecture fixée : on dit seulement si chacun aurait rempli ou non
`r2_oos > 0` et `cw_t ≥ 1,645` ; aucun ne remplace la statistique principale.

**S3 — Régimes et unité.** (a) Pour trois sous-périodes fixées ici — 2010-01-14 à 2014-05-08 (53 réunions, taux positifs),
2014-06-05 à 2022-06-09 (67 réunions, taux négatifs et achats d'actifs), 2022-07-21 à 2025-10-30 (27 réunions,
resserrement puis détente) — on rapporte `Σ f_t`, `Σ e0_t²`, `Σ e1_t²` et `1 − Σ e1² / Σ e0²`. Lecture fixée : si plus de la
moitié de `Σ f_t` total vient d'une seule sous-période, on l'écrit. (b) Le schéma principal refait avec la cible en points
de base bruts (`y = d_ois1y_pb`, cinquième prédicteur = `d_ois1y_pb` de la réunion précédente, mêmes lignes) : `r2_oos` et
`cw_t`. Lecture fixée : si `r2_oos` change de signe ou si `cw_t` passe de l'autre côté de 1,645, on écrit que le résultat
dépend de la normalisation. On rapporte aussi le nombre de réunions où le plancher de 0,25 point de base joue.

**Graphique unique** (fixé) : en fonction de la date, la somme cumulée de `e0_t² − e1_t²` et celle de `f_t`, avec les trois
sous-périodes en fond ; en encart, `p_t − m_t` contre `y_t − m_t`.

## 7. Arithmétique de puissance

**Effectifs.** 151 réunions pour la première estimation, 147 réunions d'évaluation, six coefficients. Les cibles ne se
chevauchent pas : 147 observations à peu près indépendantes pour le test. La fenêtre d'estimation passe de 151 à 297
réunions, soit environ 225 en moyenne.

**Deux règles de pouce** (`R²` = part de variance réellement prévisible, `k` = 5 prédicteurs, `n` ≈ 225, `P` = 147) :
- R² hors échantillon attendu ≈ `R² − k/n` ≈ `R² − 2,2 points`. Sans aucune prévisibilité, on attend donc environ −2 %,
  pas zéro : c'est pour cela que `r2_oos > 0` est déjà une exigence.
- `cw_t` attendu ≈ `√P × R² / √(R² + k/n)`. Pour R² = 2 % : 1,2. Pour 4 % : 1,9. Pour 7 % : 2,8. Pour 10 % : 3,5.

**Simulation** (données synthétiques : cinq prédicteurs gaussiens indépendants, erreurs gaussiennes, coefficients égaux,
151 + 147 observations, 4 000 tirages, générateur numpy `default_rng(20261112)` ; la règle du § 8 appliquée telle quelle) :

| R² vrai | survit | non concluant (zone grise) | éliminée | `r2_oos` médian [10 % ; 90 %] |
|---|---|---|---|---|
| 0 | 0,04 | 0,04 | 0,92 | −2,4 % [−5,1 ; +0,2] |
| 1 % | 0,14 | 0,10 | 0,76 | −1,5 % [−4,7 ; +2,0] |
| 2 % | 0,28 | 0,14 | 0,58 | −0,5 % [−4,2 ; +3,6] |
| 3 % | 0,43 | 0,15 | 0,42 | +0,5 % [−3,6 ; +5,2] |
| 4 % | 0,56 | 0,16 | 0,28 | +1,5 % [−3,1 ; +6,6] |
| 5 % | 0,68 | 0,14 | 0,19 | +2,5 % [−2,4 ; +8,0] |
| 7 % | 0,82 | 0,10 | 0,08 | +4,6 % [−1,1 ; +10,5] |
| 10 % | 0,93 | 0,06 | 0,01 | +7,7 % [+1,2 ; +14,2] |

Avec des erreurs à queues épaisses (loi de Student à 4 degrés de liberté), les chiffres bougent d'au plus 0,03. Quand les
coefficients changent en 2010 (survie, fenêtre croissante / glissante de 100 / gelée) : prévisibilité de 7 % qui n'apparaît
qu'après 2010 : 0,41 / 0,48 / 0,18 ; qui passe de 7 % à 3 % : 0,46 / 0,26 / 0,41 ; qui disparaît après 2010 : 0,03 / 0,02 /
0,03 (réponse juste : il n'y a rien à prévoir dans l'évaluation) ; dont le signe s'inverse en 2010 : 0,01 / 0,16 / 0,00.

**Ce que cela dit, sans fard.**
- **Ce que le test détecte** : une prévisibilité vraie d'environ **7 %** est vue quatre fois sur cinq ; 10 %, plus de neuf
  fois sur dix. À 3,5 %, c'est une fois sur deux.
- **Faux positifs** : sans aucune prévisibilité, la fiche survit une fois sur vingt-cinq et finit en zone grise une fois sur
  vingt-cinq ; elle est éliminée neuf fois sur dix.
- **Ce que les R² publiés impliquent.** Le plus proche de nos prédicteurs (Altavilla et coauteurs, 3,66 % dans l'échantillon
  avec quatre variables) correspond, une fois retiré le gain mécanique d'ajustement (de l'ordre de 4 coefficients pour
  250 réunions, soit 1,5 point ; leur effectif exact n'a pas été relevé), à un R² vrai d'environ 2 % : dans ce
  cas la fiche **survit un peu plus d'une fois sur quatre et est éliminée plus d'une fois sur deux, alors qu'un petit effet
  existe**. Si nos prédicteurs gratuits captent la moitié des 20 % de Worms (grâce surtout à la surprise précédente), la
  fiche survit neuf fois sur dix. Les 8 à 13 % de Kerssenfischer et Schmeling reposent sur d'autres prédicteurs et ne se
  transposent pas. La chance de conclure « survit » va donc d'une sur quatre à neuf sur dix selon le chiffre publié qu'on croit.
- **Conséquence** : entre 1 et 4 % de R² vrai, la faille de puissance relevée par les juges demeure. La fenêtre croissante
  ne la répare pas ; aucun choix de méthode ne crée de réunions supplémentaires. Une élimination voudra dire « pas de
  prévisibilité de l'ordre de 7 % ou plus », pas « aucune prévisibilité ».
- **Ce que la simulation embellit** : prédicteurs indépendants et sans valeurs extrêmes, volatilité constante, coefficients
  stables. La réalité est moins favorable ; les probabilités de survie ci-dessus sont des plafonds.

Temps de calcul : cinq téléchargements (17 Mo au plus), 147 régressions à six coefficients : moins d'une minute sur un portable.

## 8. Règle de verdict

Appliquée par le code de l'orchestrateur (`verdict.py`) aux nombres du vérificateur.

1. **Non concluant** si l'une de ces conditions est vraie :
   - `n_eval < 140` ou `n_estim_init < 140` — on attend 147 et 151 ; on tolère la perte d'environ 5 % des réunions pour
     donnée manquante, ce qui ne change pas la puissance ; au-delà, l'échantillon n'est plus celui qui a été préinscrit ;
   - `violations_schema > 0` ;
   - `zone_grise ≥ 1` — `cw_t` atteint le seuil de 10 % (1,282) mais les trois conditions de survie ne sont pas toutes
     remplies : signal trop faible pour survivre, trop fort pour être tué honnêtement ;
   - un champ manque, ou l'expérimentateur et le vérificateur diffèrent de plus que la tolérance.
2. Sinon, **survit** si les trois conditions sont vraies :
   - `r2_oos > 0` — la prévision en temps réel, telle quelle, a fait mieux que la moyenne passée. Le seuil zéro est
     naturel et déjà exigeant : sans prévisibilité, on attend environ −2 %, et un R² positif n'arrive qu'une fois sur huit ;
   - `cw_t ≥ 1.645` — l'écart est distinguable du hasard à 5 % unilatéral, valeur critique normale recommandée par Clark et
     West pour des modèles emboîtés (un peu prudente : 4 % de rejets sous l'hypothèse nulle dans la simulation) ;
   - `cw_t_min_sans_une ≥ 1.282` — le résultat reste significatif à 10 % quand on retire la réunion qui l'aide le plus.
3. Sinon, **éliminée** — ce qui, vu les conditions ci-dessus, revient à `cw_t < 1.282`.

Pourquoi deux conditions de fond et non une seule : `cw_t` seul peut être significatif avec un `r2_oos` négatif (le signal
existe mais le bruit d'estimation le mange : personne n'aurait gagné à s'en servir) ; `r2_oos > 0` seul arrive une fois sur
huit par hasard. « Prévisible hors échantillon » demande les deux.

Une zone grise est une raison **statistique** de non-conclusion, pas une raison de données au sens du protocole.

**Ce que « survit » voudrait dire** : de 2010 à 2025, une règle linéaire fixée à l'avance et nourrie de cinq séries gratuites
aurait prévu une part des surprises de la BCE en temps réel. **Ce que cela ne voudrait pas dire** : que le marché se trompe
(§ 9, limite 2), ni que les surprises sont de mauvais instruments dans tel article précis.
**Ce que « éliminée » voudrait dire** : cette règle n'a pas fait mieux que la moyenne passée. **Pas** que les surprises sont
imprévisibles : le test voit mal un R² vrai inférieur à 4 %, et il ne dit rien d'autres prédicteurs ni des résultats publiés
dans l'échantillon.

## 9. Limites que le plan ne répare pas

1. **Puissance entre 1 et 4 % de R² vrai (la plus grave pour le verdict).** C'est la zone où tombe l'estimation publiée la
   plus proche. Un petit effet réel sera éliminé une fois sur deux à trois fois sur quatre.
2. **Prévisibilité n'est pas erreur d'anticipation.** Une surprise prévisible peut venir d'un marché qui se trompe sur la
   réaction de la BCE, ou d'une prime de risque qui varie avec l'état de l'économie : le taux OIS contient alors une
   compensation prévisible, sans aucune erreur. Ce test ne sépare pas les deux. Il faudrait des anticipations mesurées par
   enquête, hors du périmètre.
3. **Instabilité des régimes.** La fenêtre croissante apprend un régime après l'avoir observé, jamais avant. Si le lien change
   de signe entre régimes, le test échoue (survie 0,01 dans la simulation), alors qu'une régression sur toute la période
   pourrait trouver un lien par sous-période. C'est le sens même de « hors échantillon », mais il faut le dire.
4. **La cible normalisée n'est pas la surprise en points de base** qu'utilisent les articles ; ses valeurs extrêmes aux
   changements de régime pèsent lourd. S3 donne la version brute, à titre descriptif seulement.
5. **Prédicteurs approximatifs** : actions de l'Europe développée (Royaume-Uni et Suisse compris), en dollars ; aucune
   donnée macroéconomique de la zone euro, aucune surprise d'indicateurs (payantes). Un échec peut tenir aux prédicteurs.
6. **Données non figées dans le temps** : le fichier Ken French est recalculé à chaque millésime, la courbe américaine est
   révisée, EA-MPD aussi (une cotation de 2014 a été corrigée). Les prix étaient observables à l'époque ; les fichiers
   d'aujourd'hui n'en sont pas la copie exacte.
7. **Cotations figées de 1999-2001** (zéros exacts) dans la première fenêtre d'estimation, et deux réunions par mois à cette
   époque : la surprise « précédente » y a deux semaines (parfois quelques jours), plus tard quatre à six.
8. **Valeurs extrêmes des prédicteurs** (Brent en 2008 et 2020) : non écrêtées ; elles peuvent donner une prévision très
   éloignée de la moyenne à une réunion. La condition de retrait d'une réunion et le graphique cumulé le montreront.
9. **Une seule maturité, une seule fenêtre** (OIS 1 an, événement monétaire entier). Rien sur le communiqué et la conférence
   de presse pris séparément, ni sur les facteurs d'Altavilla et coauteurs (2019).
10. **Changement d'horaire de la fenêtre en juillet 2022**, au début de la troisième sous-période.

## 10. Ce qu'on écrira dans chaque cas

Phrases fixées maintenant ; seuls les nombres entre crochets seront remplis, avec les valeurs du vérificateur (S1 à S3 :
valeurs de l'expérimentateur).

- **Survit** : « Selon un plan scellé et avec des données publiques seulement, une régression réestimée avant chaque réunion
  sur cinq variables de marché datées de la veille prévoit la surprise de la BCE (OIS 1 an, normalisée) mieux que sa
  moyenne passée sur les [n_eval] réunions de 2010 à 2025 : R² hors échantillon de [r2_oos], statistique de Clark-West de
  [cw_t] ; les travaux publiés montraient cette prévisibilité dans l'échantillon, celui-ci la montre en temps réel, sans
  pouvoir dire si elle vient d'une erreur d'anticipation ou d'une prime de risque (signe des actions : [lecture S1]). »
- **Éliminée** : « Selon un plan scellé et avec des données publiques seulement, une régression réestimée avant chaque
  réunion sur cinq variables de marché ne prévoit pas la surprise de la BCE mieux que sa moyenne passée sur les [n_eval]
  réunions de 2010 à 2025 (R² hors échantillon de [r2_oos], Clark-West de [cw_t], sous le seuil de 1,282) ; ce test ne
  détecte de façon fiable qu'une prévisibilité vraie d'au moins 7 %, il n'exclut donc pas un effet plus petit, et il ne
  contredit pas la prévisibilité dans l'échantillon déjà publiée (R² dans l'échantillon ici : [R² de S1]). »
- **Non concluant** : « Le test préinscrit de H16 ne conclut pas ([raison : zone grise, avec Clark-West de [cw_t], R² hors
  échantillon de [r2_oos] et minimum sans une réunion de [cw_t_min_sans_une] / donnée manquante / schéma violé / écart entre
  expérimentateur et vérificateur]) : avec 147 réunions, les données publiques ne permettent ni d'établir ni d'écarter une
  prévisibilité en temps réel des surprises de la BCE. »

## 11. Règle de verdict lisible par machine

```json
{
  "id": "H16",
  "fichier_analyse": "analyse_H16.csv",
  "champs_verification": [
    "n_eval",
    "n_estim_init",
    "r2_oos",
    "cw_fbar",
    "cw_se",
    "cw_t",
    "cw_t_min_sans_une",
    "zone_grise",
    "violations_schema"
  ],
  "survit_si": [
    {"champ": "r2_oos", "operateur": ">", "seuil": 0},
    {"champ": "cw_t", "operateur": ">=", "seuil": 1.645},
    {"champ": "cw_t_min_sans_une", "operateur": ">=", "seuil": 1.282}
  ],
  "non_concluant_si": [
    {"champ": "n_eval", "operateur": "<", "seuil": 140},
    {"champ": "n_estim_init", "operateur": "<", "seuil": 140},
    {"champ": "violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "zone_grise", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "n_eval": 0,
    "n_estim_init": 0,
    "r2_oos": 0.0005,
    "cw_fbar": 0.0005,
    "cw_se": 0.0005,
    "cw_t": 0.005,
    "cw_t_min_sans_une": 0.005,
    "zone_grise": 0,
    "violations_schema": 0
  }
}
```
