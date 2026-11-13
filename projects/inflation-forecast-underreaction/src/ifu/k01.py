"""K01: do individual ECB SPF forecasters over-react to their own news? (preregistration sections 6-7)

Pooled regression of error on revision (annual HICP targets, current and next year), one constant per
horizon, no time effects. The revision of target y is instrumented by the same forecaster's revision, in
the same round, of the other target year (2SLS, one instrument). Standard errors are Driscoll-Kraay:
scores summed by survey round, Newey-West with 8 lags. Critical value 1.714 (Student, 23 df).
Descriptive: naive OLS, within-round naive slope (mechanically negative), consensus and ECB staff slopes.
"""
import math

import numpy as np
import pandas as pd

from . import stats
from .measures import K01_VINTAGES

C = 1.714
LAGS = 8


def schema_violations(df):
    """The 12 schema checks of section 6 (columns, keys, rounds, targets, vintages, values, look-ups,
    differences, outturn, sample flags). Returns {check number: passed}."""
    spf, bce = df["source"] == "SPF", df["source"] == "BCE"
    year, q = df["round"].str[:4].astype(int), df["round"].str[-1].astype(int)
    lookup = dict(zip(zip(df["source"], df["forecaster"], df["t_round"], df["target_year"]), df["forecast"]))

    def same(col, keys):
        expected = np.array([lookup.get(k, np.nan) if k is not None else np.nan for k in keys])
        obs = df[col].values
        return bool(np.all((np.isnan(obs) & np.isnan(expected)) | (np.abs(obs - expected) < 1e-12)))

    first = df["t_round"] == 8007
    other = df["other_target"]
    usable = (spf & df["horizon"].isin([0, 1]) & df["t_round"].between(8008, 8103) & df["revision"].notna()
              & df["instrument"].notna() & df["error"].notna())
    n_rounds = df[usable].groupby("forecaster")["t_round"].nunique()
    ok = {
        1: len(df.columns) == 22,
        2: not df.duplicated(["source", "forecaster", "t_round", "target_year"]).any()
           and df.loc[spf, "forecaster"].str.fullmatch(r"\d{3}").all() and (df.loc[bce, "forecaster"] == "BCE").all(),
        3: (df["t_round"] == 4 * year + q - 1).all() and df["t_round"].between(8007, 8103).all()
           and set(df.loc[spf, "t_round"]) == set(range(8007, 8104)) == set(df.loc[bce, "t_round"]),
        4: (df["horizon"] == df["target_year"] - year).all() and df["horizon"].isin([0, 1, 2]).all()
           and (df["rank"] == df["t_round"] - 4 * (df["target_year"] - 1) + 1).all(),
        5: (bce.sum() == 3 * len(K01_VINTAGES) and set(df.loc[bce, "vintage"]) == set(K01_VINTAGES)
            and (df.loc[bce, "vintage"].str[0].map({"W": 1, "G": 2, "S": 3, "A": 4}) == q[bce]).all()
            and (2000 + df.loc[bce, "vintage"].str[1:].astype(int) == year[bce]).all()
            and (df.loc[bce, "title_month"] == 3 * q[bce]).all() and (df.loc[bce, "title_year"] == year[bce]).all()
            and (df.loc[spf, "vintage"] == "").all() and df.loc[spf, "title_month"].isna().all()),
        6: (df.loc[bce, "status"] == "F").all(),
        7: df["forecast"].between(-5, 15).all() and (df["outturn"].isna() == (df["target_year"] > 2025)).all()
           and df["outturn"].dropna().between(-5, 15).all(),
        8: same("prev_forecast", [None if f else (s, i, t - 1, y) for s, i, t, y, f in
                                  zip(df["source"], df["forecaster"], df["t_round"], df["target_year"], first)]),
        9: same("other_forecast", [None if np.isnan(o) else (s, i, t, int(o)) for s, i, t, o in
                                   zip(df["source"], df["forecaster"], df["t_round"], other)])
           and same("other_prev_forecast", [None if (np.isnan(o) or f) else (s, i, t - 1, int(o)) for s, i, t, o, f in
                                            zip(df["source"], df["forecaster"], df["t_round"], other, first)]),
        10: all(((df[c] - (df[a] - df[b])).abs().fillna(0) < 1e-9).all()
                and (df[c].isna() == (df[a].isna() | df[b].isna())).all()
                for c, a, b in [("revision", "forecast", "prev_forecast"), ("instrument", "other_forecast",
                                "other_prev_forecast"), ("error", "outturn", "forecast")]),
        11: (df.groupby("target_year")["outturn"].nunique(dropna=False) == 1).all(),
        12: (df.loc[spf, "n_complete_rounds"] == df.loc[spf, "forecaster"].map(n_rounds).fillna(0)).all()
            and (df["iv_sample"] == (usable & (df["n_complete_rounds"] >= 8)).astype(int)).all(),
    }
    return ok


