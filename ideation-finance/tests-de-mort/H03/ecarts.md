# H03 — Écarts à la préinscription

Rédigé par l'expérimentateur le 2026-11-12. Trois écarts. Les deux premiers sont liés et touchent un contrôle de schéma :
selon la lecture retenue, `n_violations_schema` vaut 0 ou 1. Tous les autres chiffres sont identiques dans les deux lectures.

---

## Écart 1 — La colonne `TITLE` est vide dans les 111 fichiers ; le titre est dans `TITLE_COMPL`

**Ce que dit la préinscription.** Section 5, colonne `mois_titre` : « mois lu dans `TITLE` (nom de mois anglais → 1 à 12) ;
vide si aucun nom de mois ». Section 4 : « Colonnes utiles : `KEY`, `TIME_PERIOD`, `OBS_VALUE`, `OBS_STATUS`, `TITLE` » et
« `W21` a pour titre "… March 2021 staff macroeconomic projections" ».

**Ce que contiennent les fichiers.** La colonne `TITLE` existe mais elle est vide à toutes les lignes des 111 fichiers. Le
texte cité par la préinscription (« … March 2021 staff macroeconomic projections ») se trouve dans la colonne voisine
`TITLE_COMPL`. La consigne ne peut donc pas être suivie telle qu'elle a été pensée.

**Lecture retenue (la plus littérale).** `mois_titre` est lu dans la colonne nommée `TITLE`. Elle ne contient aucun nom de
mois, donc `mois_titre` est vide dans les 444 lignes de `H03_analyse.csv`, comme le schéma le permet. Conséquence : le
contrôle n° 4 (« `mois_titre`, quand il n'est pas vide, vaut 3 × numéro du trimestre du millésime ») ne porte sur aucune
ligne et ne peut pas être violé.

**Autre lecture, chiffrée.** Si `mois_titre` est lu dans `TITLE_COMPL` :

| | Lecture retenue (`TITLE`) | Autre lecture (`TITLE_COMPL`) |
|---|---|---|
| lignes où `mois_titre` est rempli | 0 sur 444 | 444 sur 444 |
| contrôle n° 4 | sans objet, non violé | **violé sur 224 lignes (56 millésimes : les 28 `G` et les 28 `S`)** |
| `n_violations_schema` | **0** | **1** |
| les 24 autres champs du témoin | identiques | identiques |

Le fichier de l'autre lecture est gardé à part, hors du fichier d'analyse :
`annexe_lecture_TITLE_COMPL/H03_analyse_lecture_TITLE_COMPL.csv`. Il ne diffère de `H03_analyse.csv` que par la colonne
`mois_titre` (vérifié colonne par colonne). **Ce n'est pas le fichier d'analyse** ; il est là pour que l'orchestrateur puisse
faire recalculer l'autre lecture s'il le décide.

**Pourquoi c'est signalé en premier.** La préinscription (section 8, condition 1) rend le test non concluant dès que
`n_violations_schema` > 0. Le choix de lecture change donc ce champ. L'expérimentateur a appliqué la consigne reçue (lecture
la plus littérale) et ne tranche pas.

---

## Écart 2 — La correspondance des lettres `S` et `G` écrite dans la préinscription est contredite par la source

**Ce que dit la préinscription.** Section 4 : « `W` = exercice de mars (trimestre 1), `S` = juin (trimestre 2), `G` =
septembre (trimestre 3), `A` = décembre (trimestre 4) ». Elle ajoute : « Non vérifié : la correspondance des lettres `S`,
`G`, `A` (reprise de la fiche) […] ; deux contrôles du schéma (section 5) les vérifient. »

**Ce que disent les fichiers.** Dans les 111 fichiers, le titre (`TITLE_COMPL`) donne :

| Lettre | Mois dans le titre | Nombre de millésimes | Trimestre selon la préinscription | Premier trimestre de statut `F` |
|---|---|---|---|---|
| `W` | March | 28 | 1 | `t_millesime` (28 sur 28) |
| `G` | **June** (« Spring/June » en 2025 et 2026) | 28 | **3** | `t_millesime` − 1 (28 sur 28) |
| `S` | **September** (« Summer/September » en 2025 et 2026) | 28 | **2** | `t_millesime` + 1 (28 sur 28) |
| `A` | December | 27 | 4 | `t_millesime` (27 sur 27) |

Autrement dit, pour la source, `G` est l'exercice de juin et `S` celui de septembre : l'inverse de la préinscription. Le
premier trimestre projeté confirme le titre : il tombe sur le trimestre de l'exercice pour `W` et `A`, un trimestre avant
le numéro préinscrit pour `G`, un trimestre après pour `S`.

**Ce que les deux contrôles prévus ont vu.** Le contrôle n° 5 (`t_premier_F` entre `t_millesime` − 2 et `t_millesime` + 1)
tolère un décalage d'un trimestre dans chaque sens : il passe. Le contrôle n° 4 aurait détecté l'inversion, mais il est sans
objet dans la lecture littérale (écart 1). Dans le fichier d'analyse tel que préinscrit, aucun contrôle ne signale donc
l'inversion.

