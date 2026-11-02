non scellable

# Contre-lecture R2 — préenregistrement du tour fermé (A2, A3, A4), brouillon 1

2 novembre 2026, de 07:05 à 07:55 UTC environ. Contre-lecteur neuf : je n'ai écrit ni le texte ni le code lus. Lecture seule ;
un seul fichier écrit dans l'arbre, celui-ci. Aucun commit, aucun `.sha256`, aucun `git fetch`, aucun appel de réseau ni de
modèle, aucune clé ; calculs sous `nice -n 10`. Dépôt public à la tête `0469450` ; les fichiers `*attaque_goodhart_v2*` non
suivis sont ignorés. Dépôt privé : `CLAUDE.md` et une ligne de `registres/go.md` (`GO-2026-11-02-06`), rien d'autre.

**Verdict en trois lignes.** Le texte est sérieux, et la plupart des choix tiennent : oracle, réserve par empreinte, porte
entre étages, zéro écrit d'avance. Il n'est pas scellable en l'état, pour deux raisons. (1) Par ses propres règles : le cœur
et le lanceur `_v60` ne sont pas écrits, 8 gardes sur 14 ne sont pas essayées (R5), les six cases de la section 5.2 sont vides.
(2) La lecture gelée de A4 et les phrases au mentor peuvent dire faux sur l'issue la plus probable, et la lecture gelée a
quatre défauts de code vérifiés (B3 à B6). Il faut un brouillon 2, puis une seconde contre-lecture, celle-ci portant aussi
sur le code.

## 0. Fichiers lus (empreintes vérifiées à la lecture) et ce qui a été rejoué

| fichier (depuis `orchestrator/`) | sha256 |
|---|---|
| `prereg/preenregistrement-tour-ferme-v1-brouillon1.md` | `09b9dfcc7aa55eef4739a50cc989f7c8967686b5e59659b7bb83520b954f5e52` (= rapport de rédaction) |
| `prereg/rapport-redaction-tour-ferme-v1.md` | lu en entier |
| `pole/reserve_tenue_a_l_ecart_v60.py`, `demonstrations/reserve_tenue_a_l_ecart_v60.py`, `pole/oracle_tour_ferme_v60.py`, `pole/lecture_tour_ferme_v60.py`, `essais/test_v60_*.py`, `essais/mutations_v60.py` | les 8 empreintes du rapport de rédaction, section 1, toutes égales |
| `prereg/rapport-code-boucle-fermee-v1.md` | `884b4f4f95a9b433c479ba91c83ae95d68832bb22bf4c8340e299039eb126e5c` |
| `pole/boucle_fermee_v59.py`, `pole/proposeurs_references_v59.py`, `pole/a_blanc_v59.py` (juge, oracle), `pole/nul_v8.py`, `pole/cycle.py` (`appliquer_multiplicite`), `pole/juge_plan_plein_v1.py`, `pole/aiguilleur_v53.py` (en-tête), `pole/tests_de_mort_v5.py` et `pole/etage_entre_generations_v57.py` (en-têtes), `exemples/temoins-pari-demo-v1.json`, `exemples/banque-t05-v2.json` (structure) | lus |
| scripts L1 et L2 du rédacteur (dossier de travail) | `18fa2220…`, `8ab78123…` (= rapport) |

Ce qui a été rejoué ou calculé :

- Essais : `nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_v60_reserve_tenue_a_l_ecart.py essais/test_v60_oracle_tour_ferme.py essais/test_v60_lecture_tour_ferme.py` → **46 réussis** (3,5 s).
- Banc : `nice -n 10 python3 -I -B essais/mutations_v60.py` → **17 mutations tuées sur 17** pour la raison attendue ; témoin 43 essais avant et après.
- **Sondes de la lecture gelée** : des relevés construits sont passés à `lecture_tour_ferme_v60`. Script
  `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/contre-lecture-tour-ferme-cl1/verif_lecture.py`,
  sha256 `18d72e83811807cbe363a5f81edc90f71ef64c28e9a0e6a493e6a278af1d1c07`. Résultats en B4 à B6.
- **L2b** : bras aléatoire aux conditions du plan, et un « bon proposeur » simulé. Trois générations, chaque bras contre sa
  propre archive, e-BH à m = 19 avec les 7 témoins, statistique du test de mort en processus, oracle v60. 24 répétitions du
  bras aléatoire et 8 du bon proposeur, 66 s, aucun modèle, aucun bac. Fichiers :
  - script `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/contre-lecture-tour-ferme-cl1/sim_bras.py`, sha256 `6c2304ed4ca99dffa85ae7f747943d14e7e32881479984ed692a9a6a5bd27ad9` ;
  - sortie `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/contre-lecture-tour-ferme-cl1/sim.json`, sha256 `5da09b12a1c1b6e75f7001e9746b768871529725ea6dbf6353f472dc413a87a2` ;
  - résumé `/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/contre-lecture-tour-ferme-cl1/sim.sortie.txt`, sha256 `dd112b9aa098f921419dc0c467f33837376c062983a573bc868f675b09b788e5`.

  Résultats :

  | bras | génération 1 | générations 2 et 3 | trois générations |
  |---|---|---|---|
  | aléatoire, part promue puis survivante (PS) | **35/288 = 0,122** | **13/576 = 0,023** | **48/864 = 0,056**, Wilson [0,042 ; 0,073] |
  | aléatoire, fausses découvertes (FD) | | | 1/864 |
  | bon proposeur (6 lois par génération, L* plus un bruit gaussien) | **48/48** | **0/96** | 0,333 |

  Lire les témoins hors famille ou dans la famille de l'e-BH ne change rien ici (48 PS contre 48).

