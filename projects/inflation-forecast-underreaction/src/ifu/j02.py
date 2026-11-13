"""J02: full-sample slope of ECB staff projection errors on revisions at a two-quarter horizon
(preregistration sections 5-6). One observation per target quarter 1999-Q4 .. 2026-Q3.

beta_z = OLS slope of the standardised error on the standardised revision = Pearson correlation;
Newey-West standard error with 4 lags (Bartlett weights, lags counted in target quarters, no small-sample
correction). Survival guard: the correlation stays positive when any two consecutive calendar years are removed.
"""
import math

import numpy as np

from . import stats
from . import vintages as vt
from .measures import J02_VINTAGES


def schema_violations(df):
    """The 11 schema checks of section 5. Returns {check number: passed}."""
    idx = ["index_m1", "index_m2", "index_m3", "index_year_before_m1", "index_year_before_m2", "index_year_before_m3"]
    ok = {1: len(df.columns) == 26,
          2: len(df) == 108 and list(df["t_target"]) == list(range(7999, 8107)),
          3: (df["target"] == df["t_target"].map(vt.quarter_label)).all() and (df["year"] == df["t_target"] // 4).all()}
    c4 = c5 = c6 = c7 = True
    for h in (2, 3):
        code = df[f"vintage_h{h}"]
        c4 &= (df[f"t_vintage_h{h}"] == df["t_target"] - h).all() and code.isin(J02_VINTAGES).all() \
            and (code.map(vt.vintage_number) == df[f"t_vintage_h{h}"]).all()
        c5 &= (df[f"title_month_h{h}"] == 3 * code.str[0].map(vt.LETTER_QUARTER)).all() \
            and (df[f"title_year_h{h}"] == code.map(vt.code_year)).all()
        c6 &= (df[f"first_F_h{h}"] == df[f"t_vintage_h{h}"]).all()
        c7 &= (df[f"forecast_h{h}"].isna() | (df[f"status_h{h}"] == "F")).all()
    ok.update({4: c4, 5: c5, 6: c6, 7: c7})
    f = df[["forecast_h2", "forecast_h3"]].stack().dropna()
    ok[8] = (f.between(-5, 15).all() and np.allclose(f * 10, np.round(f * 10))
             and df[idx].stack().dropna().between(20, 300).all() and df["outturn"].dropna().between(-5, 15).all())
    expected = 100 * (df[idx[:3]].sum(axis=1) / df[idx[3:]].sum(axis=1) - 1)
    ok[9] = (df["outturn"].isna() == df[idx].isna().any(axis=1)).all() and \
        ((df["outturn"] - expected).abs().fillna(0) < 1e-6).all()
    ok[10] = ((df["revision"] - (df["forecast_h2"] - df["forecast_h3"])).abs().fillna(0) < 1e-6).all() and \
        ((df["error"] - (df["outturn"] - df["forecast_h2"])).abs().fillna(0) < 1e-6).all()
    by_t = df.set_index("t_target")
    ok[11] = all(by_t.at[t, f"index_year_before_m{k}"] == by_t.at[t - 4, f"index_m{k}"]
                 for t in by_t.index if t - 4 in by_t.index for k in (1, 2, 3))
    return ok


def standardised_slope(t, r, e, lags):
    """Steps 1-9 on targets t, revisions r, errors e. Returns a dict with n, beta_z, se, s_r, s_e, beta_raw,
    se_raw (zeros if n < 10 or a standard deviation is zero)."""
    n = len(r)
    s_r, s_e = (np.std(r, ddof=1), np.std(e, ddof=1)) if n > 1 else (0.0, 0.0)
    if n < 10 or s_r == 0 or s_e == 0:
        return dict(n=n, beta_z=0.0, se=0.0, s_r=0.0, s_e=0.0, beta_raw=0.0, se_raw=0.0)
    z, y = (r - r.mean()) / s_r, (e - e.mean()) / s_e
    X = np.column_stack([np.ones(n), z])
    beta, u, _ = stats.ols(X, y)
    se = math.sqrt(stats.driscoll_kraay_cov(X, u, t, lags)[1, 1])
    return dict(n=n, beta_z=beta[1], se=se, s_r=s_r, s_e=s_e, beta_raw=beta[1] * s_e / s_r, se_raw=se * s_e / s_r)


def corr_or_zero(r, e):
    return stats.pearson(r, e) if len(r) >= 10 and np.std(r) > 0 and np.std(e) > 0 else 0.0


def run(df):
    out = {"n_violations_schema": sum(not ok for ok in schema_violations(df).values())}
    c = df[df["revision"].notna() & df["error"].notna()].sort_values("t_target")
    t, yr, r, e = c["t_target"].values, c["year"].values, c["revision"].values, c["error"].values
    p = standardised_slope(t, r, e, 4)
    lo, hi = p["beta_z"] - 1.645 * p["se"], p["beta_z"] + 1.645 * p["se"]
    out.update(n_cibles=p["n"], beta_z=p["beta_z"], et_beta_z_nw4=p["se"], t_nw4=p["beta_z"] / p["se"],
               borne_basse_ic90=lo, borne_haute_ic90=hi, marge_indecision=min(-lo, hi - 0.40))
    drop_two = {Y: corr_or_zero(r[~np.isin(yr, [Y, Y + 1])], e[~np.isin(yr, [Y, Y + 1])]) for Y in range(1999, 2026)}
    out["beta_z_min_sans_deux_ans"] = min(drop_two.values())
    out["annee_debut_min"] = min(Y for Y, v in drop_two.items() if v == out["beta_z_min_sans_deux_ans"])
    out["conflit_robustesse"] = int(lo > 0 and hi >= 0.40 and out["beta_z_min_sans_deux_ans"] <= 0)
    out.update(beta_brut=p["beta_raw"], et_beta_brut_nw4=p["se_raw"], ecart_type_revision=p["s_r"],
               ecart_type_erreur=p["s_e"])
    m = t <= 8079  # S1: targets 1999-Q4 .. 2019-Q4
    p1 = standardised_slope(t[m], r[m], e[m], 4)
    out.update(n_avant_2020=p1["n"], beta_z_avant_2020=p1["beta_z"], beta_brut_avant_2020=p1["beta_raw"],
               et_beta_brut_avant_2020_nw4=p1["se_raw"])
    out["et_beta_z_nw8"] = standardised_slope(t, r, e, 8)["se"]  # S2
    out["bb_borne_basse_ic90"], out["bb_borne_haute_ic90"] = stats.moving_block_bootstrap_corr(r, e)
    m = ~((t >= 8084) & (t <= 8095))  # S3: without targets 2021-Q1 .. 2023-Q4
    p3 = standardised_slope(t[m], r[m], e[m], 4)
    out.update(n_hors_2021_2023=p3["n"], beta_z_hors_2021_2023=p3["beta_z"], et_beta_z_hors_2021_2023_nw4=p3["se"])
    drop_one = {Y: corr_or_zero(r[yr != Y], e[yr != Y]) for Y in range(1999, 2027)}
    out["beta_z_min_sans_une_annee"] = min(drop_one.values())
    extra = {"drop_two_years": drop_two, "drop_one_year": drop_one, "sample": c}
    return out, extra
