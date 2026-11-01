"""Mondes tirés au hasard dans une grammaire **hors de l'espace de recherche du chercheur mécanique** (v7, version 8).

La démonstration sur la grammaire v1 (`generer_monde_grammaire_v1.py`) flattait le chercheur mécanique : il fouille
exactement les formes de cette grammaire (softmax, par sous-population, si/sinon au seuil 0, au plus deux traits). Ici,
quatre formes qu'il ne fouille pas, pour qu'un duel futur (proposeur à modèle contre mécanique) se joue sur un terrain où le
mécanique n'est pas chez lui :
- « seuil_decale » : s = a·z_i si z_j > τ, 0 sinon, avec |τ| tiré dans [0,6 ; 1,2] (le mécanique ne coupe qu'en 0) ;
- « trois_traits » : s = a·z_i·signe(z_j)·signe(z_k) (le mécanique s'arrête à deux traits) ;
- « quadratique » : s = a·(z_i² − 1) (non monotone ; aucune forme du gabarit ne l'écrit exactement) ;
- « produit » : s = a·z_i·z_j (interaction lisse ; idem).
Le témoin vrai d'un moniteur est la loi exacte quand le gabarit l'écrit (seuil décalé, trois traits), sinon la meilleure
approximation au gabarit que j'écris à la main (quadratique : V par si/sinon sur le signe de z_i ; produit : quatre
quadrants par si/sinon imbriqués), et c'est déclaré dans `verite`. Mêmes parties que la v1 (calibrage, développement,
épreuve). La grammaire reste écrite par moi (limite déclarée).
"""

import os
import random
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))
sys.path.insert(0, ICI)

from generer_monde_grammaire_v1 import _softmax_ordinal, fiches_de_temoins  # noqa: E402,F401
from pole.outils import graine_derivee  # noqa: E402

STRUCTURES = ("seuil_decale", "trois_traits", "quadratique", "produit")


def _score(structure, z, i, j, kk, a, tau):
    if structure == "seuil_decale":
        return a * z[i] if z[j] > tau else 0.0
    if structure == "trois_traits":
        return a * z[i] * (1 if z[j] > 0 else -1) * (1 if z[kk] > 0 else -1)
    if structure == "quadratique":
        return a * (z[i] * z[i] - 1.0)
    if structure == "produit":
        return a * z[i] * z[j]
    raise ValueError(structure)


def loi_monde(structure, i, j, kk, a, tau, k):
    """Loi exacte du monde, comme fonction (hors gabarit pour « quadratique » et « produit »)."""
    import math

    def proba(z):
        s = _score(structure, z, i, j, kk, a, tau)
        e = [math.exp((c - (k - 1) / 2) * s) for c in range(k)]
        tot = sum(e)
        return [x / tot for x in e]
    return proba


def temoin_au_gabarit(structure, i, j, kk, a, tau, d, k):
    """(loi au gabarit, exacte ?)."""
    if structure == "seuil_decale":
        return {"type": "si_sinon", "condition": {"indice": j, "seuil": round(tau, 6)},
                "si": _softmax_ordinal({i: a}, d, k), "sinon": _softmax_ordinal({}, d, k)}, True
    if structure == "trois_traits":
        plus, moins = _softmax_ordinal({i: a}, d, k), _softmax_ordinal({i: -a}, d, k)
        return {"type": "si_sinon", "condition": {"indice": j, "seuil": 0.0},
                "si": {"type": "si_sinon", "condition": {"indice": kk, "seuil": 0.0}, "si": plus, "sinon": moins},
                "sinon": {"type": "si_sinon", "condition": {"indice": kk, "seuil": 0.0}, "si": moins, "sinon": plus}}, True
    if structure == "quadratique":
        # V : s ≈ a·(|z_i|·1,6 − 1,3) par branche (approximation au gabarit de a·(z² − 1) sur |z| ≤ 2)
        def branche(signe):
            l = _softmax_ordinal({i: round(signe * 1.6 * a, 6)}, d, k, [round((c - (k - 1) / 2) * (-1.3 * a), 6) for c in range(k)])
            return l
        return {"type": "si_sinon", "condition": {"indice": i, "seuil": 0.0}, "si": branche(1), "sinon": branche(-1)}, False
    if structure == "produit":
        # quatre quadrants : signe(z_j)·a·z_i·0,8 (approximation de a·z_i·z_j par |z_j| ≈ 0,8)
        plus, moins = _softmax_ordinal({i: round(0.8 * a, 6)}, d, k), _softmax_ordinal({i: round(-0.8 * a, 6)}, d, k)
        return {"type": "si_sinon", "condition": {"indice": j, "seuil": 0.0}, "si": plus, "sinon": moins}, False
    raise ValueError(structure)


def generer_monde(graine, d=4, moniteurs=3, k=3, n=900, parts=(150, 300, 450), structures=None):
    """(banque, témoins, vérité), au format de la v1."""
    from pole import selection_pari as sp
    rng = random.Random(graine_derivee(graine, "monde-grammaire-v2"))
    noms = [f"M{m}" for m in range(moniteurs)]
    verite, temoins, lois = {}, [], {}
    for m, nom in enumerate(noms):
        structure = structures[m] if structures else rng.choice(STRUCTURES)
        i, j, kk = rng.sample(range(d), 3)
        a = rng.choice([-1, 1]) * rng.uniform(1.2, 2.0)
        tau = rng.choice([-1, 1]) * rng.uniform(0.6, 1.2)
        loi_t, exacte = temoin_au_gabarit(structure, i, j, kk, a, tau, d, k)
        bruit = [t for t in range(d) if t not in (i, j, kk)][0]
        lois[nom] = loi_monde(structure, i, j, kk, a, tau, k)
        verite[nom] = {"structure": structure, "i": i, "j": j, "k": kk, "a": round(a, 6), "tau": round(tau, 6),
                       "lineaire": False, "temoin_exact": exacte, "loi": loi_t, "trait_de_bruit": bruit}
        temoins.append({"identifiant": f"V-{nom}", "verite": "vraie", "moniteur": nom, "loi": loi_t,
                        "enonce": f"Témoin vrai : la loi du moniteur {nom} ({structure}, "
                                  f"{'exacte' if exacte else 'approchée au gabarit'})"})
        temoins.append({"identifiant": f"F-{nom}", "verite": "fausse", "moniteur": nom,
                        "loi": _softmax_ordinal({bruit: 1.5}, d, k),
                        "enonce": f"Témoin faux : l'issue du moniteur {nom} suivrait le trait {bruit}"})
    instances = []
    bornes = [parts[0], parts[0] + parts[1]]
    for r in range(n):
        z = [round(rng.gauss(0.0, 1.0), 6) for _ in range(d)]
        g = rng.randrange(2)
        issues = {nom: sp.tirer_categorie(rng, lois[nom](z)) for nom in noms}
        partie = "calibrage" if r < bornes[0] else ("developpement" if r < bornes[1] else "epreuve")
        instances.append({"identifiant": f"i{r:04d}", "z": z, "g": g, "issues": issues, "partie": partie})
    banque = {"nom": f"grammaire-v2-{graine}", "traits": [f"t{t}" for t in range(d)], "sous_populations": 2,
              "moniteurs": {nom: {"nombre_issues": k, "instances": n} for nom in noms}, "instances": instances,
              "origine": "monde tiré au hasard dans la grammaire v2 (exemples/generer_monde_grammaire_v2.py)"}
    return banque, temoins, verite
