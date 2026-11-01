"""Traduction de la « force » de planter (v3) en unités lisibles, sur les traits réels de la banque v2 (calcul à part)."""
import json, math, itertools, os, sys
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # orchestrator/
sys.path.insert(0, RACINE)
from pole import selection_pari as sp
b = json.load(open(os.path.join(RACINE, 'exemples', 'banque-t05-v2.json'), encoding='utf-8'))
Z = [l["z"] for l in b["instances"]]
reels = [i for i, n in enumerate(b["traits"]) if n != "bruit"]
def loi(i, j, a, d=4, k=3):
    def br(s):
        p = [[0.0]*d for _ in range(k)]; p[0][i], p[2][i] = -s*a, s*a
        return {"type": "softmax", "poids": p, "biais": [0.0]*k}
    return {"type": "si_sinon", "condition": {"indice": j, "seuil": 0.0}, "si": br(+1), "sinon": br(-1)}
print("force | écart P(issue 2) − P(issue 0) à |z_i| = 1 | information moyenne par épisode (nat), moyenne sur les 6 paires (i, j) [min ; max] | idem sur le tiers le plus divergent")
for a in (0.1, 0.2, 0.3, 0.5, 0.8):
    ecart = (math.exp(a) - math.exp(-a)) / (math.exp(a) + 1 + math.exp(-a))
    infos, infos_haut = [], []
    for i, j in itertools.permutations(reels, 2):
        L = loi(i, j, a)
        P = [sp.proba(L, {"z": z, "g": 0}, [], 0) for z in Z]
        pbar = [sum(p[c] for p in P)/len(P) for c in range(3)]
        kl = [sum(p[c]*math.log(p[c]/pbar[c]) for c in range(3)) for p in P]
        infos.append(sum(kl)/len(kl))
        haut = sorted(kl, reverse=True)[:len(kl)//3]
        infos_haut.append(sum(haut)/len(haut))
    m = sum(infos)/len(infos); mh = sum(infos_haut)/len(infos_haut)
    print(f"{a} | {ecart:.3f} | {m:.4f} [{min(infos):.4f} ; {max(infos):.4f}] | {mh:.4f}")