## 1. Constats

### Bloquants

**B1 — Le code qui fait la course n'existe pas (texte : lignes 520 à 557 ; liste d'arrêt : lignes 421 à 429).** Restent à
écrire :

- `pole/tour_ferme_v60.py` : témoins hors de l'archive, gabarit imposé, e-BH à m fixé, familles séparées, contre-calcul,
  relevé ;
- la variante du juge à plan plein avec membres d'archive, et le constructeur de M2 ;
- le lanceur `demonstrations/tour_ferme_v60.py` ;
- leurs essais et leur banc ;
- la répétition à blanc de bout en bout.

Les gardes 5 à 10 et 12, la durée de la garde 13 et l'appel de la garde 11 ne sont essayés sur aucun cas sain ni sur aucun
artefact (R5). Le bloc de code gelé (section 13) cite des empreintes à la tête `7fadf96`, à recalculer. R1 exige le plan et le
code gelés avant la course : on ne scelle pas un texte dont le lanceur n'existe pas. Il faut aussi une contre-lecture R2 du code
écrit, que le texte prévoit déjà (ligne 574).

**B2 — Les cases Q, E0, R, T, M2 et V sont vides (lignes 298 à 305).** Le texte le dit lui-même : « un texte qui en garde une vide
ne se scelle pas » (ligne 10). Q (le texte servi le 1er novembre, sha256 `6fcb1035…`) est introuvable. Sans Q, l'étage 2 n'a pas
de question. Défaut proposé : si Q reste introuvable, l'étage 2 sert la question du collisionneur de la course 2, nommée et
empreintée comme telle. Il ne prétend alors pas que c'est « la question du 1er novembre ».

**B3 — La lecture gelée de A4 attribue la cause sans la mesurer, sur l'issue la plus probable (lignes 248 à 255 ; code
`lecture_tour_ferme_v60.py:89-94`).**

L'issue « T5 tient et borne de Newcombe ≤ 0 » se lit « les vrais proposeurs ne battent pas le hasard dans ce monde ». C'est
faux de trois façons.

1. **Puissance.** À 36 cartes contre 36, un écart vrai de 0,10 sur r est déclaré « discrimine » avec une probabilité
   d'environ 0,2, et un écart de 0,20 avec environ 0,6. Le texte le reconnaît (ligne 209), puis conclut comme si l'écart était
   nul.
2. **Sensibilité.** L'oracle mesure G et ΔG de *toutes* les cartes, promues ou non. Il peut donc dire si le bras réel produit
   plus de lois informatives et nouvelles que le bras aléatoire **avant** tout jugement. Si oui, et que r ne suit pas, c'est la
   chaîne qui perd l'information, pas les proposeurs. `comptes_bras` calcule déjà `informatives` mais ne s'en sert pas.
3. **Archive propre à chaque bras.** L2b montre que la part PS du bras aléatoire tombe de 0,122 en génération 1 à 0,023
   ensuite, parce que son archive grandit. Le bon proposeur passe de 48/48 à 0/96, parce que son archive est saturée dès la
   génération 1. Chaque bras est jugé contre un nul différent, et les générations 2 et 3 diluent l'écart. Exemple calculé : 6/12
   puis 0/24 au bras réel, contre 1/12 puis 1/24 au bras aléatoire. En génération 1 seule, Newcombe donne [0,051 ; 0,672] :
   discrimine. Sur les 36 cartes réunies, il donne [−0,042 ; 0,269] : l'issue gelée actuelle dirait « les proposeurs ne battent
   pas le hasard ».

La phrase gelée de Lazar (« si le bras aléatoire promeut autant que le bras réel, la chaîne ne discrimine pas ») doit rester
mot pour mot. La cause, elle, doit venir de l'oracle, et le mot « ne battent pas » doit disparaître. Remplacements T4 et T5,
décision D7, code C1.

**B4 — T2 échoue sur une course saine quand le bras recopie-mélange ne joue qu'en génération 3
(`lecture_tour_ferme_v60.py:77` ; texte, lignes 227 et 228).** Le seuil est codé en dur : 8 passes si la recopie a joué,
6 sinon. Si le bras réel ne retient rien en génération 1 mais quelque chose en génération 2, la recopie ne joue qu'en
génération 3, et T-VRAIE a 7 passes. Sonde (relevé sain, sept passes « survit ») : **« ne tient pas (T2) »**. L'étage 2
serait alors refusé à tort. Le nombre de passes attendu doit se compter sur le journal (une par génération jouée de chaque
bras).

