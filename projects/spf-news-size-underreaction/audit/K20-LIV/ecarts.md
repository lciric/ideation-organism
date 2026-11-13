# K20-LIV — écarts, lectures ambiguës, incidents (expérimentateur)

Aucun écart de définition, de seuil, d'échantillon ou de formule par rapport à la préinscription scellée (sha256 vérifié : identique au fichier `.sha256`). Les points ci-dessous sont des précisions de lecture et des faits à connaître.

## A. Écarts
Aucun écart.

## B. Ouvertures de fichiers hors de la liste
1. Pour inspecter la structure, j'ai affiché les 3 premières lignes des feuilles `CPI` et `TPHS` de `means.xlsx` et `individualdata.xlsx` (en-têtes, valeurs de 1946), et les premières et dernières lignes de trois séries FRED. Ce sont des données de la préinscription, pas des résultats ; aucun calcul n'a été fait avant la construction du fichier.
2. J'ai listé le dossier `K20-LIV/` (`ls`), ce qui montre le nom de `simulation_decision.py`. Je ne l'ai pas ouvert.
3. Aucun fichier d'un autre dossier de `tests-de-mort/`, rien sous `projects/`, aucun journal git. Le fichier `livingston-documentation.pdf` a été téléchargé (HTTP 200) mais pas ouvert.

## C. Lectures ambiguës et choix (le plus proche de la lettre)
1. **Journal des téléchargements.** La section 3 demande `construire_journal.json` (sha256, date, HTTP) ; la consigne demande `donnees/PROVENANCE.md`. J'ai produit les deux avec le même contenu (`telecharger.py`). Le journal est écrit par le téléchargeur, pas par `construire.py`.
2. **Ancrage de la ligne IPC 2005-06** (paire à cheval). La préinscription dit : `serie_realise` = `CPIAUCSL`, et vide `y_prev_1`, `y_prev6_1`, `revision`, `surprise`, `revision_med`. Elle ne dit pas dans quelle série lire `ancre_niv_1` (avril 2004). Une seule colonne `serie_realise` existe : j'ai lu les trois valeurs réalisées (cible, ancre 1, ancre 2) dans `CPIAUCSL`. Cette valeur n'entre dans aucune quantité non vide de la ligne. `erreur` (= `y_realise` − `y_prev_2`) et `erreur_med` restent présentes ; `complete` = 0.
3. **a et A (étape 7).** Lecture retenue (la lettre) : a = moyenne de (z_r − m_{v,0})² sur toutes les lignes principales L = 0, groupées ; A de même sur L = 1. Autre lecture : a_v et A_v par variable, puis rapports moyens. Résultats : rapport groupé **10,100** (retenu) ; moyenne des rapports par variable 11,325 ; biais mécanique mesuré groupé **0,12198** (retenu) ; avec a_v, A_v par variable, 0,12732. Les deux lectures diffèrent de 0,005 sur le biais mesuré et de 1,22 sur le rapport de variances (au-delà de la tolérance 0,01 de ce champ) ; aucune ne change la position du plancher max(0,10 ; biais) au-delà de 0,006.
4. **`biais_mecanique_nu20`.** Appliqué à la lettre : (2 b_moyen + k_moyen) × **0,10** × (1/a − 1/A). Le texte dit « formule de K20, descriptif » ; le libellé « nu20 » (ν = 0,20) et le facteur 0,10 (= ν/2) concordent avec la section 7. Valeur 0,784 : elle est grande parce que 1/a − 1/A est grand quand les rapports de variance sont de l'ordre de 10.
5. **`episode_t_min`.** Entier k (1 à 11), le plus petit en cas d'égalité.
6. **Semestres de Driscoll-Kraay.** La plage va du plus petit au plus grand semestre de l'échantillon utilisé, y compris vides. Pour l'échantillon principal elle compte 158 semestres tous peuplés ; pour les exclusions d'épisode, les semestres retirés deviennent vides.
7. **S3.** Les quatre lignes `UNPR` 2020-06…2021-12 sont réduites avec les moyennes et écarts-types des lignes principales de `UNPR`, et leur L vient de `surprise` et de Q_v (principal), comme prescrit.
8. **S6.** Les moyennes et écarts-types de `revision_med` et `erreur_med` sont calculés sur les mêmes lignes principales ; L inchangé.
9. **Types.** `n_effectif` est écrit en décimal (tolérance 1). Les huit champs entiers (comptes, indicateurs, `episode_t_min`) sont des entiers JSON.
10. **Numéro de colonne `episode`.** Rempli sur les 555 lignes (fenêtre de la `cible`), y compris hors échantillon principal ; vide hors fenêtre.
11. **Contrôle 4, bp_1 / bp_2.** Lu comme « présentes si et seulement si `variable` = `CPI` » sur chaque ligne de portée ; hors portée, seule une `bp` présente sur une variable non-IPC (ou absente sur une ligne IPC où l'autre est présente) est comptée comme anomalie.
12. **Contrôle 5.** Pour les séries quotidiennes (`DPRIME`, `DTB3`), seul l'année-mois du jour est contrôlé (pas de contrôle « jour ≥ 28 », non demandé). Pour les mensuelles, le jour est 01.

## D. Faits relevés pendant l'exécution
1. Les trois fichiers de la Fed ont exactement les tailles et sha256 de la section 3.1. Dernier mois FRED : octobre 2026 pour `CPIAUCNS`, `CPIAUCSL`, `UNRATE`. Aucun sha256 de la Fed ne diffère : pas d'enquête de décembre 2026 ajoutée.
2. Comptes de lignes : 555 / 552 complètes / 548 principales, par variable 158/156/156, 129/128/124, 89/89/89, 67/67/67, 112/112/112 : identiques à la préinscription. Épisodes (lignes principales) E1 5, E2 4, E3 4, E4 4, E5 13, E6 15, E7 28, E8 12, E9 20, E10 30, E11 36 ; hors épisode 377 : identiques.
3. Contrôles de schéma sur le fichier écrit : zéro violation ; zéro anomalie hors lignes principales (contrôles 3 à 8 sur les cellules présentes).
4. `FRED_USREC.csv` et `FRED_USRECP.csv` ont été téléchargés (la préinscription les nomme) mais ne servent pas au calcul : les fenêtres d'épisode sont celles du tableau de la section 6. ALFRED n'a pas été utilisé (la préinscription écarte le premier millésime).
5. Les cellules `#N/A` ont été lues comme manquantes (`pd.to_numeric(..., errors="coerce")`) ; les réponses individuelles de même.
6. Contrôle croisé (statsmodels, `hac-groupsum`, 2 retards) : c, et_c_dk2, b_regroupe, et_b_regroupe_dk2 et et_c_iid identiques à 6 décimales (`controle_croise_sortie.txt`).
