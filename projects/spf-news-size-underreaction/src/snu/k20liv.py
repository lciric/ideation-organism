"""K20-LIV: the blind replication of K20 on the US Livingston Survey (Philadelphia Fed), 1947-2026.
Everything here is the preregistered computation (audit/K20-LIV/preenregistrement.md, sections 3-6).

What changes from K20 (preregistration, section 2):
- two surveys a year (June, December); for a target month T (June or December) the 12-month-ahead forecast
  of survey s (T - 12) is revised by the 6-month-ahead forecast of survey s+1 (T - 6);
- level targets, in 100 x log for CPI and housing starts (TPHS); CPI forecasts are put back in the base of
  the outturn series with the base value of the same questionnaire;
- five variables: CPI, UNPR (unemployment), PRIME (prime rate), TBILL (3-month bill), TPHS (housing starts);
- surprise = outturn of the base month of s+1 (April or October) minus the point of survey s's path at that
  month (three quarters of the way from its base month to its 6-month forecast);
- latest FRED vintage for every outturn (CPIAUCNS until the survey of June 2004, CPIAUCSL after);
- Driscoll-Kraay standard errors with 2 lags of half-years; critical value 1.645;
- the mechanical-bias floor uses the noise share nu MEASURED from the individual answers (then doubled);
- a positive control (pooled slope with a lower 90% bound above 0, or the whole interval of c below 0);
- schema checks on the main rows only.
"""
import math

import numpy as np
import pandas as pd

from . import data, k20, stats

VARIABLES = ["CPI", "UNPR", "PRIME", "TBILL", "TPHS"]
FIRST_TARGET = {"CPI": "1947-12", "UNPR": "1962-06", "PRIME": "1982-06", "TBILL": "1993-06", "TPHS": "1970-12"}
LAST_TARGET = "2026-06"
SERIES = {"UNPR": "UNRATE", "PRIME": "DPRIME", "TBILL": "DTB3", "TPHS": "HOUST"}
MONTHLY = {"CPIAUCNS", "CPIAUCSL", "UNRATE", "HOUST"}
# NBER peak to trough + 14 months, in target months, overlapping windows merged; E11 joins 2020 to 2021-2023.
EPISODES = {"E1": ("1948-11", "1950-12"), "E2": ("1953-07", "1955-07"), "E3": ("1957-08", "1959-06"),
            "E4": ("1960-04", "1962-04"), "E5": ("1969-12", "1972-01"), "E6": ("1973-11", "1976-05"),
            "E7": ("1980-01", "1984-01"), "E8": ("1990-07", "1992-05"), "E9": ("2001-03", "2003-01"),
            "E10": ("2007-12", "2010-08"), "E11": ("2020-02", "2023-12")}
PANDEMIC_TARGETS = {"2020-06", "2020-12", "2021-06", "2021-12"}   # UNPR only
SURVEY_DATES = [f"{y}-{m:02d}" for y in range(1946, 2027) for m in (6, 12)][:-1]   # 1946-06 .. 2026-06
F_RANGES = {"CPI": (50, 500), "UNPR": (1, 20), "PRIME": (1, 25), "TBILL": (-1, 20), "TPHS": (0.2, 3.5)}
OUTTURN_RANGES = {"CPI": (15, 500), "UNPR": (1, 20), "PRIME": (1, 25), "TBILL": (-1, 20), "TPHS": (0.2, 3.5)}
CRIT = 1.645
LAGS = 2
COLUMNS = ["variable", "target", "half_year", "survey_1", "survey_2", "base_month_1", "base_month_2", "f12_1", "f6_2",
           "f6_1", "bp_1", "bp_2", "f12_1_med", "f6_2_med", "outturn_series", "outturn_day", "outturn_level",
           "base_day_1", "base_level_1", "base_day_2", "base_level_2", "y_f_1", "y_f_2", "y_f6_1", "y_outturn",
           "y_base_1", "y_base_2", "revision", "error", "surprise", "revision_med", "error_med", "n_answers_1",
           "var_answers_1", "n_answers_2", "var_answers_2", "complete", "main", "episode", "large"]


