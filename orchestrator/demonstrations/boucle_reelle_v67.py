"""Lanceur de la plus petite course réelle de la boucle complète de l'organisme, version 67 (fichier neuf, R12 ; le lanceur
v66 reste intact) — écart 1 au texte scellé (sortie du proposeur), option 2 décidée par le directeur (R-2426,
GO-2026-11-12-06). Copie du lanceur v66 (`demonstrations/boucle_reelle_v66.py`, `e2dd83ab…`) ; ne changent que :

- **E1-01, délai de la configuration** : les rôles réels sont construits par `roles_reels_v67` (ce fichier), copie de
  `tour_ferme_v64.roles_reels` (lanceur v64, inchangé) où `AC.commandes_v64` est remplacé par
  `pole/adaptateur_commande_v67.commandes_v67` : l'adaptateur de chaque commande externe reçoit `fournisseurs.<nom>.delai_s` au
  lieu du défaut gelé de 1 800 s (`pole/adaptateurs.py`, `DELAI_COMMANDE_S`) ; tout le reste de la construction est celui de la
  v64.
- **E1-02, garde 24 (neuve)** : `verifier_configuration_v67` = `verifier_configuration_v66` plus `verifier_delais_v67` (délai de
  l'adaptateur réel fini, > 0, ≤ 7 200 s ; `--delai-s` de la commande présent une fois et inférieur d'au moins 30 s), jouée avec
  le contenu de la configuration ; les délais vérifiés vont au manifeste (`configuration.delais_v67`).
- **E1-03, blocs du texte** : `empreintes-du-code-v67` (fermeture statique des deux programmes v67 : celle de la v66, moins le
  lanceur v66, plus ce lanceur et `pole/adaptateur_commande_v67.py`) et `plan-gele-v67` (mêmes clés et mêmes contrôles que
  `plan-gele-v66`) ; le bloc `jeu-plante-v65` ne change pas. Un texte écrit pour la v66 est refusé par la v67, et l'inverse.
- **E1-04** : nom du module chargé, préfixes des dossiers provisoires et messages en « v67 » ; manifeste : champ `lanceur` =
  « boucle-reelle-v67 ».

Ce qui ne change pas : le cœur (`pole/boucle_reelle_v66.py`, son `VERSION` et le nom du relevé, `boucle-reelle-v66.json`), la
lecture gelée v66 (programme et module, inchangés), le lecteur du registre des GO v66, les gardes 1 à 23, l'ordre du mode réel,
le mode à blanc, les codes.

En-tête du lanceur v66, inchangé dans cette copie :

Lanceur de la plus petite course réelle de la boucle complète de l'organisme, version 66 (fichier neuf, R12 ; le lanceur
v65 reste intact). Cœur : `pole/boucle_reelle_v66.py` ; lecture gelée (programme à part) : `demonstrations/lire_boucle_reelle_v66.py`,
`pole/lecture_boucle_reelle_v66.py`. Réutilise sans le modifier le lanceur du tour fermé v64 (`demonstrations/tour_ferme_v64.py` :
adaptateurs réels et commandes externes v64, doublures, machine jetable).

Deux modes, exclusifs, par le même chemin (proposeurs `ProposeurAdaptateur`, étage `AdaptateurEtageV64` enveloppé par
`EtageMesure`) :
- **à blanc** (`--a-blanc --graine G`, G < 2⁶⁴) : doublures scriptées ; jeu planté lu dans `exemples/jeu-plante-boucle-reelle-v65.md`
  (le même bloc `jeu-plante-v65` que celui du texte à sceller) ; héritage de départ écrit puis **relu par la garde 17** ;
- **réel** (`--preenregistrement P --heritage-depart H --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R
  --go ID --bac reel --utilisateur-bac U`) : plan, jeu planté, empreintes de l'héritage de départ et de la configuration, GO,
  lus dans le **texte scellé** `prereg/preenregistrement-boucle-reelle-organisme-v1-v<N>.md` (blocs `empreintes-du-code-v66`,
  `plan-gele-v66`, `jeu-plante-v65`), jamais en ligne de commande ; E = int(sha256 du texte scellé) ≥ 2⁶⁴.

Ce qui change par rapport au lanceur v65 (contre-lecture `contre-lecture-code-v65-v2.md`, `c4ddfc7f…`) :
- CLV65-07 : le GO est vérifié par `pole/registre_go_v66.verifier_go_v66` (règle des extensions de la garde de calcul ; part
  « organisme » d'une enveloppe) ; GO-2026-11-08-02 (45 USD) et GO-2026-11-10-10 (part « organisme » 45 USD) sont lus.
- CLV65-09 : **ordre du mode réel** : texte, monde, configuration (empreinte puis contenu), GO, **garde 17** (héritage de départ),
  **garde 22** (machine), garde 15 (machine jetable), et **en dernier** la construction des rôles réels, qui pose les portes de
  plafond des relais. Garde 22 : `bwrap` ≥ 0.9 ; lanceur **en superutilisateur** (sans quoi `setpriv` ne peut pas passer à
  l'utilisateur dédié et le bac tournerait sous le compte du lanceur) ; utilisateur dédié ≠ 0 ; sonde réussie **et** identité du
  bac lue dans la description de l'exécuteur sondé égale à l'utilisateur dédié demandé (la sonde vérifie, sur l'hôte, le
  propriétaire de son fichier témoin : `tests_de_mort_v2.ExecuteurBacASable.controler_hote_apres_sonde`).
- CLV65-10 : configuration v6 (`exemples/configuration-boucle-reelle-v6.json`) : commandes v6 et pièces nommées par des chemins
  **relatifs** au dossier de la configuration, sans « .. », résolus et vérifiés (fichier régulier sous ce dossier, empreinte
  nommée) ; la commande lancée de chaque fournisseur reçoit le chemin absolu résolu (copie ; l'empreinte reste celle du fichier).
- CLV65-06 : `WHICH` (module) est la fonction qui cherche `bwrap` ; les essais la remplacent pour jouer l'artefact « bwrap absent »
  même sur une machine qui a `bwrap`.
- CLV65-08 : en mode réel, les jetons d'entrée et de sortie sont relevés sur les adaptateurs à commande (`ReleveDeJetons`).

Codes : 0 relevé écrit (le code ne décide rien) ; 2 refus avant tout appel ; 3 arrêt (relevé partiel scellé ; la lecture gelée
seule dit l'issue).

Usage à blanc : python3 -I -B demonstrations/boucle_reelle_v66.py SORTIE_NEUVE --a-blanc --graine 7 --bac factice
                [--cout-simule-usd C] [--plafond-kimi-usd K --plafond-argon-usd A] [--scenario-proposeur …] [--bras reel]
"""

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
if RACINE not in sys.path:
    sys.path.insert(0, RACINE)

