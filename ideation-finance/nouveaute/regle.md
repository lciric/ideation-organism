# Vérification de nouveauté — règle figée avant toute recherche

Fiches vérifiées : F01, F04, F12, F11, F13, F16 (sortie de `jugements/agregat.json`).

Le vérificateur cherche (web, arXiv, SSRN, NBER, documents de travail des banques centrales) les travaux les plus proches
et rend, par fiche, un fichier `nouveaute/<ID>.md` avec :
- les 3 à 6 travaux les plus proches, chacun avec auteurs, année, titre, **adresse ouverte et vérifiée**, et une phrase sur ce qu'il fait ;
- ce que la fiche ajoute réellement une fois ces travaux lus ;
- un **verdict** parmi trois, sur la première ligne du fichier :
  - `VERDICT: déjà fait` — la même question a reçu une réponse, sur un échantillon qui couvre celui de la fiche, avec une méthode équivalente ;
  - `VERDICT: variante` — la question est traitée, mais la fiche change l'échantillon, la période ou la méthode d'une manière qui peut changer la réponse ;
  - `VERDICT: ouvert` — aucun travail trouvé ne répond à la question ; c'est une **question**, pas une preuve d'absence.
- une ligne `CORRECTIONS:` listant toute référence de la fiche qui se révèle fausse ou mal attribuée.

Règle de l'orchestrateur : une fiche « déjà fait » tombe. Parmi les fiches restantes, dans l'ordre de l'agrégat, les **3** premières
vont aux tests de mort. Le vérificateur ne classe pas les fiches et ne lance aucune analyse de données.
