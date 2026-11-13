# Verdict (règle R13) — course réelle de l'organisme d'idéation, code v67, configuration v8, GO-2026-11-12-06 — v1

**Verdict : l'issue rendue est confirmée — C1 « la chaîne garde (classe couverte, ce monde, cette taille) » : classe couverte du
nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte, ni sur les données réelles, ni sur la
qualité des idées. Sept réserves, aucune ne change l'issue (section 5).**

**Troisième tentative sous ce dessin** : les deux premières (code v66, GO-2026-11-10-11) se sont arrêtées au premier appel, issue
C5 « non jugeable (arrêt) », sans aucune loi jugée. Les trois relevés sont rapportés ensemble en section 4.1 (règle R4).

- **Juge** : sous-agent neuf de la session `session_01VJdZpSMxSdk2SJ1ScmdfNv`, Claude Fable 5.2 (`claude-fable-5-2`). Je n'ai
  écrit ni le préenregistrement (v1 ou v2), ni le code de l'organisme, ni la course, ni son rapport, ni la lecture. Même modèle
  que le contre-lecteur du texte v2 (agent distinct) : dit.
- **Heure** : 2026-11-12, travail de 17:27 à 17:50 UTC environ (`date -u`).
- **Critères appliqués** : ceux du texte scellé, section 8, dans l'ordre de sa table, et les vérifications V-1 à V-8 ; rien d'autre.
- **Je n'ai lu** aucun dossier `diag/`, `runs/`, ni aucune pièce des bras d'attaque, du mode tenu à l'écart, de 7a ou de 7b.

## 1. Pièces lues et empreintes (toutes vérifiées par moi)

| pièce | chemin | sha256 | vérification |
|---|---|---|---|
| texte scellé v2 (fait foi) | `docs/notes/organisme-boucle-reelle-v1/preenregistrement-boucle-reelle-organisme-v1-v2.md`, `origin/main` à `14396ae0` | `80fe4f03b4905b2376b8cd16873c9ab93da3b97e4e01a9a2932be329bab0954d` | égale à la valeur attendue ; égale au champ `preenregistrement.sha256` du relevé |
| relevé de la course | branche `donnees/course-organisme-v67-poste-local-v1` (tête `659a1297`), `docs/notes/organisme-boucle-reelle-v1/course-v67/poste-local-v1/course-reelle/boucle-reelle-v66.json` | `21bc75f4d81825695b30b2b32f21feaa91322293f6c2c3161a28dc179ec6df71` | compagnon égal |
| lecture versée | même branche, `…/poste-local-v1/lecture-course-reelle.json` | `d0ef1ee7667bdc665747c2822dcb031abfea3b38b3094782ad72ae593c016086` | compagnon égal |
| rapport de course | même branche, `…/course-v67/rapport-course-v67-poste-local-v1.md` | `8a98f2f67b8c442e65dc700c081c270ec0a025bac09e89fe03961cf424b09f65` | compagnon égal |
| tout le dossier `course-v67/` | même branche | — | 272 fichiers, 272 compagnons égaux, aucun fichier sans compagnon |
| dossier `ecart-1-sortie-proposeur-v1/` | même branche | — | 41 fichiers, 41 compagnons égaux ; contre-lecture `48633203…`, vérification courte `ed30e3de…`, configuration v8 `eb626289…` |
| relevés des deux tentatives précédentes | branche `donnees/course-organisme-v66-poste-local-v1` (tête `24c25908`), `…/course-v66/poste-local-v1/course-reelle/boucle-reelle-v66.json` et `…/poste-local-v2/…` | `c9c6212bfe16b148e5df42c27a1f631eeafbd79ca9c7b82ac048fabce69c3069` ; `5a7fc27c7dfb1c7e0911cf9df3aa0b1c785e386bfa32de0294625c5709d52b9b` | compagnons égaux (dossier `course-v66/` : 66 sur 66) |
| rapports des deux tentatives | même branche, `rapport-course-v66-poste-local-v1.md` et `-v2.md` | `83fd674b0d07a5944fb27172e07fc5cdb1ad24da83be73c9c2a724f7a8d30780` ; `89b97faf2c7ec75350e44cd8b0ba3283645c84d47fa495350a8429206c407f28` | compagnons égaux |
| arbre de l'organisme | clone neuf de `https://github.com/lciric/ideation-organism`, commit `ab53b7f482df5149d9f672f40e04220dffb4173a` (sur `origin/main` du dépôt public) | — | **99 empreintes sur 99** égales au bloc `empreintes-du-code-v67` du texte scellé ; écart de `7e415cba` à `ab53b7f4` : cinq fichiers ajoutés, aucun fichier antérieur modifié |
| registre des GO | `registres/go.md`, `origin/main` | `3bef01b574c60dc17cd043efd1aabb43d51b71aeb6dcda6a7d790e42411ce70c` | égale à l'empreinte de la copie lue par le lanceur (rapport) ; ligne GO-2026-11-12-06 (l. 313) égale à l'octet à celle de la section 13 du texte scellé |
| registre des décisions | `registres/decisions.md`, `origin/main` : R-2422, R-2423, R-2426, R-2429, R-2430, R-2440 | — | lues |

