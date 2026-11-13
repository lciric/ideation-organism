#!/usr/bin/env python3
"""K20-ZE : controle croise avec statsmodels (MCO, covariance de Driscoll-Kraay de sandwich.cov_nw_groupsum),
reduction et indicatrices ecrites autrement (formule patsy, groupby.transform). Compare a temoin.json. Usage : python3 -I controle_croise.py"""
import json, pathlib
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats import sandwich_covariance as sw

ICI = pathlib.Path(__file__).resolve().parent
d = pd.read_csv(ICI / "K20-ZE_analyse.csv", dtype={"episode": str})
T = json.loads((ICI / "temoin.json").read_text())
d["g"] = d.variable + d.horizon.astype(str)
p = d[d.principal == 1].copy()

def red(df_all, col, ref):
    mu = ref.groupby("g")[col].transform("mean"); sd = ref.groupby("g")[col].transform("std")
    m = ref.groupby("g")[col].mean(); s = ref.groupby("g")[col].std()
    return (df_all[col] - df_all.g.map(m)) / df_all.g.map(s)

def fit(df, formula, lag, time="t_tour"):
    """MCO statsmodels. cov_nw_groupsum somme les scores par valeur de `time` avec np.bincount : on lui passe t - t_min (entiers
    consecutifs), de sorte que les tours sans ligne soient des dates a somme nulle (pas de compression par position, pas de
    re-etiquetage par pd.factorize, qui se declenche si max(time) > 2 * nobs et casse l'ordre des dates)."""
    res = smf.ols(formula, data=df).fit()
    t = (df[time] - df[time].min()).to_numpy().astype(int)
    V = sw.cov_nw_groupsum(res, lag, t, weights_func=sw.weights_bartlett, use_correction=False)
    return res, V

for df in (d, p):
    df["zr"] = red(df, "revision", p); df["ze"] = red(df, "erreur", p)
p["L"] = p.grande_nouvelle
fm = "ze ~ 0 + C(g) + C(g):L + C(g):zr + zr:L"
res, V = fit(p, fm, 8)
ci = list(res.params.index).index("zr:L")
out = {}
out["c"], out["et_c_dk8"] = res.params["zr:L"], np.sqrt(V[ci, ci])
bn = [i for i, n in enumerate(res.params.index) if n.endswith(":zr") and "L" not in n]
out["b_moyen"] = res.params.iloc[bn].mean()
out["et_b_moyen_dk8"] = float(np.sqrt(np.full(6, 1 / 6) @ V[np.ix_(bn, bn)] @ np.full(6, 1 / 6)))
res0, V0 = fit(p, "ze ~ 0 + C(g) + zr", 8)
out["b_commun"], out["et_b_commun_dk8"] = res0.params["zr"], np.sqrt(V0[-1, -1])
for lag in (4, 12, 0):
    out[f"et_c_dk{lag}"] = np.sqrt(fit(p, fm, lag)[1][ci, ci])
res_i = smf.ols(fm, data=p).fit(); out["et_c_iid"] = res_i.bse["zr:L"]
# grappes par annee cible : cov_cluster (sandwich, grappes), sans correction de petit echantillon
out["et_c_grappes_annee"] = np.sqrt(sw.cov_cluster(res_i, p.annee_cible.to_numpy(), use_correction=False)[ci, ci])
for k in ("E1", "E2", "E3"):
    q = p[p.episode != k]
    r, v = fit(q, fm, 8)
    out[f"c_sans_{k}"] = r.params["zr:L"]; out[f"t_sans_{k}"] = r.params["zr:L"] / np.sqrt(v[ci, ci])
r, v = fit(d[d.complete == 1], fm.replace("L", "L"), 8) if False else (None, None)
cc = d[d.complete == 1].copy(); cc["L"] = cc.grande_nouvelle
r, v = fit(cc, fm, 8); out["c_avec_pandemie"], out["et_c_avec_pandemie_dk8"] = r.params["zr:L"], np.sqrt(v[ci, ci])
q = p[p.annee_cible <= 2019]; r, v = fit(q, fm, 8); out["c_avant_2020"], out["et_c_avant_2020_dk8"] = r.params["zr:L"], np.sqrt(v[-1, -1])
for h, nm in ((0, "annee_en_cours"), (1, "annee_suivante")):
    q = p[p.horizon == h]; r, v = fit(q, fm, 8); out[f"c_{nm}"], out[f"et_c_{nm}_dk8"] = r.params["zr:L"], np.sqrt(v[-1, -1])
# mediane
pm = p.copy(); pm["zr"] = red(pm, "revision_med", p); pm["ze"] = red(pm, "erreur_med", p)
r, v = fit(pm, fm, 8); out["c_mediane"], out["et_c_mediane_dk8"] = r.params["zr:L"], np.sqrt(v[ci, ci])
pc = p.copy(); pc["L"] = (pc.zr.abs() > 1).astype(int); r, v = fit(pc, fm, 8)
out["c_coupure_revision"], out["et_c_coupure_revision_dk8"] = r.params["zr:L"], np.sqrt(v[ci, ci])
# par variable
fv = "ze ~ 0 + C(g) + C(g):L + C(g):zr + zr:L:C(variable)"
r, v = fit(p, fv, 8)
for var in ("HICP", "RGDP", "UNEM"):
    nm = [n for n in r.params.index if n.startswith("zr:L:C(variable)[") and var in n][0]
    i = list(r.params.index).index(nm); out[f"c_{var}"], out[f"et_c_{var}_dk8"] = r.params[nm], np.sqrt(v[i, i])
# comparaison
pires = []
for k, x in out.items():
    ecart = abs(float(x) - T[k]); pires.append((ecart, k, float(x), T[k]))
pires.sort(reverse=True)
print("champs compares :", len(out))
for e, k, x, t in pires[:8]: print(f"{k:30s} croise={x:+.8f} temoin={t:+.8f} ecart={e:.2e}")
print("ecart maximal :", pires[0][0], pires[0][1])
