"""Courbe de puissance du juge sur la banque réelle (v1) — mesure de l'instrument ; exploratoire, zéro dépense.

Contexte. Sur les 13 moniteurs réels de la banque T0.5 v2 (`exemples/banque-t05-v2.json` : 120 épisodes du modèle de
8 milliards de paramètres, 60 tâches de 2 épisodes, 40 de calibrage et 80 d'épreuve), `demo_couche1_proposeur_v7.py` ne
promeut rien (« pas de dents, pas de conclusion »). Ce banc transforme le constat en mesure : la probabilité que le juge,
**tel qu'il est**, promeuve un témoin vrai planté, selon (a) la force de l'effet planté et (b) le nombre N d'épisodes
d'épreuve ; et, dans les mêmes cellules, le taux de promotion de témoins faux. Processeur seul, sans réseau, sans dépense.

Juge — réglages de `demo_couche1_proposeur_v7.py`, inchangés : sélection par pari, juge v1 sans urne (ordre secret),
nul des filles v2, nul informé (prédicteur connu ajusté sur le calibrage), nul d'archive, règle e-BH, α = 0,05,
`taille_plan` = 120, témoins jugés sans agents, politique de redite « refus ». Le chemin d'un témoin est celui du code :
`Generation.geler` (nul informé ; un témoin ne reçoit **aucun** membre d'archive, `cycle.py`), `preparer_engagement`
(plan des min(120, N) instances les plus divergentes du réservoir d'épreuve), `MondeBanque.mesures`, `sp.evaluer`, puis
`appliquer_multiplicite` (un témoin vrai est lu hors famille au seuil log(m/α) ; un témoin faux est dans la famille).

Banque de chaque répétition : la **structure** de la banque v2 (vecteurs de traits z et sous-population g de ses 120
épisodes, tâches de 2 épisodes) ; N/2 tâches d'épreuve et N/4 de calibrage (rapport 2 : 1 de la v2), tirées parmi les
60 tâches réelles **sans remise** si 3N/4 ≤ 60 (N ≤ 80), **avec remise** au-delà (une tâche réelle peut alors servir
plusieurs fois, avec des issues plantées tirées à neuf : mêmes traits, issues indépendantes). Les issues réelles ne sont
pas lues ; seules les issues plantées le sont.

Témoins — construction de `exemples/construire_banque_t05_v3.py`, réutilisée telle quelle (`planter`, `_fiche`) :
un moniteur planté par force (loi si/sinon au seuil 0 sur un trait réel z_j, softmax à 3 issues de signes opposés sur un
autre trait réel z_i, poids ±force ; paire (i, j) et signe tirés par la graine) ; témoin vrai = sa loi ; témoin faux
« bruit » = même forme sur le trait de bruit (celui de la v3) ; en plus, témoin faux « même forme » = la loi vraie jugée
sur un moniteur dont les issues sont celles du moniteur planté **permutées au hasard** entre toutes les instances (lien
trait → issue détruit, marginale gardée).

Lectures du verdict (une trajectoire, trois lectures) : « par fiche » (log W ≥ log(1/α) ≈ 3,0 à un instant, sans
multiplicité) ; « e-BH, m = 17 » (**lecture principale** : m des témoins plantés de la couche 1 bis v2, et des générations
1 à 3 de la démo, 15 à 17) ; « e-BH, m = m₀ » (m de la génération 0 de la démo sur la banque réelle : fiches de la
population v2 plus témoins faux par génération, calculé ici sur les fichiers). Variante **hors juge gelé**, lue à côté :
`taille_plan` = N (le plan prend tout le réservoir) pour N > 120.

Lecture fixée avant l'exécution (écrite le 1er novembre 2026 à 19:55 UTC, avant toute course ; recopiée telle quelle
dans le JSON et en tête du Markdown) : voir LECTURE_FIXEE ci-dessous.

Graines (R9) : `numpy.random.SeedSequence(graine, spawn_key=(N, r))` par répétition r, puis trois fils (banque,
plantation, permutation) ; `planter` reçoit l'entier tiré du fils « plantation » (il dérive ses propres flux par
`graine_derivee`, code de la v3 inchangé). Graine du juge : 20261027, celle de la démo.

Usage : python -I -B demonstrations/puissance_juge_banque_v1.py DOSSIER_NEUF [--repetitions 100] [--processus 4]
        [--forces 0.1,0.2,0.3,0.5,0.8] [--episodes 60,120,144,180,288,600] [--graine 20261101] [--sans-variante]
        python -I -B demonstrations/puissance_juge_banque_v1.py --mesurer   (coût d'une cellule, rien n'est écrit)
Sorties : DOSSIER/puissance-juge-banque-v1.json et DOSSIER/puissance-juge-banque-v1.md (aucun compagnon .sha256 :
le scellement est fait à part).
"""

import os

for _variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):  # un fil numpy par processus
    os.environ.setdefault(_variable, "1")

import argparse  # noqa: E402
import concurrent.futures  # noqa: E402
import dataclasses  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
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
from pole import nul_filles_v2 as nf  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole.cycle import ConfigGeneration, appliquer_multiplicite, preparer_engagement  # noqa: E402
from pole.fiche import Fiche, charger_fiches  # noqa: E402
from pole.monde_banque import MondeBanque  # noqa: E402
from pole.outils import graine_derivee, sha256_fichier  # noqa: E402

NOM = "puissance-juge-banque-v1"
BANQUE_REELLE = os.path.join(EXEMPLES, "banque-t05-v2.json")
POPULATION_REELLE = os.path.join(EXEMPLES, "population-banque-t05-v2.json")
TEMOINS_REELS = os.path.join(EXEMPLES, "temoins-banque-t05-v2.json")
GRAINE_DU_JUGE = 20261027  # celle de demo_couche1_proposeur_v7.py
ALPHA = 0.05
TAILLE_PLAN = 120
M_PRINCIPAL = 17
FORCES = (0.1, 0.2, 0.3, 0.5, 0.8)
EPISODES = (60, 120, 144, 180, 288, 600)
PUISSANCE_CIBLE = 0.9

