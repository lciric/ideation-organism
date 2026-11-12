# Rapport de course — course réelle de l'organisme (code v66, GO-2026-11-10-11), session du poste local — v1

Session fille du poste local de Lazar, sous la consigne
`docs/notes/g0-deux-semaines-v1/consignes-mere-2026-11-10-1136-v1/consigne-poste-local-course-v66-v3.md`
(`51043e065fdbc602227d944b5e3fe870c1da1eaa2ff098e490b23c3d0dedd25d`) et le complément de la mère R-2405 (base v65 par le paquet
`code-v65/organisme-v65-boucle-reelle-v2.bundle` de la branche `prep/organisme-v65-v1`). Heures relevées par `date -u`.
Suite de `rapport-arret-poste-local-course-v66-v1.md` (`81cc8f9b…`, arrêt avant location faute de `cef5ea60`, levé par R-2405).
L'issue n'est pas jugée ici : la phrase rendue est recopiée sans commentaire ; le verdict (R13) revient à un agent neuf.

## En une ligne

Lanceur : **code 3** (arrêt) au premier appel, le proposeur Kimi en session « erreur » (« commande externe : code 3 »), l'amont
du relais Kimi ayant répondu **HTTP 429** ; aucun appel Argon. Relevé partiel scellé, lu. Serveur détruit par son identifiant.

## Phrase rendue par le programme de lecture

> Issue C5 : « non jugeable (arrêt) » — course reel (decisif) (classe couverte du nul v8, monde jouet S-V1, une génération et demie ; rien sur la classe non couverte).

## Serveur

| point | valeur |
|---|---|
| identifiant | **175751768**, nom `organisme-v66-course`, cpx32, debian-13, hel1 ; étiquette `go=GO-2026-11-10-11` ; commande de création citant `GO_ID=GO-2026-11-10-11` |
| inventaire avant (00:01:06Z) | un serveur **non créé par cette session** : 175751342 `lean-outillage-d1a` (et sa clé SSH 132500120) ; **aucune action sur eux** |
| clé SSH jetable | ed25519 générée dans le bac à sable du poste ; partie publique enregistrée au projet (132500768), supprimée à 00:22:29Z (204) ; partie privée effacée |
| création | 2026-11-12T00:01:08Z (API) ; identifiant versé et poussé à 00:01:11Z (`poste-local-serveur-v1.md`, commit `6cbc40bf3`) |
| prix | 0,05772 EUR/h TTC (cpx32, hel1, API `server_types`) ; IPv4 primaire en sus (0,00096 EUR/h TTC selon `rapport-arret-operateur-course-v66-v1.md`) |
| destruction | `DELETE /v1/servers/175751768` à 00:22:18Z, action 667334845670771 « success » à 00:22:29Z ; `GET` → 404 ; aucune IP primaire restée liée ; inventaire après : seul `lean-outillage-d1a` (non touché) |
| vie | 00:01:08Z → 00:22:29Z (21 min 21 s) |
| coût | au plus une heure entamée : 0,05772 + 0,00096 ≈ **0,059 EUR TTC (≈ 0,07 USD)** |

