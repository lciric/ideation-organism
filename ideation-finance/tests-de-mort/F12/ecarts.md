# F12 — Écarts à la préinscription

Rédigé par l'expérimentateur le 2026-11-12. La préinscription et son fichier `.sha256` n'ont pas été modifiés
(empreinte vérifiée avant et après le travail : `b52884058d99eab33841ddd20f6978791e7a88f4ed63b40c8884ca74c5f24a7c`).

Aucun écart ne touche la définition de l'échantillon, de la statistique principale, des seuils ou des champs de `temoin.json`.
Cinq écarts ou lectures sont consignés, du plus matériel au plus petit.

## E1 — Dossier des fichiers bruts : `donnees/` au lieu de `brut/`

- **Préinscription (§ 5)** : « Fichiers bruts conservés dans `tests-de-mort/F12/brut/` ».
- **Fait** : les fichiers bruts sont dans `tests-de-mort/F12/donnees/`, avec `donnees/PROVENANCE.md` ; `construire.py` lit `donnees/`.
- **Raison** : la consigne de l'orchestrateur à l'expérimentateur nomme `donnees/`. Pour que le chemin de la préinscription
  reste valide, `brut` est un lien symbolique vers `donnees` (mêmes fichiers, aucune copie).
- **Effet sur les nombres** : aucun.

## E2 — Ambiguïté de S1 (c), « pont » France : échantillon de la mesure intrajournalière

- **Préinscription (§ 6.2, S1)** : l'en-tête de S1 dit « Lignes `RIKSBANK` renseignées, `periode ∈ {avant, apres}` » ; le point (c)
  demande « `d` pour `FR` en journalier (`RIKSBANK`) et `d` pour `FR` en intrajournalier (`EAMPD`), côte à côte ». Le texte ne
  dit pas si la mesure intrajournalière se calcule sur toutes les réunions (87 et 26) ou sur les seules réunions où la
  mesure journalière existe (85 et 25).
- **Lecture retenue (la plus littérale)** : toutes les lignes `EAMPD` de `FR` en `avant` et `apres` (87 et 26).
- **Les deux lectures, descriptives** :

| Mesure France | n avant / après | `b_avant` | `b_apres` | `d` | erreur type |
|---|---|---|---|---|---|
| journalière (`RIKSBANK`) | 85 / 25 | 0,3827 | 0,0865 | −0,2962 | 0,2181 |
| intrajournalière (`EAMPD`), toutes réunions — lecture retenue | 87 / 26 | 0,2640 | 0,0719 | −0,1920 | 0,1193 |
| intrajournalière (`EAMPD`), mêmes dates que `RIKSBANK` | 85 / 25 | 0,2645 | 0,0716 | −0,1928 | 0,1248 |

- **Effet sur le verdict** : aucun (S1 est descriptive).

## E3 — Écriture des nombres dans `analyse_F12.csv` : arrondi à dix décimales

- **Préinscription (§ 5)** : « nombres écrits avec au moins quatre décimales », sans dire s'il faut arrondir ni à combien.
- **Fait** : chaque valeur est arrondie à dix décimales puis écrite avec dix décimales fixes. `d_ecart_pb` et
  `surprise_restrictive` sont calculés à partir des valeurs **arrondies**, pour que le fichier soit cohérent avec lui-même
  (contrôles 8 et 9).
- **Raison** : les valeurs d'EA-MPD portent du bruit de virgule flottante (par exemple −19,5000171661…), et les différences
  de rendements Riksbank aussi (2,0999999999999908 pour 2,1) ; un format fixe donne un fichier identique d'une exécution à l'autre.
- **Effet sur les nombres** : inférieur à 1e-9 sur toute valeur, donc invisible à la tolérance préinscrite (0,001).

## E4 — Lecture du contrôle 7 pour une ligne `RIKSBANK` à moitié cotée (cas non rencontré)

- **Préinscription (§ 4.2 et § 5, contrôle 7)** : la variation journalière est définie série par série ; le contrôle 7 exige
  que `d_rdt_pays_pb`, `d_rdt_de_pb` et `d_ecart_pb` soient vides ensemble ou renseignés ensemble. Le texte ne dit pas quoi
  écrire si le pays est coté mais pas l'Allemagne (ou l'inverse).
- **Lecture retenue** : dans ce cas, les trois cellules de la ligne sont vides. De même, le jour de référence `s` est
  cherché série par série (lecture littérale du § 4.2), sans imposer le même `s` au pays et à l'Allemagne.
- **Effet** : aucun. Le cas ne se produit pas : les quatre jours de réunion sans cotation (2012-06-06, 2013-06-06,
  2019-06-06, 2024-06-06) manquent dans les quatre séries à la fois, et le jour de référence est le même dans les quatre
  séries pour les 143 autres réunions (vérifié par `construire.py`).

## E5 — Ajouts non préinscrits, sans effet sur la statistique

- **Nombres descriptifs ajoutés au compte rendu**, tous tirés des mêmes régressions que la statistique principale, aucun
  nouvel échantillon ni nouvel estimateur : `se_b_avant` et `se_b_apres` séparément ; le plus petit `d` obtenu en retirant
  une réunion (la préinscription ne demande que le plus grand) et les dates des deux réunions concernées ; écarts types de
  `x`, de `y` et du résidu par régime, nombre effectif `(Σx²)²/Σx⁴` et levier maximal (grandeurs que le § 7 suppose sans
  les lire) ; erreur type et R² de la régression de calage `kappa` ; pentes par régime du placebo et de S3.
- **Contre-épreuve logicielle** : la formule fermée HC3 du § 6.1 est comparée à `statsmodels` (`cov_type="HC3"`) ;
  les deux coïncident à la sixième décimale. Elle n'entre dans aucun nombre rapporté.
- **Fichiers ajoutés** : `controles_schema.py` (les dix contrôles du § 5, appelés par `construire.py` et `analyse.py`),
  `construire.log`, `analyse.log`, `resultats_analyse.json` (nombres des analyses secondaires), `S2_fenetres.csv`
  (les 95 pentes de S2), `figure_S2.png` (le graphique que le § 6.2 demande pour S2 ; `figure.png` est la figure du
  résultat principal demandée par l'orchestrateur).
- **Raison** : rendre le compte rendu vérifiable et montrer l'incertitude. **Effet sur le verdict** : aucun.

## Points conformes, signalés pour mémoire (pas des écarts)

- Empreinte et taille de `Dataset_EA-MPD.xlsx` identiques à celles de la préinscription.
- 147 réunions, 33 / 87 / 1 / 26 par période ; aucune cellule vide ou non numérique dans les colonnes utilisées.
- 85 réunions `avant` et 25 `apres` utilisables pour S1, comme attendu au § 4.2.
- Interface de la Riksbank : quatre réponses HTTP 200 au premier essai (pause de trois secondes entre les appels).
- Constantes 1,32 et 1,66 utilisées telles quelles, non recalculées.
