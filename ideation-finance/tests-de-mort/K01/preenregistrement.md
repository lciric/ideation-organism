# K01 — Préinscription du test de mort : les prévisionnistes de l'enquête de la BCE sur-réagissent-ils à leurs propres nouvelles ?

Rédigé le 2026-11-12 par le rédacteur de préinscription de K01. Le rédacteur n'a lancé aucune analyse : aucune erreur, aucune
révision, aucune moyenne, aucune régression et aucune statistique n'a été calculée sur les données. Les seuls calculs faits
sont des comptages de présence (identifiants, tours, cibles), des contrôles de format, et des calculs de puissance théoriques
(loi normale), sans donnée.

**Ce que le rédacteur a lu.** `brief.md` ; `tests-de-mort/protocole.md` et `tests-de-mort/verdict.py` ;
`generation-3/regle-generation-3.md` ; la fiche K01 de `generation-3/jugements/fiches-anonymes-generation-3.md` et les failles
des quatre juges (`agregat-generation-3.json`) ; la note de nouveauté `generation-3/nouveaute/K01.md` ; dans
`tests-de-mort/J02`, **seulement** `preenregistrement.md` et `verdict.json` ; dans `tests-de-mort/H03-v2`, **seulement** des
passages de `preenregistrement.md` (correspondance lettre / mois des millésimes, colonne `TITLE_COMPL`). Aucun fichier
d'analyse, dossier de données, script ou rapport de ces tests.

**Ce que le rédacteur a vu des données** (téléchargées le 2026-11-12 dans un dossier temporaire, hors du dépôt).
- Enquête de la BCE (`SPF_microdata_by_variable.zip`, HTTP 200) : la liste des fichiers de l'archive, les en-têtes de
  `1_HICP.csv` et de `0_Round_dates.csv`, le texte de `README_SPF_microdata.pdf`, et des comptages (types de cible, décalage
  entre année cible et année du tour, format des identifiants, format des nombres, doublons, nombre de lignes présentes par
  tour et par horizon, nombre de valeurs hors de [−5 ; 15]). **Incident déclaré** : l'affichage des trois premières lignes de
  `1_HICP.csv` a montré deux valeurs du tour 1999T1 (prévisionniste `001`, une prévision ponctuelle et une probabilité). Ce
  tour est hors de l'échantillon. Aucune autre valeur n'a été affichée.
- Base MPD de la BCE : 97 séries annuelles téléchargées (HTTP 200 pour les 97). Ont été lus : les années présentes, leur
  statut (`OBS_STATUS`), `KEY`, `TITLE_COMPL`, le nombre de décimales et le nombre de valeurs hors de [−5 ; 15]. **Aucune
  valeur de `OBS_VALUE` n'a été affichée.**
- Eurostat `prc_hicp_ainr` (HTTP 200) : en-tête, années présentes, dimensions, drapeaux, date de mise à jour, nombre de
  décimales, nombre de valeurs hors de [−5 ; 15]. **Aucune valeur n'a été affichée.**
- Les chiffres publiés de J02 (`verdict.json`), cités en section 1.

---

## 1. Question, hypothèses rivales et prédiction chiffrée

**Question.** Dans l'enquête de la BCE auprès des prévisionnistes professionnels (SPF), quand un prévisionniste révise à la
hausse sa prévision d'inflation pour une année civile, finit-il, en moyenne, trop haut (il a sur-réagi), alors que la moyenne
de l'enquête (le consensus) et les projections des services de la BCE finissent trop bas (ils ont sous-réagi) ?

**Définitions.** Un prévisionniste i, un tour d'enquête t (trimestriel), une année cible y (inflation IPCH moyenne de
l'année civile y, en %) :
- F(i, t, y) = prévision ponctuelle de i au tour t pour l'année y ;
- **révision** x = F(i, t, y) − F(i, t − 1, y) : même personne, même année cible, tour précédent ;
- **erreur** e = π(y) − F(i, t, y), où π(y) est l'inflation réalisée de l'année y.

Une année cible est prévue au plus 8 fois par une même personne : aux quatre tours de l'année y − 1 (comme « année
suivante ») puis aux quatre tours de l'année y (comme « année en cours »). Cela donne jusqu'à 7 révisions par personne et par
année cible.

**La pente erreur-révision** (Coibion et Gorodnichenko, 2015 ; Bordalo, Gennaioli, Ma et Shleifer, 2020) : pente b de la
régression de e sur x.
- b = 0 : la révision n'annonce pas l'erreur (pas de sous- ni de sur-réaction prévisible).
- b > 0 : après une révision à la hausse, l'inflation finit encore au-dessus. La prévision a **sous-réagi**.
- b < 0 : après une révision à la hausse, l'inflation finit en dessous. La prévision a **sur-réagi**.

**Hypothèses rivales** (ce que chacune prédit pour la statistique principale b_IV, définie en section 3, et pour les pentes
descriptives).

| | Hypothèse | b_IV (individus) | Consensus, BCE | Pente naïve intra-tour |
|---|---|---|---|---|
| H1 (la fiche) | Chaque prévisionniste sur-réagit à ses propres nouvelles ; la sous-réaction du consensus et de la BCE est un effet d'agrégation | **< 0** | > 0 | < 0 |
| H0a | Prévisionnistes rationnels mais informés chacun de façon partielle (information dispersée) | **= 0** | > 0 | < 0 (section 2) |
| H0b | Pas de sur-réaction ; les chiffres rapportés contiennent un bruit de saisie ou d'arrondi propre à chaque chiffre | **= 0** | ≥ 0 | < 0 (section 2) |
| H2 | Chaque prévisionniste sous-réagit lui-même (inattention, information visqueuse) | **> 0** | > 0 | non informative |

H0a et H0b produisent elles aussi une pente intra-tour négative : c'est pourquoi la statistique de la fiche ne peut pas
départager (section 2).

**Prédiction chiffrée, positionnée contre Broer et Kohlhas (2024).** Sur l'enquête de la BCE, 2000T1-2020T1, prévisions à un
an glissant, Broer et Kohlhas trouvent une pente individuelle de **−0,169 (écart-type 0,182)** par MCO, avec effets fixes de
répondant, et une pente du consensus de **0,740 (0,406)**. Pour l'inflation américaine, Bordalo et coauteurs trouvent −0,07
(0,10) sans effets fixes et −0,16 (0,07) avec effets fixes de prévisionniste. La fiche centrait sa pente individuelle sur
−0,15.

- **Prédiction de H1 pour b_IV : −0,15**, plage plausible −0,35 à 0. C'est l'ordre de grandeur de Broer et Kohlhas et de
  Bordalo et coauteurs. Dans le modèle simple des anticipations « diagnostiques » (section 2.4), −0,15 correspond à un
  paramètre de distorsion θ ≈ 0,18 ; θ = 0,5 donnerait −0,30.
- Pentes descriptives prédites par la fiche : consensus ≈ +0,4 ; BCE ≈ +0,4 (non distinguables).

**Ce que ce test ajoute à Broer et Kohlhas.**
1. La période 2020T2-2025T4, dont la poussée d'inflation de 2021-2023.
2. Des cibles annuelles à date fixe (année en cours et année suivante), au lieu d'un horizon glissant.
3. Un traitement du biais mécanique : la révision est instrumentée (section 3). Broer et Kohlhas utilisent les MCO.
4. Les trois pentes, sur les mêmes années cibles : individus, consensus et services de la BCE.

**Attente du rédacteur, pour mémoire, hors verdict.** Dans une régression sans effets fixes de temps, les erreurs communes
de 2021-2022 (tout le monde a révisé à la hausse et est resté très en dessous) pèsent beaucoup et tirent b_IV vers le haut. Le
rédacteur s'attend à une estimation de b_IV entre −0,3 et +0,3, à un écart-type de l'ordre de 0,25, et donc, le plus
probablement, au verdict « non concluant » (section 8). Il s'attend aussi à une pente naïve intra-tour nettement négative,
quel que soit le comportement réel (section 2). Le plan n'a pas été réglé pour faire survivre l'idée : le seuil de survie
(borne haute < 0) est celui de la fiche.

---

## 2. Pourquoi la statistique de la fiche ne peut pas trancher