from pole import a_blanc_v59 as A  # noqa: E402
from pole import adaptateur_commande_v67 as AC67  # noqa: E402
from pole import boucle_reelle_v65 as B65  # noqa: E402
from pole import boucle_reelle_v66 as B  # noqa: E402
from pole import registre_go_v66 as R  # noqa: E402
from pole import tour_ferme_v64 as T  # noqa: E402
from pole.outils import ecrire_json_scelle, empreinte_objet, sha256_fichier, verifier_scelle  # noqa: E402


def _charger_lanceur_v64():
    spec = importlib.util.spec_from_file_location("tour_ferme_v64_pour_boucle_reelle_v67", os.path.join(ICI, "tour_ferme_v64.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


L64 = _charger_lanceur_v64()

ETAPE = "boucle_reelle_v66"
SORTIE = "boucle-reelle-v66.json"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-boucle-reelle-organisme-v1-v[1-9][0-9]*\.md$")
JEU_A_BLANC = os.path.join(RACINE, "exemples", "jeu-plante-boucle-reelle-v65.md")
DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code-v67 : début -->", "<!-- empreintes-du-code-v67 : fin -->"
DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele-v67 : début -->", "<!-- plan-gele-v67 : fin -->"
MARQUEUR = re.compile(r"<<[A-Z0-9_-]+>>")
SHA = re.compile(r"^[0-9a-f]{64}$")
MONDE_SHA256 = L64.MONDE_SHA256_A_BLANC
DUREE_H = T.DUREE_ETAGE_1_H
BWRAP_MIN = (0, 9)
PART_DU_GO = R.PART_PAR_DEFAUT  # « organisme » : part lue dans une enveloppe (GO-2026-11-10-10)
WHICH = shutil.which  # CLV65-06 : remplacée par les essais (artefact « bwrap absent » joué même là où bwrap existe)
LANCEUR = "boucle-reelle-v67"
# Fermeture statique des imports des deux programmes v67 (arbre syntaxique, imports tardifs compris, fichiers chargés par chemin ;
# essai `Fermeture` de `essais/test_boucle_reelle_v67.py`) : les 92 fichiers du bloc v64, le cœur v65 (réutilisé), les quatre
# fichiers v66 du chemin de course (cœur, lecture, programme de lecture, registre des GO) et les deux fichiers v67 (E1-03).
FICHIERS_GELES = tuple(sorted(set(L64.FICHIERS_GELES) | {
    "demonstrations/boucle_reelle_v67.py", "demonstrations/lire_boucle_reelle_v66.py", "pole/adaptateur_commande_v67.py",
    "pole/boucle_reelle_v65.py", "pole/boucle_reelle_v66.py", "pole/lecture_boucle_reelle_v66.py", "pole/registre_go_v66.py"}))
CLES_PLAN = {"generations", "cartes_par_proposeur", "m_e_bh", "bras", "d9", "plafond_modeles_usd", "plafond_kimi_usd",
             "plafond_argon_usd", "plafond_machine_usd", "go", "go_montant_usd", "duree_h", "configuration_sha256", "monde_sha256",
             "jeu_plante_sha256", "heritage_depart_sha256"}
CLES_SECTION = {"plafond_modeles_usd", "parts_usd", "plafond_machine_usd", "commandes_v6"}
COMMANDES_V6 = ("kimi", "argon", "registre_depense_cumulee")
A_BLANC = {"generations": 2, "cartes_par_proposeur": 6, "m_e_bh": B.M_FIXE, "plafond_usd": 1e9, "duree_max_h": DUREE_H}


class PreenregistrementRefuse(B.TourRefuse):
    """Mode réel : texte autre que le fichier fixé, non scellé, à marqueur restant, code gelé non conforme, plan hors bornes."""


class MachineRefusee(B.TourRefuse):
    """Garde 22 : `bwrap` absent ou < 0.9, lanceur non superutilisateur, utilisateur du bac absent ou 0, identité du bac sondé ≠
    utilisateur dédié demandé."""


class ConfigurationRefusee(B.TourRefuse):
    """Configuration v6 d'une autre empreinte, contraire au plan, chemin absolu ou hors du dossier, commande v6 d'une autre
    empreinte (pièce M6, CLV65-10)."""


# --- texte scellé ---------------------------------------------------------------------------------------------------------------


def _bloc(texte, debut, fin, nom):
    if texte.count(debut) != 1 or texte.count(fin) != 1 or texte.find(fin) < texte.find(debut):
        raise PreenregistrementRefuse(f"bloc « {nom} » absent, en double ou mal formé dans le préenregistrement")
    return texte[texte.find(debut) + len(debut):texte.find(fin)]


def lire_plan(texte):
    """Bloc `plan-gele-v67` : lignes « clé: valeur » ; rend le plan ou lève `PreenregistrementRefuse` (gardes 20, D2, parts, GO)."""
    lignes = {}
    for l in _bloc(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele-v67").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise PreenregistrementRefuse(f"plan-gele-v67 : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    if set(lignes) != CLES_PLAN:
        raise PreenregistrementRefuse(f"plan-gele-v67 : clés attendues {sorted(CLES_PLAN)}, trouvées {sorted(lignes)}")
    try:
        entiers = {k: int(lignes[k]) for k in ("generations", "cartes_par_proposeur", "m_e_bh")}
        reels = {k: float(lignes[k].replace(",", ".")) for k in ("plafond_modeles_usd", "plafond_kimi_usd", "plafond_argon_usd",
                                                                  "plafond_machine_usd", "go_montant_usd", "duree_h")}
    except ValueError:
        raise PreenregistrementRefuse("plan-gele-v67 : générations, cartes, m, plafonds, montant et durée numériques") from None
    if lignes["bras"] != "reel_seul":
        raise PreenregistrementRefuse(f"plan-gele-v67 : bras = {lignes['bras']!r} ; « reel_seul » exigé (D1, garde 20)")
    if entiers["generations"] != B.GENERATIONS:
        raise PreenregistrementRefuse(f"plan-gele-v67 : générations = {entiers['generations']} ; le code v67 en joue 2 (D2)")
    if entiers["m_e_bh"] != B.M_FIXE or entiers["cartes_par_proposeur"] != 6:
        raise PreenregistrementRefuse("plan-gele-v67 : m = 22 et six cartes par proposeur (brouillon, sections 3.5 et 6)")
    if any(not (v > 0) for v in reels.values()):
        raise PreenregistrementRefuse("plan-gele-v67 : plafonds, montant et durée > 0")
    centimes = {k: round(v * 100) for k, v in reels.items()}
    if centimes["plafond_kimi_usd"] + centimes["plafond_argon_usd"] != centimes["plafond_modeles_usd"]:
        raise PreenregistrementRefuse("plan-gele-v67 : parts des relais (Kimi + Argon) ≠ plafond des modèles (au centime)")
    if centimes["plafond_modeles_usd"] + centimes["plafond_machine_usd"] != centimes["go_montant_usd"]:
        raise PreenregistrementRefuse("plan-gele-v67 : plafond des modèles + plafond de la machine ≠ montant du GO (au centime)")
    if reels["duree_h"] != DUREE_H:
        raise PreenregistrementRefuse(f"plan-gele-v67 : durée {reels['duree_h']:g} h ; le code gèle {DUREE_H:g} h")
    decisions = T.verifier_decisions({"d7": "archive_propre", "d9": lignes["d9"]})
    for k in ("configuration_sha256", "monde_sha256", "jeu_plante_sha256", "heritage_depart_sha256"):
        if not SHA.match(lignes[k]):
            raise PreenregistrementRefuse(f"plan-gele-v67 : {k} = 64 caractères hexadécimaux")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise PreenregistrementRefuse("plan-gele-v67 : go = GO-AAAA-MM-JJ-NN")
    return dict(entiers, **reels, bras=list(B.BRAS), decisions=decisions, go=lignes["go"],
                **{k: lignes[k] for k in ("configuration_sha256", "monde_sha256", "jeu_plante_sha256", "heritage_depart_sha256")})


def lire_preenregistrement(chemin, dossier_prereg=None, racine_code=None):
    """Garde 6 : le texte au chemin fixé, scellé, sans « brouillon », sans marqueur, gelant exactement le code présent, plan
    conforme, jeu planté conforme (garde 19), entropie ≥ 2⁶⁴ ; rend (entropie, empreinte, empreintes gelées, plan, jeu)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(dossier_prereg or DOSSIER_PREREG)
    base = os.path.basename(reel)
    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(base) or "brouillon" in base:
        raise PreenregistrementRefuse(f"mode réel : le préenregistrement est prereg/preenregistrement-boucle-reelle-organisme-v1-v<N>.md, pas {chemin}")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    restants = sorted(set(MARQUEUR.findall(texte)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) : {restants}")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", _bloc(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code-v67"), re.M)
    noms = [r for _, r in gelees]
    if sorted(noms) != sorted(FICHIERS_GELES) or len(set(noms)) != len(noms):
        raise PreenregistrementRefuse(f"code gelé ≠ fermeture : manquants {sorted(set(FICHIERS_GELES) - set(noms))}, "
                                      f"en trop {sorted(set(noms) - set(FICHIERS_GELES))}")
    ecarts = []
    for attendue, relatif in gelees:
        p = os.path.join(racine_code or RACINE, relatif)
        presente = sha256_fichier(p) if os.path.isfile(p) else "absent"
        if presente != attendue:
            ecarts.append(f"{relatif} : gelé {attendue[:12]}…, présent {presente[:12]}…")
    if ecarts:
        raise PreenregistrementRefuse("code différent du code gelé : " + " ; ".join(ecarts))
    plan = lire_plan(texte)
    jeu, _ = B65.lire_jeu_plante(texte, plan["jeu_plante_sha256"])
    empreinte = sha256_fichier(reel)
    return L64.entropie_decisive(empreinte), empreinte, dict((r, h) for h, r in gelees), plan, jeu


# --- configuration v6 et commandes v6 (pièce M6, CLV65-10) ------------------------------------------------------------------


def chemin_relatif_sous(dossier, chemin, quoi):
    """Le chemin absolu d'un chemin **relatif** au dossier (aucun chemin absolu, aucun « .. »), fichier régulier sous ce dossier
    (après résolution des liens) ; `ConfigurationRefusee` sinon."""
    if not isinstance(chemin, str) or not chemin or os.path.isabs(chemin) or ".." in chemin.replace("\\", "/").split("/"):
        raise ConfigurationRefusee(f"configuration : {quoi} : chemin relatif au dossier de la configuration exigé, sans « .. » (reçu {chemin!r})")
    racine = os.path.realpath(dossier)
    p = os.path.realpath(os.path.join(racine, chemin))
    if os.path.commonpath([racine, p]) != racine or not os.path.isfile(p):
        raise ConfigurationRefusee(f"configuration : {quoi} absent ou hors du dossier de la configuration ({chemin})")
    return p


def verifier_configuration_v66(conf, plan, dossier_conf):
    """La section `boucle_reelle_v66` (clés exactes) : plafond des modèles, parts et plafond de la machine égaux au plan gelé ;
    `budget.plafond_usd` = plafond des modèles ; pièces et commandes v6 relatives au dossier, présentes, à l'empreinte nommée ;
    la commande lancée de Kimi et d'Argon est la commande v6 nommée. Rend (section, copie de la configuration où les commandes
    lancées portent le chemin absolu résolu) ; `ConfigurationRefusee` sinon."""
    s = (conf or {}).get("boucle_reelle_v66")
    if not isinstance(s, dict) or set(s) != CLES_SECTION:
        raise ConfigurationRefusee(f"configuration : section « boucle_reelle_v66 » aux clés {sorted(CLES_SECTION)} exigée")
    try:
        parts = {k: float(v) for k, v in (s.get("parts_usd") or {}).items()}
        egaux = (float(s["plafond_modeles_usd"]) == plan["plafond_modeles_usd"] and float(s["plafond_machine_usd"]) == plan["plafond_machine_usd"]
                 and parts == {"kimi": plan["plafond_kimi_usd"], "argon": plan["plafond_argon_usd"]})
    except (TypeError, ValueError, AttributeError):
        egaux = False
    if not egaux:
        raise ConfigurationRefusee("configuration : plafonds ou parts de la section boucle_reelle_v66 ≠ plan gelé")
    if float(((conf.get("budget") or {}).get("plafond_usd")) or 0) != plan["plafond_modeles_usd"]:
        raise ConfigurationRefusee("configuration : budget.plafond_usd ≠ plafond des modèles du plan gelé")
    for nom, piece in sorted((conf.get("pieces") or {}).items()):
        chemin_relatif_sous(dossier_conf, (piece or {}).get("chemin"), f"pièce « {nom} »")
    cmds = s.get("commandes_v6") or {}
    resolues = {}
    for n in COMMANDES_V6:
        e = cmds.get(n) or {}
        if not SHA.match(str(e.get("sha256"))):
            raise ConfigurationRefusee(f"configuration : commande v6 « {n} » sans empreinte")
        p = chemin_relatif_sous(dossier_conf, e.get("chemin"), f"commande v6 « {n} »")
        if sha256_fichier(p) != e["sha256"]:
            raise ConfigurationRefusee(f"commande v6 « {n} » d'une autre empreinte que {e['sha256'][:12]}… ({e['chemin']}) : refus")
        resolues[n] = p
    copie = json.loads(json.dumps(conf))
    for n in ("kimi", "argon"):
        c = ((copie.get("fournisseurs") or {}).get(n) or {}).get("commande") or []
        if c.count(cmds[n]["chemin"]) != 1:
            raise ConfigurationRefusee(f"configuration : la commande lancée pour {n} n'est pas la commande v6 nommée")
        copie["fournisseurs"][n]["commande"] = [resolues[n] if x == cmds[n]["chemin"] else x for x in c]
    return s, copie


def verifier_configuration_v67(conf, plan, dossier_conf):
    """E1-02 : `verifier_configuration_v66` puis la garde 24 (`AC67.verifier_delais_v67`) sur la configuration lue ; rend (section,
    copie résolue, délais vérifiés) ; `ConfigurationRefusee` sinon (le motif de la garde 24 recopié)."""
    section, copie = verifier_configuration_v66(conf, plan, dossier_conf)
    try:
        delais = AC67.verifier_delais_v67(conf)
    except AC67.DelaiRefuse as x:
        raise ConfigurationRefusee(str(x)) from None
    return section, copie, delais


def roles_reels_v67(conf, plan, base_sessions, sortie, transmettre=True):
    """E1-01 : `tour_ferme_v64.roles_reels` recopiée, `AC.commandes_v64` remplacé par `AC67.commandes_v67` (délai de la
    configuration passé à l'adaptateur) ; rien d'autre ne change (refus avant toute porte et tout appel, code 2)."""
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise T.TourRefuse(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais tiennent les clés")
    g2 = L64.charger_goodhart_v2()
    budget, modeles = g2.reglages_de_configuration(conf)
    if float((conf.get("budget") or {}).get("plafond_usd") or 0) != float(plan["plafond_usd"]):
        raise T.TourRefuse(f"configuration : budget.plafond_usd = {(conf.get('budget') or {}).get('plafond_usd')!r} ≠ plafond de "
                           f"l'étage 1 ({plan['plafond_usd']} USD) : demander une configuration à empreinte neuve")
    conf2, substitutions = g2.substituer_commandes(conf, os.path.join(os.path.abspath(sortie), L64.REGISTRE_COURSE), plan["plafond_usd"])
    v8 = g2.charger_ideation_v8()
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf2, sortie, base_sessions)
    if sorted(n for n in adaptateurs if n in ("kimi", "argon")) != ["argon", "kimi"]:
        raise T.TourRefuse(f"configuration : adaptateurs « kimi » et « argon » exigés, trouvés {sorted(adaptateurs)}")
    try:
        adaptateurs, portes = AC67.commandes_v67(conf2, adaptateurs, portes)  # E1-01 : délai de la configuration
    except (L64.AC.RelaisNonCommande, AC67.DelaiRefuse) as x:
        raise T.TourRefuse(str(x)) from None
    proposeurs = [T.ProposeurAdaptateur(n, n, adaptateurs[n], os.path.join(base_sessions, "proposeur-" + n), budget, modeles[n])
                  for n in ("kimi", "argon")]
    etage = T.AdaptateurEtageV64(adaptateurs["kimi"], adaptateurs["argon"], "kimi", "argon")
    T.exiger_roles_joues(T.paires_de_roles(proposeurs, etage))
    try:
        bareme = {n: L64.AC.bareme_depuis_configuration(conf, n) for n in ("kimi", "argon")}
    except L64.AC.BaremeAbsent as x:
        raise T.TourRefuse(str(x)) from None
    etage = T.AdaptateurEtageV64(adaptateurs["kimi"], adaptateurs["argon"], "kimi", "argon",
                                 prix_caractere_usd={n: bareme[n]["prix_caractere_usd"] for n in ("kimi", "argon")})
    accuses = {n: portes[n].transmettre(L64.ETAPE, plan["parts"][n]) for n in ("kimi", "argon")} if transmettre else "non relancées (vérification seule)"
    roles = {"experimentateur": ("experimentateur-kimi", modeles["kimi"]), "verificateur": ("verificateur-argon", modeles["argon"]),
             "familles": {"experimentateur": "kimi", "verificateur": "argon"}, "relais": {"experimentateur": "kimi", "verificateur": "argon"}}
    infos = {"budget_appel_usd": budget, "modeles_demandes": modeles, "substitutions_dans_les_commandes": substitutions,
             "accuses_plafond": accuses, "parts_des_relais_usd": plan["parts"], "portes": {n: portes[n].description() for n in ("kimi", "argon")},
             "bareme_des_commandes": bareme, "adaptateurs": {n: adaptateurs[n].description() for n in ("kimi", "argon")},
             "commandes": AC67.VERSION}
    return proposeurs, etage, roles, infos


# --- garde 22 : machine -------------------------------------------------------------------------------------------------------


def version_bwrap(executer=subprocess.run, which=None):
    """(majeur, mineur) de `bwrap --version`, ou None si absent ou illisible."""
    if not (which or WHICH)("bwrap"):
        return None
    try:
        sortie = executer(["bwrap", "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"(\d+)\.(\d+)", sortie or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def exiger_machine(utilisateur_bac, version, euid):
    """Garde 22 (mode réel), avant la sonde : `bwrap` ≥ 0.9 ; lanceur en superutilisateur (seul moyen de lancer le bac sous
    l'utilisateur dédié, `setpriv`) ; utilisateur dédié sans privilège (≠ 0)."""
    if version is None or tuple(version) < BWRAP_MIN:
        raise MachineRefusee(f"machine : bwrap ≥ 0.9 exigé (lu : {version!r}) : refus avant tout appel")
    if euid != 0:
        raise MachineRefusee("machine : le lanceur doit tourner en superutilisateur (sinon le bac tourne sous le compte du lanceur, "
                             "jamais sous l'utilisateur dédié) : refus avant tout appel")
    if utilisateur_bac is None or int(utilisateur_bac) == 0:
        raise MachineRefusee("machine : utilisateur dédié sans privilège exigé (--utilisateur-bac, ≠ 0) : refus avant tout appel")
    return True


def exiger_utilisateur_du_bac(description, utilisateur_bac):
    """Garde 22, après la sonde : l'exécuteur sondé est le vrai bac (non factice, sonde réussie) et l'identité de son script sur
    l'hôte est l'utilisateur dédié demandé (`identite_du_script_sur_l_hote.utilisateur_dedie.uid`)."""
    d = description or {}
    ident = ((d.get("identite_du_script_sur_l_hote") or {}).get("utilisateur_dedie") or {})
    if d.get("factice") is not False or d.get("demande") != "reel" or not d.get("sonde"):
        raise MachineRefusee("machine : l'exécuteur n'est pas le vrai bac sondé : refus avant tout appel")
    if utilisateur_bac is None or ident.get("uid") != int(utilisateur_bac):
        raise MachineRefusee(f"machine : identité du bac sur l'hôte {ident.get('uid')!r} ≠ utilisateur dédié demandé {utilisateur_bac!r} : "
                             "refus avant tout appel")
    return True


def preparer_bac_v66(bac, utilisateur_bac, which=None):
    """Dossier du bac (identité dédiée, noyau superutilisateur) puis sonde (garde 3, refus avant tout) ; rend (dossier parent ou
    None, fabrique de l'exécuteur, description de l'exécuteur sondé). Comme `tour_ferme_v64.preparer_bac`, plus la description
    (garde 22) et `which` (CLV65-06). Si la préparation ou la sonde échoue, le dossier créé est retiré avant que le refus monte."""
    which = which or WHICH
    parent, racine_travail = None, None
    try:
        if bac == "reel" and os.geteuid() == 0 and utilisateur_bac is not None:
            parent = os.path.realpath(tempfile.mkdtemp(prefix="bac-boucle-reelle-v67-"))
            os.chmod(parent, 0o711)
            racine_travail = os.path.join(parent, "bac")
            os.mkdir(racine_travail, 0o700)
            os.chown(racine_travail, int(utilisateur_bac), int(utilisateur_bac))
        _, description = A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail, which=which)
    except BaseException:
        if parent:
            shutil.rmtree(parent, True)
        raise
    return parent, (lambda: A.choisir_executeur(bac, utilisateur_bac=utilisateur_bac, racine_travail=racine_travail, which=which)), description


# --- manifeste ----------------------------------------------------------------------------------------------------------------


def manifeste(**champs):
    try:
        np_v = __import__("numpy").__version__
    except ImportError:
        np_v = None
    try:
        commit = subprocess.run(["git", "-C", RACINE, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or "inconnu"
        modifie = bool(subprocess.run(["git", "-C", RACINE, "status", "--porcelain"], capture_output=True, text=True, timeout=30).stdout.strip())
    except (OSError, subprocess.SubprocessError):
        commit, modifie = "inconnu", None
    return dict({"version": B.VERSION, "lanceur": LANCEUR, "python": platform.python_version(), "numpy": np_v, "bwrap": version_bwrap(),
                 "depot": {"commit": commit, "arbre_modifie": modifie}, "bras": list(B.BRAS),
                 "regle_des_graines": f"SeedSequence(E, spawn_key=(cle_de_tache(tâche),)) ; tâches « {B.VERSION}|bras=reel|generation=<g>|… »",
                 "consigne_proposeur_sha256": hashlib.sha256(T.CONSIGNE_PROPOSEUR.encode()).hexdigest(),
                 "grammaire_sha256": empreinte_objet(T.GRAMMAIRE)}, **champs)


# --- programme ------------------------------------------------------------------------------------------------------------------


def principal(argv=None):
    a = argparse.ArgumentParser(description="plus petite course réelle de la boucle complète (v67) : bras réel seul, deux générations")
    a.add_argument("sortie")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true")
    g.add_argument("--preenregistrement")
    a.add_argument("--graine", type=int)
    a.add_argument("--heritage-depart")
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--bac", choices=("reel", "factice"), required=True, help="aucun défaut ; « reel » refuse sans bwrap")
    a.add_argument("--utilisateur-bac", type=int)
    a.add_argument("--verifier-seulement", action="store_true")
    for o, t in (("--generations", int), ("--plafond-usd", float), ("--plafond-kimi-usd", float), ("--plafond-argon-usd", float),
                 ("--duree-max-h", float), ("--cout-simule-usd", float), ("--cout-simule-etage-usd", float),
                 ("--prix-entree-kimi-usd-par-million-jetons", float), ("--prix-entree-argon-usd-par-million-jetons", float)):
        a.add_argument(o, type=t)
    a.add_argument("--bras", help="à blanc : « reel » seul permis (garde 20)")
    a.add_argument("--scenario-proposeur")
    a.add_argument("--scenario-experimentateur")
    a.add_argument("--scenario-verificateur")
    a.add_argument("--familles-a-blanc")
    args = a.parse_args(argv)
    noms_options = ("generations", "plafond_usd", "plafond_kimi_usd", "plafond_argon_usd", "duree_max_h", "cout_simule_usd",
                    "cout_simule_etage_usd", "prix_entree_kimi_usd_par_million_jetons", "prix_entree_argon_usd_par_million_jetons",
                    "bras", "scenario_proposeur", "scenario_experimentateur", "scenario_verificateur", "familles_a_blanc")
    options = {k: getattr(args, k) for k in noms_options if getattr(args, k) is not None}
    base_sessions, parent_bac, reel, go, depart, jetons = None, None, not args.a_blanc, None, None, None
    from pole import configuration_v56 as cfg
    try:
        if os.path.exists(args.sortie) and os.listdir(args.sortie):
            raise FileExistsError(f"dossier de sortie non vide : {args.sortie} (on n'écrase jamais)")
        if args.bac == "factice" and reel:
            raise B.TourRefuse("mode réel : bac « reel » exigé (aucune barrière avec l'exécuteur factice)")
        monde = A.charger_monde(RACINE)
        environnement, permis = dict(T.ENV_A_BLANC), ()
        if args.a_blanc:
            if args.graine is None or args.moteur or args.configuration or args.go or args.verifier_seulement or args.heritage_depart:
                raise B.TourRefuse("à blanc : --graine G seulement (ni moteur réel, ni configuration, ni GO, ni héritage donné)")
            if not 0 <= args.graine < 2 ** 64:
                raise B.TourRefuse("à blanc : graine dans [0 ; 2^64[ (l'espace ≥ 2^64 est celui des textes scellés)")
            B.exiger_bras([args.bras] if args.bras else list(B.BRAS))
            L64.verifier_monde(monde, MONDE_SHA256)
            with open(JEU_A_BLANC, encoding="utf-8") as f:
                texte_jeu = f.read()
            jeu, sha_jeu = B65.lire_jeu_plante(texte_jeu, B65.empreinte_du_bloc(texte_jeu))
            r = dict(A_BLANC, **{k: v for k, v in options.items() if k in A_BLANC})
            parts = {k: v for k, v in (("kimi", args.plafond_kimi_usd), ("argon", args.plafond_argon_usd)) if v is not None}
            plan = {"generations": r["generations"], "cartes_par_proposeur": r["cartes_par_proposeur"], "m_e_bh": r["m_e_bh"],
                    "plafond_usd": r["plafond_usd"], "duree_max_s": r["duree_max_h"] * 3600.0, "parts": parts, "bras": list(B.BRAS)}
            if plan["generations"] != B.GENERATIONS:
                raise B.TourRefuse(f"générations : {plan['generations']} ; le code v67 en joue 2 (D2)")
            decisions = T.verifier_decisions({"d7": "archive_propre", "d9": "mecanique"})
            entropie, mode, preenregistrement, conf_info = args.graine, "a-blanc (exploratoire)", None, None
            proposeurs, adaptateur, roles = L64.roles_a_blanc(args, args.sortie)
            depart = tempfile.mkdtemp(prefix="depart-v67-")
            sha_depart = B65.ecrire_heritage_depart(depart, jeu)
            chemin_depart = os.path.join(depart, B65.NOM_HERITAGE_DEPART)
            heritage_depart = B65.lire_heritage_depart(chemin_depart, sha_depart, jeu)  # garde 17
            parent_bac, fabrique, description_bac = preparer_bac_v66(args.bac, args.utilisateur_bac)
            if args.bac == "reel" and os.geteuid() == 0:
                exiger_utilisateur_du_bac(description_bac, args.utilisateur_bac)
        else:
            if args.graine is not None or options:
                raise B.TourRefuse(f"mode réel : le plan est lu dans le texte scellé ; options refusées : {sorted(options) or ['--graine']}")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration or not args.heritage_depart:
                raise B.TourRefuse("mode réel : --configuration, --heritage-depart, --moteur reel et --confirmer-moteur-reel exigés")
            entropie, empreinte, gelees, p, jeu = lire_preenregistrement(args.preenregistrement)
            sha_jeu = p["jeu_plante_sha256"]
            L64.verifier_monde(monde, p["monde_sha256"])
            plan = {"generations": p["generations"], "cartes_par_proposeur": p["cartes_par_proposeur"], "m_e_bh": p["m_e_bh"],
                    "plafond_usd": p["plafond_modeles_usd"], "duree_max_s": p["duree_h"] * 3600.0,
                    "parts": {"kimi": p["plafond_kimi_usd"], "argon": p["plafond_argon_usd"]}, "bras": list(B.BRAS)}
            decisions = p["decisions"]
            chemin_depart, sha_depart = args.heritage_depart, p["heritage_depart_sha256"]
            if not os.path.isfile(args.configuration):
                raise ConfigurationRefusee(f"configuration introuvable : {args.configuration}")
            sha_conf = sha256_fichier(args.configuration)
            if sha_conf != p["configuration_sha256"]:
                raise ConfigurationRefusee(f"configuration d'empreinte {sha_conf[:12]}… : le texte scellé gèle {p['configuration_sha256'][:12]}…")
            if not args.registre_go or args.go != p["go"]:
                raise B.GoAbsent(f"mode réel : --registre-go et --go {p['go']} (celui du texte scellé) exigés")
            try:
                go = R.verifier_go_v66(args.go, args.registre_go, p["go_montant_usd"], part=PART_DU_GO)
            except R.GoRefuse as x:
                raise B.GoAbsent(str(x)) from None
            dossier_conf = os.path.dirname(os.path.abspath(args.configuration))
            conf = cfg.lire_configuration_v56(args.configuration)
            section, conf_resolue, delais = verifier_configuration_v67(conf, p, dossier_conf)  # E1-02 : garde 24
            heritage_depart = B65.lire_heritage_depart(chemin_depart, sha_depart, jeu)  # garde 17, avant toute porte
            exiger_machine(args.utilisateur_bac, version_bwrap(), os.geteuid())  # garde 22, avant toute porte
            parent_bac, fabrique, description_bac = preparer_bac_v66("reel", args.utilisateur_bac)
            exiger_utilisateur_du_bac(description_bac, args.utilisateur_bac)
            environnement = os.environ
            permis = L64.exiger_machine_jetable_reel(environnement, conf)  # garde 15
            base_sessions = tempfile.mkdtemp(prefix="boucle-reelle-v67-sessions-")
            proposeurs, adaptateur, roles, infos = roles_reels_v67(conf_resolue, plan, base_sessions, os.path.abspath(args.sortie),
                                                                   transmettre=not args.verifier_seulement)  # portes : en dernier
            jetons = B.ReleveDeJetons()
            for p_ in proposeurs:
                jetons.instrumenter(p_.ad, p_.relais)
            for ad_, relais_ in adaptateur.roles.values():
                jetons.instrumenter(ad_, relais_)
            mode = "reel (decisif)"
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": p, "go": go}
            conf_info = dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf, environnement_permis=list(permis),
                             boucle_reelle_v66=section, delais_v67=delais, bac=description_bac)
        B.exiger_go(reel, go)
        moteur = L64.moteur_de_l_etage(reel)
        T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                                   (roles["verificateur"][0], roles["familles"]["verificateur"]))
        if args.verifier_seulement:
            print(json.dumps({"verification": "conforme", "ecriture": "aucune", "appel": "aucun", "plan": plan,
                              "configuration": conf_info}, ensure_ascii=False, indent=1, default=str))
            return 0
    except Exception as x:  # noqa: BLE001 — refus nommé avant tout appel, jamais de repli
        print(f"refus : {type(x).__name__} : {x}", file=sys.stderr)
        for d in (parent_bac, base_sessions, depart):
            if d:
                shutil.rmtree(d, True)
        return 2
    finally:
        if args.verifier_seulement:
            for d in (parent_bac, base_sessions, depart):
                if d:
                    shutil.rmtree(d, True)
    try:
        os.makedirs(args.sortie, exist_ok=True)
        m = manifeste(etape=ETAPE, mode=mode, entropie_racine=str(entropie), plan=plan, decisions=decisions,
                      preenregistrement=preenregistrement, configuration=conf_info, bac=args.bac, moteur_etage=moteur,
                      environnement_etage=sorted(environnement), monde={k: monde[k] for k in ("source", "sha256", "loi_vraie")},
                      jeu_plante_sha256=sha_jeu, heritage_depart={"chemin": os.path.abspath(chemin_depart), "sha256": sha_depart},
                      roles=roles, options_a_blanc=options if args.a_blanc else None,
                      code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                      prix_caractere_usd_etage=dict(adaptateur.prix_caractere_usd),
                      debut_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"))
        ecrire_json_scelle(os.path.join(args.sortie, "manifeste.json"), m)
    except Exception as x:  # noqa: BLE001 — CLV65-13 : avant le premier appel, une erreur d'écriture est un refus nommé (code 2)
        print(f"refus : écriture du manifeste : {type(x).__name__} : {x}", file=sys.stderr)
        for d in (parent_bac, base_sessions, depart):
            if d:
                shutil.rmtree(d, True)
        return 2
    compteur = T.Compteur(plan["plafond_usd"], plan["duree_max_s"], plan.get("parts"), time.time)
    try:
        try:
            releve, journal = B.jouer_boucle(args.sortie, monde=monde, jeu=jeu, heritage_depart=heritage_depart, racine=entropie,
                                             plan=plan, decisions=decisions, proposeurs=proposeurs, adaptateur_etage=adaptateur,
                                             roles=roles, fabrique_executeur=fabrique, compteur=compteur, reel=reel, go=go,
                                             moteur=moteur, environnement=environnement, permis_en_plus=permis, jetons=jetons)
        except Exception as x:  # noqa: BLE001 — toute exception après le manifeste est un arrêt scellé (code 3)
            partiel = getattr(x, "partiel", {}) or {}
            rel = partiel.get("releve") or {"version": B.VERSION, "arret": f"{type(x).__name__} : {x}", "complet": False,
                                            "cartes": [], "plantees": [], "generations_jouees": [], "membres_attendus": {},
                                            "retenues": {}, "etages": [], "vues_servies": {}, "archives_de_jugement": {},
                                            "incidents": [], "plan": plan}
            rapport = {"version": B.VERSION, "mode": mode, "arret": f"{type(x).__name__} : {x}", "releve": rel,
                       "journal": partiel.get("journal", []), "depense": compteur.etat(), "preenregistrement": preenregistrement,
                       "appels_proposeurs": [p.appels for p in proposeurs], "appels_etage": list(getattr(adaptateur, "appels", [])),
                       "lecture": "aucune ici : la lecture gelée (programme à part) dit l'issue", "dossier_des_sessions": base_sessions,
                       "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
            ecrire_json_scelle(os.path.join(args.sortie, SORTIE), rapport)
            print(json.dumps({"mode": mode, "arret": rapport["arret"], "depense": compteur.etat()}, ensure_ascii=False), file=sys.stderr)
            return 3
    finally:  # le dossier des sessions des proposeurs (mode réel) est gardé : pièces de l'audit A1, chemin au rapport
        for d in (parent_bac, depart):
            if d:
                shutil.rmtree(d, True)
    rapport = {"version": B.VERSION, "mode": mode, "preenregistrement": preenregistrement, "releve": releve, "journal": journal,
               "dossier_des_sessions": base_sessions,
               "depense": compteur.etat(), "appels_proposeurs": [p.appels for p in proposeurs],
               "appels_etage": list(getattr(adaptateur, "appels", [])),
               "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    sha = ecrire_json_scelle(os.path.join(args.sortie, SORTIE), rapport)
    print(json.dumps({"mode": mode, "releve_sha256": sha, "generations_jouees": releve["generations_jouees"],
                      "cartes": len(releve["cartes"]), "plantees": len(releve["plantees"]), "depense": compteur.etat(),
                      "lecture": "aucune (la lecture gelée est un autre programme)"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
