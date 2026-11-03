# Rapport de rédaction — préenregistrement du tour fermé, brouillon 6, et code `_v64`

Rédigé du 2 novembre 2026, 23:30 UTC, au 3 novembre 2026, 00:50 UTC (heures de `date -u`), par un sixième sous-agent
rédacteur-développeur, **développeur neuf** : il n'a écrit ni le code du tour fermé (`_v60` à `_v63`), ni l'étage des tests de mort,
ni les préenregistrements du tour fermé, ni leurs contre-lectures. Travail dans la seule copie isolée `/home/claude/wt/tour-ferme-v64/`
(dossier `orchestrator/`, tête `66dbcf1`, arbre sans autre changement) ; brouillons et sorties dans `/home/claude/scratch/tour-ferme-v64/`.
Aucun commit, aucun `git fetch`, `checkout`, `stash` ni `reset` ; aucun fichier existant modifié (`git status` : sept fichiers neufs non
suivis, aucun fichier suivi modifié) ; rien sous un dossier `donnees/` ; aucun appel de réseau ni de modèle ; Python par
`nice -n 10 python3 -I -B`, pytest avec `-p no:cacheprovider`, `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1` ; banc complet joué deux fois,
jamais en même temps qu'une suite d'essais. Aucun fichier `.sha256` écrit dans le dépôt ; seuls en ont écrit, hors du dépôt, les
sorties scellées des courses à blanc (dossier de travail) et les aides d'essai du pôle (dossiers temporaires retirés).

## 0. Verdict

- **Code `_v64` écrit, essayé, banc tué à 100 %** : sept fichiers neufs (section 10), la v63 et tout module partagé intacts.
  **TF-02, option (a)** : un code 4 dont la dernière ligne porte `"envoye": false` est lu « budget_depasse » pour cette session — fin
  des tours de la carte pour ce rôle, rien compté, jamais « erreur » ni arrêt — ; tout autre code non nul garde sa lecture. **Point 2** :
  le barème prudent de chaque commande (prix d'entrée par million de jetons, clé neuve de la configuration, trois caractères par
  jeton, aucun défaut) est passé à l'étage pour l'expérimentateur (la vérification préalable de `pole/tests_de_mort_v5.py` l. 468
  joue) et appliqué au vérificateur. **Durée : 72 heures** (décision de Lazar, R-1294, transmise par le coordinateur), gelée dans le
  code et au plan, toute autre durée refusée en mode décisif.
