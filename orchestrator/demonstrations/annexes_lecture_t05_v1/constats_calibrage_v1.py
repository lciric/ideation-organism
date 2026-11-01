"""Constats du calibrage cités par le préenregistrement de lecture du lot T0.5 à graines neuves (v1) — calcul à part,
sur les 288 épisodes déjà courus seulement (aucune donnée du lot neuf).

1. Table de rangs de la règle de L3 (`proposeur_scripte_banque_v1.proposer`, tout en calibrage) : témoins vrais, plus
   grand |ρ|, et les cinq couples qui étaient témoins vrais dans la banque v2 (40 épisodes de calibrage).
2. Couverture de chaque moniteur réel (instances de première passe sur 288).
3. Information par épisode de la loi « connue » (régression multinomiale à crête du juge, `ajuster_softmax`, crête 1),
   gain moyen de score logarithmique contre la marginale d'ajustement, hors échantillon : (a) par tâche, deux plis,
   dix répétitions (graines 1000 à 1009, `random.Random`) ; (b) dans les mêmes tâches, l'épisode e0, e1 ou e2 tenu à
   l'écart tour à tour (proche de l'épreuve : graines neuves sur les mêmes tâches).

Usage : python3 -I -B demonstrations/annexes_lecture_t05_v1/constats_calibrage_v1.py CHEMIN/banque-e2.json
"""

import json
import math
import os
import random
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(os.path.dirname(ICI))
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.join(RACINE, "exemples"))
sys.path.insert(0, os.path.join(RACINE, "demonstrations"))

import lecture_t05_graines_neuves_v1 as lec  # noqa: E402
from pole import selection_pari as sp  # noqa: E402
from pole.monde_banque import ajuster_softmax  # noqa: E402

COUPLES_V2 = ("3B:BALANCE|log_jetons_total", "3B:RESULT_REASONING|jetons_par_action_ecart_type",
              "3B:RIGOR|actions_valides", "8B:COHERENCE|actions_valides", "8B:RIGOR|actions_valides")


def gain(loi, lignes, nom, marginale):
    s = 0.0
    for l in lignes:
        y = int(l["issues"][nom])
        s += math.log(max(1e-12, sp.proba(loi, {"z": l["z"], "g": l["g"]}, [], 0)[y])) - math.log(marginale[y])
    return s, len(lignes)


def marginale_de(lignes, nom, k):
    ys = [int(l["issues"][nom]) for l in lignes]
    return [(ys.count(c) + 0.5) / (len(ys) + 0.5 * k) for c in range(k)]


def principal(chemin):
    cal = lec.lire_calibrage(chemin, lec.sha256_fichier(chemin))
    _, rangs, resume = lec.temoins_de_calibrage(cal)
    sortie = {"calibrage_sha256": cal["empreinte"], "resume_rangs": resume,
              "couples_v2": {c: rangs[c.split("|")[0]][c.split("|")[1]] for c in COUPLES_V2},
              "couverture": {}, "information_connue": {}}
    inst = cal["instances"]
    taches = sorted({l["tache"] for l in inst})
    for nom, m in sorted(cal["moniteurs"].items()):
        k = m["nombre_issues"]
        porteurs = [l for l in inst if nom in l["issues"]]
        sortie["couverture"][nom] = {"instances": len(porteurs), "sur": len(inst), "taux": round(len(porteurs) / len(inst), 3),
                                     "issues": k}
        par_tache = []
        for rep in range(10):
            t = taches[:]
            random.Random(1000 + rep).shuffle(t)
            for pli in (set(t[0::2]), set(t[1::2])):
                test = [l for l in porteurs if l["tache"] in pli]
                appr = [l for l in porteurs if l["tache"] not in pli]
                loi = ajuster_softmax([l["z"] for l in appr], [int(l["issues"][nom]) for l in appr], k, 1.0)
                s, n = gain(loi, test, nom, marginale_de(appr, nom, k))
                par_tache.append(s / n)
        s_tot, n_tot = 0.0, 0
        for g in (0, 1, 2):
            test = [l for l in porteurs if l["g"] == g]
            appr = [l for l in porteurs if l["g"] != g]
            loi = ajuster_softmax([l["z"] for l in appr], [int(l["issues"][nom]) for l in appr], k, 1.0)
            s, n = gain(loi, test, nom, marginale_de(appr, nom, k))
            s_tot, n_tot = s_tot + s, n_tot + n
        sortie["information_connue"][nom] = {"par_tache_nat": round(sum(par_tache) / len(par_tache), 4),
                                             "meme_tache_episode_tenu_nat": round(s_tot / n_tot, 4)}
    print(json.dumps(sortie, ensure_ascii=False, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1]))
