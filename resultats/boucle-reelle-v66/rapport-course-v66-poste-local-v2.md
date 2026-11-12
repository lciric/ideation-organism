# Rapport de course — course réelle de l'organisme (code v66, GO-2026-11-10-11), session du poste local — v2 (reprise)

Session fille du poste local de Lazar (consigne `consigne-poste-local-course-v66-v3.md`, `51043e06…`). Heures relevées par
`date -u`. Suite de `rapport-course-v66-poste-local-v1.md` (`83fd674b…` ; première course : arrêt code 3, amont Kimi 429).
L'issue n'est pas jugée ici : la phrase rendue est recopiée sans commentaire ; le verdict (R13) revient à un agent neuf.

## Écart, dit d'abord

La section 10 du texte scellé demande, après une panne de relais, « un texte neuf contre-lu » pour toute reprise. **Cette reprise
s'est faite sans texte neuf, sur autorisation directe de Lazar dans la session du poste**, verbatim : « tu as mon autorisation
dorecte pour relancer la course ». Lazar avait auparavant remplacé la clé Kimi dans l'environnement du poste (vérifiée par son
nom seulement). Rien d'autre n'a changé : même code (`7e415cba`), même configuration v6 (`4743ddbe…`), même texte scellé, même
GO, préalables 1 à 7 rejoués en entier sur une machine neuve.

Après cette reprise, Lazar a demandé dans la session : « enleve le plafond max tokens et relance ». **Non fait** : la borne de
sortie du proposeur est fixée par la configuration v6 (`--max-sortie-proposeur`, et la borne de session en dollars qui fixe
`max_tokens`) ; la changer change l'empreinte de la configuration, gelée au bloc `configuration_sha256` de la section 16 et dans
les conditions de GO-2026-11-10-11 : le lanceur refuserait (code 2) ; seule une configuration v7 sous un texte neuf contre-lu
(et une ligne de GO qui la nomme) le permet.

## En une ligne

Lanceur : **code 3** (arrêt) au premier appel. L'amont Kimi a répondu **200** après 1 553 s, mais la réponse du proposeur a été
**coupée par sa borne de sortie** : 46 714 jetons de sortie dont **46 711 de raisonnement** ; la commande Kimi v6 sort en code 5
(« réponse non conforme : tronquée ou vide » ; pour le proposeur, arrêt A.5) ; garde 13 ; aucun appel Argon.

## Phrase rendue par le programme de lecture

> Issue C5 : « non jugeable (arrêt) » — course reel (decisif) (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte).

## Serveur

| point | valeur |
|---|---|
| identifiant | **175792062**, `organisme-v66-course`, cpx32, debian-13, hel1 ; commande citant `GO_ID=GO-2026-11-10-11` ; étiquette `go` |
| inventaire avant (07:53:04Z) | 0 serveur, 0 clé SSH |
| création | 2026-11-12T07:53:06Z ; identifiant versé et poussé à 07:53:08Z (`poste-local-serveur-v2.md`, commit `375089058`) |
| prix | 0,05772 EUR/h TTC (+ IPv4 primaire, 0,00096 EUR/h TTC selon `rapport-arret-operateur-course-v66-v1.md`) |
| clé SSH jetable | 132513543, supprimée à 08:38:14Z (204) ; partie privée effacée du bac |
| destruction | `DELETE /v1/servers/175792062` à 08:38:04Z, action 667403564480133 « success » à 08:38:15Z ; `GET` → 404 ; inventaire après : 0 serveur, 0 clé |
| vie | 07:53:06Z → 08:38:15Z (45 min 9 s) |
| coût | au plus une heure entamée : ≈ **0,059 EUR TTC (≈ 0,07 USD)** |

## Préalables (section 12.3), machine neuve

Même machine type et mêmes versions que la v1 : Debian 13, `bubblewrap` 0.12.0, **Python 3.13.5, numpy 2.2.4**, pytest 8.3.5 ;
utilisateur du bac uid/gid 64097 ; arbre `7e415cba` (base `94bfd92` + paquet v65 `4660197e…` + paquet v66 `84ab119f…`,
`git bundle verify` des deux sur la machine), 492 fichiers, propre ; texte scellé sous `orchestrator/prereg/`, octets égaux ;
lanceur et préalables depuis le groupe de contrôle racine (réglage de la machine, dit au rapport v1).

| # | sortie |
|---|---|
| 1 | 07:54:16Z → 07:58:10Z, code 0, « 322 passed, 5 skipped » ; mêmes cinq motifs qu'en v1 (4 essais du vrai registre ou de la garde du dépôt de travail, absent ; 1 artefact « `bwrap` absent ») ; aucun essai du vrai bac sauté |
| 2 | 07:58:10Z → 08:03:12Z, code 0, 133 tuées sur 133 |
| 3 | 08:03:12Z → 08:03:30Z, code 0 ; étages « factice : faux » (2 + 2) ; lecture code 0, C1 à blanc (`59e890d01e00eecc3a6cf68411cd54631162fee4044a49516dbdc4881926b353`) |
| 4 | `registres/go.md` de `main` (`ff4eebd33fcbd9ef83d1763424d32dbe398598cd`) copié à 08:08:05Z : **`3101983333ad8e6a84f2f3a4a8585e039867728e587a4bd0ab7e0c3153d8f4d6`** ; ligne GO égale à l'octet |
| 5 | 08:08:16Z, code 0, « conforme », aucun appel ; uid/gid 64097 ; commandes résolues (`88930930…`, `5eae1a04…`) |
| 6 | relais Kimi **pid 94531** (08:08:42Z), Argon **pid 94543** (08:08:44Z), valeurs exactes de la section 12.3 (Kimi 33 USD, 446 appels ; Argon 7 USD, 39 appels, collisionneur v7 explicite) ; clés par l'entrée standard de SSH |
| 7 | `SORTIE_ESSAI` et `SORTIE` frères sous `/root/sorties/`, sans fragment refusé ; `TMPDIR=/tmp` |

