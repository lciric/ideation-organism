"""Banque de la couche 1 : le pilote de T0.5 (épisodes réels du modèle de 8 milliards) et les notations décisives des deux
juges, mis au format du monde sur banque (`pole/monde_banque.py`). Lecture seule des fichiers de `main` ; rien n'est
relancé ; les empreintes des sources sont consignées dans le manifeste de la banque.

Une **instance** = un épisode (tâche/e0 ou e1 ; la première passe de notation seulement, pour qu'un même texte n'entre
qu'une fois par moniteur) ; **traits** `z` (centrés-réduits sur la banque) : logarithme du nombre total de jetons générés,
nombre d'actions valides, moyenne et écart-type des jetons par action, et un **trait de bruit** tiré par graine (toute
fiche qui ne dépend que de lui est fausse par construction : témoin) ; sous-population `g` = numéro de l'épisode dans la
tâche (0 pour e0, 1 pour e1). Un **moniteur** = (juge, rubrique) ; son **issue** = la note de la rubrique, discrétisée en
classes équilibrées (points de coupe consignés) ; une note absente (None) rend l'issue absente pour ce moniteur (jamais
imputée). Partie de calibrage / partie d'épreuve : par tâche (toutes les instances d'une tâche du même côté), tirée par
graine, un tiers en calibrage.

Usage : python -I -B exemples/construire_banque_t05_v1.py RACINE_MAIN exemples/banque-t05-v2.json [--graine 20261027]
(la v1 de la banque, à cinq traits, reste dans `exemples/banque-t05-v1.json` ; le script produit désormais la v2)
"""

import argparse
import collections
import hashlib
import json
import math
import os
import random
import statistics
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))

from pole.outils import ecrire_json_scelle, graine_derivee  # noqa: E402

EPISODES = "diag/20261012-105125-t05-pilote-reel/episodes.json"
NOTATIONS = {"8B": "diag/20261017-193648-t05-notations-reel/notations-8B-decisives.json",
             "3B": "diag/20261017-193648-t05-notations-reel/notations-3B-decisives.json"}
RUBRIQUES = ("BALANCE", "COHERENCE", "NOVELTY", "RIGOR", "RESULT_REASONING", "IRRELEVANCE_PENALTY", "REDUNDANCY_PENALTY")
TRAITS = ("log_jetons_total", "actions_valides", "jetons_par_action_ecart_type", "bruit")
# v2 de la banque (27 octobre, 15:11 heure de Paris, « corrige ») : `jetons_par_action_moyenne` retiré, identique en rang à
# `log_jetons_total` quand toutes les courses ont dix actions (des fiches en double que la mémoire ne voyait pas).