## 2. Lecture gelée rejouée

Commande, depuis `orchestrator/` de l'arbre reconstruit, sur une copie du dossier `course-reelle/` :
`python -I -B demonstrations/lire_boucle_reelle_v66.py SORTIE LECTURE.json --releve-sha256 21bc75f4…` (interpréteur du dépôt de
travail, Python 3.13.18, numpy 2.4.6 ; la machine de la course avait Python 3.13.5 et numpy 2.2.4).

- Code 0 ; code « C1 » ; `aussi` vide ; phrase rendue égale à l'octet à celle du rapport :
  « Issue C1 : « la chaîne garde (classe couverte, ce monde, cette taille) » — course reel (decisif) (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte). »
- Comparaison à la lecture versée : **deux lignes seulement diffèrent**, celles que le programme écrit d'après l'horloge et le
  chemin (`lu_utc` ; `releve.chemin`). Tous les autres champs sont égaux (constats, audits, mesures, oracle, intervalles). En
  remettant dans ma sortie les deux valeurs de la lecture versée (`2026-11-12T15:07:35+00:00` ; `/root/sorties/course-reelle/boucle-reelle-v66.json`),
  son empreinte est **`d0ef1ee7667bdc665747c2822dcb031abfea3b38b3094782ad72ae593c016086`**, celle de la lecture versée. L'égalité à
  l'octet sans cette remise est impossible par construction (réserve R-7).
- Constats du programme : `p1` vrai ; `p2_v1_v2` vrai ; `p4` vrai ; `p5_copies_refusees` vrai ; `p6_tenue` vrai ; `ecarts_p6`,
  `fausses_promues`, `copies_promues`, `manques` vides ; `arret` nul ; `partiel` faux.

## 3. Vérifications V-1 à V-8 sur le relevé brut (champ `releve`)

| # | champs lus | résultat |
|---|---|---|
| V-1 | `lecture_selection` | objet (non nul) : **tient** |
| V-2 | `archives_de_jugement["2"]` | présente, 12 lois (K1 et 11 retenues) : **tient** |
| V-3 | `arret` = nul ; `generations_jouees` = [1, 2] | sans objet (aucun arrêt) |
| V-4 | `lecture_selection.refus` = nul ; `attendu` = `lu` = `lu_sur_disque` = `6e7e652ead65550859334b44884c83567feef011e90e18cea77a079a5f62bd30` | **tient** (en plus, hors texte : c'est l'empreinte du fichier versé `generation-1/bilan-generation-v59.json`) |
| V-5 | `vues_servies["1"].appels` : `kimi`, `argon`, une fois chacun, `texte_recu_sha256` = `texte_sha256` = `c4b91ee5…` ; `vues_servies["2"].appels` : `kimi`, `argon`, une fois chacun, `texte_recu_sha256` = `texte_sha256` = `5d722e41…` | **tient** pour les deux générations |
| V-6 | `selection_finale` objet ; `refus` = nul ; `lu` = `bilan_sha256` = `9f995cdf0237f5be482cf538cc9ac3d5d4a4685e5b62c02ba442423cb9e21fdd` | **tient** (en plus : empreinte du fichier versé `generation-2/bilan-generation-v59.json`) |
| V-7 | `retenues["1"]` : liste de 11 ; `retenues["2"]` : liste vide | **tient** |
| V-8 | `retenues["1"]` vide ? | **non** : 11 cartes réelles retenues en génération 1 ; la ligne C7 ne s'applique pas |

