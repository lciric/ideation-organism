# Bilan de la course d'idéation en économie et finance — 12 novembre 2026

Une course complète a été jouée en une journée : 20 fiches proposées, 3 juges, 6 vérifications de nouveauté,
3 tests de mort préinscrits. Résultat : **un test survit, deux sont non concluants, aucune idée n'est éliminée.**
Tout est dans ce dossier, scellé (sha256) à chaque étape avant que l'étape suivante ne lise.

## Ce qui a tourné

| Étape | Qui | Sortie |
|---|---|---|
| Brief et critère de choix | orchestrateur, d'après le commanditaire | `brief.md` |
| Proposition | 4 proposeurs indépendants, 5 fiches chacun | `fiches/` |
| Jugement | 3 juges séparés, sur trois modèles différents, fiches anonymes, classement complet imposé | `jugements/` |
| Agrégation | code de l'orchestrateur, scellé avant le premier jugement (méthode de Borda) | `jugements/agregat.json` |
| Nouveauté | 3 vérificateurs, sources ouvertes et lues | `nouveaute/` |
| Tests de mort | par fiche : un rédacteur de préinscription, un expérimentateur, un vérificateur sur un autre modèle | `tests-de-mort/` |
| Verdict | code de l'orchestrateur, scellé avant les préinscriptions, essayé sur 2 cas sains et 4 artefacts | `tests-de-mort/*/verdict.json` |

Accord entre juges (corrélation de rang de Spearman) : 0,59 à 0,77. Les juges discriminent : pas de plafond.

## Les six premières fiches et leur nouveauté

| Rang | Fiche | Sujet | Nouveauté | Travail le plus proche |
|---|---|---|---|---|
| 1 | F01 | Anomalies publiées : effet de la publication ou tendance commune ? | variante étroite | Xiong et Pelger (2019) contre McLean et Pontiff (2016) |
| 2 | F04 | Adjudications du Trésor américain : pression de prix | variante mince | Fleming, Liu et Nguyen (2026), jusqu'en juillet 2024 |
| 3 | F12 | Instrument de protection de la transmission de la BCE et écarts souverains | variante | Eurosystème (2025), graphique 10 |
| 4 | F11 | Hausse des droits de mutation de 2025, par département | variante ; aucune estimation publiée de l'épisode de 2025 trouvée | Bérard et Trannoy (2018) sur 2014 |
| 5 | F13 | Erreurs de projection d'inflation de la BCE | variante | Chahad et al. (2024) |
| 6 | F16 | Prime des jours d'annonces macroéconomiques | variante | Knox, Londono, Samadi et Vissing-Jorgensen (2025) |

Les cinq fiches centrées sur un modèle de langage sont classées 11e, 16e, 17e, 19e et 20e : les juges y voient
des tests de modèles sans question d'économie assez forte.

## Les trois tests de mort

| Fiche | Statistique préinscrite | Résultat (chiffre du vérificateur) | Verdict |
|---|---|---|---|
| F04 | Pression moyenne V sur les réouvertures à 10, 20 et 30 ans, 2010-2026, erreur type groupée par mois | 0,91 pb ; t = 5,6 ; 321 adjudications ; placebo à J+10 : t = 0,27 | **survit** |
| F12 | Variation de la pente écart souverain / surprise de politique monétaire, avant et après juillet 2022 | −0,35 ; erreur type 0,32 ; intervalle [−0,76 ; +0,07] ; 87 et 26 réunions | **non concluant** |
| F01 | Écart réalisé moins prédit après publication, rapporté au rendement d'origine | −0,06 ; erreur type 0,12 ; intervalle [−0,32 ; +0,19] ; 185 anomalies | **non concluant** |

Dans les trois cas l'expérimentateur et le vérificateur trouvent les mêmes chiffres.

- **F12** : le résultat tient à très peu de réunions (sans le 12 mars 2020, la variation tombe à −0,13 ; après juillet 2022,
  deux réunions portent plus de la moitié de la variance, soit environ six observations effectives). Les données publiques
  ne tranchent pas aujourd'hui.
