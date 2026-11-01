"""Proposeur scripté pour un monde sur banque (v7, en attendant le rôle proposeur) : fiches de départ « monotones » et
témoins de domaine.

- Pour chaque moniteur de la banque et chaque trait réel (hors trait de bruit), deux fiches : « l'issue croît avec le
  trait » et « l'issue décroît avec le trait » (loi softmax ordinale : poids proportionnel au rang de la classe, biais =
  logarithme des fréquences publiques de la partie de calibrage — les taux de base, connus de tous).
- Témoins **faux** par construction : fiches dont la loi ne dépend que du trait de bruit (tiré par graine, sans lien avec
  les notes), une par moniteur.
- Témoins **vrais** par construction, déclarés seulement si un trait a, sur la partie de calibrage, un lien monotone
  net avec l'issue (corrélation de rang ≥ seuil) : à vérifier, pas à présumer ; sinon aucun témoin vrai pour ce moniteur.

Usage : python -I -B exemples/proposeur_scripte_banque_v1.py exemples/banque-t05-v1.json SORTIE_POPULATION.json SORTIE_TEMOINS.json
"""

import argparse
import json
import math
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))

from pole.outils import ecrire_json_scelle  # noqa: E402

FORCE = 0.8  # poids par rang de classe, sur des traits centrés-réduits
SEUIL_TEMOIN_VRAI = 0.35


def _correlation_rang(xs, ys):
    """Corrélation de Spearman (rangs moyens pour les égalités)."""
    def rangs(v):
        ordre = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(ordre):
            j = i
            while j + 1 < len(ordre) and v[ordre[j + 1]] == v[ordre[i]]:
                j += 1
            for q in range(i, j + 1):
                r[ordre[q]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = rangs(xs), rangs(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def loi_monotone(j, d, k, sens, biais):
    poids = [[0.0] * d for _ in range(k)]
    for c in range(k):
        poids[c][j] = round(sens * FORCE * (c - (k - 1) / 2), 6)
    return {"type": "softmax", "poids": poids, "biais": [round(b, 6) for b in biais]}


def fiche_de(identifiant, enonce, loi, moniteur, k, d, domaine, operateur, contraintes=("lineaire",), temoin=None,
             banque_nom="banque-t05-v2"):
    f = {"identifiant": identifiant, "enonce": enonce, "prediction": {"signe": "+", "valeur": 0.1,
         "texte": "log-richesse moyenne par tirage positive contre la bibliothèque nulle"},
         "metrique": "richesse W contre la bibliothèque (aveugle, et prédicteur connu si servi)",
         "nul": "bibliothèque de prédicteurs aveugles (marginale, uniforme, moyennes glissantes) et prédicteur connu",
         "seuil": 20.0, "severite_attendue": 0.05, "cout_borne": 1.0,
         "protocole": "pari sur les instances d'épreuve de la banque choisies ex ante par divergence",
         "domaines": [domaine], "operateurs": [operateur], "contraintes": list(contraintes),
         "loi_predictive": loi, "espace_instances": {"dimension": d, "nombre_issues": k, "sous_populations": 2,
                                                     "moniteur": moniteur, "banque": banque_nom}}
    if temoin:
        f["temoin"] = temoin
    return f


def proposer(banque):
    traits, d = banque["traits"], len(banque["traits"])
    population, temoins, rapport = [], [], {}
    for nom, m in sorted(banque["moniteurs"].items()):
        k = m["nombre_issues"]
        calib = [l for l in banque["instances"] if l.get("partie") == "calibrage" and nom in l["issues"]]
        freq = [sum(1 for l in calib if l["issues"][nom] == c) + 0.5 for c in range(k)]
        biais = [math.log(f / sum(freq)) for f in freq]
        juge, rubrique = m["juge"], m["rubrique"]
        domaine = f"juge {juge}"
        rapport[nom] = {}
        for j, trait in enumerate(traits):
            if trait == "bruit":
                continue
            rho = _correlation_rang([l["z"][j] for l in calib], [l["issues"][nom] for l in calib])
            rapport[nom][trait] = round(rho, 3)
            for sens, mot in ((1, "croît"), (-1, "décroît")):
                ident = f"{juge}-{rubrique[:4]}-{trait[:8]}-{'plus' if sens > 0 else 'moins'}"
                population.append(fiche_de(ident, f"La note {rubrique} du juge {juge} {mot} avec {trait}",
                                           loi_monotone(j, d, k, sens, biais), nom, k, d, domaine, f"monotone:{trait}"))
            if abs(rho) >= SEUIL_TEMOIN_VRAI:
                sens = 1 if rho > 0 else -1
                temoins.append(fiche_de(f"T-{juge}-{rubrique[:4]}-{trait[:8]}-vrai",
                                        f"Témoin vrai : la note {rubrique} du juge {juge} suit {trait} (rang {rho:+.2f} en calibrage)",
                                        loi_monotone(j, d, k, sens, biais), nom, k, d, domaine, f"monotone:{trait}",
                                        temoin="vraie"))
        jb = traits.index("bruit")
        temoins.append(fiche_de(f"T-{juge}-{rubrique[:4]}-bruit-faux",
                                f"Témoin faux : la note {rubrique} du juge {juge} suit le trait de bruit",
                                loi_monotone(jb, d, k, 1, biais), nom, k, d, domaine, "monotone:bruit", temoin="fausse"))
    return population, temoins, rapport


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("banque")
    a.add_argument("population")
    a.add_argument("temoins")
    args = a.parse_args(argv)
    with open(args.banque, encoding="utf-8") as f:
        banque = json.load(f)
    population, temoins, rapport = proposer(banque)
    ecrire_json_scelle(args.population, {"fiches": population, "proposeur": "scripté v1", "banque": banque["nom"]})
    ecrire_json_scelle(args.temoins, {"fiches": temoins, "correlations_de_rang_en_calibrage": rapport})
    print(json.dumps({"fiches": len(population), "temoins_vrais": sum(t["temoin"] == "vraie" for t in temoins),
                      "temoins_faux": sum(t["temoin"] == "fausse" for t in temoins), "rangs": rapport}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
