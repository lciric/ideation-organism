"""K20-ZE -- controle croise du verificateur.

Deuxieme implementation, independante de verification.py, des chiffres cles : lecture par pandas, reduction par
groupby, quantile ecrit a la main, regressions et Driscoll-Kraay par statsmodels (cov_nw_groupsum, sommes par
tour via bincount : les tours vides comptent), grappes par annee via statsmodels, et Driscoll-Kraay par
linearmodels sur l'echantillon principal (tours contigus). Compare a verification.json.

Imprime aussi une analyse de sensibilite (hors verification.json, hors verdict) : la lecture "decimale" des
egalites de |surprise| (valeurs arrondies a 1 decimale avant le quantile et la coupure).
Usage : python3 verification_controle.py
"""
import json
import math
import pathlib

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_nw_groupsum, cov_cluster

ICI = pathlib.Path(__file__).resolve().parent
d = pd.read_csv(ICI / "K20-ZE_analyse.csv", float_precision="round_trip",
                dtype={"tour": str, "tour_prec": str, "ref_periode": str, "ref_periode_prec": str, "episode": str},
                keep_default_na=False, na_values={c: [""] for c in ["prev", "prev_prec", "prev_med",
                "prev_prec_med", "ref", "ref_prec", "prev_glissante_t4", "realise", "revision", "erreur", "surprise",
                "surprise_consensus", "revision_med", "erreur_med", "grande_nouvelle"]})
ver = json.loads((ICI / "verification.json").read_text())
K = 1.708

d["serie"] = d.variable + "_h" + d.horizon.astype(str)
P = d.principal == 1

# Exactitude des differences dans le fichier (egalite exacte en double, pas seulement a 1e-9)
for res, a, b in [("surprise", "ref", "ref_prec"), ("revision", "prev", "prev_prec"), ("erreur", "realise", "prev")]:
    m = d[res].notna()
    print(f"{res} == {a} - {b} exactement en double : {(d.loc[m, res] == d.loc[m, a] - d.loc[m, b]).sum()} / {m.sum()}")

# Reduction par groupby (constantes de l'echantillon principal, appliquees a toutes les lignes de la serie)
def reduire(col):
    st = d[P].groupby("serie")[col].agg(["mean", "std"])  # std pandas : ddof = 1
    return (d[col] - d.serie.map(st["mean"])) / d.serie.map(st["std"]), st["std"]

d["zr"], sr = reduire("revision")
d["ze"], se = reduire("erreur")
d["zrm"], _ = reduire("revision_med")
d["zem"], _ = reduire("erreur_med")
d["p"] = d.erreur + d.revision
d["zp"], _ = reduire("p")
k_moyen = float((sr / se).mean())


def quantile_lineaire(x, q):
    """Quantile 'linear' (type 7) ecrit a la main."""
    x = np.sort(np.asarray(x, dtype=float))
    h = (len(x) - 1) * q
    lo = int(math.floor(h))
    hi = min(lo + 1, len(x) - 1)
    return x[lo] + (h - lo) * (x[hi] - x[lo])


def coupe(col, echantillon, arrondi=False):
    L = pd.Series(np.nan, index=d.index)
    info = {}
    for v in ["HICP", "RGDP", "UNEM"]:
        sub = d[echantillon & (d.variable == v) & d[col].notna()]
        a = sub.groupby("t_tour")[col].first().abs()
        if arrondi:
            a = a.round(1)
        Q = quantile_lineaire(a.values, 2 / 3)
        Qn = float(np.quantile(a.values, 2 / 3))
        n_s, n_l, T = int((a > Q).sum()), int((a >= Q).sum()), len(a)
        stricte = abs(n_s / T - 1 / 3) <= abs(n_l / T - 1 / 3)
        m = (d.variable == v) & d[col].notna()
        s_abs = d.loc[m, col].abs().round(1) if arrondi else d.loc[m, col].abs()
        L[m] = ((s_abs > Q) if stricte else (s_abs >= Q)).astype(float)
        info[v] = (Q, Qn, n_s, n_l, T, "stricte" if stricte else "large")
    return L, info