def iv_fields(E, demeaned=None):
    """Steps 1-8 on sample E. `demeaned` = (e, x, z) already residualised, else demeaned by horizon."""
    if demeaned is None:
        demeaned = [stats.demean_by(E[c], E["horizon"]) for c in ("error", "revision", "instrument")]
    e, x, z = demeaned
    return stats.iv_2sls(e, x, z, E["t_round"].values, LAGS, E["target_year"].values)


def fe_residuals(E, cols):
    """Residuals of each column on forecaster dummies and a horizon-1 dummy (fixed effects)."""
    D = pd.get_dummies(E["forecaster"]).astype(float).values
    X = np.column_stack([D, (E["horizon"].values == 1).astype(float)])
    return [stats.residualise(E[c].values, X) for c in cols]


def aggregate_cells(df):
    """Consensus and ECB staff cells (round t, target y): 8008 <= t <= 8103, y = round year or next, y <= 2025.
    Consensus = mean forecast of all SPF rows of the cell; its revision uses the consensus of round t-1."""
    spf = df[df["source"] == "SPF"]
    cons = spf.groupby(["t_round", "target_year"])["forecast"].mean()
    outturn = df.dropna(subset=["outturn"]).groupby("target_year")["outturn"].first()
    rows = []
    for (t, y), c in cons.items():
        h = y - t // 4
        if 8008 <= t <= 8103 and h in (0, 1) and y <= 2025 and (t - 1, y) in cons.index and y in outturn.index:
            rows.append({"t_round": t, "target_year": y, "horizon": h, "revision": c - cons[(t - 1, y)],
                         "error": outturn[y] - c})
    consensus = pd.DataFrame(rows)
    b = df[(df["source"] == "BCE") & df["t_round"].between(8008, 8103) & df["horizon"].isin([0, 1])
           & (df["target_year"] <= 2025)].dropna(subset=["revision", "error"])
    return consensus, b[["t_round", "target_year", "horizon", "revision", "error"]].reset_index(drop=True)


def aggregate_slope(D):
    """OLS slope of error on revision with one constant per horizon, Driscoll-Kraay (8 lags) by round.
    Returns (b, se, per-row scores / sum x^2 for the difference test)."""
    if len(D) < 20:
        return 0.0, 0.0, None
    e, x = stats.demean_by(D["error"], D["horizon"]), stats.demean_by(D["revision"], D["horizon"])
    b, se, score = stats.slope_dk(e, x, x, D["t_round"].values, LAGS)
    return b, se, score / np.sum(x * x)


