"""Attaque de Goodhart contre le juge statistique, v5 (mondes **W2 et W2 gradué** contre le juge v9) : lanceur (fichier neuf, R12).
Cœur : `pole/attaque_goodhart_v5.py`, qui importe la v4. Ce lanceur charge le lanceur v4 (`demonstrations/attaque_goodhart_v4.py`,
tel quel, instance propre), qui charge les lanceurs v3 et v2, pour tout ce qui ne change pas : lecture des lignes de fournisseur,
règle « relais perdu », GO, réglages de la configuration, substitutions des commandes, commit, chargement d'`ideation_v8`.

Ce qui change par rapport au lanceur v4 :
- **texte** : `prereg/preenregistrement-attaque-goodhart-v5-v<N>.md` seulement (mode course) ; un texte de la v4 (ou antérieur)
  est refusé par son nom, et un texte au nom de la v5 dont le bloc `plan-gele` est celui de la v4 (sans `go_machine` ni `dose_w2g`,
  `juge_ancien: W1=v7, W2=v8`, mondes W1) est refusé par ses clés ou ses valeurs ; réciproquement, le lanceur v4 refuse un texte
  de la v5 (nom et clés) ;
- **bloc `plan-gele`** : lignes neuves **`go_machine`** (GO de la machine de l'hôte durable, forme GO-AAAA-MM-JJ-NN, rapporté au
  manifeste ; vérifié contre le registre par le lanceur durable) et **`dose_w2g`** (dose λ de W2g, lue, vérifiée par
  `attaque_goodhart_v5.verifier_plan` : réel dans ]0 ; 1] de la grille gelée de l'épreuve hors ligne) ; valeur fixe
  `juge_ancien: W2=v8, W2g=v8` ; mondes « W2 et W2g » ; devis de la v5 (W2g pris comme W2) pour le plafond et la durée ;
- **code gelé** : `FICHIERS_GELES` = celui du lanceur v4, plus les deux fichiers v5 (fermeture mesurée : essai `Fermeture`) ;
- **étape de dépense** : `attaque_goodhart_v5/<nom>` (jamais celle de la v3 ni de la v4) ;
- **à blanc** : Argon seul, 1 fil, 24 cartes par monde, W2 et W2g à la dose 0,5, proposeur « sortant_v9 » ; `--dose-w2g`.

Codes : 0 course complète (le code ne décide rien) ; 2 refus avant tout appel et toute écriture ; 3 arrêt (plafond, part, durée :
trace partielle écrite et scellée, aucun taux lu).

Usage : python -I -B demonstrations/attaque_goodhart_v5.py DOSSIER (--a-blanc --graine G [options] |
        --preenregistrement P --configuration CONF --moteur reel --confirmer-moteur-reel --registre-go R --go ID [--verifier-seulement])
"""

import argparse
import datetime
import importlib.util
import json
import os
import platform
import re
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
sys.path.insert(0, RACINE)

import numpy as np  # noqa: E402

from pole import attaque_goodhart_v5 as a5  # noqa: E402
from pole.outils import ecrire_json_scelle, manifeste, sha256_fichier, verifier_scelle  # noqa: E402