- **Essais : 108 (87 + 21), 107 réussis, 1 sauté par construction** (`BacReelV64` : `bwrap` absent ici, `POLE_ESSAI_BAC_REEL_NON_JOUE=1`),
  66 sous-essais réussis, 143,9 s. **Banc : 91 mutations** (72 de la v63 portées, 19 neuves) ; premier passage 90 tuées pour la raison
  attendue et 1 pour une autre raison (aide d'essai corrigée, section 5) ; **second passage 91 tuées sur 91 pour la raison attendue (aucune pour une autre raison, aucun défaut du banc, aucune survivante ; témoin de 101 essais sans échec avant et après ; 572 s)**.
- **Courses à blanc dans le bac factice** (sans `bwrap`), aux conditions du plan, racine 20261102 : code 0, 92,3 s, « tient », A4
  « discrimine » ; seconde course avec « rien envoyé » au tour 2 de chaque carte et à chaque session du vérificateur : code 0, 77,3 s,
  « tient », 60 sessions « rien envoyé », aucun arrêt. Le vrai chemin `--verifier-seulement` accepte le texte du brouillon 6 (cases
  remplies de valeurs d'essai) : « conforme ».
- **Mesures (point 3)** : la consigne du vérificateur **peut dépasser** les ≈ 27 000 caractères que 0,10 USD paie avec une sortie
  minimale de 200 jetons (26 822 avec trois sorties ordinaires pleines, 40 322 avec des sorties faites de fins de ligne, 94 322 avec
  des caractères de contrôle) ; en v64 son témoin est alors « non concluant », jamais un arrêt. **Proposition, non faite** : borne du
  vérificateur à 0,15 USD par carte, parts 42 et 8 USD (section 7).
- **Brouillon 6** : `prereg/preenregistrement-tour-ferme-v1-brouillon6.md` (889 lignes, sha256 `cdcb44706e7b3c62ccd028680cf633c1651a56a93d7de129449150b47b45aef5`) = brouillon 5 + couples
  T101 à T112 + 69 couples v64 + bloc d'empreintes de 92 fichiers. **Trois marqueurs restent** hors des zones de l'étage 2 :
  `<<CASE_CONFIGURATION_V3>>`, `<<COMMANDES_V3>>`, `<<PRECISION_GO_23>>`.
- **Réserve principale** (section 11, point 1) : un code 4 « rien envoyé » venu d'une limite propre du relais (402, 429) est lu de
  même ; chaque carte suivante finirait sans tour (« non concluant ») au lieu d'un arrêt. Remède écrit au texte (A.6 bis : constat de
  la session-depot) ; une distinction dans le code demanderait que les commandes v3 disent la cause.

## 1. Entrées lues (empreintes vérifiées)

| fichier | sha256 |
|---|---|
| consigne : `…/prompts-sous-agents/tour-ferme-v64-developpeur-brouillon6-prompt.md` (lue en entier ; elle fait foi) | — |
| `prereg/preenregistrement-tour-ferme-v1-brouillon5.md` (871 lignes, lu en entier) | `c81aa6ef72255adab76abcffc8e06cc0c570069cf09aa2035c285a54212fc3d3` |
| `prereg/contre-lecture-courte-preenregistrement-tour-ferme-v5.md` (lu en entier) | `3b525f9e86b239d4e6dd3b3fa8825a67151342f6487138f7ddd07f56e17c9695` |
| `prereg/couples-contre-lecture-tour-ferme-v5.json` (T101 à T112) | `40bb0d178c967b7da7a5109ff402c674ab8e8e2ed09f34efcd93c88125e80474` |
| rapport privé du contre-lecteur (`…/contre-lecture-courte-tour-ferme-b5-rapport.md`, lu) | — |
| `scratch/…/session-depot_2026-11-02_n294.md` (§ 4, TF-01 à TF-06) et `…_n295.md` (§ 3) | lus |
| `scratch/…/configuration-tour-ferme-v3-brouillon1.json` | `109f673c289d91d52dd86094b97085f66149dfd8416a61f2d6d1290eb68dc6bb` |
| `pole/tour_ferme_v63.py`, `demonstrations/tour_ferme_v63.py`, `pole/lecture_tour_ferme_v63.py` (lus en entier) | `9982ae3c…`, `33e4c029…`, `2e2c695a…` |
| `essais/test_tour_ferme_v63.py`, `essais/test_gardes_tour_ferme_v63.py`, `essais/mutations_tour_ferme_v63.py` (lus en entier) | `2e459e76…`, `2cd44645…`, `c8290530…` |
| `pole/tests_de_mort_v5.py` (lu en entier), `pole/adaptateurs.py` (l. 560-778), `pole/adaptateurs_v56.py`, `pole/adaptateur_kimi_v53.py` (en-tête, `lancer`), `pole/etage_entre_generations_v57.py`, `demonstrations/ideation_v8.py` (`adaptateurs_reels_v56`), `demonstrations/attaque_goodhart_v2.py` (l. 195-300) | `da524871…` ; `a1a8ede8…` ; … (égales au bloc du brouillon 5) |

Message du coordinateur reçu pendant le travail (consigné ici, appliqué) : « Lazar a tranché la garde de durée de la course : 72 heures
au lieu de 24 (réponse à ma question du 3 novembre 2026, 00:3x heure de Paris ; registre privé, ligne R-1294) » ; le reste de la
consigne inchangé. La ligne R-1294 n'a pas été lue par moi (registre privé) : la décision est citée telle que transmise.

## 2. Décisions appliquées

| point de la consigne | où dans la v64 | essais (sain ; artefact) | mutations |
|---|---|---|---|
| 1. code 4 « rien envoyé » → « budget_depasse », rien compté, jamais erreur ni arrêt ; tout autre code inchangé | `pole/adaptateur_commande_v64.py` (`AdaptateurCommandeExterneV64.lancer`, `ResultatV64`, `rien_envoye`) ; `pole/tour_ferme_v64.py` (`AdaptateurEtageV64.lancer`) ; lanceur (`AC.commandes_v64` dans `roles_reels`) | `CommandeCode4`, `EtageRienEnvoye`, `EtageV64CommandesReelles`, `CourseRienEnvoye`, `CommandesV64`, `ProposeurRienEnvoye`, `CheminReelVerifierSeulement.test_sain…` | 10 (« F, TF-02 : … ») |
| 2. `prix_caractere_usd` passé à l'étage pour chaque rôle facturé, depuis la configuration (caractères / 3, prix d'entrée par million) | `jouer_etage` (réglage `prix_caractere_usd`, relais de l'expérimentateur) ; `AdaptateurEtageV64` (même contrôle pour le vérificateur) ; `AC.bareme_depuis_configuration` ; lanceur (`roles_reels`, `prix_a_blanc`) | `BaremeDesCommandes`, `VerificationPrealable`, `PrixPasseALEtage`, `CheminReelVerifierSeulement.test_artefact_bareme_absent` | 5 (« G : … ») |
| 3. mesure des consignes ; proposition si le vérificateur dépasse | section 7 ci-dessous | `BaremeDesCommandes` (27 000 caractères) | — |
| 4. aucun module partagé modifié ; fichiers neufs versionnés | sept fichiers neufs (section 10) | `Fermeture` (bloc = fermeture statique, 92) | 72 portées |
| 5. chaque garde neuve : sain et artefact ; une mutation par changement ; mutations v63 portées et tuées | sections 4 et 5 | 108 essais | 91 |
| 6. brouillon 6 | section 9 | `--verifier-seulement` réel sur le texte | — |
| 7. rapport | ce texte | — | — |
| durée 72 h (R-1294, message du coordinateur) | `T.DUREE_ETAGE_1_H` ; `lire_plan` du lanceur ; `A_BLANC` | `DureeR1294`, `CheminReelVerifierSeulement.test_artefact_duree_24_h`, `Garde13DeBoutEnBout.test_sain_duree_par_defaut_72_h`, `SeuilsDeDuree` | 3 (« H : … ») |
| programme de lecture v64 (relevé du cœur v64 seul) | `demonstrations/lire_tour_ferme_v64.py` | `CourseSaine.test_C18_programme_de_lecture` (v62 et v63 refusés) | 1 (« I : … ») |

## 3. Ce que change la v64 (le diff v63 → v64 se lit fichier contre fichier)

**3.1 Code 4 « rien envoyé » (TF-02, option (a)).** `AdaptateurCommandeExterneV64` hérite de la commande externe v56 (recopie du modèle
servi, porte « environnement » inchangées) ; il garde la dernière ligne brute de la sortie le temps de l'appel (`lire_derniere_ligne`,
lecture large) et, si la classe gelée rend « erreur » avec le motif « commande externe : code 4 : … » et que la dernière ligne est un objet
JSON dont `envoye` **est** le booléen faux, il rend `ResultatV64("", [], 0.0, "budget_depasse", motif, rien_envoye=True)` ; le coût
déclaré par la commande (un plancher : 10⁻⁶ USD pour le relais Kimi par protocole du pôle, qui lit déjà ce cas ainsi) est dit au motif,
jamais compté. Le code de sortie est lu dans le motif de la classe gelée (`pole/adaptateurs.py` l. 757-764, gelé par son empreinte) ;
l'essai `CommandeCode4` le vérifie sur de vraies commandes locales (trois formes saines : plancher déclaré, coût nul, ni texte ni coût ;
sept artefacts : `envoye` absent, vrai, « false » en texte, `0`, code 3, code 2, refus dit — ce dernier reste « refus », R-764 —,
ligne illisible, sortie 0 ordinaire). `AdaptateurEtageV64` : un « budget_depasse » marqué « rien envoyé » est rendu à l'étage sans
arrêt, sauf part du relais épuisée ; tout autre « budget_depasse » sous le plafond passé reste un arrêt (C13). L'étage v5, inchangé, fait
le reste : expérimentateur → `fin_des_tours` « plafond de la fiche dépassé par la session (statut budget_depasse) », carte jugée sur
ses exécutions ; vérificateur → témoin « non concluant (plafond du lecteur dépassé) ». Au lanceur, `AC.commandes_v64` remplace, après
toutes les vérifications de `ideation_v8.adaptateurs_reels_v56`, les relais Kimi et Argon déclarés `commande_externe` par la v64 (même
commande, modèle servi exigé, mêmes modèles servis permis) et refait leur porte ; une entrée d'un autre type est laissée telle quelle
(Kimi par protocole reste refusé par la garde des rôles, message inchangé de l'annexe A, A.6).

**3.2 Barème passé à l'étage (point 2).** Clé neuve `fournisseurs.<kimi, argon>.prix_entree_usd_par_million_jetons` (réel fini > 0, aucun
défaut, `TourRefuse` sinon, après la garde des rôles et avant toute porte et tout appel) ; prix d'un caractère = prix / 10⁶ / 3. Celui de
Kimi est passé à l'étage (`prix_caractere_usd` dans les réglages de `jouer_etage_v57`, qui les transmet à `executer_tests_de_mort`) : la
l. 468 de l'étage v5 joue (consigne × prix > reste → « tour k : la consigne (… caractères, … USD en entrée seule au prix prudent) dépasse
le plafond restant … : fin des tours, rien envoyé »). L'étage v5 n'a pas ce contrôle pour le lecteur : `AdaptateurEtageV64` le fait pour
tout relais doté d'un prix (pour l'expérimentateur, la condition est celle de la l. 468, qui la voit d'abord ; pour le vérificateur, c'est
le seul contrôle) ; au-delà, rien n'est lancé et la session rend un « budget_depasse » marqué « rien envoyé ». Lecture de « pour chaque
rôle facturé » : expérimentateur par l'étage, vérificateur par l'adaptateur de l'étage ; le proposeur n'est pas dans l'étage (inchangé).
À blanc, options `--prix-entree-kimi-usd-par-million-jetons` et `--prix-entree-argon-usd-par-million-jetons` ; sans elles, contrôle
inactif, dit au manifeste (`prix_caractere_usd_etage` : `None`). Chaque appel de l'étage consigne la taille de sa consigne, le marquage
« rien envoyé » et le contrôle préalable ; chaque appel de proposeur, la taille de sa consigne.