def month_add(ym, n):
    """'2020-06' + 6 -> '2020-12'."""
    t = int(ym[:4]) * 12 + int(ym[5:7]) - 1 + n
    return f"{t // 12}-{t % 12 + 1:02d}"


def base_month(survey):
    """The month of the last data known to a survey's respondents: April for June, October for December."""
    return f"{survey[:4]}-04" if survey[5:] == "06" else f"{survey[:4]}-10"


def episode_of(target):
    return next((k for k, (a, b) in EPISODES.items() if a <= target <= b), "")


def to_units(variable, x):
    """Analysis units: 100 x ln for CPI and TPHS, the level for the three rates."""
    return 100 * np.log(x) if variable in ("CPI", "TPHS") else x


def outturn_series(variable, survey_2):
    if variable == "CPI":
        return "CPIAUCNS" if survey_2 <= "2004-06" else "CPIAUCSL"
    return SERIES[variable]


# ------------------------------------------------------------------------------------------ raw data
def _to_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return np.nan


def _sheets(name):
    raw = data.read_excel(data.get(f"livingston/{name}.xlsx"), VARIABLES)
    out = {}
    for v, d in raw.items():
        d = d.copy()
        d["ym"] = pd.to_datetime(d["Date"]).dt.strftime("%Y-%m")
        for c in d.columns:
            if c not in ("Date", "ym", "ID", "Category"):
                d[c] = pd.to_numeric(d[c], errors="coerce")      # '#N/A' cells -> NaN
        out[v] = d
    return out


def fred_month_last(series):
    """{'YYYY-MM': (date of the last non-empty observation of the month, value)} from the latest FRED vintage;
    HOUST is divided by 1 000 (millions, as in the survey)."""
    raw = pd.read_csv(data.get(f"fred/{series}.csv"), dtype=str, keep_default_na=False)
    raw.columns = ["d", "x"]
    raw["x"] = raw["x"].map(_to_float)
    out = {}
    for ym, g in raw.dropna(subset=["x"]).groupby(raw["d"].str[:7], sort=True):
        day, x = g.iloc[-1]["d"], float(g.iloc[-1]["x"])
        out[ym] = (day, x / 1000.0 if series == "HOUST" else x)
    return out


def load_raw():
    """Mean, median and individual sheets (indexed by survey month) and the FRED month tables."""
    means, medians = _sheets("means"), _sheets("medians")
    return {"means": {v: d.set_index("ym") for v, d in means.items()},
            "medians": {v: d.set_index("ym") for v, d in medians.items()},
            "individual": _sheets("individualdata"),
            "fred": {s: fred_month_last(s) for s in ["CPIAUCNS", "CPIAUCSL", "UNRATE", "DPRIME", "DTB3", "HOUST"]}}


# ------------------------------------------------------------------------------------------ dataset
def derived(v, r):
    """The analysis-unit quantities of section 4 from the inputs of one row (dict); NaN propagates."""
    def y_forecast(f, bp, base_level):
        if v == "CPI":
            return 100 * np.log(f) - 100 * np.log(bp) + to_units(v, base_level)
        return to_units(v, f)
    o = {"y_outturn": to_units(v, r["outturn_level"]), "y_base_1": to_units(v, r["base_level_1"]),
         "y_base_2": to_units(v, r["base_level_2"]),
         "y_f_1": y_forecast(r["f12_1"], r["bp_1"], r["base_level_1"]),
         "y_f_2": y_forecast(r["f6_2"], r["bp_2"], r["base_level_2"]),
         "y_f6_1": y_forecast(r["f6_1"], r["bp_1"], r["base_level_1"])}
    y1_med = y_forecast(r["f12_1_med"], r["bp_1"], r["base_level_1"])
    y2_med = y_forecast(r["f6_2_med"], r["bp_2"], r["base_level_2"])
    o["revision"] = o["y_f_2"] - o["y_f_1"]
    o["error"] = o["y_outturn"] - o["y_f_2"]
    o["surprise"] = o["y_base_2"] - (o["y_base_1"] + 0.75 * (o["y_f6_1"] - o["y_base_1"]))
    o["revision_med"] = y2_med - y1_med
    o["error_med"] = o["y_outturn"] - y2_med
    return o