def run(df):
    out = {"n_violations_schema": sum(not ok for ok in schema_violations(df).values())}
    E = df[df["iv_sample"] == 1].reset_index(drop=True)
    out.update(n_obs_iv=len(E), n_previsionnistes_iv=E["forecaster"].nunique(), n_tours_iv=E["t_round"].nunique())
    r = iv_fields(E)
    lo, hi = r["b"] - C * r["se"], r["b"] + C * r["se"]
    out.update(b_iv=r["b"], et_b_iv_dk8=r["se"], t_iv=r["t"], borne_basse_ic90=lo, borne_haute_ic90=hi,
               marge_indecision=min(-0.15 - lo, hi), coef_premiere_etape=r["pi"], f_premiere_etape=r["F"],
               t_forme_reduite=r["t_rf"], et_b_iv_grappes_tour=r["se_cluster_period"],
               et_b_iv_grappes_cible=r["se_cluster_year"])
    Ep = E[~E["target_year"].isin([2021, 2022, 2023])].reset_index(drop=True)
    rp = iv_fields(Ep)
    out.update(n_obs_iv_hors_2021_2023=len(Ep), b_iv_hors_2021_2023=rp["b"], et_b_iv_hors_2021_2023_dk8=rp["se"],
               borne_haute_ic90_hors_2021_2023=rp["b"] + C * rp["se"], f_premiere_etape_hors_2021_2023=rp["F"])
    out["conflit_episode"] = int(hi >= 0 and out["borne_haute_ic90_hors_2021_2023"] < 0)
    drop_one = {y: iv_fields(E[E["target_year"] != y].reset_index(drop=True))["b"] for y in range(2002, 2026)}
    out["b_iv_max_sans_une_annee"] = max(drop_one.values())
    rfe = iv_fields(E, fe_residuals(E, ["error", "revision", "instrument"]))
    out.update(b_iv_ef_prev=rfe["b"], et_b_iv_ef_prev_dk8=rfe["se"])
    # naive pooled OLS (z = x)
    e, x = stats.demean_by(E["error"], E["horizon"]), stats.demean_by(E["revision"], E["horizon"])
    b_ols, se_ols, _ = stats.slope_dk(e, x, x, E["t_round"].values, LAGS)
    out.update(b_mco_naif=b_ols, et_b_mco_naif_dk8=se_ols)
    # naive within-round slope: demean by (round, target) cell, cluster by round
    cell = E["t_round"].astype(str) + "_" + E["target_year"].astype(str)
    ew, xw = stats.demean_by(E["error"], cell), stats.demean_by(E["revision"], cell)
    b_w, _, score_w = stats.slope_dk(ew, xw, xw, E["t_round"].values, 0)
    out.update(b_intra_tour_naif=b_w, et_b_intra_tour_naif_grappes_tour=math.sqrt(
        stats.bartlett_lrv(score_w, E["t_round"].values, 0)) / np.sum(xw * xw))
    n = len(E)
    out["sigma_bruit_necessaire_mco"] = math.sqrt(max(0.0, -b_ols) * np.sum(x * x) / n)
    out["sigma_bruit_commun_necessaire_iv"] = math.sqrt(max(0.0, -r["b"]) * max(0.0, r["szx"] / n))
    Ea = E[E["target_year"] <= 2019].reset_index(drop=True)
    ra = iv_fields(Ea)
    out.update(n_obs_avant_2020=len(Ea), b_iv_avant_2020=ra["b"], et_b_iv_avant_2020_dk8=ra["se"])
    ea, xa = fe_residuals(Ea, ["error", "revision"])
    b_fe, se_fe, _ = stats.slope_dk(ea, xa, xa, Ea["t_round"].values, LAGS)
    out.update(b_mco_ef_avant_2020=b_fe, et_b_mco_ef_avant_2020_dk8=se_fe)
    # consensus and ECB staff
    cons, ecb = aggregate_cells(df)
    bc, sc, wc = aggregate_slope(cons)
    bb, sb, wb = aggregate_slope(ecb)
    out.update(n_consensus=len(cons), b_consensus=bc, et_b_consensus_dk8=sc, n_bce=len(ecb), b_bce=bb,
               et_b_bce_dk8=sb, diff_bce_moins_consensus=bb - bc)
    psi = np.concatenate([wb, -wc])
    out["et_diff_dk8"] = math.sqrt(stats.bartlett_lrv(psi, np.concatenate([ecb["t_round"], cons["t_round"]]), LAGS))
    no_ep = lambda D: D[~D["target_year"].isin([2021, 2022, 2023])].reset_index(drop=True)
    out["b_consensus_hors_2021_2023"] = aggregate_slope(no_ep(cons))[0]
    out["b_bce_hors_2021_2023"] = aggregate_slope(no_ep(ecb))[0]
    return out, {"drop_one_year": drop_one, "slopes": slope_table(E, cons, ecb)}


def slope_table(E, cons, ecb):
    """Descriptive table for figure 4: each slope with its Driscoll-Kraay se (8 lags; within-round: clustered
    by round), on the full sample and without target years 2021-2023."""
    rows = []
    for label, keep in (("full sample", lambda D: D), ("excluding 2021-2023",
                        lambda D: D[~D["target_year"].isin([2021, 2022, 2023])].reset_index(drop=True))):
        S = keep(E)
        r = iv_fields(S)
        e, x = stats.demean_by(S["error"], S["horizon"]), stats.demean_by(S["revision"], S["horizon"])
        b_ols, se_ols, _ = stats.slope_dk(e, x, x, S["t_round"].values, LAGS)
        cell = S["t_round"].astype(str) + "_" + S["target_year"].astype(str)
        ew, xw = stats.demean_by(S["error"], cell), stats.demean_by(S["revision"], cell)
        b_w, se_w, _ = stats.slope_dk(ew, xw, xw, S["t_round"].values, 0)
        bc, sc, _ = aggregate_slope(keep(cons))
        bb, sb, _ = aggregate_slope(keep(ecb))
        for name, b, se in (("Individuals, 2SLS (preregistered)", r["b"], r["se"]),
                            ("Individuals, naive pooled OLS", b_ols, se_ols),
                            ("Individuals, naive within-round", b_w, se_w),
                            ("SPF consensus", bc, sc), ("ECB staff", bb, sb)):
            rows.append({"sample": label, "estimate": name, "b": b, "se": se})
    return pd.DataFrame(rows)
