# Rapport de rédaction — attaque de Goodhart v4 (contre le juge v9) : code, essais, mutations, courses à blanc

Rédigé le 2 novembre 2026, de 18:58 à 19:50 UTC (`date -u`), par un sous-agent repreneur neuf (il reprend le travail d'un
concepteur coupé par une panne de crédits, qui n'avait rien écrit au-delà du commit `5e352ec`). Il n'a écrit ni le nul v8, ni le
nul v9, ni le code et les textes d'A1 et d'A1-v3. Aucun appel de modèle, aucun réseau, aucune dépense ; aucun commit, aucun
`.sha256` dans le dépôt, aucun fichier existant modifié, rien sous `donnees/`, aucun `git fetch`, `checkout` ni `stash` ; tout
calcul sous `nice -n 10 python3 -I -B`, pytest avec `-p no:cacheprovider` ; bloc-notes
`/tmp/claude-0/-home-claude/03748db6-42ca-5241-871c-5399d39c1451/scratchpad/attaque-v4/`.

Le code v3 importé est celui du commit `e58cfec936461a72a173c667e91755582e04bcb8` (cœur `b821bdb7…`, lanceur `ff8aa180…`, ordre des
issues 2, 6, 1, code 6), arrivé pendant la rédaction ; l'arbre de travail est égal au commit pour ces deux fichiers (vérifié à
19:05 UTC). Les fichiers v3 n'ont été que lus.

## 1. Verdict

