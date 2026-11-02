"""Attaque de Goodhart contre le juge statistique, v2 : lanceur (fichier neuf, R12). Cœur : `pole/attaque_goodhart_v2.py`.

Deux modes, exclusifs :
- **à blanc** (`--a-blanc --graine G`, G dans [0 ; 2⁶⁴[) : proposeurs scriptés, aucun réseau, aucune clé ; exploratoire, ne
  décide rien ; le plan (cartes, mondes, rejeux, plafonds, processus) se règle en ligne de commande ;
- **réel** (`--preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID`) :
  Kimi et Argon par les adaptateurs du pôle (`demonstrations/ideation_v8.adaptateurs_reels_v56`). Le plan est lu dans le
  texte scellé (bloc `plan-gele`), jamais en ligne de commande ; graine = empreinte SHA-256 du texte scellé (≥ 2⁶⁴).

Gardes avant tout appel et toute écriture (code 2) : dossier de sortie non vide ; en mode réel, préenregistrement autre que
`prereg/preenregistrement-attaque-goodhart-v2-v<N>.md` (chemin fixé, C4), non scellé, portant encore un marqueur `<<…>>`,
sans bloc `empreintes-du-code` couvrant exactement `FICHIERS_GELES` (fermeture des imports du chemin réel, mesurée par
un essai) ou dont une empreinte diffère du fichier présent, sans bloc `plan-gele` conforme (grille admise, mondes, plafond
au-dessus du maximum du devis, durée au-dessus de la durée attendue haute) ; option de plan donnée en ligne de commande ;
configuration d'une autre empreinte que celle du bloc `plan-gele` ; GO autre que celui du bloc `plan-gele`, ou ligne de
GO absente, d'un autre montant que le plafond, d'un autre type, hors de validité ou révoquée (C4, C13) ; configuration sans
`plafonds_session.proposeur` (budget par appel, aucun défaut, C5), sans proposeur ni relais « kimi » et « argon », avec une
variable de clé dans l'environnement ; budget par appel sous le pire cas de la consigne la plus longue (Kimi par protocole) ;
porte de plafond qui n'accuse pas sa part (plafond réparti entre les deux relais, C5). Substitutions déclarées (texte
scellé, manifeste) dans les commandes externes : le jeton `{REGISTRE}` devient le registre de dépense cumulée de la course
(dans la sortie), et la valeur de `--plafond-cumule-usd` devient le plafond de la course.
`--verifier-seulement` (mode réel) : toutes ces gardes, adaptateurs construits et plafonds accusés, aucun appel, aucune
écriture dans la sortie.
Codes : 0 course complète (le code ne décide rien, seule la lecture gelée décide) ; 2 refus ; 3 arrêt (plafond de dépense
ou de durée : la trace partielle est écrite et scellée, aucun taux n'est lu).

Usage : python3 -I -B demonstrations/attaque_goodhart_v2.py DOSSIER_NEUF --a-blanc --graine 7 [--cartes 12]
        [--mondes W1,W2] [--rejeux-v8 200] [--rejeux-v7 20] [--processus 2] [--sequentiel]
"""

import argparse
import datetime
import importlib.util
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402

from pole import attaque_goodhart_v2 as ag  # noqa: E402
from pole.outils import ecrire_json_scelle, manifeste, sha256_fichier, verifier_scelle  # noqa: E402

