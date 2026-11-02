# Rapport de rédaction — préenregistrement du tour fermé, brouillon 5, et code `_v63` modifié

Rédigé le 2 novembre 2026, de 18:45 à 19:14 UTC (heures de `date -u`), par un cinquième sous-agent rédacteur-développeur, qui
reprend la tâche après un développeur coupé par une panne de crédits (rien de lui dans l'arbre : aucun fichier `_v63` modifié,
aucun brouillon 5 ni rapport v5 au départ). Il n'a écrit ni le préenregistrement, ni le code `_v61` à `_v63`, ni aucune
contre-lecture. Aucun appel de modèle ni de réseau, aucune clé, aucun commit, aucun `.sha256`, aucun `git fetch`, `checkout` ou
`stash`, rien sous `donnees/` ; Python par `nice -n 10 python3 -I -B`, pytest avec `-p no:cacheprovider`, `TMPDIR=/tmp`. Fichiers
existants modifiés : les cinq fichiers `_v63` nommés en section 8, et eux seuls ; deux fichiers neufs (le brouillon 5, ce rapport).
Sorties et scripts de travail : `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/tour-ferme-v63/b5/`.
Les fichiers des autres tâches (`attaque_goodhart_v3`, `_v4`, `juges_idees_v2`, `nul_v9`, `banc_tricheurs_v9`) n'ont pas été
ouverts ; leurs noms seuls ont été vus dans `git status` et `git show --stat`.

## 0. Verdict

- **Brouillon 5 écrit, non contre-lu, non scellé** : `prereg/preenregistrement-tour-ferme-v1-brouillon5.md` (871 lignes, sha256
  `c81aa6ef72255adab76abcffc8e06cc0c570069cf09aa2035c285a54212fc3d3`) ; plan gelé : plafond 50 USD, parts 44 (Kimi) et 6 (Argon),
  durée 24 h, `go: GO-2026-11-02-23` ; borne de l'expérimentateur 0,80 USD par carte ; GO-2026-11-02-19 cité nulle part. Seul
  marqueur hors des zones de l'étage 2 : `<<CASE_CONFIGURATION_V3>>` (une occurrence, clé `configuration_sha256`).
- **Pire cas recalculé sur le `Compteur` gelé** : la course va au bout à trois générations quel que soit le nombre de tours ; à
  12 tours par carte, Kimi ≈ 22,90 USD, marge ≈ 20,91 USD au-delà du pire cas réservé au dernier étage ; devis = 31,7 cartes et
  témoins testés ; 23,2 de plus, toutes à leur borne, tiennent encore (54,9).
- **Essais v63 : 87, tous passés** (68 + 19 ; 23 sous-essais) ; **banc : 72 mutations, 72 tuées pour la raison attendue**, témoin
  83 essais sans échec avant et après ; **course à blanc dans le vrai bac : code 0, 125 s, lecture « tient »**.
- **Écart principal (changement non demandé mot pour mot)** : défaut de conception du chemin réel trouvé et corrigé — les
  proposeurs appelaient leurs relais sous le rôle « proposeur », refusé par tout adaptateur réel : la course réelle se serait
  arrêtée au premier appel (section 3). D'où 72 mutations au lieu de 69 et 87 essais au lieu de 83.

## 1. Entrées lues (empreintes vérifiées)

