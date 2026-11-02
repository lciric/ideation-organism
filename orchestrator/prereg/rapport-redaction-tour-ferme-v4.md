# Rapport de rédaction — préenregistrement du tour fermé, brouillon 4, et code `_v63`

Rédigé le 2 novembre 2026, de 17:11 à 18:24 UTC (heures de `date -u`), par un quatrième sous-agent rédacteur-développeur, neuf :
il n'a écrit ni le préenregistrement, ni le code `_v61` ou `_v62`, ni aucune des trois contre-lectures. Aucun appel de modèle ni de
réseau, aucune clé, aucun commit, aucun `git fetch`, aucun `.sha256` dans le dépôt, rien sous `donnees/`, **aucun fichier existant
modifié** (règle R12 : tout ce qui suit est neuf) ; Python par `nice -n 10 python3 -I -B`, pytest avec `-p no:cacheprovider`.
Fichiers temporaires sous le dossier de travail du rédacteur (`/tmp/claude-0/…/scratchpad/tour-ferme-v63/`), sauf ce que
l'identité dédiée du bac exige sous `/tmp` (section 8). Les fichiers `*attaque_goodhart_v3*` et
`rapport-redaction-attaque-goodhart-v3.md`, d'un autre agent, n'ont été ni ouverts ni touchés.

## 0. Verdict

- **Brouillon 4 écrit, non contre-lu, non scellé** : `prereg/preenregistrement-tour-ferme-v1-brouillon4.md` (sha256
  `55e4e98571eb39de939e955babd36d58094b45c5da0cf8092e8fe97b8463ca78`, 726 lignes). Portée et décisions D2 à D9 prises par Lazar
  (GO-2026-11-02-18) ; GO de calcul GO-2026-11-02-19, exactement 15 USD. Hors des zones de l'étage 2, **un seul marqueur reste :
  `<<CASE_CONFIGURATION_V3>>`** (empreinte de la configuration v3, chez la session-depot).
- **Code `_v63`** (I26 et I27 en option A ; I28, I29, I30, I31 ; mineurs 29, 30, 34) : **83 essais v63, tous passés** ; **banc v63 :
  69 mutations, 69 tuées pour la raison attendue**, dont les six survivantes de B10 ; **course à blanc dans le vrai bac : code 0,
  127,3 s** ; lecture v63 rejouée sur son relevé : « tient ».
- Reste avant le scellement : la contre-lecture R2 courte et neuve (section 11 ci-dessous), la case de la configuration v3, le
  commit des fichiers `_v63` puis la revérification du bloc d'empreintes.

Erreur trouvée en route, corrigée avant écriture : le texte d'I30 disait d'abord qu'Argon « tient jusqu'à ≈ 2,5 fois » la session
de vérificateur supposée ; rejoué, il tient jusqu'à ≈ 0,09 USD par session (≈ 4,5 fois) ; le brouillon 4 porte le chiffre rejoué.
Changement non demandé mot pour mot : section 14, point (4), la session-depot doit fournir un TMPDIR que l'identité dédiée
traverse (constat de la course à blanc, section 8).

## 1. Entrées lues (empreintes vérifiées)

