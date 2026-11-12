# K20 — Préinscription du test de mort : la sous-réaction du consensus grandit-elle avec la taille des nouvelles ?

Rédigé le 2026-11-12 par le rédacteur de préinscription de K20. Le rédacteur n'a lancé aucune analyse. Il n'a calculé aucune
erreur, aucune révision, aucune surprise, aucune moyenne de résultat, aucune régression et aucune statistique sur les
prévisions comparées aux réalisations. Les seuls calculs faits sont : des calculs de puissance théoriques (loi normale et
simulation sans donnée) ; des comptes de cellules présentes ou absentes ; un tableau de la précision d'écriture (nombre de
décimales) des prévisions médianes ; une vérification, sur la première ligne du fichier, de la convention de taux de
croissance de l'enquête.

**Ce que le rédacteur a lu.**
- Le brief, `tests-de-mort/protocole.md`, `tests-de-mort/verdict.py`, `generation-3/regle-generation-3.md`.
- La fiche K20 et les failles des quatre juges.
- La note de nouveauté `generation-3/nouveaute/K20.md`.
- Dans `tests-de-mort/J02`, **seulement** `preenregistrement.md` et `verdict.json`. Rien d'autre de ce dossier : ni fichier
  d'analyse, ni données, ni scripts, ni rapports.

**Ce que le rédacteur a vu des données** (téléchargées le 2026-11-12, toutes en HTTP 200).
- Fed de Philadelphie, `medianLevel.xlsx`, `meanLevel.xlsx`, `medianGrowth.xlsx`, `meanGrowth.xlsx` :
  - noms des feuilles et des colonnes ;
  - les deux premières lignes (enquêtes 1968T4 et 1969T1) des feuilles `PGDP`, `RGDP`, `UNEMP`, `CPI`, `TBILL` ;
  - la dernière enquête (2026T3) ;
  - la liste des cellules vides dans les colonnes 2, 5 et 6.
- Le nombre de décimales des prévisions médianes en niveau, par tranche de cinq ans (section 3, amendement A4). C'est une
  mesure de précision d'écriture, pas un résultat.
- Base temps réel de la Fed de Philadelphie, `pQvQd.xlsx` et `routputQvQd.xlsx` :
  - noms des colonnes ;
  - les deux premières lignes (1947T1, 1947T2) des trois premiers millésimes ;
  - pour chaque trimestre de 1968T1 à 2026T3, le **numéro du premier millésime où la valeur est présente**, sans lire la valeur.
- FRED `UNRATE`, `CPIAUCSL`, `TB3MS` : l'en-tête, la première ligne de chaque série (1948-01, 1947-01, 1934-01), la dernière
  date (2026-10) et la liste des mois vides (2025-10 pour `UNRATE` et `CPIAUCSL`).
- FRED `USRECQP` (indicateur trimestriel de récession NBER) : les trimestres marqués 1 depuis 1968.
- La documentation de l'enquête, `spf-documentation.pdf` : définitions, calendrier, convention des taux de croissance.

**Aucune valeur de prévision postérieure à 1969T1 et aucune réalisation de la période d'étude n'a été affichée.**

---

## 1. Question, définitions, hypothèses rivales et prédiction chiffrée

**Question.** Dans l'enquête de la Fed de Philadelphie auprès des prévisionnistes professionnels (cibles 1969-2026, cinq
variables), la sous-réaction du consensus est-elle plus forte quand les nouvelles sont grandes ? Et cela tient-il sur
plusieurs grands chocs, pas seulement sur 2021-2023 ? La sous-réaction se mesure par la pente positive de l'erreur sur la
révision.

**Définitions.** Pour une variable v et un trimestre cible q :
- **Enquêtes.** L'enquête du trimestre q − 3 donne la prévision `prev_h3` = F₍q−3₎(x_q), en colonne 5, trois trimestres
  avant la cible. L'enquête du trimestre q − 4 donne la prévision `prev_h4` = F₍q−4₎(x_q), en colonne 6, quatre trimestres
  avant.
- **Révision** : r = `prev_h3` − `prev_h4`. C'est ce que le consensus a changé entre deux enquêtes successives, pour la même
  cible.
- **Erreur** : e = a(q) − `prev_h3`, où a(q) est la valeur réalisée.
- **Surprise** : s = a(q − 4) − F₍q−4₎(x₍q−4₎), où F₍q−4₎(x₍q−4₎) est la prévision du trimestre courant (colonne 2) dans
  l'enquête q − 4. C'est l'écart entre la donnée du trimestre q − 4, publiée entre les deux enquêtes, et ce que le consensus
  en attendait. Une révision r répond en partie à cette nouvelle.
- **Grande nouvelle** : L = 1 si |s| est dans le tiers supérieur des |s| de la variable (règle exacte en section 6) ; sinon
  L = 0.

**Hypothèses et signe attendu de c.** c est le supplément de pente de l'erreur sur la révision quand L = 1 (section 6). Il
est mesuré en écart-type d'erreur par écart-type de révision.

