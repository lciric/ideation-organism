# Rapport de rédaction — étage des juges d'idéation, version 2, brouillon 2

Rédigé du 2 novembre 2026, 23:31 UTC, au 3 novembre 2026, 01:40 UTC (heures lues sur `date -u`), par un concepteur-développeur
neuf, qui n'a écrit ni l'étage actuel des juges, ni le protocole v2, ni le brouillon 1, ni sa contre-lecture. Copie de travail
isolée `/home/claude/wt/juges-v2/` (tête `66dbcf1`). Aucun commit, aucun compagnon `.sha256` dans le dépôt, aucun `git fetch`,
`checkout`, `stash` ou `reset`, rien sous un dossier `donnees/`, aucun appel de réseau ni de modèle ; calculs sous `nice -n 10`,
`python3 -I -B`, `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1` ; banc de mutations complet joué deux fois, jamais en même temps que
la suite d'essais. Python 3.13.18, numpy 2.5.3. Consigne suivie :
`/home/claude/controle-ia-travail/brouillons/reprise-conv-audit-2026-11-02-nuit/prompts-sous-agents/juges-idees-v2-developpeur-brouillon2-v2-prompt.md`
(sha256 `558a9f7a75d0f1ad91b2cd49f8e71c655322e0de0d194b5c3c6386fd06141385`).

## 1. Fichiers et empreintes

| fichier (sous `orchestrator/`) | état | lignes (tête → ici) | sha256 à la tête `66dbcf1` | sha256 ici |
|---|---|---|---|---|
| `pole/juges_idees_v2.py` | modifié | 2 063 → 2 996 | `604c217b41e7b427e19a521c29cc1464844417c115ff4e6a97f214a535b58a3d` | `7eee3b29f10212c169672b39ab75326c2af894f5b031594223656b29313f1067` |
| `essais/test_juges_idees_v2.py` | modifié | 858 → 1 441 | `086ca4a49633b81858e10e875ee3413cd531e657fc19cc9e4b83ea962de728ea` | `fbe7afa5f42e4ccc914d0a72d44964e937c18adfaa18f587a527abb4ba9b996e` |
| `essais/mutations_juges_idees_v2.py` | modifié | 240 → 372 | `677f95c29b0608b1f2d968af52430d4bfaac0b3ed6890603daae7baab4952237` | `7b267ef851e043bb0b62e701660f0940c3a392c10ff38deb104c8eaea4322a0e` |
| `demonstrations/validation_juges_idees_v2.py` | modifié | 598 → 657 | `1539d32425cbd7f2f5fefd64a7ba065c4078827a168df581f77560fcfa75129b` | `01eadabc95dce0206ffd32b9250ef16e8bd505dd7ed43321794ee93a1590fc27` |
| `prereg/preenregistrement-juges-idees-v2-brouillon2.md` | neuf | 669 | — | `c1df7e911c1e0f6b3b342b65a68b65bd7b362759617bfb756ec5eb08a19d9fff` |
| `prereg/rapport-redaction-juges-idees-v2-brouillon2.md` | neuf (ce fichier) | — | — | donnée hors du fichier |

Aucun module partagé modifié : `git status` ne montre que les quatre fichiers ci-dessus (et les deux neufs) ; aucun autre fichier
du dépôt n'importe le module ou le lanceur.

**Lu, empreintes vérifiées au début** : brouillon 1 `d72750747c1d07b8fd5fe388e9c6208a150bc60f9eece0140efc76645fb307ef` ; son rapport
`31a8654c976f1e0ec16290096a903952819f4fd856e7151dd1e0aa88229bd82d` ; contre-lecture
`1dc3c1943c5322731efa7deedd97e9cce7fe7746f6cec268bc05c3f980d43977` ; couples
`ad48ba2f40287b9a46b79e5e64a243880d0b72b2e95cde06b3dbfc111e55d79a` ; `pole/juges_croises_v53.py`
`c4c6ab12dc471eef078c116a4205a22d9b498da720ce71e37a0a6edae6c4239b` ; README principal
`a5e6b8622fbd7b319d74a01b9d2208c13a1e89dc17cdc37c4f1d99db6dd4b298` ; `pole/attaque_goodhart_v3.py`
`b821bdb73a2829a41d519800859bbf10216254ca97228b5a179438eed38a1c6a` ; patch interrompu
`28ef9cf8d2e6c23defd97a6d124eccc7b3ac7c995179204741f4b69628ea0966` (son compagnon vérifié). Registres du dépôt de travail, lecture
seule : `registres/go.md` `53985197d3e9780db9bf9738c050c3e746eea149af3e4024649f41db5cedef0a` (ligne 78, GO-2026-11-02-32 ; passe
`configuration_v56.verifier_go_v56` à 60 USD, vérifié le 3 novembre à 01:27 UTC) ; `registres/etat.md`
`f425a6842d3d711f419670517895f4a0c609b23b60d37873cdf4f31633f637cd` (ligne 6) ; `registres/decisions.md` lu d'abord à
`ac042c1168d62a474de13a787465c401a5955332aa0d313d0a167169783f0bc4`, puis à
`39ef7ecb153ae4af4d599886eecd02d0b6ce7a01e2e59932f7fc75ce01090201` le 3 novembre (le registre a crû pendant la session ; les
lignes citées, 1215, 1230, 1240 et 1241, relues à la seconde empreinte).

**Sorties de travail, hors dépôt** (`/home/claude/scratch/juges-v2/`) :