| fichier | sha256 |
|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon3.md` | `de068ec4222494bafc942b0b5acb7626b40f13479898baf1ad54892cd51c638b` |
| `prereg/contre-lecture-preenregistrement-tour-ferme-v3.md` | `0ecd37a2ff0c247752dcc97921cb207d6c6a49714846f01cf06907a694a4ff45` |
| `prereg/couples-contre-lecture-tour-ferme-v3.json` | `7aa25f19b9f476e083b89a2175458d4523a968b5f24df218f784c90c36494c03` |
| `prereg/rapport-redaction-tour-ferme-v3.md` | `4d4315bb0a47d6bbe71538f90ee007c8952422e7dde13904cc6565239819a8c7` |
| `pole/tour_ferme_v62.py` | `0af0f759a45cf90b769908d0fb72a2837f18994859651444fc280dc5127c3c99` |
| `pole/lecture_tour_ferme_v62.py` | `c7f6ebc8ea0cb24ed97a45362361ab9c9b3a17f0e88d43aeb914617eafd8387a` |
| `pole/evaluateur_lois_v62.py` (gardé tel quel dans le bloc v63) | `26613fe72da7f049d5dd076aab51a3808221bf52686b9d0258a201c8b38b8632` |
| `demonstrations/tour_ferme_v62.py` | `702250e351e53902028b8fb82970a3c4139e6b87cbe67f9fe66fa27186665d06` |
| `demonstrations/lire_tour_ferme_v62.py` | `e18e9858dc23623e3d00a218373a9b72c736145c2b8478e224defe22ec8bb2a9` |
| `essais/test_tour_ferme_v62.py` | `a34b859e42deadb4cc63f2558bab19b021469c8759c4df579e6ab869c940ca59` |
| `essais/mutations_tour_ferme_v62.py` | `ec6ea387c2cb01ca2280023bd703a0d1d99035d8494dd2932a93d80019ea5852` |

Sondes de la contre-lecture 3 (dossier de travail du contre-lecteur) : lues, jamais modifiées.

## 2. Décisions appliquées

- **Directeur** : I26, option A (gabarit et gardien exigent des indices entiers ; le gardien évalue la loi sur un petit jeu factice
  avant le juge ; toute exception → refus au gardien, jamais un plantage du juge ni un arrêt) ; I27, option A (aucun module exécuté
  pendant la course hors du bloc gelé ; essai de fermeture **pendant une course** à blanc).
- **Lazar, 2 novembre 2026, 17:24 UTC** : GO-2026-11-02-18 — portée : étage 1 seul ; D2, D3, D4, D7, D9 et la seconde partie de D6
  acceptées telles qu'écrites ; D5, D8 et la première partie de D6 reportées au texte de l'étage 2. GO-2026-11-02-19 — GO de
  calcul, plafond exactement 15 USD ; I30 corrigé **sous** 15 USD, sans plafond ni part relevés, justifié par le devis (section 7).

## 3. Constat par constat : où c'est fait

Lignes du brouillon 4 entre parenthèses (« l. »). Banc : `essais/mutations_tour_ferme_v63.py` (groupes `PORTEES_V62` l. 50,
`SONDES_CL3` l. 106, `CORRECTIONS_V63` l. 150).

| constat | ce qui est fait | code (fichier:ligne) | essais (cas sain et artefact) | banc | texte |
|---|---|---|---|---|---|
| **B10** (R5 sur le code gelé, gardes 5, 13, 14) | gardes essayées sur la v63 seule, à l'unité, de bout en bout (5 et 13) et au bord de chaque seuil ; les six mutations survivantes de la contre-lecture portées au banc et tuées, plus 10 mutations de bord | aucun changement : `Compteur.ajouter` `pole/tour_ferme_v63.py:221-231`, `Compteur.verifier_duree` `:243`, T2 à T5 `pole/lecture_tour_ferme_v63.py:171-184` (lignes de la v62) | `essais/test_gardes_tour_ferme_v63.py` : `Garde5PlafondEtage` (l. 65), `Garde5DeBoutEnBout` (l. 82), `Garde13Duree` (l. 109), `Garde13DeBoutEnBout` (l. 123), `Garde14T2` (l. 161), `Garde14T3` (l. 180), `Garde14T4` (l. 214), `Garde14T5` (l. 247) | 6 sondes + 10 bords tués (sortie et raisons : section 8) | T85 (l. 449), T98 (l. 437), T99 (l. 445), T100 (l. 446) |
| **I25** (critère attribué à un module non gelé) | T64, T65, T66 appliqués à la lettre puis portés sur la v63 (lecture et lanceur v63) ; le programme de lecture refuse un relevé d'une autre version du cœur | `demonstrations/lire_tour_ferme_v63.py:28`, `:50-52` | `CourseSaine` (relevé v63 lu) | « lecture v63 d'un relevé d'une autre version du cœur » tuée | l. 218, 41, 44 |
| **I26** (gardien : loi que le juge ne sait pas évaluer) | option A : (1) indices entiers (`type(x) is int`) et seuil fini, au gabarit et au gardien, motif propre ; (2) jeu factice fixe de 98 instances (traits jusqu'à ±8, deux sous-populations) : chaque nœud par `selection_pari.proba`, la loi entière aussi par l'évaluateur servi (écart ≤ 10⁻⁹) ; exception, probabilité non finie, négative ou hors du simplexe → refus au gardien ; (3) aucune exception qui remonte (vérification, gardien v59, extraction : `RecursionError`) ; grammaire servie qui le dit ; doublures « indice_flottant », « seuil_infini » | `pole/tour_ferme_v63.py:117-166` (grammaire), `:260-358` (`_entier`, `verifier_loi_servable`, `_verifier_noeud`), `:360-401` (`JEU_FACTICE_DU_GARDIEN`, `noeuds_de_la_loi`, `evaluer_sur_jeu_factice`), `:480-498` (`garder`), `:504-512` (`extraire_propositions`), `:1127-1170` (doublures) | `GardienEntiers` (l. 283), `GardienJeuFactice` (l. 329 : 6 exemples, 150 lois au hasard, 30 `loi_aleatoire`, témoins : aucun refus à tort), `AucuneExceptionQuiRemonte` (l. 372), `CourseIndiceFlottant` (l. 398 : la loi `{"indice": 1.0}` de la contre-lecture et un seuil infini → refus au gabarit, course au bout, code 0) de `essais/test_tour_ferme_v63.py` | 10 mutations « I26 » tuées | T93 remplacé par sa version v63 (l. 134) ; 4.1 (l. 118) ; garde 8 (l. 440) |
| **I27** (modules exécutés hors du bloc) | option A : bloc = fermeture statique des imports des deux programmes (arbre syntaxique, imports tardifs, fichiers chargés par chemin : 91 fichiers) ⊇ fermeture mesurée pendant une course (processus neuf ; chargement, course à blanc par le chemin réel, lecture, `--verifier-seulement` du chemin réel ; `sys.modules` et espion de `spec_from_file_location`) ; `pole/ideation.py`, `pole/tests_de_mort.py` dans le bloc ; les 8 fichiers que seule la fermeture statique ajoute sont importés par des chemins non joués | `demonstrations/tour_ferme_v63.py:69-96` (`FICHIERS_GELES`) ; aucun changement du cœur | `Fermeture` (l. 1270 : égalité exacte), `FermetureEnCourse` (l. 1327 : rien hors du bloc ; les deux modules chargés pendant la course ; artefact : bloc v62), `Garde6Complete` (l. 683 : bloc sans `pole/ideation.py` refusé) | 3 mutations « I27 » tuées | T69 remplacé par sa version v63 (l. 598) ; bloc recalculé (l. 600-692) |
| **I28** (issue A4 lue sur un arrêt) | relevé d'arrêt : `issue_a4` = « non lue (arrêt) », `cause_a4` nulle, `chiffres_partiels` ; relevé d'arrêt invalide : idem | `pole/lecture_tour_ferme_v63.py:46-47`, `:203-205`, `:255`, `:303` | `LectureV63`, `Arrets`, `ArretEnGeneration2` (le cas de la sonde : refus R-764 en génération 2 après une génération 1 complète → code 3, A4 non lue), `Garde5DeBoutEnBout` | « I28 » tuée | T76 (l. 451), 4.7 (l. 251) |
| **I29** (trouvaille hors de S1 sans conséquence) | ligne de tranche dans un contexte servi → `DefautDeCourse` : « ne tient pas (relevé invalide : défaut …) », aucune issue A4, champ `defaut` ; touche de L* → `audit_avant_lecture` (avec S1, S2, S5) | `pole/lecture_tour_ferme_v63.py:55-56`, `:84-94`, `:239-248`, `:302-304` | `LectureV63` ; `FuiteDansLesContextes` (l. 1046 : fuite simulée de bout en bout, 400 lignes trouvées, course invalide) | « I29 » tuée | T77 (l. 403), section 6 (l. 403) |
| **I30** (devis : fin de course à une carte près) | borne de l'expérimentateur **0,30 USD par carte** écrite d'avance, passée à l'étage (`budget_test_usd`) qui la tient ; pire cas avant chaque étage calculé avec elle ; parts 12 et 3 USD et plafond 15 USD inchangés | `pole/tour_ferme_v63.py:111-112`, `:755-756`, `:766`, manifeste `:1075-1076` ; étage : `pole/tests_de_mort_v5.py:460-479` (inchangé) | `ReservationI30` (l. 575), `EtageV63` (l. 632) ; `DevisI30` (`essais/test_gardes_tour_ferme_v63.py:308`) | 3 mutations « I30 » tuées | T78 (l. 554), 4.1 (l. 146), devis (l. 548, 552, 554, 555) |
| **I31** (gardes 7, 8, 9 prouvées par des essais v61) | gardes essayées sur la v63 ; le refus d'un témoin dans la sélection (survivant en v62) essayé | inchangé : `pole/tour_ferme_v63.py:875` (sélection), `:923` (`exiger_sans_temoin`), `:462-470` (gabarit), `:645` (familles) | `Garde7` (l. 433), `Garde7Selection` (l. 444), `GrammaireServie` (l. 232), `Garde8Course` (l. 489), `Garde9` (l. 504), `RefusAvantToutAppel` (l. 762) | 3 « I31 » + la sonde « témoin dans la sélection » tuées | T82, T83, T84 (l. 439-441) |
| mineur 26 (graines) | T67 appliqué puis porté sur `tour-ferme-v63` | `VERSION` `pole/tour_ferme_v63.py:84` ; manifeste `regle_des_graines` | courses d'essai | — | l. 459 |
| mineur 27 (commande de lecture) | T68 appliqué puis porté sur la v63 | `demonstrations/lire_tour_ferme_v63.py` | `CourseSaine` | — | l. 488 |
| mineur 28 (portée) | T70 à T75, T89, T90 appliqués, puis les décisions de Lazar | — | — | — | l. 7, 9, 15, 243, 710, 721-725 |
| mineur 29 (phrases au mentor ; `n1`) | T79 à T81, T95, T96 ; un relevé d'arrêt invalide se lit `n1 = arret` | `pole/lecture_tour_ferme_v63.py:303` | `LectureV63` | « mineur 29 » tuée | l. 256-258 |
| mineur 30 (P6, P7, 4.5) | T87, T88 ; la lecture v63 calcule la trajectoire de P7 et les mesures de 4.5 (meilleures D et G du bras réel par génération, refus du gardien par bras et par motif) | `pole/lecture_tour_ferme_v63.py:221`, `:258`, `:268-292` | `LectureV63` | « mineur 30 » tuée | l. 184, 189, 213 |
| mineur 31 (L2b-v62, prédictions) | T86, T91, T92 ; ligne L2b-v63 ajoutée | — | — | — | l. 169, 504, 505, 509 |
| mineur 32 (« claude-sdk ») | T94, gardé dans le paragraphe du code v63 | — | — | — | l. 563 |
| mineur 33 (« toute exception ») | T97 (« v62, C12 ; inchangé en v63 ») | — | — | — | l. 451 |
| mineur 34 (dossier du bac laissé) | sonde refusée : dossier du bac retiré avant que le refus remonte ; tout refus retire aussi le dossier des sessions | `demonstrations/tour_ferme_v63.py:291-307`, `:407-409` | `SondeDuBac` (l. 782), `CheminReelVerifierSeulement.test_sonde_refusee_rien_ne_reste` ; vu en vrai à 18:05:04 UTC (section 8) | 2 mutations tuées | garde 3 (l. 435) |
| mineur 35 (appel de la machine jetable au lanceur) | chemin réel jusqu'à `--verifier-seulement` avec texte scellé, configuration et registre de GO factices : variable absente ou hors liste → code 2 | — | `CheminReelVerifierSeulement` (l. 835) | sonde « appel retiré au lanceur » tuée (par l'essai, plus par un effet du banc) | garde 15 (l. 447) |
| mineur 36 (gardien et recopie) | mesuré : une loi retenue de plus de ≈ 1 863 caractères (mélange à l'uniforme ; ≈ 1 909 tempérée et inclinée), ou deux lois de plus de ≈ 1 925 à elles deux, font une carte de recopie de plus de 2 000 caractères, refusée au seul bras recopie ; limite déclarée, mesurée par S5 et P8, motifs lus | — (pas de changement : la borne est celle de la loi servie) | — | — | 4.1 (l. 125) |
| mineur 37 (`--verifier-seulement` non essayé) | essayé : code 0, rien écrit, aucun dossier temporaire ; GO d'un autre montant (16 USD) → code 2 | — | `CheminReelVerifierSeulement` | — | garde 15 (l. 447) |
| mineur 38 (T-ELIM) | dit pour mémoire | — | — | — | 4.1 (l. 130) |

## 4. Couples T64 à T97, cellules T85, T98 à T100

Construction par un script (`/tmp/claude-0/…/scratchpad/tour-ferme-v63/construire_brouillon4.py`, hors du dépôt) : brouillon 3
vérifié (`de068ec4…`) ; les 33 couples appliqués **à la lettre**, dans l'ordre, chaque cible présente une fois dans le brouillon 3
et une fois à son application ; **point de contrôle : le texte obtenu est celui de la contre-lecture** (715 lignes, sha256
`a6337d96b33201a7fdff9237cfb38b2a4fb57670e6bdd10572bd633ad4300ac4`, contre-lecture 3, l. 391) ; puis les quatre cellules de B10,
les 12 remplacements des décisions de Lazar, 61 adaptations au code v63 (chacune à cible unique, sinon arrêt) et le bloc
d'empreintes recalculé. « Adapté » = le couple appliqué à la lettre puis récrit là où il nomme le code v62 que la v63 remplace.

| couple | constat | ligne | état dans le brouillon 4 |
|---|---|---|---|
| T64 | I25 | 218 | adapté : lecture `pole/lecture_tour_ferme_v63.py` |
| T65 | I25 | 41 | adapté : lanceur v63 |
| T66 | I25 | 44 | adapté : lecture v63 |
| T67 | m26 | 459 | adapté : tâches `tour-ferme-v63|…` |
| T68 | m27 | 488 | adapté : lecture v63, relevé d'une autre version refusé |
| T69 | I27 | 598 | **remplacé** par la version v63 (option A : bloc = fermeture statique ⊇ fermeture mesurée) |
| T70 | m28 | 721 | adapté : code v63, L2b-v63 |
| T71 | m28 | 722 | remplacé : décisions prises (GO-2026-11-02-18) |
| T72 | m28 | 722-724 | adapté : + TMPDIR traversable par l'identité dédiée |
| T73 | m28 | 7-8 | remplacé : décisions prises, GO pris |
| T74 | m28 | 9 | adapté : le GO est pris |
| T75 | m28 | 243 | à la lettre |
| T76 | I28 | 451 | adapté : lecture v63, A4 « non lue (arrêt) » |
| T77 | I29 | 403 | adapté : la lecture v63 applique la règle |
| T78 | I30 | 554 | adapté : borne de 0,30 USD par carte, devis rejoué |
| T79, T80, T81 | m29 | 257, 256, 258 | à la lettre |
| T82, T83, T84 | I31 | 439, 440, 441 | adaptés : essais v63 |
| T85 | B10 | 449 | écrit (la cible étendue à la phrase du banc) |
| T86 | m31 | 504 | à la lettre |
| T87 | m30 | 184 | à la lettre |
| T88 | m30 | 189 | adapté : P7 calculée par la lecture v63 |
| T89 | m28 | 15 | à la lettre |
| T90 | m28 | 710 | adapté : décision D6 de Lazar |
| T91 | m31 | 169 | adapté : + L2b-v63 |
| T92 | m31 | 509 | adapté : + L2b-v63 |
| T93 | I26 | 134 | **remplacé** par la version v63 (option A : gardien v63) |
| T94 | m32 | 563 | adapté : paragraphe du code v63, contenu de T94 gardé |
| T95 | m29 | 256 | adapté : `n1 = arret` de la lecture v63 |
| T96 | m29 | 257 | à la lettre |
| T97 | m33 | 451 | adapté : « inchangé en v63 » |
| T98, T99, T100 | B10 | 437, 445, 446 | écrits (gardes 5, 13, 14) |

Contrôles faits par le script, puis rejoués : 16 marqueurs distincts avant, 9 après ; hors des zones de l'étage 2, seul
`<<CASE_CONFIGURATION_V3>>` ; dans les zones : `<<CASE_E0>>`, `<<CASE_M2>>`, `<<CASE_Q>>`, `<<CASE_R>>`, `<<CASE_T>>`, `<<CASE_V>>`,
`<<DECISION_D5>>`, `<<DECISION_D8>>` ; 7 zones appariées, **identiques à l'octet à celles du brouillon 3** ; plan relu par
`lire_plan` du lanceur v63 (GO-2026-11-02-19 ; 15, 12 et 3 USD) ; le texte, marqueur rempli d'une valeur d'essai, scellé dans un
dossier temporaire du dossier de travail (retiré), accepté par `lire_preenregistrement` du lanceur v63 (garde 6 complète) ; 30
lignes hors zone nomment encore `v62` : historique, « v62, inchangé en v63 », ou `pole/evaluateur_lois_v62.py` (servi tel quel).

## 5. Décisions de Lazar dans le texte

| marqueur ou point | ligne | texte |
|---|---|---|
| statut | 3 | « portée et décisions D2 à D9 prises par Lazar (GO-2026-11-02-18) ; GO de calcul GO-2026-11-02-19, plafond exactement 15 USD » |
| en-tête, section 0 | 7-9, 13 | décisions prises, D5, D8 et la première partie de D6 à l'étage 2 ; portée décidée |
| `<<DECISION_D2>>`, `<<DECISION_D3>>`, `<<DECISION_D4>>` | 699, 701, 702 | « Mot de Lazar : acceptée telle qu'écrite (GO-2026-11-02-18, mot de Lazar du 2 novembre 2026 à 17:24 UTC). » |
| `<<DECISION_D6>>` | 710 | seconde partie acceptée, pas de seconde réplique ; première partie (bras aléatoire de contrôle de l'étage 2) reportée par Lazar au texte de l'étage 2 |
| `<<DECISION_D7>>` | 121, 711 | acceptée telle qu'écrite (même référence) |
| `<<DECISION_D9>>` | 521, 719 | acceptée telle qu'écrite (même référence) |
| `<<CASE_GO>>` | 478, 585 | `GO-2026-11-02-19` dans la commande réelle et dans le plan gelé (GO de calcul de Lazar, plafond exactement 15 USD) |
| section 13, section 14 (3), (6) | 571, 698, 722, 725 | GO vérifié par `configuration_v56.verifier_go_v56` (alias de `configuration_v55.verifier_go_v55` : type, Lazar, validité, révocation, montant exact) ; décisions faites ; GO fait |

`<<DECISION_D5>>` et `<<DECISION_D8>>` restent dans les zones de l'étage 2 (reportées). Le statut reprend la phrase demandée ;
D5, D8 et la première partie de D6 n'y sont pas « prises » : l'en-tête et la section 14 le disent.

## 6. Ce que fait le code v63 (diff v62 → v63, en bref)

- `pole/tour_ferme_v63.py` : gardien v63 (I26), borne de 0,30 USD par carte passée à l'étage et pire cas calculé avec elle (I30),
  `VERSION` = « tour-ferme-v63 », manifeste (`jeu_factice_du_gardien_sha256`, `bornes_par_carte_usd`), doublures « refus:N[,M] »,
  « indice_flottant », « seuil_infini ». Le reste est la v62 (Compteur, sélection, contre-calcul, T1 à T5 côté relevé).
- `pole/lecture_tour_ferme_v63.py` : I28, I29, mineurs 29 et 30 ; T1 à T5 inchangés.
- `demonstrations/tour_ferme_v63.py` : `FICHIERS_GELES` de 91 fichiers (I27), dossiers temporaires retirés sur un refus (mineur 34),
  cœur et étage v63.
- `demonstrations/lire_tour_ferme_v63.py` : lecture v63 ; refus d'un relevé d'une autre version du cœur.

## 7. I30 : la correction et le devis

Lazar : tenir sous 15 USD sans relever ni le plafond ni une part. Correction : la dépense de l'expérimentateur par carte est bornée
d'avance à 0,30 USD (5 tours au prix du devis, 0,06 USD), passée à l'étage v5 (`budget_test_usd`), qui donne à chaque session pour
plafond le reste de la fiche et arrête les tours à la borne (`pole/tests_de_mort_v5.py:460-479`) ; le pire cas contrôlé avant
chaque étage se calcule avec elle (cartes × 0,30 USD pour Kimi, × 0,1 USD pour Argon). Rejoué étage par étage, dans l'ordre du
code, sur le `Compteur` gelé, aux tailles moyennes du devis (cartes réelles testées ≈ 4, 2, 2 ; ≈ 1,5 carte aléatoire et ≈ 2,4
témoins par génération et par bras ; 0,024 USD par appel de proposeur ; vérificateur 0,02 USD) :

| tours par carte | arrêt | dépense de Kimi | marge de Kimi au dernier étage | total de l'étage |
|---|---|---|---|---|
| 2 (0,04 USD le tour) | aucun | 2,61 | 8,86 | 3,31 |
| 4 | aucun | 7,68 | 4,18 | 8,39 |
| 5, 6, 6,5, 8, 12 | aucun (borne atteinte) | 9,58 | 2,42 | 10,29 |
| v62, 6 tours, borne 0,5 | aucun | 11,48 | 0,18 | — |
| v62, 6,5 tours, borne 0,5 | **arrêt** (part de Kimi 0,50 sous le pire cas 1,20) | — | — | — |

Cartes testées de plus que le devis, toutes à leur borne : jusqu'à 8 de plus, la course tient (39,7 cartes, Kimi ≤ 12 USD) ; à
partir de 8,1, arrêt avant l'étage, sans dépassement. Argon : tient jusqu'à ≈ 0,091 USD par session de vérificateur (≈ 4,5 fois
le prix SUPPOSÉ de 0,02 USD) ; arrêt avant l'étage à 0,092. Essai `DevisI30` (6,5 tours ; +8 cartes tient, +9 s'arrête ; règle v62
à 0,18 de marge puis arrêt ; vérificateur à 0,05) ; les seuils exacts ci-dessus ont été rejoués avec la même fonction
`jouer_devis`. **Prix de la borne** : une carte qui demanderait plus de ≈ 5 tours est jugée sur ce qu'elle a exécuté, « non
concluant » sans exécution réussie, compté par T4 (au-delà de 0,20 par bras : « ne tient pas (T4) ») au lieu d'arrêter la course.

## 8. Ce qui a tourné (heures de `date -u`)

- **Banc v63 complet**, 17:55:33 → 18:01:41 UTC : 69 mutations (24 du banc v62 portées sur la v63, 19 sondes et bords de la
  contre-lecture 3, 26 pour les corrections v63) ; **tuées pour la raison attendue : 69** ; autre raison 0 ; défaut du banc 0 ;
  survivantes 0 ; non appliquées 0 ; 367 s ; témoin avant et après restauration : 79 essais, 0 en échec ; code 0. Lecture de
  « a/b essais en échec » : a compte les échecs, sous-essais compris ; b, les essais lancés.
- **Banc des sondes, avec raisons** (`--seulement sonde --raisons`), 18:19:22 → 18:20:15 UTC : 10 mutations (les six de B10, le
  témoin dans la sélection, l'appel de la machine jetable au lanceur, l'étage 2, le dossier du bac), 10 tuées pour la raison
  attendue ; témoin 23 essais, 0 en échec, avant et après. Raisons : T2 à T5 → `Garde14Tk.test_artefacts` (« Tk tient sur
  l'artefact … ») ; plafond → `Garde5PlafondEtage` (« ArretTour not raised ») et `Garde5DeBoutEnBout` (le pire cas de l'étage
  arrête la course, mais pas par le plafond franchi) ; durée → `Garde13Duree`, `Garde13DeBoutEnBout` (code 0 au lieu de 3) ; témoin
  dans la sélection → `Garde7Selection` (la course s'arrête sur un `KeyError`, pas sur le refus écrit) ; machine jetable →
  `CheminReelVerifierSeulement` (code 0 au lieu de 2).
- **Essais de la section 9** (commande exacte du texte), 18:08:38 → 18:10:47 UTC, TMPDIR sous le dossier de travail : 193 essais,
  **190 passés**, 1 sauté (`BacReelV63` : l'identité 64097 ne traverse pas ce TMPDIR, motif dit), 2 en échec (`TestBacReelV59`,
  `TestBacReelV61` : même cause, sonde du bac refusée), 48 sous-essais passés, 127,7 s. Les deux en échec ont laissé leurs
  dossiers de bac sous mon TMPDIR (code v59 et v61, avant le mineur 34) : retirés. Puis, 18:11:15 → 18:12:56 UTC, **TMPDIR=/tmp**
  pour ces trois seuls essais : **3 passés** (99,9 s), aucun dossier resté sous `/tmp`. Essais v63 : 83 (65 dans
  `essais/test_tour_ferme_v63.py`, 18 dans `essais/test_gardes_tour_ferme_v63.py`), **tous passés**. Bancs v59, v60, v61 : non
  relancés (code inchangé ; cités par la section 9).
- **Course à blanc dans le vrai bac** : d'abord avec TMPDIR sous le dossier de travail, 18:05:04 UTC : **refus, code 2**
  (`BacASableIndisponible` : « bwrap: Can't find source path …/travail: Permission denied » ; `/tmp/claude-0` est en `drwx------`),
  aucun dossier laissé, aucune sortie (mineur 34 vu en vrai). **L'identité du bac exige donc `/tmp`** : 18:05:15 → 18:07:24 UTC,
  `TMPDIR=/tmp nice -n 10 python3 -I -B demonstrations/tour_ferme_v63.py …/blanc-20261102 --etage 1 --a-blanc --graine 20261102
  --bac reel --utilisateur-bac 64097` : **code 0, 127,3 s**, 152 cartes, 6 appels de proposeurs (doublures, 0 USD) ; relevé
  `d5d9f0d6fad20d977a7648d7fecc1776053422d6fa08c6f2b506efce3fbff9d7` ; manifeste : commit `9ad3ebe` (arbre modifié), 91 empreintes
  de code égales au bloc ; aucun dossier `bac-tour-ferme-v63-*` ni `tour-ferme-v63-sessions-*` resté.
- **Lecture v63 rejouée**, 18:07:40 UTC (`demonstrations/lire_tour_ferme_v63.py … --releve-sha256 d5d9f0d6…`) : lecture
  `2b19a38174197b22f2bcca4b8ab2ff0580978fd4a27aab58f4603cd3701363a2` ; « tient » (T1 à T5) ; A4 « discrimine » (à blanc,
  exploratoire, sans portée) ; réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0] ; aléatoire jugées/PS/FD [36, 3, 0] ; recopie
  jugées/PS [24, 0] ; non concluant 0 ; 32 contre-calculs concordants, 0 désaccord ; 8 passes de témoins, 6 lectures ; consignes
  d'expérimentateur avec loi 64/64 ; S1 « trop beau » déclenché (doublures voisines de L*, attendu à blanc) et porté dans
  `audit_avant_lecture` ; touches de L* 0 sur 6 contextes, lignes de tranche 0 ; refus du gardien 0 ; P7 : VD du bras réel en
  génération 1 seulement (« décroît » non calculable) ; mesures de 4.5 : meilleure D du bras réel par génération 0,0135,
  0,0149, 0,0078. Ligne L2b-v63 du texte (l. 505).

## 9. Fichiers neufs et empreintes

| fichier | sha256 |
|---|---|
| `pole/tour_ferme_v63.py` | `f3da98027c5184c094ee2d00b0fbba0d3e0f10cfc3393d74871e5a62f5d0faab` |
| `pole/lecture_tour_ferme_v63.py` | `2e2c695abcfe2715ca29101c434346658949a2c86be86ed8f9d6f68a408f94ea` |
| `demonstrations/tour_ferme_v63.py` | `a4a4effe53453137c285c6c8b6bd1b6b2bd2f9cf443f35b6d3035bcf613aa873` |
| `demonstrations/lire_tour_ferme_v63.py` | `62e93d8213e462806db723d4c759b8df79a522bffa4c3f64141c2c50ffeb3a78` |
| `essais/test_tour_ferme_v63.py` | `6236551c3516f95e330c4a71b58671aa6e9d337cf94de6d1cd747213981b5791` |
| `essais/test_gardes_tour_ferme_v63.py` | `a699e90c6f5f6d7fd8631e93cad19942b3df7495a318d0dd665bc1a644f576fb` |
| `essais/mutations_tour_ferme_v63.py` | `9b7f17d9a8649dba5928987895f144a203085d8019c6080e883ccdf216debf2d` |
| `prereg/preenregistrement-tour-ferme-v1-brouillon4.md` | `55e4e98571eb39de939e955babd36d58094b45c5da0cf8092e8fe97b8463ca78` |
| `prereg/rapport-redaction-tour-ferme-v4.md` (ce rapport) | donnée dans la réponse du rédacteur (un fichier ne porte pas sa propre empreinte) |

Bloc d'empreintes du brouillon 4 (l. 600-692) : 91 lignes, égales au disque ; les 87 fichiers suivis sont égaux à `9ad3ebe` **et**
à `d15f489`, commit d'une autre tâche (attaque de Goodhart, A1-v3) daté de 18:18:10 UTC, après l'écriture du brouillon (18:15),
qui ne touche aucun fichier du bloc ; les 4 fichiers `_v63` sont non suivis : à revérifier après commit (la garde 6 refuse tout écart).

## 10. Réserves et limites

1. **TMPDIR** : l'identité dédiée 64097 ne traverse pas le dossier de travail du rédacteur ; la course à blanc et les trois essais
   du vrai bac ont tourné avec `TMPDIR=/tmp` (dit au texte : sections 9, 10 et 14, point (4)). Les deux dossiers
   `/tmp/bac-tour-ferme-v62-*` (13:41:21 et 13:42:59 UTC) datent d'avant cette session (refus v62, mineur 34) : non touchés.
2. **Fermeture mesurée** : course à blanc, lecture et `--verifier-seulement` du chemin réel (exécuteur factice substitué à la
   sonde) ; les sessions des relais, après `--verifier-seulement`, ne sont pas jouées. La fermeture statique couvre leurs imports
   écrits. Seul chargement par chemin hors du bloc trouvé dans les 91 fichiers : `pole/attaque_goodhart_v2.banc()`
   (`demonstrations/banc_tricheurs_v8.py`), appelé seulement par des fonctions de l'attaque (`carte`, `bibliotheque_du_juge`,
   `juger`, `auditer_promues`), jamais par le tour fermé (l'espion ne l'a vu sur aucun chemin mesuré).
3. **Jeu factice** : il prouve l'évaluation sur 98 points, pas sur toutes les instances. Avec les bornes de la grammaire
   (|amplitude| et |inclinaison| ≤ 50, puissance dans ]0 ; 50], débordement d'une softmax ramené à l'uniforme sans exception),
   reste un trou théorique : fréquence et phase d'oscillation proches de 10³⁰⁷–10³⁰⁸ (cos(∞) au-delà des traits du jeu ; instances
   tirées d'une normale centrée réduite). Une borne de la fréquence et de la phase au gardien le fermerait (code nouveau).
4. **I30, prix de la borne** : au-delà de ≈ 5 tours, une carte est jugée sur ce qu'elle a exécuté ; si beaucoup de cartes en
   voulaient plus, T4 (« non concluant » ≤ 0,20 par bras) pourrait manquer : « ne tient pas (T4) » au lieu d'un arrêt. Choix à
   peser par la contre-lecture et Lazar.
5. Sonde « entropie non exigée au chemin réel » hors du banc (un texte scellé d'empreinte < 2⁶⁴ ne se fabrique pas) ; essayée à
   l'unité (`Garde6Complete`).
6. Les en-têtes « Brouillon 4 rédigé … de 17:11 à 18:15 UTC » et « à la tête `9ad3ebe` » sont vrais à l'écriture du texte ; la tête
   est depuis `d15f489` (point 9 ci-dessus).

## 11. Ce que la contre-lecture courte doit vérifier d'abord

1. **I26, gardien v63** (`pole/tour_ferme_v63.py:260-401`, `:480-512`) : entiers et seuil fini au gabarit **et** au gardien ; jeu
   factice (98 instances, `selection_pari.proba` par nœud, évaluateur servi sur la loi entière, 10⁻⁹) ; aucune exception qui
   remonte ; aucune loi légitime refusée (témoins, cartes de référence, lois au hasard ; L2b-v63 : 0 refus) ; le trou de la
   réserve 3 est-il acceptable ?
2. **I27, bloc** : 91 fichiers = fermeture statique (`Fermeture`) ⊇ fermeture mesurée (`FermetureEnCourse`) ; `pole/ideation.py`
   et `pole/tests_de_mort.py` dedans ; faut-il plus pour le chemin réel non joué après `--verifier-seulement` (réserve 2) ?
3. **I30** : borne de 0,30 USD tenue par l'étage (`pole/tests_de_mort_v5.py:460-479`) et utilisée au pire cas (`:755-756`) ;
   devis rejoué sur le `Compteur` gelé (`DevisI30`) ; plafond 15, parts 12 et 3 inchangés ; le prix de la borne (réserve 4).
4. **B10** : `essais/test_gardes_tour_ferme_v63.py` n'importe que le code gelé v63 ; relancer
   `essais/mutations_tour_ferme_v63.py --seulement sonde --raisons` : chaque sonde tuée par l'essai voulu, pas par un effet du banc.
5. **I28, I29, mineurs 29 et 30** (`pole/lecture_tour_ferme_v63.py:46-56`, `:84-94`, `:203-205`, `:239-258`, `:268-304`) : aucune
   issue A4 sur un arrêt ; fuite de tranche → relevé invalide ; T1 à T5 inchangés depuis la v62 (diff) ; course saine toujours
   « tient ».
6. **Les 33 couples** : texte de contrôle `a6337d96…` (celui de la contre-lecture), puis les 61 adaptations v63 : aucune ne change le
   sens d'un couple au-delà du nom du code ; surtout T69 et T93 (remplacés, option A), T76, T77, T78.
7. **Décisions de Lazar** : six marqueurs et `<<CASE_GO>>` remplacés avec la référence exacte ; D6 coupée ; phrase de statut
   demandée ; seul `<<CASE_CONFIGURATION_V3>>` hors zone ; zones identiques à l'octet au brouillon 3.
8. **Table de la section 7** : chaque essai cité existe dans un fichier v63, porte sur le code gelé, et une mutation par cellule
   est tuée (sorties de la section 8).
9. **TMPDIR** pour la course réelle chez la session-depot et pour les trois essais du vrai bac (sections 9 et 14 (4)).
10. **Ligne L2b-v63 et bloc** : rejouer la commande à blanc et la lecture (relevé `d5d9f0d6…`, lecture `2b19a381…`), comparer les
    chiffres ; « aucune prédiction changée après L2b-v63 » ; 91 empreintes (disque ; 87 à `9ad3ebe` et `d15f489`), à refaire
    après le commit des fichiers `_v63`.