Note : la fiche versée à la création (`poste-local-serveur-v1.md`, scellée) porte l'identifiant, le nom, le GO et la clé, mais
ses champs « lieu », « création » et « prix » sont restés vides (le script lisait un champ `datacenter` que l'API ne rend plus) ;
les valeurs justes sont celles de ce tableau. Fiche non réécrite (R12).

## Machine et charge

- Debian 13 (noyau 6.12.113+deb13-cloud-amd64), 4 cœurs, 7 Go ; groupes de contrôle v2.
- `bubblewrap` 0.12.0 ; **Python 3.13.5** ; **numpy 2.2.4** ; pytest 8.3.5 ; scipy (paquet Debian) ; `setpriv` de util-linux.
- Utilisateur du bac : `bacpole`, uid 64097, gid 64097, sans interpréteur de commandes, sans dossier personnel.
- Arbre de l'organisme : base publique `94bfd92` + paquet v65 (`4660197e4ee5890ac30bef8da496c5d023fa4e57372f5f53dbd6c19fa8186ed6`,
  compagnon égal ; tête `cef5ea60ea22a9bb46a2b0be761972672a4c2ede`) + paquet v66 (`84ab119f0b3eefdd689b4be03f03bb776ebd2c7c1247b9d76e903181a419b1bc`) ;
  `git bundle verify` des deux paquets sur la machine ; tête **`7e415cbaaa3ff602db43a44dad6b4307c08352c7`**, 492 fichiers,
  arbre propre ; **98 empreintes du bloc `empreintes-du-code-v66` égales** (contrôlées sur le poste avant l'envoi).
- Texte scellé copié sous `orchestrator/prereg/preenregistrement-boucle-reelle-organisme-v1-v1.md` (octets égaux, compagnon OK,
  `46d7545b…`) ; dossier de course = `configuration-v6/` versé (`configuration-boucle-reelle-v6.json` `4743ddbe…`) avec
  `heritage-depart-v65.json` et son compagnon ; relais Kimi `relais_kimi_v3.py` `d54ed2bce54f5c89e9f078d1a03b5d8159894d6565ae560c3601c1e63ca76239` ;
  collisionneur v7 `c9725f025407c3ece3e8c16d19cfdfdec078f084a811f0a3b6ea3209be5d98dc` ; tous les compagnons OK.
- **Réglage de la machine** (sans effet sur le code, la configuration ni le plan) : le lanceur et les préalables sont joués
  depuis le **groupe de contrôle racine** (`echo $$ > /sys/fs/cgroup/cgroup.procs`, puis `0::/`) : sous cgroup v2, le groupe d'une
  session SSH ne peut pas déléguer `memory` à ses enfants tout en contenant le lanceur (règle « pas de processus internes ») ; le
  groupe racine le peut. C'est le point annoncé par `rapport-arret-operateur-course-v66-v1.md` ; la sonde du bac l'a confirmé
  (« mémoire du bac entier bornée (groupe de contrôle) »).

## Préalables de la section 12.3

| # | sortie |
|---|---|
| 1 | 00:03:24Z → 00:07:34Z, **code 0**, « 322 passed, 5 skipped » (327 essais, comme 323 + 4 du développeur). Sautés (motifs relevés par `-rs`) : 4 essais du **vrai registre** ou de la garde de calcul du dépôt de travail, absent de la machine (`test_registre_go_v66.py` l. 104, 181, 190 ; `test_boucle_reelle_v66.py` l. 899), déclarés non joués comme le prévoit le texte ; 1 artefact « `bwrap` absent » (`test_boucle_reelle_v65.py` l. 531), injouable là où `bwrap` est présent. **Aucun essai du vrai bac sauté** : les quatre que le développeur sautait ont été joués et réussis. |
| 2 | 00:07:34Z → 00:12:54Z, **code 0**, « 133 tuées pour la raison attendue sur 133 mutations » |
| 3 | 00:12:54Z → 00:13:12Z, **code 0** (`--a-blanc --graine 20261110 --bac reel --utilisateur-bac 64097`) ; étages « factice : faux » (2 au relevé, 2 au journal) ; lecture code 0 (C1 à blanc, `4dd64df5ae1ef5151025ed6777ef7f995e8d1210ef34727c0e9e82b204b6c1aa`) |
| 4 | `registres/go.md` de `main` (`f63553c81d72bfe4c9030c66224652dac381bc8a`) copié sur la machine à 00:18:29Z : **`3101983333ad8e6a84f2f3a4a8585e039867728e587a4bd0ab7e0c3153d8f4d6`** ; ligne GO-2026-11-10-11 égale à l'octet à la section 13 |
| 5 | 00:18:40Z, **code 0** : « verification : conforme », « ecriture : aucune », « appel : aucun » ; bac sous uid/gid 64097 ; sonde complète (réseau refusé, aucun superutilisateur, mémoire bornée, borne de processus tenue) ; commandes résolues `/root/course/commandes-v6/commande_kimi_v6.py` (`88930930…`) et `…/commande_argon_v56_nuit_v6.py` (`5eae1a04…`) ; `SORTIE` non créée |
| 6 | relais lancés à 00:19:47Z (Kimi, **pid 89110**, port 8804) et 00:19:49Z (Argon, **pid 89122**, port 8805), valeurs exactes de la section 12.3 : Kimi `--modeles-permis kimi-k3.1-pro --plafond-usd 33 --prix-entree 2 --prix-sortie 10 --prix-cache 2 --max-appels 446` ; Argon `servir --plafond-usd 7 --max-appels 39 --collisionneur <chemin du collisionneur v7 sur la machine> --sha-collisionneur c9725f02…` ; clés passées par l'entrée standard de SSH vers le seul environnement de chaque relais (Argon : valeur de `GEMINI_API_KEY_2` sous le nom `GEMINI_API_KEY`) ; écoute sur 127.0.0.1 seulement |
| 7 | `SORTIE_ESSAI` et `SORTIE` frères (`<machine>/root/sorties/essai-a-blanc`, `…/course-reelle`), aucun fragment refusé ; `TMPDIR=/tmp` |

## Lanceur (section 12.4)

- Commande de la section 12.4 sous `env -i` (noms permis seulement, `POLE_MACHINE_JETABLE_V56=1`, aucune clé), depuis `orchestrator/`,
  lanceur en superutilisateur, `--go GO-2026-11-10-11`, `--registre-go` = la copie du point 4.
- `--verifier-seulement`, relais lancés : 00:20:24Z → 00:20:25Z, **code 0**, « conforme ».
- Course : 00:20:25Z → 00:20:27Z, **code 3**. Arrêt écrit au relevé : « ArretTour : proposeur kimi : session 'erreur', erreur
  'commande externe : code 3 : ', refus None : arrêt (garde 13 ; jamais « réponse illisible ») » ; `incidents` vide.
- Relevé : `course-reelle/boucle-reelle-v66.json` **`c9c6212bfe16b148e5df42c27a1f631eeafbd79ca9c7b82ac048fabce69c3069`** (compagnon du lanceur).
- Lecture : `lire_boucle_reelle_v66.py SORTIE LECTURE.json --releve-sha256 c9c6212b…`, **code 0** ; `lecture-course-reelle.json`
  `7de89198c7ec7838ec66ff256cb3c729c81fea3bf6a3410635c9bc18c2333d82` ; code « C5 ».
- Dossier des sessions des proposeurs (audit A1) : `/tmp/boucle-reelle-v66-sessions-5lq7ip_1` sur la machine ; contenu :
  `proposeur-kimi/boucle-reelle-v66|bras=reel|generation=1/`, **dossier vide** (aucun fichier) ; rapatrié tel quel (un dossier
  vide ne se verse pas dans git : sa liste est ici).

## Relais et dépense

| relais | appels | dépense tenue par le relais | détail |
|---|---|---|---|
| Kimi | 1 | **0,499998 USD** | journal : `POST /v1/chat/completions`, modèle `kimi-k3.1-pro`, 15 405 octets envoyés, **statut amont 429**, 257 octets de réponse, 0,22 s, `usage` absent : coût compté à la réserve de pire cas (`cout_origine` « pire_cas » au registre de dépense cumulée). La somme réellement facturée par le fournisseur n'est pas lisible d'ici. |
| Argon | 0 | **0 USD** | aucun appel ; journal non créé |
| total modèles | 1 | **0,499998 USD** (borne haute) | sous les parts (Kimi 33, Argon 7) |

Relais arrêtés **par leur PID** (R10), chaque PID vérifié contre le port qu'il tenait : Kimi 89110 à 00:21:50Z, Argon 89122 à
00:21:52Z ; ports 8804 et 8805 libres ensuite.

## Pièces rapatriées

Sous `docs/notes/organisme-boucle-reelle-v1/course-v66/poste-local-v1/` (noms neufs), chacune avec son compagnon :
`course-reelle/` (relevé et compagnon du lanceur, manifeste et compagnon, registre de dépense cumulée), `lecture-course-reelle.json`,
`essai-a-blanc/` (relevé et lecture du préalable 3), `journaux/` (préalables 1 à 5, vérification, lanceur, lecture, sorties et
journal des relais). Archive rapatriée `e7d3aa0e1a8d338efd7a02297745c35dea65b8754a2faaa1f816dce60cb78111` (égale des deux côtés).
**Aucune clé** : recherche des trois valeurs (par descripteur, jamais en argument) → 0 fichier ; garde des secrets → 0.
Correspondance légitime de la garde des données du poste : le nom du dépôt de travail, champ `depot` du manifeste et des deux
sorties de vérification (3 fichiers) ; texte laissé intact.

## Incidents

1. Amont Kimi : HTTP 429 au premier appel du proposeur (génération 1) ; arrêt par la garde 13 ; aucune bascule. La section 10 du
   texte : « arrêt pour infrastructure, jamais de bascule silencieuse vers l'autre fournisseur ; une reprise demande un texte neuf
   contre-lu ». Aucune relance faite.
2. Fiche du serveur versée avec trois champs vides (voir « Serveur »).
3. Un serveur d'une autre session (`lean-outillage-d1a`) était présent à l'inventaire ; non touché.

## Lignes proposées pour la session mère

- `registres/depenses.md` : `| 2026-11-12 | GO-2026-11-10-11 | Course réelle de l'organisme v66, poste local : machine Hetzner 175751768 (cpx32, hel1, debian-13), 00:01:08Z → 00:22:29Z (21 min 21 s) ; ≈ 0,059 EUR TTC (≈ 0,07 USD) | Hetzner |` et `| 2026-11-12 | GO-2026-11-10-11 | Course réelle de l'organisme v66, poste local : relais Kimi, 1 appel (amont 429, coût compté à la réserve de pire cas) ; 0,499998 USD au plus | Kimi (Moonshot) |` ; relais Argon : 0 USD. Cumul sous la ligne : ≈ 0,07 + 0,07 + 0,50 ≈ **0,64 USD** au plus.
- `registres/arrets.md` : `| 2026-11-12T00:22:29Z | Hetzner 175751768 | Course v66 (GO-2026-11-10-11), poste local : serveur détruit par l'identifiant (action 667334845670771 « success », GET 404) ; clé SSH 132500768 supprimée |` ; `| 2026-11-12T00:21:50Z | relais Kimi pid 89110 | arrêté par le PID |` ; `| 2026-11-12T00:21:52Z | relais Argon pid 89122 | arrêté par le PID |`.

Écrit le 2026-11-12T00:24:48Z (heure relevée par `date -u`).
