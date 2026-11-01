"""Monde tiré au hasard dans une grammaire, sans modèle (v7, version 7) — pour arbitrer des proposeurs hors de ma lignée.

Synthèse du collisionneur « proposeur enfichable » (`0a209c33…`, convergence « confondant d'autorat ») : un monde planté par
la lignée qui a écrit les gabarits du proposeur ne peut pas arbitrer ce proposeur. Ici, la **grammaire** est fixée d'avance
et chaque monde en est un tirage par graine, sans choix d'auteur sur la structure d'un monde particulier. La grammaire
reste écrite par moi : c'est la limite déclarée.

Grammaire (par moniteur, K issues ordinales, score s(z, g), loi p(c) ∝ exp((c − (K − 1)/2)·s)) :
- « monotone » : s = a·z_i ;
- « combinaison » : s = a·z_i + b·z_j ;
- « interaction » : s = a·z_i·signe(z_j) (l'effet de i s'inverse avec le signe de j) ;
- « sous_population » : s = a·z_i si g = 0, −a·z_i sinon ;
- « seuil » : s = a·z_i si z_j > τ, 0 sinon (τ tiré dans [−0,5 ; 0,5]).
Toutes sont exprimables au gabarit du proposeur (softmax, par sous-population, si/sinon à seuil) : le témoin vrai d'un
moniteur est sa loi exacte. Les deux premières sont linéaires (le prédicteur connu, linéaire en tous les traits, les
contient presque) ; les trois autres ne le sont pas. Parties : calibrage (prédicteur connu), développement (exploration,
distincte du calibrage), épreuve ; par instance (pas de tâches ici).

Usage : python -I -B exemples/generer_monde_grammaire_v1.py GRAINE SORTIE_DOSSIER_NEUF
"""

import json
import math
import os
import random
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))

from pole.outils import ecrire_json_scelle, graine_derivee  # noqa: E402

STRUCTURES = ("monotone", "combinaison", "interaction", "sous_population", "seuil")
LINEAIRES = ("monotone", "combinaison")


def _softmax_ordinal(poids_par_trait, d, k, biais=None):
    """Loi softmax ordinale : poids de l'issue c = (c − (K−1)/2)·w ; w : dictionnaire trait → coefficient."""
    poids = [[0.0] * d for _ in range(k)]
    for c in range(k):
        for t, w in poids_par_trait.items():
            poids[c][t] = round((c - (k - 1) / 2) * w, 6)
    return {"type": "softmax", "poids": poids, "biais": list(biais or [0.0] * k)}


def loi_de_structure(structure, i, j, a, b, tau, d, k):
    """Loi exacte de la structure, au gabarit du proposeur (borne des poids : 4 ; (K−1)/2·|a| ≤ 4 pour a ≤ 2,5 et K ≤ 3)."""
    if structure == "monotone":
        return _softmax_ordinal({i: a}, d, k)
    if structure == "combinaison":
        return _softmax_ordinal({i: a, j: b}, d, k)
    if structure == "interaction":
        return {"type": "si_sinon", "condition": {"indice": j, "seuil": 0.0},
                "si": _softmax_ordinal({i: a}, d, k), "sinon": _softmax_ordinal({i: -a}, d, k)}
    if structure == "sous_population":
        return {"type": "par_sous_population", "lois": {"0": _softmax_ordinal({i: a}, d, k), "1": _softmax_ordinal({i: -a}, d, k)}}
    if structure == "seuil":
        return {"type": "si_sinon", "condition": {"indice": j, "seuil": round(tau, 6)},
                "si": _softmax_ordinal({i: a}, d, k), "sinon": _softmax_ordinal({}, d, k)}
    raise ValueError(structure)


