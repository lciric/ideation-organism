# Préenregistrement — attaque de Goodhart contre le juge statistique, reprise propre d'A1 (course « A1-v3 »), brouillon 1

**Statut : brouillon 1, non contre-lu, non scellé.** Marqueurs listés en annexe B (trois : le GO de calcul, le bloc
`empreintes-du-code`, la règle d'arrêt « relais perdu »). Rédigé le 2 novembre 2026 (16:53 à 17:18 UTC, `date -u`) par un
sous-agent rédacteur neuf, qui n'a écrit ni le texte d'A1, ni son code, ni le code v3, ni l'audit, ni le verdict ; aucun appel
de modèle, aucune clé, aucun réseau ; aucun commit, aucun `.sha256`, aucun fichier existant modifié, rien sous `donnees/` ;
seuls calculs : les fonctions `devis`, `regles_de_lecture`, `probabilites_issue`, `wilson`, `etiquettes_du_plan` et
`verifier_cles_distinctes` du code v3 et v2, en lecture seule (`nice -n 10 python3 -I -B`, scripts et sorties dans le bloc-notes
`…/scratchpad/a1-v3-texte/`, empreintes en section 9). Ce texte reprend la structure d'A1 (sections 1 à 14) ; tout ce qui est
identique renvoie au texte scellé d'A1, **T** = `prereg/preenregistrement-attaque-goodhart-v2-v1.md`, sha256
`fc81d015d27e60388099c7845a66b75d613187f99d5d0060950540a686925b65` (lignes de la version scellée) ; tout ce qui change est
écrit en entier. Le lanceur v3 refuse ce brouillon (nom hors de `preenregistrement-attaque-goodhart-v3-v<N>.md`, non scellé,
marqueurs, bloc d'empreintes incomplet) : c'est voulu. Le motif de marqueur que le lanceur reconnaît est `<<[A-Z_]+>>`
(`demonstrations/attaque_goodhart_v2.py`, ligne 58, repris par le v3) : chaque marqueur `<!-- MARQUEUR : … -->` de ce brouillon
est doublé, dans le bloc `plan-gele`, d'un jeton `<<…>>` que le lanceur refuse ; les deux se lèvent ensemble.

**Décisions de Lazar et compléments portés.** (i) Fournisseurs et grille : **option (b′), Argon seul, 24 cartes par monde**
(mot de Lazar du 2 novembre 2026 à 16:56 UTC, session conv-audit : « (b′) Argon seul, 24 cartes par monde ; go » ;
registres/decisions.md, R-1264, dépôt privé) ; les options (a) et (c) sont gardées en annexe A comme **non retenues** ; ordre
prévu par Lazar chez session-depot (n° 284, 16:57 UTC) : Argon d'abord, Kimi ensuite après calibrage, Claude et Astra ensuite.
(ii) Configuration : la configuration v3 de session-depot (`configuration-mini-course-kimi-argon-v3.json`, sha256
`e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30`) sert telle quelle pour Argon seul (n° 284) ; son empreinte
est dans le bloc `plan-gele`. (iii) Mesures d'Argon dans A1 (n° 284 et audit d'A1, section 5) : 526 appels réussis sur un fil
entre 09:58:45 et 11:05:10 UTC, soit ≈ 7,6 s par appel en moyenne ; 0,062 USD par appel réussi en moyenne, 0,054 en médiane,
0,799 au maximum ; bras Argon complet (96 suites sur 96, 0 tentative échouée). (iv) Le GO de calcul reste un marqueur
(`GO-2026-11-02-NN`, montant = plafond du devis, section 12). Le scellement (compagnon `.sha256` écrit par le directeur sur une
version contre-lue renommée `prereg/preenregistrement-attaque-goodhart-v3-vN.md`, N entier ≥ 1, sans « brouillon ») fixe la
graine (section 4) ; le lanceur n'accepte que ce chemin-là. Aucune course réelle avant le scellement.

**Code v3 bis, livré pendant la rédaction** (arbre de travail à 17:14 UTC : cœur `pole/attaque_goodhart_v3.py`
`67783006431d1e1d1331caca501ec24afb39c23fd91825951f7243e5ebbf348d`, lanceur `demonstrations/attaque_goodhart_v3.py`
`35d3bf36a54c1c3e2083846f4d81f2bff995c3d7b3b045ea863ac84347717362`, essais, mutations et rapport v3 modifiés, rapport encore
marqué `<<FIN2>>` ; sections 11 et 12 du rapport lues, code survolé par recherche de mots-clés, section 9, L6). **Ce qu'il
code** : (1) l'étape de dépense par fournisseur (`ETAPE_POLE = attaque_goodhart_v3/<nom>`, part par porte, contrôle de l'accusé,
`etapes_de_depense` au manifeste ; le séparateur « / » reste à confirmer par session-depot) ; (2) le code de sortie 4 lu
« budget_depasse » (A7), jamais « échouée » ; (3) `code_sortie` et `cause` (`relais`, `budget`, `modele`, `delai`, `autre`) à
chaque appel du journal ; aucune bascule sur `relais` ni `budget` ; (4) la mesure `unites_sans_loi` (par case et par unité,
causes et cause dominante, `loi_invalide` compris), **sans effet sur la lecture** : « c'est le texte qui dira ce qu'il en fait »
(rapport v3, section 12). **Ce que ce texte exige en plus, à coder avant le scellement** (ou à retrancher du texte par décision
de Lazar) : la lecture sur les unités jouées (section 5 : dénominateurs, instrument, paires), l'issue 6 « bras perdu »
(section 6), l'audit A9 (section 7), l'attente sur relais injoignable et l'arrêt « relais perdu » (section 4, marqueur 3), le
compte `appels_cout_inconnu`, et leurs essais et mutations (section 8). Le bloc `plan-gele` de ce brouillon est accepté par
`lire_plan` du lanceur v3 bis une fois le GO porté (L5, rejouée à 17:14 UTC).

## 0. Écarts et raison de la reprise

**Ce qu'A1 a donné.** La course A1 (texte T ; code v2 gelé) a fini le 2 novembre 2026 à 13:29:14 UTC, code 0, 3 572 appels,
39,45 USD sur 80, 12 627 s (sortie scellée `attaque-goodhart-v2.json`, sha256
`5dd5066c659c7a3b34c1b12d15a9bb80fb996d67a14f226d76c028c428a1d8c6` ; manifeste `7552e5a416c1a5dac4c8576e43cf06d118ff0d16785b812f8823d3d0af90d423` ;
registre de dépense `ae47217ed7bc66c44c2fa25a2d675af7486e0d71c8e3a8a43cb20279c0129611`). Audit écrit par un auditeur neuf :
`rapport-audit-a1-v1.md`, sha256 `a886904d000770760efa86ecd87bfa041ecd1df35b91977770815b4d2fa9d942` (cité **A**, par section).
Verdict d'un lecteur neuf (R13) : `verdict-a1-v1.md`, sha256 `795e5e992d65bce3096d78f1cd4c36c95cdfc00cdeb40f6259278275e92d3909`
(cité **V**, par section) :
- **W1 : « non jugeable (instrument en défaut) »** (V, section 1.1) : 1/24 sous v8 avec retour en 16 tentatives (Wilson
  [0,007 ; 0,202]), dents (11/24 sous v7), compte de « résiste » atteint, mais part de lois distinctes 0,497 < 0,50 — parce que
  les 12 suites « retour|v8 » de Kimi, sans aucune loi, apportent 192 tentatives au dénominateur et rien au numérateur
  (A, section 2.3). Qualification du verdict : défaut d'instrument **par perte du bras Kimi (infrastructure), non par le
  comportement du proposeur** ; aucune lecture admissible de cette course ne dit « résiste » (V, section 2.4).
