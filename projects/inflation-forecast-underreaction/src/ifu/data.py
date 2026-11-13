"""Raw data: download each source file once, keep it in data/raw/, and record where it came from.

Every file is fetched by `get(name)`. If the file is already in the cache it is reused as is;
otherwise it is downloaded (with retries and growing waits, because the ECB and Eurostat APIs
are intermittent) and written without any change. Each file's URL, origin, date, sha256 and
number of rows go to data/raw/provenance.json, from which data/raw/PROVENANCE.md is written.
"""
import datetime
import hashlib
import json
import os
import shutil
import time
import urllib.request
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
RAW = Path(os.environ.get("IFU_RAW_DIR", PROJECT / "data" / "raw"))

ECB_API = "https://data-api.ecb.europa.eu/service/data/MPD/"
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
PHILLY_SPF = ("https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/"
              "survey-of-professional-forecasters/historical-data/")
PHILLY_RTDSM = "https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
ALFRED = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id="

# The vintage codes used by at least one test (letter + two-digit year; W=Mar, G=Jun, S=Sep, A=Dec).
QUARTERLY_CODES = [f"{l}{y % 100:02d}" for y in range(1999, 2026) for l in "WGSA"] + ["W26", "G26", "S26"]
ANNUAL_CODES = ["A01"] + [f"{l}{y % 100:02d}" for y in range(2002, 2026) for l in "WGSA"]


def catalogue():
    """Map every cache file name (relative to data/raw) to (URL, expected start of the file)."""
    cat = {}
    for code in QUARTERLY_CODES:
        cat[f"ecb_mpd/MPD_Q_U2_HIC_A_{code}.csv"] = (ECB_API + f"Q.U2.HIC.A.{code}.0000?format=csvdata", b"KEY,")
    for code in ANNUAL_CODES:
        cat[f"ecb_mpd/MPD_A_U2_HIC_A_{code}.csv"] = (ECB_API + f"A.U2.HIC.A.{code}.0000?format=csvdata", b"KEY,")
    cat["ecb_mpd/MPD_serieskeysonly.csv"] = (ECB_API[:-1] + "?detail=serieskeysonly&format=csvdata", b"KEY,")
    cat["ecb_spf/SPF_microdata_by_variable.zip"] = (
        "https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip", b"PK")
    cat["eurostat/prc_hicp_minr_M_I15_TOTAL_EA.csv"] = (
        EUROSTAT + "prc_hicp_minr/M.I15.TOTAL.EA?format=SDMX-CSV", b"DATAFLOW")
    cat["eurostat/prc_hicp_ainr_A_RCH_A_AVG_TOTAL_EA.csv"] = (
        EUROSTAT + "prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV", b"DATAFLOW")
    for f in ["meanGrowth", "meanLevel", "medianGrowth", "medianLevel"]:
        cat[f"philly_spf/{f}.xlsx"] = (PHILLY_SPF + f + ".xlsx", b"PK")
    for f in ["pQvQd", "routputQvQd"]:
        cat[f"philly_rtdsm/{f}.xlsx"] = (PHILLY_RTDSM + f + ".xlsx", b"PK")
    for s in ["UNRATE", "CPIAUCSL", "TB3MS", "USRECQP"]:
        cat[f"fred/{s}.csv"] = (FRED + s, b"observation_date")
    return cat