La fiche prenait la pente « intra-tour » : régression de l'erreur sur la révision avec des effets fixes cible × tour (et
prévisionniste), c'est-à-dire en ne gardant que les écarts entre prévisionnistes d'un même tour. Les quatre juges ont relevé
que cette pente est négative mécaniquement. Il y a trois raisons, et la troisième (le bruit) n'est pas la seule.

**2.1 Le réalisé disparaît.** À tour et à année cible donnés, tous les prévisionnistes ont la même inflation réalisée π(y).
L'écart de l'erreur de i à la moyenne du tour vaut donc exactement −(F(i,t,y) − F̄(t,y)) : c'est l'écart de sa prévision à la
moyenne, changé de signe. L'inflation réalisée n'entre plus dans le calcul. Notons d_t l'écart de i à la moyenne au tour t,
V_t sa variance dans la population des prévisionnistes et C la covariance entre d_t et d_{t−1}. La pente intra-tour vaut
alors :

  pente intra-tour = Cov(−d_t, d_t − d_{t−1}) / Var(d_t − d_{t−1}) = −(V_t − C) / (V_t + V_{t−1} − 2C).

Elle ne dépend que de l'évolution de la **dispersion** des prévisions. Elle ne dit rien de leur justesse. Si la dispersion
est la même aux deux tours (V_t = V_{t−1}), elle vaut **exactement −1/2**, quel que soit le comportement des prévisionnistes.
On remarque que la valeur publiée par Kučinskas et Peters sur l'enquête américaine (−0,49) en est proche. On n'en tire aucune
conclusion sur leur travail, dont on n'a pas vérifié la définition exacte de la révision.

**2.2 Même des prévisionnistes rationnels donnent une pente intra-tour négative.** Pour un prévisionniste rationnel,
l'erreur n'est prévisible par rien de ce qu'il sait au tour t, y compris sa propre révision. Donc, sur toutes les
observations mises ensemble, Cov(e, x) = 0. Or, par la loi de la covariance totale :

  Cov(e, x) = moyenne des covariances intra-tour + covariance entre tours des moyennes (ē_t, x̄_t).

Le second terme est le numérateur de la pente du **consensus**. Avec une information dispersée, le consensus sous-réagit
(Coibion et Gorodnichenko, 2015) : ce terme est positif. Le premier terme est donc **négatif**, de même taille. Une pente
intra-tour négative est ainsi une prédiction de H0a, pas seulement de H1. (Ce calcul est fait ici ; on ne l'a pas trouvé
écrit sous cette forme dans les travaux lus.)

**2.3 Le bruit de mesure.** Si le chiffre rapporté vaut la croyance plus un bruit η de variance σ² et d'autocorrélation φ,
la révision contient +η_t − η_{t−1} et l'erreur −η_t. La pente estimée est déplacée de −σ²(1 − φ)/Var(x) (Juodis et
Kučinskas, 2023). Les effets fixes ne retirent pas ce bruit, qui est propre à chaque personne. Ils l'aggravent même, en
retirant la variation commune de la révision.

**2.4 Pourquoi pas la révision retardée comme instrument.** C'était la piste naturelle (Bordalo et coauteurs régressent
l'erreur sur des révisions antérieures). Elle ne convient pas ici. Pour une prévision à date fixe, la révision d'un
prévisionniste rationnel est imprévisible à partir de son passé : c'est une différence de martingale. Dans le modèle simple
des anticipations diagnostiques, la prévision rapportée vaut F_t = F*_t + θ(F*_t − F*_{t−1}), où F* est la prévision
rationnelle. On a alors :
- erreur e_t = e*_t − θ ΔF*_t ;
- révision retardée ΔF_{t−1} = (1 + θ) ΔF*_{t−1} − θ ΔF*_{t−2}.

Ni e*_t ni ΔF*_t ne sont prévisibles par le passé. Donc Cov(e_t, ΔF_{t−1}) = 0 et la pente instrumentée vaut 0, **même quand
la sur-réaction existe (θ > 0)**. Sous H0a, la première étape vaut même zéro (instrument faible). La révision retardée n'a
donc pas de puissance contre H1. Il faut un instrument qui bouge avec les nouvelles du tour t, mais pas avec le bruit du
chiffre évalué.

**Conséquence.** La pente intra-tour (et la pente MCO simple) est rapportée **à titre descriptif seulement**. Elle n'entre
pas dans le verdict.

---

## 3. La statistique retenue, en mots

**Régression regroupée, sans effets fixes de temps.** On garde toutes les observations (prévisionniste × tour × année cible)
dans une seule régression, avec une constante par horizon (année en cours, année suivante). Sans effets fixes de temps, le
réalisé reste dans l'erreur. Sous **toute** hypothèse de rationalité (H0a comprise), l'erreur est imprévisible par ce que le
prévisionniste sait au tour t : la pente vaut 0. C'est la définition de Bordalo et coauteurs et de Broer et Kohlhas.

**Instrument : la révision, au même tour, de l'autre année cible.** À chaque tour, le prévisionniste donne deux prévisions
annuelles : l'année en cours et l'année suivante. Pour l'observation « année y », on instrumente la révision de y par la
révision, au même tour et par la même personne, de l'autre année (y + 1 si y est l'année en cours, y − 1 si y est l'année
suivante). Deux moindres carrés en deux étapes, un seul instrument :
- **première étape** : on explique la révision de l'année y par la révision de l'autre année ;
- **seconde étape** : on régresse l'erreur sur la partie de la révision ainsi expliquée.

**Pourquoi cela traite le bruit.** Une nouvelle sur l'inflation (un prix du pétrole, un chiffre mensuel) fait réviser les
deux années dans le même sens : l'instrument est corrélé à la révision. En revanche, une faute de frappe ou un arrondi sur
le chiffre de l'année y n'a pas de raison de se retrouver dans le chiffre de l'autre année. Le bruit propre au chiffre évalué
n'entre pas dans l'instrument, donc il ne crée plus de pente mécanique.

**Pourquoi l'instrument reste valide sous l'hypothèse nulle.** La révision de l'autre année est connue du prévisionniste au
tour t. Sous la rationalité, elle ne prédit pas l'erreur. La pente instrumentée vaut 0 sous H0a et H0b.

**Ce qu'elle vaut sous H1.** Dans le modèle diagnostique de 2.4, avec des chocs stables d'un tour à l'autre, la pente
instrumentée vaut −θ(1 + θ)/((1 + θ)² + θ²) : −0,09 pour θ = 0,1 ; −0,15 pour θ = 0,18 ; −0,30 pour θ = 0,5. C'est la
même valeur que les MCO donneraient sans bruit. L'instrument a donc de la puissance contre H1.

**Ce qu'il ne traite pas.** Un bruit **commun aux deux années** (par exemple un écart de communication du prévisionniste qui
déplace tous ses chiffres du même tour) reste dans l'instrument. Le biais devient −ρσ²(1 − φ)/Cov(x, z), où ρ est la
corrélation du bruit entre les deux années. On rapporte le bruit commun qui suffirait à produire la pente observée
(`sigma_bruit_commun_necessaire_iv`, section 6) : c'est la borne explicite de Juodis et Kučinskas, adaptée à l'instrument.

**Inférence.** Sans effets fixes de temps, l'erreur a une forte part commune : tous les prévisionnistes d'une même année cible
partagent la même inflation réalisée, et une année cible est prévue lors de 8 tours. Grouper par tour seul (96 groupes)
supposerait les tours indépendants, ce qui est faux. On calcule, pour chaque tour, la somme des contributions de ses
observations au numérateur de la pente, ce qui donne une série de 96 nombres. On prend la variance de long terme de cette
série par Newey-West à **8 retards** (deux ans : les 8 tours qui partagent une année cible). C'est l'écart-type de Driscoll et
Kraay, c'est-à-dire un groupement par tour étendu aux tours voisins. Valeur critique unilatérale : **1,714**, quantile à 95 %
de la loi de Student à 23 degrés de liberté. On ne compte en effet pas plus de 24 années cibles indépendantes (2002-2025).
L'écart-type groupé par tour seul (96 groupes) et l'écart-type groupé par année cible (24 groupes) sont rapportés à titre
descriptif.

