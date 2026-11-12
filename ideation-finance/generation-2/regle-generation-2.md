# Génération 2 — règle figée le 12 novembre 2026, avant les verdicts de H13 et H03

## Sélection (ce qui passe d'une génération à l'autre)
- Sont **parents** les fiches dont le verdict, calculé par l'orchestrateur (`tests-de-mort/*/verdict.json`), est « survit »,
  dans les deux courses de la génération 1. Une fiche « non concluante » ou « éliminée » n'est pas parent.
- À l'heure où cette règle est écrite : F04 survit ; F01, F12 et F04-bis sont non concluantes ; H16 est éliminée ; H13 et H03
  ne sont pas jugées. Les proposeurs de la génération 2 ne sont lancés qu'après ces deux verdicts.

## Ce qui est servi aux proposeurs
- Pour chaque parent : sa fiche, sa préinscription résumée, ses résultats chiffrés (statistique, erreur type, effectifs,
  dispersion mesurée), ses limites écrites, et ce que les lectures exploratoires ont montré, marqué comme exploratoire.
- Le **registre des résultats** de toutes les fiches testées : titre, verdict, résultat en une ligne. Ce sont des faits mesurés
  sur des données, pas des goûts.
- La liste des 35 titres déjà proposés, à ne pas reprendre.
- **Ne sont jamais servis** : les classements, notes et failles des juges des deux courses (la mémoire ne sert pas le goût des
  juges aux proposeurs), ni la famille d'origine d'une fiche.

## Ce que les proposeurs rendent
Trois familles (Kimi, Gemini, Claude), même consigne, sans outils, cinq fiches chacune :
- au moins **trois fiches filles** d'un parent. Une fille doit changer au moins un de ces quatre éléments et dire lequel :
  la statistique, l'échantillon ou le marché, la source de données, l'identification. Une fille qui reformule son parent sans
  rien changer de ces quatre éléments est refusée avant le jugement (contrôle de forme par l'orchestrateur, sur le champ
  « Parent et différence ») ;
- au plus **deux fiches libres**, qui doivent citer le résultat du registre qui les motive.

## Jugement, nouveauté, tests
- Trois juges (Kimi, Gemini, Claude), même consigne, fiches anonymes, grille de la course 2 avec un axe de plus,
  « apport » (ce que la fiche ajoute à ce qui est déjà mesuré : 1 = redite du parent, 5 = tranche une question que le parent a ouverte).
  Agrégation par somme des rangs, code scellé avant la lecture des fiches.
- Vérification de nouveauté et de données sur les fiches retenues, puis tests de mort sur les trois premières encore debout,
  selon `tests-de-mort/protocole.md`. Verdict par `tests-de-mort/verdict.py`.