| sortie | contenu | sha256 |
|---|---|---|
| `puissance-b2.json` | tables de puissance et plan joué (section 5 du brouillon) | `6026cdc3664d627c929cdacf26faca66903b7b1d8e662d7e377ed32612d40fea` |
| `sondes/chiffres-brouillon2.json` | matériaux, forme, diagnosticité des deux jeux, tailles d'entrée, appels par phase | `de2f4f94f754321a87c1b4f2801b480d5d86c3be2837692330a4585bedf8e6f6` |
| `sondes/forme_lois_fausses.txt` | indices de forme, bonnes lois contre lois fausses | `375ee440de8a1042208df606c2be448f484eecc70c49648e9fd0038fae4ca957` |
| `sondes/forme2_adapte.txt` | juge sans tables de la contre-lecture rejoué (script `cb1f8bed…`) | `85e9b5ebf59d96ff31414060d1ae5c4846f93386e015c199a8354b03df872e6a` |
| `essais-final.txt` | suite d'essais sur le code final | `692d320c8841aad609c471e9257f2324d4f54b2ee4e79a91fd2f9126670efd8b` |
| `banc/mutations-1.txt` | premier banc complet | `5fe262fe7f7e0a7816582146d047124b5b3720edb3725edfd0e4e8b5b16565c4` |
| `banc/mutations-2.txt` | second banc complet | `b22b92b1007c8495155ed0c6abb6889f5f60c6fc0fc2e7efc743a8e9ae10c2d1` |
| `courses/<scénario>/` | six courses à blanc, sorties scellées par le lanceur lui-même | section 7 |

## 2. Ce qui vient du patch interrompu, ce qui est refait

Le patch (`+562 −109` lignes sur `pole/juges_idees_v2.py`, base `c15a073`) passe `git apply --check` sur la copie ; appliqué, le
module vaut `bc64a2a36df5e4356579b234af6233f5d3a790d9aba38b421bc3a54f52a4cd4c` (copie gardée hors dépôt). Il a été relu en entier
et rejoué (matériaux `93e3351a…`, tentatives 6, 7 et 22 : conformes à ses cinq indices de forme), puis réécrit en partie.

**Repris, vérifié, puis modifié** : l'idée des trois mondes et des étiquettes d'a priori par caractéristique ; les genres « loi
fausse graduée » et « signe contraire » ; les indices de forme étendus bornés des deux côtés ; le compteur à parts ; la première
écriture de `classer_resultat` (statut « refus » de la commande v56 lu comme A2 selon `refus.evenement`) ; le bras sans dossier
comme phase d'étapes ; l'esquisse du contrôle de diagnosticité (un juge « forme », un juge « dossier sans tables » descriptif).

**Refait, et pourquoi** :
- code 4 (plafond de session, registre, 402, 429) : le patch arrêtait la course (« dépense »), comme le proposait la contre-lecture ;
  un 429 est passager, et un arrêt de la course sur une limite de débit est le « non concluant par défaut de conception » que
  Lazar refuse ; ici, ce qui n'a pas été envoyé (code 3 ou 4 au coût plancher) est attendu et repris, et le compteur à parts
  arrête déjà, avant l'appel, tout appel qui ne tient plus dans le plafond ou dans la part ;
- relais injoignable : le patch bornait l'attente à 30 minutes cumulées par appel, puis perdait l'appel pour de bon ; ici, attente
  sans borne par appel, panne du juge après 6 heures sans aucune réponse ;
- pertes : le patch ne reprenait jamais un appel perdu et comptait toutes les pertes, non les seules définitives ; ici, reprise en
  fin d'étape (mêmes entrées, mêmes identifiants), au plus deux fois, puis perte définitive, et la règle des 15 % porte sur les
  pertes définitives ;
- coûts : le patch faisait entrer les coûts des échecs dans le prix observé et notait 0 pour un A2 à coût inconnu ; ici, tout
  incident est compté dans la dépense, jamais dans le prix observé, et un coût inconnu compte le plafond de session ;
- arrêts : le patch arrêtait toujours la course (garde de validité sur toutes les phases confondues) ; ici, un arrêt de A dans la
  phase décisive de A arrête la course (I0), tout autre arrêt n'arrête que son juge (`ArretJuge`, `ArretPanne`, `ArretPart`),
  consigné et nommé en réserve ;
- matériaux : un sixième indice (sens de la loi) et une caractéristique décroissante d'effet vrai neuve par monde (`lecture`,
  `aide`, `confirmations`), pour que le sens de la loi ne sépare plus les classes (empreinte nouvelle `59737a16…`) ;
- contrôle de diagnosticité : six juges de forme à préférences lexicographiques au lieu d'un, et le juge « dossier sans tables »
  rendu décisif pour D1b (au lieu de descriptif), avec D1 réduit au test ;
- tout le reste est écrit ici : plan des phases et règles de projection, mesures, lecture gelée (D1 à D7, D1b, S0 à S3, T1, T0,
  T-), prédictions P1 à P16, puissance, juges scriptés de panne, lanceur, essais et banc.

## 3. Blocages levés : avant, après, essai, mutation

Les essais sont dans `essais/test_juges_idees_v2.py` (classe.essai, [cas de sous-essai]) ; les mutations sont celles du banc
`essais/mutations_juges_idees_v2.py`, toutes tuées pour la raison attendue au second banc (section 6).

**B1 — témoins séparables sans lire de table.**
- Avant : matériaux du brouillon 1 (`c3eeb559…`) : indice « gabarit gradué » 0,80, « caractéristique binaire » 0,30, a priori 0,85 ;
  contrôle de forme à deux indices (longueur, chiffres) ; le juge sans tables de la contre-lecture tenait D1 16 fois sur 20.