**3.3 Durée de 72 heures (R-1294).** `DUREE_ETAGE_1_H = 72.0` dans le cœur ; `lire_plan` refuse tout plan dont `duree_etage_1_h` ≠ 72
(`PreenregistrementRefuse`, code 2, motif « … le code v64 gèle 72 h (décision de Lazar, R-1294) … ») ; à blanc, 72 h par défaut,
`--duree-max-h` permis (essais de la garde 13). Le seuil par session à 60,7 cartes et témoins testés passe de ≈ 81 s à ≈ 299 s : ≈ 3,7 fois
plus large (le coordinateur écrivait « ≈ 3 fois » : les exécutions du bac, comptées à leur délai, se retranchent de la durée avant la
division, d'où un rapport supérieur à 72 / 24).

**3.4 Noms.** `VERSION` « tour-ferme-v64 » (tâches des graines, relevé) ; étape `tour_ferme_v64` (porte « environnement » :
`ETAPE_POLE=tour_ferme_v64`) ; dossiers temporaires `bac-tour-ferme-v64-…`, `tour-ferme-v64-sessions-…` ; fiches de l'étage marquées
« tour-ferme-v64 » ; `FICHIERS_GELES` : 92 fichiers, égal à la fermeture statique des imports des deux programmes v64 (essai `Fermeture`),
qui contient la fermeture mesurée pendant une course (`FermetureEnCourse`). Doublures : scénarios « rien_envoye[:N] » (expérimentateur)
et « rien_envoye » (vérificateur, option `--scenario-verificateur`). Programme de lecture v64 : n'accepte que les relevés du cœur v64 ;
la lecture `pole/lecture_tour_ferme_v63.py` est inchangée (aucun critère, aucune issue ne change).

**3.5 Ce que la v64 ne change pas, dit.** Un proposeur qui rend « budget_depasse », « rien envoyé » compris, arrête la course (A.5 ;
essai `ProposeurRienEnvoye`) ; tout code non nul autre que 4 « rien envoyé » reste « erreur » (arrêt) ; le devis et les bornes
(0,80 et 0,1 USD par carte, 50 = 44 + 6 USD) ; les prédictions, critères et issues ; les zones de l'étage 2.

## 4. Essais (heures de `date -u`, 3 novembre)

- **Suites v64**, `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B -m pytest -q -p no:cacheprovider -rs
  essais/test_tour_ferme_v64.py essais/test_gardes_tour_ferme_v64.py` : premier passage 00:02:46 → 00:05:12 (107 réussis, 1 sauté,
  66 sous-essais, 145,6 s) ; après la correction de l'aide d'essai (section 5), **00:26:13 → 00:28:38 : 107 réussis, 1 sauté
  (`BacReelV64`, « ESSAI RÉEL NON JOUÉ »), 66 sous-essais réussis, 143,9 s** ; aucun dossier `tour-ferme-v64-*`, `essai-v64-*` ni
  `bac-tour-*` resté sous `/tmp`. Collectés : 87 et 21.
- **Portés** (68 + 19) : tous les essais v63, mêmes classes et mêmes noms, sur le code v64 (`EtageV63` devient `EtageV64` ; plan d'essai
  à 72 h ; `CourseSaine` vérifie relevé et manifeste v64 ; le programme de lecture refuse les relevés v62 **et** v63 ; `Fermeture` : 92
  fichiers, aucun fichier v63 hors la lecture).
- **Neufs** (19 + 2), chacun sur un cas sain et un artefact : `CommandeCode4` (2), `EtageRienEnvoye` (2), `EtageV64CommandesReelles` (2 :
  de vraies commandes locales ; artefact v56 → `EtageInterrompu`), `CourseRienEnvoye` (2 courses à blanc), `ProposeurRienEnvoye`,
  `CommandesV64`, `BaremeDesCommandes`, `VerificationPrealable`, `PrixPasseALEtage` (3 : espion des réglages, prix d'essai, prix qui fait
  tout mordre), `DureeR1294` (2), `CheminReelVerifierSeulement.test_artefact_bareme_absent` (3 sous-cas) et `.test_artefact_duree_24_h` ;
  `Garde13DeBoutEnBout.test_sain_duree_par_defaut_72_h` et `SeuilsDeDuree` (gardes).
- Les essais v63 ne portent que sur le code v63 (inchangé) ; ils n'ont pas été rejoués.

## 5. Banc de mutations (`essais/mutations_tour_ferme_v64.py`, deux passages complets)

- **Premier passage**, 00:13:57 → 00:22:02 : 91 mutations ; **90 tuées pour la raison attendue, 1 tuée pour une autre raison**, 0 défaut
  du banc, 0 survivante ; témoin 101 essais, 0 en échec avant et après ; 484 s. La mutation en cause, portée de la v63 : « garde des
  rôles retirée au lanceur ». Sans la garde des rôles, la configuration d'essai « Kimi par protocole » était refusée plus loin par la
  garde neuve du barème (clé absente de l'entrée Kimi par protocole) : code 2, autre motif. Correction (aide d'essai seulement,
  `preparer_chemin_reel`) : la clé du barème est portée aussi par l'entrée Kimi par protocole, inerte pour elle, pour que la garde des
  rôles soit la seule à refuser cet artefact ; rejoué seul (`--seulement "garde des rôles"`, 00:22:42 → 00:22:46) : 2 sur 2 tuées pour
  la raison attendue.
- **Second passage**, 00:38:37 → 00:48:10 : **91 mutations, 91 tuées pour la raison attendue**, 0 pour une autre raison, 0 défaut du banc, 0 survivante, 0 non appliquée ; témoin 101 essais, 0 en échec avant et après ; 572 s ; code 0 ; empreintes des sept fichiers v64 relevées au lancement, égales à celles de la section 10.
- **Mutations neuves (19)** : F, TF-02 — code 4 non lu ; `envoye` non exigé faux ; tout code non nul lu « rien envoyé » ; coût déclaré
  compté ; session non marquée ; marque jamais reconnue ; arrêt de l'étage sur un « rien envoyé » ; part épuisée ignorée ; relais restés en
  v56 au lanceur ; porte non refaite — G — prix non passé à l'étage ; vérification préalable du vérificateur retirée ; 4 caractères par
  jeton ; barème absent accepté au lanceur ; prix invalide accepté — H — vérification du plan neutralisée ; constante ramenée à 24 h ;
  défaut à blanc ramené à 24 h — I — programme de lecture qui lit les relevés v63. Sous-ensembles mis au point avant (00:08:57 →
  00:13:05) : 19 sur 19 tuées pour la raison attendue.
- **Portées (72)** : mêmes fragments que la v63, sur le code v64 ; une seule réécrite, « C13 : « budget_depasse » d'un relais pris pour le
  plafond de la fiche », dont le fragment est la condition d'arrêt de `AdaptateurEtageV64` (`if part_epuisee or (not rien and cout < …):`).

## 6. Courses à blanc (bac factice, sans `bwrap`) et chemin réel jusqu'à `--verifier-seulement`

- **L2b-v64-b6**, `TMPDIR=/tmp POLE_ESSAI_BAC_REEL_NON_JOUE=1 nice -n 10 python3 -I -B demonstrations/tour_ferme_v64.py SORTIE --etage 1
  --a-blanc --graine 20261102 --bac factice --prix-entree-kimi-usd-par-million-jetons 10 --prix-entree-argon-usd-par-million-jetons 10`,
  00:23:02 → 00:24:34 : **code 0, 92,3 s** ; lecture par `demonstrations/lire_tour_ferme_v64.py … --releve-sha256` à 00:24:46 : **« tient »,
  A4 « discrimine »**, T1 à T5 tenus ; réel jugées/PS/VD/FD/refus [36, 12, 12, 0, 0], aléatoire [36, 0, 0], recopie [24, 0] ; 30 cartes et
  témoins testés (12 cartes réelles en génération 1, 18 passes de témoins), 0 « non concluant », 30 contre-calculs concordants ; S1
  déclenché (doublures voisines de L*, attendu à blanc), S2 et S5 non ; touches de L* 0 sur 6 contextes, lignes de tranche 0 ; aucune
  vérification préalable ni session « rien envoyé » ; relevé `13b0e20ac95f14f75462efc3016a0eceacd7deb532914fc433cb23c66b075462`, manifeste
  `4d3f4522c942e7f2ece02ef7325809b9da2010f09c2291b4bc083ed8586ebbec` (92 empreintes de code égales au disque et au bloc du brouillon 6),
  lecture `3dd8517cb8f98b5ee2ece3f613268410ea033cca57069bda9901ca6072f144c4`. Les comptes diffèrent de L2b-v63-b5 à la même racine :
  les tâches des graines portent « tour-ferme-v64 » (autres tirages ; le bras aléatoire n'a aucune PS en génération 1, cas que P4 donne à
  ≈ 0,21).
- **Seconde course**, mêmes conditions plus `--scenario-experimentateur rien_envoye:2 --scenario-verificateur rien_envoye`, 00:28:55 →
  00:30:13 : **code 0, 77,3 s, « tient », A4 « discrimine »** ; 90 sessions de l'étage dont **60 « rien envoyé »** (30 d'expérimentateur
  au tour 2, 30 de vérificateur), coût 0, **aucun arrêt** ; 30 testés (20 « survit », 10 « éliminée », 0 « non concluant ») ; relevé
  `7cf91149046adbfd7c41f84cad4381906598ecb64721f5ab727c49decd5f6be7`, lecture `9333bbd3821ee5e773ae247d4da65b224cd5df81331ae9805d312a85add662dc`.
