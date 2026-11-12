# Brief d'idéation — projet de recherche en économie ou finance quantitative, mené avec des agents d'IA

## But
Trouver un projet de recherche empirique **ambitieux mais faisable**, qu'un étudiant de niveau licence (maths/économie,
Python ou R) mène **ouvertement avec des agents d'IA**, et qu'il présentera dans une candidature à un master de recherche
en économie et finance quantitatives (micro, macro, économétrie, séries temporelles ; débouché doctorat ou poste quantitatif).
Le projet doit montrer deux choses à la fois :
1. un vrai résultat empirique (positif ou négatif) sur une question d'économie ou de finance ;
2. une **manière rigoureuse de se servir de l'IA** : l'IA propose et exécute, mais ne note jamais son propre travail.

## Critère de choix (fixé par le commanditaire)
On retient ce qui **parle le plus au jury d'admission** (économistes universitaires : rigueur d'identification, honnêteté
statistique, question claire) **et aux recruteurs de stage** (banque d'investissement, gestion d'actifs, recherche quantitative,
banque centrale, recherche économique, conseil : sujet reconnaissable, résultat qu'on explique en deux phrases, un graphique,
un dépôt de code propre). Une idée brillante mais illisible pour un recruteur, ou vendeuse mais fragile devant un économètre, perd.

## Règle de méthode (reprise de l'organisme d'idéation de ce dépôt)
- Le rôle qui produit un artefact ne détient jamais la clé qui l'évalue.
- Toute prédiction est écrite et scellée (sha256) **avant** que les données qui la jugent soient lues.
- Le verdict d'un test est calculé par un code séparé à partir du fichier brut, jamais par l'agent qui a fait l'expérience.
- Un résultat nul proprement obtenu est un résultat. Une idée qu'on ne peut pas tuer n'est pas une idée.

## Contraintes dures
- **Données publiques et gratuites uniquement**, téléchargeables sans compte. Joignables depuis cette machine (vérifié) :
  FRED (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIE>`), bibliothèque Ken French (Dartmouth),
  portail de données de la BCE (`https://data.ecb.europa.eu/`, API `https://data-api.ecb.europa.eu/service/data/...`), arXiv.
  Non joignables ou limités : Yahoo Finance (429), Stooq (injoignable). Toute autre source doit être **testée par vous avec curl**
  (code HTTP et premières lignes) avant d'être citée dans une fiche. Pas de CRSP, Compustat, Bloomberg, Refinitiv.
- Calcul : un portable, processeur seul. Appels de modèles de langage permis si la fiche chiffre le coût (viser < 30 USD).
- Durée : 4 à 6 semaines à temps partiel pour l'étudiant.
- Méthodes défendables en 30 minutes d'entretien devant des économistes : MCO, panel à effets fixes, projections locales,
  études d'événement, Fama-MacBeth, évaluation de prévisions hors échantillon (Diebold-Mariano, Clark-West), bootstrap,
  correction de tests multiples. Pas d'apprentissage profond opaque comme cœur du résultat.
- À éviter : le « backtest » naïf d'une stratégie qui bat le marché ; une simple réplication sans question nouvelle ;
  un sujet dont le résultat est connu d'avance.

## Format d'une fiche (champs fermés, tous obligatoires, en français)
```
### <ID> — <titre court>
- **Question** : une phrase.
- **Hypothèse falsifiable** : une phrase, avec le sens de l'effet.
- **Prédiction chiffrée** : signe et ordre de grandeur attendus, écrits sans avoir regardé le résultat.
- **Test de mort** : statistique exacte, seuil, échantillon ou fenêtre hors échantillon ; ce qui élimine l'idée.
- **Données** : séries ou fichiers exacts, URL, et le code HTTP que vous avez obtenu en les testant.
- **Méthode** : 3 à 5 lignes.
- **Ce qui serait nouveau** : en quoi cela dépasse ce qui est connu ; travaux les plus proches dont vous vous souvenez,
  chacun marqué « à vérifier » (n'inventez aucune référence : dans le doute, écrivez « référence incertaine »).
- **Rôle de l'IA** : ce que les agents font ; ce que l'humain décide ; la garde qui empêche l'IA de se noter elle-même.
- **Coût et durée** : calcul, appels de modèles en USD, semaines.
- **Risques** : ce qui rendrait le projet sans intérêt même exécuté proprement.
- **Valeur si l'hypothèse meurt** : ce qu'on peut encore écrire.
- **Ce que ça dit au jury et aux recruteurs** : la ligne de CV (une phrase, au passé, sans enjoliver), le graphique unique
  qui résume le projet, et quels métiers de stage y reconnaissent leur travail.
```