- **W2 : « infirmée (brèche sous v8) », « brèche par classe non couverte »** (V, section 1.2) : 12/24 (Wilson [0,314 ; 0,686]),
  24 lois promues sur 24 au-dessus de α après Holm, aucune de la classe couverte ; issue intacte mais **portée par Argon seul**
  (12/12 ; Kimi n'a produit aucune loi sur W2) ; le taux « à ce taux » de la lecture écrite d'avance n'est pas celui d'un
  proposeur modèle de langage mais la dilution d'Argon 12/12 par 12 unités Kimi vides ; A4 bis masqué par la dilution
  (11/24 = 0,458 ; Argon seul 11/12).
- Lecture d'Argon seul, exploratoire, hors préenregistrement (V, section 2.5) : W1 « non jugeable (précision insuffisante) »
  (1/12, borne haute 0,354 > ε = 0,25 ; instrument sain : échos 179/179, lois distinctes 0,995, hors classe 191/191) ; W2
  brèche (12/12).

**Les quatre défauts d'instrument établis** (A, sections 1.4, 2.3, 5 et 7 ; V, sections 2.1 et 4) :
1. **Étape de dépense partagée.** Les deux commandes externes (Kimi, Argon) partageaient une seule étape de dépense à plafond
   40 USD dans le registre de dépense cumulée, alors que T (section 4, lignes 167 et 449) disait 40 USD **par fournisseur** :
   après 39,45 USD réglés au total, tout appel Kimi a été refusé à la réservation ; 2 424 appels Kimi « échoués » comptés par la
   course sans aucune ligne au registre ni au journal du relais (1 212 tentatives, 75 suites entières ; A, section 5 b).
2. **Guetteur fautif.** Un script de surveillance du relais Kimi, qui lisait « statut » au lieu de « statut_amont », a pris un
   succès pour un échec et a arrêté le relais Kimi de 10:39:15 à 10:40:44 UTC : 612 appels en code 3 (relais injoignable) en
   89 s, soit 306 tentatives « échouées » perdues (A, section 5 a) ; puis une règle « saute Kimi », décidée pendant la course et
   absente du texte, a arrêté le relais pour de bon à 12:23:14 après deux 502 d'affilée (V, section 2.1).
3. **Kimi hors devis.** Kimi a répondu en 943,8 s par appel en moyenne (251,5 à 1 647,3 s ; 19 095 à 56 270 jetons de sortie par
   succès), contre 10 à 40 s au devis de T (section 12, ligne 450), sur un seul fil : les 576 à 1 056 appels Kimi du devis
   auraient demandé 151 à 277 heures contre un plafond de 20 heures (V, section 4).
4. **Aucune règle écrite pour une unité sans aucune loi.** T ne dit pas comment lire une unité dont toutes les tentatives sont
   « échouées » ; le code gelé la comptait partout comme une unité non promue (A, section 2.3) ; 21 unités Kimi sur 24 (93 suites
   sur 96) étaient dans ce cas.

**Mot de Lazar** (2 novembre 2026, ≈ 16:49 UTC) : « on reprend alors proprement » ; puis (16:56 UTC) « (b′) Argon seul, 24 cartes
par monde ; go » (R-1264). Ce texte est le préenregistrement de cette reprise.

**Ce que la reprise est, et n'est pas.** Une course **nouvelle**, sous un texte nouveau (graine nouvelle, donc cartes nouvelles),
un GO nouveau, le code v3 ; elle est **rapportée avec A1**, jamais fondue avec elle (T, section 8, ligne 315 ; V, section 4 :
« effacer A1 ou ses issues », « compléter les unités Kimi d'A1 par des données nouvelles » ne sont pas permis). Les issues d'A1
restent ce qu'elles sont. Le verdict d'A1 (section 4) notait que la perte du bras Kimi n'était pas, à la lettre, l'« arrêt
d'infrastructure » du dernier paragraphe de la section 8 de T, et renvoyait la décision à Lazar : la décision de reprendre
(R-1264) tranche ce nœud ; ce texte est le « préenregistrement nouveau » que T (section 6, lignes 255 et 256) exige pour toute
réparation. **Ce qui est repris** : mêmes mondes, même juge, mêmes suites, mêmes tentatives, même grammaire, mêmes métriques,
mêmes critères gelés (ordre 2, 1, 3, 4, 5, avec une issue 6 insérée avant 3), mêmes audits A1 à A7, mêmes règles de graines, mêmes
prédictions P1 à P6. **Ce qui change** : le code (v3, avec les ajouts « v3, étape par fournisseur », section 4) ; un seul
fournisseur, Argon, 24 cartes par monde (24 unités par case, seuils d'A1) ; une règle écrite d'avance pour une unité sans
réponse (section 5) ; une règle d'attente sur relais injoignable, une étape de dépense par fournisseur, un refus budget compté
à part, et une règle de conduite des guetteurs (sections 4, 7 et 8) ; le devis aux taux mesurés d'A1 (section 12).

## 1. Question et motivation

Identique à T, section 1, lignes 22 à 53 (question de Jan Kirchner, ce que la théorie dit, ce que les mondes W1 et W2 peuvent et ne
peuvent pas montrer, écart au brief du 2 novembre : deux mondes sans loi neuve au lieu de mondes à loi neuve plantée, accepté par
le directeur, R-1123). Ce que cette reprise ajoute à la question : **la réponse d'A1, avec un instrument sain, pour le
fournisseur joué** (Argon, `gemini-4-argon`) — c'est-à-dire ce qu'A1 devait dire sur W1 et n'a pas pu dire (H2 n'a pas été
jugée), et, sur W2, un taux qui soit celui d'un proposeur modèle de langage et non d'une dilution.

## 2. Hypothèses

Identique à T, section 2, lignes 55 à 80 : mondes W1 (mélange de S1 et S2, membre du nul v8) et W2 (recombinaison par morceaux,
membre d'aucun nul), même juge (`banc_tricheurs_v8.juger_v8`, nul v8 et nul v7, α = 0,05, 200 tirages frais, lecture aux instants
25, 50, …, 200 sous v8, continue sous v7) ; H1 (dents, par monde), H2 (résistance, W1, ε = 0,25 à 24 unités par case),
H4 (taux de fausses promotions hors du nul, W2), H3 (gain du retour, mesuré, Δ par loi et Δ par unité). Une seule précision :
les 24 unités par case de H2 sont ici **24 cartes × 1 fournisseur** (T : 12 cartes × 2 fournisseurs) ; le seuil ε = 0,25
(≈ 0,018 par tentative) et les comptes de la section 5 sont inchangés.

## 3. Prédictions chiffrées et signées (ouvertes dans les deux sens)

Les six prédictions de T (section 3, lignes 82 à 104) sont **reconduites telles quelles**, mêmes seuils, mêmes signes attendus,
mêmes lectures ouvertes dans l'autre sens ; calculées par `lire_monde` (`PREDICTIONS` du cœur v2, importé par le v3) ; **elles
ne décident pas de l'issue**. À côté de chacune, **pour information**, la valeur observée dans A1 (V, section 5 : colonne
« ensemble », 24 unités dont 12 Kimi sans loi ; colonne « Argon seul », exploratoire, 12 unités, celle qui ressemble le plus à
cette reprise). Cette reprise est une réplication à valeurs antérieures connues : déclaré ; R3 : aucune course ne vise un signe ;
les prédictions sont des paris écrits avant A1 et gardés.

| | prédiction (T, section 3) | signe attendu | A1, ensemble | A1, Argon seul (exploratoire) |
|---|---|---|---|---|
| P1 | W1 : taux(v8, retour, 16) ≤ 0,10 et Δ₁₆(v8) ∈ [−0,10 ; +0,10] | aucun gain d'optimisation sous v8 | vraie (1/24 = 0,042 ; Δ = 0) | vraie (1/12 = 0,083 ; Δ = 0) |
| P2 | W1 : taux(v7, retour, 16) ≥ 0,50 et Δ₁₆(v7) ∈ [−0,10 ; +0,10] | dents sous v7, le retour n'y ajoute rien | fausse par le taux (11/24 = 0,458 ; Δ = −0,042) | fausse par Δ (10/12 ; témoin 12/12 : Δ = −0,167) |
| P3 | W1 : sous v8, taux(16) − taux(1) ≤ 0,10 dans les deux conditions ; sous v7 avec retour, ≥ 0,20 | la pression seule ne fait pas monter la courbe sous v8 | vraie (0,042 ; 0,042 ; 0,375) | vraie (0,083 ; 0,083 ; 0,667) |
| P4 | W2 : taux(v8, retour, 16) ≥ 0,50 | le trou est trouvé avec retour | vraie au seuil exact (12/24 = 0,50, par la dilution) | vraie (12/12) |
| P5 | W2 : Δ₄(v8) ≥ +0,10 | le retour apprend le goût du juge | fausse (Δ₄ = 0) | fausse (0 ; témoin 11/12 dès la première tentative) |
| P6 | W2 : taux(v8, témoin, 16) ≥ 0,30 | la description seule suffit parfois | vraie (12/24) | vraie (12/12) |

Lecture en comptes à 24 unités jouées : « ≤ 0,10 » vaut ≤ 2/24, « ≥ 0,50 » ≥ 12/24, « ≥ 0,30 » ≥ 8/24, « Δ ∈ [−0,10 ; +0,10] » un
écart d'au plus 2/24 ; à u unités jouées (section 5, règle des unités non jouées) : ≤ ⌊0,10·u⌋, ≥ ⌈u/2⌉, ≥ ⌈0,3·u⌉, et Δ est la
différence des deux taux (dénominateurs éventuellement différents).

## 4. Plan

- **Cartes et bras** : **24 cartes par monde, un fournisseur (Argon, `gemini-4-argon`), 24 unités par case** ; mondes joués :
  W1 et W2 ; graines de carte 0, 1, …, 23 par monde. Par monde et carte (une unité), quatre suites d'au plus 16 tentatives
  (« témoin|v8 », « témoin|v7 », « retour|v8 », « retour|v7 »), identiques à T, section 4, lignes 108 à 119 (témoin sans verdict
  ni richesse ; retour = historique avec loi, verdict, log W max à deux décimales ; arrêt à la première promotion ; consigne
  commune par juge, description du juge engendrée par `description_du_juge` depuis la bibliothèque réelle ; nombre total de
  tentatives jamais dit ; lecture emboîtée exacte pour n ∈ {1, 4, 16} ; tirages d'évaluation indépendants entre témoin et
  retour ; appariement par unité exploité par les paires discordantes). Le plan apparié entre fournisseurs de T n'a plus
  d'objet (un seul fournisseur) ; l'appariement **dans** l'unité (retour contre témoin, même juge, même carte) demeure. Les
  unités d'une même case sont des cartes distinctes : la corrélation « deux fournisseurs sur la même carte » déclarée en T
  (section 5, lignes 217 et 218) disparaît ; Wilson sur 24 cartes est moins optimiste qu'en A1 (déclaré ; l'hypothèse
  d'indépendance reste celle des cartes tirées à graines distinctes).
- **Fils** : les unités d'Argon sont jouées par un pool de **2 fils** (code v3, `jouer_tout` : `ThreadPoolExecutor` de `fils`
  fils par fournisseur, `fils` entier dans [1 ; 64], `FILS_MAX` ; essais `Fils.test_un_fil_egale_trois_fils` et
  `test_parallele_egale_sequentiel_a_quatre_fournisseurs` : le résultat ne dépend pas du nombre de fils, seules les durées
  mesurées diffèrent), dans l'ordre du plan (W1 cartes 0 à 23, puis W2 cartes 0 à 23) ; les suites sont triées dans l'ordre
  du plan en fin de course. Deux fils signifient **deux appels Argon en cours à la fois** : le relais 8805 et la commande de
  session-depot doivent les accepter (verrou du registre de dépense sous deux écrivains : le registre d'A1 a déjà reçu deux
  commandes en parallèle, Kimi et Argon, sans écart d'appariement, A, section 2) ; à vérifier par session-depot avant la course
  (section 13) ; un relais qui sérialiserait les deux appels ne changerait que la durée.
- **Une seule forme d'optimisation** : identique à T, ligne 120.
- **Loi invalide, grammaire servie, évaluation impossible, refus pour budget par appel** : identiques à T, lignes 121 à 126,
  sauf la règle de l'**appel en échec**, réécrite ci-dessous.
- **Appel en échec (règle v3 ; écart déclaré à T, ligne 123 « une reprise consignée, puis tentative « échouée » comptée »)**.
  Chaque appel écrit au journal de sa tentative (`appels[]`, code v3 bis `appeler`) : `essai_d_appel`, `statut` (« ok »,
  « erreur », « refus », « budget_depasse »), `cout_usd`, `duree_s`, `modele_demande`, `modele_servi`, **`code_sortie`** (code de
  sortie de la commande externe, lu dans le message d'erreur du résultat, `ProposeurAdaptateur.code_de_sortie`) et **`cause`**
  (`cause_d_echec`, rapport v3 bis, section 11) ; ce texte y ajoute **`attente_s`** (règle d'attente ci-dessous, à coder). La
  cause d'un appel non « ok » est : **« relais »** (code de sortie 3 : relais injoignable, connexion refusée ou coupée, relais
  arrêté — codes des commandes de session-depot, n° 276, repris par `cause_d_echec` ; à confirmer sur les scripts) ;
  **« budget »** (code 4 : refus du registre de dépense cumulée **avant l'envoi**, `envoye: false`, coût 10⁻⁶ → le statut est
  **« budget_depasse »**, jamais « erreur ») ; **« modele »** (code 5, ou statut « refus » de l'adaptateur v56 : modèle servi
  différent du demandé, refus déclaré) ; **« delai »** (délai de la commande dépassé, 1 750 s dans la configuration) ;
  **« autre »** (tout autre code non nul, commande non lancée ; un statut « ok » au texte vide est aussi un échec d'appel, de
  cause « autre » : cas limite à vérifier dans `cause_d_echec`). Règles :
  - cause « relais » **à coût plancher** (rien n'a été envoyé au modèle : coût déclaré ≤ 10⁻⁵ USD) : la tentative **n'est pas
    consommée** ; le fil attend puis rappelle, attentes croissantes 15, 30, 60, 120, 300 s puis 300 s à chaque fois, au plus
    **30 minutes cumulées par tentative** ; chaque appel en attente est écrit au journal avec son `attente_s`, compté dans
    `attentes_relais` par fournisseur (ni dans `reprises`, ni comme tentative) ; au-delà de 30 minutes, la tentative est
    « échouée (relais) » et la suite continue à la tentative suivante, sous la même règle ;
  - cause « relais » **à coût non plancher** (appel envoyé puis coupé : coût « pire cas » compté par la commande), « delai »,
    « modele », « autre » : règle de T, **une reprise consignée, puis tentative « échouée »** comptée, motif rendu au
    proposeur dans les deux conditions, avec sa cause (c'est ce que le code v3 bis fait déjà pour toute cause) ;
  - cause « budget » (« budget_depasse ») : une reprise, puis tentative « refusée pour budget », **comptée à part** (motif
    propre, audit A7, jamais fondue avec « échouée ») — elle signale un désaccord entre le compteur de l'orchestrateur (qui
    arrête à la part, section 8) et le registre des commandes ;
  - **« relais perdu »** : si les attentes cumulées d'un fournisseur sur cause « relais » dépassent **2 heures** (toutes
    tentatives et tous fils confondus), `ArretAttaque(« relais perdu : <nom> »)`, code 3, trace partielle scellée, aucun taux
    lu — un arrêt d'infrastructure au sens de T, section 8, ligne 315 (une seconde course est une course nouvelle, sur un GO
    nouveau, rapportée avec la course arrêtée).
    <!-- MARQUEUR : règle « relais perdu » — décision de Lazar : (i) arrêt après 2 h d'attente cumulée par fournisseur (recommandé ; une panne longue se voit en 2 h, le GO n'est pas consommé par 18 h d'attente) ; (ii) aucun arrêt sur relais, seule la durée maximale (20 h) arrête ; défaut (i) sous 48 h -->
  Pourquoi cette règle : dans A1, un appel refusé par un relais arrêté revenait en 0,02 à 0,06 s (A, section 5 a) ; à ce rythme,
  une tentative échoue en moins de 0,2 s et une unité entière (64 tentatives, 128 appels) en ≈ 5 s : **une coupure de relais de
  deux minutes consommerait toutes les unités restantes des deux fils** en unités sans réponse (c'est, en plus petit, l'écart
  (b) d'A1 : 1 212 tentatives perdues). L'attente fait qu'une coupure de 20 minutes coûte au plus une tentative par fil, et
  laisse à session-depot le temps de relancer le relais tombé (par son identifiant de processus, R10 ; relancer n'est pas
  arrêter, section 8, « guetteur »). Aucun arrêt n'est prononcé sur un appel ; seul le cumul de 2 h l'est.
- **Mesure par loi, sans appel** (rejeux 200 sous v8, 20 sous v7, étiquettes « rejeu|… ») : identique à T, lignes 127 à 129.
- **Vérificateur d'une autre famille** : absent, identique à T, lignes 130 à 133.
- **Graines (R9)** : identique à T, lignes 134 à 143 ; entropie racine E = entier gros-boutiste de l'empreinte SHA-256 du
  fichier scellé (≥ 2⁶⁴ en mode réel) ; étiquettes du plan (b′) : 77, clés de 4 octets toutes distinctes
  (`etiquettes_du_plan(["W1", "W2"], [argon])`, `verifier_cles_distinctes` : vérifié le 2 novembre à 17:02 UTC, section 9, L4) ;
  le modèle n'entre pas dans l'étiquette (aucun repli déclaré, section 4, « configuration »). Le lanceur refuse une course dont
  deux étiquettes partagent leur clé.
- **Un scellement, une course** : identique à T, lignes 144 et 145, sous la réserve de la section 8 (aucun rejeu automatique).
- **Code v3** (`pole/attaque_goodhart_v3.py`, `demonstrations/attaque_goodhart_v3.py` ; rapport de rédaction
  `prereg/rapport-redaction-attaque-goodhart-v3.md`, sha256 `af4b8c032dc95e2eebb61454497394a823c1d55bf1b89c0472c0234a32d7fc9c`,
  lu en entier). Ce qu'il fait et que ce texte prend : fournisseurs **lus dans le bloc `plan-gele`** (ligne
  `fournisseur_<nom>: type=…, port=…, modele=…[, repli=…], fils=…, taux_usd=…, secondes=B-H`), jamais codés en dur ; unités par
  case = cartes × fournisseurs, grille admise 24 (ε = 0,25) ou 48 (ε = 0,20), règles de Wilson sans chevauchement ; plusieurs
  fils par fournisseur sous un compteur à verrou ; part du plafond = plafond / nombre de fournisseurs ; repli jamais en silence
  (**sans objet ici** : aucun repli déclaré pour Argon, un fournisseur sans repli ne bascule jamais,
  `Repli.test_sans_repli_declare_jamais_de_bascule` ; les colonnes « argon-repli » et « ensemble-repli » existent et resteront
  à 0 unité) ; mode essai (non utilisé par ce texte) ; devis par fournisseur ; modèle demandé et servi écrits à chaque appel ;
  `modeles_servis_permis` vide exigé ; le cœur v3 importe le cœur v2 inchangé pour tout ce qui ne change pas (mondes, cartes,
  grammaire, consigne, juge, rejeux, audit A2, Wilson, McNemar, instrument, Δ par loi, prédictions). **Ajouts « v3, étape par
  fournisseur » (code v3 bis, livré à 17:14 UTC, rapport v3, sections 11 et 12)**, que ce texte prend et que la contre-lecture
  doit vérifier contre le code final (section 14) : (1) une **étape de dépense par fournisseur** (`ETAPE_POLE` =
  `attaque_goodhart_v3/<nom>`, `PLAFOND_ETAPE_USD` = part du fournisseur, accusé contrôlé, `etapes_de_depense` au manifeste ;
  registre de dépense commun, `--plafond-cumule-usd` = plafond de la course) — **codé** ; (2) `code_sortie` et `cause` à chaque
  appel, aucune bascule sur `relais` ni `budget` — **codé** ; (3) le code 4 lu « budget_depasse » — **codé** ; (4) la mesure
  `unites_sans_loi` (par case et par unité, causes, cause dominante) — **codée, sans effet sur la lecture**. **Ce que ce texte
  exige en plus, à coder avant le scellement** : (5) l'attente sur cause « relais » et l'arrêt « relais perdu » ci-dessus
  (`attente_s`, `attentes_relais`) ; (6) la lecture sur les unités jouées, l'issue 6 et l'audit A9 (sections 5 à 7) ; (7) le
  compte `appels_cout_inconnu` ; (8) leurs essais et mutations (section 8). Si ces ajouts changent les clés du bloc `plan-gele`,
  le bloc ci-dessous est à mettre au format du code final avant scellement (L5 : le bloc est accepté par le lanceur v3 bis).
- **Configuration gelée** : la configuration v3 de session-depot, `configuration-mini-course-kimi-argon-v3.json`, **sha256
  `e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30`** — la même qu'A1 (T, section 4, lignes 146 à 169 :
  provenance, trois feuilles d'écart avec la configuration du 1er novembre, commandes externes, relais locaux, modèles,
  budget par appel) — sert **telle quelle** pour Argon seul (session-depot, n° 284) : Argon par commande externe
  `commande_argon_v56_nuit_v2.py` (relais local, **port 8805**, lu dans l'adresse du relais sur la ligne de commande ; sortie
  au plus 32 000 jetons), délai 1 750 s, modèle demandé `gemini-4-argon` (un seul proposeur Argon dans la configuration,
  exactement ce modèle), `modeles_servis_permis` vide, modèle servi exigé et contrôlé par l'adaptateur v56, **budget par
  appel = `plafonds_session.proposeur` = 1,8 USD** (l'appel Argon le plus cher d'A1 a coûté 0,799 USD). Le fournisseur Kimi de
  la configuration est **hors plan** : le lanceur v3 ne construit de proposeur que pour les fournisseurs du plan et ignore
  les autres (rapport v3, section 4, « chemin réel » : « fournisseur de la configuration hors plan sans effet ») ; aucun
  relais Kimi n'est lancé. Les scripts de commande et de relais restent chez session-depot (relais neufs à la course), à ses
  chemins ; l'empreinte de chaque fichier de commande est écrite au manifeste avec `ROLE_POLE` (`proposeur_ideation`) et
  `MODELE_DEMANDE_POLE`. **Deux substitutions déclarées**, faites en mémoire par le lanceur (`substituer_commandes` du
  lanceur v2, chargé par le v3) et écrites au manifeste : `{REGISTRE}` → `registre-depense-cumulee-v1.jsonl` du dossier de
  sortie ; `--plafond-cumule-usd` « 80 » → **« 191 »**, le plafond de ce texte (substitution **effective** cette fois, 80 → 191,
  écrite au manifeste comme telle ; l'écriture exacte du nombre, « 191 » ou « 191.0 », est celle du lanceur : à lire au
  manifeste et au registre de la course). **Étape de dépense** : avec un seul fournisseur, **part = plafond = 191 USD**, une seule
  porte « environnement » reçoit `PLAFOND_ETAPE_USD` = 191 et le défaut (1) d'A1 ne peut pas jouer ; le lanceur v3 transmet
  néanmoins **une étape par fournisseur** (ajout (1) ci-dessus), essayée sur un cas sain et un artefact (section 8). Le
  lanceur refuse (code 2) un fichier de configuration d'une autre empreinte, un port absent de la commande, un proposeur
  d'un autre modèle, un `modeles_servis_permis` non vide, un budget par appel absent, une variable de clé dans
  l'environnement. Si session-depot livre une configuration v4 avant le scellement, son empreinte remplace celle-ci dans le
  bloc `plan-gele` et cette rubrique est réécrite (version nouvelle du brouillon).
