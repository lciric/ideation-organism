# Préenregistrement de lecture — lot T0.5 à graines neuves, juge à plan pleine épreuve (v1)

- Auteur : lignée conv-audit (rédaction par un sous-agent ; contre-lecture par un agent neuf, section 17).
- Date de rédaction : 1er novembre 2026, 20:50–22:00 UTC. Scellement visé : avant le 2 novembre, 02:00 UTC.
- **Aucune notation du lot neuf n'a été lue par qui que ce soit** au moment de la rédaction : le lot tourne depuis
  21:16–21:21 UTC (fin estimée 02:00–03:00 UTC) ; aucun fichier du lot n'existait sur le disque de la rédaction, et aucun
  compte tiré des résumés des courses n'a été montré à la rédaction.
- Code d'analyse (dépôt public, fichiers neufs ; aucun commit à la rédaction : les empreintes font foi, section 15) :
  `demonstrations/lecture_t05_graines_neuves_v1.py`, `pole/juge_plan_plein_v1.py` ; essais
  `essais/test_lecture_t05_graines_neuves_v1.py` ; annexes `demonstrations/annexes_lecture_t05_v1/constats_calibrage_v1.py`
  et `puissance_par_paire_v1.py`.
- Documents qui font foi :
  - courbe de puissance publiée : `resultats/puissance-juge-banque-v1-2026-11-01/puissance-juge-banque-v1.json`
    (sha256 `060216fef755b77ecc488195b6eba56d52ecdd3c530855c18cc8610cd17b4c55`), son rendu `.md` (réserves) et la
    traduction force → information `force-en-clair-v1.txt` (sha256 `7419358857c824e0…`) ;
  - lectures L1–L4 : `demonstrations/demo_couche1_v7.py` (docstring l. 12-17, calcul l. 120-137) ; E1–E4 :
    `demonstrations/demo_couche1_proposeur_v7.py` (l. 12-17) ;
  - calibrage : banque `banque-e2.json` (288 épisodes, construite par `exemples/construire_banque_t05_v3.py` pour la
    lecture exploratoire v2 de la couche 1 bis), sha256 `f59018fb047af289ba1f466430fa9c577d6a0b6d4843a51831b19bd3c197b22e`
    (fichier non public ; seule son empreinte est citée) ;
  - lot (production seule, aucune lecture) : kit scellé au commit `f40c8aa9b789164f22c5cd2d883a77e20e68e04f` du dépôt de
    travail ; fiches de production scellées `prereg/T0.5-graines-neuves-{a,b,c,d}-v1.md` (A `e14946e3…`, B `1baf41cf…`,
    C `4af4ca08…`, D `c24db30e…`) ; table des identifiants `table-identifiants-graines-neuves-v1.json` (sha256
    `76375391f4860f71271ae9239dbc1afa6cdba06eb830dda035762705cc0a772f` : 96 lignes « tâche d'origine → identifiant
    `<origine>-g2` → lot »), dérivée de `origines-taches-graines-neuves-v2.json` (`ea231aab…`) ; chaîne du pilote
    inchangée : invite b0 (système H.3 `52ab1e255360cf80…`, grille H.4 `cb103166b1c21f8c…`, index des invites
    `adb4b8bca7788baf…`), `juges.py` `52610b0a…` et `rubrique.py` `da2f7a1e…` au commit gelé `2660b07`, configuration
    `T0.5-pilote-config-v1.json` `6979a00e…` (empreinte canonique `db3ad3ce…`).

## 0. En bref

Le lot de cette nuit (les 96 tâches déjà courues, 3 épisodes par tâche, graines neuves, identifiants `<origine>-g2`,
quatre courses a, b, c, d de 30, 30, 30 et 6 tâches) est une **épreuve neuve lue une seule fois**. Calibrage et définition
des témoins se font sur les 288 épisodes déjà courus. Le juge lit l'épreuve avec un **plan qui prend toute l'épreuve** (bras
décisif) et avec le **plan gelé de 120** (bras de comparaison). Deux constats préalables, tirés du calibrage et du kit :
(i) **la règle de L3 ne déclare aucun témoin vrai réel** (plus grand |ρ| = 0,248 < 0,35) : les dents du juge se mesurent
sur des **témoins plantés** sur les traits réels des épisodes neufs, et la question de fond (« les notes dépendent-elles
des traits ? ») sur la **loi connue** de chaque moniteur, jugée contre la bibliothèque aveugle ; (ii) les épisodes `e2`
ne sont notés que si l'échéance de 15 000 s le permet (notations « descriptives ») : **192 à 288 épisodes d'épreuve**,
192 à 210 le plus probable. Prédiction principale : juge valide (aucun témoin faux promu), denté (témoins plantés de force
0,5 et 0,8 promus sous le plan plein), **aucune loi réelle promue** ; d'où une borne chiffrée, moniteur par moniteur, sur
l'information que les traits portent sur les notes.

## 1. Rôle du lot : choix et options rejetées

**Choix : épreuve neuve lue une seule fois.**
- Calibrage = les 288 épisodes déjà courus (60 tâches du pilote et 36 de la couche 1 bis, trois épisodes chacune,
  notes de première passe des juges 8B et 3B, grille H.4), tels que `banque-e2.json` les porte : normalisation des traits,
  points de coupe des 13 moniteurs réels, prédicteur connu de chaque moniteur, témoins réels.
- Épreuve = les épisodes à graines neuves des mêmes 96 tâches (identifiant `<origine>-g2`), lus une fois par le script,
  après scellement ; rien de l'épreuve ne sert à définir une fiche, un seuil, une coupe ou une normalisation.

**Option rejetée : banque élargie** (fusionner anciens et neufs en 576 épisodes, puis repartager par tâche). Raisons :
(i) les 288 épisodes anciens ont été lus plusieurs fois (lectures exploratoires de la couche 1 bis, démonstrations,
courbe de puissance) : toute épreuve qui en contient est exposée ; (ii) les épisodes neufs sont la seule donnée fraîche,
il faut la garder entière pour l'épreuve ; (iii) un repartage par tâche mettrait anciens et neufs d'une même tâche du même
côté et diviserait l'épreuve par deux sans rien gagner en indépendance, puisque toutes les tâches ont déjà été vues.
**Autre option écartée** : calibrage sur les épisodes anciens de 48 tâches, épreuve sur les épisodes neufs des 48 autres :
épreuve réduite de moitié (plan plein, force 0,5 : ≈ 0,73 à N = 144 contre ≈ 0,96 à N = 288, courbe publiée), et la
généralisation à des tâches « non vues » reste impossible (les 96 tâches ont toutes été lues).