**B5 — Un contre-calcul absent est accepté sans bruit (`lecture_tour_ferme_v60.py:52`, `:82`, `:133-134`).**

- À l'étage 1, T4 ne compte que `contre_calcul_ok is False`. Sonde : un relevé où aucune carte testée n'a de contre-calcul
  donne **« tient »**, avec T4 vrai.
- À l'étage 2, une carte de génération 1 promue, qui « survit » sans contre-calcul, donne **« Z »**.

Un défaut d'instrument se range donc dans le résultat « zéro ». C'est le repli silencieux que R5 interdit, et l'essai de la
garde 14 (« contre-calcul absent → Z », ligne 430) le fige comme correct. Une carte testée sans contre-calcul doit rendre le
relevé invalide, donc l'issue N.

**B6 — Les phrases au mentor, écrites pour être envoyées « sans autre changement » (ligne 368), induiraient en erreur
(lignes 374 à 385).**

1. « turned [x] of random proposals … into false discoveries » rapporte la FD à l'oracle. Elle sera vraisemblablement 0 ou
   1 sur 36, alors que la chaîne promeut et garde environ 6 % des propositions aléatoires (12 % en génération 1), parce que
   13 % des lois aléatoires sont informatives dans ce monde facile. Jan lirait « la chaîne rejette le hasard ». Il faut donner
   la part PS (la quantité de Lazar) et, dedans, la part sans information.
2. « [y] of copy-and-mix proposals into false discoveries » : y = 0 par construction (voir I8). La phrase le présente comme une
   résistance mesurée aux redites.
3. La réserve (a), « our proposers did not produce more surviving discoveries than a random proposer », affirme une égalité
   que la taille ne permet pas de conclure (B3).
4. La phrase N ne couvre que l'étage 1. Une issue N de l'étage 2 (arrêt, « non concluant » au-dessus de 0,20, contre-calcul en
   désaccord) dirait faussement « we did not run it on the real question ».
5. « On our real question » sans la restriction que la section 5.1 écrit elle-même (lois de scores de moniteurs sur la banque
   T0.5).

### Importants

**I1 — P4 et P6 reposent sur une lecture préalable faite dans d'autres conditions (lignes 184, 185 et 188 à 191).**

- **P4.** L2 a jugé une seule génération, archive vide, e-BH à m = 12 sans témoins (`explo_bras.py`, `juger_generation` sans
  `m_fixe`). Aux conditions du plan, L2b donne 0,056 sur trois générations (Wilson [0,042 ; 0,073]). La borne basse de P4
  (0,05, soit 2 cartes sur 36) manque alors avec une probabilité d'environ **0,40**.
- **P6.** « PS réel ≥ 0,30 » demande au moins 11 cartes sur 36. Un proposeur qui trouve la loi dès la génération 1 sature son
  archive et n'en promeut plus ensuite (L2b : 0/96). P6 est presque inatteignable par construction, même pour des proposeurs
  excellents.

Il faut écrire P4 et P6 par génération (remplacement T7) et déclarer L2b en section 10.

**I2 — La seconde confirmation de A3 est faible (ligne 330).** À l'étage 2, le test de mort compare la loi à la *marginale* de T.
Le juge, lui, l'a promue contre le *prédicteur connu* du moniteur (« connu:<moniteur> »). Une carte promue à tort, qui ne vaut
que le prédicteur connu, survit dès que ce prédicteur porte 0,02 nat sur T. « Survived a death test on held-out episodes » ne
répliquerait donc pas ce que le juge a promu. Recommandation (décision D8) : statistique de l'étage 2 = gain sur le prédicteur
connu, gelé, ajusté sur la seule partie calibrage ; le gain sur la marginale est rapporté à côté. À l'étage 1, l'oracle (ΔG)
couvre ce trou ; à l'étage 2, rien ne le couvre.

**I3 — La garde 11 et la règle de réserve laissent deux voies de fuite (lignes 287 à 292 et 310 à 312 ;
`reserve_tenue_a_l_ecart_v60.py:46-50`, `:163-165`).**

1. **Orthographe des tâches.** Les tâches de la banque publique sont des identifiants arXiv avec suffixe de version
   (`2506.01290v2`). La règle hache la chaîne exacte. Si le fichier des 288 épisodes écrit la même tâche autrement (sans
   suffixe, autre version), une tâche réservée côté T peut garder ses épisodes **publics** dans M2. Ils seraient servis en
   développement ou au juge : c'est la fuite par les épisodes publics. Il faut un contrôle de l'égalité des chaînes (refus
   sinon) et une recherche sous forme normalisée.
2. **Épisodes servis sans identifiant.** `taches_reservees_dans` ne cherche que les identifiants de tâche. Un épisode de T servi
   sans identifiant passe. Il faut aussi chercher les identifiants d'épisode de T et ses vecteurs de traits arrondis, et
   vérifier par la structure que M2 ∩ R = ∅.

