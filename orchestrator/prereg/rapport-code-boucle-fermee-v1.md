# Rapport de code — boucle fermée entre générations (tâche A2, partie code) et bras de référence (A4), v1

2 novembre 2026. Processeur seul, aucun réseau, aucun appel de modèle, aucune clé, aucun commit, aucun `.sha256` posé à côté des
fichiers neufs (le journal du mode à blanc est scellé dans sa sortie, hors de l'arbre). Python 3.13 du système, numpy 2.5.3.

**Verdict.** La flèche « sélection → génération suivante » est fermée dans le code v59 : la génération g+1 lit le bilan scellé de
la génération g, puis la sélection, les cartes et les verdicts du noyau qu'il nomme, chacun vérifié (sceau et empreinte consignée)
avant lecture ; refus net sinon. Le mode à blanc a joué deux générations par bras **dans le vrai bac à sable** (`bwrap` 0.9.0,
identité sans privilège 64097), code de sortie 0. Essais v59 : 28 réussis (28 sous-essais) ; essais existants rejoués : 107 réussis
(182 sous-essais) ; banc de mutations v59 : 9 sur 9 tuées pour la raison attendue.

## 1. Fichiers neufs (suffixe `_v59`, premier libre : aucun fichier `*v59*` n'existait)

| fichier (sous `orchestrator/`) | sha256 |
|---|---|
| `pole/boucle_fermee_v59.py` | `a2de486592fc98c14e13bb9071d272fb65d4f49de38dd188ee64857698177681` |
| `pole/a_blanc_v59.py` | `606aa8b4fcc38786b38cf2954da46533eed9384232a56100d22ff30b8ce0826c` |
| `pole/proposeurs_references_v59.py` | `7d00371a8fcfa3efc2c17b2f0ab33d18ef83b41f3988744ea12dcf823806f68f` |
| `pole/course2_v59.py` | `b5a19a479bba806acb71f6ba49e238b79c717c5423d8ea17a5921c57eae82262` |
| `pole/ideation_v59.py` | `069f920aaf8345309cb59e41354be7c566b68f86ae23cd9864ee34cef5833169` |
| `demonstrations/mode_a_blanc_v59.py` | `3f0f8de0b26d0f4d9807b3ce363c3f3c0a50914af6dcadb5492acad2cd98a4b0` |
| `demonstrations/ideation_v59.py` | `5419137ca0bb910b0c057a7ab1a19cd409d7c5c643bf485b6f3f9c0588523eef` |
| `essais/test_v59_boucle_fermee.py` | `ffaad449020249de43677f5fbd4ebc18a2702d5a54f4260e59de72137088b21f` |
| `essais/mutations_v59.py` | `2594f5fb0cbe89121c84e494012292dc26f9ee4031d4a556502acf593200dcce` |

Aucun fichier existant modifié (`git status` : seuls ces neuf fichiers et ce rapport, non suivis). Les `.sha256` compagnons et le
commit restent à faire par la session qui intègre (consigne de la tâche).

## 2. Ce qui change par rapport aux v57 (et pourquoi)

- **Lecture de la sélection** (`boucle_fermee_v59.lire_heritage`) : en v57b la sélection était écrite et scellée, jamais lue.
  En v59, chaque génération scelle un bilan (`bilan-generation-v59.json`) qui nomme, avec leurs empreintes, la sélection v57, ses
  cartes (lois comprises) et le `verdict-noyau-v5.json` de chaque carte testée. La génération suivante reçoit **l'empreinte du
  bilan** de l'orchestrateur et lit chaque fichier une fois, en octets : fichier régulier (aucun lien suivi), sceau compagnon
  juste, empreinte égale à celle consignée — sinon `SelectionNonVerifiee`. Puis contre-vérification : retenues = cartes dont le
  verdict scellé du noyau est « survit » (`survivantes_des_verdicts`), présentes parmi les cartes, archive cohérente — sinon
  `HeritageRefuse`. Aucun repli, aucune lecture partielle.
- **Ce que voient les proposeurs** : les seules lois de l'archive (retenues cumulées), jamais un verdict, une richesse, une
  promotion, un motif ou un compte (`vue_pour_proposeur`, garde `exiger_vue_sans_verdict`). C'est un changement de ce que voient
  les proposeurs (la v57 le réservait au directeur) : il est demandé par la tâche A2 ; le préenregistrement du tour fermé doit le dire.
- **Course 2 v59** (`course2_v59.executer_course_v59`) : l'héritage de g+1 est `heritage_depuis_selection` (sélection v57 vérifiée
  par l'empreinte que l'étage de g a consignée ; seules les retenues, par nom et énoncé) au lieu de `texte_heritage` (classement
  des juges) ; plus d'une génération sans étage de tests de mort est refusé avant toute génération.