**Conséquence assumée** : calibrage et épreuve partagent les mêmes 96 tâches (pas les mêmes épisodes). L'épreuve mesure
la tenue sur **graines neuves des mêmes tâches**, pas sur des tâches neuves ; un effet de tâche (difficulté d'un article)
commun aux deux côtés peut faire tenir une loi. Les épisodes d'une même tâche sont corrélés : la puissance se compte en
tâches (96), et tout intervalle se calcule par rééchantillonnage **par tâche**.

## 2. Constats du calibrage (288 épisodes déjà courus ; aucune donnée du lot)

Calculés par `demonstrations/annexes_lecture_t05_v1/constats_calibrage_v1.py` (sha256 `e234286d8decf393…`) sur
`banque-e2.json` (sha256 `f59018fb…`), sortie de la rédaction sha256 `d24f8bedbbfe203b…` ; le script de lecture recalcule la
table de rangs et s'arrête (A7) si elle diffère.

1. **Règle de L3** (`exemples/proposeur_scripte_banque_v1.py`, inchangée : corrélation de Spearman de chaque trait réel
   avec l'issue, sur le calibrage ; témoin vrai si |ρ| ≥ 0,35) : **aucun témoin vrai** sur les 13 moniteurs × 3 traits.
   Plus grand |ρ| = **0,248** (3B:BALANCE et l'écart-type des jetons par action) ; les cinq couples qui étaient témoins
   vrais dans la banque v2 (|ρ| de 0,38 à 0,52 sur ses 40 épisodes de calibrage) valent ici 0,146, −0,046, 0,121, 0,075
   et 0,110 : **les « témoins vrais » de la banque v2 ne tiennent pas sur 288 épisodes** (effet de petit échantillon).
   Témoins faux : 13 (un par moniteur, loi monotone sur le trait de bruit).
2. **Couverture** (instances de première passe portant une note entière ; sur les 192 épisodes e0–e1 / sur les 96 e2) :
   3B:BALANCE 0,505 / 0,281 ; 3B:COHERENCE 0,891 / 0,927 ; 3B:NOVELTY 0,844 / 0,802 ; 3B:REDUNDANCY_PENALTY 0,802 /
   0,802 ; 3B:RESULT_REASONING 0,432 / 0,406 ; 3B:RIGOR 0,708 / 0,688 ; 8B:BALANCE 0,589 / 0,552 ; 8B:COHERENCE 0,682 /
   0,625 ; 8B:IRRELEVANCE_PENALTY 0,714 / 0,677 ; 8B:NOVELTY 0,646 / 0,573 ; 8B:REDUNDANCY_PENALTY 0,698 / 0,625 ;
   8B:RESULT_REASONING 0,583 / 0,542 ; 8B:RIGOR 0,609 / 0,562. Moniteurs à 3 issues : 3B:COHERENCE, 3B:NOVELTY,
   8B:COHERENCE, 8B:NOVELTY, 8B:RIGOR ; les huit autres à 2 issues.
3. **Information de la loi connue hors échantillon** (gain moyen de score logarithmique contre la marginale
   d'ajustement, nat par épisode) : par tâche (deux plis, dix répétitions) **négative pour les 13 moniteurs** (de −0,0075 à
   −0,0629) ; dans les mêmes tâches, un épisode tenu à l'écart (situation proche de l'épreuve) : au plus **+0,0085**
   (3B:RIGOR), +0,0030 (8B:BALANCE), +0,0011 (3B:BALANCE), les dix autres ≤ 0. Sur le calibrage, les traits ne portent
   donc presque aucune information sur les notes.

## 3. Hypothèses

- **H1 (validité)** : sur des notes réelles neuves, le juge — plan plein comme plan gelé, monde informé comme aveugle — ne
  promeut aucun témoin faux sous la règle e-BH.
- **H2 (dents)** : sur les traits réels des épisodes neufs, le juge à plan plein promeut une loi correctement spécifiée de
  force ≥ 0,5 (puissance prédite 0,85 à 0,96 selon N, section 7) ; le gain du plan plein sur le plan gelé est mesuré (son
  signe est garanti par construction, section 4).
- **H3 (lois réelles)** : la dépendance des notes aux trois traits, apprise sur le calibrage (loi connue), ne bat pas la
  bibliothèque aveugle sur l'épreuve ; aucune loi réelle n'est promue.
- Hypothèses de travail : épisodes et notes du lot produits par la même chaîne que le calibrage (agent 8B, juges 8B et 3B,
  grille H.4, invite b0, température 1,0 ; fiches de production citées en tête) ; trait de bruit indépendant de tout par
  construction (tiré par graine).

## 4. Configuration gelée

**Juge** (`pole/juge_plan_plein_v1.py`) : sélection par pari ; juge v1 **sans urne** (ordre secret) ; nul des filles v2 ;
**nul v8** (`pole/nul_v8.py` : `nul_archive=True`, `nul_archive_ajuste=True`, `nul_filles="v2"`, `selection="pari"`,
imposés par `configuration_nul_v8`, qui refuse tout réglage contraire) ; règle de multiplicité **e-BH**, α = 0,05 ;
témoins jugés sans agents ; politique de redite « refus » ; `taille_plan_filles` 120 ; `instants_filles` 6 ;
`part_calibrage` 12 ; graine du juge **20261027** (celle de la courbe et des démonstrations).
- **Bras « plein » (décisif)** : `taille_plan` = nombre d'instances d'épreuve de la banque ; le plan de chaque fiche est
  son réservoir entier (garde `verifier_plan_plein` : un plan plus court arrête, aucun repli) ; une `taille_plan` plus
  petite que l'épreuve est refusée (`PlanPleinRefuse`).
- **Bras « gelé » (comparaison)** : `taille_plan` = 120 (le juge de la courbe). Pour un moniteur à moins de 120 instances
  jugées, les deux bras ont le même plan.
- **Invariant du préfixe** (propriété du code, vérifiée à chaque lecture) : les deux bras mélangent le réservoir avec la
  même graine (graine du juge et empreinte de la fiche) et le trient de même par divergence ; le plan gelé est donc
  exactement les 120 premières instances du plan plein, dans le même ordre, et la richesse est calculée dans l'ordre du
  plan (sur une banque, l'ordre secret ne change pas l'ordre d'évaluation). Les trajectoires de log W coïncident sur les
  120 premiers instants : en lecture continue, log W max (plein) ≥ log W max (gelé), et tout témoin vrai (hors famille,
  seuil fixe) promu sous le plan gelé l'est sous le plan plein. **« Plein au moins autant que gelé » n'est donc pas une
  prédiction mais un invariant** ; la comparaison des bras mesure le gain du plan plein, jamais son signe. Pour une fiche
  en famille, la e-valeur finale diffère d'un bras à l'autre : son verdict e-BH peut changer dans les deux sens.

**Nul.** Génération unique, archive vide, fiches sans parents : le nul v8 s'y réduit à la bibliothèque aveugle du juge v1
sans urne (marginale au maximum de vraisemblance, uniforme, moyennes glissantes) plus, dans le monde **informé**, le membre
« connu » du moniteur (régression multinomiale à crête ajustée sur le calibrage). La garde `verifier_archive_vide` le
vérifie pour chaque fiche. **Cette lecture ne mesure donc rien du nul v8 lui-même** ; elle l'impose pour que le juge lu
soit celui d'aujourd'hui. Lecture continue (log W maximal sur les instants du plan ; aucun membre ajusté, donc pas de
lecture aux instants fixés) ; chemin d'une fiche : celui de `puissance_juge_banque_v1.juger_temoin` (gel, plan par
divergence, issues déposées par le noyau, `selection_pari.evaluer`).

**Deux familles**, chacune lue par la règle e-BH de production (`cycle.appliquer_multiplicite`, m fixé avant toute issue
= nombre de fiches non « vraies » de la famille ; témoins vrais hors famille, au seuil log(m/α)) :
- **Famille T (décisive)**, monde **informé** : 13 témoins faux réels, 0 témoin vrai réel (section 2), 3 témoins vrais
  plantés, 6 témoins faux plantés. **m_T = 19** ; seuil e-BH log(19/0,05) = **5,94**.
- **Famille R (lois réelles ; préenregistrée, non décisive pour le juge)**, monde **aveugle** : 13 lois connues (une par
  moniteur réel) et les 13 témoins faux réels. **m_R = 26** ; seuil log(26/0,05) = **6,25**. Monde aveugle parce que la
  loi connue *est* le membre informé : sous le monde informé, elle ne pourrait jamais gagner.

Quatre configurations jugent donc la même épreuve : T-plein, T-gelé, R-plein, R-gelé. Ce qui est décisif dans chacune est
fixé ici (section 6) ; aucune « meilleure des quatre » n'est retenue après coup.

## 5. Fiches jugées (toutes fixées avant l'épreuve ; empreintes écrites dans la sortie)

- **Témoins réels** : `proposeur_scripte_banque_v1.proposer` appliqué au calibrage seul, inchangé (loi monotone :
  poids 0,8 × (rang de classe − milieu) sur le trait, biais = logarithme des fréquences de calibrage). 13 faux (trait de
  bruit), 0 vrai. Seuls les champs descriptifs `espace_instances.banque` et `sous_populations` sont réécrits.
- **Témoins plantés** (contrôle des dents, au régime réel des traits) : `construire_banque_t05_v3.planter` sur la banque
  complète (calibrage + épreuve), 3 moniteurs plantés de forces **0,3, 0,5, 0,8** (dans cet ordre : `plante:0`, `:1`,
  `:2` ; paire de traits et signe tirés par la graine de plantation), issues tirées pour chaque instance des deux côtés ;
  pour chacun, comme la courbe : `TVP` (vrai, sa loi exacte), `TFP` (faux, même forme sur le trait de bruit), `TFN` (faux,
  loi vraie sur un moniteur dont les issues plantées sont **permutées** entre toutes les instances). Le membre informé
  d'un moniteur planté est ajusté sur ses issues de calibrage.
- **Lois connues** (famille R) : pour chaque moniteur réel, la loi du membre informé du juge ajusté sur le calibrage seul
  (`MondeBanque.membres_informes`, crête 1) ; fiche `LR-<juge>-<rubrique>`. Garde A8 : identique au membre informé du
  monde de lecture.

## 6. Lectures (reprises de L1–L4 et E3, adaptées)

- **L1 (décisive)** : aucun témoin faux promu (verdict e-BH) dans aucune des quatre configurations. Le seuil par fiche
  (log W ≥ log 20) est rapporté pour chaque témoin faux, non décisif (déclencheur d'audit, section 13).
- **L3′ réel** : témoins vrais de la règle de L3, lus sous le monde aveugle, plan plein (tradition de L3, lue sous
  « aveugle ») : fraction promue et intervalle par rééchantillonnage par tâche. **Ici : aucun témoin vrai réel → « dents
  non mesurées » sur les témoins réels, par construction** (la garde A7 arrête si le calibrage en donnait un).
- **L3′ planté (décisive pour les dents)** : fraction des 3 témoins vrais plantés promus (e-BH, hors famille, seuil
  log(m_T/α)) sous T-plein, avec intervalle à 95 % par rééchantillonnage **par tâche** (B = 1000, section 8) ; verdict par
  force.
- **« Pas de dents »** : état des dents de chaque configuration de T, règle de production (`cycle._etat_dents`) : « dents »
  si au moins un témoin vrai promu, « pas de dents » si des témoins vrais sont jugés et aucun n'est promu, « dents non
  mesurées » sinon ; rapporté à part pour les seuls témoins réels.
- **L4′ (comparaison des deux bras, lue sans seuil)** : gain du plan plein = témoins plantés promus sous T-plein et non
  sous T-gelé, par force, log W maximal des deux bras, et la différence rééchantillonnée (plein − gelé) ; lois réelles
  promues sous R-plein contre R-gelé. L'invariant du préfixe est vérifié pour toutes les fiches des deux familles (plan
  gelé = préfixe du plan plein ; log W max plein ≥ gelé ; aucun témoin vrai promu sous gelé et pas sous plein).
- **LR (lois réelles, E3 adaptée)** : lois connues promues sous R-plein (e-BH, m_R = 26) ; pour chaque moniteur : N jugé,
  log W maximal, promue ou non, et la borne I*(N) de la section 12.
- **Exposition** : lectures de l'épreuve (une : le script refuse un dossier de sortie non vide ; toute autre exécution
  est déclarée et ne compte pas), configurations (4), fiches jugées par famille (T : 22 ; R : 26), verdicts montrés à un
  proposeur avant la lecture (0 : aucun proposeur), répliques de rééchantillonnage (elles ne choisissent rien), tâches
  d'épreuve.
- L2 (« informé » ⊆ « aveugle ») n'est pas reprise : les familles T et R n'ont pas les mêmes fiches.

## 7. Prédictions chiffrées et signées

**N_ép** = nombre d'épisodes d'épreuve retenus. Les notations décisives couvrent e0 et e1 (192 épisodes) ; les
descriptives (e2) n'existent que si l'échéance de 15 000 s ne frappe pas avant : **192** si aucune course n'a ses
descriptives, **210** si seul le lot D (6 tâches, le plus court) les a, **288** si toutes les ont (moins, dans chaque cas,
les ensembles vides, non notés). Les témoins plantés portent une issue sur chaque épisode retenu : leur N est N_ép. Taux
de la courbe publiée : lecture principale e-BH m = 17 ; plan = N pour le bras plein, plan de 120 pour le bras gelé ;
interpolation linéaire en N (fonction `puissance_courbe` du script, qui prend le N_ép observé).

| prédiction | signe / valeur | N_ép = 192 | N_ép = 210 | N_ép = 288 | réfutée si |
|---|---|---|---|---|---|
| P1 (L1) | 0 témoin faux promu, dans chacune des 4 configurations | P ≥ 0,9 | idem | idem | ≥ 1 témoin faux promu (e-BH) |
| P2 | 0 témoin vrai réel | certain (calibrage) | idem | idem | A7 (arrêt) |
| P3 (L3′ planté, plein) | fraction ≥ 2/3 | taux 0,344 / 0,852 / 0,989 (forces 0,3 / 0,5 / 0,8) ; fraction attendue 0,73 ; P(≥ 2/3) ≈ 0,90 | 0,394 / 0,873 / 0,990 ; 0,75 ; P ≈ 0,92 | 0,612 / 0,964 / 0,996 ; 0,86 ; P ≈ 0,98 | fraction ≤ 1/3 |
| P4 (L4′, lue sans seuil) | gain du plan plein (témoins plantés promus sous plein et non sous gelé) | gelé 0,258 / 0,730 / 0,944 ; gain attendu 0,25 ; P(gain ≥ 1) ≈ 0,23 | gelé 0,282 / 0,731 / 0,930 ; 0,31 ; P ≈ 0,28 | gelé 0,386 / 0,734 / 0,866 ; 0,59 ; P ≈ 0,48 | — (signe garanti ; un gain négatif est une incohérence, I5) |
| P5 (LR) | 0 loi réelle promue (plein et gelé) | P(≥ 1) ≤ 0,1 | idem | idem | ≥ 1 loi promue |

Les probabilités de P3 et P4 supposent les trois forces indépendantes ; par l'invariant du préfixe, la probabilité qu'une
force soit gagnée par le plan plein est la différence des deux taux (plein − gelé). P5 vient de la section 2 :
l'information hors échantillon de la loi connue (≤ 0,0085 nat par épisode, 3B:RIGOR ; ≤ 0,003 pour les douze autres) est
très au-dessous de I*(N) (≥ 0,054 nat, section 12), où la courbe donne une puissance de 0,9 ; à 0,0085 nat (force ≈ 0,17),
la courbe donne ≈ 0,03 à N = 202 et ≈ 0,08 à N = 288 ; à ≤ 0,003 nat (force ≤ 0,1), ≈ 0 ; le seuil de la famille R (6,25)
est plus haut que celui de la courbe (5,83).

**Prédiction conditionnelle aux paires tirées.** La courbe moyenne sur les paires de traits ; une plantation n'en tire
qu'une par force. La table ci-dessous donne le taux de promotion (plein / gelé) de chaque paire (i : trait de la softmax ;
j : trait du seuil) et de chaque force, mesuré avec le juge de cette lecture (monde informé, m = 19) sur les traits réels
du calibrage pris comme substitut de l'épreuve (40 répétitions par cellule ;
`demonstrations/annexes_lecture_t05_v1/puissance_par_paire_v1.py`) à N = 192 (vecteurs des e0 et e1) et à N = 288 (e0 à e2).
Une fois la graine de plantation connue (au scellement), la sortie rapporte, pour les paires tirées, l'espérance du
nombre de témoins plantés promus, P(fraction ≥ 2/3) et P(I4), interpolés linéairement en N entre 192 et 288 ; ces
quantités sont **lues** (non décisives) et servent à l'audit d'un échec des dents.

