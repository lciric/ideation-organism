#!/usr/bin/env python3
"""K20-LIV -- contrôle croisé du vérificateur, par une seconde implémentation indépendante de verification.py.

- lecture du fichier par pandas (et non par le module csv) ;
- matrices de régression construites par pandas ;
- coefficients et écarts-types de Driscoll-Kraay calculés par statsmodels (cov_type='hac-groupsum', sans correction)
  et par linearmodels (PanelOLS, cov_type='kernel', Bartlett, debiased=False).
  Ces deux bibliothèques comptent les retards par position dans la suite des dates présentes. Pour obtenir des
  retards en semestres calendaires (section 6, étape 4), on ajoute, pour chaque semestre vide entre le plus petit et le
  plus grand semestre de l'échantillon, une ligne nulle (X = 0, y = 0) : elle n'entre ni dans X'X ni dans les scores.
- les champs dérivés sont recalculés ici et comparés à verification.json.
Aucun autre fichier n'est lu. Usage : python3 -B verification_controle.py
"""
import json
import pathlib
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

warnings.filterwarnings("ignore")
ICI = pathlib.Path(__file__).resolve().parent
VARS = ["CPI", "UNPR", "PRIME", "TBILL", "TPHS"]
FEN = {"E1": ("1948-11", "1950-12"), "E2": ("1953-07", "1955-07"), "E3": ("1957-08", "1959-06"),
       "E4": ("1960-04", "1962-04"), "E5": ("1969-12", "1972-01"), "E6": ("1973-11", "1976-05"),
       "E7": ("1980-01", "1984-01"), "E8": ("1990-07", "1992-05"), "E9": ("2001-03", "2003-01"),
       "E10": ("2007-12", "2010-08"), "E11": ("2020-02", "2023-12")}

df = pd.read_csv(ICI / "K20-LIV_analyse.csv", float_precision="round_trip", keep_default_na=False,
                 na_values={c: [""] for c in []})
num = [c for c in df.columns if c not in ("variable", "cible", "enquete_1", "enquete_2", "mois_ancre_1", "mois_ancre_2",
                                          "serie_realise", "jour_realise", "jour_ancre_1", "jour_ancre_2", "episode")]
for c in num:
    df[c] = pd.to_numeric(df[c].replace("", np.nan))
df["cible_p"] = pd.PeriodIndex(df["cible"], freq="M")

# principal recalculé par une autre écriture de la définition
complete = df[["revision", "erreur", "surprise"]].notna().all(axis=1)
pand = (df["variable"] == "UNPR") & df["cible"].isin(["2020-06", "2020-12", "2021-06", "2021-12"])
princ = complete & (df["n_rep_1"] >= 2) & (df["n_rep_2"] >= 2) & df["var_rep_1"].notna() & df["var_rep_2"].notna() & ~pand
assert (princ.astype(int) == df["principal"]).all()
P = df[princ].copy()

# réduction
g = P.groupby("variable")
stats = pd.DataFrame({"mr": g["revision"].mean(), "sr": g["revision"].std(ddof=1),
                      "me": g["erreur"].mean(), "se": g["erreur"].std(ddof=1),
                      "mrm": g["revision_med"].mean(), "srm": g["revision_med"].std(ddof=1),
                      "mem": g["erreur_med"].mean(), "sem": g["erreur_med"].std(ddof=1)})
d = df.join(stats, on="variable")
df["zr"] = (d["revision"] - d["mr"]) / d["sr"]
df["ze"] = (d["erreur"] - d["me"]) / d["se"]
df["zrm"] = (d["revision_med"] - d["mrm"]) / d["srm"]
df["zem"] = (d["erreur_med"] - d["mem"]) / d["sem"]
Q = P.assign(a=P["surprise"].abs()).groupby("variable")["a"].quantile(2 / 3, interpolation="linear")
df["L"] = np.where(df["surprise"].notna(), (df["surprise"].abs() > df["variable"].map(Q)).astype(float), np.nan)
df["Lp"] = (df["zr"].abs() > 1).astype(float)
P = df[princ].copy()
kv = (stats["sr"] / stats["se"]).reindex(VARS)


