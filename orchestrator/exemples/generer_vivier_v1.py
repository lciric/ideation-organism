"""Vivier de démonstration (sélection par pari, 4 traits) : 60 fiches de départ sur 6 domaines et 4 opérateurs (deux
par fiche : beaucoup de paires valides), la moitié vraies (graine fixe), pour que le choix des paires de recombinaison
compte (marchepieds contre strates). Mot de Lazar du 27 octobre, 13:52 heure de Paris (« il faut un vivier plus grand »).
Usage (depuis ce dossier) : python -I -B generer_vivier_v1.py"""
import copy
import json
import os
import random
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))
from pole import selection_pari as sp  # noqa: E402

DOMAINES = ("memoire spectrale", "graphes", "morphologie", "representation", "arret", "hachage")
OPERATEURS = ("projection", "seuillage", "normalisation", "agregation")
N = 60

with open(os.path.join(ICI, "population-pari-demo-v1.json"), encoding="utf-8") as f:
    gabarit = json.load(f)["fiches"][0]
rng = random.Random("vivier-v1")
fiches, verites = [], {}
for i in range(N):
    domaine = DOMAINES[i % len(DOMAINES)]
    operateurs = rng.sample(OPERATEURS, 2)
    trait, issue = rng.randrange(4) + 1, rng.randrange(3) + 1
    fiche = copy.deepcopy(gabarit)
    fiche.update({"identifiant": f"V{i + 1:02d}", "domaines": [domaine], "operateurs": sorted(operateurs), "contraintes": [],
                  "enonce": f"Hypothèse V{i + 1:02d} : le trait {trait} oriente l'issue {issue} dans le domaine {domaine} "
                            f"par {operateurs[0]} et {operateurs[1]}",
                  "loi_predictive": sp.loi_softmax_aleatoire(rng, 3, 4),
                  "espace_instances": {"nombre_issues": 3, "dimension": 4, "sous_populations": 2}})
    fiches.append(fiche)
    verites[fiche["enonce"]] = rng.random() < 0.5
for nom, contenu in (("population-pari-vivier60-4traits-v1.json", {"fiches": fiches}),
                     ("monde-pari-vivier60-v1.json", {"lecture": "Vérités du vivier de 60 fiches (simulation).", "verites": verites})):
    chemin = os.path.join(ICI, nom)
    if os.path.exists(chemin):
        sys.exit(f"existe déjà : {nom} (on n'écrase jamais)")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(contenu, f, ensure_ascii=False, indent=1, sort_keys=True)
print(N, "fiches ;", sum(verites.values()), "vraies")