def consensus_noise(raw, v, survey, col):
    """(number of numeric individual answers, their variance (n-1) in analysis units) for one survey cell."""
    ind = raw["individual"][v]
    x = ind.loc[ind["ym"] == survey, f"{v}_{col}"].dropna().values.astype(float)
    return (len(x), float(np.var(to_units(v, x), ddof=1))) if len(x) >= 2 else (len(x), np.nan)


def build_k20liv(raw=None):
    """555 rows = variable x target month (the preregistered K20-LIV_analyse.csv, English column names).
    French names: target = cible, half_year = semestre (2 x year + 0 for June, 1 for December), survey_1/2 =
    enquete_1/2, base_month_1/2 = mois_ancre_1/2, f12_1 = prev_12m_1, f6_2 = prev_6m_2, f6_1 = prev_6m_1,
    outturn_series = serie_realise, outturn_day = jour_realise, outturn_level = realise_niv, base_day_k =
    jour_ancre_k, base_level_k = ancre_niv_k, y_f_1 = y_prev_1, y_f_2 = y_prev_2, y_f6_1 = y_prev6_1,
    y_outturn = y_realise, y_base_k = y_ancre_k, error = erreur, n_answers_k = n_rep_k, var_answers_k =
    var_rep_k, main = principal, large = grande_nouvelle."""
    raw = raw or load_raw()
    M, MED, F = raw["means"], raw["medians"], raw["fred"]
    rows = []
    for v in VARIABLES:
        t = FIRST_TARGET[v]
        while t <= LAST_TARGET:
            s1, s2 = month_add(t, -12), month_add(t, -6)
            b1, b2 = base_month(s1), base_month(s2)
            series = outturn_series(v, s2)
            r = {"variable": v, "target": t, "half_year": 2 * int(t[:4]) + (0 if t[5:] == "06" else 1),
                 "survey_1": s1, "survey_2": s2, "base_month_1": b1, "base_month_2": b2,
                 "f12_1": M[v].at[s1, f"{v}_12M"], "f6_2": M[v].at[s2, f"{v}_6M"], "f6_1": M[v].at[s1, f"{v}_6M"],
                 "bp_1": M["CPI"].at[s1, "CPI_BP"] if v == "CPI" else np.nan,
                 "bp_2": M["CPI"].at[s2, "CPI_BP"] if v == "CPI" else np.nan,
                 "f12_1_med": MED[v].at[s1, f"{v}_12M"], "f6_2_med": MED[v].at[s2, f"{v}_6M"],
                 "outturn_series": series}
            for day, level, month in (("outturn_day", "outturn_level", t), ("base_day_1", "base_level_1", b1),
                                      ("base_day_2", "base_level_2", b2)):
                r[day], r[level] = F[series].get(month, ("", np.nan))
            r.update(derived(v, r))
            if v == "CPI" and s1 == "2004-06":   # the pair straddles the switch to seasonally adjusted CPI
                for k in ("y_f_1", "y_f6_1", "revision", "surprise", "revision_med"):
                    r[k] = np.nan
            r["n_answers_1"], r["var_answers_1"] = consensus_noise(raw, v, s1, "12M")
            r["n_answers_2"], r["var_answers_2"] = consensus_noise(raw, v, s2, "6M")
            r["episode"] = episode_of(t)
            rows.append(r)
            t = month_add(t, 6)
    df = pd.DataFrame(rows)
    df["complete"] = df[["revision", "error", "surprise"]].notna().all(axis=1).astype(int)
    df["main"] = main_rows(df).astype(int)
    df["large"] = large_news(df, df["main"] == 1)
    return df[COLUMNS]


