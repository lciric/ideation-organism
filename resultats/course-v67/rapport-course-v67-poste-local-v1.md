# Rapport de course — course réelle de l'organisme (code v67, configuration v8, GO-2026-11-12-06), session du poste local — v1

**Troisième tentative sous ce dessin (deux arrêts C5 avant, sous GO-2026-11-10-11 : relevés `c9c6212b…` et `5a7fc27c…`) ; les
trois relevés se rapportent ensemble (R4).**

Session fille du poste local de Lazar, sous la consigne `docs/notes/organisme-boucle-reelle-v1/course-v67/consigne-poste-local-course-v67-v4.md`
(`7349680b53aa3da0ec68ae3ac1fdc2d89ed51eee0c42d53403e16c73938ba7be`, compagnon OK) et le texte scellé v2
`preenregistrement-boucle-reelle-organisme-v1-v2.md` (`80fe4f03b4905b2376b8cd16873c9ab93da3b97e4e01a9a2932be329bab0954d`, compagnon OK).
Heures relevées par `date -u`. L'issue n'est pas jugée ici : la phrase rendue est recopiée sans commentaire ; le verdict (R13)
revient à un agent neuf de la session mère.

## En une ligne

Lanceur : **code 0**, relevé complet, deux générations jouées, aucun arrêt, aucun incident au relevé ; lecture code 0.

## Phrase rendue par le programme de lecture

> Issue C1 : « la chaîne garde (classe couverte, ce monde, cette taille) » — course reel (decisif) (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte).

## Consigne : deux remarques

- L'en-tête de la consigne v4 dit encore « Statut : brouillon 1, non exécutable » ; le fichier porte pourtant son nom final
  (`…-v4.md`), l'empreinte donnée par la mère, et sa section « Marqueurs » dit « Tous remplis par la session mère (R-2430) ;
  version exécutable ». Lu comme un en-tête non mis à jour ; signalé à Lazar avant toute dépense.
- La consigne est arrivée par un message de la session mère ; **la dépense a été engagée sur le « go » explicite de Lazar dans la
  session du poste** (question posée après la préparation sans dépense ; réponse : « Go, lance la course »).

## Dépôt, routine, arbre (sans dépense)