| paire (i \| j) | force 0,3 : N = 192 | N = 288 | force 0,5 : N = 192 | N = 288 | force 0,8 : N = 192 | N = 288 |
|---|---|---|---|---|---|---|
| log jetons \| actions valides | 0,375 / 0,35 | 0,85 / 0,725 | 0,975 / 0,975 | 1 / 0,975 | 1 / 1 | 1 / 1 |
| log jetons \| é.-t. jetons/action | 0,025 / 0 | 0,475 / 0,075 | 0,625 / 0,35 | 0,95 / 0,575 | 0,95 / 0,85 | 1 / 0,95 |
| actions valides \| log jetons | 0,5 / 0,4 | 0,675 / 0,3 | 0,9 / 0,875 | 1 / 0,95 | 1 / 1 | 1 / 1 |
| actions valides \| é.-t. jetons/action | 0,45 / 0,4 | 0,725 / 0,525 | 0,925 / 0,925 | 1 / 0,95 | 1 / 1 | 1 / 1 |
| é.-t. jetons/action \| log jetons | 0,175 / 0,05 | 0,3 / 0,1 | 0,85 / 0,7 | 0,975 / 0,55 | 1 / 0,95 | 1 / 0,975 |
| é.-t. jetons/action \| actions valides | 0,375 / 0,275 | 0,8 / 0,625 | 1 / 0,975 | 0,975 / 0,975 | 1 / 0,975 | 1 / 1 |
| **moyenne des 6 paires** | 0,317 / 0,246 | 0,638 / 0,392 | 0,879 / 0,8 | 0,983 / 0,829 | 0,992 / 0,963 | 1 / 0,987 |

