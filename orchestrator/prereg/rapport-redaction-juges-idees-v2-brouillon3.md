# Rapport de rédaction — juges d'idéation v2, brouillon 3 (code et texte)

3 novembre 2026, de 07:02 à 10:20 UTC (heures de `date -u`). Concepteur-développeur neuf : je n'ai écrit ni l'étage des juges
d'idéation, ni le protocole v2, ni ses brouillons 1 et 2, ni leurs contre-lectures, ni les essais, le banc ou le lanceur avant ce
tour. Consigne : `/home/claude/controle-ia-travail/brouillons/reprise-conv-audit-2026-11-02-nuit/prompts-sous-agents/juges-idees-v2-developpeur-brouillon3-prompt.md`.
Copie de travail : `/home/claude/wt/juges-v3/` (tête `eaa74ca`). Aucun commit, aucun compagnon `.sha256`, aucun `git fetch`,
`checkout`, `stash` ou `reset`, rien sous un dossier `donnees/`, aucun réseau, aucun modèle ; quatre fichiers existants modifiés
(ceux que la consigne nomme), deux fichiers neufs (le brouillon 3 et ce rapport) ; brouillons de travail sous
`/home/claude/scratch/juges-v3/`. Calculs sous `nice -n 10 python3 -I -B`, `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1`, pytest avec
`-p no:cacheprovider`. Le processus du serveur a redémarré vers 09:10 UTC pendant le travail ; rien n'était perdu sur disque, la
seule tâche en cours (une sélection du banc, sans sortie écrite) a été relancée.

## 0. En bref

- **B8 levé** (matériaux, contrôles, juges) : lois fausses **appariées** à une bonne loi (écart à un point près, même rédaction,
  taux centrés au même endroit), deux interactions fausses contredites par une table 3, sens réparti (M12) ; contrôle de forme à
  quatorze indices et au vocabulaire sur les deux comparaisons (D1 et sous-ensemble de D1b) ; contrôle de diagnosticité à 23 juges de
  surface — ampleur, seuils, interaction, signe, longueur, chiffres, vocabulaire, plus haut pourcentage, ordre, position, et leurs
  contraires et combinaisons — qui **échouent tous** (D1 au plus 1 fois sur 20, D1b au plus 1 fois sur 20, aire moyenne des lois
  fausses au plus 0,607), et un juge témoin « lecteur des tables » qui **réussit** (D1b 20 fois sur 20, aire 0,997). Les matériaux du
  brouillon 2 (`59737a16…`, reconstruits à l'octet) sont refusés pour la raison de la contre-lecture (« ampleur » et « seuil » : D1b
  20 sur 20, aires 0,958 et 0,958 ; « seuil » D1 2 sur 20, aire 0,624 : les chiffres de la contre-lecture, rejoués).
- **B9 levé** (politique du relais) : table des codes de la commande réelle (n° 294, § 3) — code 3 au plancher comme au pire cas
  attendu et repris sans limite de nombre ni compte d'échecs de suite (pire cas compté) ; code 4 et refus de requête (413) : arrêts
  nommés au premier appel, sans attente ; dans les phases décisives, aucune panne par la durée (seule la garde de 48 h) ; marge
  d'incidents d'Argon écrite au devis. Course à blanc de la contre-lecture (cinq codes 3 au pire cas dans la phase décisive de A) :
  I0 au brouillon 2, **I1, lecture identique à l'octet à la course sans panne** ici.
- **I6, I7, I8 levés** ; **I9** écrit (épreuve étendue, section 13 ordonnée) ; **M8 à M16** levés (code ou couple).
- Essais : **102 réussis** (79 + 23 neufs), 81 sous-essais. Banc : **133 mutations** (104 + 29 neuves), 133 tuées pour la raison attendue au second et dernier lancement complet (le premier, arrêté par la limite de mémoire après 81 mutations, a révélé six défauts du banc, corrigés et rejoués par sélection).
- Brouillon 3 : `prereg/preenregistrement-juges-idees-v2-brouillon3.md`, un seul marqueur, « À REMPLIR » (le commit).

## 1. Fichiers et empreintes

