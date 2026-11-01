"""Lecture préenregistrée du lot T0.5 à graines neuves (v1) — épreuve neuve lue une seule fois.

Préenregistrement : `prereg/preenregistrement-lecture-t05-graines-neuves-v1.md` (scellé avant toute lecture ; ce script
applique ses lectures telles qu'écrites, rien d'autre). Processeur seul, sans réseau, sans dépense.

Rôle du lot. Calibrage = les 288 épisodes déjà courus (96 tâches × 3), lus dans la banque `banque-e2.json` (empreinte
fixée ci-dessous) : normalisation des traits, coupes des moniteurs, prédicteurs connus, définition des témoins (règle de
L3 : lien de rang ≥ 0,35 en calibrage ; témoins faux : loi sur le trait de bruit). Épreuve = les 288 épisodes à graines
neuves (mêmes 96 tâches, identifiants `<origine>-g2`, lots a à d de la table du kit de production), lus une fois : chaque
`--run` est le `diag/<run>/` d'une branche de résultats (`episodes.json`, notations décisives exigées — e0 passes 0 et 1, e1
passe 0 —, notations descriptives — e2 passe 0 — lues si présentes) ; passe retenue : `passe-0`.

Juge : `pole/juge_plan_plein_v1.py` — bras « plein » (le plan prend tout le réservoir de chaque fiche) et bras « gelé »
(plan de 120, juge de la courbe de puissance), nul v8, génération unique, archive vide. Deux familles (règle e-BH de
production, m fixé avant toute issue = fiches non « vraies » de la famille) :
- famille T (décisive), monde **informé** (membre « connu » ajusté sur le calibrage) : témoins réels (faux : bruit ; vrais :
  règle de L3) et témoins plantés (lois si/sinon de `construire_banque_t05_v3.planter`, forces 0,3, 0,5, 0,8, sur les
  traits réels des épisodes de calibrage et d'épreuve ; faux « bruit » et « même forme permutée ») ;
- famille R (lois réelles, préenregistrée, non décisive pour le juge), monde **aveugle** : la loi « connue » de chaque
  moniteur réel (ajustée sur le calibrage) comme fiche, plus les témoins réels.

Liste d'arrêt (exception `Arret`, codes A1 à A8 ; aucun message ne contient une note ni une issue) : fichier manquant
(A1 ; dont notations décisives d'une course, lot de la table sans course), empreinte discordante (A2 ; dont table des
identifiants et bloc d'empreintes du code au préenregistrement), notation, épisode, tâche ou lot en double (A3), moniteur
à moins de K = 60 instances jugées dans l'épreuve (A4), tâche ou épisode partagé entre calibrage et épreuve, tâche sans
le suffixe « -g2 » à l'épreuve, tâche « -g2 » au calibrage (A5), format non conforme (A6), calibrage qui ne redonne pas la
table de rangs du préenregistrement (A7), incohérence interne du juge (A8). Un arrêt écrit `arret.json` dans le dossier de
sortie et rien d'autre. L'absence des notations descriptives n'est pas un arrêt (échéance de 15 000 s prévue).

Graines (R9) : `numpy.random.SeedSequence(int(empreinte du préenregistrement, 16))`, quatre fils dans l'ordre : bruit de
l'épreuve, plantation, permutation, rééchantillonnage ; graine du juge 20261027 (constante du juge). Voir le
préenregistrement, section « Graines ».

Usage :
  python3 -I -B demonstrations/lecture_t05_graines_neuves_v1.py --preenregistrement PREREG.md \
      [--empreinte-preenregistrement HEX] --calibrage banque-e2.json --table-identifiants TABLE.json \
      --run DIAG_a --run DIAG_b --run DIAG_c --run DIAG_d [--notations-sup DOSSIER ...] \
      --sortie DOSSIER_NEUF_HORS_DU_DEPOT_PUBLIC [--reechantillonnages 1000] [--processus 1]
Sorties : DOSSIER/lecture-t05-graines-neuves-v1.json et .md (aucun compagnon .sha256 : le scellement est fait à part).
Toute autre empreinte de calibrage que celle du préenregistrement fait une **course à blanc** (non opposable, marquée
comme telle) : c'est le chemin des essais sur données synthétiques.
"""

import os

for _variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):  # un fil numpy par processus
    os.environ.setdefault(_variable, "1")

import argparse  # noqa: E402
import collections  # noqa: E402
import concurrent.futures  # noqa: E402
import copy  # noqa: E402
import dataclasses  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(ICI)
EXEMPLES = os.path.join(RACINE, "exemples")
sys.path.insert(0, RACINE)
sys.path.insert(0, EXEMPLES)

import construire_banque_t05_v3 as b3  # noqa: E402
import proposeur_scripte_banque_v1 as ps  # noqa: E402
from pole import juge_plan_plein_v1 as jpp  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole.cycle import appliquer_multiplicite, preparer_engagement  # noqa: E402
from pole.fiche import Fiche  # noqa: E402
from pole.monde_banque import MondeBanque  # noqa: E402
from pole.outils import empreinte_objet, graine_derivee, sha256_fichier  # noqa: E402

NOM = "lecture-t05-graines-neuves-v1"
# Calibrage : banque des 288 épisodes déjà courus (lecture exploratoire v2 de la couche 1 bis), empreinte vérifiée.
EMPREINTE_CALIBRAGE = "f59018fb047af289ba1f466430fa9c577d6a0b6d4843a51831b19bd3c197b22e"
# Table de rangs du calibrage (règle de L3, `proposeur_scripte_banque_v1.proposer`), écrite au préenregistrement :
CALIBRAGE_ATTENDU = {"temoins_vrais": 0, "temoins_faux": 13, "moniteurs": 13, "rang_max_abs": 0.248,
                     "couple_max": "3B:BALANCE|jetons_par_action_ecart_type"}
JUGES = ("8B", "3B")
VARIANTE_GRILLE = "b0"  # grille H.4, invite b0 (pilote et notations du 17 octobre)
PASSE = "passe-0"
K_MIN = 60  # instances d'épreuve jugées par moniteur réel, au moins (liste d'arrêt A4)
FORCES_PLANTEES = (0.3, 0.5, 0.8)
ALPHA = jpp.ALPHA
SEUIL_TEMOIN_VRAI = ps.SEUIL_TEMOIN_VRAI  # 0,35
FICHIERS_DECISIFS = {j: f"notations-{j}-decisives.json" for j in JUGES}  # e0 passes 0 et 1, e1 passe 0
FICHIERS_DESCRIPTIFS = {j: f"notations-{j}-descriptives.json" for j in JUGES}  # e2 passe 0 (absents si échéance)
SUFFIXE_EPREUVE = "-g2"  # identifiant d'épreuve = identifiant d'origine + « -g2 » (kit de production)
EMPREINTE_TABLE = "76375391f4860f71271ae9239dbc1afa6cdba06eb830dda035762705cc0a772f"  # table des identifiants du kit
LOTS_ATTENDUS = {"a": 30, "b": 30, "c": 30, "d": 6}
CIBLE_PUISSANCE = 0.9

# Courbe de puissance publiée (`resultats/puissance-juge-banque-v1-2026-11-01/puissance-juge-banque-v1.json`, sha256
# 060216fe…), lecture principale e-BH m = 17 : taux de promotion des témoins vrais plantés. Plan = N (variante) pour
# N ≥ 144 ; pour N ≤ 120 le plan gelé et la variante coïncident. Extraits du JSON par programme, non recopiés à la main.
COURBE_SOURCE = {"fichier": "resultats/puissance-juge-banque-v1-2026-11-01/puissance-juge-banque-v1.json",
                 "sha256": "060216fef755b77ecc488195b6eba56d52ecdd3c530855c18cc8610cd17b4c55",
                 "force_en_clair": "resultats/puissance-juge-banque-v1-2026-11-01/force-en-clair-v1.txt",
                 "force_en_clair_sha256": "7419358857c824e0f67c76fb8a130faef1cf0071ce27b5d4bd0bbd900106a1a6"}
COURBE_N = (60, 120, 144, 180, 288, 600)
COURBE_PLAN_N = {0.1: (0.0, 0.0, 0.0, 0.0, 0.0, 0.008), 0.2: (0.0, 0.002, 0.014, 0.03, 0.116, 0.552),
                 0.3: (0.0, 0.11, 0.158, 0.31, 0.612, 0.938), 0.5: (0.164, 0.646, 0.73, 0.838, 0.964, 1.0),
                 0.8: (0.692, 0.948, 0.972, 0.988, 0.996, 1.0)}