def download(url, start, tries=10, first_wait=5, timeout=120):
    """Return the body of `url`. Retry on errors, on empty bodies (FRED sometimes sends them) and on
    bodies that do not start as expected (an HTML error page). Waits grow: 5, 10, 20 s ... capped at 60 s.
    Python's default user agent is used on purpose: FRED/ALFRED refuse many browser-like agents."""
    wait, last = first_wait, None
    for attempt in range(1, tries + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as resp:
                body = resp.read()
            if body.startswith(start):
                return body, attempt
            last = f"unexpected start {body[:40]!r}"
        except Exception as exc:  # HTTP 503, time-outs, resets
            last = repr(exc)
        if attempt < tries:
            time.sleep(wait)
            wait = min(2 * wait, 60)
    raise RuntimeError(f"could not download {url} after {tries} tries: {last}")


def alfred_csv(series, vintage_date):
    """One ALFRED vintage of a FRED series (not used by the four tests; kept for real-time extensions)."""
    url = ALFRED + f"{series}&vintage_date={vintage_date}"
    return download(url, b"observation_date")[0]


def _log_path():
    return RAW / "provenance.json"


def _read_log():
    p = _log_path()
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _record(name, url, origin):
    log = _read_log()
    path = RAW / name
    log[name] = {"url": url, "origin": origin,
                 "date_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
    _log_path().write_text(json.dumps(log, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def get(name):
    """Path of cache file `name`; downloads it first if it is not in the cache."""
    path = RAW / name
    if path.exists():
        return path
    url, start = catalogue()[name]
    body, attempts = download(url, start)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    _record(name, url, f"downloaded ({attempts} attempt(s))")
    return path


def get_all():
    """Make sure every file of the catalogue is in the cache."""
    for name in catalogue():
        get(name)


# --------------------------------------------------------------------------- seeding from the sealed tests
def seed_sources():
    """Where each cache file can be found among the raw downloads of the sealed tests (raw files only)."""
    src = {}
    for code in QUARTERLY_CODES:
        folder = "H03-v2"  # the J02 copies are byte-identical; H03-v2 is the only one with G26 and S26
        src[f"ecb_mpd/MPD_Q_U2_HIC_A_{code}.csv"] = f"{folder}/donnees/MPD_Q_U2_HIC_A_{code}.csv"
    for code in ANNUAL_CODES:
        src[f"ecb_mpd/MPD_A_U2_HIC_A_{code}.csv"] = f"K01/donnees/MPD_A.U2.HIC.A.{code}.0000.csv"
    src["ecb_mpd/MPD_serieskeysonly.csv"] = "H03-v2/donnees/MPD_serieskeysonly.csv"
    src["ecb_spf/SPF_microdata_by_variable.zip"] = "K01/donnees/SPF_microdata_by_variable.zip"
    src["eurostat/prc_hicp_minr_M_I15_TOTAL_EA.csv"] = "J02/donnees/prc_hicp_minr_M_I15_TOTAL_EA.csv"
    src["eurostat/prc_hicp_ainr_A_RCH_A_AVG_TOTAL_EA.csv"] = "K01/donnees/prc_hicp_ainr_A.RCH_A_AVG.TOTAL.EA.csv"
    for f in ["meanGrowth", "meanLevel", "medianGrowth", "medianLevel"]:
        src[f"philly_spf/{f}.xlsx"] = f"K20/donnees/{f}.xlsx"
    for f in ["pQvQd", "routputQvQd"]:
        src[f"philly_rtdsm/{f}.xlsx"] = f"K20/donnees/{f}.xlsx"
    for s in ["UNRATE", "CPIAUCSL", "TB3MS", "USRECQP"]:
        src[f"fred/{s}.csv"] = f"K20/donnees/{s}.csv"
    return src


def seed_from(tests_dir):
    """Copy, byte for byte, the raw files the sealed tests downloaded into the empty cache slots."""
    tests_dir = Path(tests_dir)
    cat = catalogue()
    for name, rel in seed_sources().items():
        target, source = RAW / name, tests_dir / rel
        if target.exists() or not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        _record(name, cat[name][0], f"copied from sealed test folder tests-de-mort/{rel}")


# --------------------------------------------------------------------------- PROVENANCE.md
def count_rows(name):
    """Data rows of a cache file (CSV: lines minus header; zip: rows of 1_HICP.csv; xlsx: first sheet)."""
    path = RAW / name
    if name.endswith(".csv"):
        return max(len(path.read_bytes().splitlines()) - 1, 0)
    if name.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            return len(z.read("1_HICP.csv").splitlines()) - 1
    return len(read_excel(path, 0))


def read_excel(path, sheet):
    """pandas.read_excel with a work-around: openpyxl 3.1 refuses the Philadelphia real-time files because
    of a malformed date in their document properties, so we skip reading those properties."""
    import openpyxl.reader.excel
    import pandas as pd
    openpyxl.reader.excel.ExcelReader.read_properties = lambda self: None
    return pd.read_excel(path, sheet_name=sheet)


def write_provenance():
    """Write data/raw/PROVENANCE.md from provenance.json and the files on disk."""
    log = _read_log()
    lines = ["# Provenance of the raw data cache", "",
             "Every file below is kept exactly as received. `origin` says whether it was downloaded by",
             "`src/ifu/data.py` or copied, byte for byte, from the raw-download folder (`donnees/`) of one of the",
             "sealed tests (`ideation-finance/tests-de-mort/<ID>/donnees/`, downloaded there on 2026-11-12/13 and",
             "listed in that folder's own PROVENANCE.md). Only raw API responses and source files were copied, never",
             "an analysis CSV. Delete `data/raw/` and run `python run_all.py` to download everything again.",
             "`date (UTC)` is the date the file entered this cache. `rows` = data rows (CSV: lines minus header;",
             "zip: rows of `1_HICP.csv`; xlsx: rows of the first sheet minus header).", "",
             "| file | URL | origin | date (UTC) | sha256 | bytes | rows |", "|---|---|---|---|---|---|---|"]
    for name in sorted(log):
        e = log[name]
        sha = hashlib.sha256((RAW / name).read_bytes()).hexdigest()
        flag = "" if sha == e["sha256"] else " (CHANGED since logged)"
        lines.append(f"| `{name}` | {e['url']} | {e['origin']} | {e['date_utc']} | `{sha}`{flag} | "
                     f"{e['bytes']} | {count_rows(name)} |")
    (RAW / "PROVENANCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3 and sys.argv[1] == "--seed":
        seed_from(sys.argv[2])
    get_all()
    write_provenance()