---

## 4. Amendements déclarés à la fiche

| N° | La fiche disait | Ce test fait | Raison |
|---|---|---|---|
| A1 | Statistique de mort : pente intra-tour (effets fixes cible × tour et prévisionniste) de l'erreur réduite sur la révision réduite | Pente regroupée **instrumentée** (révision de l'autre année au même tour), sans effets fixes de temps ni de prévisionniste, en points d'erreur par point de révision ; la pente intra-tour est descriptive | Les quatre juges et la note de nouveauté : la pente intra-tour est négative mécaniquement. La section 2 montre trois raisons, dont l'identité 2.1 (le réalisé disparaît) |
| A2 | Variables réduites | Variables en points de pourcentage, non réduites | Avec un instrument, réduire ne fait que changer d'échelle ; la pente brute se compare directement à Broer et Kohlhas et à Bordalo et coauteurs |
| A3 | Effets fixes de prévisionniste | Retirés de la statistique principale ; une version avec effets fixes est rapportée (`b_iv_ef_prev`) | Sous la rationalité, la pente vaut 0 sans eux. Avec environ 90 observations par prévisionniste, le retrait de la moyenne individuelle introduit des révisions futures dans le régresseur (biais de type Nickell). La version avec effets fixes sert à la comparaison avec Broer et Kohlhas |
| A4 | « Écarts types groupés par tour » (test de mort) ; « Newey-West à 4 retards » (méthode) | Driscoll-Kraay : sommes par tour, Newey-West à 8 retards ; valeur critique 1,714 ; groupement par tour (96) et par année cible (24) rapporté | Sans effets fixes de temps, les erreurs d'une même année cible sont communes à 8 tours : il faut au moins 7 retards |
| A5 | Tours 2002-2026 | Tours **2002T1-2025T4** (96 tours) ; années cibles **2002-2025** | Les cibles 2026 et 2027 ne sont pas réalisées (note de nouveauté, correction 5) |
| A6 | Réalisé : « première publication annuelle » | Millésime fixe : Eurostat `prc_hicp_ainr`, taux de variation de la moyenne annuelle (`RCH_A_AVG`), mise à jour du 17/09/26 | Eurostat ne sert pas de base de millésimes (note de nouveauté, correction 6) |
| A7 | BCE : moyennes annuelles tirées des trajectoires trimestrielles de la MPD | Séries **annuelles** `MPD.A.U2.HIC.A.<millésime>.0000` | Note de nouveauté, correction 4 |
| A8 | « Meurt aussi si la pente est négative sur l'échantillon complet mais pas sur 2002-2019 (borne supérieure ≥ 0) » | Garde de signe : b_IV hors années cibles 2021-2023 < 0, sinon éliminée. Clause symétrique : si l'effet n'apparaît que sans 2021-2023, non concluant. La pente sur les cibles 2002-2019 est rapportée à titre descriptif | Garder l'esprit de la fiche (le résultat ne doit pas tenir à la poussée de 2021-2023). Sans ces années, il reste 21 années cibles, trop peu pour un second test : on demande un signe |
| A9 | Deux issues (meurt ou non) | Trois issues, avec une zone d'indécision : l'intervalle à 90 % contient à la fois 0 et −0,15 | Section 7 : avec un écart-type de l'ordre de 0,25, « éliminée » ne voudrait plus rien dire si l'on éliminait chaque fois que l'intervalle touche 0 |
| A10 | Robustesse : exclusion des prévisionnistes présents moins de 8 tours ; retrait d'une année à la fois | La règle des 8 tours devient la règle de l'échantillon principal ; le retrait d'une année cible à la fois est rapporté (`b_iv_max_sans_une_annee`) | Fixer l'échantillon avant de voir les chiffres |
| A11 | Comparaison BCE-consensus descriptive | Inchangé, descriptive ; on ajoute l'écart BCE − consensus et son écart-type, et ce qu'on peut et ne peut pas en conclure (section 7) | Faille principale relevée par les juges : le manque de puissance |
| A12 | Rôle de l'IA : deux agents de nettoyage et un script de différences | Rôles du protocole (expérimentateur, vérificateur, `verdict.py`) ; contrôles de schéma automatiques | Le protocole remplace ce dispositif |

---

## 5. Données

Tous les fichiers bruts sont enregistrés dans `tests-de-mort/K01/donnees/`, avec sha256, date et code HTTP dans
`tests-de-mort/K01/construire_journal.json`. Téléchargements : jusqu'à 10 essais, délai maximal de 120 s par essai, 10 s entre
deux essais. Si un fichier nommé ici manque, l'expérimentateur s'arrête : non concluant pour une raison de données.

**Source 1 — prévisions individuelles de l'enquête de la BCE.**

```
https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip
```

- Testé le 2026-11-12 : HTTP 200, 12 035 888 octets, sha256 `49348fa33c5e5d58aa3e05aac56cf5df23ab29439862ab6e3ccafe68797b51f4`.
- L'archive contient **deux copies** de chaque fichier : l'une à la racine, l'autre sous `D:/spf-disc-casper/output_files/`.
  Les deux copies de `1_HICP.csv` ont le même sha256 (`a8e99246d20bbf3ac81dabfdc3ce2d2a7ad19889a532372d37e166d44f585aa7`).
  **On lit la copie à la racine.**
- Si l'archive téléchargée a un autre sha256 (mise à jour par la BCE), on continue avec elle et on l'écrit dans `ecarts.md`.
  La fenêtre de tours est fixée ci-dessous, donc l'ajout de tours postérieurs à 2025T4 ne change rien.
- Fichier `1_HICP.csv`, colonnes `ref_round, fct_topic, forecaster_id, target_period_type, target_period, table_name,
  prob_interval, value` (CSV, guillemets, `NA` pour vide).
