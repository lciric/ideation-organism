# H03-v2 — Préinscription du test de mort : les erreurs de projection d'inflation de la BCE étaient-elles prévisibles en temps réel ?

## Amendement v2

Rédigé le 2026-11-12 par le rédacteur de préinscription de l'amendement, qui n'a pris aucune part à la course annulée. Ce texte
remplace la préinscription H03 (sha256 `ea611aca877077d8b5014037d777c31041f8bbf131ced534c7f622e9de9633b7`), dont la course a
été annulée par l'orchestrateur (`tests-de-mort/H03/annulation.md`). Il reprend la v1 mot pour mot, sauf les douze passages
listés ici et deux sections ajoutées : celle-ci, et « Autres erreurs constatées, non corrigées » à la fin. Le rédacteur de la
v2 n'a lancé aucune analyse : aucune erreur, révision, moyenne ou statistique n'a été calculée sur les données.

**L'erreur corrigée.** La v1 associait la lettre `S` à l'exercice de juin et la lettre `G` à celui de septembre. Dans la
source, c'est l'inverse. Et le contrôle de schéma n° 4, qui devait comparer le mois du titre à la lettre, lisait la colonne
`TITLE`, vide dans la source : il ne portait sur aucune ligne. Le titre est dans la colonne `TITLE_COMPL`.

**Correspondance confirmée.** `W` = mars (trimestre 1), `G` = juin (trimestre 2), `S` = septembre (trimestre 3), `A` =
décembre (trimestre 4). La colonne qui porte le nom de l'exercice est `TITLE_COMPL`. Vérifié par le rédacteur de la v2 sur
six séries téléchargées par l'API le 2026-11-12 (HTTP 200 au premier essai pour chacune) :