def generer_monde(graine, d=4, moniteurs=3, k=3, n=900, parts=(150, 300, 450), structures=None):
    """(banque, témoins, vérité) ; `structures` : liste imposée (une par moniteur), sinon tirée."""
    from pole import selection_pari as sp
    rng = random.Random(graine_derivee(graine, "monde-grammaire"))
    noms = [f"M{m}" for m in range(moniteurs)]
    verite, temoins = {}, []
    for m, nom in enumerate(noms):
        structure = structures[m] if structures else rng.choice(STRUCTURES)
        i, j = rng.sample(range(d), 2)
        a = rng.choice([-1, 1]) * rng.uniform(1.2, 2.2)
        b = rng.choice([-1, 1]) * rng.uniform(1.0, 2.0)
        tau = rng.uniform(-0.5, 0.5)
        loi = loi_de_structure(structure, i, j, a, b, tau, d, k)
        bruit = [t for t in range(d) if t not in (i, j)][0]
        verite[nom] = {"structure": structure, "i": i, "j": j, "a": round(a, 6), "b": round(b, 6), "tau": round(tau, 6),
                       "lineaire": structure in LINEAIRES, "loi": loi, "trait_de_bruit": bruit}
        temoins.append({"identifiant": f"V-{nom}", "verite": "vraie", "moniteur": nom, "loi": loi,
                        "enonce": f"Témoin vrai : la loi exacte du moniteur {nom} ({structure})"})
        temoins.append({"identifiant": f"F-{nom}", "verite": "fausse", "moniteur": nom,
                        "loi": _softmax_ordinal({bruit: 1.5}, d, k),
                        "enonce": f"Témoin faux : l'issue du moniteur {nom} suivrait le trait {bruit}"})
    instances = []
    bornes = [parts[0], parts[0] + parts[1]]
    for r in range(n):
        z = [round(rng.gauss(0.0, 1.0), 6) for _ in range(d)]
        g = rng.randrange(2)
        issues = {nom: sp.tirer_categorie(rng, sp.proba(verite[nom]["loi"], {"z": z, "g": g}, [], 0)) for nom in noms}
        partie = "calibrage" if r < bornes[0] else ("developpement" if r < bornes[1] else "epreuve")
        instances.append({"identifiant": f"i{r:04d}", "z": z, "g": g, "issues": issues, "partie": partie})
    banque = {"nom": f"grammaire-{graine}", "traits": [f"t{t}" for t in range(d)], "sous_populations": 2,
              "moniteurs": {nom: {"nombre_issues": k, "instances": n} for nom in noms}, "instances": instances,
              "origine": "monde tiré au hasard dans la grammaire v1 (exemples/generer_monde_grammaire_v1.py)"}
    return banque, temoins, verite


def fiches_de_temoins(temoins, d, k, alpha=0.05):
    """Fiches du pôle pour les témoins (au gabarit des fiches du proposeur)."""
    from pole.fiche import Fiche
    sortie = []
    for t in temoins:
        sortie.append(Fiche.depuis_dict({
            "identifiant": t["identifiant"], "enonce": t["enonce"],
            "prediction": {"signe": "+", "valeur": 0.1, "texte": "log-richesse positive"},
            "metrique": "richesse W contre la bibliothèque", "nul": "prédicteurs aveugles et connu",
            "seuil": round(1 / alpha, 6), "severite_attendue": alpha, "cout_borne": 1.0,
            "protocole": "pari sur l'épreuve après le gel", "domaines": [f"moniteur {t['moniteur']}"],
            "operateurs": ["témoin"], "contraintes": [], "temoin": t["verite"], "loi_predictive": t["loi"],
            "espace_instances": {"dimension": d, "nombre_issues": k, "sous_populations": 2, "moniteur": t["moniteur"]}}).valider())
    return sortie


def principal(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 2:
        print(__doc__.split("Usage : ")[1])
        return 2
    graine, sortie = int(argv[0]), argv[1]
    if os.path.exists(sortie) and os.listdir(sortie):
        raise FileExistsError(sortie)
    banque, temoins, verite = generer_monde(graine)
    ecrire_json_scelle(os.path.join(sortie, "banque.json"), banque)
    ecrire_json_scelle(os.path.join(sortie, "temoins.json"), temoins)
    ecrire_json_scelle(os.path.join(sortie, "verite.json"), {n: {k: v for k, v in x.items() if k != "loi"} for n, x in verite.items()})
    print(json.dumps({n: x["structure"] for n, x in verite.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