LECTURE_FIXEE = {
    "ecrite": "2026-11-01, 19:55 UTC, avant toute course",
    "lecture_principale": "e-BH, m = 17 (témoin vrai hors famille au seuil log(m/α)), juge gelé (taille_plan = 120)",
    "P1": {"texte": "à force 0,5 et N = 144 épisodes d'épreuve, taux de promotion des témoins vrais ≥ 0,8 (réplique la "
                    "couche 1 bis v2 : force 0,5 promue à 144 épisodes d'épreuve, plan de 120, m = 17)",
           "force": 0.5, "episodes": 144, "seuil_minimal": 0.8},
    "P2": {"texte": "à force ≤ 0,2 et N ≤ 180, taux de promotion des témoins vrais < 0,5 dans chaque cellule",
           "force_maximale": 0.2, "episodes_maximal": 180, "seuil_strict": 0.5},
    "P3": {"texte": "taux de promotion des témoins faux ≤ 0,05 dans chaque cellule, pour les deux sortes de témoins faux "
                    "(bruit, même forme permutée) et les trois lectures (par fiche, e-BH m = 17, e-BH m = m₀), juge gelé ; "
                    "la borne haute de Clopper-Pearson est rapportée, non décisive",
           "seuil_maximal": 0.05},
    "L4": {"texte": "lue, sans seuil : gain de puissance de N = 120 à N = 600, juge gelé (plan de 120) contre la variante "
                    "taille_plan = N"},
}


# --- structure réelle et banque d'une répétition ------------------------------------------------------------------
_STRUCTURE = {}


def structure_reelle(chemin=BANQUE_REELLE):
    """Tâches de la banque réelle (traits et sous-population de chaque épisode) ; aucune issue réelle n'est gardée."""
    if chemin not in _STRUCTURE:
        with open(chemin, encoding="utf-8") as f:
            banque = json.load(f)
        taches = {}
        for ligne in banque["instances"]:
            taches.setdefault(ligne["tache"], []).append({"z": list(ligne["z"]), "g": int(ligne["g"])})
        tailles = sorted({len(v) for v in taches.values()})
        if tailles != [2]:
            raise ValueError(f"banque réelle : tâches de tailles {tailles}, 2 épisodes par tâche attendus")
        parties = {}
        for ligne in banque["instances"]:
            parties[ligne.get("partie", "epreuve")] = parties.get(ligne.get("partie", "epreuve"), 0) + 1
        _STRUCTURE[chemin] = {"traits": list(banque["traits"]), "sous_populations": int(banque.get("sous_populations", 2)),
                              "taches": [taches[t] for t in sorted(taches)], "episodes": len(banque["instances"]),
                              "parties": parties, "moniteurs_reels": len(banque["moniteurs"])}
    return _STRUCTURE[chemin]


def graines_de(graine, n_epreuve, r):
    """R9 : une SeedSequence par (N, répétition), trois fils (banque, plantation, permutation)."""
    ss = np.random.SeedSequence(graine, spawn_key=(int(n_epreuve), int(r)))
    fils = ss.spawn(3)
    return {"banque": fils[0], "plantation": int(fils[1].generate_state(1, dtype=np.uint64)[0]), "permutation": fils[2]}


def banque_de_repetition(structure, n_epreuve, forces, graines):
    """Banque plantée d'une répétition (au format du monde sur banque), ses moniteurs plantés et nuls, et ses témoins."""
    if n_epreuve % 4:
        raise ValueError("N doit être multiple de 4 (N/2 tâches d'épreuve, N/4 de calibrage)")
    n_cal, n_ep = n_epreuve // 4, n_epreuve // 2
    total = n_cal + n_ep
    rng = np.random.default_rng(graines["banque"])
    remise = total > len(structure["taches"])
    choix = rng.choice(len(structure["taches"]), size=total, replace=remise)
    instances = []
    for k, t in enumerate(choix):
        partie = "calibrage" if k < n_cal else "epreuve"
        for ep in structure["taches"][int(t)]:
            instances.append({"identifiant": f"r{k:04d}/e{ep['g']}", "tache": f"r{k:04d}", "g": ep["g"], "z": list(ep["z"]),
                              "issues": {}, "partie": partie})
    effectifs = {p: sum(1 for l in instances if l["partie"] == p) for p in ("calibrage", "epreuve")}
    if effectifs["epreuve"] != n_epreuve:
        raise ValueError(f"banque : {effectifs['epreuve']} instances d'épreuve pour N = {n_epreuve}")
    banque = {"nom": f"{NOM}-N{n_epreuve}", "traits": list(structure["traits"]), "sous_populations": structure["sous_populations"],
              "moniteurs": {}, "instances": instances}
    plantes = b3.planter(banque, len(forces), graines["plantation"], tuple(forces))
    rng_perm = np.random.default_rng(graines["permutation"])
    for p in plantes:
        nul = "nul:" + p["moniteur"].split(":", 1)[1]
        valeurs = [l["issues"][p["moniteur"]] for l in instances]
        for l, i in zip(instances, rng_perm.permutation(len(valeurs))):
            l["issues"][nul] = int(valeurs[int(i)])
        banque["moniteurs"][nul] = {"juge": "nul", "rubrique": "permutation", "coupes": None, "nombre_issues": 3,
                                    "instances": len(instances)}
    d = len(banque["traits"])
    k_de = {n: m["nombre_issues"] for n, m in banque["moniteurs"].items()}
    temoins = []
    for numero, p in enumerate(plantes, 1):  # comme fabriquer_temoins (v3) pour les plantés, plus le faux « même forme »
        nul = "nul:" + p["moniteur"].split(":", 1)[1]
        tv = b3._fiche(f"TVP{numero:02d}", {"moniteur": p["moniteur"], "loi_predictive": p["loi_vraie"],
                                            "etiquette": f"vrai planté : force {p['force']}"}, "vraie", d, k_de, banque,
                       f"L'issue du moniteur {p['moniteur']} suit une loi à seuil sur deux traits réels (n° {numero})")
        tfb = b3._fiche(f"TFP{numero:02d}", {"moniteur": p["moniteur"], "loi_predictive": p["loi_fausse"],
                                             "etiquette": "faux planté : même forme sur le trait de bruit"}, "fausse", d, k_de,
                        banque, f"L'issue du moniteur {p['moniteur']} suit une loi à seuil sur le trait de bruit (n° {numero})")
        tff = b3._fiche(f"TFN{numero:02d}", {"moniteur": nul, "loi_predictive": p["loi_vraie"],
                                             "etiquette": "faux : loi vraie, issues permutées"}, "fausse", d, k_de, banque,
                        f"L'issue du moniteur {nul} suit une loi à seuil sur deux traits réels (n° {numero})")
        temoins.append({"force": p["force"], "i": p["i"], "j": p["j"],
                        "fiches": {cle: Fiche.depuis_dict(x).valider() for cle, x in (("tv", tv), ("tfb", tfb), ("tff", tff))}})
    return banque, temoins, {"remise": bool(remise), "effectifs": effectifs}