- Clone neuf sous Linux (objets empruntés à l'ancien clone puis dissociés : `alternates` absent), identité `poste-local` /
  `poste-local@invalid` pour ce clone seulement ; branche `donnees/course-organisme-v67-poste-local-v1` partie de `origin/main`
  à `c68f13b4bc99c704f88e030ce5123de5ba0ca37d`. Bac à sable neuf (`<bac>` = un dossier neuf du poste, hors du dépôt, distinct de celui des courses v66).
- Routine : `sha256sum -c sha256sums-lancement-v2.txt` → 3 OK, code 0 ; **`verifier-arbre` non lancé** (précaution 3).
- Chaîne reconstruite sur le poste : base publique `94bfd92` → paquet v65 `4660197e…` (tête `cef5ea60`) → paquet v66 `84ab119f…`
  (tête `7e415cba`) → paquet v67 `8bfcd5936285da8bae2a57ff9e72c82950e21b370af01a7fcb90f8d018179cab` (tête **`ab53b7f482df5149d9f672f40e04220dffb4173a`**) ;
  `git bundle verify` « okay » pour les trois ; 497 fichiers, arbre propre ; **99 empreintes sur 99** égales au bloc
  `empreintes-du-code-v67` du texte v2.
- Charge : configuration v8 `eb6262890927bfc351bf2a32c21d0dcf121445256a5ebe6c4eaee70b9265b31d`, héritage `93dcf517…` et compagnon,
  relais Kimi `d54ed2bc…`, collisionneur v7 `c9725f02…`, texte v2 ; tous les compagnons OK ; archive `793981cf…`.

## Serveur

| point | valeur |
|---|---|
| inventaire avant (14:01:30Z) | 0 serveur, 0 clé SSH |
| identifiant | **175834755**, `organisme-v67-course`, cpx32, debian-13, **hel1** ; commande citant `GO_ID=GO-2026-11-12-06` ; étiquette `go=GO-2026-11-12-06` |
| création | 2026-11-12T14:01:34Z (API) |
| fiche | `course-v67/poste-local-serveur-v1.md` poussée à 14:01:45Z (commit `2744efaed`) **mais vide (0 octet)** : une erreur de substitution du gabarit de l'interpréteur a vidé le fichier avant son scellement ; l'identifiant figure dans le message du commit. Fiche complète versée sous un nom neuf, `poste-local-serveur-v1-bis.md`, poussée à 14:02:27Z (commit `c64603cff`, 53 s après la création), contenu contrôlé avant le commit. La fiche vide n'est pas réécrite (R12). |
| prix | 0,05772 EUR/h TTC (`server_types`, hel1) ; IPv4 primaire 0,00096 EUR/h TTC (`pricing`) |
| clé SSH jetable | 132525071, supprimée à 17:19:48Z (204) ; partie privée effacée du bac |
| destruction | `DELETE /v1/servers/175834755` à 17:19:27Z, action 667480874417041 « success » à 17:19:43Z ; `GET` → 404 ; aucune IP primaire restée liée ; inventaire après : 0 serveur, 0 clé |
| vie | 14:01:34Z → 17:19:43Z (**3 h 18 min 9 s**) |
| coût | 4 heures entamées × (0,05772 + 0,00096) ≈ **0,235 EUR TTC (≈ 0,27 USD)** |

**Incident de durée** : la course a fini à 15:07:35Z ; les relais (inactifs) et le serveur ont tourné jusqu'à 17:18–17:19Z. Le
poste a perdu son réseau pendant la course (journal de suivi : « Connection timed out » puis « No route to host » répétés),
ce qui a retardé la reprise de la main par la session du poste d'environ deux heures. Sans effet sur la course (exécuteur
détaché sur la machine) ; effet sur le coût de la machine seulement (≈ 0,12 EUR de plus).

## Machine et préalables (section 12.3 du texte v2)

Debian 13 (noyau 6.12.107+deb13-cloud-amd64), 4 cœurs, 7 Go ; `bubblewrap` 0.12.0 ; **Python 3.13.5** ; **numpy 2.2.4** ; pytest
8.3.5 ; utilisateur du bac `bacpole` uid/gid 64097. Arbre `ab53b7f` sur la machine (paquet complet, puis `git bundle verify` des
paquets versés), 497 fichiers, propre ; texte v2 sous `orchestrator/prereg/`, octets égaux, compagnon OK. Préalables et lanceur
joués depuis le **groupe de contrôle racine** (`0::/` vérifié ; précaution 4 ; sonde : « mémoire du bac entier bornée (groupe de contrôle) »).