## Lanceur (section 12.4)

- `--verifier-seulement`, relais lancés : 08:09:01Z → 08:09:02Z, code 0, « conforme ».
- Course : 08:09:02Z → 08:34:56Z, **code 3**. Arrêt au relevé : « ArretTour : proposeur kimi : session 'erreur', erreur 'commande
  externe : code 5 : ', refus None : arrêt (garde 13 ; jamais « réponse illisible ») » ; `incidents` vide ; générations jouées : aucune.
- Relevé `course-reelle/boucle-reelle-v66.json` **`5a7fc27c7dfb1c7e0911cf9df3aa0b1c785e386bfa32de0294625c5709d52b9b`**.
- Lecture, code 0 : `lecture-course-reelle.json` `edae8c4f4cdaac2aec90079ff0c55637c2750d3d5d8c01337ed8a53237fd5323`, code « C5 ».
- Dossier des sessions des proposeurs (audit A1) : `/tmp/boucle-reelle-v66-sessions-eyadpnwb` ; contenu :
  `proposeur-kimi/boucle-reelle-v66|bras=reel|generation=1/`, **dossier vide** (liste donnée ici ; un dossier vide ne se verse pas).

## Relais et dépense

| relais | appels | dépense | détail (journal du relais, `ef66948b…`) |
|---|---|---|---|
| Kimi | 1 | **0,481706 USD** (usage lu) | statut amont **200**, `modele_servi` kimi-k3.1-pro, 1 552,967 s ; 7 283 jetons d'entrée (dont 7 168 en écriture de cache), **46 714 de sortie dont 46 711 de raisonnement** ; 119 977 octets de réponse |
| Argon | 0 | 0 USD | aucun appel ; journal non créé |

Lecture du code 5 (en-tête de `commande_kimi_v6.py`, sans juger l'issue) : « 5 réponse non conforme (vide, … » ; réponse coupée
par sa borne (`finish_reason` « length ») : code 0 admis pour l'étage de tests seulement ; « Pour le proposeur et le juge, rien ne
change (code 5, arrêt : A.5) ». `max_tokens` = min(sortie maximale du rôle, ce que paie le reste du plafond de session) ; les jetons
de raisonnement comptent dans `completion_tokens`, donc dans cette borne.

Relais arrêtés **par leur PID** (R10), PID vérifié contre le port : Kimi 94531 à 08:36:48Z, Argon 94543 à 08:36:50Z ; ports libres.

## Pièces rapatriées

`docs/notes/organisme-boucle-reelle-v1/course-v66/poste-local-v2/` (noms neufs, compagnons) : relevé et manifeste (compagnons du
lanceur), registre de dépense cumulée, lecture, essai à blanc, journaux des préalables, de la vérification, du lanceur, de la
lecture et des relais. Archive `f1478581e93d51cb309d67e70e18beadb74061aa28c1da1f37f04d8b22b2228b` (égale des deux côtés).
Aucune clé (recherche des trois valeurs par descripteur : 0 ; garde des secrets : 0) ; correspondance légitime : nom du dépôt de
travail, champ `depot` de 3 fichiers, texte intact.

## Dépense cumulée sous GO-2026-11-10-11

Machine : 175573391 (≈ 0,07 USD, mère) + 175751768 (≈ 0,07) + 175792062 (≈ 0,07) ≈ **0,21 USD** ; modèles : Kimi 0,499998
(v1, réserve de pire cas, amont 429) + 0,481706 (v2) ≈ **0,98 USD** au plus ; Argon 0. **Total ≈ 1,19 USD au plus** sur 45.

## Lignes proposées pour la session mère

- `registres/depenses.md` : `| 2026-11-12 | GO-2026-11-10-11 | Course réelle de l'organisme v66, poste local, reprise : machine Hetzner 175792062 (cpx32, hel1, debian-13), 07:53:06Z → 08:38:15Z (45 min 9 s) ; ≈ 0,059 EUR TTC (≈ 0,07 USD) | Hetzner |` ; `| 2026-11-12 | GO-2026-11-10-11 | Course réelle de l'organisme v66, poste local, reprise : relais Kimi, 1 appel (réponse du proposeur coupée à sa borne de sortie) ; 0,481706 USD | Kimi (Moonshot) |` ; Argon 0 USD.
- `registres/arrets.md` : `| 2026-11-12T08:38:15Z | Hetzner 175792062 | Course v66 (GO-2026-11-10-11), poste local, reprise : serveur détruit par l'identifiant (action 667403564480133 « success », GET 404) ; clé SSH 132513543 supprimée |` ; `| 2026-11-12T08:36:48Z | relais Kimi pid 94531 | arrêté par le PID |` ; `| 2026-11-12T08:36:50Z | relais Argon pid 94543 | arrêté par le PID |`.
- `registres/decisions.md` (à la mère) : reprise sans texte neuf, sur mot direct de Lazar (verbatim ci-dessus) ; demande de Lazar
  « enleve le plafond max tokens et relance » non exécutée (configuration gelée), à traiter par une configuration v7 et un texte neuf.

Écrit le 2026-11-12T08:39:38Z (heure relevée par `date -u`).