# --- le juge, tel qu'il est -------------------------------------------------------------------------------------
def config_du_juge(taille_plan=TAILLE_PLAN):
    """Réglages de demo_couche1_proposeur_v7.py (bras « référence » : le chemin des témoins est le même dans les trois)."""
    return ConfigGeneration(selection="pari", juge="v1", nul_filles="v2", urne=False, graine=GRAINE_DU_JUGE,
                            taille_plan=taille_plan, taille_plan_filles=120, instants_filles=6, part_calibrage=12,
                            budget_generation_usd=200.0, concurrence=4, multiplicite="e-bh", temoins_sans_agent=True,
                            nul_archive=True, propositions_par_generation=0, exploration_developpement=False,
                            politique_redite="refus").valider()


def juger_temoin(monde, fiche, config):
    """Chemin d'un témoin sans agent à la génération 0 : Generation.geler (nul informé ; aucun membre d'archive pour un
    témoin), preparer_engagement, mesures déposées par le noyau, Generation._juger_pari (héritage nul sous « refus »)."""
    graine_noyau = graine_derivee(config.graine, "noyau", 0)  # Generation.__init__, noyau_secret faux, génération 0
    supplementaires = list(monde.membres_informes(fiche))
    gele = preparer_engagement(fiche, config, None, reservoir=monde.reservoir(fiche, 0),
                               membres_supplementaires=supplementaires or None, moniteur=monde.moniteur_de(fiche))
    mesures = monde.mesures(fiche.enonce, gele, graine_noyau, 0)
    if gele.engagement.get("instants_lecture"):
        return nf.evaluer_v2(gele, mesures, graine_noyau=graine_noyau)
    return sp.evaluer(gele, mesures, graine_noyau=graine_noyau)


def lire_verdicts(evs, ms):
    """Trois lectures d'une même génération : par fiche (évaluateur seul), puis e-BH (`appliquer_multiplicite`) à chaque m,
    le témoin vrai hors famille, les deux témoins faux dans la famille (les m − 2 autres fiches à e = 0)."""
    sortie = {"par_fiche": {cle: bool(ev["promue"]) for cle, ev in evs.items()}}
    for m in ms:
        issues = {cle: {"verdict_final": "survit" if ev["promue"] else "eliminee", "motif": "", "pari": dict(ev),
                        "temoin": "vraie" if cle == "tv" else "fausse"} for cle, ev in evs.items()}
        appliquer_multiplicite(issues, ALPHA, m_fixe=m)
        sortie[f"e_bh_m{m}"] = {cle: issues[cle]["verdict_final"] == "survit" for cle in issues}
    return sortie


def executer_unite(arguments):
    graine, n_epreuve, r, forces, ms, variante = arguments
    debut = time.time()
    graines = graines_de(graine, n_epreuve, r)
    banque, temoins, info = banque_de_repetition(structure_reelle(), n_epreuve, forces, graines)
    plans = {"gele": config_du_juge()}
    if variante and n_epreuve > TAILLE_PLAN:
        plans["plan_N"] = config_du_juge(n_epreuve)
    sortie = {"N": n_epreuve, "r": r, "graine_plantation": graines["plantation"], "remise": info["remise"],
              "calibrage": info["effectifs"]["calibrage"], "resultats": []}
    with tempfile.TemporaryDirectory(prefix="puissance-v1-") as tmp:
        chemin = os.path.join(tmp, "banque.json")
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(banque, f)
        monde = MondeBanque(chemin, GRAINE_DU_JUGE, nul_informe=True)
        for t in temoins:
            for nom_plan, config in plans.items():
                evs = {cle: juger_temoin(monde, fiche, config) for cle, fiche in t["fiches"].items()}
                sortie["resultats"].append({
                    "force": t["force"], "plan": nom_plan, "i": t["i"], "j": t["j"],
                    "n_plan": evs["tv"]["nombre_tirages"],
                    "log_w_max": {cle: round(ev["log_richesse_max"], 4) for cle, ev in evs.items()},
                    "log_w_final": {cle: round(ev["log_richesse_finale"], 4) for cle, ev in evs.items()},
                    "verdicts": lire_verdicts(evs, ms)})
    sortie["duree_s"] = round(time.time() - debut, 3)
    return sortie


# --- agrégation ----------------------------------------------------------------------------------------------------
def _log_binom(n, k, p):
    if p <= 0.0:
        return 0.0 if k == 0 else -math.inf
    if p >= 1.0:
        return 0.0 if k == n else -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p)


def _cdf(k, n, p):
    return min(1.0, sum(math.exp(_log_binom(n, i, p)) for i in range(0, k + 1)))


