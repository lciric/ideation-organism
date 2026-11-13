"""K20-ZE: the blind euro-area replication of K20 on the ECB Survey of Professional Forecasters.
Everything here is the preregistered computation (audit/K20-ZE/preenregistrement.md, sections 3-6).

What changes from K20 (preregistration, section 2.2):
- annual targets (calendar-year averages) 2000-2025, three variables (HICP inflation, real GDP growth,
  unemployment), eight survey rounds per target: one row per variable x target year x round (624 rows);
- consensus = mean of the individual point forecasts of the round (at least 20 answers);
- revision = consensus of round t - consensus of round t-1, same target year; error = outturn - consensus;
- surprise = reference value R(t) - R(t-1), where R(t) is the latest published figure the ECB sends to the
  forecasters at the start of round t: the news published between two rounds, with no survey noise in it;
- six series (variable x horizon) each with its own constant, class effect and base slope; c is common;
- 'large' = top third of |surprise| per variable over the rounds of the main sample, with a strict or a
  broad cut, whichever gives the share closest to one third (values have one decimal, so there are ties);
- Driscoll-Kraay standard errors with 8 lags (scores summed by round, empty rounds count as zero) and the
  critical value 1.708 (Student, 25 degrees of freedom: about 26 independent target years);
- a positive control: the base under-reaction must be visible (common slope or small-news slope with a
  lower 90% bound above 0);
- schema checks count for the verdict only on the rows that enter the computation (the fix of K20's guard).

Surprises are computed in double precision without rounding (the reading of the letter used by both the
experimenter and the verifier; ecarts.md, C1).
"""
import io
import math
import re
import zipfile

import numpy as np
import pandas as pd

from . import data, stats

VARIABLES = ["HICP", "RGDP", "UNEM"]
SERIES = [f"{v}_h{h}" for v in VARIABLES for h in (0, 1)]
SPF_FILES = {"HICP": "1_HICP.csv", "RGDP": "3_RGDP.csv", "UNEM": "5_UNEM.csv"}
REFERENCE_TYPE = {"HICP": "M_REFERENCE", "RGDP": "Q_REFERENCE", "UNEM": "M_REFERENCE"}
ROLLING_TYPE = {"HICP": "M_YEAR_1_AHEAD", "RGDP": "Q_YEAR_1_AHEAD", "UNEM": "M_YEAR_1_AHEAD"}
EUROSTAT_FILES = {"HICP": "eurostat/prc_hicp_ainr_A_RCH_A_AVG_TOTAL_EA.csv",
                  "RGDP": "eurostat/nama_10_gdp_A_CLV_PCH_PRE_B1GQ_EA.csv",
                  "UNEM": "eurostat/une_rt_m_M_NSA_TOTAL_PC_ACT_T_EA21.csv"}
# Euro-area recessions (CEPR-EABCN, peak to trough) and the 2021-2023 inflation surge, in quarter numbers.
EPISODES = {"E1": (8032, 8037), "E2": (8046, 8052), "E3": (8079, 8095)}
EPISODE_LABELS = {"E1": "2008Q1-2009Q2", "E2": "2011Q3-2013Q1", "E3": "2019Q4-2023Q4"}
FIRST_ROUND = 7996           # 1999Q1
MIN_ANSWERS = 20
CRIT = 1.708                 # Student t, 25 degrees of freedom, 95% quantile
LAGS = 8
YEARS = range(2000, 2026)
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
F_RANGES = {"HICP": (-3, 12), "RGDP": (-10, 10), "UNEM": (3, 15)}
REF_RANGES = {"HICP": (-3, 12), "RGDP": (-20, 20), "UNEM": (3, 15)}
COLUMNS = ["variable", "target_year", "round", "t_round", "rank", "horizon", "prev_round", "horizon_prev",
           "n_answers", "n_answers_prev", "f", "f_prev", "f_med", "f_prev_med", "ref_period", "ref",
           "ref_period_prev", "ref_prev", "rolling_t4", "outturn", "revision", "error", "surprise",
           "surprise_consensus", "revision_med", "error_med", "complete", "main", "episode", "large"]


def round_number(label):
    """'2007Q3' -> 8030 (4 x year + quarter - 1); None if the label is not of that form."""
    m = re.fullmatch(r"(\d{4})Q([1-4])", label)
    return 4 * int(m.group(1)) + int(m.group(2)) - 1 if m else None