def X16(t, L="L", zr="zr"):
    D = pd.get_dummies(t["variable"]).reindex(columns=VARS, fill_value=0).astype(float)
    cols = {f"a_{v}": D[v] for v in VARS}
    cols.update({f"d_{v}": D[v] * t[L] for v in VARS})
    cols.update({f"b_{v}": D[v] * t[zr] for v in VARS})
    cols["c"] = t[zr] * t[L]
    return pd.DataFrame(cols, index=t.index)


def X20(t):
    X = X16(t).drop(columns="c")
    D = pd.get_dummies(t["variable"]).reindex(columns=VARS, fill_value=0).astype(float)
    for v in VARS:
        X[f"c_{v}"] = D[v] * t["zr"] * t["L"]
    return X


def X6(t):
    D = pd.get_dummies(t["variable"]).reindex(columns=VARS, fill_value=0).astype(float)
    X = pd.DataFrame({f"a_{v}": D[v] for v in VARS}, index=t.index)
    X["b"] = t["zr"]
    return X


def avec_lignes_nulles(y, X, sem):
    """Ajoute une ligne nulle par semestre vide entre min et max (retards calendaires)."""
    tous = np.arange(sem.min(), sem.max() + 1)
    vides = np.setdiff1d(tous, sem.unique())
    if len(vides) == 0:
        return y.to_numpy(), X.to_numpy(), sem.to_numpy(), 0
    Xz = np.zeros((len(vides), X.shape[1]))
    return (np.concatenate([y.to_numpy(), np.zeros(len(vides))]), np.vstack([X.to_numpy(), Xz]),
            np.concatenate([sem.to_numpy(), vides]), len(vides))


def sm_dk(t, X, y="ze", lags=2, nom="c"):
    yy, XX, ss, nv = avec_lignes_nulles(t[y], X, t["semestre"])
    # Codes de temps 0, 1, ... (semestre - minimum) : avec les codes bruts (3895 à 4052 > 2n), statsmodels renumérote
    # par pd.factorize, dans l'ordre de première apparition, ce qui mélange l'ordre des semestres.
    ss = ss - ss.min()
    j = list(X.columns).index(nom)
    if lags == 0:
        r = sm.OLS(yy, XX).fit(cov_type="cluster", cov_kwds={"groups": ss, "use_correction": False,
                                                             "df_correction": False})
    else:
        r = sm.OLS(yy, XX).fit(cov_type="hac-groupsum", cov_kwds={"time": ss, "maxlags": lags,
                                                                  "use_correction": False})
    return float(r.params[j]), float(np.sqrt(r.cov_params()[j, j])), nv


def lm_dk(t, X, y="ze", lags=2, nom="c"):
    from linearmodels.panel import PanelOLS
    yy, XX, ss, nv = avec_lignes_nulles(t[y], X, t["semestre"])
    ent = np.concatenate([t["variable"].to_numpy(), np.array(["PAD"] * nv)])
    idx = pd.MultiIndex.from_arrays([ent, ss], names=["entite", "temps"])
    Y = pd.Series(yy, index=idx, name="y")
    XD = pd.DataFrame(XX, index=idx, columns=X.columns)
    m = PanelOLS(Y, XD, check_rank=False)
    if lags == 0:
        r = m.fit(cov_type="clustered", cluster_time=True, debiased=False, group_debias=False)
    else:
        r = m.fit(cov_type="kernel", kernel="bartlett", bandwidth=lags, debiased=False)
    return float(r.params[nom]), float(r.std_errors[nom])


ver = json.loads((ICI / "verification.json").read_text())
moi = {}