def clopper_pearson(k, n, niveau=0.95):
    """Intervalle binomial exact (Clopper-Pearson), bilatéral, par bissection sur la fonction de répartition."""
    a = (1.0 - niveau) / 2.0

    def bissection(f, cible):
        bas, haut = 0.0, 1.0
        for _ in range(100):
            milieu = (bas + haut) / 2
            if f(milieu) > cible:
                bas = milieu
            else:
                haut = milieu
        return (bas + haut) / 2

    basse = 0.0 if k == 0 else bissection(lambda p: 1.0 - (1.0 - _cdf(k - 1, n, p)), 1.0 - a)  # P(X ≥ k) = a
    haute = 1.0 if k == n else bissection(lambda p: _cdf(k, n, p), a)  # P(X ≤ k) = a
    return [round(basse, 4), round(haute, 4)]


def _quantile(valeurs, q):
    v = sorted(valeurs)
    return round(v[min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))], 3)


def agreger(unites, forces, episodes, lectures, variante):
    cellules = []
    plans = ["gele"] + (["plan_N"] if variante else [])
    for plan in plans:
        for f in forces:
            for n in episodes:
                if plan == "plan_N" and n <= TAILLE_PLAN:
                    continue
                lignes = [x for u in unites if u["N"] == n for x in u["resultats"] if x["force"] == f and x["plan"] == plan]
                if not lignes:
                    continue
                R = len(lignes)
                cellule = {"plan": plan, "force": f, "N": n, "repetitions": R,
                           "n_plan": sorted({x["n_plan"] for x in lignes}),
                           "remise": any(u["remise"] for u in unites if u["N"] == n),
                           "log_w_max_vrais": {"q10": _quantile([x["log_w_max"]["tv"] for x in lignes], 0.10),
                                               "mediane": _quantile([x["log_w_max"]["tv"] for x in lignes], 0.50),
                                               "q90": _quantile([x["log_w_max"]["tv"] for x in lignes], 0.90)},
                           "log_w_max_faux_q99": {cle: _quantile([x["log_w_max"][cle] for x in lignes], 0.99)
                                                  for cle in ("tfb", "tff")},
                           "lectures": {}}
                for lec in lectures:
                    bloc = {}
                    for cle, nom in (("tv", "vrais"), ("tfb", "faux_bruit"), ("tff", "faux_meme_forme")):
                        k = sum(bool(x["verdicts"][lec][cle]) for x in lignes)
                        bloc[nom] = {"promus": k, "taux": round(k / R, 4), "ic95_exact": clopper_pearson(k, R)}
                    kf = bloc["faux_bruit"]["promus"] + bloc["faux_meme_forme"]["promus"]
                    bloc["faux_ensemble"] = {"promus": kf, "jugés": 2 * R, "taux": round(kf / (2 * R), 4),
                                             "ic95_exact": clopper_pearson(kf, 2 * R)}
                    cellule["lectures"][lec] = bloc
                cellules.append(cellule)
    return cellules


def n_minimal(cellules, plan, lecture, forces, episodes, cible=PUISSANCE_CIBLE):
    """Par force : plus petit N de la grille où le taux atteint la cible, et N interpolé linéairement entre ce point et le
    précédent (interpolation linéaire, dite comme telle) ; « non atteint » si aucun point de la grille ne l'atteint."""
    sortie = {}
    for f in forces:
        points = [(c["N"], c["lectures"][lecture]["vrais"]["taux"]) for c in cellules
                  if c["plan"] == plan and c["force"] == f]
        if plan == "plan_N":  # la variante ne diffère du juge gelé qu'au-delà de 120 : on reprend ses points ≤ 120
            points = [(c["N"], c["lectures"][lecture]["vrais"]["taux"]) for c in cellules
                      if c["plan"] == "gele" and c["force"] == f and c["N"] <= TAILLE_PLAN] + points
        points.sort()
        premier = next((i for i, (_, p) in enumerate(points) if p >= cible), None)
        if premier is None:
            sortie[str(f)] = {"atteint": False, "N_interpole": None, "mention": f"non atteint sur la grille (N ≤ {points[-1][0]})"}
            continue
        retombe = any(p < cible for _, p in points[premier + 1:])
        if premier == 0:
            sortie[str(f)] = {"atteint": True, "N_interpole": None, "N_grille": points[0][0],
                              "mention": f"atteint dès le premier point de la grille (N ≤ {points[0][0]})", "non_monotone": retombe}
            continue
        (n0, p0), (n1, p1) = points[premier - 1], points[premier]
        n_star = n0 + (cible - p0) * (n1 - n0) / (p1 - p0)
        sortie[str(f)] = {"atteint": True, "N_interpole": round(n_star, 1), "entre": [n0, n1], "taux_aux_bornes": [p0, p1],
                          "mention": "interpolation linéaire entre deux points de la grille", "non_monotone": retombe}
    return sortie