- Lignes retenues : `table_name` = `Point` ; `forecaster_id` numérique (codes à trois chiffres, `001` à `137` ; les codes
  `AGG` et `ECB` sont exclus : `AGG` est la moyenne publiée, `ECB` une valeur de référence donnée en début de tour) ;
  `target_period_type` dans {`A_YEAR_0_AHEAD`, `A_YEAR_1_AHEAD`, `A_YEAR_2_AHEAD`} (moyenne annuelle de l'année du tour, de
  l'année suivante, de la deuxième année suivante, selon le README) ; `ref_round` de `2001Q4` à `2025Q4`. Le tour 2001T4 ne
  sert qu'à fournir les prévisions précédentes du tour 2002T1.
- Constaté par le rédacteur (comptages, sans valeur) :
  - 31 983 lignes `Point` ; aucun doublon (tour, identifiant, type, cible) ;
  - année cible − année du tour = 0, 1, 2 pour 100 % des lignes des trois types ;
  - tous les identifiants numériques ont trois chiffres ;
  - `A_YEAR_2_AHEAD` existe à **tous** les tours T4 de 2000 à 2026 ; cela fournit la prévision précédente des révisions des
    tours T1 ;
  - aucune valeur non numérique ;
  - dans la fenêtre 2001T4-2025T4 : 14 255 lignes (5 457 année en cours, 5 346 année suivante, 3 452 deuxième année),
    97 tours, 106 identifiants, aucune valeur hors de [−5 ; 15].
- `0_Round_dates.csv` (sha256 `c960dcc2…`) : les tours partent en janvier-février (T1), mars-avril (T2), juin-juillet (T3) et
  septembre-octobre (T4).

**Source 2 — projections annuelles des services de la BCE (MPD).** Une série par exercice :

```
https://data-api.ecb.europa.eu/service/data/MPD/A.U2.HIC.A.<MILLÉSIME>.0000?format=csvdata
```

- **Liste figée des 97 millésimes** : `A01`, puis `W`, `G`, `S`, `A` pour chaque année de 2002 à 2025 (`W02` … `A25`).
- Correspondance vérifiée dans H03-v2 et ici : `W` = mars (trimestre 1), `G` = juin (2), `S` = septembre (3), `A` =
  décembre (4).
- Colonnes utilisées : `KEY`, `TIME_PERIOD` (année), `OBS_VALUE`, `OBS_STATUS`, `TITLE_COMPL`. La colonne `TITLE` est vide.
- Constaté par le rédacteur sur les **97** séries (HTTP 200 pour toutes) :
  - le mois et l'année écrits dans `TITLE_COMPL` (dernier nom de mois anglais, dernière année à quatre chiffres) concordent
    avec la lettre et l'année du code, pour les 97 ;
  - la première année de statut `F` est l'année de l'exercice, pour les 97 ;
  - les années Y, Y + 1 et Y + 2 (Y = année de l'exercice) existent toutes avec le statut `F` : 291 lignes ;
  - les valeurs ont 0 ou 1 décimale ; aucune n'est hors de [−5 ; 15].
- **Calendrier.** L'exercice `W` de l'année Y reçoit le même numéro de tour que le tour T1 de l'enquête, et ainsi de suite.
  L'exercice de la BCE est arrêté environ deux mois après le tour d'enquête de même numéro : son information est plus
  récente (note de nouveauté, correction 7). La comparaison porte sur les mêmes années cibles et le même nombre de tours
  restants, pas sur le même jour.

**Source 3 — inflation réalisée : Eurostat, `prc_hicp_ainr`** (IPCH, ECOICOP v2), taux de variation de la moyenne
annuelle, zone euro à composition évolutive.

```
https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV
```

- Testé le 2026-11-12 : HTTP 200 ; colonnes `DATAFLOW, LAST UPDATE, freq, unit, coicop18, geo, TIME_PERIOD, OBS_VALUE,
  OBS_FLAG, CONF_STATUS` ; 29 années, 1997 à 2025, aucune vide, aucun drapeau, une décimale ; mise à jour `17/09/26` ;
  sha256 du fichier reçu `43ef7b6b85ff0268d912b1e7d405a8790f7ad049aea427387a53f2781ad0505e`.
- C'est le concept de l'enquête : « moyenne annuelle de l'année civile » (README de l'enquête).
- Si le fichier reçu a une autre date de mise à jour ou un autre sha256, on l'utilise et on l'écrit dans `ecarts.md`.

**Coût.** Une archive de 12 Mo, 97 requêtes à l'API de la BCE (de 10 à 15 s chacune, avec des délais dépassés possibles), une
requête Eurostat. Les calculs prennent quelques secondes : quelques minutes sur un portable en tout.

---

## 6. Fichier d'analyse

**Nom** : `tests-de-mort/K01/K01_analyse.csv`. UTF-8, séparateur virgule, point décimal, première ligne = noms de colonnes,
cellule vide = manquant. **Une ligne par source × prévisionniste × tour × année cible.** `id_prev` est du texte (les zéros en
tête comptent : lire avec `dtype=str`). Tri : `source`, `id_prev`, `t_tour`, `annee_cible`.

**Lignes.**
- **SPF** : chaque ligne retenue de la source 1 (section 5). 14 255 lignes attendues.
- **BCE** : pour chacun des 97 millésimes, les années Y, Y + 1 et Y + 2 de statut `F`. 291 lignes attendues.

Si les nombres de lignes diffèrent (archive mise à jour), on continue et on l'écrit dans `ecarts.md`.

**Colonnes** (22, dans cet ordre, sans aucune autre).

| Colonne | Type | Contenu |
|---|---|---|
| `source` | texte | `SPF` ou `BCE` |
| `id_prev` | texte | SPF : `forecaster_id` tel quel (trois chiffres) ; BCE : `BCE` |
| `tour` | texte | forme `2021Q3` ; SPF : `ref_round` ; BCE : année du millésime + trimestre de la lettre |
| `t_tour` | entier | 4 × année + trimestre − 1 (2001Q4 → 8007 ; 2002Q1 → 8008 ; 2025Q4 → 8103) |
| `millesime` | texte | BCE : code (`W21`…) ; SPF : vide |
| `statut` | texte | BCE : `OBS_STATUS` de la ligne lue ; SPF : vide |
| `mois_titre` | entier | BCE : mois du dernier nom de mois anglais complet de `TITLE_COMPL` (1 à 12) ; SPF : vide |
| `annee_titre` | entier | BCE : dernière année à quatre chiffres de `TITLE_COMPL` ; SPF : vide |
| `annee_cible` | entier | année civile prévue |
| `horizon` | entier | `annee_cible` − année du tour : 0, 1 ou 2 |
| `rang` | entier | `t_tour` − 4 × (`annee_cible` − 1) + 1 : de 1 (T1 de l'année précédente) à 8 (T4 de l'année cible) ; de −3 à 0 pour l'horizon 2 |
| `prevision` | décimal | prévision, en %, telle que publiée |
| `prevision_prec` | décimal | `prevision` de la ligne (même `source`, même `id_prev`, `t_tour` − 1, même `annee_cible`) ; vide si elle n'existe pas ou si `t_tour` = 8007 |
| `revision` | décimal | `prevision` − `prevision_prec`, en points ; vide si l'une est vide |
| `autre_cible` | entier | `annee_cible` + 1 si `horizon` = 0 ; `annee_cible` − 1 si `horizon` = 1 ; vide si `horizon` = 2 |
| `prevision_autre` | décimal | `prevision` de la ligne (même source, même identifiant, même `t_tour`, `annee_cible` = `autre_cible`) ; vide sinon |
| `prevision_autre_prec` | décimal | `prevision` de la ligne (même source, même identifiant, `t_tour` − 1, `annee_cible` = `autre_cible`) ; vide si elle n'existe pas ou si `t_tour` = 8007 |
| `instrument` | décimal | `prevision_autre` − `prevision_autre_prec`, en points ; vide si l'une est vide |
| `realise` | décimal | `OBS_VALUE` d'Eurostat pour `annee_cible` si `annee_cible` ≤ 2025 ; vide sinon |
| `erreur` | décimal | `realise` − `prevision`, en points ; vide si l'une est vide |
| `nb_tours_complets` | entier | SPF : nombre de valeurs distinctes de `t_tour` dans [8008 ; 8103] où cet identifiant a au moins une ligne d'`horizon` 0 ou 1 avec `revision`, `instrument` et `erreur` non vides (même valeur sur toutes ses lignes) ; BCE : vide |
| `echantillon_iv` | entier | 1 si `source` = `SPF`, `horizon` ∈ {0, 1}, 8008 ≤ `t_tour` ≤ 8103, `revision`, `instrument` et `erreur` non vides, et `nb_tours_complets` ≥ 8 ; 0 sinon |

Les différences sont écrites avec au moins 6 décimales, sans arrondi.

**Comptes attendus** (comptages de présence faits par le rédacteur, sans valeur) :
- lignes SPF d'horizon 0 ou 1, tours 2002T1-2025T4, cible ≤ 2025 : 10 474 ;
- dont avec révision : 8 873 ;
- dont avec révision et instrument : 8 663, pour 105 identifiants ;
- **échantillon principal (`echantillon_iv` = 1) : 8 595 lignes, 94 prévisionnistes, 96 tours, 24 années cibles (2002-2025)** ;
  4 393 d'horizon 0 et 4 202 d'horizon 1 ; de 47 à 108 lignes par tour (médiane 92) ;
- hors années cibles 2021-2023 : 7 425 lignes sur 88 tours ;
- années cibles 2002-2019 : 6 269 lignes ;
- cellules agrégées (tour × année cible) : 188 pour le consensus et 188 pour la BCE (96 d'horizon 0 et 92 d'horizon 1).

**Contrôles de schéma.** Le vérificateur les refait sur le fichier. `n_violations_schema` = nombre de contrôles violés (0
attendu, 12 au plus). Un contrôle est violé s'il échoue sur une seule ligne. La colonne de droite dit ce que le rédacteur a
vérifié sur les lignes réelles (présences et formats, sans valeur de résultat).

| N° | Contrôle | Vérifié sur les données réelles |
|---|---|---|
| 1 | **Colonnes** : les 22 noms ci-dessus, dans cet ordre, sans autre colonne | sans objet (fichier à construire) |
| 2 | **Clé** : (`source`, `id_prev`, `t_tour`, `annee_cible`) unique ; `source` ∈ {`SPF`, `BCE`} ; `id_prev` = trois chiffres si SPF, `BCE` si BCE | oui : 0 doublon dans `1_HICP.csv` ; tous les identifiants numériques ont trois chiffres |
| 3 | **Tours** : `tour` de forme `AAAAQn` ; `t_tour` = 4 × AAAA + n − 1 ; 8007 ≤ `t_tour` ≤ 8103 ; les lignes SPF prennent les 97 valeurs de 8007 à 8103, les lignes BCE aussi | oui : 97 tours SPF de 2001Q4 à 2025Q4, tous au bon format ; 97 millésimes BCE |
| 4 | **Cibles** : `horizon` = `annee_cible` − AAAA ∈ {0, 1, 2} ; `rang` suit sa formule | oui : décalage 0, 1, 2 pour 100 % des lignes des trois types |
| 5 | **Millésimes BCE** : sur les lignes BCE, `millesime`, `statut`, `mois_titre`, `annee_titre` non vides ; la lettre donne le trimestre de `tour` (`W` 1, `G` 2, `S` 3, `A` 4) et les deux chiffres son année ; `mois_titre` = 3 × trimestre ; `annee_titre` = année ; les 97 codes de la liste figée, 3 lignes chacun. Sur les lignes SPF, ces quatre colonnes sont vides | oui : les 97 séries, titre, lettre et année concordants ; 3 années de statut `F` chacune |
| 6 | **Statut** : `statut` = `F` sur toutes les lignes BCE | oui : 291 sur 291 |
| 7 | **Valeurs** : `prevision` non vide, entre −5 et 15 ; `realise` vide si et seulement si `annee_cible` > 2025, sinon entre −5 et 15 avec une décimale au plus | oui : 0 valeur hors de [−5 ; 15] parmi les 14 255 prévisions SPF et les 291 BCE ; Eurostat : 1997-2025, une décimale, 0 hors bornes |
| 8 | **Prévision précédente** : pour `t_tour` ≥ 8008, `prevision_prec` égale la `prevision` de la ligne (même source, même identifiant, `t_tour` − 1, même `annee_cible`) quand elle existe, et est vide sinon ; vide quand `t_tour` = 8007 | présence : 8 873 révisions possibles dans la fenêtre |
| 9 | **Autre cible** : `autre_cible` suit sa définition ; `prevision_autre` et `prevision_autre_prec` égalent les `prevision` des lignes désignées quand elles existent, et sont vides sinon (et vides quand `horizon` = 2) | présence : 8 663 lignes avec révision et instrument ; `A_YEAR_2_AHEAD` présent à tous les tours T4 |
| 10 | **Calculs** : `revision`, `instrument`, `erreur` égalent leur différence à 10⁻⁹ près, et sont vides si et seulement si un terme est vide | sans objet (calcul) |
| 11 | **Réalisé** : `realise` prend une seule valeur par `annee_cible` sur toutes les lignes | oui : une ligne par année chez Eurostat |
| 12 | **Échantillon** : `nb_tours_complets` et `echantillon_iv` suivent leurs définitions | présence : 8 595 lignes, 94 identifiants, 96 tours |

---

## 7. Statistique

Tout se calcule à partir du seul fichier d'analyse, en double précision, sans arrondi intermédiaire.

**Notations.** Échantillon E : lignes avec `echantillon_iv` = 1. e = `erreur`, x = `revision`, z = `instrument`. Groupe
d'horizon : `horizon` (0 ou 1). n = nombre de lignes de E (`n_obs_iv`) ; `n_previsionnistes_iv` = nombre d'identifiants
distincts ; `n_tours_iv` = nombre de `t_tour` distincts.

**Variance de long terme à 8 retards**, LRV₈(S), d'une série S_t indexée par `t_tour` :
LRV₈ = Σ_t S_t² + 2 × Σ_{j=1..8} (1 − j/9) × Σ_t S_t S_{t−j}. La dernière somme porte sur les couples de tours présents dont
les numéros diffèrent de j. Un tour absent ne crée aucun couple. Aucune correction de petit échantillon.

**Statistique principale : b_IV, deux moindres carrés, un instrument.**
1. Retirer à e, x et z leur moyenne **dans leur groupe d'horizon**, sur E : ẽ, x̃, z̃. C'est l'effet d'une constante par
   horizon (théorème de Frisch-Waugh-Lovell).
2. **b_IV** = Σ z̃ ẽ / Σ z̃ x̃ (`b_iv`).
3. Résidus u = ẽ − b_IV x̃ ; pour chaque tour t, S_t = Σ (sur les lignes du tour t) z̃ u.
4. `et_b_iv_dk8` = racine(LRV₈(S)) / |Σ z̃ x̃|. `t_iv` = b_IV / `et_b_iv_dk8`.
5. `borne_basse_ic90` = b_IV − 1,714 × et ; `borne_haute_ic90` = b_IV + 1,714 × et.
6. **Première étape** : π = Σ z̃ x̃ / Σ z̃² (`coef_premiere_etape`) ; v = x̃ − π z̃ ; S^fs_t = Σ z̃ v par tour ;
   et_π = racine(LRV₈(S^fs)) / Σ z̃² ; **`f_premiere_etape`** = (π / et_π)².
7. **Forme réduite** (test de b = 0 robuste à un instrument faible : avec un seul instrument, c'est le test
   d'Anderson-Rubin) : ρ = Σ z̃ ẽ / Σ z̃² ; w = ẽ − ρ z̃ ; et_ρ = racine(LRV₈(Σ par tour de z̃ w)) / Σ z̃² ;
   `t_forme_reduite` = ρ / et_ρ.
8. Écarts-types descriptifs : `et_b_iv_grappes_tour` = racine(Σ_t S_t²) / |Σ z̃ x̃| (96 groupes) ;
   `et_b_iv_grappes_cible` = racine(Σ_g S_g²) / |Σ z̃ x̃|, où S_g = Σ z̃ u sur les lignes d'`annee_cible` g (24 groupes).

**Garde et clause de l'épisode 2021-2023.** E' = E sans les lignes d'`annee_cible` 2021, 2022 ou 2023. Étapes 1 à 6 refaites
sur E' (moyennes retirées dans E') : `n_obs_iv_hors_2021_2023`, `b_iv_hors_2021_2023`, `et_b_iv_hors_2021_2023_dk8`,
`borne_haute_ic90_hors_2021_2023` = b + 1,714 × et, `f_premiere_etape_hors_2021_2023`.

**Champs dérivés pour la règle.**
- `marge_indecision` = le plus petit des deux nombres (−0,15 − `borne_basse_ic90`) et (`borne_haute_ic90`). Il est positif
  ou nul exactement quand l'intervalle à 90 % contient à la fois 0 et −0,15.
- `conflit_episode` = 1 si `borne_haute_ic90` ≥ 0 et `borne_haute_ic90_hors_2021_2023` < 0 ; 0 sinon.

**Descriptifs, hors verdict.**
- `b_iv_max_sans_une_annee` : la plus grande (la moins négative) des 24 valeurs de b_IV obtenues en retirant une seule année
  cible de 2002 à 2025 (étapes 1 et 2 refaites).
- **Effets fixes de prévisionniste** : on remplace l'étape 1 par les résidus de la régression MCO de e, x et z sur des
  indicatrices d'identifiant et l'indicatrice `horizon` = 1. Étapes 2 à 4 : `b_iv_ef_prev`, `et_b_iv_ef_prev_dk8`.
- **MCO naïf regroupé** : b = Σ x̃ ẽ / Σ x̃² (`b_mco_naif`) ; S_t = Σ x̃ (ẽ − b x̃) ; `et_b_mco_naif_dk8`.
- **Pente naïve intra-tour** (la statistique de la fiche, sans effets fixes de prévisionniste) : on retire à e et à x leur
  moyenne dans la cellule (`t_tour`, `annee_cible`) sur E, ce qui donne ë et ẍ ; b = Σ ẍ ë / Σ ẍ² (`b_intra_tour_naif`) ;
  û = ë − b ẍ ; `et_b_intra_tour_naif_grappes_tour` = racine(Σ_t (Σ ẍ û)²) / Σ ẍ² (96 groupes).
- **Bornes de bruit** (Juodis et Kučinskas, φ = 0) :
  - `sigma_bruit_necessaire_mco` = racine(max(0, −`b_mco_naif`) × Σ x̃²/n) : écart-type d'un bruit blanc qui suffirait à
    produire à lui seul la pente MCO ;
  - `sigma_bruit_commun_necessaire_iv` = racine(max(0, −b_IV) × max(0, Σ z̃ x̃/n)) : écart-type d'un bruit **commun aux deux
    années** (ρ = 1) qui suffirait à produire à lui seul b_IV.
  - Repère : un arrondi au dixième donne un bruit d'écart-type 0,1/√12 ≈ 0,029 point.
- **Avant 2020** (comparaison avec Broer et Kohlhas) : E restreint aux années cibles ≤ 2019 : `n_obs_avant_2020`,
  `b_iv_avant_2020`, `et_b_iv_avant_2020_dk8` (étapes 1 à 4) ; `b_mco_ef_avant_2020` et `et_b_mco_ef_avant_2020_dk8` (MCO avec
  indicatrices d'identifiant et d'horizon, comme Broer et Kohlhas).
- **Consensus et BCE.** Cellules (t, y) : 8008 ≤ t ≤ 8103, y = année du tour ou l'année suivante, y ≤ 2025.
  - Consensus C(t, y) = moyenne de `prevision` sur **toutes** les lignes SPF du tour t et de l'année y (tous les
    répondants, sans le filtre des 8 tours). Révision x_c = C(t, y) − C(t − 1, y) ; erreur e_c = `realise`(y) − C(t, y).
  - BCE : lignes `source` = `BCE` de ces cellules, x = `revision`, e = `erreur`.
  - Pour chaque source : moyennes retirées dans le groupe d'horizon ; b = Σ x̃ ẽ / Σ x̃² ; S_t = Σ x̃ (ẽ − b x̃) ;
    et = racine(LRV₈(S)) / Σ x̃². Champs : `n_consensus`, `b_consensus`, `et_b_consensus_dk8`, `n_bce`, `b_bce`,
    `et_b_bce_dk8`.
  - Écart : `diff_bce_moins_consensus` = `b_bce` − `b_consensus` ; ψ_t = S^BCE_t / D_BCE − S^cons_t / D_cons, où D = Σ x̃² de
    chaque source ; `et_diff_dk8` = racine(LRV₈(ψ)).
  - `b_consensus_hors_2021_2023` et `b_bce_hors_2021_2023` : mêmes pentes sans les années cibles 2021-2023.