# principal
X = X16(P)
moi["c"], moi["et_c_dk2"], _ = sm_dk(P, X)
lm_c, lm_et = lm_dk(P, X)
_, moi["et_c_dk4"], _ = sm_dk(P, X, lags=4)
_, moi["et_c_dk0"], _ = sm_dk(P, X, lags=0)
_, lm_et4 = lm_dk(P, X, lags=4)
_, lm_et0 = lm_dk(P, X, lags=0)
ols = sm.OLS(P["ze"].to_numpy(), X.to_numpy()).fit()
moi["et_c_iid"] = float(ols.bse[-1])
moi["b_moyen"] = float(np.mean(ols.params[10:15]))
moi["k_moyen"] = float(kv.mean())
moi["pente_moyenne_grandes"] = moi["b_moyen"] + moi["c"]
moi["t_c"] = moi["c"] / moi["et_c_dk2"]
moi["borne_basse_ic90"] = moi["c"] - 1.645 * moi["et_c_dk2"]
moi["borne_haute_ic90"] = moi["c"] + 1.645 * moi["et_c_dk2"]
moi["n_principal"] = int(len(P))
moi["n_effectif"] = len(P) * (moi["et_c_iid"] / moi["et_c_dk2"]) ** 2
moi["n_grands"] = int(P["L"].sum())
moi["n_dates"] = int(P["semestre"].nunique())
moi["n_dates_grands"] = int(P.loc[P["L"] == 1, "semestre"].nunique())

# contrôle positif
moi["b_regroupe"], moi["et_b_regroupe_dk2"], _ = sm_dk(P, X6(P), nom="b")
lm_b, lm_eb = lm_dk(P, X6(P), nom="b")
moi["borne_basse_b_ic90"] = moi["b_regroupe"] - 1.645 * moi["et_b_regroupe_dk2"]
moi["controle_positif_ok"] = int(moi["borne_basse_b_ic90"] > 0 or moi["borne_haute_ic90"] < 0)

# biais mécanique : moyennes regroupées
P["m"] = P.groupby(["variable", "L"])["zr"].transform("mean")
dev = (P["zr"] - P["m"]) ** 2
a = dev[P["L"] == 0].mean()
A = dev[P["L"] == 1].mean()
moi["rapport_variance_revision"] = float(A / a)
P["nu"] = (P["var_rep_1"] / P["n_rep_1"] + P["var_rep_2"] / P["n_rep_2"]) / P["variable"].map(stats["sr"] ** 2)
moi["nu_mesure"] = float(P.groupby("variable")["nu"].median().reindex(VARS).mean())
f = (2 * moi["b_moyen"] + moi["k_moyen"]) * (1 / a - 1 / A)
moi["biais_mecanique_mesure"] = float(f * moi["nu_mesure"])
moi["biais_mecanique_nu20"] = float(f * 0.10)
moi["seuil_survie_bas"] = max(0.10, moi["biais_mecanique_mesure"])
moi["borne_basse_moins_seuil"] = moi["borne_basse_ic90"] - moi["seuil_survie_bas"]
moi["marge_indecision"] = min(moi["seuil_survie_bas"] - moi["borne_basse_ic90"], moi["borne_haute_ic90"] - 0.40)

# épisodes
tk, lm_tk = {}, {}
for k in range(1, 12):
    lo, hi = (pd.Period(x, freq="M") for x in FEN[f"E{k}"])
    S = P[~((P["cible_p"] >= lo) & (P["cible_p"] <= hi))]
    ck, ek, nv = sm_dk(S, X16(S))
    moi[f"c_sans_E{k}"] = ck
    tk[k] = ck / ek
    lc, le = lm_dk(S, X16(S))
    lm_tk[k] = lc / le