d["L"], infoL = coupe("surprise", P)
print("Coupure (Q main, Q numpy, n>, n>=, T, coupure) :", infoL)
print("L recalcule == grande_nouvelle du fichier :",
      bool(((d.L == d.grande_nouvelle) | (d.L.isna() & d.grande_nouvelle.isna())).all()))

series = sorted(d.serie.unique())


def design(sub, L, zr="zr", par_variable=False):
    X = pd.DataFrame(index=sub.index)
    ss = sorted(sub.serie.unique())
    for g in ss:
        X[f"a_{g}"] = (sub.serie == g).astype(float)
    for g in ss:
        X[f"d_{g}"] = (sub.serie == g).astype(float) * L[sub.index]
    for g in ss:
        X[f"b_{g}"] = (sub.serie == g).astype(float) * sub[zr]
    if par_variable:
        for v in ["HICP", "RGDP", "UNEM"]:
            X[f"c_{v}"] = sub[zr] * L[sub.index] * (sub.variable == v)
    else:
        X["c"] = sub[zr] * L[sub.index]
    return X


def sm_fit(mask, L, ze="ze", zr="zr", lags=8, par_variable=False):
    sub = d[mask]
    X = design(sub, L, zr, par_variable)
    r = sm.OLS(sub[ze].values, X.values).fit()
    time = (sub.t_tour - sub.t_tour.min()).values.astype(int)
    V = cov_nw_groupsum(r, lags, time, use_correction=False)
    return r, V, X


out = {}
r, V, X = sm_fit(P, d.L)
cols = list(X.columns)
ic = cols.index("c")
out["c"] = r.params[ic]
out["et_c_dk8"] = math.sqrt(V[ic, ic])
out["borne_basse_ic90"] = out["c"] - K * out["et_c_dk8"]
out["borne_haute_ic90"] = out["c"] + K * out["et_c_dk8"]
w = np.array([1 / 6 if n.startswith("b_") else 0.0 for n in cols])
out["b_moyen"] = float(w @ r.params)
out["et_b_moyen_dk8"] = math.sqrt(w @ V @ w)
out["et_c_iid"] = r.bse[ic]
out["n_effectif"] = r.nobs * (r.bse[ic] / out["et_c_dk8"]) ** 2
for lag in (4, 12, 0):
    out[f"et_c_dk{lag}"] = math.sqrt(cov_nw_groupsum(r, lag, (d[P].t_tour - d[P].t_tour.min()).values,
                                                     use_correction=False)[ic, ic])
out["et_c_grappes_annee"] = math.sqrt(cov_cluster(r, d[P].annee_cible.values, use_correction=False)[ic, ic])

# Pente commune
sub = d[P]
Xb = pd.get_dummies(sub.serie, dtype=float)
Xb["zr"] = sub.zr
rb = sm.OLS(sub.ze.values, Xb.values).fit()
Vb = cov_nw_groupsum(rb, 8, (sub.t_tour - sub.t_tour.min()).values, use_correction=False)
out["b_commun"] = rb.params[-1]
out["et_b_commun_dk8"] = math.sqrt(Vb[-1, -1])

# Pertinence
def rapport(z, L):
    sub = d[P].assign(z=d[P][z], L=L[P])
    dev = sub.z - sub.groupby(["serie", "L"]).z.transform("mean")
    return float((dev[sub.L == 1] ** 2).mean() / (dev[sub.L == 0] ** 2).mean()), \
        float((dev[sub.L == 0] ** 2).mean()), float((dev[sub.L == 1] ** 2).mean())

out["rapport_variance_revision"], a, A = rapport("zr", d.L)
out["rapport_variance_ecart_prec"] = rapport("zp", d.L)[0]
out["biais_mecanique_nu20"] = (2 * out["b_moyen"] + k_moyen) * 0.10 * (1 / a - 1 / A)
out["k_moyen"] = k_moyen

# Episodes
for k in (1, 2, 3):
    rk, Vk, Xk = sm_fit(P & (d.episode != f"E{k}"), d.L)
    out[f"c_sans_E{k}"] = rk.params[-1]
    out[f"t_sans_E{k}"] = rk.params[-1] / math.sqrt(Vk[-1, -1])