def _charger_lanceur_v4():
    spec = importlib.util.spec_from_file_location("attaque_goodhart_v4_lanceur_pour_v5", os.path.join(ICI, "attaque_goodhart_v4.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # instance propre, inchangée (R12)
    return m


l4 = _charger_lanceur_v4()
l3 = l4.l3
l2 = l4.l2
a4 = a5.a4
a3 = a5.a3
ag = a5.ag
ETAPE = "attaque_goodhart_v5"


def etape_du_fournisseur(nom):
    """Étape de dépense propre à un fournisseur de la v5 : `attaque_goodhart_v5/<nom>` (jamais celle de la v3 ni de la v4)."""
    return f"{ETAPE}/{nom}"


SORTIE = "attaque-goodhart-v5.json"
DOSSIER_PREREG = os.path.join(RACINE, "prereg")
NOM_PREREG = re.compile(r"^preenregistrement-attaque-goodhart-v5-v[1-9][0-9]*\.md$")
DEBUT_EMPREINTES, FIN_EMPREINTES, DEBUT_PLAN, FIN_PLAN = l2.DEBUT_EMPREINTES, l2.FIN_EMPREINTES, l2.DEBUT_PLAN, l2.FIN_PLAN
MARQUEUR, SHA, GRILLE, REGISTRE_COURSE = l3.MARQUEUR, l2.SHA, l2.GRILLE, l2.REGISTRE_COURSE
PreenregistrementRefuse = l2.PreenregistrementRefuse
GO = re.compile(r"^GO-\d{4}-\d{2}-\d{2}-\d{2}$")
JUGE_ANCIEN_TEXTE = ", ".join(f"{w}={n}" for w, n in sorted(a5.JUGE_ANCIEN.items()))
PLAN_FIXE = {"tentatives": str(ag.N_MAX), "rejeux_v9": str(a5.REJEUX["v9"]), "rejeux_ancien": str(a5.REJEUX["ancien"]),
             "rejeux_audit": str(a5.REJEUX_AUDIT), "juge_ancien": JUGE_ANCIEN_TEXTE, "fournisseurs_en_parallele": "oui",
             "processus_rejeux": "2"}
CLES_PLAN = {"mode", "grille", "mondes", "fournisseurs", "essais_avant_repli", "relais_perdu_h", "plafond_usd", "duree_max_h",
             "decision_ecart", "configuration_sha256", "go", "go_machine", "dose_w2g"}
FICHIERS_GELES = tuple(sorted(set(l4.FICHIERS_GELES) | {"demonstrations/attaque_goodhart_v5.py", "pole/attaque_goodhart_v5.py"}))
OPTIONS_DE_PLAN = ("cartes", "mondes", "dose_w2g", "fournisseurs", "fils", "panne", "code_panne", "muet", "coupure_relais_s", "relais_perdu_h",
                   "essais_avant_repli", "n_max", "rejeux_v9", "rejeux_ancien", "rejeux_audit", "plafond_usd", "duree_max_h", "processus",
                   "sequentiel", "proposeur", "sans_echo", "cout_simule_usd")
A_BLANC = {"cartes": 24, "mondes": "W2,W2g", "dose_w2g": 0.5, "fournisseurs": "argon", "fils": "1", "panne": None, "code_panne": None,
           "muet": False, "coupure_relais_s": None, "relais_perdu_h": "aucun", "essais_avant_repli": 3, "n_max": ag.N_MAX,
           "rejeux_v9": a5.REJEUX["v9"], "rejeux_ancien": a5.REJEUX["ancien"], "rejeux_audit": a5.REJEUX_AUDIT, "plafond_usd": 1e9,
           "duree_max_h": 72.0, "processus": 2, "sequentiel": False, "proposeur": "sortant_v9", "sans_echo": False, "cout_simule_usd": 0.0}


# --- préenregistrement : bloc plan-gele v5 ----------------------------------------------------------------------------------
def lire_plan(texte):
    """Bloc `plan-gele` v5 (mode course) : rend le plan ou lève `PreenregistrementRefuse`. Fournisseurs lus du texte (lignes
    `fournisseur_<nom>` de la v3) ; `go_machine` et `dose_w2g` exigés ; dose vérifiée par le cœur v5 (grille gelée, 0 refusé) ;
    devis de la v5 : plafond ≥ maximum, durée ≥ durée attendue haute."""
    lignes = {}
    for l in l2._bloc(texte, DEBUT_PLAN, FIN_PLAN, "plan-gele").splitlines():
        m = re.match(r"^\s*([a-z0-9_]+)\s*:\s*(.+?)\s*$", l)
        if m:
            if m.group(1) in lignes:
                raise PreenregistrementRefuse(f"plan-gele : clé {m.group(1)!r} en double")
            lignes[m.group(1)] = m.group(2)
    if lignes.get("mode") not in a5.MODES:
        raise PreenregistrementRefuse(f"plan-gele : mode = course (la v5 n'a pas de mode essai), reçu {lignes.get('mode')!r}")
    noms = [n.strip() for n in lignes.get("fournisseurs", "").split(",") if n.strip()]
    lignes_f = {l3.LIGNE_FOURNISSEUR.match(k).group(1): v for k, v in lignes.items() if l3.LIGNE_FOURNISSEUR.match(k)}
    attendues = CLES_PLAN | set(PLAN_FIXE) | {f"fournisseur_{n}" for n in noms}
    if set(lignes) != attendues:
        raise PreenregistrementRefuse(f"plan-gele : clés attendues {sorted(attendues)}, trouvées {sorted(lignes)}")
    if not noms or len(set(noms)) != len(noms) or set(lignes_f) != set(noms):
        raise PreenregistrementRefuse(f"plan-gele : fournisseurs {noms!r} : liste non vide sans doublon, une ligne fournisseur_<nom> chacun")
    for k, v in PLAN_FIXE.items():
        if lignes[k] != v:
            raise PreenregistrementRefuse(f"plan-gele : {k} = {lignes[k]!r}, le code gelé dit {v!r}")
    try:
        fournisseurs = a3.verifier_fournisseurs([l3.lire_fournisseur(n, lignes_f[n]) for n in noms])
    except a3.AttaqueRefusee as e:
        raise PreenregistrementRefuse(f"plan-gele : {e}") from None
    mondes = [m.strip() for m in re.split(r",| et ", lignes["mondes"]) if m.strip()]
    if not mondes or len(set(mondes)) != len(mondes) or not set(mondes) <= set(a5.MONDES):
        raise PreenregistrementRefuse(f"plan-gele : mondes {lignes['mondes']!r} (W2, W2g ou « W2 et W2g »)")
    mondes = [w for w in a5.MONDES if w in mondes]
    essais = l3._entier(lignes["essais_avant_repli"], "essais_avant_repli")
    plafond, duree = l3._nombre(lignes["plafond_usd"], "plafond_usd"), l3._nombre(lignes["duree_max_h"], "duree_max_h")
    dose = l3._nombre(lignes["dose_w2g"], "dose_w2g")
    g = GRILLE.match(lignes["grille"])
    if not g:
        raise PreenregistrementRefuse(f"plan-gele : grille {lignes['grille']!r} (« C cartes par monde, U unités par case »)")
    if not lignes["decision_ecart"].strip():
        raise PreenregistrementRefuse("plan-gele : decision_ecart vide")
    plan = {"mode": "course", "mondes": mondes, "fournisseurs": fournisseurs, "n_max": ag.N_MAX, "essais_avant_repli": essais,
            "relais_perdu_h": lignes["relais_perdu_h"], "relais_perdu_s": l3.lire_relais_perdu(lignes["relais_perdu_h"]),
            "plafond_usd": plafond, "duree_max_s": duree * 3600.0, "parallele": True, "configuration_sha256": lignes["configuration_sha256"],
            "go": lignes["go"], "go_machine": lignes["go_machine"], "dose_w2g": dose, "cartes": int(g.group(1)),
            "unites_par_case": int(g.group(2)), "rejeux": dict(a5.REJEUX), "rejeux_audit": a5.REJEUX_AUDIT, "processus": 2,
            "decision_ecart": lignes["decision_ecart"]}
    try:
        a5.verifier_plan(plan)
        d = a5.devis(plan["cartes"], mondes, fournisseurs)
    except a3.AttaqueRefusee as e:
        raise PreenregistrementRefuse(f"plan-gele : {e}") from None
    if not plafond >= d["total"]["usd_max"]:
        raise PreenregistrementRefuse(f"plan-gele : plafond {plafond} USD sous le maximum du devis ({d['total']['usd_max']} USD ; R20)")
    if not duree >= d["total"]["duree_attendue_haute_h"]:
        raise PreenregistrementRefuse(f"plan-gele : durée {duree} h sous la durée attendue haute ({d['total']['duree_attendue_haute_h']:.2f} h : "
                                      "appels du fournisseur le plus long à ses fils, évaluations en course, rejeux sur deux cœurs)")
    if not SHA.match(lignes["configuration_sha256"]):
        raise PreenregistrementRefuse("plan-gele : configuration_sha256 = 64 caractères hexadécimaux")
    if not GO.match(lignes["go"]):
        raise PreenregistrementRefuse("plan-gele : go = GO-AAAA-MM-JJ-NN")
    if not GO.match(lignes["go_machine"]):
        raise PreenregistrementRefuse("plan-gele : go_machine = GO-AAAA-MM-JJ-NN (GO de la machine de l'hôte durable)")
    if lignes["go_machine"] == lignes["go"]:
        raise PreenregistrementRefuse("plan-gele : go_machine égal à go (la machine et les appels ont chacun leur GO)")
    plan["devis"] = d
    return plan


def lire_preenregistrement(chemin):
    """Mode réel : `prereg/preenregistrement-attaque-goodhart-v5-v<N>.md`, scellé, sans marqueur, gelant exactement le code présent ;
    rend (entropie, empreinte, empreintes gelées, plan)."""
    reel, dossier = os.path.realpath(chemin), os.path.realpath(DOSSIER_PREREG)
    if os.path.dirname(reel) != dossier or not NOM_PREREG.match(os.path.basename(reel)):
        raise PreenregistrementRefuse("mode réel : le texte est prereg/preenregistrement-attaque-goodhart-v5-v<N>.md, "
                                      f"pas {chemin} (la graine est son empreinte)")
    if not os.path.isfile(reel):
        raise PreenregistrementRefuse(f"préenregistrement introuvable : {chemin}")
    if not verifier_scelle(reel):
        raise PreenregistrementRefuse(f"préenregistrement non scellé (compagnon .sha256 absent ou non conforme) : {chemin}")
    with open(reel, encoding="utf-8") as f:
        texte = f.read()
    restants = sorted(set(MARQUEUR.findall(texte)))
    if restants:
        raise PreenregistrementRefuse(f"marqueur(s) non rempli(s) : {restants} (à lever avant scellement)")
    gelees = re.findall(r"^([0-9a-f]{64})  (\S+)$", l2._bloc(texte, DEBUT_EMPREINTES, FIN_EMPREINTES, "empreintes-du-code"), re.M)
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


# --- chemin réel ----------------------------------------------------------------------------------------------------------------
def proposeurs_reels(conf, plan, base_sessions, sortie):
    """`proposeurs_reels` du lanceur v4, avec l'étape de dépense de la v5 (`attaque_goodhart_v5/<nom>`) et la consigne la plus
    longue mesurée sur W2 et sur W2g (à la dose du plan) ; rend (proposeurs, accusés, informations du manifeste)."""
    from pole.adaptateurs_v56 import AdaptateurCommandeExterneV56
    from pole.relais import noms_de_cle_presents
    presents = noms_de_cle_presents(os.environ)
    if presents:
        raise ag.AttaqueRefusee(f"variables de clé dans l'environnement de l'orchestrateur ({', '.join(presents)}) : les relais tiennent les clés")
    fournisseurs = plan["fournisseurs"]
    budget, modeles = l3.reglages_de_configuration(conf, fournisseurs)
    conf, substitutions = l2.substituer_commandes(conf, os.path.join(os.path.abspath(sortie), REGISTRE_COURSE), plan["plafond_usd"])
    v8 = l2.charger_ideation_v8()
    adaptateurs, portes = v8.adaptateurs_reels_v56(conf, sortie, base_sessions)
    manquants = [f["nom"] for f in fournisseurs if f["nom"] not in adaptateurs]
    if manquants:
        raise ag.AttaqueRefusee(f"configuration : adaptateurs manquants pour {manquants}")
    for f in fournisseurs:
        if not isinstance(adaptateurs[f["nom"]], AdaptateurCommandeExterneV56):
            raise ag.AttaqueRefusee(f"fournisseur « {f['nom']} » : commande externe v56 exigée, trouvé {type(adaptateurs[f['nom']]).__name__}")
    part = plan["plafond_usd"] / len(fournisseurs)
    accuses = {f["nom"]: portes[f["nom"]].transmettre(etape_du_fournisseur(f["nom"]), part) for f in fournisseurs}
    for f in fournisseurs:
        if accuses[f["nom"]].get("etape") != etape_du_fournisseur(f["nom"]) or abs(accuses[f["nom"]].get("plafond_usd", -1) - part) > 0.01:
            raise ag.AttaqueRefusee(f"porte de « {f['nom']} » : accusé {accuses[f['nom']]!r}, attendu étape "
                                    f"{etape_du_fournisseur(f['nom'])!r} et part {part:.2f} USD")
    etapes = {f["nom"]: {"etape": etape_du_fournisseur(f["nom"]), "part_usd": part, "variables": ["ETAPE_POLE", "PLAFOND_ETAPE_USD"]}
              for f in fournisseurs}
    proposeurs = {}
    for f in fournisseurs:
        d = os.path.join(base_sessions, f["nom"])
        os.makedirs(d, exist_ok=True)
        proposeurs[f["nom"]] = a5.ProposeurAdaptateur(adaptateurs[f["nom"]], d, budget, (f["modele"],) + ((f["repli"],) if f.get("repli") else ()))
    cartes = [a5.carte(1, 0, w, plan.get("dose_w2g") if w == "W2g" else None) for w in plan["mondes"]]
    longue = max((a5.consigne(c, [], cond, 1, j) for c in cartes for cond, j in a5.SUITES), key=len)
    infos = {"budget_appel_usd": budget, "modeles_demandes": modeles, "replis_declares": {f["nom"]: f.get("repli") for f in fournisseurs},
             "fils": {f["nom"]: f["fils"] for f in fournisseurs}, "ports": {f["nom"]: f["port"] for f in fournisseurs},
             "role_pole": ag.ROLE, "part_par_relais_usd": part, "etapes_de_depense": etapes,
             "substitutions_dans_les_commandes": substitutions,
             "consigne_vierge_la_plus_longue_octets": len(longue.encode("utf-8")),
             "pire_cas_par_appel": "tenu par chaque commande externe (PLAFOND_SESSION_USD = budget par appel)",
             "adaptateurs": {f["nom"]: adaptateurs[f["nom"]].description() for f in fournisseurs},
             "portes": {f["nom"]: portes[f["nom"]].description() for f in fournisseurs}}
    return proposeurs, accuses, infos


# --- programme --------------------------------------------------------------------------------------------------------------------
def principal(argv=None):
    a = argparse.ArgumentParser(description="Attaque de Goodhart contre le juge statistique (v5 : W2 et W2 gradué contre le juge v9)")
    a.add_argument("dossier")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--a-blanc", action="store_true", help="proposeurs scriptés, sans réseau (exploratoire)")
    g.add_argument("--preenregistrement", help="mode réel : texte scellé (graine = son empreinte)")
    a.add_argument("--graine", type=int)
    a.add_argument("--configuration")
    a.add_argument("--moteur", choices=("reel",))
    a.add_argument("--confirmer-moteur-reel", action="store_true")
    a.add_argument("--registre-go")
    a.add_argument("--go")
    a.add_argument("--verifier-seulement", action="store_true")
    a.add_argument("--cartes", type=int)
    a.add_argument("--mondes")
    a.add_argument("--dose-w2g", type=float, help="à blanc : dose λ de W2g (défaut 0,5 ; en réel, lue du texte scellé)")
    a.add_argument("--fournisseurs", help="à blanc : noms parmi les plans de référence de la v3 (défaut : argon)")
    a.add_argument("--fils", help="à blanc : N (tous) ou nom=N,… (défaut : 1)")
    a.add_argument("--panne", help="à blanc : MODELE:I-J ou MODELE:* ; plusieurs séparés par « ; »")
    a.add_argument("--code-panne", type=int, help="à blanc : code de sortie simulé des pannes (3 relais, 4 budget, 5 modèle, 6 délai)")
    a.add_argument("--muet", action="store_true", default=None)
    a.add_argument("--coupure-relais-s", type=float)
    a.add_argument("--relais-perdu-h")
    a.add_argument("--essais-avant-repli", type=int)
    a.add_argument("--n-max", type=int)
    a.add_argument("--rejeux-v9", type=int)
    a.add_argument("--rejeux-ancien", type=int)
    a.add_argument("--rejeux-audit", type=int)
    a.add_argument("--plafond-usd", type=float)
    a.add_argument("--duree-max-h", type=float)
    a.add_argument("--processus", type=int)
    a.add_argument("--sequentiel", action="store_true", default=None)
    a.add_argument("--proposeur", choices=("sortant_v9", "sortant", "melangeur"))
    a.add_argument("--sans-echo", action="store_true", default=None)
    a.add_argument("--cout-simule-usd", type=float)
    args = a.parse_args(argv)
    from pole import configuration_v56 as cfg
    try:
        if os.path.exists(args.dossier) and os.listdir(args.dossier):
            raise FileExistsError(f"dossier de sortie non vide : {args.dossier} (on n'écrase jamais)")
        donnees = {k: getattr(args, k) for k in OPTIONS_DE_PLAN if getattr(args, k) is not None}
        if args.a_blanc:
            if args.graine is None or args.moteur or args.configuration or args.go or args.verifier_seulement:
                raise ag.AttaqueRefusee("à blanc : --graine G seulement (ni moteur réel, ni configuration, ni GO)")
            r = dict(A_BLANC, **donnees)
            mondes = [w for w in a5.MONDES if w in r["mondes"].split(",")]
            if sorted(mondes) != sorted(set(r["mondes"].split(","))):
                raise ag.AttaqueRefusee(f"--mondes : parmi {a5.MONDES}, reçu {r['mondes']!r}")
            fournisseurs = l3.fournisseurs_a_blanc(r["fournisseurs"], r["fils"])
            plan = {"mode": "course", "cartes": r["cartes"], "mondes": mondes, "fournisseurs": fournisseurs, "n_max": r["n_max"],
                    "essais_avant_repli": r["essais_avant_repli"], "plafond_usd": r["plafond_usd"], "duree_max_s": r["duree_max_h"] * 3600.0,
                    "processus": r["processus"], "parallele": not r["sequentiel"], "exiger_grille": False,
                    "rejeux": {"v9": r["rejeux_v9"], "ancien": r["rejeux_ancien"]}, "rejeux_audit": r["rejeux_audit"],
                    "relais_perdu_h": str(r["relais_perdu_h"]), "dose_w2g": r["dose_w2g"] if "W2g" in mondes else None}
            plan["relais_perdu_s"] = l3.lire_relais_perdu(plan["relais_perdu_h"])
            a5.verifier_plan(plan)
            entropie = ag.verifier_entropie(args.graine, decisif=False)
            mode, preenregistrement, conf_info = "a-blanc (exploratoire, course)", None, None
            pannes = l3.pannes_a_blanc(r["panne"])
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
            go = l3.verifier_go(args.registre_go, args.go, plan, cfg)
            conf = cfg.lire_configuration_v56(args.configuration)
            base_sessions = tempfile.mkdtemp(prefix="attaque-goodhart-v5-sessions-")  # hors de la sortie
            proposeurs, accuses, infos = proposeurs_reels(conf, plan, base_sessions, os.path.abspath(args.dossier))
            mode = "reel (decisif, course)"
            preenregistrement = {"chemin": os.path.relpath(os.path.realpath(args.preenregistrement), RACINE), "sha256": empreinte,
                                 "empreintes_du_code_verifiees": gelees, "plan": {k: v for k, v in plan.items() if k != "devis"},
                                 "devis": plan["devis"], "go": go, "go_machine": plan["go_machine"]}
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
        proposeurs = {f["nom"]: a5.ProposeurScripte(args.proposeur or A_BLANC["proposeur"], echo=not args.sans_echo,
                                                    cout_par_appel=args.cout_simule_usd or 0.0, pannes=pannes, code_echec=args.code_panne,
                                                    muet=bool(args.muet), coupure_relais_s=args.coupure_relais_s)
                      for f in plan["fournisseurs"]}
    os.makedirs(args.dossier, exist_ok=True)
    verite_w2g = None
    if "W2g" in plan["mondes"]:
        verite_w2g = {"dose_w2g": plan["dose_w2g"], "definition": a5.description()["monde_w2g"], "ecart": a5.description()["ecart_w2g"],
                      "cartes": {str(ci): a5.carte(entropie, ci, "W2g", plan["dose_w2g"])["verite"] for ci in range(plan["cartes"])}}
    m = manifeste(attaque=a5.VERSION, mode=mode, entropie_racine=str(entropie),
                  plan={k: v for k, v in plan.items() if k != "devis"}, devis=plan.get("devis") or a5.devis(plan["cartes"], plan["mondes"], plan["fournisseurs"]),
                  preenregistrement=preenregistrement, configuration=conf_info, coeur=a5.description(), numpy=np.__version__,
                  python=platform.python_version(), depot=l2.commit(), code_sha256={r: sha256_fichier(os.path.join(RACINE, r)) for r in FICHIERS_GELES},
                  verite_w2g=verite_w2g,
                  proposeur_a_blanc=((args.proposeur or A_BLANC["proposeur"]) + ("" if not args.sans_echo else ", sans écho")
                                     + (f", pannes {sorted(pannes)}" if pannes else "")) if args.a_blanc else None)
    m["regle_des_graines"] = ("SeedSequence (R9), règle de la v3 : entropie = int(SHA-256 du texte scellé, 16) en mode réel, --graine (< 2^64) "
                              "à blanc ; étiquettes « <monde>|<fournisseur>|<condition>|<juge> » où <juge> est le rôle (« v9 » ou « ancien ») ; "
                              "mondes W2 (graines « monde|W2 », « developpement|W2 ») et W2g (« monde|W2g », « developpement|W2g » : lois "
                              "d'archive et loi neuve N tirées de la graine de la carte) ; le nul effectif de l'ancien juge (v8) est écrit dans "
                              "chaque suite (« nul ») ; la vérité de W2g (N, dose, écart) est au manifeste, jamais dans une consigne")
    for k in ("regle_du_repli", "regle_des_unites_jouees", "regle_de_l_attente", "regle_du_cout_inconnu"):
        m[k] = a3.description()[k]
    ecrire_json_scelle(os.path.join(args.dossier, "manifeste.json"), m)
    compteur = a3.Compteur(plan["plafond_usd"], plan["duree_max_s"], time.time, plan["fournisseurs"], None,
                           relais_perdu_s=plan.get("relais_perdu_s"))
    sortie = os.path.join(args.dossier, SORTIE)
    commun = lambda: {"attaque": a5.VERSION, "mode": mode, "appels": compteur.appels, "reprises": compteur.reprises,  # noqa: E731
                      "depense_usd": round(compteur.usd, 4), "depense_par_fournisseur_usd": compteur.par_fournisseur,
                      "appels_par_fournisseur": compteur.appels_par_fournisseur, "appels_budget_depasse": compteur.budget_depasse,
                      "modeles_servis": compteur.modeles_servis, "par_fournisseur_et_modele_demande": compteur.par_modele,
                      "unites_basculees_sur_repli": compteur.replis, "attentes_relais": compteur.attentes_relais,
                      "attente_relais_s": {f: round(v, 1) for f, v in compteur.attente_relais_s.items()},
                      "appels_cout_inconnu": compteur.cout_inconnu, "cout_inconnu_usd": compteur.cout_inconnu_usd,
                      "relais_perdu_s": plan.get("relais_perdu_s"), "dose_w2g": plan.get("dose_w2g"), "duree_s": round(time.time() - compteur.debut, 1),
                      "fin_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    try:
        suites, rejeux, audits = a5.jouer_tout(proposeurs, entropie, plan, compteur, decisif=not args.a_blanc,
                                               parallele=plan["parallele"], processus=plan["processus"])
    except ag.ArretAttaque as e:
        rapport = dict(commun(), arret=str(e), suites_partielles=e.partiel.get("suites", []),
                       unites_sans_loi=a3.unites_sans_loi(e.partiel.get("suites", [])),
                       issue="non jugeable (arrêt) : aucun taux lu", rejeux_partiels=e.partiel.get("rejeux", []))
        ecrire_json_scelle(sortie, rapport)
        print(json.dumps({k: rapport[k] for k in ("mode", "arret", "appels", "depense_usd", "duree_s")}, ensure_ascii=False), file=sys.stderr)
        return 3
    lecture = a5.lire(suites, rejeux, audits, plan["mondes"], plan["unites_par_case"], entropie, plan["fournisseurs"], plan.get("dose_w2g"))
    rapport = dict(commun(), preenregistrement=preenregistrement, lecture=lecture, unites_sans_loi=a3.unites_sans_loi(suites),
                   suites=suites, rejeux=rejeux, audit_A2=audits, verite_w2g=verite_w2g)
    ecrire_json_scelle(sortie, rapport)
    print(json.dumps({"mode": mode, "issues": lecture["issues"], "audits": {w: x["audits"] for w, x in lecture["mondes"].items()},
                      "appels": compteur.appels, "depense_usd": rapport["depense_usd"], "duree_s": rapport["duree_s"],
                      "violations_de_monotonie": {w: x["violations_de_monotonie"] for w, x in lecture["mondes"].items()},
                      "unites_sans_loi": rapport["unites_sans_loi"]["total_sans_loi"], "attentes_relais": compteur.attentes_relais},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
