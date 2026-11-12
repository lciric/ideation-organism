# F01 — Préenregistrement du test de mort

Texte figé avant toute lecture de rendements. Le rédacteur n'exécute rien ; l'expérimentateur construit `panel.csv` et
calcule ; le vérificateur recalcule à partir de `panel.csv` et de ce seul texte ; le verdict est rendu par `verdict.py`.

**Ce que le rédacteur a lu pour écrire ce texte.** La fiche, les failles des trois juges, la note de nouveauté ; l'article de
McLean et Pontiff (2016), sections II.B et II.D, pour vérifier la définition de leurs indicatrices ; `SignalDoc.csv` en
entier (table descriptive : années de publication et d'échantillon, aucune série de rendement) ; les 200 derniers kilooctets
de `PredictorLSretWide.parquet` (pied de fichier : noms et types des colonnes) ; les notes de version 2026.10.
Tous les effectifs cités plus bas sont calculés **à partir des seules années** de `SignalDoc.csv`, en supposant les rendements
complets. Aucun rendement mensuel n'a été lu, aucune moyenne, régression ou statistique de rendement n'a été calculée.

---

## 1. Question, hypothèse, prédiction

**Question.** Quand une anomalie est publiée, son rendement long-court baisse-t-il **de plus** que ce qu'expliquent, aux
mêmes mois, la fin de son échantillon d'origine et le mouvement commun des anomalies pas encore publiées ?

**Grandeur estimée, notée θ.** Écart moyen, pendant les cinq années civiles qui suivent l'année de publication, entre le
rendement mensuel réalisé d'une anomalie et le rendement qu'elle aurait eu au même mois si elle était restée « sortie de son
échantillon d'origine mais pas encore publiée », divisé par le rendement mensuel moyen des anomalies sur leur échantillon
d'origine. θ = −0,30 se lit : « la publication retire 30 % du rendement d'origine, en plus de la baisse de fin d'échantillon ».

**Hypothèse (celle de la fiche).** θ < 0.

**Prédiction chiffrée (celle de la fiche, inchangée).** θ entre −0,20 et −0,40, valeur centrale **−0,30**, soit environ
−13 à −26 points de base par mois pour un rendement d'origine moyen de 65 points de base.
Les deux autres prédictions de la fiche (baisse de −10 % à −25 % entre fin d'échantillon et publication ; absence de tendance
préalable) ne sont pas jugées : la première est rapportée à titre descriptif, la seconde devient une garde de validité (§ 5.3).

**Position par rapport aux travaux les plus proches.**

| Travail | Ce qu'il donne pour cette grandeur | Ce qu'il ne tranche pas |
|---|---|---|
| McLean et Pontiff (2016), tableau II, col. 1 (97 prédicteurs, effets fixes de prédicteur, sans contrôle du temps) | après échantillon mais avant publication : −15,0 pb ; après publication : −33,7 pb ; écart −18,7 pb, soit **−32 %** de 58,2 pb ; test d'égalité p = 0,024 | aucun contrôle du calendrier |
| McLean et Pontiff (2016), tableau III, col. 4 (effets fixes de mois ajoutés) | −17,9 pb et −31,0 pb ; écart −13,1 pb, soit **−22,5 %** | **l'écart n'est ni testé ni assorti d'une erreur type** ; les effets de mois sont estimés en se servant aussi des prédicteurs déjà publiés comme témoins |
| Xiong et Pelger (2019), section 7 (contrefactuel par facteurs latents tiré des anomalies pas encore publiées) | plus de 80 % des anomalies baissent, environ 14 % de façon significative à 5 % (d'après la note de nouveauté) | des tests anomalie par anomalie, peu puissants ; pas d'effet moyen groupé avec intervalle, dans l'unité de McLean et Pontiff |

Deux précisions.
1. Les deux indicatrices de McLean et Pontiff sont **exclusives** (la première vaut 1 « after the end of the original
   sample but still pre-publication »). L'effet propre à la publication est donc la **différence** des deux coefficients.
   Le « −53 % » relevé par la note de nouveauté est la baisse totale par rapport à l'échantillon d'origine, pas la grandeur
   de la fiche ; la grandeur comparable est −22,5 % (avec effets de mois) ou −32 % (sans), toutes deux **dans** la
   fourchette prédite par la fiche. La note de nouveauté se trompe sur ce point de lecture, pas sur les chiffres.
2. Ce que ce test peut ajouter : **un seul nombre groupé, avec son intervalle, pour l'effet propre à la publication, où le
   calendrier est mesuré uniquement sur des anomalies pas encore publiées**, sur 189 anomalies au lieu de 97. C'est la
   grandeur qui sépare la lecture de McLean et Pontiff (θ ≈ −0,2 à −0,3) de la lecture « fin d'échantillon et calendrier »
   (θ ≈ 0) vers laquelle penchent Xiong et Pelger. Ce test **n'ajoute pas de période** : sa fenêtre s'arrête en 2013,
   comme celle de McLean et Pontiff.

---

## 2. Amendements déclarés au test de la fiche

| # | Test de la fiche | Ce texte | Raison |
|---|---|---|---|
| A1 | Choix de plan fixés sur les cohortes publiées jusqu'en 2000 ; verdict sur les cohortes 2001-2011 | Aucune phase d'exploration. Tout est fixé ici sans lire de rendement ; toutes les cohortes dont les années traitées tombent dans 1974-2013 sont jugées (publication 1977 à 2012, 189 anomalies) | Faille « puissance » du juge 3. Réserver des cohortes ne sert plus à rien puisque rien n'est exploré, et coûte 57 anomalies traitées sur 189 |
| A2 | Variable : rendement mensuel divisé par la moyenne d'origine de l'anomalie | Rendement brut en % par mois ; une seule division, à la fin, par la moyenne d'origine des anomalies traitées | Faille « rendement normalisé très bruité » (juge 3) : un petit dénominateur fait exploser le bruit d'une anomalie. C'est aussi l'unité de McLean et Pontiff (pb, puis rapport à 58,2 pb) |
| A3 | Régression empilée, effets fixes pile×mois et pile×anomalie, coefficients par temps d'événement ; témoins = anomalies publiées au moins cinq ans plus tard | Estimateur par imputation en deux étapes (§ 5.1) : un modèle ajusté sur les seules observations d'anomalies pas encore publiées, puis la moyenne des écarts « réalisé moins prédit » sur les observations traitées | Même principe (jamais une anomalie déjà publiée comme témoin), robuste aux effets hétérogènes que la fiche renvoyait à une robustesse, et **un seul nombre** recalculable. La règle « publiée au moins cinq ans plus tard » laissait 21 témoins à la cohorte 2008, 4 à la cohorte 2011 et aucun ensuite ; ici, à chaque mois, toute anomalie pas encore publiée sert |
| A4 | Deux ruptures distinguées pour l'anomalie traitée seulement | Un décalage commun « sortie de l'échantillon d'origine » appliqué à **toute** anomalie, témoins compris | Un témoin qui sort de son échantillon d'origine pendant la fenêtre baisse pour cause de sélection statistique ; sans ce terme la comparaison est biaisée contre l'hypothèse |
| A5 | Date de publication = année (reconnu comme risque) | Convention : l'année de publication est **exclue des deux côtés** ; traité = années civiles P+1 à P+5 ; témoin jusqu'à P−1. Fenêtre de robustesse en analyse secondaire S1 | Failles 1 et 2 (date imprécise, atténuation vers zéro). Aucun mois n'est mal classé ; coût : jusqu'à douze mois d'après publication perdus |
| A6 | Erreurs groupées par mois et par anomalie | Jackknife par blocs d'une année civile (40 blocs), valeur critique de Student à 16 degrés de liberté | Failles 2 et 3 (anomalies corrélées). Toutes les anomalies d'une même année partent ensemble : corrélations entre anomalies et dépendance à l'intérieur de l'année sont couvertes. Aucun tirage aléatoire, donc expérimentateur et vérificateur obtiennent le même nombre. Le groupement par anomalie est abandonné (limite L6) |
| A7 | Meurt si l'intervalle à 95 % contient 0 ou si l'estimation est plus faible que 10 % | Trois issues. Survie : conditions de la fiche, inchangées. Élimination : l'intervalle contient 0 (ou l'effet est sous 10 %) **et** exclut −0,30. Sinon non concluant | Faille 3. À la précision attendue (§ 6), la règle de la fiche tuerait une hypothèse vraie de la taille prédite environ trois fois sur dix, et plus d'une fois sur deux si l'erreur type est en haut de fourchette. Un non-rejet n'est pas une preuve d'absence |
| A8 | Garde : coefficients d'avance conjointement significatifs → plan invalide | Garde conservée, réduite à **un** coefficient d'avance (dernière année civile avant publication) | L'attente entre fin d'échantillon et publication dure 3 à 4 ans en moyenne : il n'y a pas de quoi estimer cinq avances |
| A9 | Mêmes calculs sur les signaux placebo | Retirés du test de mort | Leur moyenne d'origine est proche de zéro (rapport non défini) et le nombre d'analyses secondaires est plafonné à trois. Restent au programme du projet si l'idée survit |
| A10 | « Dix ans de données en plus » | Abandonné comme argument | Note de nouveauté : il ne reste plus assez d'anomalies pas encore publiées après 2013 (14 en 2013, 6 en 2014, 0 après 2015) |

Ce qui ne peut pas être corrigé par le plan est listé au § 9.

---

## 3. Données

Source unique : Open Source Asset Pricing (Chen et Zimmermann), version **2026.10**, branche `Data-Release-2026.10`,
sans compte.

| Fichier | Adresse exacte | Testé | Contenu utile |
|---|---|---|---|
| Table des signaux | `https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/Data-Release-2026.10/SignalDoc.csv` | 200, 183 100 octets | `Acronym`, `Cat.Signal`, `Year`, `SampleStartYear`, `SampleEndYear` (parmi 29 colonnes) |
| Rendements long-court | `https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/Data-Release-2026.10/Portfolios/Full%20Sets%20OP/PredictorLSretWide.parquet` | 206 sur requête partielle, 1 439 671 octets | colonne `date` (type date), puis 212 colonnes réelles nommées par `Acronym` ; rendement mensuel **en pour cent** du mois indiqué |
| Notes de version (pour mémoire) | `https://huggingface.co/datasets/OpenSourceAP/CrossSection/resolve/Data-Release-2026.10/Release%20Notes%202026.10.md` | 200 | données jusqu'à décembre 2025 ; unités ; exceptions |

Il n'existe pas de version CSV des rendements (404) : lire le Parquet avec `pyarrow` ou `polars` (à installer ; absent de la
machine au moment de l'écriture). Fichiers placebo, portefeuilles complets : non utilisés.

**Anomalies gardées.** Toutes les lignes de `SignalDoc.csv` avec `Cat.Signal == "Predictor"` (212 attendues), jointes aux
colonnes de même nom du Parquet. Aucun filtre sur la performance, la statistique t ou la qualité de reproduction.

**Mois gardés dans `panel.csv`.** Tous les mois où le rendement existe (de 1926 à 2025).
L'estimation n'utilise que les années civiles **1974 à 2013** (première année où une anomalie peut être traitée ;
dernière année où il reste au moins 14 anomalies pas encore publiées par mois). Les mois d'échantillon d'origine
antérieurs à 1974 ne servent qu'à calculer la moyenne d'origine.

**Ce qui compte comme manquant.**
- Un des deux fichiers n'est pas obtenu en HTTP 200 après cinq essais espacés : donnée manquante, verdict « non concluant ».
- Une taille différente de celles ci-dessus : noté dans `ecarts.md`, on continue si les contrôles de schéma passent.
- Un prédicteur de la table sans colonne dans le Parquet, ou dont une des trois années est vide : exclu, nommé dans `ecarts.md`.
- Un rendement mensuel absent (nul, NaN) : pas de ligne. Jamais remplacé, ni par zéro ni par interpolation.
  Exceptions connues d'après les notes de version : `Activism1`, `Activism2`, `Governance` s'arrêtent en 2007,
  `PatentsRD` en 2006, `ProbInformedTrading` en 2012.
- Une anomalie avec moins de 60 lignes de statut `origine` : exclue de l'estimation (elle reste dans `panel.csv`), nommée dans `ecarts.md`.
- Les effectifs minimaux du § 7 décident si ces pertes rendent le test non concluant.

---

## 4. Fichier d'analyse : `tests-de-mort/F01/panel.csv`

CSV UTF-8, séparateur virgule, point décimal, une ligne d'en-tête. **Une ligne par anomalie × mois** où le rendement existe.
Environ 150 000 lignes attendues. Triées par `signal` puis `date`.

Notations par anomalie : P = `annee_pub`, D = `annee_debut_ech`, F = `annee_fin_ech`.

| Colonne | Type | Unité, définition |
|---|---|---|
| `signal` | texte | `Acronym` de la table des signaux |
| `date` | texte `AAAA-MM` | mois du rendement (colonne `date` du Parquet ramenée au mois) |
| `annee` | entier | année civile de `date` |
| `ret` | réel | rendement long-court du mois, **en % par mois** (1,25 veut dire 1,25 %), tel que fourni, signe inchangé, au moins 10 chiffres significatifs |
| `annee_pub` | entier | `Year` |
| `annee_debut_ech` | entier | `SampleStartYear` |
| `annee_fin_ech` | entier | `SampleEndYear` |
| `statut` | texte | `avant` si annee < D ; `origine` si D ≤ annee ≤ F ; `attente` si F < annee < P ; `annee_pub` si annee = P ; `publie` si P+1 ≤ annee ≤ P+5 ; `apres` si annee > P+5 |
| `dans_fenetre` | entier 0/1 | 1 si 1974 ≤ annee ≤ 2013 |
| `moy_origine` | réel | % par mois ; moyenne de `ret` sur **toutes** les lignes `origine` de l'anomalie (toutes dates) ; même valeur sur toutes les lignes de l'anomalie ; vide s'il n'y en a aucune |

**Contrôles de schéma** (le vérificateur les refait tous ; `n_violations_schema` = nombre de contrôles en échec) :
1. Colonnes exactement celles du tableau, dans cet ordre.
2. Couple (`signal`, `date`) unique.
3. Au plus 212 valeurs distinctes de `signal`.
4. `date` au format `AAAA-MM`, mois de 01 à 12 ; `annee` égale aux quatre premiers caractères ; 1926 ≤ annee ≤ 2025.
5. `ret` présent et fini sur toutes les lignes ; médiane de |`ret`| sur tout le fichier entre 0,5 et 10 (preuve que l'unité est le pour cent).
6. `annee_pub`, `annee_debut_ech`, `annee_fin_ech` constantes par anomalie ; D ≤ F < P ; 1973 ≤ P ≤ 2016.
7. `statut` égal à la règle du tableau, recalculée.
8. `dans_fenetre` égal à la règle, recalculée.
9. `moy_origine` constante par anomalie et égale à la moyenne recalculée, à 1e-8 près.
10. Identifiabilité : la matrice de l'étape 1 du § 5.1 (indicatrices d'anomalie, indicatrices de mois sauf le premier mois, indicatrice `attente`) est de plein rang colonne sur l'échantillon complet.

Effectifs attendus si aucun rendement ne manque dans la fenêtre (calculés sur les années seules, pour repérer une erreur
de construction ; un écart de quelques pour cent est normal) : 57 204 lignes `origine` et 8 904 lignes `attente` dans
l'ensemble U ; 10 296 lignes dans l'ensemble T, venant de 189 anomalies ; 210 anomalies présentes dans U.

---

## 5. Statistique

Aucun tirage aléatoire nulle part : pas de graine. Coût : une régression d'environ 66 000 lignes et 700 indicatrices,
refaite 41 fois pour la statistique principale et 41 fois pour la garde, puis autant pour chaque analyse secondaire ;
quelques minutes sur un portable, sans carte graphique.

### 5.1 Statistique principale : `theta`

Soit K l'ensemble des anomalies ayant au moins 60 lignes `origine`.

- **U** (observations non traitées) : lignes avec `dans_fenetre = 1`, `statut` ∈ {`origine`, `attente`}, `signal` ∈ K.
- **T** (observations traitées) : lignes avec `dans_fenetre = 1`, `statut = publie`, dont l'anomalie a au moins une ligne
  dans U et dont le mois a au moins une ligne dans U.

Les lignes `avant`, `annee_pub` et `apres` ne servent à rien dans la statistique principale : une anomalie déjà publiée
n'est jamais témoin.

**Étape 1.** Moindres carrés ordinaires, non pondérés, sur U :

```
ret[i,t] = a[i] + l[t] + b * att[i,t] + e[i,t]
```

`a[i]` : un effet fixe par anomalie ; `l[t]` : un effet fixe par mois (`date`) ; `att[i,t]` = 1 si `statut = attente`, 0 sinon.
Une indicatrice de mois est omise (le premier mois de U) ; les valeurs ajustées ne dépendent pas de ce choix.

**Étape 2.** Pour chaque ligne de T :

```
tau[i,t] = ret[i,t] − ( â[i] + l̂[t] + b̂ )
```

c'est-à-dire le réalisé moins ce que le modèle prédit pour la même anomalie, le même mois, si elle était encore en attente.

**Agrégation.**

```
tau_bar = moyenne simple de tau[i,t] sur les lignes de T          (% par mois)
m_bar   = moyenne simple de moy_origine[i] sur les lignes de T    (% par mois)
theta   = tau_bar / m_bar
```

### 5.2 Erreur type et intervalle : jackknife par année civile

Pour chaque année g de 1974 à 2013 ayant au moins une ligne dans U ou T (`n_blocs` = leur nombre G, 40 attendu) :
retirer de U et de T toutes les lignes avec `annee = g` ; redéfinir T (anomalie et mois encore présents dans U réduit) ;
refaire les étapes 1 et 2 ; calculer `theta_g = tau_bar_g / m_bar_g`. Les `moy_origine` ne sont pas recalculées.

```
theta_point       = moyenne des G valeurs theta_g
se_theta          = racine( (G − 1) / G × somme sur g de (theta_g − theta_point)² )
borne_basse_ic95  = theta − 2,12 × se_theta
borne_haute_ic95  = theta + 2,12 × se_theta
marge_ambiguite   = min( borne_haute_ic95 , −0,30 − borne_basse_ic95 )
```

`theta` est l'estimation sur l'échantillon complet (§ 5.1), pas `theta_point`. La constante 2,12 est le quantile 97,5 %
d'une loi de Student à 16 degrés de liberté : les 40 années ne pèsent pas autant (2005-2013 portent les deux tiers des
lignes traitées) et le nombre effectif de blocs, (somme des effectifs traités par année)² / somme de leurs carrés, vaut 17.
`marge_ambiguite ≥ 0` veut dire exactement : l'intervalle contient à la fois 0 et −0,30.