**Convention.** Si un échantillon a moins de 100 lignes (individus) ou moins de 20 cellules (agrégés), ou si un dénominateur
est nul, ses champs valent 0. Le verdict est alors « non concluant » par les conditions de taille ou de première étape.

**Fichiers.** L'expérimentateur écrit `temoin.json`, le vérificateur `verification.json`. Les deux contiennent tous les
champs de la règle (section 11), en nombres. Ni l'un ni l'autre n'écrit de verdict.

---

## 8. Arithmétique de puissance

Calculs sans donnée, en loi normale, l'écart-type étant traité comme connu.

**Écart-type attendu de b_IV.**
- Broer et Kohlhas obtiennent 0,18 par MCO sur environ 80 tours.
- Sans effets fixes de temps, la précision vient surtout de la part **commune** des erreurs et des révisions, c'est-à-dire
  d'environ 24 années cibles. Les 8 595 lignes n'y changent presque rien.
- Calcul d'ordre de grandeur, avec des hypothèses non mesurées :
  - révisions du consensus d'écart-type 0,2 point ;
  - révisions individuelles autour du consensus d'écart-type 0,25 ;
  - corrélation entre les révisions des deux années de 0,6 pour la part commune et de 0,5 pour la part individuelle ;
  - erreur du consensus d'écart-type 0,6.
  On obtient un écart-type MCO de l'ordre de 0,15. L'instrument le multiplie par environ 1/corrélation(x, z), soit 1,5 à 2.
