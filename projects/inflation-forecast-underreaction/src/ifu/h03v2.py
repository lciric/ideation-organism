"""H03-v2: could a recursive real-time correction rule based on revisions have predicted ECB staff
inflation projection errors? (preregistration sections 5-6)

For each complete row i (targets 2004-Q1 .. 2025-Q4, horizons 1-4) a slope b_i of error on revision is
estimated by OLS with a constant on the rows of the same horizon whose error was already known at the
vintage of row i (t_read <= t_vintage(i)), with at least 8 points. The announced correction is
c_i = b_i * revision_i (the constant is not applied). The statistic is the mean over 11 two-year blocks of
the uncentred correlation between c and the realised error.
"""
import math

import numpy as np
import pandas as pd

from . import stats
from . import vintages as vt
from .measures import H03_VINTAGES

Q95 = {11: 1.8125, 10: 1.8331, 9: 1.8595, 8: 1.8946, 7: 1.9432, 6: 2.0150, 5: 2.1318}  # Student 95%, K-1 df


def schema_violations(df):
    """The 11 schema checks of section 5, on the analysis dataset. Returns {check number: passed}."""
    t_of = {vt.vintage_number(c): c for c in H03_VINTAGES}
    index = {(v, h): f for v, h, f in zip(df["vintage"], df["horizon"], df["forecast"])}
    by_target = df.groupby("t_target").agg(n_out=("outturn", lambda x: x.nunique(dropna=False)),
                                           n_read=("t_read", lambda x: x.nunique(dropna=False)))
    read = df[df["outturn"].notna()]
    ok = {
        1: list(df.columns) == ["vintage", "t_vintage", "title_month", "first_F", "horizon", "target", "t_target",
                                "forecast", "prev_vintage", "prev_forecast", "outturn_vintage", "t_read", "outturn",
                                "revision", "error"],
        2: len(df) == 444 and not df.duplicated(["vintage", "horizon"]).any() and set(df["vintage"]) == set(H03_VINTAGES),
        3: (df["t_vintage"] == df["vintage"].map(vt.vintage_number)).all()
           and (df["t_target"] == df["t_vintage"] + df["horizon"]).all()
           and (df["target"] == df["t_target"].map(vt.quarter_label)).all(),
        4: ((df["title_month"] == 3 * df["vintage"].str[0].map(vt.LETTER_QUARTER)) | df["title_month"].isna()).all(),
        5: (df["first_F"].isna() | df["first_F"].between(df["t_vintage"] - 2, df["t_vintage"] + 1)).all(),
        6: all(one_decimal(df[c]) for c in ("forecast", "prev_forecast", "outturn")),
        7: ((df["revision"].isna() == (df["forecast"].isna() | df["prev_forecast"].isna())).all()
            and ((df["revision"] - (df["forecast"] - df["prev_forecast"])).abs().fillna(0) < 1e-6).all()
            and (df["error"].isna() == (df["outturn"].isna() | df["forecast"].isna())).all()
            and ((df["error"] - (df["outturn"] - df["forecast"])).abs().fillna(0) < 1e-6).all()),
        8: ((df["t_read"].isna() == df["outturn"].isna()).all()
            and (read["t_read"] - read["t_target"]).isin([2, 3, 4]).all() and (read["t_read"] <= 8106).all()
            and (read["t_read"].astype(int).map(t_of) == read["outturn_vintage"]).all()),
        9: all(p == ("" if v == "W99" else t_of.get(t - 1, "")) for v, t, p in
               zip(df["vintage"], df["t_vintage"], df["prev_vintage"])),
        10: (by_target["n_out"] == 1).all() and (by_target["n_read"] == 1).all(),
        11: all(_same(pf, index.get((pv, h + 1), np.nan)) for pv, h, pf in
                zip(df["prev_vintage"], df["horizon"], df["prev_forecast"]) if h <= 3 and pv),
    }
    return ok


def one_decimal(values):
    """Empty, or a number in [-5, 15] with at most one decimal (a multiple of 0.1)."""
    x = values.dropna()
    return bool(x.between(-5, 15).all() and np.allclose(x * 10, np.round(x * 10)))


def _same(a, b):
    return (np.isnan(a) and np.isnan(b)) or (not np.isnan(a) and not np.isnan(b) and abs(a - b) < 1e-9)