def lire_predictions(cellules, lectures, forces, episodes):
    def taux(plan, lecture, f, n, quoi="vrais"):
        c = next((c for c in cellules if c["plan"] == plan and c["force"] == f and c["N"] == n), None)
        return None if c is None else c["lectures"][lecture][quoi]
    lp = f"e_bh_m{M_PRINCIPAL}"
    p1 = LECTURE_FIXEE["P1"]
    t1 = taux("gele", lp, p1["force"], p1["episodes"])
    P1 = {"cellule": {"force": p1["force"], "N": p1["episodes"]}, "observe": t1,
          "tenu": None if t1 is None else t1["taux"] >= p1["seuil_minimal"]}
    p2 = LECTURE_FIXEE["P2"]
    c2 = [{"force": f, "N": n, "taux": taux("gele", lp, f, n)["taux"]} for f in forces for n in episodes
          if f <= p2["force_maximale"] and n <= p2["episodes_maximal"] and taux("gele", lp, f, n) is not None]
    P2 = {"cellules": c2, "tenu": None if not c2 else all(x["taux"] < p2["seuil_strict"] for x in c2),
          "cellules_en_defaut": [x for x in c2 if x["taux"] >= p2["seuil_strict"]]}
    seuil3 = LECTURE_FIXEE["P3"]["seuil_maximal"]
    pire, defauts = None, []
    for c in cellules:
        if c["plan"] != "gele":
            continue
        for lec in lectures:
            for quoi in ("faux_bruit", "faux_meme_forme"):
                t = c["lectures"][lec][quoi]
                entree = {"force": c["force"], "N": c["N"], "lecture": lec, "sorte": quoi, "taux": t["taux"],
                          "promus": t["promus"], "ic95_exact": t["ic95_exact"]}
                if pire is None or t["taux"] > pire["taux"]:
                    pire = entree
                if t["taux"] > seuil3:
                    defauts.append(entree)
    P3 = {"pire_cellule": pire, "cellules_en_defaut": defauts, "tenu": not defauts,
          "borne_haute_ic95_la_plus_haute": max((c["lectures"][lec][q]["ic95_exact"][1] for c in cellules if c["plan"] == "gele"
                                                 for lec in lectures for q in ("faux_bruit", "faux_meme_forme")), default=None)}
    variante_faux = [{"force": c["force"], "N": c["N"], "lecture": lec, "sorte": q, "taux": c["lectures"][lec][q]["taux"]}
                     for c in cellules if c["plan"] == "plan_N" for lec in lectures for q in ("faux_bruit", "faux_meme_forme")
                     if c["lectures"][lec][q]["taux"] > seuil3]
    L4 = {}
    for f in forces:
        a, b = taux("gele", lp, f, 120), taux("gele", lp, f, max(episodes))
        v = taux("plan_N", lp, f, max(episodes))
        L4[str(f)] = {"gele_N120": None if a is None else a["taux"], f"gele_N{max(episodes)}": None if b is None else b["taux"],
                      f"plan_N_N{max(episodes)}": None if v is None else v["taux"]}
    return {"P1": P1, "P2": P2, "P3": P3, "P3_variante_lue_cellules_au_dessus_du_seuil": variante_faux, "L4": L4}


# --- Markdown (tous les chiffres viennent du JSON) -----------------------------------------------------------------
def _fr(x, chiffres=2):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "oui" if x else "non"
    if isinstance(x, int):
        return str(x)
    return f"{x:.{chiffres}f}".replace(".", ",")


def _tenu(v):
    return "**non lisible**" if v is None else ("**tenu**" if v else "**non tenu**")