| Millésime | Fin du texte de `TITLE_COMPL` | Colonne `TITLE` | Premier trimestre de statut `F` |
|---|---|---|---|
| `W21` | « … March 2021 staff macroeconomic projections » | vide à toutes les lignes | 2021-Q1 |
| `G21` | « … June 2021 staff macroeconomic projections » | vide à toutes les lignes | 2021-Q2 |
| `S21` | « … September 2021 staff macroeconomic projections » | vide à toutes les lignes | 2021-Q3 |
| `A21` | « … December 2021 staff macroeconomic projections » | vide à toutes les lignes | 2021-Q4 |
| `G25` | « … Spring/June 2025  staff macroeconomic projections » (deux espaces après l'année) | vide à toutes les lignes | 2025-Q2 |
| `S25` | « … Summer/September 2025  staff macroeconomic projections » (deux espaces après l'année) | vide à toutes les lignes | 2025-Q3 |

Dans ces six séries, le premier trimestre projeté est le trimestre de l'exercice lui-même. L'expérimentateur de la course
annulée rapporte la même correspondance pour les 111 millésimes (`tests-de-mort/H03/ecarts.md`, écart 2).

**Passages changés** (dans l'ordre du texte ; « v1 » = ancien libellé, « v2 » = nouveau libellé).

| N° | Où | v1 | v2 | Raison |
|---|---|---|---|---|
| 1 | titre | `# H03 — Préinscription…` | `# H03-v2 — Préinscription…` | nouvel identifiant du test amendé |
| 2 | section 3, ligne A11 | « (dernier : `G26`) » | « (dernier : `S26`) » | correspondance : le dernier exercice de la liste, septembre 2026, porte la lettre `S` |
| 3 | section 4, « Liste figée » | « `S` = juin (trimestre 2), `G` = septembre (trimestre 3) » | « `G` = juin (trimestre 2), `S` = septembre (trimestre 3) » | correspondance : c'est l'erreur qui a fait annuler la course |
| 4 | section 4, « Liste figée » | « `W`, `S`, `G`, `A` pour chaque année de 1999 à 2025 (108 codes), plus `W26`, `S26`, `G26` » | « `W`, `G`, `S`, `A` pour chaque année de 1999 à 2025 (108 codes), plus `W26`, `G26`, `S26` » | correspondance : ordre des exercices dans l'année ; les 111 codes sont les mêmes |
| 5 | section 4, « Liste figée » | « Non vérifié : la correspondance des lettres `S`, `G`, `A` (reprise de la fiche) et le contenu des millésimes anciens ; deux contrôles du schéma (section 5) les vérifient. » | « Vérifié pour la v2, dans la colonne `TITLE_COMPL` et par le premier trimestre de statut `F` : la correspondance des lettres sur `W21`, `G21`, `S21`, `A21`, `G25` et `S25` (détail dans « Amendement v2 »). Non vérifié par le rédacteur : la correspondance des lettres pour les autres millésimes et le contenu des millésimes anciens ; deux contrôles du schéma (section 5) les vérifient. » | la phrase de la v1 serait fausse : la correspondance n'est plus reprise de la fiche, elle a été vérifiée sur six millésimes |
| 6 | section 4, « Format constaté » | « Colonnes utiles : … `OBS_STATUS` (…), `TITLE`. » | « Colonnes utiles : … `OBS_STATUS` (…), `TITLE_COMPL`. » | colonne : `TITLE` existe mais elle est vide ; le titre est dans `TITLE_COMPL` |
| 7 | section 4, « Téléchargement » | `tests-de-mort/H03/donnees/MPD_Q_U2_HIC_A_<MILLÉSIME>.csv` | `tests-de-mort/H03-v2/donnees/MPD_Q_U2_HIC_A_<MILLÉSIME>.csv` | nouvel identifiant : la course amendée a son propre dossier et n'écrit rien dans celui de la course annulée |
| 8 | section 4, « Lecture de la valeur réalisée » | « (lu dans `G26`) » | « (lu dans `S26`) » | correspondance : le millésime de numéro 8106 (2026-Q3) est `S26` |
| 9 | section 5, « Nom » | `tests-de-mort/H03/H03_analyse.csv` | `tests-de-mort/H03-v2/H03-v2_analyse.csv` | nouvel identifiant et nouveau nom du fichier d'analyse |
| 10 | section 5, tableau, colonne `mois_titre` | « mois lu dans `TITLE` » | « mois lu dans `TITLE_COMPL` » | colonne : c'est cette définition que lit le contrôle n° 4 ; lu dans `TITLE`, il ne portait sur aucune ligne |
| 11 | section 11, bloc json | `"id": "H03"` | `"id": "H03-v2"` | nouvel identifiant |
| 12 | section 11, bloc json | `"fichier_analyse": "H03_analyse.csv"` | `"fichier_analyse": "H03-v2_analyse.csv"` | nouveau nom du fichier d'analyse |

**Le contrôle n° 4 reste une garde.** Son libellé est celui de la v1 (« `mois_titre`, quand il n'est pas vide, vaut 3 ×
(numéro du trimestre du millésime) »). Avec le passage n° 10, il compare maintenant le mois écrit dans `TITLE_COMPL` au
trimestre tiré de la lettre. Un seul désaccord donne `n_violations_schema` > 0, donc « non concluant » (section 8,
condition 1, inchangée).

**Passages dont le libellé est identique à la v1, mais dont l'effet change avec la correspondance.** Ils sont écrits avec
des numéros de trimestre, pas avec des lettres ; aucun mot n'en a été changé.
- Numéro du millésime (section 4, « Numéro de trimestre » ; section 5, `t_millesime` et contrôle n° 3) : un millésime `G`
  prend le trimestre 2 et un millésime `S` le trimestre 3. Exemples tirés de la formule : `G21` a t = 8085, `S21` a
  t = 8086.
- Ordre des millésimes dans une année (tri du fichier d'analyse par `t_millesime`) : `W`, `G`, `S`, `A`.
- Millésime précédent et révision (section 2, « révision » ; section 4, « Lecture de la projection précédente » ; section 5,
  `millesime_precedent`, contrôles n° 9 et n° 11) : le millésime de numéro `t_millesime` − 1 est maintenant l'exercice publié
  juste avant — décembre de l'année d'avant pour `W`, `W` pour `G`, `G` pour `S`, `S` pour `A`. Chaque révision compare deux
  exercices consécutifs.
- Valeur réalisée (section 4) et règle d'apprentissage (section 6, étape 2, `t_lecture` ≤ `t_millesime`) : les numéros
  suivent maintenant l'ordre de publication.
- Nombres attendus : aucun ne change. 111 millésimes (les mêmes codes), 444 lignes, 15 colonnes, 11 contrôles, 88 trimestres
  cibles, 352 lignes évaluées au plus, 11 blocs, dernier trimestre cible réalisé 2026-Q1, numéro maximal 8106.

**Rien d'autre n'est changé.** Les seuils, la statistique, les blocs, les gardes, l'arithmétique de puissance et la règle de
verdict sont identiques à la v1, au mot et au chiffre près. Le paragraphe « Ce que le rédacteur a vu des données » qui suit
est celui de la v1 : il décrit ce qu'avait vu le rédacteur de la v1 et il est laissé tel quel.

**Ce qui avait été vu avant de sceller la v2.**
- Selon `tests-de-mort/H03/annulation.md`, recopié : « Ce qui a été vu avant de la sceller : les chiffres de la course
  annulée ci-dessus, et rien sous la bonne correspondance. » Les chiffres que ce document donne : la corrélation moyenne de
  la course annulée (−0,06), calculée sous la correspondance fausse, et les 224 lignes qui violent le contrôle n° 4 quand
  on le lit sur `TITLE_COMPL`. L'expérimentateur de la course annulée n'a pas calculé la statistique sous la bonne
  correspondance.
- Ce que le rédacteur de la v2 a lu : `annulation.md`, la v1 scellée et `ecarts.md` du dossier H03, et rien d'autre de ce
  dossier (ni témoin, ni fichiers d'analyse, ni rapports, ni annexe, ni fichiers de vérification, ni données). `ecarts.md`
  ne donne ni la statistique ni ses bornes ; il donne des faits de structure de la course annulée, tous sous la
  correspondance fausse : le tableau lettre / mois du titre / premier trimestre projeté des 111 millésimes ;
  `n_violations_schema` égal à 0 ou à 1 selon la colonne lue ; 111 fichiers reçus au premier essai ; 6 206 clés, pas de clé
  `A26` ; 11 blocs valides avec 8 lignes par horizon ; 426 valeurs réalisées présentes, toutes lues au numéro cible + 2.
- Ce que le rédacteur de la v2 a vu de la source : les six séries du tableau ci-dessus. De chacune : les noms de colonnes,
  le nombre de lignes, le contenu de `TITLE` et de `TITLE_COMPL`, le dernier trimestre de statut `A` et le premier de
  statut `F`. Aucune valeur de `OBS_VALUE` n'a été affichée.
- Un seul calcul a été fait, sans donnée : la vérification de l'exemple « deux blocs parfaits, neuf blocs nuls » de la
  section 7 (voir « Autres erreurs constatées, non corrigées »).

Le texte de la v1, avec les douze passages changés, commence sous ce trait.

---

Rédigé le 2026-11-12 par le rédacteur de préinscription. Le rédacteur n'a lancé aucune analyse : aucune erreur, moyenne,
régression ou statistique n'a été calculée sur les données. Les seuls calculs faits sont des calculs de puissance théoriques
(loi de Student non centrale), sans donnée.

**Ce que le rédacteur a vu des données.** (a) La liste des 6 206 clés de séries de la base MPD (clés seules, sans valeur) :
HTTP 200 au premier essai. (b) Une seule série, `MPD.Q.U2.HIC.A.W21.0000` (HTTP 200 au premier essai) : la ligne d'en-tête,
les trois premières lignes (valeurs historiques de 1995), le nombre de lignes (116 trimestres, 1995-Q1 à 2023-Q4), la colonne
des dates et la colonne `OBS_STATUS` des quatorze dernières lignes **sans les valeurs**, et le format des nombres (une
décimale). Aucune valeur de projection ni aucune valeur réalisée postérieure à 1995 n'a été affichée.
**Ce que le rédacteur sait par ailleurs** : les résultats publiés résumés dans `nouveaute/F13.md` (tests en échantillon de la
BCE et de trois équipes extérieures). Ces résultats ont guidé des choix de plan ; c'est dit dans les limites.

---

## 1. Ce test peut-il trancher ?

**Réponse courte : le test de la fiche, non. Le test redessiné ici, en partie seulement.** Il peut trancher si la vérité est
à l'un des deux bouts (pas de prévisibilité du tout, ou une prévisibilité au moins aussi forte que ce que la fiche prédit).
Il ne peut pas trancher si la vérité est entre les deux, et la règle de verdict rend alors « non concluant ».

**Pourquoi le test de la fiche ne peut pas trancher.** Les trois juges ont raison. À l'horizon de 4 trimestres, deux erreurs
de projection faites à moins de 4 trimestres d'écart partagent les mêmes chocs : 23 millésimes font environ 23 / 4 ≈ 6
observations indépendantes. De plus, le test compare des erreurs **au carré** : les erreurs de 2021-2022 sont plusieurs fois
plus grandes que les autres, donc ces deux années pèsent presque tout. Enfin, une différence d'erreurs quadratiques est une
statistique peu sensible : si la corrélation entre la correction et l'erreur vaut ρ, le t attendu vaut environ ρ × √N / 2.
Avec N = 6 et l'effet prédit par la fiche (ρ entre 0,22 et 0,39, voir section 2), le t attendu est de 0,3 à 0,5 : la
puissance est de 15 à 20 %. Un tel test « tue » l'idée quatre fois sur cinq même si elle est vraie.

**Ce que le nouveau plan change, et ce que chaque changement rapporte vraiment.**

| Changement | Ce qu'il rapporte | Ce qu'il ne règle pas |
|---|---|---|
| Évaluer toute l'histoire (cibles 2004 à 2025) avec une règle récursive fixée ici | 88 trimestres cibles au lieu de 23 millésimes ; la règle n'est plus choisie en connaissant 2021-2022 | le plan lui-même est écrit en 2026 par quelqu'un qui connaît l'épisode |
| Regrouper les horizons 1 à 4 | un peu d'information en plus | peu : dans un même millésime, les révisions des quatre horizons bougent ensemble |
| Statistique sans unité par bloc de deux ans, tous les blocs pesant autant | 2021-2022 ne pèse plus que 2 blocs sur 11 ; deux blocs seuls ne peuvent pas faire survivre l'idée (section 7) | à l'intérieur d'un bloc, les grosses erreurs pèsent encore plus que les petites |
| Tester la covariance entre correction et erreur, pas la différence d'erreurs quadratiques | le t attendu double (ρ × √N au lieu de ρ × √N / 2) | on teste « l'erreur était prévisible », ce qui est un peu moins que « la règle telle quelle réduit l'erreur » ; une garde traite ce second point |
| Écart-type calculé entre blocs | le chevauchement est traité sans hypothèse : si les données sont plus dépendantes que prévu, l'intervalle s'élargit et le verdict devient « non concluant » | 11 blocs seulement : la précision elle-même est mal connue |

**Combien d'observations indépendantes ?** 11 blocs de deux ans. À l'intérieur d'un bloc, on attend l'équivalent d'environ 8
observations indépendantes (une par millésime : sous l'hypothèse d'efficience, les nouvelles de deux trimestres différents
sont indépendantes ; les quatre horizons d'un même millésime comptent à peu près pour un). Cela fait de l'ordre de **90
observations effectives** au lieu de 6, avec une fourchette honnête de 45 à 130. Ce chiffre central repose sur un raisonnement,
pas sur une mesure : le rédacteur n'avait pas le droit de regarder les données.

**Ce que cela donne** (probabilités calculées sans donnée, section 7 ; ce sont des plafonds) :

| Si la vérité est… | survit | éliminée | non concluant |
|---|---|---|---|
| aucune prévisibilité (R = 0) | 5 % | 61 % (39 à 76 %) | 34 % |
| le bas de la prédiction de la fiche (R = 0,22) | 61 % (39 à 76 %) | 5 % | 34 % |
| le haut de la prédiction de la fiche (R = 0,39) | 96 % (78 à 99 %) | < 1 % | 4 % |
| un petit effet (R = 0,11, proche de ce qu'on trouve aux États-Unis) | 25 % | 25 % | 50 % |

Entre parenthèses : scénario pessimiste (45 observations effectives) et optimiste (130).

**Conclusion honnête.** Le plan passe d'une puissance de 15-20 % à environ 60 % contre le bas de la prédiction de la fiche,
et à plus de 90 % contre le haut. Ce n'est pas les 80 % qu'on vise d'habitude. Contre un petit effet, le test ne peut rien
dire, et aucun plan fondé sur ces données publiques ne le pourrait : il n'existe que 111 exercices de projection, et on ne
peut pas en fabriquer d'autres. Dans ce cas, la règle rend « non concluant », pas « éliminée ». Deux choses resteront hors
de portée quel que soit le verdict : savoir si la prévisibilité vient du jugement des services ou des hypothèses techniques
imposées (pétrole, taux), et disposer de données vraiment postérieures à l'écriture du plan.

---

## 2. Question, hypothèse et prédiction chiffrée

**Question.** Quand les services de la BCE et de l'Eurosystème publiaient une projection d'inflation, pouvait-on, avec les
seules données connues ce jour-là, prévoir une partie de l'erreur à venir à partir de la révision par rapport à l'exercice
précédent ?

**Position par rapport à l'évaluation de la BCE.** L'article du Bulletin économique n° 5/2024 (Chahad et coauteurs) fait déjà
la régression de l'erreur sur la révision, **en échantillon**, par fenêtres glissantes, jusqu'à 2024T1 : il conclut à une
rigidité aux horizons de 1 à 3 trimestres. Un test en échantillon dit qu'un lien existe quand on regarde toute la période
après coup. Il ne dit pas si quelqu'un aurait pu s'en servir à l'époque : le coefficient peut changer de taille ou de signe
d'une période à l'autre. **Ce que ce test ajoute** : la règle de correction est estimée à chaque millésime avec les seules
données connues à cette date, puis jugée sur ce qui suit (temps réel, hors échantillon), sur toute l'histoire et jusqu'aux
cibles de 2025. La note de nouveauté n'a trouvé aucun exercice de ce type pour la BCE.

**Définitions.** Variable : inflation IPCH de la zone euro, glissement annuel trimestriel, en %. Pour un millésime v et un
trimestre cible q situé h trimestres après le trimestre du millésime (h = 1 à 4) :
- erreur = valeur réalisée en temps réel − projection ;
- révision = projection du millésime v − projection du millésime précédent pour le même trimestre cible ;
- correction = b × révision, où b est la pente estimée avec les seules données connues au millésime v (section 6).

**Hypothèse falsifiable.** Les projections sous-réagissent : la correction annoncée par la règle en temps réel est corrélée
positivement avec l'erreur qui se réalise ensuite.

**Statistique principale.** R̄ : moyenne, sur 11 blocs de deux ans (cibles 2004 à 2025), de la corrélation non centrée, dans
le bloc, entre la correction annoncée et l'erreur réalisée. R̄ = 0 : la règle n'annonce rien. R̄ = 1 : elle annonce tout.
Lecture simple : avec une corrélation R, une règle bien réglée retire une part R² de l'erreur quadratique.

**Prédiction chiffrée de la fiche, traduite dans cette statistique.** La fiche prédit un rapport d'erreurs quadratiques de
0,85 à 0,95. Comme rapport = 1 − R², cela correspond à **R̄ entre 0,22 et 0,39**, avec une pente b positive dans la majorité
des cas. La fiche prédit aussi un gain à 4 trimestres et aucun à 1 trimestre : ce profil par horizon sera montré à titre
descriptif (section 6, analyse S2).

**Attente du rédacteur, écrite pour mémoire (elle n'entre pas dans le verdict).** Les travaux publiés pèsent contre la
prédiction : coefficient non significatif sur 1999-2019 (Granziera et coauteurs), rigidité à 1-3 trimestres plutôt qu'à 4
(BCE), gain d'environ 1 % seulement sur enquêtes américaines (Eva et Winkler, soit R ≈ 0,1). Le rédacteur s'attend à un R̄
entre 0 et 0,15, donc à « éliminée » ou « non concluant » plutôt qu'à « survit ».

---

## 3. Amendements déclarés

Chaque ligne change le test de mort écrit dans la fiche. Le test de la fiche, tel qu'écrit, est quand même calculé et montré
à titre descriptif (analyse S1).

| N° | La fiche disait | Ce test fait | Raison |
|---|---|---|---|
| A1 | millésimes 2020T1 et suivants (environ 23) | toutes les cibles de 2004T1 à 2025T4 (88 trimestres) | 6 observations indépendantes ne tranchent rien ; l'épisode 2021-2022 décidait seul (les trois juges) |
| A2 | règle figée sur les millésimes d'avant 2020 | règle récursive : à chaque millésime, pente réestimée sur tout ce qui est connu ; règle entièrement écrite ici | une règle figée en 2019 n'utilise pas ce qu'on apprend ensuite ; la règle ne dépend plus d'une date de coupure choisie en connaissant l'épisode |
| A3 | horizon principal : 4 trimestres | horizons 1, 2, 3 et 4 regroupés, une pente par horizon | plus d'information ; la BCE trouve la rigidité aux horizons courts, la fiche à 4 : regrouper évite de parier sur un seul |
| A4 | différence des pertes quadratiques, test de Diebold-Mariano corrigé (HLN) | corrélation non centrée entre correction et erreur, par bloc de deux ans, moyenne des blocs | la différence de pertes quadratiques a un t attendu deux fois plus faible et se laisse dominer par les grosses erreurs ; la corrélation par bloc est sans unité |
| A5 | écart-type de Diebold-Mariano | test de Student sur les moyennes de blocs, avec correction pour la ressemblance de deux blocs voisins | le chevauchement est traité par construction, sans choix de fenêtre de lissage ; méthode qu'on explique en une phrase |
| A6 | meurt si rapport ≥ 0,95 ou p > 0,10 | trois issues : survit, éliminée, non concluant ; seuil unilatéral de 5 % | avec peu de puissance, « non significatif » ne prouve pas l'absence d'effet : l'idée n'est éliminée que si les données excluent le plus petit effet prédit ; 5 % est le seuil qu'un jury attend |
| A7 | (rien) | deux gardes pour survivre : R̄ positif hors blocs 2020-2023 ; rapport d'erreurs quadratiques par bloc < 1 | répondre à « le succès viendrait d'un épisode unique » ; vérifier que la règle telle quelle réduit bien l'erreur, comme la fiche le dit |
| A8 | constante de la régression : non précisé | constante estimée mais non appliquée ; au moins 8 points pour estimer | la constante évite que la pente ramasse un biais moyen ; on ne l'applique pas, parce que corriger un biais moyen est une autre idée, déjà étudiée |
| A9 | réalisation lue deux trimestres plus tard | inchangé, avec repli sur le millésime suivant (trois, puis quatre trimestres plus tard) si la valeur manque | ne pas perdre une observation pour un trou isolé |
| A10 | horizons secondaires 1, 2, 6, 8 avec correction de Holm ; comparaison à la marche aléatoire et à l'enquête SPF ; décomposition pétrole | retirés du test de mort | ils ne servent pas au verdict ; les horizons 6 et 8 ne sont pas garantis dans tous les millésimes ; ils restent au programme du projet si la fiche survit |
| A11 | millésime de décembre 2026 scellé à part | exclu : la liste des 111 millésimes est figée (dernier : `S26`) | il sera publié après cette préinscription ; une observation de plus ne change rien et brouillerait la liste |
| A12 | (rien) | analyse placebo descriptive (S3) | voir si la règle « marche » aussi avec une révision vieille de deux ans, ce qui signalerait un biais lent plutôt qu'une sous-réaction aux nouvelles |

---

## 4. Données

**Source unique.** Base des projections macroéconomiques de la BCE (MPD), par l'API du portail de données de la BCE.
Aucun compte. Aucune autre source.

**Séries.** Une série par exercice de projection (millésime) :

```
https://data-api.ecb.europa.eu/service/data/MPD/Q.U2.HIC.A.<MILLÉSIME>.0000?format=csvdata
```

Clé : `MPD.Q.U2.HIC.A.<MILLÉSIME>.0000` (fréquence trimestrielle, zone euro `U2`, IPCH total `HIC`, taux de croissance annuel
`A`, origine `0000`). Liste des clés, pour contrôle :
`https://data-api.ecb.europa.eu/service/data/MPD?detail=serieskeysonly&format=csvdata`.

**Liste figée des 111 millésimes.** Code = une lettre + deux chiffres d'année. Lettres : `W` = exercice de mars (trimestre 1),
`G` = juin (trimestre 2), `S` = septembre (trimestre 3), `A` = décembre (trimestre 4). Années : `99` = 1999, `00` à `26` =
2000 à 2026. La liste est : `W`, `G`, `S`, `A` pour chaque année de 1999 à 2025 (108 codes), plus `W26`, `G26`, `S26`.
Tout autre code est ignoré, y compris `A26` s'il existe au moment du téléchargement. Vérifié par le rédacteur : ces 111 clés
existent dans la liste ; `W21` a pour titre « … March 2021 staff macroeconomic projections ». Vérifié pour la v2, dans la
colonne `TITLE_COMPL` et par le premier trimestre de statut `F` : la correspondance des lettres sur `W21`, `G21`, `S21`,
`A21`, `G25` et `S25` (détail dans « Amendement v2 »). Non vérifié par le rédacteur : la correspondance des lettres pour
les autres millésimes et le contenu des millésimes anciens ; deux contrôles du schéma (section 5) les vérifient.

**Numéro de trimestre.** Pour tout trimestre : t = 4 × année + (numéro du trimestre − 1). Exemples : 1999-Q1 → 7996 ;
2004-Q1 → 8016 ; 2025-Q4 → 8103 ; 2026-Q3 → 8106. Le millésime `W21` a t = 8084.

**Format constaté (sur `W21`).** CSV avec en-tête. Colonnes utiles : `KEY`, `TIME_PERIOD` (forme `1995-Q1`), `OBS_VALUE`
(nombre à une décimale, parfois écrit sans décimale), `OBS_STATUS` (`A` = valeur observée, `F` = valeur projetée), `TITLE_COMPL`.
Dans `W21`, les trimestres jusqu'à 2020-Q4 ont le statut `A` ; 2021-Q1 à 2023-Q4 ont le statut `F`.

**Téléchargement.** L'API est intermittente (503 et délais dépassés constatés par les auteurs de la fiche). Pour chaque
millésime : jusqu'à 10 essais espacés de 10 secondes ; on garde le premier fichier reçu avec HTTP 200 et une ligne d'en-tête
conforme. Chaque fichier brut est gardé sous `tests-de-mort/H03-v2/donnees/MPD_Q_U2_HIC_A_<MILLÉSIME>.csv`, avec son sha256, la
date et le code HTTP dans `construire_journal.json`. **Si un seul des 111 fichiers ne peut pas être obtenu, l'expérimentateur
s'arrête et ne construit pas le fichier d'analyse** : la fiche est alors non concluante pour une raison de données.

**Lecture de la projection.** Pour le millésime v (numéro t_v) et l'horizon h (1 à 4), le trimestre cible est q = t_v + h.
La projection est `OBS_VALUE` à la ligne `TIME_PERIOD` = q du fichier du millésime v, **à condition que `OBS_STATUS` = `F`**.
Manquante si : la ligne n'existe pas, la valeur est vide, ou le statut n'est pas `F`.

**Lecture de la projection précédente.** Même règle, dans le fichier du millésime dont le numéro vaut t_v − 1, pour le même
trimestre cible q (c'est donc sa projection à l'horizon h + 1). Manquante dans les mêmes cas, et pour `W99` qui n'a pas de
prédécesseur.

**Lecture de la valeur réalisée en temps réel.** Pour le trimestre cible q : on ouvre le millésime de numéro q + 2 et on lit
`OBS_VALUE` à la ligne `TIME_PERIOD` = q, **à condition que `OBS_STATUS` = `A`**. Si la ligne manque, si la valeur est vide ou
si le statut n'est pas `A`, on essaie le millésime q + 3, puis q + 4. Si aucun des trois ne convient, ou s'ils sont hors de
la liste figée, la valeur réalisée est manquante. On note le numéro du millésime de lecture (`t_lecture`). Conséquence : le
dernier trimestre cible qui a une valeur réalisée est 2026-Q1 (lu dans `S26`).

**Ce qui compte comme manquant, en résumé.** Une ligne du fichier d'analyse est **complète** si la projection, la projection
précédente et la valeur réalisée sont toutes les trois présentes. On ne remplace jamais une valeur manquante par une autre
source, une interpolation ou une valeur annuelle.

---

## 5. Fichier d'analyse

**Nom** : `tests-de-mort/H03-v2/H03-v2_analyse.csv`. UTF-8, séparateur virgule, point décimal, première ligne = noms de colonnes,
cellule vide = manquant. **Une ligne par (millésime, trimestre cible, horizon)** : les 111 millésimes × les horizons 1, 2,
3, 4, soit **exactement 444 lignes**, y compris quand des valeurs manquent. Tri : `t_millesime` croissant, puis `horizon`.

| Colonne | Type | Unité, contenu |
|---|---|---|
| `millesime` | texte | code du millésime, par exemple `W21` |
| `t_millesime` | entier | numéro du trimestre du millésime (formule ci-dessus) |
| `mois_titre` | entier ou vide | mois lu dans `TITLE_COMPL` (nom de mois anglais → 1 à 12) ; vide si aucun nom de mois |
| `t_premier_F` | entier ou vide | numéro du premier trimestre de statut `F` dans le fichier du millésime ; vide s'il n'y en a aucun |
| `horizon` | entier | 1, 2, 3 ou 4 (trimestres) |
| `cible` | texte | trimestre cible, forme `2022-Q1` |
| `t_cible` | entier | `t_millesime` + `horizon` |
| `projection` | décimal ou vide | % en glissement annuel, une décimale |
| `millesime_precedent` | texte ou vide | code du millésime de numéro `t_millesime` − 1 ; vide pour `W99` |
| `projection_precedente` | décimal ou vide | % en glissement annuel, une décimale |
| `millesime_realise` | texte ou vide | code du millésime où la valeur réalisée a été lue |
| `t_lecture` | entier ou vide | numéro de ce millésime |
| `realise` | décimal ou vide | % en glissement annuel, une décimale |
| `revision` | décimal ou vide | `projection` − `projection_precedente`, en points de pourcentage, arrondi à une décimale |
| `erreur` | décimal ou vide | `realise` − `projection`, en points de pourcentage, arrondi à une décimale |

**Contrôles de schéma.** Le vérificateur les refait sur le fichier. `n_violations_schema` = nombre de contrôles violés
(0 attendu, 11 au plus).
1. Les 15 colonnes ci-dessus, dans cet ordre, avec ces noms exacts.
2. Exactement 444 lignes ; chaque couple (`millesime`, `horizon`) présent une fois ; 111 millésimes, tous dans la liste figée.
3. `t_millesime` égal à la valeur tirée du code (lettre et année) ; `t_cible` = `t_millesime` + `horizon` ; `cible` cohérent
   avec `t_cible`.
4. `mois_titre`, quand il n'est pas vide, vaut 3 × (numéro du trimestre du millésime).
5. `t_premier_F`, quand il n'est pas vide, est compris entre `t_millesime` − 2 et `t_millesime` + 1 (dans `W21`, il vaut
   `t_millesime`).
6. `projection`, `projection_precedente`, `realise` : vides, ou nombres entre −5 et 15 avec au plus une décimale.
7. `revision` est vide si et seulement si `projection` ou `projection_precedente` est vide ; sinon elle vaut leur différence
   à 0,000001 près. Même règle pour `erreur` avec `realise` et `projection`.
8. `t_lecture` et `millesime_realise` sont vides si et seulement si `realise` est vide ; sinon `t_lecture` vaut `t_cible` + 2,
   + 3 ou + 4, ne dépasse pas 8106, et correspond au code `millesime_realise`.
9. `millesime_precedent` est le code du numéro `t_millesime` − 1 (vide pour `W99` seulement).
10. Toutes les lignes qui ont le même `t_cible` ont le même `realise` et le même `t_lecture`.
11. Pour `horizon` ≤ 3 : `projection_precedente` de la ligne (v, h) est égale à `projection` de la ligne (millésime
    précédent, h + 1), ou les deux sont vides.

---

## 6. Statistique

Tout se calcule à partir du fichier d'analyse seul, en nombres flottants double précision, sans arrondi intermédiaire.
Aucun tirage aléatoire. Le téléchargement (111 requêtes) et le calcul tiennent en quelques minutes sur un portable.
Notation : pour une ligne i, r_i = `revision`, e_i = `erreur`.

**Étape 1 — lignes complètes.** Une ligne est complète si `revision` et `erreur` sont toutes deux présentes.

**Étape 2 — règle de correction récursive.** Pour chaque ligne complète i dont `t_cible` est entre 8016 et 8103 inclus
(cibles 2004-Q1 à 2025-Q4) :
- son **ensemble d'apprentissage** A(i) est l'ensemble des lignes complètes j de **même horizon** telles que
  `t_lecture`(j) ≤ `t_millesime`(i). En clair : les couples (révision, erreur) dont l'erreur était déjà connue le jour du
  millésime de la ligne i. La ligne i n'en fait jamais partie ;
- n_A = nombre de lignes de A(i) ; r̄ et ē = moyennes de r et de e sur A(i) ; S_rr = Σ (r_j − r̄)² sur A(i) ;
- la ligne i est **évaluée** si n_A ≥ 8 et S_rr > 10⁻¹² ;
- pente (moindres carrés ordinaires avec constante) : b_i = Σ (r_j − r̄)(e_j − ē) / S_rr ;
- correction annoncée : c_i = b_i × r_i. La constante n'est pas appliquée. La projection corrigée serait `projection` + c_i,
  et son erreur e_i − c_i.

**Étape 3 — blocs.** Chaque ligne évaluée va dans le bloc k = partie entière de ((`t_cible` − 8016) / 8), k = 0 à 10 :
bloc 0 = cibles 2004-2005, bloc 1 = 2006-2007, …, bloc 8 = 2020-2021, bloc 9 = 2022-2023, bloc 10 = 2024-2025. Un bloc
contient au plus 32 lignes. Un bloc est **valide** s'il a au moins 16 lignes évaluées, Σ c_i² > 10⁻¹² et Σ e_i² > 10⁻¹²
(sommes sur les lignes évaluées du bloc).

**Étape 4 — statistique de bloc.** Pour chaque bloc valide : R_k = Σ c_i e_i / racine(Σ c_i² × Σ e_i²). C'est une
corrélation calculée sans retrancher les moyennes : sous l'hypothèse d'efficience, l'erreur a une moyenne nulle sachant
ce qui est connu, donc il n'y a pas de moyenne à retrancher. R_k est entre −1 et 1.

**Étape 5 — statistique principale et intervalle.** K = nombre de blocs valides.
- **R̄ = moyenne simple des R_k** (champ `r_moyen`).
- g0 = Σ (R_k − R̄)² / (K − 1).
- g1 = Σ (R_k − R̄)(R_k+1 − R̄) / (K − 1), somme sur les paires de blocs valides dont les indices se suivent (k et k + 1).
- Écart-type de R̄ : **ET = racine((g0 + 2 × max(g1, 0)) / K)** (champ `et_r_moyen`). Le terme g1 traite le chevauchement
  qui reste entre deux blocs voisins : une projection faite fin 2005 pour début 2006 partage des chocs avec le bloc
  précédent. On n'élargit l'intervalle que si les blocs voisins se ressemblent ; on ne le rétrécit jamais.
- Quantile de Student à 95 %, K − 1 degrés de liberté : q = 1,8125 (K = 11) ; 1,8331 (K = 10) ; 1,8595 (K = 9) ; 1,8946
  (K = 8) ; 1,9432 (K = 7) ; 2,0150 (K = 6) ; 2,1318 (K = 5).
- `borne_basse_ic90` = R̄ − q × ET ; `borne_haute_ic90` = R̄ + q × ET. « Borne basse > 0 » est un test unilatéral à 5 % de
  R̄ > 0 ; « borne haute < 0,22 » est un test unilatéral à 5 % de R̄ < 0,22.
- Si K < 5 : `r_moyen`, `et_r_moyen`, les deux bornes, `r_hors_episode` valent 0 et `rapport_eqm_geo` vaut 1, par
  convention (le verdict est de toute façon non concluant).

**Étape 6 — gardes et champs dérivés.**
- `r_hors_episode` = moyenne simple des R_k sur les blocs valides autres que les blocs 8 et 9 (cibles 2020 à 2023).
- `rapport_eqm_geo` : pour chaque bloc valide, Q_k = Σ (e_i − c_i)² / Σ e_i² (remplacé par 10⁻⁶ s'il est plus petit) ;
  `rapport_eqm_geo` = exponentielle de la moyenne simple des logarithmes de Q_k. En dessous de 1 : dans un bloc typique,
  la règle telle quelle réduit l'erreur quadratique.
- `marge_indecision` = le plus petit des deux nombres (−`borne_basse_ic90`) et (`borne_haute_ic90` − 0,22). Elle est
  positive ou nulle exactement quand l'intervalle contient à la fois 0 et 0,22.
- `conflit_gardes` = 1 si `borne_basse_ic90` > 0 et (`r_hors_episode` ≤ 0 ou `rapport_eqm_geo` ≥ 1) ; 0 sinon.
- `n_obs_evaluees` = nombre de lignes évaluées (tous blocs) ; `n_blocs` = K.

**Analyses secondaires — descriptives, hors verdict.** Elles sont calculées et rapportées quoi qu'il arrive.

*S1 — Le test de la fiche tel qu'elle l'avait écrit.* Lignes d'horizon 4, complètes, avec `t_millesime` ≥ 8080 (2020-Q1) et
règle de l'étape 2 applicable (n_A ≥ 8, S_rr > 10⁻¹²), sans borne sur `t_cible`, rangées par `t_millesime` croissant ; n =
leur nombre (`n_obs_h4_2020`). `rapport_eqm_h4_2020` = Σ (e_i − c_i)² / Σ e_i². Pour le test : d_i = e_i² − (e_i − c_i)² ;
d̄ = moyenne ; γ_j = (1/n) Σ (d_i − d̄)(d_i−j − d̄) pour j = 0 à 3 ; V = (γ_0 + 2 (γ_1 + γ_2 + γ_3)) / n ; DM = d̄ / racine(V) ;
correction de Harvey-Leybourne-Newbold : DM* = DM × racine((n + 1 − 8 + 12/n) / n) ; `p_dm_hln_h4_2020` = probabilité
qu'une loi de Student à n − 1 degrés de liberté dépasse DM*. Si n < 8 ou V ≤ 0 : p = 1 par convention ; si n = 0 : rapport = 1.

*S2 — Lecture en clair.* Sur toutes les lignes évaluées : `rapport_eqm_global` = Σ (e_i − c_i)² / Σ e_i² ;
`rapport_eqm_hors_2021_2022` = le même en retirant les lignes dont `t_cible` est entre 8084 et 8091 ; `taux_amelioration` =
G / (G + P), où une ligne compte dans G si |e_i − c_i| < |e_i| − 10⁻⁹ et dans P si |e_i − c_i| > |e_i| + 10⁻⁹ (0,5 si
G + P = 0) ; `part_b_positif` = part des lignes évaluées avec b_i > 0. Par horizon h = 1 à 4 : `r_moyen_h1` à `r_moyen_h4` =
moyenne simple, sur les blocs, de R_k calculé avec les seules lignes évaluées d'horizon h (bloc retenu s'il a au moins 4
telles lignes et des sommes de carrés > 10⁻¹² ; 0 si aucun bloc).

*S3 — Placebo.* On refait les étapes 2 à 5 en remplaçant, pour chaque ligne i, la révision r_i par la révision de la ligne
de même horizon dont `t_millesime` vaut `t_millesime`(i) − 8 (une révision vieille de deux ans, qui ne porte aucune nouvelle
sur la cible de la ligne i). Une ligne est complète pour le placebo si cette révision décalée et son `erreur` sont
présentes ; l'apprentissage utilise les couples (révision décalée, erreur). On rapporte `r_moyen_placebo`, `et_r_placebo`
et `n_blocs_placebo` (0, 0 et le nombre de blocs si moins de 5 blocs valides). Lecture écrite d'avance : si
`r_moyen_placebo` dépasse 1,8 fois `et_r_placebo`, on écrira que la prévisibilité ne vient pas spécialement de la révision
récente, mais d'un biais lent.

**Fichiers.** L'expérimentateur écrit `temoin.json`, le vérificateur `verification.json` ; les deux contiennent tous les
champs de la règle (section 11), en nombres. Ni l'un ni l'autre n'écrit de verdict.

---

## 7. Arithmétique de puissance

Tout ce qui suit est calculé sans donnée, à partir de la loi de Student non centrale.

**Nombre d'observations.** Au plus 88 trimestres cibles × 4 horizons = 352 lignes évaluées, dans 11 blocs. Elles ne sont pas
indépendantes. Raisonnement : si les projections sont efficientes, la révision d'un millésime est une « nouvelle », et les
nouvelles de deux trimestres différents sont indépendantes ; les quatre horizons d'un même millésime reçoivent à peu près la
même nouvelle. Un bloc de deux ans contient donc environ m = 8 nouvelles indépendantes. Scénarios : pessimiste m = 4
(nouvelles très inégales en taille dans un bloc, pente commune mal estimée), central m = 8, optimiste m = 12 (les horizons
apportent un peu d'information propre). Soit 44, 88 ou 132 observations effectives.

**Écart-type attendu.** L'écart-type d'un R_k vaut environ 1 / racine(m), celui de R̄ environ 1 / racine(11 × m), avant la
correction de voisinage (qui l'augmente de 5 à 10 % en moyenne).

| Scénario | Observations effectives | ET attendu de R̄ | R̄ minimal pour survivre | Effet détecté 8 fois sur 10 | Éliminée si R̄ est sous |
|---|---|---|---|---|---|
| pessimiste (m = 4) | 44 | 0,15 | 0,27 | 0,40 | −0,05 |
| central (m = 8) | 88 | 0,11 | 0,19 | 0,29 | 0,03 |
| optimiste (m = 12) | 132 | 0,09 | 0,16 | 0,23 | 0,06 |

**Ce que le test peut détecter.** Dans le scénario central, un effet de R = 0,29 ou plus (une règle bien réglée retirerait
au moins 8 % de l'erreur quadratique) est détecté 8 fois sur 10. Le haut de la prédiction de la fiche (0,39) est détecté
96 fois sur 100.

**Ce qu'il détecte mal.** Le bas de la prédiction de la fiche (0,22) : 61 % de chances de survivre (39 % en pessimiste, 76 %
en optimiste), 34 % de « non concluant ».

**Ce qu'il ne peut pas détecter.** Un effet de R = 0,11 (gain possible de 1 % de l'erreur quadratique) : une chance sur
quatre de survivre, une sur quatre d'être éliminé, une sur deux de « non concluant ». Aucun effet inférieur à 0,15 environ
ne peut être séparé de zéro avec ces données.

**Ces chiffres sont des plafonds**, pour trois raisons : la règle en temps réel se trompe parfois sur le signe de la pente,
surtout au début (8 à 20 points d'apprentissage), ce qui abaisse le R̄ atteint ; les deux gardes peuvent transformer une
survie en « non concluant » ; les données sont arrondies à 0,1 point, ce qui ajoute un peu de bruit aux révisions.

**Protection contre l'épisode unique.** Si la règle était parfaite dans les deux blocs 2020-2021 et 2022-2023 (R = 1) et
nulle dans les neuf autres, on aurait R̄ = 0,18 et t = 1,49 sans correction de voisinage, 1,07 avec : sous le seuil de 1,81.
Deux blocs ne suffisent donc jamais. La garde `r_hors_episode` l'exige en plus directement.

**Comparaison avec le test de la fiche.** 6 observations indépendantes, différence d'erreurs quadratiques : t attendu de
0,27 à 0,48, puissance de 15 à 20 % au seuil de 10 %.

---

## 8. Règle de verdict

Le verdict est calculé par `verdict.py` à partir des chiffres du vérificateur. « Survit » veut dire : les erreurs étaient
prévisibles en temps réel par la règle de révision.

**Non concluant** si l'une de ces conditions est vraie :
1. `n_violations_schema` > 0 — le fichier d'analyse ne respecte pas son schéma ; on ne juge pas une idée sur un fichier douteux.
2. `n_blocs` < 9 — avec moins de 9 blocs valides sur 11, il manque plus de quatre ans de données : la base ne contient pas
   ce que la fiche annonçait, et le test de Student devient trop fragile.
3. `n_obs_evaluees` < 220 — moins de 62 % des 352 lignes possibles : même raison.
4. `marge_indecision` ≥ 0 — l'intervalle à 90 % contient à la fois 0 (pas de prévisibilité) et 0,22 (le plus petit effet
   prédit par la fiche) : les données ne peuvent pas choisir entre les deux.
5. `conflit_gardes` ≥ 1 — R̄ est significativement positif, mais soit il ne l'est plus hors des blocs 2020-2023, soit la
   règle telle quelle ne réduit pas l'erreur quadratique : les indices se contredisent.
6. Écart entre expérimentateur et vérificateur supérieur à la tolérance sur un champ, ou champ absent (protocole).

**Survit** si aucune condition ci-dessus n'est vraie et si les trois conditions suivantes le sont :
- `borne_basse_ic90` > 0. Seuil 0 : c'est la valeur de R̄ quand la règle n'annonce rien. Intervalle à 90 % : test unilatéral
  à 5 %, parce que l'hypothèse a un sens (corrélation positive) et que 5 % est le seuil d'usage.
- `r_hors_episode` > 0. On demande seulement un signe positif, pas un test : neuf blocs ont trop peu de puissance pour un
  test, mais un signe négatif hors 2020-2023 voudrait dire que tout vient de l'épisode.
- `rapport_eqm_geo` < 1. Seuil 1 : au-dessus, la règle telle quelle augmente l'erreur quadratique dans un bloc typique, et
  la phrase de la fiche (« la correction réduit l'erreur ») serait fausse même si l'erreur est prévisible. Le seuil de 0,95
  de la fiche n'est pas repris : il portait sur un autre échantillon et l'inférence est portée par R̄.

**Éliminée** dans tous les autres cas, c'est-à-dire quand `borne_basse_ic90` ≤ 0 et `borne_haute_ic90` < 0,22 : R̄ n'est pas
distinguable de zéro **et** les données excluent, au seuil de 5 %, le plus petit effet que la fiche prédisait. Seuil 0,22 :
la fiche prédit un rapport d'erreurs quadratiques d'au plus 0,95, soit R² ≥ 0,05, soit R ≥ racine(0,05) = 0,22. C'est le
seuil le plus favorable à la fiche : une règle estimée avec du bruit a besoin d'un R un peu plus grand pour atteindre 0,95.

**Tolérances.** 0 sur les champs entiers ; 0,005 sur les moyennes, écarts-types, rapports et probabilités ; 0,01 sur les
bornes et la marge (elles cumulent deux arrondis).

---

## 9. Limites

1. **Puissance moyenne.** Contre le bas de la prédiction de la fiche, le test conclut environ six fois sur dix dans le
   scénario central, quatre fois sur dix dans le pessimiste. Le nombre d'observations effectives (90) est un raisonnement,
   pas une mesure.
2. **Le plan n'est pas aveugle.** La règle est estimée en temps réel, mais le plan (horizons 1 à 4, blocs de deux ans,
   forme de la règle) est écrit en 2026 par quelqu'un qui connaît l'épisode 2021-2022 et les résultats en échantillon publiés
   jusqu'à 2024T1. Aucune donnée n'est postérieure au plan.
3. **Prévisible n'est pas fautif.** Les projections sont conditionnelles à des hypothèses techniques (pétrole tiré des
   contrats à terme, taux de marché). Une erreur prévisible peut venir de ces hypothèses et non du jugement des services.
   Ce test ne les sépare pas.
4. **Temps réel pour qui ?** Les millésimes de 1999-2000 et certains exercices anciens n'ont pas été publiés à l'époque
   avec ce détail trimestriel. « En temps réel » veut dire : avec les chiffres que les services avaient, pas forcément ceux
   qu'un observateur extérieur voyait.
5. **Onze blocs.** Le test de Student suppose des moyennes de blocs à peu près normales et indépendantes ; la correction de
   voisinage ne traite que deux blocs qui se suivent ; la pente estimée est commune à tous les blocs, ce qui crée un lien
   faible entre eux.
6. **Dans un bloc, les grosses erreurs pèsent plus.** La corrélation est sans unité d'un bloc à l'autre, pas à l'intérieur
   d'un bloc ; les horizons longs, aux erreurs plus grandes, y pèsent davantage.
7. **Biais lent.** Si les erreurs et les révisions gardent le même signe pendant des années (par exemple 2013-2019), R̄
   peut être positif sans sous-réaction aux nouvelles récentes. Le placebo S3 le signale, sans entrer dans le verdict.
8. **Données arrondies à 0,1 point**, et contenu des millésimes anciens non vérifié : si les anciens fichiers n'ont pas de
   statut `F` ou pas de détail trimestriel, des blocs manqueront et le verdict sera « non concluant » pour une raison de données.
9. **R̄ mesure une corrélation, pas un gain.** Un R̄ de 0,22 correspond à un gain d'au plus 5 % de l'erreur quadratique ;
   le gain réellement obtenu par la règle est donné par les rapports descriptifs.

---

## 10. Ce qu'on écrira dans chaque cas

- **Survit** : « Sur les cibles de 2004 à 2025, une règle estimée avec les seules données connues à chaque exercice
  annonçait une partie des erreurs de projection d'inflation de la BCE (corrélation moyenne par bloc de deux ans : R̄, avec
  son intervalle à 90 %), y compris hors 2020-2023 ; le sens (sous-réaction si la part de pentes positives dépasse la moitié),
  le gain en erreur quadratique et le placebo sont donnés à titre descriptif, et le test ne dit pas si cela vient du jugement
  des services ou des hypothèses techniques. »
- **Éliminée** : « Sur les cibles de 2004 à 2025, la règle de révision estimée en temps réel n'annonçait pas les erreurs de
  projection d'inflation de la BCE : la corrélation moyenne n'est pas distinguable de zéro et les données excluent, au seuil
  de 5 %, le plus petit effet que la fiche prédisait (0,22) ; le lien trouvé en échantillon par la BCE n'était pas exploitable
  à l'époque par cette règle. »
- **Non concluant, par indécision** (`marge_indecision` ≥ 0) : « Avec 111 exercices de projection, les données ne permettent
  ni d'établir ni d'exclure une prévisibilité de la taille prédite : l'intervalle à 90 % de R̄ contient à la fois 0 et 0,22 ;
  on publie l'intervalle et on ne conclut pas. »
- **Non concluant, par conflit** (`conflit_gardes` = 1) : « La corrélation moyenne est positive, mais elle tient à la
  période 2020-2023 ou ne se traduit pas en baisse de l'erreur quadratique ; on ne peut pas dire que la règle aurait servi. »
- **Non concluant, par les données** (schéma, blocs ou lignes insuffisants, fichier manquant, écart entre expérimentateur
  et vérificateur) : « Le test n'a pas pu être mené comme préinscrit ; la raison exacte est écrite dans `ecarts.md` et aucune
  conclusion n'est tirée sur l'hypothèse. »

---

## 11. Règle lisible par machine

```json
{
  "id": "H03-v2",
  "fichier_analyse": "H03-v2_analyse.csv",
  "champs_verification": [
    "n_violations_schema",
    "n_obs_evaluees",
    "n_blocs",
    "r_moyen",
    "et_r_moyen",
    "borne_basse_ic90",
    "borne_haute_ic90",
    "marge_indecision",
    "r_hors_episode",
    "rapport_eqm_geo",
    "conflit_gardes",
    "n_obs_h4_2020",
    "rapport_eqm_h4_2020",
    "p_dm_hln_h4_2020",
    "rapport_eqm_global",
    "rapport_eqm_hors_2021_2022",
    "taux_amelioration",
    "part_b_positif",
    "r_moyen_h1",
    "r_moyen_h2",
    "r_moyen_h3",
    "r_moyen_h4",
    "r_moyen_placebo",
    "et_r_placebo",
    "n_blocs_placebo"
  ],
  "survit_si": [
    {"champ": "borne_basse_ic90", "operateur": ">", "seuil": 0},
    {"champ": "r_hors_episode", "operateur": ">", "seuil": 0},
    {"champ": "rapport_eqm_geo", "operateur": "<", "seuil": 1}
  ],
  "non_concluant_si": [
    {"champ": "n_violations_schema", "operateur": ">", "seuil": 0},
    {"champ": "n_blocs", "operateur": "<", "seuil": 9},
    {"champ": "n_obs_evaluees", "operateur": "<", "seuil": 220},
    {"champ": "marge_indecision", "operateur": ">=", "seuil": 0},
    {"champ": "conflit_gardes", "operateur": ">=", "seuil": 1}
  ],
  "tolerance": {
    "n_violations_schema": 0,
    "n_obs_evaluees": 0,
    "n_blocs": 0,
    "r_moyen": 0.005,
    "et_r_moyen": 0.005,
    "borne_basse_ic90": 0.01,
    "borne_haute_ic90": 0.01,
    "marge_indecision": 0.01,
    "r_hors_episode": 0.005,
    "rapport_eqm_geo": 0.005,
    "conflit_gardes": 0,
    "n_obs_h4_2020": 0,
    "rapport_eqm_h4_2020": 0.005,
    "p_dm_hln_h4_2020": 0.005,
    "rapport_eqm_global": 0.005,
    "rapport_eqm_hors_2021_2022": 0.005,
    "taux_amelioration": 0.005,
    "part_b_positif": 0.005,
    "r_moyen_h1": 0.005,
    "r_moyen_h2": 0.005,
    "r_moyen_h3": 0.005,
    "r_moyen_h4": 0.005,
    "r_moyen_placebo": 0.005,
    "et_r_placebo": 0.005,
    "n_blocs_placebo": 0
  }
}
```

---

## Autres erreurs constatées, non corrigées

Section ajoutée par le rédacteur de la v2. Rien de ce qui suit n'a été corrigé dans le texte : l'orchestrateur décide.

1. **Section 7, « Protection contre l'épisode unique » : le chiffre 1,07.** Le texte dit que, si R vaut 1 dans les blocs
   2020-2021 et 2022-2023 (blocs 8 et 9) et 0 dans les neuf autres, t vaut 1,49 sans correction de voisinage et 1,07 avec.
   Refait sans donnée avec les formules de la section 6, étape 5 : 1,49 sans correction (conforme), mais **1,13** avec
   correction. Le chiffre 1,07 s'obtient si les deux blocs parfaits sont les deux derniers (blocs 9 et 10) ; or le bloc 10
   (2024-2025) vient après l'épisode. Les deux valeurs sont sous le seuil de 1,81 : la conclusion de la phrase (« deux blocs
   ne suffisent donc jamais ») tient. Ce chiffre est une illustration ; il n'entre dans aucun champ, aucun seuil et aucune
   règle. Sans lien avec la correspondance des lettres.

2. **Remarque sur deux gardes (pas une erreur de fait).** Le contrôle n° 4 ne porte que sur les lignes où `mois_titre`
   n'est pas vide : si `TITLE_COMPL` ne contenait aucun nom de mois, il serait de nouveau sans objet. Sur les six séries
   lues pour la v2, le titre contient un nom de mois ; la course annulée rapporte 444 lignes remplies sur 444. Le contrôle
   n° 5 accepte tout premier trimestre projeté entre `t_millesime` − 2 et `t_millesime` + 1 : seul, il n'aurait pas vu
   l'inversion. Les deux libellés sont ceux de la v1, laissés tels quels comme demandé.