Aucun manque, aucun écart : les vérifications n'ajoutent rien aux constats du programme ; programme et texte ne divergent pas.

**Lecture de la table de la section 8, dans l'ordre** : C5 non (aucun arrêt, relevé complet, V-1, V-2, V-5, V-7 tiennent) ; C4 non
(P6 tenue, V-4 à V-6 tiennent, aucune copie promue) ; C2 non (F1 à F4 non promues en génération 1 ni 2) ; C3 non (V1 et V2
promues puis survivantes en génération 1) ; C6 non (T-ELIM promue puis éliminée, T-MAL refusée au gardien) ; C7 non (V-8) ;
**C1 : P1, P4, P6 tenues et V-1 à V-7 tenues.**

P2 tient (rien à écrire en tête). Aucune fausse découverte d'une carte réelle selon l'oracle (`oracle.fausses_decouvertes_reelles` vide).

## 4. Audit de symétrie (règle R4 ; audit A1 « trop beau », déclenché d'office par C1)

Le résultat est propre ; il reçoit l'audit qu'aurait reçu un échec. Constats, puis ce que j'ai cherché sans le trouver.

### 4.1 Les trois relevés ensemble

| tentative | relevé | code du lanceur | lois jugées | issue | cause |
|---|---|---|---|---|---|
| 1 (v66, 12 novembre, 00:01 UTC) | `c9c6212b…` | 3 | 0 carte, 0 loi plantée ; `generations_jouees` vide | C5 | proposeur Kimi en erreur (amont du relais : HTTP 429) ; garde 13 |
| 2 (v66) | `5a7fc27c…` | 3 | 0 carte, 0 loi plantée ; `generations_jouees` vide | C5 | réponse du proposeur Kimi coupée à sa borne (46 714 jetons de sortie) ; garde 13 |
| 3 (v67) | `21bc75f4…` | 0 | 23 cartes, 18 lois plantées, deux générations | C1 | — |

- Les lectures versées des tentatives 1 et 2 (`7de89198…`, `edae8c4f…`) disent C5, `aussi` vide, aucune fausse ni copie promue,
  aucun écart de P6 : aucun « C2 » ni « C4 (partielle) » masqué par un arrêt.
- **Aucun résultat n'était visible avant l'écart 1** : zéro jugement dans les deux premiers relevés. L'écart ne change que des
  bornes de sortie et des délais (code : cinq fichiers ajoutés, aucun modifié ; configuration v8 ; relais Kimi) ; les sections 4
  à 9 du texte sont celles du v1. La troisième tentative n'est donc pas un tirage choisi parmi trois résultats.
- **Graines neuves** : la racine du relevé 3 est l'entier de l'empreinte du texte v2 (vérifié : `int("80fe4f03…", 16)` = champ
  `racine`) ; celle des tentatives 1 et 2 était l'entier de l'empreinte du texte v1.
- Constat dans les deux sens : les deux appels du proposeur Kimi de la tentative 3 (31 891 et 38 343 jetons de sortie ; 861 s et
  1 099 s) auraient tenu sous les bornes du v1 (46 714 jetons, 1 800 s). Le succès tient donc autant à la longueur variable du
  raisonnement du modèle qu'à l'écart ; cela ne touche aucun critère.
- La tentative 2 a été une reprise sans texte neuf, sur mot direct de Lazar (R-2422), alors que la section 10 du texte v1 demandait
  un texte neuf contre-lu pour une reprise ; déclaré au registre ; cela concerne le v66, non ce relevé (lancé sous un texte neuf,
  contre-lu et scellé).

### 4.2 Le juge a-t-il été contourné ? — rejeu hors ligne des 40 jugements