def markdown(r):
    reg, lp = r["reglages"], f"e_bh_m{r['reglages']['m_principal']}"
    forces, episodes = reg["forces"], reg["episodes"]
    noms_lectures = {"par_fiche": "par fiche (log W ≥ log(1/α))", lp: f"e-BH, m = {reg['m_principal']} (principale)",
                     f"e_bh_m{reg['m_generation_0']}": f"e-BH, m = {reg['m_generation_0']}"}
    seuils = {k: _fr(v, 2) for k, v in r["seuils_log"].items()}
    L = []
    L.append(f"# Puissance du juge sur la banque réelle — v1 ({r['date_utc']})\n")
    L.append("## Lecture fixée avant l'exécution\n")
    L.append(f"Écrite : {r['lecture_fixee']['ecrite']}. Lecture principale : {r['lecture_fixee']['lecture_principale']}.\n")
    for p in ("P1", "P2", "P3", "L4"):
        L.append(f"- **{p}** : {r['lecture_fixee'][p]['texte']}.")
    L.append("")
    L.append("## Ce qu'on mesure\n")
    L.append(f"Juge : réglages de `demo_couche1_proposeur_v7.py` (juge v1 sans urne, nul informé, nul d'archive — sans effet "
             f"sur un témoin —, règle e-BH, α = {_fr(reg['alpha'])}, taille_plan = {reg['taille_plan']}). Seuils en log W : "
             f"par fiche {seuils['par_fiche']} ; e-BH m = {reg['m_principal']} : {seuils[lp]} ; "
             f"e-BH m = {reg['m_generation_0']} : {seuils['e_bh_m' + str(reg['m_generation_0'])]}. "
             f"Banque : structure de `banque-t05-v2.json` ({r['banque_reelle']['episodes']} épisodes, "
             f"{r['banque_reelle']['taches']} tâches) ; N/2 tâches d'épreuve, N/4 de calibrage ; tirage "
             f"{r['banque_reelle']['regle_de_tirage']}. Répétitions par cellule : {reg['repetitions']} ; durée "
             f"{_fr(r['duree_s'], 1)} s sur {reg['processus']} processus ({r['environnement']['coeurs']} cœurs).\n")
    L.append(f"## Puissance — lecture principale (e-BH, m = {reg['m_principal']}), juge gelé\n")
    L.append("Taux de promotion des témoins vrais [intervalle exact à 95 %] ; N = épisodes d'épreuve ; plan = min(N, "
             f"{reg['taille_plan']}).\n")
    L.append("| force | " + " | ".join(f"N = {n}" + (" (remise)" if r["remise_par_N"][str(n)] else "") for n in episodes) + " |")
    L.append("|---|" + "---|" * len(episodes))
    cel = {(c["plan"], c["force"], c["N"]): c for c in r["cellules"]}
    for f in forces:
        cases = []
        for n in episodes:
            v = cel[("gele", f, n)]["lectures"][lp]["vrais"]
            cases.append(f"{_fr(v['taux'])} [{_fr(v['ic95_exact'][0])} ; {_fr(v['ic95_exact'][1])}]")
        L.append(f"| {_fr(f, 1)} | " + " | ".join(cases) + " |")
    L.append("")
    for lec in [k for k in r["lectures"] if k != lp]:
        L.append(f"### Autre lecture : {noms_lectures[lec]}, juge gelé\n")
        L.append("| force | " + " | ".join(f"N = {n}" for n in episodes) + " |")
        L.append("|---|" + "---|" * len(episodes))
        for f in forces:
            L.append(f"| {_fr(f, 1)} | " + " | ".join(_fr(cel[("gele", f, n)]["lectures"][lec]["vrais"]["taux"]) for n in episodes) + " |")
        L.append("")
    L.append("### Richesse des témoins vrais : log W maximal, médiane [décile 1 ; décile 9], juge gelé\n")
    L.append("| force | " + " | ".join(f"N = {n}" for n in episodes) + " |")
    L.append("|---|" + "---|" * len(episodes))
    for f in forces:
        cases = []
        for n in episodes:
            q = cel[("gele", f, n)]["log_w_max_vrais"]
            cases.append(f"{_fr(q['mediane'], 1)} [{_fr(q['q10'], 1)} ; {_fr(q['q90'], 1)}]")
        L.append(f"| {_fr(f, 1)} | " + " | ".join(cases) + " |")
    L.append("")
    grands = [n for n in episodes if n > reg["taille_plan"]]
    if r["reglages"]["variante"] and grands:
        L.append(f"## Variante hors juge gelé : taille_plan = N (lecture principale)\n")
        L.append("| force | " + " | ".join(f"N = {n}" for n in grands) + " |")
        L.append("|---|" + "---|" * len(grands))
        for f in forces:
            cases = []
            for n in grands:
                v = cel[("plan_N", f, n)]["lectures"][lp]["vrais"]
                cases.append(f"{_fr(v['taux'])} [{_fr(v['ic95_exact'][0])} ; {_fr(v['ic95_exact'][1])}]")
            L.append(f"| {_fr(f, 1)} | " + " | ".join(cases) + " |")
        L.append("")
    L.append("## Témoins faux (juge gelé)\n")
    L.append("Promus sur jugés (bruit + même forme permutée), par lecture ; borne haute exacte à 95 % de la cellule.\n")
    L.append("| force | N | " + " | ".join(noms_lectures[k] for k in r["lectures"]) + " |")
    L.append("|---|---|" + "---|" * len(r["lectures"]))
    for f in forces:
        for n in episodes:
            c = cel[("gele", f, n)]
            cases = [f"{c['lectures'][k]['faux_ensemble']['promus']}/{c['lectures'][k]['faux_ensemble']['jugés']} "
                     f"(≤ {_fr(c['lectures'][k]['faux_ensemble']['ic95_exact'][1], 3)})" for k in r["lectures"]]
            L.append(f"| {_fr(f, 1)} | {n} | " + " | ".join(cases) + " |")
    L.append("")
    L.append(f"## N minimal pour une puissance de {_fr(reg['puissance_cible'], 1)} (interpolation linéaire entre points de la grille)\n")
    L.append("| force | juge gelé (lecture principale) | variante taille_plan = N |")
    L.append("|---|---|---|")
    for f in forces:
        cases = []
        for plan in ("gele", "plan_N"):
            x = r["n_minimal"].get(plan, {}).get(str(f))
            if x is None:
                cases.append("—")
            elif x.get("N_interpole") is not None:
                cases.append(f"≈ {_fr(x['N_interpole'], 0)} (entre {x['entre'][0]} et {x['entre'][1]})"
                             + (" ; retombe plus loin" if x.get("non_monotone") else ""))
            else:
                cases.append(x["mention"])
        L.append(f"| {_fr(f, 1)} | " + " | ".join(cases) + " |")
    L.append("")
    lec = r["lecture"]
    L.append("## Ce qui a tenu\n")
    p1 = lec["P1"]
    o1 = p1["observe"]
    L.append(f"- **P1** {_tenu(p1['tenu'])} : force {_fr(p1['cellule']['force'], 1)}, N = {p1['cellule']['N']} : taux "
             + (f"{_fr(o1['taux'])} [{_fr(o1['ic95_exact'][0])} ; {_fr(o1['ic95_exact'][1])}]" if o1 else "— (cellule hors grille)")
             + f" (seuil ≥ {_fr(r['lecture_fixee']['P1']['seuil_minimal'], 1)}).")
    p2 = lec["P2"]
    detail2 = ", ".join(f"{_fr(x['force'], 1)} × {x['N']} → {_fr(x['taux'])}" for x in p2["cellules"]) or "aucune cellule"
    L.append(f"- **P2** {_tenu(p2['tenu'])} : {detail2} (seuil < {_fr(r['lecture_fixee']['P2']['seuil_strict'], 1)}).")
    p3 = lec["P3"]
    pire = p3["pire_cellule"]
    L.append(f"- **P3** {_tenu(p3['tenu'])} : taux de faux le plus haut {_fr(pire['taux'], 3)} (force {_fr(pire['force'], 1)}, "
             f"N = {pire['N']}, {noms_lectures[pire['lecture']]}, {pire['sorte']}) ; plus haute borne exacte à 95 % "
             f"(par sorte de témoin faux, {reg['repetitions']} jugés par cellule) : "
             f"{_fr(p3['borne_haute_ic95_la_plus_haute'], 3)} ; cellules au-dessus du seuil : {len(p3['cellules_en_defaut'])}. "
             f"Variante (lue) : {len(lec['P3_variante_lue_cellules_au_dessus_du_seuil'])} cellule(s) au-dessus du seuil.")
    grand = str(max(episodes))
    detail4 = " ; ".join(f"force {_fr(float(f), 1)} : {_fr(v['gele_N120'])} → {_fr(v['gele_N' + grand])} (gelé), "
                         f"{_fr(v['plan_N_N' + grand])} (taille_plan = N)" for f, v in lec["L4"].items())
    L.append(f"- **L4** (lue) : de N = 120 à N = {grand}, {detail4}.")
    L.append("")
    L.append("## Réserves\n")
    for x in r["reserves"]:
        L.append(f"- {x}")
    L.append("")
    L.append(f"Fichiers : `{r['fichiers']['json']}` (chiffres), ce Markdown (rendu du JSON). Script : "
             f"`demonstrations/puissance_juge_banque_v1.py` (sha256 {r['empreintes']['script'][:12]}…).\n")
    return "\n".join(L)


