# H03-v2 — Écarts à la préinscription

Écrit par l'expérimentateur le 2026-11-12. Préinscription exécutée : `preenregistrement.md`, sha256
`ca1b83452e562a4bbb9f4ba309bc1b709ce199b2297d03d2a6e3b599930f6d6d` (vérifié avant et après la course ; ni ce fichier ni
son `.sha256` n'ont été modifiés).

## En tête : la préinscription dit-elle quelque chose de faux sur les données ?

**Non : aucune affirmation de fait de la préinscription sur les données ne s'est révélée fausse.** Chaque affirmation
vérifiable a été confrontée aux 111 fichiers bruts et à la liste des clés :

| Affirmation de la préinscription | Constat sur les données téléchargées |
|---|---|
| `W` = mars (T1), `G` = juin (T2), `S` = septembre (T3), `A` = décembre (T4) | vrai pour les 111 millésimes : le mois écrit dans `TITLE_COMPL` vaut 3 × le trimestre tiré de la lettre (28 mars, 28 juin, 28 septembre, 27 décembre), et le premier trimestre de statut `F` est le trimestre du millésime dans les 111 fichiers |
| la colonne `TITLE` existe et elle est vide ; le titre est dans `TITLE_COMPL` | vrai dans les 111 fichiers |
| les six titres du tableau de l'amendement (`W21`, `G21`, `S21`, `A21`, `G25`, `S25`), y compris les deux espaces après l'année en 2025 | conformes, au caractère près |
| 6 206 clés dans la base MPD ; les 111 clés existent ; `A26` peut ne pas exister | 6 206 clés ; 111 clés `MPD.Q.U2.HIC.A.*.0000`, exactement la liste figée ; pas de clé `A26` |
| `W21` : 116 trimestres, 1995-Q1 à 2023-Q4, statut `A` jusqu'à 2020-Q4, `F` de 2021-Q1 à 2023-Q4 | conforme |
| `OBS_VALUE` : une décimale, parfois sans décimale | conforme : 7 712 valeurs à une décimale, 987 sans décimale, aucune à deux décimales ou plus, aucune vide |
| dernier trimestre cible avec valeur réalisée : 2026-Q1, lu dans `S26` | conforme |
| nombres attendus : 111 millésimes, 444 lignes, 15 colonnes, 88 trimestres cibles, 352 lignes évaluées au plus, 11 blocs, numéro maximal 8106 | conformes (352 lignes évaluées, 11 blocs valides de 32 lignes) |

Une seule inexactitude du texte est connue, et elle ne porte pas sur les données : le chiffre illustratif « 1,07 » de la
section 7 (« Protection contre l'épisode unique »), déjà signalé par le rédacteur de la v2 dans « Autres erreurs constatées,
non corrigées ». Refait ici à la main avec les formules de la section 6, étape 5, sans donnée : 1,49 sans correction de
voisinage, 1,13 avec. Ce chiffre n'entre dans aucun champ, aucun seuil ni aucune règle ; il n'a rien changé à l'exécution.

Rien n'a donc été calculé sous une lecture « corrigée » : il n'y en a pas.

## Écarts et lectures retenues

Sept points. **Aucun ne change un nombre du fichier d'analyse ni un champ de `temoin.json`.** Les points 2, 4, 5 et 6 sont
des passages où le texte laisse un choix ; la lecture la plus littérale a été prise, et l'autre lecture donne ici les
mêmes nombres.

| N° | Passage de la préinscription | Ce qui a été fait | Raison | Effet sur les nombres |
|---|---|---|---|---|
| 1 | Section 4, « Téléchargement » : le journal s'appelle `construire_journal.json`, ce qui suggère un seul script qui télécharge et construit | Deux scripts : `telecharger.py` télécharge et écrit `construire_journal.json` (sha256, date, code HTTP, essais) ; `construire.py` ne fait aucune requête, reconstruit le fichier d'analyse à partir de `donnees/` seul et ajoute au même journal une rubrique « construction » (comptes, contrôles). Il compare au passage le sha256 de chaque fichier brut à celui du journal | la consigne de course demande un `construire.py` qui reconstruit à partir de `donnees/` seul | aucun |
| 2 | Section 4 : « une ligne d'en-tête conforme » — « conforme » n'est pas défini | Lecture retenue : la première ligne contient les cinq colonnes que la préinscription dit utiles (`KEY`, `TIME_PERIOD`, `OBS_VALUE`, `OBS_STATUS`, `TITLE_COMPL`) | lecture la plus littérale du mot « utiles » | aucun : les 111 fichiers ont été reçus au premier essai avec HTTP 200 et ont tous exactement la même ligne d'en-tête (32 colonnes) ; toute autre définition raisonnable garde les mêmes fichiers |
| 3 | Section 4 : seuls les 111 fichiers de séries sont nommés sous `donnees/` | Un fichier brut de plus est gardé : `donnees/MPD_serieskeysonly.csv` (la liste des clés que la préinscription donne « pour contrôle »), avec sa ligne dans `PROVENANCE.md` et dans le journal. `donnees/PROVENANCE.md` est aussi dans ce dossier (demandé par la consigne de course) | garder la trace du contrôle des 111 clés et de l'absence de `A26` | aucun : `construire.py` ne lit pas ce fichier |
| 4 | Section 5, colonne `mois_titre` : « mois lu dans `TITLE_COMPL` (nom de mois anglais → 1 à 12) » — la règle ne dit pas quoi faire si le titre contient plusieurs noms de mois, ni où chercher | Lecture retenue : nom de mois anglais cherché comme mot entier dans tout le texte de `TITLE_COMPL` ; le script s'arrêterait s'il en trouvait deux différents | lecture la plus littérale | aucun : chacun des 111 titres contient exactement un nom de mois. Depuis 2025 il est précédé d'une saison (« Winter/March », « Spring/June », « Summer/September », « Autumn/December ») ; « prendre le dernier nom de mois du titre » donne les mêmes 111 valeurs |
| 5 | Section 5 : `projection`, `projection_precedente`, `realise` « une décimale » ; section 4 : `OBS_VALUE` « parfois écrit sans décimale » | Toutes les valeurs sont écrites avec une décimale dans le fichier d'analyse (« 2 » dans la source devient « 2.0 ») ; `revision` et `erreur` sont calculées en arithmétique décimale exacte sur les textes de la source, puis arrondies à une décimale (arrondi sans effet, les entrées ayant au plus une décimale) ; un zéro n'est jamais écrit « -0.0 » | le schéma demande une décimale ; recopier « 2 » tel quel aurait aussi passé le contrôle n° 6 | aucun : mêmes valeurs numériques dans les deux lectures |
| 6 | Section 6, S2 : `r_moyen_h1` à `r_moyen_h4`, « bloc retenu s'il a au moins 4 telles lignes et des sommes de carrés > 10⁻¹² » — le texte ne dit pas si le bloc doit en plus être « valide » au sens de l'étape 3 | Lecture retenue : le critère par horizon seul (au moins 4 lignes évaluées de l'horizon h dans le bloc, sommes de carrés > 10⁻¹²) | lecture la plus littérale | aucun : les 11 blocs sont valides et ont chacun 8 lignes par horizon ; les deux lectures donnent les mêmes quatre nombres |
| 7 | Section 4 : « on garde le premier fichier reçu avec HTTP 200 » | Avant de lancer `telecharger.py`, une requête d'essai a été faite sur `W21` pour vérifier que l'API répondait (HTTP 200, écrite hors du dossier de travail). Le fichier `W21` gardé dans `donnees/` est celui reçu ensuite par `telecharger.py` : c'est donc la deuxième réponse HTTP 200 reçue pour ce millésime, pas la première | test de connexion fait avant d'écrire le script | aucun : les deux réponses sont identiques à l'octet près (même sha256 `c665a998…681a61`) |

## Ce qui n'est pas un écart, pour mémoire

- **Aveugle respecté.** Rien n'a été ouvert dans `tests-de-mort/H03/` (ni script, ni fichier d'analyse, ni rapport, ni
  résultat, ni données). L'exception permise (copier les fichiers bruts de `H03/donnees/`) n'a pas été utilisée : les 111
  séries ont été téléchargées à neuf. Aucune autre fiche, aucun jugement, aucun autre test n'a été lu.
- **Règle de reprise.** Jamais sollicitée : 112 requêtes (111 séries + la liste des clés), 112 réponses HTTP 200 au premier
  essai, entre 19:21:41 et 19:31:25 UTC le 2026-11-12, avec 1,5 seconde de pause entre deux requêtes.
- **Repli de la valeur réalisée** (millésime q + 3, puis q + 4). Jamais sollicité : les 426 valeurs réalisées présentes sont
  toutes lues au numéro cible + 2.
- **Conventions de repli** (K < 5, n < 8, V ≤ 0, G + P = 0, aucun bloc par horizon). Aucune n'a joué.
- **Quantile de Student.** Celui du tableau de la préinscription pour K = 11 (1,8125), pour la statistique principale comme
  pour le placebo.
- **Fichiers en plus de ceux demandés**, tous dérivés et sans effet sur le témoin : `controles_schema.py` (les 11 contrôles,
  utilisés par les deux scripts), `analyse_detail.json` (détail par bloc), `lignes_evaluees.csv` (les 352 lignes évaluées
  avec n_A, S_rr, b, c et le bloc).