- Après : trois mondes rééquilibrés (`59737a16d4f5250398ac52bc5b1e26952f356cd26fbafa9b1ed9a28afac5284d`) ; six indices dans
  [0,35 ; 0,65] (longueur 0,624, chiffres 0,531, gabarit 0,500, binaire 0,467, a priori 0,520, sens 0,527) ; contrôle de
  diagnosticité avant tout appel (six juges de forme : D1 au plus 1 fois sur 20, aires moyennes 0,407 à 0,593 ; juge « dossier sans
  tables » : D1b 0 fois sur 20) ; le juge de la contre-lecture rejoué sur ce code : aire 0,545, D1 0 fois sur 20 (0,533 et 0 avec
  l'a priori), contre 0,823 et 18 fois sur 20 sur les matériaux du brouillon 1 reconstruits ; D1b qualificatif et lecture T1, T0,
  T- ; P14 ; classe « signe contraire ».
- Essais : `Materiaux.test_cas_sain_deterministe_composition_et_gardes`, `Materiaux.test_sens_des_lois_et_champ_signe`,
  `Materiaux.test_artefacts_forme` (matériaux du brouillon 1 refusés ; borne basse ; réduction à deux indices),
  `Materiaux.test_artefact_verite_non_etablie` (loi fausse graduée, de deux groupes, signe contraire, champ « signe »),
  `Diagnosticite.test_artefact_diagnosticite_brouillon1` (cas sain : matériaux de ce texte admis ; artefact : brouillon 1 refusé).
- Mutations : « contrôle de forme des témoins ignoré », « contrôle de forme réduit à la longueur et aux chiffres (brouillon 1) »,
  « contrôle de forme sans borne basse », « loi fausse graduée non contrôlée contre la table », « loi fausse de deux groupes non
  contrôlée contre la table », « signe contraire non contrôlé », « champ « signe » non contrôlé », « contrôle de diagnosticité
  ignoré par la garde des matériaux », « diagnosticité : juges de forme jamais retenus contre les matériaux », « diagnosticité : D1b
  du juge « dossier sans tables » jamais retenu ».
- Reste (point 2 de la section 9) : sur le sous-ensemble de D1b, longueur 0,657 et chiffres 0,638 entre bonnes lois et lois
  fausses ; les juges « longueur » et « chiffres » y tiennent D1b 2 fois sur 20. Dit dans le brouillon (sections 4 et 10).

**B2 — statuts du relais lus comme des réponses du juge.**
- Avant : A2 contrôlé sur « ok » seulement ; tout autre statut lu comme une réponse vide ; code 4 sans coût compté au plafond de
  session dans le prix observé, puis arrêt par projection (I0) ; code 3 ou 6 lus comme réponses inexploitables, puis garde de
  validité (I0) ; projection contre le seul plafond total.
- Après : `classer_resultat` (réponse, A2, refus du modèle, quota, relais, délai, non conforme, réglage, dépassement, autre) ;
  `appeler` : A2 → arrêt de la course au premier appel ; rien d'envoyé → attente 15, 30, 60, 120 puis 300 s et même appel repris,
  panne après 6 heures sans réponse ; échec coûteux → perte, coût hors du prix observé, reprise en fin d'étape au plus deux fois,
  puis perte définitive ; cinq échecs coûteux de suite → panne ; pertes définitives au-delà de 15 % de la phase décisive de A →
  I0 « infrastructure » ; projection contre le reste de la part du juge et du plafond ; arrêts par juge hors de la phase décisive
  de A.
- Essais : `Relais` (10 essais, dont `test_classement_des_statuts`, `test_a2_modele_servi_different_absent_ou_refus_au_premier_appel`,
  `test_rien_d_envoye_attente_puis_reprise_sans_perte`, `test_artefact_relais_injoignable_trop_longtemps_juge_en_panne`,
  `test_echec_couteux_perdu_hors_du_prix_observe`, `test_reprise_bornee_puis_perte_definitive`,
  `test_artefact_pertes_definitives_au_dela_de_15_pour_cent`) ; `Pannes` (10 essais) ;
  `LanceurCheminReel.test_statuts_du_relais_par_la_vraie_commande_externe` (par `AdaptateurCommandeExterneV56` et une commande
  factice : code 4 puis code 3 au coût plancher → attentes ; code 3 muet → perte reprise, coût inconnu de 1,00 USD hors du prix
  observé ; refus du modèle → réponse inexploitable ; autre modèle servi → arrêt A2) ;
  `LanceurCheminReel.test_course_reelle_factice_arretee_par_la_garde_de_validite` ; `LanceurABlanc.test_a_blanc_juge_b_en_panne`.
- Mutations : les trois mutations A2, « refus du modèle lu comme une réponse », « rien d'envoyé compté comme une perte », « quota
  (code 4) non repris après attente », « panne du juge jamais déclarée », « échecs coûteux consécutifs jamais une panne », « appel
  perdu jamais repris », « reprise sans borne », « pertes définitives sans plafond de 15 % », « incident compté dans le prix
  observé », « arrêt du juge B étendu à toute la course », « arrêt dans la phase décisive de A non remonté à la course », « juge
  arrêté : ses étapes suivantes jouées quand même », « erreur d'un relais non convertie en arrêt ».

**B3 — plafond de 60 USD.** Avant : 30 USD au texte et au code. Après : `PLAFOND_MAX_USD = 60`, bloc `plan-gele` à 60, 24 et 36 ;
le GO doit porter exactement le plafond. Essais : `LanceurCheminReel.test_cas_sain_verifier_seulement_aucune_ecriture` (parts
accusées 24 et 36) ; `test_artefacts_du_chemin_reel` [plafond au-dessus de 60], [parts au-dessus du plafond] ;
`test_artefacts_go_et_environnement` (GO de 25 USD : « pas exactement »). Mutations : « lanceur : plafond au-dessus de 60 USD
admis », « lanceur : parts des juges hors du plafond admises », « lanceur : GO non vérifié au registre ».

**B4 — bras « ancien protocole sans dossier ».** Avant : absent. Après : phase `sans-dossier-a` (30 appels d'Argon), entrée égale
octet pour octet à celle de la v53, graines propres, D7, S0 à S3, P12, P13, effet du dossier (DeLong bilatéral) et gain total
(DeLong unilatéral), descriptifs. Essais : `Entrees.test_entree_ancienne_sans_dossier_identique_a_la_v53`,
`Mesures.test_bras_sans_dossier_mesure`, `Lecture.test_lectures_jointes_bras_et_tables`,
`LanceurCheminReelComplet.test_cas_sain_course_reelle_factice_complete` (30 appels sans dossier). Mutation : « lecture du bras :
S1 confondue avec S2 ».

**B5 — garde de durée.** Avant : 6 heures. Après : 48 heures, garde contre une boucle folle seulement (durée haute du devis 6,07
heures). Essais : `Compteur.test_cas_sain_et_artefacts_du_compteur` [durée 0, −1, infinie], `Pannes.test_artefact_duree_maximale`,
`test_artefacts_du_chemin_reel` [durée maximale nulle], [durée haute au-dessus de la durée maximale]. Mutations : « durée maximale
ignorée », « durée maximale nulle admise (cœur) », « lanceur : durée maximale nulle admise », « lanceur : durée haute non comparée à
la durée maximale ».

**B6 — choix des juges.** Avant : Astra hors du périmètre écrit du GO ; Kimi écarté pour des raisons qui tombaient à 60 USD.
Après : GO-2026-11-02-32 nomme Argon (relais 8805) et Astra (commande 8807) et exclut Kimi ; le texte le cite, sans marqueur ;
étiquettes, familles et relais distincts exigés par le cœur et par le lanceur ; aucun juge de la famille des gabarits ; budget par
appel au moins deux fois le prix de plan le plus haut. Reste l'épreuve de la commande Astra (`<<EPREUVE_ASTRA_8807>>`). Essais :
`Plan.test_artefacts_juges_de_la_famille_des_gabarits_de_meme_famille_ou_de_meme_relais`, `test_artefacts_du_chemin_reel` [juges
sur le même relais], [juge de la famille des gabarits], [relais du juge absent], [budget par appel sous deux fois le prix de plan].
Mutations : « juge de la famille des gabarits admis (cœur) », « juges A et B sur le même relais admis (cœur) », leurs deux
pendants du lanceur, « lanceur : relais d'un juge absent admis », « lanceur : budget par appel sous deux fois le prix de plan
admis ».

**B7 — sept gardes sans essai d'artefact.** Chacune a maintenant son artefact et sa mutation, tuée pour la raison attendue :

| garde (contre-lecture, B7) | artefact | mutation |
|---|---|---|
| durée haute au-dessus de la durée maximale | `test_artefacts_du_chemin_reel` [durée haute au-dessus de la durée maximale] | « lanceur : durée haute non comparée à la durée maximale » |
| lot réel soumis à la garde A4 de la configuration | `test_artefacts_pieces_et_lot_reel` (fiche réelle qui nomme un témoin) | « lanceur : lot réel non soumis à la garde A4 de la configuration » |
| pièce de la configuration absente | `test_artefacts_pieces_et_lot_reel` (pièce `question_course_2` retirée) | « lanceur : pièce de la configuration absente admise » |
| texte au bon nom hors du dossier fixé | `test_artefacts_du_chemin_reel` [bon nom hors du dossier fixé] | « lanceur : texte au bon nom hors du dossier fixé admis » |
| A2 : modèle servi absent | `Relais.test_a2_modele_servi_different_absent_ou_refus_au_premier_appel` [absent] | « A2 : modèle servi absent admis » |
| `duree_max_h` nulle | `test_artefacts_du_chemin_reel` [durée maximale nulle] ; cœur : `Compteur.test_cas_sain_et_artefacts_du_compteur` | « lanceur : durée maximale nulle admise » ; « durée maximale nulle admise (cœur) » |
| juges A et B sur le même relais | `test_artefacts_du_chemin_reel` [juges sur le même relais] ; `Plan.test_artefacts_juges_…` | « lanceur : juges A et B sur le même relais admis » ; pendant du cœur |

**Puissance (contre-lecture, I1).** Avant : 10 contre 10, D1 = aire ≥ 0,75 et p < 0,05 : 0,73 à une aire vraie de 0,8 ; plan
joué, I1 dans 8 courses sur 40 à une exactitude de 0,75. Après : 15 contre 15 (GO-2026-11-02-32), D1 = le test seul : 0,927 à 0,8,
0,985 à 0,85 ; D4 au niveau 0,10 : D1 et D4 ensemble 0,894 à 0,8 et 0,979 à 0,85 ; plan joué : I1 dans 49 courses sur 60 à une
exactitude de 0,75, 55 sur 60 à 0,80, 59 sur 60 à 0,85. Essais : `Statistiques.test_puissance`, `Statistiques.test_binomial_exact`,
`Statistiques.test_aire_et_mann_whitney`, `Lecture.test_seuils_du_texte_egaux_au_code`. Mutations : « aire : égalités comptées
comme victoires », « test binomial : queue mal comptée », « seuil binomial décalé d'un cran ». Le recalcul de la contre-lecture
(0,928 à 15 contre 15, aire 0,8, avec son propre script) et celui-ci (0,927) diffèrent dans le bruit de simulation (écart type
d'environ 0,002 à 20 000 répétitions).

**Autres points de la contre-lecture.**
- I2 (la consigne nomme les défauts plantés) : classe « signe contraire » ajoutée (trois fiches), lue par P15 ; dit en portée.
- I3 (réglages de raisonnement) : `--effort` et `--reflexion` à recopier avec l'épreuve d'Astra (marqueur unique, permis par la
  consigne).
- I4 (consigne figée de l'ancien juge et garde A4) : `exiger_entrees` avant tout appel (le lanceur la joue) ; vérification par la
  session qui tient les pièces avant le scellement (section 13 du brouillon).
- I5 (sens de D6) : D6 redéfini en exactitude de B (test binomial) ; le kappa reste descriptif (P6), relation (2p − 1)² dite.
- M1 : lignes de `kappa_cohen` (133 à 140). M2 : sans objet (D1 au test seul). M3 : bascule groupée par (tirage, paire), essai
  `Statistiques.test_bascule_comptee_par_tirage_et_par_paire`, mutation « bascule groupée par paire tous tirages confondus ».
  M4 : sources du devis écrites (chemin, ligne, empreinte). M5 : identifiant réel de la forme des témoins refusé, essai
  `Plan.test_regle_de_famille_sur_le_lot_reel`, mutation « identifiant réel de la forme des témoins admis ». M6 : indicateur « au
  plafond » aligné sur D2 (`SEUIL_PLAFOND = 0.8`). M7 : gardes vérifiées dans des essais partagés, citées section 4.

## 4. Liste d'arrêt : gardes, essais, mutations (R5)

Cas sain commun du chemin réel : `LanceurCheminReel.test_cas_sain_verifier_seulement_aucune_ecriture` (code 0, aucune écriture,
parts accusées) et `LanceurCheminReelComplet.test_cas_sain_course_reelle_factice_complete` (course complète par des commandes
factices, code 0). « chemin » = `LanceurCheminReel.test_artefacts_du_chemin_reel` [cas].

| garde | artefact | mutation tuée |
|---|---|---|
| texte d'un autre nom, brouillon | chemin [brouillon] | « lanceur : brouillon admis » |
| texte au bon nom hors de `prereg/` | chemin [bon nom hors du dossier fixé] | « lanceur : texte au bon nom hors du dossier fixé admis » |
| texte non scellé | chemin [non scellé] | « lanceur : texte non scellé admis » |
| marqueur restant | chemin [marqueur restant] (`<<EPREUVE_ASTRA_8807>>`) | « lanceur : marqueur restant admis » |
| code ≠ code gelé | chemin [code différent] | « lanceur : empreintes du code non comparées » |
| fermeture incomplète | chemin [fermeture incomplète] ; `Fermeture.test_fichiers_geles_egaux_a_la_fermeture` | « lanceur : fermeture du code incomplète admise » |
| clés du plan | chemin [clé de plan manquante] | « lanceur : clés du plan non vérifiées » |
| valeurs fixes du plan, dont la politique du relais | chemin [valeur fixe différente du code], [politique du relais différente] | « lanceur : valeurs fixes du plan non comparées » |
| consigne v2 ≠ code | chemin [consigne v2 autre] | « lanceur : consigne v2 d'une autre empreinte admise » |
| plafond au-dessus de 60 USD | chemin [plafond au-dessus de 60] | « lanceur : plafond au-dessus de 60 USD admis » |
| parts hors du plafond | chemin [parts au-dessus du plafond] | « lanceur : parts des juges hors du plafond admises » |
| durée maximale nulle ou négative | chemin [durée maximale nulle] ; `Compteur.test_cas_sain_et_artefacts_du_compteur` | lanceur et cœur |
| juges de même relais, de même famille | chemin [juges sur le même relais] ; `Plan.test_artefacts_juges_…` | lanceur et cœur |
| juge de la famille des gabarits | chemin [juge de la famille des gabarits] ; `Plan.test_artefacts_juges_…` | lanceur et cœur |
| graine, option de plan en réel | chemin [graine en réel], [option de plan en réel] | « lanceur : graine admise en mode réel », « … options de plan admises … » |
| configuration d'une autre empreinte | chemin [autre configuration] | « lanceur : configuration d'une autre empreinte admise » |
| GO autre que celui du texte | chemin [GO autre que celui du texte] | « lanceur : GO autre que celui du texte admis » |
| GO d'un autre montant | `test_artefacts_go_et_environnement` (25 USD) | « lanceur : GO non vérifié au registre » |
| variable de clé dans l'environnement | `test_artefacts_go_et_environnement` (`GH_TOKEN`) | « lanceur : variable de clé admise » |
| budget par appel sous deux fois le prix de plan | chemin [budget par appel sous deux fois le prix de plan] | « lanceur : budget par appel sous deux fois le prix de plan admis » |
| matériaux d'une autre empreinte | chemin [matériaux autres] ; `Materiaux.test_artefact_materiaux_alteres_ou_autre_empreinte` | lanceur ; « empreinte interne … non vérifiée », « matériaux d'une autre empreinte … » |
| vérité connue non établie | `Materiaux.test_artefact_verite_non_etablie` | cinq mutations (section 3, B1) |
| forme qui sépare les classes | `Materiaux.test_artefacts_forme` | trois mutations |
| classement possible sans les tables | `Diagnosticite.test_artefact_diagnosticite_brouillon1` | trois mutations |
| étiquette interdite dans un témoin | `Materiaux.test_artefact_etiquette_interdite_dans_un_temoin` | « étiquette interdite dans un témoin non contrôlée » |
| pièce absente | `test_artefacts_pieces_et_lot_reel` | « lanceur : pièce de la configuration absente admise » |
| lot réel hors de la garde A4 | `test_artefacts_pieces_et_lot_reel` | « lanceur : lot réel non soumis à la garde A4 … » |
| relais absent | chemin [relais du juge absent] | « lanceur : relais d'un juge absent admis » |
| dépense requise au-dessus de la part d'un juge | chemin [part sous le devis requis] | « lanceur : devis requis non comparé à la part du juge » |
| durée haute du devis au-dessus de la durée maximale | chemin [durée haute au-dessus de la durée maximale] | « lanceur : durée haute non comparée … » |
| pendant la course : plafond, part, projection | `Compteur.test_cas_sain_et_artefacts_du_compteur`, `Compteur.test_parts_des_juges`, `Pannes.test_artefact_phase_decisive_de_a_au_dessus_de_sa_part_arret_avant_tout_appel`, `Pannes.test_part_de_b_trop_chere_etapes_non_jouees_sans_arret`, `Pannes.test_phase_descriptive_non_jouee_si_la_part_ne_suffit_pas` | « plafond de dépense de la course ignoré », « part du juge ignorée », les deux « projection : reste … ignoré », « projections de la dépense toujours tenues », « phase décisive de A au-delà de la part : pas d'arrêt », « phase de B projetée en bloc » |
| pendant la course : durée | `Pannes.test_artefact_duree_maximale` | « durée maximale ignorée » |
| pendant la course : coût illisible | `Compteur.test_cas_sain_et_artefacts_du_compteur` | « coût déclaré illisible admis » |
| pendant la course : A2 | `Relais.test_a2_…` ; `Pannes.test_artefact_a2_pendant_la_course` ; chemin réel par la commande externe | trois mutations A2 |
| pendant la course : étiquette interdite dans une entrée | `Entrees.test_artefact_etiquette_dans_une_entree_pendant_la_course`, `Entrees.test_artefacts_etiquette_et_champ_reserve` | « étiquette interdite pendant la course : erreur brute … », « garde A4 retirée de l'entrée complète d'une paire » |
| réponses inexploitables (validité) | `Mesures.test_artefacts_citations_fausses_ou_reponses_illisibles_arretent_la_phase_decisive_de_a`, `Pannes.test_b_illisible_n_arrete_que_b_pour_la_phase` | « garde de validité retirée » |
| statuts du relais | section 3, B2 | treize mutations |
| erreur d'un relais | `Pannes.test_artefact_erreur_d_un_relais_arrete_avec_le_journal` | « erreur d'un relais non convertie en arrêt » |

**Gardes sans mutation propre ici, et pourquoi** (à juger par la contre-lecture) : la consigne figée de l'ancien juge passée à la
garde A4 des témoins (`exiger_entrees`) a son artefact au niveau de la fonction
(`Entrees.test_artefacts_etiquette_et_champ_reserve`) mais aucune mutation : la retirer laisserait l'arrêt au premier appel (garde
A4 de `entree_ancienne`, code 3, journal partiel, aucune dépense), pas avant l'écriture ; GO absent du registre, d'un autre type,
échu, révoqué : code partagé `pole/configuration_v55.py` (l. 72-100), essayé par `essais/test_v53_instruments.py` (l. 94-97) et
`essais/test_v55_corrections.py` (l. 299) ; pièce altérée et porte de plafond qui accuse faux : code partagé, essayé par
`essais/test_v56_corrections.py` (l. 238) ; dépense requise au-dessus du plafond total : redondante (parts dans le plafond).

## 5. Essais

`cd orchestrator && TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider essais/test_juges_idees_v2.py`
sur le code final (empreintes de la section 1), le 3 novembre de 01:09:19 à 01:11:09 UTC : **79 essais réussis, 72 sous-essais
réussis, 109,63 s**, code 0 (sortie `essais-final.txt`). Par classe : `Materiaux` 7, `Diagnosticite` 1 (la plus longue : deux
contrôles de diagnosticité complets), `Entrees` 4, `Citations` 3, `Plan` 6, `BradleyTerry` 3, `Verdicts` 2, `Statistiques` 7, `Relais` 10,
`Compteur` 2, `Mesures` 8, `Pannes` 10, `Lecture` 4, `LanceurABlanc` 4, `LanceurCheminReel` 6, `LanceurCheminReelComplet` 1,
`Fermeture` 1. Le chemin réel passe par la vraie commande externe v56 et une commande de juge factice (script local, aucune clé,
aucun réseau).

## 6. Banc de mutations

`TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B essais/mutations_juges_idees_v2.py --raisons` (depuis
`orchestrator/`) ; 104 mutations ; témoin : les 73 essais des classes visées (toutes sauf `LanceurABlanc`, `LanceurCheminReelComplet`
et `Fermeture`).

- **Banc 1** (2 novembre, pas sur le code final) : 102 tuées pour la raison attendue, 1 tuée pour une autre raison, 1 survivante.
  Survivante : « étiquette interdite dans un témoin non contrôlée » — l'insertion de la classe `Diagnosticite` au milieu de
  `Materiaux` avait fait passer deux essais de `Materiaux` dans `Diagnosticite`, que la mutation ne visait pas ; correction : classe
  `Diagnosticite` placée après les essais de `Materiaux`. Autre raison : « projections de la dépense toujours tenues », tuée par
  `ArretPart` et par « [] is not true » (effets directs de la mutation : la part est atteinte, la phase est jouée), hors du motif
  attendu ; correction : motif élargi à ces deux textes (déclaré : décision prise après lecture du banc). Les deux mutations ont
  été vérifiées tuées par un rejeu ciblé (`outils/banc_partiel.py`, hors dépôt), pas par un banc complet.
- **Banc 2** (3 novembre, 01:11:54 à 01:23:45 UTC, code final, empreintes relevées au départ et inchangées à la fin) : **104 tuées
  pour la raison attendue, 0 pour une autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée** ; témoin 73 essais, 0 en
  échec, avant et après ; code 0 (sortie `banc/mutations-2.txt`).
- Défaut d'affichage connu : le compte « essais en échec » additionne les sous-essais en échec (« durée maximale nulle admise
  (cœur) : 3/2 » = trois sous-essais d'un même essai sur deux essais visés) ; sans effet sur le classement.

## 7. Courses à blanc de bout en bout (juges scriptés, horloge virtuelle, aucun appel)

`python3 -I -B demonstrations/validation_juges_idees_v2.py SORTIE --a-blanc --graine 20261102 …` (script
`outils/courses_a_blanc.sh`, hors dépôt), sur le code final (le manifeste de chaque course porte les empreintes
`7eee3b29…` et `01eadabc…`) ; code 0 et sceaux vérifiés (`sha256sum -c`) pour les six ; lot réel de substitution (12 fiches, 6
admises pour A) ; 32 comparaisons de B à cette graine. Les prix sont ceux du plan (Argon 0,062, Astra à la borne de 0,50 USD).

| course | juges | issue | bras ; tables | mesures | dépense, appels | arrêts, réserves, audit |
|---|---|---|---|---|---|---|
| au plafond | A et B « plafond » | **I3a** | S2 ; T0 | aire v2 0,500 (p = 1) ; ancien : notables 1,00, aire 0,500 ; part du premier 1,00 | 48,856 USD ; 350 | audit : aire v2, kappa, exactitude de B (0,438) « décevants » ; ancien « trop propre » |
| parfait | A et B « parfait » | **I2b** | S3 ; T1 | aire v2 0,898, tirage 2 0,951, lois fausses 0,924 ; Spearman 0,721 ; ancien parfait aussi (notables 0,50, aire 1) : D3 = −0,102 | 48,856 ; 350 | audit « trop beau » (kappa 1, exactitude de B 1, aucune bascule) |
| bruité | A et B « bruite » (justes à 0,75, biais de position de 0,10 par défaut) | **I2b** | S3 ; T1 | aire v2 0,693 (p = 0,037) ; tirage 2 0,782 ; lois fausses 0,762 (p = 0,028) ; B 0,688 sur 32 (p = 0,025) ; ancien : notables 0,667 | 48,856 ; 350 | audit : Spearman 0,041 « décevant » |
| biaisé de position | A « bruite » 0,85, biais 0,5 ; B « bruite » | **I4** (D4, D5) | S3 ; T0 | aire v2 0,707 (p = 0,028) ; tirage 2 0,556 (p = 0,312) ; part du premier 0,778 ; bascule 0,611 | 48,856 ; 350 | audit : Spearman −0,336 « décevant » |
| un juge en panne | A « indulgent », relais injoignable sur les appels 40 à 70 et délais aux appels 100 et 150 ; B en panne dès le premier appel | **I1a** | S2 ; T1 | A : 31 attentes (8 325 s), 2 pertes reprises, aucune définitive ; B : 75 attentes, `ArretPanne` après 21 905 s sans réponse ; D6 non mesuré | 19,856 USD (A 19,856, dont 2,00 pour deux délais comptés au plafond de session, hors du prix observé ; B 0,0001) ; 397 ; durée virtuelle 32 699 s | réserves « accord du juge B non mesuré », « juge B arrêté en phase décisive B » ; audit « instrument : juge arrêté » ; la phase décisive de A et le bras sans dossier jouent jusqu'au bout |
| référence | A « indulgent », B « parfait » | **I1a** | S2 ; T1 | aire v2 0,898 ; D3 = +0,398 ; toutes les prédictions tenues sauf P11 | 48,856 (A 17,856, B 31,0) ; 350 ; durée virtuelle 2 924 s | audit « trop beau » et « trop propre » |

Empreintes des lectures scellées : au plafond `b95686c8…983e`, parfait `8b686f62…db2f`, bruité `34134bba…f84a`, biaisé
`0ae165e5…b972`, panne `7fde3a16…6c6c`, référence `4a789c05…3967`. Dans toutes les courses sauf « panne », les deux phases réelles
de B ne sont pas jouées : à 0,50 USD par appel, la part de B (36 USD) ne les tient plus après 31 USD (règle de projection « toute la
phase »), sans arrêt. Ces courses éprouvent le code, pas les juges réels ; « parfait » montre qu'un ancien protocole scripté qui
lit la vérité ne sature pas (I2, S3) : c'est un artefact du juge scripté, voulu.

## 8. Devis (section 12 du brouillon)

Argon : 0,062 USD et 7,6 s par appel mesurés (526 appels d'A1, R-1266) ; Astra : non mesuré, borne prudente de 0,50 USD par appel
(deux fois le taux de 0,25 USD du plan A1-bis ; « 10/50 supposé », R-1251). **Requis** : Argon 276 appels, 17,11 USD (part 24) ;
Astra au plus 69 appels, 34,50 USD (part 36) ; total requis au plus 51,61 USD. **Maximum** : Argon 302 appels (18,72 USD), Astra 95
appels (47,50 USD : au-dessus de sa part ; ses phases réelles ne sont alors pas jouées). **Attendu** à la graine 20261102 : 39,36
USD au taux de 0,25 USD, toutes phases ; 48,86 USD à la borne de 0,50 USD, sans les phases réelles d'Astra — au-dessus de
l'attendu de 30 à 43 USD du GO, sous le plafond de 60 USD. **Durée** : 0,88 à 6,07 heures séquentielles (plan maximal 0,94 à
6,52), sans attente du relais ; garde de 48 heures. Le relais Argon sert un appel à la fois : aucune autre course sur lui pendant
celle-ci.

## 9. Les dix points qu'une contre-lecture neuve doit vérifier en premier

1. **Matériaux rééquilibrés** (`59737a16…`, trois mondes, 36 fiches) : vérité de chaque fiche relue sur les tables (au moins un
   échantillon à la main, en plus de `verifier_materiaux`) ; étiquettes d'a priori (choix du rédacteur : heure de lancement,
   taille de l'écran, police, langue des commentaires, fuseau… « peu plausibles ») ; libellé et sens des trois fiches « signe
   contraire » ; caractéristique d'effet vrai laissée sans fiche dans chaque monde.
2. **Force du contrôle de diagnosticité** : il ne couvre que les juges scriptés qu'il nomme ; seuils (2 courses sur 20, aire 0,62)
   fixés pendant la rédaction, après les premières mesures ; indice de longueur à 0,624, près de la borne 0,65 ; **fuite sur le
   sous-ensemble de D1b** (longueur 0,657, chiffres 0,638 entre bonnes lois et lois fausses ; D1b tenu 2 fois sur 20 par les juges
   « longueur » et « chiffres ») : à corriger dans un brouillon 3 (contrôle de forme étendu à ce sous-ensemble, longueur des lois
   fausses), au prix d'un nouveau banc.
3. **Seuils D1, D4, D5 choisis après les simulations** (déclaré, section 9 du brouillon) : D1 au test seul (aire ≥ 0,68 à 15
   contre 15) ; D4 au niveau 0,10 (un juge dont la discrimination ne se reproduit pas passe D4 une fois sur dix) ; D5 à 0,15 (jusqu'à
   30 % de comparaisons tranchées par la position) ; vérifier qu'aucun n'est trop indulgent pour un positif, et que la course
   « biaisée de position » donne bien I4.
4. **D6 redéfini** (exactitude de B, test binomial au niveau 0,10, au moins 20 comparaisons valides) : répond-il à H3 (« un juge
   d'une autre famille départage lui aussi ») ? 24 à 36 paires mélangées selon les graines (au plus 39) : toujours mesurable si B
   répond ; B ne voit que des paires mélangées sans le savoir (choix par étiquettes, propre à la validation).
5. **Politique du relais** : code 4 (dont 429 et 402) traité comme « rien d'envoyé », attendu sans borne par appel jusqu'à 6 heures
   sans réponse — vérifier contre les commandes réelles (R-1277) qu'un code 4 dû à un budget de session trop petit ne peut pas
   tourner 6 heures (garde du budget par appel ; épreuve d'Astra : budget minimal accepté) ; seuil du coût plancher 10⁻⁵ USD contre
   10⁻⁶ déclaré ; reprises (deux) et règle des 15 % ; code 2 (réglage) compté comme échec coûteux (cinq de suite : panne) ; et
   le seuil de panne de 6 heures : une panne d'Argon plus longue pendant la phase décisive de A donne I0, alors que la garde de
   48 heures laisserait attendre davantage (choix du rédacteur, à trancher).
6. **Arrêt d'un juge contre arrêt de la course** : tout arrêt de A dans sa phase décisive arrête la course (I0) ; ailleurs, seul le
   juge s'arrête ; règles de projection (tout ou arrêt, étape par étape pour B, toute la phase ailleurs) et ordre des phases (les
   comparaisons de B avant son ancien protocole) : vérifier qu'aucun arrêt de B ne change la lecture de D1 à D5, et que la course
   « panne » le montre.
7. **Devis et budget par appel** : Astra jamais mesuré ; borne de 0,50 USD ; attendu 39,36 à 48,86 USD (le haut au-dessus des 30 à
   43 USD du GO) ; `plafonds_session.juge` ≥ 1,00 USD exigé de la configuration ; entrée de comparaison de 8 500 à 9 700 caractères,
   alors qu'Argon a été mesuré sur d'autres appels ; parts portées au relais par la porte de plafond.
8. **Lecture des statuts sur le chemin réel** : `classer_resultat` dépend des formats des adaptateurs gelés (« commande externe :
   code N : … », « refus (R-764) : … (code N : …) », « délai de 1800 s dépassé », noms d'événement de `refus`) : les relire dans
   `pole/adaptateurs.py` et `pole/adaptateurs_v56.py` à la tête, et vérifier que la commande factice des essais reproduit les
   sorties de la commande Argon réelle (codes 2 à 6, ligne de coût, commande muette).
9. **Conditions de lecture** : validité (phase décisive de A complète, pertes définitives ≤ 15 %, validité ≥ 0,85 à chaque tirage,
   au moins 27 verdicts lisibles sur 30), ordre I0, I3, I4, I1/I2, lectures S et T jointes sans changer l'issue, réserves écrites
   d'avance ; et les gardes sans mutation propre (section 4 : `exiger_entrees` ; GO, pièces et porte de plafond par le code
   partagé).
10. **Statistiques à recalculer indépendamment** : Mann et Whitney exact (U critique 153 sur 225 et niveau 0,0488 à 15 contre 15 ;
    145 et 0,0936 pour D4 ; 77 sur 105 et 0,0455 pour D1b), DeLong (unilatéral ; bilatéral pour l'effet du dossier), binomial
    exact (k critique par effectif), plafond de Spearman 0,751, Bradley et Terry avec effet de position (crêtes 0,5 et 0,5),
    tables de puissance (graine 20261102, 20 000 répétitions) et plan joué (60 graines par ligne).

## 10. Incidents, écarts et réserves

- Banc 1 : une survivante et une mutation tuée pour une autre raison (section 6), corrigées ; motif élargi après lecture, déclaré.
- Le patch a été appliqué dans la copie de travail (sur l'un des quatre fichiers permis), puis le fichier réécrit.
- Une première course à blanc a écrit dans `/tmp/jv2-blanc-1` ; supprimée ; les suivantes écrivent sous le bloc-notes.
- Les courses à blanc écrivent, comme le lanceur le fait toujours, leurs propres sceaux `.sha256` dans leur dossier de sortie, sous
  le bloc-notes ; aucun fichier `.sha256` dans le dépôt.
- La machine a redémarré vers 01:07 UTC le 3 novembre (processus 1 neuf, `uptime` d'une minute à 01:08 UTC) ; après, aucun
  processus Python n'était visible. Rien n'a été fait sous `/home/claude/ideation-organism/` ; l'état de la course décisive qui y
  tournait n'a pas été vérifié ici.
- `registres/decisions.md` du dépôt de travail a changé pendant la session (empreintes en section 1) ; les lignes citées sont
  inchangées.
- Les matériaux « mondes-brouillon1 » reconstruits par ce code (artefact des essais, `f4ff3485…`) ne sont pas octet pour octet ceux
  du brouillon 1 (`c3eeb559…`) : mêmes dossiers et mêmes classes, cinq champs de texte différents (écarts écrits arrondis comme
  les taux affichés, seuils de deux prédictions, « dix » au lieu de « 10 » dans les deux textes longs) et les étiquettes de
  contrôle ; l'artefact reste refusé pour les mêmes raisons.