- **Vrai `principal` jusqu'à `--verifier-seulement` sur le texte du brouillon 6** (script `verifier_seulement_b6.py`, 00:38:14 → 00:38:16 sur le texte candidat, rejoué de 00:50:12 à 00:50:13 sur le texte déposé, mêmes résultats ;
  copie du texte nommée `preenregistrement-tour-ferme-v1-v1.md` hors du dépôt, cases remplies de valeurs d'essai, configuration d'essai
  des essais v64 à 50 USD, registre d'essai GO-2026-11-02-23 à 50 USD, environnement vidé, sonde du bac remplacée par l'exécuteur
  factice, **sceau simulé en mémoire**, aucun `.sha256` écrit pour ce texte) : **code 0, « conforme »** (garde 6 complète : 92 empreintes
  égales au disque, plan 72 h soit 259 200 s, 50 = 44 + 6, entropie ≥ 2⁶⁴ ; barème lu ; relais Kimi et Argon en commande externe v64) ;
  artefacts, code 2, rien écrit, aucun dossier temporaire : cases `<<COMMANDES_V3>>` et `<<PRECISION_GO_23>>` laissées (« marqueur(s) non
  rempli(s) hors de l'étage 2 ») ; plan à 24 h (« … gèle 72 h (décision de Lazar, R-1294) ») ; barème de Kimi absent.
- **Non joué** : aucune course dans le vrai bac (`bwrap` absent de cette machine ; l'identité dédiée sert à la course décisive en cours
  ailleurs) ; `BacReelV64` sauté avec son motif.

## 7. Mesures (point 3 de la décision)

Barème prudent (session-depot, message n° 294, § 4) : trois caractères par jeton ; Argon 10 USD par million de jetons en entrée et 50 en
sortie ; Kimi : sortie minimale 4 096 jetons à 10 USD par million ; **prix d'entrée de Kimi inconnu ici** (10 USD par million pris comme
prix d'essai). Script `mesures_v64.py`, sortie `courses/mesures-v64.json` (dossier de travail).

| consigne | course à blanc L2b-v64-b6 (caractères) | plus grande permise par l'étage (caractères) |
|---|---|---|
| vérificateur (lecteur témoin) | 30 sessions : 8 115 à 8 220 (médiane 8 124) | une exécution, une ligne RESULTAT : 8 233 ; trois exécutions aux sorties ordinaires pleines (3 000 + 1 500 caractères servis chacune) et 20 lignes RESULTAT, loi servie de 2 000 caractères : **26 822** ; mêmes sorties faites de fins de ligne (échappées en 2 caractères) : **40 322** ; de caractères de contrôle (6 caractères) : **94 322** ; 2 000 fichiers produits aux noms de 200 octets : ≈ 1 268 774 |
| expérimentateur | 60 sessions : 10 591 à 12 072 (médiane 11 272) ; premier tour, loi maximale : 12 519 | `consigne_experimentateur_maximale` (historique au quota servi) : 393 422 |
| proposeur | 6 sessions : 13 519 à 15 736 | — |

- **Vérificateur** : 0,10 USD paie, avec une sortie minimale de 200 jetons, **≈ 27 000 caractères** (15 000 avec la sortie minimale de
  1 000 jetons des commandes v2 ; 30 000 en entrée seule, seuil du contrôle préalable de la v64). **Oui, la consigne du vérificateur peut
  le dépasser** : il faut 0,0994 USD pour 26 822 caractères (au bord), 0,1444 USD pour 40 322, 0,3244 USD pour 94 322. En v64, le
  dépassement ne coûte que le témoin (« non concluant », jamais décisif), sans arrêt ni dépense.
  **Proposition (non faite)** : relever la borne du vérificateur à **0,15 USD par carte** (≈ 42 000 caractères au barème, sortie de 200
  jetons) avec des parts **42 et 8 USD** ; rejeu du devis sur le `Compteur` gelé (fonction `jouer_devis`, borne posée en mémoire) :
  20,7 cartes testées de plus que le devis tiennent encore, même si chaque session du vérificateur atteint sa borne (23,2 aujourd'hui ;
  à 0,15 USD avec 44 et 6 : 7,8 seulement ; à 0,35 USD, le partage 44 et 6 ne tient plus aux tailles du devis si le vérificateur atteint
  sa borne). Prix : code `_v65` (constante du cœur), plan et devis du texte, essais et banc, contre-lecture. Recommandation : ne pas
  relever (le témoin n'est jamais décisif et la v64 retire l'arrêt), sauf si Lazar tient au témoin pour les sorties longues (confiance
  moyenne). Une borne des noms de fichiers produits servis au lecteur relèverait de l'étage v5 (code partagé, hors de ce travail).
- **Expérimentateur** : à 10 USD par million en entrée (prix d'essai), la plus longue consigne réelle demande ≈ 0,081 USD avec la sortie
  minimale de 4 096 jetons : la commande refuserait en code 4 les derniers tours d'une carte dont le reste tombe sous ce montant ; en v64
  c'est une fin des tours, la carte jugée sur ses exécutions.
- **Proposeur** : 0,50 USD paie ≈ 135 000 caractères au barème d'Argon (≈ 137 700 pour Kimi au prix d'essai) ; consignes réelles
  ≤ 15 736 : marge ≈ 8,6.

## 8. Devis

Inchangé par la v64 (section 12 du brouillon 6) : une session « rien envoyé » ne coûte rien, la vérification préalable ne fait qu'arrêter
des tours, bornes et parts inchangées. Rejoué sur le `Compteur` gelé par `DevisI30` (essais v64, réussis) : 2 tours (0,04 USD) Kimi 2,61,
Argon 0,71, total 3,31 USD ; 4 tours 8,39 ; 6 tours 12,19 ; 8 tours 15,99 ; **12 tours 23,60** (Kimi 22,90, marge 20,91) ; chaque carte à
sa borne **26,14** ; 23,2 cartes de plus à leur borne tiennent encore (54,9 testées), 29 de plus à 12 tours au prix du devis (60,7) ; au-delà,
arrêt avant l'étage, code 3, sans dépassement. Durée de 72 h, seuils par session (essai `SeuilsDeDuree`) : 12 tours aux tailles du devis
≈ 593 s (24 h : ≈ 179) ; 54,9 testés ≈ 333 s (≈ 93) ; 60,7 testés ≈ 299 s (≈ 81) ; 3 tours ≈ 1 866 s (≈ 565). Ligne GO-2026-11-02-23 : elle
cite `af92034` et « ≈ 3,3 à 12 USD » ; une ligne de précision du directeur humain est attendue (case `<<PRECISION_GO_23>>`).

## 9. Brouillon 6 : construction et contrôles

- **T101 à T112** appliqués dans l'ordre au brouillon 5 par `appliquer_t101_t112.py` puis par `construire_brouillon6.py` : chaque « ancien »
  présent une fois dans le brouillon 5 et une fois à son application ; texte obtenu 873 lignes (`2ded3ee9…`), comme l'annonçait la
  contre-lecture.
- **69 couples v64** (V01 à V69), chacun appliqué avec son nombre d'occurrences exigé (un pour tous), aucun dans une zone de l'étage 2 ;
  consignés, rejouables, dans `/home/claude/scratch/tour-ferme-v64/brouillon6/couples-v64-brouillon6.json` (sha256 `4c1b03cbec8fe65c891aad5074abd3cc87926af69c6db88aad2bea88f0668d42`) ;
  V21 remplace le paragraphe « Essais v63 de l'étage 1 … » entier. Contenu : titre, statut (décision citée, R-1294, rédaction), section 0
  (changements du brouillon 5 au brouillon 6, sept points), sections 1, 4.1, 4.3, 4.6, 7 (gardes 5, 13, 14 ; **garde 16 neuve** ; paragraphe
  des essais), 8, 9, 10 (ligne L2b-v64-b6), 10 bis, 12 (borne, prix de la borne, vérificateur et mesure, proposeur, durée et seuils), 13
  (code `_v64`, commandes v3, clé du barème, plan `duree_etage_1_h: 72`, empreintes), 14 (points 1, 2, 4, 6) et annexe A (A.1, A.4 à A.9 ;
  clé neuve du barème en A.6 ; A.6 bis mis à la v64).
- **Bloc d'empreintes** recalculé sur la copie de travail dans l'ordre de `FICHIERS_GELES` : 92 lignes ; 88 égales au bloc du brouillon 5
  et à `git show 66dbcf1:` ; 4 neuves (`demonstrations/tour_ferme_v64.py`, `demonstrations/lire_tour_ferme_v64.py`, `pole/tour_ferme_v64.py`,
  `pole/adaptateur_commande_v64.py`) ; 3 sorties (les fichiers `_v63` du cœur, du lanceur et du programme de lecture).
- **Contrôles** : sept zones de l'étage 2 identiques à l'octet à celles du brouillon 5 ; marqueurs hors des zones : exactement
  `<<CASE_CONFIGURATION_V3>>` (plan gelé), `<<COMMANDES_V3>>` (section 13), `<<PRECISION_GO_23>>` (section 14, point (6)), une fois chacun ;
  plan relu par `lire_plan` du lanceur v64 (case remplie d'une valeur d'essai) : 72 h, 50, 44, 6, GO-2026-11-02-23 ; garde 6 complète et
  `--verifier-seulement` réel : section 6.

## 10. Fichiers neufs et empreintes (depuis `orchestrator/`, `sha256sum`)

| fichier | lignes | sha256 |
|---|---|---|
| `pole/tour_ferme_v64.py` | 1 386 | `35a8294e24c870685435b990d6c03cd33cb5b2e288bcb2cc91cd9af04679c2da` |
| `pole/adaptateur_commande_v64.py` | 174 | `adb7328721342601eb487856840e385493e6e35c522c90d804a4f8c96bfb5700` |
| `demonstrations/tour_ferme_v64.py` | 523 | `98c1a1a205cfe58ec277b64fbf4778e567246cfb1f0cc6882c1071704c01ae01` |
| `demonstrations/lire_tour_ferme_v64.py` | 80 | `393b17cc859a634036778cab364c5fb2ae2ff1aa7c34ddec27b2246732b9952b` |
| `essais/test_tour_ferme_v64.py` | 1 879 | `5227916338c1e51e05dd777821ff0b87ce14d1ca0246da35c56979ed1a3abe36` |
| `essais/test_gardes_tour_ferme_v64.py` | 392 | `d6e6535e33d8a88681b2c47384773a212779b940054b4cd13a52ee1dc1d33073` |
| `essais/mutations_tour_ferme_v64.py` | 342 | `5066ada268dafc1519b30708c3bfa5c855833e82d81696fbda58965c2894a908` |
| `prereg/preenregistrement-tour-ferme-v1-brouillon6.md` | 889 | `cdcb44706e7b3c62ccd028680cf633c1651a56a93d7de129449150b47b45aef5` |
| `prereg/rapport-redaction-tour-ferme-v6.md` | ce texte | (dans la réponse au coordinateur) |

Brouillons de travail (`/home/claude/scratch/tour-ferme-v64/travail/`) : générateurs des essais, du banc et du brouillon 6, couples T,
mesures, vérification du chemin réel ; sorties dans `…/courses/` (deux courses, lectures, journaux des bancs, mesures).

## 11. Réserves et écarts

1. **Code 4 venu d'une limite propre du relais.** La session-depot écrit (n° 294) que la commande lit aussi les refus 402 (plafond du
   relais) et 429 (nombre d'appels) en code 4, rien parti. La v64 les lit comme la consigne le veut : fin des tours de la carte pour ce
   rôle. Si une telle limite mordait en cours de course, chaque carte suivante finirait sans tour (« non concluant ») et la lecture
   rendrait « ne tient pas (T2 ou T4) » au lieu d'un arrêt (essai `CourseRienEnvoye.test_tour_1_…` : code 0, cartes « non concluant »,
   n1 = critère). Remède écrit au texte (A.6 bis : plafonds des relais ≥ leurs parts, nombre d'appels ≥ 1 731 et 147, aucun autre usage
   des relais pendant la course). Distinguer dans le code exigerait que la dernière ligne des commandes v3 dise la cause (par exemple
   « plafond de session » contre « plafond du relais ») : décision à prendre avec la session-depot.