- **F01** : l'intervalle contient à la fois zéro et la baisse de 30 % prédite, de justesse (borne basse à −0,32).
  Cinq anomalies font basculer l'estimation (sans les cinq plus négatives : +0,02). Une ambiguïté de la préinscription
  (comptage des 60 mois d'origine) a deux lectures ; les deux donnent « non concluant ».

## La piste la plus intéressante (exploratoire)

Découpée par année **après** le verdict, la pression mesurée par F04 est de 1,0 à 2,2 pb par an de 2011 à 2021, puis
proche de zéro de 2022 à 2026 (`tests-de-mort/F04/figure-exploratoire-par-annee.png`). Trois lectures possibles :

1. **Le marché a changé.** La littérature dit déjà que la pression faiblit (Fleming, Liu et Nguyen 2026 : « faiblit nettement »
   en 2015-2024 ; Somogyi, Wallen et Xu 2025 : plus de baisse des rendements après les adjudications depuis 2011).
   Notre mesure, elle, tient jusqu'en 2021 et casse d'un coup.
2. **La mesure a changé.** Le 6 décembre 2021, le Trésor a remplacé la méthode de sa courbe de rendements
   (spline d'Hermite, puis méthode « monotone convexe » ; vérifié sur les deux pages du Trésor). Il dit que l'écart entre
   les deux méthodes est en moyenne de −0,1 à 0,5 pb avec un écart-type de 0,2 à 1,0 pb : c'est la taille de l'effet mesuré.
3. **Le hasard de la découpe.** Elle a été choisie après avoir vu les données.

**Le test qui départage existe et n'a pas été joué.** Le Trésor publie un fichier des deux méthodes côte à côte pour
l'exercice 2021 (octobre 2020 à septembre 2021 ; `fy2021-mc-vs-hs-combined.csv`, joignable, contenu non lu). Sur cette année,
on peut calculer la pression sur les mêmes adjudications avec l'ancienne et la nouvelle méthode. Si elle est là avec l'ancienne
et absente avec la nouvelle, c'est la mesure ; si elle est là avec les deux, c'est le marché. Environ 24 réouvertures :
à préinscrire avant d'ouvrir le fichier.

## Limites de cette course

- **Une seule famille de modèles.** Proposeurs, juges et vérificateurs sont tous des modèles Claude (de modèles différents
  pour les juges et les vérificateurs). L'organisme demande des familles différentes ; les clés existent, elles n'ont pas été utilisées.
- **Le vérificateur ne contrôle que le calcul**, à partir du fichier d'analyse. La construction de ce fichier à partir des
  données brutes n'a été contrôlée que pour F04, par l'orchestrateur (1 926 valeurs identiques aux fichiers bruts ;
  la sélection des 321 adjudications dans la source n'a pas été contrôlée). Pour F01 et F12, elle ne l'a pas été.
- **Le verdict « survit » de F04 porte sur une mesure dont la source change de méthode en cours d'échantillon.**
  La préinscription ne le savait pas. Le chiffre est exact ; son interprétation attend le test ci-dessus.
- **Nouveauté modeste.** Les six fiches sont des variantes de travaux publiés. Aucune n'est une découverte en attente.
- **La réserve (F11) n'a pas été jouée** : les deux « non concluant » viennent d'un manque de puissance, pas d'une donnée manquante.
- **Aucun résultat n'a été relu par un économiste.**

## Recommandation

Selon le critère du commanditaire (ce qui parle au jury et aux recruteurs), **F04, les adjudications du Trésor**, est le
meilleur point de départ : seul test qui tranche, sujet que reconnaît un pupitre de taux, résultat qui tient en deux phrases
et un graphique, et un test décisif court encore à jouer. **F01, les anomalies publiées**, est le second choix : premier chez
les juges, sujet central pour la recherche quantitative en gestion d'actifs, mais sans conclusion à cette taille d'échantillon.

Le projet devient celui de l'étudiant à partir d'ici : c'est lui qui signe la préinscription du test décisif, relance les
trois rôles, lit le verdict et rédige.
