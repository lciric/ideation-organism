"""Forecast errors and revisions: the four analysis datasets, built from the raw files only.

Sign conventions, the same in all four tests:
- error    = outturn - forecast             (positive: the forecast was too low);
- revision = new forecast - older forecast  (same target, previous survey round or exercise).
Under-reaction means a positive slope of error on revision: after an upward revision the
outcome ends up even higher.

Each `build_*` function returns one row per unit of the preregistered analysis file
(English column names; the French names of the preregistration are given in each docstring).
"""
import io
import zipfile

import numpy as np
import pandas as pd

from . import data
from . import vintages as vt


def forecast_error(outturn, forecast):
    """outturn - forecast."""
    return outturn - forecast


def forecast_revision(new, old):
    """new forecast - older forecast for the same target."""
    return new - old


def _nan(x):
    return np.nan if x is None else x


# ------------------------------------------------------------------------------------------ H03-v2
H03_VINTAGES = [f"{l}{y % 100:02d}" for y in range(1999, 2026) for l in "WGSA"] + ["W26", "G26", "S26"]


def build_h03v2():
    """444 rows = 111 vintages x horizons 1-4 (H03-v2_analyse.csv). Columns (French name in brackets):
    vintage (millesime), t_vintage, title_month (mois_titre), first_F (t_premier_F), horizon, target (cible),
    t_target, forecast (projection, status F in vintage v), prev_vintage (millesime_precedent),
    prev_forecast (projection_precedente, status F in vintage v - 1), outturn_vintage (millesime_realise),
    t_read (t_lecture), outturn (realise, real time: status A in vintage q+2, else q+3, else q+4),
    revision and error, both rounded to one decimal as the preregistration prescribes."""
    series = {vt.vintage_number(c): vt.load_quarterly(c) for c in H03_VINTAGES}
    rows = []
    for code in H03_VINTAGES:
        tv = vt.vintage_number(code)
        s = series[tv]
        info = vt.vintage_info(s)
        prev = series.get(tv - 1)  # None for W99 (A98 is not in the list)
        for h in range(1, 5):
            q = tv + h
            outturn, t_read = vt.realtime_outturn(q, series)
            rows.append({
                "vintage": code, "t_vintage": tv, "title_month": info["title_month"], "first_F": info["first_F"],
                "horizon": h, "target": vt.quarter_label(q), "t_target": q,
                "forecast": _nan(vt.value_with_status(s, q, "F")),
                "prev_vintage": vt.vintage_code(tv - 1) if prev is not None else "",
                "prev_forecast": _nan(vt.value_with_status(prev, q, "F")) if prev is not None else np.nan,
                "outturn_vintage": vt.vintage_code(t_read) if t_read else "", "t_read": _nan(t_read),
                "outturn": _nan(outturn)})
    df = pd.DataFrame(rows)
    df["revision"] = forecast_revision(df["forecast"], df["prev_forecast"]).round(1)
    df["error"] = forecast_error(df["outturn"], df["forecast"]).round(1)
    return df


# ------------------------------------------------------------------------------------------ J02
J02_VINTAGES = [f"{l}{y % 100:02d}" for y in range(1999, 2026) for l in "WGSA"] + ["W26"]


def eurostat_series(name):
    """SDMX-CSV from Eurostat -> Series indexed by TIME_PERIOD ('1996-01' or '1997')."""
    raw = pd.read_csv(data.get(name), dtype=str, keep_default_na=False)
    return pd.Series(pd.to_numeric(raw["OBS_VALUE"].replace("", np.nan)).values, index=raw["TIME_PERIOD"])


def quarter_months(t):
    """The three months ('YYYY-MM') of quarter number t."""
    year, q = t // 4, t % 4 + 1
    return [f"{year}-{m:02d}" for m in range(3 * q - 2, 3 * q + 1)]