2. **Rien en vrai bac.** Courses à blanc dans le bac factice seulement, comme la consigne le demande ; la ligne de la section 9 « à rejouer
   dans le vrai bac avant le scellement » le dit.
3. **Code de sortie lu dans un motif d'erreur** (« commande externe : code N : … ») de la classe gelée, plutôt que dans le processus :
   couplage tenu par l'empreinte de `pole/adaptateurs.py` et par des essais sur de vraies commandes ; l'autre voie (recopier `lancer`)
   dupliquait la gestion des processus.
4. **« Pour chaque rôle facturé »** lu ainsi : expérimentateur par l'étage (l. 468), vérificateur par l'adaptateur de l'étage v64 (l'étage
   v5 n'a pas de contrôle pour le lecteur) ; proposeurs hors de l'étage, inchangés (un code 4 d'un proposeur reste un arrêt).
5. **« Rien compté »** : 0 USD compté ; la commande, elle, peut inscrire son plancher (10⁻⁶ USD) dans son registre cumulé : écart
   négligeable, dit au motif de chaque session.
6. **Clé neuve de configuration** : la configuration v3 brouillon 1 (`109f673c…`) ne la porte pas (vérifié : `BaremeAbsent` pour Kimi et
   Argon) : la v64 la refuserait, code 2 ; la session-depot doit l'ajouter avec le prix d'entrée exact du barème de chaque commande v3.
7. **Étape renommée** `tour_ferme_v64` : une commande qui contrôlerait `ETAPE_POLE` doit l'accepter (A.6 bis le demande).
8. **Aide d'essai corrigée entre les deux passages du banc** (section 5) : seul `preparer_chemin_reel` a changé (clé du barème aussi sur
   l'entrée Kimi par protocole) ; aucun code gelé n'a changé entre les deux passages (empreintes relevées au lancement du second).
9. **Décisions citées telles que transmises** : « TF-02, options (a) et (c), décision du directeur, 3 novembre 2026 » (consigne) et
   R-1294 (message du coordinateur) ; ni le registre privé ni la ligne R-1294 n'ont été lus par moi.
10. **Barème de Kimi inconnu ici** : les montants de l'expérimentateur et du proposeur de Kimi sont donnés au prix d'essai de 10 USD par
    million en entrée.

## 12. Les dix points qu'une contre-lecture courte neuve doit vérifier en premier

1. **Lecture du code 4** (`pole/adaptateur_commande_v64.py`, `AdaptateurCommandeExterneV64.lancer`) : seul un code 4 avec `envoye` égal au
   booléen faux devient « budget_depasse » ; le code lu dans le motif de `pole/adaptateurs.py` l. 757-764 ; essais `CommandeCode4` (sain,
   sept artefacts) et mutations « F, TF-02 » 1 à 6.
2. **Arrêts gardés** (`AdaptateurEtageV64.lancer`, condition `part_epuisee or (not rien and cout < …)`) : un « budget_depasse » non marqué
   sous le plafond passé et la part épuisée arrêtent toujours ; rien d'autre n'est assoupli que le cas marqué.
3. **Limites propres des relais** lues en code 4 (réserve 1) : suffit-il d'A.6 bis, ou faut-il une cause dans la dernière ligne des
   commandes v3 et une lecture qui arrête la course sur une limite du relais ?
4. **Barème passé à l'étage** : `jouer_etage` → réglage `prix_caractere_usd` → `jouer_etage_v57` → `executer_tests_de_mort` l. 468 (essai
   espion `PrixPasseALEtage`) ; contrôle du vérificateur dans l'adaptateur de l'étage ; trois caractères par jeton ; aucun défaut.