- 2021-2023 agrandit à la fois les révisions (ce qui aide) et les erreurs (ce qui nuit).
- Trois scénarios : **optimiste 0,15 ; central 0,25 ; pessimiste 0,40.**

**Ce que la règle demande** (section 9 ; c = 1,714 ; δ = 0,15) :
- survie si b̂ < −c × et ;
- élimination si b̂ > c × et − 0,15 ;
- entre les deux : non concluant.

| et | survit si b̂ < | éliminée si b̂ > | effet détecté 8 fois sur 10 |
|---|---|---|---|
| 0,15 | −0,26 | +0,11 | −0,38 |
| 0,25 | −0,43 | +0,28 | −0,64 |
| 0,40 | −0,69 | +0,54 | −1,02 |

**Probabilités des trois issues** (survit / éliminée / non concluant), avant la garde de signe et la clause de l'épisode :

| Vraie pente b | et = 0,15 | et = 0,25 (central) | et = 0,40 |
|---|---|---|---|
| −0,40 | 83 / 0 / 17 % | 45 / 0 / 54 % | 24 / 1 / 75 % |
| −0,30 (θ = 0,5) | 61 / 0 / 38 % | 30 / 1 / 69 % | 17 / 2 / 81 % |
| **−0,15 (prédiction)** | 24 / 4 / 72 % | **13 / 4 / 82 %** | 9 / 4 / 87 % |
| 0 (H0a, H0b) | 4 / 24 / 72 % | 4 / 13 / 82 % | 4 / 9 / 87 % |
| +0,15 | 0 / 61 / 38 % | 1 / 30 / 69 % | 2 / 17 / 81 % |
| +0,30 (H2, ou part commune de 2021-2022) | 0 / 90 / 10 % | 0 / 53 / 46 % | 1 / 28 / 72 % |

**Lecture honnête.**
- **Ce test est peu puissant.** Dans le scénario central, la pente prédite (−0,15) ne survit qu'une fois sur huit. L'issue
  la plus probable, sous H1 comme sous H0, est « non concluant ».
- Le test ne tranche que si la vraie pente est loin de zéro : une sur-réaction forte (−0,4 et au-delà), ou une sous-réaction
  individuelle (+0,3 et au-delà).
- Le prix est assumé. La statistique de la fiche avait, selon la fiche, un écart-type de 0,03 à 0,05, mais elle mesure la
  dispersion et non la justesse (section 2). Une statistique précise et biaisée par construction ne vaut pas mieux qu'une
  statistique juste et imprécise.
- Sans zone d'indécision (règle de la fiche : éliminée dès que la borne haute est ≥ 0), la pente prédite serait éliminée
  83 % du temps dans le scénario central : « éliminée » ne voudrait plus rien dire. D'où A9.
- **Instrument.** On s'attend à une première étape très forte : les révisions des deux années bougent ensemble, avec des
  milliers de lignes et 96 tours. Cette attente n'est pas mesurée. Le seuil de 23,1 ne devrait mordre que si les deux années
  sont révisées indépendamment.
- Les probabilités de survie du tableau sont des **plafonds** : la garde de signe hors 2021-2023 peut transformer une survie
  en élimination.
- Une erreur de première espèce de 5 % suppose que l'écart-type de Driscoll-Kraay est juste. Avec 24 années cibles et des
  poids de Bartlett, il est souvent un peu trop petit (limite 5). La valeur critique 1,714 au lieu de 1,645 en corrige une
  partie.

**Consensus et BCE (descriptifs).**
- 188 cellules chacun, mais environ 24 années cibles indépendantes. Écart-type attendu de chaque pente : 0,25 à 0,40
  (Broer et Kohlhas : 0,41 pour le consensus ; J02 : 0,30 pour la pente brute de la BCE sur des cibles trimestrielles).
- Si la vraie pente est +0,4, la probabilité d'une borne basse positive va de 24 % (et = 0,40) à 45 % (et = 0,25).
- Pour l'écart BCE − consensus, les deux pentes partagent les mêmes chocs : écart-type attendu 0,20 à 0,35. **Effet
  minimal détectable 8 fois sur 10 : 0,5 à 0,9**, plus grand que les pentes elles-mêmes.
- **Ce qu'on peut conclure** : le signe de chaque pente agrégée, avec son intervalle, et si elle dépend de 2021-2023
  (champs `_hors_2021_2023`).