- **Graines** (R9) : `graine_de_tache(racine, tache)` = `SeedSequence(racine, spawn_key=(cle_de_tache(tache),))`, la clé de
  tâche de `graines_v53` ; les tirages frais du juge sont dérivés de la tâche **et** de l'empreinte de l'engagement gelé.
- **Proposeurs de référence** : `proposeurs_references.py` (v7) avait l'aléatoire (graines d'avant R9) mais aucun proposeur qui
  recopie ou mélange des lois promues ; `proposeurs_references_v59.py` donne les deux, sans modèle.

## 3. Ce que le README appelle « étage v56 », vérifié dans le code, et son remplacement

- **Lanceur** : `demonstrations/ideation_v8.py --course-2` appelle `course2_v56.executer_course_v56`, qui joue
  `etage_entre_generations_v56.jouer_etage_v56`, dont l'exécuteur par défaut est `tests_de_mort_v3.executer_tests_de_mort`. Or
  `tests_de_mort_v3` ne redéfinit que `ExecuteurBacASable` (borne 768 Mo) et `MEMOIRE_BAC_MIN_MO` et reprend tout le reste de la
  v2 par `import *` : la fonction de l'étage « v56 » **est l'objet `tests_de_mort_v2.executer_tests_de_mort`**, dont le verdict
  est la lecture mécanique de la dernière ligne `RESULTAT:` imprimée par le script. L'exécuteur est passé explicitement par
  `demonstrations/ideation_v5.reglages_etage` (bac de la v3).
- **Tour** : `pole/ideation_v2.py` importe en dur, lignes 175-180, `executer_tests_de_mort`, `valider_champ_test`,
  `extraire_prereg_court`, `GABARIT_TEST`, `ExecuteurBacASable`… de `tests_de_mort_v2` (étage v2 lui-même, bac à 512 Mo minimum).
- **Remplacement** : `demonstrations/ideation_v59.py` charge une instance propre du lanceur v8 et lui donne la course
  `course2_v59` (étage v57 → `tests_de_mort_v5`, sélection, lecture par la génération suivante) ; `pole/ideation_v59.py` charge
  une instance propre du tour v2 et remplace ces six noms par ceux de `tests_de_mort_v5`. Limite dite : la mesure de devis de la
  plus grosse consigne du lecteur (import local dans une fonction du tour v2) mesure encore celle du lecteur v2 (taille seulement).

## 4. Mode à blanc — commande, journal, code de sortie

Commande jouée (depuis `orchestrator/`, 31 s) :

```
nice -n 10 python3 -I -B demonstrations/mode_a_blanc_v59.py SORTIE --graine 20261102 --bac reel --utilisateur-bac 64097
code de sortie: 0
```

Journal scellé `journal-a-blanc-v59.json`, sha256 `ba75c28663d314ee49ed4b116d1608014451d5ef10125eaac9db5e86c728aae6` (sortie dans
le dossier de travail de la session, hors de l'arbre). Extraits :

```
départ : racine 20261102, bac reel, réseau aucun, monde exemples/temoins-pari-demo-v1.json (fdf4d5c1…), loi vraie S-V1
ÉTAGE bras=scripte|generation=1 : bwrap, factice=False, {survit 1, éliminée 2, non concluant 1}
scripte 1 : gardien refuse G1-MALFORMEE (sans bloc statistique) ; promues [INCONCLUSIVE, ELIMINEE, VRAIE, FAUSSE-2] ;
            verdicts VRAIE survit, ELIMINEE éliminée, FAUSSE-2 éliminée, INCONCLUSIVE non concluant ; retenues [G1-VRAIE] ;
            bilan 7cf78ebb…, sélection 2f535914…
scripte 2 : héritage lu 7cf78ebb… (archive [G1-VRAIE]) ; copie et mélange de G1-VRAIE, FAUSSE-4 : aucune promue
aleatoire 1 : promues [INCONCLUSIVE, VRAIE, ELIMINEE, ALEA-06, FAUSSE-2] ; retenues [G1-VRAIE, G1-ALEA-06]
aleatoire 2 : héritage lu 77ba89d0… (archive [G1-ALEA-06, G1-VRAIE]) ; 6 lois aléatoires : aucune promue
recopie_melange 1 : « héritage vide : aucune loi retenue à recopier » ; retenues [G1-VRAIE]
recopie_melange 2 : héritage lu 6dee05b0… ; 3 cartes (copie, mélange à l'uniforme, tempérée-inclinée) : aucune promue
```

Synthèse par bras (proposées / refusées au gardien / jugées / promues / testées / survivantes / retenues / promues puis survivantes) :
scripte g1 7/1/6/4/4/1/1/1, g2 3/0/3/0/0/0/0/0 ; aleatoire g1 13/1/12/5/5/2/2/2, g2 6/0/6/0/0/0/0/0 ; recopie_melange g1
7/1/6/3/3/1/1/1, g2 3/0/3/0/0/0/0/0. Le même jeu avec l'exécuteur factice (demandé explicitement) donne les mêmes promues,
verdicts et retenues (essai `TestBacReelV59`).

À lire honnêtement : (i) **G1-FAUSSE-2 est promue par le juge** en génération 1 (log W max 7,68 ; gain oracle −0,13 nat sur la
marginale du monde) puis éliminée par son test de mort : une fausse promotion du juge, vue une fois sur une graine, pas un taux ;
(ii) G1-ALEA-06 (loi aléatoire, gain oracle +0,30 nat, divergence 0,22 nat à la loi plantée) est promue et survit : vraie
information, pas la loi plantée — la définition d'une « fausse découverte » est à fixer au préenregistrement ; (iii) en
génération 2 l'archive contient la loi plantée, qui est alors un membre du nul v8 : par l'argument de Ville, toute promotion y
est bornée par α ; les zéros de la génération 2 sont attendus par construction.

## 5. Essais

- `essais/test_v59_boucle_fermee.py` : **28 réussis, 28 sous-essais** (`nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider
  essais/test_v59_boucle_fermee.py`, 15 s), dont l'essai du vrai bac à sable, **joué** ici. Gardes (cas sain + artefact) : lecture
  de l'héritage (sélection réécrite avec un sceau juste, altérée sans sceau, bilan d'une autre empreinte, fichier absent, lien
  symbolique, retenue non survivante réécrite de façon cohérente → contre-vérification), vue sans verdict, graines, bac réel sans
  `bwrap`, superutilisateur sans utilisateur dédié, course v59 sans étage, tour v59 (champ sans bloc refusé).
