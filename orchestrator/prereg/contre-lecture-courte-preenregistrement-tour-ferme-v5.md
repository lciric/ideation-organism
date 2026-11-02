scellable après couples — aucun bloquant ; B10 et I25 à I31 traités, chacun prouvé sur le code gelé par ses essais et ses mutations (rejoués) ; changements du brouillon 5 conformes (GO-23 seul, 50 = 44 + 6, borne 0,80, rôles et garde des rôles, annexe A contre le code) ; un important (I32 : rôles et plafonds de session des commandes des relais, invisibles à blanc et à `--verifier-seulement`), six mineurs (39 à 44) ; couples T101 à T112, texte seul ; reste la case de la configuration v3

# Contre-lecture R2 courte — préenregistrement du tour fermé (étage 1), brouillon 5, et code `_v63` au commit `a12713a`

2 novembre 2026, de 19:38 à 20:15 UTC environ (heures de `date -u`). Contre-lecteur neuf : je n'ai écrit ni les brouillons 1 à 5, ni
le code `_v61` à `_v63`, ni aucune contre-lecture ni aucun rapport de rédaction. Lecture seule du dépôt public ; aucun commit, aucun
`.sha256`, aucun fichier existant modifié, rien sous `donnees/`, aucun `git fetch`, aucun appel de réseau ni de modèle ; Python par
`nice -n 10 python3 -I -B`, pytest avec `-p no:cacheprovider`, `TMPDIR=/tmp`. Deux fichiers neufs : ce texte et
`prereg/couples-contre-lecture-tour-ferme-v5.json`. Mes scripts et sorties : `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/tour-ferme-clc5/`.
Dépôt à la tête `08b1f17` au début ; entre `a12713a` et cette tête, seul un préenregistrement d'une autre tâche a changé (aucun
fichier de ce tour). Pendant la contre-lecture, d'autres tâches ont committé `516feca` (attaque de Goodhart v4, nul v9, juges v2) et
modifié `pole/juges_idees_v2.py` dans l'arbre : aucun de ces fichiers n'est dans le bloc gelé ; à 20:08 UTC, les 91 empreintes du bloc
restent égales au disque et à `516feca`. Les fichiers de ces tâches n'ont pas été ouverts.

**Verdict en trois lignes.**

1. **Scellable après les couples T101 à T112** (texte seul : aucun code, aucun essai, ni le plan ni le bloc d'empreintes ne
   changent) et la case `configuration_sha256` portée par la session-depot ; aucun bloquant.
2. Ce que la contre-lecture 3 demandait est fait et prouvé sur le code gelé (B10, I25 à I31 ; 33 couples et 4 cellules) ; le
   brouillon 5 n'a rien cassé : 87 essais sur 87, banc des sondes 10 sur 10, six mutations du brouillon 5 et d'I30 tuées pour la
   raison attendue ; zones de l'étage 2 identiques à l'octet, un seul marqueur ; 91 empreintes égales au disque et à `a12713a` ;
   devis refait à l'identique ; chemin réel `--verifier-seulement` « conforme » sur une copie scellée du texte.
3. Reste un risque du chemin réel de la même famille que le défaut des rôles (**I32**) : les commandes des relais n'ont jamais joué
   les rôles de l'étage ni ses plafonds de session (vérificateur à 0,1 USD) ; un refus serait un arrêt sans issue ; à faire
   vérifier par la session-depot avant d'écrire la configuration (T111, T112). Option à la main de Lazar : durée 72 h (mineur 40).

## 0. Fichiers lus, empreintes, ce qui a été rejoué

