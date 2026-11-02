non scellable — bloquant B10 (règle R5 : durée de la garde 13, plafond de l'étage de la garde 5 et critères T2 à T5 de la garde 14 ne sont essayés par aucun essai sur le code gelé v62 ; six mutations survivantes) ; puis 33 couples T64 à T97, quatre cellules à récrire avec les essais neufs, décisions I26 et I27, marqueurs

# Contre-lecture R2 n° 3 — préenregistrement du tour fermé (étage 1 seul), brouillon 3, et code `_v62`

2 novembre 2026, de 16:40 à 17:15 UTC environ (heures de `date -u`). Contre-lecteur neuf : je n'ai écrit ni les brouillons 1 à 3, ni le
code `_v61` ou `_v62`, ni les contre-lectures 1 et 2. Lecture seule du dépôt public ; aucun commit, aucun `.sha256`, aucun fichier
existant modifié, rien sous `donnees/`, aucun `git fetch`, aucun appel de réseau ni de modèle ; calculs sous `nice -n 10`. Tout ce que
j'ai écrit est sous `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/tour-ferme-cl3/` (ce fichier, mes
sondes, mes relevés, les couples en JSON). Dépôt à la tête `421d090` ; le brouillon 3 et le code v62 sont suivis depuis `8247cac`.

**Verdict en quatre lignes.** Le brouillon 3 applique la contre-lecture 2 pour l'étage 1, et le code v62 corrige ce qu'elle
demandait : la loi et l'évaluateur arrivent à l'expérimentateur par le préenregistrement court, la grammaire arrive aux proposeurs,
T1 attend toutes les lectures d'héritage, tout arrêt est scellé ; essais (39), banc (24 sur 24) et bloc des 81 empreintes se
vérifient. Mais (B10) trois gardes de la liste d'arrêt ne sont essayées que sur le code v61, qui n'est plus gelé : six mutations du
code gelé survivent à toute la suite v62. Il reste en outre une contradiction du texte sur le calcul de la porte (I25 : la section
4.6 nomme la lecture v61), un trou du gardien qui peut arrêter la course payante (I26), deux modules exécutés hors du bloc gelé (I27),
et des écarts de lecture (I28, I29) et de devis (I30) à écrire.

## 0. Fichiers lus, empreintes vérifiées, ce qui a été rejoué