- Rejoués : `test_v57_verdict_noyau.py`, `test_v57b_cablage_verdict.py`, `test_v58_nul_v8.py` : **107 réussis, 182 sous-essais**.

## 6. Banc de mutations v59 (`python3 -I -B essais/mutations_v59.py`) : 9 / 9 tuées pour la raison attendue

| mutant | raison attendue | observée |
|---|---|---|
| la génération suivante ignore la sélection (héritage initial) | `None != '<empreinte>'` / listes différentes | tuée (4/5 essais en échec) |
| l'empreinte de la sélection n'est pas vérifiée | `SelectionNonVerifiee not raised` | tuée (2/6) |
| un test de mort échoué compte comme survivant | listes différentes / `HeritageRefuse` | tuée (2/3) |
| contre-vérification des retenues sautée | `HeritageRefuse not raised` | tuée (1/6) |
| bac à sable contourné en silence (repli factice sans `bwrap`) | `BacASableIndisponible not raised` | tuée (1/4) |
| graine non dérivée de la tâche (`spawn_key=()`) | graines égales | tuée (1/2) |
| un proposeur de référence voit le verdict du juge (évaluations servies avec la vue) | `VueAvecVerdict` | tuée (erreur de classe) |
| garde de la vue neutralisée | `VueAvecVerdict not raised` | tuée (6/3) |
| proposeur aléatoire sans vérification de sa vue | `VueAvecVerdict not raised` | tuée (1/3) |

Témoin avant et après : 20 essais, 0 en échec. Premier passage : la mutation de la graine n'était pas appliquée (fragment présent
deux fois, docstring comprise) et la contre-vérification sautée était tuée par la garde de cohérence de l'archive (autre raison) ;
corrigés (fragment de code exact ; artefact rendu cohérent aussi pour l'archive), puis 9/9.

## 7. Bac à sable : joué

`bwrap` 0.9.0 présent (`/usr/bin/bwrap`), noyau superutilisateur : l'étage exige une identité dédiée sans privilège ; le mode à
blanc prend `--utilisateur-bac 64097` (vérifiée par `setpriv`) et un dossier racine à elle (0700, parent 0711), retiré à la fin.
Sonde : réseau isolé, écriture hors du dossier refusée, aucune capacité, filtre d'appels système, mémoire bornée. Sur une machine
sans `bwrap`, `--bac reel` est refusé (code 2) et l'essai réel **échoue** sauf `POLE_ESSAI_BAC_REEL_NON_JOUE=1` (ignoré avec le
motif « ESSAI RÉEL NON JOUÉ ») ; `--bac` n'a pas de défaut ; le factice doit être demandé et le journal le dit.

## 8. Ce qui reste ouvert

1. `course2_v59` n'est essayée que par unités (refus sans étage, `heritage_depuis_selection`) : aucune course 2 simulée de bout en
   bout sous v59 (`GenerationV56` + étage) ; aucune mutation de la course v59 au banc.