**Ce qui a été fait.** La préinscription est exécutée à la lettre : `t_millesime` est tiré du code avec `S` = trimestre 2 et
`G` = trimestre 3. Le point n'est pas ambigu dans le texte ; il est contraire aux faits. Il est consigné ici comme point
impossible à satisfaire tel qu'écrit (on ne peut pas avoir à la fois « `S` = exercice de juin » et le contenu du fichier `S`).

**Ce que cela change dans la construction du test** (faits de structure, sans aucun chiffre de résultat) :

- *Horizons.* Pour un millésime `S` (exercice de septembre, numéroté au trimestre 2), l'horizon 1 vise le trimestre de
  l'exercice lui-même et l'horizon 4 vise trois trimestres plus loin. Pour un millésime `G` (exercice de juin, numéroté au
  trimestre 3), l'horizon 1 vise deux trimestres après l'exercice et l'horizon 4 cinq trimestres après.
- *Révisions.* Le « millésime précédent » est celui du numéro `t_millesime` − 1. Sur les quatre révisions d'une année, une
  seule compare deux exercices qui se suivent (`W` : mars moins décembre). Les trois autres comparent : septembre moins mars
  (`S`), **juin moins septembre de la même année** (`G`, donc à rebours du temps), décembre moins juin (`A`).
- *Temps réel.* La règle d'apprentissage retient les lignes dont `t_lecture` ≤ `t_millesime`. Pour une ligne d'un millésime
  `G` (juin), elle admet donc des valeurs réalisées lues dans le fichier `S` de la même année (septembre), publiées après.
  À l'inverse, pour une ligne d'un millésime `S`, elle écarte des valeurs lues en juin qui étaient connues.
- *Valeur réalisée.* Toutes les valeurs réalisées ont été trouvées au premier essai (numéro cible + 2, statut `A`), mais ce
  numéro désigne, selon le trimestre cible, l'exercice publié un, deux ou trois trimestres après la cible.

**Ce qui n'a pas été fait, volontairement.** L'expérimentateur n'a pas recalculé la statistique avec la correspondance
corrigée (`G` = trimestre 2, `S` = trimestre 3). Ce serait une analyse non préinscrite, et son résultat ôterait tout
aveugle à une éventuelle préinscription amendée. Aucun chiffre de ce type n'existe dans ce dossier.

---

## Écart 3 — Le téléchargement est fait par un script séparé de `construire.py`

**Ce que dit la préinscription.** Section 4 : le sha256, la date et le code HTTP de chaque fichier vont dans
`construire_journal.json`, ce qui suggère un seul script qui télécharge et construit.

**Ce qui a été fait.** L'ordre de mission demande que `construire.py` rebâtisse le fichier d'analyse à partir de `donnees/`
seul. Le téléchargement est donc dans `telecharger.py`, qui écrit `construire_journal.json` (nom préinscrit). `construire.py`
ne fait aucune requête. Règle de téléchargement appliquée : celle de la préinscription (jusqu'à 10 essais espacés de 10 s,
premier fichier reçu avec HTTP 200 et en-tête conforme), et non celle de l'ordre de mission (8 essais avec attente
croissante). La question est restée théorique : les 111 fichiers ont été reçus au premier essai.

Détails non fixés par la préinscription et choisis par l'expérimentateur : délai maximal de 180 s par requête, pause de
1,5 s entre deux millésimes, en-tête `Accept-Encoding: identity`. Une requête d'essai sur `W21` a été faite à 18:59:47 UTC
avant de lancer le script ; son fichier n'a pas été gardé (il est identique octet pour octet à celui gardé ensuite).
La liste des clés, que la préinscription cite « pour contrôle », a été téléchargée en plus (`MPD_serieskeysonly.csv`) :
6 206 clés, les 111 clés attendues présentes, pas de clé `A26`.

**Effet sur les chiffres.** Aucun.

---

## Précisions qui ne sont pas des écarts

- **`r_moyen_h1` à `r_moyen_h4`.** La phrase « moyenne simple, sur les blocs, de R_k […] (bloc retenu s'il a au moins 4
  telles lignes […]) » peut se lire avec ou sans l'exigence que le bloc soit aussi valide au sens de l'étape 3. Lecture
  retenue : le seul critère écrit (au moins 4 lignes de l'horizon, sommes de carrés > 10⁻¹²). Les deux lectures donnent
  exactement les mêmes chiffres ici : les 11 blocs sont valides et ont 8 lignes par horizon.
- **Quantile de Student.** La valeur de la table préinscrite est utilisée telle quelle (1,8125 pour K = 11) ; la valeur
  exacte est 1,81246. Effet sur les bornes : moins de 0,00001.
- **Écriture des nombres dans le fichier d'analyse.** Les valeurs sont écrites avec une décimale (« 2 » devient « 2.0 ») et
  un zéro négatif est écrit « 0.0 ». Les valeurs brutes ont toutes au plus une décimale ; rien n'a été arrondi en dehors de
  l'arrondi à une décimale que le schéma demande pour `revision` et `erreur`.
- **Repli de lecture de la valeur réalisée (A9).** Jamais utilisé : les 426 valeurs réalisées présentes ont été lues au
  numéro cible + 2.