J'ai rejoué, avec le code gelé de l'arbre reconstruit (`pole/a_blanc_v59.juger_carte`), chacun des 40 jugements du relevé (23
cartes, 17 lois plantées ; T-MAL n'est pas jugée), avec la racine du relevé, la tâche
`boucle-reelle-v66|bras=reel|generation=<g>|carte=<identifiant servi>` (ou `|plantee=`) et l'archive consignée de sa génération.
**40 sur 40 égaux** au relevé : empreinte d'engagement, graines, nombre de membres d'archive, log W maximal à six décimales,
promotion, membre dominant final et, pour les lois plantées, log e et promotion au seuil log(22/0,05) ≈ 6,0868. Le rejeu a
tourné sous numpy 2.4.6 (course : 2.2.4) : aucune sensibilité à la version.

| loi | génération | membres d'archive (attendus) | log W maximal | promue | test de mort |
|---|---|---|---|---|---|
| V1 | 1 | 4 (4) | 91,823 | oui | survit (0,496303 ≥ 0,02) |
| V2 | 1 | 4 (4) | 61,430 | oui | survit (0,396128 ≥ 0,02) |
| V3 ; V4 (mesure P3) | 1 | 4 (4) | 4,248 ; 5,875 | non (sous 6,0868) | — |
| F1 ; F2 ; F3 ; F4 | 1 | 4 (4) | −0,792 ; −0,517 ; −0,115 ; −1,287 | non | — |
| T-ELIM | 1 | 4 (4) | 78,802 | oui | éliminée (0,488220 < 2,0) |
| T-MAL | 1 | — | — | refusée au gardien (bloc `test_de_mort.statistique` absent) | — |
| F1 ; F2 ; F3 ; F4 | 2 | 37 (37) | −13,577 ; −16,431 ; −14,352 ; −19,053 | non | — |
| C1 ; C2 ; C3 ; C4 (copies) | 2 | 37 (37) | −2,714 ; −1,163 ; −0,788 ; −2,946 | non | — |

- Les lois plantées du relevé (V1 à V4, F1 à F4, T-ELIM, T-MAL ; génération 1 et F1 à F4 de la génération 2) sont **égales au bloc
  `jeu-plante-v65` du texte scellé** (comparaison en JSON canonique).
- Les fausses ont toutes un log W maximal ≤ 0 (plus grand : −0,115, F3 en génération 1).
- Cartes réelles : génération 1, 11 jugées avec 4 membres, toutes promues (log e de 6,68 à 14,58 ; règle de Benjamini et Hochberg
  à m = 22 : le seuil le plus bas, au rang 11, est log(40) ≈ 3,69) ; génération 2, 12 jugées avec 37 membres, aucune promue
  (log W maximal de −1,08 à −6,40).

### 4.3 La génération 2 a-t-elle vraiment lu la sélection ? — la preuve n'est pas vide

- Vue servie en génération 2 = archive de jugement de la génération 2 = {K1} ∪ les 11 retenues ; retenues écrites = lues = celles
  du relevé ; chaque loi de l'archive est la loi de sa carte de génération 1 ; **aucune loi plantée dans la vue ni parmi les
  retenues** (ni par identifiant, ni par contenu).
- Les copies C1 à C4 sont bien celles des quatre premières retenues par log e (`F-85ebb8a13dbd`, `F-2a1b31f3b5b5`, `F-0e383ebd264a`,
  `F-70e224d5849f`), de contenu égal à leur source.
- **Contre-épreuve que j'ajoute (hors critères, sans effet sur l'issue)** : j'ai rejugé les copies avec le même code et les mêmes
  graines, mais avec l'archive {K1} seule, comme si la sélection n'avait pas été lue. Elles sont alors **toutes promues** (log W
  maximal 93,6 ; 76,9 ; 82,6 ; 87,1). Leur refus en course (log W < 0) vient donc bien de la sélection lue. Même contre-épreuve
  pour F1 à F4 sans aucune archive : trois sur quatre promues (log W maximal 9,5 ; 10,4 ; 12,4 ; F1 à 5,9, sous le seuil) ; la
  protection vient de l'archive, comme le texte l'annonce (section 3.4).

### 4.4 Le bac à sable et l'expérimentateur — sur les fichiers bruts

