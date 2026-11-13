"""ECB/Eurosystem staff projection vintages (Macroeconomic Projection Database, MPD).

A vintage is one projection exercise, coded by a letter and a two-digit year. The letter mapping,
checked against the exercise name in the TITLE_COMPL column (the TITLE column is empty), is:
W = March (quarter 1), G = June (quarter 2), S = September (quarter 3), A = December (quarter 4).
(The voided first run of H03 had G and S swapped.)

Quarters are numbered t = 4 * year + (quarter - 1): 1999-Q1 -> 7996, 2021-Q1 -> 8084.
A vintage's number is the number of its own quarter: W21 -> 8084, G21 -> 8085.
"""
import re

import numpy as np
import pandas as pd

from . import data

LETTER_QUARTER = {"W": 1, "G": 2, "S": 3, "A": 4}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]


def quarter_number(year, quarter):
    return 4 * year + quarter - 1


def quarter_label(t):
    """7996 -> '1999-Q1'."""
    return f"{t // 4}-Q{t % 4 + 1}"


def code_year(code):
    yy = int(code[1:])
    return 1900 + yy if yy >= 90 else 2000 + yy


def vintage_number(code):
    """'W21' -> 8084."""
    return quarter_number(code_year(code), LETTER_QUARTER[code[0]])


def vintage_code(t):
    """8084 -> 'W21' (inverse of vintage_number)."""
    return f"{'WGSA'[t % 4]}{(t // 4) % 100:02d}"


def title_month(title):
    """Month (1-12) of the last full English month name in the title, or None ('Spring/June 2025' -> 6)."""
    names = re.findall(r"\b(" + "|".join(MONTHS) + r")\b", title)
    return MONTHS.index(names[-1]) + 1 if names else None


def title_year(title):
    """Last four-digit year in the title, or None."""
    years = re.findall(r"\b(19\d\d|20\d\d)\b", title)
    return int(years[-1]) if years else None


def read_mpd(path):
    """One MPD series file -> DataFrame with columns period, t, value, status, title.
    For quarterly files t is the quarter number; for annual files t is the year."""
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    out = pd.DataFrame({"period": raw["TIME_PERIOD"], "status": raw["OBS_STATUS"], "title": raw["TITLE_COMPL"]})
    out["value"] = pd.to_numeric(raw["OBS_VALUE"].replace("", np.nan))
    if out["period"].str.contains("-Q").all():
        out["t"] = [quarter_number(int(p[:4]), int(p[-1])) for p in out["period"]]
    else:
        out["t"] = out["period"].astype(int)
    return out


def load_quarterly(code):
    return read_mpd(data.get(f"ecb_mpd/MPD_Q_U2_HIC_A_{code}.csv"))


def load_annual(code):
    return read_mpd(data.get(f"ecb_mpd/MPD_A_U2_HIC_A_{code}.csv"))


def value_with_status(series, t, status):
    """The value at period t if the row exists, is not empty and has the given OBS_STATUS
    ('F' = projected, 'A' = observed); otherwise None."""
    row = series[(series["t"] == t) & (series["status"] == status) & series["value"].notna()]
    return float(row["value"].iloc[0]) if len(row) else None


def first_projected(series):
    """Number of the first period with status F, or None."""
    f = series.loc[series["status"] == "F", "t"]
    return int(f.min()) if len(f) else None


def vintage_info(series):
    """Month and year written in TITLE_COMPL and the first projected period of one vintage."""
    title = series["title"].iloc[0]
    return {"title_month": title_month(title), "title_year": title_year(title),
            "first_F": first_projected(series)}


def realtime_outturn(target, vintages, last_vintage=8106):
    """H03-v2 real-time realisation of quarter `target`: the observed value (status A) in the vintage
    published two quarters later; if missing, three, then four quarters later. Vintages outside the
    frozen list (number > last_vintage) cannot be used. Returns (value, reading vintage number) or (None, None).
    `vintages` maps vintage number -> series."""
    for lag in (2, 3, 4):
        tv = target + lag
        if tv > last_vintage or tv not in vintages:
            continue
        v = value_with_status(vintages[tv], target, "A")
        if v is not None:
            return v, tv
    return None, None