Taux plein / gelé. Moyennes des six paires à comparer à la courbe : N = 192, plein 0,344 / 0,852 / 0,989 ; N = 288, plein 0,612 / 0,964 / 0,996. Sorties de l'annexe : N = 192 sha256 `22d12017…`, N = 288 sha256 `30de2400…` (annexe sha256 `f8b73c12…`). Cas le plus défavorable des paires à N = 192 : force 0,5 sur (log jetons | é.-t. jetons/action), 0,625 ; P(I4) y reste ≤ 0,02.

**Instances jugées par moniteur réel, attendues** : N_M ≈ couverture e0–e1 × 192 + couverture e2 × (épisodes e2
retenus) — même chaîne, même grille, notes de première passe ; intervalle ≈ ± 2·√(Σ N·p·(1 − p)) (binomial, hors effet de
lot) :

| moniteur | N_ép = 192 | N_ép = 210 | N_ép = 288 |
|---|---|---|---|
| 3B:BALANCE | 97 [83 ; 111] | 102 | 124 [108 ; 140] |
| 3B:COHERENCE | 171 [162 ; 180] | 188 | 260 [250 ; 270] |
| 3B:NOVELTY | 162 [152 ; 172] | 176 | 239 [226 ; 252] |
| 3B:REDUNDANCY_PENALTY | 154 [143 ; 165] | 168 | 231 [217 ; 245] |
| 3B:RESULT_REASONING | 83 [69 ; 97] | 90 | 122 [105 ; 139] |
| 3B:RIGOR | 136 [123 ; 149] | 148 | 202 [186 ; 218] |
| 8B:BALANCE | 113 [99 ; 127] | 123 | 166 [149 ; 183] |
| 8B:COHERENCE | 131 [118 ; 144] | 142 | 191 [175 ; 207] |
| 8B:IRRELEVANCE_PENALTY | 137 [124 ; 150] | 149 | 202 [186 ; 218] |
| 8B:NOVELTY | 124 [111 ; 137] | 134 | 179 [163 ; 195] |
| 8B:REDUNDANCY_PENALTY | 134 [121 ; 147] | 145 | 194 [178 ; 210] |
| 8B:RESULT_REASONING | 112 [98 ; 126] | 122 | 164 [147 ; 181] |
| 8B:RIGOR | 117 [103 ; 131] | 127 | 171 [154 ; 188] |