Pour chacun des 14 tests de mort (V1, V2, T-ELIM et les 11 cartes réelles promues de la génération 1) :

- `execution-01/resultat.json` : commande `setpriv --reuid 64097 --regid 64097 … bwrap --unshare-all --unshare-net … --seccomp …`,
  code 0, statut « réussie », une seule exécution, aucun incident ; étages `bac_a_sable` = « bwrap », `factice` = faux.
- La loi du script écrit par l'expérimentateur est celle du relevé (14 sur 14).
- **J'ai recalculé hors du bac**, avec l'évaluateur gelé (`pole/evaluateur_lois_v62.py`, `26613fe7…`, égal à la copie servie dans la
  tranche) et la tranche versée (`episodes.csv`, `14c2d8d1…`), le fichier `gains.csv` de chaque loi : **égal à l'octet** à la copie
  scellée, 14 sur 14 (400 épisodes) ; la moyenne est celle du verdict du noyau et du contre-calcul de l'orchestrateur ; l'empreinte
  de la copie est celle du verdict.
- Expérimentateur appelé : journal du relais Kimi (`6c0f9f57…`), 30 appels, tous `kimi-k3.1-pro`, statut amont 200, `usage`
  présent : 2 de proposeur et 28 d'expérimentateur (14 tests × 2 tours : un script, puis « fin ») ; journal du relais Argon
  (`c5ae29a0…`), 16 appels, tous `gemini-4-argon`, « OK » : 2 de proposeur et 14 de vérificateur. Mêmes comptes que
  `appels_etage` (28 et 14) et `appels_proposeurs` (4) du relevé ; sommes des coûts égales à celles du relevé.
- **Aucun modèle de la famille Claude** : le champ `moteur_etage` = « claude-sdk » est le mot de l'étage v5 pour « mode réel »
  (`demonstrations/tour_ferme_v64.py`, `moteur_de_l_etage`) ; les deux journaux de relais ne portent que Kimi et Argon.

### 4.5 Ce que j'ai cherché, et qui rendrait le résultat « trop beau »

| soupçon | constat |
|---|---|
| arrêts évités, gardes desserrées | `arret` nul, `incidents` vide ; code v67 = v66 plus cinq fichiers ajoutés ; préalables : 407 essais passés et 6 sautés (aucun du vrai bac), 151 mutations tuées sur 151, essai à blanc au vrai bac code 0, vérification « conforme » ; plafonds des relais égaux aux parts (33 et 7) |
| cartes non jouées | génération 1 : Kimi a rendu **5** lois et non 6 (le texte dit « au plus 6 ») : 11 cartes, puis 12 en génération 2 ; aucune refusée au gardien ; aucune ignorée (réserve R-4) |
| juge contourné | non : 40 jugements rejoués égaux (4.2) |
| toutes les cartes réelles de la génération 1 promues, survivantes et « vraies découvertes » (11 sur 11) | s'explique sans fuite : K1 ignore le trait z1, qui porte ≈ 0,47 nat par épisode ; toute loi qui ajoute z1 gagne 0,42 à 0,46 nat sur la tranche (L* : 0,496). Fuite cherchée : 0 touche des paramètres de L* dans les contextes de la génération 1 ; 0 ligne de la tranche dans les contextes servis ; 0 touche hors de la loi gelée dans les 42 consignes de l'étage. Ces 11 lois sont des variantes proches (trois lois de Kimi partagent la même base) : ce ne sont pas 11 idées (réserve R-5) |
| loi plantée vue par les proposeurs | **2 touches signalées par le programme et tues par le rapport de course** : en génération 2, pour chaque proposeur, la valeur « 1.3 » au chemin `contexte.lois_retenues[3].loi.poids[1][1]`, égale à deux décimales au paramètre `poids[2][0]` de L* (1,296203). Relue à la main : c'est le poids de z1 pour l'issue 1 de la carte réelle retenue `F-6e2a1edad084` (G1-kimi-02), valeur ronde, à une autre place que le paramètre de L* (dont le poids de même place vaut 3,134). **Coïncidence, pas une fuite** ; mesure sans issue (réserve R-1) |
| dépense anormalement basse | 1,99431 USD de modèles (Kimi 1,13813 ; Argon 0,85618), 46 appels relayés. Le compte est exact : 4 appels de proposeur + 14 tests × 3 appels. Le texte v2 attendait ≈ 3 à 4 USD : l'écart vient de ce que la génération 2 n'a eu aucun test (aucune promotion) et que les deux appels longs de Kimi ont coûté 0,33 et 0,40 USD, loin de leur pire cas (1,35). Prix recalculés sur deux appels : justes |
| troisième tentative après deux arrêts | section 4.1 : rien n'avait été jugé ; critères inchangés ; graines neuves |
| fiche du serveur vide | `poste-local-serveur-v1.md` : 0 octet, scellée telle quelle ; fiche complète `-bis` 53 s après ; sans rapport avec le relevé |
| réseau du poste perdu | la course tournait détachée sur la machine : journal continu de 14:21:52 à 15:07:32 UTC, dernier appel relayé à 15:07:22 ; aucun appel après la fin ; effet sur la seule durée de location (≈ 2 heures, ≈ 0,12 EUR) |
| consigne dont l'en-tête dit « brouillon » | différentiel entre le brouillon 1 (`9656d71a…`) et la consigne v4 (`7349680b…`) : les marqueurs remplis et la section « Marqueurs », rien d'autre ; aucun marqueur restant ; l'en-tête n'a pas été mis à jour (erreur déclarée, R-2440) ; exécutée sur le « go » explicite de Lazar. La consigne n'est pas une pièce des critères : sans effet sur la lecture |
| arbre modifié | le manifeste dit `depot.arbre_modifie` = vrai alors que le rapport dit « arbre propre » (réserve R-3) |