COURBE_GELE = {0.1: (0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 0.2: (0.0, 0.002, 0.012, 0.016, 0.054, 0.186),
               0.3: (0.0, 0.11, 0.148, 0.242, 0.386, 0.544), 0.5: (0.164, 0.646, 0.706, 0.73, 0.734, 0.694),
               0.8: (0.692, 0.948, 0.948, 0.954, 0.866, 0.81)}
# Information moyenne par épisode (nat) de la loi plantée, moyenne sur les 6 paires de traits (force-en-clair-v1.txt).
INFO_PAR_FORCE = ((0.1, 0.0028), (0.2, 0.0110), (0.3, 0.0239), (0.5, 0.0602), (0.8, 0.1281))
# Puissance par paire (i : trait de la softmax, j : trait du seuil ; indices de `traits`) et par force, (plein, gelé), sur
# les traits réels du calibrage pris comme substitut de l'épreuve, juge de cette lecture, m = 19, 40 répétitions par
# cellule : `demonstrations/annexes_lecture_t05_v1/puissance_par_paire_v1.py` (sha256 f8b73c12…) ; N = 192 (vecteurs
# des e0 et e1, sortie sha256 22d12017…) et N = 288 (e0 à e2, sortie sha256 30de2400…). Tables recopiées des sorties
# par programme. Servent aux prédictions conditionnelles aux paires tirées (préenregistrement, section 7), lues.
PUISSANCE_PAR_PAIRE_192 = {
    (0, 1, 0.3): (0.375, 0.35), (0, 1, 0.5): (0.975, 0.975), (0, 1, 0.8): (1.0, 1.0), (0, 2, 0.3): (0.025, 0.0),
    (0, 2, 0.5): (0.625, 0.35), (0, 2, 0.8): (0.95, 0.85), (1, 0, 0.3): (0.5, 0.4), (1, 0, 0.5): (0.9, 0.875),
    (1, 0, 0.8): (1.0, 1.0), (1, 2, 0.3): (0.45, 0.4), (1, 2, 0.5): (0.925, 0.925), (1, 2, 0.8): (1.0, 1.0),
    (2, 0, 0.3): (0.175, 0.05), (2, 0, 0.5): (0.85, 0.7), (2, 0, 0.8): (1.0, 0.95), (2, 1, 0.3): (0.375, 0.275),
    (2, 1, 0.5): (1.0, 0.975), (2, 1, 0.8): (1.0, 0.975)}
PUISSANCE_PAR_PAIRE_288 = {
    (0, 1, 0.3): (0.85, 0.725), (0, 1, 0.5): (1.0, 0.975), (0, 1, 0.8): (1.0, 1.0), (0, 2, 0.3): (0.475, 0.075),
    (0, 2, 0.5): (0.95, 0.575), (0, 2, 0.8): (1.0, 0.95), (1, 0, 0.3): (0.675, 0.3), (1, 0, 0.5): (1.0, 0.95),
    (1, 0, 0.8): (1.0, 1.0), (1, 2, 0.3): (0.725, 0.525), (1, 2, 0.5): (1.0, 0.95), (1, 2, 0.8): (1.0, 1.0),
    (2, 0, 0.3): (0.3, 0.1), (2, 0, 0.5): (0.975, 0.55), (2, 0, 0.8): (1.0, 0.975), (2, 1, 0.3): (0.8, 0.625),
    (2, 1, 0.5): (0.975, 0.975), (2, 1, 0.8): (1.0, 1.0)}


def conditionnel_aux_paires(plantes, n):
    """Prédictions conditionnelles aux paires tirées par la graine de plantation : taux par paire et par force interpolés
    linéairement en N entre les tables à 192 et à 288 (bornés à ces valeurs) ; lues, non décisives."""
    poids = min(1.0, max(0.0, (float(n) - 192.0) / 96.0))
    par, p_plein = {}, []
    for numero, p in enumerate(plantes, 1):
        cle = (int(p["i"]), int(p["j"]), float(p["force"]))
        if cle not in PUISSANCE_PAR_PAIRE_192 or cle not in PUISSANCE_PAR_PAIRE_288:
            par[f"TVP{numero:02d}"] = {"i": cle[0], "j": cle[1], "force": cle[2], "plein": None, "gele": None}
            p_plein.append(None)
            continue
        a, b = PUISSANCE_PAR_PAIRE_192[cle], PUISSANCE_PAR_PAIRE_288[cle]
        pl, ge = (round(x + (y - x) * poids, 4) for x, y in zip(a, b))
        par[f"TVP{numero:02d}"] = {"i": cle[0], "j": cle[1], "force": cle[2], "plein": pl, "gele": ge}
        p_plein.append(pl)
    if any(x is None for x in p_plein):
        return {"par_temoin": par, "applicable": False, "n": n}
    import itertools
    au_moins_deux_tiers = sum(math.prod(x if o else 1 - x for x, o in zip(p_plein, issue))
                              for issue in itertools.product((0, 1), repeat=len(p_plein))
                              if sum(issue) >= 2 * len(p_plein) / 3 - 1e-9)
    i4 = math.prod(1 - par[t]["plein"] for t in par if par[t]["force"] in (0.5, 0.8))
    return {"par_temoin": par, "applicable": True, "n": n, "attendu_plein": round(sum(p_plein), 3),
            "attendu_gele": round(sum(par[t]["gele"] for t in par), 3),
            "proba_fraction_au_moins_deux_tiers": round(au_moins_deux_tiers, 3), "proba_I4": round(i4, 4)}


class Arret(Exception):
    """Arrêt de la liste du préenregistrement ; `code` A1 à A8 ; le message ne porte jamais de note ni d'issue."""

    def __init__(self, code, message):
        super().__init__(f"{code} : {message}")
        self.code, self.message = code, message


# --- courbe : interpolations écrites d'avance -----------------------------------------------------------------------
def _interp(x, xs, ys):
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    raise ValueError(x)


def puissance_courbe(force, n, plan="plein"):
    """Taux de promotion d'un témoin vrai planté de force `force` (grille 0,1 à 0,8) à N instances jugées, interpolé
    linéairement en N sur la grille de la courbe ; plan « plein » (variante plan = N) ou « gele » (plan de 120)."""
    table = COURBE_PLAN_N if plan == "plein" else COURBE_GELE
    return _interp(n, COURBE_N, table[force])


def force_detectable(n, cible=CIBLE_PUISSANCE):
    """Plus petite force (interpolée linéairement entre forces de la grille) dont la puissance, plan plein, atteint
    `cible` à N instances ; None si la force 0,8 ne l'atteint pas."""
    forces = sorted(COURBE_PLAN_N)
    p = [puissance_courbe(f, n, "plein") for f in forces]
    if p[0] >= cible:
        return forces[0]
    for (f0, p0), (f1, p1) in zip(zip(forces, p), zip(forces[1:], p[1:])):
        if p0 < cible <= p1:
            return f0 + (f1 - f0) * (cible - p0) / (p1 - p0)
    return None


def information_de_force(force):
    return _interp(force, [f for f, _ in INFO_PAR_FORCE], [i for _, i in INFO_PAR_FORCE])


def borne_information(n):
    """I*(N) : information par épisode (nat) à partir de laquelle une loi de la forme plantée est promue avec une
    probabilité ≥ 0,9 sous le plan plein, à N instances jugées (lu sur la courbe) ; None hors de la grille."""
    f = force_detectable(n)
    return None if f is None else {"force": round(f, 3), "information_nat": round(information_de_force(f), 4)}


# --- fichiers et empreintes ------------------------------------------------------------------------------------------
def empreinte_compagnon(chemin):
    """A1 si le fichier ou son compagnon `.sha256` manque ; A2 si l'empreinte du fichier n'est pas celle du compagnon."""
    if not os.path.isfile(chemin):
        raise Arret("A1", f"fichier manquant : {chemin}")
    if not os.path.isfile(chemin + ".sha256"):
        raise Arret("A1", f"compagnon .sha256 manquant : {chemin}.sha256")
    with open(chemin + ".sha256", encoding="utf-8") as f:
        morceaux = f.read().split()
    if not morceaux or len(morceaux[0]) != 64:
        raise Arret("A2", f"compagnon illisible : {chemin}.sha256")
    reelle = sha256_fichier(chemin)
    if reelle != morceaux[0].lower():
        raise Arret("A2", f"empreinte discordante : {chemin} (lu {reelle[:12]}…, compagnon {morceaux[0][:12]}…)")
    return reelle


FICHIERS_DE_CODE_EXIGES = ("demonstrations/lecture_t05_graines_neuves_v1.py", "pole/juge_plan_plein_v1.py")


def verifier_code(chemin_prereg, a_blanc):
    """A2 : chaque ligne « empreinte␣␣chemin » du préenregistrement (bloc de la section « Commande exacte », chemins relatifs
    à la racine du code) doit redonner l'empreinte du fichier ; le bloc doit couvrir ce script et le juge. En course à
    blanc, un préenregistrement sans bloc est accepté (consigné)."""
    import re
    with open(chemin_prereg, encoding="utf-8") as f:
        lignes = re.findall(r"^([0-9a-f]{64})  ([A-Za-z0-9_./-]+)$", f.read(), flags=re.MULTILINE)
    if not lignes:
        if a_blanc:
            return {"applique": False, "motif": "course à blanc : préenregistrement sans bloc d'empreintes"}
        raise Arret("A2", "bloc d'empreintes du code absent du préenregistrement")
    table = dict((chemin, h) for h, chemin in lignes)
    absents = [c for c in FICHIERS_DE_CODE_EXIGES if c not in table]
    if absents:
        raise Arret("A2", f"bloc d'empreintes du code incomplet : {absents}")
    ecarts = []
    for chemin, attendue in sorted(table.items()):
        complet = os.path.join(RACINE, chemin)
        if not os.path.isfile(complet):
            raise Arret("A1", f"fichier de code manquant : {chemin}")
        if sha256_fichier(complet) != attendue:
            ecarts.append(chemin)
    if ecarts:
        raise Arret("A2", f"code différent du préenregistrement : {ecarts}")
    return {"applique": True, "fichiers": table}


def _charger_json(chemin):
    try:
        with open(chemin, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise Arret("A6", f"JSON illisible : {chemin} ({type(e).__name__})") from None


# --- calibrage -------------------------------------------------------------------------------------------------------
def lire_calibrage(chemin, empreinte_attendue):
    """Banque de calibrage : moniteurs réels (juges 8B et 3B, rubriques de la v3), toutes les instances en calibrage."""
    if not os.path.isfile(chemin):
        raise Arret("A1", f"banque de calibrage manquante : {chemin}")
    reelle = sha256_fichier(chemin)
    if reelle != empreinte_attendue:
        raise Arret("A2", f"banque de calibrage : empreinte {reelle[:12]}…, attendue {empreinte_attendue[:12]}…")
    b = _charger_json(chemin)
    if list(b.get("traits", [])) != list(b3.TRAITS):
        raise Arret("A6", f"traits du calibrage {b.get('traits')} ≠ {list(b3.TRAITS)}")
    norm = b.get("normalisation") or {}
    if len(norm.get("moyennes", [])) != len(b3.TRAITS) or len(norm.get("ecarts_types", [])) != len(b3.TRAITS):
        raise Arret("A6", "normalisation du calibrage absente ou incomplète")
    moniteurs = {n: dict(m) for n, m in b["moniteurs"].items() if m.get("juge") in JUGES and m.get("rubrique") in b3.RUBRIQUES}
    if not moniteurs:
        raise Arret("A6", "aucun moniteur réel dans le calibrage")
    for n, m in moniteurs.items():
        if n != f"{m['juge']}:{m['rubrique']}" or not isinstance(m.get("coupes"), list) or m["nombre_issues"] != len(m["coupes"]) + 1:
            raise Arret("A6", f"moniteur de calibrage mal formé : {n}")
    instances, vus = [], set()
    for l in b["instances"]:
        ident, tache = l.get("identifiant"), l.get("tache")
        if not isinstance(ident, str) or not isinstance(tache, str) or not ident.startswith(tache + "/e"):
            raise Arret("A6", f"instance de calibrage mal formée : {ident!r}")
        if ident in vus:
            raise Arret("A3", f"instance de calibrage en double : {ident}")
        vus.add(ident)
        instances.append({"identifiant": ident, "tache": tache, "g": int(l["g"]), "z": [float(x) for x in l["z"]],
                          "issues": {k: int(v) for k, v in l["issues"].items() if k in moniteurs}, "partie": "calibrage"})
    return {"nom": b.get("nom", "calibrage"), "empreinte": reelle, "traits": list(b["traits"]),
            "sous_populations": max(int(b.get("sous_populations", 2)), 1 + max(l["g"] for l in instances)),
            "normalisation": {"moyennes": list(norm["moyennes"]), "ecarts_types": list(norm["ecarts_types"])},
            "moniteurs": moniteurs, "instances": instances}


def temoins_de_calibrage(banque_cal):
    """Témoins réels par la règle de L3 (`proposeur_scripte_banque_v1.proposer`, inchangé) sur le seul calibrage."""
    _, temoins, rangs = ps.proposer({"traits": banque_cal["traits"], "moniteurs": banque_cal["moniteurs"],
                                     "instances": banque_cal["instances"]})
    fiches = []
    for t in temoins:
        t = copy.deepcopy(t)
        t["espace_instances"].update(sous_populations=banque_cal["sous_populations"], banque=NOM + ":calibrage")
        t["source"] = f"{NOM} : règle de L3 sur le calibrage ({t['temoin']})"
        fiches.append(Fiche.depuis_dict(t).valider())
    couples = [(abs(r), f"{m}|{tr}") for m, d in rangs.items() for tr, r in d.items()]
    haut = max(couples) if couples else (0.0, None)
    resume = {"temoins_vrais": sum(f.temoin == "vraie" for f in fiches), "temoins_faux": sum(f.temoin == "fausse" for f in fiches),
              "moniteurs": len(rangs), "rang_max_abs": round(haut[0], 3), "couple_max": haut[1]}
    return fiches, rangs, resume


def verifier_table_de_rangs(resume, a_blanc):
    """A7 : sur le calibrage du préenregistrement, la règle doit redonner la table écrite (aucun témoin vrai réel)."""
    if a_blanc:
        return {"applique": False, "motif": "course à blanc (autre calibrage)"}
    ecarts = {k: (resume.get(k), v) for k, v in CALIBRAGE_ATTENDU.items()
              if (abs(resume.get(k) - v) > 5e-4 if isinstance(v, float) else resume.get(k) != v)}
    if ecarts:
        raise Arret("A7", f"table de rangs du calibrage différente du préenregistrement : {ecarts}")
    return {"applique": True, "conforme": True}


# --- lot neuf : lecture et contrôles (aucune valeur de note dans les messages) ---------------------------------------
def lire_table(chemin, empreinte_attendue):
    """Table des identifiants du kit de production (tâche d'origine → identifiant « -g2 » → lot)."""
    if not chemin or not os.path.isfile(chemin):
        raise Arret("A1", f"table des identifiants manquante : {chemin}")
    reelle = sha256_fichier(chemin)
    if reelle != empreinte_attendue:
        raise Arret("A2", f"table des identifiants : empreinte {reelle[:12]}…, attendue {empreinte_attendue[:12]}…")
    t = _charger_json(chemin)
    lignes = t.get("table") if isinstance(t, dict) else None
    if not isinstance(lignes, list) or not lignes:
        raise Arret("A6", "table des identifiants sans champ « table »")
    par_identifiant = {}
    for x in lignes:
        ident, origine, lot = (x.get(k) if isinstance(x, dict) else None for k in ("identifiant", "tache_origine", "lot"))
        if not all(isinstance(v, str) for v in (ident, origine, lot)) or ident != origine + SUFFIXE_EPREUVE \
                or lot not in LOTS_ATTENDUS or ident in par_identifiant:
            raise Arret("A6", f"ligne de table mal formée ou en double : {ident!r}")
        par_identifiant[ident] = {"origine": origine, "lot": lot}
    comptes = collections.Counter(v["lot"] for v in par_identifiant.values())
    if dict(comptes) != LOTS_ATTENDUS:
        raise Arret("A6", f"table des identifiants : lots {dict(comptes)} ≠ {LOTS_ATTENDUS}")
    return {"empreinte": reelle, "par_identifiant": par_identifiant}


def _lire_notations(chemin, juge, episodes, taches_cal, ids_cal, cles, notes):
    d = _charger_json(chemin)
    liste = (d.get("resultat") or {}).get("notations")
    if not isinstance(liste, list):
        raise Arret("A6", f"{chemin} : resultat.notations absent")
    for n in liste:
        cle = n.get("cle") if isinstance(n, dict) else None
        parties = cle.split("/") if isinstance(cle, str) else []
        if len(parties) != 4 or parties[0] != f"juge-{juge}" or not parties[2].startswith("e") \
                or not parties[3].startswith("passe-"):
            raise Arret("A6", f"{chemin} : clé de notation mal formée : {cle!r}")
        if n.get("variante") != VARIANTE_GRILLE:
            raise Arret("A6", f"{chemin} : notation {cle} hors de la grille attendue (variante ≠ {VARIANTE_GRILLE})")
        if not isinstance(n.get("notes"), dict):
            raise Arret("A6", f"{chemin} : notation {cle} sans champ notes")
        _, tache, ep, passe = parties
        ident = f"{tache}/{ep}"
        if (juge, ident, passe) in cles:
            raise Arret("A3", f"notation en double : {cle}")
        cles.add((juge, ident, passe))
        if tache in taches_cal or ident in ids_cal:
            raise Arret("A5", f"notation d'une tâche du calibrage : {tache}")
        if not tache.endswith(SUFFIXE_EPREUVE):
            raise Arret("A5", f"notation d'une tâche sans le suffixe {SUFFIXE_EPREUVE} : {tache}")
        if ident not in episodes:
            raise Arret("A6", f"{chemin} : notation {cle} sans épisode dans les courses")
        if passe == PASSE:
            notes[(juge, ident)] = dict(n["notes"])
    return len(liste)


def lire_lot(runs, notations_sup, banque_cal, table=None):
    """Courses du lot : dans chaque dossier `--run` (le `diag/<run>/` d'une branche de résultats), `episodes.json` et les
    notations **décisives** des deux juges (e0 passes 0 et 1, e1 passe 0) sont exigés ; les notations **descriptives**
    (e2 passe 0) sont lues si présentes (elles manquent si l'échéance de 15 000 s frappe avant). Dans un dossier
    `--notations-sup`, les deux sortes sont facultatives."""
    if not runs:
        raise Arret("A1", "aucun dossier de course (--run)")
    taches_cal = {l["tache"] for l in banque_cal["instances"]}
    ids_cal = {l["identifiant"] for l in banque_cal["instances"]}
    suffixees = sorted(t for t in taches_cal if t.endswith(SUFFIXE_EPREUVE))
    if suffixees:
        raise Arret("A5", f"tâche « {SUFFIXE_EPREUVE} » au calibrage : {suffixees[:3]}")
    sources, episodes, tache_de_course = {}, {}, {}
    for run in runs:
        chemin = os.path.join(run, "episodes.json")
        sources[chemin] = empreinte_compagnon(chemin)
        d = _charger_json(chemin)
        fiches = (d.get("resultat") or {}).get("fiches")
        if not isinstance(fiches, list) or not fiches:
            raise Arret("A6", f"{chemin} : resultat.fiches absent ou vide")
        for e in fiches:
            ident, tache = e.get("episode"), e.get("tache")
            if not isinstance(ident, str) or not isinstance(tache, str) or "/" in tache or not ident.startswith(tache + "/e") \
                    or not ident.rsplit("/e", 1)[1].isdigit():
                raise Arret("A6", f"{chemin} : identifiant d'épisode mal formé : {ident!r}")
            jetons, bilan = e.get("jetons_par_action"), e.get("bilan")
            if not isinstance(jetons, list) or not isinstance(bilan, dict) or not isinstance(bilan.get("actions_valides"), (int, float)):
                raise Arret("A6", f"{chemin} : épisode {ident} sans jetons_par_action ni bilan.actions_valides")
            if tache in taches_cal or ident in ids_cal:
                raise Arret("A5", f"tâche ou épisode présent au calibrage et à l'épreuve : {tache}")
            if not tache.endswith(SUFFIXE_EPREUVE):
                raise Arret("A5", f"tâche de l'épreuve sans le suffixe {SUFFIXE_EPREUVE} : {tache}")
            if ident in episodes:
                raise Arret("A3", f"épisode en double : {ident}")
            if tache in tache_de_course and tache_de_course[tache] != run:
                raise Arret("A3", f"tâche présente dans deux courses : {tache}")
            tache_de_course[tache] = run
            episodes[ident] = {"episode": ident, "tache": tache, "jetons_par_action": list(jetons),
                               "actions_valides": float(bilan["actions_valides"])}
    lots_des_courses = {}
    if table is not None:
        for tache in tache_de_course:
            ligne = table["par_identifiant"].get(tache)
            if ligne is None:
                raise Arret("A6", f"tâche absente de la table des identifiants : {tache}")
            if ligne["origine"] not in taches_cal:
                raise Arret("A6", f"tâche d'origine absente du calibrage : {ligne['origine']}")
        for run in runs:
            lots = {table["par_identifiant"][t]["lot"] for t, r in tache_de_course.items() if r == run}
            if len(lots) != 1:
                raise Arret("A6", f"course {run} : tâches de plusieurs lots {sorted(lots)}")
            lot = lots.pop()
            if lot in lots_des_courses.values():
                raise Arret("A3", f"lot {lot} présent dans deux courses")
            lots_des_courses[run] = lot
            attendues = {t for t, v in table["par_identifiant"].items() if v["lot"] == lot}
            manquantes = attendues - {t for t, r in tache_de_course.items() if r == run}
            if manquantes:
                raise Arret("A1", f"lot {lot} : {len(manquantes)} tâche(s) de la table absente(s) des épisodes")
        absents = sorted(set(LOTS_ATTENDUS) - set(lots_des_courses.values()))
        if absents:
            raise Arret("A1", f"lot(s) manquant(s) : {absents}")
    notes, cles, fichiers = {}, set(), {}
    for dossier, exige in [(r, True) for r in runs] + [(n, False) for n in notations_sup]:
        for juge in JUGES:
            for sorte, gabarit in (("decisives", FICHIERS_DECISIFS), ("descriptives", FICHIERS_DESCRIPTIFS)):
                chemin = os.path.join(dossier, gabarit[juge])
                if not os.path.exists(chemin):
                    if exige and sorte == "decisives":
                        raise Arret("A1", f"notations décisives manquantes : {chemin}")
                    fichiers[f"{dossier}|{juge}|{sorte}"] = "absent"
                    continue
                sources[chemin] = empreinte_compagnon(chemin)
                fichiers[f"{dossier}|{juge}|{sorte}"] = _lire_notations(chemin, juge, episodes, taches_cal, ids_cal, cles, notes)
    # Rapporté, jamais un arrêt : appariement des tâches neuves aux tâches du calibrage par le suffixe.
    appariement = collections.Counter(
        "une" if t[:-len(SUFFIXE_EPREUVE)] in taches_cal else "aucune" for t in tache_de_course)
    return {"episodes": episodes, "notes": notes, "sources": sources,
            "comptes": {"courses": len(runs), "dossiers_notations_sup": len(notations_sup),
                        "episodes": len(episodes), "taches": len(tache_de_course),
                        "notations_lues": len(cles), "notations_passe_0": len(notes),
                        "fichiers_de_notations": fichiers, "lots_des_courses": lots_des_courses,
                        "table_des_identifiants": None if table is None else table["empreinte"],
                        "taches_appariees_au_calibrage_par_suffixe": dict(appariement)}}


def construire_epreuve(lot, banque_cal, graine_bruit):
    """Instances d'épreuve : mêmes traits que la v3, normalisés par le calibrage ; trait de bruit tiré N(0, 1) par la
    graine « bruit » dans l'ordre des identifiants ; issues = coupes du calibrage sur la note de première passe."""
    moy, ect = banque_cal["normalisation"]["moyennes"], banque_cal["normalisation"]["ecarts_types"]
    notes = lot["notes"]
    retenus, sans_jetons, sans_notation = [], 0, 0
    for ident in sorted(lot["episodes"]):
        e = lot["episodes"][ident]
        if not e["jetons_par_action"]:
            sans_jetons += 1
            continue
        if any(not isinstance(x, (int, float)) or isinstance(x, bool) or x < 0 for x in e["jetons_par_action"]) \
                or sum(e["jetons_par_action"]) <= 0:
            raise Arret("A6", f"épisode {ident} : jetons_par_action non numériques, négatifs ou de somme nulle")
        if not any((j, ident) in notes for j in JUGES):
            sans_notation += 1
            continue
        retenus.append(e)
    rng = np.random.default_rng(graine_bruit)
    instances = []
    for e in retenus:
        j = e["jetons_par_action"]
        bruts = [math.log(sum(j)), e["actions_valides"], statistics.pstdev(j)]
        z = [round((x - m) / s, 6) for x, m, s in zip(bruts, moy, ect)] + [round(float(rng.standard_normal()), 6)]
        issues = {}
        for nom, m in banque_cal["moniteurs"].items():
            v = (notes.get((m["juge"], e["episode"])) or {}).get(m["rubrique"])
            if isinstance(v, int) and not isinstance(v, bool):
                issues[nom] = b3.classe(v, m["coupes"])
        instances.append({"identifiant": e["episode"], "tache": e["tache"], "g": int(e["episode"].rsplit("/e", 1)[1]),
                          "z": z, "issues": issues, "partie": "epreuve"})
    comptes = {"episodes_retenus": len(instances), "exclus_sans_jetons": sans_jetons, "exclus_sans_notation": sans_notation,
               "taches_retenues": len({l["tache"] for l in instances})}
    return instances, comptes


def verifier_moniteurs(instances, moniteurs, k_min=K_MIN):
    comptes = {n: sum(1 for l in instances if n in l["issues"]) for n in sorted(moniteurs)}
    pauvres = {n: c for n, c in comptes.items() if c < k_min}
    if pauvres:
        raise Arret("A4", f"moniteur(s) à moins de {k_min} instances jugées dans l'épreuve : {sorted(pauvres)} "
                          f"(comptes {pauvres})")
    return comptes


# --- graines ---------------------------------------------------------------------------------------------------------
def graines_de(empreinte_hex):
    ss = np.random.SeedSequence(int(empreinte_hex, 16))
    fils = ss.spawn(4)
    return {"entropie_hex": empreinte_hex, "bruit": fils[0],
            "plantation": int(fils[1].generate_state(1, dtype=np.uint64)[0]),
            "permutation": fils[2], "reechantillonnage": fils[3]}


# --- banque complète, témoins plantés, lois connues -----------------------------------------------------------------
def banque_complete(banque_cal, instances_epreuve, graines):
    instances = copy.deepcopy(banque_cal["instances"]) + copy.deepcopy(instances_epreuve)
    banque = {"nom": NOM, "traits": list(banque_cal["traits"]),
              "sous_populations": max(banque_cal["sous_populations"], 1 + max(l["g"] for l in instances)),
              "moniteurs": copy.deepcopy(banque_cal["moniteurs"]), "instances": instances}
    plantes = b3.planter(banque, len(FORCES_PLANTEES), graines["plantation"], FORCES_PLANTEES)
    rng_perm = np.random.default_rng(graines["permutation"])
    for p in plantes:  # témoin faux « même forme » : issues plantées permutées entre toutes les instances
        nul = "nul:" + p["moniteur"].split(":", 1)[1]
        valeurs = [l["issues"][p["moniteur"]] for l in instances]
        for l, i in zip(instances, rng_perm.permutation(len(valeurs))):
            l["issues"][nul] = int(valeurs[int(i)])
        banque["moniteurs"][nul] = {"juge": "nul", "rubrique": "permutation", "coupes": None, "nombre_issues": 3,
                                    "instances": len(instances)}
    return banque, plantes


def temoins_plantes(banque, plantes):
    d = len(banque["traits"])
    k_de = {n: m["nombre_issues"] for n, m in banque["moniteurs"].items()}
    sortie = []
    for numero, p in enumerate(plantes, 1):  # comme `puissance_juge_banque_v1.banque_de_repetition`
        nul = "nul:" + p["moniteur"].split(":", 1)[1]
        tv = b3._fiche(f"TVP{numero:02d}", {"moniteur": p["moniteur"], "loi_predictive": p["loi_vraie"],
                                            "etiquette": f"vrai planté : force {p['force']}"}, "vraie", d, k_de, banque,
                       f"L'issue du moniteur {p['moniteur']} suit une loi à seuil sur deux traits réels (n° {numero})")
        tfb = b3._fiche(f"TFP{numero:02d}", {"moniteur": p["moniteur"], "loi_predictive": p["loi_fausse"],
                                             "etiquette": "faux planté : même forme sur le trait de bruit"}, "fausse", d,
                        k_de, banque, f"L'issue du moniteur {p['moniteur']} suit une loi à seuil sur le trait de bruit (n° {numero})")
        tff = b3._fiche(f"TFN{numero:02d}", {"moniteur": nul, "loi_predictive": p["loi_vraie"],
                                             "etiquette": "faux : loi vraie, issues permutées"}, "fausse", d, k_de, banque,
                        f"L'issue du moniteur {nul} suit une loi à seuil sur deux traits réels (n° {numero})")
        for x in (tv, tfb, tff):
            sortie.append(Fiche.depuis_dict(x).valider())
    return sortie


def _ecrire_banque(banque, dossier, nom="banque.json"):
    chemin = os.path.join(dossier, nom)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(banque, f)
    return chemin


def lois_connues(banque_cal, dossier):
    """Loi « connue » de chaque moniteur réel : le membre informé du juge, ajusté sur le calibrage seul (avant l'épreuve)."""
    monde = MondeBanque(_ecrire_banque({"nom": NOM + ":calibrage", "traits": banque_cal["traits"],
                                        "sous_populations": banque_cal["sous_populations"],
                                        "moniteurs": banque_cal["moniteurs"], "instances": banque_cal["instances"]},
                                       dossier, "calibrage.json"), jpp.GRAINE_DU_JUGE, nul_informe=True)
    d = len(banque_cal["traits"])
    sortie = {}
    for nom, m in sorted(banque_cal["moniteurs"].items()):
        factice = type("F", (), {"espace_instances": {"moniteur": nom, "nombre_issues": m["nombre_issues"], "dimension": d}})()
        sortie[nom] = monde.membres_informes(factice)[0]["loi"]
    return sortie


def fiches_lois_reelles(lois, banque_cal):
    d = len(banque_cal["traits"])
    sortie = []
    for nom, loi in sorted(lois.items()):
        m = banque_cal["moniteurs"][nom]
        sortie.append(Fiche.depuis_dict({
            "identifiant": f"LR-{m['juge']}-{m['rubrique']}",
            "enonce": f"La note {m['rubrique']} du juge {m['juge']} suit la loi connue ajustée sur les 288 épisodes déjà courus",
            "prediction": {"signe": "+", "valeur": 0.1, "texte": "la loi connue bat la bibliothèque aveugle sur l'épreuve"},
            "metrique": "richesse W contre la bibliothèque aveugle", "nul": "bibliothèque aveugle du juge v1 (sans urne)",
            "seuil": 20.0, "severite_attendue": ALPHA, "cout_borne": 1.0,
            "protocole": "pari sur toutes les instances d'épreuve du moniteur", "domaines": [f"juge {m['juge']}"],
            "operateurs": ["loi connue"], "contraintes": ["lineaire"], "loi_predictive": loi,
            "espace_instances": {"dimension": d, "nombre_issues": m["nombre_issues"], "moniteur": nom,
                                 "sous_populations": banque_cal["sous_populations"], "banque": NOM + ":calibrage"},
            "source": f"{NOM} : loi connue (membre informé) ajustée sur le calibrage"}).valider())
    return sortie


# --- le juge ---------------------------------------------------------------------------------------------------------
def juger(monde, fiche, config, plein):
    """Chemin d'une fiche sans agent à la génération 0 (celui de `puissance_juge_banque_v1.juger_temoin`) : archive vide
    (gardé), nul informé si le monde le porte, plan par divergence, mesures déposées par le noyau, évaluation continue."""
    jpp.verifier_archive_vide(fiche, config)
    if abs(fiche.severite_attendue - config.alpha) > 1e-12 or fiche.loi_predictive is None:
        raise Arret("A8", f"{fiche.identifiant} : sévérité différente de α ou loi absente")
    graine_noyau = graine_derivee(config.graine, "noyau", 0)
    reservoir = monde.reservoir(fiche, 0)
    supplementaires = list(monde.membres_informes(fiche))
    gele = preparer_engagement(fiche, config, None, reservoir=reservoir, membres_supplementaires=supplementaires or None,
                               moniteur=monde.moniteur_de(fiche))
    if plein:
        jpp.verifier_plan_plein(gele, reservoir)
    if gele.engagement.get("instants_lecture"):
        raise Arret("A8", f"{fiche.identifiant} : lecture aux instants inattendue (membres ajustés présents)")
    mesures = monde.mesures(fiche.enonce, gele, graine_noyau, 0)
    ev = sp.evaluer(gele, mesures, graine_noyau=graine_noyau)
    ev["n_reservoir"] = len(reservoir)
    ev["membres_du_nul"] = [m["nom"] for m in gele.engagement["bibliotheque"]]
    plan = gele.engagement["instances"]
    ev["empreinte_plan"] = empreinte_objet(plan)
    ev["empreinte_prefixe_gele"] = empreinte_objet(plan[:jpp.TAILLE_PLAN_GELE])  # invariant du préfixe (L4′)
    return ev


def lire_famille(evs, temoins, m):
    """Deux lectures d'une famille jugée : par fiche (log W ≥ log(1/α) à un instant) et e-BH à m fixé (production :
    `appliquer_multiplicite`, témoins vrais hors famille au seuil log(m/α))."""
    issues = {i: {"verdict_final": "survit" if ev["promue"] else "eliminee", "motif": "", "pari": dict(ev),
                  "temoin": temoins[i]} for i, ev in evs.items()}
    appliquer_multiplicite(issues, ALPHA, m_fixe=m)
    sortie = {}
    for i, ev in evs.items():
        mult = issues[i]["pari"].get("multiplicite") or {}
        sortie[i] = {"temoin": temoins[i], "par_fiche": bool(ev["promue"]), "e_bh": issues[i]["verdict_final"] == "survit",
                     "log_w_max": round(ev["log_richesse_max"], 4), "log_w_final": round(ev["log_richesse_finale"], 4),
                     "n_plan": ev["nombre_tirages"], "n_reservoir": ev["n_reservoir"], "t_promotion": ev["t_promotion"],
                     "membre_dominant_final": ev["membre_dominant_final"], "log_e": mult.get("log_e"),
                     "empreinte_plan": ev["empreinte_plan"], "empreinte_prefixe_gele": ev["empreinte_prefixe_gele"]}
    return sortie


def etat_dents(verdicts, cle="e_bh"):
    vrais = [v for v in verdicts.values() if v["temoin"] == "vraie"]
    if not vrais:
        return "dents non mesurées"
    return "dents" if any(v[cle] for v in vrais) else "pas de dents"


def configurations(n_epreuve):
    return {"plein": jpp.configuration_plan_plein(n_epreuve), "gele": jpp.configuration_plan_gele()}


def juger_famille(chemin_banque, informe, fiches, m, n_epreuve):
    monde = MondeBanque(chemin_banque, jpp.GRAINE_DU_JUGE, nul_informe=informe)
    temoins = {f.identifiant: f.temoin for f in fiches}
    sortie = {}
    for bras, config in configurations(n_epreuve).items():
        evs = {f.identifiant: juger(monde, f, config, plein=(bras == "plein")) for f in fiches}
        sortie[bras] = lire_famille(evs, temoins, m)
    return sortie


# --- rééchantillonnage par tâche (témoins vrais) ----------------------------------------------------------------------
def banque_reechantillonnee(banque, tirage, taches):
    cal = [l for l in banque["instances"] if l["partie"] == "calibrage"]
    par_tache = collections.defaultdict(list)
    for l in banque["instances"]:
        if l["partie"] == "epreuve":
            par_tache[l["tache"]].append(l)
    neuves = []
    for copie, indice in enumerate(tirage):
        for l in par_tache[taches[int(indice)]]:
            neuves.append(dict(l, identifiant=f"b{copie:03d}/{l['identifiant']}", tache=f"b{copie:03d}/{l['tache']}",
                               issues=dict(l["issues"])))
    return dict(banque, instances=cal + neuves)


def _unite_reechantillonnage(arguments):
    banque, tirages, taches, vrais_t, vrais_r, m_t, m_r = arguments
    sortie = []
    vrais_t = [Fiche.depuis_dict(x) for x in vrais_t]
    vrais_r = [Fiche.depuis_dict(x) for x in vrais_r]
    with tempfile.TemporaryDirectory(prefix="lecture-t05-bs-") as tmp:
        for tirage in tirages:
            b = banque_reechantillonnee(banque, tirage, taches)
            chemin = _ecrire_banque(b, tmp)
            n_ep = sum(1 for l in b["instances"] if l["partie"] == "epreuve")
            ligne = {}
            for informe, fiches, m, famille in ((True, vrais_t, m_t, "T"), (False, vrais_r, m_r, "R")):
                if not fiches:
                    continue
                verdicts = juger_famille(chemin, informe, fiches, m, n_ep)
                ligne[famille] = {bras: {i: v["e_bh"] for i, v in vb.items()} for bras, vb in verdicts.items()}
            sortie.append(ligne)
    return sortie


def reechantillonner(banque, fiches_vraies_t, fiches_vraies_r, m_t, m_r, graine, nombre, processus):
    taches = sorted({l["tache"] for l in banque["instances"] if l["partie"] == "epreuve"})
    rng = np.random.default_rng(graine)
    tirages = [rng.integers(0, len(taches), size=len(taches)).tolist() for _ in range(nombre)]
    if not tirages or not (fiches_vraies_t or fiches_vraies_r):
        return {"repliques": 0, "taches": len(taches), "lignes": []}
    vt = [f.vers_dict() for f in fiches_vraies_t]
    vr = [f.vers_dict() for f in fiches_vraies_r]
    lots = [tirages[i::max(1, processus)] for i in range(max(1, processus))]
    arguments = [(banque, lot, taches, vt, vr, m_t, m_r) for lot in lots if lot]
    if processus > 1:
        with concurrent.futures.ProcessPoolExecutor(max_workers=processus) as pool:
            morceaux = list(pool.map(_unite_reechantillonnage, arguments))
    else:
        morceaux = [_unite_reechantillonnage(a) for a in arguments]
    lignes = [x for m in morceaux for x in m]
    return {"repliques": len(lignes), "taches": len(taches), "lignes": lignes}


def _quantile(valeurs, q):
    v = sorted(valeurs)
    if not v:
        return None
    return v[min(len(v) - 1, max(0, int(math.floor(q * (len(v) - 1) + 0.5))))]


def resumer_reechantillonnage(bs, famille, bras, idents):
    if not idents or not bs["lignes"]:
        return None
    fractions = [sum(l[famille][bras][i] for i in idents) / len(idents) for l in bs["lignes"]]
    return {"repliques": len(fractions), "moyenne": round(sum(fractions) / len(fractions), 4),
            "intervalle_95": [round(_quantile(fractions, 0.025), 4), round(_quantile(fractions, 0.975), 4)],
            "frequence_par_temoin": {i: round(sum(l[famille][bras][i] for l in bs["lignes"]) / len(bs["lignes"]), 4)
                                     for i in idents}}


def difference_reechantillonnage(bs, famille, idents):
    if not idents or not bs["lignes"]:
        return None
    d = [sum(l[famille]["plein"][i] for i in idents) - sum(l[famille]["gele"][i] for i in idents) for l in bs["lignes"]]
    return {"moyenne": round(sum(d) / len(d), 4), "intervalle_95": [_quantile(d, 0.025), _quantile(d, 0.975)],
            "part_plein_superieur_ou_egal": round(sum(x >= 0 for x in d) / len(d), 4)}


# --- lectures (telles qu'écrites au préenregistrement) ---------------------------------------------------------------
def lectures(r):
    T, R = r["familles"]["T"], r["familles"]["R"]
    vrais_plantes = sorted(i for i in T["verdicts"]["plein"] if i.startswith("TVP"))
    vrais_reels_r = sorted(i for i, v in R["verdicts"]["plein"].items() if v["temoin"] == "vraie")
    L = {}
    # L1 (décisive) : aucun témoin faux promu (e-BH), dans aucune des quatre configurations.
    faux = {f"{fam}-{bras}": sorted(i for i, v in F["verdicts"][bras].items() if v["temoin"] == "fausse" and v["e_bh"])
            for fam, F in (("T", T), ("R", R)) for bras in ("plein", "gele")}
    faux_par_fiche = {f"{fam}-{bras}": sorted(i for i, v in F["verdicts"][bras].items() if v["temoin"] == "fausse" and v["par_fiche"])
                      for fam, F in (("T", T), ("R", R)) for bras in ("plein", "gele")}
    L["L1"] = {"tenu": not any(faux.values()), "faux_promus_e_bh": faux, "faux_au_seuil_par_fiche_lu": faux_par_fiche}
    # L3′ réel : témoins vrais de la règle de L3, lus sous le monde aveugle, plan plein (tradition de L3).
    if vrais_reels_r:
        k = sum(R["verdicts"]["plein"][i]["e_bh"] for i in vrais_reels_r)
        L["L3_reel"] = {"etat": "dents" if k else "pas de dents", "promus": k, "juges": len(vrais_reels_r),
                        "fraction": round(k / len(vrais_reels_r), 4),
                        "reechantillonnage": resumer_reechantillonnage(r["reechantillonnage"], "R", "plein", vrais_reels_r)}
    else:
        L["L3_reel"] = {"etat": "dents non mesurées", "promus": 0, "juges": 0, "fraction": None,
                        "motif": "aucun témoin vrai réel : aucun couple (moniteur, trait) n'atteint |ρ| ≥ 0,35 au calibrage"}
    # L3′ planté (décisive pour les dents) : témoins vrais plantés, monde informé, plan plein.
    kp = sum(T["verdicts"]["plein"][i]["e_bh"] for i in vrais_plantes)
    L["L3_plante"] = {"promus": kp, "juges": len(vrais_plantes), "fraction": round(kp / len(vrais_plantes), 4) if vrais_plantes else None,
                      "conditionnel_aux_paires": conditionnel_aux_paires(r["plantes"], r["epreuve"]["episodes_retenus"]),
                      "par_force": {str(f): T["verdicts"]["plein"][i]["e_bh"] for f, i in zip(r["forces_plantees"], vrais_plantes)},
                      "reechantillonnage": resumer_reechantillonnage(r["reechantillonnage"], "T", "plein", vrais_plantes)}
    L["dents"] = {f"T-{bras}": etat_dents(T["verdicts"][bras]) for bras in ("plein", "gele")}
    L["dents"]["reels_seuls"] = L["L3_reel"]["etat"]
    # Comparaison des bras (L4′) : le plan gelé est le préfixe du plan plein (même ordre) ; invariant vérifié, gain lu.
    ecarts_prefixe = []
    for fam, F in (("T", T), ("R", R)):
        for i, p in F["verdicts"]["plein"].items():
            g = F["verdicts"]["gele"][i]
            if g["empreinte_plan"] != p["empreinte_prefixe_gele"]:
                ecarts_prefixe.append(f"{fam}:{i} : plan gelé ≠ préfixe du plan plein")
            if p["log_w_max"] < g["log_w_max"] - 1e-6:
                ecarts_prefixe.append(f"{fam}:{i} : log W max plein < gelé")
            if g["temoin"] == "vraie" and g["e_bh"] and not p["e_bh"]:
                ecarts_prefixe.append(f"{fam}:{i} : témoin vrai promu sous le plan gelé, pas sous le plan plein")
    L["invariant_prefixe"] = {"tenu": not ecarts_prefixe, "ecarts": ecarts_prefixe}
    kg = sum(T["verdicts"]["gele"][i]["e_bh"] for i in vrais_plantes)
    lr = lambda bras: sorted(i for i, v in R["verdicts"][bras].items() if i.startswith("LR-") and v["e_bh"])  # noqa: E731
    L["L4_comparaison"] = {"plantes_promus": {"plein": kp, "gele": kg}, "gain_du_plan_plein": kp - kg,
                           "plein_au_moins_autant": kp >= kg,
                           "par_force": {str(f): {"plein": T["verdicts"]["plein"][i]["e_bh"], "gele": T["verdicts"]["gele"][i]["e_bh"],
                                                  "log_w_max_plein": T["verdicts"]["plein"][i]["log_w_max"],
                                                  "log_w_max_gele": T["verdicts"]["gele"][i]["log_w_max"]}
                                         for f, i in zip(r["forces_plantees"], vrais_plantes)},
                           "difference_reechantillonnage": difference_reechantillonnage(r["reechantillonnage"], "T", vrais_plantes),
                           "lois_reelles_promues": {"plein": lr("plein"), "gele": lr("gele")}}
    # LR (lois réelles, préenregistrée, non décisive pour le juge) : lois connues promues, monde aveugle, plan plein.
    promues = lr("plein")
    bornes = {}
    for i, v in sorted(R["verdicts"]["plein"].items()):
        if not i.startswith("LR-"):
            continue
        n = v["n_plan"]
        bornes[i] = {"n_juge": n, "promue": v["e_bh"], "log_w_max": v["log_w_max"], "borne": borne_information(n)}
    L["LR"] = {"promues_plein": promues, "promues_gele": lr("gele"), "par_moniteur": bornes,
               "lecture": "aucune loi réelle promue : borne I*(N) par moniteur" if not promues else
                          "loi(s) réelle(s) promue(s) : audit R4 obligatoire avant toute phrase"}
    L["exposition"] = {"lectures_de_l_epreuve": 1, "configurations": 4,
                       "fiches_jugees": {"T": len(T["verdicts"]["plein"]), "R": len(R["verdicts"]["plein"])},
                       "verdicts_montres_a_un_proposeur_avant_la_lecture": 0,
                       "repliques_de_reechantillonnage": r["reechantillonnage"]["repliques"],
                       "taches_d_epreuve": r["epreuve"]["taches_retenues"]}
    L["predictions"] = verifier_predictions(r, L, vrais_plantes)
    L["issue"] = issue_de(L)
    L["audit_R4"] = declencheurs_r4(r, L, vrais_plantes)
    return L


def verifier_predictions(r, L, vrais_plantes):
    n = r["epreuve"]["episodes_retenus"]
    P = {}
    P["P1_L1_tenu"] = {"predit": True, "observe": L["L1"]["tenu"], "tenu": L["L1"]["tenu"]}
    P["P2_aucun_temoin_vrai_reel"] = {"predit": 0, "observe": L["L3_reel"]["juges"], "tenu": L["L3_reel"]["juges"] == 0}
    attendu = {str(f): round(puissance_courbe(f, n, "plein"), 3) for f in r["forces_plantees"]}
    P["P3_plantes_plein_au_moins_deux_tiers"] = {"predit": ">= 2/3", "observe": L["L3_plante"]["fraction"],
                                                  "taux_courbe_attendus": attendu,
                                                  "conditionnel_aux_paires": L["L3_plante"]["conditionnel_aux_paires"],
                                                  "tenu": L["L3_plante"]["fraction"] is not None and L["L3_plante"]["fraction"] >= 2 / 3 - 1e-9}
    attendu_g = {str(f): round(puissance_courbe(f, n, "gele"), 3) for f in r["forces_plantees"]}
    gain = round(sum(puissance_courbe(f, n, "plein") - puissance_courbe(f, n, "gele") for f in r["forces_plantees"]), 3)
    P["P4_gain_du_plan_plein_lu"] = {"predit": f"gain attendu {gain} témoin (lu, sans seuil ; signe garanti par l'invariant)",
                                      "observe": L["L4_comparaison"]["gain_du_plan_plein"], "taux_courbe_gele": attendu_g,
                                      "tenu": None}
    P["P5_aucune_loi_reelle_promue"] = {"predit": "0 (plein et gelé)",
                                        "observe": {"plein": len(L["LR"]["promues_plein"]), "gele": len(L["LR"]["promues_gele"])},
                                        "tenu": not L["LR"]["promues_plein"] and not L["LR"]["promues_gele"]}
    return P


def issue_de(L):
    """Issues écrites d'avance (préenregistrement, section « Issues »)."""
    if not L["L1"]["tenu"]:
        return {"code": "I3", "texte": "alarme de validité : un témoin faux promu ; aucune autre lecture n'est interprétée ; "
                                       "audit R4 et nœud de Lazar"}
    forts = [L["L3_plante"]["par_force"].get(str(f)) for f in (0.5, 0.8)]
    if not any(forts):
        return {"code": "I4", "texte": "pas de dents aux forces 0,5 et 0,8 sous le plan plein (prédit ≥ 0,96) : contraire à la "
                                       "courbe ; audit R4 de la chaîne ; aucune conclusion sur les lois réelles"}
    if not L["invariant_prefixe"]["tenu"]:
        return {"code": "I5", "texte": "invariant du préfixe non tenu (le plan gelé doit être le préfixe du plan plein) : "
                                       "incohérence de la chaîne ; audit R4 ; lectures LR données sans conclusion"}
    if L["LR"]["promues_plein"]:
        return {"code": "I2", "texte": "juge valide et denté ; loi(s) réelle(s) promue(s) sous le plan plein : réplique de la "
                                       "dépendance connue sur graines neuves des mêmes tâches, après audit R4"}
    return {"code": "I1", "texte": "juge valide et denté ; aucune loi réelle promue : borne I*(N) par moniteur"}


def declencheurs_r4(r, L, vrais_plantes):
    """Déclencheurs symétriques (R4) : trop beau ou trop mauvais, le même audit."""
    T, R = r["familles"]["T"], r["familles"]["R"]
    d = []
    for fam, F in (("T", T), ("R", R)):
        for bras in ("plein", "gele"):
            for i, v in F["verdicts"][bras].items():
                if v["temoin"] == "fausse" and v["par_fiche"]:
                    d.append(f"trop beau : témoin faux {i} au seuil par fiche ({fam}-{bras})")
    for i in sorted(set(L["LR"]["promues_plein"]) | set(L["LR"]["promues_gele"])):
        bras = [b for b in ("plein", "gele") if i in L["LR"][f"promues_{b}"]]
        d.append(f"trop beau : loi réelle {i} promue ({', '.join(bras)} ; information prédite au calibrage ≤ 0,01 nat par "
                 "épisode)")
    for f, i in zip(r["forces_plantees"], vrais_plantes):
        v = T["verdicts"]["plein"][i]
        if f >= 0.5 and not v["e_bh"]:
            d.append(f"trop mauvais : témoin planté de force {f} non promu sous le plan plein")
        if v["log_w_max"] < 0:
            d.append(f"trop mauvais : témoin planté de force {f} à log W max négatif sous le plan plein")
    for e in L["invariant_prefixe"]["ecarts"]:
        d.append(f"incohérence : {e}")
    return {"declenche": bool(d), "motifs": d}


# --- Markdown (tous les chiffres viennent du JSON écrit) ---------------------------------------------------------------
def _fr(x, chiffres=2):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "oui" if x else "non"
    if isinstance(x, int):
        return str(x)
    return f"{x:.{chiffres}f}".replace(".", ",")


def markdown(r):
    L = r["lecture"]
    A = []
    titre = "Lecture du lot T0.5 à graines neuves — v1" + (" — COURSE À BLANC (non opposable)" if r["a_blanc"] else "")
    A.append(f"# {titre}\n")
    A.append(f"Date : {r['date_utc']}. Préenregistrement : `{r['preenregistrement']['chemin']}` (sha256 "
             f"{r['preenregistrement']['sha256']}). Calibrage : sha256 {r['calibrage']['empreinte']}. Code : "
             f"sha256 {r['empreintes']['script']} (script), {r['empreintes']['juge_plan_plein_v1']} (juge).\n")
    A.append(f"## Issue : {L['issue']['code']}\n\n{L['issue']['texte']}.\n")
    A.append("## Épreuve\n")
    e = r["epreuve"]
    A.append(f"Épisodes retenus : {e['episodes_retenus']} ({e['taches_retenues']} tâches) ; exclus sans jetons : "
             f"{e['exclus_sans_jetons']} ; exclus sans notation : {e['exclus_sans_notation']}. Instances jugées par moniteur "
             f"réel : " + ", ".join(f"{k} {v}" for k, v in r["instances_par_moniteur"].items()) + ".\n")
    A.append("## Lectures\n")
    A.append(f"- **L1** (décisive) {'tenu' if L['L1']['tenu'] else '**non tenu**'} : témoins faux promus (e-BH) "
             + "; ".join(f"{k} : {v or 'aucun'}" for k, v in L["L1"]["faux_promus_e_bh"].items()) + ".")
    lr3 = L["L3_reel"]
    A.append(f"- **L3′ réel** : {lr3['etat']} ({lr3['promus']} promus sur {lr3['juges']} jugés).")
    lp = L["L3_plante"]
    bs = lp.get("reechantillonnage") or {}
    A.append(f"- **L3′ planté** (décisive, monde informé, plan plein) : {lp['promus']}/{lp['juges']} promus "
             f"(fraction {_fr(lp['fraction'])}) ; par force : "
             + ", ".join(f"{k} → {_fr(v)}" for k, v in lp["par_force"].items())
             + (f" ; rééchantillonnage par tâche ({bs['repliques']} répliques) : moyenne {_fr(bs['moyenne'])}, intervalle à "
                f"95 % [{_fr(bs['intervalle_95'][0])} ; {_fr(bs['intervalle_95'][1])}]" if bs else "") + ".")
    cp = lp.get("conditionnel_aux_paires") or {}
    if cp.get("applicable"):
        A.append(f"  Prédiction conditionnelle aux paires tirées : attendus plein {_fr(cp['attendu_plein'])}, gelé "
                 f"{_fr(cp['attendu_gele'])} ; P(fraction ≥ 2/3) = {_fr(cp['proba_fraction_au_moins_deux_tiers'])} ; "
                 f"P(I4) = {_fr(cp['proba_I4'], 4)}.")
    A.append(f"- **Dents** : " + ", ".join(f"{k} : {v}" for k, v in L["dents"].items()) + ".")
    c = L["L4_comparaison"]
    dbs = c.get("difference_reechantillonnage") or {}
    A.append(f"- **L4′ comparaison** (lue) : témoins plantés promus, plein {c['plantes_promus']['plein']}, gelé "
             f"{c['plantes_promus']['gele']} ; gain du plan plein : {c['gain_du_plan_plein']}"
             + (f" ; différence rééchantillonnée : moyenne {_fr(dbs['moyenne'])}, intervalle [{dbs['intervalle_95'][0]} ; "
                f"{dbs['intervalle_95'][1]}]" if dbs else "")
             + f" ; lois réelles promues, plein {c['lois_reelles_promues']['plein'] or 'aucune'}, gelé "
               f"{c['lois_reelles_promues']['gele'] or 'aucune'}.")
    A.append(f"- **LR** (lois réelles, monde aveugle, plan plein) : {L['LR']['lecture']}.")
    A.append("")
    A.append("| moniteur (loi connue) | N jugé | log W max | promue | borne I*(N) (nat/épisode ; force) |")
    A.append("|---|---|---|---|---|")
    for i, b in L["LR"]["par_moniteur"].items():
        borne = b["borne"]
        A.append(f"| {i} | {b['n_juge']} | {_fr(b['log_w_max'])} | {_fr(b['promue'])} | "
                 + (f"{_fr(borne['information_nat'], 3)} ; {_fr(borne['force'], 2)}" if borne else "hors grille") + " |")
    A.append("")
    A.append("## Témoins de la famille T (monde informé)\n")
    A.append("| fiche | vérité | log W max plein | e-BH plein | log W max gelé | e-BH gelé | N plan plein / gelé |")
    A.append("|---|---|---|---|---|---|---|")
    T = r["familles"]["T"]["verdicts"]
    for i in sorted(T["plein"]):
        p, g = T["plein"][i], T["gele"][i]
        A.append(f"| {i} | {p['temoin']} | {_fr(p['log_w_max'])} | {_fr(p['e_bh'])} | {_fr(g['log_w_max'])} | {_fr(g['e_bh'])} | "
                 f"{p['n_plan']} / {g['n_plan']} |")
    A.append("")
    A.append("## Prédictions\n")
    for k, v in L["predictions"].items():
        etat = "lu" if v["tenu"] is None else ("tenu" if v["tenu"] else "**non tenu**")
        A.append(f"- **{k}** : prédit {v['predit']}, observé {v['observe']} → {etat}.")
    A.append(f"- **Invariant du préfixe** : {'tenu' if L['invariant_prefixe']['tenu'] else '**non tenu** : ' + '; '.join(L['invariant_prefixe']['ecarts'])}.")
    A.append("")
    A.append("## Exposition\n")
    A.append("; ".join(f"{k} : {v}" for k, v in L["exposition"].items()) + ".\n")
    A.append("## Audit R4\n")
    A.append(("Déclenché : " + " ; ".join(L["audit_R4"]["motifs"])) if L["audit_R4"]["declenche"] else "Aucun déclencheur.")
    A.append("")
    A.append(f"Seuils : par fiche log(1/α) = {_fr(r['seuils_log']['par_fiche'], 3)} (lu) ; e-BH famille T, m = {r['familles']['T']['m']} : "
             f"log(m/α) = {_fr(r['seuils_log']['T'], 3)} ; famille R, m = {r['familles']['R']['m']} : {_fr(r['seuils_log']['R'], 3)} "
             f"(décisifs).\n")
    return "\n".join(A)


# --- principal --------------------------------------------------------------------------------------------------------
def _chemin_lisible(chemin):
    """Chemin relatif à la racine du code s'il y est, absolu sinon."""
    absolu = os.path.abspath(chemin)
    relatif = os.path.relpath(absolu, RACINE)
    return absolu if relatif.startswith("..") else relatif


def _ecrire_arret(dossier, arret, contexte):
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, "arret.json")
    with open(chemin, "x", encoding="utf-8") as f:
        f.write(json.dumps({"nom": NOM, "arret": arret.code, "message": arret.message, "contexte": contexte,
                            "date_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())},
                           ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return chemin


def executer(args):
    debut, quand = time.time(), time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    contexte = {"etape": "préenregistrement"}
    try:
        empreinte_prereg = empreinte_compagnon(args.preenregistrement)
        if args.empreinte_preenregistrement and args.empreinte_preenregistrement.lower() != empreinte_prereg:
            raise Arret("A2", f"préenregistrement : empreinte {empreinte_prereg[:12]}…, attendue "
                              f"{args.empreinte_preenregistrement[:12]}…")
        graines = graines_de(empreinte_prereg)
        attendue = args.empreinte_calibrage or EMPREINTE_CALIBRAGE
        a_blanc = attendue != EMPREINTE_CALIBRAGE
        contexte["etape"] = "code"
        code = verifier_code(args.preenregistrement, a_blanc)
        contexte["etape"] = "calibrage"
        banque_cal = lire_calibrage(args.calibrage, attendue)
        temoins_reels, rangs, resume_rangs = temoins_de_calibrage(banque_cal)
        a7 = verifier_table_de_rangs(resume_rangs, a_blanc)
        contexte["etape"] = "lot"
        table = lire_table(args.table_identifiants, EMPREINTE_TABLE if not a_blanc else (args.empreinte_table or EMPREINTE_TABLE))
        lot = lire_lot(args.run, args.notations_sup, banque_cal, table)
        instances, comptes_epreuve = construire_epreuve(lot, banque_cal, graines["bruit"])
        par_moniteur = verifier_moniteurs(instances, banque_cal["moniteurs"], K_MIN)
        contexte["etape"] = "juge"
        with tempfile.TemporaryDirectory(prefix="lecture-t05-") as tmp:
            connues = lois_connues(banque_cal, tmp)
            banque, plantes = banque_complete(banque_cal, instances, graines)
            chemin_banque = _ecrire_banque(banque, tmp)
            monde_informe = MondeBanque(chemin_banque, jpp.GRAINE_DU_JUGE, nul_informe=True)
            for nom, loi in connues.items():  # A8 : la loi connue servie en fiche est celle du membre informé
                factice = type("F", (), {"espace_instances": {"moniteur": nom, "nombre_issues": banque["moniteurs"][nom]["nombre_issues"],
                                                               "dimension": len(banque["traits"])}})()
                if monde_informe.membres_informes(factice)[0]["loi"] != loi:
                    raise Arret("A8", f"loi connue de {nom} différente du membre informé du monde de lecture")
            plantes_fiches = temoins_plantes(banque, plantes)
            famille_t = temoins_reels + plantes_fiches
            famille_r = fiches_lois_reelles(connues, banque_cal) + temoins_reels
            m_t = sum(1 for f in famille_t if f.temoin != "vraie")
            m_r = sum(1 for f in famille_r if f.temoin != "vraie")
            n_epreuve = len(instances)
            verdicts_t = juger_famille(chemin_banque, True, famille_t, m_t, n_epreuve)
            verdicts_r = juger_famille(chemin_banque, False, famille_r, m_r, n_epreuve)
            vrais_t = [f for f in famille_t if f.temoin == "vraie" and f.identifiant.startswith("TVP")]
            vrais_r = [f for f in famille_r if f.temoin == "vraie"]
            contexte["etape"] = "rééchantillonnage"
            bs = reechantillonner(banque, vrais_t, vrais_r, m_t, m_r, graines["reechantillonnage"],
                                  args.reechantillonnages, args.processus)
    except Arret as a:
        chemin = _ecrire_arret(args.sortie, a, contexte)
        print(json.dumps({"arret": a.code, "message": a.message, "fichier": chemin}, ensure_ascii=False))
        return 2
    with open(os.path.abspath(__file__), "rb") as f:
        empreinte_script = hashlib.sha256(f.read()).hexdigest()
    r = {
        "nom": NOM, "date_utc": quand, "duree_s": round(time.time() - debut, 1), "a_blanc": a_blanc,
        "preenregistrement": {"chemin": _chemin_lisible(args.preenregistrement), "sha256": empreinte_prereg,
                              "verification_du_code": code},
        "calibrage": {"empreinte": banque_cal["empreinte"], "attendue": attendue, "instances": len(banque_cal["instances"]),
                      "taches": len({l["tache"] for l in banque_cal["instances"]}), "moniteurs": sorted(banque_cal["moniteurs"]),
                      "normalisation": banque_cal["normalisation"], "table_de_rangs": rangs, "resume_rangs": resume_rangs,
                      "garde_A7": a7},
        "lot": {"sources": dict(lot["sources"]),
                "comptes": lot["comptes"]},
        "epreuve": comptes_epreuve, "instances_par_moniteur": par_moniteur, "k_min": K_MIN,
        "forces_plantees": list(FORCES_PLANTEES),
        "plantes": [{k: v for k, v in p.items() if not k.startswith("loi")} for p in plantes],
        "graines": {"regle": "numpy.random.SeedSequence(int(sha256 du préenregistrement, 16)).spawn(4) : bruit, plantation, "
                             "permutation, rééchantillonnage ; graine du juge 20261027",
                    "entropie_hex": graines["entropie_hex"], "plantation": graines["plantation"],
                    "juge": jpp.GRAINE_DU_JUGE},
        "configurations": {b: dataclasses.asdict(c) for b, c in configurations(n_epreuve).items()},
        "familles": {
            "T": {"monde": "informé", "m": m_t, "fiches": {f.identifiant: f.empreinte() for f in famille_t},
                  "verdicts": verdicts_t},
            "R": {"monde": "aveugle", "m": m_r, "fiches": {f.identifiant: f.empreinte() for f in famille_r},
                  "verdicts": verdicts_r}},
        "seuils_log": {"par_fiche": math.log(1 / ALPHA), "T": math.log(m_t / ALPHA), "R": math.log(m_r / ALPHA)},
        "reechantillonnage": bs,
        "courbe": COURBE_SOURCE,
        "environnement": {"python": platform.python_version(), "numpy": np.__version__, "coeurs": os.cpu_count(),
                          "processus": args.processus},
        "empreintes": {"script": empreinte_script, "juge_plan_plein_v1": sha256_fichier(os.path.join(RACINE, "pole", "juge_plan_plein_v1.py")),
                       **{f"pole/{n}": sha256_fichier(os.path.join(RACINE, "pole", n))
                          for n in ("selection_pari.py", "monde_banque.py", "cycle.py", "nul_v8.py", "fiche.py")},
                       "exemples/construire_banque_t05_v3.py": sha256_fichier(os.path.join(EXEMPLES, "construire_banque_t05_v3.py")),
                       "exemples/proposeur_scripte_banque_v1.py": sha256_fichier(os.path.join(EXEMPLES, "proposeur_scripte_banque_v1.py"))},
    }
    r["lecture"] = lectures(r)
    chemin_json = os.path.join(args.sortie, f"{NOM}.json")
    chemin_md = os.path.join(args.sortie, f"{NOM}.md")
    with open(chemin_json, "x", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False, indent=1, sort_keys=True, allow_nan=False) + "\n")
    with open(chemin_json, encoding="utf-8") as f:  # le Markdown est rendu depuis le JSON écrit, rien d'autre
        relu = json.load(f)
    with open(chemin_md, "x", encoding="utf-8") as f:
        f.write(markdown(relu))
    print(json.dumps({"issue": r["lecture"]["issue"]["code"], "L1": r["lecture"]["L1"]["tenu"],
                      "L3_plante": r["lecture"]["L3_plante"]["fraction"], "a_blanc": a_blanc, "duree_s": r["duree_s"]},
                     ensure_ascii=False))
    return 0


def analyseur():
    a = argparse.ArgumentParser(description="Lecture préenregistrée du lot T0.5 à graines neuves (v1)")
    a.add_argument("--preenregistrement", required=True)
    a.add_argument("--empreinte-preenregistrement", default=None)
    a.add_argument("--calibrage", required=True)
    a.add_argument("--empreinte-calibrage", default=None, help="autre que celle du préenregistrement : course à blanc")
    a.add_argument("--table-identifiants", required=True, help="table des identifiants du kit (tâche d'origine → -g2 → lot)")
    a.add_argument("--empreinte-table", default=None, help="course à blanc seulement")
    a.add_argument("--run", action="append", default=[], help="dossier diag/<run>/ d'une branche de résultats")
    a.add_argument("--notations-sup", action="append", default=[])
    a.add_argument("--sortie", required=True)
    a.add_argument("--reechantillonnages", type=int, default=1000)
    a.add_argument("--processus", type=int, default=1)
    return a


def principal(argv=None):
    args = analyseur().parse_args(argv)
    if args.reechantillonnages < 0 or args.processus < 1:
        raise SystemExit("--reechantillonnages ≥ 0 et --processus ≥ 1")
    depot_public = os.path.dirname(RACINE)  # la sortie porte des données réelles dérivées : jamais dans le dépôt public
    if os.path.commonpath([os.path.abspath(args.sortie), depot_public]) == depot_public:
        raise SystemExit(f"sortie dans le dépôt public ({depot_public}) : refusée")
    if os.path.exists(args.sortie) and os.listdir(args.sortie):
        raise FileExistsError(args.sortie)
    os.makedirs(args.sortie, exist_ok=True)
    return executer(args)


if __name__ == "__main__":
    sys.exit(principal())