Le « ≈ 30 % » de notes complètes cité pour la grille H.4 compte les notations où **toutes** les rubriques sont lisibles ;
un moniteur n'a besoin que de la sienne : sa couverture va de 28 à 93 %.

## 8. Métriques et intervalles

- Richesse : log W_t = log q(y_1..t) − max_m log p̂_m(y_1..t) sur les instances du plan, dans l'ordre du plan
  (`selection_pari.evaluer`) ; log W maximal et final rapportés.
- Verdict e-BH : e-valeur = richesse arrêtée au premier instant où elle atteint log(m/α), sinon la richesse finale ;
  k* = plus grand k tel que e_(k) ≥ m/(α·k) ; témoins vrais hors famille, retenus si e ≥ m/α.
- **Rééchantillonnage par tâche** : B = 1000 répliques ; dans chacune, les tâches d'épreuve (triées par identifiant) sont
  tirées avec remise (`integers(0, T, size=T)`, T = nombre de tâches) ; chaque copie de tâche apporte ses épisodes avec
  leurs issues observées (réelles et plantées) sous un identifiant préfixé ; le calibrage ne change pas ; le juge est
  rejoué en entier (monde reconstruit, plans, ordre secret) sur les témoins vrais (plantés : famille T, monde informé ;
  réels s'il y en avait : famille R, monde aveugle), aux mêmes m. Intervalle à 95 % = quantiles empiriques 2,5 % et 97,5 %
  (rang le plus proche) de la fraction promue ; fréquence de promotion par témoin ; différence plein − gelé.

## 9. Seuils : lequel est décisif

- **Décisif : la règle e-BH à log(m/α)** — famille T : m_T = 19, seuil d'un témoin vrai 5,94 ; famille R : m_R = 26,
  seuil 6,25 ; pour une fiche en famille, seuil log(m/(α·k*)).
- **Rapporté, non décisif : W ≥ 1/α = 20 par fiche** (log 20 ≈ 3,00 ; « seuil 20,0 » des fiches). Il sert de déclencheur
  d'audit pour les témoins faux (section 13), jamais de verdict.

## 10. Graines (R9)

Soit H l'empreinte sha256 (hexadécimale) du fichier de ce préenregistrement **tel que scellé** (vérifiée contre son
compagnon `.sha256`, et contre la valeur passée en `--empreinte-preenregistrement`). Alors
`ss = numpy.random.SeedSequence(int(H, 16))`, `fils = ss.spawn(4)`, dans cet ordre :
1. **bruit** : un générateur `g = default_rng(fils[0])` ; `g.standard_normal()` tiré successivement pour chaque épisode
   d'épreuve retenu, dans l'ordre des identifiants triés, arrondi à 6 décimales : trait de bruit z (loi N(0, 1), non
   renormalisé) ;
2. **plantation** : l'entier `fils[1].generate_state(1, dtype=uint64)[0]`, passé à
   `planter(banque, 3, graine, (0.3, 0.5, 0.8))`, qui dérive ses propres flux (`graine_derivee`) ;
3. **permutation** : un générateur `default_rng(fils[2])`, dont on tire successivement une permutation de n (toutes
   les instances, dans l'ordre de la banque : calibrage dans l'ordre de `banque-e2.json`, puis épreuve triée) pour chaque
   moniteur planté, dans l'ordre `plante:0, 1, 2` ;
4. **rééchantillonnage** : un générateur `default_rng(fils[3])`, dont on tire successivement `integers(0, T, size=T)`
   pour chaque réplique, dans l'ordre (T = nombre de tâches d'épreuve, triées par identifiant).

Graine du juge : 20261027 (constante du juge, non dérivée). numpy ≥ 1.25 (2.5.3 à la rédaction). La sortie consigne H,
l'entier de plantation, les paires tirées, les versions et les empreintes de tous les fichiers de code.

## 11. Plan d'analyse (ce que fait le script, dans l'ordre)

1. Vérifier le préenregistrement (compagnon, valeur attendue), dériver les graines, puis vérifier le **code** : chaque
   ligne « empreinte  chemin » du bloc de la section 15 doit redonner l'empreinte du fichier (le bloc doit couvrir le
   script et le juge) ; hors course à blanc, un bloc absent ou une différence arrête (A2).
2. Lire le calibrage (empreinte `f59018fb…` ; toute autre empreinte fait une course à blanc, marquée et non opposable) ;
   garder les 13 moniteurs réels ; tout en calibrage ; témoins réels par la règle ; garde A7.
3. Lire la table des identifiants (empreinte `76375391…`), puis le lot. Chaque dossier `--run` est le `diag/<run>/` d'une
   branche de résultats (`<run>` = `AAAAMMJJ-HHMMSS-t05-pilote-reel`) : `episodes.json` (champ `resultat.fiches`) et les
   notations **décisives** `notations-8B-decisives.json` et `notations-3B-decisives.json` y sont exigés ; les notations
   **descriptives** `notations-8B-descriptives.json` et `notations-3B-descriptives.json` (e2) sont lues si elles existent
   (leur absence est consignée, jamais un arrêt) ; chaque fichier lu exige son compagnon `.sha256`. Clé de notation
   `juge-<8B|3B>/<identifiant>/e<k>/passe-<p>` ; **passe retenue : `passe-0`** pour chaque épisode (e0, e1, e2), comme au
   calibrage (`e0/passe-1` est lue pour les gardes, jamais retenue). Gardes A1, A2, A3, A5, A6 ; chaque course doit
   couvrir exactement les tâches d'un lot de la table, et les quatre lots doivent être là. Rapporté sans arrêt :
   appariement de chaque tâche `-g2` à sa tâche d'origine du calibrage (attendu : 96).
4. Construire l'épreuve comme la v3 : épisode retenu s'il a des jetons et au moins une notation de première passe ;
   traits log(somme des jetons), actions valides, écart-type des jetons par action, **normalisés par les moyennes et
   écarts-types du calibrage** ; bruit tiré (section 10) ; issue d'un moniteur = classe de la note entière par les
   **coupes du calibrage** ; sous-population g = numéro d'épisode.