| Hypothèse | Ce qu'elle dit | Signe de c |
|---|---|---|
| H1 — fiche K20 | les prévisionnistes révisent trop peu quand il faudrait réviser beaucoup (réticence aux grandes révisions, lissage) | **c > 0** |
| H0 — rigidité de taille fixe | information rigide ou bruitée à degré constant ; Coibion et Gorodnichenko (2012) : la pente ne dépend pas de la taille des chocs | c = 0 |
| H2 — attention qui monte avec les chocs | inattention rationnelle ; moins de rigidité en période agitée et après les grands chocs visibles (Coibion et Gorodnichenko 2015, sections 4.2-4.3 ; Baker, McElroy et Sheng 2020) | c < 0 |
| H3 — sur-réaction aux nouvelles extrêmes | règle de prévision linéaire face à des chocs à queues épaisses ; sous-réaction aux nouvelles ordinaires, sur-réaction aux nouvelles extrêmes (de Silva, Larsen-Hallock, Rej et Thesmar 2025, sur des ventes d'entreprises) | c < 0, et une pente des grandes nouvelles (b + c) qui peut devenir négative |
| H4 — artefact de mesure | le bruit du consensus atténue davantage la pente là où les révisions varient peu | c > 0, petit (section 7) |
| H5 — dépendance à la persistance | plus de sous-réaction quand l'inflation est élevée (Kučinskas et Peters 2024), via la persistance de l'inflation | c > 0 surtout pour les prix ; c par variable, descriptif |

**Prédiction chiffrée de la fiche, reprise telle quelle.**
- Pente de base, petites nouvelles : b ≈ +0,3.
- Supplément pour les grandes nouvelles : **c ≈ +0,4**, plage +0,2 à +0,6.
- Unités : écart-type d'erreur par écart-type de révision, variables regroupées.

La fiche définissait « grande » par la taille de la révision elle-même. Ce test la définit par la surprise (amendement A1).
L'enjeu chiffré reste 0,40 (section 9).

**Attente du rédacteur, pour mémoire et hors verdict.** La littérature penche contre H1 : Coibion et Gorodnichenko (2015),
de Silva et coauteurs (2025). Le biais mécanique restant est positif mais petit (section 7). Le tri par la surprise dilue
un éventuel effet de non-linéarité dans la révision (section 10, limite 3). Le rédacteur s'attend donc à un c compris entre
−0,2 et +0,15, et plutôt à une élimination. Il ne sait pas de quel côté des seuils le résultat tombera.

---

## 2. Ce qui est connu avant le scellement

**Le parent, J02, a survécu** (`J02/verdict.json`) :
- pente réduite de l'erreur sur la révision des projections d'inflation de la BCE à horizon 2 : β_z = 0,443 (é.-t. 0,196) ;
- avant 2020 : 0,134 ;
- hors 2021-2023 : 0,144 ;
- minimum en retirant deux années consécutives : 0,050, quand on retire 2021-2022.

J02 dit que la sous-réaction de la BCE est portée par un épisode. Il ne dit rien de la pente par taille de nouvelle, ni de
l'enquête américaine. Aucun chiffre de K20 n'en découle.

**Ce qui est publié sur cette enquête** (note de nouveauté) :
- la pente de base erreur sur révision : Coibion et Gorodnichenko (2015) ; Bordalo, Gennaioli, Ma et Shleifer (2020),
  tableau 3, avec le consensus moyen ;
- une dépendance à l'état : moins de rigidité en période agitée (Coibion et Gorodnichenko 2015) ; plus de sous-réaction
  quand l'inflation est élevée (Kučinskas et Peters 2024).

Personne, à la connaissance de la note, n'a publié le supplément de pente selon la taille des nouvelles sur le consensus de
cette enquête.

**Le plan n'a pas été réglé sur des résultats.** Les seules informations sur les données vues avant le scellement sont
celles de l'en-tête. Les choix de la section 3 répondent chacun à une faille nommée par un juge ou à une correction de la
note de nouveauté.

**Règle d'aveuglement pour la suite.** L'expérimentateur et le vérificateur de K20 n'ouvrent aucun fichier d'un autre
dossier de `tests-de-mort/`, sauf `protocole.md` et `verdict.py`. S'ils l'ont fait, ils l'écrivent dans `ecarts.md`.

---

## 3. Amendements déclarés à la fiche

| N° | La fiche disait | Ce test fait | Raison |
|---|---|---|---|
| A1 | grande nouvelle = \|z\| > 1, z étant la **révision** réduite | grande nouvelle = **tiers supérieur de \|surprise\|** sur la donnée du trimestre q − 4, publiée entre les deux enquêtes, propre à chaque variable | juges Kimi et Claude : une grande révision n'est pas une grande nouvelle exogène, et trier sur la révision crée l'interaction par le bruit et la régression vers la moyenne ; la note de nouveauté montre que ce biais va dans le sens de l'hypothèse. La surprise ne contient pas la prévision évaluée (section 7) |
| A2 | mort si t(c) < 1,645 contre 0 | survie seulement si la borne basse de l'intervalle à 90 % dépasse un **plancher de biais** = max(0,10 ; biais mécanique calculé avec 20 % de bruit) | le tri par la surprise ne supprime pas tout le biais : l'atténuation différentielle subsiste. Le plancher l'absorbe (section 7) |
| A3 | e = a_v + b·rev + c·rev·1{\|z\|>1} : pente commune, pas d'effet propre de la classe | constante, effet propre de la classe et pente de base **propres à chaque variable** ; c commun | juge Astra : une pente commune confond la non-linéarité avec des différences entre variables. Une interaction sans son effet propre attribue à la pente un écart de niveau |
| A4 | médianes | **moyennes** de l'enquête (`meanLevel`, `meanGrowth`) ; médianes en analyse secondaire | les niveaux médians du déflateur sont des entiers dans les 7 premières enquêtes, et à une décimale sur un indice proche de 100 dans 60 % des cas de 1970 à 1994. L'arrondi d'une seule réponse entre alors dans la révision et dans l'erreur, ce qui nourrit le biais de A1. La moyenne de 30 à 40 réponses réduit cet arrondi. Bordalo et coauteurs utilisent la moyenne (note de nouveauté) |
| A5 | niveaux à horizons 3 et 4 | **taux de croissance trimestriels annualisés** pour `PGDP` et `RGDP` (`dpgdp5`, `dpgdp6`, `drgdp5`, `drgdp6`) ; niveaux pour `UNEMP` et `TBILL` ; `CPI` déjà en taux | note de nouveauté, correction 2 : l'année de base change et n'est pas remise à l'échelle. Un taux calculé dans une seule enquête n'en dépend pas |
| A6 | réalisés ALFRED environ un an après la cible | `PGDP`, `RGDP` : **première publication** de la base temps réel de Philadelphie (`P`, `ROUTPUT`) ; `UNEMP`, `CPI`, `TBILL` : **dernier millésime FRED** | note de nouveauté, correction 4 : `GDPDEF` et `GDPC1` n'ont pas de millésime avant décembre 1991 ; `TB3MS` n'en a aucun. Justification détaillée en section 4 |
| A7 | 1968-2026, cinq variables | cibles 1969T4-2026T3 pour `PGDP`, `RGDP`, `UNEMP` ; 1982T3-2026T3 pour `CPI`, `TBILL` ; `RGDP` et `UNEMP` sans les cibles 2020T1-2021T4 dans l'échantillon principal | note de nouveauté, correction 3 : `CPI` et `TBILL` commencent en 1981T3, et il faut une enquête q − 4. Exclusion pandémique : voir section 4 |
| A8 | cinq épisodes choisis à la main | **sept fenêtres objectives** : chaque récession NBER, du pic au creux + 4 trimestres, fenêtres qui se chevauchent fusionnées, et la poussée d'inflation 2021-2023 jointe à la récession de 2020 | juge Kimi : la liste doit être fixée et loyale. La règle NBER évite de choisir les épisodes, et le « + 4 » couvre toute cible dont l'information tombe dans l'épisode |
| A9 | c > 0 dans chaque échantillon d'exclusion | survie si **t ≥ 1** dans chaque exclusion ; éliminée si un c d'exclusion est ≤ 0 alors que le test principal passe ; non concluant entre les deux | juge Kimi : le signe seul laisse passer un effet porté par un épisode une fois sur deux. Juge Gemini : la significativité dans chaque exclusion coûte trop de puissance. Le seuil t ≥ 1 est le compromis, chiffré en section 8 |
| A10 | deux issues | trois issues : survit, éliminée, non concluant, comme le parent | le protocole veut une règle complète. Un intervalle qui contient à la fois le plancher et 0,40 ne tranche pas |
| A11 | Newey-West à 4 retards groupé par trimestre | Driscoll-Kraay : scores sommés par trimestre cible, puis Newey-West à 4 retards en temps calendaire ; 8 retards et 0 retard en analyse secondaire | c'est la même idée, écrite exactement. Juges Astra et Claude : les variables partagent les chocs d'un trimestre. On rapporte un nombre d'observations effectives |
| A12 | réduction par un écart-type en fenêtre croissante | réduction par l'écart-type de chaque variable sur l'échantillon principal | la coupure ne dépend plus de la révision : la fenêtre croissante, qui protégeait le seuil \|z\| > 1, n'a plus d'objet. Le test est en échantillon |
| A13 | — | condition de pertinence : la variance des révisions doit être au moins 1,25 fois plus grande dans la classe des grandes nouvelles | sinon le tri par la surprise ne sépare pas les grandes révisions des petites, et le test ne répond pas à la question |

---

## 4. Données

Toutes les sources sont publiques, sans compte. Les fichiers bruts vont dans `tests-de-mort/K20/donnees/`. Le sha256, la
date et le code HTTP de chaque fichier vont dans `tests-de-mort/K20/construire_journal.json`. Chaque téléchargement a
jusqu'à 5 essais, avec un délai de 120 s par essai. **Si un fichier manque, l'expérimentateur s'arrête** : le verdict est
non concluant, pour une raison de données.

### 4.1 Prévisions — Fed de Philadelphie, enquête auprès des prévisionnistes professionnels

Préfixe : `https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/`

| Fichier | Feuilles utilisées | Colonnes |
|---|---|---|
| `meanGrowth.xlsx` (principal) | `PGDP`, `RGDP` | `YEAR`, `QUARTER`, `dpgdp2`, `dpgdp5`, `dpgdp6` ; `drgdp2`, `drgdp5`, `drgdp6` |
| `meanLevel.xlsx` (principal) | `UNEMP`, `CPI`, `TBILL` | `YEAR`, `QUARTER`, `UNEMP2`, `UNEMP5`, `UNEMP6` ; `CPI2`, `CPI5`, `CPI6` ; `TBILL2`, `TBILL5`, `TBILL6` |
| `medianGrowth.xlsx` (secondaire) | `PGDP`, `RGDP` | `dpgdp5`, `dpgdp6` ; `drgdp5`, `drgdp6` |
| `medianLevel.xlsx` (secondaire) | `UNEMP`, `CPI`, `TBILL` | `UNEMP5`, `UNEMP6` ; `CPI5`, `CPI6` ; `TBILL5`, `TBILL6` |

**Ce qui a été vérifié sur les fichiers réels** :
- 232 lignes par feuille, enquêtes 1968T4 à 2026T3 ;
- colonne 1 = trimestre précédent, colonne 2 = trimestre courant, colonnes 3 à 6 = les quatre trimestres suivants
  (documentation) ;
- les taux de `meanGrowth` et `medianGrowth` sont les taux annualisés des niveaux moyens ou médians d'une même enquête :
  100 × ((niveau_h / niveau_{h−1})⁴ − 1). Vérifié sur l'enquête 1968T4 : (123,3253 / 122,000)⁴ − 1 = 4,4166 %, égal à
  `dpgdp2` de `meanGrowth` ; (123 / 122)⁴ − 1 = 3,3192 %, égal à `dpgdp2` de `medianGrowth`.

Unités :
- `PGDP` : taux trimestriel annualisé du déflateur, en % ; déflateur du PNB avant 1992.
- `RGDP` : taux trimestriel annualisé du PIB réel, en % ; PNB réel avant 1992, et calculé NGDP / PGDP × 100 avant 1981T3.
- `CPI` : taux trimestriel annualisé de l'indice moyen du trimestre, en %.
- `UNEMP` : moyenne trimestrielle du taux de chômage, en points.
- `TBILL` : moyenne trimestrielle du taux des bons du Trésor à 3 mois, en points.

**Lecture.** Le numéro de trimestre est t = 4 × année + (trimestre − 1). Exemples : 1969T4 → 7879 ; 1982T3 → 7930 ;
2026T3 → 8106. Pour la cible t :
- `prev_h3` = colonne 5 de l'enquête t − 3 ;
- `prev_h4` = colonne 6 de l'enquête t − 4 ;
- `nowcast_q4` = colonne 2 de l'enquête t − 4.

Une cellule vide est manquante. Aucune autre source ne la remplace.

**Cellules vides vérifiées** (moyennes et médianes, même motif) : la colonne 6 manque dans les enquêtes 1969T1, 1969T2,
1969T3, 1970T1 et 1974T3 pour `PGDP`, `RGDP` et `UNEMP`. Les cibles 1970T1, 1970T2, 1970T3, 1971T1 et 1975T3 n'ont donc pas
de `prev_h4`. Aucune autre cellule utile n'est vide.

### 4.2 Réalisations

**Choix : première publication pour `PGDP` et `RGDP`, dernier millésime FRED pour `UNEMP`, `CPI` et `TBILL`.**

Pourquoi la première publication pour les comptes nationaux :
1. Elle mesure le même concept que celui qui était prévu : le PNB avant 1992, et la même année de base, aux révisions de
   référence près. Un millésime récent mesure un autre concept : le PIB en chaîne, avec la R&D capitalisée depuis 2013. Ce
   changement de concept fabriquerait des « erreurs » que personne ne pouvait prévoir.
2. Elle existe pour toutes les cibles, dans une seule source : la base temps réel de Philadelphie a les millésimes de 1965T4
   à 2026T4. ALFRED n'a `GDPDEF` et `GDPC1` qu'à partir de décembre 1991.
3. Un millésime fixe un an après la cible ferait perdre les quatre dernières cibles, et il chevaucherait des révisions de
   référence à des dates différentes selon les cibles.
4. Le bruit de la première publication est dans le réalisé, donc dans la variable expliquée seulement. Il élargit les
   intervalles mais ne biaise pas la pente, sauf s'il est corrélé à la révision.

Pourquoi le dernier millésime pour les trois autres variables : `UNRATE` et `CPIAUCSL` ne sont révisés que par les
coefficients saisonniers (de quelques centièmes à un dixième), et `TB3MS` n'est jamais révisé. Les millésimes réels de ces
séries sont incomplets : `CPIAUCSL` commence en 1973 avec des fenêtres de 19 mois, et `TB3MS` n'a aucun millésime.

**Source A — base temps réel de la Fed de Philadelphie.**
- `https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/pQvQd.xlsx`
  (feuille `P`)
- `https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/routputQvQd.xlsx`
  (feuille `ROUTPUT`)

Vérifié : 319 lignes. La colonne `DATE` a la forme `1947:Q1`, de 1947T1 à 2026T3. Il y a 245 colonnes de millésimes, `P65Q4`
à `P26Q4` et `ROUTPUT65Q4` à `ROUTPUT26Q4`. Les cellules sont toutes numériques ou vides.

Le numéro d'un millésime `P{aa}Q{n}` est t = 4 × année + n − 1, avec année = 1900 + aa si aa ≥ 60, sinon 2000 + aa.

**Note technique** : `openpyxl` 3.1 refuse d'ouvrir ces deux fichiers, à cause d'une date mal formée dans leurs propriétés.
Contournement vérifié :

```
import openpyxl.reader.excel as ex
ex.ExcelReader.read_properties = lambda self: None
```

On l'écrit avant `pandas.read_excel`.

**Première publication de la cible t** : parmi les millésimes rangés par numéro croissant, le premier dont le numéro est
supérieur à t et où les lignes t et t − 1 sont toutes deux remplies. On note :
- `niveau_cible` = valeur de la ligne t ;
- `niveau_avant` = valeur de la ligne t − 1, dans ce même millésime ;
- a(t) = 100 × ((`niveau_cible` / `niveau_avant`)⁴ − 1).

Vérifié sur les fichiers (présence seulement) : ce millésime est t + 1 pour toutes les cibles nécessaires, sauf 1995T4,
2025T3 et 2025T4. Pour ces trois cibles, c'est t + 2 (fermetures de l'administration fédérale). La date du millésime, au
milieu du trimestre, correspond à la date limite de l'enquête. Les prévisionnistes de l'enquête t + 1 avaient donc vu cette
publication, sauf pour ces trois trimestres.