def build_j02():
    """108 rows, targets 1999-Q4 .. 2026-Q3 (J02_analyse.csv). For target q: f2 = projection (status F) in
    the vintage of quarter q-2, f3 = in the vintage of quarter q-3; outturn a(q) = 100 * (sum of the 3 monthly
    HICP indices of q / sum of the same months a year earlier - 1), latest Eurostat prc_hicp_minr (I15, EA),
    unrounded. revision = f2 - f3; error = a - f2."""
    hicp = eurostat_series("eurostat/prc_hicp_minr_M_I15_TOTAL_EA.csv")
    hicp = hicp[hicp.index <= "2026-09"]  # months after 2026-09 are ignored
    rows = []
    cache = {}
    for t in range(7999, 8107):
        row = {"target": vt.quarter_label(t), "t_target": t, "year": t // 4}
        for h in (2, 3):
            code = vt.vintage_code(t - h)
            if code not in cache:
                cache[code] = vt.load_quarterly(code)
            s = cache[code]
            info = vt.vintage_info(s)
            line = s[s["t"] == t]
            row.update({f"vintage_h{h}": code, f"t_vintage_h{h}": t - h, f"title_month_h{h}": info["title_month"],
                        f"title_year_h{h}": info["title_year"], f"first_F_h{h}": info["first_F"],
                        f"status_h{h}": line["status"].iloc[0] if len(line) else "",
                        f"forecast_h{h}": _nan(vt.value_with_status(s, t, "F"))})
        for k, (m, m_prev) in enumerate(zip(quarter_months(t), quarter_months(t - 4)), start=1):
            row[f"index_m{k}"] = hicp.get(m, np.nan)
            row[f"index_year_before_m{k}"] = hicp.get(m_prev, np.nan)
        rows.append(row)
    df = pd.DataFrame(rows)
    now = df[["index_m1", "index_m2", "index_m3"]].sum(axis=1, min_count=3)
    before = df[["index_year_before_m1", "index_year_before_m2", "index_year_before_m3"]].sum(axis=1, min_count=3)
    df["outturn"] = 100 * (now / before - 1)
    df["revision"] = forecast_revision(df["forecast_h2"], df["forecast_h3"])
    df["error"] = forecast_error(df["outturn"], df["forecast_h2"])
    return df


# ------------------------------------------------------------------------------------------ K01
K01_VINTAGES = ["A01"] + [f"{l}{y % 100:02d}" for y in range(2002, 2026) for l in "WGSA"]


def read_ecb_spf_points():
    """Point forecasts of annual HICP inflation, individual forecasters, ECB SPF rounds 2001Q4-2025Q4
    (root copy of 1_HICP.csv in the archive; AGG and ECB rows dropped)."""
    with zipfile.ZipFile(data.get("ecb_spf/SPF_microdata_by_variable.zip")) as z:
        raw = pd.read_csv(io.BytesIO(z.read("1_HICP.csv")), dtype=str, keep_default_na=False)
    keep = ((raw["table_name"] == "Point") & raw["forecaster_id"].str.fullmatch(r"\d{3}")
            & raw["target_period_type"].isin(["A_YEAR_0_AHEAD", "A_YEAR_1_AHEAD", "A_YEAR_2_AHEAD"])
            & (raw["ref_round"] >= "2001Q4") & (raw["ref_round"] <= "2025Q4"))
    p = raw[keep]
    return pd.DataFrame({"source": "SPF", "forecaster": p["forecaster_id"].values, "round": p["ref_round"].values,
                         "t_round": [vt.quarter_number(int(r[:4]), int(r[-1])) for r in p["ref_round"]],
                         "vintage": "", "status": "", "title_month": np.nan, "title_year": np.nan,
                         "target_year": p["target_period"].astype(int).values,
                         "forecast": pd.to_numeric(p["value"]).values})


def read_ecb_staff_annual():
    """ECB/Eurosystem staff annual HICP projections: for each of 97 vintages (A01, W02 .. A25) of year Y,
    the years Y, Y+1, Y+2 with status F."""
    rows = []
    for code in K01_VINTAGES:
        s = vt.load_annual(code)
        info = vt.vintage_info(s)
        Y, t = vt.code_year(code), vt.vintage_number(code)
        for y in (Y, Y + 1, Y + 2):
            line = s[(s["t"] == y) & (s["status"] == "F")]
            if len(line):
                rows.append({"source": "BCE", "forecaster": "BCE", "round": f"{Y}Q{vt.LETTER_QUARTER[code[0]]}",
                             "t_round": t, "vintage": code, "status": "F", "title_month": info["title_month"],
                             "title_year": info["title_year"], "target_year": y,
                             "forecast": float(line["value"].iloc[0])})
    return pd.DataFrame(rows)


def build_k01():
    """One row per source x forecaster x round x target year (K01_analyse.csv). Columns (French in brackets):
    source, forecaster (id_prev), round (tour), t_round, vintage, status, title_month, title_year,
    target_year (annee_cible), horizon (target year - round year), rank, forecast (prevision),
    prev_forecast (same forecaster, round t-1, same target), revision, other_target (y+1 if horizon 0,
    y-1 if horizon 1), other_forecast, other_prev_forecast, instrument (revision of the other target in the same
    round), outturn (Eurostat prc_hicp_ainr, y <= 2025), error, n_complete_rounds (nb_tours_complets),
    iv_sample (echantillon_iv)."""
    df = pd.concat([read_ecb_spf_points(), read_ecb_staff_annual()], ignore_index=True)
    df["horizon"] = df["target_year"] - df["t_round"] // 4
    df["rank"] = df["t_round"] - 4 * (df["target_year"] - 1) + 1
    lookup = dict(zip(zip(df["source"], df["forecaster"], df["t_round"], df["target_year"]), df["forecast"]))

    def find(src, fid, t, y):
        return lookup.get((src, fid, t, y), np.nan)

    first = df["t_round"] == 8007  # 2001Q4 / A01 only provide the previous forecasts of 2002Q1
    df["prev_forecast"] = [np.nan if f else find(s, i, t - 1, y)
                           for s, i, t, y, f in zip(df["source"], df["forecaster"], df["t_round"], df["target_year"], first)]
    df["revision"] = forecast_revision(df["forecast"], df["prev_forecast"])
    df["other_target"] = np.where(df["horizon"] == 0, df["target_year"] + 1,
                                  np.where(df["horizon"] == 1, df["target_year"] - 1, np.nan))
    df["other_forecast"] = [np.nan if np.isnan(o) else find(s, i, t, int(o))
                            for s, i, t, o in zip(df["source"], df["forecaster"], df["t_round"], df["other_target"])]
    df["other_prev_forecast"] = [np.nan if (np.isnan(o) or f) else find(s, i, t - 1, int(o))
                                 for s, i, t, o, f in zip(df["source"], df["forecaster"], df["t_round"],
                                                          df["other_target"], first)]
    df["instrument"] = forecast_revision(df["other_forecast"], df["other_prev_forecast"])
    hicp = eurostat_series("eurostat/prc_hicp_ainr_A_RCH_A_AVG_TOTAL_EA.csv")
    df["outturn"] = [hicp.get(str(y), np.nan) if y <= 2025 else np.nan for y in df["target_year"]]
    df["error"] = forecast_error(df["outturn"], df["forecast"])
    usable = ((df["source"] == "SPF") & df["horizon"].isin([0, 1]) & df["t_round"].between(8008, 8103)
              & df["revision"].notna() & df["instrument"].notna() & df["error"].notna())
    rounds = df[usable].groupby("forecaster")["t_round"].nunique()
    df["n_complete_rounds"] = np.where(df["source"] == "SPF", df["forecaster"].map(rounds).fillna(0), np.nan)
    df["iv_sample"] = (usable & (df["n_complete_rounds"] >= 8)).astype(int)
    return df.sort_values(["source", "forecaster", "t_round", "target_year"], ignore_index=True)


# ------------------------------------------------------------------------------------------ K20
K20_VARIABLES = {  # variable: (growth or level workbook, sheet, column prefix)
    "PGDP": ("Growth", "PGDP", "dpgdp"), "RGDP": ("Growth", "RGDP", "drgdp"),
    "UNEMP": ("Level", "UNEMP", "UNEMP"), "CPI": ("Level", "CPI", "CPI"), "TBILL": ("Level", "TBILL", "TBILL")}
K20_EPISODES = {"E1": (7879, 7887), "E2": (7895, 7904), "E3": (7920, 7935), "E4": (7962, 7968),
                "E5": (8004, 8011), "E6": (8031, 8041), "E7": (8079, 8095)}
FRED_SERIES = {"UNEMP": "UNRATE", "CPI": "CPIAUCSL", "TBILL": "TB3MS"}


def read_philly_spf(stat, variable):
    """Consensus (stat = 'mean' or 'median') survey of variable -> DataFrame indexed by survey quarter number
    with columns q2 (current quarter), q5 (3 quarters ahead), q6 (4 quarters ahead)."""
    kind, sheet, prefix = K20_VARIABLES[variable]
    raw = data.read_excel(data.get(f"philly_spf/{stat}{kind}.xlsx"), sheet)
    out = pd.DataFrame({f"q{k}": pd.to_numeric(raw[f"{prefix}{k}"], errors="coerce").values for k in (2, 5, 6)})
    out.index = [vt.quarter_number(int(y), int(q)) for y, q in zip(raw["YEAR"], raw["QUARTER"])]
    return out


def rtdsm_vintages(variable):
    """Philadelphia Fed real-time data set (P or ROUTPUT): DataFrame of levels, rows = quarter number,
    columns = vintage codes, sorted by vintage number."""
    name, sheet = {"PGDP": ("pQvQd", "P"), "RGDP": ("routputQvQd", "ROUTPUT")}[variable]
    raw = data.read_excel(data.get(f"philly_rtdsm/{name}.xlsx"), sheet)
    raw.index = [vt.quarter_number(int(d[:4]), int(d[-1])) for d in raw["DATE"]]
    levels = raw.drop(columns="DATE").apply(pd.to_numeric, errors="coerce")
    return levels[sorted(levels.columns, key=rtdsm_vintage_number)]


def rtdsm_vintage_number(code):
    """'P96Q2' or 'ROUTPUT96Q2' -> quarter number (years >= 60 are 19xx)."""
    yy, q = int(code[-4:-2]), int(code[-1])
    return vt.quarter_number(1900 + yy if yy >= 60 else 2000 + yy, q)


def first_release(levels, t):
    """First publication of quarter t: the first vintage numbered after t where rows t and t-1 are both filled.
    Returns (vintage code, level of t, level of t-1) or ('', nan, nan)."""
    if t not in levels.index or t - 1 not in levels.index:
        return "", np.nan, np.nan
    for code in levels.columns:
        if rtdsm_vintage_number(code) > t and pd.notna(levels.at[t, code]) and pd.notna(levels.at[t - 1, code]):
            return code, levels.at[t, code], levels.at[t - 1, code]
    return "", np.nan, np.nan


def fred_quarterly_mean(series):
    """Latest FRED vintage of a monthly series -> Series of quarterly means (NaN if a month is missing)."""
    raw = pd.read_csv(data.get(f"fred/{series}.csv"), dtype=str, keep_default_na=False)
    values = pd.to_numeric(raw.iloc[:, 1].replace({"": np.nan, ".": np.nan}))
    dates = pd.to_datetime(raw["observation_date"])
    t = [vt.quarter_number(d.year, (d.month - 1) // 3 + 1) for d in dates]
    g = pd.DataFrame({"t": t, "v": values}).groupby("t")["v"]
    return g.mean().where(g.count() == 3)


def annualised(level, level_before):
    """Quarterly growth at an annual rate, in %: 100 * ((level / level_before)^4 - 1)."""
    return 100 * ((level / level_before) ** 4 - 1)


def k20_outturn(variable, t, rt=None, fred=None):
    """(vintage label, level, previous level, outturn) of quarter t, as defined in K20 section 4.2."""
    if variable in ("PGDP", "RGDP"):
        code, lvl, before = first_release(rt, t)
        return code, lvl, before, (annualised(lvl, before) if code else np.nan)
    lvl = fred.get(t, np.nan)
    if variable == "CPI":
        before = fred.get(t - 1, np.nan)
        value = annualised(lvl, before)
    else:
        before, value = np.nan, lvl
    return ("FRED" if pd.notna(value) else ""), lvl, before, value


def build_k20():
    """1 038 rows = variable x target quarter (K20_analyse.csv): PGDP, RGDP, UNEMP 1969-Q4..2026-Q3,
    CPI, TBILL 1982-Q3..2026-Q3. Philadelphia Fed SPF mean consensus: f_h3 = column 5 of survey t-3,
    f_h4 = column 6 of survey t-4, nowcast_q4 = column 2 of survey t-4 (medians kept for S6).
    revision = f_h3 - f_h4; error = outturn - f_h3; surprise = outturn(t-4) - nowcast_q4.
    `main` drops RGDP and UNEMP targets 2020-Q1..2021-Q4; `large` (grande_nouvelle) = |surprise| above the
    2/3 quantile of |surprise| over the main rows of the variable."""
    rows = []
    for v in K20_VARIABLES:
        mean, med = read_philly_spf("mean", v), read_philly_spf("median", v)
        rt = rtdsm_vintages(v) if v in ("PGDP", "RGDP") else None
        fred = fred_quarterly_mean(FRED_SERIES[v]) if v in FRED_SERIES else None
        start = 7879 if v in ("PGDP", "RGDP", "UNEMP") else 7930
        for t in range(start, 8107):
            code, lvl, before, a = k20_outturn(v, t, rt, fred)
            code4, lvl4, before4, a4 = k20_outturn(v, t - 4, rt, fred)
            rows.append({
                "variable": v, "target": vt.quarter_label(t), "t_target": t, "year": t // 4,
                "t_survey_h3": t - 3, "t_survey_h4": t - 4,
                "f_h3": mean.at[t - 3, "q5"], "f_h4": mean.at[t - 4, "q6"], "nowcast_q4": mean.at[t - 4, "q2"],
                "f_h3_med": med.at[t - 3, "q5"], "f_h4_med": med.at[t - 4, "q6"],
                "outturn_vintage": code, "level": lvl, "level_before": before, "outturn": a,
                "outturn_vintage_q4": code4, "level_q4": lvl4, "level_before_q4": before4, "outturn_q4": a4})
    df = pd.DataFrame(rows)
    df["revision"] = forecast_revision(df["f_h3"], df["f_h4"])
    df["error"] = forecast_error(df["outturn"], df["f_h3"])
    df["surprise"] = forecast_error(df["outturn_q4"], df["nowcast_q4"])
    df["revision_med"] = forecast_revision(df["f_h3_med"], df["f_h4_med"])
    df["error_med"] = forecast_error(df["outturn"], df["f_h3_med"])
    df["complete"] = (df["revision"].notna() & df["error"].notna() & df["surprise"].notna()).astype(int)
    pandemic = df["variable"].isin(["RGDP", "UNEMP"]) & df["t_target"].between(8080, 8087)
    df["main"] = ((df["complete"] == 1) & ~pandemic).astype(int)
    df["episode"] = ""
    for name, (lo, hi) in K20_EPISODES.items():
        df.loc[df["t_target"].between(lo, hi), "episode"] = name
    df["large"] = np.nan
    for v in K20_VARIABLES:
        main_v = (df["variable"] == v) & (df["main"] == 1)
        cut = np.quantile(np.abs(df.loc[main_v, "surprise"]), 2 / 3)
        has = (df["variable"] == v) & df["surprise"].notna()
        df.loc[has, "large"] = (np.abs(df.loc[has, "surprise"]) > cut).astype(float)
    return df
