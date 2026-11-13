"""K20-LIV : montre que chaque contrôle de schéma détecte une altération délibérée, sur une COPIE en mémoire (le vrai fichier n'est jamais écrit)."""
import sys, pathlib, copy
import numpy as np, pandas as pd
R = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(R))
from controles import *
base = pd.read_csv(R / "K20-LIV_analyse.csv", dtype={"episode": str})
v0, a0 = controles(base); assert n_violations(v0) == 0 and len(a0) == 0
def idx(var, cible): return base.index[(base.variable == var) & (base.cible == cible)][0]
def test(n, nom, f, hors_portee=False):
    d = base.copy(); f(d); viol, anom = controles(d)
    detecte = bool(viol[n]) and (n in viol)
    autres = [k for k in viol if viol[k] and k != n]
    print(f"controle {n:2d} | {nom:55s} | viole: {sorted(k for k in viol if viol[k])} | anomalies hors principal: {len(anom)}")
    return viol, anom
res = {}
i = idx("CPI", "1990-06"); u = idx("UNPR", "1999-12"); p = idx("PRIME", "2000-06")
def f1(d): d.insert(0, "extra", 1)
res[1] = test(1, "colonne ajoutée", f1)
def f1b(d): d.rename(columns={"revision": "revison"}, inplace=True)
test(1, "colonne renommée", f1b)
def f2(d): d.loc[u, "cible"] = "1999-09"
res[2] = test(2, "cible de mois 09", f2)
def f2b(d): d.loc[u, ["variable", "cible"]] = ["CPI", "1990-06"]
test(2, "couple (variable, cible) dupliqué / variable hors plage", f2b)
def f3(d): d.loc[i, "enquete_2"] = "1990-06"
res[3] = test(3, "enquete_2 non suivante", f3)
def f3b(d): d.loc[i, "mois_ancre_1"] = "1989-05"
test(3, "mois de base faux", f3b)
def f4(d): d.loc[u, "prev_6m_2"] = np.nan
res[4] = test(4, "prev_6m_2 supprimée", f4)
def f4b(d): d.loc[p, "bp_1"] = 100.0
test(4, "bp_1 présente sur une variable non IPC", f4b)
def f5(d): d.loc[i, "serie_realise"] = "CPIAUCSL"
res[5] = test(5, "série réalisée fausse (IPC avant 2004)", f5)
def f5b(d): d.loc[u, "jour_realise"] = "1999-11-01"
test(5, "jour de lecture d'un autre mois", f5b)
def f6(d): d.loc[u, "prev_12m_1"] = 150.0
res[6] = test(6, "prévision de chômage hors plage", f6)
def f6b(d): d.loc[i, "realise_niv"] = 600.0
test(6, "IPC réalisé hors plage", f6b)
def f7(d): d.loc[u, "erreur"] += 0.01
res[7] = test(7, "erreur écartée de 0,01", f7)
def f7b(d): d.loc[i, "y_prev_1"] += 1e-4
test(7, "y_prev_1 de l'IPC écartée de 1e-4", f7b)
def f8(d): d.loc[u, "n_rep_1"] = 1
res[8] = test(8, "n_rep_1 = 1", f8)
def f8b(d): d.loc[u, "var_rep_2"] = -0.1
test(8, "variance négative", f8b)
def f9(d): d.loc[u, "complete"] = 0
res[9] = test(9, "complete faux", f9)
def f9b(d): d.loc[idx("UNPR", "2020-06"), "principal"] = 1
test(9, "ligne pandémie marquée principale", f9b)
def f10(d): d.loc[u, "episode"] = "E3"
res[10] = test(10, "épisode faux", f10)
def f10b(d): d.loc[idx("CPI", "2008-06"), "episode"] = np.nan
test(10, "épisode effacé", f10b)
def f11(d): d.loc[u, "grande_nouvelle"] = 1 - d.loc[u, "grande_nouvelle"]
res[11] = test(11, "grande_nouvelle inversée", f11)
print("--- altérations HORS lignes principales : comptées comme anomalies, jamais comme violations")
h = idx("CPI", "2005-06"); h2 = idx("UNPR", "2020-06"); h3 = idx("UNPR", "2026-06")
def g1(d): d.loc[h2, "prev_12m_1"] = 150.0
test(6, "plage violée sur UNPR 2020-06 (hors principal)", g1)
def g2(d): d.loc[h3, "enquete_1"] = "2025-09"
test(3, "date fausse sur UNPR 2026-06 (hors principal)", g2)
def g3(d): d.loc[h, "n_rep_1"] = 1
test(8, "bruit faux sur CPI 2005-06 (hors principal)", g3)