**Source B — FRED, dernier millésime.**
- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE`
- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL`
- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS`

Vérifié : l'en-tête est `observation_date,<SÉRIE>` ; les données sont mensuelles jusqu'à 2026-10. **Le mois 2025-10 est vide
pour `UNRATE` et `CPIAUCSL`**, faute de collecte pendant la fermeture de l'administration. `TB3MS` n'a aucun vide.

Calcul de la réalisation :
- `niveau_cible` = moyenne des trois mois du trimestre t, manquante si l'un des trois mois est vide ou vaut « . ».
- `UNEMP`, `TBILL` : a(t) = `niveau_cible`, et `niveau_avant` reste vide.
- `CPI` : `niveau_avant` = la même moyenne pour t − 1, et a(t) = 100 × ((`niveau_cible` / `niveau_avant`)⁴ − 1). C'est la
  définition de l'enquête : variation annualisée de l'indice moyen du trimestre.

Conséquence vérifiée : a(t) manque pour `UNEMP` 2025T4, `CPI` 2025T4 et `CPI` 2026T1.

**La surprise** se lit de la même façon pour le trimestre t − 4 : colonnes `niveau_q4`, `niveau_avant_q4`, `realise_q4`.

**Pourquoi une exclusion pandémique pour `RGDP` et `UNEMP` seulement** (cibles 2020T1-2021T4, soit 8 trimestres) :
- En 2020, le PIB réel trimestriel annualisé a bougé de plus de 30 points, et le chômage de 10 points en un trimestre. C'est
  un arrêt administratif de l'activité, d'une taille que rien d'autre dans l'échantillon n'approche. Pour ces deux variables,
  une poignée de cibles aurait plus de poids sur c que des décennies.
- La fenêtre 2020T1-2021T4 couvre toutes les cibles dont le réalisé, la surprise (trimestre t − 4) ou les deux enquêtes
  (t − 4, t − 3) tombent en 2020.
- Les prix et les taux (`PGDP`, `CPI`, `TBILL`) gardent ces cibles : leurs mouvements de 2020 sont grands mais pas d'un autre
  ordre que 1974 ou 1980.
- L'analyse secondaire S3 remet ces cibles.
- Ce choix vient de ce que tout le monde sait de 2020, pas des données de l'enquête. Il est écrit avant toute lecture.

---

## 5. Fichier d'analyse

**Nom** : `tests-de-mort/K20/K20_analyse.csv`. Format : UTF-8, séparateur virgule, point décimal, première ligne = noms de
colonnes, cellule vide = manquant.

**Une ligne par variable × trimestre cible**, exactement **1 038 lignes**, y compris quand des valeurs manquent :
- `PGDP`, `RGDP`, `UNEMP` : cibles 1969T4 à 2026T3, numéros 7879 à 8106, soit 228 lignes chacune ;
- `CPI`, `TBILL` : cibles 1982T3 à 2026T3, numéros 7930 à 8106, soit 177 lignes chacune.

Tri : variable dans l'ordre `PGDP`, `RGDP`, `UNEMP`, `CPI`, `TBILL`, puis `t_cible` croissant.

| # | Colonne | Type | Contenu, unité |
|---|---|---|---|
| 1 | `variable` | texte | `PGDP`, `RGDP`, `UNEMP`, `CPI` ou `TBILL` |
| 2 | `cible` | texte | trimestre cible, forme `1985-Q2` |
| 3 | `t_cible` | entier | numéro du trimestre cible |
| 4 | `annee_cible` | entier | année de la cible |
| 5 | `t_enquete_h3` | entier | `t_cible` − 3 |
| 6 | `t_enquete_h4` | entier | `t_cible` − 4 |
| 7 | `prev_h3` | décimal | prévision moyenne, colonne 5 de l'enquête `t_enquete_h3`, telle que publiée ; % annualisé (`PGDP`, `RGDP`, `CPI`) ou points (`UNEMP`, `TBILL`) |
| 8 | `prev_h4` | décimal | prévision moyenne, colonne 6 de l'enquête `t_enquete_h4` |
| 9 | `nowcast_q4` | décimal | prévision moyenne, colonne 2 de l'enquête `t_enquete_h4` (trimestre `t_cible` − 4) |
| 10 | `prev_h3_med` | décimal | comme 7, médiane |
| 11 | `prev_h4_med` | décimal | comme 8, médiane |
| 12 | `millesime_realise` | texte | code du millésime de première publication (`P96Q2`, `ROUTPUT70Q1`…) pour `PGDP`, `RGDP` ; `FRED` pour les trois autres ; vide si `realise` est vide |
| 13 | `niveau_cible` | décimal | niveau du trimestre cible : indice ou milliards (`PGDP`, `RGDP`, dans ce millésime) ; moyenne de 3 mois (`CPI`, `UNEMP`, `TBILL`), au moins 8 décimales |
| 14 | `niveau_avant` | décimal | niveau du trimestre précédent (`PGDP`, `RGDP` dans le même millésime ; `CPI` moyenne de 3 mois) ; vide pour `UNEMP` et `TBILL` |
| 15 | `realise` | décimal | a(t), au moins 8 décimales |
| 16 | `millesime_realise_q4` | texte | comme 12, pour le trimestre `t_cible` − 4 |
| 17 | `niveau_q4` | décimal | comme 13, trimestre `t_cible` − 4 |
| 18 | `niveau_avant_q4` | décimal | comme 14, trimestre `t_cible` − 5 |
| 19 | `realise_q4` | décimal | a(t − 4) |
| 20 | `revision` | décimal | `prev_h3` − `prev_h4` (au moins 8 décimales) |
| 21 | `erreur` | décimal | `realise` − `prev_h3` |
| 22 | `surprise` | décimal | `realise_q4` − `nowcast_q4` |
| 23 | `revision_med` | décimal | `prev_h3_med` − `prev_h4_med` |
| 24 | `erreur_med` | décimal | `realise` − `prev_h3_med` |
| 25 | `complete` | entier | 1 si `revision`, `erreur` et `surprise` sont toutes présentes ; sinon 0 |
| 26 | `principal` | entier | 1 si `complete` = 1 et si la ligne n'est pas (`RGDP` ou `UNEMP`) avec `t_cible` de 8080 à 8087 (2020T1-2021T4) ; sinon 0 |
| 27 | `episode` | texte | `E1` … `E7` si `t_cible` tombe dans la fenêtre (section 6) ; sinon vide |
| 28 | `grande_nouvelle` | entier | L (section 6) si `surprise` est présente ; sinon vide |

Soit exactement 28 colonnes, dans cet ordre et sans aucune autre.

**Comptes attendus**, vérifiés sur les fichiers réels par la seule présence des cellules :

| | `PGDP` | `RGDP` | `UNEMP` | `CPI` | `TBILL` | Total |
|---|---|---|---|---|---|---|
| lignes | 228 | 228 | 228 | 177 | 177 | 1 038 |
| `complete` = 1 | 223 | 223 | 222 | 175 | 177 | 1 020 |
| `principal` = 1 | 223 | 215 | 214 | 175 | 177 | **1 004** |

L'échantillon principal couvre 223 trimestres cibles distincts. Les lignes principales par épisode sont : E1 15, E2 27,
E3 60, E4 35, E5 40, E6 55, E7 69 ; hors épisode, 703.

**Contrôles de schéma.** Le vérificateur les refait sur le fichier. `n_violations_schema` = nombre de contrôles violés
(0 attendu, 12 au plus). Un contrôle est violé s'il échoue sur une seule ligne. La dernière colonne dit ce qui a été vérifié
sur des lignes réelles avant le scellement (règle de la génération 3).

| N° | Contrôle | Vérifié avant scellement |
|---|---|---|
| 1 | **Colonnes** : les 28 noms ci-dessus, dans cet ordre, sans autre | noms des colonnes sources vérifiés (section 4) ; le fichier n'existe pas encore |
| 2 | **Grille** : exactement 1 038 lignes ; chaque couple (variable, `t_cible`) de la grille une seule fois ; tri conforme | oui : grille construite à partir des identifiants réels, 1 038 lignes |
| 3 | **Identifiants** : `cible` = « année-Qn » et `annee_cible` = année tirés de `t_cible` ; `t_enquete_h3` = `t_cible` − 3 ; `t_enquete_h4` = `t_cible` − 4 | oui, sur les premières lignes (1969-Q4 → 7879, enquêtes 7876 et 7875) |
| 4 | **Présence des prévisions** : `prev_h4` et `prev_h4_med` vides exactement pour les 15 lignes (`PGDP`, `RGDP`, `UNEMP`) × (1970-Q1, 1970-Q2, 1970-Q3, 1971-Q1, 1975-Q3) ; `prev_h3`, `prev_h3_med`, `nowcast_q4` jamais vides | oui, sur toutes les lignes (présence seulement) |
| 5 | **Millésimes** : pour `PGDP` (préfixe `P`) et `RGDP` (préfixe `ROUTPUT`), quand `realise` est présente, `millesime_realise` a la forme préfixe + `aaQn`, et son numéro vaut `t_cible` + 1, sauf `t_cible` + 2 exactement pour 1995-Q4, 2025-Q3 et 2025-Q4 ; même règle pour `millesime_realise_q4` avec le trimestre `t_cible` − 4 (donc + 2 pour les cibles 1996-Q4 et 2026-Q3) ; `FRED` pour les autres variables | oui, sur toutes les lignes (présence seulement) |
| 6 | **Plages plausibles** : `prev_h3`, `prev_h4`, `nowcast_q4`, versions médianes, `realise`, `realise_q4` dans [−10 ; 25] (`PGDP`), [−40 ; 40] (`RGDP`), [2 ; 16] (`UNEMP`), [−15 ; 25] (`CPI`), [−0,5 ; 20] (`TBILL`) ; niveaux dans [50 ; 300] (`PGDP`), [500 ; 40 000] (`RGDP`), [20 ; 400] (`CPI`), et les mêmes plages que les taux pour `UNEMP` et `TBILL` | sur les premières lignes seulement (enquête 1968T4 ; niveaux de 1968 vus dans `meanLevel`) ; le reste ne l'est pas, à dessein |
| 7 | **Formules** : `realise` (resp. `realise_q4`) = 100 × ((niveau / niveau_avant)⁴ − 1) à 10⁻⁶ près pour `PGDP`, `RGDP`, `CPI`, et = niveau pour `UNEMP`, `TBILL` ; vide si et seulement si une composante est vide ; `revision`, `erreur`, `surprise`, `revision_med`, `erreur_med` égales à leurs différences à 10⁻⁶ près, vides si et seulement si un opérande est vide | la convention de taux vérifiée sur la ligne 1968T4 (section 4.1) ; les différences ne sont pas calculées (ce seraient des résultats) |
| 8 | **Cohérence entre lignes** : pour toute ligne (v, t) dont la ligne (v, t − 4) existe, `realise_q4`(v, t) = `realise`(v, t − 4) à 10⁻⁶ près et `millesime_realise_q4`(v, t) = `millesime_realise`(v, t − 4), quand les deux sont présents | oui pour les codes de millésime (délais cohérents : 1995T4 ↔ 1996T4, 2025T3 ↔ 2026T3) |
| 9 | **Niveaux** : `niveau_avant` et `niveau_avant_q4` vides pour `UNEMP` et `TBILL` ; présents pour `PGDP`, `RGDP` et `CPI` quand le niveau correspondant l'est | oui (structure des sources) |
| 10 | **Indicateurs** : `complete` et `principal` conformes à leur définition | oui (présence : 1 020 et 1 004) |
| 11 | **Épisodes** : `episode` = `Ek` si et seulement si `t_cible` est dans la fenêtre k de la section 6 ; sinon vide | oui (comptes par épisode ci-dessus) |
| 12 | **Grande nouvelle** : `grande_nouvelle` présente si et seulement si `surprise` l'est ; vaut 1 si et seulement si \|`surprise`\| > Q_v, avec Q_v recalculé comme en section 6 | non : la surprise est un résultat, elle n'a pas été lue |

---

## 6. Statistique

Tout se calcule à partir du seul fichier d'analyse, en double précision, sans arrondi intermédiaire.

**Échantillon principal.** Les lignes `principal` = 1. On note n = `n_principal`, avec 1 004 attendus.

**Étape 1 — réduction**, pour chaque variable v, sur ses lignes principales :
- moyennes et écarts-types (diviseur n_v − 1) de `revision` et de `erreur` : s_{r,v} et s_{e,v} ;
- variables réduites : z_r = (`revision` − moyenne) / s_{r,v} et z_e = (`erreur` − moyenne) / s_{e,v} ;
- k_v = s_{r,v} / s_{e,v}, et `k_moyen` = moyenne des cinq k_v.

Toutes les lignes de v reçoivent ces mêmes constantes, y compris hors échantillon principal (pour S3).

**Étape 2 — grande nouvelle.** Pour chaque variable v :
- Q_v = `numpy.quantile(|surprise|, 2/3)`, méthode linéaire par défaut, calculé sur les lignes principales de v ;
- sur toute ligne où `surprise` est présente, L = 1 si |`surprise`| > Q_v, sinon 0.

Par construction, à peu près un tiers des lignes principales de chaque variable a L = 1. Q_v et L sont calculés une fois,
puis gardés tels quels dans toutes les analyses.

**Étape 3 — régression principale**, par MCO sur les lignes principales :

  z_e = Σ_v α_v·D_v + Σ_v δ_v·D_v·L + Σ_v b_v·D_v·z_r + **c**·z_r·L + u

- D_v = indicatrice de la variable v.
- 16 paramètres, dans cet ordre : 5 constantes, 5 effets de classe, 5 pentes de base, puis c.
- b_v est la pente de l'erreur sur la révision pour les petites nouvelles de la variable v ; b_v + c est la pente pour ses
  grandes nouvelles.
- **c** (`c`) est le supplément de pente commun.
- `b_moyen` = moyenne des cinq b̂_v ; `pente_moyenne_grandes` = `b_moyen` + c.

**Étape 4 — écart-type de Driscoll-Kraay à 4 retards** (« Newey-West groupé par trimestre »). On regroupe par trimestre pour
tenir compte des chocs communs aux variables, et on ajoute des retards pour le chevauchement des cibles.
1. X = matrice des 16 régresseurs ; û = résidus ; h_i = X_i·û_i.
2. Pour chaque numéro de trimestre τ, du plus petit au plus grand `t_cible` de l'échantillon, **y compris les trimestres sans
   ligne** : H_τ = Σ des h_i des lignes de ce trimestre (vecteur nul s'il n'y en a pas).
3. Ω = Σ_τ H_τ H_τ' + Σ_{j=1..4} (1 − j/5) × Σ_τ (H_τ H_{τ−j}' + H_{τ−j} H_τ').
4. V = (X'X)⁻¹ Ω (X'X)⁻¹, **sans correction de petit échantillon**.
5. `et_c_dk4` = racine de l'élément de V qui correspond à c.

On n'utilise pas `statsmodels` (`hac-groupsum`) pour le verdict : il compte les retards par position et non par trimestre,
ce qui diffère dès qu'un trimestre est vide.

**Étape 5.**
- `t_c` = c / `et_c_dk4`.
- `borne_basse_ic90` = c − 1,645 × `et_c_dk4` ; `borne_haute_ic90` = c + 1,645 × `et_c_dk4`.

**Pourquoi 4 retards.**
- L'erreur d'une prévision faite trois trimestres avant la cible contient les nouvelles du milieu du trimestre t − 3 jusqu'à
  la publication de t, un mois après la fin de t. Les erreurs de deux cibles distantes de 1, 2 ou 3 trimestres partagent donc
  des chocs : c'est une moyenne mobile d'ordre 3. Il faut au moins 3 retards.
- La règle de Newey et West, partie entière de 4 × (T/100)^(2/9), donne 4 pour T = 223 trimestres.
- C'est le choix de la fiche.
- Les poids de Bartlett sous-pondèrent les retards 2 et 3 : 8 retards sont rapportés à côté (S2).

**Observations effectives** (réponse aux juges Astra et Claude) :
- `et_c_iid` = écart-type MCO classique de c, avec σ̂² = Σû² / (n − 16) ;
- `n_effectif` = n × (`et_c_iid` / `et_c_dk4`)². C'est le nombre d'observations indépendantes qui donnerait la même
  précision ;
- on rapporte aussi `n_grands` (lignes principales avec L = 1), `n_trimestres` (trimestres distincts de l'échantillon
  principal, 223 attendus) et `n_trimestres_grands` (trimestres avec au moins une ligne L = 1).

**Champs du biais mécanique** (section 7) :
- m_{v,ℓ} = moyenne de z_r parmi les lignes principales de v avec L = ℓ ;
- a = moyenne de (z_r − m_{v,0})² sur les lignes L = 0 ; A = moyenne de (z_r − m_{v,1})² sur les lignes L = 1 ;
- `rapport_variance_revision` = A / a ;
- `biais_mecanique_nu20` = (2 × `b_moyen` + `k_moyen`) × 0,10 × (1/a − 1/A) ;
- `seuil_survie_bas` = max(0,10 ; `biais_mecanique_nu20`) ;
- `borne_basse_moins_seuil` = `borne_basse_ic90` − `seuil_survie_bas`.

**Garde de robustesse sur les épisodes (entre dans le verdict).** Les fenêtres sont en trimestres cibles, fixées
maintenant. Chacune va du pic NBER au creux NBER + 4 trimestres (dates trimestrielles du NBER, vérifiées sur FRED
`USRECQP`), et les fenêtres qui se chevauchent sont fusionnées :

| Code | Fenêtre de cibles | Numéros | Ce qu'elle contient |
|---|---|---|---|
| E1 | 1969T4-1971T4 | 7879-7887 | récession 1969T4-1970T4 |
| E2 | 1973T4-1976T1 | 7895-7904 | choc pétrolier, récession 1973T4-1975T1 |
| E3 | 1980T1-1983T4 | 7920-7935 | récessions 1980T1-1980T3 et 1981T3-1982T4 (désinflation de Volcker) |
| E4 | 1990T3-1992T1 | 7962-7968 | récession 1990T3-1991T1 |
| E5 | 2001T1-2002T4 | 8004-8011 | récession 2001T1-2001T4 |
| E6 | 2007T4-2010T2 | 8031-8041 | grande récession 2007T4-2009T2 |
| E7 | 2019T4-2023T4 | 8079-8095 | récession 2019T4-2020T2 jointe à la poussée d'inflation 2021T1-2023T4, la période du parent |

Le « + 4 » vient de ceci : la cible t dépend d'informations datées de t − 4 (surprise, première enquête) à t (réalisé). Elle
est donc touchée par un épisode [P ; T] si t est entre P et T + 4.

Pour chaque k = 1 à 7 :
- on refait l'étape 3 sur les lignes principales hors fenêtre k, avec les mêmes z et le même L ;
- on calcule l'écart-type comme à l'étape 4 (les trimestres retirés deviennent des trimestres sans ligne) ;
- on en tire c_(−k) (`c_sans_E1` … `c_sans_E7`) et t_(−k) = c_(−k) / et_(−k).

Champs :
- `t_min_sans_episode` = min_k t_(−k) ;
- `episode_t_min` = le k qui le donne (le plus petit en cas d'égalité) ;
- `c_min_sans_episode` = min_k c_(−k).

**Champs dérivés pour la règle.**
- `marge_indecision` = min(`seuil_survie_bas` − `borne_basse_ic90` ; `borne_haute_ic90` − 0,40). Elle est positive ou
  nulle exactement quand l'intervalle à 90 % contient à la fois le plancher de biais et 0,40.
- `conflit_robustesse` = 1 si les quatre conditions suivantes tiennent ; sinon 0 :
  - `borne_basse_ic90` > `seuil_survie_bas` ;
  - `borne_haute_ic90` ≥ 0,40 ;
  - `t_min_sans_episode` < 1 ;
  - `c_min_sans_episode` > 0.

**Convention.** Si n < 50, ou si une matrice X'X est singulière, tous les champs numériques concernés valent 0. L'incident
est écrit dans `ecarts.md`. Si cela touche le test principal, le verdict est de toute façon non concluant, par `n_principal`
ou par le schéma.

**Analyses secondaires — descriptives, hors verdict, calculées et rapportées quoi qu'il arrive.** Chacune reprend les
étapes 3 à 5 (écart-type de Driscoll-Kraay à 4 retards), avec les z et le L de l'échantillon principal, sauf mention
contraire.
- **S1 — par variable** : c_v propre à chaque variable (20 paramètres : α_v, δ_v, b_v, c_v). Champs `c_PGDP`, `c_RGDP`,
  `c_UNEMP`, `c_CPI`, `c_TBILL`, et leurs écarts-types `et_c_<v>_dk4`. Ils répondent à H5 : l'effet est-il seulement sur
  les prix ?
- **S2 — inférence** : `et_c_dk8` (8 retards) et `et_c_dk0` (groupement par trimestre seul, 0 retard).
- **S3 — avec la pandémie** : lignes `complete` = 1, y compris `RGDP` et `UNEMP` 2020T1-2021T4. Champs `c_avec_pandemie`,
  `et_c_avec_pandemie_dk4`.
- **S4 — depuis 1985** : lignes principales avec `t_cible` ≥ 7940 (1985T1). Champs `c_depuis_1985`,
  `et_c_depuis_1985_dk4`. Cela sépare la taille des nouvelles de l'époque : les grandes surprises sont concentrées dans les
  années 1970 et au début des années 1980.
- **S5 — avant 2020**, la condition de la fiche : lignes principales avec `t_cible` ≤ 8079 (2019T4). Champs `c_avant_2020`,
  `et_c_avant_2020_dk4`.
- **S6 — médianes** : `revision_med` et `erreur_med` à la place de `revision` et `erreur`, réduites de la même façon sur les
  mêmes lignes ; L inchangé. Champs `c_mediane`, `et_c_mediane_dk4`.
- **S7 — coupure de la fiche** : L' = 1 si |z_r| > 1 (la révision elle-même), à la place de L, partout dans l'étape 3.
  Champs `c_coupure_revision`, `et_c_coupure_revision_dk4`. L'écart entre ce chiffre et c montre combien le tri sur la
  révision change la réponse. Il n'est pas lu comme une preuve : il contient le biais de la section 7.

**Fichiers.** L'expérimentateur écrit `temoin.json` et le vérificateur `verification.json`. Les deux contiennent tous les
champs de la règle (section 12), en nombres. Ni l'un ni l'autre n'écrit de verdict.

---

## 7. Le biais mécanique : ce que le plan enlève, ce qui reste

**Le problème** (note de nouveauté, juges Kimi et Claude). Écrivons le consensus publié comme la vraie prévision plus un
bruit ε (composition changeante du panel, arrondis). Le bruit ε_t de l'enquête t entre dans la révision avec le signe +
et dans l'erreur avec le signe −. Cela produit deux effets :
1. **Covariance négative.** La pente erreur-révision est tirée vers le bas d'autant plus que la vraie révision varie peu.
   Dans la classe des petites révisions, le bruit pèse une plus grande part de la variance : la pente y est plus abaissée,
   donc c est gonflé.
2. **Sélection sur le bruit.** Si on trie sur |révision|, on trie aussi sur |ε_t|. Quand les vraies nouvelles ont des queues
   plus épaisses que le bruit, une grande révision est surtout du signal, et une petite surtout du bruit. La pente est
   écrasée en bas et pas en haut : c > 0, même si la vraie pente est partout la même.

**Ce que le plan enlève.** La classe dépend de la surprise s = a(t − 4) − F₍t−4₎(x₍t−4₎) :
- s ne contient **pas** le bruit de l'enquête t − 3, celle de la prévision évaluée. Trier sur |s| ne trie donc pas sur le
  bruit commun à la révision et à l'erreur : l'effet 2 disparaît.
- s contient le bruit de l'enquête t − 4. Ce bruit entre dans la révision (signe −) mais pas dans l'erreur. Trier sur |s|
  ajoute donc un peu de bruit à la révision dans la classe L = 1. Cela atténue davantage la pente des grandes nouvelles et
  pousse c **vers le bas**, contre l'hypothèse : sens prudent.
- Le consensus moyen (A4) réduit l'arrondi, qui fait partie de ε.

**Ce qui reste : l'atténuation différentielle (effet 1).** Si la surprise trie bien les nouvelles, la vraie révision varie
plus dans la classe L = 1. Avec un bruit de même variance partout, sa part y est plus petite. En variables réduites, si la
vraie pente vaut β partout, la pente mesurée dans la classe C vaut :

  pente_C = β − (2β + k) × ω̃ / var(z_r | C)

- ω̃ = ν/2, où ν est la part du bruit dans la variance de la révision ;
- k = s_r / s_e.

D'où un c purement mécanique :

  c_méca = (2β + k) × (ν/2) × (1/a − 1/A)

avec a et A les variances de z_r dans les classes L = 0 et L = 1. C'est exactement `biais_mecanique_nu20`, avec ν = 0,20,
β estimé par `b_moyen` et k par `k_moyen`.

**Ordre de grandeur de ν** (hypothèse non mesurée ; le mesurer demanderait les réponses individuelles) :
- Le bruit d'une moyenne de N réponses vaut environ σ_d / √N, où σ_d est la dispersion entre prévisionnistes.
- Avec N ≈ 30 à 40, une dispersion de l'ordre d'un demi à un point pour les taux trimestriels annualisés, une révision
  d'écart-type de 0,3 à 0,7 point, et la persistance des écarts individuels d'une enquête à l'autre, on obtient ν ≈ 0,02
  à 0,12 selon la variable.
- Le panel est tombé vers 15 réponses autour de 1989-1990, et les premières enquêtes arrondissaient le déflateur à l'unité.
  Là, ν est plus grand.
- **ν = 0,20 est une marge de prudence** d'environ deux fois la valeur centrale.

**Chiffres.** Avec β ≈ 0,3, k ≈ 0,3 et ν = 0,20 :

| Rapport A/a | 1/a − 1/A | c_méca |
|---|---|---|
| 2 (a = 0,75, A = 1,5) | 0,67 | ≈ 0,06 |
| 3 (a = 0,6, A = 1,8) | 1,11 | ≈ 0,10 |

D'où le plancher **max(0,10 ; `biais_mecanique_nu20`)** : la survie exige que tout l'intervalle à 90 % soit au-dessus du
biais mécanique plausible le plus haut, et pas seulement au-dessus de 0.

**Ce qui n'est pas couvert, dans les deux sens.**
- **Vers le bas** : la dispersion des prévisions monte dans les périodes agitées. Le bruit est alors plus grand dans la
  classe L = 1, ce qui réduit c_méca : le plancher est prudent.
- **Vers le haut** : si ν dépasse 0,20 (panel de 15, arrondis), le plancher est trop bas. On ne peut pas l'exclure (limite 2).

---

## 8. Arithmétique de puissance

Calculs sans donnée : loi normale, et une simulation de 200 000 tirages avec des écarts-types supposés connus.

**Écart-type de c si les observations étaient indépendantes.**
- Lignes : n ≈ 1 004, dont n_L ≈ 335 avec L = 1 et n_S ≈ 669 avec L = 0.
- Hypothèses : var(z_r | L = 1) ≈ 1,5 et var(z_r | L = 0) ≈ 0,75 (rapport 2) ; variance résiduelle ≈ 1,5 dans la classe
  L = 1 (les erreurs sont plus grandes quand les nouvelles le sont) et ≈ 0,6 dans la classe L = 0.
- Alors : ET_iid(c) ≈ √(1,5 / (335 × 1,5) + 0,6 / (669 × 0,75)) ≈ √(0,0030 + 0,0012) ≈ **0,065**.

**Trois raisons de l'augmenter** (effet de plan, sur la variance) :
1. **Chevauchement des cibles**, moyenne mobile d'ordre 3 : facteur 1 + 2 Σ_j ρ_r(j) ρ_u(j) ≈ 1,3 à 1,8.
2. **Chocs communs aux variables d'un même trimestre** : environ 4,5 lignes par trimestre, corrélation des scores 0,1 à 0,3 ;
   facteur ≈ 1,3 à 2,0.
3. **Queues épaisses et volatilité groupée** : les grandes nouvelles tombent dans peu de trimestres ; facteur ≈ 1,2 à 2,5.

| Scénario | Effet de plan | ET(c) | Observations effectives | dont grandes nouvelles |
|---|---|---|---|---|
| optimiste | 2,0 | **0,10** | ≈ 500 | ≈ 170 |
| central | 4,3 | **0,14** | ≈ 230 | ≈ 80 |
| pessimiste | 9,0 | **0,20** | ≈ 110 | ≈ 37 |

Les 1 004 lignes valent donc, au centre, environ 230 observations indépendantes, et la classe qui identifie c en vaut environ
80. La fiche annonçait environ 200 observations effectives et un écart-type de 0,15 à 0,20 : c'est le scénario central à
pessimiste.

**Seuils implicites** (plancher pris à 0,10) :

| ET(c) | survit si ĉ > | éliminée si ĉ < | effet qui survit 8 fois sur 10 |
|---|---|---|---|
| 0,10 | 0,265 | 0,236 | 0,35 |
| 0,14 | 0,330 | 0,170 | 0,45 |
| 0,20 | 0,429 | 0,071 | 0,60 |

**Probabilités des trois issues**, survit / éliminée / non concluant, garde d'épisodes comprise. Simulation : sept épisodes
qui portent respectivement 3, 10, 17, 4, 5, 10 et 12 % de l'information sur c ; le reste en porte 39 %.

| Vrai c | ET = 0,10 | ET = 0,14 (central) | ET = 0,20 |
|---|---|---|---|
| −0,20 (H2 ou H3) | 0 / 100 / 0 % | 0 / 100 / 0 % | 0 / 91 / 9 % |
| 0 (H0) | 0 / 99 / 1 % | 1 / 89 / 10 % | 2 / 64 / 34 % |
| +0,07 (biais mécanique seul) | 3 / 95 / 2 % | 3 / 76 / 21 % | 4 / 50 / 46 % |
| +0,20 (bas de la plage de la fiche) | 26 / 64 / 10 % | 18 / 41 / 41 % | 13 / 26 / 61 % |
| +0,30 | 64 / 26 / 10 % | 41 / 18 / 41 % | 26 / 13 / 61 % |
| **+0,40 (prédiction)** | **91 / 5 / 4 %** | **69 / 5 / 26 %** | **44 / 5 / 51 %** |
| +0,60 (haut de la plage) | 100 / 0 / 0 % | 97 / 0 / 2 % | 80 / 0 / 19 % |
| moyenne 0,40 mais portée par E7 seul | 16 / 46 / 38 % | 16 / 25 / 59 % | 16 / 8 / 76 % |
| moyenne 0,40 mais portée par E3 seul | 16 / 46 / 38 % | 16 / 25 / 59 % | 16 / 9 / 75 % |

**Lecture.**
- **Le test ne survit pas au seul biais mécanique** : 3 à 4 % de survie si le vrai c ne vaut que le biais (0,07).
- **Au centre, il tranche aux deux bouts** : il élimine une interaction nulle 9 fois sur 10, et fait survivre la prédiction
  (0,40) 7 fois sur 10.
- **Il tranche mal au milieu** : un vrai c de 0,20 survit 18 % du temps et est éliminé 41 % du temps. La fiche le disait :
  un effet de 0,2 ne serait pas détecté.
- **Dans le scénario pessimiste, il est faible** : la prédiction ne survit que 44 % du temps, et un c nul n'est éliminé que
  64 % du temps. Un « non concluant » sera alors fréquent, et sera un vrai résultat de puissance, pas un échec de
  construction.
- **La garde d'épisodes coûte presque rien** quand l'effet est partout (les colonnes « survit » coïncident avec la condition
  principale seule). Mais elle ramène à 16 % la survie d'un effet porté par un seul épisode. Avec le signe seul (la fiche),
  ce serait environ 50 %.
- Ces probabilités supposent un écart-type de Driscoll-Kraay juste. Avec 223 trimestres et des queues épaisses, il est
  souvent un peu trop petit (limite 7).

**Minimum d'échantillon.** 1 004 lignes principales sont attendues, comptées sur les fichiers réels. Sous 1 000 (plus de
4 lignes perdues de façon imprévue), la construction a un problème. Le verdict est alors « non concluant ».

---

## 9. Règle de verdict

Le verdict est calculé par `verdict.py` à partir des chiffres du vérificateur. « Survit » veut dire : sur 1969-2026, la
pente de l'erreur sur la révision du consensus est plus forte après une grande surprise. Ce supplément est
significativement au-dessus du biais mécanique plausible, compatible avec la taille prédite (0,40), et ne tient à aucun
épisode isolé.

**Non concluant** si l'une de ces conditions est vraie :
1. `n_violations_schema` > 0 : le fichier d'analyse est hors schéma. On ne juge pas une idée sur un fichier douteux.
2. `n_principal` < 1 000 : voir « Minimum d'échantillon » (section 8).
3. `rapport_variance_revision` < 1,25 : la classe des grandes surprises n'a pas des révisions nettement plus grandes. Le tri
   ne sépare pas les grandes nouvelles des petites, et le test ne mesure pas ce que demande la question. Seuil : avec un tri
   au hasard, le rapport vaudrait environ 1. On demande 25 % de variance en plus, soit 12 % d'écart-type, ce qui reste
   modeste.
4. `marge_indecision` ≥ 0 : l'intervalle à 90 % contient à la fois le plancher de biais et 0,40. Les données ne
   choisissent pas.
5. `conflit_robustesse` ≥ 1 : l'intervalle est au-dessus du plancher et contient 0,40, mais retirer un épisode fait tomber
   t sous 1 sans changer le signe. La preuve est fragile sans être contredite.
6. Écart entre expérimentateur et vérificateur au-delà de la tolérance sur un champ, ou champ absent (protocole).

**Survit** si aucune condition ci-dessus n'est vraie et si les trois suivantes le sont :
- `borne_basse_moins_seuil` > 0 : tout l'intervalle à 90 % est au-dessus de max(0,10 ; biais calculé). C'est un test
  unilatéral à 5 % : l'hypothèse a un sens (c > 0). Le plancher remplace 0 parce qu'une partie de c peut être mécanique
  (section 7).
- `borne_haute_ic90` ≥ 0,40 : 0,40 est la prédiction ponctuelle de la fiche, reprise sans changement, avec la même logique
  que le parent J02.
- `t_min_sans_episode` ≥ 1,0 : sans n'importe lequel des sept épisodes, l'interaction reste au moins à un écart-type
  au-dessus de 0. Ce seuil bloque 84 % des effets portés par un seul épisode, pour un coût de puissance presque nul
  (section 8). Le seuil 1,645 dans chaque exclusion coûterait trop de puissance (juge Gemini), et le signe seul ne bloquerait
  qu'une fois sur deux (juge Kimi).

**Éliminée** dans tous les autres cas. Avec les conditions de non-conclusion, cela arrive exactement dans deux cas :
- **(a)** `borne_haute_ic90` < 0,40 : les données excluent, au seuil unilatéral de 5 %, le supplément de 0,40 prédit. Cela
  vaut si c est nul, négatif (H2 ou H3), ou positif mais nettement plus petit que prévu.
- **(b)** le test principal passe, mais `c_min_sans_episode` ≤ 0 : sans un épisode, l'interaction disparaît ou change de
  signe. La réponse à « cela tient-il sur plusieurs grands chocs ? » est alors non.

**Tolérances** (écart maximal entre expérimentateur et vérificateur, qui calculent sur le même fichier) :
- 0 sur les champs entiers ;
- 0,005 sur les coefficients, écarts-types, moyennes et biais ;
- 0,01 sur les bornes, marges, plancher et rapport de variances ;
- 0,02 sur les t ;
- 1 sur `n_effectif`.

---

## 10. Limites

1. **Le plan n'est pas aveugle.** Le rédacteur connaît la littérature, le verdict du parent, l'histoire des épisodes et
   l'ampleur de 2020 (d'où l'exclusion pandémique). Aucune donnée de résultat n'a été lue. Mais on ne peut pas prouver que
   ces connaissances n'ont pas orienté les choix.
2. **Le biais mécanique est borné, pas supprimé.** Le plancher suppose qu'au plus 20 % de la variance des révisions est du
   bruit. Dans les enquêtes à 15 réponses (vers 1989-1990) et dans les premières enquêtes, arrondies, ce peut être plus.
   Sans les réponses individuelles, on ne mesure pas ν.
3. **Le test porte sur les grandes surprises, pas sur la non-linéarité dans la révision.** Les MCO pondèrent par le carré de
   la révision. Les grandes révisions dominent donc déjà la pente des deux classes. Si le vrai mécanisme est un seuil dans la
   taille de la révision (le modèle de la fiche : +0,4 au-delà d'un écart-type), le tri par la surprise ne le montre qu'à
   environ 0,06 à 0,15, ce qui est indétectable. Une élimination dira alors : « pas de sous-réaction plus forte après les
   grandes surprises ». Elle ne dira pas : « aucune non-linéarité dans la révision ». S7 donne le chiffre de la coupure de
   la fiche, à lire avec son biais.
4. **Taille ou époque.** Les grandes surprises sont concentrées dans les années 1970 et au début des années 1980.
   Coibion et Gorodnichenko trouvent moins de rigidité à cette époque, ce qui joue contre l'hypothèse. S4 (depuis 1985) le
   sépare en partie, hors verdict.
5. **Données anciennes.**
   - Le calendrier des enquêtes ASA/NBER d'avant 1990T2 est incertain.
   - `RGDP` est calculé avant 1981T3.
   - Les prévisions portent sur le PNB avant 1992.
   - La surprise des cibles `PGDP` et `RGDP` 1996T4 et 2026T3 s'appuie sur une publication que les prévisionnistes n'avaient
     pas encore vue (publication retardée).
6. **Réalisés mixtes.** On prend la première publication pour les comptes nationaux et le dernier millésime pour le reste.
   Les bons du Trésor viennent de moyennes mensuelles du marché secondaire, alors que l'enquête vise la moyenne des taux
   quotidiens. Les écarts sont de quelques centièmes.
7. **Écart-type de Driscoll-Kraay.** Avec 223 trimestres, des grandes nouvelles concentrées dans peu d'entre eux et des
   queues épaisses, il est souvent trop petit, ce qui rend la survie un peu trop facile. S2 (8 retards, 0 retard) le dira,
   sans corriger le verdict.
8. **Choix d'échantillon.**
   - L'exclusion pandémique de `RGDP` et `UNEMP` est un choix (S3 la défait).
   - Octobre 2025 manque (chômage, IPC), ce qui retire trois cibles.
   - Le consensus moyen est sensible à une réponse aberrante (S6 montre la médiane).
9. **Une seule statistique décide.** Les analyses secondaires (environ vingt chiffres) sont descriptives. Aucune ne peut
   sauver ni tuer l'idée, et l'on ne cherchera pas après coup celle qui « marche ».
10. **Sous-réaction ou lissage.** Comme pour le parent, une pente positive peut venir d'une agrégation de prévisionnistes
    rationnels mais mal informés, ou d'un lissage voulu. On écrira « les erreurs suivent davantage les révisions après les
    grandes surprises », jamais « les prévisionnistes sont irrationnels ».

---

## 11. Ce qu'on écrira dans chaque cas

- **Survit** : « Sur 1 004 couples variable × trimestre (1969-2026, cinq variables de l'enquête), la pente de l'erreur sur
  la révision du consensus est plus forte de c (intervalle à 90 %) dans le tiers des trimestres qui suivent les plus
  grandes surprises sur les données. C'est plus que le biais de mesure plausible le plus haut, compatible avec le +0,40
  prédit, et l'effet reste à au moins un écart-type de zéro quel que soit l'épisode retiré. La sous-réaction n'est donc pas
  propre à 2021-2023. » On donne à côté : `n_effectif`, c par variable, c depuis 1985, c avec la médiane, c avec la coupure
  de la fiche.
- **Éliminée, interaction négative** (`borne_haute_ic90` < 0) : « Après les grandes surprises, les erreurs suivent *moins*
  les révisions, et la pente des grandes nouvelles vaut `pente_moyenne_grandes`. Cela va dans le sens des modèles où
  l'attention monte avec les chocs (Coibion et Gorodnichenko 2015) ou de la sur-réaction aux nouvelles extrêmes (de Silva et
  coauteurs 2025). La sous-réaction de la BCE en 2021-2022 n'est pas une règle des grands chocs. »
- **Éliminée, interaction indistinguable de zéro** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` ≤ 0) : « La pente de
  l'erreur sur la révision ne dépend pas de la taille des surprises de façon détectable, et les données excluent au seuil de
  5 % le supplément de 0,40 prédit. »