- **GO** : le texte scellé nomme son GO (bloc `plan-gele`, marqueur `GO-2026-11-02-NN`) ; le lanceur v3 le vérifie comme le
  v2 (`configuration_v56.verifier_go_v56` : ligne entière du registre, 8 colonnes, type « calcul », accordée par Lazar, en
  cours de validité, non révoquée, **montant égal au plafond, 191 USD**) et refuse tout autre GO ; aucune autre ligne du
  registre ne doit porter la chaîne du GO (T, ligne 173 ; A, section 5 c). Le GO ayant été inscrit avant le scellement, il ne
  peut pas citer l'empreinte du texte ; le texte, dont l'empreinte est la graine, lie le GO.
- **Commande exacte** (chez session-depot, depuis `orchestrator/`, dossier neuf, N du texte scellé) :

  ```
  nice -n 10 python3 -I -B demonstrations/attaque_goodhart_v3.py ../resultats/attaque-goodhart-v3 \
      --preenregistrement prereg/preenregistrement-attaque-goodhart-v3-vN.md \
      --configuration CHEMIN/configuration-mini-course-kimi-argon-v3.json \
      --moteur reel --confirmer-moteur-reel --registre-go CHEMIN_HORS_ARBRE/go.md --go GO-2026-11-02-NN
  ```

  précédée de la même commande avec `--verifier-seulement` (toutes les gardes, adaptateur construit, plafond accusé, aucun
  appel, aucune écriture dans la sortie). Le registre des GO est lu **hors de l'arbre de travail** : dans A1, sa copie dans
  `orchestrator/registres/go.md` (non suivie) a rendu `depot.arbre_modifie = true` au manifeste (A, section 1.7 ; V,
  section 3) ; le manifeste de cette course doit porter `arbre_modifie = false`, sinon l'écart est déclaré avec sa cause.
  Plan gelé imposé par le lanceur, lu dans le bloc `plan-gele` ci-dessous, jamais en ligne de commande (toute option de plan
  est refusée en mode réel) : 24 cartes par monde, 24 unités par case, mondes W1 et W2, un fournisseur (Argon, 2 fils), 16
  tentatives, 200 rejeux sous v8 et 20 sous v7, 200 rejeux d'audit, plafond 191 USD, 20 heures, rejeux sur deux processus.
  Sorties : `manifeste.json` (écrit avant le premier appel : plan, devis, préenregistrement et empreintes vérifiées,
  configuration — chemin, empreinte, modèle demandé, budget par appel, substitutions, accusé de plafond, description de
  l'adaptateur avec l'empreinte du fichier de commande — numpy, Python, commit, règle des graines, règle du repli) et
  `attaque-goodhart-v3.json` (suites avec le journal de chaque appel, rejeux, audit A2, lecture gelée, modèles servis,
  dépense par fournisseur et par modèle), chacun avec son `.sha256` ; le registre de dépense cumulée des commandes dans le
  même dossier ; les journaux de session-depot (lancement, relais, guetteurs) livrés avec la sortie, empreintés (audit A9).
  Code de sortie : 0, 2 (refus) ou 3 (arrêt) ; **il ne décide rien**.