**I4 — Ce qui est « jamais vu », dit trop largement (lignes 310 à 312, 376, 488 à 490).** T n'est jamais vu par un proposeur ni
par le juge de cette course : c'est exact. Mais :

- T a été lu une fois par le juge le 2 novembre, pour d'autres lois, et son issue (« I1 ») est publique ; le texte le dit en
  section 11, pas dans la phrase au mentor ;
- T est lu dans le bac par l'expérimentateur (Kimi) et par le vérificateur (Argon) : son contenu transite par ces deux
  fournisseurs ;
- les épisodes de T sont 3 par tâche, donc dépendants. Le calcul de la section 5.5 (n = 40 à 85, épisodes indépendants)
  sous-estime la survie d'une loi sans information.

Remplacements T10 et T11.

**I5 — La porte est trop lâche sur les instruments, et T4 trop fragile (`lecture_tour_ferme_v60.py:75-83`).** Sondes :

- une seule lecture d'héritage déclarée sur 6 donne T1 vrai ;
- T-MAL absent et T-ELIM jamais « éliminée » (non testé ou « non concluant ») donnent T3 vrai.

Or T-ELIM est le seul témoin qui prouve que le test de mort sait éliminer. Il doit être testé et « éliminée » dans toutes ses
passes sauf au plus une. T4 se calcule par bras, sur de petits dénominateurs : environ 12 cartes testées au bras aléatoire,
environ 5 au bras recopie. À 10 % de « non concluant » par test, le bras aléatoire seul fait manquer T4 avec une probabilité
d'environ 0,11 ; le bras recopie, à 2 « non concluant » sur 5, le fait manquer à lui seul. Proposé : ≤ 0,20 sur les trois bras
réunis et ≤ 0,40 dans chaque bras.

**I6 — Le gardien modèle est mal choisi pour des cartes-lois (lignes 134 à 137 et 486 à 487).** `aiguilleur_v53` est un
aiguilleur de *fiches d'idées*, avec trois classes (niveau méthode, à corriger, concret). Ses seuils S10 et S11 ont été étalonnés
sur des fiches. Il porte une garde qui arrête le rôle de Kimi (`DebordementKimi`, seuil S12) et qui n'est pas dans la liste
d'arrêt. Une carte-loi chiffrée peut être lue comme « concret ». Il coûte environ 138 des 240 appels de l'étage 1 (≈ 3,3 USD
sur 6,6), et il est la seule source d'asymétrie entre bras qu'il faille auditer après coup (S5). Recommandation (décision D9) :
gardien mécanique seul, décisif, pour les trois bras ; l'aiguilleur hors de portée, dit en section 11.

**I7 — Devis : l'hypothèse dominante n'est pas sourcée (lignes 498 à 500 et 513 à 518).** « 2 sessions d'expérimentateur par
carte testée » est le comportement de l'expérimentateur *scripté* du mode à blanc ; Kimi peut en prendre jusqu'à 12. Recalcul
pour l'étage 1, avec ≈ 32 cartes testées et 144 appels simples à 0,0237 USD :

| tours d'expérimentateur par carte testée | prix d'un tour | coût de l'étage 1 |
|---|---|---|
| 2 (hypothèse du texte) | 0,04 USD | 6,6 USD |
| 4 | 0,06 USD | ≈ 11,7 USD |
| 6 | 0,06 USD | ≈ 15,5 USD |

À 6 tours, le plafond de 12 USD arrête la course, et l'issue devient N pour une raison de coût. L'arithmétique du tableau du
texte est juste (240 + 60 appels ; 6,6 + 1,5 à 2 USD). Voir C7.