| pièce (depuis `orchestrator/`) | vérification |
|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon5.md` | `c81aa6ef72255adab76abcffc8e06cc0c570069cf09aa2035c285a54212fc3d3`, 871 lignes : conformes ; lu en entier |
| `prereg/preenregistrement-tour-ferme-v1-brouillon4.md` | `55e4e98571eb39de939e955babd36d58094b45c5da0cf8092e8fe97b8463ca78` ; diff avec le brouillon 5 (29 morceaux), chacun relu à sa place |
| `prereg/rapport-redaction-tour-ferme-v5.md` ; `…-v4.md` | `d6922632b53ce749a225bf0d39e7be4ced5e4697cb9407fc4061fab035dc74eb` ; `8dee9d2a…` (égale au rapport v5) ; lus en entier |
| `prereg/contre-lecture-preenregistrement-tour-ferme-v3.md` ; `prereg/couples-contre-lecture-tour-ferme-v3.json` | `0ecd37a2…`, `7aa25f19…` : égales à leurs compagnons (`sha256sum -c`) ; lus en entier |
| `pole/tour_ferme_v63.py`, `pole/lecture_tour_ferme_v63.py`, `demonstrations/tour_ferme_v63.py`, `demonstrations/lire_tour_ferme_v63.py` | `9982ae3c…`, `2e2c695a…`, `33e4c029…`, `62e93d82…` : égales au rapport v5, au bloc du texte et à `git show a12713a:` ; diff `af92034` → `a12713a` lu en entier (deux fichiers du bloc changent : le cœur et le lanceur) |
| `essais/test_tour_ferme_v63.py`, `essais/test_gardes_tour_ferme_v63.py`, `essais/mutations_tour_ferme_v63.py` | `2e459e76…`, `2cd44645…`, `c8290530…` : égales au rapport v5 et à `a12713a` ; lus pour ce qui est cité ici |
| `pole/tests_de_mort_v5.py` | `da524871…` (égale au bloc) ; borne par carte l. 456-479, sessions l. 341-414, lecteur l. 625-631 |
| fonctions appelées par le chemin réel | `pole/adaptateurs.py` (commande externe), `pole/adaptateurs_v56.py`, `pole/adaptateur_kimi_v53.py`, `demonstrations/ideation_v8.adaptateurs_reels_v56`, `demonstrations/attaque_goodhart_v2.py` (`reglages_de_configuration`, `substituer_commandes`), `pole/configuration_v53.py` et `_v55.py` (GO), `pole/etage_entre_generations_v55.py` et `_v56.py`, `pole/a_blanc_v59.choisir_executeur`, `pole/relais.py` |

Rejoué ou vérifié (sorties dans le dossier de travail ci-dessus) :

- **Essais** (commande demandée) : `TMPDIR=/tmp nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_tour_ferme_v63.py
  essais/test_gardes_tour_ferme_v63.py`, 19:39:20 → 19:41:25 UTC : **87 réussis, 23 sous-essais réussis, 124,21 s, code 0**
  (`BacReelV63` joué, non sauté) ; aucun dossier `bac-tour-ferme-v63-*` ni `tour-ferme-v63-sessions-*` resté sous `/tmp`.
- **Banc des sondes** (commande demandée) : `TMPDIR=/tmp nice -n 10 python3 -I -B essais/mutations_tour_ferme_v63.py --seulement sonde
  --raisons`, 19:42:13 → 19:43:34 UTC : **10 mutations (les neuf sondes de la contre-lecture 3 et « mineur 34 : dossier du bac
  laissé par une sonde refusée »), 10 tuées pour la raison attendue**, autre raison 0, défaut du banc 0, survivantes 0 ; témoin
  24 essais, 0 en échec, avant et après ; 80 s ; code 0.
- **En plus**, même banc, `--seulement "brouillon 5" --raisons` puis `--seulement I30 --raisons`, 19:49:37 → 19:49:40 UTC : **3 et
  3 mutations, 6 tuées pour la raison attendue** (rôle « proposeur » : 2/2 essais en échec ; garde des rôles neutralisée : 1/2 ;
  garde retirée au lanceur : 1/5 ; borne non passée à l'étage : 1/1 ; pire cas à 0,5 USD : 1/1 ; borne ramenée à 0,30 USD : 4/5) ;
  témoins 7 et 6 essais, 0 en échec. Le banc complet (72) n'est pas rejoué ici (rejoué par conv-audit, 72 sur 72).
- **Contrôles mécaniques du texte** (`verifier_b5.py`, `couples_clc5.py`, 19:44 → 20:02 UTC) : zones, marqueurs, occurrences des GO,
  plan relu par `lire_plan` du lanceur (case remplie d'une valeur d'essai), bloc d'empreintes contre le disque, `a12713a`, la tête et
  `af92034`, garde 6 complète (`lire_preenregistrement`) sur une copie scellée dans mon dossier de travail, avant et après les couples.
- **Registre de GO du dépôt de travail** (privé, lu sans modification) : `configuration_v56.verifier_go_v56("GO-2026-11-02-23", …, 50.0)`
  **accepte** la ligne ; à 49 et à 15 USD : refus ; `GO-2026-11-02-19` à 50 USD : refus.
- **Chemin réel jusqu'à `--verifier-seulement`** (`verifier_seulement_b5.py`, processus à environnement vidé : `PATH`, `HOME`, `TMPDIR`,
  `POLE_MACHINE_JETABLE_V56=1`) : le vrai `principal` du lanceur v63, `DOSSIER_PREREG` pointé sur mon dossier, sonde du bac remplacée par
  l'exécuteur factice (aucune identité dédiée utilisée), sur une copie scellée du brouillon 5 dont la case porte l'empreinte d'une
  configuration v3 simulée : la configuration v2 du 1er novembre (copie de travail, `4ae5a1e0…`, celle que cite la section 13 ; son
  contenu, privé, n'est pas recopié ici), pièces remplacées par des fichiers factices à leur empreinte, `budget.plafond_usd` = 50, rien
  d'autre ; registre de GO réel. Résultat : **code 0, « conforme »**, rien écrit, aucun dossier temporaire resté ; plan lu 50 USD,
  parts 44 et 6, 86 400 s ; `--plafond-cumule-usd` des deux commandes remplacé par « 50 ». Même essai, Kimi déclaré `kimi_protocole` :
  **code 2**, « relais kimi (AdaptateurKimiProtocole) : rôle « experimentateur_test » non joué par cet adaptateur … », le message
  de l'annexe A, A.6 (avec une porte « commande » ; avec la porte « environnement », refus plus tôt, `ConfigurationRefusee`, comme
  le dit A.6).
- **Devis refait indépendamment** (`devis_cl.py` : mon propre ordre des étages, pas `jouer_devis`, sur le `Compteur` gelé) : les six
  lignes de la table de la section 12 retrouvées au centime (Kimi 2,61 / 7,68 / 11,48 / 15,29 / 22,90 / 25,43 ; Argon 0,71 ; marges
  39,66 / 34,98 / 31,46 / 27,94 / 20,91 / 18,57) ; +23,2 cartes tiennent et +23,3 s'arrêtent (vérificateur à 0,02 ou à sa borne) ;
  +29,0 à 12 tours ; 40/10 : +18,2 ; 45/5 : +24,4 et +17,5 ; seuils de durée 179 s (devis) et 93 s (54,9 testés).
- **Course à blanc L2b-v63-b5** (relevé `ade7d47e…` et manifeste `257b94ed…` du rédacteur, relus sans relancer le vrai bac) : 91
  empreintes du manifeste égales au bloc du brouillon 5 ; bornes 0,8 et 0,1 ; lecture v63 : « tient », A4 « discrimine », réel
  [36, 12, 12, 0], aléatoire [36, 3, 0], recopie [24, 0], 0 non concluant, 32 testés ; 64 sessions d'expérimentateur, plafond passé
  au plus 0,8 : la ligne L2b-v63-b5 (l. 516) est exacte.

## 1. Constats (numérotation à la suite de la contre-lecture 3)

### Bloquants

Aucun.

### Important

**I32 — Les commandes des relais n'ont jamais joué les rôles de l'étage ni ses plafonds de session ; rien ne le vérifie avant la
course.** Le brouillon 5 a trouvé et corrigé un défaut d'interface entre le code gelé et les adaptateurs (rôle « proposeur ») ;
la garde neuve `exiger_roles_joues` (`pole/tour_ferme_v63.py:685-694`) tient la frontière **côté pôle** (les adaptateurs du pôle
acceptent leurs rôles : vérifié, section 3). Le maillon suivant, la commande de chaque relais, reste hors de toute garde :
(a) la commande Kimi doit accepter `ROLE_POLE=experimentateur_test`, la commande Argon `lecteur_test` (le rapport v5 le dit,
réserve 3 ; le texte ne l'exige nulle part) ; (b) la commande reçoit `PLAFOND_SESSION_USD` = le reste de la borne de 0,80 USD de la
carte pour l'expérimentateur (décroissant au fil des tours, `pole/tests_de_mort_v5.py:461-474`) et **0,1 USD pour le vérificateur**
(`BUDGET_VERIFICATEUR_PAR_CARTE_USD`, `pole/tour_ferme_v63.py:125`, défaut de l'étage, non relevé au brouillon 5) ; une commande qui
réserve son pire cas et refuse une session sous ce plafond sort avec un code non nul ou sans coût : `AdaptateurCommandeExterne.lancer`
rend « erreur » (`pole/adaptateurs.py:751-765`), l'étage lève `EtageInterrompu` (`pole/tests_de_mort_v5.py:408-412`), d'où un arrêt
de la course (code 3, aucune issue) — **même pour le vérificateur**, qui n'est jamais décisif. `--verifier-seulement` n'appelle rien,
les doublures acceptent tout plafond : aucune course à blanc ne peut le voir ; l'étage n'a jamais tourné pour de vrai avec ces relais
(section 1). Enfin la configuration est gelée par son empreinte : une option de commande à corriger après le scellement exige un texte
nouveau (la reprise de la section 7 ne vaut que pour une panne d'infrastructure). Remède, texte seul : annexe A, A.6 bis neuve
(T112) et section 14, point (4) (T111) — la session-depot vérifie, **par lecture du code de ses deux commandes, sans appel**, les
rôles acceptés et l'absence de refus avant dépense aux plafonds que le code passera, règle au besoin les options de ses commandes
dans la configuration **avant** d'en calculer l'empreinte, et écrit ce constat avec l'empreinte remise. Autre option, plus chère :
relever la borne du vérificateur (code `_v63` modifié, devis et parts à refaire : à 0,25 USD par carte, le devis ne tient plus à
44/6 si chaque session de vérificateur atteint sa borne ; à 40/10, +8 cartes seulement ; essais et banc à rejouer, contre-lecture
courte neuve). Recommandation : A.6 bis (confiance moyenne : le risque dépend d'un code que je ne peux pas lire d'ici).

### Mineurs

39. **Le prix de la borne n'est plus écrit.** Le brouillon 4 disait ce qui arrive quand la borne mord (« une carte qui demanderait
    plus de ≈ 5 tours est jugée sur ce qu'elle a exécuté, « non concluant » sans exécution réussie, compté par T4, au lieu d'arrêter
    la course », brouillon 4, l. 554) ; le brouillon 5 a remplacé ce paragraphe et ne garde que la condition (« la borne ne mord
    qu'au-delà de 0,067 USD par tour en moyenne », l. 565), suivie de « aucune carte n'est jugée sur une exécution tronquée par la
    borne » (aussi l. 17, 156, 559). Le prix d'un tour de Kimi expérimentateur reste inconnu (C7) ; la conséquence, inchangée dans le
    code (`pole/tests_de_mort_v5.py:461-464`, `:477-479`), doit rester écrite, avec où la lire (`fin_des_tours` du `resultat.json`
    scellé de chaque fiche). Couples T102 et T106.
40. **Durée de 24 heures : « jamais un couperet » se lit « ne coupe jamais une carte ni un étage » ; si elle mordait, la course
    s'arrêterait sans issue.** Le code est conforme à la description (`Compteur.verifier_duree`, `pole/tour_ferme_v63.py:260-262`,
    appelée seulement par `Compteur.ajouter`, après chaque appel de proposeur et après chaque étage : un étage n'est jamais
    interrompu). Mais le seuil écrit (« ≈ 93 s avec 54,9 cartes testées à 12 tours ») est celui d'un scénario : à 60,7 testés
    (12 tours au prix du devis, que la section 12 donne comme tenant sous le plafond) il vaut ≈ 81 s, et moins si des tours moins
    chers laissaient tester plus de cartes ; la latence réelle d'une session de Kimi expérimentateur n'est pas mesurée (devis : 10
    à 40 s par appel). Couples T103, T104, T108 (seuils exacts, aucun changement de valeur). **Décision possible de Lazar** (« arrête
    de mettre des budgets temps et de les couper ») : 72 heures, comme la reprise de l'attaque (GO-2026-11-02-21), sans coût en
    dollars (la dépense est bornée par le plafond et les parts ; chaque appel de commande est borné à 1 800 s) ; seuils à 72 h :
    ≈ 593 s (devis, 12 tours), ≈ 333 s (54,9 testés), ≈ 299 s (60,7 testés). Recommandation : 72 h (confiance moyenne) ; défaut :
    24 h tel qu'écrit avec T103, T104, T108. Si 72 h : `duree_etage_1_h: 72` au plan (l. 598) et les mots « 24 heures » ou « 24 h »
    du statut (l. 3), de la section 0 (T103), de la garde 13 (T104), de la section 10 bis (l. 525) et de la section 12 (T108),
    seuils ci-dessus ; `lire_plan` accepte toute durée > 0, aucun code ne change.
41. **« Il faudrait que le juge promeuve presque tout » (l. 576) situe mal l'arrêt par la dépense.** Le maximum de 144 testés
    (≈ 130 USD) n'est pas ce qui ferait mordre le plafond : l'arrêt avant un étage vient dès ≈ 55 testés si chacun dépense sa borne
    (≈ 61 à 12 tours au prix du devis), ≈ 1,7 fois le devis — un bras réel promu presque entier à chaque génération en est un
    exemple. Et seul un excès de cartes testées peut le faire mordre : l'arrêt prendrait alors la place de l'issue qu'il aurait
    fallu lire (« ne tient pas (T3, T5) » d'un juge laxiste) — asymétrie à dire (R4). Couple T107.
42. **La ligne de GO-2026-11-02-23 (registre privé) décrit le code et l'attendu d'avant le brouillon 5** : elle nomme le commit
    `af92034` (code du brouillon 4) et un attendu écrit avant le devis du brouillon 5 (celui-ci : ≈ 3,3 USD à 2 tours, ≈ 23,6 USD à
    12 tours, ≈ 26,1 USD si chaque carte atteint sa borne) ; le code gelé est celui de `a12713a` (deux fichiers du bloc changés : la
    borne et les rôles). Le lanceur n'en lit que
    l'identifiant, le type, l'auteur, les dates, les révocations et le montant (`pole/configuration_v55.py:72-100`), tous conformes ;
    aucun changement du texte : une ligne de précision au registre, par le directeur, suffit.
43. **Table du devis, ligne « 1, recopie-mélange » (l. 558) : « ≈ 2,5 testés »**, alors que le devis rejoué (31,7 testés) compte
    2,4 témoins par génération pour ce bras, soit 4,8 en générations 2 et 3, et aucune carte promue (L2). Antérieur au brouillon 5
    (ligne inchangée depuis le brouillon 4), sans effet sur le devis rejoué ni sur une issue : pour mémoire, aucun couple.
44. **Phrases périmées au scellement** (sans marqueur, le lanceur ne les lit pas) : en-tête « non commités » (l. 5), section 10 bis
    « contre-lecture … à faire » (l. 525), section 13 « non commités : à revérifier après commit » (l. 615), section 14, point (2)
    (l. 739). Couples T101, T105, T109, T110. Le titre et le statut (l. 1 et 3 : « brouillon 5, non contre-lu, non scellé »,
    « contre-lecture R2 courte et neuve à faire ») restent à récrire par le directeur au scellement, comme pour les brouillons
    précédents.

## 2. La contre-lecture 3 : B10 et I25 à I31, prouvés sur le code gelé

Lignes du brouillon 5 en « l. » ; essais : `essais/test_tour_ferme_v63.py` (TT) et `essais/test_gardes_tour_ferme_v63.py` (TG) ;
mutations : libellés exacts de `essais/mutations_tour_ferme_v63.py` ; « rejouée » = tuée pour la raison attendue sous mes yeux,
sinon banc complet du rédacteur et de conv-audit (72 sur 72).

| constat | code gelé | essais (cas sain ; artefact) | mutations | texte | état |
|---|---|---|---|---|---|
| **B10**, garde 5 (plafond de l'étage) | `Compteur.ajouter`, `pole/tour_ferme_v63.py:246-247` | TG `Garde5PlafondEtage.test_unite_sain_et_artefact`, `.test_unite_filet_derriere_les_parts` (l. 68-82) ; `Garde5DeBoutEnBout.test_sain_plafond_large_course_au_bout`, `.test_artefact_plafond_franchi_arret_scelle` (l. 85-98 : code 3, relevé partiel scellé, N1 d'arrêt, A4 « non lue (arrêt) ») | « B10, garde 5 : plafond global de l'étage neutralisé (sonde) » (rejouée : 3/4 en échec) ; « B10, garde 5 : égalité au plafond refusée » | l. 447 (T98) | traité |
| **B10**, garde 13 (durée) | `Compteur.verifier_duree`, `pole/tour_ferme_v63.py:260-262` | TG `Garde13Duree.test_unite_sain_et_artefact` (l. 112-123, horloge factice) ; `Garde13DeBoutEnBout.test_sain`, `.test_artefact_duree_franchie_arret_scelle` (l. 126-136) | « B10, garde 13 : durée neutralisée (sonde) » (rejouée : 2/3) ; « B10, garde 13 : égalité à la durée refusée » | l. 455 (T99) | traité |
| **B10**, garde 14 (T2 à T5) | `lire_etage1`, `pole/lecture_tour_ferme_v63.py:171-184` | TG `Garde14T2`, `Garde14T3`, `Garde14T4`, `Garde14T5` (l. 164-275 : bord exact de chaque seuil tenu, un pas au-delà → « ne tient pas (Tk) ») | « B10, garde 14 : T2 / T3 / T4 / T5 neutralisé (sonde) » (rejouées : 1/2, 6/2 avec sous-essais, 1/2, 1/2) ; huit bords (« T2, « sauf au plus une » → deux », « T3, au plus 1 témoin faux retenu → 2 », « T3, T-ELIM « sauf au plus une » → deux », « T4, ≤ 0,20 devient < 0,20 », « T4, seuil par bras ignoré », « T4, désaccord du contre-calcul ignoré », « T5, au plus 1 FD aléatoire → 2 », « T5, FD de la recopie ignorées ») | l. 456 (T100), l. 459 (T85) | traité |
| **I25** (porte attribuée à un module non gelé) | lecture v63 seule ; `demonstrations/lire_tour_ferme_v63.py:28`, `:50-52` (relevé d'une autre version du cœur refusé) | TT `CourseSaine` (relevé v63 lu, l. 982) | « lecture v63 d'un relevé d'une autre version du cœur » | l. 228 (T64), l. 51 (T65), l. 54 (T66) | traité |
| **I26** (loi que le juge ne sait pas évaluer) | `pole/tour_ferme_v63.py` : `_entier` `:277`, `verifier_loi_servable` `:286`, `_verifier_noeud` `:308`, `JEU_FACTICE_DU_GARDIEN` `:377`, `evaluer_sur_jeu_factice` `:401`, `garder` `:497`, `extraire_propositions` `:521` ; sonde : la loi `{"indice": 1.0}` de la contre-lecture 3 est refusée au gabarit (« condition.indice entier 0 ou 1 exigé (reçu 1.0 (float)) »), `{"indice": 1}` acceptée et évaluée | TT `GardienEntiers` (l. 285), `GardienJeuFactice` (l. 331), `AucuneExceptionQuiRemonte` (l. 374), `CourseIndiceFlottant` (l. 400) | dix « I26 : … » (indice, sous-population, trait et issue, seuil non fini, jeu factice retiré, écart de l'évaluateur, simplexe, exception du gabarit, exception du gardien, réponse trop imbriquée) | l. 144 (T93, version v63), garde 8 (l. 450) | traité (trou théorique de la réserve 3 du rapport v4 : section 5) |
| **I27** (modules exécutés hors du bloc) | `FICHIERS_GELES`, `demonstrations/tour_ferme_v63.py:79-101` (91 fichiers, dont `pole/ideation.py` et `pole/tests_de_mort.py`) | TT `Fermeture` (l. 1352), `FermetureEnCourse` (l. 1409), `Garde6Complete` (l. 750 : bloc sans `pole/ideation.py` refusé) | « I27 : pole/ideation.py hors du bloc gelé », « I27 : pole/tests_de_mort.py hors du bloc gelé », « I27 : module d'un chemin non joué hors du bloc gelé » | l. 615 (T69, version v63) | traité ; `import sys` du brouillon 5 est de la bibliothèque standard |
| **I28** (A4 lue sur un arrêt) | `pole/lecture_tour_ferme_v63.py:203-205`, `:301-304` | TT `LectureV63` (l. 1208), `Arrets` (l. 1086), `ArretEnGeneration2` (l. 1110) ; TG `Garde5DeBoutEnBout` (A4 « non lue (arrêt) ») | « I28 : issue A4 lue sur un arrêt (v62) » | l. 461 (T76), l. 261 | traité |
| **I29** (trouvaille hors de S1) | `pole/lecture_tour_ferme_v63.py` : `exiger_recherche` `:84-94` (ligne de tranche → `DefautDeCourse`), `:242-244` (touche de L* → `audit_avant_lecture`) | TT `LectureV63.test_I29_ligne_de_tranche_releve_invalide_et_touche_auditee` (l. 1273), `FuiteDansLesContextes` (l. 1128, dont `test_touche_de_L_etoile_trouvee`) | « I29 : ligne de tranche dans un contexte sans conséquence (v62) » (la branche « touche → audit » a son essai, pas de mutation au banc : ce n'est pas une garde d'arrêt) | l. 413 (T77) | traité |
| **I30** (devis), revu au brouillon 5 | borne `pole/tour_ferme_v63.py:124` ; passée à l'étage `:812` ; pire cas `:801-802` ; manifeste `:1121-1122` ; tenue par l'étage `pole/tests_de_mort_v5.py:460-479` | TT `ReservationI30.test_pire_cas_calcule_avec_la_borne` (l. 577 : 3 × 0,80 = 2,4 permis, 2,3 refusé), `EtageV63.test_sain_simule_et_factice_refuse_au_moteur_reel` (l. 699 : `budget_test_usd` 0,80, plafonds passés ≤ 0,80) ; TG `DevisI30` (4 essais, l. 315-349) | « I30 : borne par carte non passée à l'étage », « I30 : pire cas de l'étage à 0,5 USD par carte (règle v62, sous la borne) », « I30 : borne par carte ramenée à 0,30 USD (brouillon 4 : 5 tours, cartes tronquées) » (les trois rejouées) | l. 17-18, 156, 447, 559, 565-576 (T78, version du brouillon 5) | traité ; mineurs 39 et 41 |
| **I31** (gardes 7, 8, 9 prouvées en v61) | témoin dans la sélection `pole/tour_ferme_v63.py:921`, `exiger_sans_temoin` `:969`, `completer_carte` `:479`, `exiger_familles_separees` `:663-666` | TT `Garde7` (l. 435), `Garde7Selection` (l. 446), `GrammaireServie` (l. 234), `Garde8Course` (l. 491), `Garde9` (l. 506), `RefusAvantToutAppel` (l. 829) | « I31, garde 7 : témoin dans la sélection non refusé (sonde) » (rejouée : 1/2), « I31, garde 7 : témoin dans l'archive ou la vue accepté », « I31, garde 8 : clés en trop acceptées au gabarit », « I31, garde 9 : familles non séparées acceptées », « C9 : borne ±4 du gabarit non tenue » | l. 449-451 (T82, T83, T84) | traité |

**Couples T64 à T97 et cellules T85, T98, T99, T100.** Appliqués à la lettre au brouillon 4 (texte de contrôle `a6337d96…`, celui de
la contre-lecture 3, rapport v4 section 4), puis adaptés au code v63 ; dans le brouillon 5 : aucune des 33 cibles ne reste (sauf T77,
T81 et T93, dont la cible est le début du texte nouveau, gardé) ; 8 textes nouveaux à la lettre (T75, T79, T80, T81, T86, T87, T89,
T96), 25 adaptés (nom du code v63, décisions de Lazar, T69 et T93 dans leur version de l'option A) ; relus à leur place : aucune
adaptation ne change le sens d'un couple au-delà du nom du code ou de la décision prise. Les quatre cellules de B10 sont écrites
(l. 447, 455, 456, 459) et nomment des essais qui existent et portent sur le code gelé seul. Mineurs 26 à 38 : appliqués (relus :
26 l. 469, 27 l. 498, 29 l. 266 et lecture `:303`, 30 l. 199 et `trajectoire_p7`, 31 l. 514, 32 l. 580, 33 l. 461, 34 `preparer_bac`
`demonstrations/tour_ferme_v63.py:298-314` avec sa mutation rejouée, 35 et 37 `CheminReelVerifierSeulement` avec la mutation de la
garde 15 rejouée, 36 l. 136, 38 l. 141).

## 3. Les changements du brouillon 4 au brouillon 5 (section 0)

| changement | ce qui a été vérifié | résultat |
|---|---|---|
| GO-2026-11-02-23 seul | « GO-2026-11-02-19 » : 0 occurrence ; « GO-2026-11-02-23 » : 16, toutes hors des zones (statut, section 0, commande l. 488, plan l. 602, section 13, section 14, annexe A) ; registre : ligne acceptée à 50 USD, refusée à 49 et 15 | conforme (mineur 42 pour la ligne du registre) |
| plafond 50 = 44 + 6 au centime | plan l. 595-597 ; `lire_plan` (case remplie d'une valeur d'essai) rend 50, 44, 6, 24 h, `GO-2026-11-02-23`, `archive_du_bras_reel`, `mecanique` ; garde au centime `demonstrations/tour_ferme_v63.py:162-163` ; `budget.plafond_usd` = 50 exigé (`:260-262`) ; « 15 USD » restant : l. 9, 21, 525, 565, 742, tous historiques | conforme |
| borne de 0,80 USD par carte, 12 tours | `BUDGET_EXPERIMENTATEUR_PAR_CARTE_USD = 0.80` (`pole/tour_ferme_v63.py:124`) ≥ 12 × 0,06 (`TOURS_MAX_PAR_FICHE` = 12, `pole/tests_de_mort_v2.py:139`) ; passée à l'étage (`:812`) qui plafonne chaque session au reste de la fiche ; `prix_caractere_usd` non passé (`None`) : aucune autre coupe des tours | conforme (mineur 39) |
| pire cas recalculé et marge | `verifier_parts_avant_etage` (`pole/tour_ferme_v63.py:250-258`) avec n × 0,80 et n × 0,1 (`:801-802`) ; table de la section 12 refaite indépendamment, au centime ; capacités et partages retrouvés | conforme (mineur 41) |
| durée 24 h, garde et non couperet | plan l. 598 ; vérifiée après chaque appel de proposeur et chaque étage seulement (`pole/tour_ferme_v63.py:248`, `:821`, `:860-862`) | conforme (mineur 40) |
| rôle des proposeurs et garde des rôles | `af92034` passait « proposeur » (`git show af92034:` l. 532) ; refusé par la commande externe (`pole/adaptateurs.py:619`, `:724-725`) et par Kimi par protocole (`pole/adaptateur_kimi_v53.py:34`, `:110-111`) ; `ROLE_PROPOSEUR` (`pole/tour_ferme_v63.py:129`) employé (`:550`) ; `roles_permis` / `paires_de_roles` / `exiger_roles_joues` (`:669-694`) ; appelée dans `roles_reels` **avant** `transmettre` (`demonstrations/tour_ferme_v63.py:271-272`) et avant `preparer_bac`, et dans `roles_a_blanc` (`:294`) ; refus → `TourRefuse` → code 2, dossiers retirés (`:412-417`) ; doublures (`pole/tour_ferme_v63.py:1177`, `:1257`, `:1289`) ; `RolesDesRelais` (deux essais, l. 607-665) et `CheminReelVerifierSeulement.test_artefact_kimi_par_protocole` (l. 953) réussis ; trois mutations rejouées ; chemin réel `--verifier-seulement` sur la forme de la configuration du 1er novembre : « conforme » ; Kimi par protocole : code 2 | conforme ; côté commandes des relais : I32 |
| annexe A | A.1 contre `principal` (`demonstrations/tour_ferme_v63.py:317-411`) ; A.2 (`:385-387`) ; A.3 contre `lire_registre_go` (`pole/configuration_v53.py:258-281`) et `verifier_go_v55` / `lire_plafond` (`pole/configuration_v55.py:53-100`) ; A.4 : la configuration du 1er novembre, clés inertes gardées, passe `lire_configuration_v56` (essai ci-dessus) ; A.5 (`reglages_de_configuration`, `demonstrations/attaque_goodhart_v2.py:212-230`) ; A.6 (`adaptateurs_reels_v56`, `demonstrations/ideation_v8.py:59-81` ; environnement de la commande `pole/adaptateurs.py:648-664` et `pole/adaptateurs_v56.py:67-71` ; dernière ligne `pole/adaptateurs.py:703-719` ; délai 1 800 s `:622`, non passé par `adaptateurs_reels_v56` ; substitutions `demonstrations/attaque_goodhart_v2.py:233-250` ; portes `pole/adaptateurs_v56.py:209-219`) ; A.7 (`EFFORT_PAR_ROLE` seulement dans l'adaptateur du kit, `pole/adaptateurs.py:55-56`, `:79`, `:330`) ; A.8 : `NOMS_PERMIS` (37 noms) égal à la liste de l'annexe, règle des noms de clé égale à `nom_de_cle_v55` (`pole/etage_entre_generations_v55.py:22-27`), identité et dossier du bac (`preparer_bac`, `choisir_executeur`, `pole/a_blanc_v59.py:310-328` ; le délai de 60 s de l'exécuteur est remplacé par les 120 s que passe l'étage, `pole/tests_de_mort_v2.py:1581`) | conforme ; un ajout, A.6 bis (I32) |
| ce que le diff de code change | `git diff af92034 a12713a` : deux fichiers du bloc (cœur : borne, rôle, garde, doublures, docstring ; lanceur : appels de la garde, docstring) ; trois fichiers d'essais et de banc hors du bloc ; rien d'autre | conforme |

## 4. Zones, marqueur, bloc d'empreintes

- **Zones de l'étage 2** : 7 ouvertures, 7 fermetures, appariées ; les 7 zones du brouillon 5 sont **identiques à l'octet** à celles du
  brouillon 4 (14 661, 800, 570, 580, 455, 347 et 342 octets).
- **Marqueurs** : hors des zones, **un seul**, `<<CASE_CONFIGURATION_V3>>`, une occurrence (l. 601, clé `configuration_sha256`) ;
  dans les zones : `<<CASE_E0>>`, `<<CASE_M2>>`, `<<CASE_Q>>`, `<<CASE_R>>`, `<<CASE_T>>`, `<<CASE_V>>`, `<<DECISION_D5>>`,
  `<<DECISION_D8>>`. Le texte tel quel, scellé en copie, est refusé par la garde 6 (« marqueur(s) non rempli(s) hors de l'étage 2 :
  ['<<CASE_CONFIGURATION_V3>>'] ») ; case remplie d'une valeur d'essai, il est accepté (garde 6 complète, E ≥ 2⁶⁴).
- **Bloc d'empreintes** (l. 617-709) : 91 lignes, mêmes noms et même ordre que `FICHIERS_GELES` ; **chaque empreinte égale au disque,
  à `git show a12713a:` et à la tête `08b1f17`** (0 écart sur 273 comparaisons) ; deux lignes diffèrent du bloc du brouillon 4, et
  de `af92034` : `demonstrations/tour_ferme_v63.py` et `pole/tour_ferme_v63.py`, exactement les deux fichiers modifiés. La revérification
  « après commit » que demandait le texte est faite (T109).
- **Après les couples** (contrôle sur une copie) : chaque cible présente une fois dans le brouillon 5 et une fois à son application,
  dans l'ordre ; zones identiques, marqueurs inchangés, plan et bloc inchangés, garde 6 complète acceptée (case d'essai) ; texte
  obtenu : 873 lignes.

## 5. Issues écrites d'avance et bornes restantes

**Chaque issue peut tomber dans les deux sens.**

| issue | dans un sens | dans l'autre | remarque |
|---|---|---|---|
| T1 | « tient » : courses à blanc (L2b-v63-b5) | manque : tout arrêt, incident, lecture d'héritage absente (`Garde5DeBoutEnBout`, `Garde13DeBoutEnBout`, `Arrets`, `ArretEnGeneration2`, `LectureV63`) | — |
| T2 | tient au bord : une passe manquée (`Garde14T2.test_sain_une_passe_manquee_au_plus`) | deux passes sans « survit », une « éliminée », une absente (`.test_artefacts`) | un « non concluant » de T-VRAIE compte contre T2 : le vrai expérimentateur peut le faire manquer |
| T3 | une fausse retenue et une passe de T-ELIM manquée tiennent | deux fausses retenues, T-ELIM « survit », deux passes de T-ELIM manquées, T-MAL passé ou absent | — |
| T4 | bords 8/40 et 5/13 tiennent | 9/40, 6/13, recopie 3/6, un désaccord du contre-calcul | — |
| T5 | une FD par bras tient | deux FD aléatoires ou deux de la recopie | T5 manqué donne aussi A4 « la chaîne ne discrimine pas » |
| A4 | « discrimine » (à blanc : réel [36, 12] contre aléatoire [36, 3]) | « promeut autant » (borne basse de Newcombe ≤ 0, avec sa cause), « ne discrimine pas », « non mesurable », « non lue (arrêt) » | exigeant : la saturation de l'archive après la génération 1 (P6 ; L2b 0/96) concentre l'écart en génération 1 ; puissance dite (≈ 0,2 à 0,10, ≈ 0,6 à 0,20) ; génération 1 rapportée à côté : dit, non une issue par construction |

**Bornes qui pourraient encore rendre une issue non concluante (ou une course sans issue), et leur prix.** Aucune ne le fait par
construction.

| borne (où) | si elle mord | par construction ? | prix pour l'écarter |
|---|---|---|---|
| borne de l'expérimentateur, 0,80 USD par carte (`pole/tour_ferme_v63.py:124` ; `pole/tests_de_mort_v5.py:460-479`) | fin des tours de la carte, jugée sur ce qu'elle a exécuté : « non concluant » sans exécution réussie (T4 ; T2 ou T3 pour un témoin) | non : seulement si le tour moyen dépasse 0,067 USD (prix inconnu, C7) et que la carte veut ses 12 tours | 1,00 USD : capacité +12,2 cartes au lieu de +23,2 ; 1,20 USD : +4,9 (devis refait sur le `Compteur` gelé) ; code, essais et banc à reprendre ; texte : mineur 39 |
| garde-fou de 12 tours, 3 exécutions de 120 s (défauts de l'étage v5, `pole/tests_de_mort_v2.py:133-139`, `pole/tests_de_mort_v5.py:540`), 768 Mo (`MEMOIRE_BAC_MO`, `pole/tour_ferme_v63.py:117`) | même effet, pour une carte qui voudrait plus | non (un script sur 400 épisodes prend quelques secondes au plus) | code de l'étage v5, hors de ce tour |
| parts 44 et 6 USD, pire cas réservé avant chaque étage (`pole/tour_ferme_v63.py:250-258`, `:801-802`) | arrêt avant un étage, code 3, aucune issue, chiffres partiels | non : dès ≈ 55 testés à la borne (≈ 61 à 12 tours), ≈ 1,7 fois le devis ; seul un excès de promotions (asymétrie, mineur 41) | couvrir le maximum théorique de 144 testés : ≈ 130 USD (+80 USD au GO) |
| plafond de l'étage, 50 USD (`pole/tour_ferme_v63.py:246-247`) | filet derrière les parts (somme des parts = plafond) | non | — |
| durée, 24 h (`pole/tour_ferme_v63.py:260-262`) | arrêt, code 3, aucune issue | non : seuils ≈ 81 à 179 s par session à 12 tours, ≈ 565 s à 3 tours (mineur 40) | 72 h : 0 USD, texte seul (plan et cinq phrases) |
| délai de 1 800 s par appel de commande externe (`pole/adaptateurs.py:622`, non réglable ici) | session en erreur, arrêt, code 3 | non (un appel de 30 minutes est un appel pendu) | code neuf (délai lu dans la configuration) ; la conséquence est dite en A.6 (« session en erreur → arrêt ») |
| plafond de session des proposeurs (`plafonds_session.proposeur`, configuration ; A.5) | « budget_depasse » → arrêt | non s'il est pris large (A.5 conseille ≥ 0,50 USD ; la configuration du 1er novembre est au-dessus) | 0 USD |
| plafonds de session passés aux commandes (expérimentateur : reste de 0,80 USD ; vérificateur : 0,1 USD) contre la réservation propre des commandes | refus de la commande → « erreur » → arrêt (I32) | inconnu d'ici : code des commandes privé | 0 USD si les commandes acceptent ; sinon leurs options, dans la configuration, avant son empreinte (A.6 bis) ; relever la borne du vérificateur : code neuf et parts à refaire (I32) |
| borne de 2 000 caractères de la loi servie (`TAILLE_MAX_LOI_SERVIE`) | refus au gardien, au seul bras recopie (mineur 36 de la contre-lecture 3, l. 136) | non (mesuré par S5 et P8) | — |
| gardien : fréquence et phase d'oscillation non bornées | exception au juge sur une instance dont un trait dépasse ±8 en valeur absolue : arrêt | non : probabilité ≈ 10⁻¹⁵ par tirage ; trou dit au rapport v4 (réserve 3), pas au texte : pour mémoire | borne au gardien (code neuf) |

## 6. Ce qui reste avant le scellement, dans l'ordre

1. **Couples T101 à T112** (section 7 et `prereg/couples-contre-lecture-tour-ferme-v5.json`), par le directeur ; texte seul.
2. **Décision du mineur 40** (Lazar ou le directeur) : 72 h ou 24 h ; défaut : 24 h tel qu'écrit, avec T103, T104 et T108.
3. **Session-depot** : la configuration v3 (annexe A ; Kimi et Argon en commande externe), **le constat de A.6 bis** (rôles et plafonds
   de session acceptés par ses deux commandes, par lecture de leur code), puis l'empreinte du fichier définitif portée à la clé
   `configuration_sha256` ; `bwrap` 0.9.0, identité dédiée, `TMPDIR=/tmp`, machine jetable ; un passage `--verifier-seulement` qui
   rend « conforme » sur le texte scellé.
4. **Registre** : une ligne de précision pour GO-2026-11-02-23 (mineur 42), par le directeur.
5. **Scellement** par le directeur : titre et statut récrits (l. 1 et 3), nom `preenregistrement-tour-ferme-v1-v<N>.md`, compagnon
   `.sha256`, commit et poussée **avant** la course ; revérifier alors le bloc (il ne change pas avec ces couples). Après la course :
   lecture par `demonstrations/lire_tour_ferme_v63.py … --releve-sha256 SHA`, verdict par un lecteur neuf (R13).

Aucun point de ce rapport ne demande d'appel de modèle, de dépense, ni de code neuf.

## 7. Remplacements (couples T101 à T112)

Fichier de référence : `prereg/couples-contre-lecture-tour-ferme-v5.json` (même contenu). À appliquer dans l'ordre, chacun sur le
texte obtenu après les précédents ; chaque cible figure exactement une fois dans le brouillon 5 (`c81aa6ef…`) et encore une fois à
son application ; aucun texte nouveau ne porte de marqueur `<<…>>` ni de balise de zone.

**T101** — mineur 44 (en-tête : commit des fichiers `_v63`) ; brouillon 5, l. 5

remplacer :

~~~~text
cinq d'entre eux modifiés dans l'arbre de travail, non commités)
~~~~

par :

~~~~text
cinq d'entre eux modifiés dans l'arbre de travail, non commités à l'écriture du texte, commités depuis au commit `a12713a`)
~~~~

**T102** — mineur 39 (section 0, point 1 : la borne au prix du devis) ; brouillon 5, l. 17

remplacer :

~~~~text
aucune carte n'est jugée sur une exécution tronquée par la borne (sections 4.1 et 12).
~~~~

par :

~~~~text
à ce prix, aucune carte n'est jugée sur une exécution tronquée par la borne ; au-delà de 0,067 USD par tour en moyenne (prix réel d'un tour inconnu, C7), ce que la borne coûte est écrit en section 12 (sections 4.1 et 12).
~~~~

**T103** — mineur 40 (section 0, point 3 : ce que la durée coupe) ; brouillon 5, l. 19

remplacer :

~~~~text
3. **Durée de l'étage 1 : 24 heures** (4 au brouillon 4) : garde contre une boucle folle, jamais un couperet (section 12).
~~~~

par :

~~~~text
3. **Durée de l'étage 1 : 24 heures** (4 au brouillon 4) : garde contre une boucle folle, qui ne coupe jamais une carte ni un étage en cours ; si elle mordait, la course s'arrêterait sans issue (code 3) : seuils en section 12.
~~~~

**T104** — mineur 40 (section 7, garde 13) ; brouillon 5, l. 455

remplacer :

~~~~text
durée > plafond (24 h étage 1, garde contre une boucle folle, jamais un couperet ; 2 h étage 2)
~~~~

par :

~~~~text
durée > plafond (24 h étage 1, garde contre une boucle folle, qui ne coupe jamais une carte ni un étage en cours, seuils en section 12 ; 2 h étage 2)
~~~~

**T105** — mineur 44 (section 10 bis : contre-lecture courte faite) ; brouillon 5, l. 525

remplacer :

~~~~text
**Contre-lecture R2 courte et neuve à faire, sur ce texte, le diff v62 → v63 (code v63 du brouillon 5) et les essais neufs.**
~~~~

par :

~~~~text
Contre-lecture R2 courte et neuve, sur ce texte, le diff v62 → v63 (code v63 du brouillon 5) et les essais neufs : `prereg/contre-lecture-courte-preenregistrement-tour-ferme-v5.md` (2 novembre 2026, sous-agent neuf), verdict « scellable après couples » (aucun bloquant ; important I32 ; mineurs 39 à 44) ; ses couples T101 à T112 (`prereg/couples-contre-lecture-tour-ferme-v5.json`) sont appliqués à ce texte ; empreintes des deux fichiers dans leurs compagnons `.sha256`.
~~~~

**T106** — mineur 39 (section 12 : prix de la borne, s'il était dépassé) ; brouillon 5, l. 565

remplacer :

~~~~text
(12 × 0,06 = 0,72 USD ; la borne ne mord qu'au-delà de 0,067 USD par tour en moyenne) : aucune carte n'est jugée sur une exécution tronquée par la borne.
~~~~

par :

~~~~text
(12 × 0,06 = 0,72 USD ; la borne ne mord qu'au-delà de 0,067 USD par tour en moyenne, prix réel d'un tour de Kimi inconnu, C7) : à ce prix, aucune carte n'est jugée sur une exécution tronquée par la borne. Prix de la borne, si ce prix était dépassé : une carte qui voudrait ses 12 tours finirait ses tours à la borne (champ `fin_des_tours` de son `resultat.json` scellé : « plafond de la fiche … atteint » ou « budget_depasse ») et serait jugée sur ce qu'elle a exécuté — « non concluant » sans exécution réussie, compté par T4 —, jamais un arrêt du fait du code (pour les commandes des relais : annexe A, A.6 bis).
~~~~

**T107** — mineur 41 (section 12 : où mord le plafond, asymétrie R4) ; brouillon 5, l. 576

remplacer :

~~~~text
il faudrait que le juge promeuve presque tout, témoins faux compris, ce que L1, L2 et L2b excluent ; si cela arrivait, la course s'arrêterait avant un étage (arrêt de la liste, code 3, aucune issue lue), jamais sur une carte tronquée.
~~~~

par :

~~~~text
il faudrait que le juge promeuve presque tout, témoins faux compris, ce que L1, L2 et L2b excluent. L'arrêt viendrait bien avant ce maximum : dès ≈ 55 cartes et témoins testés si chacun dépense sa borne (≈ 61 à 12 tours au prix du devis ; davantage si les tours coûtent moins), soit ≈ 1,7 fois le devis — par exemple un bras réel promu presque entier à chaque génération, ou un juge laxiste ; la course s'arrêterait alors avant un étage (arrêt de la liste, code 3, aucune issue lue, chiffres partiels rapportés), jamais sur une carte tronquée. Asymétrie dite (R4) : seul un excès de cartes testées, c'est-à-dire de promotions, peut faire mordre ce plafond, et l'arrêt prendrait alors la place de l'issue qu'il aurait fallu lire (« ne tient pas (T3, T5) » d'un juge laxiste, ou l'issue A4 d'un bras réel très fécond).
~~~~

**T108** — mineur 40 (section 12 : seuils de la durée) ; brouillon 5, l. 576

remplacer :

~~~~text
il ne peut mordre avant le plafond de dépense que si la session moyenne dépasse ≈ 93 s avec 54,9 cartes testées à 12 tours (≈ 179 s aux tailles du devis), plus du double de la latence du devis ; une course saine ne l'atteint pas,
~~~~

par :

~~~~text
il mord avant le plafond de dépense si la durée moyenne d'une session dépasse (24 h − durée des exécutions du bac) / nombre de sessions : à 12 tours par carte, ≈ 179 s aux tailles du devis (31,7 testés), ≈ 93 s à 54,9 testés (tous à leur borne), ≈ 81 s à 60,7 testés (12 tours au prix du devis), moins encore si des tours moins chers laissaient tester plus de cartes ; à 3 tours par carte aux tailles du devis, ≈ 565 s (exécutions comptées à 3 × 120 s par carte) ; la latence réelle d'une session de Kimi expérimentateur n'est pas mesurée (devis : 10 à 40 s par appel) ; une course aux tailles du devis ne l'atteint pas,
~~~~

**T109** — mineur 44 (section 13 : bloc d'empreintes revérifié après commit) ; brouillon 5, l. 615

remplacer :

~~~~text
modifiés au brouillon 5, non commités : à revérifier après commit ;
~~~~

par :

~~~~text
modifiés au brouillon 5, non commités à l'écriture, commités depuis au commit `a12713a` ; revérifiées par la contre-lecture courte du 2 novembre 2026 : les 91 empreintes égales à l'arbre de travail, à `a12713a` et à la tête `08b1f17` ;
~~~~

**T110** — mineur 44 (section 14, point (2)) ; brouillon 5, l. 739

remplacer :

~~~~text
(2) la contre-lecture R2 courte et neuve de ce brouillon 5, du diff v62 → v63 et des essais neufs, par un sous-agent neuf ;
~~~~

par :

~~~~text
(2) fait : la contre-lecture R2 courte et neuve de ce brouillon 5, du diff v62 → v63 et des essais neufs, par un sous-agent neuf (`prereg/contre-lecture-courte-preenregistrement-tour-ferme-v5.md`), ses couples appliqués ;
~~~~

**T111** — I32 (section 14, point (4) : le constat de la session-depot) ; brouillon 5, l. 740

remplacer :

~~~~text
liste exacte de ce que le code lit : annexe A ; son empreinte va à la clé `configuration_sha256` du plan gelé)
~~~~

par :

~~~~text
liste exacte de ce que le code lit : annexe A ; son empreinte va à la clé `configuration_sha256` du plan gelé ; avant d'écrire ce fichier, le constat de l'annexe A, A.6 bis : rôles et plafonds de session acceptés par ses deux commandes)
~~~~

**T112** — I32 (annexe A, A.6 bis neuve : ce que les commandes des relais doivent accepter) ; brouillon 5, l. 841

remplacer :

~~~~text
**A.7 — Vérificateur et expérimentateur : modèle, port, effort.**
~~~~

par :

~~~~text
**A.6 bis — Ce que les commandes des relais doivent accepter (contre-lecture courte, I32).** Le code ne voit d'une commande que son code de sortie et sa dernière ligne : il ne peut savoir ni si elle joue le rôle qu'il lui donne (`ROLE_POLE`), ni si elle refuse une session dont `PLAFOND_SESSION_USD` est sous sa propre réservation de pire cas (sortie maximale de son rôle, plancher de sortie). Une commande qui refuse — code de sortie non nul, ou coût absent ou nul — rend « erreur » : session en échec, **arrêt de la course** (code 3, aucune issue), même pour le vérificateur, qui n'est jamais décisif ; la configuration étant gelée par son empreinte, la corriger exige un texte nouveau (la reprise de la section 7 ne vaut que pour une panne d'infrastructure). Le passage `--verifier-seulement` n'appelle rien et ne le voit pas ; aucune course à blanc ne l'a joué (doublures) ; l'étage des tests de mort n'a jamais tourné pour de vrai avec ces relais (section 1). Avant d'écrire le fichier définitif et son empreinte (A.2), la session-depot vérifie par lecture du code de ses deux commandes (aucun appel) : Kimi accepte `proposeur_ideation` et `experimentateur_test`, Argon `proposeur_ideation` et `lecteur_test` ; aucune ne refuse avant dépense une session dont le plafond vaut, pour l'expérimentateur, le reste de la borne de 0,80 USD de la carte (0,80 USD au premier tour, parfois quelques centimes au dernier), pour le vérificateur 0,1 USD à chaque session (le plus bas des plafonds fixes de la course), pour un proposeur `plafonds_session.proposeur` ; au besoin, elle règle les options de ses commandes dans la configuration, gelées ensuite par son empreinte. Elle écrit ce constat avec l'empreinte qu'elle remet.

**A.7 — Vérificateur et expérimentateur : modèle, port, effort.**
~~~~