def main_rows(df):
    """complete, at least 2 individual answers with a variance in both surveys, and not UNPR 2020-06..2021-12."""
    return (df[["revision", "error", "surprise"]].notna().all(axis=1) & (df["n_answers_1"] >= 2)
            & (df["n_answers_2"] >= 2) & df["var_answers_1"].notna() & df["var_answers_2"].notna()
            & ~((df["variable"] == "UNPR") & df["target"].isin(PANDEMIC_TARGETS)))


def large_news(df, sample):
    """L = 1 if |surprise| > Q_v (strict), Q_v = 2/3 quantile (numpy linear) of |surprise| over the rows of
    `sample` of the variable; NaN where the surprise is missing."""
    out = pd.Series(np.nan, index=df.index)
    for v in VARIABLES:
        Q = np.quantile(np.abs(df.loc[sample & (df["variable"] == v), "surprise"].values), 2 / 3)
        has = (df["variable"] == v) & df["surprise"].notna()
        out[has] = (np.abs(df.loc[has, "surprise"]) > Q).astype(float)
    return out


# ------------------------------------------------------------------------------------------ schema
def schema_checks(df):
    """The 11 checks of section 5, on the main rows (main = 1, or main by the recomputed definition).
    Returns (n_violations_schema, anomalies outside the main rows for checks 3-8, failures by check)."""
    fail = {k: pd.Series(False, index=df.index) for k in range(2, 12)}
    cols_ok = list(df.columns) == COLUMNS
    scope = (df["main"] == 1) | main_rows(df)
    v, t = df["variable"], df["target"]
    # 2 keys
    first = v.map(FIRST_TARGET)
    fail[2] = ~v.isin(VARIABLES) | ~t.str[5:].isin(["06", "12"]) | (t < first) | (t > LAST_TARGET)
    fail[2] |= df.duplicated(["variable", "target"], keep=False)
    # 3 survey dates
    idx = {d: i for i, d in enumerate(SURVEY_DATES)}
    fail[3] = pd.Series([not (s1 in idx and s2 in idx and idx[s2] == idx[s1] + 1 and tt == month_add(s2, 6)
                              and s1 == f"{int(tt[:4]) - 1}-{tt[5:]}" and m1 == base_month(s1) and m2 == base_month(s2)
                              and hy == 2 * int(tt[:4]) + (0 if tt[5:] == "06" else 1))
                         for s1, s2, tt, m1, m2, hy in zip(df["survey_1"], df["survey_2"], t, df["base_month_1"],
                                                           df["base_month_2"], df["half_year"])], index=df.index)
    # 4 presence
    needed = ["f12_1", "f6_2", "f6_1", "outturn_level", "base_level_1", "base_level_2", "y_f_1", "y_f_2", "y_f6_1",
              "y_outturn", "y_base_1", "y_base_2", "revision", "error", "surprise", "n_answers_1", "var_answers_1",
              "n_answers_2", "var_answers_2", "large"]
    fail[4] = (df[needed].isna().any(axis=1) | (df[["outturn_series", "outturn_day", "base_day_1", "base_day_2"]] == "").any(axis=1)
               | (df[["bp_1", "bp_2"]].notna().all(axis=1) != (v == "CPI"))
               | (df[["bp_1", "bp_2"]].notna().any(axis=1) != (v == "CPI")))
    # 5 series and days
    fail[5] = pd.Series([ser != outturn_series(vv, s2) or any(d and (d[:7] != m or (ser in MONTHLY and d[8:] != "01"))
                                                              for d, m in ((d0, tt), (d1, m1), (d2, m2)))
                         for vv, ser, s2, tt, m1, m2, d0, d1, d2 in zip(v, df["outturn_series"], df["survey_2"], t,
                                                                        df["base_month_1"], df["base_month_2"],
                                                                        df["outturn_day"], df["base_day_1"], df["base_day_2"])],
                        index=df.index)
    # 6 ranges
    c6 = pd.Series(False, index=df.index)
    for var in VARIABLES:
        mv = v == var
        for cols, (lo, hi) in ((["f12_1", "f6_2", "f6_1", "bp_1", "bp_2"], F_RANGES[var]),
                               (["outturn_level", "base_level_1", "base_level_2"], OUTTURN_RANGES[var])):
            x = df.loc[mv, cols]
            c6[mv] |= (x.notna() & ~x.apply(lambda col: col.between(lo, hi))).any(axis=1)
    fail[6] = c6
    # 7 formulas
    c7 = []
    for i, r in df.iterrows():
        o = derived(r["variable"], r)
        bad = False
        for k, x in o.items():
            y = r[k]
            if pd.notna(y) and (pd.isna(x) or abs(x - y) > 1e-6):
                bad = True
        c7.append(bad)
    fail[7] = pd.Series(c7, index=df.index)
    # 8 noise
    fail[8] = ((df["n_answers_1"] < 2) | (df["n_answers_2"] < 2) | (df["var_answers_1"] < 0) | (df["var_answers_2"] < 0))
    # 9 indicators
    complete = df[["revision", "error", "surprise"]].notna().all(axis=1)
    fail[9] = ~complete | (df["main"] != main_rows(df).astype(int))
    # 10 episodes
    fail[10] = df["episode"] != t.map(episode_of)
    # 11 large news
    L = large_news(df, scope)
    fail[11] = ~df["large"].isin([0, 1]) | (df["large"] != L)
    violated = ([1] if not cols_ok else []) + [k for k in range(2, 12) if (fail[k] & scope).any()]
    # anomalies outside the main rows: checks 3-8 on present cells (checks 4 and 7 need the cells; 4 is skipped)
    anomalies = int(sum((fail[k] & ~scope).sum() for k in (3, 5, 6, 7, 8)))
    return len(violated), anomalies, fail