# Secondaires
def sec(nom, mask, L, ze="ze", zr="zr"):
    rs, Vs, _ = sm_fit(mask, L, ze, zr)
    out[f"c_{nom}"] = rs.params[-1]
    out[f"et_c_{nom}_dk8"] = math.sqrt(Vs[-1, -1])

sec("avec_pandemie", d.complete == 1, d.L)
sec("avant_2020", P & (d.annee_cible <= 2019), d.L)
sec("annee_en_cours", P & (d.horizon == 0), d.L)
sec("annee_suivante", P & (d.horizon == 1), d.L)
sec("mediane", P, d.L, "zem", "zrm")
sec("coupure_revision", P, (d.zr.abs() > 1).astype(float))
P8 = P & d.surprise_consensus.notna()
L8, info8 = coupe("surprise_consensus", P8)
out["n_surprise_consensus"] = int(P8.sum())
sec("surprise_consensus", P8, L8)
r1, V1, X1 = sm_fit(P, d.L, par_variable=True)
for v in ["HICP", "RGDP", "UNEM"]:
    j = list(X1.columns).index(f"c_{v}")
    out[f"c_{v}"] = r1.params[j]
    out[f"et_c_{v}_dk8"] = math.sqrt(V1[j, j])

# linearmodels : Driscoll-Kraay (noyau de Bartlett, largeur 8) sur l'echantillon principal
try:
    from linearmodels.panel import PanelOLS
    sub = d[P].copy()
    sub["entite"] = sub.variable + sub.annee_cible.astype(str)
    Xl = design(sub, d.L)
    Xl.index = pd.MultiIndex.from_arrays([sub.entite, sub.t_tour])
    yl = pd.Series(sub.ze.values, index=Xl.index)
    rl = PanelOLS(yl, Xl).fit(cov_type="kernel", kernel="bartlett", bandwidth=8, debiased=False)
    print(f"linearmodels : c = {rl.params['c']!r}, et DK = {rl.std_errors['c']!r}")
except Exception as e:  # le controle reste valable sans linearmodels
    print("linearmodels indisponible :", type(e).__name__, e)

print("\nComparaison verification.py / controle statsmodels (ecart absolu) :")
pire = 0.0
for f, x in out.items():
    e = abs(float(x) - float(ver[f]))
    pire = max(pire, e)
    print(f"  {f:32s} {ver[f]!r:>24} {float(x)!r:>24}  {e:.2e}")
print("plus grand ecart :", pire)

# ------------------------------------------------------------------------------------------------------------
# Sensibilite (hors verdict) : egalites decimales de |surprise|
# ------------------------------------------------------------------------------------------------------------
print("\nSENSIBILITE, hors verification.json : |surprise| arrondi a 1 decimale avant quantile et coupure")
La, infoA = coupe("surprise", P, arrondi=True)
print("Coupure :", infoA)
print("lignes principales dont L change :", int((La[P] != d.L[P]).sum()),
      "; tours (variable, tour) :", sorted(set(zip(d[P & (La != d.L)].variable, d[P & (La != d.L)].tour))))
ra, Va, Xa = sm_fit(P, La)
ca, eta = ra.params[-1], math.sqrt(Va[-1, -1])
wa = np.array([1 / 6 if n.startswith("b_") else 0.0 for n in Xa.columns])
bma = float(wa @ ra.params)
rv, aa, AA = rapport("zr", La)
bia = (2 * bma + k_moyen) * 0.10 * (1 / aa - 1 / AA)
seuil = max(0.10, bia)
tk = {}
ck = {}
for k in (1, 2, 3):
    rk, Vk, _ = sm_fit(P & (d.episode != f"E{k}"), La)
    ck[k], tk[k] = rk.params[-1], rk.params[-1] / math.sqrt(Vk[-1, -1])
print(f"  c = {ca:.4f} ; et_dk8 = {eta:.4f} ; IC90 = [{ca - K * eta:.4f} ; {ca + K * eta:.4f}] ; "
      f"b_moyen = {bma:.4f} ; rapport = {rv:.3f} ; biais = {bia:.4f} ; seuil = {seuil:.4f} ; "
      f"n_grands = {int((La[P] == 1).sum())}")
print("  c sans E1..E3 :", {k: round(v, 4) for k, v in ck.items()}, "; t :", {k: round(v, 3) for k, v in tk.items()})
