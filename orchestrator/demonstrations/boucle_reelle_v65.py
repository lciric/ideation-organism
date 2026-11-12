"""Lanceur de la plus petite course réelle de la boucle complète de l'organisme, version 65 (fichier neuf, R12). Cœur :
`pole/boucle_reelle_v65.py` ; lecture gelée (programme à part) : `demonstrations/lire_boucle_reelle_v65.py`,
`pole/lecture_boucle_reelle_v65.py`. Réutilise sans le modifier le lanceur du tour fermé v64 (`demonstrations/tour_ferme_v64.py` :
adaptateurs réels et commandes externes v64, doublures, bac à sable, machine jetable).

Deux modes, exclusifs, qui passent par **le même chemin** (proposeurs `ProposeurAdaptateur`, étage `AdaptateurEtageV64`) :
- **à blanc** (`--a-blanc --graine G`, G < 2⁶⁴) : doublures scriptées ; jeu planté lu dans `exemples/jeu-plante-boucle-reelle-v65.md`
  (même bloc que celui du texte à sceller), héritage de départ écrit dans `SORTIE/depart/` puis **relu par la garde 17** ;
- **réel** (`--preenregistrement P --heritage-depart H --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R
  --go ID --utilisateur-bac U`) : le plan, le jeu planté, l'empreinte de l'héritage de départ, l'empreinte de la configuration
  et le GO sont lus dans le **texte scellé** `prereg/preenregistrement-boucle-reelle-organisme-v1-v<N>.md`, jamais en ligne de
  commande ; E = int(sha256 du texte scellé) ≥ 2⁶⁴.

Gardes avant tout appel (code 2) : dossier de sortie non vide ; bac sans défaut (« reel » exige `bwrap`, aucun repli sur
l'exécuteur factice ; garde 3) ; mode réel : texte hors du nom fixé, non scellé, à « brouillon », à marqueur `<<…>>`, code gelé non
conforme (`FICHIERS_GELES`), plan hors bornes (garde 20 bras réel seul ; D2 deux générations ; m = 22 ; parts Kimi + Argon =
plafond des modèles ; plafond des modèles + machine = montant du GO ; durée 72 h), jeu planté d'une autre empreinte ou fausse hors
de la classe couverte (garde 19), héritage de départ d'une autre empreinte (garde 17), configuration d'une autre empreinte, ou
dont la section `boucle_reelle_v65` contredit le plan, ou dont une commande v6 n'a pas l'empreinte nommée (pièce M6), GO absent,
d'un autre identifiant ou d'un montant insuffisant, machine (garde 22 : `bwrap` ≥ 0.9, utilisateur dédié ≠ 0, sonde réussie),
variable de clé, machine non jetable, rôle non tenu par un adaptateur. À blanc : `--bras` autre que « reel » (garde 20),
`--generations` autre que 2 (D2).
Codes : 0 relevé écrit (le code ne décide rien) ; 2 refus ; 3 arrêt (relevé partiel scellé, aucune issue lue sauf C5).

Usage à blanc : python3 -I -B demonstrations/boucle_reelle_v65.py SORTIE_NEUVE --a-blanc --graine 7 --bac factice
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
from pole import boucle_reelle_v65 as B  # noqa: E402
from pole import tour_ferme_v64 as T  # noqa: E402
from pole.outils import ecrire_json_scelle, empreinte_objet, sha256_fichier, verifier_scelle  # noqa: E402


def _charger_lanceur_v64():
    spec = importlib.util.spec_from_file_location("tour_ferme_v64_pour_boucle_reelle_v65", os.path.join(ICI, "tour_ferme_v64.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


L64 = _charger_lanceur_v64()

ETAPE = "boucle_reelle_v65"
SORTIE = "boucle-reelle-v65.json"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-boucle-reelle-organisme-v1-v[1-9][0-9]*\.md$")
JEU_A_BLANC = os.path.join(RACINE, "exemples", "jeu-plante-boucle-reelle-v65.md")
DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code-v65 : début -->", "<!-- empreintes-du-code-v65 : fin -->"
DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele-v65 : début -->", "<!-- plan-gele-v65 : fin -->"
MARQUEUR = re.compile(r"<<[A-Z0-9_-]+>>")
SHA = re.compile(r"^[0-9a-f]{64}$")
MONDE_SHA256 = L64.MONDE_SHA256_A_BLANC
DUREE_H = T.DUREE_ETAGE_1_H
BWRAP_MIN = (0, 9)
# Fermeture statique des imports des deux programmes v65 (arbre syntaxique, imports tardifs compris, fichiers chargés par chemin,
# évaluateur servi ; essai `Fermeture` de `essais/test_boucle_reelle_v65.py`) : les 92 fichiers du bloc v64 plus les quatre
# fichiers v65 (deux programmes, cœur, lecture).
FICHIERS_GELES = tuple(sorted(set(L64.FICHIERS_GELES) | {
    "demonstrations/boucle_reelle_v65.py", "demonstrations/lire_boucle_reelle_v65.py", "pole/boucle_reelle_v65.py",
    "pole/lecture_boucle_reelle_v65.py"}))
CLES_PLAN = {"generations", "cartes_par_proposeur", "m_e_bh", "bras", "d9", "plafond_modeles_usd", "plafond_kimi_usd",
             "plafond_argon_usd", "plafond_machine_usd", "go", "go_montant_usd", "duree_h", "configuration_sha256", "monde_sha256",
             "jeu_plante_sha256", "heritage_depart_sha256"}
A_BLANC = {"generations": 2, "cartes_par_proposeur": 6, "m_e_bh": B.M_FIXE, "plafond_usd": 1e9, "duree_max_h": DUREE_H}


class PreenregistrementRefuse(B.TourRefuse):
    """Mode réel : texte autre que le fichier fixé, non scellé, à marqueur restant, code gelé non conforme, plan hors bornes."""


class MachineRefusee(B.TourRefuse):
    """Garde 22 : `bwrap` absent ou < 0.9, utilisateur du bac absent ou superutilisateur, sonde refusée."""


class ConfigurationRefusee(B.TourRefuse):
    """Configuration v5 d'une autre empreinte, contraire au plan, ou commande v6 d'une autre empreinte (pièce M6)."""


# --- texte scellé ---------------------------------------------------------------------------------------------------------------


def _bloc(texte, debut, fin, nom):
    if texte.count(debut) != 1 or texte.count(fin) != 1 or texte.find(fin) < texte.find(debut):
        raise PreenregistrementRefuse(f"bloc « {nom} » absent, en double ou mal formé dans le préenregistrement")
    return texte[texte.find(debut) + len(debut):texte.find(fin)]


def lire_plan(texte):
    """Bloc `plan-gele-v65` : lignes « clé: valeur » ; rend le plan ou lève `PreenregistrementRefuse` (gardes 20, D2, parts, GO)."""
    lignes = {}
    for l in _bloc(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele-v65").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise PreenregistrementRefuse(f"plan-gele-v65 : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    if set(lignes) != CLES_PLAN:
        raise PreenregistrementRefuse(f"plan-gele-v65 : clés attendues {sorted(CLES_PLAN)}, trouvées {sorted(lignes)}")
    try:
        entiers = {k: int(lignes[k]) for k in ("generations", "cartes_par_proposeur", "m_e_bh")}
        reels = {k: float(lignes[k].replace(",", ".")) for k in ("plafond_modeles_usd", "plafond_kimi_usd", "plafond_argon_usd",
                                                                  "plafond_machine_usd", "go_montant_usd", "duree_h")}
    except ValueError:
        raise PreenregistrementRefuse("plan-gele-v65 : générations, cartes, m, plafonds, montant et durée numériques") from None
    if lignes["bras"] != "reel_seul":
        raise PreenregistrementRefuse(f"plan-gele-v65 : bras = {lignes['bras']!r} ; « reel_seul » exigé (D1, garde 20)")
    if entiers["generations"] != B.GENERATIONS:
        raise PreenregistrementRefuse(f"plan-gele-v65 : générations = {entiers['generations']} ; le code v65 en joue 2 (D2)")
    if entiers["m_e_bh"] != B.M_FIXE or entiers["cartes_par_proposeur"] != 6:
        raise PreenregistrementRefuse("plan-gele-v65 : m = 22 et six cartes par proposeur (brouillon, sections 3.5 et 6)")
    if any(v <= 0 for v in reels.values()):
        raise PreenregistrementRefuse("plan-gele-v65 : plafonds, montant et durée > 0")
    centimes = {k: round(v * 100) for k, v in reels.items()}
    if centimes["plafond_kimi_usd"] + centimes["plafond_argon_usd"] != centimes["plafond_modeles_usd"]:
        raise PreenregistrementRefuse("plan-gele-v65 : parts des relais (Kimi + Argon) ≠ plafond des modèles (au centime)")
    if centimes["plafond_modeles_usd"] + centimes["plafond_machine_usd"] != centimes["go_montant_usd"]:
        raise PreenregistrementRefuse("plan-gele-v65 : plafond des modèles + plafond de la machine ≠ montant du GO (au centime)")
    if reels["duree_h"] != DUREE_H:
        raise PreenregistrementRefuse(f"plan-gele-v65 : durée {reels['duree_h']:g} h ; le code gèle {DUREE_H:g} h")
    decisions = T.verifier_decisions({"d7": "archive_propre", "d9": lignes["d9"]})
    for k in ("configuration_sha256", "monde_sha256", "jeu_plante_sha256", "heritage_depart_sha256"):
        if not SHA.match(lignes[k]):
            raise PreenregistrementRefuse(f"plan-gele-v65 : {k} = 64 caractères hexadécimaux")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise PreenregistrementRefuse("plan-gele-v65 : go = GO-AAAA-MM-JJ-NN")
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
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", _bloc(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code-v65"), re.M)
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
    jeu, _ = B.lire_jeu_plante(texte, plan["jeu_plante_sha256"])
    empreinte = sha256_fichier(reel)
    return L64.entropie_decisive(empreinte), empreinte, dict((r, h) for h, r in gelees), plan, jeu


# --- configuration v5 et commandes v6 (pièce M6) --------------------------------------------------------------------------------


def verifier_configuration_v65(conf, plan):
    """La section `boucle_reelle_v65` de la configuration : GO, plafond des modèles, parts et plafond de la machine égaux au plan
    gelé ; `budget.plafond_usd` = plafond des modèles ; chaque commande v6 nommée a l'empreinte nommée et est celle que la
    configuration lance. Rend la section ; `ConfigurationRefusee` sinon."""
    s = (conf or {}).get("boucle_reelle_v65")
    if not isinstance(s, dict):
        raise ConfigurationRefusee("configuration sans section « boucle_reelle_v65 »")
    if s.get("go") != plan["go"] or float(s.get("plafond_modeles_usd") or 0) != plan["plafond_modeles_usd"] \
            or float(s.get("plafond_machine_usd") or 0) != plan["plafond_machine_usd"] \
            or {k: float(v) for k, v in (s.get("parts_usd") or {}).items()} != {"kimi": plan["plafond_kimi_usd"], "argon": plan["plafond_argon_usd"]}:
        raise ConfigurationRefusee("configuration : GO, plafonds ou parts de la section boucle_reelle_v65 ≠ plan gelé")
    if float(((conf.get("budget") or {}).get("plafond_usd")) or 0) != plan["plafond_modeles_usd"]:
        raise ConfigurationRefusee("configuration : budget.plafond_usd ≠ plafond des modèles du plan gelé")
    cmds = s.get("commandes_v6") or {}
    for n in ("kimi", "argon", "registre_depense_cumulee"):
        e = cmds.get(n) or {}
        if not isinstance(e.get("chemin"), str) or not SHA.match(str(e.get("sha256"))):
            raise ConfigurationRefusee(f"configuration : commande v6 « {n} » sans chemin ni empreinte")
        if not os.path.isfile(e["chemin"]) or sha256_fichier(e["chemin"]) != e["sha256"]:
            raise ConfigurationRefusee(f"commande v6 « {n} » absente ou d'une autre empreinte que {e['sha256'][:12]}… ({e['chemin']}) : refus")
    for n in ("kimi", "argon"):
        c = ((conf.get("fournisseurs") or {}).get(n) or {}).get("commande") or []
        if cmds[n]["chemin"] not in c:
            raise ConfigurationRefusee(f"configuration : la commande lancée pour {n} n'est pas la commande v6 nommée")
    return s


# --- garde 22 : machine -------------------------------------------------------------------------------------------------------


def version_bwrap(executer=subprocess.run, which=shutil.which):
    """(majeur, mineur) de `bwrap --version`, ou None si absent ou illisible."""
    if not which("bwrap"):
        return None
    try:
        sortie = executer(["bwrap", "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"(\d+)\.(\d+)", sortie or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def exiger_machine(utilisateur_bac, version=None):
    """Garde 22 (mode réel) : `bwrap` ≥ 0.9 et utilisateur dédié sans privilège (≠ 0) ; la sonde suit (`preparer_bac`)."""
    if version is None or tuple(version) < BWRAP_MIN:
        raise MachineRefusee(f"machine : bwrap ≥ 0.9 exigé (lu : {version!r}) : refus avant tout appel")
    if utilisateur_bac is None or int(utilisateur_bac) == 0:
        raise MachineRefusee("machine : utilisateur dédié sans privilège exigé (--utilisateur-bac, ≠ 0) : refus avant tout appel")
    return True


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
    return dict({"version": B.VERSION, "python": platform.python_version(), "numpy": np_v, "bwrap": version_bwrap(),
                 "depot": {"commit": commit, "arbre_modifie": modifie}, "bras": list(B.BRAS),
                 "regle_des_graines": f"SeedSequence(E, spawn_key=(cle_de_tache(tâche),)) ; tâches « {B.VERSION}|bras=reel|generation=<g>|… »",
                 "consigne_proposeur_sha256": hashlib.sha256(T.CONSIGNE_PROPOSEUR.encode()).hexdigest(),
                 "grammaire_sha256": empreinte_objet(T.GRAMMAIRE)}, **champs)


# --- programme ------------------------------------------------------------------------------------------------------------------


def principal(argv=None):
    a = argparse.ArgumentParser(description="plus petite course réelle de la boucle complète (v65) : bras réel seul, deux générations")
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
    base_sessions, parent_bac, reel, go, depart = None, None, not args.a_blanc, None, None
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
            jeu, sha_jeu = B.lire_jeu_plante(texte_jeu, B.empreinte_du_bloc(texte_jeu))
            r = dict(A_BLANC, **{k: v for k, v in options.items() if k in A_BLANC})
            parts = {k: v for k, v in (("kimi", args.plafond_kimi_usd), ("argon", args.plafond_argon_usd)) if v is not None}
            plan = {"generations": r["generations"], "cartes_par_proposeur": r["cartes_par_proposeur"], "m_e_bh": r["m_e_bh"],
                    "plafond_usd": r["plafond_usd"], "duree_max_s": r["duree_max_h"] * 3600.0, "parts": parts, "bras": list(B.BRAS)}
            if plan["generations"] != B.GENERATIONS:
                raise B.TourRefuse(f"générations : {plan['generations']} ; le code v65 en joue 2 (D2)")
            decisions = T.verifier_decisions({"d7": "archive_propre", "d9": "mecanique"})
            entropie, mode, preenregistrement, conf_info = args.graine, "a-blanc (exploratoire)", None, None
            proposeurs, adaptateur, roles = L64.roles_a_blanc(args, args.sortie)
            depart = tempfile.mkdtemp(prefix="depart-v65-")
            sha_depart = B.ecrire_heritage_depart(depart, jeu)
            chemin_depart = os.path.join(depart, B.NOM_HERITAGE_DEPART)
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
                go = cfg.verifier_go_v56(args.go, args.registre_go, p["go_montant_usd"])
            except cfg.GoRefuse as x:
                raise B.GoAbsent(str(x)) from None
            conf = cfg.lire_configuration_v56(args.configuration)
            section = verifier_configuration_v65(conf, p)
            exiger_machine(args.utilisateur_bac, version_bwrap())
            environnement = os.environ
            permis = L64.exiger_machine_jetable_reel(environnement, conf)
            base_sessions = tempfile.mkdtemp(prefix="boucle-reelle-v65-sessions-")
            proposeurs, adaptateur, roles, infos = L64.roles_reels(conf, plan, base_sessions, os.path.abspath(args.sortie),
                                                                   transmettre=not args.verifier_seulement)
            mode = "reel (decisif)"
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": p, "go": go}
            conf_info = dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf, environnement_permis=list(permis),
                             boucle_reelle_v65=section)
        heritage_depart = B.lire_heritage_depart(chemin_depart, sha_depart, jeu)  # garde 17, dans les deux modes
        B.exiger_go(reel, go)
        moteur = L64.moteur_de_l_etage(reel)
        T.exiger_familles_separees((roles["experimentateur"][0], roles["familles"]["experimentateur"]),
                                   (roles["verificateur"][0], roles["familles"]["verificateur"]))
        parent_bac, fabrique = L64.preparer_bac(args.bac, args.utilisateur_bac)
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
    compteur = T.Compteur(plan["plafond_usd"], plan["duree_max_s"], plan.get("parts"), time.time)
    try:
        try:
            releve, journal = B.jouer_boucle(args.sortie, monde=monde, jeu=jeu, heritage_depart=heritage_depart, racine=entropie,
                                             plan=plan, decisions=decisions, proposeurs=proposeurs, adaptateur_etage=adaptateur,
                                             roles=roles, fabrique_executeur=fabrique, compteur=compteur, reel=reel, go=go,
                                             moteur=moteur, environnement=environnement, permis_en_plus=permis)
        except Exception as x:  # noqa: BLE001 — toute exception après le manifeste est un arrêt scellé (code 3)
            partiel = getattr(x, "partiel", {}) or {}
            rel = partiel.get("releve") or {"version": B.VERSION, "arret": f"{type(x).__name__} : {x}", "complet": False,
                                            "cartes": [], "plantees": [], "generations_jouees": [], "membres_attendus": {},
                                            "retenues": {}, "etages": [], "plan": plan}
            rapport = {"version": B.VERSION, "mode": mode, "arret": f"{type(x).__name__} : {x}", "releve": rel,
                       "journal": partiel.get("journal", []), "depense": compteur.etat(), "preenregistrement": preenregistrement,
                       "appels_proposeurs": [p.appels for p in proposeurs], "appels_etage": list(getattr(adaptateur, "appels", [])),
                       "issue": "non jugeable (arrêt) : la lecture gelée dit C5 (et C2 ou C4 « partielle » s'il y a lieu)",
                       "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
            ecrire_json_scelle(os.path.join(args.sortie, SORTIE), rapport)
            print(json.dumps({"mode": mode, "arret": rapport["arret"], "depense": compteur.etat()}, ensure_ascii=False), file=sys.stderr)
            return 3
    finally:
        if parent_bac:
            shutil.rmtree(parent_bac, True)
        if depart:
            shutil.rmtree(depart, True)
    rapport = {"version": B.VERSION, "mode": mode, "preenregistrement": preenregistrement, "releve": releve, "journal": journal,
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
