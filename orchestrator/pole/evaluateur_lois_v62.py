"""Évaluateur de référence des lois du tour fermé, version 62 (fichier neuf, R12) — bibliothèque standard seule, aucun import
du pôle : ce fichier est **servi tel quel** dans la tranche de chaque étage de tests de mort (`tranche/evaluateur_lois_v62.py`,
même empreinte pour toutes les fiches ; contre-lecture 2, B7 et C8) et lu par l'expérimentateur dans le bac à sable.

`proba(loi, instance)` reproduit `selection_pari.proba(loi, instance, [], 0)` pour les six types du gabarit fermé des proposeurs
(fixe, softmax, par_sous_population, melange, si_sinon, transformee) : chaque probabilité relevée au plancher 1e-12 puis
renormalisée, mêmes opérations dans le même ordre (essai : égalité à 1e-12 près sur des lois tirées de chaque type).
`gains(loi, chemin)` : gain de log-score par épisode de la loi sur la marginale empirique de la tranche (comptes + 0,5), en nat ;
`ecrire_gains(loi, chemin, sortie)` écrit le fichier brut `episode,gain` en pleine précision (`repr`), jamais arrondi, et
imprime la moyenne (ligne témoin). Usage dans le script de l'expérimentateur :

    import json, runpy
    ev = runpy.run_path('tranche/evaluateur_lois_v62.py')
    ev['ecrire_gains'](json.loads(LOI), 'tranche/episodes.csv', 'gains.csv')
"""

import csv
import math

PLANCHER = 1e-12
NOMBRE_ISSUES = 3


def _normaliser(p):
    p = [max(PLANCHER, float(x)) for x in p]
    s = sum(p)
    return [x / s for x in p]


def _condition(condition, instance):
    if "sous_population" in condition:
        return instance.get("g") == condition["sous_population"]
    return instance["z"][condition["indice"]] > condition.get("seuil", 0.0)


def proba(loi, instance):
    """Loi prédictive de l'issue sachant l'instance {z: [z0, z1], g: 0 ou 1}."""
    genre = loi["type"]
    if genre == "fixe":
        return _normaliser(loi["probas"])
    if genre == "softmax":
        z = instance["z"]
        scores = [b + sum(w * x for w, x in zip(ligne, z)) for ligne, b in zip(loi["poids"], loi["biais"])]
        m = max(scores)
        return _normaliser([math.exp(s - m) for s in scores])
    if genre == "par_sous_population":
        return proba(loi["lois"].get(str(instance.get("g")), loi.get("defaut")), instance)
    if genre == "melange":
        mix = [0.0] * len(proba(loi["composantes"][0], instance))
        for poids, composante in zip(loi["poids"], loi["composantes"]):
            for k, p in enumerate(proba(composante, instance)):
                mix[k] += poids * p
        return _normaliser(mix)
    if genre == "si_sinon":
        return proba(loi["si"] if _condition(loi["condition"], instance) else loi["sinon"], instance)
    if genre == "transformee":
        p = proba(loi["base"], instance)
        if loi.get("melange_aveugle"):
            lam, b = loi["melange_aveugle"]["lambda"], _normaliser(loi["melange_aveugle"]["probas"])
            p = [(1 - lam) * x + lam * y for x, y in zip(p, b)]
        if loi.get("puissance") is not None:
            p = _normaliser([max(x, PLANCHER) ** loi["puissance"] for x in p])
        if loi.get("inclinaison"):
            p = _normaliser([x * math.exp(beta) for x, beta in zip(p, loi["inclinaison"])])
        if loi.get("oscillation"):
            o = loi["oscillation"]
            facteur = math.exp(o["amplitude"] * math.cos(o["frequence"] * instance["z"][o["trait"]] + o.get("phase", 0.0)))
            p = _normaliser([x * facteur if k == o["issue"] else x for k, x in enumerate(p)])
        return _normaliser(p)
    raise ValueError("type de loi hors du gabarit : " + repr(genre))


def lire_episodes(chemin):
    with open(chemin, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def gains(loi, chemin):
    """Gains de log-score par épisode (nat), dans l'ordre du fichier ; marginale empirique de la tranche, comptes + 0,5."""
    lignes = lire_episodes(chemin)
    comptes = [0.5] * NOMBRE_ISSUES
    for r in lignes:
        comptes[int(r["y"])] += 1
    s = sum(comptes)
    marg = [c / s for c in comptes]
    sortie = []
    for r in lignes:
        y = int(r["y"])
        p = proba(loi, {"z": [float(r["z0"]), float(r["z1"])], "g": int(r["g"])})
        sortie.append(math.log(max(p[y], 1e-12)) - math.log(marg[y]))
    return sortie


def ecrire_gains(loi, chemin, sortie="gains.csv"):
    """Écrit le fichier brut (colonnes episode, gain ; pleine précision) et imprime la moyenne ; rend la moyenne."""
    g = gains(loi, chemin)
    with open(sortie, "w", encoding="utf-8") as f:
        f.write("episode,gain\n" + "".join("%d,%r\n" % (i, x) for i, x in enumerate(g, 1)))
    moyenne = sum(g) / len(g)
    print("RESULTAT: %r" % moyenne)
    return moyenne