- **Ce qu'on ne peut pas conclure** :
  - que la BCE « se comporte comme le consensus » (un écart non significatif n'est pas une égalité) ;
  - que la BCE « se comporte comme un comité » plutôt que comme un prévisionniste ;
  - qu'elle diffère du consensus, sauf écart supérieur à environ 0,6.
  C'est pourquoi ces pentes restent hors du verdict.

**Minimum d'échantillon.** 8 595 lignes, 94 prévisionnistes et 96 tours sont attendus. On déclare non concluant :
- sous **8 000 lignes** (−7 %) ou sous **80 prévisionnistes** : cela signalerait un problème de construction ;
- sous **94 tours** : plus de deux tours manquants voudraient dire qu'un tour entier de l'archive n'a pas été lu.

---

## 9. Règle de verdict

Le verdict est calculé par `verdict.py` à partir des chiffres du vérificateur. « Survit » veut dire : sur les années cibles
2002-2025, les erreurs des prévisionnistes individuels de l'enquête de la BCE vont significativement dans le sens inverse de
leurs révisions (sur-réaction). Cela est établi par une pente purgée du bruit propre à chaque chiffre, et ne tient pas à
2021-2023.

**Non concluant** si l'une de ces conditions est vraie :
1. `n_violations_schema` > 0 : fichier hors schéma ; on ne juge pas une idée sur un fichier douteux.
2. `n_obs_iv` < 8 000, `n_previsionnistes_iv` < 80, ou `n_tours_iv` < 94 : voir « Minimum d'échantillon » (section 8).
3. `f_premiere_etape` < 23,1 : instrument faible. C'est le seuil de Montiel Olea et Pflueger (2013) pour un instrument avec
   des erreurs groupées : au-delà, le biais de l'estimateur reste sous 10 % d'une référence défavorable, au niveau 5 %.
   Sous ce seuil, l'intervalle de b_IV n'est pas fiable.
4. `f_premiere_etape_hors_2021_2023` < 10 : la garde de signe porte sur une pente sans instrument utilisable. Le seuil usuel
   de Staiger et Stock suffit, car on ne demande qu'un signe.
5. `marge_indecision` ≥ 0 : l'intervalle à 90 % contient à la fois 0 (pas de sur-réaction) et −0,15 (la prédiction) ; les
   données ne choisissent pas.
6. `conflit_episode` ≥ 1 : la sur-réaction n'est pas établie sur 2002-2025, mais elle l'est sans les années cibles
   2021-2023. Le jugement dépendrait alors de la manière de compter un seul épisode exceptionnel. La fiche ne prévoyait pas ce
   cas ; l'éliminer sur la seule foi de 2021-2023 serait juger l'idée sur l'épisode.
7. Écart entre expérimentateur et vérificateur au-delà de la tolérance sur un champ, ou champ absent (protocole).

**Survit** si aucune condition ci-dessus n'est vraie et si les deux suivantes le sont :
- `borne_haute_ic90` < 0. Seuil 0 : pente nulle = pas de sur-réaction (H0a, H0b). C'est un test unilatéral à 5 % de b < 0,
  la condition de survie de la fiche (« meurt si la borne supérieure de l'IC à 90 % est ≥ 0 »), appliquée à la statistique
  purgée.
- `b_iv_hors_2021_2023` < 0. Seuil 0 : on demande un signe, pas un test (21 années cibles ne donnent pas la puissance d'un
  second test). Un signe nul ou positif voudrait dire que la poussée de 2021-2023 porte seule la sur-réaction. C'est la
  seconde condition de mort de la fiche, appliquée à la période hors épisode.

**Éliminée** dans tous les autres cas. Compte tenu des conditions de non-conclusion, cela arrive exactement dans deux cas :
- (a) `borne_haute_ic90` ≥ 0 et `borne_basse_ic90` > −0,15 : les données excluent, au seuil unilatéral de 5 %, une
  sur-réaction de la taille prédite. Si en plus `borne_basse_ic90` > 0, les individus **sous-réagissent** (H2).
- (b) `borne_haute_ic90` < 0 mais `b_iv_hors_2021_2023` ≥ 0 : la sur-réaction ne tient qu'à 2021-2023.

**Pourquoi −0,15 comme borne de la zone d'indécision.** C'est le centre de la prédiction de la fiche, et l'ordre de grandeur
de Broer et Kohlhas (−0,169) et de Bordalo et coauteurs pour l'inflation (−0,07 à −0,16). Éliminer demande d'exclure la
sur-réaction **telle qu'elle a été chiffrée**, pas n'importe quelle sur-réaction minuscule.

**Tolérances** (écart maximal entre expérimentateur et vérificateur, qui calculent sur le même fichier) :
- 0 sur les champs entiers et les indicatrices ;
- 0,005 sur les pentes, les écarts-types et les bornes de bruit ;
- 0,01 sur les bornes d'intervalle et la marge ;
- 0,02 sur les t ;
- 1 sur les F (un F de plusieurs centaines varie de plus d'une unité pour une différence de 0,005 sur t).

---

## 10. Limites

1. **Le bruit commun aux deux années n'est pas traité.** Si un prévisionniste déplace, à un tour donné, ses deux chiffres
   annuels dans le même sens pour une raison étrangère à ses croyances, l'instrument porte ce bruit. b_IV est alors encore
   biaisé vers le négatif, de −ρσ²(1 − φ)/Cov(x, z). C'est le cas, par exemple, des incitations stratégiques à se
   distinguer, que Gemmi et Valchev (2026) jugent propres aux enquêtes. Une survie se lira donc comme « les **chiffres
   rapportés** sur-réagissent », jamais comme « les croyances sur-réagissent ». `sigma_bruit_commun_necessaire_iv` dit quelle
   taille ce bruit commun devrait avoir pour tout expliquer.
2. **La puissance est faible** (section 8). Le verdict le plus probable est « non concluant », même si la prédiction est
   vraie.
3. **On ne sépare plus nouvelles communes et nouvelles individuelles.** La pente regroupée répond à : « le prévisionniste
   sur-réagit-il, en moyenne, à ses révisions ? » (au sens de Bordalo et coauteurs). Elle ne dit pas s'il sur-réagit à
   l'information qui lui est propre plutôt qu'à l'information publique. C'était la question de la pente intra-tour, mais
   celle-ci ne peut pas y répondre (section 2).
4. **Un épisode pèse lourd.** Sans effets fixes de temps, 2021-2022 (grandes révisions, grandes erreurs communes) domine la
   régression. La garde de signe et la clause de conflit encadrent ce poids sans le supprimer. `b_iv_max_sans_une_annee`
   montrera si une seule année porte le résultat.
5. **Écart-type de Driscoll-Kraay en petit échantillon.** Avec environ 24 années cibles indépendantes, il est souvent trop
   petit, ce qui rend la survie un peu trop facile. L'écart-type groupé par année cible (24 groupes) est rapporté à côté.
6. **Réalisé du dernier millésime**, en ECOICOP v2, arrondi au dixième, et non le chiffre que les prévisionnistes voyaient à
   l'époque. Cela décale de la même quantité toutes les erreurs d'une année cible ; l'effet sur la pente est faible mais pas
   nul.
7. **Prévisions arrondies et révisions nulles.** Beaucoup de révisions valent 0 ou ±0,1. L'arrondi propre à chaque chiffre
   est traité par l'instrument, mais il réduit la variation utile.
8. **Composition du panel.** Le consensus est la moyenne de tous les répondants du tour ; sa révision mêle de vrais
   changements d'avis et des entrées-sorties du panel. Les identifiants sont supposés stables (documentation de la BCE).
9. **Calendrier BCE contre enquête.** À tour égal, l'exercice de la BCE a environ deux mois d'information de plus. La
   comparaison BCE-consensus est donc à la fois peu puissante et un peu déséquilibrée en faveur de la BCE.
10. **Le plan n'est pas aveugle.** Il est écrit en 2026 par quelqu'un qui connaît la poussée de 2021-2023, les chiffres de
    Broer et Kohlhas et le verdict de J02 (sous-réaction des projections trimestrielles de la BCE, 0,44, portée par
    2021-2022). Deux valeurs du tour 1999T1 ont été vues par incident. Les choix principaux suivent la fiche, les juges et la
    note de nouveauté, mais on ne peut pas le prouver.
11. **Seuil de 8 tours** par prévisionniste : c'est celui de la fiche. Il retire 11 identifiants et 68 lignes (comptage de
    présence) ; un autre seuil aurait été défendable.

---

## 11. Ce qu'on écrira dans chaque cas

Dans tous les cas, on publie aussi, comme descriptifs : la pente MCO naïve, la pente naïve intra-tour (avec la phrase « elle
mesure l'évolution de la dispersion des prévisions, pas leur justesse »), les deux bornes de bruit, la pente avec effets
fixes avant 2020 à côté du −0,169 (0,182) de Broer et Kohlhas, et les pentes du consensus et de la BCE avec leur écart.

- **Survit** : « Sur les années cibles 2002-2025 de l'enquête de la BCE (8 595 révisions, 94 prévisionnistes), les erreurs
  individuelles vont dans le sens inverse des révisions, même quand la révision est instrumentée par la révision de l'autre
  année au même tour, ce qui retire le bruit propre à chaque chiffre : pente b_IV avec son intervalle à 90 %, négative aussi
  sans 2021-2023. Les chiffres rapportés sur-réagissent ; un bruit commun aux deux années d'au moins σ (borne rapportée)
  serait nécessaire pour l'expliquer autrement. »
- **Éliminée, pas de sur-réaction de la taille prédite** (cas a, borne basse entre −0,15 et 0) : « La pente purgée du bruit
  n'est pas distinguable de zéro et les données excluent, au seuil de 5 %, une sur-réaction de −0,15 ; la pente intra-tour
  négative n'était qu'un effet de dispersion et de bruit. »
- **Éliminée, sous-réaction individuelle** (cas a, borne basse > 0) : « Les prévisionnistes pris un à un sous-réagissent eux
  aussi : la sous-réaction du consensus et de la BCE n'est pas un simple effet d'agrégation. C'est un résultat contraire au
  schéma américain de Bordalo et coauteurs, à nuancer par le poids de 2021-2022 (pente hors 2021-2023 rapportée). »
- **Éliminée, sur-réaction portée par 2021-2023** (cas b) : « La pente est significativement négative sur 2002-2025 mais
  pas hors des années cibles 2021-2023 ; elle ne décrit pas un comportement ordinaire. »
- **Non concluant, par indécision** (`marge_indecision` ≥ 0, l'issue la plus probable) : « Avec une pente purgée du bruit,
  l'intervalle à 90 % contient à la fois 0 et −0,15 : sur 24 années cibles, l'enquête de la BCE ne permet pas de dire si les
  prévisionnistes sur-réagissent. La pente intra-tour, très précise, ne le permet pas non plus : elle est négative par
  construction. »
- **Non concluant, par conflit** (`conflit_episode` = 1) : « La sur-réaction est établie hors 2021-2023, mais pas sur toute
  la période ; la conclusion dépend d'un seul épisode, on ne conclut pas. »
- **Non concluant, par instrument faible** : « Les révisions des deux années ne bougent pas assez ensemble pour servir
  d'instrument ; la méthode préinscrite ne s'applique pas. »
- **Non concluant, par les données** (schéma, taille, fichier manquant, écart entre expérimentateur et vérificateur) : « Le
  test n'a pas pu être mené comme préinscrit ; la raison exacte est dans `ecarts.md` et aucune conclusion n'est tirée sur
  l'hypothèse. »

---

## 12. Règle lisible par machine

```json
{
  "id": "K01",
  "fichier_analyse": "K01_analyse.csv",
  "champs_verification": [
    "n_violations_schema",
    "n_obs_iv",
    "n_previsionnistes_iv",
    "n_tours_iv",
    "b_iv",
    "et_b_iv_dk8",
    "t_iv",
    "borne_basse_ic90",
    "borne_haute_ic90",
    "marge_indecision",
    "coef_premiere_etape",
    "f_premiere_etape",
    "t_forme_reduite",
    "et_b_iv_grappes_tour",
    "et_b_iv_grappes_cible",
    "n_obs_iv_hors_2021_2023",
    "b_iv_hors_2021_2023",
    "et_b_iv_hors_2021_2023_dk8",
    "borne_haute_ic90_hors_2021_2023",
    "f_premiere_etape_hors_2021_2023",
    "conflit_episode",
    "b_iv_max_sans_une_annee",
    "b_iv_ef_prev",
    "et_b_iv_ef_prev_dk8",
    "b_mco_naif",
    "et_b_mco_naif_dk8",
    "b_intra_tour_naif",
    "et_b_intra_tour_naif_grappes_tour",
    "sigma_bruit_necessaire_mco",
    "sigma_bruit_commun_necessaire_iv",
    "n_obs_avant_2020",
    "b_iv_avant_2020",
    "et_b_iv_avant_2020_dk8",
    "b_mco_ef_avant_2020",
    "et_b_mco_ef_avant_2020_dk8",
    "n_consensus",
    "b_consensus",
    "et_b_consensus_dk8",
    "n_bce",
    "b_bce",
    "et_b_bce_dk8",
    "diff_bce_moins_consensus",
    "et_diff_dk8",
    "b_consensus_hors_2021_2023",
    "b_bce_hors_2021_2023"
  ],
  "survit_si": [
    {"champ": "borne_haute_ic90", "operateur": "<", "seuil": 0},
    {"champ": "b_iv_hors_2021_2023", "operateur": "<", "seuil": 0}
  ],
  "non_concluant_si": [
    {"champ": "n_violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "n_obs_iv", "operateur": "<", "seuil": 8000},
    {"champ": "n_previsionnistes_iv", "operateur": "<", "seuil": 80},
    {"champ": "n_tours_iv", "operateur": "<", "seuil": 94},
    {"champ": "f_premiere_etape", "operateur": "<", "seuil": 23.1},
    {"champ": "f_premiere_etape_hors_2021_2023", "operateur": "<", "seuil": 10},
    {"champ": "marge_indecision", "operateur": ">=", "seuil": 0},
    {"champ": "conflit_episode", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "n_violations_schema": 0,
    "n_obs_iv": 0,
    "n_previsionnistes_iv": 0,
    "n_tours_iv": 0,
    "b_iv": 0.005,
    "et_b_iv_dk8": 0.005,
    "t_iv": 0.02,
    "borne_basse_ic90": 0.01,
    "borne_haute_ic90": 0.01,
    "marge_indecision": 0.01,
    "coef_premiere_etape": 0.005,
    "f_premiere_etape": 1,
    "t_forme_reduite": 0.02,
    "et_b_iv_grappes_tour": 0.005,
    "et_b_iv_grappes_cible": 0.005,
    "n_obs_iv_hors_2021_2023": 0,
    "b_iv_hors_2021_2023": 0.005,
    "et_b_iv_hors_2021_2023_dk8": 0.005,
    "borne_haute_ic90_hors_2021_2023": 0.01,
    "f_premiere_etape_hors_2021_2023": 1,
    "conflit_episode": 0,
    "b_iv_max_sans_une_annee": 0.005,
    "b_iv_ef_prev": 0.005,
    "et_b_iv_ef_prev_dk8": 0.005,
    "b_mco_naif": 0.005,
    "et_b_mco_naif_dk8": 0.005,
    "b_intra_tour_naif": 0.005,
    "et_b_intra_tour_naif_grappes_tour": 0.005,
    "sigma_bruit_necessaire_mco": 0.005,
    "sigma_bruit_commun_necessaire_iv": 0.005,
    "n_obs_avant_2020": 0,
    "b_iv_avant_2020": 0.005,
    "et_b_iv_avant_2020_dk8": 0.005,
    "b_mco_ef_avant_2020": 0.005,
    "et_b_mco_ef_avant_2020_dk8": 0.005,
    "n_consensus": 0,
    "b_consensus": 0.005,
    "et_b_consensus_dk8": 0.005,
    "n_bce": 0,
    "b_bce": 0.005,
    "et_b_bce_dk8": 0.005,
    "diff_bce_moins_consensus": 0.005,
    "et_diff_dk8": 0.005,
    "b_consensus_hors_2021_2023": 0.005,
    "b_bce_hors_2021_2023": 0.005
  }
}
```