| fichier (depuis `orchestrator/`) | avant (tête `eaa74ca`) | après |
|---|---|---|
| `pole/juges_idees_v2.py` (modifié) | `7eee3b29f10212c169672b39ab75326c2af894f5b031594223656b29313f1067` | `57e4474aef700adbe9e494ce3955f62b62c2152c810e262e5914fdf675f4a3c8` |
| `demonstrations/validation_juges_idees_v2.py` (modifié) | `01eadabc95dce0206ffd32b9250ef16e8bd505dd7ed43321794ee93a1590fc27` | `2494a56fa0de4c7df087e3a4683465210055ad558daf9d96e2ebeffe0bcf45b1` |
| `essais/test_juges_idees_v2.py` (modifié) | `fbe7afa5f42e4ccc914d0a72d44964e937c18adfaa18f587a527abb4ba9b996e` | `7e01500b1c890dacfb730fea93aacfa09a8efa89d44520cd95ba7da999978bf1` |
| `essais/mutations_juges_idees_v2.py` (modifié) | `7b267ef851e043bb0b62e701660f0940c3a392c10ff38deb104c8eaea4322a0e` | `cb84dda4eee931ea1e2a75314b0dd698083b1026327ffaccbef0e804a9a91d63` |
| `prereg/preenregistrement-juges-idees-v2-brouillon3.md` (neuf) | — | `2680cf6a5c7f080d796a9089a85d3c454f030a02186b5dc3d24728c600523dce` |
| `prereg/rapport-redaction-juges-idees-v2-brouillon3.md` (neuf, ce fichier) | — | (non écrite ici : un fichier ne porte pas sa propre empreinte) |