# ------------------------------------------------------------------------------------------ estimation
def standardise(df):
    """Step 1: per variable, standardise revision and error (and their median versions) with the mean and the
    standard deviation (n-1) of the main rows. Returns (copy with z columns and t_target = half_year,
    {(variable, column): standard deviation})."""
    out = df.copy()
    out["t_target"] = out["half_year"]          # the period that k20.regress groups by
    return k20.standardise(out)


def regress(D, zr="z_r", ze="z_e", large="large", by_variable=False, lags=(LAGS,)):
    """Steps 3-4 with K20's estimator: 5 constants, 5 class effects, 5 base slopes, c (or 5 c_v);
    Driscoll-Kraay by half-year."""
    return k20.regress(D, zr=zr, ze=ze, large=large, by_variable=by_variable, lags=lags, variables=VARIABLES)


def pooled_slope(D, lags=LAGS):
    """Step 6 (positive control): one constant per variable and one pooled slope, no size split."""
    X = np.column_stack([(D["variable"] == v).astype(float).values for v in VARIABLES] + [D["z_r"].values])
    beta, u, _ = stats.ols(X, D["z_e"].values)
    V = stats.driscoll_kraay_cov(X, u, D["t_target"].values, lags)
    return float(beta[-1]), math.sqrt(V[-1, -1])