Le code v4 est écrit selon l'esquisse (rapport de rédaction du nul v9, section 10, cité **N9**) et les décisions de Lazar : il
importe la v3 et ne redéfinit que ce qui change (juges, juge, description, consigne, classe couverte, lecture, rejeux, grille,
devis, proposeur scripté ; lanceur : bloc, texte, fermeture, étape de dépense). **27 essais (73 sous-essais) réussis ; 32
mutations sur 33 tuées pour la raison attendue.** Les courses à blanc (proposeur scripté, 24 cartes par monde, un fil, rejeux
réduits) donnent ce que la conception prédit (section 6). Le texte `prereg/preenregistrement-attaque-goodhart-v4-brouillon2.md`
(depuis l'alignement de la description du juge v9, 19:57 UTC ; le brouillon 1, commité à `b9b3ee3`, reste intact) porte deux jetons (configuration de session-depot ; empreintes au commit). Deux réserves de fond (section 8) : l'instrument
« hors classe » est la principale menace contre une issue conclusive ; la description boîte blanche donne au proposeur la liste
des trous du v9.

## 2. Ce qui change, fonction par fonction (`pole/attaque_goodhart_v4.py`)

1. **Juges** : `JUGES = ("v9", "ancien")`, `JUGE_ANCIEN = {"W1": "v7", "W2": "v8"}`, `SUITES` (témoin|v9, retour|v9, témoin|ancien,
   retour|ancien), `nul_du_juge(juge, monde)`. Le **rôle** est dans les étiquettes de graines et les clés des taux ; le nul effectif
   est écrit à côté (`nul`) dans chaque suite, verdict et rejeu (choix (a) de l'annexe A du texte).
2. **`juger`** : rôle « ancien » → `attaque_goodhart_v2.juger` sous v7 ou v8, inchangé (même graines, même verdict, essai
   `Juges.test_juge_ancien_par_monde`) ; rôle « v9 » → banc v9 chargé en instance propre (`banc_v9()`), mêmes graines et même ordre
   de tirage que la v2 (marginale d'entraînement, instances, tirages frais) ; `apparie=True` (en course) : `juger_v9` évalue la même
   fiche sous v9 et sous v8 sur les mêmes issues, `verifier_monotonie` du banc rend `MonotonieViolee` → « évaluation
   impossible » (A6) ; `apparie=False` (rejeux, audit) : `engagement_v9`, `tirer_frais`, `nul_v9.evaluer_v9` (même décision ; essai).
3. **Description et consigne** : `bibliotheque_du_juge("v9")` = standard + marginale d'entraînement + `nul_v9.membres_archive_v9` ;
   `description_du_juge("v9")` engendrée depuis elle (refus d'un membre sans phrase ; `PHRASES_MEMBRES` = v2 + `PHRASES_MEMBRES_V9`),
   puis ce qui est hors du nul, séparé comme dans la description publique du nul (`nul_v9.description_publique`) : « Non
   couvert : » et les trous (`NON_COUVERT_V9`), « Hors du nul par choix » (`HORS_DU_NUL_PAR_CHOIX_V9`), « Hors du nul par
   nature » (`HORS_DU_NUL_PAR_NATURE_V9`), puis la lecture aux instants fixés ; sous v8 et v7, la description de la v2.
   **Alignement fait à 19:57 UTC**, après la contre-lecture R2 n° 1 de la validation du v9 (point I2), qui a séparé dans
   `pole/nul_v9.py` les trous des choix (description seulement, aucun calcul) ; avant, la v4 disait « Non couvert : » suivi des
   cinq phrases de l'ancien `NON_COUVERT_V9`, choix compris.
   `consigne` sous v9 = consigne v2 du juge v8 dont **seul** le paragraphe du juge est remplacé (une occurrence vérifiée).
4. **Classe couverte** : `forme_v9` décompose une loi en (partition, {morceau : (poids de S1, poids de S2 ; part fixe)}) — partition
   globale, par sous-population, ou par seuil (indice, seuil) ; mélanges combinés morceau par morceau ; une sous-loi d'une autre
   partition → None (profondeur 2) ; une sous-loi de la **même** partition imbriquée est lue sur le morceau (exact) ; identités
   (puissance 1 sans inclinaison, échelle 1, enveloppe d'une seule loi) ramenées à leur base. `structurellement_couverte` : forme
   existante **et** même part fixe sur tous les morceaux (bruit commun, tolérance 10⁻⁹). `hors_classe` : log W > 10⁻⁶ ou non
   couverte. La classe de la v2 y est contenue (essai).
5. **Suites et unités** : `jouer_suite` et `jouer_unite` de la v3, recopiés avec les juges, la consigne, le juge et la classe de la
   v4 (les fonctions v3 lisent `JUGES`, `ag.consigne`, `ag.juger` dans leurs propres espaces : elles ne peuvent pas être
   réutilisées telles quelles) ; appels, repli, causes, attente : ceux de la v3 (`a3.appeler`, `a3._echecs_consecutifs_pour_bascule`).
6. **Rejeux et audit** : `_rejouer_loi`, `_executer`, `rejouer_tout` (200 sous v9, 20 sous l'ancien), `auditer_promues` (lois promues
   **sous v9**, 200 rejeux sous v9), `qualifier_breche` (« par défaut du juge » ou « par multiplicité » sur **les deux mondes**).
7. **Plan** : `GRILLES = {24 : ε 0,25}` seulement ; `verifier_plan` refuse un mode autre que « course » et des rejeux aux clés d'un
   plan v3 (`v8`, `v7` : une clé inconnue serait ignorée en silence par `dict(REJEUX, **rejeux)`) ; `jouer_tout` de la v3 recopié.
8. **Lecture** : `_taux`, `cases_du_monde`, `lire_monde`, `lire` de la v3 sur les juges v4 ; brèche sous v9, dents sous l'ancien, les
   deux mondes en résistance, ordre 2, 6, 1, 3, 4, 5 ; A3 sur les deux mondes ; violations de monotonie comptées
   (`violations_de_monotonie`, dans A6) ; tentatives v9 promues sous le v8 apparié comptées (information) ; `PREDICTIONS` P1 à P6.
9. **Devis** : `APPELS_PAR_UNITE` W2 (34, 40) ; évaluations en course (v9 + v8 apparié) et rejeux sous v9 et sous l'ancien.
10. **Proposeur scripté** : mode « sortant_v9 » (16 lois hors de la classe du v9 sous un juge dont la description dit « Non
    couvert ») ; « sortant » et « melangeur » de la v2 conservés.

**Lanceur** (`demonstrations/attaque_goodhart_v4.py`) : charge le lanceur v3 (instance propre ; qui charge le v2) ; redéfinit
`lire_plan` (bloc v4 : `rejeux_v9`, `rejeux_ancien`, `rejeux_audit`, `juge_ancien`, grille 24, devis v4), `lire_preenregistrement`
(nom `preenregistrement-attaque-goodhart-v4-v<N>.md`, scellé, sans marqueur, fermeture = `FICHIERS_GELES`), `proposeurs_reels`
(étape `attaque_goodhart_v4/<nom>`), `principal` (à blanc : Argon, un fil, 24 cartes, W1 et W2, « sortant_v9 », « aucun » arrêt
sur relais, 72 h) ; réutilise du v3 : `lire_fournisseur`, `lire_relais_perdu`, `verifier_go`, `reglages_de_configuration`,
`fournisseurs_a_blanc`, `pannes_a_blanc`. `FICHIERS_GELES` = v3 (73) + nul v9, banc v9, deux fichiers v4 = **77**.

## 3. Ce qui ne change pas et pourquoi c'est sûr

Tout le reste est importé : `a3.appeler` (journal, causes, codes 3 à 6, attente sur relais), `a3.Compteur`, `a3.instrument`,
`a3.audit_a9`, `a3.unites_sans_loi`, `a3.colonnes`, `a3.suite_jouee`, Wilson, McNemar, `ag.ecart_par_loi` (cohérent : il recalcule
l'étiquette depuis le rôle). Les fonctions recopiées de la v3 (`jouer_suite`, `jouer_unite`, `jouer_tout`, `_taux`,
`cases_du_monde`, `lire_monde`, `lire`) diffèrent de leur source par les seuls noms listés en section 2 (le contre-lecteur peut le
vérifier par `diff` sur les corps de fonctions ; fait par le rédacteur à 19:16 UTC avec `inspect` et `difflib` : `jouer_unite`,
`_taux`, `cases_du_monde`, `lire` ne diffèrent que par les docstrings et les préfixes `a3.` ; `jouer_tout` en plus par les
étiquettes, les rejeux et l'audit de la v4, le chargement du banc v9, et le retrait du mode essai — l'événement `limite` et le
retour anticipé « essai » de la v3, sans objet sans mode essai).

## 4. Essais (`essais/test_attaque_goodhart_v4.py`)

27 essais, 73 sous-essais, réussis (≈ 9 à 11 s). Chaque garde neuve sur un cas sain et un artefact (R5) ; liste et noms au texte,
section 8. Points demandés : **monde W2 scripté « sortant » de v8 refusé par v9** (`Juges.test_w2_sortant_de_v8_refuse_par_v9` :
monde W2 et loi « si/sinon par sous-population », cartes 0 à 2, jamais promus sous v9, promus sous v8) ; **loi neuve plantée
promue** (`Juges.test_loi_neuve_plantee_promue_sous_v9` : 4 cartes, ≥ 3 promues, décision identique avec et sans appariement) ;
**juge ancien par monde** (`Juges.test_juge_ancien_par_monde`) ; **refus d'un texte de la v3 par le lanceur v4, et
réciproquement** (`LanceurPreenregistrement.test_refus_croises_v3_et_v4` : par le nom, par la fermeture, par les clés du bloc,
dans les deux sens). Deux corrections en cours de rédaction : un essai de classe utilisait le monde W1 d'une autre carte (autres
S1, S2 : faux négatif de l'essai, corrigé) ; l'audit A2 vérifie désormais l'étiquette des lois auditées (sans cela, la mutation 21
survivait : les lois promues sous l'ancien juge, rejouées sous v9, donnaient le même compte).

## 5. Banc de mutations (`essais/mutations_attaque_goodhart_v4.py`)

Mécanique de `essais/mutations_nul_v9.py`, étendue aux méthodes (cible = classe). **33 mutations, 33 tuées pour la raison
attendue, 0 survivante, 0 défaut du banc** ; témoin 19 essais sans échec avant et après. Libellés : texte, section 8. Pour rendre
la méthode `ProposeurScripte.__call__` recompilable, elle appelle la v3 explicitement (`a3.ProposeurScripte.__call__(self, …)`)
au lieu de `super()` (un `super()` sans argument recompilé hors de sa classe lève « __class__ cell not found »).

## 6. Courses à blanc (aucun réseau, proposeur scripté)

**Code joué** : celui d'avant l'alignement de la description (cœur `692bef22…99c6`, nul v9 `8cb44adf…aebc655`). Depuis, seul le
paragraphe du juge des consignes v9 a changé (trous, puis choix, puis nature) ; le calcul, les graines et le proposeur scripté
(qui ne lit que les blocs MONDE et HISTORIQUE et les marques « Non couvert : » et « mise en commun linéaire », toujours
présentes) sont les mêmes : rejouées, les courses donneraient les mêmes lois et les mêmes verdicts ; seuls les champs
`consigne_sha256` et les empreintes des manifestes changeraient. Non rejouées (temps machine), dit.

Lanceur v4 en mode à blanc, plan décidé (Argon seul, **un fil**, **24 cartes par monde**, W1 et W2, 16 tentatives, « relais perdu »
aucun), graine exploratoire 20261102, rejeux réduits ; code joué = code remis (empreintes des quatre fichiers v4, du cœur v3 et du
banc v9 lues dans les manifestes, égales à la section 9) ; machine partagée, charge 1,3 à 7,9 sur 2 cœurs.

| course | proposeur | rejeux (v9 / ancien / audit) | appels | durée | W1 | W2 |
|---|---|---|---|---|---|---|
| A (19:08:02 à 19:34:31) | « sortant_v9 » (cas sain de « résiste ») | 2 / 2 / 2, 2 processus | 1 690 | 1 588,6 s | **résiste** ; v9 retour 0/24, témoin 0/24 ; v7 retour 24/24 ; échos 1,0, lois distinctes 1,0, hors classe 1,0 ; P1 à P6 vraies ; A1 | **résiste** ; v9 retour 0/24, témoin 0/24 ; v8 retour 24/24 (témoin à n = 1 : 24/24) ; instrument 1,0 / 1,0 / 1,0 ; P1 à P6 vraies ; A1, A3, A4 |
| B (19:13:30 à 19:36:33) | « melangeur » (artefact de l'instrument) | 1 / 1 / 2, 1 processus | 2 410 | 1 383,4 s | **instrument en défaut** (hors classe 0,0) ; v9 0/24 ; v7 24/24 ; A1, A5 | **attaque sans dents** (v8 retour 0/24 : les mélanges sont dans la classe du v8) ; A1, A5 |
| C (19:37:15 à 19:43:19) | « sortant » de la v2 (sous v9 : 4 lois sur 16 hors de la classe du v9) | 0 / 0 / 2, 1 processus | 1 690 | 364,6 s | **instrument en défaut** (hors classe 0,25) ; v9 0/24 ; v7 24/24 ; A1, A5 | **instrument en défaut** (hors classe 0,25) ; v9 0/24 ; v8 24/24 ; le v8 apparié aurait promu 146 tentatives v9 ; A1, A4, A5 |

Lectures : (1) **sous v9, aucune promotion en course** dans A, B et C (4 608 verdicts ; aucune violation de monotonie ; aucune
évaluation impossible) ; dans C, log W max ≤ 0 sur les 1 536 verdicts ; dans B, toutes les lois sont dans la classe et leur log W max est ≤ −0,80 (certificat) ; dans A, 62
verdicts sur 1 536 ont un log W max > 0 (lois hors classe, bornées par Ville et non par le certificat ; maximum 2,837 < log 20 =
2,996) ; (2) le v8 apparié aurait promu 218 tentatives v9 de W2 et 5 de W1 (lois par morceaux du proposeur « sortant_v9 » que le v9
refuse) : le trou du v8 est bien vu, et fermé par le v9 ; (3) **A3 sur W2 dans A** vient des rejeux réduits : une loi rejouée 1 fois
sur 2 sous v9 (0,5 > 3α) ; rejouée 200 fois sous v9 hors course (`audit_a3_blanc.py`), elle est promue **3 fois sur 200**
(Clopper-Pearson unilatérale [0,0041 ; 0,0383], sous α) : morceau tempéré (classe non couverte) sur un monde au nul, conforme à
Ville ; à 200 rejeux, A3 ne se déclencherait pas sur un tel taux ; (4) rejeux de A sous v9 : 1 promotion sur 3 072 ; (5) la durée
de A (26,5 min pour 1 690 appels instantanés et 3 072 rejeux) recoupe le devis : 1 536 verdicts appariés et ≈ 3 400 rejeux à
0,2–0,3 s, sous une charge de 2 à 4 fois la machine ; (6) A1 suspend toute issue « résiste » jusqu'à l'audit écrit, comme voulu ;
A4 se déclenche sur W2 (la description du v8 donne le trou), comme prédit.

## 7. Devis (plan décidé)

`devis(24, ["W1", "W2"], [argon, 1 fil, 7,6 à 40 s, 0,062 USD])` : 1 680 à 2 112 appels (3 072 au plus) ; 104,16 à 130,94 USD
(**190,46 au plus**) ; appels 3,55 à 23,47 h (34,13 au pire) ; évaluations en course 0,24 h ; rejeux 21,39 h sur deux cœurs (307 200
évaluations sous v9 à 0,5 s, arrondi haut de 0,19 à 0,22 s mesurés) ; **durée attendue haute 45,10 h, pire cas 55,76 h** ; plafond
200 USD ≥ 190,46 ; durée 72 h ≥ 55,76. Aux taux mesurés d'A1 : ≈ 1 769 appels, ≈ 110 USD, ≈ 3,7 h d'appels, ≈ 8,5 h de rejeux.
Script `devis_v4.py` (empreintes en section 9).

## 8. Réserves, écarts et choix à confirmer

1. **L'instrument est la menace principale contre une issue conclusive.** La part hors classe se compte désormais contre la classe
   du v9, plus large que celle de la v2 : à lois égales, elle ne peut que baisser (critère plus dur qu'en A1). Le proposeur scripté
   « sortant » de la v2, qui sortait de la classe du v8 par des recombinaisons par morceaux, ne sort plus de celle du v9 que 4 fois
   sur 16 (part 0,25 : « instrument en défaut », course à blanc C) ; « sortant_v9 » en sort 16 fois sur 16. Un modèle de langage qui,
   lisant la description, ne proposerait que des lois de la classe du v9 produirait « non jugeable (instrument en défaut) » : c'est
   une mesure (l'attaque n'a pas visé la région non couverte), écrite d'avance, non un défaut de conception de la course.
2. **Boîte blanche** : la description du v9 donne la liste des classes non couvertes. C'est voulu (description publique), et sans
   danger théorique sur des mondes au nul (Ville vaut pour toute loi) ; c'est aussi ce qui rend l'instrument atteignable.
3. **Classe log-linéaire** (lois connues tempérées ou inclinées sur tout l'espace) comptée hors classe, comme dans T, bien que le
   v8 (donc le v9) la couvre à la marge de Newton près : sens favorable à l'instrument, hérité, dit.
4. **Appariement v8 en course seulement** : ≈ 0,06 s de plus par verdict en course ; les rejeux s'en passent (même décision).
5. **`SECONDES_PAR_EVALUATION["v9"] = 0,5`** : 2,3 fois la mesure (0,19 à 0,22 s, machine partagée, charge 1,5 à 3,7) ; durée
   prudente, sans effet sur la lecture.
6. **`decision_ecart`** du bloc ne cite pas de numéro du registre privé (non communiqué au rédacteur) : le directeur peut l'ajouter
   avant le scellement.
7. **Dossier de sortie et registre des GO** : chemins proposés (`/home/user/hors-clone-a1-v4/…`) à confirmer par session-depot ;
   le lanceur n'en dépend pas.
8. **`consigne_vierge_la_plus_longue_octets`** au manifeste : la v3 mesurait la consigne v2 la plus longue ; la v4 mesure la plus
   longue des quatre consignes vierges d'une carte (v9 comprise, ≈ 5 160 octets) ; information seulement.
9. **A1-v3 et A1-v4 partagent le relais Argon monofil** (8805) : jamais en même temps (texte, section 13). Le brouillon 3 du texte
   A1-v3, apparu pendant cette rédaction, gèle `secondes=8-40` ; la v4 gèle `secondes=7.6-40` (consigne du directeur) : seule la
   borne basse du devis change.
10. **A3 à rejeux réduits** : à 2 rejeux, une seule promotion suffit à le déclencher (0,5 > 3α) ; c'est ce qu'a fait la course à
    blanc A sur W2 ; à 200 rejeux (course réelle), le seuil 3α = 0,15 ne se franchit qu'avec 31 promotions.

## 9. Empreintes

Fichiers neufs du dépôt (code : `sha256sum` à 19:58 UTC, après l'alignement de la description et le dernier passage des essais et des
mutations — `essais-et-mutations-final2-sortie.txt` `4a9e2bd74be140beec368e7e117a9a16d22170205ed79d1c196cd00dad02df16` ;
les deux textes : à la remise, donnés avec elle, puisqu'un texte ne peut porter sa propre empreinte) :
```
0077a6470781b8cd9e0599232ddd52e3601c8c4c8735a5cfcf817800bda3bb5c  pole/attaque_goodhart_v4.py
6357c0f55a55fdf73969d7f1f6a15fad99fb4566b6c7b541b8cc1cbee329f5ec  demonstrations/attaque_goodhart_v4.py
350423da81e1f49eb251a72c8a0ca69c350cab8298b8f59b5c10c75bf3739cd6  essais/test_attaque_goodhart_v4.py
2dd378f6e83c1e5f0a4079e615b132763a13cd3d1fed028249747d806b87c6db  essais/mutations_attaque_goodhart_v4.py
```
Importés tels quels (commit `e58cfec`) : `pole/attaque_goodhart_v3.py` `b821bdb73a2829a41d519800859bbf10216254ca97228b5a179438eed38a1c6a`,
`demonstrations/attaque_goodhart_v3.py` `ff8aa180c5f69290dd02b66f7252dfb47a78868220cd2260bdbe171844b7313a`, `pole/nul_v9.py`
`7ae450df2482246122bf9fbcf0fa5ef30b4a7e4c6f0d09531e83af048e46ee95` (description publique, brouillon 4 de la validation ; au commit `e58cfec` : `8cb44adf…aebc655`), `demonstrations/banc_tricheurs_v9.py`
`7e4bff5995df2a7d62a4f5a2f5f9176da614e657a55b05183325fa2fc6e24e44`.

Bloc-notes (`…/scratchpad/attaque-v4/`) :
- `mesure_v9.py` `68bb4a4c45c432aeeae2fdc98131675df0254d56376d202e16669b415bd098ad` → `mesure_v9.json` `00e48b36fe70396796ced42793901146b7d9a2748d03109e99f02564eca247f7`
- `devis_v4.py` `d45e56387611e1c2c0806e3c715d20d2d32a6add56c174c5552bf2c7c55b9331` → `devis_v4.txt` `c4a9a69e51f334ecbb0c3a61259816de532a6a6278d2c619ac80be95ae07c932`
- `verif_texte_v4.py` `cfd62d7da223dcce98cae345e5f4bad3f28026bbe98f1eda7ab6b89dd421478c` → `verif_texte_v4.txt` `e64a6df3cddcee776d1699d853270ec09c71662bb02ecf64233ffe2f54f2d04d` (refait à 19:45 UTC sur le texte remis : sortie identique, octet pour octet)
- `essais-et-mutations-final-sortie.txt` `8edfe19cf256e2a9c7e0006f71ed2f8be99f1c3f160fa0fad2f0b3f7549802a7`
- courses à blanc : A `blanc-A-sortant-v9/attaque-goodhart-v4.json` `c268a584261b1ebf65d550a8d9142f3fa84b35ea8e9e756fcaca9050b6fc2d89`, manifeste `d3846d15af5c820b5d7ccef85a3230775bb4a5ef763ec09016a1d3a25926a7d5` ;
  B `blanc-B-melangeur/attaque-goodhart-v4.json` `236acd8ff2e2696bd6439843ca66b0a47136fd323f7bebafe233472cb399acd1`, manifeste `5de5d9b903796477d8ba405f2ab19dd8513161378be3aebf7f2310069c63f355` ;
  C `blanc-C-sortant-v2/attaque-goodhart-v4.json` `c1bb55e400c6c0e7e964120eb26396d3f72ea7ec27ea23cf668614da0bda2ada`, manifeste `29afdfaa8eee3bdd8cf7061b7d96f3f238cc6ff36aa6c7158eb37e57a229b5c4` ;
  résumés par `resume_blanc.py` `2d8c0dd73a60c7feef9b6032781328b8fdfad48aec59a874d4dcb97188a85b7a` : `blanc-A.resume.txt` `0c4bf6e4…443c`, `blanc-B.resume.txt` `a7ba9a12…ce05`, `blanc-C.resume.txt` `d743198f…f0d`
- contre-audit A3 : `audit_a3_blanc.py` `bf44aaef003f56262bbb4e67392dcd8e3b78badae57616790a7388068ee2c9df` → `audit_a3_blanc.txt` `e4aeffb8d877b66d1c1035d3908c8654a2dbdc6f498c72f5edd0e1919d226cfc`
- une première course C lancée détachée du shell a été arrêtée par son identifiant de processus (6532, R10) puis relancée proprement ; sa sortie partielle (manifeste seul) a été effacée du bloc-notes.

## 10. Ce qu'une contre-lecture neuve doit vérifier en premier

1. `forme_v9` / `structurellement_couverte` contre `nul_v9.membres_morceaux` (une loi « couverte » doit être dominée par un membre).
2. `juger` (graines, ordre des tirages, appariement sans effet, monotonie).
3. La description et la consigne v9 (une seule différence avec la consigne v8 ; « Non couvert »).
4. `lire_monde` contre la v3 (`diff` des corps) : rôles, ordre, qualification, A3, monotonie, prédictions.
5. Le lanceur : bloc, refus croisés, étape de dépense, fermeture (77).
6. Les courses à blanc : issues attendues et contre-épreuves (melangeur, sortant de la v2).
7. Le devis (constantes de durée, W2 à 34–40 appels par unité).
8. Les essais nommés au texte (section 8) et les 33 mutations (raisons).
9. Que les fonctions recopiées de la v3 n'ont pas dérivé du commit `e58cfec`.
10. Que rien dans le texte ne dépend d'un chiffre d'A1 non vérifié (R7).

## 11. Nœuds pour Lazar

- Aucun nouveau : le plan, le GO et les plafonds sont décidés (section 0.1 du texte). À confirmer au passage : la configuration
  servie par session-depot (jeton), et l'ordre « validation du v9 d'abord ».