def sha256_fichier(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for morceau in iter(lambda: f.read(1 << 16), b""):
            h.update(morceau)
    return h.hexdigest()


def classes_equilibrees(valeurs, maximum=3, part_minimale=0.10):
    """Points de coupe (valeur incluse dans la classe du bas) : trois classes si la plus petite pèse au moins
    `part_minimale` de l'effectif (coupes qui maximisent la plus petite classe), sinon deux, sinon None (moniteur écarté)."""
    import itertools
    compte = collections.Counter(valeurs)
    niveaux = sorted(compte)
    total = len(valeurs)
    for k in range(min(maximum, len(niveaux)), 1, -1):
        meilleur, taille = None, -1
        for coupes in itertools.combinations(niveaux[:-1], k - 1):
            effectifs = collections.Counter(classe(v, coupes) for v in valeurs)
            plus_petite = min(effectifs.get(i, 0) for i in range(k))
            if plus_petite > taille:
                meilleur, taille = list(coupes), plus_petite
        if meilleur is not None and taille >= part_minimale * total:
            return meilleur
    return None


def classe(valeur, coupes):
    return sum(1 for c in coupes if valeur > c)


def construire(racine_main, graine):
    with open(os.path.join(racine_main, EPISODES), encoding="utf-8") as f:
        episodes = json.load(f)["resultat"]["fiches"]
    sources = {EPISODES: sha256_fichier(os.path.join(racine_main, EPISODES))}
    notes = {}
    for juge, chemin in NOTATIONS.items():
        sources[chemin] = sha256_fichier(os.path.join(racine_main, chemin))
        with open(os.path.join(racine_main, chemin), encoding="utf-8") as f:
            for n in json.load(f)["resultat"]["notations"]:
                _, tache, ep, passe = n["cle"].split("/")
                if passe != "passe-0":
                    continue
                notes[(juge, f"{tache}/{ep}")] = n["notes"]
    rng = random.Random(graine_derivee(graine, "banque-t05", "bruit"))
    lignes = []
    for e in episodes:
        jetons = e["jetons_par_action"]
        if not jetons or not any((juge, e["episode"]) in notes for juge in NOTATIONS):
            continue  # épisode jamais noté (troisième épisode de chaque tâche) : hors banque
        lignes.append({"identifiant": e["episode"], "tache": e["tache"], "g": int(e["episode"].rsplit("/e", 1)[1]),
                       "bruts": [math.log(sum(jetons)), float(e["bilan"]["actions_valides"]),
                                 statistics.pstdev(jetons), rng.gauss(0.0, 1.0)]})
    moyennes = [statistics.fmean(l["bruts"][j] for l in lignes) for j in range(len(TRAITS))]
    ecarts = [statistics.pstdev([l["bruts"][j] for l in lignes]) or 1.0 for j in range(len(TRAITS))]
    for l in lignes:
        l["z"] = [round((x - m) / s, 6) for x, m, s in zip(l["bruts"], moyennes, ecarts)]
    moniteurs = {}
    for juge in NOTATIONS:
        for rub in RUBRIQUES:
            valeurs = [notes[(juge, l["identifiant"])][rub] for l in lignes
                       if (juge, l["identifiant"]) in notes and isinstance(notes[(juge, l["identifiant"])].get(rub), int)]
            if len(valeurs) < 30:
                continue
            coupes = classes_equilibrees(valeurs)
            if coupes is None:
                continue
            moniteurs[f"{juge}:{rub}"] = {"juge": juge, "rubrique": rub, "coupes": coupes,
                                          "nombre_issues": len(coupes) + 1, "instances": len(valeurs)}
    for l in lignes:
        l["issues"] = {}
        for nom, m in moniteurs.items():
            n = notes.get((m["juge"], l["identifiant"]))
            if n is not None and isinstance(n.get(m["rubrique"]), int):
                l["issues"][nom] = classe(n[m["rubrique"]], m["coupes"])
    taches = sorted({l["tache"] for l in lignes})
    rng_part = random.Random(graine_derivee(graine, "banque-t05", "partition"))
    rng_part.shuffle(taches)
    calibrage = set(taches[:len(taches) // 3])
    for l in lignes:
        l["partie"] = "calibrage" if l["tache"] in calibrage else "epreuve"
        del l["bruts"]
    lignes.sort(key=lambda l: l["identifiant"])
    return {"nom": "banque-t05-v2", "graine": graine, "traits": list(TRAITS), "sous_populations": 2,
            "normalisation": {"moyennes": moyennes, "ecarts_types": ecarts},
            "moniteurs": moniteurs, "instances": lignes, "sources": sources,
            "notes": "une instance par épisode et par moniteur (première passe) ; tâches entières d'un même côté de la "
                     "partition ; les épisodes d'une même tâche restent dépendants (limite déclarée)"}


def principal(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("racine_main")
    a.add_argument("sortie")
    a.add_argument("--graine", type=int, default=20261027)
    args = a.parse_args(argv)
    banque = construire(args.racine_main, args.graine)
    ecrire_json_scelle(args.sortie, banque)
    print(json.dumps({"instances": len(banque["instances"]), "calibrage": sum(l["partie"] == "calibrage" for l in banque["instances"]),
                      "moniteurs": {k: (v["nombre_issues"], v["instances"]) for k, v in banque["moniteurs"].items()}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