2. Le lanceur v59 n'est essayé que pour son aiguillage (course v59 appelée) ; `--moteur simule` n'a pas été joué avec lui.
3. Le tour v59 n'est essayé que pour le remplacement des noms (et le refus d'un champ sans bloc) ; aucun tour complet joué.
4. Mode à blanc : gardien scripté (forme seule, pas `aiguilleur_v53`) ; « vérificateur » = lecteur témoin scripté de l'étage (autre
   étiquette de famille) + contre-vérification mécanique par la génération suivante ; aucun vérificateur à modèle.
5. Une seule graine jouée : aucun taux. La déclaration de machine jetable de l'étage est posée par le mode à blanc lui-même
   (`PATH`, `POLE_MACHINE_JETABLE_V56=1`), sans secret ; ce n'est pas une machine louée.
6. Les cartes de référence en génération 2 font face à une archive qui contient la loi plantée : un bras de référence mesuré sur
   archive vide (génération 1 seulement) ou sur un monde à plusieurs lois plantées reste à décider au préenregistrement.

## 9. Ce que le préenregistrement du tour fermé (A2) avec ses deux bras de référence (A4) devra citer

- **Commandes** (depuis `orchestrator/`) : mode à blanc `nice -n 10 python3 -I -B demonstrations/mode_a_blanc_v59.py SORTIE_NEUVE
  --graine G --bac reel --utilisateur-bac 64097 [--generations N] [--cartes-reference n]` ; essais `nice -n 10 python3 -I -B -m
  pytest -q -p no:cacheprovider essais/test_v59_boucle_fermee.py` ; banc `nice -n 10 python3 -I -B essais/mutations_v59.py` ;
  course réelle `python -I -B demonstrations/ideation_v59.py --course-2 CONF SORTIE --generations N …` (gardes du lanceur v8).
- **Fichiers et empreintes** : section 1 ; plus `pole/tests_de_mort_v5.py` (`da524871…`), `pole/etage_entre_generations_v57.py`
  (`e4bf3681…`), `pole/course2_v57.py` (`2efc4e0e…`), `pole/nul_v8.py` (`cc452aaf…`), scellés et inchangés (essai `TestR12V59`).
- **Mondes plantés disponibles** (`exemples/`) : `temoins-pari-demo-v1.json` (sha256 `fdf4d5c1ca0d2971b416ee5f694deff7a4696fe5defb3a6a1843dffef1231877`),
  loi vraie du mode à blanc = loi de S-V1 (softmax, 3 issues, 2 traits) ; S-V2 à S-V4 vraies et S-F1 à S-F4 fausses au sens de
  la table `monde-pari-demo-v1.json` (chaque fiche vraie est son propre monde : monde tautologique). Autres : `temoins-pari-demo-
  4traits-v1.json` (4 traits), `monde-pari-vivier60-v1.json` + `population-pari-vivier60-4traits-v1.json` (60 énoncés, table de
  vérités), générateurs `generer_monde_grammaire_v1.py` / `_v2.py` (lois hors du gabarit du chercheur mécanique),
  `construire_banque_t05_v3.py` (témoins plantés sur la banque réelle, privée en partie). Le monde à loi unique du mode à blanc
  est le seul où « fausse découverte » se lit contre une loi connue ; l'oracle consigne gain attendu et divergence par carte.
- **Comptes d'instrument pour un audit de symétrie (R4)**, par bras et par génération (bilan scellé et journal) : proposées,
  refusées au gardien (motifs), jugées, m de la règle e-BH, promues, testées, verdicts (survit, éliminée, non concluant), refusées
  à l'étage, survivantes, retenues, promues puis survivantes, sessions d'expérimentateur et de vérificateur, exécutions, tirages
  par carte jugée (200), épisodes de tranche (400), motifs du proposeur ; par carte : log W max, log e, membre dominant du nul,
  nombre de membres d'archive, empreinte d'engagement, graines (plan, noyau, frais), oracle (gain attendu, divergence, loi plantée).
- **Appels de modèles d'un tour réel, par carte (pour le devis)** : proposition (les cartes viennent par lots, un appel par
  proposeur et par passe) ; gardien `aiguilleur_v53` : 1 appel par carte ; juges croisés : 1 appel par carte et par juge de la
  configuration ; lecteurs d'étiquettes et fusions du bisociateur selon la configuration ; juge statistique, mémoire, moisson :
  aucun appel de modèle ; tests de mort, pour les seules candidates de l'étage (au plus `nombre` ≤ 12 par génération) : au plus 12
  sessions d'expérimentateur par carte (une par tour ; 3 exécutions au plus ; plafond 0,5 USD par carte par défaut) et 1 session
  de lecteur témoin (0,1 USD par défaut). Le mode à blanc en a joué 0 (expérimentateur et vérificateur scriptés : 1 tour d'exécution
  plus 1 tour de fin, 1 lecteur par carte testée).