5. Garde A4 (K = 60).
6. Banque complète, plantation, permutation, lois connues ; juger les familles T (monde informé) et R (monde aveugle) dans
   les deux bras ; invariant du préfixe.
7. Rééchantillonnage par tâche (B = 1000).
8. Lectures, prédictions (dont la prédiction conditionnelle aux paires tirées), issue, déclencheurs R4 ; écrire
   `lecture-t05-graines-neuves-v1.json` puis son rendu `.md` (rendu depuis le JSON écrit) ; aucun compagnon `.sha256`
   (scellement à part, R6).

## 12. Critères de lecture gelés — issues écrites d'avance et règle d'interprétation

**Issues** (la première qui s'applique, dans cet ordre) :

| issue | condition | lecture |
|---|---|---|
| I6 | arrêt (A1–A8) | rien n'est lu ; `arret.json` seul ; un addendum scellé est nécessaire avant toute nouvelle tentative |
| I3 | L1 non tenu | **alarme de validité** ; aucune autre lecture n'est interprétée ; audit R4 ; nœud du directeur |
| I4 | T-plein ne promeut ni la force 0,5 ni la force 0,8 | **pas de dents contraire à la courbe** (prédit 0,85 et 0,99 à N_ép = 192 ; 0,96 et 0,996 à 288 ; P(I4) conditionnelle aux paires tirées rapportée) ; audit R4 de la chaîne ; aucune conclusion sur les lois réelles |
| I5 | invariant du préfixe non tenu (plan gelé ≠ préfixe du plan plein, ou log W max plein < gelé, ou témoin vrai promu sous gelé et pas sous plein) | **incohérence de la chaîne** ; audit R4 ; LR rapportée sans conclusion |
| I2 | au moins une loi réelle promue sous R-plein | réplique de la dépendance connue sur graines neuves des mêmes tâches, **après** audit R4 (contraire à P5) |
| I1 | sinon | **issue prédite** : juge valide et denté ; aucune loi réelle promue ; borne I*(N_M) par moniteur |

**Règle d'interprétation.**

*(a) Si aucune loi réelle n'est promue (I1)* — borne sur la force des lois réelles, via la courbe. Pour un moniteur jugé
sur N_M instances, I*(N_M) est l'information par épisode (nat ; information mutuelle issue–traits sous la loi, comme
`force-en-clair-v1.txt`) à partir de laquelle une loi de la forme plantée, correctement spécifiée, est promue avec une
probabilité ≥ 0,9 sous le plan plein : force interpolée sur la courbe à N_M, traduite en information
(`borne_information` du script). Valeurs gelées : N = 120 → 0,117 nat (force 0,75) ; 144 → 0,108 (0,71) ; 180 → 0,088
(0,62) ; 200 → 0,081 (0,59) ; 240 → 0,060 (0,50) ; 260 → 0,057 (0,48) ; 288 → 0,054 (0,46) ; en dessous de N ≈ 109 :
hors grille (la force 0,8 n'y atteint pas 0,9 ; aucune borne — à N_ép = 192, c'est attendu pour 3B:BALANCE et
3B:RESULT_REASONING). **Ce que cela dit** : sur graines neuves des mêmes 96 tâches, la dépendance de la note du moniteur
M aux trois traits, sous la forme engagée (la loi connue), porte moins que I*(N_M) nat par épisode, au risque 0,1 de
manquer une loi qui l'atteindrait — à condition que l'issue soit I1 (dents confirmées : au moins une des forces 0,5 et
0,8 promue sous le plan plein ; invariant du préfixe tenu). **Ce que cela ne dit pas** : qu'aucune dépendance n'existe
(une dépendance plus faible que I*, ou d'une autre forme — non linéaire, par tâche, par épisode —, échappe à la borne) ;
quoi que ce soit sur des tâches neuves ; quoi que ce soit des traits internes de l'agent ; la borne est celle de lois de
la forme plantée (si/sinon sur deux traits), transposée à la loi connue par l'information par épisode (approximation
dite).