ETAPE = "attaque_goodhart_v2"
SORTIE = "attaque-goodhart-v2.json"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-attaque-goodhart-v2-v[1-9][0-9]*\.md$")
DEBUT_EMPREINTES, FIN_EMPREINTES = "<!-- empreintes-du-code : début -->", "<!-- empreintes-du-code : fin -->"
DEBUT_PLAN, FIN_PLAN = "<!-- plan-gele : début -->", "<!-- plan-gele : fin -->"
MARQUEUR = re.compile(r"<<[A-Z_]+>>")
GRILLE = re.compile(r"^(\d+) cartes par monde, (\d+) unités par case$")
SHA = re.compile(r"^[0-9a-f]{64}$")
REGISTRE_COURSE = "registre-depense-cumulee-v1.jsonl"
# Valeurs fixes du bloc plan-gele (le texte les écrit, le lanceur vérifie qu'il dit la même chose que le code).
PLAN_FIXE = {"tentatives": str(ag.N_MAX), "rejeux_v8": str(ag.REJEUX["v8"]), "rejeux_v7": str(ag.REJEUX["v7"]),
             "rejeux_audit": str(ag.REJEUX_AUDIT), "fournisseurs_en_parallele": "oui", "processus_rejeux": "2"}
# Fermeture des imports du chemin réel (essai `Fermeture.test_fichiers_geles_egaux_a_la_fermeture`) : le texte scellé
# gèle l'empreinte de chacun, le lanceur refuse tout écart.
FICHIERS_GELES = (
    "demonstrations/attaque_goodhart_v2.py", "demonstrations/banc_tricheurs_v7.py", "demonstrations/banc_tricheurs_v8.py",
    "demonstrations/ideation_v2.py", "demonstrations/ideation_v4.py", "demonstrations/ideation_v5.py", "demonstrations/ideation_v6.py",
    "demonstrations/ideation_v7.py", "demonstrations/ideation_v8.py",
    "pole/__init__.py", "pole/adaptateur_kimi_v53.py", "pole/adaptateurs.py", "pole/adaptateurs_v56.py",
    "pole/aiguilleur_v53.py", "pole/attaque_goodhart_v2.py", "pole/bisociateur_v53.py", "pole/bisociateur_v54.py",
    "pole/bisociateur_v55.py", "pole/budget_v53.py", "pole/budget_v54.py", "pole/budget_v56.py", "pole/caviardage.py",
    "pole/coffre_v53.py", "pole/coffre_v55.py", "pole/configuration_v53.py", "pole/configuration_v54.py",
    "pole/configuration_v55.py", "pole/configuration_v56.py", "pole/controles_pari.py", "pole/course2_v53.py",
    "pole/course2_v54.py", "pole/course2_v55.py", "pole/course2_v56.py", "pole/cycle.py", "pole/dossier_ferme.py",
    "pole/etage_entre_generations_v53.py", "pole/etage_entre_generations_v54.py", "pole/etage_entre_generations_v55.py",
    "pole/etage_entre_generations_v56.py", "pole/fiche.py", "pole/fiches_v53.py", "pole/fiches_v54.py",
    "pole/garde_outils.py", "pole/gardes_e0_v54.py", "pole/gardes_e0_v55.py", "pole/gardes_e0_v56.py",
    "pole/graines_v53.py", "pole/ideation_v2.py", "pole/juges_croises_v53.py", "pole/memoire.py", "pole/memoire_v53.py",
    "pole/mesures_v54.py", "pole/moisson.py", "pole/noyau_v54.py", "pole/noyau_v55.py", "pole/noyau_v56.py",
    "pole/nul_filles_v2.py", "pole/nul_v8.py", "pole/outils.py", "pole/pari_apparie.py", "pole/prepilote_v54.py",
    "pole/prepilote_v55.py", "pole/prepilote_v56.py", "pole/protocole_outils.py", "pole/relais.py", "pole/relais_reel.py",
    "pole/selection_pari.py", "pole/suivi_roles_v54.py", "pole/tableau_v53.py", "pole/tests_de_mort_v2.py",
    "pole/tests_de_mort_v3.py")
OPTIONS_DE_PLAN = ("cartes", "mondes", "n_max", "rejeux_v8", "rejeux_v7", "rejeux_audit", "plafond_usd", "duree_max_h",
                   "processus", "sequentiel", "proposeur", "sans_echo", "cout_simule_usd")