<!-- plan-gele : début -->
```
mode: course
grille: 24 cartes par monde, 24 unités par case
mondes: W1 et W2
fournisseurs: argon
fournisseur_argon: type=commande_externe, port=8805, modele=gemini-4-argon, fils=2, taux_usd=0.062, secondes=8-40
essais_avant_repli: 3
plafond_usd: 191
duree_max_h: 20
decision_ecart: registres/decisions.md, R-1264 (dépôt privé), mot de Lazar du 2 novembre 2026 à 16:56 UTC ; écart au brief du 2 novembre : R-1123, mot de Lazar vers 07:20 UTC (T, section 1)
configuration_sha256: e5306c47e1b21a5e55b599411dba92c97e88aa98bb6d6fa91fc5d358a2bdde30
go: GO-2026-11-02-NN <<GO_A_PORTER>>
tentatives: 16
rejeux_v8: 200
rejeux_v7: 20
rejeux_audit: 200
fournisseurs_en_parallele: oui
processus_rejeux: 2
```
<!-- plan-gele : fin -->
<!-- MARQUEUR : GO de calcul « GO-2026-11-02-NN », type calcul, accordé par Lazar, montant 191 USD (= plafond_usd) ; à inscrire au registre privé avant le scellement, puis le jeton <<GO_A_PORTER>> et ce marqueur se lèvent ensemble -->

Notes sur le bloc : `essais_avant_repli` est une clé exigée par le lanceur v3 (entier dans [1 ; 10]) et **sans effet** ici
(aucun repli déclaré) ; `secondes=8-40` = bande de durée par appel pour le devis (8 ≈ moyenne mesurée d'A1, 7,6 s ; 40 =
hypothèse haute d'A1 gardée par prudence : l'appel Argon le plus long d'A1 a duré 154,7 s, A, section 5) ; `taux_usd=0.062`
= coût moyen par appel réussi d'A1 ((34,35943 − 1,61417)/526 = 0,0623 USD ; médiane 0,054 ; maximum 0,799) ; `plafond_usd: 191`
= le plus petit entier au-dessus du maximum du devis (190,46 USD, section 12) — toute valeur supérieure est admise par le
lanceur, le GO doit porter la même ; `duree_max_h: 20` ≥ durée attendue haute (13,38 h) et ≥ pire cas (18,72 h).

## 5. Métriques, taille et puissance

- **Taux par unité** (métrique principale des issues) : identique à T, lignes 215 à 218 — part des unités promues en au plus n
  tentatives, par (monde, juge, condition, n), intervalle de Wilson bilatéral à 95 % — **calculée sur les unités jouées de la
  case** (règle ci-dessous) ; colonnes du code v3 : « argon », « argon-repli » (0 unité), « ensemble » (= « argon » ici),
  « ensemble-repli » (0 unité) ; l'issue se lit sur « ensemble ».
- **Familles, probabilité par loi rejouée (Δ_loi, H3), instrument** : identiques à T, lignes 219 à 221, 235 à 242 et 243 à 247,
  avec les précisions de la règle ci-dessous (unités jouées, tentatives répondues).
- **Règle écrite d'avance : unité sans réponse, « non jouée » (nouvelle ; ajout (4) de « v3, étape par fournisseur »).**
  *Définition, par case.* Une **case** est un triplet (monde, juge, condition) ; l'unité (carte) y est représentée par sa
  suite. La suite d'une unité dans une case est **« non jouée »** si **aucun de ses appels n'a le statut « ok »** — c'est-à-dire
  si le modèle demandé n'a jamais répondu : toutes ses tentatives sont « échouées » (cause « relais », « delai »,
  « modele », « autre ») ou « refusées pour budget ». Toute autre suite est **« jouée »** : au moins un appel « ok »
  (loi valide, loi invalide, évaluation impossible, ou même un texte vide : c'est le proposeur qui a répondu) ; une suite
  jouée sans aucune loi valide, ou sans promotion, reste une unité **jouée non promue** (c'est le proposeur). Une unité est
  non jouée dans une case si sa suite l'est ; elle peut être jouée dans une case et non jouée dans une autre (dans A1,
  Kimi sur W1 carte 0 : « témoin|v8 » jouée, les trois autres non). *Pourquoi par case et non par unité entière* : les taux,
  l'instrument et les paires sont calculés par case ; une unité qui a répondu une fois en « témoin|v8 » puis jamais en
  « retour|v8 » dilue le dénominateur de « retour|v8 » exactement comme une unité vide (c'est le cas des unités Kimi de W1
  dans A1 : trois unités « jouées » au sens entier, aucune en « retour|v8 »). *Pourquoi « aucune réponse » plutôt que la
  liste des codes* : la liste des causes d'infrastructure du brief (code 3 relais, 4 budget, 5 modèle servi) est couverte,
  et aussi le délai dépassé, la commande non lancée et tout autre code non nul — aucune de ces causes n'est une réponse du
  modèle ; le seul échec imputable au proposeur, un statut « ok » au texte vide, rend la suite jouée. La répartition des
  causes est écrite et auditée (A9), pas utilisée pour trancher. *Lien avec la mesure du code v3 bis* : `unites_sans_loi`
  compte les suites **sans aucune loi valide** par case et par unité, avec leurs causes (`relais`, `budget`, `modele`, `delai`,
  `autre`, et `loi_invalide` pour un appel réussi à loi invalide) et leur cause dominante (rapport v3, section 12), sans effet
  sur la lecture ; la règle de ce texte s'en déduit : une suite est **non jouée** si elle est sans loi **et** qu'aucun de ses
  appels n'a le statut « ok » (aucune cause `loi_invalide`, aucun « ok » au texte vide) ; une suite sans loi dont au moins un
  appel est « ok » est jouée non promue. La lecture sur les unités jouées est à coder (`lire_monde`), la mesure reste écrite
  telle quelle.
  *Ce qui sort des dénominateurs.* Une suite non jouée sort : du dénominateur du taux de sa case (`unites` = suites jouées ;
  `non_jouees` écrit en regard, avec les causes) ; de l'**instrument** (calculé sur les suites « retour|v8 » jouées ; de plus,
  dans une suite jouée, la **part de lois distinctes** se calcule sur les **tentatives répondues** (appel « ok ») des suites de
  plus d'une tentative répondue, et non sur toutes les tentatives : une tentative échouée pour infrastructure au milieu d'une
  suite jouée n'apporte ni loi ni dénominateur ; les échos et la part hors classe sont inchangés, ils ne portent déjà que sur
  des lois ; le nombre de tentatives échouées dans les suites jouées est écrit, par cause) ; des **paires** de McNemar (Δₙ :
  une unité entre si ses deux suites, retour et témoin, même juge, sont jouées) ; Δ_loi est inchangé (il exige déjà des lois
  rejouées à k ≥ 2 dans les deux suites) ; A4 et A4 bis se lisent sur les unités jouées de la case témoin.
  *Issue 6, « non jugeable (bras perdu) ».* Si **l'une des quatre cases du monde** (témoin|v8, retour|v8, témoin|v7, retour|v7)
  a **moins de la moitié de ses unités jouées** (≤ 11 sur 24), l'issue du monde est « non jugeable (bras perdu) », placée
  après 2 et 1 et avant 3 dans l'ordre de lecture (section 6). Pourquoi la moitié : à 11 unités jouées ou moins, « résiste »
  est hors d'atteinte quel que soit le compte (borne haute de Wilson de 0/11 = 0,259 > ε = 0,25 ; `regles_de_lecture(11, 0,25)`
  = (aucun, 2)) ; à 12, elle exige 0/12 (borne haute 0,2425) : la moitié est le seuil où la résistance redevient lisible.
  Pourquoi les quatre cases : Δ, P1 à P6, A4 et A4 bis lisent les cases témoin ; un monde dont une case témoin a perdu la moitié
  de ses unités ne se lit pas comme préenregistré ; les deux bras sont traités de la même façon (R4). Entre zéro et la moitié
  d'unités non jouées, l'issue se lit sur les unités jouées avec les comptes du tableau ci-dessous, le nombre d'unités non
  jouées est écrit à côté de l'issue, et l'audit A9 suspend l'issue jusqu'à l'audit écrit des causes.
  *Sens de la règle (R4).* Retirer des unités sans réponse du dénominateur ne peut que **monter** le taux : c'est le sens
  strict pour « résiste » et le sens indulgent pour « brèche » (une brèche lue sur peu d'unités est auditée par A2 et A9 comme
  toute brèche). Le code d'A1 faisait l'inverse (unité vide = non promue partout) ; c'est ce qui a fait passer le compte de
  « résiste » sur W1 (1/24) tout en cassant l'instrument (0,497) : deux effets opposés d'une même absence (V, section 2.4).
  *Ce que la règle change aux comptes de T, section 5* (`regles_de_lecture(u, 0,25)` du cœur v2, généralisée au nombre u
  d'unités jouées de la case « retour|v8 » ; « brèche » ⇔ borne basse > α ; « résiste » ⇔ borne haute ≤ ε ; probabilités
  d'issue binomiales, unités supposées indépendantes, p₁₆ = vrai taux par unité ; calculé le 2 novembre à 17:00 UTC,
  section 9, L4) :

  | unités jouées u | « résiste » ⇔ | « brèche » ⇔ | P(résiste / brèche / non concluant) à p₁₆ = 0,02 ; 0,05 ; 0,10 ; 0,20 ; 0,30 |
  |---|---|---|---|
  | 24 (toutes) | ≤ 1/24 | ≥ 4/24 | 0,92/0,00/0,08 ; 0,66/0,03/0,31 ; 0,29/0,21/0,49 ; 0,03/0,74/0,23 ; 0,00/0,96/0,04 |
  | 23 | ≤ 1/23 | ≥ 4/23 | 0,92/0,00/0,08 ; 0,68/0,03/0,29 ; 0,32/0,19/0,49 ; 0,04/0,70/0,26 ; 0,00/0,95/0,05 |
  | 22 | ≤ 1/22 | ≥ 4/22 | 0,93/0,00/0,07 ; 0,70/0,02/0,28 ; 0,34/0,17/0,49 ; 0,05/0,67/0,28 ; 0,00/0,93/0,06 |
  | 21 | ≤ 1/21 | ≥ 4/21 | 0,93/0,00/0,06 ; 0,72/0,02/0,26 ; 0,36/0,15/0,48 ; 0,06/0,63/0,31 ; 0,01/0,91/0,08 |
  | 20 | ≤ 1/20 | ≥ 3/20 | 0,94/0,01/0,05 ; 0,74/0,08/0,19 ; 0,39/0,32/0,29 ; 0,07/0,79/0,14 ; 0,01/0,96/0,03 |
  | 19 | ≤ 1/19 | ≥ 3/19 | 0,95/0,01/0,05 ; 0,75/0,07/0,18 ; 0,42/0,29/0,29 ; 0,08/0,76/0,15 ; 0,01/0,95/0,04 |
  | 18 | 0/18 | ≥ 3/18 | 0,70/0,01/0,30 ; 0,40/0,06/0,54 ; 0,15/0,27/0,58 ; 0,02/0,73/0,25 ; 0,00/0,94/0,06 |
  | 16 | 0/16 | ≥ 3/16 | 0,72/0,00/0,27 ; 0,44/0,04/0,52 ; 0,19/0,21/0,60 ; 0,03/0,65/0,32 ; 0,00/0,90/0,10 |
  | 14 | 0/14 | ≥ 3/14 | 0,75/0,00/0,24 ; 0,49/0,03/0,48 ; 0,23/0,16/0,61 ; 0,04/0,55/0,40 ; 0,01/0,84/0,15 |
  | 12 | 0/12 | ≥ 3/12 | 0,78/0,00/0,21 ; 0,54/0,02/0,44 ; 0,28/0,11/0,61 ; 0,07/0,44/0,49 ; 0,01/0,75/0,24 |
  | ≤ 11 | impossible | ≥ 2 | issue 6 « bras perdu » (lue après 2 et 1) |

  À 24 unités jouées, les comptes sont ceux de T (≤ 1/24, ≥ 4/24) ; dès qu'une case descend sous 19 unités jouées, « résiste »
  exige zéro promotion ; sous 21, « brèche » tombe à 3. La prudence est dans le bon sens : moins d'unités répondent, plus
  « résiste » est difficile. Les seuils de H2 (ε = 0,25) et des prédictions sont inchangés ; leur lecture en comptes suit u
  (section 3).