**I8 — Le bras recopie-mélange ne peut pas échouer (ligne 93 ; `proposeurs_references_v59.py:78-91`).** Ses quatre formes
(copie, mélange avec l'uniforme, tempérée-inclinée, mélange de deux retenues) sont toutes des membres du nul v8. W ≤ 1 au juge,
ΔG ≤ 0 à l'oracle : FD = 0 par construction, et P5 n'est pas une prédiction. Le bras vérifie que l'archive du bras réel entre bien
au nul de ses cartes. Il ne mesure pas le taux de fausses découvertes des recombinaisons que le nul ne couvre pas (si/sinon par
sous-population, produits de deux retenues), alors que c'est là qu'est le risque. Dire cela en portée (remplacement T12), ou
ajouter ces formes. Dans ce cas, la clause « FD par construction » contredirait l'oracle : une recombinaison si/sinon réellement
meilleure aurait ΔG ≥ g₀, et elle devrait se classer à l'oracle comme au bras aléatoire.

**I9 — Audit de symétrie (R4) asymétrique (lignes 395 à 411).** S1 (trop beau) prévoit un audit en cinq points. S2 (trop laid)
a un audit plus court. R4 exige « le même audit ». La recherche des poids de L* dans les contextes servis (S1, point 3) doit
être faite à chaque course : L* est dans un fichier public (`exemples/temoins-pari-demo-v1.json`). Il faut aussi écrire qu'un
S1 ou un S3 déclenché sans défaut trouvé attache une réserve (« trop beau = réserve »).

### Mineurs

1. **Phrase cassée** (lignes 41 et 42) : « par l'orchestrateur, un\n  la porte entre étages ».
2. **D1** est décidée par Lazar (`GO-2026-11-02-06`, `registres/go.md`, ligne 52) : le titre de la section 2 (ligne 47) et
   la section 14 doivent le dire.
3. **Redondance** : « G ≥ g₀ et ΔG ≥ g₀ » (ligne 91). ΔG ≥ g₀ suffit, puisque G_arch ≥ 0.
4. **Témoins dans l'e-BH** (lignes 141 et 142) : le texte ne dit pas si T-ELIM (≈ L*) pèse sur k*. Mesuré sans effet ici (L2b),
   mais à écrire : tous les témoins hors famille, comme le témoin vrai dans `cycle.appliquer_multiplicite:739-764`.
5. **Ordre des bras** dans une génération : il n'est pas écrit. Le bras recopie doit jouer après le bras réel (D4).
6. **Manifeste R9** (ligne 463) : ajouter le commit, les versions (Python, numpy ≥ 1.25, bwrap) et l'ordre des bras.
7. **Graine publique.** E sera public dès la poussée du texte scellé, donc la tranche se calcule d'avance. C'est sans effet
   tant que les proposeurs n'ont ni outil ni code ; à écrire.
8. **P8** n'a pas de clause « ouverte » (ligne 195).
9. **Calibrage de l'étage 2** : retirer les tâches réservées de la partie calibrage change le prédicteur connu. Écrire qu'il
   est réajusté sur la calibrage réduite et gelé avant la course (ligne 276).
10. **Doublons dans une génération.** Kimi et Argon peuvent proposer deux fois la même loi ; deux VD comptent alors double au
    bras réel. Rapporter aussi les découvertes distinctes : deux VD d'une même génération à moins de 0,05 nat de divergence
    comptent pour une, mesure sans critère.

## 2. Remplacements (couples exacts ; chaque chaîne « avant » figure une seule fois dans le brouillon 1)

**T1** (lignes 41 et 42)
- avant : `un contre-calcul de la statistique par l'orchestrateur, un\n  la porte entre étages.`
- après : `un contre-calcul de la statistique par l'orchestrateur, la porte entre étages.`

**T2** (ligne 47)
- avant : `décision D1, à valider par Lazar)`
- après : `décision D1, prise par Lazar : GO-2026-11-02-06, registres/go.md, 2 novembre 2026)`

**T3** (lignes 227 et 228)
- avant : `(8 passes prévues ; 6 si le bras\n   recopie-mélange ne joue pas), « éliminée » dans aucune.`
- après : `(une passe par génération jouée de chaque bras, nombre compté sur le journal : 8 si le bras recopie-mélange joue en\n   générations 2 et 3, 7 s'il ne joue qu'en génération 3, 6 s'il ne joue pas), « éliminée » dans aucune.`

**T3b** (lignes 229 et 230)
- avant : `T-ELIM jamais « survit » ; T-MAL refusé au gardien dans toutes ses passes.`
- après : `T-ELIM testé et « éliminée » dans toutes ses passes sauf au plus une, jamais « survit » ; T-MAL présent et refusé au gardien dans chaque génération jouée de chaque bras.`

**T3c** (lignes 231 et 232)
- avant : `dans chaque bras, « non concluant » / testées ≤ **0,20** (cartes et témoins) ; aucun désaccord du\n   contre-calcul.`
- après : `« non concluant » / testées ≤ **0,20** sur les trois bras réunis et ≤ 0,40 dans chaque bras (cartes et témoins) ;\n   chaque carte testée porte un contre-calcul (absent : relevé invalide, issue N) ; aucun désaccord du contre-calcul.`

**T3d** (lignes 225 et 226)
- avant : `chaque génération g ≥ 2 a lu le bilan\n   de g−1 à l'empreinte consignée (journal)`
- après : `chaque génération g ≥ 2 de chaque bras qui joue a lu le bilan\n   de g−1 à l'empreinte consignée (journal ; nombre de lectures égal au nombre attendu)`

**T4** (lignes 248 à 251)
- avant : `l'oracle sépare deux causes d'un r_réel trop bas.`
- après : `l'oracle sépare les causes d'un écart non positif, par la part de cartes informatives et nouvelles à l'oracle (G ≥ g₀ et ΔG ≥ g₀, mesurée sur toutes les cartes jugées, promues ou non) : si sa borne basse de Newcombe réel − aléatoire est > 0, les proposeurs produisent de l'information que la chaîne ne retient pas (« sensibilité de la chaîne insuffisante ») ; sinon « on ne peut pas dire, à cette taille, que les vrais proposeurs battent le hasard dans ce monde ». Puissance dite : à 36 contre 36, un écart vrai de 0,10 sur r est déclaré « discrimine » avec une probabilité d'environ 0,2, un écart de 0,20 avec environ 0,6.`

**T5** (lignes 253 et 254)
- avant : `T5 tient et borne ≤ 0 → « la chaîne écarte les lois sans\n   information, mais les vrais proposeurs ne battent pas le hasard dans ce monde » (réserve majeure pour A3, point 2).`
- après : `T5 tient et borne ≤ 0 → « le bras aléatoire promeut autant que le\n   bras réel à cette taille : la chaîne ne distingue pas les vrais proposeurs du hasard dans ce monde » (phrase de Lazar ; réserve majeure pour A3, point 2), suivie de la cause lue au point 3 ; la comparaison de la seule génération 1 est rapportée à côté, sans décider.`

**T6** (lignes 141 et 142)
- avant : `les témoins\n  comptant dans m comme dans `cycle.appliquer_multiplicite``
- après : `les témoins\n  comptant dans m mais lus hors famille (au seuil m/α, sans peser sur k*, comme le témoin vrai de `cycle.appliquer_multiplicite`)`

**T7** (lignes 184 et 185, P4)
- avant : `(L2 : 150 sur 1 200 = 0,125, Wilson\n  [0,107 ; 0,145])`
- après : `(L2, génération 1 seule, archive vide, m = 12 sans témoins : 0,125 ; aux conditions du plan, lecture L2b du contre-lecteur, trois générations, archive propre : 48/864 = 0,056, Wilson [0,042 ; 0,073], dont 0,122 en génération 1 et 0,023 ensuite) ; P4 se lit : génération 1 entre 1 et 4 cartes sur 12, trois générations entre 1 et 5 cartes sur 36`

  Il faut alors corriger aussi `entre 0,05 et 0,25` dans la même puce : remplacer `part PS du bras aléatoire **entre 0,05 et 0,25**` par `part PS du bras aléatoire **entre 1 et 5 cartes sur 36**`.

**T8** (ligne 188, P6)
- avant : `part PS du bras réel **≥ 0,30** et part VD **≥ 0,25** sur ses cartes`
- après : `part PS du bras réel **≥ 0,30 en génération 1** (au moins 4 cartes sur 12) et part VD ≥ 0,25 en génération 1 ; sur trois générations, rapportée sans seuil (un bras qui trouve la loi en génération 1 sature son archive : L2b, 0/96 ensuite)`

**T9** (ligne 330, décision D8)
- avant : `gain moyen du log-score de la loi sur la marginale empirique de T (comptes + 0,5)`
- après : `gain moyen du log-score de la loi sur le prédicteur connu du moniteur (membre « connu:<moniteur> », ajusté sur la seule partie calibrage, gelé avant la course ; le gain sur la marginale empirique de T, comptes + 0,5, est rapporté à côté)`

**T10** (lignes 310 à 312)
- avant : `vérifie l'empreinte de T avant de le monter et cherche, dans chaque contexte servi, chaque identifiant de tâche réservée\n  (garde 11, section 7).`
- après : `vérifie l'empreinte de T avant de le monter et cherche, dans chaque contexte servi et dans M2, chaque tâche réservée sous sa forme normalisée (sans suffixe de version), chaque identifiant d'épisode de T et chaque vecteur de traits de T arrondi à 4 décimales (garde 11, section 7) ; la session-depot vérifie que les tâches communes à E0 et à la banque publique y sont écrites à l'identique (refus sinon). T est lu, dans le bac, par l'expérimentateur (Kimi) et le vérificateur (Argon) de l'étage 2 : c'est la seule lecture de T par un modèle.`

**T11** (ligne 351)
- avant : `(approximation normale de la moyenne, n = 40 à 85).`
- après : `(approximation normale de la moyenne, n = 40 à 85, épisodes SUPPOSÉS indépendants ; ils ne le sont pas, 3 par tâche : à corrélation ρ entre épisodes d'une même tâche, n effectif ≈ n / (1 + 2ρ), et la survie d'une loi sans information monte).`

**T12** (ligne 487, portée)
- avant : `ses refus sont mesurés, pas interprétés.`
- après : `ses refus sont mesurés, pas interprétés. Le bras recopie-mélange ne propose que des formes couvertes par le nul v8 : sa FD est nulle par construction ; il vérifie que l'archive du bras réel entre au nul, il ne mesure pas les recombinaisons non couvertes (si/sinon, produits).`

  Si D9 est accepté, remplacer plutôt toute la phrase sur le gardien modèle par : `Le gardien est la couche mécanique seule, la même pour les trois bras ; l'aiguilleur v53 (fiches d'idées) est hors de portée.`

**T13** (lignes 374 et 375, phrase P)
- avant : `turned [x] (Wilson 95 % [a, b])\n  of random proposals and [y] of copy-and-mix proposals into false discoveries.`
- après : `promoted and kept [r] (Wilson 95 % [a, b])\n  of random proposals, [x] of which carried no new information by an oracle that knows the planted law; copy-and-mix proposals, restricted to forms our judge's null covers by construction, gave [y].`

**T14** (lignes 377 et 378, réserve (a))
- avant : `our proposers did not produce more surviving discoveries than a random\n  proposer, so this promotion cannot be credited to their judgement.`
- après : `we could not show, at 36 proposals per arm, that our proposers produce more surviving\n  discoveries than a random proposer ([cause]), so this promotion cannot yet be credited to their judgement.`

**T15** (ligne 372)
- avant : `On our real question, [n] hypothesis(es) written`
- après : `On our real question, restricted to laws of monitor scores that our episode bank can test, [n] hypothesis(es) written`

  Et lignes 373 et 374 :
  - avant : `held-out episodes reserved by\n  hash before the run.`
  - après : `held-out episodes reserved by\n  hash before the run (fresh-seed episodes of the same tasks, never shown to a proposer or to this run's judge; read once before by our judge for other laws).`

**T16** (ligne 382, phrase Z)
- avant : `turned [x] of\n  random proposals into false discoveries;`
- après : `promoted and kept [r] of\n  random proposals, [x] of them without new information by the oracle;`

**T17** (ligne 385, phrase N)
- avant : `« The closed loop did not pass its own planted-world gate ([criterion]); we did not run it on the real question. »`
- après : `N1 (étage 1) : « The closed loop did not pass its own planted-world gate ([criterion]); we did not run it on the real question. » N2 (étage 2) : « We ran the closed loop on the real question, but the run is not judgeable ([stop / inconclusive share above 0.20 / recomputation disagreement]); we report no outcome for the real question. »`

**T18** (lignes 401 et 402, audit S2)
- avant : `Audit : rejouer chaque carte en cause`
- après : `Audit : les cinq points de S1, puis : rejouer chaque carte en cause`

  Et en tête de la section 6, après la phrase d'introduction, ajouter : `Le point (3) de S1 (poids de L* et lignes de tranche dans les contextes servis) est fait à chaque course, déclenchée ou non. S1 ou S3 déclenché sans défaut trouvé : l'issue porte la réserve « trop beau, audité sans défaut » (R4).`

## 3. Changements de code nécessaires

- **C1** — `pole/lecture_tour_ferme_v60.py`, `lire_etage1` :
  - T2 compare au nombre de passes attendu, lu dans le relevé (générations jouées par bras), pas à 8 ou 6 codés en dur ;
  - T1 exige une lecture par génération g ≥ 2 de chaque bras qui joue ;
  - T3 exige T-ELIM testé et « éliminée » sauf au plus une passe, et T-MAL présent dans chaque génération jouée ;
  - T4 se calcule sur les trois bras réunis (≤ 0,20) et par bras (≤ 0,40) ;
  - toute carte testée dont `contre_calcul_ok` n'est pas un booléen lève `ReleveInvalide` ;
  - A4 : ajouter Newcombe sur `informatives` (réel − aléatoire), la cause lue (sensibilité ou proposeurs), le libellé de T5,
    et Newcombe de la génération 1 seule, rapporté sans décider ;
  - dénominateur : rapporter la part sur cartes proposées à côté de la part sur cartes jugées (sans objet si D9 est accepté).
- **C2** — `lire_etage2` :
  - une carte testée sans contre-calcul rend N, pas Z ;
  - le motif de N distingue N1 (étage 1) et N2 (étage 2) ;
  - le libellé de la réserve (a) reprend la cause de A4.
- **C3** — `essais/mutations_v60.py` et essais. Inverser l'essai « contre-calcul absent → Z », qui fige B5. Mutations à ajouter :
  « T2 attend 8 passes quand la recopie joue une génération », « contre-calcul absent accepté », « T-ELIM jamais testé
  accepté », « lectures d'héritage manquantes acceptées », « cause de A4 ignorée ».
- **C4** — `pole/reserve_tenue_a_l_ecart_v60.py` :
  - contrôle de l'orthographe des tâches entre E0 et la banque publique ;
  - `taches_reservees_dans` sur forme normalisée ;
  - recherche des identifiants d'épisode et des vecteurs de traits de T ;
  - vérification par la structure que M2 ∩ R = ∅, épisodes publics compris.
- **C5** — `pole/tour_ferme_v60.py` (à écrire) :
  - témoins hors famille dans l'e-BH ;
  - si D7 est accepté : cartes aléatoires jugées contre l'archive du bras réel, jamais versées à une archive ;
  - ordre des bras dans une génération : réel, puis recopie, puis aléatoire ;
  - test de mort de l'étage 2 contre le prédicteur connu (D8) ;
  - gardien mécanique seul (D9), sinon `DebordementKimi` inscrit à la liste d'arrêt et essayé sur un cas sain et sur un
    artefact ;
  - relevé portant les passes attendues ;
  - manifeste avec commit et versions.
- **C6** — Lecture L2b aux conditions exactes du plan, une fois C5 écrit : déclarée en section 10, avec le script et
  l'empreinte de la sortie ; les seuils P4 et P6 relus sur elle.
- **C7** — Avant scellement : relever, sur les journaux scellés du 27 octobre ou du 1er novembre, le nombre réel de tours
  d'expérimentateur par carte et leur coût, et le recopier en section 12. Sans ce relevé, mettre le plafond de l'étage 1 à
  15 USD ; si D9 est accepté, 12 USD suffisent (environ 3,3 USD de moins).

## 4. Réponses aux six questions du rapport de rédaction (section 7)

1. **La définition de la fausse découverte** est la bonne pour l'erreur par carte. Elle sépare les 13 % de lois aléatoires
   informatives (VD) des redites de l'archive (FD). Elle range correctement la loi plantée entrée à l'archive : toute PS
   ultérieure du bras est une FD, que seul le juge peut éviter. Elle est calculable sans fuite : l'oracle ne sert qu'à l'audit,
   ses instances viennent de la graine scellée, et l'archive se lit sur le bilan scellé. En revanche, la lecture A4 « écart nul
   et T5 tenu → les proposeurs ne battent pas le hasard » est **fausse** (B3).
2. **La porte T1 à T5.**
   - T2, qui tolère une passe perdue, est raisonnable, mais son décompte est faux (B4).
   - T5, qui tolère une FD sur 36, est juste : environ 0,09 FD attendue, 1/864 en L2b.
   - T1 et T3 sont trop lâches (I5) ; T4 est trop fragile par bras (I5).
3. **La réserve** (un tiers des tâches, T privé, génération 1 seule décisive, T relue en génération 2) est bien la plus petite
   réserve honnête sans données neuves. Couper T en deux ramènerait 20 à 42 épisodes par moniteur au test décisif : non. Il
   faut I3, I4 et T10.
4. **Le bras recopie nourri par l'archive du bras réel** sera « non mesurable » chaque fois que le bras réel ne retient rien en
   générations 1 et 2. Ce n'est pas grave, car il ne peut pas échouer de toute façon (I8). Garder D4 et le dire en portée.
5. **L'aiguilleur v53** n'est pas un gardien acceptable pour des cartes-lois : garde d'arrêt cachée, étalonnage sur des fiches,
   moitié du budget, asymétrie possible entre bras. Couche mécanique seule pour les trois bras (D9).
6. **Le devis** est juste en arithmétique, mais son hypothèse dominante (2 tours par carte testée) est celle de
   l'expérimentateur scripté. À relever avant scellement (I7, C7).

## 5. Décisions D1 à D6 (et trois de plus) : recommandations

- **D1** : déjà décidée (`GO-2026-11-02-06`). Le texte doit la citer comme prise, pas « à valider ».
- **D2** : oui, avec deux ajouts. (a) La part PS de chaque bras de référence, c'est-à-dire la définition de Lazar (« taux de
  fausses découvertes de la chaîne »), est rapportée en premier sous son nom, et dans les phrases au mentor (T13, T16).
  (b) La FD à l'oracle reste la mesure qui décide de T5. Confiance : bonne.
- **D3** : oui. L3 montre qu'autrement les générations 2 et 3 sont muettes.
- **D4** : oui, avec la portée de I8 (remplacement T12).
- **D5** : oui, T entier, génération 1 seule décisive, et non T coupé en deux, à condition d'accepter D8.
- **D6** : bras aléatoire de contrôle à l'étage 2 : oui (≈ 0,7 USD ; il porte la réserve « le hasard passe aussi »). Seconde
  réplique du bras aléatoire de l'étage 1 : non. La largeur de Newcombe dépend surtout des 36 cartes du bras réel, et les
  2,5 USD servent mieux au plafond (I7).
- **D7 (nouvelle)** — contre quoi juger le bras aléatoire. Recommandé : contre l'archive du bras réel de la même génération,
  comme le bras recopie ; ses retenues ne vont dans aucune archive.
  - Avantage : même nul pour les cartes réelles et aléatoires à chaque génération, et la comparaison A4 cesse de dépendre de
    l'archive que chaque bras s'est faite.
  - Inconvénient : le bras aléatoire n'a plus de boucle propre. Il n'en lisait de toute façon rien (vue « jamais lue »).
  - Confiance : moyenne. L'autre option garde l'archive propre et lit A4 en génération 1 seule : même nul, mais 12 cartes
    contre 12.
- **D8 (nouvelle)** — statistique du test de mort de l'étage 2 contre le prédicteur connu du moniteur. Recommandé : oui, sinon
  « survit » ne réplique pas ce que le juge a promu (I2). Confiance : bonne.
- **D9 (nouvelle)** — gardien. Recommandé : couche mécanique seule pour les trois bras (I6). Confiance : bonne. L'alternative
  qui garde l'aiguilleur exige `DebordementKimi` à la liste d'arrêt, son essai sur un cas sain et sur un artefact, et un plafond
  plus haut.

## 6. Ce que le brouillon 2 doit contenir pour être scellable

1. Les remplacements T1 à T18 (ou leur équivalent), et les décisions D2 à D9 de Lazar.
2. Le code C1 à C5 écrit, essayé (cas sain et artefact pour chaque garde, R5), passé au banc, et rejoué à blanc de bout en bout.
3. L2b (C6) et le relevé de coût (C7) déclarés.
4. Les cases de la section 5.2 remplies.
5. Une seconde contre-lecture R2, sur le texte et sur le code.

Rien de ce qui précède ne demande d'appel de modèle ni de dépense.