def round_label(t):
    return f"{t // 4}Q{t % 4 + 1}"


def reference_period(variable, t):
    """Period of the reference value sent at round t (preregistration 3.1, with its listed exceptions):
    HICP, last month of the quarter before the round (2024Q2: February 2024); RGDP, quarter t-2;
    UNEM, second month before the start of the round's quarter (six exceptions)."""
    year, q = t // 4, t % 4 + 1
    if variable == "RGDP":
        return round_label(t - 2)
    exceptions = {"HICP": {(2024, 2): (2024, 2)},
                  "UNEM": {(2000, 1): (1999, 12), (2023, 1): (2022, 10), (2023, 4): (2023, 7),
                           (2024, 1): (2023, 10), (2024, 2): (2024, 1), (2024, 4): (2024, 7)}}[variable]
    if (year, q) in exceptions:
        y, m = exceptions[(year, q)]
    else:
        month = 12 * year + 3 * (q - 1) - (1 if variable == "HICP" else 2)   # 0-based absolute month
        y, m = month // 12, month % 12 + 1
    return f"{y}{MONTHS[m - 1]}"


def in_episode(t_round, target_year, window):
    """A row (target y, round t) carries the information from round t-1 to the end of year y; it belongs to
    the episode [P, T] if that interval meets the window: t - 1 <= T and 4y + 3 >= P."""
    P, T = window
    return t_round - 1 <= T and 4 * target_year + 3 >= P


# ------------------------------------------------------------------------------------------ raw data
def read_spf(variable):
    """Point forecasts of one variable from the ECB SPF archive (root copy of the CSV), as text."""
    with zipfile.ZipFile(data.get("ecb_spf/SPF_microdata_by_variable.zip")) as z:
        raw = pd.read_csv(io.BytesIO(z.read(SPF_FILES[variable])), dtype=str, keep_default_na=False)
    raw = raw[raw["table_name"] == "Point"].copy()
    raw["t"] = raw["ref_round"].map(round_number)
    raw["x"] = raw["value"].map(_to_float)
    return raw


def _to_float(text):
    """Python's correctly rounded float parsing (pandas' fast parser can differ in the last bit, which
    matters for ties in |surprise|); NaN for an empty or non-numeric cell."""
    try:
        return float(text)
    except ValueError:
        return np.nan


def outturns():
    """{variable: {year: outturn}} from the latest Eurostat files: annual average HICP inflation, annual real
    GDP growth, and the mean of the 12 monthly unemployment rates (EA21; years with 12 months only)."""
    out = {}
    for v in VARIABLES:
        e = pd.read_csv(data.get(EUROSTAT_FILES[v]), dtype=str, keep_default_na=False)
        x = e["OBS_VALUE"].map(_to_float)
        if v == "UNEM":
            g = x.groupby(e["TIME_PERIOD"].str[:4].astype(int))
            out[v] = {int(y): float(np.mean(vals)) for y, vals in g if len(vals) == 12}
        else:
            out[v] = {int(y): float(val) for y, val in zip(e["TIME_PERIOD"], x)}
    return out


def load_raw():
    """Everything the dataset is built from: consensus cells, reference values, rolling-forecast cells,
    outturns. Cells are {(round, type, target): (n answers, mean, median)}."""
    raw = {"cells": {}, "refs": {}, "rolling": {}, "outturn": outturns()}
    for v in VARIABLES:
        d = read_spf(v)
        indiv = d[d["forecaster_id"].str.fullmatch(r"\d{3}")]
        annual = indiv[indiv["target_period_type"].isin(["A_YEAR_0_AHEAD", "A_YEAR_1_AHEAD", "A_YEAR_2_AHEAD"])]
        raw["cells"][v] = {(int(t), typ, tgt): (len(g), float(np.mean(g["x"].values)), float(np.median(g["x"].values)))
                           for (t, typ, tgt), g in annual.groupby(["t", "target_period_type", "target_period"])}
        ecb = d[(d["forecaster_id"] == "ECB") & (d["target_period_type"] == REFERENCE_TYPE[v])]
        raw["refs"][v] = {int(t): (p, float(x)) for t, p, x in zip(ecb["t"], ecb["target_period"], ecb["x"])}
        rolling = indiv[indiv["target_period_type"] == ROLLING_TYPE[v]]
        raw["rolling"][v] = {(int(t), p): (len(g), float(np.mean(g["x"].values)))
                             for (t, p), g in rolling.groupby(["t", "target_period"])}
    return raw