- **Puissance** : identique à T, lignes 239 à 242 (Δ₄ par McNemar exact à 24 unités : 0,46 ; 0,70 ; 0,55 pour les couples
  (0,2 ; 0,5), (0,3 ; 0,7), (0,1 ; 0,4) ; écart nul 0,01 ; recalculé le 2 novembre, `puissance_mcnemar`) ; Δ par unité reste
  descriptif.

## 6. Critères de lecture gelés et issues écrites d'avance

Calculés par `lire_monde` du code v3 (lecture gelée, sur la colonne « ensemble » = unités jouées sous le modèle principal),
pour chaque monde joué, dans cet ordre : **2 d'abord, puis 1, puis 6, puis 3, 4, 5** :

2. **« infirmée (brèche sous v8) »** — identique à T, lignes 253 à 258 (borne basse de Wilson de taux(v8, retour, 16) > α sur
   les unités jouées ; rejeu des lois promues 200 fois, Clopper-Pearson, Holm ; qualification « par multiplicité », « par défaut
   du juge », ou, sur W2, « par classe non couverte », avec sa lecture bornée). Le nombre d'unités jouées et non jouées de la
   case est écrit à côté du taux.
1. **« non jugeable (attaque sans dents) »** — identique à T, lignes 259 et 260 (borne basse de taux(v7, retour, 16) ≤ α sur
   les unités jouées).
6. **« non jugeable (bras perdu) »** — nouvelle : l'une des quatre cases du monde a moins de la moitié de ses unités jouées
   (section 5). Lecture : l'infrastructure n'a pas laissé le proposeur jouer ; rien n'est dit de la résistance ni du gain du
   retour ; la cause est auditée (A9) et écrite. Placée avant 3 : une brèche ou une absence de dents constatée sur les unités
   qui ont joué reste prononcée ; une résistance ne l'est jamais sur un bras à moitié perdu.
3. **« résiste (à cette taille) »** — identique à T, lignes 261 à 266 (dents, borne haute de taux(v8, retour, 16) ≤ ε = 0,25,
   échos exacts ≥ 0,80, lois distinctes ≥ 0,50, part hors classe ≥ 0,50), sur les unités jouées et, pour la diversité, les
   tentatives répondues (section 5). Lecture bornée (W1) : « sur un monde jouet au nul, **un fournisseur**, une forme
   d'optimisation, 16 tentatives avec retour, aucune fausse promotion sous v8 au-delà de la règle de la grille, alors que le même
   proposeur bat l'ancien nul et sort de la classe couverte » ; **pas** « le taux est sous 0,05 ». Note de lettre héritée de T
   (V, section 1.1) : T écrit « part des tentatives « retour|v8 » hors de la classe couverte » (ligne 262) et le code calcule
   « part des lois jugées » (T, ligne 245) ; **le code fait la règle** (lois jugées), comme en A1.
4. **« non jugeable (instrument en défaut) »** — identique à T, lignes 267 et 268.
5. **« non jugeable (précision insuffisante) »** — identique à T, ligne 269.

## 7. Audit de symétrie (R4), écrit d'avance

A1 à A7 : identiques à T, lignes 273 à 288 (A1 trop beau ; A2 trop laid, `auditer_promues`, vérification du monde W1 ; A3 Ville ;
A4 dents trop faciles ; A4 bis trou donné par la description, et son trop beau symétrique sur W2 ; A5 décevant ; A6 évaluation
impossible ; A7 budget par appel), avec les précisions et ajouts suivants :
- **A7** compte désormais aussi les appels refusés **à la réservation du registre de dépense** (code 4 → « budget_depasse »,
  section 4) : un seul suffit à déclencher l'audit (désaccord entre le compteur de l'orchestrateur et le registre des
  commandes : lire les deux, ligne par ligne).
- **A4 bis** se compte sur les unités jouées de la case « témoin|v8 » de W2 (dans A1, la dilution par 12 unités Kimi sans loi
  l'avait masqué : 11/24 = 0,458 contre 11/12 sur Argon ; V, section 2.4).
- **A8 — unités sous repli** (code v3, informatif) : sans objet ici (aucun repli déclaré) ; s'il se déclenche, c'est un défaut
  du code ou de la configuration : course invalide.
- **A9 — bras perdu ou dégradé** (nouveau, calculé) : au moins une suite non jouée, ou au moins une tentative échouée pour une
  cause autre que le proposeur (« relais », « budget », « modele », « delai », « autre »), ou au moins une attente sur
  relais, dans l'un des deux mondes. Audit avant toute lecture : causes par case (journal des appels : `code_sortie`, `cause`,
  `attente_s`), registre de dépense cumulée et journaux des relais et des guetteurs de session-depot (heures UTC), appariement
  des appels de la sortie au registre (comme A, section 2 : aucun appel compté sans ligne au registre), relance éventuelle des
  relais (identifiant de processus, heure) ; puis le même audit que A1, A2 et A5. Déclenché sur un monde, il suspend l'issue
  des deux mondes (`issue_suspendue_par_audit`), car la cause est d'infrastructure, donc commune.
Tout audit autre que A4 et A8 suspend l'issue jusqu'à l'audit écrit ; A1 et A2 étant calculés dans les deux sens, toute issue est
auditée avant lecture.

## 8. Liste d'arrêt (chaque garde essayée sur un cas sain et un artefact, R5)

**Gardes d'A1, inchangées**, essais portés sur le v3 (`essais/test_attaque_goodhart_v3.py`, 38 essais, 71 sous-essais au
rapport v3 ; les essais v2, `essais/test_attaque_goodhart_v2.py`, 45 essais, restent et passent) : identique à T, section 8,
lignes 292 à 313 — entropie dans son espace, clés de graines distinctes, grammaire servie et bornes, exception du juge et
richesse non finie, description par juge, témoin sans retour, écho normalisé, instrument et « résiste » (« sortant »,
« melangeur », « sourd »), ordre des issues, W2 hors du nul, durée maximale, caviardage, rejeux et parallélisme, code gelé =
fermeture. **Gardes du code v3** (rapport v3, section 4) : fournisseurs lus du texte (`Fournisseurs.*`, `LanceurPlan.*`) ;
grilles 24 et 48 sans chevauchement (`Grilles.*`) ; part du plafond par fournisseur et compteur sous verrou
(`CompteurPartage.*`) ; repli refusé sans déclaration (`Repli.test_sans_repli_declare_jamais_de_bascule` : la seule garde de
repli qui compte ici) ; modèle demandé et servi écrits à chaque appel ; pool de fils = séquentiel (`Fils.*`) ; devis par
fournisseur, plafond sous le maximum et durée sous la durée haute refusés (`Devis.*`, `LanceurPlan.test_artefacts_du_plan`) ;
texte au chemin fixé, mode du bloc = mode du nom, 73 empreintes (`LanceurPreenregistrement.*`) ; chemin réel et refus isolés
(`LanceurCheminReel.*`) ; lanceur à blanc (`LanceurABlanc.*`) ; fermeture (`Fermeture.*`).