A_BLANC = {"cartes": 3, "mondes": "W1,W2", "n_max": ag.N_MAX, "rejeux_v8": ag.REJEUX["v8"], "rejeux_v7": ag.REJEUX["v7"],
           "rejeux_audit": ag.REJEUX_AUDIT, "plafond_usd": 1e9, "duree_max_h": 24.0, "processus": 2, "sequentiel": False,
           "proposeur": "sortant", "sans_echo": False, "cout_simule_usd": 0.0}


class PreenregistrementRefuse(ag.AttaqueRefusee):
    """Mode réel : texte autre que le fichier fixé, non scellé, à marqueur restant, sans code gelé conforme ou sans plan."""


# --- préenregistrement (C4) ---------------------------------------------------------------------------------------------
def _bloc(texte, debut, fin, nom):
    i, j = texte.find(debut), texte.find(fin)
    if i < 0 or j < i:
        raise PreenregistrementRefuse(f"bloc « {nom} » absent du préenregistrement")
    return texte[i + len(debut):j]


def lire_plan(texte):
    """Bloc `plan-gele` : lignes « clé: valeur » ; rend le plan de la course (dict) ou lève `PreenregistrementRefuse`."""
    lignes = {}
    for l in _bloc(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise PreenregistrementRefuse(f"plan-gele : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    attendues = {"grille", "mondes", "plafond_usd", "duree_max_h", "decision_ecart", "configuration_sha256", "go"} | set(PLAN_FIXE)
    if set(lignes) != attendues:
        raise PreenregistrementRefuse(f"plan-gele : clés attendues {sorted(attendues)}, trouvées {sorted(lignes)}")
    for k, v in PLAN_FIXE.items():
        if lignes[k] != v:
            raise PreenregistrementRefuse(f"plan-gele : {k} = {lignes[k]!r}, le code gelé dit {v!r}")
    g = GRILLE.match(lignes["grille"])
    if not g or int(g.group(1)) not in ag.GRILLES or int(g.group(2)) != ag.GRILLES[int(g.group(1))]["unites"]:
        raise PreenregistrementRefuse(f"plan-gele : grille {lignes['grille']!r} ; admises : "
                                      + " ; ".join(f"{c} cartes par monde, {v['unites']} unités par case" for c, v in ag.GRILLES.items()))
    mondes = [m.strip() for m in re.split(r",| et ", lignes["mondes"]) if m.strip()]
    if not mondes or len(set(mondes)) != len(mondes) or not set(mondes) <= set(ag.MONDES):
        raise PreenregistrementRefuse(f"plan-gele : mondes {lignes['mondes']!r} (W1, W2 ou « W1 et W2 »)")
    mondes = [w for w in ag.MONDES if w in mondes]
    try:
        plafond, duree = float(lignes["plafond_usd"].replace(",", ".")), float(lignes["duree_max_h"].replace(",", "."))
    except ValueError:
        raise PreenregistrementRefuse("plan-gele : plafond_usd et duree_max_h numériques") from None
    d = ag.devis(int(g.group(1)), mondes)
    if not plafond >= d["usd_max"]:
        raise PreenregistrementRefuse(f"plan-gele : plafond {plafond} USD sous le maximum du devis ({d['usd_max']} USD, R20)")
    attendue = d["duree_parallele_h"][1] + d["rejeux_h"]
    if not duree >= attendue:
        raise PreenregistrementRefuse(f"plan-gele : durée {duree} h sous la durée attendue haute ({attendue:.1f} h : appels en "
                                      "parallèle à 40 s, plus rejeux sur deux cœurs)")
    if not lignes["decision_ecart"].strip():
        raise PreenregistrementRefuse("plan-gele : decision_ecart vide")
    if not SHA.match(lignes["configuration_sha256"]):
        raise PreenregistrementRefuse("plan-gele : configuration_sha256 = 64 caractères hexadécimaux")
    if not re.fullmatch(r"GO-\d{4}-\d{2}-\d{2}-\d{2}", lignes["go"]):
        raise PreenregistrementRefuse("plan-gele : go = GO-AAAA-MM-JJ-NN")
    return {"cartes": int(g.group(1)), "mondes": mondes, "n_max": ag.N_MAX, "rejeux": dict(ag.REJEUX),
            "rejeux_audit": ag.REJEUX_AUDIT, "plafond_usd": plafond, "duree_max_s": duree * 3600.0, "processus": 2,
            "parallele": True, "decision_ecart": lignes["decision_ecart"], "configuration_sha256": lignes["configuration_sha256"],
            "go": lignes["go"], "devis": d}


def lire_preenregistrement(chemin):
    """Mode réel : le texte au chemin fixé, scellé, sans marqueur, gelant exactement le code présent ; rend (entropie,
    empreinte, empreintes gelées, plan)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(DOSSIER_PREREG)
    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)):
        raise PreenregistrementRefuse(f"mode réel : le préenregistrement est prereg/preenregistrement-attaque-goodhart-v2-v<N>.md, "
                                      f"pas {chemin} (la graine est l'empreinte de ce fichier-là)")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    restants = sorted(set(MARQUEUR.findall(texte)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) : {restants} (décision de Lazar à porter avant scellement)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", _bloc(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code"), re.M)
    noms = [r for _, r in gelees]
    if sorted(noms) != sorted(FICHIERS_GELES) or len(set(noms)) != len(noms):
        raise PreenregistrementRefuse(f"code gelé ≠ fermeture du chemin réel : manquants {sorted(set(FICHIERS_GELES) - set(noms))}, "
                                      f"en trop {sorted(set(noms) - set(FICHIERS_GELES))}")
    ecarts = []
    for attendue, relatif in gelees:
        p = os.path.join(RACINE, relatif)
        presente = sha256_fichier(p) if os.path.isfile(p) else "absent"
        if presente != attendue:
            ecarts.append(f"{relatif} : gelé {attendue[:12]}…, présent {presente[:12]}…")
    if ecarts:
        raise PreenregistrementRefuse("code différent du code gelé : " + " ; ".join(ecarts))
    plan = lire_plan(texte)
    empreinte = sha256_fichier(reel)
    return ag.verifier_entropie(int(empreinte, 16), decisif=True), empreinte, dict((r, h) for h, r in gelees), plan


def verifier_go(registre, go, plan, cfg):
    """Le GO nommé par le texte scellé (bloc `plan-gele`, C4 : le texte, dont l'empreinte est la graine, cite son GO), sur
    une ligne entière du registre (format à 8 colonnes, `configuration_v56.verifier_go_v56` : identifiant exact, type
    calcul, accordée par Lazar, en cours de validité, non révoquée, montant égal au plafond)."""
    if not registre or not go:
        raise ag.AttaqueRefusee("mode réel : --registre-go et --go exigés (GO de Lazar sur devis)")
    if go != plan["go"]:
        raise ag.AttaqueRefusee(f"GO {go} : le texte scellé nomme {plan['go']} (aucun autre GO)")
    try:
        return cfg.verifier_go_v56(go, registre, plan["plafond_usd"])
    except cfg.GoRefuse as e:
        raise ag.AttaqueRefusee(str(e)) from None


# --- chemin réel (C5, C11) -----------------------------------------------------------------------------------------------
_V8 = {}


def charger_ideation_v8():
    if "m" not in _V8:
        spec = importlib.util.spec_from_file_location("ideation_v8_pour_goodhart_v2", os.path.join(ICI, "ideation_v8.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)  # instance propre (R12)
        _V8["m"] = m
    return _V8["m"]


def reglages_de_configuration(conf):
    """Budget par appel = plafond de session du rôle proposeur (`plafonds_session.proposeur`, aucun défaut) ; modèle demandé
    de chaque fournisseur (proposeurs de la configuration) ; relais « kimi » (protocole ou commande externe) et « argon »
    (commande externe)."""
    b = (conf.get("plafonds_session") or {}).get("proposeur")
    if not ag._reel(b, 0.0) or not b > 0:
        raise ag.AttaqueRefusee("configuration : plafonds_session.proposeur exigé (budget par appel, réel > 0, aucun défaut)")
    modeles = {}
    for f in ag.FOURNISSEURS:
        p = [x for x in conf.get("proposeurs") or [] if isinstance(x, dict) and x.get("fournisseur") == f]
        if len(p) != 1 or not isinstance(p[0].get("modele"), str) or not p[0]["modele"]:
            raise ag.AttaqueRefusee(f"configuration : exactement un proposeur « {f} » avec son modèle exact (trouvés {len(p)})")
        modeles[f] = p[0]["modele"]
    four = conf.get("fournisseurs") or {}
    types = {"kimi": ("kimi_protocole", "commande_externe"), "argon": ("commande_externe",)}
    for f, t in types.items():
        if (four.get(f) or {}).get("type") not in t:
            raise ag.AttaqueRefusee(f"configuration : relais « {f} » de type {' ou '.join(t)} exigé (trouvé {(four.get(f) or {}).get('type')!r})")
    return float(b), modeles


def substituer_commandes(conf, registre, plafond_usd):
    """Copie de la configuration où, dans chaque commande externe, le jeton `{REGISTRE}` devient `registre` et la valeur de
    `--plafond-cumule-usd` devient le plafond de la course ; rend (copie, substitutions faites). Déclaré au texte scellé et
    écrit au manifeste ; la configuration lue (et son empreinte) reste celle du fichier."""
    copie = json.loads(json.dumps(conf))
    faites = []
    for nom, f in sorted((copie.get("fournisseurs") or {}).items()):
        c = f.get("commande") if isinstance(f, dict) and f.get("type") == "commande_externe" else None
        if not isinstance(c, list):
            continue
        for i, x in enumerate(c):
            if isinstance(x, str) and "{REGISTRE}" in x:
                c[i] = x.replace("{REGISTRE}", registre)
                faites.append({"fournisseur": nom, "argument": i, "avant": x, "apres": c[i]})
            if x == "--plafond-cumule-usd" and i + 1 < len(c):
                avant, c[i + 1] = c[i + 1], f"{plafond_usd:g}"
                faites.append({"fournisseur": nom, "argument": i + 1, "avant": avant, "apres": c[i + 1]})
    return copie, faites


def consigne_la_plus_longue():
    """Consigne de pire taille : tentative 16 du bras retour sous v8, historique de 15 lois de 6 000 octets."""
    c = ag.carte(0, 0, "W1")
    loi = {"type": "fixe", "probas": [1.0, 1.0, 1.0]}
    remplissage = {"type": "melange", "composantes": [loi] * 300, "poids": [1 / 300] * 300}
    while len(json.dumps(remplissage, separators=(",", ":"))) > ag.OCTETS_MAX_LOI:
        remplissage["composantes"].pop()
        remplissage["poids"] = [1 / len(remplissage["composantes"])] * len(remplissage["composantes"])
    hist = [{"tentative": k, "loi": remplissage, "verdict": "non promue", "log_w_max": -123.45} for k in range(1, 16)]
    return ag.consigne(c, hist, "retour", 16, "v8")


def proposeurs_reels(conf, plafond_usd, base_sessions, sortie):
    """Adaptateurs du chemin réel, plafond réparti entre les portes, pire cas du budget par appel ; rend (proposeurs,
    accusés, informations du manifeste)."""
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise ag.AttaqueRefusee(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais "
                                "tiennent les clés")
    budget, modeles = reglages_de_configuration(conf)
    conf, substitutions = substituer_commandes(conf, os.path.join(os.path.abspath(sortie), REGISTRE_COURSE), plafond_usd)
    v8 = charger_ideation_v8()
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf, sortie, base_sessions)
    if sorted(n for n in adaptateurs if n in ag.FOURNISSEURS) != sorted(ag.FOURNISSEURS):
        raise ag.AttaqueRefusee(f"configuration : adaptateurs « kimi » et « argon » exigés, trouvés {sorted(adaptateurs)}")
    longue = consigne_la_plus_longue()
    kimi = adaptateurs["kimi"]
    if hasattr(kimi, "corps") and kimi.corps(longue, budget, modeles["kimi"])[0] is None:
        raise ag.AttaqueRefusee(f"budget par appel {budget} USD sous le pire cas de Kimi pour la consigne la plus longue "
                                f"({len(longue.encode('utf-8'))} octets) : les dernières tentatives seraient refusées")
    part = plafond_usd / len(ag.FOURNISSEURS)
    accuses = {n: portes[n].transmettre(ETAPE, part) for n in ag.FOURNISSEURS}
    proposeurs = {}
    for n in ag.FOURNISSEURS:
        d = os.path.join(base_sessions, n)
        os.makedirs(d, exist_ok=True)
        proposeurs[n] = ag.ProposeurAdaptateur(adaptateurs[n], d, budget, modeles[n])
    infos = {"budget_appel_usd": budget, "modeles_demandes": modeles, "role_pole": ag.ROLE, "part_par_relais_usd": part,
             "substitutions_dans_les_commandes": substitutions,
             "consigne_la_plus_longue_octets": len(longue.encode("utf-8")),
             "adaptateurs": {n: (adaptateurs[n].description() if hasattr(adaptateurs[n], "description") else type(adaptateurs[n]).__name__)
                             for n in ag.FOURNISSEURS},
             "portes": {n: portes[n].description() for n in ag.FOURNISSEURS}}
    return proposeurs, accuses, infos


def commit():
    try:
        r = subprocess.run(["git", "-C", RACINE, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10)
        etat = subprocess.run(["git", "-C", RACINE, "status", "--porcelain"], capture_output=True, text=True, timeout=30)
        return {"commit": r.stdout.strip() or "inconnu", "arbre_modifie": bool(etat.stdout.strip())}
    except (OSError, subprocess.SubprocessError):
        return {"commit": "inconnu (hors dépôt git)", "arbre_modifie": None}


# --- programme ----------------------------------------------------------------------------------------------------------
def principal(argv=None):
    a = argparse.ArgumentParser(description="Attaque de Goodhart contre le juge statistique (v2)")
    a.add_argument("dossier")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true", help="proposeurs scriptés, sans réseau (exploratoire)")
    g.add_argument("--preenregistrement", help="mode réel : préenregistrement scellé (graine = son empreinte)")
    a.add_argument("--graine", type=int)
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--verifier-seulement", action="store_true")
    a.add_argument("--cartes", type=int)
    a.add_argument("--mondes")
    a.add_argument("--n-max", type=int)
    a.add_argument("--rejeux-v8", type=int)
    a.add_argument("--rejeux-v7", type=int)
    a.add_argument("--rejeux-audit", type=int)
    a.add_argument("--plafond-usd", type=float)
    a.add_argument("--duree-max-h", type=float)
    a.add_argument("--processus", type=int)
    a.add_argument("--sequentiel", action="store_true", default=None)
    a.add_argument("--proposeur", choices=("sortant", "melangeur"))
    a.add_argument("--sans-echo", action="store_true", default=None)
    a.add_argument("--cout-simule-usd", type=float, help="à blanc : coût fictif par appel scripté (liste d'arrêt)")
    args = a.parse_args(argv)
    from pole import configuration_v56 as cfg
    base_sessions = None
    try:
        if os.path.exists(args.dossier) and os.listdir(args.dossier):
            raise FileExistsError(f"dossier de sortie non vide : {args.dossier} (on n'écrase jamais)")
        donnees = {k: getattr(args, k) for k in OPTIONS_DE_PLAN if getattr(args, k) is not None}
        if args.a_blanc:
            if args.graine is None or args.moteur or args.configuration or args.go or args.verifier_seulement:
                raise ag.AttaqueRefusee("à blanc : --graine G seulement (ni moteur réel, ni configuration, ni GO)")
            r = dict(A_BLANC, **donnees)
            plan = {"cartes": r["cartes"], "mondes": [w for w in ag.MONDES if w in r["mondes"].split(",")], "n_max": r["n_max"],
                    "rejeux": {"v8": r["rejeux_v8"], "v7": r["rejeux_v7"]}, "rejeux_audit": r["rejeux_audit"],
                    "plafond_usd": r["plafond_usd"], "duree_max_s": r["duree_max_h"] * 3600.0, "processus": r["processus"],
                    "parallele": not r["sequentiel"]}
            if sorted(plan["mondes"]) != sorted(set(r["mondes"].split(","))):
                raise ag.AttaqueRefusee(f"--mondes : parmi {ag.MONDES}, reçu {r['mondes']!r}")
            ag.verifier_plan(plan)
            entropie = ag.verifier_entropie(args.graine, decisif=False)
            mode, preenregistrement, conf_info = "a-blanc (exploratoire)", None, None
        else:
            if args.graine is not None:
                raise ag.AttaqueRefusee("mode réel : la graine est l'empreinte du préenregistrement, --graine refusée")
            if donnees:
                raise ag.AttaqueRefusee(f"mode réel : le plan est lu dans le texte scellé ; options refusées : {sorted(donnees)}")
            if args.moteur != "reel" or not args.confirmer_moteur_reel or not args.configuration:
                raise ag.AttaqueRefusee("mode réel : --configuration, --moteur reel et --confirmer-moteur-reel exigés")
            entropie, empreinte, gelees, plan = lire_preenregistrement(args.preenregistrement)
            if not os.path.isfile(args.configuration):
                raise ag.AttaqueRefusee(f"configuration introuvable : {args.configuration}")
            sha_conf = sha256_fichier(args.configuration)
            if sha_conf != plan["configuration_sha256"]:
                raise ag.AttaqueRefusee(f"configuration d'empreinte {sha_conf[:12]}… : le texte scellé gèle "
                                        f"{plan['configuration_sha256'][:12]}… (aucune autre configuration)")
            go = verifier_go(args.registre_go, args.go, plan, cfg)
            conf = cfg.lire_configuration_v56(args.configuration)
            base_sessions = tempfile.mkdtemp(prefix="attaque-goodhart-v2-sessions-")  # hors de la sortie
            proposeurs, accuses, infos = proposeurs_reels(conf, plan["plafond_usd"], base_sessions,
                                                          os.path.abspath(args.dossier))
            mode = "reel (decisif)"
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": {k: v for k, v in plan.items() if k != "devis"},
                                 "devis": plan["devis"], "go": go}
            conf_info = dict(infos, chemin=os.path.abspath(args.configuration), sha256=sha_conf,
                             empreinte_configuration=conf.get("empreinte_configuration"), accuses_plafond=accuses)
            if args.verifier_seulement:
                print(json.dumps({"verification": "conforme", "ecriture": "aucune", "appel": "aucun", "plan": preenregistrement["plan"],
                                  "configuration": conf_info}, ensure_ascii=False, indent=1, default=str))
                return 0
    except (FileExistsError, ag.AttaqueRefusee, cfg.ConfigurationRefusee) as e:
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001 — refus nommé (relais, porte, configuration), jamais de repli
        print(f"refus : {type(e).__name__} : {e}", file=sys.stderr)
        return 2
    if args.a_blanc:
        proposeurs = {f: ag.ProposeurScripte(plan_mode(args), echo=not args.sans_echo, cout_par_appel=args.cout_simule_usd or 0.0)
                      for f in ag.FOURNISSEURS}
    os.makedirs(args.dossier, exist_ok=True)
    m = manifeste(attaque=ag.VERSION, mode=mode, entropie_racine=str(entropie),
                  plan={k: v for k, v in plan.items() if k != "devis"}, preenregistrement=preenregistrement,
                  configuration=conf_info, coeur=ag.description(), numpy=np.__version__, python=platform.python_version(),
                  depot=commit(), code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                  proposeur_a_blanc=(plan_mode(args) + ("" if not args.sans_echo else ", sans écho")) if args.a_blanc else None)
    m["regle_des_graines"] = ("SeedSequence (R9) : entropie = int(SHA-256 du préenregistrement scellé, 16) en mode réel, --graine "
                              "(< 2^64) à blanc ; carte c du monde w : spawn_key=(cle('monde|w'), c) ; développement : "
                              "(cle('developpement|w'), c) ; évaluation de la tentative k : (cle('<monde>|<fournisseur>|<condition>|"
                              "<juge>|scenario|noyau|frais'), c, k) ; rejeu r : (cle('rejeu|<monde>|…'), c, k, 1 + r) ; audit A2 : "
                              "(cle('audit|<monde>|…'), c, k, 1 + r) ; rééchantillonnage : (cle('bootstrap'), cle('<monde>|<juge>'))")
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), m)
    compteur = ag.Compteur(plan["plafond_usd"], plan["duree_max_s"], time.time)
    try:
        suites, rejeux, audits = ag.jouer_tout(proposeurs, entropie, plan, compteur, decisif=not args.a_blanc,
                                               parallele=plan["parallele"], processus=plan["processus"])
    except ag.ArretAttaque as e:
        rapport = {"attaque": ag.VERSION, "mode": mode, "arret": str(e), "appels": compteur.appels, "reprises": compteur.reprises,
                   "depense_usd": round(compteur.usd, 4), "depense_par_fournisseur_usd": compteur.par_fournisseur,
                   "duree_s": round(time.time() - compteur.debut, 1), "issue": "non jugeable (arrêt) : aucun taux lu",
                   "suites_partielles": e.partiel.get("suites", []), "rejeux_partiels": e.partiel.get("rejeux", [])}
        ecrire_json_scelle(os.path.join(args.dossier, SORTIE), rapport)
        print(json.dumps({k: rapport[k] for k in ("mode", "arret", "appels", "depense_usd", "duree_s", "issue")}, ensure_ascii=False),
              file=sys.stderr)
        return 3
    lecture = ag.lire(suites, rejeux, audits, plan["mondes"], plan["cartes"], entropie)
    rapport = {"attaque": ag.VERSION, "mode": mode, "preenregistrement": preenregistrement, "appels": compteur.appels,
               "reprises": compteur.reprises, "depense_usd": round(compteur.usd, 4),
               "depense_par_fournisseur_usd": compteur.par_fournisseur, "appels_budget_depasse": compteur.budget_depasse,
               "modeles_servis": compteur.modeles_servis, "duree_s": round(time.time() - compteur.debut, 1),
               "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
               "lecture": lecture, "suites": suites, "rejeux": rejeux, "audit_A2": audits}
    ecrire_json_scelle(os.path.join(args.dossier, SORTIE), rapport)
    print(json.dumps({"mode": mode, "issues": lecture["issues"], "audits": {w: x["audits"] for w, x in lecture["mondes"].items()},
                      "appels": compteur.appels, "depense_usd": rapport["depense_usd"], "duree_s": rapport["duree_s"]},
                     ensure_ascii=False, indent=1))
    return 0


def plan_mode(args):
    return args.proposeur or A_BLANC["proposeur"]


if __name__ == "__main__":
    sys.exit(principal())