# ------------------------------------------------------------------------------------------ dataset
def build_k20ze(raw=None):
    """624 rows = variable x target year 2000-2025 x rank 1-8 (the preregistered K20-ZE_analyse.csv, English
    column names). French names: target_year = annee_cible, round = tour, rank = rang, prev_round = tour_prec,
    horizon_prev = horizon_prec, n_answers = n_rep, f = prev (consensus), f_prev = prev_prec, f_med = prev_med,
    ref_period = ref_periode, rolling_t4 = prev_glissante_t4, outturn = realise, error = erreur,
    main = principal, large = grande_nouvelle.
    Rank 1 is round Q1 of year y-1, rank 8 round Q4 of year y; horizon = 1 (next year) for ranks 1-4, 0 after."""
    raw = raw or load_raw()
    rows = []
    for v in VARIABLES:
        cells, refs, rolling = raw["cells"][v], raw["refs"][v], raw["rolling"][v]
        for y in YEARS:
            for rank in range(1, 9):
                t = 4 * (y - 1) + rank - 1
                tp = t - 1
                h, hp = y - t // 4, y - tp // 4
                n, mean, med = cells.get((t, f"A_YEAR_{h}_AHEAD", str(y)), (0, np.nan, np.nan))
                n_p, mean_p, med_p = (cells.get((tp, f"A_YEAR_{hp}_AHEAD", str(y)), (0, np.nan, np.nan))
                                      if tp >= FIRST_ROUND else (0, np.nan, np.nan))
                ref_period, ref = refs.get(t, ("", np.nan))
                ref_period_prev, ref_prev = refs.get(tp, ("", np.nan))
                roll = np.nan
                if ref_period and t - 4 >= FIRST_ROUND:
                    n_roll, m_roll = rolling.get((t - 4, ref_period), (0, np.nan))
                    roll = m_roll if n_roll >= MIN_ANSWERS else np.nan
                rows.append({"variable": v, "target_year": y, "round": round_label(t), "t_round": t, "rank": rank,
                             "horizon": h, "prev_round": round_label(tp), "horizon_prev": hp,
                             "n_answers": n, "n_answers_prev": n_p,
                             "f": mean if n >= MIN_ANSWERS else np.nan, "f_prev": mean_p if n_p >= MIN_ANSWERS else np.nan,
                             "f_med": med if n >= MIN_ANSWERS else np.nan,
                             "f_prev_med": med_p if n_p >= MIN_ANSWERS else np.nan,
                             "ref_period": ref_period, "ref": ref, "ref_period_prev": ref_period_prev,
                             "ref_prev": ref_prev, "rolling_t4": roll, "outturn": raw["outturn"][v].get(y, np.nan)})
    df = pd.DataFrame(rows)
    df["revision"] = df["f"] - df["f_prev"]
    df["error"] = df["outturn"] - df["f"]
    df["surprise"] = df["ref"] - df["ref_prev"]
    df["surprise_consensus"] = df["ref"] - df["rolling_t4"]
    df["revision_med"] = df["f_med"] - df["f_prev_med"]
    df["error_med"] = df["outturn"] - df["f_med"]
    df["complete"] = df[["revision", "error", "surprise"]].notna().all(axis=1).astype(int)
    df["main"] = ((df["complete"] == 1) & ~pandemic(df)).astype(int)
    df["episode"] = [next((k for k, w in EPISODES.items() if in_episode(t, y, w)), "")
                     for t, y in zip(df["t_round"], df["target_year"])]
    df["large"] = large_news(df, "surprise", df["main"] == 1)
    return df[COLUMNS]


def pandemic(df):
    """RGDP and UNEM rows whose target year is 2020 or 2021 or whose round is in 2020Q1-2021Q4."""
    return df["variable"].isin(["RGDP", "UNEM"]) & (df["target_year"].isin([2020, 2021])
                                                   | df["t_round"].between(8080, 8087))