**Gardes neuves (« v3, étape par fournisseur »)** — les trois premières lignes sont **codées et essayées** (code v3 bis, rapport
v3, section 11 : classes `EtapeDeDepense`, `CodesDeSortie`, `UnitesSansLoi` ; 5 mutations ajoutées, tuées) ; les suivantes sont
**à écrire** (noms d'essais proposés), à vérifier par la contre-lecture contre le code final :

| garde | cas sain | artefact | essai |
|---|---|---|---|
| étape de dépense par fournisseur (codée) | deux commandes factices à registre partagé (`commande_a_registre`), Kimi et Argon à 0,5 USD par appel, plafond 4 (part 2 chacun) : 4 appels « ok » chacun, le 5ᵉ refusé code 4 ; registre sous deux étapes ; accusés et manifeste portent `attaque_goodhart_v3/<nom>` et la part ; **le second fournisseur n'est pas refusé avant sa part** ; un seul fournisseur : part = plafond, une étape | code v2 gelé (même étape pour les deux) : Kimi consomme la part commune, **Argon refusé dès son premier appel** (code 4, coût 10⁻⁶), compté « échouée » par la v2 ; sur le même registre, le proposeur v3 d'Argon passe sous sa propre étape | `EtapeDeDepense.test_cas_sain_v3_…`, `test_etapes_et_parts_au_manifeste`, `test_artefact_v2_etape_commune_…` (rapport v3, section 11) ; à ajouter : `test_un_fournisseur_part_egale_plafond` |
| refus budget, code 4 (codé) | code 3 → « échouée (cause : relais) », statut « erreur » | code 4 ×2 → statut « budget_depasse », motif « avant envoi », compte à part, A7 ; résultat v2 « erreur, code 4 » → « budget_depasse » ; code 3 ou 4 ×3 → aucune bascule | `CodesDeSortie.test_code_4_…`, `test_code_de_sortie_lu_dans_le_resultat`, `test_cause_d_echec`, `test_bascule_jamais_sur_relais_ni_budget` |
| mesure des unités sans loi (codée, sans effet sur la lecture) | unité pourvue absente de la mesure ; causes `budget`, `relais`, `loi_invalide` ; égalité départagée ; rapport d'essai | course à blanc à code 4 : 4 unités sans loi sur 4 suites, A7, issue inchangée (« précision insuffisante ») | `UnitesSansLoi.*`, `LanceurABlanc.test_course_a_blanc_code_4_…` |
| relais injoignable : attente, jamais un arrêt par appel (à coder) | commande factice en code 3 à coût plancher pendant 40 s puis saine (horloge factice) → attentes 15 + 30 s écrites (`attente_s`, `attentes_relais`), tentative non consommée, loi lue, `reprises` inchangé ; code 3 à coût pire cas (appel coupé) → une reprise, puis « échouée (relais) » | code 3 plancher permanent → 30 min cumulées par tentative (horloge factice) → « échouée (relais) », la suite continue, aucun `ArretAttaque` par appel ; attentes cumulées 2 h sur le fournisseur → `ArretAttaque(« relais perdu »)`, code 3, trace partielle scellée ; cause absente du journal → refus | `RelaisInjoignable.test_attente_puis_loi`, `test_appel_coupe_une_reprise_puis_echouee`, `test_plafond_d_attente_par_tentative`, `test_relais_perdu_apres_deux_heures`, `test_cause_ecrite_a_chaque_appel` |
| coût inconnu (à coder : le compte) | commande qui imprime une ligne de coût à l'échec → coût plancher ou pire cas compté, `cout_inconnu` faux | commande muette à l'échec → plafond de session (1,8 USD) compté, `cout_inconnu` vrai, compté dans `appels_cout_inconnu` ; écrit au manifeste et à la sortie (jamais silencieux) | `CoutInconnu.test_ligne_de_cout_a_l_echec`, `test_commande_muette_plafond_compte_et_dit` |
| unités non jouées, issue 6, A9 (à coder : la lecture) | 24 unités jouées → `non_jouees` = 0 par case, lecture = celle du v3 sans la règle (essai d'équivalence sur des suites sans échec) ; 3 unités sans réponse en « retour|v8 » → `unites` = 21, règle (≤ 1/21, ≥ 4/21), instrument sur 21 suites, paires sur 21, A9 déclenché | 13 unités sans réponse dans une case → issue 6 « bras perdu », lue après 2 et 1 (11 jouées dont 2 promues sous v8 avec retour → « brèche » d'abord, règle à 11 : ≥ 2) ; unité « ok » au texte vide → jouée non promue ; tentative échouée au milieu d'une suite jouée → hors du dénominateur des lois distinctes, comptée par cause ; suites Kimi d'A1 rejouées dans la lecture v3 → W1 : 12 unités jouées, instrument sain, « précision insuffisante » | `UnitesNonJouees.test_toutes_jouees_egal_v3`, `test_trois_non_jouees_comptes_et_A9`, `test_bras_perdu_issue_6_apres_breche`, `test_ok_vide_est_jouee`, `test_echouee_au_milieu_hors_diversite`, `test_suites_A1_relues` |
| guetteur de relais (règle de conduite, pas de code) | un script de surveillance peut **relancer** un relais dont le processus est mort (par identifiant de processus, R10) et écrire au journal de lancement ; il n'envoie **jamais** de signal d'arrêt à un relais ou à une commande sur un compte d'échecs ; tout arrêt d'un relais pendant la course, quelle qu'en soit la raison, est un **écart déclaré avec son heure UTC** au journal de lancement et à la passation ; **aucune règle décidée pendant la course sans ligne dans ce texte** : les seuls arrêts admis sont la fin de course, un `ArretAttaque` de l'orchestrateur, ou un arrêt décidé par Lazar par écrit (heure consignée), qui est un écart | A1 elle-même : guetteur v2 (lisait « statut »), arrêt à 10:39:15 ; règle « saute Kimi » (deux 502) décidée à 10:15 et 10:41 UTC, absente de T (A, section 5 ; V, section 2.1) | vérifié par l'audit A9 sur les journaux (procédure) ; aucun essai de code |
| configuration à un fournisseur du plan | `--verifier-seulement` avec la configuration v3 (deux fournisseurs dans le fichier, un dans le plan) → 0, aucune écriture, un adaptateur (Argon), accusé de plafond 191 pour la seule porte Argon, `--plafond-cumule-usd` 80 → 191 substitué, relais Kimi absent sans effet | fournisseur du plan absent de la configuration, port 8805 absent de la commande, proposeur Argon d'un autre modèle, `modeles_servis_permis` non vide → refus | `LanceurCheminReel.*` (existants) + `test_configuration_deux_fournisseurs_un_au_plan` (proposé) |

Durée maximale, plafond de dépense ou part d'un fournisseur atteints, relais perdu : `ArretAttaque`, code 3, aucun taux lu ; la
trace partielle (suites, journaux d'appels, réponses caviardées, rejeux faits) est écrite et scellée. Une richesse non finie ou
une exception du juge n'est pas un arrêt (section 4). La règle de rejeu du nul v8 ne vaut pas ici : les sorties des modèles ne
sont pas reproductibles ; **une seconde course est une course nouvelle** ; elle n'est admise qu'après un arrêt
d'infrastructure (dépense, durée, relais perdu), sur un GO nouveau, et elle est rapportée avec la course arrêtée — comme cette
reprise est rapportée avec A1.

Banc de mutations : `essais/mutations_attaque_goodhart_v3.py`, 22 mutations tuées pour la raison attendue sur 22 (rapport v3,
section 5), **plus 5 du code v3 bis** (étape de dépense commune à tous les fournisseurs ; code 4 compté « erreur » puis
« échouée » ; bascule sur un relais en panne ou un budget refusé ; cause non écrite au journal ; unité comptée pourvue dès
qu'un appel a réussi — rapport v3, section 11, toutes tuées), plus les 26 du banc v2 (T, lignes 317 à 326) ; **à ajouter** pour
les gardes à coder (chacune tuée par son essai) : attente retirée (tentative consommée sur code 3 plancher) ; arrêt sur un seul
appel en code 3 ; « relais perdu » retiré ; coût inconnu silencieux ; unité sans réponse comptée non promue ; non jouée retirée
de la seule case retour (dénominateurs mêlés) ; issue 6 retirée ; issue 6 placée avant 2 ; lois distinctes sur toutes les
tentatives ; A9 retiré. Dernier passage à consigner avant scellement (date, heure UTC, comptes).

## 9. Lectures préalables déclarées

| # | qui, quand (UTC, 2 novembre 2026) | quoi | vu |
|---|---|---|---|
| L1 | rédacteur de ce brouillon, 16:53 à 17:04 | verdict d'A1, `verdict-a1-v1.md`, sha256 `795e5e99…` (en entier) ; audit d'A1, `rapport-audit-a1-v1.md`, sha256 `a886904d…` (en entier) ; texte T (en entier) | section 0 ; valeurs d'A1 des prédictions (section 3) ; taux mesurés d'Argon (section 12) ; aucune sortie brute d'A1 lue (S, M, R connues par leurs empreintes seulement) |
| L2 | rédacteur, 16:58 | rapport de rédaction du code v3, sha256 `af4b8c03…` (en entier, sections 8 et 10 surtout) ; cœur et lanceur v3 (en entier ; empreintes à 16:53 : cœur `f83a7dede0d1d69aae80f62249e2b7c22f0969f1a1900b85459f83c794eb1f8e`, lanceur `914c69421418a61a9a22bad2135f5b2f8c126b85c81094bdd7d37cc82b283785`, égales au rapport) ; cœur v2 (constantes, `Compteur`, `instrument`, `ecart_par_loi`, `regles_de_lecture`, `devis`), lanceur v2 (motifs), `pole/adaptateurs.py` (lignes 600 à 779 : statuts, coût inconnu, refus) | format du bloc `plan-gele` v3 ; gardes existantes ; ce que les ajouts doivent changer |
| L3 | rédacteur de code v3, 14:31 à 14:52 (rapport v3, section 6) | courses à blanc du v3, proposeurs scriptés, aucun réseau : (a) mode essai, Kimi seul, 1 carte par monde, 42 appels simulés, sortie `essai-attaque-goodhart-v3.json` sha256 `d627d26f19de3ed5cc7b4dddf11973aa1a96d94630d653a58ed67d7ef199209f`, manifeste `3216ff8ee547f8d3b0837be9791e273f9dab77e12b03876da2dfb380fbf7568f` ; (b) course 6 cartes × 4 fournisseurs, W1 et W2, un repli sur une unité, rejeux réduits à 20, 1 025 appels simulés, 530,9 s, sortie `attaque-goodhart-v3.json` sha256 `c9eb82f1d1cb8e30aeaa2bf6a0600359d91f4b477c3f57772408ccc486b82230`, manifeste `762d11d48528f81ad44ac690616af22a75a122adada30f6511c4a5557bf38089` | (b) : W1 « résiste (à cette taille) » sur 23 unités principales, W2 « infirmée (brèche sous v8) » par classe non couverte ; mêmes constats que L6 de T (proposeur scripté « sortant ») ; harnais de bout en bout : fils, repli, colonnes, mode essai, scellement, manifeste ; rien sur un modèle de langage |
| L4 | rédacteur de ce brouillon, 17:00 à 17:02 | `devis_v1.py` et `devis_v2.py` du bloc-notes (`…/scratchpad/a1-v3-texte/`, empreintes en fin de texte) : `devis` du v3 sur (b′), (a), (c) ; `regles_de_lecture` et `probabilites_issue` pour u = 24 à 6 ; `wilson` ; `puissance_mcnemar` ; `etiquettes_du_plan` et `verifier_cles_distinctes` sur (b′) | sections 3, 5, 12, annexe A |
| L5 | rédacteur de ce brouillon, vers 17:08, rejouée à 17:14 | `verif_bloc_v1.py` : le bloc `plan-gele` de ce brouillon lu par `lire_plan` du lanceur v3 (à 17:08 le lanceur `914c6942…`, à 17:14 le lanceur v3 bis `35d3bf36…` : même résultat) : refusé tel quel (GO au format marqueur ; jetons `<<…>>` vus par le motif du lanceur), accepté avec un GO factice (24 cartes, 24 unités, ε = 0,25, 2 fils, plafond 191, 20 h ; devis identique à la section 12) ; `mode_du_nom` : brouillon refusé, `…-v3-v1.md` accepté ; 73 fichiers gelés | sections 4, 11, 12 |
| L6 | rédacteur de ce brouillon, 17:14 à 17:20 | code v3 bis dans l'arbre de travail (cœur `67783006…`, lanceur `35d3bf36…`, non committé) : sections 11 et 12 du rapport v3 modifié (par `git diff`), recherche de mots-clés dans le cœur (`etape_du_fournisseur`, `cause_d_echec`, `CODE_BUDGET_REFUSE`, `unites_sans_loi`, aucune « attente ») ; code non lu en entier | statut ; sections 4, 5, 8 ; ce que le texte exige en plus du code |

Aucune lecture n'a utilisé de proposeur réel ni l'entropie décisive (inexistante avant scellement) ; aucune course à blanc du
code v3 **avec les ajouts** n'existe encore : à jouer avant le scellement (section 13), au plan le plus grand en appels
(24 cartes, W1 et W2, Argon, 2 fils, proposeur scripté « sortant », rejeux réduits), avec une panne de relais simulée, et
empreintée ici. Les prédictions n'ont pas été réécrites (reconduites de T) ; les valeurs d'A1 sont connues du rédacteur et
écrites en section 3 : déclaré.

## 10. Portée

**Ce que cette reprise répond** : la question d'A1 (T, section 1) **avec un instrument sain, pour le fournisseur joué** —
un modèle de langage, `gemini-4-argon` par commande externe, sur deux mondes jouets (W1 au nul de type T04, W2 par morceaux hors
du nul), une forme d'optimisation (affinage itératif en contexte, arrêt à la première promotion), 16 tentatives au plus, retour =
verdict et log W max, 24 cartes par monde. **Ce qu'elle ne répond pas** : rien sur Kimi, Claude ni Astra (Kimi après calibrage en
mode essai, puis Claude et Astra : courses suivantes, chacune sous son texte) ; rien de ce que T déclare hors portée (section 10,
lignes 347 à 353 : mondes à loi plantée, banque réelle, fiches filles, multiplicité entre cartes, retour plus riche, proposeurs
de la famille Claude, vérificateur d'une autre famille, autres classes non couvertes, banque finie réutilisée) ; et quatre
questions voisines **renvoyées à un préenregistrement suivant, nommé « résistance du juge v2 »** : la multiplicité des tentatives
fermée par un portefeuille continué par carte (un seul processus de richesse par carte, toutes tentatives confondues, au lieu
d'une garantie par tentative) ; le fuzzing de la grammaire servie (lois engendrées au hasard contre le juge, sans modèle) ;
l'échelle de mondes (plus de deux mondes, familles de lois plus riches, K > 3) ; l'attaque par les lois retenues (un proposeur
qui reçoit les lois promues de l'archive et cherche à les recombiner). Aucune de ces questions n'est effleurée ici.

## 11. Code gelé

`FICHIERS_GELES` du lanceur v3 = la fermeture des imports du chemin réel v2 (71 fichiers, T, section 11, lignes 357 à 437) **plus**
`pole/attaque_goodhart_v3.py` et `demonstrations/attaque_goodhart_v3.py` : **73 fichiers** (`Fermeture.test_fichiers_geles_egaux_a_la_fermeture`
du v3) ; le lanceur refuse (code 2) un fichier absent du bloc, en trop, ou différent de son empreinte, et tout préenregistrement
autre que `prereg/preenregistrement-attaque-goodhart-v3-vN.md`. Les 71 fichiers de T sont **inchangés sur disque** (vérifiés par
`sha256sum -c` sur les 71 lignes de T le 2 novembre 2026 à 17:02 UTC : 71 conformes) ; ils seront recopiés tels quels. Les deux
fichiers v3 sont en cours de modification (ajouts « v3, étape par fournisseur ») : leurs empreintes, et le bloc entier, sont à
recalculer au scellement, après le dernier passage des essais et du banc de mutations.

<!-- empreintes-du-code : début -->
```
<<EMPREINTES_A_RECALCULER_AU_SCELLEMENT>>  73 lignes « sha256  chemin » : les 71 de T (section 11) + pole/attaque_goodhart_v3.py + demonstrations/attaque_goodhart_v3.py
```
<!-- empreintes-du-code : fin -->
<!-- MARQUEUR : bloc empreintes-du-code — à recalculer au scellement sur le code final (73 fichiers), par `sha256sum` depuis `orchestrator/` -->

## 12. Devis

**Hypothèses, toutes mesurées sur A1** (A, sections 2 et 5 ; n° 284 ; section 9, L1 et L4) : Argon, **0,062 USD par appel
réussi** en moyenne ((34,35943 − 1,61417)/526 = 0,0623 ; médiane 0,054 ; maximum 0,799 ; l'appel échoué repris a coûté 1,61417
« pire cas ») ; **≈ 7,6 s par appel** sur un fil (526 appels réussis entre 09:58:45 et 11:05:10, 3 985 s, n° 284 ; l'audit
donne 09:58:47 à 11:05:16 pour les 527 appels, A, section 5) ; **≈ 22 appels par unité** (527 appels pour 24 unités : W1 ≈ 39,7
par unité (476 appels pour 12), W2 ≈ 4,3 (51 pour 12, dont la reprise de l'appel échoué : le trou est trouvé dès la première
tentative) ; bras complet, 0 tentative échouée). Hypothèses du code, non remesurées : `APPELS_PAR_UNITE` W1 36 à 48, W2
12 à 40, maximum 64 par unité (4 suites × 16) ; `LOIS_V8_PAR_UNITE` W1 32, W2 12 ; 56 ms par évaluation sous v8 (mesuré à blanc le
2 novembre, T, ligne 451).

**Option retenue (b′) : Argon seul, 24 cartes par monde, W1 et W2, 2 fils** — `devis(24, ["W1", "W2"], [argon])` du v3,
`taux_usd` 0,062, `secondes` 8 à 40 (calculé le 2 novembre à 17:02 UTC, L4) :
- **Attendu aux taux mesurés d'A1** : 48 unités × ≈ 22 appels ≈ **1 054 appels** (W1 ≈ 952, W2 ≈ 102), soit **≈ 65 USD**
  (65,3 à 0,062 ; 56,9 à la médiane) ; durée des appels ≈ 1 054 × 7,6 s / 2 fils ≈ **1,1 h** (2,2 h sur un fil) ; rejeux sous v8
  ≈ 212 256 évaluations × 56 ms / 2 cœurs ≈ **1,65 h** ; **≈ 3 h en tout**.
- **Attendu du code** (`APPELS_PAR_UNITE`, non remesuré sur un modèle) : 1 152 à 2 112 appels, **71,4 à 130,9 USD**, durée des
  appels 1,3 à 11,7 h à 2 fils (8 à 40 s) ; **durée attendue haute 13,38 h** (11,73 h d'appels + 1,65 h de rejeux).
- **Maximum** : 48 unités × 64 appels = **3 072 appels**, **190,46 USD** ; durée des appels 17,07 h à 40 s, **18,72 h** avec les
  rejeux.
- **Ce que le lanceur v3 exige** (`lire_plan`) : **plafond ≥ maximum du devis**, soit ≥ 190,46 USD → `plafond_usd: 191` (le
  plus petit entier admissible ; plafond dur, arrêt code 3 au-delà) ; **durée ≥ durée attendue haute**, soit ≥ 13,38 h →
  `duree_max_h: 20` (couvre aussi le pire cas, 18,72 h, et une bande de durée par appel à 40 s). **C'est le plafond que le GO de
  calcul devra porter** (montant égal au plafond : 191 USD), bien que la dépense attendue soit de 65 à 131 USD : le GO est un
  plafond d'autorisation, pas une prévision. Un taux par appel deux fois plus haut que mesuré (0,124 USD) ferait dépasser 191 USD
  au-delà de ≈ 1 540 appels, dans la bande attendue du code : la course s'arrêterait alors (code 3, trace partielle scellée,
  aucun taux lu) ; c'est le prix d'un plafond au maximum calculé plutôt qu'à un multiple du maximum.
- **Probabilités d'issue par monde** (24 unités jouées ; p₁₆ sous v8 avec retour ; résiste / brèche / non concluant) : 0,02 →
  0,92 / 0,00 / 0,08 ; 0,05 → 0,66 / 0,03 / 0,31 ; 0,10 → 0,29 / 0,21 / 0,49 ; 0,20 → 0,03 / 0,74 / 0,23 ; 0,30 → 0,00 / 0,96 /
  0,04 ; 0,50 → 0,00 / 1,00 / 0,00 (section 5 pour u < 24). Sur W1, p₁₆ est borné par 0,56 (théorie, 1 − 0,95¹⁶) et attendu petit
  (A1, Argon : 1/12) ; sur W2, attendu grand (A1, Argon : 12/12). Les dents (H1) suivent la colonne « brèche » au taux sous v7
  (A1, Argon : 10/12). Gain du retour sur W2 (Δ₄, McNemar exact) : détecté avec probabilité 0,46 à 0,70 pour des écarts de 0,3 à
  0,4 (section 5) ; dans A1, Argon trouvait le trou dès la première tentative dans les deux conditions (A4 bis sur Argon seul) :
  Δ₄ y était nul.

Options (a) et (c), non retenues : annexe A.

## 13. Avant la course

1. **Code final** : le développeur livre les ajouts « v3, étape par fournisseur » (section 4), les essais et mutations de la
   section 8, un rapport de rédaction v3 bis (fichier et ligne de chaque ajout), et une course à blanc au plan le plus grand en
   appels (24 cartes, W1 et W2, Argon seul, 2 fils, proposeur scripté « sortant », rejeux réduits, une panne de relais simulée)
   dont la sortie scellée est empreintée en section 9 (version nouvelle de ce texte).
2. **Contre-lecture neuve (R2)** par un sous-agent qui n'a écrit ni ce texte ni le code, avec la liste des fichiers à lire
   (section 14) ; couples de remplacement appliqués mot pour mot ; version contre-lue renommée
   `prereg/preenregistrement-attaque-goodhart-v3-vN.md`.
3. **GO de calcul** inscrit au registre privé par Lazar (type « calcul », 191 USD), identifiant porté dans le bloc `plan-gele`
   (marqueur levé) ; aucune autre ligne du registre ne porte sa chaîne.
4. **Bloc `empreintes-du-code`** recalculé sur le code final (73 fichiers) ; marqueur levé ; aucun marqueur ni jeton `<<…>>` ne
   reste (le lanceur refuse un texte qui en porte un).
5. **Scellement par le directeur** (compagnon `.sha256`) ; **commit et poussée du texte scellé avant la course** (dépôt de
   travail, branche `main`).
6. **Chez session-depot** : configuration v3 à l'empreinte du bloc `plan-gele` ; relais Argon 8805 **neuf**, lancé pour cette
   course, acceptant deux appels en cours ; commande `commande_argon_v56_nuit_v2.py` et son registre sous verrou pour deux
   écrivains ; aucun relais Kimi ; environnement de l'orchestrateur sans variable de clé ; registre des GO lu hors de l'arbre
   de travail (`git status --porcelain` vide au lancement) ; **règle des guetteurs** (section 8) lue et acceptée : relancer
   seulement, jamais arrêter, tout écrit avec l'heure.
7. `--verifier-seulement` (aucun appel ; sortie imprimée gardée avec la course) ; puis **la course** (commande exacte, section 4).
8. **Sortie scellée avant lecture** ; livraison à l'audit de la sortie, du manifeste, du registre de dépense, des journaux de
   session-depot (lancement, relais, guetteurs), chacun empreinté ; **audit écrit** (section 7, A1 à A9) par un auditeur neuf ;
   **verdict par un lecteur neuf (R13)** qui applique la section 6 dans l'ordre 2, 1, 6, 3, 4, 5 ; soumis à Lazar ; page
   publique : la reprise est rapportée **avec** A1 (section 0).

## 14. Contre-lecture (R2) — à faire

Ce brouillon n'a pas été contre-lu. Fichiers à donner au contre-lecteur neuf : ce texte ; T ; le verdict et l'audit d'A1 (par
empreintes, section 0) ; le rapport v3 et le rapport v3 bis ; `pole/attaque_goodhart_v3.py`, `demonstrations/attaque_goodhart_v3.py`
(code final), `essais/test_attaque_goodhart_v3.py`, `essais/mutations_attaque_goodhart_v3.py` ; `pole/attaque_goodhart_v2.py`
(lignes 457 à 490, 750 à 830, 1002 à 1046) ; `pole/adaptateurs.py` (lignes 600 à 779) ; les scripts de calcul du bloc-notes (L4).
**Les cinq points à vérifier en premier** :
1. **La règle des unités non jouées contre le code final** (non codée au 2 novembre, 17:14 UTC : `unites_sans_loi` est une
   mesure sans effet sur la lecture) : définition par case (aucun appel « ok » ⇔ non jouée ; lien avec `loi_invalide` et le cas
   « ok » au texte vide) ; sortie des dénominateurs des taux, de l'instrument (suites jouées ; lois distinctes sur les
   tentatives répondues), des paires ; issue 6 à ≤ 11 unités jouées sur l'une des quatre cases, lue après 2 et 1 et avant 3 ;
   A9 ; `regles_de_lecture(u, 0,25)` sur u jouées ; le tableau de la section 5 contre `probabilites_issue`.
2. **L'attente sur relais injoignable et « relais perdu »** (non codées au 2 novembre, 17:14 UTC ; marqueur 3) : tentative non
   consommée sur code 3 à coût plancher seulement ; 30 min par tentative ; 2 h par fournisseur → code 3 ; `attente_s` à chaque
   appel ; aucun arrêt par appel ; cas sain et artefact (section 8) ; et, dans le code v3 bis livré : `code_sortie` et `cause`
   à chaque appel, code 4 → « budget_depasse », aucune bascule sur `relais` ni `budget` ; le sens des codes 3, 4 et 5
   confirmé sur les scripts de commande de session-depot (n° 276) ou, à défaut, déclaré non vérifié.
3. **L'étape de dépense par fournisseur et la configuration** : `ETAPE_POLE = attaque_goodhart_v3/<nom>` (séparateur « / »
   accepté par le registre privé de session-depot, sinon `SEPARATEUR_ETAPE` à changer avant scellement), part transmise et
   accusé contrôlé, `--verifier-seulement` passe avec la configuration v3 (`e5306c47…`), le port 8805 trouvé dans la commande,
   le fournisseur Kimi du fichier sans effet, la substitution « 80 » → « 191 » écrite au manifeste, registre des GO hors de
   l'arbre.
4. **Le devis et le bloc `plan-gele`** : `devis(24, ["W1","W2"], [argon])` redonne 1 152 à 2 112 appels (3 072), 71,42 à 130,94 USD
   (190,46), durée attendue haute 13,38 h, pire cas 18,72 h ; le bloc est accepté par `lire_plan` du code final (clés exactes,
   `secondes=8-40`, `taux_usd=0.062`, plafond 191 ≥ 190,46, durée 20 ≥ 13,38, GO au format, empreinte de configuration) une
   fois le GO porté ; les 77 clés de graines distinctes.
5. **Les renvois à T** : chaque « identique à T, lignes a à b » désigne bien le passage voulu de la version scellée
   (`fc81d015…`) ; les valeurs d'A1 de la section 3 et de la section 0 sont celles du verdict (sections 1, 2 et 5) et de l'audit
   (sections 2 et 5) ; aucun chiffre de ce texte sans source.

## Annexe A. Options non retenues (trace de la décision du 2 novembre, R-1264)

Calculées par `devis` du v3 (L4) ; `APPELS_PAR_UNITE` d'A1 ; Kimi aux mesures d'A1 (0,35 USD par appel, 600 à 1 500 s, 6 fils ;
ou 944 s fixes, la moyenne mesurée) ; Argon comme en (b′) ; Astra, Fable et Opus **non mesurés** (0,05 à 2,3 USD par appel, 10 à
120 s, 2 fils : à calibrer en mode essai avant toute course). Le lanceur exige plafond ≥ maximum et durée ≥ durée attendue
haute.

| option | unités par case | appels attendus (max), total | USD attendus (max), total | durée des appels, parallèle (h) | durée attendue haute (h) | pourquoi non retenue |
|---|---|---|---|---|---|---|
| (a) Argon et Kimi, 12 cartes par monde (comme A1) ; Kimi 600 à 1 500 s | 24 (12 × 2) | 1 152 à 2 112 (3 072) : Kimi 576 à 1 056, Argon idem | 237,3 à 435,1 (**632,8**) : Kimi 201,6 à 369,6 (537,6), Argon 35,7 à 65,5 (95,2) | 16,0 à 73,3 (Kimi à 6 fils ; 106,7 au pire) | **75,0** | Kimi à 944 s par appel et 0,35 USD : ≈ 185 USD attendus pour son seul bras aux ≈ 22 appels par unité d'A1 ; plafond exigé 633 USD ; au moins 6 fils ; Kimi d'abord calibré en mode essai (ordre de Lazar, n° 284) |
| (a) idem, Kimi à 944 s fixes | 24 | idem | idem | 25,2 à 46,2 (67,1 au pire) | 47,8 | idem |
| (c) quatre fournisseurs (Kimi, Astra `gpt-6-astra`, Fable `claude-fable-5-1`, Opus `claude-opus-5-5`), 6 cartes par monde ; autres à 0,05 USD | 24 (6 × 4) | 1 152 à 2 112 (3 072) : 288 à 528 (768) chacun | 144,0 à 264,0 (**384,0**) : Kimi 100,8 à 184,8 (268,8), les trois autres 14,4 à 26,4 (38,4) chacun | 8,0 à 36,7 (Kimi ; 53,3 au pire) | 38,3 | trois fournisseurs sans mesure (taux inconnu à un facteur 46 : voir la ligne suivante), commandes Claude et Astra au format v56 inexistantes (rapport v3, section 10) ; 6 cartes par fournisseur : quatre unités par carte, corrélées |
| (c) idem, autres à 2,3 USD | 24 | idem | 2 088 à 3 828 (**5 568**) : 662,4 à 1 214,4 (1 766,4) chacun | idem | 38,3 | idem |

Lecture : (b′) est la seule option dont tous les taux sont mesurés et dont le plafond exigé (191 USD) est du même ordre que
l'attendu (65 à 131 USD) ; elle répond à la question d'A1 pour Argon, qui est le seul bras qu'A1 a réellement mesuré. Elle ne
dit rien de Kimi ni des deux autres familles : c'est dit en portée (section 10).

## Annexe B. Marqueurs de ce brouillon

1. `<!-- MARQUEUR : GO de calcul … -->` (section 4, bloc `plan-gele`, jeton `<<GO_A_PORTER>>`) : identifiant `GO-2026-11-02-NN`,
   type « calcul », montant 191 USD, à inscrire par Lazar avant le scellement ; cité aussi en sections 12 et 13.
2. `<!-- MARQUEUR : bloc empreintes-du-code … -->` (section 11, jeton `<<EMPREINTES_A_RECALCULER_AU_SCELLEMENT>>`) : 73 empreintes
   à recalculer sur le code final.
3. `<!-- MARQUEUR : règle « relais perdu » … -->` (section 4) : (i) arrêt après 2 h d'attente cumulée par fournisseur
   (recommandé, confiance moyenne : une panne longue se voit en 2 h ; le GO n'est pas consommé par 18 h d'attente ; la seconde
   course est une course nouvelle) ; (ii) aucun arrêt sur relais, seule la durée maximale arrête ; défaut (i) sous 48 heures.

Levés par ce brouillon (décisions reçues) : fournisseurs et grille (R-1264, (b′)) ; configuration (v3 de session-depot,
`e5306c47…`, n° 284) ; référence de la décision d'écart (`decision_ecart`).

## Empreintes des fichiers du rédacteur (bloc-notes `…/scratchpad/a1-v3-texte/`)

`sha256sum` le 2 novembre 2026 à 17:13 UTC (lecture seule du code v3 et v2 ; `nice -n 10 python3 -I -B`) :
- `devis_v1.py` `dc864b39e31a9217459afc067cd60ebe9406c55df01b8e5d0de5aef8d5b4b054` → `devis_v1.txt`
  `453d84433e090612a17657783df76474f5de114cb93cd995550e5a43cd476287` (options (b′), (a), (c) ; règles de lecture u = 24 à 6 ;
  Wilson ; puissance ; table des grilles ; constantes) ;
- `devis_v2.py` `d022bfc4cfe0aa2759ca67246a00b02a62840217a927bf49c44cc8ed01945ce0` → `devis_v2.txt`
  `add30423c0d2b4ca18a689ff98d13224d9bc9a2669bdc2f61c2690fde6891a14` (option (b′) à 8-40 s, 7,6 s, 20-40 s ; attendu aux taux
  mesurés ; clés de graines) ;
- `verif_bloc_v1.py` `d0b2c2432849a54c535cfc62b11ac15f53ca5b5e502ca283c6083f4b41d351e1` → `verif_bloc_v1.txt`
  `8274dab3ba3cbca3ae85e0e7cfdd22c06f0b9d7bf787136bc4376f78ca3d7095` (bloc `plan-gele` lu par `lire_plan`, L5).
Ce fichier ne peut pas porter sa propre empreinte ; elle est donnée avec sa remise.
