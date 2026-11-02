# Rapport de rédaction — tour fermé, brouillon 3 et code `_v62` (étage 1 seul)

2 novembre 2026, lecture à partir de 13:05 UTC environ, premier fichier écrit à 13:32, rapport à 13:58 UTC. Rédacteur-développeur neuf : je n'ai écrit ni les contre-lectures 1 et 2, ni les
brouillons 1 et 2, ni le code `_v61`. Aucun appel de modèle, aucune clé, aucun réseau, aucun commit, aucun `git fetch`, aucun
`.sha256` écrit dans le dépôt, aucune ref `donnees/*` ni `calcul/*` ; calculs sous `nice -n 10` ; fichiers neufs seulement (R12).
Dépôt à la tête `82ad7a8` ; `git status` ne montre que les huit fichiers neufs ci-dessous. Dépôt privé : `CLAUDE.md` seulement.

## 1. Verdict

Code `_v62` écrit pour l'étage 1 (B7, B8, B9 et C8 à C22 de la contre-lecture 2), essayé (39 essais), passé au banc (24 mutations
tuées sur 24 pour la raison attendue) et rejoué à blanc dans le vrai bac sur 5 racines, **les doublures scriptées branchées sur le
chemin réel** (aucun canal hors bande). Brouillon 3 construit (couples T19 à T63 de l'étage 1, zones de l'étage 2 hors de ce
scellement, plan de l'étage 1, 81 empreintes v62). **Non scellable encore** : troisième contre-lecture neuve (texte et code v62), mot
de Lazar sur D2, D3, D4, D6, D7, D9 et sur la portée, configuration v3 et GO à 15 USD (marqueurs).

## 2. Fichiers neufs

| fichier (depuis `orchestrator/`) | sha256 |
|---|---|
| `pole/tour_ferme_v62.py` | `0af0f759a45cf90b769908d0fb72a2837f18994859651444fc280dc5127c3c99` |
| `pole/evaluateur_lois_v62.py` | `26613fe72da7f049d5dd076aab51a3808221bf52686b9d0258a201c8b38b8632` |
| `pole/lecture_tour_ferme_v62.py` | `c7f6ebc8ea0cb24ed97a45362361ab9c9b3a17f0e88d43aeb914617eafd8387a` |
| `demonstrations/tour_ferme_v62.py` | `702250e351e53902028b8fb82970a3c4139e6b87cbe67f9fe66fa27186665d06` |
| `demonstrations/lire_tour_ferme_v62.py` | `e18e9858dc23623e3d00a218373a9b72c736145c2b8478e224defe22ec8bb2a9` |
| `essais/test_tour_ferme_v62.py` | `a34b859e42deadb4cc63f2558bab19b021469c8759c4df579e6ab869c940ca59` |
| `essais/mutations_tour_ferme_v62.py` | `ec6ea387c2cb01ca2280023bd703a0d1d99035d8494dd2932a93d80019ea5852` |
| `prereg/preenregistrement-tour-ferme-v1-brouillon3.md` (717 lignes) | `de068ec4222494bafc942b0b5acb7626b40f13479898baf1ad54892cd51c638b` |

Hors de l'arbre (bloc-notes `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/tf62/`) :
`construire_brouillon3.py` (`cc7a6dc2b36d501da177eb23b3d1fcfc0e1b0ff566e80ff6241c22e189384b7f` ; le brouillon 3 = brouillon 2
`37ae595f…` vérifié à l'octet + 86 remplacements, chaque cible présente une fois au moment de son application, 16 marqueurs distincts
avant et après), `couples_cl2.json` (les 45 couples extraits de la contre-lecture 2, `b6d7e8cc…`), `courir_blanc.sh` (`567c7e59…`),
`resumer_repetitions.py` (`59564136…`), `repetitions_v62.json` (`7578e83f…`), relevés des répétitions `blanc-<racine>/`.

## 3. Constats de la contre-lecture 2

| constat | état | où |
|---|---|---|
| **B7** loi non servie | **appliqué** : texte du test = loi gelée en JSON canonique (≤ 2 000 caractères ; refus motivé au gardien au-delà) ; évaluateur de référence copié dans la tranche et nommé dans les données ; tout arrive par le préenregistrement court | `pole/tour_ferme_v62.py:295` (`texte_du_test`), `:600` (`creer_tranche`), `:371` (`garder`) ; `pole/evaluateur_lois_v62.py` |
| **B8** grammaire non servie | **appliqué** : grammaire exacte (6 types, champs, formules, bornes, un exemple valide par type) dans le contexte, consigne qui la nomme ; le gardien tient exactement cette grammaire (types, champs exacts, structure, bornes de sûreté, taille) pour tous les bras et témoins ; borne ±4 au gabarit des proposeurs | `:85` (`GRAMMAIRE`), `:132`, `:225` (`verifier_loi_servable`), `:353`, `:435` |
| **B9** T1 manqué sur course saine | **appliqué** : lectures attendues = toutes les (bras, g), 2 ≤ g ≤ `plan.generations`, jouées ou non | `pole/lecture_tour_ferme_v62.py:145` |
| I10 arrêts non scellés | **appliqué** : toute exception d'une génération → `ArretTour` + relevé partiel ; proposeur non « ok », refus R-764, modèle servi non conforme → arrêt ; le lanceur rattrape toute exception après le manifeste (code 3, rapport scellé) | `pole/tour_ferme_v62.py:403`, `:907` ; `demonstrations/tour_ferme_v62.py:405` |
| I11 trois lectures du désaccord | **appliqué** par T40, T42, T63 : un désaccord du contre-calcul, une session en échec, un refus de modèle **arrêtent** la course | brouillon 3 l. 95, 443, 446 |
| I12 parts des relais | **appliqué** : `plafond_kimi_usd: 12`, `plafond_argon_usd: 3` au plan (somme = plafond, au centime) ; parts transmises aux portes ; compteur par relais ; arrêt avant un étage si part restante < pire cas (cartes × 0,5 USD pour l'expérimentateur, × 0,1 pour le vérificateur : appliqué autrement que « × 0,6 pour chacun », qui compte deux fois) ; « budget_depasse » d'un relais (coût sous le plafond passé, ou part épuisée) → arrêt | `pole/tour_ferme_v62.py:177`, `:534` ; lanceur `:119`, `:247` |
| I13 marqueurs dans la vue | **appliqué** (T23, T56 à T60) | brouillon 3 l. 56, 689 à 700 |
| I14 précision | **appliqué** : pleine précision exigée (texte du test), évaluateur qui écrit `repr`, choix gardé : désaccord → arrêt ; essai « arrondi à 4 décimales » : arrêt si l'écart dépasse 10⁻⁶ | `:295` ; `essais/test_tour_ferme_v62.py` (`PleinePrecision`) |
| I15 expérimentateur non aveugle | **appliqué** : identifiant `F-<12 hex>` (empreinte de l'identifiant réel) pour toute carte et tout témoin, titre et hypothèse neutres, correspondance au relevé | `:324`, `:329` |
| I16 P4 sous D7 | **appliqué** (T28 + cas intermédiaire écrit : archive vide en génération 2 → bande 1 à 8) | lecture `:120` ; brouillon 3 l. 182 |
| I17 A4 sans carte réelle | **appliqué** : « non mesurable (aucune carte réelle jugée) » | lecture `:175` |
| I18 point (3) de S1 | **appliqué** : `recherche_loi_plantee` calculée par le cœur sur chaque contexte servi (paramètres de L* exacts et à deux décimales, comparés en nombres ; épisodes de tranche dans les contextes) ; absente ou mal formée → relevé invalide | cœur `:469`, `:907` et suivantes ; lecture `:68` |
| I19 garde 6 sans cas sain | **appliqué** : cas sain complet accepté ; artefacts sceau faux, marqueur hors zone, empreinte de code, zone ouverte, « brouillon », hors du dossier, entropie | `Garde6Complete` |
| I20 aucune commande de lecture | **appliqué** : `demonstrations/lire_tour_ferme_v62.py` (sceau, empreinte facultative, jamais d'écrasement) | |
| I21 « ne substitue aucun plafond » | **appliqué** (T53) | brouillon 3 l. 570 |
| I22 machine jetable | **appliqué** : mode réel = `os.environ` + `environnement_permis` de la configuration, vérifiés avant tout appel et passés à l'étage | lanceur `:206`, `:365` |
| I23 recopie de g sur le bilan de g | **appliqué** (C19) : la recopie de g lit le bilan réel de g−1 | cœur `:858` |
| I24 monde non gelé | **appliqué** : clé `monde_sha256` au plan (et constante à blanc), comparée avant tout appel | lanceur `:199` |
| mineurs 11 à 21 | 11 (T19, T47), 12 (T20, T21, T61), 13 (T22 autrement), 14 (T26 autrement : le code annonce 768 Mo), 15 (T30 ; T32 autrement), 16 (T34), 17 (T44), 18 (T48, T49), 19 (T50 + calcul au cœur `:817`), 20 (T54), 21 (C21 : « claude-sdk » en mode réel) : **appliqués** | |
| mineur 22 durée | **dit** (T42) ; code inchangé (un étage en cours n'est pas interrompu) | |
| mineur 23 `--verifier-seulement` | **appliqué** : portes non relancées, dossier de sessions retiré | lanceur `:230` (`transmettre`) |
| mineur 24 | **appliqué** : propositions au-delà de 6 comptées (`ignorees_au_dela_du_maximum`) ; copie de la tranche vérifiée contre l'index avant le contre-calcul | cœur `:582` |
| mineur 25 (étage 2) | **hors périmètre (étage 2)** | |

Ajouts de code non demandés mot pour mot, à contre-lire : (1) gardien = `a_blanc_v59.garder` **plus** la grammaire servie (types,
champs exacts, structure : `par_sous_population` couvrant les deux sous-populations ou à `defaut`, indices de traits 0 ou 1 ; bornes
de sûreté 50 pour inclinaison, amplitude, puissance), le même pour tous ; sans cela une loi « valide » pour `valider_loi` (champ
inconnu, `calendrier`, sous-population sans loi, inclinaison 10³) faisait planter le juge ou ouvrait un canal de texte libre vers
l'expérimentateur ; la borne ±4 ne vaut que pour les propositions (T-F4 a un poids de −4,1) ; (2) le proposeur scripté ajuste une
softmax sur les épisodes de développement servis (il ne connaît plus L*, que la v61 lui passait hors bande).

## 4. Couples T19 à T63

Appliqués tels quels (ligne du brouillon 3) : T19 (3), T20 (42), T21 (45), T23 (56), T24 (119), T25 (128), T27 (146), T28 (182),
T29 (223), T30 (229), T31 (252), T33 (404), T34 (427), T35 (438), T36 (439), T37 (440), T38 (441), T39 (442), T40 (443), T41 (445),
T42 (446), T43 (447-448), T44 (460), T45 (462), T46 (489), T47-T49 (504), T50 (514), T51 (554), T53 (570), T54 (598), T56 (689),
T57 (691), T58 (692), T59 (697, en zone), T60 (700), T61 (711), T62 (716), T63 (95). Les cellules « à écrire (v62) » de T35, T36,
T40, T42, T43 et la phrase de T50 ont ensuite été mises à jour avec les essais v62 qui existent (suites dites dans le script).

Appliqués autrement :
- **T22** (54) : la v62 sert des identifiants opaques ; la phrase « l'identifiant … dit sa génération et son auteur » serait fausse.
- **T26** (142) : le code v62 passe `memoire_mo = 768` à l'étage : la consigne annonce la borne tenue.
- **T32** : la section 5.6 est hors de ce scellement ; N1 et sa variante d'arrêt vont dans une **section 4.8 nouvelle** (254), avec
  deux phrases au mentor pour « tient » (contre-lecture 2, section 7.A.3 : « une phrase au mentor pour l'issue de l'étage 1 seul est à
  écrire ») : **texte neuf, à contre-lire**.
- **T52** (565), **T55** (688) : D8 n'est plus au plan gelé (étage 2) ; seuls D7 et D9 y sont lus.

Hors périmètre (étage 2) : aucun couple n'a été refusé ; la section 5, S3, S4, la commande de l'étage 2, le bullet de portée de
l'étage 2, D5 et D8 de la section 14 et le plan de l'étage 2 sont entre balises `etage-2-hors-scellement` (7 zones), non corrigés ;
la garde 11 est marquée « étage 2 : hors de ce scellement » dans sa cellule (une balise couperait le tableau).

Marqueurs : 16 distincts, avant et après. Hors des zones (à remplir avant de sceller l'étage 1) : `<<DECISION_D2>>`, `D3`, `D4`, `D6`,
`D7`, `D9`, `<<CASE_CONFIGURATION_V3>>`, `<<CASE_GO>>` (deux fois). Dans les zones : `D5`, `D8`, `Q`, `E0`, `R`, `T`, `M2`, `V` (deux
fois). Vérifié : le brouillon 3, marqueurs hors zone remplis par des valeurs d'essai et scellé dans un dossier temporaire, passe
`lire_preenregistrement` du lanceur v62 (81 empreintes égales, plan de l'étage 1 lu).

## 5. Changements de code C8 à C22

C8 à C21 : appliqués pour l'étage 1 (tableau de la section 3). C13 : « plan par étage pour `go` et `configuration_sha256` » sans objet
(étage 1 seul). C22 : 5 racines, section 7 ci-dessous.

## 6. Essais et banc (commandes exactes, depuis `orchestrator/`)

- `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_tour_ferme_v62.py` : **39 réussis en 53,8 s**, code 0
  (vrai bac compris : `BacReelV62`, `bwrap` 0.9.0, identité 64097). Classes : `EvaluateurDeReference`, `ServiceDeLaLoi` (C8),
  `GrammaireServie` (C9), `Aveugle` (C15), `Garde7`, `ProposeurChemin` (C12), `PartsDesRelais` (C13), `PleinePrecision` (C14),
  `EtageV62` (C21), `PlanEtage1`, `Garde6Complete` (C17), `MachineJetable` (C11), `MondeGele` (C20), `RefusAvantToutAppel`,
  `CourseSaine` (C8, C9, C15, C18, C19 sur une course du chemin réel), `CourseMuette` (B9 : relevés produits par le cœur, bras réel
  muet en génération 1 puis en générations 1 et 2 → « tient » ; la lecture v61 du second dit T1 manqué), `Arrets` (session en échec,
  refus R-764 d'un proposeur, gains arrondis à 2 décimales, gains fabriqués, part de relais → code 3, relevé partiel scellé, `n1 =
  arret`), `LectureV62`, `Fermeture`, `BacReelV62`.
- `nice -n 10 python3 -I -B essais/mutations_tour_ferme_v62.py` : **24 mutations, 24 tuées pour la raison attendue**, 0 survivante,
  témoin 32 essais avant et après, 99 s, code 0. Une première passe avait 2 mutations de la garde 6 « tuées pour une autre raison »
  (la fonction recompilée lit une copie des globales : le dossier temporaire n'était pas vu) : `lire_preenregistrement` prend
  désormais le dossier en paramètre d'essai ; repassées : tuées pour la raison attendue.
- Essais v59 à v61 : non rejoués ici (aucun de leurs fichiers n'a changé).

## 7. Répétition à blanc dans le vrai bac (C22)

`nice -n 10 python3 -I -B demonstrations/tour_ferme_v62.py SORTIE --etage 1 --a-blanc --graine G --bac reel --utilisateur-bac 64097`,
une course à la fois (deux lancées en parallèle ont été refusées par la sonde, verrou de l'identité dédiée, code 2 en 0,7 s : garde 3
juste ; relancées seules) :

| racine | code | durée | issue | A4 | réel jugées / PS / VD / FD / refus | aléatoire jugées / PS / FD | recopie jugées / PS | non concluant | consignes avec loi |
|---|---|---|---|---|---|---|---|---|---|
| 20261102 | 0 | 97,8 s | tient | discrimine | 36 / 12 / 12 / 0 / 0 | 36 / 1 / 0 | 24 / 0 | 0 | 60 / 60 |
| 20261103 | 0 | 102,1 s | tient | discrimine | 36 / 12 / 12 / 0 / 0 | 36 / 1 / 0 | 24 / 0 | 0 | 66 / 66 |
| 20261104 | 0 | 107,5 s | tient | discrimine | 36 / 12 / 12 / 0 / 0 | 36 / 2 / 0 | 24 / 0 | 0 | 66 / 66 |
| 20261105 | 0 | 127,3 s | tient | discrimine | 36 / 12 / 12 / 0 / 0 | 36 / 1 / 0 | 24 / 0 | 0 | 60 / 60 |
| 20261106 | 0 | 110,3 s | tient | discrimine | 36 / 12 / 12 / 0 / 0 | 36 / 1 / 0 | 24 / 0 | 0 | 64 / 64 |

13:41 à 13:52 UTC, 0 USD. S1 « trop beau » déclenché partout (la softmax ajustée sur 200 épisodes atteint D ≤ 0,05 en génération 1 :
attendu à blanc) ; 0 touche de L* sur 6 contextes cherchés par course ; P4 « informative ». Code : la racine 20261104 a couru sur le
code final (81 empreintes égales) ; les quatre autres sur un lanceur antérieur d'une seule modification (paramètre d'essai
`dossier_prereg` de `lire_preenregistrement`, chemin réel seulement) ; cœur, évaluateur, lecture identiques. Limite dite : les
doublures ne reçoivent que ce que reçoivent les modèles, mais restent des doublures ; les adaptateurs réels (commandes des relais,
portes, contrôle du modèle servi) ne sont essayés ici qu'à leur interface (`ProposeurChemin`, `PartsDesRelais`), pas de bout en bout.

## 8. Ce qui reste avant le scellement

1. Troisième contre-lecture R2 neuve, sur le brouillon 3 et le code v62 (fichiers : ce rapport, le brouillon 3, les sept fichiers de
   code et d'essais ci-dessus, `construire_brouillon3.py`, la contre-lecture 2 ; à lire en priorité : la section 4.8 neuve, le gardien
   élargi à la grammaire, le cas intermédiaire de P4, le pire cas par relais).
2. Mot de Lazar : portée (étage 1 seul, défaut sous 48 heures), D2, D3, D4, D6, D7, D9 ; cases `<<CASE_CONFIGURATION_V3>>`
   (configuration v3 à `budget.plafond_usd` = 15 et relais Kimi et Argon) et `<<CASE_GO>>` (GO de type calcul, exactement 15 USD).
3. Session-depot : `bwrap` 0.9.0 et identité dédiée sans privilège ; machine jetable (`POLE_MACHINE_JETABLE_V56=1`, environnement dans
   la liste blanche ou `environnement_permis`) ; un passage `--verifier-seulement` avec la vraie configuration.
4. Après commit des fichiers v62 : revérifier le bloc des empreintes à la nouvelle tête ; scellement par le directeur, commit et
   poussée avant la course ; puis lecture par `demonstrations/lire_tour_ferme_v62.py` et verdict par un lecteur neuf (R13).
5. Étage 2 : préenregistrement à part (texte des zones, cœur, garde 11, GO et configuration à 5 USD).