moi["t_min_sans_episode"] = min(tk.values())
moi["episode_t_min"] = min(k for k in tk if tk[k] == moi["t_min_sans_episode"])
moi["c_min_sans_episode"] = min(moi[f"c_sans_E{k}"] for k in range(1, 12))
moi["conflit_robustesse"] = int(moi["borne_basse_ic90"] > moi["seuil_survie_bas"] and moi["borne_haute_ic90"] >= 0.40
                                and moi["t_min_sans_episode"] < 1 and moi["c_min_sans_episode"] > 0)

# secondaires
X2 = X20(P)
for v in VARS:
    moi[f"c_{v}"], moi[f"et_c_{v}_dk2"], _ = sm_dk(P, X2, nom=f"c_{v}")
S3 = df[princ | (pand & complete)]
moi["c_avec_pandemie"], moi["et_c_avec_pandemie_dk2"], _ = sm_dk(S3, X16(S3))
S4 = P[P["cible_p"] >= pd.Period("1985-06", freq="M")]
moi["c_depuis_1985"], moi["et_c_depuis_1985_dk2"], _ = sm_dk(S4, X16(S4))
S5 = P[P["cible_p"] <= pd.Period("2019-12", freq="M")]
moi["c_avant_2020"], moi["et_c_avant_2020_dk2"], _ = sm_dk(S5, X16(S5))
moi["c_mediane"], moi["et_c_mediane_dk2"], _ = sm_dk(P, X16(P, zr="zrm"), y="zem")
moi["c_coupure_revision"], moi["et_c_coupure_revision_dk2"], _ = sm_dk(P, X16(P, L="Lp"))

print("Champ                          verification.py         contrôle (statsmodels)   écart")
pire = 0.0
for k, x in moi.items():
    e = abs(ver[k] - x)
    pire = max(pire, e)
    print(f"{k:30s} {ver[k]!r:24} {x!r:24} {e:.2e}")
print(f"\nÉcart maximal verification.py / statsmodels sur {len(moi)} champs : {pire:.2e}")
print("Champs de la règle non recalculés ici (comptes de schéma) :",
      [c for c in ver if c not in moi])
print("\nlinearmodels (PanelOLS, Driscoll-Kraay, debiased=False) :")
print(f"  c {lm_c!r} (écart {abs(lm_c - ver['c']):.2e}) ; et_c_dk2 {lm_et!r} (écart {abs(lm_et - ver['et_c_dk2']):.2e})")
print(f"  et_c_dk4 {lm_et4!r} (écart {abs(lm_et4 - ver['et_c_dk4']):.2e}) ; "
      f"et_c_dk0 {lm_et0!r} (écart {abs(lm_et0 - ver['et_c_dk0']):.2e})")
print(f"  b_regroupe {lm_b!r} (écart {abs(lm_b - ver['b_regroupe']):.2e}) ; "
      f"et_b_regroupe_dk2 {lm_eb!r} (écart {abs(lm_eb - ver['et_b_regroupe_dk2']):.2e})")
print(f"  t sans épisode, écart maximal : {max(abs(lm_tk[k] - tk[k]) for k in tk):.2e}")
# Pour mémoire : deux pièges de statsmodels (hac-groupsum), sur l'échantillon principal et sans E7
def sm_brut(t, codes):
    r = sm.OLS(t["ze"].to_numpy(), X16(t).to_numpy()).fit(
        cov_type="hac-groupsum", cov_kwds={"time": codes, "maxlags": 2, "use_correction": False})
    return float(r.bse[-1])
for lab, t, cle in (("principal", P, "et_c_dk2"), ("sans E7", P[P["episode"] != "E7"], None)):
    s = t["semestre"].to_numpy()
    rang = pd.Series(s).rank(method="dense").astype(int).to_numpy() - 1  # rang parmi les semestres présents
    ref = ver[cle] if cle else moi["c_sans_E7"] / tk[7]
    print(f"{lab:10s}: codes bruts {sm_brut(t, s)!r} ; rang (retards par position) {sm_brut(t, rang)!r} ; "
          f"semestre - min (retards calendaires) {sm_brut(t, s - s.min())!r} ; verification.py {ref!r}")