## 5. Réserves

- **R-1 — touches de la recherche de la loi plantée non rapportées.** Deux touches « à deux décimales » dans les contextes des
  proposeurs en génération 2 ; le texte attendait « aucun touché » ; le rapport de course ne les mentionne pas. Relues ici :
  coïncidence (section 4.5). À écrire au rapport au directeur.
- **R-2 — deux pièces brutes de l'audit A1 manquent.** (a) Le dossier des sessions des proposeurs est vide (quatre dossiers sans
  fichier, dit au rapport) : la réponse brute des proposeurs n'est pas gardée ; je ne peux donc pas vérifier que les cartes sont
  bien ce que les modèles ont rendu ; je ne compte pas ce point comme tenu. Ce qui en tient lieu : les journaux des relais
  (appels, jetons, octets), l'égalité du texte reçu et du texte bâti (V-5), les cartes du relevé. (b) Aucun fichier témoin ni
  journal de `bwrap` propre à chaque `gains.csv` n'est versé ; la machine est détruite. Ce qui en tient lieu : la commande complète
  de chaque exécution, la description de la sonde au manifeste, et mon recalcul hors bac, égal à l'octet. Les critères P1, P4 et
  P6 ne dépendent pas de (a) ; le recalcul couvre (b) pour la valeur des verdicts, non pour l'isolement lui-même.
- **R-3 — `arbre_modifie` = vrai au manifeste**, sans explication au rapport (même valeur aux deux tentatives v66 ; cause
  probable : la copie du texte scellé sous `orchestrator/prereg/`, fichier non suivi). Les 99 empreintes du code ont été vérifiées
  par le lanceur (relevé) et par moi sur le clone public : le code qui a tourné est le code gelé.
- **R-4 — une carte de moins.** Kimi a rendu 5 lois en génération 1 : 23 cartes réelles et non 24. Permis par le texte (« au
  plus 6 ») ; m reste 22.
- **R-5 — la génération 2 n'a exercé ni le bac ni la sélection sur un contenu.** Aucune carte réelle promue en génération 2 :
  aucun test de mort, sélection finale vide (scellée, relue : V-6). C'est « une génération et demie » au sens strict. Les 11
  retenues de la génération 1 sont des variantes proches d'un même constat (l'effet de z1) : le compte ne dit rien de la qualité
  ni de la diversité des idées, et 12 refus sur 12 en génération 2 ne disent rien d'une capacité à progresser au-delà.
