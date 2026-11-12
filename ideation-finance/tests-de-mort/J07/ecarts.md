# J07 — Écarts à la préinscription (expérimentateur)

**Affirmations factuelles de la préinscription sur les données : aucune ne s'est révélée fausse.** 438 dates de millésime
(première 1989-12-08), 3 corrections (2002-12-09, 2003-10-10, 2020-05-11), 435 publications dont 431 datées de 1990 à 2025,
ligne de contrôle du 1990-02-02 (A1 = 275, v3 = 1990-04-06, A3 = 361, N = −86), aucune ligne `complet` = 0, une seule
publication double (2025-12-16) : tout est conforme. Deux constats mineurs, qui ne sont pas des écarts, sont notés en fin de
fichier (première prévision en 1997 et non « vers 1996 » ; « troisième estimation » de septembre 2025).

## Écarts

### É1. Emplacement des fichiers bruts : `J07/donnees/` au lieu de `J07/brut/`
- Préinscription (section 4) : « L'expérimentateur enregistre chaque fichier brut dans `tests-de-mort/J07/brut/` ».
- Fait : les fichiers bruts sont dans `J07/donnees/` (avec `PROVENANCE.md`), parce que la consigne de livraison de
  l'orchestrateur exige `donnees/` et que `construire.py` doit tout reconstruire depuis `donnees/` seul. Pour respecter aussi
  le texte scellé, `J07/brut` est un lien symbolique vers `donnees/` : les mêmes fichiers sont accessibles aux deux chemins.
- Effet sur les chiffres : aucun.

## Ambiguïtés tranchées par la lecture la plus littérale (avec l'autre lecture quand elle est calculable)

### A1. Publications « de révision large » : seules les publications comptent comme w
- Étape 4 : « Une publication w est de révision large si… ». Lecture littérale retenue : w parcourt les publications
  seulement ; les trois millésimes de correction ne sont pas des w.
- Autre lecture (les corrections comptent aussi, comparées au millésime qui les précède) : 2002-12-09 ne modifie que
  septembre 2002 et 2020-05-11 que février-avril 2020, et les seules lignes dont la fenêtre [date(v), date(v3)] contient ces
  dates ont déjà `revision_large` = 1 ; 2003-10-10 ne modifie que des mois de 1958 à 1989, hors de la fenêtre m′ − 11 … m′ − 2.
  **Les deux lectures donnent exactement le même fichier et les mêmes chiffres.**

### A2. S3 : erreurs types Newey-West sans correction de petit échantillon
- S3 dit « erreurs types Newey-West (Bartlett, 4 retards) » sans préciser la correction. Retenu : sans correction
  (`use_correction=False`), par cohérence avec l'amendement B7 de la statistique principale.
- Autre lecture (avec correction n/(n − k)) : erreurs types 3,752 (constante), 0,02830 (x1), 0,08864 (x2) au lieu de
  3,734 ; 0,02816 ; 0,08821 ; t de x2 = −2,281 au lieu de −2,292. Descriptif seulement.

### A3. S3 : « écart-type de y »
- Rapporté avec le dénominateur n − 1 (58,534) ; avec n : 58,439.

## Ce qui n'est pas un écart, mais est noté
- **Aucun fichier du dossier `H13/` n'a été copié, ouvert ni lu.** L'orchestrateur permettait de copier les millésimes bruts
  de H13 ; la préinscription (section 4, amendement B4) l'interdit. Le texte scellé l'emporte : les 438 millésimes ont été
  retéléchargés (37 requêtes groupées, toutes réussies au premier essai).
- `temoin.json` ne contient que les huit champs de vérification, sans clé `descriptif` (facultative selon la section 6) ;
  S1 à S3 sont dans `analyse_resultats.json`.
- Fichiers produits en plus de ceux que nomme la préinscription : `telecharger.py`, `journal_telechargement.csv`,
  `construire_controles.json`, `analyse_resultats.json`, `previsions.csv`. Ils ne changent aucun calcul.
- `date_info_predicteurs` est calculé comme la plus récente des dates des colonnes `PAYEMS_AAAAMMJJ` lues (v pour A1, R1, R2 ;
  prec(v) pour T et pour R1, R2) : c'est toujours `date_publication`.
- Contrôle `statsmodels` de la statistique principale : 1,871964402071882 (formule) contre 1,8719644020718824
  (`statsmodels`) : identiques.

## Constats sur les données (pas des écarts)
1. **Première prévision le 1997-02-07**, pas « vers 1996 » (section 6, attendu indicatif). P = 248 exactement comme attendu.
   La phrase type de la section 11 (« de 1996 à 2025 ») devrait donc lire « de 1997 à 2025 ».
2. **Septembre 2025** (publication du 2025-11-20, admissible, dernière prévision) : la règle mécanique donne v3 = 2025-12-16
   (première publication avec fin ≥ novembre 2025), soit la **deuxième** publication après v, à 26 jours, et non une
   publication « environ deux mois plus tard ». À cause de la fermeture de l'administration fédérale à l'automne 2025, la
   valeur de septembre lue le 2025-12-16 (+108) est en pratique sa deuxième et dernière estimation mensuelle (inchangée le
   2026-01-09). La règle a été appliquée telle qu'écrite. C'est la seule ligne du fichier où v3 n'est pas la deuxième
   publication suivante. Sa contribution à Σ(e0² − e1²) est de +291 sur un total de +17 945.