def tie_aware_cut(abs_s):
    """Section 6.2: Q = 2/3 quantile (numpy linear) of the per-round |s|; the cut is strict (|s| > Q) if the
    share of rounds above Q is at least as close to 1/3 as the share at or above Q, broad (|s| >= Q)
    otherwise. Returns (Q, strict)."""
    a = np.asarray(abs_s, dtype=float)
    Q = float(np.quantile(a, 2 / 3))
    n_strict, n_broad = int(np.sum(a > Q)), int(np.sum(a >= Q))
    return Q, abs(n_strict / len(a) - 1 / 3) <= abs(n_broad / len(a) - 1 / 3)


def large_news(df, col, sample):
    """L per variable, from the distinct rounds of `sample` (one |col| per round, constant within a round);
    applied to every row of the variable where col is present."""
    out = pd.Series(np.nan, index=df.index)
    for v in VARIABLES:
        sel = (df["variable"] == v) & sample & df[col].notna()
        per_round = df.loc[sel].groupby("t_round")[col].first().abs()
        Q, strict = tie_aware_cut(per_round.values)
        has = (df["variable"] == v) & df[col].notna()
        s = df.loc[has, col].abs()
        out[has] = (s > Q if strict else s >= Q).astype(float)
    return out


# ------------------------------------------------------------------------------------------ schema
def schema_checks(df, raw):
    """The 12 checks of section 4.4. Returns (n_violations_schema, n_anomalies_outside_main, failures) where
    failures = {check: boolean Series of failing rows} (checks 1 and 2: a bool for the whole file).
    File checks (1, 2) and the membership check (10) always count; the other row checks count only when
    they fail on a main row, and their failures on other rows are counted as anomalies."""
    n = len(df)
    fail = {k: pd.Series(False, index=df.index) for k in range(3, 13)}
    file_ok = {1: list(df.columns) == COLUMNS}
    grid = [(v, y, 4 * (y - 1) + j - 1) for v in VARIABLES for y in YEARS for j in range(1, 9)]
    file_ok[2] = n == 624 and list(zip(df["variable"], df["target_year"], df["t_round"])) == grid
    t, y = df["t_round"], df["target_year"]
    # 3 identifiers
    yr = df["round"].map(lambda s: int(s[:4]) if round_number(s) is not None else -1)
    fail[3] = ((df["round"].map(round_number) != t) | (df["rank"] != t - 4 * (y - 1) + 1) | ~df["rank"].between(1, 8)
               | (df["horizon"] != y - yr) | (df["horizon"] != np.where(df["rank"] <= 4, 1, 0))
               | (df["prev_round"] != (t - 1).map(round_label)) | (df["horizon_prev"] != y - (t - 1) // 4)
               | ~df["horizon_prev"].isin([0, 1, 2]))
    # 4 answers and presence (also: the counts equal the raw cells)
    raw_n = [raw["cells"][v].get((tt, f"A_YEAR_{h}_AHEAD", str(yy)), (0,))[0]
             for v, tt, h, yy in zip(df["variable"], t, df["horizon"], y)]
    raw_np = [raw["cells"][v].get((tt - 1, f"A_YEAR_{h}_AHEAD", str(yy)), (0,))[0] if tt - 1 >= FIRST_ROUND else 0
              for v, tt, h, yy in zip(df["variable"], t, df["horizon_prev"], y)]
    main = df["main"] == 1
    fail[4] = ((df["f"].notna() != (df["n_answers"] >= MIN_ANSWERS))
               | (df["f_prev"].notna() != (df["n_answers_prev"] >= MIN_ANSWERS))
               | (df["n_answers"] != raw_n) | (df["n_answers_prev"] != raw_np)
               | (main & ((df["n_answers"] < MIN_ANSWERS) | (df["n_answers_prev"] < MIN_ANSWERS)
                          | df[["f", "f_prev", "f_med", "f_prev_med"]].isna().any(axis=1))))
    # 5 reference values: present, equal to the ECB line, period as in 3.1; previous round likewise
    c5 = []
    for v, tt, p, r, pp, rp in zip(df["variable"], t, df["ref_period"], df["ref"], df["ref_period_prev"], df["ref_prev"]):
        ok = (p, r) == raw["refs"][v].get(tt) and p == reference_period(v, tt)
        if tt - 1 >= FIRST_ROUND:
            ok &= (pp, rp) == raw["refs"][v].get(tt - 1) and pp == reference_period(v, tt - 1)
        else:
            ok &= pp == "" and np.isnan(rp)
        c5.append(not ok)
    fail[5] = pd.Series(c5, index=df.index)
    # 6 ranges
    c6 = pd.Series(False, index=df.index)
    for v in VARIABLES:
        mv = df["variable"] == v
        for cols, (lo, hi) in ((["f", "f_prev", "f_med", "f_prev_med", "outturn"], F_RANGES[v]),
                               (["ref", "ref_prev"], REF_RANGES[v])):
            x = df.loc[mv, cols]
            c6[mv] |= (x.notna() & ~x.apply(lambda col: col.between(lo, hi))).any(axis=1)
    fail[6] = c6
    # 7 formulas, and rolling_t4 present iff at least 20 rolling forecasts of round t-4 for ref_period
    c7 = pd.Series(False, index=df.index)
    for d, a, b in (("revision", "f", "f_prev"), ("error", "outturn", "f"), ("surprise", "ref", "ref_prev"),
                    ("surprise_consensus", "ref", "rolling_t4"), ("revision_med", "f_med", "f_prev_med"),
                    ("error_med", "outturn", "f_med")):
        empty = df[a].isna() | df[b].isna()
        c7 |= (df[d].isna() != empty) | ((df[d] - (df[a] - df[b])).abs() > 1e-9)
    n_roll = [raw["rolling"][v].get((tt - 4, p), (0,))[0] if tt - 4 >= FIRST_ROUND and p else 0
              for v, tt, p in zip(df["variable"], t, df["ref_period"])]
    c7 |= df["rolling_t4"].notna() != (pd.Series(n_roll, index=df.index) >= MIN_ANSWERS)
    fail[7] = c7
    # 8 consistency between rows
    key = df.set_index(["variable", "target_year", "t_round"])
    c8 = []
    for v, yy, tt, fp, nap in zip(df["variable"], y, t, df["f_prev"], df["n_answers_prev"]):
        k = (v, yy, tt - 1)
        c8.append(k in key.index and not (_same(key.at[k, "f"], fp) and key.at[k, "n_answers"] == nap))
    c8 = pd.Series(c8, index=df.index)
    by_round = df.groupby(["variable", "t_round"])
    for col in ("ref", "ref_period", "ref_prev", "surprise", "large"):
        c8 |= by_round[col].transform(lambda s: s.astype(str).nunique() > 1)
    ref_of = {(v, tt): r for v, tt, r in zip(df["variable"], t, df["ref"])}
    c8 |= pd.Series([(v, tt - 1) in ref_of and not _same(ref_of[(v, tt - 1)], rp)
                     for v, tt, rp in zip(df["variable"], t, df["ref_prev"])], index=df.index)
    fail[8] = c8
    # 9 outturn: one value per (variable, target year), equal to the raw Eurostat value
    c9 = df.groupby(["variable", "target_year"])["outturn"].transform(lambda s: s.astype(str).nunique() > 1)
    c9 |= pd.Series([not (abs(a - raw["outturn"][v].get(yy, np.inf)) <= 1e-9)
                     for v, yy, a in zip(df["variable"], y, df["outturn"])], index=df.index)
    fail[9] = c9
    # 10 membership, on every row
    complete = df[["revision", "error", "surprise"]].notna().all(axis=1)
    fail[10] = (df["complete"] != complete.astype(int)) | (df["main"] != (complete & ~pandemic(df)).astype(int))
    # 11 episodes
    expected = [next((k for k, w in EPISODES.items() if in_episode(tt, yy, w)), "") for tt, yy in zip(t, y)]
    fail[11] = df["episode"] != pd.Series(expected, index=df.index)
    # 12 large news
    L = large_news(df, "surprise", main)
    fail[12] = ((df["large"].isna() != df["surprise"].isna()) | (df["large"].notna() & (df["large"] != L))
                | by_round["large"].transform(lambda s: s.astype(str).nunique() > 1))
    counted = [k for k in (1, 2) if not file_ok[k]]
    counted += [k for k in range(3, 13) if (fail[k].any() if k == 10 else (fail[k] & main).any())]
    anomalies = int(sum((fail[k] & ~main).sum() for k in range(3, 13) if k != 10))
    return len(counted), anomalies, {**file_ok, **fail}


def _same(a, b):
    return (pd.isna(a) and pd.isna(b)) or a == b


# ------------------------------------------------------------------------------------------ estimation
def standardise(df):
    """Section 6.1: per series (variable x horizon), standardise revision, error, their median versions and
    p = error + revision with the mean and standard deviation (n-1) of the main rows; every row of the series
    gets these constants. Returns (copy with series and z columns, {series: k_g = s_r / s_e})."""
    out = df.copy()
    out["series"] = out["variable"] + "_h" + out["horizon"].astype(str)
    out["gap_prev"] = out["error"] + out["revision"]
    k = {}
    for g in SERIES:
        mg = out["series"] == g
        sel = mg & (out["main"] == 1)
        for col, z in (("revision", "z_r"), ("error", "z_e"), ("revision_med", "z_r_med"),
                       ("error_med", "z_e_med"), ("gap_prev", "z_p")):
            out.loc[mg, z] = (out.loc[mg, col] - out.loc[sel, col].mean()) / out.loc[sel, col].std(ddof=1)
        k[g] = out.loc[sel, "revision"].std(ddof=1) / out.loc[sel, "error"].std(ddof=1)
    return out, k


def design(D, zr="z_r", large="large", by_variable=False):
    """Regressors in the preregistered order: per series present in D, a constant, a class effect and a base
    slope; then c (or one c per variable, S1)."""
    groups = [g for g in SERIES if g in set(D["series"])]
    dg = [(D["series"] == g).astype(float).values for g in groups]
    cols = dg + [d * D[large].values for d in dg] + [d * D[zr].values for d in dg]
    if by_variable:
        cols += [(D["variable"] == v).astype(float).values * D[zr].values * D[large].values for v in VARIABLES]
    else:
        cols.append(D[zr].values * D[large].values)
    return np.column_stack(cols)


def regress(D, zr="z_r", ze="z_e", large="large", by_variable=False, lags=(LAGS,), X=None):
    """OLS and Driscoll-Kraay covariances (scores summed by round). Returns {'beta', 'n', 'iid', 'year',
    <lag>: covariance}; 'year' is the covariance clustered by target year (S2)."""
    D = D.dropna(subset=[zr, ze] + ([large] if X is None else []))
    X = design(D, zr, large, by_variable) if X is None else X(D)
    beta, u, _ = stats.ols(X, D[ze].values)
    out = {"beta": beta, "n": len(D), "iid": stats.iid_cov(X, u),
           "year": stats.driscoll_kraay_cov(X, u, D["target_year"].values, 0)}
    for L in lags:
        out[L] = stats.driscoll_kraay_cov(X, u, D["t_round"].values, L)
    return out


def c_and_se(R, j=None, lags=LAGS):
    j = len(R["beta"]) - 1 if j is None else j
    return float(R["beta"][j]), math.sqrt(R[lags][j, j])


def common_slope_design(D):
    """Positive control (6.6): one constant per series and one common slope, no size split."""
    groups = [g for g in SERIES if g in set(D["series"])]
    return np.column_stack([(D["series"] == g).astype(float).values for g in groups] + [D["z_r"].values])


def variance_ratio(D, z, large="large"):
    """A / a: variance of z after large news over that after small news, each around its series-class mean."""
    dev = D[z] - D.groupby(["series", large])[z].transform("mean")
    a, A = float(np.mean(dev[D[large] == 0] ** 2)), float(np.mean(dev[D[large] == 1] ** 2))
    return A / a, a, A


def run(df, raw):
    """All 65 preregistered fields (French names, as in the sealed verdict) and the working data."""
    n_viol, n_anom, _ = schema_checks(df, raw)
    d, k = standardise(df)
    base = d[d["main"] == 1].copy()
    out = {"n_violations_schema": n_viol, "n_anomalies_hors_principal": n_anom, "n_principal": len(base),
           "n_tours": int(base["t_round"].nunique()), "n_annees_cibles": int(base["target_year"].nunique()),
           "n_grands": int((base["large"] == 1).sum()),
           "n_tours_grands": int(base.loc[base["large"] == 1, "t_round"].nunique())}
    R = regress(base, lags=(8, 4, 12, 0))
    c, se = c_and_se(R)
    lo, hi = c - CRIT * se, c + CRIT * se
    w = np.zeros(len(R["beta"]))
    w[12:18] = 1 / 6
    b_mean, se_b_mean = stats.combination(R["beta"], R[8], w)
    Rb = regress(base, X=common_slope_design)
    b_common, se_b_common = c_and_se(Rb)
    out.update(c=c, et_c_dk8=se, t_c=c / se, borne_basse_ic90=lo, borne_haute_ic90=hi, b_moyen=b_mean,
               et_b_moyen_dk8=se_b_mean, borne_basse_b_moyen_ic90=b_mean - CRIT * se_b_mean, b_commun=b_common,
               et_b_commun_dk8=se_b_common, borne_basse_b_commun_ic90=b_common - CRIT * se_b_common)
    out["controle_positif_ok"] = int(out["borne_basse_b_commun_ic90"] > 0 or out["borne_basse_b_moyen_ic90"] > 0)
    k_mean = float(np.mean([k[g] for g in SERIES]))
    ratio, a, A = variance_ratio(base, "z_r")
    bias = (2 * b_mean + k_mean) * 0.10 * (1 / a - 1 / A)
    floor = max(0.10, bias)
    out.update(k_moyen=k_mean, pente_moyenne_grandes=b_mean + c, rapport_variance_revision=ratio,
               rapport_variance_ecart_prec=variance_ratio(base, "z_p")[0])
    out["pertinence_manquante"] = int(ratio < 1.25 and lo - floor <= 0)
    out.update(biais_mecanique_nu20=bias, seuil_survie_bas=floor, borne_basse_moins_seuil=lo - floor,
               marge_indecision=min(floor - lo, hi - 0.40))
    without = {}
    for i, name in enumerate(EPISODES, start=1):
        ck, sk = c_and_se(regress(base[base["episode"] != name]))
        without[i] = (ck, ck / sk, sk)
    for i in without:
        out[f"c_sans_E{i}"] = without[i][0]
    for i in without:
        out[f"t_sans_E{i}"] = without[i][1]
    t_min = min(w_[1] for w_ in without.values())
    out.update(t_min_sans_episode=t_min, c_min_sans_episode=min(w_[0] for w_ in without.values()),
               episode_t_min=min(i for i, w_ in without.items() if w_[1] == t_min))
    out["conflit_robustesse"] = int(lo > floor and hi >= 0.40 and t_min < 1 and out["c_min_sans_episode"] > 0)
    se_iid = math.sqrt(R["iid"][-1, -1])
    out.update(et_c_iid=se_iid, n_effectif=len(base) * (se_iid / se) ** 2,
               et_c_dk4=c_and_se(R, lags=4)[1], et_c_dk12=c_and_se(R, lags=12)[1], et_c_dk0=c_and_se(R, lags=0)[1],
               et_c_grappes_annee=c_and_se(R, lags="year")[1])
    out["c_avec_pandemie"], out["et_c_avec_pandemie_dk8"] = c_and_se(regress(d[d["complete"] == 1]))
    out["c_avant_2020"], out["et_c_avant_2020_dk8"] = c_and_se(regress(base[base["target_year"] <= 2019]))
    out["c_annee_en_cours"], out["et_c_annee_en_cours_dk8"] = c_and_se(regress(base[base["horizon"] == 0]))
    out["c_annee_suivante"], out["et_c_annee_suivante_dk8"] = c_and_se(regress(base[base["horizon"] == 1]))
    out["c_mediane"], out["et_c_mediane_dk8"] = c_and_se(regress(base, zr="z_r_med", ze="z_e_med"))
    base["large_revision"] = (np.abs(base["z_r"]) > 1).astype(float)
    out["c_coupure_revision"], out["et_c_coupure_revision_dk8"] = c_and_se(regress(base, large="large_revision"))
    s8 = base[base["surprise_consensus"].notna()].copy()
    s8["large_consensus"] = large_news(s8, "surprise_consensus", pd.Series(True, index=s8.index))
    out["n_surprise_consensus"] = len(s8)
    out["c_surprise_consensus"], out["et_c_surprise_consensus_dk8"] = c_and_se(regress(s8, large="large_consensus"))
    R1 = regress(base, by_variable=True)
    for i, v in enumerate(VARIABLES):
        out[f"c_{v}"] = c_and_se(R1, 18 + i)[0]
    for i, v in enumerate(VARIABLES):
        out[f"et_c_{v}_dk8"] = c_and_se(R1, 18 + i)[1]
    return out, {"data": d, "base": base, "main_fit": R, "by_variable_fit": R1, "common_fit": Rb,
                 "without_episode": without, "k": k}