| # | sortie |
|---|---|
| 1 | 14:03:20Z → 14:08:51Z, **code 0**, « 407 passed, 6 skipped » (dix fichiers). Motifs (`-rs`) : `test_boucle_reelle_v66.py:899` « vrai registre absent : non joué » (×2) ; `test_registre_go_v66.py` l. 104 (garde de calcul du dépôt de travail absente), l. 181 et 190 (vrai registre absent) ; `test_boucle_reelle_v65.py:531` (artefact « `bwrap` absent », injouable où `bwrap` est présent). **Aucun essai du vrai bac sauté.** |
| 2 | 14:08:51Z → 14:14:07Z, **code 0**, « 151 tuées pour la raison attendue sur 151 mutations » |
| 3 | 14:14:07Z → 14:14:25Z, **code 0** (`boucle_reelle_v67.py --a-blanc --graine 20261110 --bac reel --utilisateur-bac 64097`) ; étages « factice : faux » (2 au relevé, 2 au journal) ; lecture code 0, C1 à blanc (`98b598f7fe9e2d5902ee82c0c54d519c3834abde1105b966b37d479307ab2d4c`) |
| 4 | `registres/go.md` de `main` (`549588593ae0bed37a9fac1a4e7ac3d3f138e662`) copié à 14:20:56Z : **`3bef01b574c60dc17cd043efd1aabb43d51b71aeb6dcda6a7d790e42411ce70c`** ; ligne GO-2026-11-12-06 égale à l'octet à la section 13 du texte v2 |
| 5 | 14:21:09Z, **code 0** : « verification : conforme », « ecriture : aucune », « appel : aucun » ; uid/gid 64097 ; garde 24, `delais_v67` : **Kimi adaptateur 7 200 s, commande 7 150 s ; Argon 1 800 s et 1 750 s** ; `SORTIE` non créée |
| 6 | relais Kimi **pid 110065**, port 8804, lancé 14:21:30Z : `--port 8804 --modeles-permis kimi-k3.1-pro --plafond-usd 33 --prix-entree 2 --prix-sortie 10 --prix-cache 2 --max-appels 446 --delai-amont-s 7200 --delai-silence-s 1800 --journal <journal>` ; ligne « prêt » : « délai 7200.0 s, silence 1800.0 s » (`/relais/etat` : `delai_amont_s` 7200.0, `delai_silence_s` 1800.0). Relais Argon **pid 110077**, port 8805, 14:21:31Z : `servir --port 8805 --plafond-usd 7 --max-appels 39 --journal <journal> --collisionneur <collisionneur v7 de la machine> --sha-collisionneur c9725f025407c3ece3e8c16d19cfdfdec078f084a811f0a3b6ea3209be5d98dc`. Clés par l'entrée standard de SSH vers le seul environnement de chaque relais ; écoute sur 127.0.0.1 seulement |
| 7 | `SORTIE_ESSAI` et `SORTIE` frères sous `/root/sorties/` (machine), aucun fragment refusé ; `TMPDIR=/tmp` |

## Lanceur (section 12.4 du texte v2)

- `env -i` (noms permis seulement, `POLE_MACHINE_JETABLE_V56=1`, aucune clé), depuis `orchestrator/`, en superutilisateur :
  `demonstrations/boucle_reelle_v67.py SORTIE --preenregistrement prereg/preenregistrement-boucle-reelle-organisme-v1-v2.md
  --heritage-depart DOSSIER_COURSE/heritage-depart-v65.json --configuration DOSSIER_COURSE/configuration-boucle-reelle-v8.json
  --moteur reel --confirmer-moteur-reel --registre-go CHEMIN/registres/go.md --go GO-2026-11-12-06 --bac reel --utilisateur-bac 64097`.
- `--verifier-seulement`, relais lancés : 14:21:50Z → 14:21:52Z, code 0, « conforme ».
- Course : 14:21:52Z → 15:07:32Z, **code 0**. Relevé (nom écrit par le lanceur : `boucle-reelle-v66.json`) **`21bc75f4d81825695b30b2b32f21feaa91322293f6c2c3161a28dc179ec6df71`** ;
  `arret` nul ; `generations_jouees` [1, 2] ; `complet` vrai ; `incidents` vide ; 23 cartes ; sessions des proposeurs : quatre,
  toutes « ok ». Ce qui précède est recopié du relevé, sans lecture de l'issue.
- Lecture (`lire_boucle_reelle_v66.py SORTIE LECTURE.json --releve-sha256 21bc75f4…`) : code 0 ; `lecture-course-reelle.json`
  `d0ef1ee7667bdc665747c2822dcb031abfea3b38b3094782ad72ae593c016086` ; code « C1 ».
- Dossier des sessions des proposeurs (audit A1) : sur la machine, sous `/tmp/` ; contenu : `proposeur-kimi/` et
  `proposeur-argon/`, chacun avec `boucle-reelle-v66|bras=reel|generation=1/` et `…|generation=2/`, **quatre dossiers vides, aucun
  fichier** (liste donnée ici ; un dossier vide ne se verse pas).

## Dépense