def apply_rule(df, revision_col="revision", first_target=8016, last_target=8103):
    """Step 2: recursive real-time slope for every complete row with target in [first_target, last_target].
    Returns the evaluated rows with columns b (slope), c (correction b * revision), n_train and block."""
    complete = df[df[revision_col].notna() & df["error"].notna()]
    out = []
    for _, row in complete.iterrows():
        if not first_target <= row["t_target"] <= last_target:
            continue
        train = complete[(complete["horizon"] == row["horizon"]) & (complete["t_read"] <= row["t_vintage"])]
        r, e = train[revision_col].values, train["error"].values
        if len(train) < 8:
            continue
        srr = np.sum((r - r.mean()) ** 2)
        if not srr > 1e-12:
            continue
        b = np.sum((r - r.mean()) * (e - e.mean())) / srr
        out.append(dict(row, rev=row[revision_col], b=b, c=b * row[revision_col], n_train=len(train),
                        block=(row["t_target"] - 8016) // 8))
    return pd.DataFrame(out)


def block_table(ev, min_rows=16):
    """Step 3-4: per two-year block k = 0..10: number of rows, validity, R_k (uncentred correlation of c and e)
    and Q_k = sum (e - c)^2 / sum e^2."""
    rows = []
    for k in range(11):
        b = ev[ev["block"] == k] if len(ev) else ev
        sc, se = float(np.sum(b["c"] ** 2)) if len(b) else 0.0, float(np.sum(b["error"] ** 2)) if len(b) else 0.0
        valid = len(b) >= min_rows and sc > 1e-12 and se > 1e-12
        rows.append({"block": k, "years": f"{2004 + 2 * k}-{2005 + 2 * k}", "n": len(b), "valid": valid,
                     "R": stats.uncentred_corr(b["c"], b["error"]) if valid else np.nan,
                     "Q": float(np.sum((b["error"] - b["c"]) ** 2)) / se if valid else np.nan})
    return pd.DataFrame(rows)


def summary(blocks):
    """Step 5: K, mean of R_k and its standard error (zeros if fewer than 5 valid blocks)."""
    valid = blocks[blocks["valid"]]
    K = len(valid)
    if K < 5:
        return K, 0.0, 0.0
    rbar, se = stats.block_mean_se(dict(zip(valid["block"], valid["R"])))
    return K, rbar, se


def run(df):
    """All 25 preregistered fields, plus tables used by the figures."""
    out = {"n_violations_schema": sum(not ok for ok in schema_violations(df).values())}
    ev = apply_rule(df)
    blocks = block_table(ev)
    K, rbar, se = summary(blocks)
    out.update(n_obs_evaluees=len(ev), n_blocs=K)
    valid = blocks[blocks["valid"]]
    if K >= 5:
        lo, hi = rbar - Q95[K] * se, rbar + Q95[K] * se
        outside = valid[~valid["block"].isin([8, 9])]["R"]
        out.update(r_moyen=rbar, et_r_moyen=se, borne_basse_ic90=lo, borne_haute_ic90=hi,
                   r_hors_episode=float(outside.mean()) if len(outside) else 0.0,
                   rapport_eqm_geo=math.exp(np.mean(np.log(np.maximum(valid["Q"], 1e-6)))))
    else:
        out.update(r_moyen=0.0, et_r_moyen=0.0, borne_basse_ic90=0.0, borne_haute_ic90=0.0, r_hors_episode=0.0,
                   rapport_eqm_geo=1.0)
    out["marge_indecision"] = min(-out["borne_basse_ic90"], out["borne_haute_ic90"] - 0.22)
    out["conflit_gardes"] = int(out["borne_basse_ic90"] > 0 and (out["r_hors_episode"] <= 0 or out["rapport_eqm_geo"] >= 1))

    # S1: the card's original test, horizon 4, vintages from 2020-Q1, no bound on the target
    s1 = apply_rule(df[df["horizon"] == 4], first_target=-10**9, last_target=10**9)
    s1 = s1[s1["t_vintage"] >= 8080].sort_values("t_vintage", kind="stable") if len(s1) else s1
    out["n_obs_h4_2020"] = len(s1)
    if len(s1):
        out["rapport_eqm_h4_2020"] = float(np.sum((s1["error"] - s1["c"]) ** 2) / np.sum(s1["error"] ** 2))
    else:
        out["rapport_eqm_h4_2020"] = 1.0
    d = (s1["error"] ** 2 - (s1["error"] - s1["c"]) ** 2).values if len(s1) else np.array([])
    out["p_dm_hln_h4_2020"] = stats.dm_hln_pvalue(d, lags=3)

    # S2: plain-language ratios
    e, c = ev["error"], ev["c"]
    out["rapport_eqm_global"] = float(np.sum((e - c) ** 2) / np.sum(e ** 2))
    keep = ~ev["t_target"].between(8084, 8091)
    out["rapport_eqm_hors_2021_2022"] = float(np.sum((e[keep] - c[keep]) ** 2) / np.sum(e[keep] ** 2))
    gain = int(np.sum(np.abs(e - c) < np.abs(e) - 1e-9))
    loss = int(np.sum(np.abs(e - c) > np.abs(e) + 1e-9))
    out["taux_amelioration"] = gain / (gain + loss) if gain + loss else 0.5
    out["part_b_positif"] = float(np.mean(ev["b"] > 0))
    for h in range(1, 5):
        bh = block_table(ev[ev["horizon"] == h], min_rows=4)
        out[f"r_moyen_h{h}"] = float(bh.loc[bh["valid"], "R"].mean()) if bh["valid"].any() else 0.0

    # S3: placebo with the revision of the same horizon made two years (8 vintages) earlier
    lag = df[["t_vintage", "horizon", "revision"]].rename(columns={"revision": "placebo_revision"})
    lag["t_vintage"] = lag["t_vintage"] + 8
    dfp = df.merge(lag, on=["t_vintage", "horizon"], how="left")
    evp = apply_rule(dfp, revision_col="placebo_revision")
    Kp, rp, sp = summary(block_table(evp))
    out.update(r_moyen_placebo=rp, et_r_placebo=sp, n_blocs_placebo=Kp)
    return out, {"evaluated": ev, "blocks": blocks}