| fichier | sha256 |
|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon4.md` (lu en entier ; inchangé) | `55e4e98571eb39de939e955babd36d58094b45c5da0cf8092e8fe97b8463ca78` |
| `prereg/rapport-redaction-tour-ferme-v4.md` (lu en entier) | `8dee9d2ae469eeea61f0a3a575e13cfd2659c302ebec47ed9c41c392f536c512` |
| `pole/tour_ferme_v63.py` avant modification (= `af92034`) | `f3da98027c5184c094ee2d00b0fbba0d3e0f10cfc3393d74871e5a62f5d0faab` |
| `demonstrations/tour_ferme_v63.py` avant modification (= `af92034`) | `a4a4effe53453137c285c6c8b6bd1b6b2bd2f9cf443f35b6d3035bcf613aa873` |
| `essais/test_tour_ferme_v63.py` avant modification (= `af92034`) | `6236551c3516f95e330c4a71b58671aa6e9d337cf94de6d1cd747213981b5791` |
| `essais/test_gardes_tour_ferme_v63.py` avant modification (= `af92034`) | `a699e90c6f5f6d7fd8631e93cad19942b3df7495a318d0dd665bc1a644f576fb` |
| `essais/mutations_tour_ferme_v63.py` avant modification (= `af92034`) | `9b7f17d9a8649dba5928987895f144a203085d8019c6080e883ccdf216debf2d` |

Lus aussi (code, sans modification) : `pole/tests_de_mort_v5.py` (étage, `TOURS_MAX_PAR_FICHE` importé de
`pole/tests_de_mort_v2.py:139`), `pole/etage_entre_generations_v56.py`, `_v57.py`, `pole/configuration_v53.py` à `_v56.py`,
`pole/budget_v56.py`, `pole/adaptateurs.py` (commande externe), `pole/adaptateurs_v56.py`, `pole/adaptateur_kimi_v53.py`,
`pole/relais.py`, `pole/a_blanc_v59.py` (`choisir_executeur`), `demonstrations/attaque_goodhart_v2.py`
(`reglages_de_configuration`, `substituer_commandes`), `demonstrations/ideation_v8.py` (`adaptateurs_reels_v56`),
`essais/aides_v56.py`.

## 2. Ce qui change dans le code v63 (fichiers modifiés, pas de v64)

| quoi | où |
|---|---|
| `BUDGET_EXPERIMENTATEUR_PAR_CARTE_USD` = **0,80** (0,30 avant) : couvre les 12 tours du garde-fou au prix prudent de 0,06 USD (0,72) ; commentaire et docstring de tête (point C) récrits ; commentaire du pire cas | `pole/tour_ferme_v63.py:24-31`, `:118-124`, `:799-801` (pire cas `n * borne`, inchangé dans sa forme), `:812` (passée à l'étage) |
| `ROLE_PROPOSEUR` = « proposeur_ideation » ; `ProposeurAdaptateur.proposer` l'emploie | `:125-129`, `:550` |
| `roles_permis`, `paires_de_roles`, `exiger_roles_joues` : chaque adaptateur doit accepter le rôle qu'il jouera, sinon `TourRefuse` | `:669-697` ; docstring point E `:35-40` ; `import sys` |
| doublures : `ROLES_PERMIS` déclarés et tenus (proposeur, expérimentateur, vérificateur), comme les adaptateurs réels | `:1177`, `:1257`, `:1289` |
| lanceur : garde des rôles appelée dans `roles_reels` **avant** la relance des portes et tout appel, et dans `roles_a_blanc` ; docstring | `demonstrations/tour_ferme_v63.py:13-16`, `:30-31`, `:271`, `:294` |
| essais : `ReservationI30` (3 × 0,80 = 2,4 ; 2,4 permis, 2,3 refusé), `EtageV63` et `CourseSaine` (0,80) ; neuf : `RolesDesRelais` (2 essais), `CheminReelVerifierSeulement.test_artefact_kimi_par_protocole` | `essais/test_tour_ferme_v63.py:577-603`, `:604-666`, `:953-962` |
| essais : `DevisI30` récrit au plan du brouillon 5 (4 essais : borne ≥ 12 × 0,06 ; course au bout de 2 à 12 tours et à la borne ; limite 23,2 / 23,3 cartes, vérificateur au prix supposé et à sa borne ; 29 cartes à 12 tours ; historique v62 gardé, plan 15/12/3 passé explicitement) | `essais/test_gardes_tour_ferme_v63.py:11-16`, `:281-349` |
| banc : mutation de borne à 0,30 USD (remplace « relevée à 0,5 USD ») ; 3 neuves pour les rôles | `essais/mutations_tour_ferme_v63.py:194-204` |

Inchangés : `pole/lecture_tour_ferme_v63.py`, `demonstrations/lire_tour_ferme_v63.py`, `FICHIERS_GELES` (91 fichiers ; `import
sys` est de la bibliothèque standard, hors du bloc ; `Fermeture` et `FermetureEnCourse` passent).

## 3. Le défaut des rôles (écart : changement non demandé mot pour mot)

Trouvé en écrivant l'annexe (ce que le chemin réel fait des adaptateurs de la configuration). `ProposeurAdaptateur.proposer`
(v61, v62, v63 du brouillon 4) appelait `self.ad.lancer("proposeur", …)`. Sonde hors du dépôt (`…/b5/sonde_roles.py`, aucun
réseau : `/bin/false`, ouvreur factice) :

| adaptateur réel | « proposeur » | « proposeur_ideation » | « experimentateur_test » | « lecteur_test » |
|---|---|---|---|---|
| `AdaptateurCommandeExterneV56` | **refusé** (`ValueError`) | accepté | accepté | accepté |
| `AdaptateurKimiProtocole` | **refusé** | accepté | **refusé** | **refusé** |

Conséquence en mode réel, brouillon 4 : la `ValueError` du premier appel de proposeur, après le manifeste, est un arrêt (C12) :
code 3, aucune dépense, texte scellé perdu pour un défaut de code. Les doublures acceptaient tout rôle : les courses à blanc ne
pouvaient pas le voir. Et Kimi en `kimi_protocole` (type que `reglages_de_configuration` admet) n'aurait pas pu jouer
l'expérimentateur : arrêt au premier étage, après les proposeurs. Correction : rôle `proposeur_ideation` ; garde des rôles avant
toute porte et tout appel (code 2, vue dès `--verifier-seulement`) ; doublures aux rôles des adaptateurs réels. Essais : cas sain
sur une vraie `AdaptateurCommandeExterneV56` (commande locale qui rend le rôle et le modèle reçus : proposeur, expérimentateur,
vérificateur) ; artefacts : Kimi par protocole, adaptateur sans liste de rôles, rôle « proposeur », doublures hors rôle ; chemin
réel `--verifier-seulement` avec Kimi par protocole → code 2. Trois mutations tuées. Conséquence pour la session-depot : **Kimi
doit être une commande externe** (annexe A, A.6).

## 4. Pire cas, devis et marge (sur le `Compteur` gelé)

Rejeu étage par étage dans l'ordre du code (réel, recopie, aléatoire ; cartes puis témoins ; contrôle du pire cas avant chaque
étage, dépense après), plan 50 / 44 / 6, borne 0,80 USD, vérificateur 0,1 USD au pire cas, aux tailles du devis (cartes réelles
testées 4, 2, 2 ; 1,5 aléatoire et 2,4 témoins par génération et bras ; **31,7 cartes et témoins testés**) ; 6 appels de
proposeur à 0,024 USD ; vérificateur 0,02 USD (SUPPOSÉ). Scripts : `…/b5/devis_b5.py`, `…/b5/devis_course_blanc.py` ; essai
`DevisI30`.

| tours par carte | arrêt | Kimi | Argon | total | marge de Kimi au dernier étage |
|---|---|---|---|---|---|
| 2 (0,04 USD le tour) | aucun | 2,61 | 0,71 | 3,31 | 39,66 |
| 4 | aucun | 7,68 | 0,71 | 8,39 | 34,98 |
| 6 | aucun | 11,48 | 0,71 | 12,19 | 31,46 |
| 8 | aucun | 15,29 | 0,71 | 15,99 | 27,94 |
| **12** | aucun | **22,90** | 0,71 | **23,60** | **20,91** |
| toutes à la borne | aucun | 25,43 | 0,71 | 26,14 | 18,57 |

- Capacité : +23,2 cartes (toutes à leur borne) tiennent, +23,3 s'arrêtent avant l'étage, sans dépassement — vérificateur à 0,02
  ou à sa borne de 0,1 ; à 12 tours au prix du devis, +29,0.
- Comptes exacts de la course à blanc (32 testés, dont 12 cartes réelles en génération 1) : Kimi 23,11 USD à 12 tours (25,67 à
  la borne), marge 20,73 (18,33).
- Partage : 44 / 6 maximise les cartes couvertes au pire cas des deux rôles (optimum 44,39 / 5,61) ; 40 / 10 : +18,2 ; 45 / 5 :
  +24,4, mais +17,5 si le vérificateur atteint sa borne.
- Non couvert, dit au texte : maximum théorique 144 testés (36 + 36 + 24 + 6 × 8), ≈ 130 USD à leurs bornes ; il ne serait atteint
  que si le juge promouvait presque tout ; ce serait un arrêt avant un étage, jamais une carte tronquée.
- Durée : 24 h ne mord avant le plafond de dépense que si la session moyenne dépasse ≈ 93 s (54,9 testés à 12 tours, 3 × 120 s
  d'exécution) ou ≈ 179 s (devis) ; attendu à 12 tours : ≈ 1,2 à 4,6 h, plus ≤ 3,2 h d'exécutions au pire. Le délai d'exécution
  est bien de 120 s (`tests_de_mort_v5.py:540` passe `delai_execution_s`, défaut 120).

## 5. Essais, banc, course à blanc (heures de `date -u`)

- **Essais** (commande demandée, `TMPDIR=/tmp`), 18:56:37 → 18:58:18 : **87 passés, 23 sous-essais passés, 100,46 s**, code 0
  (68 dans `essais/test_tour_ferme_v63.py`, 19 dans `essais/test_gardes_tour_ferme_v63.py` ; `BacReelV63` joué, non sauté).
  Sortie : `…/b5/essais-v63.txt`.
- **Banc** `essais/mutations_tour_ferme_v63.py`, 18:58:29 → 19:04:42 : **72 mutations (24 portées de la v62, 19 sondes et bords
  de la contre-lecture 3, 29 corrections v63) ; 72 tuées pour la raison attendue** ; autre raison 0, défaut du banc 0, survivantes
  0, non appliquées 0 ; 373 s ; témoin 83 essais, 0 en échec, avant et après restauration ; code 0. Les quatre mutations du
  brouillon 5 : borne à 0,30 (4/5 essais en échec), rôle « proposeur » (2/2), garde neutralisée (1/2), garde retirée au lanceur
  (1/5). Sortie : `…/b5/banc-v63.txt`.
- **Course à blanc de la section 9**, vrai bac, 19:04:58 → 19:07:03 : `TMPDIR=/tmp nice -n 10 python3 -I -B
  demonstrations/tour_ferme_v63.py …/b5/blanc-20261102 --etage 1 --a-blanc --graine 20261102 --bac reel --utilisateur-bac 64097` :
  **code 0, 125 s**, 152 cartes, 6 appels de proposeurs ; relevé `ade7d47e4e25471e2e8cd9a1121f103d293188616c730c65e20752695091deda`
  (scellé) ; manifeste : borne 0,80, commit `c15a073` (arbre modifié), 91 empreintes égales au disque et au bloc du brouillon 5 ;
  aucun dossier `bac-tour-ferme-v63-*` ni `tour-ferme-v63-sessions-*` resté sous `/tmp`.
- **Lecture v63**, 19:07:10 : lecture `edb42838c95631d301c09f458e4fa6437b0ce43f9c5d4e11d7e6f108efee262a` : **« tient »** (T1 à
  T5), A4 « discrimine » (à blanc, sans portée) ; réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0], aléatoire [36, 3, 0], recopie
  [24, 0] ; non concluant 0 ; 32 testés, 32 contre-calculs concordants ; 64/64 consignes d'expérimentateur avec loi, plafond de
  session passé ≤ 0,80 ; touches de L* 0 sur 6 contextes, lignes de tranche 0, refus du gardien 0 ; S1 déclenché (attendu à
  blanc) ; mêmes comptes que L2b-v63 (même racine). Ligne L2b-v63-b5 du texte (l. 516).
- Non relancés : les essais et bancs v59, v60, v61 cités par la section 9 (code inchangé).

## 6. Brouillon 5 : construction et contrôles

Construit par script (`…/b5/construire_brouillon5.py`, entrées `figures.json`, `paragraphe-devis.md`, `annexe-a.md`) : brouillon
4 vérifié à son empreinte, remplacements à cible unique (sinon arrêt), paragraphe des plafonds de la section 12 remplacé, bloc
d'empreintes recalculé sur le disque, annexe A ajoutée, puis contrôles : **sept zones de l'étage 2 identiques à l'octet** à celles
du brouillon 4 ; marqueurs hors zone = {`<<CASE_CONFIGURATION_V3>>`}, une occurrence ; dans les zones : `<<CASE_E0>>`,
`<<CASE_M2>>`, `<<CASE_Q>>`, `<<CASE_R>>`, `<<CASE_T>>`, `<<CASE_V>>`, `<<DECISION_D5>>`, `<<DECISION_D8>>` (inchangés) ;
« GO-2026-11-02-19 » absent ; plan relu par `lire_plan` du lanceur (50, 44, 6, 24, GO-2026-11-02-23) ; garde 6 complète
(`lire_preenregistrement`) sur une copie scellée, case remplie d'une valeur d'essai, dans un dossier temporaire retiré ; les « 0,30
USD » restants sont tous historiques (brouillon 4, ligne L2b-v63).

Où sont les changements : statut l. 3 ; têtes l. 5 ; section 0, liste des changements l. 15-23 ; 4.1 (rôle, borne) ; 4.3 ; section
7, gardes 5 et 13 et paragraphe des essais (l. 447, 455, 459) ; section 9, commandes (l. 486-487 : `TMPDIR=/tmp`, GO-23) ; section
10, L2b-v63 qualifiée « code du brouillon 4 », L2b-v63-b5 neuve (l. 515-516) ; 10 bis ; section 12, lignes « étage 1 » et
« total », paragraphe des plafonds (l. 565-576) ; section 13, code, GO, renvoi à l'annexe, plan (l. 590-605), phrase et bloc
d'empreintes (l. 617-709 : deux lignes changent, `pole/tour_ferme_v63.py` et `demonstrations/tour_ferme_v63.py`) ; section 14,
points (1), (2), (4), (6) ; annexe A (l. 745-871).

## 7. Annexe A (pour la session-depot) en bref

Ce que lit la v63, dans l'ordre : ligne de commande et texte scellé (A.1) ; **empreinte des octets** de la configuration = clé
`configuration_sha256` (A.2) ; ligne de GO à 8 colonnes, type « calcul », « Lazar », dates, aucune révocation, **un seul montant,
exactement 50 USD** (A.3) ; lecture complète du schéma de la course 2 (v53, v54, v56), clés inertes comprises, tableau des domaines
(A.4) ; `budget.plafond_usd` = **50**, `plafonds_session.proposeur` réel > 0 (une session au-delà arrête la course : conseillé ≥
0,50 USD) (A.5) ; `proposeurs` (un kimi, un argon, modèle exact, le même pour tous les rôles du relais), **Kimi et Argon en
`commande_externe`**, `commande`, environnement transmis (`ROLE_POLE`, `MODELE_DEMANDE_POLE`, `PLAFOND_SESSION_USD`,
`ETAPE_POLE`, `PLAFOND_ETAPE_USD`), ligne rendue `{texte, cout_usd, modele_servi}`, `modeles_servis_permis`, substitutions
`{REGISTRE}` et `--plafond-cumule-usd` (aucune garde ne les exige), `porte_plafond` pour **chaque** fournisseur, accusé d'une porte
« commande » (A.6) ; **vérificateur : modèle** = `proposeurs[fournisseur="argon"].modele`, **port** : aucune clé lue (seulement
dans une `url_relais`, et `kimi_protocole` est refusé ; sinon dans la commande, opaque, gelé par l'empreinte), **effort** : ni lu
ni transmis (à fixer dans la commande) (A.7) ; `POLE_MACHINE_JETABLE_V56=1`, liste blanche `NOMS_PERMIS` en entier,
`environnement_permis` = exactement les noms non secrets présents hors de cette liste (vide sinon), `bwrap`, `--utilisateur-bac`
exigé sous le superutilisateur, **TMPDIR traversable par l'identité dédiée, `/tmp`** (A.8) ; ce qui n'est lu nulle part (A.9).

## 8. Fichiers et empreintes (depuis `orchestrator/`, `sha256sum`)

| fichier | état | sha256 |
|---|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon5.md` | neuf | `c81aa6ef72255adab76abcffc8e06cc0c570069cf09aa2035c285a54212fc3d3` |
| `prereg/rapport-redaction-tour-ferme-v5.md` (ce rapport) | neuf | donnée dans la réponse du rédacteur (un fichier ne porte pas sa propre empreinte) |
| `pole/tour_ferme_v63.py` | modifié (dans le bloc gelé) | `9982ae3c819eedec78f5c1757e876f01051d2fd732c1e2371692a3823cf13c40` |
| `demonstrations/tour_ferme_v63.py` | modifié (dans le bloc gelé) | `33e4c0292a4370168cc62f0b83ea53e45d53474af7a9e9aff5b601c4b2918262` |
| `essais/test_tour_ferme_v63.py` | modifié | `2e459e760ab3c97dd8ec775c06db60148d0aaa69f8a5f75007122b505c7f1da5` |
| `essais/test_gardes_tour_ferme_v63.py` | modifié | `2cd44645b4bcbd058b1553fe1e8702deca8ce6674dc2c296a03c43ca5e3d9204` |
| `essais/mutations_tour_ferme_v63.py` | modifié | `c8290530a49b94e0fba412ae06c61a0adc60c43173eb4b79668f0e4e2b8b2102` |