def reserves(r):
    reg, br = r["reglages"], r["banque_reelle"]
    return [
        f"« Force » = coefficient a de `planter` (v3) : logit ±a·z_i sur les issues 0 et 2 d'un moniteur à 3 issues "
        f"(issue 1 à 0), signe inversé selon le signe d'un autre trait z_j ; z centrés réduits. C'est une loi **non "
        f"linéaire** que le nul informé (softmax linéaire ajustée sur le calibrage) ne capture pas ; un effet linéaire de même "
        f"taille serait en partie absorbé par le nul informé : la courbe est une borne haute pour un tel effet.",
        "Le témoin vrai engage **la loi exacte du monde** (témoin oracle) : la puissance mesurée est celle d'une fiche "
        "parfaitement spécifiée ; une fiche réelle (forme, traits, coefficients approchés) en a moins.",
        f"Les moniteurs plantés portent une issue sur **toutes** les instances ; les moniteurs réels de la banque v2 n'en "
        f"portent que sur une partie (de {br['instances_par_moniteur_reel'][0]} à {br['instances_par_moniteur_reel'][1]} des "
        f"{br['episodes']} épisodes) et ont 2 ou 3 issues à coupes déséquilibrées : N épisodes réels donnent moins d'instances "
        f"jugées par moniteur que N ici.",
        f"La banque réelle n'a que {br['parties'].get('epreuve')} épisodes d'épreuve ({br['taches']} tâches au total) : "
        f"toutes les cellules N où 3N/4 tâches dépassent {br['taches']} sont tirées **avec remise** (mêmes traits répétés, "
        f"issues plantées indépendantes). Avec un plan plafonné à {reg['taille_plan']}, le sélecteur par divergence prend les "
        f"instances les plus extrêmes : au-delà de N = {reg['taille_plan']}, il choisit des copies des mêmes épisodes réels "
        f"extrêmes ; de vrais épisodes neufs auraient des extrêmes plus extrêmes.",
        f"Juge gelé : taille_plan = {reg['taille_plan']} ; au-delà, N n'agit que sur le choix des {reg['taille_plan']} "
        f"instances, pas sur leur nombre (la variante taille_plan = N dit ce que donnerait un plan qui grandit).",
        f"Le seuil effectif d'un témoin vrai sous e-BH est log(m/α), pas log(1/α) ≈ {_fr(r['seuils_log']['par_fiche'], 2)} : "
        f"{_fr(r['seuils_log']['e_bh_m' + str(reg['m_principal'])], 2)} à m = {reg['m_principal']}, "
        f"{_fr(r['seuils_log']['e_bh_m' + str(reg['m_generation_0'])], 2)} à m = {reg['m_generation_0']} ; la puissance "
        f"dépend donc de la taille de la génération, que ce banc ne tire pas (deux valeurs lues).",
        "Famille e-BH reconstituée : un témoin vrai (hors famille) et deux témoins faux, les m − 2 autres fiches à e = 0. "
        "C'est exact tant que les fiches réelles ont log W < log(1/α) (aucune promue dans la démo) ; des fiches réelles "
        "fortes abaisseraient le seuil des faux (k* plus grand).",
        f"Les {len(reg['forces'])} forces d'une répétition partagent la même banque (mêmes traits, issues indépendantes par "
        f"moniteur) : les cellules d'une même ligne N sont corrélées entre forces, pas entre répétitions.",
        "Le plan est trié par divergence ; les ex aequo (le trait « actions_valides » est un compte entier) sont départagés "
        "par le mélange du réservoir, dont la graine est l'empreinte de la fiche : renommer un témoin peut changer sa richesse "
        "maximale. Vérifié hors banc sur la couche 1 bis v2 : le chemin du témoin de ce script redonne exactement les log W "
        "du journal quand la fiche porte les noms du pôle, et s'en écarte un peu sous un autre nom.",
        "Banc exploratoire, sans préenregistrement scellé ni contre-lecture : rien d'opposable ; la lecture fixée en tête "
        "est datée dans le script, pas scellée avant la course.",
    ]