*(b) Si des lois réelles sont promues (I2)* — **ce que cela dit** : la loi connue du moniteur, apprise sur les 288
épisodes déjà courus, prédit les notes des épisodes neufs des mêmes tâches mieux que la bibliothèque aveugle, avec un taux
de fausses découvertes ≤ α dans la famille R. **Ce que cela ne dit pas** : que la loi vaut sur des tâches neuves ; qu'elle
est causale ; qu'elle n'est pas un effet de tâche (difficulté de l'article) commun aux deux côtés ; que les notes des juges
mesurent la qualité ; quoi que ce soit des états internes de l'agent. Contraire à P5 : l'audit R4 passe avant toute
phrase.

*(c) Si des témoins vrais plantés sont promus (dents)* — **ce que cela dit** : à ce N, sur les traits réels de ces
épisodes neufs (sans remise, contrairement aux grandes cellules de la courbe), le juge détecte une loi correctement
spécifiée de la force promue ; le gain du plan plein sur le plan gelé (L4′) dit ce que les instances au-delà des 120
premières apportent à ce N. **Ce que cela ne dit pas** : rien sur les lois réelles ; rien du nul v8 (sans effet ici) ;
une seule banque et trois témoins (l'intervalle par tâche dit la stabilité, pas une puissance).

*(d) Témoins vrais réels* — aucun n'existe (section 2) ; si la garde A7 ne les excluait pas et qu'ils étaient promus, cela
dirait que le lien monotone repéré au calibrage tient sur graines neuves des mêmes tâches, rien de plus (mêmes réserves
qu'en (b)).

**Comparaison des bras** : le gain et son intervalle par tâche sont rapportés ; ni l'un ni l'autre n'est un test de
validité (les deux bras lisent les mêmes données, et le signe est garanti par l'invariant).

## 13. Audit de symétrie (R4)

Le même audit, par un agent neuf (ni auteur de ce texte ni de la lecture), se déclenche sur un résultat trop beau **ou**
trop mauvais :
- trop beau : un témoin faux au seuil par fiche (log W ≥ log 20) dans une configuration ; une loi réelle promue (plein ou
  gelé) ;
- trop mauvais : un témoin planté de force ≥ 0,5 non promu sous T-plein ; un témoin planté de log W maximal négatif sous
  T-plein ;
- incohérence : invariant du préfixe non tenu pour une fiche.

Probabilité, sous le nul, qu'un témoin faux franchisse le seuil par fiche quelque part (32 témoins faux, quatre
configurations, fortement corrélées) : de l'ordre de 0,1 à 0,3 (courbe : jusqu'à 1,8 % par témoin faux et par cellule) ;
ce déclenchement ouvre l'audit, il ne change aucun verdict. Un témoin planté de force 0,5 manqué a une probabilité
conditionnelle à sa paire lue dans la table de la section 7 : elle est rapportée.

Contenu de l'audit : relecture des empreintes (lot, table, calibrage, code, préenregistrement) ; recompte indépendant des
épisodes, notations et instances par moniteur depuis les fichiers du lot ; contrôle que chaque tâche de l'épreuve est
`<origine>-g2` d'une tâche du calibrage et d'elle seule (table) ; trajectoire de log W et membre dominant final de chaque
fiche en cause ; couverture et déséquilibre des issues du moniteur en cause (calibrage contre épreuve) ; pour une loi
promue : part de la richesse portée par quelques tâches (retrait d'une tâche à la fois) ; pour un témoin planté manqué :
paire tirée et taux de la table conditionnelle, position de ses instances dans le plan. Le verdict de l'audit est écrit
avant toute phrase sur le résultat.

## 14. Liste d'arrêt

Un arrêt écrit `arret.json` (code, message sans aucune note ni issue, étape) dans le dossier de sortie et rien d'autre ;
aucun repli silencieux (R5) ; chaque garde est essayée sur un cas sain et sur un artefact
(`essais/test_lecture_t05_graines_neuves_v1.py`).

| code | condition | action |
|---|---|---|
| A1 | fichier manquant : banque de calibrage, préenregistrement ou son compagnon, table des identifiants, `episodes.json` d'une course, notations **décisives** d'un juge dans une course, compagnon `.sha256` d'un fichier lu ; lot de la table sans course ; tâche d'un lot absente des épisodes de sa course | arrêt ; verser le fichier, relancer dans un dossier neuf |
| A2 | empreinte discordante : calibrage ≠ `f59018fb…` (hors course à blanc) ; table ≠ `76375391…` ; un fichier du lot ≠ son compagnon ; préenregistrement ≠ compagnon ou ≠ valeur attendue ; un fichier de code ≠ le bloc de la section 15 (ou bloc absent) | arrêt ; rien n'est lu |
| A3 | doublon : même notation (juge, tâche/épisode, passe) deux fois, dans un fichier ou entre fichiers ; même épisode deux fois ; même tâche dans deux courses ; même lot dans deux courses | arrêt |
| A4 | moniteur réel à moins de **K = 60** instances jugées dans l'épreuve (K = plus petit N de la courbe ; attendu ≥ 69 à N_ép = 192, ≥ 105 à 288) | arrêt ; addendum avant toute lecture |
| A5 | tâche ou épisode présent au calibrage et à l'épreuve (identifiant identique) ; **identifiant de tâche sans le suffixe `-g2` dans l'épreuve** (épisodes ou notations) ; **tâche `-g2` au calibrage** ; notation d'une tâche du calibrage | arrêt |
| A6 | format : identifiant d'épisode hors « tâche/eK » ; clé de notation hors « juge-XB/tâche/eK/passe-N » ; `variante` ≠ « b0 » (invite b0, grille H.4) ; notation sans épisode dans les courses ; champ `notes` absent ; JSON illisible ; jetons non numériques ; tâche hors de la table, ou dont l'origine n'est pas au calibrage ; course mêlant deux lots ; table mal formée ; traits ou normalisation du calibrage non conformes | arrêt ; addendum de format scellé avant toute lecture des notes |
| A7 | la règle de L3 sur le calibrage ne redonne pas la table de la section 2 (0 témoin vrai, 13 faux, 13 moniteurs, plus grand |ρ| 0,248 sur 3B:BALANCE et l'écart-type des jetons par action) | arrêt |
| A8 | incohérence interne : loi connue ≠ membre informé du monde de lecture ; lecture aux instants inattendue ; sévérité ≠ α ; plan plein plus court que le réservoir (`PlanPleinRefuse`) | arrêt |

L'absence des notations descriptives (e2) n'est **pas** un arrêt : c'est l'issue prévue par les fiches de production
quand l'échéance de 15 000 s frappe ; elle est consignée et les e2 non notés sortent de l'épreuve.

## 15. Commande exacte

Empreintes du code (chemins relatifs à `orchestrator/` ; à recalculer et recopier ici au scellement si un fichier change
d'ici là). **Le script vérifie lui-même ce bloc** au lancement (section 11, étape 1) : toute différence = A2 ; le lanceur
peut aussi le vérifier avant, avec `sha256sum -c` sur une copie du bloc :

```
91973f2582c4db08d86250594adec317bc6796095bfdd60d3119a8c21dde179d  demonstrations/lecture_t05_graines_neuves_v1.py
6bcec082991bd8a4d55d195adb0e7b35f4e5dec00f85330e70863da96f4b4569  pole/juge_plan_plein_v1.py
359928110d757cd54cc0d2773910c7360895b68cac5d17e0e4b4e9933ef306bc  pole/selection_pari.py
33088eb9088549a20ffd489687928a1f1469d1df85a025db29bc9ce3f93e7b18  pole/monde_banque.py
798f039042e3ee1f18df5c566f5a0ddee5dac5c98225c8ce621e267174c8ee18  pole/cycle.py
cc452aafd17121a7c0ec42829eea47063ffee1f6cdf7f642e264d528f976b888  pole/nul_v8.py
ec018f147196222268d91358ce2038bb35bf76069e6bf8928dea9e3db59d1074  pole/fiche.py
71f1d08613bf335aa9ef7aa1397f20aa24553fea2f1b858c10b265d62f8ab79e  pole/memoire.py
966d9553026aad1eb7d97fa677334f1b59f22a39f15eef95134d63bc47634444  pole/outils.py
dff00005b80e8bfdd5cf3198336cbaebd0ca21752dc1c0d983835cc71f7fdaeb  exemples/construire_banque_t05_v3.py
cdfa818d0f6f9a6740e4dc6d6905d9515ffc617d6d047a7fdf566ffdfb31937d  exemples/proposeur_scripte_banque_v1.py
```

Après versement des quatre courses — chaque branche de résultats `calcul/t05-graines-neuves-<lot>-v1` récupérée par une
refspec explicite (jamais de ref `donnees/*`), son arbre extrait dans un dossier neuf hors des dépôts ; `DOSSIER_<lot>` =
son dossier `diag/<run>/` (celui qui contient `episodes.json`) — et extraction de la table des identifiants depuis le kit
(`git show f40c8aa9:donnees/t05-graines-neuves-v1/table-identifiants-graines-neuves-v1.json > "$TABLE"`, sha256
`76375391…`) :

```
cd orchestrator                                    # racine du code public, à l'état des empreintes ci-dessus
python3 -I -B demonstrations/lecture_t05_graines_neuves_v1.py \
  --preenregistrement prereg/preenregistrement-lecture-t05-graines-neuves-v1.md \
  --empreinte-preenregistrement <H, empreinte scellée de ce fichier> \
  --calibrage <chemin de banque-e2.json> \
  --table-identifiants "$TABLE" \
  --run "$DOSSIER_a" --run "$DOSSIER_b" --run "$DOSSIER_c" --run "$DOSSIER_d" \
  --sortie <dossier neuf, hors du dépôt public> --reechantillonnages 1000 --processus 1
```

Durée mesurée sur l'essai de plomberie de même forme (quatre lots, 192 épisodes retenus) : ≈ 5 s sans rééchantillonnage,
≈ 0,2 à 0,5 s par réplique selon la charge (≈ 4 à 8 min pour 1000, un cœur partagé). La sortie contient des données réelles
dérivées : elle reste hors du dépôt public jusqu'à décision (le script refuse un dossier de sortie situé dans le dépôt
public).

## 16. Réserves

1. **Aucun témoin vrai réel** : la question « le juge a-t-il des dents sur des liens réels ? » ne peut pas être tranchée
   par ce lot ; les dents sont mesurées sur des lois plantées (oracle, forme si/sinon), sur les traits réels des épisodes
   neufs. Un abaissement du seuil de la règle (par exemple |ρ| ≥ 0,2) aurait donné des « témoins vrais » de |ρ| ≈ 0,25 à
   la vérité non établie (les témoins v2 de |ρ| ≥ 0,38 se sont effondrés à 288 épisodes) : non retenu.
2. Graines neuves sur les **mêmes tâches** : effet de tâche partagé ; la puissance se compte en tâches (96).
3. **e2 probablement non notés** pour les lots de 30 tâches (échéance de 15 000 s pendant les descriptives, prévue par les
   fiches de production) : N_ép ≈ 192 à 210, d'où des prédictions plus faibles (section 7) et aucune borne pour les deux
   moniteurs les moins couverts (3B:BALANCE, 3B:RESULT_REASONING, sous N ≈ 109). Les e2 non notés relèveraient d'une
   notation complémentaire et d'un **autre** préenregistrement (ils ne s'ajoutent pas à cette lecture).
4. La courbe a été calculée sur la structure de la banque v2 (60 tâches de 2 épisodes, calibrage de N/4, tirage avec
   remise au-delà de N = 80) : ici 96 tâches de 2 ou 3 épisodes, calibrage de 288 épisodes, sans remise ; m_T = 19 au lieu
   de 17 (seuil 5,94 au lieu de 5,83). La table par paire, mesurée dans la forme de cette lecture, l'encadre (section 7).
5. La borne I*(N) transpose la puissance de lois plantées (si/sinon) à la loi connue (softmax linéaire) par l'information
   par épisode : approximation.
6. **Ordre du plan et moyennes glissantes** : le plan est évalué dans l'ordre de divergence ; sur un trait discret (actions
   valides : peu de valeurs), cet ordre groupe les valeurs égales, et le membre « moyenne glissante » du nul suit ces
   blocs ; une loi monotone juste sur un tel trait peut alors perdre contre lui (constaté sur banque synthétique pendant
   la rédaction). Cela ne touche ni la validité ni les témoins plantés (la table par paire le mesure) ; cela pèserait sur
   des témoins vrais réels monotones sur « actions valides » (il n'y en a pas).
7. Le rééchantillonnage avec remise duplique des tâches : sous le plan gelé, le sélecteur par divergence peut choisir
   plusieurs copies des mêmes instances extrêmes ; l'intervalle du bras gelé et celui de la différence en sont biaisés ;
   celui du bras plein (décisif) ne l'est pas de cette façon (tout le réservoir est pris).
8. Format du lot : celui du kit scellé (identifiants, noms de fichiers, clés, passe retenue), vérifié sur le code gelé
   de la chaîne (`lancer_pilote_a.py` et `pilote_a.py` au commit `2660b07` : mêmes champs que les notations du 17 octobre,
   `variante` « b0 ») et sur les fichiers réels du pilote ; tout écart arrête (A6) **avant** toute lecture de note.
9. Le nul v8 n'agit pas sur une génération unique à archive vide : il est imposé, pas mesuré.
10. Une seule lecture, trois témoins plantés : les fractions de L3′ sont grossières (0, 1/3, 2/3, 1) ; l'intervalle par
    tâche en dit la stabilité.

## 17. Contre-lecture

À faire par un agent neuf, avant le scellement ; son rapport (chemin, empreinte) et le traitement de chaque remarque
(acceptée, refusée et pourquoi) seront consignés ici avant le scellement. Fichiers à lui donner (R2) : ce texte ;
`demonstrations/lecture_t05_graines_neuves_v1.py` ; `pole/juge_plan_plein_v1.py` ;
`essais/test_lecture_t05_graines_neuves_v1.py` ; `demonstrations/annexes_lecture_t05_v1/constats_calibrage_v1.py` et
`puissance_par_paire_v1.py` ; `demonstrations/demo_couche1_v7.py` (L1–L4) ; `demonstrations/demo_couche1_proposeur_v7.py`
(E1–E4) ; `demonstrations/puissance_juge_banque_v1.py` et `../resultats/puissance-juge-banque-v1-2026-11-01/` (JSON,
Markdown, `force-en-clair-v1.txt`) ; `exemples/proposeur_scripte_banque_v1.py` ; `exemples/construire_banque_t05_v3.py`
(`planter`, `_fiche`, `classes_equilibrees`, `lire_sources` l. 82-123) ; `pole/nul_v8.py` ; `pole/cycle.py`
(`preparer_engagement`, `membres_de_l_archive`, `appliquer_multiplicite`, `_etat_dents`) ; `pole/monde_banque.py` ;
`pole/selection_pari.py` (`evaluer`, `selection_divergence`, membres du nul) ; du kit de production (dépôt de travail,
commit `f40c8aa9`) : la section « Pour la lecture » de `docs/procedures/graines-neuves-T0.5-v1/LISEZMOI-kit-graines-neuves-v2.md`
et une fiche de production.

Essais de la rédaction : 36 essais, 36 réussis (`python3 -B -m pytest -q essais/test_lecture_t05_graines_neuves_v1.py`). Essais
de plomberie sur les formats réels (copies hors dépôt de fichiers anciens déjà lus, jamais du lot) : épisodes du pilote et
notations décisives du 17 octobre, tâches renommées `-g2` et réparties en lots a et b selon la vraie table → arrêt A1
attendu (lots c et d absents) ; avec des lots c et d fabriqués en renommant les fichiers du lot b → course complète sur
192 épisodes retenus (descriptives absentes), vrai calibrage (A7 conforme), vraie table, code vérifié contre ce bloc,
invariant du préfixe tenu, instances par moniteur dans les intervalles de la section 7 (85 à 176).
