"""Population et témoins de démonstration à 4 traits (sélection par pari), tirés des fichiers à 2 traits : mêmes fiches,
mêmes énoncés (donc mêmes vérités, `monde-pari-demo-v1.json`), lois softmax neuves de dimension 4 (graine fixe).
Usage (depuis ce dossier) : python -I -B generer_demo_4traits_v1.py"""
import json
import os
import random
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ICI))
from pole import selection_pari as sp  # noqa: E402

for source, cible in (("population-pari-demo-v1.json", "population-pari-demo-4traits-v1.json"),
                      ("temoins-pari-demo-v1.json", "temoins-pari-demo-4traits-v1.json")):
    with open(os.path.join(ICI, source), encoding="utf-8") as f:
        donnees = json.load(f)
    fiches = donnees["fiches"] if isinstance(donnees, dict) else donnees
    for fiche in fiches:
        rng = random.Random(f"demo-4traits-v1|{fiche['identifiant']}")
        fiche["loi_predictive"] = sp.loi_softmax_aleatoire(rng, 3, 4)
        fiche["espace_instances"] = dict(fiche.get("espace_instances") or {}, nombre_issues=3, dimension=4)
    if os.path.exists(os.path.join(ICI, cible)):
        sys.exit(f"existe déjà : {cible} (on n'écrase jamais)")
    with open(os.path.join(ICI, cible), "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=1, sort_keys=True)
    print(cible, len(fiches))