- **R-6 — mesure des jetons d'Argon.** La lecture gelée compte les 16 appels d'Argon « sans usage » (sommes à 0) alors que le
  relevé porte bien leur usage, sous d'autres noms de champs (`entree`, `sortie`) que ceux que le texte annonçait. Mesure sans
  issue ; le coût, lui, est juste (journal du relais).
- **R-7 — égalité « à l'octet » de la lecture rejouée** : obtenue après remise de l'heure et du chemin de la lecture versée (deux
  lignes) ; tous les champs de fond sont égaux sans remise.

Dites pour mémoire, sans réserve : V3 et V4 non promues (mesure P3 ; la simulation donnait 617 et 501 sur 1 000) ; le plafond de
5 USD de la machine n'est tenu par aucun code (dépense ≈ 0,27 USD) ; `verifier-arbre` non lancé par le poste (non exigé par le
texte) ; simulation de puissance faite sous numpy 2.4.6, course sous 2.2.4 (rejeu égal).

## 6. Portée

- **Ce que l'issue dit** : avec de vrais agents (Kimi et Argon), un vrai bac à sable et les lois plantées du texte, la chaîne a
  (a) laissé passer V1 et V2 jusqu'à la survie, (b) refusé F1 à F4 dans les deux générations, jugées avec l'archive de leur
  génération, (c) jugé la génération 2 avec la sélection de la génération 1, sur un contenu (11 retenues, quatre copies refusées,
  promues si la sélection n'est pas lue) ; les deux cas d'instrument ont fait ce qu'ils devaient.
- **Bornes** : classe couverte du nul v8 ; monde jouet S-V1 (3 issues, 2 traits) ; archive de départ d'une loi ; deux
  fournisseurs ; une génération complète et une seconde jusqu'à sa sélection ; une seule course jugée.
- **Rien** sur : la classe non couverte (recombinaisons par morceaux, produits, compositions) — et des cartes réelles retenues
  ici sont de ces formes (`si_sinon`, `par_sous_population`), classées vraies par l'oracle, ce que C1 ne garantit pas en général ;
  la puissance aux effets faibles des données réelles ; la qualité des idées ; l'universalité sur des familles inédites (N-044) ;
  la composition des proposeurs (N-045, N-058).
- Selon la section 14 du texte, cette issue se rapporte **toujours avec A1-v3** (brèche hors classe établie) et avec cette portée.
- **Ce qu'elle ouvre** (section 8, ligne C1) : la proposition au directeur de plusieurs générations. C'est une proposition ;
  la décision, et toute dépense, restent à Lazar. Sous une chaîne correcte l'issue était presque certaine par construction
  (simulation : 1 000 sur 1 000) : elle établit l'absence de défaut de plomberie observé à cette taille, pas une performance.

## Annexe — rejeux, pour qui veut les refaire

Depuis `orchestrator/` de l'arbre `ab53b7f4`, avec `R` = le champ `releve` du fichier de course :

```
from pole import a_blanc_v59 as A
monde = A.charger_monde(".")                      # monde["sha256"] == R["monde_sha256"]
for c in R["cartes"] + R["plantees"]:             # sauf T-MAL (refusée au gardien)
    genre = "plantee" if "nom" in c else "carte"
    g = c["generation"]
    ev, d = A.juger_carte(c["loi"], monde, R["archives_de_jugement"][str(g)], int(R["racine"]),
                          f"boucle-reelle-v66|bras=reel|generation={g}|{genre}={c['identifiant_servi']}")
    # comparer d["empreinte_engagement"], d["graines"], d["membres_d_archive"], round(ev["log_richesse_max"], 6), ev["promue"]
# contre-épreuve des copies : même appel avec R["archives_de_jugement"]["1"] à la place de l'archive de la génération 2
```

Recalcul d'un `gains.csv` : `runpy.run_path("pole/evaluateur_lois_v62.py")["gains"](loi, ".../generation-1/exploratoire-etage/tranche/episodes.csv")`,
puis `"episode,gain\n" + "".join("%d,%r\n" % (i, x) for i, x in enumerate(g, 1))`, à comparer à `execution-01/produits/gains.csv.copie`.
