# Course 2 — vérification de nouveauté et des données, règle figée avant toute recherche

Fiches vérifiées : les quatre fiches nouvelles parmi les six retenues de `jugements/agregat-course-2.json` — H13, H16, H15, H07.
(Les deux autres, H03 et H10, sont des fiches de la course 1 déjà vérifiées : `../nouveaute/F13.md` et `../nouveaute/F04.md`.)

Par fiche, un fichier `nouveaute/<ID>.md` dont les trois premières lignes sont :
- `VERDICT: déjà fait` | `VERDICT: variante` | `VERDICT: ouvert` — mêmes définitions que la course 1 (`../nouveaute/regle.md`) ;
- `DONNEES: accessibles` | `DONNEES: partielles` | `DONNEES: manquantes` — les proposeurs de la course 2 n'avaient aucun outil :
  le vérificateur teste lui-même chaque source indispensable au test de mort (code HTTP, premières lignes, présence de la
  variable et de la période nécessaires). « manquantes » = une donnée indispensable au test n'existe pas en accès public ;
  « partielles » = elle existe mais sur une période ou une granularité plus étroite que la fiche ne le suppose (dire laquelle) ;
- `CORRECTIONS:` toute référence, ordre de grandeur « de mémoire » ou nom de série de la fiche qui se révèle faux.

Suivent : les 3 à 6 travaux les plus proches (auteurs, année, titre, adresse ouverte et lue, ce qu'ils font et trouvent) ;
ce que la fiche ajoute réellement ; le détail des tests de données. Le vérificateur ne lance aucune analyse statistique et ne
regarde aucun résultat du test de la fiche.

Règle de l'orchestrateur : une fiche « déjà fait » ou « manquantes » tombe. Parmi les six retenues encore debout, dans l'ordre
de l'agrégat, les **trois** premières non encore testées vont aux tests de mort (protocole de `../tests-de-mort/protocole.md`).