### 5.3 Garde de validité, reprise de la fiche : `t_avance`

Ce n'est ni la statistique principale ni une analyse descriptive : elle ne peut que rendre le test non concluant.
Même régression qu'à l'étape 1, sur U, avec un terme de plus :

```
ret[i,t] = a[i] + l[t] + b * att[i,t] + d * av[i,t] + e[i,t]
```

`av[i,t]` = 1 si `statut = attente` et `annee = annee_pub − 1`, 0 sinon. `se_d` par le même jackknife (mêmes 40 blocs,
même formule, appliquée à `d`). `t_avance = d̂ / se_d`. Si |t_avance| ≥ 2,12, le rendement de la dernière année avant
publication s'écarte déjà de celui des années d'attente précédentes : le plan est déclaré invalide.

### 5.4 Trois analyses secondaires, descriptives, sans effet sur le verdict

Calculées par l'expérimentateur seulement, rapportées avec leur erreur type jackknife (même formule), étiquetées
« descriptif » partout où elles apparaissent.

- **S1 — Fenêtre sur la date de publication.** (a) T = années P à P+4 (l'année de publication comptée comme traitée), U inchangé.
  (b) T inchangé, lignes `attente` de l'année P−1 retirées de U (témoins arrêtés deux ans avant la parution).
- **S2 — Biais de sélection propre à chaque anomalie.** À l'étape 1, remplacer `a[i] + b*att` par un effet fixe par couple
  (anomalie, statut) ; à l'étape 2, prédire avec l'effet (anomalie, `attente`) ; T restreint aux anomalies ayant au moins une
  ligne `attente` dans U.
- **S3 — Spécification de McLean et Pontiff sur les mêmes données.** Lignes `dans_fenetre = 1` de statut `origine`, `attente`,
  `publie`, `apres` ; régression de `ret` sur effets fixes d'anomalie et de mois, une indicatrice `attente` et une indicatrice
  « publiée » (`publie` ou `apres`) ; rapporter les deux coefficients et leur différence divisée par la moyenne simple des
  `moy_origine`. Sert à voir ce que change le fait d'interdire les témoins déjà publiés.

---

## 6. Arithmétique de puissance

Tout ce qui suit vient des années de publication et d'échantillon, et de chiffres publiés ; rien ne vient des rendements.

**Trois plans comparés avant de choisir.** L'estimateur est linéaire dans les rendements : son erreur type vaut
σ × (racine de la somme des carrés des poids), et les poids ne dépendent que des dates. Avec σ l'écart type mensuel
résiduel d'un rendement long-court :

| Plan | Erreur type de `tau_bar` | Observations indépendantes équivalentes |
|---|---|---|
| Témoins = seules observations `attente` (ni échantillon d'origine, ni décalage commun) | 0,058 σ | 300 |
| Effet fixe (anomalie, statut), témoins `origine` + `attente` (analyse S2) | 0,023 σ | 1 960 |
| **Plan retenu** : effet fixe d'anomalie + décalage commun `attente` | **0,0171 σ** | **3 400** |

Le premier plan, le plus « propre », est inutilisable : les périodes d'attente durent 1 à 10 ans et se chevauchent peu, si
bien que le mouvement commun du calendrier n'y est connu que de proche en proche. Le plan retenu paie sa précision par une
hypothèse (limite L3). Il vaut 3 400 anomalies-mois indépendantes et non 10 296, pour deux raisons : le décalage commun
repose sur 8 904 lignes `attente` ; et près de la moitié des lignes traitées tombent en 2008-2013, quand il ne reste que 54
puis 14 anomalies pas encore publiées par mois. En blocs : 40 années, 17 effectives.

**Bruit.** McLean et Pontiff (tableau II) donnent un écart de 18,7 pb entre leurs deux coefficients avec p = 0,024, donc une
erreur type d'environ 8,3 pb, obtenue avec à peu près 97 × 56 = 5 400 mois d'attente et 97 × 156 = 15 100 mois publiés :
σ effectif ≈ 5,2 % par mois, corrélations entre anomalies comprises (corrélation moyenne qu'ils rapportent : 0,033).
Fourchette retenue : σ de 4,0 à 5,5 %.

- Erreur type de `tau_bar` : 0,0171 × (4,0 à 5,5) = **6,8 à 9,4 pb par mois**.
- Rendement d'origine moyen `m_bar` : 58 pb (McLean et Pontiff) à 75 pb.
- Erreur type de `theta` : **0,09 à 0,16, valeur centrale 0,12.** Le juge 3 annonçait 0,15 à 0,20 pour le plan de la fiche.
- Effet prédit : −0,30. Rapport effet / erreur type : 2,5 au centre, 1,9 dans le mauvais cas, 3,3 dans le bon.

**Ce que fait la règle du § 7** (approximation normale ; dernière colonne : probabilité de mourir sous la règle d'origine de la fiche) :

| Erreur type | Vrai θ | survit | éliminée | non concluant | règle de la fiche : meurt |
|---|---|---|---|---|---|
| 0,09 | 0 | 2 % | 89 % | 10 % | 97 % |
| 0,09 | −0,20 | 54 % | 16 % | 30 % | 40 % |
| 0,09 | −0,30 | 89 % | 2 % | 10 % | 9 % |
| 0,09 | −0,40 | 99 % | 0 % | 1 % | 1 % |
| **0,12** | **0** | **2 %** | **65 %** | **34 %** | 97 % |
| 0,12 | −0,20 | 33 % | 10 % | 58 % | 62 % |
| **0,12** | **−0,30** | **65 %** | **2 %** | **34 %** | 30 % |
| 0,12 | −0,40 | 89 % | 0 % | 11 % | 9 % |
| 0,16 | 0 | 2 % | 40 % | 58 % | 97 % |
| 0,16 | −0,20 | 19 % | 7 % | 74 % | 76 % |
| 0,16 | −0,30 | 40 % | 2 % | 58 % | 53 % |
| 0,16 | −0,40 | 65 % | 0 % | 35 % | 30 % |

**Lecture honnête.** Le test **peut** tuer une hypothèse fausse (θ = 0 : éliminée 65 % du temps au centre, déclarée à tort
survivante 2 % du temps) et **peut** laisser vivre une hypothèse vraie de la taille prédite (θ = −0,30 : survit 65 %, tuée à
tort 2 %). Mais il est **faible** : au centre de la fourchette il ne tranche que deux fois sur trois, et quatre fois sur dix
si l'erreur type est à 0,16. Un effet vrai au bas de la fourchette prédite (−0,20) serait tué à tort 7 à 16 % du temps.
La cause est structurelle : entre la fin de l'échantillon d'origine et la publication, il n'existe au total qu'environ 9 000
anomalies-mois, et aucun plan ne peut connaître le niveau « hors échantillon, pas encore publié » mieux que
σ / racine(9 000) ≈ 5 pb, soit 0,08 en unité de θ. Les trois plans ci-dessus sont la trace de la recherche d'un plan plus
puissant ; il n'y en a pas de meilleur sans hypothèse supplémentaire.

**Garde `t_avance`.** Son erreur type attendue est 0,025 σ, soit 10 à 14 pb : elle ne voit qu'une anticipation massive
(plus de 25 pb environ). Fausse alerte : 5 % par construction.

---

## 7. Règle de verdict

Nombres pris dans `verification.json` (ceux du vérificateur). Dans cet ordre :

1. **Non concluant** si l'une de ces conditions est vraie :
   - `n_lignes_traitees` < 9 000 (lignes de T sur l'échantillon complet ; 10 296 attendues) ;
   - `n_anomalies_traitees` < 170 (anomalies distinctes dans T ; 189 attendues) ;
   - `n_lignes_attente` < 7 800 (lignes `attente` de U ; 8 904 attendues) ;
   - `n_blocs` < 40 ;
   - `n_violations_schema` > 0 ;
   - `t_avance` ≥ 2,12 ou `t_avance` ≤ −2,12 (plan invalide) ;
   - `marge_ambiguite` ≥ 0 (l'intervalle à 95 % contient à la fois 0 et −0,30) ;
   - et, selon le protocole : fichier nommé manquant, ou écart entre expérimentateur et vérificateur au-delà de la tolérance.
2. Sinon **survit** si `borne_haute_ic95` < 0 **et** `theta` ≤ −0,10.
3. Sinon **éliminée** : l'intervalle contient 0 (ou l'effet est inférieur à 10 % en valeur absolue) et il exclut −0,30.

Tolérances entre expérimentateur et vérificateur : 0,005 sur `theta`, `se_theta` ; 0,015 sur les deux bornes et sur
`marge_ambiguite` ; 0,003 sur `tau_bar`, `m_bar`, `b_attente` (% par mois) ; 0,05 sur `t_avance` ; 0 sur les effectifs.
`b_attente` (le coefficient b̂ de l'étape 1) est rapporté sans entrer dans le verdict. L'expérimentateur imprime les mêmes
champs, à titre de témoin ; `n_lignes_traitees`, `n_anomalies_traitees` et `n_lignes_attente` se comptent sur l'échantillon complet.

---

## 8. Ce qu'on écrira dans chaque cas

- **Survit.** « Comparé, aux mêmes mois, à des anomalies pas encore publiées, le rendement long-court d'une anomalie baisse
  dans les cinq années civiles qui suivent sa publication de [−100 × theta] % de son rendement d'origine (intervalle à 95 % :
  [bornes]), en plus de la baisse commune de fin d'échantillon : l'effet de publication de McLean et Pontiff résiste quand le
  calendrier est mesuré sur les seules anomalies pas encore publiées, sur une fenêtre qui ne dépasse pas la leur (2013). »
- **Éliminée.** « Comparé, aux mêmes mois, à des anomalies pas encore publiées, on ne détecte pas de baisse propre à la
  publication (theta = [valeur], intervalle à 95 % : [bornes]) et une baisse de 30 % ou plus est rejetée : sur ces données,
  l'érosion après publication ne se distingue pas de la baisse de fin d'échantillon et du mouvement commun du calendrier — sans
  exclure que la diffusion avant parution ait déjà agi pendant l'attente. »
- **Non concluant.** « Le test ne tranche pas ([condition déclenchée] ; theta = [valeur], intervalle à 95 % : [bornes]) : ces
  données ne permettent ni de confirmer ni d'écarter un effet de publication de la taille prédite, et aucune conclusion sur
  l'hypothèse n'en est tirée. »

---

## 9. Limites que le plan ne corrige pas

- **L1 — Puissance.** Voir § 6 : une fois sur trois au centre, plus d'une fois sur deux dans le mauvais cas, le test finit
  non concluant quelle que soit la vérité.
- **L2 — La date de traitement est celle de la revue.** Les documents de travail circulent souvent deux ou trois ans avant ;
  la période d'attente est donc peut-être déjà en partie « traitée », ce qui tire θ vers zéro. Une élimination peut refléter
  une diffusion plus précoce plutôt qu'une absence d'effet. La table ne donne aucune date de document de travail ; la garde
  `t_avance` ne voit que la dernière année et seulement une anticipation massive.
- **L3 — Décalage de fin d'échantillon supposé commun.** Si le biais de sélection varie d'une anomalie à l'autre et se trouve
  lié à la durée d'attente, θ est biaisé. S2 lève l'hypothèse, avec une erreur type attendue un tiers plus grande, et reste descriptive.
- **L4 — Pas de données nouvelles.** Fenêtre close en 2013, mêmes titres américains que McLean et Pontiff et Xiong et Pelger :
  c'est une autre méthode sur le même passé, pas une confirmation indépendante.
- **L5 — Mouvement du calendrier supposé additif** et commun aux anomalies encore dans leur échantillon d'origine et aux autres.
- **L6 — Inférence conditionnelle aux 189 anomalies.** Le jackknife par année couvre les corrélations entre anomalies, pas une
  dépendance d'une même anomalie au-delà de l'année ni le tirage des anomalies dans une population plus large.
- **L7 — Portefeuilles reconstruits.** Les rendements sont ceux de la reproduction ouverte (construction de l'article d'origine),
  pas les quintiles de McLean et Pontiff ; un écart avec leurs chiffres peut venir de là.
- **L8 — Cohortes tronquées ou absentes.** Les cohortes 2009-2012 ont moins de cinq années traitées dans la fenêtre ;
  23 anomalies (publiées en 1973 ou de 2013 à 2016) ne sont jamais traitées.

---

## 10. Règle lisible par machine

```json
{
  "id": "F01",
  "fichier_analyse": "panel.csv",
  "champs_verification": [
    "theta",
    "se_theta",
    "borne_basse_ic95",
    "borne_haute_ic95",
    "marge_ambiguite",
    "tau_bar",
    "m_bar",
    "b_attente",
    "t_avance",
    "n_lignes_traitees",
    "n_anomalies_traitees",
    "n_lignes_attente",
    "n_blocs",
    "n_violations_schema"
  ],
  "survit_si": [
    {"champ": "borne_haute_ic95", "operateur": "<", "seuil": 0},
    {"champ": "theta", "operateur": "<=", "seuil": -0.10}
  ],
  "non_concluant_si": [
    {"champ": "n_lignes_traitees", "operateur": "<", "seuil": 9000},
    {"champ": "n_anomalies_traitees", "operateur": "<", "seuil": 170},
    {"champ": "n_lignes_attente", "operateur": "<", "seuil": 7800},
    {"champ": "n_blocs", "operateur": "<", "seuil": 40},
    {"champ": "n_violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "t_avance", "operateur": ">=", "seuil": 2.12},
    {"champ": "t_avance", "operateur": "<=", "seuil": -2.12},
    {"champ": "marge_ambiguite", "operateur": ">=", "seuil": 0}
  ],
  "tolerance": {
    "theta": 0.005,
    "se_theta": 0.005,
    "borne_basse_ic95": 0.015,
    "borne_haute_ic95": 0.015,
    "marge_ambiguite": 0.015,
    "tau_bar": 0.003,
    "m_bar": 0.003,
    "b_attente": 0.003,
    "t_avance": 0.05,
    "n_lignes_traitees": 0,
    "n_anomalies_traitees": 0,
    "n_lignes_attente": 0,
    "n_blocs": 0,
    "n_violations_schema": 0
  }
}
```
