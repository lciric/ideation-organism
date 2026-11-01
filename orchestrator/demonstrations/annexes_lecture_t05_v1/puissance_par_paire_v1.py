"""Puissance des témoins plantés **par paire de traits** (i : trait de la softmax, j : trait du seuil), sur les traits réels
du calibrage (288 épisodes déjà courus) — calcul à part, cité par le préenregistrement de lecture du lot T0.5 à graines
neuves (v1). Aucune donnée du lot neuf.

Banque de chaque répétition : calibrage = les 288 épisodes (traits réels) ; épreuve = des copies des mêmes 288 vecteurs de
traits (substitut des épisodes neufs, dont les traits ont la même loi), issues plantées tirées à neuf des deux côtés.
Loi plantée : celle de `construire_banque_t05_v3.planter` (si/sinon au seuil 0 sur z_j ; softmax ±a·z_i sur les issues 0
et 2, signes opposés dans les deux branches), paire (i, j) imposée, signe de a tiré. Juge : celui de la lecture (monde
informé, nul v8, famille T : témoin vrai hors famille au seuil log(19/α) = 5,94), bras plein (288) et gelé (120).
Graines : `numpy.random.SeedSequence(20261102, spawn_key=(i, j, indice de force, répétition))`.

Option `--episodes 0,1` : l'épreuve ne reprend que les vecteurs des épisodes e0 et e1 (192 instances : cas où les
notations descriptives des e2 manquent).

Usage : python3 -I -B demonstrations/annexes_lecture_t05_v1/puissance_par_paire_v1.py CHEMIN/banque-e2.json [--repetitions 30]
        [--episodes 0,1,2]
"""

import argparse
import itertools
import json
import os
import sys
import tempfile

import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(os.path.dirname(ICI))
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.join(RACINE, "exemples"))
sys.path.insert(0, os.path.join(RACINE, "demonstrations"))

import construire_banque_t05_v3 as b3  # noqa: E402
import lecture_t05_graines_neuves_v1 as lec  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole.fiche import Fiche  # noqa: E402

FORCES = (0.3, 0.5, 0.8)
M_T = 19


def loi_plantee(i, j, a, d=4, k=3):
    def branche(signe):
        poids = [[0.0] * d for _ in range(k)]
        poids[0][i], poids[2][i] = round(-signe * a, 6), round(signe * a, 6)
        return {"type": "softmax", "poids": poids, "biais": [0.0] * k}
    return {"type": "si_sinon", "condition": {"indice": j, "seuil": 0.0}, "si": branche(+1), "sinon": branche(-1)}


def unite(banque_cal, i, j, f_idx, r, tmp, episodes=(0, 1, 2)):
    ss = np.random.SeedSequence(20261102, spawn_key=(i, j, f_idx, r))
    rng = np.random.default_rng(ss)
    a = FORCES[f_idx] * (1 if rng.random() < 0.5 else -1)
    loi = loi_plantee(i, j, a)
    cal = [dict(l, issues={}) for l in banque_cal["instances"]]
    ep = [dict(l, identifiant="n/" + l["identifiant"], tache="n-" + l["tache"], partie="epreuve", issues={})
          for l in banque_cal["instances"] if l["g"] in episodes]
    for l in cal + ep:
        p = sp.proba(loi, {"z": l["z"], "g": l["g"]}, [], 0)
        l["issues"] = {"plante:x": int(rng.choice(3, p=np.asarray(p) / sum(p)))}
    banque = {"nom": "paire", "traits": banque_cal["traits"], "sous_populations": 3,
              "moniteurs": {"plante:x": {"juge": "plante", "rubrique": "plante", "coupes": None, "nombre_issues": 3,
                                         "instances": len(cal) + len(ep)}}, "instances": cal + ep}
    fiche = Fiche.depuis_dict(b3._fiche("TVP01", {"moniteur": "plante:x", "loi_predictive": loi, "etiquette": "vrai planté"},
                                        "vraie", 4, {"plante:x": 3}, banque, "loi plantée")).valider()
    chemin = lec._ecrire_banque(banque, tmp)
    v = lec.juger_famille(chemin, True, [fiche], M_T, len(ep))
    return {b: v[b]["TVP01"]["e_bh"] for b in ("plein", "gele")}


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("calibrage")
    a.add_argument("--repetitions", type=int, default=30)
    a.add_argument("--episodes", default="0,1,2")
    args = a.parse_args(argv)
    banque_cal = lec.lire_calibrage(args.calibrage, lec.sha256_fichier(args.calibrage))
    table = {}
    with tempfile.TemporaryDirectory() as tmp:
        for i, j in itertools.permutations(range(3), 2):
            for f_idx, f in enumerate(FORCES):
                episodes = tuple(int(x) for x in args.episodes.split(","))
                res = [unite(banque_cal, i, j, f_idx, r, tmp, episodes) for r in range(args.repetitions)]
                table[f"{banque_cal['traits'][i]}|{banque_cal['traits'][j]}|{f}"] = {
                    "plein": round(sum(x["plein"] for x in res) / len(res), 3),
                    "gele": round(sum(x["gele"] for x in res) / len(res), 3), "repetitions": len(res)}
                print(i, j, f, table[f"{banque_cal['traits'][i]}|{banque_cal['traits'][j]}|{f}"], flush=True)
    print(json.dumps({"calibrage_sha256": banque_cal["empreinte"], "m": M_T, "episodes": args.episodes, "table": table},
                     ensure_ascii=False, indent=1,
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
