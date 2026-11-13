"""K20: does the under-reaction of the Philadelphia Fed SPF consensus grow after large surprises?
(preregistration sections 5-6)

Pooled over five variables, in standardised units (per variable):
  z_e = sum_v a_v D_v + sum_v d_v D_v L + sum_v b_v D_v z_r + c z_r L + u
where L = 1 for the top third of |surprise| of the variable. c is the extra slope after large surprises.
Driscoll-Kraay standard errors: scores summed by target quarter (empty quarters count), 4 lags.
"""
import math

import numpy as np
import pandas as pd

from . import stats
from . import vintages as vt
from .measures import K20_EPISODES, K20_VARIABLES, rtdsm_vintage_number

VARS = list(K20_VARIABLES)
RANGES = {"PGDP": (-10, 25), "RGDP": (-40, 40), "UNEMP": (2, 16), "CPI": (-15, 25), "TBILL": (-0.5, 20)}
LEVEL_RANGES = {"PGDP": (50, 300), "RGDP": (500, 40000), "CPI": (20, 400), "UNEMP": (2, 16), "TBILL": (-0.5, 20)}


def schema_violations(df):
    """The 12 schema checks of section 5. Returns {check number: passed}.
    Check 9 (previous level present whenever the level is) fails on one row, CPI 2026-Q1: October 2025 is
    missing in FRED, so the 2025-Q4 average is missing while the 2026-Q1 average exists. The sealed verdict
    records exactly this violation (n_violations_schema = 1, verdict 'non concluant')."""
    t = df["t_target"]
    grid = [(v, q) for v in VARS for q in range(7879 if v in ("PGDP", "RGDP", "UNEMP") else 7930, 8107)]
    no_h4 = df["variable"].isin(["PGDP", "RGDP", "UNEMP"]) & t.isin(
        [vt.quarter_number(y, q) for y, q in [(1970, 1), (1970, 2), (1970, 3), (1971, 1), (1975, 3)]])
    ok = {1: len(df.columns) == 28,
          2: list(zip(df["variable"], t)) == grid,
          3: (df["target"] == t.map(vt.quarter_label)).all() and (df["year"] == t // 4).all()
             and (df["t_survey_h3"] == t - 3).all() and (df["t_survey_h4"] == t - 4).all(),
          4: (df["f_h4"].isna() == no_h4).all() and (df["f_h4_med"].isna() == no_h4).all()
             and df[["f_h3", "f_h3_med", "nowcast_q4"]].notna().all().all()}
    c5 = True
    qn = vt.quarter_number
    # first release one quarter after the target, two quarters after for 1995Q4, 2025Q3, 2025Q4 (shutdowns);
    # for the surprise quarter t-4 the late targets are therefore 1996Q4 and 2026Q3
    for col_v, col_a, shift, late in (("outturn_vintage", "outturn", 1, {qn(1995, 4), qn(2025, 3), qn(2025, 4)}),
                                      ("outturn_vintage_q4", "outturn_q4", -3, {qn(1996, 4), qn(2026, 3)})):
        for v, q, code, a in zip(df["variable"], t, df[col_v], df[col_a]):
            if pd.isna(a):
                continue
            if v in ("PGDP", "RGDP"):
                prefix = {"PGDP": "P", "RGDP": "ROUTPUT"}[v]
                c5 &= code.startswith(prefix) and rtdsm_vintage_number(code) == q + shift + (q in late)
            else:
                c5 &= code == "FRED"
    ok[5] = c5
    c6 = True
    for v in VARS:
        s = df[df["variable"] == v]
        lo, hi = RANGES[v]
        c6 &= s[["f_h3", "f_h4", "nowcast_q4", "f_h3_med", "f_h4_med", "outturn", "outturn_q4"]].stack().dropna().between(lo, hi).all()
        lo, hi = LEVEL_RANGES[v]
        c6 &= s[["level", "level_before", "level_q4", "level_before_q4"]].stack().dropna().between(lo, hi).all()
    ok[6] = bool(c6)
    growth = df["variable"].isin(["PGDP", "RGDP", "CPI"])
    c7 = True
    for a, lvl, before in (("outturn", "level", "level_before"), ("outturn_q4", "level_q4", "level_before_q4")):
        calc = np.where(growth, 100 * ((df[lvl] / df[before]) ** 4 - 1), df[lvl])
        c7 &= ((df[a] - calc).abs().fillna(0) < 1e-6).all() and (df[a].isna() == np.isnan(calc)).all()
    for d, a, b in (("revision", "f_h3", "f_h4"), ("error", "outturn", "f_h3"), ("surprise", "outturn_q4", "nowcast_q4"),
                    ("revision_med", "f_h3_med", "f_h4_med"), ("error_med", "outturn", "f_h3_med")):
        c7 &= ((df[d] - (df[a] - df[b])).abs().fillna(0) < 1e-6).all() and (df[d].isna() == (df[a].isna() | df[b].isna())).all()
    ok[7] = bool(c7)
    prev = df.set_index(["variable", "t_target"])
    c8 = True
    for v, q, a4, m4 in zip(df["variable"], t, df["outturn_q4"], df["outturn_vintage_q4"]):
        if (v, q - 4) in prev.index:
            a, m = prev.at[(v, q - 4), "outturn"], prev.at[(v, q - 4), "outturn_vintage"]
            c8 &= (pd.isna(a) or pd.isna(a4) or abs(a - a4) < 1e-6) and (m == "" or m4 == "" or m == m4)
    ok[8] = bool(c8)
    level_only = df["variable"].isin(["UNEMP", "TBILL"])
    ok[9] = bool(df.loc[level_only, ["level_before", "level_before_q4"]].isna().all().all()
                 and not (growth & df["level"].notna() & df["level_before"].isna()).any()
                 and not (growth & df["level_q4"].notna() & df["level_before_q4"].isna()).any())
    complete = df[["revision", "error", "surprise"]].notna().all(axis=1).astype(int)
    pandemic = df["variable"].isin(["RGDP", "UNEMP"]) & t.between(8080, 8087)
    ok[10] = (df["complete"] == complete).all() and (df["main"] == ((complete == 1) & ~pandemic).astype(int)).all()
    episode = pd.Series("", index=df.index)
    for name, (lo, hi) in K20_EPISODES.items():
        episode[t.between(lo, hi)] = name
    ok[11] = (df["episode"] == episode).all()
    c12 = (df["large"].isna() == df["surprise"].isna()).all()
    for v in VARS:
        cut = np.quantile(np.abs(df.loc[(df["variable"] == v) & (df["main"] == 1), "surprise"]), 2 / 3)
        s = df[(df["variable"] == v) & df["surprise"].notna()]
        c12 &= (s["large"] == (np.abs(s["surprise"]) > cut)).all()
    ok[12] = bool(c12)
    return ok


def standardise(df):
    """Step 1: per variable, standardise revision and error (and their median versions) with the mean and
    standard deviation (n-1) of the main rows; every row of the variable gets these constants. Returns a copy
    with columns z_r, z_e, z_r_med, z_e_med and the table of constants."""
    out = df.copy()
    consts = {}
    for v in VARS:
        mv = out["variable"] == v
        main = mv & (out["main"] == 1)
        for col, z in (("revision", "z_r"), ("error", "z_e"), ("revision_med", "z_r_med"), ("error_med", "z_e_med")):
            m, s = out.loc[main, col].mean(), out.loc[main, col].std(ddof=1)
            out.loc[mv, z] = (out.loc[mv, col] - m) / s
            consts[(v, col)] = s
    return out, consts


def design(D, zr="z_r", large="large", by_variable=False):
    """Regressors in the preregistered order: 5 constants, 5 class effects, 5 base slopes, then c
    (or one c per variable when by_variable)."""
    dv = [(D["variable"] == v).astype(float).values for v in VARS]
    cols = dv + [d * D[large].values for d in dv] + [d * D[zr].values for d in dv]
    cols += [d * D[zr].values * D[large].values for d in dv] if by_variable else [D[zr].values * D[large].values]
    return np.column_stack(cols)


def regress(D, zr="z_r", ze="z_e", large="large", by_variable=False, lags=(4,)):
    """Step 3-4: OLS and Driscoll-Kraay covariances (scores summed by target quarter). Returns a dict."""
    D = D.dropna(subset=[zr, ze, large])
    X = design(D, zr, large, by_variable)
    beta, u, _ = stats.ols(X, D[ze].values)
    out = {"beta": beta, "n": len(D), "iid": stats.iid_cov(X, u)}
    for L in lags:
        out[L] = stats.driscoll_kraay_cov(X, u, D["t_target"].values, L)
    return out


def c_and_se(R, j=15, lags=4):
    return float(R["beta"][j]), math.sqrt(R[lags][j, j])


def run(df):
    out = {"n_violations_schema": sum(not ok for ok in schema_violations(df).values())}
    d, consts = standardise(df)
    base = d[d["main"] == 1].copy()
    out["n_principal"] = len(base)
    R = regress(base, lags=(4, 8, 0))
    c, se = c_and_se(R)
    lo, hi = c - 1.645 * se, c + 1.645 * se
    b_mean = float(np.mean(R["beta"][10:15]))
    k_mean = float(np.mean([consts[(v, "revision")] / consts[(v, "error")] for v in VARS]))
    out.update(c=c, et_c_dk4=se, t_c=c / se, borne_basse_ic90=lo, borne_haute_ic90=hi)
    # mechanical-bias fields: within-class variances of z_r around the class mean of each variable
    dev = base["z_r"] - base.groupby(["variable", "large"])["z_r"].transform("mean")
    a, A = float(np.mean(dev[base["large"] == 0] ** 2)), float(np.mean(dev[base["large"] == 1] ** 2))
    bias = (2 * b_mean + k_mean) * 0.10 * (1 / a - 1 / A)
    floor = max(0.10, bias)
    out.update(rapport_variance_revision=A / a, b_moyen=b_mean, k_moyen=k_mean, pente_moyenne_grandes=b_mean + c,
               biais_mecanique_nu20=bias, seuil_survie_bas=floor, borne_basse_moins_seuil=lo - floor,
               marge_indecision=min(floor - lo, hi - 0.40))
    without = {}
    for k, (name, (w0, w1)) in enumerate(K20_EPISODES.items(), start=1):
        ck, sk = c_and_se(regress(base[~base["t_target"].between(w0, w1)]))
        without[k] = (ck, ck / sk)
    t_min = min(tk for _, tk in without.values())
    out.update(t_min_sans_episode=t_min, c_min_sans_episode=min(ck for ck, _ in without.values()),
               episode_t_min=min(k for k, (_, tk) in without.items() if tk == t_min))
    out["conflit_robustesse"] = int(lo > floor and hi >= 0.40 and t_min < 1 and out["c_min_sans_episode"] > 0)
    se_iid = math.sqrt(R["iid"][15, 15])
    out.update(n_grands=int((base["large"] == 1).sum()), n_trimestres=base["t_target"].nunique(),
               n_trimestres_grands=base.loc[base["large"] == 1, "t_target"].nunique(), et_c_iid=se_iid,
               n_effectif=len(base) * (se_iid / se) ** 2)
    for k in without:
        out[f"c_sans_E{k}"] = without[k][0]
    out["et_c_dk8"], out["et_c_dk0"] = c_and_se(R, lags=8)[1], c_and_se(R, lags=0)[1]
    out["c_avec_pandemie"], out["et_c_avec_pandemie_dk4"] = c_and_se(regress(d[d["complete"] == 1]))
    out["c_depuis_1985"], out["et_c_depuis_1985_dk4"] = c_and_se(regress(base[base["t_target"] >= 7940]))
    out["c_avant_2020"], out["et_c_avant_2020_dk4"] = c_and_se(regress(base[base["t_target"] <= 8079]))
    out["c_mediane"], out["et_c_mediane_dk4"] = c_and_se(regress(base, zr="z_r_med", ze="z_e_med"))
    base["large_revision"] = (np.abs(base["z_r"]) > 1).astype(float)
    out["c_coupure_revision"], out["et_c_coupure_revision_dk4"] = c_and_se(regress(base, large="large_revision"))
    R1 = regress(base, by_variable=True)
    for i, v in enumerate(VARS):
        out[f"c_{v}"], out[f"et_c_{v}_dk4"] = c_and_se(R1, 15 + i)
    # descriptive: base slope b_v and large-surprise slope b_v + c_v per variable (figure 5)
    per_var = pd.DataFrame({"variable": VARS, "b_small": R1["beta"][10:15], "c": R1["beta"][15:20],
                            "se_small": np.sqrt(np.diag(R1[4])[10:15]),
                            "se_large": [math.sqrt(R1[4][10 + i, 10 + i] + R1[4][15 + i, 15 + i]
                                                   + 2 * R1[4][10 + i, 15 + i]) for i in range(5)]})
    per_var["b_large"] = per_var["b_small"] + per_var["c"]
    return out, {"per_variable": per_var, "without_episode": without, "data": d}