| pièce (depuis `orchestrator/`) | vérification |
|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon3.md` | sha256 `de068ec4222494bafc942b0b5acb7626b40f13479898baf1ad54892cd51c638b`, 717 lignes : conformes ; lu en entier |
| `prereg/rapport-redaction-tour-ferme-v3.md` | `4d4315bb0a47d6bbe71538f90ee007c8952422e7dde13904cc6565239819a8c7` ; lu en entier |
| les sept fichiers v62 (`pole/tour_ferme_v62.py`, `pole/evaluateur_lois_v62.py`, `pole/lecture_tour_ferme_v62.py`, `demonstrations/tour_ferme_v62.py`, `demonstrations/lire_tour_ferme_v62.py`, `essais/test_tour_ferme_v62.py`, `essais/mutations_tour_ferme_v62.py`) | les sept empreintes du rapport, toutes égales ; lus en entier |
| `prereg/contre-lecture-preenregistrement-tour-ferme-v2.md` | `8a74dfd2…`, égale à son compagnon ; lue en entier ; `…-v1.md` (`9684f64b…`) et le brouillon 2 (`37ae595f…`) pour le diff |
| fonctions du pôle appelées par le code v62 | `selection_pari` (`valider_loi`, `proba`, `_condition`, `tirer_instances`), `a_blanc_v59` (`garder`, `juger_carte`, `choisir_executeur`), `adaptateurs.controle_modele_resultat`, `configuration_v55.verifier_go_v55` (= `verifier_go_v56`), `ideation_v8.adaptateurs_reels_v56`, `etage_entre_generations_v57.jouer_etage_v57`, `tests_de_mort_v2/v5` (délais, budgets, `charger_tranche`), `dossier_ferme.charger_dossier_ferme`, `proposeurs_references_v59.proposer_recopie_melange`, essais v61 cités par le texte |

Rejoué ou vérifié (commandes et sorties dans le bloc-notes) :

- **Construction du brouillon 3** (`…/scratchpad/tf62/construire_brouillon3.py`, `cc7a6dc2…`, couples `b6d7e8cc…`, répétitions
  `7578e83f…`) rejouée hors du dépôt : sortie **égale à l'octet** au brouillon 3 (`de068ec4…`), 86 remplacements, 16 marqueurs
  (8 hors zone), 7 zones. Les 45 couples du JSON sont **identiques** à ceux de la section 9 de la contre-lecture 2 (extraction
  indépendante, `outils/extraire_couples.py`).
- **Bloc des empreintes** : 81 lignes, mêmes noms et même ordre que `FICHIERS_GELES` (`demonstrations/tour_ferme_v62.py:60-80`) ;
  chaque empreinte égale à l'arbre **et** à `git show 8247cac:` **et** à `git show 421d090:` (162 comparaisons, 0 écart).
- **Essais v62** : `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_tour_ferme_v62.py` (j'ajoute
  `-p no:cacheprovider` pour ne pas réécrire `.pytest_cache` de l'arbre), en deux passes : 38 essais avec `TMPDIR` dans le bloc-notes
  (`-k "not BacReelV62"`, 26,0 s), puis `BacReelV62` seul avec un dossier temporaire sous `/tmp` (l'identité 64097 ne traverse pas
  `/tmp/claude-0`, `drwx------`), 29,5 s : **39 réussis, code 0**, 16:48 à 16:49 UTC ; dossiers temporaires retirés.
- **Banc** : `nice -n 10 python3 -I -B essais/mutations_tour_ferme_v62.py`, lu d'abord (recompilation en mémoire,
  `essais/mutations_v55.appliquer` ; écritures seulement en dossiers `tempfile`), `TMPDIR` dans le bloc-notes : **24 mutations,
  24 tuées pour la raison attendue**, 0 survivante, témoin 32 essais avant et après, 16:49:23 à 16:51:04 UTC, code 0.
- **Cinq répétitions à blanc** (`…/tf62/blanc-2026110[2-6]/`) : relevés scellés, empreintes égales à celles du texte (L2b-v62) ;
  lecture v62 rejouée sur chacun : chiffres de la ligne L2b-v62 retrouvés (« tient », « discrimine », réel [36, 12, 12, 0, 0],
  aléatoire [36, 1 ou 2, 0], recopie [24, 0], S1 déclenché, 0 touche, 6 contextes). Manifestes : seule la racine 20261104 a couru
  sur le code gelé ; les quatre autres sur un lanceur antérieur (écart au bloc : `demonstrations/tour_ferme_v62.py` seul), ce que
  dit le rapport et pas le texte (mineur 31).
- **Mes sondes** (`outils/`, sorties `sondes-*.txt`, `fermeture-dynamique.txt`) :
  - `sondes_mutations_cl3.py` (`56f8a556…`) : dix mutations en mémoire du code gelé, chacune contre toute la suite v62 sauf le vrai
    bac (38 essais), 16:53 à 17:00 UTC ; résultats en section 4 ;
  - `sondes_chemin_cl3.py` (`00663f8d…`) : loi à indice flottant (I26), lignes de tranche et poids de L* servis (I29), arrêt en
    génération 2 (I28), courses à blanc, bac factice, dans le bloc-notes ;
  - `fermeture_dynamique_cl3.py` (`e6cd3b17…`) : modules du dépôt chargés **pendant** une course (I27).

Observé en passant, sans y toucher : (a) deux dossiers `/tmp/bac-tour-ferme-v62-e7km355x` et `…-jbq82650`, créés à 13:41:21 et
13:42:59 UTC, laissés par les deux courses du rédacteur refusées par la sonde du bac (mineur 34) ; (b) de 16:56 à 16:59 UTC,
pendant mes sondes, quatre fichiers `*_v3.py` de l'attaque de Goodhart ont été modifiés dans l'arbre par un autre travail
(`git status` : `M`, 359 lignes ajoutées), puis, à 17:07 UTC, `prereg/rapport-redaction-attaque-goodhart-v3.md` ; hors de mon
périmètre, hors du bloc v62 et de sa fermeture, non touchés. Aucun autre fichier de l'arbre n'a changé depuis mon début (vérifié en fin).

## 1. Constats (numérotation à la suite de la contre-lecture 2)

### Bloquant

**B10 — Règle R5 non tenue sur le code gelé : trois gardes ne sont essayées que sur le code v61.** La table de la section 7 cite,
pour la garde 5 (« plafond franchi → arrêt, code 3 ») et la garde 13 (durée), `Garde5Et13` de `essais/test_v61_tour_ferme.py`, et
pour la garde 14 (« chaque critère T1 à T5 manqué → « ne tient pas » »), `essais/test_v61_lecture_tour_ferme.py`. Ces essais
importent `pole.tour_ferme_v61` et `pole.lecture_tour_ferme_v61` (lignes 19-20 et 6), qui ne sont plus dans le code gelé (section
13 : « il n'est plus dans le code gelé de ce texte »). Le code gelé a ses propres copies : `Compteur.ajouter` (plafond de l'étage,
`pole/tour_ferme_v62.py:194-195`), `Compteur.verifier_duree` (`:208-210`), `lire_etage1` (T2 à T5, `pole/lecture_tour_ferme_v62.py:149-162`).
Mes mutations en mémoire de ces lignes **survivent toutes** à la suite v62 entière (0 essai en échec sur 38) : T2, T3, T4, T5
neutralisés ; plafond de l'étage neutralisé ; durée neutralisée. La phrase de la section 7 « Essais v62 de l'étage 1 : … (gardes 5 à
10, 12 à 15 …, cas sain et artefact) » est donc fausse pour ces trois gardes. Remède **sans toucher au code gelé** (les essais ne sont
pas dans le bloc) : un fichier d'essais neuf qui porte sur v62 les essais v61 `Garde5Et13` (compteur sans parts : plafond franchi ;
horloge factice : durée franchie ; un cas sain chacun ; si possible une course à blanc `--duree-max-h` minuscule → code 3, relevé
partiel scellé) et `test_T2…`, `test_T3_I5…`, `test_T4…`, `test_T5…` (relevés synthétiques de `releve_sain` modifiés), avec une
mutation par critère au banc ; puis les cellules 5, 13 et 14 et la phrase « Essais v62 … » récrites (couples T85, T98, T99, T100,
section 7). Le plafond de l'étage est en mode réel un filet derrière les parts des relais (somme des parts = plafond, contrôlée par
`lire_plan`), mais la garde est écrite et revendiquée : elle s'essaie.

### Importants

**I25 — Le critère gelé de la porte est attribué à un module non gelé.** Section 4.6 (l. 219) : « Calculé par
`pole/lecture_tour_ferme_v61.lire_etage1` ». Or la lecture gelée est `pole/lecture_tour_ferme_v62.py` (section 9, l. 489 ; section
13, l. 563 ; bloc, l. 654), et la v61 donne un autre T1 (B9 : « ne tient pas (T1) » sur une course saine où le bras réel est muet en
générations 1 et 2 ; l'essai `CourseMuette` le montre encore, `essais/test_tour_ferme_v62.py:596`). Scellé tel quel, le texte
désignerait deux calculs différents de la porte. Mêmes restes, moins graves : section 1, l. 42 (« écrit en `_v61` ») et l. 45
(« remplacée pour ce texte par `pole/lecture_tour_ferme_v61.py` »), couples T20 et T21 appliqués à la lettre puis devenus faux avec
la v62. Couples T64, T65, T66.

**I26 — Le gardien v62 accepte une loi que le juge ne sait pas évaluer : une proposition plausible arrête la course payante.**
`verifier_loi_servable` contrôle `condition.indice` d'un `si_sinon` par `c["indice"] not in (0, 1)` (`pole/tour_ferme_v62.py:266`),
que `1.0` passe ; `selection_pari.valider_loi` n'exige qu'une clé `indice` (`pole/selection_pari.py:207-209`) ; puis
`selection_pari._condition` (`:106`) et l'évaluateur servi (`pole/evaluateur_lois_v62.py:33`) indexent `instance["z"][1.0]`. Sonde
`sondes_chemin_cl3.py`, loi `{"type": "si_sinon", "condition": {"indice": 1.0, "seuil": 0.0}, …}` (JSON valide, « 0 ou 1 » en
valeur) : gabarit du proposeur **accepté**, gardien **accepté**, juge `TypeError` ; course à blanc entière : **code 3**, arrêt
« ArretTour : TypeError : list indices must be integers or slices, not float », lecture « ne tient pas (T1, T2) », `n1 = arret`.
Un seul `1.0` d'un proposeur réel arrête donc la course de 15 USD, alors que le texte dit la grammaire « tenue par le gardien »
(l. 563). Les autres indices sont tenus (`oscillation.trait` et `issue` : entiers exigés par `valider_loi`). Choix (proposer avec
recommandation) : **(A, recommandé)** code v63 : indices entiers exigés (`type(x) is int`) et, plus sûr, au gardien, la loi évaluée
par `selection_pari.proba` sur quelques instances, toute exception ou probabilité non finie refusée, essai et mutation ; **(B)** garder
v62 et déclarer la limite (couple T93). Le refus serait le même pour les trois bras (R4).

**I27 — Deux modules du dépôt sont exécutés pendant la course hors du bloc gelé.** `creer_tranche` (`pole/tour_ferme_v62.py:624`)
appelle `v5.charger_tranche` → `tests_de_mort_v2.charger_tranche` (`pole/tests_de_mort_v2.py:2302-2308`) →
`dossier_ferme.charger_dossier_ferme`, dont l'import tardif `from .ideation import fragments_interdits_dans`
(`pole/dossier_ferme.py:211-213`) charge `pole/ideation.py`, qui importe `pole/tests_de_mort.py`. Sonde
`fermeture_dynamique_cl3.py` (course à blanc dans le processus) : modules chargés pendant la course et absents du bloc :
**`pole/ideation.py`** (`4ee70d25567a9b3ac90911cc5ebee8cebba0537d541e7a0ebc1fa3ed170abdc2`) et **`pole/tests_de_mort.py`**
(`fc5d3507b33e13094d64751ff2b4564ba5ed4c238f93aaae808c458b3c123252`), tous deux inchangés depuis `dc2b2ba`. L'essai `Fermeture`
(`essais/test_tour_ferme_v62.py:733-751`) ne regarde que le chargement des deux programmes ; la phrase du texte « fermeture des imports
des chemins à blanc et réel » (l. 598) et celle de la contre-lecture 2 (« aucun module importé hors du bloc ») sont fausses à
l'exécution. La garde 6 ne verrait pas un changement de ces deux fichiers entre le scellement et la course. Choix : **(A, recommandé
si une v63 est faite)** les ajouter à `FICHIERS_GELES` et écrire un essai de fermeture **pendant une course** ; **(B)** déclarer la
limite avec les deux empreintes et faire vérifier celles-ci par la session-depot juste avant la course (couple T69).

**I28 — Sur un arrêt, la lecture gelée rend quand même une issue A4.** `lire_etage1` calcule l'issue A4 sur tout relevé valide,
arrêt compris (`pole/lecture_tour_ferme_v62.py:171-180`) ; le texte dit « Arrêt = sortie scellée telle quelle, code 3, aucune issue
lue » (l. 452) et le rapport d'arrêt écrit « non jugeable (arrêt) : aucune issue lue » (`demonstrations/tour_ferme_v62.py:413`).
Sonde (refus R-764 d'un proposeur en génération 2, après une génération 1 complète) : code 3, lecture « ne tient pas (T1) »,
`n1 = arret` **et** `issue_a4 = "discrimine"`, Newcombe [0,180 ; 1,0], `reserve_majeure_pour_a3 = False`. Un lecteur pourrait
rapporter « discrimine » d'une course arrêtée. Le texte doit dire ce qui est lu (couple T76) ; en v63, la lecture pourrait rendre
`issue_a4 = "non lue (arrêt)"`.

**I29 — Le point (3) de S1 est calculé, mais une trouvaille hors de S1 n'a aucune conséquence écrite.** Sonde : épisodes de
développement remplacés par les lignes de la tranche de la même tâche (fuite simulée) : `lignes_de_tranche_dans_les_contextes` =
400, rapportées dans `audits` ; poids de L* à deux décimales placés dans un contexte : 24 touches. Dans les deux cas, issue
« tient » (S1 non déclenché). Le texte (l. 404) ne donne une conséquence (« course invalide ») qu'à l'audit d'un S1 déclenché. La
détection marche (et fait ce que demandait C16), mais une fuite de la tranche vers les proposeurs invaliderait le test de mort du
bras réel quelle que soit l'issue. Couple T77 (ligne de tranche → défaut ; touche de L* → audit, car une coïncidence avec un épisode
de développement à 6 décimales reste possible, de l'ordre du pour cent par course). Aucun essai v62 n'essaie la détection elle-même
(mes sondes le font) : à ajouter avec B10.

**I30 — Devis : vers 6 tours par carte, la fin de la course tient à une carte promue près.** Avant chaque étage, la part restante
d'un relais doit couvrir cartes × 0,5 USD (Kimi) ou × 0,1 USD (Argon) (`pole/tour_ferme_v62.py:636-637`, `:198-206` ; appliqué
autrement que les « × 0,6 » de C13, à juste titre : un relais par rôle). Aux tailles moyennes du devis (cartes réelles testées ≈ 4, 2,
2 ; ≈ 1,5 carte aléatoire et ≈ 2,4 témoins par génération et par bras ; recopie ≈ 2,4 témoins) et à 0,36 USD par carte (6 tours à
0,06), Kimi a ≈ 1,38 USD avant le dernier étage (témoins du bras aléatoire, génération 3), qui en exige ≈ 1,2 : la course finit avec
≈ 0,18 USD de marge (dépense de Kimi ≈ 11,5 USD) ; une carte ou un témoin promu de plus en chemin (les doublures promouvaient 12
cartes réelles en génération 1), ou 6,5 tours par carte, et elle s'arrête en génération 3, sans issue. À 4 tours, marge ≈ 3,7 USD ;
à 5 tours, ≈ 1,9 USD (calcul refait ici, étage par étage dans l'ordre du code, 0,024 USD par appel de proposeur Kimi). Le texte (l. 554) présente 6 tours (≈ 12,2 USD, Kimi ≈ 11,6)
comme tenant sous le plafond, sans le dire. Pour le GO, c'est à écrire (couple T78) ; relever la part de Kimi (par exemple 13,5 et
1,5) est une option de Lazar, à peser contre le pire cas d'Argon (≤ 1,2 USD par étage) et son coût de vérificateur, SUPPOSÉ.

**I31 — La table de la section 7 cite encore les essais v61 comme preuves pour les gardes 7, 8 et 9.** Les cellules (l. 440-442,
couples T37 à T39 de la contre-lecture 2) disent « (v61), mutation tuée » : ces essais et mutations portent sur le code v61. Pour le
code gelé, les preuves sont `Garde7` v62 (archive et vue), `GrammaireServie` (gabarit) et `RefusAvantToutAppel` (familles) ; R5 est
tenue pour ces trois gardes **telles qu'écrites** (cas sain et artefact sur v62). Le refus d'un témoin entré dans la sélection
(`jouer_generation`, `:755-756`) n'est essayé par aucun essai v62 (mutation survivante), mais il n'est pas l'artefact écrit de la
garde 7. Couples T82, T83, T84.

### Mineurs

26. **Graines (R9)** : la section 8 (l. 460) nomme les tâches `tour-ferme-v61|…` (couple T44 appliqué à la lettre) ; le cœur gelé
    a `VERSION = "tour-ferme-v62"` (`pole/tour_ferme_v62.py:58`), et le manifeste écrit la règle exacte (`:954`). Couple T67.
27. **Commande de lecture** (l. 489) : « à écrire en v62 », « `lire_tour` », et pas de `--releve-sha256` (le programme l'accepte,
    `demonstrations/lire_tour_ferme_v62.py:53`) ; la lecture doit vérifier l'empreinte imprimée et commitée en fin de course. Couple T68.
28. **Portée mal reportée** : en-tête « décisions D2 à D9 » (l. 8) et cases de la section 5.2 dites à remplir sous peine de non-
    scellement (l. 9-10), alors qu'elles sont en zone ; section 0 « Un seul préenregistrement, deux étages » (l. 16) ; section 4.7
    « phrase au mentor (section 5.6) » (l. 244, zone) au lieu de 4.8 ; section 14, points (1) (code v62 dit manquant), (3) (D2 à
    D9) et (4) (question, réserve, M2 de l'étage 2) ; D6 décidée pour ses deux parties dans un texte qui ne scelle que l'étage 1.
    Couples T70 à T75, T89, T90.
29. **Phrases au mentor (section 4.8, neuve)** : « 36 proposals per arm » est fixé alors que le bras réel peut juger moins de 36
    cartes ; « [x] of which » est ambigu ; la liste des arrêts entre crochets omet le refus de modèle et l'arrêt sur exception ;
    aucune place pour la réserve R4 « trop beau » ; un relevé d'arrêt invalide se lit `n1 = critere` (`pole/lecture_tour_ferme_v62.py:229-232`).
    Couples T79, T80, T81, T95, T96.
30. **P6 et P7** : « (au moins 4 cartes sur 12) » alors que la lecture divise par les cartes jugées (`:194`) ; la trajectoire de P7
    et les mesures de la section 4.5 ne sont pas calculées par la lecture gelée (`vd_plantee` par génération l'est). Couples T87, T88.
31. **L2b-v62** ne dit pas que quatre racines sur cinq ont couru sur un lanceur antérieur au code gelé (manifestes) ; et les
    prédictions sont dites écrites « après L0 à L4 » (l. 170, l. 510) alors que P4 a été récrite après L2b-v61 et complétée avec
    L2b-v62. Couples T86, T91, T92.
32. **« claude-sdk »** : le mot passé à l'étage en mode réel (`demonstrations/tour_ferme_v62.py:217-220`) sera écrit dans chaque
    manifeste de tests de mort d'une course où aucun modèle Claude n'est appelé ; le texte ne le dit pas. Couple T94.
33. **« toute exception »** (l. 452) : le lanceur rattrape `Exception` (`:382`, `:405`) ; un signal (interruption, arrêt de la
    machine) ne laisse que le manifeste. Couple T97.
34. **Refus de la sonde du bac** : `preparer_bac` crée son dossier temporaire avant la sonde (`demonstrations/tour_ferme_v62.py:277-283`) ;
    un refus (garde 3) le laisse sous `/tmp` (deux restes du rédacteur). Aucun effet sur une sortie ; à corriger en v63.
35. **Appel de la machine jetable au lanceur** (`:366`) : essayé seulement au niveau de la fonction (`MachineJetable`) ; la mutation
    de l'appel n'est tuée que par un effet du banc (la fonction recompilée lit une copie des globales, ce qui fait échouer `MondeGele`
    pour une autre raison). Un essai du chemin réel avec texte scellé, configuration et registre de GO factices dans un dossier
    temporaire le couvrirait.
36. **Gardien et recopie** : un mélange de deux lois réelles de plus de ≈ 1 000 caractères dépasse la borne de 2 000 et serait refusé
    au seul bras recopie (`pole/proposeurs_references_v59.py:82-89`) ; cas limite, mesuré par S5 et P8.
37. **`--verifier-seulement`** (mineur 23 de la contre-lecture 2) : appliqué (portes non relancées, dossier de sessions retiré,
    `:247`, `:385-390`), mais essayé par aucun essai ; c'est le premier passage du chemin réel chez la session-depot.
38. **Témoin T-ELIM** : son seuil servi (« au moins 2,0 ») le distingue des autres fiches pour l'expérimentateur ; sans effet sur son
    verdict (contre-calcul), dit pour mémoire.

## 2. Constats de la contre-lecture 2 : état dans le brouillon 3 et le code v62

Lignes du brouillon 3 ; code en `fichier:ligne`. « Conforme » = appliqué comme demandé ; « autrement » = écart, dit justifié ou non,
déclaré ou non.

| constat | état | texte | code et essais |
|---|---|---|---|
| **B7** loi non servie | **conforme** : loi gelée en JSON canonique dans le texte du test, évaluateur copié dans la tranche et nommé dans les données, l'expérimentateur scripté ne lit que sa consigne ; borne 2 000 caractères (dite au proposeur dans la grammaire, pas chiffrée au texte) | l. 146 | `pole/tour_ferme_v62.py:295-310`, `:600-624`, `:233-235`, `:1060-1071` ; `pole/evaluateur_lois_v62.py` ; `ServiceDeLaLoi`, `CourseSaine.test_C8` ; consignes avec loi 60/60 à 66/66 dans les cinq répétitions ; mutation C8 tuée |
| **B8** grammaire non servie | **conforme**, et étendu (gardien élargi, section 3) ; trou de l'indice flottant (I26) | l. 56, 119 | `:85-137`, `:225-292`, `:353-382`, `:435-442` ; `GrammaireServie`, `CourseSaine.test_C9` ; 2 mutations tuées |
| **B9** T1 sur course saine | **conforme** dans la lecture v62 ; mais la section 4.6 nomme encore la lecture v61 (I25) | l. 223 ; l. 219 (I25) | lecture `:145-148` ; cœur `:858-874` ; `CourseMuette` (relevés du cœur, « tient »), `LectureV62.test_B9` ; mutation C10 tuée |
| I10 arrêts non scellés | **conforme** (`Exception` seulement, mineur 33) | l. 446, 452 | `:403-426`, `:905-910`, `:929-930` ; lanceur `:400-417` ; `ProposeurChemin`, `Arrets` ; 2 mutations tuées |
| I11 trois lectures du désaccord | **conforme** (arrêt partout) | l. 95, 443, 446 | `:662-665` |
| I12 parts des relais | **conforme** ; pire cas par relais (0,5 et 0,1) au lieu de 0,6 chacun : **autrement, justifié** (un relais par rôle), déclaré au rapport, pas au texte ; conséquence au devis non dite (I30) | l. 438, 554, 579-580 | `:177-215`, `:534-560`, `:636-637` ; lanceur `:141-142`, `:247` ; `PartsDesRelais`, `Arrets` (part) ; 3 mutations tuées ; plafond global de l'étage non essayé (B10) |
| I13 marqueurs dans la vue | **conforme** | l. 56 ; 689-700 | — |
| I14 précision | **conforme** (choix gardé : arrêt) | l. 146, 443 | `:295-302` ; évaluateur `:98` ; `PleinePrecision` ; 2 mutations tuées |
| I15 expérimentateur aveugle | **conforme** (mineur 38) | l. 54, 128 | `:324-350`, `:704-706`, `:718-720` ; `Aveugle`, `CourseSaine.test_C15` ; mutation tuée |
| I16 P4 sous D7 | **conforme** + cas intermédiaire neuf (section 3) | l. 182 | lecture `:120-125`, `:184-191` ; `LectureV62.test_I16` ; mutation tuée |
| I17 A4 sans carte réelle | **conforme** (étendu au cas, impossible en pratique, d'un bras aléatoire sans carte jugée, sous la même étiquette) | l. 252 | lecture `:174-175` ; `LectureV62.test_I17` ; mutation tuée |
| I18 point (3) de S1 | **conforme** (calculé ; absent → relevé invalide) ; conséquence d'une trouvaille hors S1 non écrite (I29) ; détection non essayée par un artefact | l. 404 | `:469-490`, `:688-690`, `:912-920` ; lecture `:68-74` ; `LectureV62.test_I18` ; mutation tuée ; mes sondes 2a et 2b |
| I19 garde 6 sans cas sain | **conforme** | l. 439 | `Garde6Complete` ; 2 mutations tuées |
| I20 commande de lecture | **conforme** (code) ; commande du texte périmée (mineur 27) | l. 489 | `demonstrations/lire_tour_ferme_v62.py` ; `CourseSaine.test_C18` ; mutation tuée |
| I21 « ne substitue aucun plafond » | **conforme** | l. 571 | lanceur `:242` |
| I22 machine jetable | **conforme** (environnement du processus, liste permise de la configuration, vérifiés avant tout appel puis à chaque étage) ; appel non essayé de bout en bout (mineur 35) | l. 448 | lanceur `:206-214`, `:365-366` ; `jouer_etage_v57` ; `MachineJetable` ; mutation tuée (fonction) |
| I23 recopie sur g−1 | **conforme** | l. 124 | `:858`, `:865` ; `CourseSaine.test_C19` ; mutation tuée |
| I24 monde gelé | **conforme** | l. 586 | lanceur `:199-203`, `:334`, `:348` ; `MondeGele` ; mutation tuée |
| mineur 11 heures | **conforme** (T19, T47) ; le brouillon 3 ne date pas sa propre rédaction (rapport : 13:05 à 13:58 UTC ; fichier 13:56, commit 14:49 UTC) | l. 3, 504 | — |
| mineur 12 passages périmés | appliqués (T20, T21, T61) **puis périmés par la v62** (I25, mineur 28) | l. 42, 45, 711 | — |
| mineur 13 identifiant opaque | **autrement, justifié et déclaré** (T22 : la v62 sert `F-<12 hex>`) | l. 54 | `:324-326` |
| mineur 14 mémoire | **autrement, justifié et déclaré** (T26 : 768 Mo annoncés et tenus) | l. 142 | `:80`, `:646` ; `EtageV62` (`memoire_mo` 768) |
| mineur 15 arrêt | **conforme** (T30) ; T32 **autrement, justifié et déclaré** (section 4.8 neuve) | l. 229, 257 | lecture `:215` |
| mineur 16 S5 | **conforme** (T34) | l. 427 | lecture `:204-212` ; mutation tuée |
| mineur 17 préfixe, graine publique | T44 appliqué **puis périmé** (mineur 26) ; T45 **conforme** | l. 460, 463 | `:58` |
| mineur 18 L2b-v61 | **conforme** (T48, T49) | l. 504 | — |
| mineur 19 `vd_distinctes` | **conforme**, calculé avant toute lecture (définition neuve, section 3) | l. 514 | `:817-836`, `:921-924` |
| mineur 20 tête des empreintes | **conforme** ; à mettre à jour (vérifiées à `8247cac` et `421d090`, I27) | l. 598 | — |
| mineur 21 moteur | **conforme** (« claude-sdk » en réel) ; non dit au texte (mineur 32) | l. 563 | lanceur `:217-220` ; `EtageV62` ; mutation tuée |
| mineur 22 durée | **dit** (T42), code inchangé | l. 446 | `:196`, `:208-210` ; non essayé en v62 (B10) |
| mineur 23 `--verifier-seulement` | **conforme**, non essayé (mineur 37) | — | lanceur `:247`, `:385-390` |
| mineur 24 | **conforme** | — | `:698-700`, `:585-586` ; `PleinePrecision.test_copie_de_tranche_verifiee` ; mutation tuée |
| mineur 25 (étage 2) | hors de ce scellement, dit | zones | — |

Couples T19 à T63 (contre-lecture 2, section 9), vérifiés par la construction rejouée à l'octet et relus à leur place :

| couple | état | ligne |
|---|---|---|
| T19 | conforme | 3 |
| T20, T21 | conformes, puis périmés par la v62 (I25 : T65, T66) | 42, 45 |
| T22 | autrement, justifié et déclaré | 54 |
| T23, T24, T25 | conformes | 56, 119, 128 |
| T26 | autrement, justifié et déclaré | 142 |
| T27 | conforme | 146 |
| T28 | conforme, plus le cas intermédiaire (section 3) | 182 |
| T29, T30, T31 | conformes | 223, 229, 252 |
| T32 | autrement (section 4.8), justifié et déclaré | 257 |
| T33, T34 | conformes | 404, 427 |
| T35, T36 | conformes, cellules mises à jour pour v62 ; T35 cite encore `Garde5Et13` v61 pour le plafond (B10) | 438, 439 |
| T37, T38, T39 | conformes, mais citent des essais v61 (I31 : T82, T83, T84) | 440-442 |
| T40, T41 | conformes, cellules mises à jour pour v62 | 443, 445 |
| T42 | conforme ; durée : `Garde5Et13` v61 seulement (B10) | 446 |
| T43 | conforme ; garde 14 : T2 à T5 sur v61 seulement (B10) ; garde 15 mise à jour | 447-448 |
| T44 | conforme, puis périmé (mineur 26 : T67) | 460 |
| T45 | conforme | 463 |
| T46 | conforme, cellule périmée (mineur 27 : T68) | 489 |
| T47, T48, T49 | conformes | 504 |
| T50 | conforme, plus la définition calculée | 514 |
| T51 | conforme ; « par exemple » périmé (T78) | 554 |
| T52 | autrement (D7 et D9 au plan, D8 en zone), justifié et déclaré | 565 |
| T53 | conforme | 571 |
| T54 | conforme, plus la suite (T69) | 598 |
| T55 | autrement, justifié et déclaré | 688 |
| T56, T57, T58 | conformes | 689, 691, 692 |
| T59 | conforme (en zone) | 697 |
| T60 | conforme (portée de D6 : T90) | 700 |
| T61 | conforme, puis périmé (T70) | 711 |
| T62 | conforme | 716 |
| T63 | conforme | 95 |

Changements de code C8 à C22 : C8 à C21 appliqués pour l'étage 1 (table ci-dessus) ; C13 « plan par étage » sans objet (étage 1
seul) ; C22 : cinq racines, vérifiées.

## 3. Ce qui est neuf (non demandé mot pour mot) et ce que cela fait aux règles

| nouveauté | jugement |
|---|---|
| Portée « étage 1 seul », zones `etage-2-hors-scellement` (7), lanceur qui les ignore (marqueurs compris) et refuse `--etage 2` | Rien d'affaibli pour l'étage 1 ; A3 reportée et dite. Les zones se vérifient (ouverture et fermeture appariées, `Garde6Complete` : zone ouverte refusée). Restes de portée hors zone : mineur 28. Un marqueur d'étage 1 caché dans une zone échapperait au contrôle : il n'y en a pas (relu). |
| Gardien élargi à la grammaire servie (types, champs exacts, structure, bornes de sûreté 50, taille 2 000), le même pour les trois bras et les témoins ; borne ±4 aux seules propositions | Plus strict, symétrique (R4) ; les sept témoins et les cartes de référence le passent (essais, cinq racines : 0 refus). N'affaiblit aucun critère. Mais il **ne tient pas** exactement la grammaire qu'il annonce (I26) ; cas limite du bras recopie (mineur 36). |
| Proposeur scripté qui ajuste une softmax sur les épisodes servis | Supprime le canal hors bande de la v61 ; S1 « trop beau » attendu à blanc (dit). Aucun effet sur le chemin réel. |
| P4 : cas intermédiaire (archive vide en génération 2 → bande 1 à 8) et opération « informative = archive de jugement non vide en génération 2 » | Comble un cas non écrit, avant toute lecture ; prédiction non décisive. Écrit après L2b-v62 : à déclarer (couple T92). |
| Section 4.8, phrases au mentor de l'étage 1 | Fidèles aux issues gelées, sans revendication au-delà ; défauts de détail (mineur 29). |
| Pire cas par relais 0,5 et 0,1 USD | Juste ; ses conséquences au devis ne sont pas dites (I30). |
| `vd_distinctes` (divergence symétrique < 0,05 nat sur les instances de l'oracle) et `recherche_loi_plantee` calculés au cœur | Mesures sans critère ou audit, définies et calculées avant toute lecture (R1). Conséquence d'une trouvaille du point (3) : I29. |
| Essais `Fermeture` et bloc à 81 lignes | Conformes au chargement ; insuffisants à l'exécution (I27). |
| Ligne L2b-v62 (cinq racines) | Chiffres exacts (rejoués) ; code utilisé non dit (mineur 31). |
| Arrêt sur toute exception, désaccord du contre-calcul → arrêt | Renforce la liste d'arrêt (R5 : aucun repli silencieux) ; sur un arrêt, l'issue A4 calculée doit être dite non lue (I28). |

Règles : **R1** — hypothèses, prédictions chiffrées et signées, métriques, seuils, critères T1 à T5, issues A4, liste d'arrêt et plan
d'étage 1 sont écrits ; restent I25 (le calcul de la porte doit désigner le code gelé), I28 et I29 (ce qui est lu sur un arrêt et sur
une trouvaille du point (3)), P7 et la section 4.5 (mineur 30). **R3** — aucune course visant un signe : les répétitions à blanc ne
décident rien et sont déclarées. **R4** — S1 et S2 de même profondeur, S5 sur le gardien et le « non concluant » ; gardien identique
pour tous les bras. **R5** — non tenue pour les gardes 5 (plafond de l'étage), 13 (durée) et 14 (T2 à T5) sur le code gelé (B10) ;
tenue pour les autres gardes telles qu'écrites (section 4). **R9** — `SeedSequence(E, spawn_key=(cle_de_tache(tâche),))` par tâche
(`boucle_fermee_v59`, inchangé) ; manifeste par course (commit, état de l'arbre, Python, numpy, `bwrap`, ordre des bras, empreintes de
l'évaluateur, de la consigne et de la grammaire, règle des graines, plan, décisions, entropie, configuration, rôles, empreintes du code)
vu sur les cinq manifestes ; nom des tâches à corriger au texte (mineur 26).

## 4. Le code contre le texte : la liste d'arrêt garde par garde, et le banc

| garde | cas sain sur le code gelé | artefact sur le code gelé | état R5 |
|---|---|---|---|
| 1 à 4 | essais v59 (`boucle_fermee_v59`, `a_blanc_v59`, inchangés et gelés) | idem | tenue (non rejouée ici ; fichiers inchangés) |
| 5 plafond de dépense | parts : `PartsDesRelais`, courses saines | part franchie, pire cas, « budget_depasse » d'un relais : `PartsDesRelais`, `Arrets` (code 3, scellé) | **plafond de l'étage : aucun essai v62, mutation survivante (B10)** |
| 6 préenregistrement scellé | `Garde6Complete` (texte scellé complet accepté) | sceau faux, marqueur hors zone, empreinte de code, zone ouverte, « brouillon », hors du dossier, entropie | tenue (l'entropie ne s'essaie qu'à l'unité : un texte d'empreinte < 2⁶⁴ ne se fabrique pas) |
| 7 témoins | `Garde7` (archive et vue saines) | témoin réel ou servi dans l'archive → `TemoinRetenu` | tenue telle qu'écrite ; refus dans la sélection non essayé (I31) |
| 8 gabarit imposé | `GrammaireServie` (propositions complétées) | `test_de_mort` porté, clés, énoncé, borne ±4 | tenue |
| 9 familles | courses d'essai (familles a, b) | `--familles-a-blanc a,a` → code 2 | tenue |
| 10 contre-calcul | `PleinePrecision`, courses saines (contre-calculs concordants) | gains arrondis à 2 décimales, gains fabriqués → code 3, relevé partiel scellé | tenue |
| 12 porte | `--etage 1` | `--etage 2` → code 2 (`RefusAvantToutAppel`) | tenue |
| 13 modèle servi, session, durée | `ProposeurChemin` (statut « ok ») | refus R-764, erreur, modèle servi autre, « budget_depasse » ; session en échec à l'étage (`Arrets`) | **durée : aucun essai v62, mutation survivante (B10)** ; refus R-764 de l'expérimentateur non essayé de bout en bout (même chemin que l'erreur de session) |
| 14 lecture gelée | `LectureV62.test_sain…`, `CourseMuette`, `CourseSaine` | T1 (lectures, arrêt), I16, I17, I18, S5, contre-calcul absent | **T2, T3, T4, T5 : aucun essai v62, quatre mutations survivantes (B10)** |
| 15 machine jetable | `MachineJetable` (fonction) | variable absente, variable hors liste | tenue à la fonction ; appel du lanceur non essayé (mineur 35) |

**Le banc tue-t-il ce qu'il prétend ?** Oui pour ses 24 mutations, chacune tuée par l'essai nommé et pour la raison attendue (motif
retrouvé dans la trace) ; témoin 32 essais avant et après. Il ne prétend rien sur les gardes 5 (plafond de l'étage), 7 (sélection),
13 (durée) et 14 (T2 à T5) : mes sondes, sur toute la suite v62 (38 essais, sans le vrai bac) :

| mutation en mémoire du code gelé | résultat |
|---|---|
| T2 neutralisé (`lecture_tour_ferme_v62.lire_etage1`) | **survivante** (0/38) |
| T3 neutralisé | **survivante** (0/38) |
| T4 neutralisé | **survivante** (0/38) |
| T5 neutralisé | **survivante** (0/38) |
| plafond de l'étage neutralisé (`Compteur.ajouter`) | **survivante** (0/38) |
| durée neutralisée (`Compteur.verifier_duree`) | **survivante** (0/38) |
| témoin dans la sélection non refusé (`jouer_generation`) | **survivante** (0/38) |
| appel de la machine jetable retiré au lanceur | tuée **pour une autre raison** (`MondeGele` : copie des globales par la recompilation) |
| entropie non exigée au chemin réel | survivante, attendu (artefact non fabricable ; unité essayée) |
| étage 2 non refusé | tuée (`RefusAvantToutAppel`) |

## 5. Essais rejoués (récapitulatif)

| quoi | commande (depuis `orchestrator/`) | résultat |
|---|---|---|
| essais v62 | `TMPDIR=…/tmp-essais nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_tour_ferme_v62.py -k "not BacReelV62"` puis `… -k BacReelV62` (TMPDIR par défaut) | 38 + 1 réussis, code 0 (26,0 s + 29,5 s) |
| banc v62 | `TMPDIR=…/tmp-banc nice -n 10 python3 -I -B essais/mutations_tour_ferme_v62.py` | 24/24 tuées pour la raison attendue, témoin 32/32, code 0, 101 s |
| construction du brouillon 3 | `nice -n 10 python3 -I -B …/tf62/construire_brouillon3.py <orchestrator> <sortie neuve>` | égale à l'octet (`de068ec4…`) |
| bloc des empreintes | `sha256sum -c` et `git show 8247cac:` / `421d090:` | 81/81, 0 écart |
| lecture v62 sur les cinq relevés à blanc | `lire_tour_etage_1` | chiffres de L2b-v62 retrouvés |
| sondes | `outils/sondes_mutations_cl3.py`, `outils/sondes_chemin_cl3.py`, `outils/fermeture_dynamique_cl3.py` | section 1 et section 4 |

Non rejoués : essais et bancs v59 à v61 (aucun de leurs fichiers n'a changé ; ils ne portent pas sur le code v62), répétitions à
blanc dans le vrai bac (cinq relevés lus et relus à la place).

## 6. Ce qui reste avant le scellement

**Marqueurs hors des zones (à remplir ; le lanceur refuse tout texte qui en garde un)** — 8 distincts, 9 occurrences, lignes du
brouillon 3 : `<<DECISION_D7>>` (l. 122), `<<CASE_GO>>` (l. 479, commande ; l. 585, plan), `<<DECISION_D9>>` (l. 521),
`<<CASE_CONFIGURATION_V3>>` (l. 584), `<<DECISION_D2>>` (l. 689), `<<DECISION_D3>>` (l. 691), `<<DECISION_D4>>` (l. 692),
`<<DECISION_D6>>` (l. 700). **Dans les zones (restent vides sous ce scellement)** : `<<CASE_Q>>` (310), `<<CASE_E0>>` (311),
`<<CASE_R>>` (312), `<<CASE_T>>` (313), `<<CASE_M2>>` (314), `<<CASE_V>>` (315, 592), `<<DECISION_D8>>` (338), `<<DECISION_D5>>` (697).
Rappel : D2, D3, D4 et D6 sont écrites dans le code gelé (un refus = code et texte nouveaux) ; D7 et D9 sont aussi au plan (`d7`,
`d9`) : un autre choix change la ligne du plan et, pour D7, la prédiction P4 écrite « sous D7 archive du bras réel ».

**Sans marqueur, à remplacer au scellement** : le titre (« brouillon 3 », l. 1) ; le statut (l. 3 : « non contre-lu une troisième
fois … non scellé. Portée : l'étage 1 seul (décision de Lazar en attente, défaut sous 48 heures : étage 1 seul) ») par le statut
scellé et la décision de portée prise (ou son défaut appliqué, daté) ; la phrase « **Troisième contre-lecture à faire, sur ce texte et
sur le code `_v62`.** » (l. 514) par la référence à cette contre-lecture (chemin, empreinte, verdict) et à la contre-lecture courte
ci-dessous. Le lanceur ne vérifie aucune de ces trois phrases.

**Travail et décisions, dans l'ordre :**

1. **B10** : essais v62 des gardes 5 (plafond de l'étage), 13 (durée) et 14 (T2 à T5), avec leurs mutations au banc ; le code gelé
   ne change pas (les essais sont hors du bloc). Avec eux, de préférence : un artefact de la détection du point (3) (I29), un essai
   du chemin réel jusqu'à `--verifier-seulement` avec configuration et registre de GO factices (mineurs 35, 37), le refus d'un témoin
   dans la sélection (I31).
2. **Décisions I26 et I27** (proposer avec recommandation) : (A) code v63 (gardien qui exige des indices entiers et évalue la loi ;
   `FICHIERS_GELES` étendu à `pole/ideation.py` et `pole/tests_de_mort.py` avec un essai de fermeture pendant une course ; au passage,
   I28 en code et mineur 34), nouveau bloc d'empreintes ; ou (B) v62 gardée, couples T69 et T93 appliqués, les deux empreintes
   vérifiées par la session-depot juste avant la course. Ma recommandation : (A), confiance moyenne : B10 impose déjà un brouillon 4 et
   une contre-lecture courte ; (B) laisse une course de 15 USD exposée à une sortie plausible d'un proposeur.
3. **Brouillon 4** = brouillon 3 + les 33 couples de la section 7 (T64 à T97 ; T69 et T93 selon la décision 2) + les quatre cellules
   T85, T98, T99, T100 récrites avec les noms des essais de B10 (et, si v63, la section 13 et le bloc récrits).
4. **Contre-lecture R2 courte et neuve** du brouillon 4 et des essais neufs (et du diff v62 → v63 s'il y en a un).
5. **Mot de Lazar** : portée (défaut sous 48 heures : étage 1 seul), D2, D3, D4, D6, D7, D9 ; part de Kimi au vu de I30.
6. **Session-depot** : configuration v3 (`budget.plafond_usd` = 15, relais `kimi` et `argon`, `etage_tests_de_mort.environnement_permis`)
   et son empreinte ; GO de type « calcul », par Lazar, valide, d'exactement 15 USD (`verifier_go_v55`) ; `bwrap` 0.9.0, identité
   dédiée sans privilège, aucune autre course de cette identité ; `POLE_MACHINE_JETABLE_V56=1` et environnement en liste blanche ;
   un passage `--verifier-seulement` ; si (B), les empreintes de `pole/ideation.py` et `pole/tests_de_mort.py`.
7. Scellement par le directeur (nom `preenregistrement-tour-ferme-v1-v<N>.md`, compagnon `.sha256`), commit et poussée **avant** la
   course ; après la course, lecture par `demonstrations/lire_tour_ferme_v62.py … --releve-sha256 SHA` et verdict par un lecteur neuf
   (R13).

**Le texte est-il scellable une fois les marqueurs remplis ?** Non tel quel : il désignerait une lecture non gelée pour la porte
(I25) et revendiquerait des essais qui ne portent pas sur le code gelé (B10). Il le devient avec les points 1 à 5 ci-dessus : aucune
autre réserve de fond que les décisions I26, I27 et I30, qui appartiennent à Lazar.

## 7. Remplacements (brouillon 3 → brouillon 4)

Fichier de référence : `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/tour-ferme-cl3/couples/couples_cl3.json`
(33 couples, sha256 `7aa25f19b9f476e083b89a2175458d4523a968b5f24df218f784c90c36494c03`). Vérifié par `couples/verifier_couples_cl3.py`
(`4ad88ecc…`) : chaque cible figure exactement une fois dans le brouillon 3 (`de068ec4…`) et encore une fois au moment de son
application, dans l'ordre ci-dessous ; les 16 marqueurs sont conservés (8 hors zone) ; 7 zones appariées ; le plan de l'étage 1 est
relu par `lire_plan` du lanceur v62 ; texte obtenu : 715 lignes, sha256 `a6337d96b33201a7fdff9237cfb38b2a4fb57670e6bdd10572bd633ad4300ac4`
(sans T85, T98 à T100, qui s'écrivent avec B10). T69 et T93 valent pour l'option (B) de I27 et de I26 ; avec une v63, ils
tombent (section 13 et bloc récrits). Le numéro T85 est réservé (cible ci-dessous).

**T64** — 4.6 : la porte calculée par le code gelé (I25)

remplacer :

~~~~text
Calculé par `pole/lecture_tour_ferme_v61.lire_etage1` (C1, C2 appliqués ; la v60 reste, inchangée) sur le relevé scellé, dans cet ordre ;
~~~~

par :

~~~~text
Calculé par `pole/lecture_tour_ferme_v62.lire_etage1`, appelée par `lire_tour_etage_1` (programme `demonstrations/lire_tour_ferme_v62.py`, section 9 ; C10 et C16 de la contre-lecture 2 appliqués ; les lectures v60 et v61 restent inchangées, hors du code gelé de ce texte) sur le relevé scellé, dans cet ordre ;
~~~~

**T65** — 1 : lanceur v62 (I25)

remplacer :

~~~~text
un lanceur à vrais modèles (écrit en `_v61` pour l'étage 1, section 13 ; cœur de l'étage 2 non écrit)
~~~~

par :

~~~~text
un lanceur à vrais modèles (écrit en `_v61`, remplacé pour ce texte par `demonstrations/tour_ferme_v62.py`, étage 1 seul, section 13 ; cœur de l'étage 2 non écrit)
~~~~

**T66** — 1 : lecture v62 (I25)

remplacer :

~~~~text
(`pole/lecture_tour_ferme_v60.py`, remplacée pour ce texte par `pole/lecture_tour_ferme_v61.py`, section 4.6)
~~~~

par :

~~~~text
(`pole/lecture_tour_ferme_v60.py`, remplacée par `pole/lecture_tour_ferme_v61.py`, puis, pour ce texte, par `pole/lecture_tour_ferme_v62.py`, section 4.6)
~~~~

**T67** — 8 : nom des tâches des graines (mineur 26, règle R9)

remplacer :

~~~~text
`tour-ferme-v61|etage=<e>|bras=<b>|generation=<g>` (préfixe = `VERSION` du cœur gelé ; `tour-ferme-v62|…` avec un cœur v62) suivies de
~~~~

par :

~~~~text
`tour-ferme-v62|etage=1|bras=<b>|generation=<g>` (préfixe = `VERSION` du cœur gelé `pole/tour_ferme_v62.py` ; règle recopiée au manifeste, champ `regle_des_graines`) suivies de
~~~~

**T68** — 9 : commande de la lecture gelée (mineur 27)

remplacer :

~~~~text
`nice -n 10 python3 -I -B demonstrations/lire_tour_ferme_v62.py ../resultats/tour-ferme-v1-etage1 LECTURE.json` (à écrire en v62 : vérifie le sceau et l'empreinte du relevé, applique `lire_tour` au champ `releve`, écrit la lecture scellée qu'exige la garde 12).
~~~~

par :

~~~~text
`nice -n 10 python3 -I -B demonstrations/lire_tour_ferme_v62.py ../resultats/tour-ferme-v1-etage1 LECTURE.json --releve-sha256 SHA` (SHA : l'empreinte du relevé imprimée par le lanceur à la fin de la course et commitée avec lui ; le programme vérifie le sceau et cette empreinte, applique `lire_tour_etage_1` au seul champ `releve`, écrit la lecture scellée sans jamais écraser une lecture existante ; c'est elle que lira la porte du préenregistrement de l'étage 2).
~~~~

**T69** — 13 : tête des empreintes et limite de la fermeture (I27, option B ; caduc si v63)

remplacer :

~~~~text
recalculées ci-dessous pour le code v62, arbre de travail à la tête `82ad7a8`, fichiers v62 non suivis : à revérifier après commit)
~~~~

par :

~~~~text
recalculées ci-dessous pour le code v62 à la tête `82ad7a8` ; revérifiées par la contre-lecture 3 aux commits `8247cac` et `421d090` : 81 empreintes égales à l'arbre et aux deux commits. Limite : cette fermeture est celle du chargement des programmes ; pendant la course, l'import tardif de `dossier_ferme.charger_dossier_ferme` (appelé à chaque création de tranche) charge et exécute deux modules du dépôt absents de ce bloc, que le lanceur ne vérifie pas : `pole/ideation.py` (`4ee70d25567a9b3ac90911cc5ebee8cebba0537d541e7a0ebc1fa3ed170abdc2`) et `pole/tests_de_mort.py` (`fc5d3507b33e13094d64751ff2b4564ba5ed4c238f93aaae808c458b3c123252`) ; la session-depot vérifie ces deux empreintes juste avant la course)
~~~~

**T70** — 14, point (1) (mineur 28)

remplacer :

~~~~text
(1) le code `_v62` (contre-lecture 2 : loi servie à l'expérimentateur, grammaire servie aux proposeurs, lectures d'héritage, arrêts scellés, relais, machine jetable) et, pour l'étage 2, son cœur ; leurs essais, leur banc de mutations et une répétition à blanc où les rôles scriptés ne reçoivent que ce que reçoivent les modèles ;
~~~~

par :

~~~~text
(1) fait pour l'étage 1 : le code `_v62` (contre-lecture 2 : loi servie à l'expérimentateur, grammaire servie aux proposeurs, lectures d'héritage, arrêts scellés, relais, machine jetable), ses essais, son banc de mutations et cinq répétitions à blanc où les rôles scriptés ne reçoivent que ce que reçoivent les modèles (L2b-v62) ; le cœur de l'étage 2 relève du préenregistrement de l'étage 2 ;
~~~~

**T71** — 14, point (3) (mineur 28)

remplacer :

~~~~text
(3) les décisions D2 à D9 (marqueurs)
~~~~

par :

~~~~text
(3) les décisions D2, D3, D4, D6, D7 et D9 (marqueurs ; D5 et D8 relèvent de l'étage 2)
~~~~

**T72** — 14, point (4) (mineur 28)

remplacer :

~~~~text
(4) chez la
session-depot : le texte et l'empreinte de la question du 1er novembre et la configuration de son tour (modèles,
adaptateurs), l'exécution de la réserve et les cases de la section 5.2, le monde M2, les clés, **`bwrap` 0.9.0 et une identité
dédiée sans privilège sur son instance** ;
~~~~

par :

~~~~text
(4) chez la
session-depot : la configuration v3 de l'étage 1 (modèles et adaptateurs du tour du 1er novembre, `budget.plafond_usd` = 15, relais de Kimi et d'Argon), les clés, **`bwrap` 0.9.0 et une identité
dédiée sans privilège sur son instance**, la machine jetable (`POLE_MACHINE_JETABLE_V56=1`, environnement dans la liste blanche) et un passage `--verifier-seulement` ; la question du 1er novembre, la réserve, les cases de la section 5.2 et le monde M2 relèvent de l'étage 2 ;
~~~~

**T73** — en-tête : décisions de ce scellement (mineur 28)

remplacer :

~~~~text
la validation par Lazar des décisions D2 à D9 (section 14 ; D1 est prise)
~~~~

par :

~~~~text
la validation par Lazar des décisions D2, D3, D4, D6, D7 et D9 (section 14 ; D1 est prise ; D5 et D8 relèvent de l'étage 2)
~~~~

**T74** — en-tête : cases de la section 5.2 (mineur 28)

remplacer :

~~~~text
Les cases « à remplir avant scellement » (section 5.2) sont remplies par la session-depot, qui tient les
données privées, puis relues par le contre-lecteur ; un texte qui en garde une vide ne se scelle pas.
~~~~

par :

~~~~text
Les cases de la section 5.2 relèvent de l'étage 2, hors de ce scellement ; pour l'étage 1, la session-depot porte l'empreinte de la configuration v3 et l'identifiant du GO (section 13) ; un texte qui garde un marqueur hors des zones de l'étage 2 ne se scelle pas (le lanceur le refuse, garde 6).
~~~~

**T75** — 4.7 : renvoi à la phrase au mentor (mineur 28)

remplacer :

~~~~text
la phrase au mentor (section 5.6)
~~~~

par :

~~~~text
la phrase au mentor (section 4.8)
~~~~

**T76** — 7 : ce qui est lu sur un arrêt (I28)

remplacer :

~~~~text
Arrêt = sortie scellée telle quelle, code 3, aucune issue lue ;
~~~~

par :

~~~~text
Arrêt = sortie scellée telle quelle, code 3, aucune issue lue : la lecture v62 rend « ne tient pas (T1) » et `n1 = arret` (phrase N1 d'arrêt, section 4.8) ; l'issue A4 qu'elle calcule sur le relevé partiel n'est ni lue ni rapportée comme issue (ses chiffres, s'ils sont cités, le sont comme partiels) ;
~~~~

**T77** — 6 : conséquence du point (3) de S1 (I29)

remplacer :

~~~~text
S1 ou S3 déclenché sans défaut trouvé : l'issue porte la réserve « trop beau, audité sans défaut » (R4).
~~~~

par :

~~~~text
S1 ou S3 déclenché sans défaut trouvé : l'issue porte la réserve « trop beau, audité sans défaut » (R4). Point (3), S1 déclenché ou non : une ligne de tranche dans un contexte servi est un défaut (course invalide, aucune issue) ; une touche des paramètres de L* est auditée avant toute lecture d'issue (coïncidence d'un nombre servi, par exemple d'un épisode de développement, ou fuite : défaut) ; la lecture v62 rapporte ce point (`audits`), elle ne l'applique pas.
~~~~

**T78** — 12 : pire cas avant chaque étage (I30)

remplacer :

~~~~text
par exemple 12 USD pour Kimi et 3 USD pour Argon, v62)
~~~~

par :

~~~~text
12 USD pour Kimi et 3 USD pour Argon, v62 ; avant chaque étage de tests de mort, la part restante d'un relais doit couvrir son pire cas, cartes de l'étage × 0,5 USD pour Kimi et × 0,1 USD pour Argon : à 6 tours par carte et aux tailles moyennes ci-dessus, la marge de Kimi avant le dernier étage n'est que ≈ 0,2 USD, et une carte ou un témoin promu de plus en chemin, ou 6,5 tours par carte, arrête la course en génération 3 — arrêt, phrase N1 d'arrêt, aucune issue ; à 4 tours, marge ≈ 3,7 USD)
~~~~

**T79** — 4.8 : taille dite au mentor (mineur 29)

remplacer :

~~~~text
This is one planted world, three generations, 36 proposals per arm. »
~~~~

par :

~~~~text
This is one planted world, three generations, [n_real] model proposals and [n_random] random proposals judged. »
~~~~

**T80** — 4.8 : arrêts nommés (mineur 29)

remplacer :

~~~~text
([stop: budget / duration / recomputation disagreement / session failure])
~~~~

par :

~~~~text
([stop: budget / duration / recomputation disagreement / session failure / model refusal / other: (type)])
~~~~

**T81** — 4.8 : réserve R4 (mineur 29)

remplacer :

~~~~text
« not measurable: no proposal from the models was judged ».
~~~~

par :

~~~~text
« not measurable: no proposal from the models was judged ». Si S1 est déclenché et audité sans défaut (section 6), la phrase « tient » se termine par : « The run was flagged as too clean and audited; no defect was found. »
~~~~

**T82** — 7, garde 7 : preuves sur le code gelé (I31)

remplacer :

~~~~text
| 7 | témoins jamais retenus ni servis | témoin promu et survivant : absent de la sélection, de l'archive, de la vue | témoin introduit dans l'archive → refus | `Garde7` (v61), mutation tuée |
~~~~

par :

~~~~text
| 7 | témoins jamais retenus ni servis | témoin promu et survivant : absent de la sélection, de l'archive, de la vue | témoin introduit dans l'archive → refus | v62 : `Garde7` (archive et vue ; identifiant réel ou servi d'un témoin → `TemoinRetenu`) ; le refus d'un témoin dans la sélection (`jouer_generation`) n'est essayé par aucun essai v62 ; `Garde7` v61 et sa mutation portent sur le code v61 |
~~~~

**T83** — 7, garde 8 : preuves sur le code gelé (I31)

remplacer :

~~~~text
→ refusée au gardien mécanique | `Garde8` et lanceur `--scenario-proposeur hors_gabarit` (v61), mutation tuée |
~~~~

par :

~~~~text
→ refusée au gardien mécanique | v62 : `GrammaireServie` (proposition complétée acceptée ; proposition qui porte un `test_de_mort`, clé manquante, énoncé trop long → refusée), mutation de la borne ±4 tuée ; `Garde8` et `--scenario-proposeur hors_gabarit` : v61 |
~~~~

**T84** — 7, garde 9 : preuves sur le code gelé (I31)

remplacer :

~~~~text
| 9 | familles séparées | expérimentateur Kimi, vérificateur Argon | même famille → refus avant toute session | `Garde9` et lanceur `--familles-a-blanc a,a`, code 2 (v61), mutation tuée |
~~~~

par :

~~~~text
| 9 | familles séparées | expérimentateur Kimi, vérificateur Argon | même famille → refus avant toute session | v62 : `RefusAvantToutAppel` (`--familles-a-blanc a,a` → code 2, rien écrit) et toutes les courses d'essai v62 (familles distinctes) ; `Garde9` et sa mutation : v61 |
~~~~

**T86** — 10, L2b-v62 : code utilisé (mineur 31)

remplacer :

~~~~text
aucun canal hors bande ; 5 racines |
~~~~

par :

~~~~text
aucun canal hors bande ; 5 racines ; la racine 20261104 sur le code gelé (81 empreintes égales au manifeste), les quatre autres sur un lanceur antérieur d'une modification (paramètre d'essai `dossier_prereg` de `lire_preenregistrement`, chemin réel seulement ; cœur, évaluateur et lecture identiques) |
~~~~

**T87** — 4.3, P6 : dénominateur (mineur 30)

remplacer :

~~~~text
(au moins 4 cartes sur 12)
~~~~

par :

~~~~text
(parmi les cartes jugées de la génération 1 ; au moins 4 sur 12 si toutes passent le gardien)
~~~~

**T88** — 4.3, P7 : trajectoire calculée par le lecteur (mineur 30)

remplacer :

~~~~text
décroît** de la génération 1 à la génération 3 (mesurée, sans seuil).
~~~~

par :

~~~~text
décroît** de la génération 1 à la génération 3 (mesurée, sans seuil ; la lecture v62 rend `vd_plantee` par génération mais ne calcule pas cette trajectoire : le lecteur la calcule sur les champs `divergence_nat` du relevé, cartes VD du bras réel, sans autre choix).
~~~~

**T89** — 0 : deux étages, un seul scellé (mineur 28)

remplacer :

~~~~text
Un seul préenregistrement, deux étages.
~~~~

par :

~~~~text
Deux étages ; ce texte ne scelle que le premier (section 0, portée).
~~~~

**T90** — 14, D6 : sa partie de l'étage 1 (mineur 28)

remplacer :

~~~~text
- **D6** — bras aléatoire de contrôle à l'étage 2 (oui, ≈ 0,7 USD) ; seconde réplique du bras aléatoire de l'étage 1 : non (recommandation : les 2,5 USD servent mieux au plafond). Mot de Lazar : <<DECISION_D6>>.
~~~~

par :

~~~~text
- **D6** (pour ce scellement, sa seule partie de l'étage 1) — seconde réplique du bras aléatoire de l'étage 1 : non (recommandation : les 2,5 USD servent mieux au plafond). Mot de Lazar : <<DECISION_D6>>. Le bras aléatoire de contrôle de l'étage 2 (oui, ≈ 0,7 USD) relève du préenregistrement de l'étage 2.
~~~~

**T91** — 4.3 : lectures préalables déclarées (mineur 31)

remplacer :

~~~~text
Écrites après les lectures préalables L0 à L4 (section 10)
~~~~

par :

~~~~text
Écrites après les lectures préalables L0 à L4, L2b-v61 et L2b-v62 (section 10)
~~~~

**T92** — 10 : prédictions écrites après (mineur 31)

remplacer :

~~~~text
Les
prédictions ont été écrites après L0 à L4 : déclaré
~~~~

par :

~~~~text
Les
prédictions ont été écrites après L0 à L4 (P4 récrite par la contre-lecture 2 après L2b-v61 ; son cas intermédiaire ajouté par le rédacteur 3, avec L2b-v62) : déclaré
~~~~

**T93** — 4.1, gardien : limite connue (I26, option B ; caduc si v63)

remplacer :

~~~~text
le lanceur refuse `d9 = aiguilleur` avant tout appel).
~~~~

par :

~~~~text
le lanceur refuse `d9 = aiguilleur` avant tout appel). Limite connue du gardien v62 (contre-lecture 3) : `condition.indice` d'une loi `si_sinon` y est accepté en nombre à virgule (`1.0`), que le juge ne sait pas évaluer ; une telle proposition, jugée, arrête la course (code 3, `TypeError`, N1 d'arrêt).
~~~~

**T94** — 13 : « claude-sdk » (mineur 32)

remplacer :

~~~~text
monde gelé, moteur de l'étage)
~~~~

par :

~~~~text
monde gelé, moteur de l'étage : « claude-sdk » en mode réel, mot de l'étage v5 pour « coûts réels, exécuteur factice refusé » ; aucun modèle Claude n'est appelé)
~~~~

**T95** — 4.8 : N1 d'arrêt sur relevé invalide (mineur 29)

remplacer :

~~~~text
(T1 manqué par un arrêt de la liste d'arrêt ; champ `n1 = arret` de la lecture v62)
~~~~

par :

~~~~text
(T1 manqué par un arrêt de la liste d'arrêt ; champ `n1 = arret` de la lecture v62 ; un relevé d'arrêt jugé invalide, `n1 = critere` avec un champ `arret` non nul, se dit aussi par cette phrase)
~~~~

**T96** — 4.8 : « [x] of which » (mineur 29)

remplacer :

~~~~text
([x] of which carried no new information by an oracle that knows the planted law)
~~~~

par :

~~~~text
([x] of the random proposals kept carried no new information by an oracle that knows the planted law)
~~~~

**T97** — 7 : signal et panne de la machine (mineur 33)

remplacer :

~~~~text
toute exception après le manifeste est un arrêt (v62, C12) ;
~~~~

par :

~~~~text
toute exception (classe Python `Exception`) après le manifeste est un arrêt (v62, C12) ; une interruption par signal ou une panne de la machine ne laisse que le manifeste, sans relevé : course sans issue, reprise selon la phrase suivante ;
~~~~

**À écrire avec B10** (cibles exactes, chacune présente une fois dans le brouillon 3 et encore une fois après les 33 couples ;
le texte nouveau nomme les essais v62 écrits pour B10 et leurs mutations) :

- **T85** — section 7, phrase des essais : remplacer « Essais v62 de l'étage 1 : `essais/test_tour_ferme_v62.py` (gardes 5 à 10, 12 à 15 et corrections C8 à C21, cas sain et artefact) » par la liste exacte des fichiers d'essais v62 et des gardes que chacun essaie.
- **T98** — garde 5 : remplacer « `essais/test_v61_tour_ferme.py` (`Garde5Et13` ; lanceur, code 3) ; parts des relais : » par la citation de l'essai v62 du plafond de l'étage (cas sain, artefact, code 3 de bout en bout si écrit).
- **T99** — garde 13 : remplacer « durée : `Garde5Et13` (horloge factice, v61) ; » par la citation de l'essai v62 de la durée (horloge factice).
- **T100** — garde 14 : remplacer « `essais/test_v61_lecture_tour_ferme.py` (14 essais), 6 mutations tuées ; » par la citation des essais v62 de T2 à T5 et de leurs mutations.

## 8. Si une v63 est faite (option A de I26 et I27)

Fichiers neufs, aucun `_v62` modifié (R12) ; pour chaque changement, un essai cas sain et artefact et une mutation tuée :

1. Gardien : `condition.indice` et `condition.sous_population` exigés entiers (`type(x) is int`) ; et la loi évaluée par
   `selection_pari.proba` sur quelques instances fixes, toute exception ou probabilité non finie refusée au gardien (motif dit),
   pour les trois bras et les témoins (I26).
2. `FICHIERS_GELES` étendu à `pole/ideation.py` et `pole/tests_de_mort.py`, et à tout autre module qu'un essai de fermeture **pendant
   une course** (modules du dépôt présents dans `sys.modules` après une course à blanc) trouverait (I27).
3. Lecture : `issue_a4 = « non lue (arrêt) »` quand le relevé porte un arrêt ; `n1 = « arret »` pour un relevé invalide qui porte un
   arrêt ; une ligne de tranche dans un contexte servi → relevé invalide (I28, I29, mineur 29).
4. `preparer_bac` : dossier temporaire retiré quand la sonde refuse (mineur 34).
5. Puis : bloc des empreintes recalculé, essais et banc rejoués, une répétition à blanc dans le vrai bac, contre-lecture courte du
   diff v62 → v63 avec le brouillon 4.

Aucun point de ce rapport ne demande d'appel de modèle ni de dépense.
