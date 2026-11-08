# Journal de l'essai à blanc v65 de la boucle complète (bras réel seul, deux générations) — v1

- **Développeur** : Claude Opus 5.5 (`claude-opus-5-5`), développeur neuf : je n'ai écrit aucune pièce de l'organisme ni du programme
  de contrôle, ni le brouillon 1 du préenregistrement de la course.
- **Date et heures** (temps universel, `date -u`) : 8 novembre 2026, essai joué de 06:58:36 à 06:59:06 (code v65 gelé pour l'essai).
- **Dépense** : aucune. Aucun appel de modèle, aucun réseau vers un fournisseur, aucune clé ni variable d'environnement lue.
- **Arbre** : `/home/user/wt-organisme-v65`, branche `prep/organisme-v65-boucle-reelle`, partie de `94bfd92` ; code v65 non commis.
- **Interpréteur** : `/home/user/controle-ia-travail/.venv/bin/python -I -B` (Python 3.13.18, numpy 2.4.6, scipy 1.17.1) : le Python du
  système (numpy 2.5.3) n'a ni pytest ni scipy ; pièce M7 du brouillon (interpréteur de la machine de la course) ouverte.
- **Fournisseurs simulés** : doublures scriptées de la v64 (proposeurs, expérimentateur, vérificateur) branchées sur le chemin réel
  (`ProposeurAdaptateur`, `AdaptateurEtageV64`) ; elles ne lisent que le texte servi.
- **Exécuteur** : **factice, déclaré** (`--bac factice` ; manifeste : `bac_factice_declare: true` ; journal de l'étage :
  `factice: true`) ; le vrai bac à sable n'a pas tourné (pas de `bwrap` sur cette machine).
- **Sorties** (scellées par le code de l'organisme, compagnons `.sha256` compris) : hors de l'arbre, dans le bloc-notes de la session,
  `/tmp/claude-0/-home-user/4a4722d4-e39d-57bd-bde3-e6a99e2eecdf/scratchpad/v65/essai-a-blanc-v65-final/` (journal brut :
  `journal-brut.txt`).

## 1. Commandes, heures, codes (depuis `orchestrator/`, sorties `E=…/essai-a-blanc-v65-final`)

| heure | commande | code | issue |
|---|---|---|---|
| 06:58:36 | `demonstrations/boucle_reelle_v65.py $E/s-bac-reel --a-blanc --graine 20261108 --bac reel` | **2** | « BacASableIndisponible : bac réel demandé : bwrap absent de cette machine : refus, aucun repli sur l'exécuteur factice » ; aucun dossier créé (garde 3, garde 22) |
| 06:58:36 → 06:58:57 | même commande, `--bac factice` (explicite) | **0** | rapport `s/boucle-reelle-v65.json` `ac033b5d1f0fd7e54ad26f4d35a4cee16dbc9c454d0edd6e055822e698fefc7d` ; manifeste `077ae3104ef04e55d7e4629f02a382fb7b2086f4d49c9abd7763abc23a926962` |
| 06:58:57 → 06:59:00 | `demonstrations/lire_boucle_reelle_v65.py $E/s $E/lecture-s.json --releve-sha256 ac033b5d…` | **0** | lecture `e7805ac3314b331ffbad70f9c5bb8f81587f0314bc39f030691368d8fae2f76e` : issue **C1** (« la chaîne garde »), audit A1 déclenché d'office, **A1 non conforme : bac factice** (attendu à blanc) |
| 06:59:00 → 06:59:03 | course, `--scenario-experimentateur erreur` | **3** | arrêt scellé : « EtageInterrompu : session experimentateur_test/experimentateur-scripte (famille-a) : statut 'erreur' » ; rapport partiel `9bc9cee5…` ; les dix lois plantées de la génération 1 et leurs promotions sont au relevé partiel (jugement écrit avant les étages) |
| 06:59:03 → 06:59:05 | lecture du rapport arrêté | **0** | lecture `c12ff455…` : issue **C5** (« non jugeable (arrêt) »), aucune partielle (aucune fausse promue) |
| 06:59:05 → 06:59:06 | course, `--plafond-kimi-usd 0.05 --plafond-argon-usd 0.05 --cout-simule-usd 0.06` | **3** | « PlafondAtteint : arrêt au plafond : appel du relais kimi de borne 0.0600 USD non lancé (part restante 0.0500 USD…) » ; 0 appel, 0 USD (`88b9df06…`) |
| 06:59:06 | course de nouveau dans `$E/s` | **2** | « dossier de sortie non vide … (on n'écrase jamais) » |

## 2. Ce que montre la course saine (code 0)

- **Bras réel seul** : un seul dossier `bras-reel/` ; quatre appels de proposeurs (deux par génération : génération 2 complète).
- **Héritage de départ (M1)** : génération 1 servie et jugée avec {K1} (`61d47d6f…`, l'empreinte du texte) ; vue de la génération 1 :
  une loi (K1).
- **Jeu planté (M2) et jugement avec l'archive (M3)**, génération 1, 4 membres d'archive pour chaque loi plantée (ceux de {K1}) :

| loi | gardien | promue (log e ≥ log(22/0,05)) | verdict du noyau | log e | log W maximal |
|---|---|---|---|---|---|
| V1 | passe | oui | survit | 16,19 | 94,13 |
| V2 | passe | oui | survit | 7,00 | 65,34 |
| V3 | passe | oui | survit | 6,22 | 6,22 |
| V4 | passe | oui | survit | 8,02 | 8,02 |
| F1 à F4 | passent | **non** | — | −0,40 à −2,38 | **−0,16 à −0,82** (≤ 0 : membres du nul) |
| T-ELIM | passe | oui | **éliminée** | 8,18 | 94,51 |
| T-MAL | **refusée** | — | — | — | — |

- **Génération 2 lit la sélection (M4)** : empreinte lue = écrite (lecture de la génération 2 et lecture finale) ; 12 cartes retenues en
  génération 1 ; vue de la génération 2 = K1 + 12 retenues (13 lois) ; archive de jugement de la génération 2 = les mêmes, **40 membres
  d'archive** pour chaque loi jugée (cartes, fausses, copies) ; copies C1 à C4 des quatre premières retenues par log e : **toutes
  refusées** (log W maximal −0,65 à −5,46) ; F1 à F4 replantées : refusées (−11,1 à −13,0) ; aucune carte de la génération 2 promue (les
  doublures reproposent les lois déjà retenues) ; aucune loi plantée testée en génération 2 (§ 3.7).
- **Recherche de la loi plantée** : 0 touche dans les contextes des proposeurs ; 34 consignes de l'étage cherchées, **0 touche hors de
  la loi gelée servie**, 84 dans les lois gelées (V1 = L* et ses dérivées, servies à l'expérimentateur comme le veut le test).
- **Lecture gelée** : C1 ; P3 mesurée (V3 et V4 promues puis survivantes) ; A1 dit « bac factice » et ne conclut pas « tout conforme ».

## 3. Ce qui casse, ou reste ouvert (aucun contournement écrit)

| constat | effet | ce qu'il faut |
|---|---|---|
| `bwrap` absent ici | rien n'est montré du vrai bac à sable ; refus propre code 2 | machine jetable à `bwrap` ≥ 0.9 et utilisateur dédié (M0) ; y rejouer cet essai avec `--bac reel --utilisateur-bac 64097` et l'essai `BacReel.test_course_dans_le_vrai_bac` |
| le registre des GO du dépôt de travail porte un identifiant en double (`GO-2026-10-24-07`, lignes 53 et 54) | `configuration_v53.lire_registre_go` refuse le registre entier : le mode réel serait refusé (code 2) au GO, même pour GO-2026-11-08-02 | décision de la session mère (registre, ou registre d'extrait daté) avant le lancement ; la ligne GO-2026-11-08-02 seule est lue conforme à 45 USD (essai `GardesDeDepense`) |
| commandes v6 absentes de cette machine (`main` ne les porte pas) | la garde v65 refuse, code 2 (« commande v6 … absente ») | verser `outils/commandes-tour-ferme-v1` (`12f9e0e3`) au chemin que nomme la configuration v5 (M6) ; poser la configuration v5 à côté de la v4 (pièces relatives) |
| plafond de la machine (5 USD) | porté par le plan, la configuration et le compteur (`ajouter_machine`), mais aucune source de facture n'alimente le compteur | tenu par la location de la machine (session de dépôt) |
| `--plafond-cumule-usd` des commandes | le code réutilisé de la v64 (`substituer_commandes`) le met au plafond des modèles (40 USD, registre commun aux deux relais), non aux parts 33 et 7 comme l'écrit le devis (§ 5) ; les parts sont tenues par les portes des relais et le compteur | décision : garder (recommandé, code éprouvé) ou une substitution par relais (code neuf) |
| interpréteur | numpy 2.4.6 ici, 2.5.3 documenté | M7 : rejouer essais, banc et cet essai sur la machine de la course |
