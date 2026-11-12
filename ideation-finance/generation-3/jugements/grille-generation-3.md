# Génération 3 — grille des juges et règle d'agrégation, figées avant la lecture de toute fiche de la génération 3

## Ce qui est jugé
Un lot anonyme de vingt fiches (cinq par proposeur : Kimi, Gemini, Astra, Claude), sous identifiants opaques K01…K20, dans un ordre
tiré par une graine dérivée du sha256 des fichiers de fiches. Le juge ne sait pas quelle famille a écrit une fiche. Il reçoit
aussi le **registre des résultats** que les proposeurs ont reçu (faits mesurés sur les fiches déjà testées), pour pouvoir juger
ce qu'une fiche ajoute. Il ne reçoit aucun classement ni aucune note d'un juge précédent.

## Les juges
Quatre juges de familles différentes — Kimi, Gemini, Astra, Claude — reçoivent exactement la même consigne. Aucun ne voit les autres.

## Critère de choix
Ce qui parle le plus au jury d'admission d'un master de recherche en économie et finance quantitatives **et** aux recruteurs de
stage, pour un étudiant dont les centres d'intérêt sont, par ordre : économie monétaire, banque centrale, macroéconomie, puis
finance de marché, et dont les projets existants portent sur les actions.

## Axes (note entière de 1 à 5)
1. **jury** — question claire, identification honnête.
2. **recruteurs** — sujet reconnaissable, résultat en deux phrases.
3. **tuable** — le test peut vraiment éliminer l'idée, avec assez d'observations indépendantes pour trancher.
4. **interet** — adéquation aux centres d'intérêt et apport au profil.
5. **nouveaute** — d'après ce que le juge sait de la littérature.
6. **apport** — ce que la fiche ajoute à ce qui est déjà mesuré dans le registre. 1 = redite d'un résultat du registre ;
   3 = prolongement utile ; 5 = tranche une question qu'un résultat du registre a ouverte.

## Contraintes de forme
- Classement complet du rang 1 au rang 20, sans ex æquo.
- Mention : au plus **5** « à retenir », au moins **8** « à écarter », le reste « possible ».
- Pour chaque fiche, la **faille la plus grave** en une phrase.

## Sortie
Uniquement un tableau JSON de 20 objets, sans texte autour :
`{"id": "K07", "rang": 1, "mention": "à retenir", "jury": 5, "recruteurs": 4, "tuable": 5, "interet": 4, "nouveaute": 3, "apport": 4, "faille": "..."}`

## Agrégation (code de l'orchestrateur, `jugements/agreger_generation_3.py`)
Somme des rangs des quatre juges (Borda), départage par jury + recruteurs puis identifiant. Une fiche « à écarter » pour deux
juges ou plus sort des retenues. Les **cinq** premières sont retenues. Sont rapportés : le classement, l'accord entre juges, le
rang moyen par famille de proposeur, et le rang que chaque juge donne aux fiches de sa propre famille et à celles des autres.