- **Éliminée, interaction positive mais plus petite que prévu** (`borne_haute_ic90` < 0,40 et `borne_basse_ic90` > 0) :
  « Les erreurs suivent un peu plus les révisions après les grandes surprises, mais nettement moins que prédit. Une partie
  de cet écart peut venir du bruit de mesure (plancher `seuil_survie_bas`). »
- **Éliminée, effet porté par un épisode** (`c_min_sans_episode` ≤ 0 avec le test principal passé) : « L'interaction est
  significative sur toute la période, mais elle disparaît sans l'épisode `episode_t_min`. La plus forte sous-réaction aux
  grandes nouvelles tient à ce seul choc, comme la pente de la BCE tenait à 2021-2022. »
- **Non concluant, par indécision** (`marge_indecision` ≥ 0) : « Avec environ `n_effectif` observations effectives,
  l'intervalle à 90 % de c contient à la fois le biais de mesure plausible et le +0,40 prédit. On publie l'intervalle et on
  ne conclut pas. »
- **Non concluant, par conflit** (`conflit_robustesse` = 1) : « L'interaction est au-dessus du plancher sur toute la
  période et reste positive sans chaque épisode, mais à moins d'un écart-type de zéro sans `episode_t_min`. On ne conclut
  pas. »
- **Non concluant, par pertinence** (`rapport_variance_revision` < 1,25) : « Les grandes surprises sur les données
  n'entraînent pas de révisions nettement plus grandes. Le tri ne sépare pas les grandes nouvelles des petites, et la
  question reste ouverte. Il faudrait les réponses individuelles pour trier sur la révision sans biais. »