Bloc d'empreintes du brouillon 5 : 91 lignes, égales au disque ; les 89 autres fichiers gelés sont égaux à `af92034` et à la tête
`e58cfec`. La tête a bougé pendant la session (`5e352ec` → `c15a073` → `e58cfec`, commits d'autres tâches qui ne touchent aucun
fichier du bloc ni aucun des cinq fichiers ci-dessus).

## 9. Réserves et écarts

1. **Changement non demandé** : rôle des proposeurs et garde des rôles (section 3) ; la mutation « borne relevée à 0,5 USD » est
   remplacée par « borne ramenée à 0,30 USD » (le 0,5 n'est plus un relèvement) ; d'où 72 mutations et 87 essais, pas 69 et 83.
2. **12 tours au prix prudent** : la borne couvre 12 tours si le tour moyen coûte ≤ 0,067 USD. La consigne grandit avec
   l'historique de la fiche ; le prix réel d'un tour de Kimi reste inconnu (journaux privés, C7). Au-delà, une carte serait jugée
   sur ce qu'elle a exécuté (« non concluant » sans exécution réussie, compté par T4), jamais un arrêt.
3. **Ce que la v63 ne garde pas, dit à l'annexe** : un plafond de session de proposeur trop bas arrête la course ; les arguments
   `{REGISTRE}` et `--plafond-cumule-usd` ne sont exigés par aucune garde ; la commande Kimi de la session-depot doit accepter
   `ROLE_POLE=experimentateur_test` (je ne peux pas le vérifier d'ici) ; délai de 1 800 s par appel de commande externe, non
   réglable.
4. **TMPDIR** : tout a tourné avec `TMPDIR=/tmp` (l'identité 64097 ne traverse pas le dossier de travail, constat du brouillon 4) ;
   la commande réelle de la section 9 porte maintenant `TMPDIR=/tmp`.
5. **Course à blanc** : elle ne peut pas montrer la borne au travail (doublures gratuites, deux tours) ; la borne et le pire cas
   sont prouvés par `ReservationI30`, `EtageV63` et `DevisI30`, et les rôles par `RolesDesRelais` sur un adaptateur réel.
6. L'en-tête du brouillon dit « rédigé de 18:45 à 19:11 UTC » (écriture du texte) ; le rapport est achevé à 19:14.

## 10. La contre-lecture courte : dix lignes à vérifier d'abord

1. `pole/tour_ferme_v63.py:118-129` : borne 0,80 et `ROLE_PROPOSEUR` ; la borne arrive à l'étage (`:812`) et au pire cas (`:799-801`).
2. `DevisI30` (`essais/test_gardes_tour_ferme_v63.py:281-349`) rejoue bien le `Compteur` gelé au plan 50 / 44 / 6 ; refaire la table de la section 12.
3. Le défaut des rôles est réel : `git show af92034:orchestrator/pole/tour_ferme_v63.py` passe « proposeur » ; `pole/adaptateurs.py:619` et `pole/adaptateur_kimi_v53.py:34` le refusent (table des adaptateurs de `…/b5/sonde_roles.py`, indépendante de la v63).
4. `exiger_roles_joues` (`:669-697`) est appelée avant `transmettre` dans `roles_reels` (`demonstrations/tour_ferme_v63.py:271`) et dans `roles_a_blanc` (`:294`).
5. Les doublures refusent tout autre rôle (`:1177`, `:1257`, `:1289`) sans changer un verdict à blanc (L2b-v63-b5 = L2b-v63).
6. Plan gelé (l. 590-605) : 50 = 44 + 6 au centime, 24 h, GO-2026-11-02-23 ; GO-2026-11-02-19 cité nulle part.
7. Sept zones de l'étage 2 identiques à l'octet au brouillon 4 ; une seule case hors zone (`configuration_sha256`).
8. Bloc d'empreintes (l. 617-709) égal au disque ; à revérifier après le commit des cinq fichiers `_v63`.
9. Annexe A (l. 745-871) contre le code : chaque domaine et chaque garde nommée existent (`configuration_v53` à `_v56`, `adaptateurs_v56`, `etage_entre_generations_v56`, `a_blanc_v59`).
10. Section 12 : la phrase « 24 heures, jamais un couperet » et le seuil de ≈ 93 s ; la limite dite des 144 cartes (≈ 130 USD) non couverte.
