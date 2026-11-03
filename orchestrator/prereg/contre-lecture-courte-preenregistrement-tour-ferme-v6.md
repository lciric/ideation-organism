scellable après couples — un bloquant (B11 : le code 4 « rien envoyé » doit être réservé aux refus que la session porte en elle-même ; sinon une limite d'un relais ou d'une commande rend une issue fausse au lieu d'un arrêt), levé par les couples T113 à T128 (texte seul) et par le constat de la session-depot sur ses commandes v3 ; code v64 conforme à ce qu'il dit, rejoué (107 essais, 91 mutations sur 91, garde 6 réelle « conforme ») ; brouillon 6 = brouillon 5 + T101 à T112 + V01 à V69 + bloc, à l'octet ; deux importants (I33, I34), dix mineurs (45 à 54) ; borne du vérificateur : ne pas relever

# Contre-lecture R2 courte — préenregistrement du tour fermé (étage 1), brouillon 6, et code `_v64` au commit `63ed933`

3 novembre 2026, de 00:57 à 01:45 UTC environ (heures de `date -u`). Contre-lecteur neuf (R2) : je n'ai écrit ni le code du tour
fermé (`_v60` à `_v64`), ni l'étage des tests de mort, ni aucun préenregistrement, rapport ou contre-lecture du tour fermé.
Consigne lue en entier (`/home/claude/controle-ia-travail/brouillons/reprise-conv-audit-2026-11-02-nuit/prompts-sous-agents/contre-lecture-courte-tour-ferme-v64-brouillon6-prompt.md`).
Lecture seule du dépôt ; aucun commit, aucun `.sha256`, aucun fichier existant modifié, rien sous `donnees/`, aucun `git fetch`,
`checkout` ni `stash`, aucun appel de réseau ni de modèle ; Python par `nice -n 10 python3 -I -B`, pytest avec `-p no:cacheprovider`,
`TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1`. Le dossier `../resultats/banc-tricheurs-v9-validation-v1/` (course décisive en cours
dans ce clone) n'a été ni ouvert ni listé ; `git status` n'a été joué que restreint à `orchestrator/`. Deux fichiers neufs : ce texte
et `prereg/couples-contre-lecture-tour-ferme-v6.json`. Mes scripts et sorties : `/home/claude/scratch/tour-ferme-v64/contre-lecture/`
(`outils/`, `sorties/`, `course-rien-envoye-tour1/`). Pendant la contre-lecture, une autre tâche a écrit deux fichiers neufs non suivis
sous `prereg/` (contre-lecture de l'attaque de Goodhart v3, brouillon 4) : non ouverts, hors du bloc gelé.

**Verdict en trois lignes.**

1. **Scellable après les couples T113 à T128** (texte seul : aucun code, aucun essai, ni le plan ni le bloc d'empreintes ne changent ;
   garde 6 du lanceur v64 rejouée sur le texte obtenu, cases remplies d'essai : « conforme ») et après les trois cases ; **un
   bloquant, B11**, levé par ces couples et par le constat de la session-depot sur ses commandes v3 — prix à accepter par écrit : une
   limite propre d'un relais ou d'une commande devient un arrêt (code 3, reprise pour panne d'infrastructure), jamais une issue.
2. Le code v64 fait ce que le texte dit, et seulement cela : seul un code 4 dont la dernière ligne porte le booléen `"envoye": false`
   devient « rien envoyé » ; les arrêts du noyau (plafond de 50 USD, parts de 44 et 6 USD et pire cas avant l'étage au compteur,
   part épuisée à l'adaptateur de l'étage) sont intacts ; le barème est exigé après la garde des rôles et avant toute porte et tout appel ; 72 h est la seule durée acceptée en
   mode décisif ; les seuils de la section 12 sont exacts. Rejoué : 107 essais réussis, 1 sauté par construction, 66 sous-essais ;
   banc 91 sur 91 pour la raison attendue ; brouillon 6 reconstruit à l'octet ; zones identiques ; trois marqueurs ; 92 empreintes
   égales au disque, à `63ed933` et à la fermeture.
3. Ce qui reste est dans les commandes v3, invisible à blanc et à `--verifier-seulement` : une limite d'un relais lue « rien envoyé »
   rend « ne tient pas (T2, T3, T4) » et A4 « promeut autant » au lieu d'un arrêt (B11 ; course à blanc L2b-cl6) ; une ligne de
   code 4 qui porte `"modele_servi": null` est lue « refus » → arrêt (I33 ; sonde sur vraies commandes locales) ; une réponse coupée
   par sa borne de sortie sort en code non nul → arrêt, même au vérificateur (I34). Borne du vérificateur : ne pas la relever.

## 0. Fichiers lus, empreintes, ce qui a été rejoué

| pièce | vérification |
|---|---|
| `prereg/rapport-redaction-tour-ferme-v6.md` | `c2d6765a5993f66ffc0e7ef67691c54edc9ff7a1dc4d62f51265c409de22e749` ; lu en entier, dix points d'abord |
| `prereg/preenregistrement-tour-ferme-v1-brouillon6.md` | `cdcb44706e7b3c62ccd028680cf633c1651a56a93d7de129449150b47b45aef5`, 889 lignes : égal au rapport, au commit `63ed933` et à la copie `brouillon6-candidat.md` du rédacteur ; passages changés relus à leur place, sections 0, 6, 7, 12, 13, 14 et annexe A lues |
| `prereg/preenregistrement-tour-ferme-v1-brouillon5.md` ; `prereg/couples-contre-lecture-tour-ferme-v5.json` ; `prereg/contre-lecture-courte-preenregistrement-tour-ferme-v5.md` | `c81aa6ef…`, `40bb0d17…`, `3b525f9e…` : égales au rapport ; la contre-lecture précédente lue en entier |
| couples du rédacteur, `/home/claude/scratch/tour-ferme-v64/brouillon6/couples-v64-brouillon6.json` | `4c1b03cbec8fe65c891aad5074abd3cc87926af69c6db88aad2bea88f0668d42`, 69 couples lus un à un |
| session-depot, n° 294 (§ 3 et § 4, TF-01 à TF-06) et n° 295 (§ 3) ; configuration v3, brouillon 1 | lus ; configuration `109f673c289d91d52dd86094b97085f66149dfd8416a61f2d6d1290eb68dc6bb` |
| code v64 : `pole/adaptateur_commande_v64.py`, `pole/tour_ferme_v64.py`, `demonstrations/tour_ferme_v64.py`, `demonstrations/lire_tour_ferme_v64.py` | `adb73287…`, `35a8294e…`, `98c1a1a2…`, `393b17cc…` : égales au rapport et à `63ed933` ; le module de commande lu en entier, les trois autres par leur diff à la v63 (lu en entier), puis `roles_reels`, `principal`, `lire_plan`, `jouer_etage`, `jouer_etage_1`, `Compteur`, `AdaptateurEtageV64` à leur place |
| essais et banc v64 | `5227916…`, `d6e6535e…`, `5066ada2…` : égales au rapport ; lus pour `CommandeCode4`, `EtageRienEnvoye`, `CourseRienEnvoye`, `ProposeurRienEnvoye`, `CommandesV64`, `BaremeDesCommandes`, `VerificationPrealable`, `PrixPasseALEtage`, `Fermeture`, `FermetureEnCourse`, la mécanique du banc (recompilation en mémoire, aucun fichier écrit) |
| code partagé appelé | `pole/adaptateurs.py` l. 554-778 (commande externe : l. 751-765 pour un code non nul, `controle_modele` l. 680-700), `pole/adaptateurs_v56.py` l. 40-225, `pole/tests_de_mort_v5.py` l. 232-243, 341-479, 600-700, `pole/etage_entre_generations_v57.py` (`jouer_etage_v57`), `demonstrations/ideation_v8.py` (`adaptateurs_reels_v56`), `demonstrations/attaque_goodhart_v2.py` l. 203-252, `pole/lecture_tour_ferme_v63.py` l. 100-260 |
| commande de Kimi v1 (dépôt de travail, `docs/notes/ideation-organisme-v1/relais-kimi-v1/commande_kimi_v1.py`, `3a98845e…`) | lue pour la forme de ses sorties (la v2 et la v3 ne sont pas lisibles d'ici) : code 4 = pire cas au-dessus du plafond, sans `modele_servi` ; tout refus 4xx du relais en code 3 ; réponse tronquée en code 5 ; réservation d'entrée à un jeton par octet du corps, plus 1 024 |

Rejoué ou vérifié (sorties dans mon dossier de travail) :

- **Essais** (commande de la consigne), 01:11:41 → 01:13:20 UTC : **107 réussis, 1 sauté (`BacReelV64`, « ESSAI RÉEL NON JOUÉ »), 66
  sous-essais réussis, 98,44 s, code 0** ; aucun dossier `essai-v64-*`, `tour-ferme-v64-*` ni `bac-tour-ferme-v64-*` resté sous `/tmp` ;
  `git status -- orchestrator` propre avant et après.
- **Banc de mutations, une fois** (`essais/mutations_tour_ferme_v64.py --raisons`), 01:14:57 → 01:23:52 UTC : **91 mutations (24 + 19 +
  29 + 19), 91 tuées pour la raison attendue**, autre raison 0, défaut du banc 0, survivantes 0, non appliquées 0 ; témoin 101 essais,
  0 en échec avant et après ; 534 s ; code 0 ; empreintes des sept fichiers v64 relevées au lancement, égales au rapport.
- **Brouillon 6 rejoué** (`outils/rejouer_b6.py`) : brouillon 5 + T101 à T112 (chaque « ancien » une fois) = `2ded3ee9…`, 873 lignes,
  égal à la copie du rédacteur ; + V01 à V69 (occurrences exigées, toutes à 1, hors des zones, aucune balise touchée ; V37 et V48
  ajoutent les marqueurs `<<COMMANDES_V3>>` et `<<PRECISION_GO_23>>`) ; + bloc recalculé sur le disque dans l'ordre de `FICHIERS_GELES`
  = **`cdcb4470…`, identique à l'octet au brouillon 6**.
- **Garde 6 réelle sur le texte du brouillon 6** (`outils/garde6_b6.py` : vrai `lire_preenregistrement` du lanceur v64, copie nommée
  comme un texte scellé dans mon dossier, sceau simulé en mémoire, aucun `.sha256` écrit) : tel quel, refus « marqueur(s) non
  rempli(s) hors de l'étage 2 : ['<<CASE_CONFIGURATION_V3>>', '<<COMMANDES_V3>>', '<<PRECISION_GO_23>>'] » ; cases remplies d'essai :
  **conforme**, 92 empreintes vérifiées, plan 3 générations, 6 et 12 cartes, m = 19, 50 = 44 + 6 USD, **72 h**, D7 archive du bras
  réel, D9 mécanique, GO-2026-11-02-23, entropie de 254 bits ; plan à 24 h : refus « … le code v64 gèle 72 h (décision de Lazar,
  R-1294) … » ; une case laissée : refus qui la nomme.
- **Fermeture** (`outils/fermeture_cl.py`, règle à moi, plus large : tout chemin littéral en « .py » résolu) : 94 fichiers, les 92 du
  bloc plus `demonstrations/banc_tricheurs_v8.py` et `_v7.py`, que seule `pole/attaque_goodhart_v2.banc()` charge (mineur 48).
- **Sonde de la lecture du code 4** (`outils/sonde_code4.py`, vraies commandes locales, aucun réseau) : neuf formes de dernière ligne
  (section 1, I33).
- **Course à blanc L2b-cl6** (bac factice, conditions du plan, racine 20261102, barème d'essai 10 USD par million de jetons pour les
  deux relais, `--scenario-experimentateur rien_envoye:1`), 01:24:54 → 01:25:03 UTC, code 0 ; lue par
  `demonstrations/lire_tour_ferme_v64.py … --releve-sha256` : section 1, B11. Relevé `389fc91575bdcebad2e8dbe385fd4b76d731a2f50333888b07844efcdc0840af`,
  manifeste `3f74d5f18873271bf813757def3e6ea0db2669eaf16b615c0bdfd0e6c14be71c` (92 empreintes de code égales au bloc, durée gelée
  72 h, 259 200 s), lecture `1cdcdd23def75b1d31676f5e315c6ce4387703323248a6380a72b834ce52e4fd`.
- **Courses du rédacteur relues** (sans relancer) : L2b-v64-b6, relevé `13b0e20a…`, manifeste `4d3f4522…` (92 empreintes égales au
  bloc), lecture `3dd8517c…` ; seconde course, relevé `7cf91149…`, lecture `9333bbd3…` : chaque chiffre de la ligne L2b-v64-b6
  (section 10) retrouvé (90 sessions, 60 « rien envoyé », tailles des consignes, [36, 12, 12, 0, 0], [36, 0, 0], [24, 0], 30 testés).
- **Seuils de durée** refaits à la main sur la formule de la section 12 : (259 200 s − cartes × 3 × 120 s) / (cartes × 13 + 6) =
  592,6 s (31,7), 332,7 s (54,9), 298,5 s (60,7) ; à 3 tours, 247 788 / 132,8 = 1 865,9 s ; à 24 h, 179,4 ; 92,6 ; 81,2 ; 564,7 :
  **exacts**, rapport 3,68 à 60,7 testés (les exécutions se retranchent avant la division, d'où plus que 72 / 24).
- **Couples T113 à T128** (`outils/verifier_couples_v6.py`) : chacun une fois dans le brouillon 6 et à son application, hors des zones,
  sans marqueur ni balise ; zones identiques, marqueurs inchangés, plan et bloc inchangés ; texte obtenu 891 lignes ; garde 6 complète
  sur ce texte (cases d'essai) : conforme, 92 empreintes, 72 h, 50 = 44 + 6.

## 1. Constats (numérotation à la suite : B11 après B10 de la contre-lecture 3, I33 après I32, mineurs à partir de 45)

### Bloquant

**B11 — Le code 4 « rien envoyé » n'est pas réservé aux refus de la session : une limite du relais ou de la commande donne une issue
fausse, pas un arrêt.** La lecture v64 est juste et limitée à son cas (section 2, Q1) : `AdaptateurCommandeExterneV64.lancer`
(`pole/adaptateur_commande_v64.py:119-129`) ne change que le statut « erreur » d'un code 4 dont la dernière ligne porte le booléen
faux. Mais elle ne sait pas **pourquoi** la commande n'a rien envoyé, et la session-depot écrit (n° 294, § 3) que la commande d'Argon v2
sort aussi en code 4 « rien parti » les refus propres du relais : 402 (son plafond) et 429 (son nombre d'appels) ; rien ne dit qu'une v3
n'y mettra pas aussi son plafond cumulé (`--plafond-cumule-usd`, registre commun aux deux commandes, `demonstrations/tour_ferme_v64.py:292`)
ou un contrôle de `PLAFOND_ETAPE_USD`. Pour le vérificateur, c'est sans prix (témoin jamais décisif) ; pour un proposeur, c'est un
arrêt (A.5) ; **pour l'expérimentateur, chaque carte suivante finit ses tours au premier tour, sans exécution**. Joué (course à blanc
L2b-cl6, « rien envoyé » au premier tour de chaque carte, ce que rendrait une telle limite) : code 0, 51 cartes et témoins testés, tous
« non concluant », et la lecture gelée rend **« ne tient pas (T2, T3, T4) », n1 « critère », A4 « le bras aléatoire promeut autant que
le bras réel à cette taille », cause « sensibilité de la chaîne insuffisante »** ; T1 tient (aucun arrêt, aucun incident) ; seul S2 est
déclenché, et son audit (section 6) finit par « lecture des critères, sans les changer » ; S5 ne l'est pas (la part de « non concluant »
est la même dans tous les bras). Une panne d'infrastructure deviendrait ainsi une issue scientifique négative, et seulement négative
(asymétrie, R4) ; le texte le dit pour T4 (A.6 bis, V61), pas pour A4. Les arrêts du noyau, eux, ne sont pas masqués : plafond et
parts au `Compteur` (`pole/tour_ferme_v64.py:267-287`), part épuisée dans l'adaptateur de l'étage (`:779-783`) — mutation « part du relais
épuisée ignorée sur un « rien envoyé » » tuée.
Remède, texte seul (couples T114, T116, T117, T121, T126 ; T118 déclare la course L2b-cl6) : **le code 4 « rien envoyé » est réservé aux
refus que la session porte en elle-même** — son pire cas au-dessus de `PLAFOND_SESSION_USD`, ou, si la commande la contrôle, une
consigne au-delà de la fenêtre d'entrée du modèle — ; **tout refus qui tient à l'état du relais ou de la commande sort en un autre code
non nul** (par exemple 3 au plancher, rien parti, comme le font déjà les 400, 403, 411 et 413 du relais d'Argon, et la commande de
Kimi v1 pour tout refus 4xx du relais) : la v64, inchangée, le lit « erreur » → arrêt, code 3, relevé partiel scellé, reprise de la
section 7 (panne d'infrastructure). La session-depot l'écrit dans les v3 qu'elle rédige et le constate en A.6 bis (T128). Défense en
profondeur, recommandée (T115) : audit **S6** en section 6 — une carte dont `fin_des_tours` commence par « tour 1 : » et dit
« budget_depasse » ou « rien envoyé » n'a pas pu être coupée par sa borne (au premier tour le plafond passé est 0,80 USD, la consigne
et la sortie minimale en coûtent ≈ 0,08) : défaut, course invalide, aucune issue ; il attrape aussi une faute d'unité du prix du
barème (mineur 52) et une commande qui n'aurait pas suivi la règle. Écarté : lire une cause dans la dernière ligne (« cause » =
« plafond_session ») demanderait une v65 (code, essais, banc, contre-lecture) pour la même garantie, qui repose de toute façon sur le
code de la commande ; la cause reste utile au registre de la commande (T128), pour l'audit. **Prix, à accepter par écrit** : une limite
propre d'un relais ou d'une commande devient un arrêt sans issue (rare si A.6 bis est tenu : plafonds des relais au moins égaux aux
parts, nombre d'appels au moins 1 731 et 147, aucun autre usage des relais — le relais d'Argon 8805 sert aussi A1-v3, le compte de
Kimi aussi GO-11 et GO-25, n° 294, § 2 et § 3). Recommandation : couples T113 à T128 avec S6 (confiance 0,75 ; 0,6 pour l'utilité de S6).

### Importants

**I33 — Une ligne de code 4 « rien envoyé » au coût plancher qui porte aussi `modele_servi` nul ou vide est lue « refus » : arrêt.**
Sur un code non nul, la classe gelée appelle `controle_modele(objet, modele, seulement_si_dit=True)` dès que la ligne est conforme
(texte, coût fini > 0 : le plancher de 10⁻⁶ USD l'est), **avant** que la v64 ne voie le code (`pole/adaptateurs.py:751-760`, `:690`) ;
une clé `modele_servi` présente, nulle ou vide, fait un refus (R-764). Sonde sur vraies commandes locales (`sorties/sonde-code4/sonde-code4.json`) :
plancher sans `modele_servi` → « rien envoyé » ; plancher et `"modele_servi": null` → **« refus »**, l'adaptateur de l'étage le rend,
l'étage v5 lève `EtageInterrompu` (`pole/tests_de_mort_v5.py:383-407`) : arrêt ; `""` → refus ; `"stop_reason": "refusal"` → refus ;
`modele_servi` égal au modèle demandé → « rien envoyé » ; coût nul ou ligne sans texte avec `modele_servi` nul → « rien envoyé » (la
ligne n'est pas conforme, le contrôle du modèle ne joue pas) ; code 3 au plancher → erreur. Les essais v64 ne le voient pas : l'aide
`commande_locale` remplace un `modele_servi` nul par le modèle demandé (`essais/test_tour_ferme_v64.py:1521-1531`). La commande de
Kimi v1 n'écrit pas `modele_servi` sur son code 4 ; les v3 s'écrivent maintenant. Remède, texte seul (T117, T121, T128) : la dernière
ligne d'un code 4 ne porte ni `modele_servi` (sauf le modèle demandé exactement), ni `refus`, ni `stop_reason` ; constat A.6 bis.

**I34 — Une réponse coupée par sa borne de sortie, ou une consigne au-delà de la fenêtre du modèle, sort en code non nul : arrêt,
même au vérificateur.** La v64 n'assouplit que le code 4 ; tout autre code non nul reste « erreur » → arrêt (doctrine R5 et R-764,
à garder). Or la commande de Kimi v1 sort en code 5 sur `finish_reason` « length », et ses jetons de raisonnement comptent dans
`completion_tokens`, donc dans `max_tokens` = ce que le reste du plafond paie. Bornes de sortie de l'étage : expérimentateur, 16 000
jetons au plus, puis ce que le reste de la borne paie vers la fin d'une carte, jusqu'à la sortie minimale de 4 096 ; la longueur
réelle d'une réponse de Kimi expérimentateur, raisonnement compris, n'est pas mesurée (C7) ; vérificateur, ≈ 1 460 jetons que 0,1 USD paie après une consigne de
8 124 caractères au barème d'Argon, 1 000 au brouillon 1 de la configuration v3 (`--max-sortie-lecteur`), quand la configuration du
1er novembre bornait à 4 000 la sortie d'Argon hors proposeur. Une réponse coupée y arrêterait la course entière, après les
propositions payées — la famille de défaut que TF-02 voulait retirer. Côté entrée : l'étage permet une consigne d'expérimentateur
de ≈ 393 000 caractères (mesure du rapport v6) ; au prix d'entrée de Kimi v1 (2 USD par million), la vérification préalable la laisse
passer à 0,80 USD ; au-delà de la fenêtre du modèle, l'erreur de l'interface sortirait en code non nul (3 ou 5 chez Kimi v1) : arrêt. Remède, texte seul (T120,
T127, T128) : pour `experimentateur_test` et `lecteur_test`, une réponse coupée est rendue **en code 0** avec son texte, son coût et
`modele_servi` (l'étage lit alors « réponse sans demande », fin des tours, ou un témoin « non concluant ») ; la sortie minimale de
chaque rôle reste celle d'une réponse entière (l'exigence de T112, au brouillon 5, « aucune ne refuse … parfois quelques centimes
au dernier », écrite quand tout refus arrêtait la course, contredit l'option (c) et pousserait à l'abaisser : T127) ; la plus longue consigne tient dans la fenêtre du modèle, ou
la commande la refuse avant envoi en code 4. Les proposeurs restent arrêtés par une réponse coupée (A.5) : 0,50 USD paie ≈ 9 000 jetons
de sortie d'Argon (50 USD par million) ; le prix moyen d'un appel du 1er novembre (0,0237 USD) laisse une marge, à confirmer au constat.
Autres codes non nuls du vérificateur (quota de l'interface, prompt bloqué, délai) : arrêt, gardé (aucun repli silencieux).

### Mineurs

45. **Garde 16, « (402 d'un relais) »** (section 7) : l'artefact « « budget_depasse » non marqué sous le plafond passé (402 d'un relais)
    → arrêt » vaut pour un adaptateur qui rendrait lui-même « budget_depasse » (l'essai `EtageRienEnvoye` le fabrique), pas pour ce tour :
    par une commande, un 402 du relais arrive en code 4 « rien envoyé », lu sans arrêt (B11). Couple T117.
46. **Phrases périmées au scellement** : en-tête « non commités » (V03), section 10 bis « à faire » (V31), section 13 « à revérifier après
    commit » (V44), section 14, point (2) « à faire » (V46) ; les quatre fichiers v64 du bloc sont commités à `63ed933` et les 92
    empreintes y sont égales (0 écart sur 92 ; les 88 autres égales à `66dbcf1` et à `9776ed0`). Couples T113, T119, T123, T124. Titre
    et statut (l. 1 et 3) restent au directeur, au scellement.
47. **Compagnons `.sha256` absents** : la section 10 bis (T105) dit les empreintes de la contre-lecture courte du brouillon 5 et de ses
    couples « dans leurs compagnons `.sha256` » ; aucun n'existe sous `prereg/` (vérifié sur disque, R11) ; il en ira de même de ce texte
    et de ses couples (consigne : aucun `.sha256`). À écrire au scellement (R6) : T119 le dit.
48. **Règle de la fermeture statique** : `imports_de` (`essais/test_tour_ferme_v64.py:1362-1384`) ne suit un chemin littéral en « .py »
    que dans le dossier du fichier ; `pole/attaque_goodhart_v2.banc()` charge `demonstrations/banc_tricheurs_v8.py` (qui charge `_v7`)
    par un chemin d'un autre dossier ; aucune course du tour ne l'appelle (`FermetureEnCourse` ; seuls `reglages_de_configuration`,
    `substituer_commandes` et `charger_ideation_v8` servent) ; hérité de la v63, sans effet. Couple T122 (description exacte).
49. **Crédit du compte Kimi (TF-06)** : absent de la section 14 ; sans recharge, la première session de Kimi sort en erreur, arrêt
    sans issue. Couple T125.
50. **Empreintes des commandes v3 non gardées** : le lanceur ne compare pas les fichiers de commande à `<<COMMANDES_V3>>` ; il relève
    leur empreinte au manifeste (`configuration.adaptateurs.<relais>.empreintes`, `description()` de la commande externe). Couple T121 :
    comparaison par le lecteur neuf, écart = défaut de course.
51. **Trois caractères par jeton supposés pour Kimi** : la session-depot les donne pour Argon (n° 294, § 4) ; la commande de Kimi v1
    réserve un jeton par octet du corps (plus 1 024) : la vérification préalable v64 y est plus lâche que la commande, sans effet (le
    code 4 de la commande reste lu sans arrêt) ; seule une commande qui compterait moins d'un jeton par trois caractères ferait refuser
    à la v64 ce qu'elle accepterait. Constat A.6 bis (T128).
52. **Prix du barème sans borne haute** (`prix_caractere_commande` exige seulement un réel fini > 0) : une faute d'unité (prix par
    milliard) couperait chaque carte au premier tour, sans arrêt, comme en B11 ; le manifeste écrit le barème lu
    (`configuration.bareme_des_commandes`) ; S6 (T115) en fait un défaut ; une borne dans le code demanderait une v65.
53. **Cause d'un « rien envoyé » non tracée par le noyau** : le motif v64 (`pole/adaptateur_commande_v64.py:125-128`) remplace celui de la
    classe gelée et perd la sortie d'erreur et le champ `erreur` de la dernière ligne ; `appels_etage` ne garde que `rien_envoye`,
    `verification_prealable` et `budget_passe_usd`. La cause n'est lisible qu'au registre de la commande (T128 : l'y écrire). Pour mémoire.
54. **« La borne ne mord qu'au-delà de 0,067 USD par tour »** (section 12) : avec la réservation de la commande (entrée et 4 096 jetons
    de sortie, ≈ 0,08 USD au prix d'essai), le douzième tour est refusé dès que le reste tombe sous ≈ 0,08 USD, soit au-delà de ≈ 0,065
    USD par tour sur onze tours ; « à 0,06 USD, aucune carte n'est jugée sur une exécution tronquée » reste vrai. Pour mémoire, aucun
    couple.

## 2. Réponses aux six questions de la consigne

**Q1 — Code 4 « rien envoyé ».** *Juste et limitée* : `MOTIF_CODE` (`pole/adaptateur_commande_v64.py:55`) lit le code dans le motif de
la classe gelée, dont les deux branches « erreur » d'un code non nul commencent par « commande externe : code N : » (`pole/adaptateurs.py:751-762`) ;
un délai dépassé ou une commande non lancée n'ont pas ce motif ; la ligne est relue largement (`derniere_ligne_json`, même dernière
ligne non vide que la classe gelée) ; `envoye is False` exige le booléen. Neuf formes sondées (I33), dix essais et dix mutations
« F » : seul ce cas change. *Sans masquer un arrêt du noyau* : plafond de 50 USD et parts au `Compteur` (aucun coût compté pour un
« rien envoyé », donc rien n'y change), pire cas réservé avant chaque étage, part épuisée gardée dans l'adaptateur de l'étage
(`:779-783`), proposeur arrêté (`ProposeurRienEnvoye`). *Ce qui est masqué* : les limites que la commande ou son relais tiennent
eux-mêmes, si elles sortent en code 4 — B11. **Recommandation** : ne pas l'accepter tel quel ; exiger que les commandes v3 sortent ces
refus hors du code 4 (aucun code neuf) ; une cause sur la dernière ligne, oui pour le registre de la commande, non comme lecture du
code (v65 pour la même garantie) ; S6 en défense (confiance 0,75).

**Q2 — Barème.** Chemin vérifié : `fournisseurs.<kimi, argon>.prix_entree_usd_par_million_jetons` → `AC.bareme_depuis_configuration(conf, n)`
(`demonstrations/tour_ferme_v64.py:306`) → prix / 10⁶ / 3 → `AdaptateurEtageV64(prix_caractere_usd=…)` (réel fini > 0 ou `None`,
`TourRefuse` sinon) → `jouer_etage` (`pole/tour_ferme_v64.py:873-877`) → `jouer_etage_v57`, qui passe tous les réglages
(`pole/etage_entre_generations_v57.py:77`) → `executer_tests_de_mort(prix_caractere_usd=…)` → l. 468 de l'étage v5 (expérimentateur) ;
vérificateur : `pole/tour_ferme_v64.py:763`. Refus si absent, nul, négatif, non fini, booléen ou texte : `BaremeAbsent` → `TourRefuse`
→ code 2, dossiers temporaires retirés (`BaremeDesCommandes`, `CheminReelVerifierSeulement.test_artefact_bareme_absent`, mutation
« barème absent accepté » tuée). Ordre : variables de clé, plafond de la configuration, substitutions, construction des adaptateurs
v56 puis v64 (aucun appel), garde des rôles (`:304`), **barème** (`:306`), puis seulement relance des portes (`:311`), familles, sonde
du bac ; `--verifier-seulement` passe par le même chemin (barème exigé, portes non relancées). Le prix est lu dans la configuration
originale, les adaptateurs dans sa copie substituée : même clé, même valeur. Mineurs 51 et 52.

**Q3 — 72 heures.** `DUREE_ETAGE_1_H = 72.0` (`pole/tour_ferme_v64.py:158`), écrite au manifeste ; `lire_plan` refuse toute autre valeur
(`demonstrations/tour_ferme_v64.py:188-190` ; 24, 71,5, 72,5, 4 et 10⁹ h refusées par `DureeR1294` ; 24 h refusée sur le texte réel,
section 0) ; en mode décisif, toute option de plan, `--duree-max-h` comprise, est refusée (`:430`) ; défaut à blanc 72 h ;
`Compteur` à 259 200 s (manifestes de L2b-v64-b6 et de L2b-cl6). Seuils de la section 12 refaits à la main : exacts (section 0) ;
« ≈ 3,7 fois plus large » juste (3,68).

**Q4 — Brouillon 6.** Oui, et rien d'autre : rejoué à l'octet (section 0). Sept zones de l'étage 2 identiques à l'octet (14 661, 800,
570, 580, 455, 347 et 342 octets). Aucun couple V ne touche les sections 2, 3, 4.2, 4.4, 4.5, 4.7, 4.8, 5, 6 ni 11 ; en 4.3 (V12) et
4.6 (V13), seuls un nom de course et le nom du programme de lecture changent : **aucune prédiction, aucun critère, aucune issue
changés** — ce qui change, c'est ce qui peut alimenter T4 (B11). Bloc : 92 lignes, ordre de `FICHIERS_GELES`, égales au disque, à
`63ed933` (tête) et à la fermeture statique du code (`Fermeture`, rejoué) ; 88 égales au bloc du brouillon 5 et à `66dbcf1` ; 4 neuves ;
3 sorties (les `_v63` du cœur, du lanceur et du programme de lecture). Marqueurs hors des zones : exactement `<<CASE_CONFIGURATION_V3>>`
(plan gelé), `<<COMMANDES_V3>>` (section 13), `<<PRECISION_GO_23>>` (section 14), une fois chacun ; dans les zones : les huit du
brouillon 5.

**Q5 — Borne du vérificateur à 0,15 USD.** D'accord avec le rédacteur : **ne pas la relever** pour la taille des consignes (témoin
jamais décisif, « rien envoyé » sans arrêt en v64 ; arithmétique retrouvée : 42 000 caractères à 0,15 USD ; 7,8 cartes de plus à 44 et
6 USD, ≈ 20,7 à 42 et 8). La contrainte qui compte est ailleurs : la **sortie** du vérificateur, ≈ 1 460 jetons à 0,1 USD (≈ 2 460 à
0,15) ; elle n'est sans prix que si la commande rend une réponse coupée en code 0 (I34). Recommandation : garder 0,1 USD et exiger le
code 0 des réponses coupées (T128) ; ne relever (vers 0,25 USD, parts à refaire, v65) que si la session-depot ne peut pas l'écrire
(confiance 0,6).

**Q6 — Ce qui rendrait la course non concluante par défaut de conception.** Dans l'ordre du risque : B11 (issue fausse, la pire) ; I34
(arrêt sur réponse coupée ou consigne trop longue) ; I33 (arrêt sur la forme de la ligne de code 4) ; I32 restant (rôles et plafonds
des commandes, constat A.6 bis) ; mineur 52 (prix faux : comme B11, S6 l'attrape) ; mineur 49 (crédit Kimi : arrêt immédiat, sans
dépense). Aucun ne demande de code neuf ; tous se lèvent par le texte et le constat de la session-depot, sur les commandes v3 qu'elle
écrit maintenant. Option à la main de Lazar (dépense, GO à part) : un essai réel minimal des deux commandes v3 dans les rôles de l'étage
(une session de chaque, moins de 1 USD) lèverait I32 à I34 mieux que la lecture du code.

## 3. Les dix points du rédacteur, vérifiés

| point | vérifié | état |
|---|---|---|
| 1. lecture du code 4 | code, sonde de neuf formes, `CommandeCode4`, mutations F 1 à 6 rejouées | conforme ; forme de la ligne : I33 |
| 2. arrêts gardés | `:779-783` ; `EtageRienEnvoye` ; mutations « arrêt sur un rien envoyé », « part épuisée ignorée » | conforme |
| 3. limites propres des relais | course L2b-cl6 : issue fausse | B11 |
| 4. barème passé à l'étage | chemin jusqu'à la l. 468 et `:763` ; `PrixPasseALEtage` (espion) | conforme ; mineur 51 |
| 5. clé neuve | ordre des gardes, A.6 (V56) contre le code | conforme ; mineur 52 |
| 6. 72 heures | constante, `lire_plan`, options, défaut, seuils refaits | conforme |
| 7. brouillon 6 rejoué | à l'octet ; zones ; aucune prédiction, aucun critère | conforme |
| 8. bloc de 92 empreintes | disque, `63ed933`, fermeture, manifestes | conforme ; mineur 48 |
| 9. mesure du vérificateur | `pole/lecture_tour_ferme_v63.py` ne lit jamais le lecteur témoin (verdicts du noyau seuls, `pole/tour_ferme_v64.py:903-904`) : un témoin « non concluant » ne pèse sur aucun critère ni audit | conforme ; borne : Q5, I34 |
| 10. cases et chemin réel | trois marqueurs ; course dans le vrai bac et `--verifier-seulement` scellé à jouer chez la machine qui lance | à faire (section 4) |

## 4. Ce qui reste avant le scellement, dans l'ordre

1. **Décision du directeur sur B11** (prix écrit : une limite propre d'un relais ou d'une commande devient un arrêt) et sur S6 ; puis
   **couples T113 à T128** (section 5 et `prereg/couples-contre-lecture-tour-ferme-v6.json`), texte seul.
2. **Session-depot** : commandes v3 (TF-01, option (c), et les règles de B11, I33, I34), le **constat A.6 bis** complet (T128), la
   configuration v3 avec la clé du barème (prix exact de chaque commande) et son empreinte à `<<CASE_CONFIGURATION_V3>>`, les chemins
   et empreintes des commandes à `<<COMMANDES_V3>>`, le crédit du compte Kimi ; puis, chez la machine qui lance, une course à blanc v64
   dans le vrai bac (`bwrap`, identité dédiée, `TMPDIR=/tmp`, barème de la configuration) et un passage `--verifier-seulement` sur le
   texte scellé.
3. **Directeur humain** : la ligne de précision de GO-2026-11-02-23 (`<<PRECISION_GO_23>>`).
4. **Scellement** : titre et statut récrits, nom `preenregistrement-tour-ferme-v1-v<N>.md`, compagnons `.sha256` (ce texte, ses couples
   et ceux du brouillon 5 compris, mineur 47), commit et poussée **avant** la course ; revérifier le bloc. Après la course : lecture par
   `demonstrations/lire_tour_ferme_v64.py … --releve-sha256 SHA`, S6 et comparaison des empreintes des commandes par le lecteur neuf
   (R13).

Aucun point de ce rapport ne demande d'appel de modèle, de dépense ni de code neuf.

## 5. Remplacements (couples T113 à T128)

Fichier de référence : `prereg/couples-contre-lecture-tour-ferme-v6.json` (même contenu). À appliquer dans l'ordre, chacun sur le
texte obtenu après les précédents ; chaque cible figure exactement une fois dans le brouillon 6 (`cdcb4470…`) et encore une fois à
son application ; aucune n'est dans une zone de l'étage 2 ; aucun texte nouveau ne porte de marqueur `<<…>>` ni de balise ; zones,
marqueurs, plan gelé et bloc d'empreintes inchangés (texte obtenu : 891 lignes ; garde 6 complète « conforme », cases d'essai).
Les couples de B11 (T114 à T118, T121, T126, T128) supposent son prix accepté ; T115 (S6) est l'option recommandée de défense en
profondeur.

**T113** — mineur 46 (en-tête : commit des fichiers `_v64`)

remplacer :

~~~~text
(copie de travail isolée ; sept fichiers `_v64` neufs, non suivis, non commités)
~~~~

par :

~~~~text
(copie de travail isolée ; sept fichiers `_v64` neufs, non suivis, non commités à l'écriture du texte, commités depuis au commit `63ed933`)
~~~~

**T114** — B11, I33, I34 (section 0, point 7 : ce que les commandes v3 doivent faire)

remplacer :

~~~~text
(TF-01 : rôles de l'étage acceptés, sortie minimale par rôle ; chemins et empreintes en section 13)
~~~~

par :

~~~~text
(TF-01 : rôles de l'étage acceptés, sortie minimale par rôle ; code 4 réservé aux refus que la session porte en elle-même, tout refus qui tient à l'état du relais ou de la commande hors du code 4, réponse coupée des rôles de l'étage rendue en code 0 : annexe A, A.6 bis ; chemins et empreintes en section 13)
~~~~

**T115** — B11 (section 6 : audit S6, fin des tours au premier tour d'une carte ; défense en profondeur, option recommandée)

remplacer :

~~~~text
(un gardien qui refuse les cartes réelles et non les scriptées fausserait A4).
~~~~

par :

~~~~text
(un gardien qui refuse les cartes réelles et non les scriptées fausserait A4).
- **S6 — fin des tours au premier tour d'une carte (v64 ; contre-lecture courte du brouillon 6, B11)**, vérifié à chaque course, déclenché ou non, par le lecteur neuf (R13) sur les `resultat.json` scellés, avant toute lecture d'issue : une carte dont le champ `fin_des_tours` commence par « tour 1 : » et dit « budget_depasse » ou « rien envoyé » n'a pas été coupée par sa borne (au premier tour, le plafond passé est la borne entière, 0,80 USD, quand la consigne et la sortie minimale en coûtent ≈ 0,08 au barème d'essai) : la limite vient d'ailleurs (relais, commande, prix de la configuration) ; une seule suffit : défaut, course invalide, aucune issue, chiffres partiels rapportés. Le témoin du vérificateur n'entre pas dans S6 (un « rien envoyé » y est permis, jamais décisif).
~~~~

**T116** — B11 (section 7, garde 5 : le plafond d'un relais reste un arrêt)

remplacer :

~~~~text
plafond d'un relais atteint (« budget_depasse » hors plafond de la fiche, sauf session « rien envoyé », garde 16) → arrêt, jamais « non concluant »
~~~~

par :

~~~~text
plafond d'un relais atteint (« budget_depasse » hors plafond de la fiche ; refus propre du relais ou de la commande — 402, 429, plafond cumulé — que les commandes v3 sortent hors du code 4, annexe A, A.6 bis) → arrêt, jamais « non concluant » ; seule une session « rien envoyé » à son plafond de session finit les tours de la carte (garde 16)
~~~~

**T117** — mineur 45 (section 7, garde 16 : « 402 d'un relais » ne vaut pas pour une commande ; ligne de code 4 lue « refus »)

remplacer :

~~~~text
« budget_depasse » non marqué sous le plafond passé (402 d'un relais) ou part du relais épuisée → arrêt (C13)
~~~~

par :

~~~~text
« budget_depasse » non marqué sous le plafond passé ou part du relais épuisée → arrêt (C13) ; ligne de code 4 au coût plancher qui porte aussi `modele_servi` nul ou vide, ou un refus → refus (R-764), arrêt (sonde de la contre-lecture courte du brouillon 6, hors des essais v64) ; refus propre d'un relais ou de la commande (402, 429, plafond cumulé) : hors du code 4 par les commandes v3, donc erreur et arrêt (annexe A, A.6 bis)
~~~~

**T118** — B11 (section 10 : course à blanc déclarée du contre-lecteur)

remplacer :

~~~~text
| L4 | rédacteur, ≈ 07:24 |
~~~~

par :

~~~~text
| L2b-cl6 | contre-lecteur du brouillon 6, 3 novembre, 01:24:54 à 01:25:03 UTC (lecture juste après) | course à blanc du lanceur v64 sur le code gelé de ce texte, bac factice, aux conditions du plan, barème d'essai de 10 USD par million de jetons pour les deux relais, « rien envoyé » au premier tour de chaque carte (`--scenario-experimentateur rien_envoye:1` : ce que rendrait une limite du relais ou de la commande sortie en code 4) | 20261102 | code 0, 51 cartes et témoins testés, tous « non concluant », 51 sessions d'expérimentateur « rien envoyé » au plafond de 0,80 USD, lecture par le programme v64 : « ne tient pas (T2, T3, T4) », n1 « critère », A4 « le bras aléatoire promeut autant que le bras réel » (cause : sensibilité insuffisante), S2 seul déclenché ; relevé `389fc91575bdceba…`, lecture `1cdcdd23def75b1d…` ; prédictions inchangées |
| L4 | rédacteur, ≈ 07:24 |
~~~~

**T119** — mineur 46 (section 10 bis : contre-lecture courte du brouillon 6 faite)

remplacer :

~~~~text
**Contre-lecture R2 courte et neuve à faire, sur ce texte, le diff v63 → v64 et les essais neufs.**
~~~~

par :

~~~~text
Contre-lecture R2 courte et neuve, sur ce texte, le diff v63 → v64 et les essais neufs : `prereg/contre-lecture-courte-preenregistrement-tour-ferme-v6.md` (3 novembre 2026, sous-agent neuf), verdict « scellable après couples » (bloquant B11, levé par ses couples et par le constat de la session-depot sur ses commandes v3 ; importants I33 et I34 ; mineurs 45 à 54) ; ses couples T113 à T128 (`prereg/couples-contre-lecture-tour-ferme-v6.json`) sont appliqués à ce texte ; compagnons `.sha256` de ce rapport et de ces couples, comme de ceux de la contre-lecture courte du brouillon 5, à écrire au scellement (R6).
~~~~

**T120** — I34 (section 12 : sortie du vérificateur bornée par son plafond)

remplacer :

~~~~text
celles de la course à blanc L2b-v64-b6 en font de 8 115 à 8 220, celle de trois exécutions aux sorties pleines peut en faire 26 822 (texte ordinaire), 40 322 (fins de ligne) ou davantage (mesures au rapport v6).
~~~~

par :

~~~~text
celles de la course à blanc L2b-v64-b6 en font de 8 115 à 8 220, celle de trois exécutions aux sorties pleines peut en faire 26 822 (texte ordinaire), 40 322 (fins de ligne) ou davantage (mesures au rapport v6) ; sa sortie, elle, est bornée par ce plafond à ≈ 1 460 jetons pour une consigne de 8 124 caractères (1 000 au brouillon 1 de la configuration v3, `--max-sortie-lecteur` ; la configuration du 1er novembre bornait à 4 000 jetons la sortie d'Argon hors proposeur, `--max-sortie-court`) : une réponse coupée reste un témoin « non concluant » si la commande la rend en code 0, et arrêterait la course en code non nul (annexe A, A.6 bis).
~~~~

**T121** — B11, I33, I34, mineur 50 (section 13 : ce que les commandes v3 doivent faire ; leurs empreintes au manifeste)

remplacer :

~~~~text
`"envoye": false` sur la dernière ligne de toute sortie en code 4 où rien n'est parti) ; chemins et empreintes : 
~~~~

par :

~~~~text
code 4 réservé aux refus que la session porte en elle-même (pire cas au-dessus de `PLAFOND_SESSION_USD` ; consigne au-delà de la fenêtre d'entrée du modèle, si la commande la contrôle), rien parti, dernière ligne `"envoye": false` sans `modele_servi` nul ni refus ; tout refus qui tient à l'état du relais ou de la commande en un autre code non nul ; réponse coupée des rôles de l'étage rendue en code 0 : annexe A, A.6 bis) ; le lanceur ne vérifie pas leurs empreintes, il relève celle de chaque fichier de commande au manifeste (`configuration.adaptateurs.<relais>.empreintes`) : le lecteur neuf (R13) les compare à celles-ci, un écart est un défaut de course ; chemins et empreintes : 
~~~~

**T122** — mineur 48 (section 13 : règle exacte de la fermeture statique)

remplacer :

~~~~text
fichiers chargés par chemin, évaluateur servi : 92 fichiers en v64, égalité exacte essayée par `Fermeture`
~~~~

par :

~~~~text
fichiers chargés par chemin depuis leur propre dossier, évaluateur servi : 92 fichiers en v64, égalité exacte essayée par `Fermeture` ; `demonstrations/banc_tricheurs_v8.py` et `demonstrations/banc_tricheurs_v7.py`, que seule la fonction `banc()` de `pole/attaque_goodhart_v2.py` chargerait, par un chemin d'un autre dossier, n'y sont pas, et aucune course du tour n'appelle cette fonction
~~~~

**T123** — mineur 46 (section 13 : bloc revérifié après commit)

remplacer :

~~~~text
(quatre fichiers du bloc sont neufs, non suivis, à revérifier après commit : `demonstrations/tour_ferme_v64.py`, `demonstrations/lire_tour_ferme_v64.py`, `pole/tour_ferme_v64.py` et `pole/adaptateur_commande_v64.py` ;
~~~~

par :

~~~~text
(quatre fichiers du bloc sont neufs, non suivis à l'écriture, commités depuis au commit `63ed933` : `demonstrations/tour_ferme_v64.py`, `demonstrations/lire_tour_ferme_v64.py`, `pole/tour_ferme_v64.py` et `pole/adaptateur_commande_v64.py` ; revérifiées par la contre-lecture courte du 3 novembre 2026 : les 92 empreintes égales à l'arbre de travail et à `63ed933` ;
~~~~

**T124** — mineur 46 (section 14, point (2))

remplacer :

~~~~text
à faire : la contre-lecture R2 courte et neuve de ce brouillon 6, du diff v63 → v64 et des essais neufs, par un sous-agent neuf ;
~~~~

par :

~~~~text
fait : la contre-lecture R2 courte et neuve de ce brouillon 6, du diff v63 → v64 et des essais neufs, par un sous-agent neuf (`prereg/contre-lecture-courte-preenregistrement-tour-ferme-v6.md`), ses couples appliqués ;
~~~~

**T125** — mineur 49 (section 14, point (4) : crédit du compte Kimi, TF-06)

remplacer :

~~~~text
), les clés, **`bwrap` 0.9.0 et une identité
~~~~

par :

~~~~text
), les clés et le crédit du compte Kimi (TF-06 : compte sans crédit le 2 novembre ; sans recharge, la première session de Kimi sort en erreur : arrêt, code 3, aucune issue), **`bwrap` 0.9.0 et une identité
~~~~

**T126** — B11 (annexe A, A.6 bis : le code 4 réservé au plafond de session)

remplacer :

~~~~text
Une limite propre du relais que la commande lit aussi en code 4 « rien envoyé » (refus 402 du plafond du relais, 429 de son nombre d'appels : message n° 294 de la session-depot) serait lue de même, sans arrêt : chaque carte suivante finirait ses tours sans exécution (« non concluant », compté par T4) au lieu d'un arrêt.
~~~~

par :

~~~~text
**Le code 4 « rien envoyé » est réservé aux refus que la session porte en elle-même** (contre-lecture courte du brouillon 6, B11) — son pire cas au-dessus de `PLAFOND_SESSION_USD` ; une consigne au-delà de la fenêtre d'entrée du modèle, si la commande la contrôle avant envoi — : tout refus qui tient à l'état du relais ou de la commande — plafond ou nombre d'appels propres du relais (402, 429 : la commande d'Argon v2 les sortait en code 4, message n° 294 de la session-depot), plafond cumulé de la commande (`--plafond-cumule-usd`, registre), plafond d'étape (`PLAFOND_ETAPE_USD`), toute autre garde de la commande — sort en un autre code non nul (par exemple 3 au plancher, rien parti, comme les 400, 403, 411 et 413 du relais, et comme la commande de Kimi v1 pour tout refus du relais) : lu « erreur », arrêt de la course (code 3, relevé partiel scellé, aucune issue ; la reprise de la section 7 vaut pour cette panne d'infrastructure). Sans cette règle, une telle limite serait lue « rien envoyé » : chaque carte suivante finirait ses tours sans exécution, et la lecture gelée rendrait une issue fausse au lieu d'un arrêt (section 10, L2b-cl6 : « ne tient pas (T2, T3, T4) » et A4 « promeut autant », code 0) ; asymétrie (R4) : une limite d'infrastructure ne peut que faire manquer l'étage. Prix de la règle : une limite propre d'un relais ou d'une commande devient un arrêt, jamais une issue.
~~~~

**T127** — I34 (annexe A, A.6 bis : l'exigence du brouillon 5 contredisait la v64 et l'option (c))

remplacer :

~~~~text
aucune ne refuse avant dépense une session dont le plafond vaut, pour l'expérimentateur, le reste de la borne de 0,80 USD de la carte (0,80 USD au premier tour, parfois quelques centimes au dernier), pour le vérificateur 0,1 USD à chaque session (le plus bas des plafonds fixes de la course), pour un proposeur `plafonds_session.proposeur` ;
~~~~

par :

~~~~text
aucune ne refuse avant dépense, autrement qu'en code 4 « rien envoyé » (ci-dessous), une session dont le plafond vaut, pour l'expérimentateur, le reste de la borne de 0,80 USD de la carte (0,80 USD au premier tour, parfois quelques centimes au dernier : sous le prix de l'entrée et de la sortie minimale du rôle, le refus en code 4 est la fin des tours prévue en v64), pour le vérificateur 0,1 USD à chaque session (le plus bas des plafonds fixes de la course), pour un proposeur `plafonds_session.proposeur` ; la sortie minimale de chaque rôle reste celle d'une réponse entière du rôle (abaissée pour accepter les derniers centimes, elle rendrait des réponses coupées) ;
~~~~

**T128** — B11, I33, I34, mineur 51 (annexe A, A.6 bis : ce que la session-depot vérifie en v64)

remplacer :

~~~~text
v64 : elle vérifie aussi que toute sortie en code 4 où rien n'est parti porte `"envoye": false` (booléen) sur sa dernière ligne ;
~~~~

par :

~~~~text
v64 : elle vérifie aussi que chaque commande ne sort en code 4 que pour un refus que la session porte en elle-même (ci-dessus), rien parti, sa dernière ligne portant `"envoye": false` (booléen), sans clé `modele_servi` (ou exactement le modèle demandé), sans `refus` ni `stop_reason` (une ligne au coût plancher qui porte `"modele_servi": null` ou vide est lue « refus », R-764 : arrêt ; I33), de préférence avec sa cause (`"cause": "plafond_session"`), écrite aussi à son registre ; que tout refus qui tient à l'état du relais ou de la commande sort en un autre code non nul (ci-dessus) ; que ses contrôles cumulés (plafond cumulé, `PLAFOND_ETAPE_USD`) portent sur ce que le noyau compte au même relais, le registre `{REGISTRE}` étant commun aux deux commandes ; que, pour `experimentateur_test` et `lecteur_test`, une réponse coupée par sa borne de sortie (`finish_reason` « length », `MAX_TOKENS`) est rendue en code 0 avec son texte, son coût et `modele_servi` (l'étage y lit une réponse sans demande, fin des tours, ou un témoin « non concluant ») et jamais en code non nul, qui arrêterait la course (la commande de Kimi v1 sort en code 5 sur une réponse tronquée ; I34) ; que la plus longue consigne d'expérimentateur que l'étage permet (≈ 393 000 caractères, mesure du rapport v6) tient dans la fenêtre d'entrée du modèle servi, ou que la commande la refuse avant envoi en code 4 (sinon l'erreur de l'interface sortirait en code 3 : arrêt ; I34) ; que sa réservation d'entrée compte au moins un jeton par trois caractères de consigne (sinon la vérification préalable de la v64 refuserait des sessions que la commande accepterait) ;
~~~~