def mesurer(graine, forces, ms, processus):
    print(f"cœurs : {os.cpu_count()} ; processus prévus : {processus}")
    for n in (60, 144, 600):
        for variante in (False, True):
            if variante and n <= TAILLE_PLAN:
                continue
            debut = time.time()
            u = [executer_unite((graine + 999, n, r, forces, ms, variante)) for r in range(2)]
            print(f"N = {n:4d}, variante {variante!s:5} : {(time.time() - debut) / 2:.2f} s par répétition "
                  f"(toutes forces) ; plan {sorted({x['n_plan'] for x in u[0]['resultats']})}")
    return 0


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("dossier", nargs="?")
    a.add_argument("--repetitions", type=int, default=100)
    a.add_argument("--processus", type=int, default=min(4, os.cpu_count() or 1))
    a.add_argument("--forces", default=",".join(str(f) for f in FORCES))
    a.add_argument("--episodes", default=",".join(str(n) for n in EPISODES))
    a.add_argument("--graine", type=int, default=20261101)
    a.add_argument("--sans-variante", action="store_true")
    a.add_argument("--mesurer", action="store_true")
    args = a.parse_args(argv)
    forces = [float(x) for x in args.forces.split(",")]
    episodes = sorted(int(x) for x in args.episodes.split(","))
    population, temoins_reels = charger_fiches(POPULATION_REELLE), charger_fiches(TEMOINS_REELS)
    faux_par_generation = min(sum(t.temoin == "vraie" for t in temoins_reels), sum(t.temoin == "fausse" for t in temoins_reels))
    m_generation_0 = len(population) + faux_par_generation  # démo, génération 0 : population + témoins faux (m_fixe)
    ms = sorted({M_PRINCIPAL, m_generation_0})
    if args.mesurer:
        return mesurer(args.graine, forces, ms, args.processus)
    if not args.dossier:
        a.error("DOSSIER_NEUF requis (sauf --mesurer)")
    if args.repetitions < 50:
        a.error("au moins 50 répétitions par cellule")
    if os.path.exists(args.dossier) and os.listdir(args.dossier):
        raise FileExistsError(args.dossier)
    os.makedirs(args.dossier, exist_ok=True)
    chemin_json = os.path.join(args.dossier, f"{NOM}.json")
    chemin_md = os.path.join(args.dossier, f"{NOM}.md")
    for c in (chemin_json, chemin_md):
        if os.path.exists(c):
            raise FileExistsError(c)
    variante = not args.sans_variante
    debut, quand = time.time(), time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    taches = [(args.graine, n, r, forces, ms, variante) for n in episodes for r in range(args.repetitions)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.processus) as pool:
        unites = list(pool.map(executer_unite, taches, chunksize=4))
    duree = round(time.time() - debut, 1)
    lectures = ["par_fiche"] + [f"e_bh_m{m}" for m in ms]
    cellules = agreger(unites, forces, episodes, lectures, variante)
    s = structure_reelle()
    with open(BANQUE_REELLE, encoding="utf-8") as f:
        brute = json.load(f)
    couverture = [m["instances"] for m in brute["moniteurs"].values()]
    with open(os.path.abspath(__file__), "rb") as f:
        empreinte_script = hashlib.sha256(f.read()).hexdigest()
    r = {
        "nom": NOM, "date_utc": quand, "duree_s": duree, "lecture_fixee": LECTURE_FIXEE,
        "reglages": {"forces": forces, "episodes": episodes, "repetitions": args.repetitions, "processus": args.processus,
                     "graine": args.graine, "graine_du_juge": GRAINE_DU_JUGE, "alpha": ALPHA, "taille_plan": TAILLE_PLAN,
                     "m_principal": M_PRINCIPAL, "m_generation_0": m_generation_0, "puissance_cible": PUISSANCE_CIBLE,
                     "variante": variante, "config_du_juge": dataclasses.asdict(config_du_juge()),
                     "provenance_m": {str(M_PRINCIPAL): "m des témoins plantés de la couche 1 bis v2 (course e2) ; générations "
                                                        "1 à 3 de la démo sur la banque réelle : 15 à 17",
                                      str(m_generation_0): f"génération 0 de la démo : {len(population)} fiches de la population "
                                                           f"v2 + {faux_par_generation} témoins faux par génération"}},
        "seuils_log": {"par_fiche": math.log(1 / ALPHA), **{f"e_bh_m{m}": math.log(m / ALPHA) for m in ms}},
        "lectures": lectures,
        "banque_reelle": {"chemin": os.path.relpath(BANQUE_REELLE, RACINE), "sha256": sha256_fichier(BANQUE_REELLE),
                          "episodes": s["episodes"], "taches": len(s["taches"]), "parties": s["parties"],
                          "moniteurs_reels": s["moniteurs_reels"], "instances_par_moniteur_reel": [min(couverture), max(couverture)],
                          "regle_de_tirage": f"par tâche, sans remise si 3N/4 ≤ {len(s['taches'])}, avec remise au-delà"},
        "remise_par_N": {str(n): any(u["remise"] for u in unites if u["N"] == n) for n in episodes},
        "calibrage_par_N": {str(n): sorted({u["calibrage"] for u in unites if u["N"] == n}) for n in episodes},
        "cellules": cellules,
        "n_minimal": {plan: n_minimal(cellules, plan, f"e_bh_m{M_PRINCIPAL}", forces, episodes)
                      for plan in (["gele", "plan_N"] if variante else ["gele"])},
        "graines": {"regle": "numpy.random.SeedSequence(graine, spawn_key=(N, r)) ; trois fils : banque (tirage des tâches et "
                             "partition), plantation (entier passé à construire_banque_t05_v3.planter), permutation (faux "
                             "« même forme »)",
                    "plantation_par_N": {str(n): [u["graine_plantation"] for u in sorted(unites, key=lambda u: u["r"]) if u["N"] == n]
                                         for n in episodes}},
        "duree_par_unite_s": {str(n): round(sum(u["duree_s"] for u in unites if u["N"] == n) / max(1, sum(1 for u in unites if u["N"] == n)), 3)
                              for n in episodes},
        "environnement": {"python": platform.python_version(), "numpy": np.__version__, "coeurs": os.cpu_count(),
                          "plateforme": sys.platform},
        "empreintes": {"script": empreinte_script,
                       "construire_banque_t05_v3": sha256_fichier(os.path.join(EXEMPLES, "construire_banque_t05_v3.py")),
                       "demo_couche1_proposeur_v7": sha256_fichier(os.path.join(ICI, "demo_couche1_proposeur_v7.py")),
                       "population_v2": sha256_fichier(POPULATION_REELLE), "temoins_v2": sha256_fichier(TEMOINS_REELS),
                       **{f"pole/{n}": sha256_fichier(os.path.join(RACINE, "pole", n))
                          for n in ("selection_pari.py", "monde_banque.py", "cycle.py", "nul_filles_v2.py", "engagement_apparie.py")}},
        "fichiers": {"json": f"{NOM}.json", "md": f"{NOM}.md"},
    }
    r["lecture"] = lire_predictions(cellules, lectures, forces, episodes)
    r["reserves"] = reserves(r)
    with open(chemin_json, "x", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False, indent=1, sort_keys=True, allow_nan=False) + "\n")
    with open(chemin_json, encoding="utf-8") as f:  # le Markdown est rendu depuis le JSON écrit, rien d'autre
        relu = json.load(f)
    with open(chemin_md, "x", encoding="utf-8") as f:
        f.write(markdown(relu))
    print(json.dumps({"duree_s": duree, "P1": r["lecture"]["P1"]["tenu"], "P2": r["lecture"]["P2"]["tenu"],
                      "P3": r["lecture"]["P3"]["tenu"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
