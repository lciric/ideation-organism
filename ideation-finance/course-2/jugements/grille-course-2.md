# Course 2 — grille des juges et règle d'agrégation, figées avant la lecture de toute fiche de la course 2

## Ce qui est jugé
Un seul lot anonyme, `jugements/fiches-anonymes-course-2.md` : les quinze fiches de la course 2 (cinq par proposeur : Kimi,
Gemini, Claude) et les six fiches retenues de la course 1, sous identifiants opaques H01…H21, dans un ordre tiré par une graine
dérivée du sha256 des fichiers de fiches. Le juge ne sait ni quelle famille a écrit une fiche, ni de quelle course elle vient,
ni ce que la course 1 en a dit, ni si elle a été testée. Les fiches de la course 1 n'ont pas le champ « Arithmétique de
puissance » : son absence ne doit pas être pénalisée en soi.

## Les juges
Trois juges de familles différentes — Kimi, Gemini, Claude — reçoivent **exactement la même consigne**. Aucun ne voit les
autres. Aucun ne modifie une fiche ni ne lance d'analyse.

## Critère de choix
Ce qui parle le plus au jury d'admission d'un master de recherche en économie et finance quantitatives **et** aux recruteurs de
stage, pour un étudiant dont les centres d'intérêt sont, par ordre : économie monétaire, banque centrale, macroéconomie, puis
finance de marché, et dont les projets existants portent sur les actions.

## Axes (note entière de 1 à 5)
1. **jury** — question claire, identification honnête. 1 = corrélation habillée ou résultat connu d'avance ; 5 = un économètre poserait des questions par intérêt, pas par doute.
2. **recruteurs** — sujet reconnaissable, résultat en deux phrases. 1 = illisible hors de l'université ; 5 = on en parle en entretien.
3. **tuable** — le test peut vraiment éliminer l'idée, avec assez d'observations indépendantes pour trancher. 1 = infalsifiable ou sans puissance ; 5 = seuil net, puissance suffisante.
4. **interet** — adéquation aux centres d'intérêt et apport au profil. 1 = hors sujet ou redite des projets actions ; 5 = cœur monétaire ou banque centrale.
5. **nouveaute** — d'après ce que le juge sait de la littérature. 1 = fait cent fois ; 5 = pas d'équivalent connu.

## Contraintes de forme
- Classement complet du rang 1 au rang 21, sans ex æquo.
- Mention : au plus **5** « à retenir », au moins **8** « à écarter », le reste « possible ».
- Pour chaque fiche, la **faille la plus grave** en une phrase.

## Sortie
Uniquement un tableau JSON de 21 objets, sans texte autour :
`{"id": "H07", "rang": 1, "mention": "à retenir", "jury": 5, "recruteurs": 4, "tuable": 5, "interet": 4, "nouveaute": 3, "faille": "..."}`

## Agrégation (code de l'orchestrateur, `jugements/agreger_course_2.py`)
Somme des rangs des trois juges (Borda), départage par jury + recruteurs puis identifiant. Une fiche « à écarter » pour deux
juges ou plus sort des retenues. Sont rapportés : le classement, l'accord entre juges, le rang moyen des fiches selon la
famille du proposeur, le rang que chaque juge donne aux fiches de sa propre famille et à celles des autres, et la place des
six fiches de la course 1 dans le nouveau classement.