- **Non concluant, par les données** (schéma, moins de 1 000 lignes, fichier manquant, écart entre expérimentateur et
  vérificateur) : « Le test n'a pas pu être mené comme préinscrit. La raison exacte est dans `ecarts.md`, et aucune
  conclusion n'est tirée sur l'hypothèse. »

---

## 12. Règle lisible par machine

```json
{
  "id": "K20",
  "fichier_analyse": "K20_analyse.csv",
  "champs_verification": [
    "n_violations_schema",
    "n_principal",
    "c",
    "et_c_dk4",
    "t_c",
    "borne_basse_ic90",
    "borne_haute_ic90",
    "rapport_variance_revision",
    "b_moyen",
    "k_moyen",
    "pente_moyenne_grandes",
    "biais_mecanique_nu20",
    "seuil_survie_bas",
    "borne_basse_moins_seuil",
    "marge_indecision",
    "t_min_sans_episode",
    "c_min_sans_episode",
    "episode_t_min",
    "conflit_robustesse",
    "n_grands",
    "n_trimestres",
    "n_trimestres_grands",
    "et_c_iid",
    "n_effectif",
    "c_sans_E1",
    "c_sans_E2",
    "c_sans_E3",
    "c_sans_E4",
    "c_sans_E5",
    "c_sans_E6",
    "c_sans_E7",
    "et_c_dk8",
    "et_c_dk0",
    "c_avec_pandemie",
    "et_c_avec_pandemie_dk4",
    "c_depuis_1985",
    "et_c_depuis_1985_dk4",
    "c_avant_2020",
    "et_c_avant_2020_dk4",
    "c_mediane",
    "et_c_mediane_dk4",
    "c_coupure_revision",
    "et_c_coupure_revision_dk4",
    "c_PGDP",
    "c_RGDP",
    "c_UNEMP",
    "c_CPI",
    "c_TBILL",
    "et_c_PGDP_dk4",
    "et_c_RGDP_dk4",
    "et_c_UNEMP_dk4",
    "et_c_CPI_dk4",
    "et_c_TBILL_dk4"
  ],
  "survit_si": [
    {"champ": "borne_basse_moins_seuil", "operateur": ">", "seuil": 0},
    {"champ": "borne_haute_ic90", "operateur": ">=", "seuil": 0.40},
    {"champ": "t_min_sans_episode", "operateur": ">=", "seuil": 1.0}
  ],
  "non_concluant_si": [
    {"champ": "n_violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "n_principal", "operateur": "<", "seuil": 1000},
    {"champ": "rapport_variance_revision", "operateur": "<", "seuil": 1.25},
    {"champ": "marge_indecision", "operateur": ">=", "seuil": 0},
    {"champ": "conflit_robustesse", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "n_violations_schema": 0,
    "n_principal": 0,
    "c": 0.005,
    "et_c_dk4": 0.005,
    "t_c": 0.02,
    "borne_basse_ic90": 0.01,
    "borne_haute_ic90": 0.01,
    "rapport_variance_revision": 0.01,
    "b_moyen": 0.005,
    "k_moyen": 0.005,
    "pente_moyenne_grandes": 0.005,
    "biais_mecanique_nu20": 0.005,
    "seuil_survie_bas": 0.01,
    "borne_basse_moins_seuil": 0.01,
    "marge_indecision": 0.01,
    "t_min_sans_episode": 0.02,
    "c_min_sans_episode": 0.005,
    "episode_t_min": 0,
    "conflit_robustesse": 0,
    "n_grands": 0,
    "n_trimestres": 0,
    "n_trimestres_grands": 0,
    "et_c_iid": 0.005,
    "n_effectif": 1,
    "c_sans_E1": 0.005,
    "c_sans_E2": 0.005,
    "c_sans_E3": 0.005,
    "c_sans_E4": 0.005,
    "c_sans_E5": 0.005,
    "c_sans_E6": 0.005,
    "c_sans_E7": 0.005,
    "et_c_dk8": 0.005,
    "et_c_dk0": 0.005,
    "c_avec_pandemie": 0.005,
    "et_c_avec_pandemie_dk4": 0.005,
    "c_depuis_1985": 0.005,
    "et_c_depuis_1985_dk4": 0.005,
    "c_avant_2020": 0.005,
    "et_c_avant_2020_dk4": 0.005,
    "c_mediane": 0.005,
    "et_c_mediane_dk4": 0.005,
    "c_coupure_revision": 0.005,
    "et_c_coupure_revision_dk4": 0.005,
    "c_PGDP": 0.005,
    "c_RGDP": 0.005,
    "c_UNEMP": 0.005,
    "c_CPI": 0.005,
    "c_TBILL": 0.005,
    "et_c_PGDP_dk4": 0.005,
    "et_c_RGDP_dk4": 0.005,
    "et_c_UNEMP_dk4": 0.005,
    "et_c_CPI_dk4": 0.005,
    "et_c_TBILL_dk4": 0.005
  }
}
```
