# Génération 3 — vérification de nouveauté et des données, règle figée avant toute recherche

Fiches vérifiées : les cinq retenues de `jugements/agregat-generation-3.json` — K11, K20, K01, K17, K16.

Mêmes définitions et même format que la course 2 (`../course-2/nouveaute/regle-course-2.md`) : trois premières lignes
`VERDICT: déjà fait | variante | ouvert`, `DONNEES: accessibles | partielles | manquantes`, `CORRECTIONS:` ; puis les 3 à 6
travaux les plus proches (adresse ouverte et lue), ce que la fiche ajoute réellement, le détail des tests de données.

En plus, pour la génération 2 : le vérificateur compare chaque fiche aux **résultats déjà mesurés** du registre (dossier
`../tests-de-mort/`, fichiers `verdict.json` et `preenregistrement.md` seulement) ; une fiche dont le test reproduit, à la
spécification près, un test déjà jugé est « déjà fait », même si la littérature ne l'a pas publié.

Règle de l'orchestrateur : une fiche « déjà fait » ou « manquantes » tombe. Parmi les retenues encore debout, dans l'ordre de
l'agrégat, les **trois** premières vont aux tests de mort (`../tests-de-mort/protocole.md`), verdict par `../tests-de-mort/verdict.py`.

Ajout pour la génération 3 : K17 et K16 posent la même question (révisions sectorielles de l'emploi) ; si le vérificateur les juge
redondantes, seule la mieux classée (K17) peut aller aux tests, et la suivante dans l'ordre de l'agrégat la remplace.