def run(df):
    """All 63 preregistered fields (French names, as in the sealed verdict) and the working data."""
    n_viol, n_anom, _ = schema_checks(df)
    d, consts = standardise(df)
    base = d[d["main"] == 1].copy()
    out = {"n_violations_schema": n_viol, "n_principal": len(base)}
    R = regress(base, lags=(2, 4, 0))
    c, se = k20.c_and_se(R, lags=2)
    lo, hi = c - CRIT * se, c + CRIT * se
    b_mean = float(np.mean(R["beta"][10:15]))
    k_mean = float(np.mean([consts[(v, "revision")] / consts[(v, "error")] for v in VARIABLES]))
    b_pooled, se_b = pooled_slope(base)
    out.update(c=c, et_c_dk2=se, t_c=c / se, borne_basse_ic90=lo, borne_haute_ic90=hi)
    dev = base["z_r"] - base.groupby(["variable", "large"])["z_r"].transform("mean")
    a, A = float(np.mean(dev[base["large"] == 0] ** 2)), float(np.mean(dev[base["large"] == 1] ** 2))
    nu_v = [float(np.median((base.loc[base["variable"] == v, "var_answers_1"] / base.loc[base["variable"] == v, "n_answers_1"]
                             + base.loc[base["variable"] == v, "var_answers_2"] / base.loc[base["variable"] == v, "n_answers_2"])
                            / consts[(v, "revision")] ** 2)) for v in VARIABLES]
    nu = float(np.mean(nu_v))
    factor = (2 * b_mean + k_mean) * (1 / a - 1 / A)
    floor = max(0.10, factor * nu)
    out.update(rapport_variance_revision=A / a, b_moyen=b_mean, k_moyen=k_mean, pente_moyenne_grandes=b_mean + c,
               b_regroupe=b_pooled, et_b_regroupe_dk2=se_b, borne_basse_b_ic90=b_pooled - CRIT * se_b)
    out["controle_positif_ok"] = int(out["borne_basse_b_ic90"] > 0 or hi < 0)
    out.update(nu_mesure=nu, biais_mecanique_mesure=factor * nu, biais_mecanique_nu20=factor * 0.10,
               seuil_survie_bas=floor, borne_basse_moins_seuil=lo - floor, marge_indecision=min(floor - lo, hi - 0.40))
    without = {}
    for k, name in enumerate(EPISODES, start=1):
        ck, sk = k20.c_and_se(regress(base[base["episode"] != name]), lags=2)
        without[k] = (ck, ck / sk, sk)
    t_min = min(w[1] for w in without.values())
    out.update(t_min_sans_episode=t_min, c_min_sans_episode=min(w[0] for w in without.values()),
               episode_t_min=min(k for k, w in without.items() if w[1] == t_min))
    out["conflit_robustesse"] = int(lo > floor and hi >= 0.40 and t_min < 1 and out["c_min_sans_episode"] > 0)
    se_iid = math.sqrt(R["iid"][15, 15])
    out.update(n_grands=int((base["large"] == 1).sum()), n_dates=int(base["half_year"].nunique()),
               n_dates_grands=int(base.loc[base["large"] == 1, "half_year"].nunique()), et_c_iid=se_iid,
               n_effectif=len(base) * (se_iid / se) ** 2)
    for k in without:
        out[f"c_sans_E{k}"] = without[k][0]
    out["et_c_dk4"], out["et_c_dk0"] = k20.c_and_se(R, lags=4)[1], k20.c_and_se(R, lags=0)[1]
    pandemic = d[(d["variable"] == "UNPR") & d["target"].isin(PANDEMIC_TARGETS) & (d["complete"] == 1)]
    out["c_avec_pandemie"], out["et_c_avec_pandemie_dk2"] = k20.c_and_se(regress(pd.concat([base, pandemic])), lags=2)
    out["c_depuis_1985"], out["et_c_depuis_1985_dk2"] = k20.c_and_se(regress(base[base["target"] >= "1985-06"]), lags=2)
    out["c_avant_2020"], out["et_c_avant_2020_dk2"] = k20.c_and_se(regress(base[base["target"] <= "2019-12"]), lags=2)
    out["c_mediane"], out["et_c_mediane_dk2"] = k20.c_and_se(regress(base, zr="z_r_med", ze="z_e_med"), lags=2)
    base["large_revision"] = (np.abs(base["z_r"]) > 1).astype(float)
    out["c_coupure_revision"], out["et_c_coupure_revision_dk2"] = k20.c_and_se(regress(base, large="large_revision"), lags=2)
    R1 = regress(base, by_variable=True)
    for i, v in enumerate(VARIABLES):
        out[f"c_{v}"] = k20.c_and_se(R1, 15 + i, lags=2)[0]
    for i, v in enumerate(VARIABLES):
        out[f"et_c_{v}_dk2"] = k20.c_and_se(R1, 15 + i, lags=2)[1]
    return out, {"data": d, "base": base, "main_fit": R, "by_variable_fit": R1, "without_episode": without,
                 "nu_by_variable": dict(zip(VARIABLES, nu_v)), "consts": consts}
