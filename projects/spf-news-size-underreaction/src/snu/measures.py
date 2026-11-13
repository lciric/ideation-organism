"""Forecast errors, revisions and surprises: the K20 analysis dataset, built from the raw files only.

Sign conventions:
- error    = outturn - forecast             (positive: the forecast was too low);
- revision = new forecast - older forecast  (same target, previous survey);
- surprise = outturn of quarter t-4 - the consensus nowcast of quarter t-4 made in survey t-4.
Under-reaction means a positive slope of error on revision: after an upward revision the outcome
ends up even higher than the revised forecast.

Quarters are numbered t = 4 * year + (quarter - 1): 1969-Q4 -> 7879, 1982-Q3 -> 7930, 2026-Q3 -> 8106.
"""
import numpy as np
import pandas as pd

from . import data

K20_VARIABLES = {  # variable: (growth or level workbook, sheet, column prefix)
    "PGDP": ("Growth", "PGDP", "dpgdp"), "RGDP": ("Growth", "RGDP", "drgdp"),
    "UNEMP": ("Level", "UNEMP", "UNEMP"), "CPI": ("Level", "CPI", "CPI"), "TBILL": ("Level", "TBILL", "TBILL")}
# Episode windows in target quarters: NBER peak to trough + 4 quarters, overlapping windows merged,
# E7 joins the 2020 recession and the 2021-2023 inflation surge (preregistration section 6).
K20_EPISODES = {"E1": (7879, 7887), "E2": (7895, 7904), "E3": (7920, 7935), "E4": (7962, 7968),
                "E5": (8004, 8011), "E6": (8031, 8041), "E7": (8079, 8095)}
EPISODE_LABELS = {"E1": "1969Q4-1971Q4", "E2": "1973Q4-1976Q1", "E3": "1980Q1-1983Q4", "E4": "1990Q3-1992Q1",
                  "E5": "2001Q1-2002Q4", "E6": "2007Q4-2010Q2", "E7": "2019Q4-2023Q4"}
FRED_SERIES = {"UNEMP": "UNRATE", "CPI": "CPIAUCSL", "TBILL": "TB3MS"}


def quarter_number(year, quarter):
    """(1969, 4) -> 7879."""
    return 4 * year + quarter - 1


def quarter_label(t):
    """7879 -> '1969-Q4'."""
    return f"{t // 4}-Q{t % 4 + 1}"


def forecast_error(outturn, forecast):
    """outturn - forecast."""
    return outturn - forecast


def forecast_revision(new, old):
    """new forecast - older forecast for the same target."""
    return new - old


def annualised(level, level_before):
    """Quarterly growth at an annual rate, in %: 100 * ((level / level_before)^4 - 1)."""
    return 100 * ((level / level_before) ** 4 - 1)


def read_philly_spf(stat, variable):
    """Consensus (stat = 'mean' or 'median') of `variable` -> DataFrame indexed by survey quarter number,
    columns q2 (current quarter), q5 (3 quarters ahead), q6 (4 quarters ahead)."""
    kind, sheet, prefix = K20_VARIABLES[variable]
    raw = data.read_excel(data.get(f"philly_spf/{stat}{kind}.xlsx"), sheet)
    out = pd.DataFrame({f"q{k}": pd.to_numeric(raw[f"{prefix}{k}"], errors="coerce").values for k in (2, 5, 6)})
    out.index = [quarter_number(int(y), int(q)) for y, q in zip(raw["YEAR"], raw["QUARTER"])]
    return out


def rtdsm_vintage_number(code):
    """'P96Q2' or 'ROUTPUT96Q2' -> quarter number (two-digit years >= 60 are 19xx)."""
    yy, q = int(code[-4:-2]), int(code[-1])
    return quarter_number(1900 + yy if yy >= 60 else 2000 + yy, q)


def rtdsm_vintages(variable):
    """Philadelphia Fed real-time data set (P or ROUTPUT): levels, rows = quarter number,
    columns = vintage codes sorted by vintage number."""
    name, sheet = {"PGDP": ("pQvQd", "P"), "RGDP": ("routputQvQd", "ROUTPUT")}[variable]
    raw = data.read_excel(data.get(f"philly_rtdsm/{name}.xlsx"), sheet)
    raw.index = [quarter_number(int(d[:4]), int(d[-1])) for d in raw["DATE"]]
    levels = raw.drop(columns="DATE").apply(pd.to_numeric, errors="coerce")
    return levels[sorted(levels.columns, key=rtdsm_vintage_number)]


def first_release(levels, t):
    """First publication of quarter t: the first vintage numbered after t in which rows t and t-1 are both
    filled. Returns (vintage code, level of t, level of t-1) or ('', nan, nan)."""
    if t not in levels.index or t - 1 not in levels.index:
        return "", np.nan, np.nan
    for code in levels.columns:
        if rtdsm_vintage_number(code) > t and pd.notna(levels.at[t, code]) and pd.notna(levels.at[t - 1, code]):
            return code, levels.at[t, code], levels.at[t - 1, code]
    return "", np.nan, np.nan


def fred_quarterly_mean(series):
    """Latest FRED vintage of a monthly series -> quarterly means (NaN if any of the three months is missing)."""
    raw = pd.read_csv(data.get(f"fred/{series}.csv"), dtype=str, keep_default_na=False)
    values = pd.to_numeric(raw.iloc[:, 1].replace({"": np.nan, ".": np.nan}))
    dates = pd.to_datetime(raw["observation_date"])
    t = [quarter_number(d.year, (d.month - 1) // 3 + 1) for d in dates]
    g = pd.DataFrame({"t": t, "v": values}).groupby("t")["v"]
    return g.mean().where(g.count() == 3)


def k20_outturn(variable, t, rt=None, fred=None):
    """(vintage label, level, previous level, outturn) of quarter t (preregistration section 4.2):
    first release for PGDP and RGDP, latest FRED vintage for UNEMP, CPI and TBILL."""
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
    """1 038 rows = variable x target quarter (the preregistered K20_analyse.csv, English column names):
    PGDP, RGDP, UNEMP targets 1969-Q4..2026-Q3; CPI, TBILL 1982-Q3..2026-Q3.

    Mean consensus of the Philadelphia Fed SPF: f_h3 (prev_h3) = column 5 of survey t-3, f_h4 (prev_h4) =
    column 6 of survey t-4, nowcast_q4 = column 2 of survey t-4; medians kept for the S6 check.
    revision = f_h3 - f_h4; error (erreur) = outturn (realise) - f_h3; surprise = outturn(t-4) - nowcast_q4.
    `main` (principal) drops RGDP and UNEMP targets 2020-Q1..2021-Q4; `large` (grande_nouvelle) = 1 when
    |surprise| is above the 2/3 quantile of |surprise| over the main rows of the variable."""
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
                "variable": v, "target": quarter_label(t), "t_target": t, "year": t // 4,
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
    df["large"] = top_third(df, "surprise")
    return df


def top_third(df, col):
    """1.0 where |col| is above the 2/3 quantile (numpy linear method) of |col| over the main rows of the
    same variable, 0.0 elsewhere, NaN where col is missing. The cut is strict: |col| > Q_v."""
    out = pd.Series(np.nan, index=df.index)
    for v in df["variable"].unique():
        main_v = (df["variable"] == v) & (df["main"] == 1)
        cut = np.quantile(np.abs(df.loc[main_v, col]), 2 / 3)
        has = (df["variable"] == v) & df[col].notna()
        out[has] = (np.abs(df.loc[has, col]) > cut).astype(float)
    return out