5. **Clé neuve `prix_entree_usd_par_million_jetons`** : refus avant toute porte et tout appel (code 2), ordre des gardes (rôles, puis
   barème), annexe A, A.6 ; la configuration v3 définitive doit la porter (`<<CASE_CONFIGURATION_V3>>`).
6. **Durée de 72 h** : constante, `lire_plan` (toute autre durée refusée en mode décisif), défaut à blanc ; seuils de la section 12
   (≈ 593, 333, 299 et 1 866 s ; ≈ 3,7 fois à 60,7 testés) contre `SeuilsDeDuree`.
7. **Brouillon 6 rejoué** : brouillon 5 + T101 à T112 + V01 à V69 (`couples-v64-brouillon6.json`) + bloc → texte identique à l'octet ;
   zones de l'étage 2 inchangées ; aucun couple ne change une prédiction, un critère ou une issue ; garde 16 neuve en section 7.
8. **Bloc d'empreintes** (92) contre le disque, `FICHIERS_GELES` et la fermeture statique (`Fermeture`, `FermetureEnCourse`) ; 88 égales à
   `66dbcf1` et au brouillon 5.
9. **Mesure du vérificateur** (section 7) : la consigne peut dépasser ≈ 27 000 caractères ; vérifier qu'un témoin « non concluant » ne pèse
   sur aucun critère ni audit de la lecture v63, et trancher la proposition de borne à 0,15 USD (parts 42 et 8).
10. **Cases restantes et chemin réel** : `<<CASE_CONFIGURATION_V3>>`, `<<COMMANDES_V3>>` (commandes v3 : rôles de l'étage, sortie minimale
    par rôle, `envoye` faux en code 4, `ETAPE_POLE=tour_ferme_v64`), `<<PRECISION_GO_23>>` ; une course à blanc v64 dans le vrai bac et un
    `--verifier-seulement` sur le texte scellé restent à jouer chez la machine qui lance.