| relais | appels | dépense | détail |
|---|---|---|---|
| Kimi | 30 (tous statut amont 200, `usage` lu pour tous, aucun pire cas compté) | **1,13813 USD** | 87 853 jetons de sortie en tout ; deux appels longs : 14:36:14Z, 861,0 s, 31 891 jetons de sortie dont 30 981 de raisonnement, 0,333476 USD ; 15:07:02Z, 1 098,6 s, 38 343 dont 36 908 de raisonnement, 0,400484 USD ; les autres ≤ 57 s. Journal `6c0f9f57…` |
| Argon | 16 (statut « OK ») | **0,85618 USD** | durée maximale 32,9 s. Journal `c5ae29a0…` |
| **modèles, GO-2026-11-12-06** | 46 appels relayés (8 sessions au compteur du lanceur) | **1,99431 USD** | lanceur : `par_role_usd` proposeur 1,10442, tests de mort 0,88989 ; parts 33 et 7 |
| machine, GO-2026-11-12-06 | | **≈ 0,27 USD** (0,235 EUR TTC) | 175834755, 3 h 18 min |
| **total sous GO-2026-11-12-06** | | **≈ 2,26 USD** | sur 45 |
| à part : GO-2026-11-10-11 | | **≈ 1,19 USD au plus** | courses v66 (rapports `83fd674b…`, `89b97faf…`), **non comptée dans la nouvelle ligne** |
| exposition des deux lignes | | **≈ 3,45 USD au plus** | |

Relais arrêtés **par leur PID** (R10), PID vérifié contre le port : Kimi 110065 à 17:18:32Z, Argon 110077 à 17:18:34Z ; ports libres.

## Pièces rapatriées

Sous `docs/notes/organisme-boucle-reelle-v1/course-v67/poste-local-v1/` (noms neufs, compagnons) : `course-reelle/` (relevé et
manifeste avec les compagnons du lanceur, registre de dépense cumulée, dossiers `generation-1/` et `generation-2/`),
`lecture-course-reelle.json`, `essai-a-blanc/`, `journaux/` (préalables 1 à 5, vérification, lanceur, lecture, sorties et journaux
des deux relais). Archive `75d408631488cc367d6b299e20bc7da366ccb96228781085388ae583294ff892` (égale des deux côtés).
**Aucune clé** : recherche des trois valeurs par descripteur → 0 fichier ; garde des secrets → 0. Correspondance légitime de la
garde des données du poste : le nom du dépôt de travail, champ `depot` du manifeste et des deux sorties de vérification
(3 fichiers, aucune autre ligne) ; texte intact.

## Incidents

1. Fiche du serveur versée vide (voir « Serveur ») ; fiche complète sous un nom neuf.
2. Perte de réseau du poste pendant la course ; machine et relais gardés ≈ 2 heures après la fin (voir « Serveur »).
3. Aucune demande de Lazar hors consigne dans cette session (ni relance, ni borne, ni délai).

## Lignes proposées pour la session mère

- `registres/depenses.md` : `| 2026-11-12 | GO-2026-11-12-06 | Course réelle de l'organisme v67 (configuration v8), poste local : machine Hetzner 175834755 (cpx32, hel1, debian-13), 14:01:34Z → 17:19:43Z (3 h 18 min 9 s) ; ≈ 0,235 EUR TTC (≈ 0,27 USD) | Hetzner |` ; `| 2026-11-12 | GO-2026-11-12-06 | Course réelle de l'organisme v67, poste local : relais Kimi, 30 appels, 1,13813 USD | Kimi (Moonshot) |` ; `| 2026-11-12 | GO-2026-11-12-06 | Course réelle de l'organisme v67, poste local : relais Argon, 16 appels, 0,85618 USD | Argon (Gemini) |`. Total sous la ligne ≈ 2,26 USD.
- `registres/arrets.md` : `| 2026-11-12T17:19:43Z | Hetzner 175834755 | Course v67 (GO-2026-11-12-06), poste local : serveur détruit par l'identifiant (action 667480874417041 « success », GET 404) ; clé SSH 132525071 supprimée |` ; `| 2026-11-12T17:18:32Z | relais Kimi pid 110065 | arrêté par le PID |` ; `| 2026-11-12T17:18:34Z | relais Argon pid 110077 | arrêté par le PID |`.

Écrit le 2026-11-12T17:22:11Z (heure relevée par `date -u`).
