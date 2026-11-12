# Tests de mort — protocole figé avant toute préinscription

## Fiches testées
Les six fiches vérifiées ont reçu le verdict « variante » ; aucune ne tombe. Selon la règle scellée (`nouveaute/regle.md`),
les trois premières de l'agrégat vont aux tests : **F01, F04, F12**. Réserve, dans l'ordre : F11, F13, F16 — une réserve
n'est jouée que si une fiche testée finit « non concluante » pour une raison de données.

## Trois rôles séparés par fiche
1. **Rédacteur de préinscription** — lit la fiche, les failles relevées par les juges et la note de nouveauté ; écrit
   `tests-de-mort/<ID>/preenregistrement.md` : données exactes, schéma du fichier d'analyse, statistique, seuil, règle de verdict.
   Il peut amender le test de la fiche pour répondre aux failles, en le déclarant. Il ne lance aucune analyse.
   L'orchestrateur scelle le texte (sha256) ; plus rien n'y change ensuite.
2. **Expérimentateur** — session neuve. Télécharge les données, construit le fichier d'analyse nommé par la préinscription,
   écrit son script, calcule la statistique. Ce qu'il imprime n'est qu'un témoin.
3. **Vérificateur** — session neuve, autre modèle. Ne lit ni le script ni les chiffres de l'expérimentateur : il recalcule la
   statistique à partir du fichier d'analyse et de la seule préinscription, et écrit `verification.json`.

## Verdict
Calculé par le code de l'orchestrateur (`tests-de-mort/verdict.py`) à partir de `verification.json` et du seuil de la préinscription :
- **survit** ou **éliminée**, selon la règle écrite dans la préinscription, appliquée au chiffre du vérificateur ;
- **non concluant** si une donnée nommée manque, si l'échantillon est sous le minimum préinscrit, si le fichier d'analyse viole
  son schéma, ou si l'expérimentateur et le vérificateur diffèrent de plus que la tolérance préinscrite.
Aucun agent n'écrit le verdict. Toute déviation à la préinscription est écrite dans `ecarts.md` avec sa raison.