Pièces lues : la contre-lecture v2 (`8b91ab570df978d05f6cbe38f1f0e2e33d5f78b238c8f54c334d61c195b74999`, en entier) et ses 12 couples
(`e20cdc1f1d77fe0176b53e926338cdc57e381df4f96328871f3405aa0599592c`) ; le brouillon 2 (`c1df7e91…`, en entier) ; le n° 294 de
session-depot (`81e601fad368cbf06e8cce0ff30b79f97c5063f5bc263db042356e7bea2878c5`, en entier) ; `pole/adaptateurs.py` l. 355-775
(`modele_conforme`, `AdaptateurCommandeExterne.lancer`), `pole/adaptateur_commande_v64.py` (en entier), `pole/attaque_goodhart_v3.py`
l. 60-130 (politique d'A1-v3.1) ; `registres/go.md` ligne 78 (GO-2026-11-02-32 ; registre lu à 08:35 UTC,
`45d56fa0c86fb8580761ff1256fc6d5efecda20363f268ec80844314f2c62be5` ; `verifier_go_v56` : 60 USD admis, 59 et 61 refusés « pas
exactement ») et ligne 79 (GO-2026-11-03-01, seconde course d'A1-v3) ; `registres/decisions.md` lignes 1215, 1230, 1238-1242
(R-1276 à la ligne 1240), 1257-1258, 1264-1265, 1302-1333 (registre lu à 08:35 UTC, `1b1042fca63917e103e5780b7f5ee13e290c9ab4dbc161e4bf5e5aeedd6efa3e`).

## 2. Points levés : avant, après, essai, mutation

Chaque garde neuve a un essai sur un cas sain et sur un artefact (R5) et au moins une mutation, tuée par le banc pour la raison
attendue (section 4).

| point | avant (brouillon 2) | après (brouillon 3) | essais (cas sain / artefact) | mutations |
|---|---|---|---|---|
| **B8** témoins séparables sans lire une table | écart affirmé des lois fausses tiré dans (6, 7, 8) ; seuil de prédiction 3 pour toutes ; aire 1,000 entre bonnes lois et lois fausses ; juges « seuil » et « ampleur » : D1b 20 sur 20 | jeu « mondes-v3 » (`2ee2f2e4…`) : appariement (écart, rédaction, centre des taux) ; deux interactions fausses (table 3) ; sens et champ « signe » répartis ; effet de la bonne loi graduée croissante à 0,45 ; contrôle de forme 14 indices + vocabulaire × 2 comparaisons ; 23 juges de surface tenus à D1 et à D1b ; témoin « lecteur des tables » tenu à réussir | `Materiaux.test_ecarts_apparies_et_tables_lues`, `test_artefact_forme_brouillon2_et_sous_ensemble_de_d1b` (dont un indice synthétique qui ne sépare que le sous-ensemble de D1b) ; `Diagnosticite.test_cas_sain_juges_adverses_echouent_et_le_lecteur_des_tables_reussit`, `test_artefact_diagnosticite_brouillon2`, `test_artefact_temoin_qui_ne_lit_pas_les_tables` | écart non apparié ; interaction fausse non appariée ; centre des taux non apparié ; forme sans le sous-ensemble de D1b ; vocabulaire non contrôlé ; écart annoncé hors des indices ; signe « - » hors des indices ; juges adverses retirés ; D1b des juges de surface jamais retenu ; témoin jamais exigé ; lecteur sans comparaison des chiffres (11) |
| **B9 (i)** code 3 au pire cas | perte, cinq de suite → panne → I0 en quelques secondes | attendu et repris sans limite de nombre (15 s → 1 800 s), pire cas compté, aucun compte d'échecs de suite | `Relais.test_rien_d_envoye_attente_puis_reprise_sans_perte` (plancher et pire cas), `test_code_3_au_pire_cas_en_rafale_attendu_sans_limite_de_nombre` ; `Pannes.test_rafale_de_codes_3_au_pire_cas_dans_la_phase_decisive_de_a` ; `LanceurCheminReel.test_statuts_du_relais_par_la_vraie_commande_externe` | quota de Google non repris ; code 3 compté comme une perte ; compte d'échecs appliqué au code 3 ; attentes bornées à 300 s |
| **B9 (ii)** code 4 | attendu 6 h comme un relais injoignable (« un 429 est passager ») | arrêt nommé `ArretRefusBudget` au premier appel, sans attente (juge hors de la phase décisive de A, course dans celle-ci) ; `ArretPart` ou `ArretDevis` si le budget de l'appel était déjà borné par la part ou le plafond ; refus de requête (code 3 au plancher portant HTTP 400, 403, 411, 413) : `ArretRequete` | `Relais.test_artefacts_code_4_et_refus_de_requete_arret_nomme_sans_attente` ; `Pannes.test_code_4_de_b_n_arrete_que_b`, `test_artefact_code_4_de_a_arrete_la_course` ; `LanceurCheminReel.test_artefacts_code_4_et_refus_de_requete_par_la_vraie_commande_externe` | code 4 attendu comme un code 3 ; code 4 borné par la part lu comme refus de budget ; 413 attendu comme un relais injoignable |
| **B9 (iii)** panne de 6 h dans la phase décisive | I0 après 6 h d'un relais injoignable | aucune panne par la durée dans les phases décisives ; seule la garde de 48 h (boucle folle) | `Pannes.test_relais_de_a_injoignable_sept_heures_puis_reprise` (même issue, mêmes forces), `test_b_hors_service_attendu_jusqu_a_la_garde_de_duree`, `test_artefact_a_hors_service_arrete_la_course_issue_i0` (48 h) | panne de 6 h dans les phases décisives |
| échec coûteux (B9) | repris en fin d'étape sans attente | attente 30, 60, 120, 300 s avant l'appel suivant (relais à un fil) | `Relais.test_attente_apres_un_echec_couteux` | aucune attente après un échec coûteux |
| **I6** horloge de panne | partie du dernier succès : panne au premier échec après une longue pause | partie du premier échec de la série, remise à zéro sur une réponse | `Relais.test_horloge_de_panne_part_du_premier_echec_de_la_serie`, `test_artefact_serie_d_echecs_de_plus_de_6_heures_hors_des_phases_decisives` | horloge partie du dernier succès ; horloge non remise à zéro |
| **I7** ordre des phases, identifiant servi | bras sans dossier joué après B ; `modeles_servis_permis` ignoré par le cœur | bras juste après la phase décisive de A ; liste explicite de la configuration admise par le contrôle A2 du cœur, comme par l'adaptateur | `Pannes.test_a2_de_b_apres_le_bras_sans_dossier` ; `Plan.test_cas_sain_etapes_v2` ; `LanceurCheminReel.test_identifiant_servi_admis_par_la_configuration` | ordre du brouillon 2 ; identifiants admis ignorés (cœur) ; non transmis (lanceur) |
| **I8** journal | en mémoire jusqu'à la fin | journal au fil de l'eau (une ligne JSON vidée et synchronisée par entrée), scellé à la fin ; signal de fin et clavier convertis en `ArretInterruption` (journal partiel scellé) ; règle d'une course tuée (I0 « infrastructure », aucune relance sans GO) au texte et au manifeste | `Pannes.test_journal_au_fil_de_l_eau_et_interruption` ; `LanceurABlanc.test_journal_au_fil_de_l_eau_scelle_et_complet`, `test_interruption_journal_partiel_et_fil_scelles` | journal non écrit au fil ; interruption non convertie ; fil non scellé sur un arrêt |
| **I9** épreuve, configuration | à compléter | texte : épreuve étendue (table des codes provoquée sur chaque commande, 413, pire cas réservé de l'entrée la plus longue), section 13 ordonnée (relevés du relais 8805, configuration, ordonnancement avec A1-v3 et sa seconde course) | (texte) | — |
| **M8, M9, M13, M14, M16** | | couples C1 à C4, C9 à C12 (section 15 du texte) | (texte) | — |
| **M10** constantes mortes | `CLASSES_HORS_TABLES`, `A_PRIORI`, `ROLES` | retirées | `Materiaux.test_constantes_mortes_retirees` | — |
| **M11** redite de monde-2 invisible | « dossier sans tables » : D1 15 sur 20 | redite lue aussi par les mots propres de la loi établie ; D1 20 sur 20, D1b 0 | `Materiaux.test_redite_lue_par_les_mots_propres_de_la_loi_etablie` | redite lue par le seul nom |
| **M12** champ « signe » « - » | 3 bonnes, 0 mauvaise (aire 0,600) | 3 bonnes, 2 mauvaises (0,533 ; 0,529 sur le sous-ensemble de D1b), indice borné | dans `test_artefact_forme_brouillon2_…` | signe « - » hors des indices |
| **M15** refus non nommé | `KeyError` rendu en code 2 sans nom | porte de plafond absente : refus nommé | `LanceurCheminReel.test_artefact_porte_de_plafond_absente_refus_nomme` | porte de plafond absente admise |
| marqueur unique | trois marqueurs `<<…>>` | « À REMPLIR » (le commit), refusé par le lanceur comme les autres | `LanceurCheminReel.test_artefacts_du_chemin_reel` [marqueur « À REMPLIR » restant] | « À REMPLIR » non cherché |

**Ce qui tient, inchangé** : B2 au sens strict (aucun statut lu comme une réponse), B6, B7, puissance (15 contre 15, trois mondes :
tables analytiques recalculées à l'identique, D1 0,927 à une aire de 0,8), plafond exact de 60 USD, garde de 48 heures en tant que
garde, statistiques (Bradley et Terry, deux ordres), consigne v2 (`6978f0a4…`), les 79 essais (un renommé, `test_b_hors_service_…`,
dont l'attendu change avec B9 : B n'est plus « en panne » dans sa phase décisive, il est attendu jusqu'à la garde de durée) et les 104
mutations (fragments mis à jour quand le code a changé ; deux libellés repris pour la table réelle des codes : « code 3 (rien
d'envoyé ou pire cas) compté comme une perte » et « quota de Google (code 3 au pire cas) non repris »).

## 3. Essais

`TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py`
→ **102 réussis, 81 sous-essais réussis, 406,72 s (09:37:04 à 09:43:51 UTC, code 0 ; sortie `essais-final.txt` du bloc-notes, `f9b38fd76856cd3cb37ebbafca1a9b6856d6fb98f4b71897acf7f5dba5fe0304` ; d'autres sessions faisaient tourner leurs essais sur la machine : 223 s à la passe précédente, 09:11 UTC, sur l'arbre d'avant le dernier essai retouché)**. Les 23 essais neufs sont nommés à la section 2. Le contrôle de diagnosticité, joué par trois essais sur trois jeux
de matériaux, coûte environ une minute par jeu (il était de 55 s pour 7 juges ; il en joue 25, accéléré : garde A4 sautée quand la
liste d'étiquettes est vide, normalisation des citations mémorisée, scores des juges scriptés mémorisés par fiche).

## 4. Banc de mutations

Commande : `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B essais/mutations_juges_idees_v2.py --raisons` (depuis
`orchestrator/`). Mécanique inchangée (fonction recompilée en mémoire, substituée, restaurée ; aucun fichier modifié ; « tuée »
seulement si un essai visé échoue avec le motif attendu). Ajouts : option `--seulement MOTIF` (sélection, pour la mise au point) ; la
mémoire du contrôle de diagnosticité est **restaurée après chaque mutation** et vidée avant toute mutation du cœur qui peut toucher
son chemin (une sélection de mise au point l'avait vue polluée : un contrôle calculé sous la mutation du lecteur des tables servait aux
mutations suivantes, d'où de faux refus des matériaux dans les essais du chemin réel).

**Deux lancements complets, la limite de la consigne :**
1. **Premier lancement complet** (08:35 UTC) : **arrêté par la limite de mémoire du conteneur après 81 mutations sur 133** (08:35 à
   09:03 UTC ; 75 tuées pour la raison attendue, 2 survivantes, 3 non appliquées, 1 tuée pour une autre raison ; sortie
   `banc/mutations-1.txt`, `5f127ab161ae6b1777dfb48219a04dd9f6f4bfc25dce34f42e72dda8ca1dc019`). Cause : la mutation « durée maximale ignorée » jouait les essais
   `Pannes` où un relais est injoignable pour toujours dans une phase décisive ; sans la garde de durée, et puisqu'il n'y a plus de
   panne par la durée dans les phases décisives (B9), la course attend sans fin (journal d'attentes grandissant, 4,8 Go, processus tué
   par la limite de mémoire). C'est la démonstration que la garde de 48 heures est la seule borne de ces attentes, comme le texte le
   dit ; la mutation vise maintenant `Compteur` et `Pannes.test_artefact_duree_maximale` seulement (dit au banc). Les six autres
   constats, corrigés : deux survivantes (« contrôle de forme sans borne basse », « contrôle de forme sans le sous-ensemble de D1b ») —
   les essais ne les isolaient pas, le contrôle du vocabulaire, neuf, refusait aussi les matériaux : l'un neutralise maintenant le
   vocabulaire, l'autre ajoute un indice synthétique qui ne sépare que le sous-ensemble de D1b (aire 0,467 sur les témoins d'évaluation,
   0,200 sur le sous-ensemble) ; trois fragments périmés (le code avait changé après l'écriture de la mutation) ; un motif attendu trop
   étroit (témoin du lecteur des tables).
2. Sélections de mise au point (pas des lancements complets) : les 52 mutations que le premier lancement n'avait pas atteintes, les
   six corrigées et les autres de B8, 63 en tout (`banc/selection-reste.txt`, `8b0644baf927498d1e851649d5c3fe6ceb90c0709a596f41677bcbeccb93369e`, 09:11 à 09:34
   UTC) : 62 tuées pour la raison attendue, 1 survivante (« sous-ensemble de D1b » : jouée sur l'essai d'avant l'indice synthétique,
   chargé avant la correction) ; rejouée seule après la correction (`banc/selection-sous-ensemble.txt`,
   `756b5945aa5c9df7abe1377c8e535d72ffc7ab00068b031c82d7d49edae5dae6`) : tuée.
3. **Second et dernier lancement complet** (09:44:16 à 10:19:02 UTC, aucune suite d'essais complète en même temps ; sortie
   `banc/mutations-2.txt`, `df3263ce856360213aa3ba3a4663cc8e9d0be30e06c607e220eb62ec41f3d3ba`) : **133 mutations, 133 tuées pour la raison attendue**, 0 pour une autre
   raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin 101 essais, 0 en échec avant et après ; les quatre fichiers
   inchangés après le banc (`sha256sum -c` : OK).

Les 29 mutations neuves (B8 : 11, dont vocabulaire et centre des taux ; B9 : 7, plus les deux libellés repris pour la table réelle des
codes ; I6 : 2 ; I7 : 3 ; I8 : 3 ; M11, M15 et le marqueur « À REMPLIR » : 3 ; 31 libellés neufs ou repris en tout) sont nommées à la section 2 ; les 104 du brouillon 2 y
restent, fragments mis à jour.

## 5. Courses à blanc (juges scriptés, horloge virtuelle, aucun appel)

`python3 -I -B demonstrations/validation_juges_idees_v2.py SORTIE --a-blanc --graine 20261102 [--panne-a …]` (juges par défaut : A
« indulgent », B « parfait » ; coûts fictifs 0,062 et 0,5 USD par appel ; pire cas scripté 0,30 USD) ; sorties sous
`/home/claude/scratch/juges-v3/courses/`, sceaux vérifiés par `sha256sum -c` (0 écart) :

| course | pannes scriptées | issue | appels | attentes | dépense A ; B (incidents de A) | lecture | journal au fil (lignes) |
|---|---|---|---|---|---|---|---|
| `bout-en-bout` | aucune | I1a, S2, T1 (code 0) | 350 | 0 | 17,856 ; 31,0 (0) | `099ec809…` | 400, `2fde8b9c…` |
| `rafale-code3-pire-cas-15` | A : codes 3 au pire cas aux appels 100-104, quota de Google 150-159 (phase décisive de A) | **I1a, S2, T1** (code 0) | 365 | 15 (8 250 s) | 22,356 ; 31,0 (4,50) | **`099ec809…`** (égale à la course sans panne) | 415, `68009447…` |
| `rafale-code3-pire-cas` | A : 100-104 et quota 150-169 (25 pires cas) | I1a, **S0**, T1 (code 0) | 345 | 25 (26 250 s) | 23,496 ; 31,0 (7,50) | `5bfc03e8…` | 393, `848e1883…` |
| `relais-a-injoignable-7h` | A : relais injoignable aux appels 60-80 (7,6 h d'attente) | I1a, S2, T1 (code 0) | 371 | 21 (27 525 s) | 17,856 ; 31,0 (0) | `099ec809…` (égale) | 421, `8bb78892…` |
| `code4-a-decisive` | A : code 4 (402 du relais) dès l'appel 120 | **I0** (code 3, `ArretRefusBudget`, immédiat, aucune attente) | 120 | 0 | 7,378 ; 0 | `52669ada…` | 132, `65310255…` |
| `code4-b` | B : code 4 dès son 3e appel | I1a, S2, T1 (code 0 ; B arrêté, réserve « accord du juge B non mesuré ») | 291 | 0 | 17,856 ; 1,0 | `78827a3a…` | 334, `7ae66926…` |

Lecture : la rafale de codes 3 au pire cas que la contre-lecture avait jouée (I0 au 104e appel, 0 attente) est attendue et reprise ;
la lecture est **identique à l'octet** à celle de la course sans panne, comme celle d'un relais injoignable 7,6 heures. **Constat
neuf** (course à 25 pires cas) : au pire cas scripté de 0,30 USD, 25 tentatives (7,50 USD) dépassent la marge d'incidents de la part
de A (6,89 USD) ; la phase décisive a pu finir (sa projection tenait encore), mais le bras sans dossier, projeté ensuite sur ce qui
restait de la part, n'a pas été joué (S0, règle « toute la phase doit tenir ») : la marge est la borne réelle (point 3 de la section 8).

## 6. Devis au pire cas

Plafond exact 60 USD (GO-2026-11-02-32) ; parts 24 USD (Argon) et 36 USD (Astra). **Pire cas de la course = 24 + 36 = 60 USD** par
construction : le compteur à parts refuse tout appel dont le budget ne tient plus dans le reste de la part du juge ou du plafond, les
portes de plafond accusent chaque part, le registre des commandes porte le plafond de la course. Requis au prix du plan : Argon 276
appels, 17,11 USD ; Astra au plus 69 appels, 34,50 USD à la borne prudente de 0,50 USD par appel ; total requis au plus 51,61 USD.
**Marge d'incidents** : Argon 6,89 USD, soit 29 tentatives au pire cas réservé de l'entrée la plus longue (10 654 caractères,
≈ 0,235 USD au barème prudent de la commande : 10 et 50 USD par million, caractères divisés par 3, 4 000 jetons de sortie ; n° 294,
section 4), environ 11,6 heures d'erreurs continues de l'interface absorbées dans la phase décisive de A ; Astra 1,50 USD à la borne
prudente. Durée hors attentes : 0,88 à 6,07 heures (inchangée), garde de 48 heures.

## 7. Marqueur restant

Un seul, « À REMPLIR », à la section 11 (le commit qui portera ce code) ; le lanceur refuse tout texte qui le porte (essai et
mutation neufs). Le texte ne porte plus aucun marqueur `<<…>>` (vérifié par le motif du lanceur). Deux pièces restent à produire avant
le scellement, sans marqueur : l'empreinte de la configuration (la ligne `configuration_sha256` du bloc `plan-gele` dit « relevée
avant le scellement » ; le lanceur la refuse tant qu'elle n'est pas une empreinte) et le relevé de l'épreuve (une phrase de la
section 4 dit qu'il la remplacera). Les empreintes du code (62 lignes) sont écrites, relevées sur l'arbre de rédaction à 08:35 UTC
(le cœur et le lanceur n'ont plus changé depuis : `57e4474a…`, `2494a56f…`).

## 8. Décisions à porter au directeur (proposer avec recommandation ; défaut sous 48 heures)

1. **Panne dans les phases décisives.** Enjeu : R-1276 interdit un budget de temps qui coupe une mesure décisive. Options : (a) aucune
   panne par la durée, seule la garde de 48 h (codé) — avantage : aucune coupe ; inconvénient : un relais mort pour de bon immobilise
   la course jusqu'à 48 h ; (b) un seuil long, 24 h — avantage : rend la machine plus tôt ; inconvénient : un budget de temps qui coupe.
   Recommandation : (a), confiance 0,8. Défaut : (a).
2. **A2 du juge B.** Enjeu : un A2 de B arrête la course (règle inchangée) ; depuis I7, le bras sans dossier est déjà joué. Options :
   (a) garder l'arrêt de la course (codé) ; (b) n'arrêter que B (A2 tenu : aucune réponse d'un autre modèle n'est servie). Recommandation
   (a), confiance 0,6 : un modèle servi différent dit un relais qui ne se comporte plus comme convenu ; ce que (b) sauverait se réduit
   aux phases descriptives. Défaut : (a).
3. **Marge d'incidents d'Argon.** Enjeu : au-delà d'environ 29 tentatives au pire cas (≈ 11,6 h d'erreurs continues de l'interface),
   la part de A (24 USD, fixée par le GO) est atteinte : I0 « part » dans la phase décisive, ou bras sans dossier non joué après elle.
   Options : (a) garder les parts du GO (codé) ; (b) demander un GO qui porte la part d'Argon à 30 USD et celle d'Astra à 30 (Astra
   requis 34,50 à la borne prudente : à confirmer par l'épreuve) ; (c) allonger l'attente au pire cas jusqu'à 3 600 s (22 h couvertes,
   reprise plus lente). Recommandation : (a) puis, si l'épreuve mesure Astra sous 0,40 USD par appel, (b) ; confiance 0,5. Défaut : (a).
4. **Reconnaissance du refus de requête.** Le cœur reconnaît un 400, 403, 411 ou 413 du relais par « HTTP 4xx » dans le motif du code
   3 ; la forme exacte de la ligne d'erreur de la commande n'est pas connue d'ici : l'épreuve la relève (provoquer un 413 ne coûte rien).
   Si elle diffère, nouveau texte (sinon une erreur de requête serait attendue jusqu'à la garde de 48 h, sans dépense).

## 9. Dix points pour la contre-lecture

1. **B8, preuve par juges** : rejouer `controle_diagnosticite` sur les trois jeux (`construire_materiaux(20261102)`, `"mondes-v2"`,
   `"mondes-brouillon1"`) ; vérifier que les 23 juges de surface échouent et que le lecteur des tables réussit sur `mondes-v3`, et que
   `mondes-v2` est refusé pour « ampleur » et « seuil » ; chercher un juge de surface que je n'ai pas écrit (par exemple une
   préférence pour la paire de taux la plus « ronde », pour un titre plutôt qu'un autre, pour la position du chiffre dans la phrase).
2. **B8, appariement** : une loi fausse reprend la rédaction et l'écart d'une bonne loi du même monde ; monde-3-07 (loi fausse,
   « brouillons ») et monde-3-01 (bonne loi, « actions ») écrivent les mêmes taux (19 % et 45 %) aux mêmes variantes : seule la table
   les départage ; est-ce un indice de surface (deux hypothèses presque jumelles dans une paire) ou exactement ce que le plan veut ?
3. **B8, retouches après mesure** (section 9 du texte) : les matériaux ont été retouchés trois fois après un balayage ou un contrôle
   (centrage, effet à 0,45, centrage sur la bonne loi appariée), seuils inchangés ; le dire suffit-il ?
4. **B8, lecteur des tables** : `verifier_par_les_tables` lit les tables 1 à 3 du texte servi seul ; vérifier qu'il ne lit aucune
   métadonnée et qu'il ne réussit pas pour une autre raison (essai `test_ecarts_apparies_et_tables_lues` : il ne contredit que les dix
   lois fausses, et ne trouve rien à vérifier que dans la définition et le texte long).
5. **B9, table des codes** : la lecture du n° 294 (§ 3) est-elle bien celle du code (code 3 au plancher : relais injoignable **et**
   refus 400, 403, 411, 413 du relais ; au pire cas : toute erreur de l'interface) ; le cœur distingue le refus de requête par le motif
   « HTTP 4xx » : l'épreuve doit le confirmer (décision 4).
6. **B9, attente sans limite** : un code 3 au pire cas n'est jamais une panne ; la part borne la dépense ; vérifier qu'aucune boucle ne
   peut tourner sans dépense ni attente (chaque passage compte, attend, journalise ; la garde de 48 h tient) ; la course à 25 pires cas
   (section 5) perd le bras sans dossier par la part : acceptable ? (décision 3).
7. **I6, I8** : l'horloge de panne (`Compteur.echec`, `succes`, `verifier_panne`) et le journal au fil de l'eau (`Journal.fil`,
   `FilJournal`, `_interruption`) : un signal de fin pendant `adaptateur.lancer` tue bien la commande (adaptateur gelé, `killpg`) puis
   scelle le journal ; une ligne du fil par entrée, dans l'ordre (essai `test_journal_au_fil_de_l_eau_scelle_et_complet`).
8. **I7** : `modeles_servis_permis` est repris de l'adaptateur construit par la configuration (`juges_reels`), pas relu à côté ; le
   plan écrit au manifeste le porte ; un identifiant hors de la liste reste un A2 au premier appel.
9. **Texte** : un seul marqueur ; `configuration_sha256` et le relevé de l'épreuve sans marqueur mais refusés par le lanceur ou annoncés
   par une phrase ; les 12 couples appliqués (texte intermédiaire égal à l'aperçu de la contre-lecture, `bf68deb4…`), C6, C8 et C9 refaits
   pour la raison dite (section 15) ; la table du plan joué recalculée (I1 dans 56 courses sur 60 à 0,75 au lieu de 49).
10. **Banc** : le premier lancement complet est mort par manque de mémoire sur la mutation « durée maximale ignorée » (essais qui, sans la garde de durée et sans panne dans les phases décisives, ne finissent pas) ; je l'ai restreinte aux essais qui finissent : vérifier que ce n'est pas une garde affaiblie (sans la garde de 48 h, un relais mort pour toujours dans une phase décisive fait attendre la course sans fin : c'est voulu par B9, et la garde est la seule borne) ; vérifier aussi l'isolement des deux essais du contrôle de forme (vocabulaire neutralisé, indice synthétique) et la restauration de la mémoire du contrôle après chaque mutation.

## Annexe — bloc-notes (`/home/claude/scratch/juges-v3/`, hors dépôt)

| fichier | sha256 | rôle |
|---|---|---|
| `sondes/balayage_surface.py` | `d8e6bc5c81ee65d06c905427815f1bbb92c6e9ff0e01ea0aa9db58aa2388a5dc` | balayage de 127 traits de surface (B8) |
| `sondes/diagnosticite-final3.json` | `2a2a2e5496e37bdcf0d6b6856962a10242653eb1adc4b9fd0bcc7fec41ed01a6` | contrôle de diagnosticité, trois jeux |
| `sondes/diagnosticite-v3.txt` | `c738ab0327ec3d0f60d83dcfdd8868517a4c26eb36ebe83d696a676793dddf26` | contrôle de diagnosticité, jeu du texte (lisible) |
| `sondes/diagnosticite-final.txt` | `629f66125b2259e6e8eacf5656fa91dc1b041d959e6ad9c9c7e06ffa6f6fbcaf` | contrôle, jeux du brouillon 2 et du brouillon 1 (et un jeu intermédiaire refusé) |
| `sondes/forme-final.json` | `fcfcf89769eb850fe00a2a1b087634c54c6683e3b231d590556406f5e0e2f2ff` | contrôle de forme, trois jeux |
| `sondes/puissance-b3.json` | `af9c52f874d6f3a8b063166bfe3b987c4092b349d9c8b40e14652c01920aac02` | tables de puissance et plan joué (section 5 du texte) |
| `sondes/empreintes-du-code.txt` | `ab0e7fb1f5bdb00c02ee8632e3b73b909c3fecfcdf6230c460a93c6d49204e9c` | bloc de la section 11 (62 lignes) |
| `sondes/chiffres-texte.json` | `9dcc20c765ccd7e69135630eb706861cbc58b1108efc6c9887394add7afbe8cd` | valeurs recopiées dans le texte |
| `texte/b2-plus-couples.md` | `bf68deb47a58364efcbcc3d9f1e89e8795172d0dd96d04531052ae90e227c167` | brouillon 2 + 12 couples (égal à l'aperçu de la contre-lecture) |
| `texte/composer.py` | `ded6167014493b9d05d5cde9a7f6b5561dc9665d6ae84f6f7edb342c3870f865` | composition du brouillon 3 |
| `texte/valeurs.py` | `07b5e645cd69cfd2156588d4bcef55138f3d7e743b205636328daafbf449b75a` | blocs de texte du brouillon 3 |
| `essais-final.txt` | `f9b38fd76856cd3cb37ebbafca1a9b6856d6fb98f4b71897acf7f5dba5fe0304` | suite d'essais finale |
| `banc/mutations-1.txt` | `5f127ab161ae6b1777dfb48219a04dd9f6f4bfc25dce34f42e72dda8ca1dc019` | premier lancement complet (arrêté à 81) |
| `banc/selection-reste.txt` | `8b0644baf927498d1e851649d5c3fe6ceb90c0709a596f41677bcbeccb93369e` | sélection de 63 |
| `banc/selection-sous-ensemble.txt` | `756b5945aa5c9df7abe1377c8e535d72ffc7ab00068b031c82d7d49edae5dae6` | sélection de 1 |
| `banc/mutations-2.txt` | `df3263ce856360213aa3ba3a4663cc8e9d0be30e06c607e220eb62ec41f3d3ba` | second lancement complet : 133 sur 133 |
| `courses/bout-en-bout/lecture-juges-idees-v2.json` | `099ec809616b155180ffe6c9f9c451bedd96a0db25a937f1a826fda6a0086dc4` | course à blanc, lecture |
| `courses/bout-en-bout/journal-au-fil-juges-idees-v2.jsonl` | `2fde8b9c38e7e072a3d686361c5a339c10d70d966128a36d5d7dd592f155d25a` | course à blanc, journal au fil de l'eau |
| `courses/rafale-code3-pire-cas-15/lecture-juges-idees-v2.json` | `099ec809616b155180ffe6c9f9c451bedd96a0db25a937f1a826fda6a0086dc4` | course à blanc, lecture |
| `courses/rafale-code3-pire-cas-15/journal-au-fil-juges-idees-v2.jsonl` | `680094477af096e673ccf97b8ef29a9fdd2d8f305891dee1122bf7182486441c` | course à blanc, journal au fil de l'eau |
| `courses/rafale-code3-pire-cas/lecture-juges-idees-v2.json` | `5bfc03e863e3f4bf6f4a1281e61ffc7b5c5ed55a365bc39d2033d7661a181d68` | course à blanc, lecture |
| `courses/rafale-code3-pire-cas/journal-au-fil-juges-idees-v2.jsonl` | `848e1883060869787b6716a68078b68fb640e8f34ec689e5758bb642f5835a1e` | course à blanc, journal au fil de l'eau |
| `courses/relais-a-injoignable-7h/lecture-juges-idees-v2.json` | `099ec809616b155180ffe6c9f9c451bedd96a0db25a937f1a826fda6a0086dc4` | course à blanc, lecture |
| `courses/relais-a-injoignable-7h/journal-au-fil-juges-idees-v2.jsonl` | `8bb788923791a6d414afa7c2ec17fea551b4328a8c0cb0c6657cb1f9bb0edede` | course à blanc, journal au fil de l'eau |
| `courses/code4-a-decisive/lecture-juges-idees-v2.json` | `52669adadf180717c54183ab1172fe2a51d479d0e75f19a8b758ce7d6577d0b3` | course à blanc, lecture |
| `courses/code4-a-decisive/journal-au-fil-juges-idees-v2.jsonl` | `65310255f9a9e9262caa8a071ec9201870ba635206165d6f7ae36ad677b34a26` | course à blanc, journal au fil de l'eau |
| `courses/code4-b/lecture-juges-idees-v2.json` | `78827a3af4fdd45bd65a49d5cde419658859b05cce20d5a516aa1c7d97d8d54f` | course à blanc, lecture |
| `courses/code4-b/journal-au-fil-juges-idees-v2.jsonl` | `7ae66926b14edd24c23bfacb33fec3d0f2d96e96879fcc337f4545546de2e7b8` | course à blanc, journal au fil de l'eau |
