#!/usr/bin/env python3
"""K20-ZE : lecture alternative de 6.2 (egalites exactes sur les valeurs decimales : |surprise| arrondi a 6 decimales
avant Q_v et la coupure). Sert uniquement a documenter l'ambiguite dans ecarts.md ; n'ecrit PAS temoin.json."""
import importlib.util, json, pathlib
import numpy as np
ICI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("analyse", ICI / "analyse.py")
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
d = A.charge()
P = d.principal == 1
d2 = d.copy(); d2["surprise"] = d2.surprise.round(6)
Lalt, info = A.grande(d2, "surprise", P)
L = d["grande_nouvelle"].astype(float)
m = d.surprise.notna()
print("lignes dont L differe :", int((L[m] != Lalt[m]).sum()), " dont principales :", int((L[m & P] != Lalt[m & P]).sum()))
print(json.dumps(info, indent=1))
Talt, _ = A.calculer(d, Lalt)
Tlit, _ = A.calculer(d, L)
cles = ["n_grands", "n_tours_grands", "c", "et_c_dk8", "t_c", "borne_basse_ic90", "borne_haute_ic90", "b_moyen", "controle_positif_ok",
        "rapport_variance_revision", "biais_mecanique_nu20", "seuil_survie_bas", "borne_basse_moins_seuil", "marge_indecision",
        "pertinence_manquante", "c_sans_E1", "c_sans_E2", "c_sans_E3", "t_sans_E1", "t_sans_E2", "t_sans_E3", "t_min_sans_episode",
        "c_min_sans_episode", "conflit_robustesse", "n_effectif", "c_HICP", "c_RGDP", "c_UNEM"]
for k in cles: print(f"{k:28s} litterale={Tlit[k]!r:>24}  arrondie={Talt[k]!r:>24}")
json.dump({"info": info, "litterale": {k: Tlit[k] for k in cles}, "arrondie": {k: Talt[k] for k in cles}},
          open(ICI / "lecture_alternative.json", "w"), indent=1, default=float)
