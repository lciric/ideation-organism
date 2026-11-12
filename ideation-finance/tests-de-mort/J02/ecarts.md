# J02 — Écarts à la préinscription (expérimentateur)

**Affirmations factuelles de la préinscription sur les données : aucune n'a été trouvée fausse.** Vérifié sur les fichiers
téléchargés le 2026-11-12 : 111 millésimes `Q.U2.HIC.A` dans la liste des clés MPD (les 109 de la liste figée, plus `G26`
et `S26`) ; colonne `TITLE` vide, nom de l'exercice dans `TITLE_COMPL` ; `W99` a 12 lignes, premier trimestre `F` 1999-Q1,
dernier trimestre 2000-Q4 ; dans les 109 millésimes, le premier trimestre `F` est le trimestre de l'exercice (contrôle 6) ;
Eurostat `prc_hicp_minr` `M.I15.TOTAL.EA` : colonnes annoncées, 369 mois de 1996-01 à 2026-09, aucun vide, mise à jour du
04/11/26 ; 108 cibles complètes, comme annoncé.

Trois écarts, tous sans effet sur le fichier d'analyse et sur les chiffres.

## É1 — Règle d'essai pour Eurostat

La section 4 fixe la règle d'essai (10 essais, 120 s, 10 s d'attente) pour la MPD seulement. **Fait :** la même règle a
été appliquée au fichier Eurostat (premier HTTP 200 avec un en-tête contenant `TIME_PERIOD`, `OBS_VALUE`, `OBS_FLAG`).
**Raison :** aucune règle n'est écrite ; reprendre celle de la MPD est la lecture la plus proche du texte. **Effet :** nul,
le fichier a été reçu au premier essai.

## É2 — Date et code HTTP écrits d'abord dans un journal de téléchargement

La section 4 demande sha256, date et code HTTP dans `construire_journal.json`. **Fait :** le téléchargement est fait par
un script séparé, `telecharger.py`, qui écrit date, code HTTP, historique des essais et sha256 dans
`telecharger_journal.json` ; `construire.py` recalcule les sha256 depuis `donnees/` et recopie date et code HTTP dans
`construire_journal.json`, qui contient donc bien les trois informations pour chaque fichier. **Raison :** la consigne de
l'orchestrateur demande que `construire.py` reconstruise le fichier d'analyse à partir de `donnees/` seul, sans réseau.
**Effet :** nul. (Exception : la liste des clés MPD, téléchargée par `curl` pour contrôle, a sa date et son code HTTP dans
`donnees/PROVENANCE.md` et non dans le journal ; ce fichier n'entre pas dans le fichier d'analyse.)

## É3 — Aveuglement : contact avec le dossier `H03-v2`

La section 2 interdit d'ouvrir **aucun** fichier de `tests-de-mort/H03-v2` et demande d'écrire ici tout manquement.
**Fait :** au début du travail, avant d'avoir lu la préinscription, j'ai **listé les noms** des fichiers de
`tests-de-mort/H03-v2/` et de `tests-de-mort/H03-v2/donnees/` (commande `ls`), parce que la consigne de l'orchestrateur
proposait d'y reprendre les fichiers bruts MPD. **Aucun fichier de ce dossier n'a été ouvert, lu ni copié** ; tous les
fichiers bruts de J02 ont été retéléchargés depuis les API (voir `donnees/PROVENANCE.md`). Entre l'autorisation de
réutilisation de l'orchestrateur et la règle d'aveuglement de la préinscription, j'ai suivi la préinscription.
Pour mémoire aussi : les cinq premières lignes (docstring et imports) de `tests-de-mort/verdict.py` ont été affichées en
même temps que le contrôle du sceau ; le reste n'a pas été lu. Ce fichier n'est pas interdit par la préinscription.
**Effet :** nul sur les données et les calculs.

## Lectures retenues là où le texte laissait un choix (pas des écarts)

- `annee_titre` : « année à quatre chiffres lue dans `TITLE_COMPL` » ; le code prend la dernière si plusieurs. Sur les
  données, chaque titre n'en contient qu'une : aucune différence possible.
- `mois_titre` : dernier nom de mois anglais complet, mots entiers. Les titres de G25, S25, A25 et W26 commencent par un
  nom de saison (« Spring/June 2025 », etc.) ; les saisons ne sont pas des mois ; le mois lu est June, September, December,
  March, conforme à la lettre.
- Bootstrap : un appel `rng.integers(0, n − 7, size=k)` par tirage, dans l'ordre des tirages ; remplacement d'un tirage à
  variable constante par le tirage suivant du même générateur (aucun cas sur 9 999).
- Écriture : projections et indices recopiés tels que publiés (chaîne du fichier brut) ; `realise` et `erreur` à 12
  décimales, `revision` à 10 décimales.
- Fichiers produits en plus de ceux que nomme la préinscription (`telecharger.py`, `telecharger_journal.json`,
  `controles_schema.py`, `analyse_detail.json`, `donnees/MPD_cles_serieskeysonly.csv`) : sans effet sur les calculs.
