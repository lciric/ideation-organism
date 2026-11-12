# Grille des juges et règle d'agrégation — figées avant la lecture de toute fiche

## Ce que chaque juge reçoit
Le brief (`brief.md`) et le fichier `jugements/fiches-anonymes.md` : toutes les fiches, sous identifiants opaques F01…Fnn,
dans un ordre tiré par une graine dérivée du sha256 des fichiers de fiches. Un juge ne voit ni les autres juges, ni leurs notes,
ni l'identité du proposeur. Un juge ne modifie aucune fiche et ne lance aucune analyse.

## Axes (note entière de 1 à 5, ancres obligatoires)
1. **Jury** — un économètre du comité d'admission y voit-il une question claire et une identification honnête ?
   1 = corrélation habillée, ou résultat connu d'avance ; 3 = correct mais scolaire ; 5 = il poserait des questions par intérêt, pas par doute.
2. **Recruteurs** — un recruteur de stage (banque, gestion d'actifs, recherche quantitative, banque centrale, recherche économique)
   comprend-il le sujet en deux phrases et y reconnaît-il son métier ?
   1 = illisible hors du milieu universitaire ; 3 = compréhensible, sans accroche ; 5 = il en parle pendant l'entretien.
3. **Tuable et faisable** — le test de mort peut-il vraiment éliminer l'idée, avec des données vérifiées, en 4 à 6 semaines ?
   1 = infalsifiable ou données douteuses ; 3 = faisable mais le seuil est mou ; 5 = prédiction chiffrée, seuil net, données en main.
4. **Usage de l'IA** — l'IA fait-elle un travail réel, sous une garde qui l'empêche de se noter elle-même ?
   1 = décor ; 3 = assistant de code ; 5 = l'IA est indispensable au projet et la garde est le cœur de la méthode.
5. **Nouveauté présumée** — d'après ce que le juge sait de la littérature (sera vérifié ensuite, séparément).
   1 = fait cent fois ; 3 = variante d'un travail connu ; 5 = le juge ne connaît pas d'équivalent.

## Contraintes de forme (contre le plafond observé dans la deuxième course réelle de l'organisme)
- **Classement complet obligatoire**, du rang 1 au rang n, sans ex æquo.
- Mention : au plus **4** fiches « à retenir », au moins **8** fiches « à écarter », le reste « possible ».
- Pour chaque fiche : la **faille la plus grave** en une phrase (obligatoire, même pour la première).

## Sortie
Un fichier `jugements/juge-<n>.json` : liste d'objets
`{"id": "F07", "rang": 1, "mention": "à retenir", "jury": 5, "recruteurs": 4, "tuable": 5, "ia": 4, "nouveaute": 3, "faille": "..."}`.

## Règle d'agrégation (calculée par le code de l'orchestrateur, pas par un juge)
- Score d'une fiche = somme de ses rangs chez les trois juges (méthode de Borda, le plus petit gagne) ;
  départage par la somme des notes « jury » + « recruteurs », puis par l'identifiant.
- Les **6** premières vont à la vérification de nouveauté. Une fiche classée « à écarter » par deux juges ou plus est retirée
  de ces 6 et remplacée par la suivante.
- Après la nouveauté, les **3** premières encore debout vont aux tests de mort.
