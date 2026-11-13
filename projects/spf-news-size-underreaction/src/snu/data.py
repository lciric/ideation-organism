"""Raw data: download each source file once, keep it in data/raw/, and record where it came from.

`get(name)` returns the path of a cache file. If the file is already in the cache it is reused as is;
otherwise it is downloaded (with retries and growing waits) and written without any change. Each file's
URL, origin, date, sha256 and size go to data/raw/provenance.json, from which data/raw/PROVENANCE.md is
written.

The catalogue is grouped by test (`CATALOGUES`). A later test (for instance the euro-area replication
K20-ZE) adds its own group of files here; nothing else in this module changes.
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
RAW = Path(os.environ.get("SNU_RAW_DIR", PROJECT / "data" / "raw"))

PHILLY_SPF = ("https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/"
              "survey-of-professional-forecasters/historical-data/")
PHILLY_RTDSM = "https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
ECB_SPF = "https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip"
EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"

# FRED answers reliably only to curl's default user agent; the Philadelphia Fed accepts it too.
USER_AGENT = "curl/8.5.0"


def k20_catalogue():
    """K20 files: cache name -> (URL, expected first bytes of a valid file)."""
    cat = {}
    for f in ["meanGrowth", "meanLevel", "medianGrowth", "medianLevel"]:
        cat[f"philly_spf/{f}.xlsx"] = (PHILLY_SPF + f + ".xlsx", b"PK")
    for f in ["pQvQd", "routputQvQd"]:
        cat[f"philly_rtdsm/{f}.xlsx"] = (PHILLY_RTDSM + f + ".xlsx", b"PK")
    for s in ["UNRATE", "CPIAUCSL", "TB3MS", "USRECQP"]:
        cat[f"fred/{s}.csv"] = (FRED + s, b"observation_date")
    return cat


def k20ze_catalogue():
    """K20-ZE files (euro area): the ECB SPF micro-data archive and three Eurostat series."""
    return {
        "ecb_spf/SPF_microdata_by_variable.zip": (ECB_SPF, b"PK"),
        "eurostat/prc_hicp_ainr_A_RCH_A_AVG_TOTAL_EA.csv": (
            EUROSTAT + "prc_hicp_ainr/A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV", b"DATAFLOW"),
        "eurostat/nama_10_gdp_A_CLV_PCH_PRE_B1GQ_EA.csv": (
            EUROSTAT + "nama_10_gdp/A.CLV_PCH_PRE.B1GQ.EA?format=SDMX-CSV", b"DATAFLOW"),
        "eurostat/une_rt_m_M_NSA_TOTAL_PC_ACT_T_EA21.csv": (
            EUROSTAT + "une_rt_m/M.NSA.TOTAL.PC_ACT.T.EA21?format=SDMX-CSV", b"DATAFLOW"),
    }


# K20-LIV (US Livingston Survey) is being preregistered; its file group will be added here.
CATALOGUES = {"K20": k20_catalogue, "K20-ZE": k20ze_catalogue}

# Name of each cache file in the raw-download folder (`donnees/`) of the sealed test, for seeding.
SEALED_NAMES = {
    "K20": {name: Path(name).name for name in k20_catalogue()},
    "K20-ZE": {"ecb_spf/SPF_microdata_by_variable.zip": "SPF_microdata_by_variable.zip",
               "eurostat/prc_hicp_ainr_A_RCH_A_AVG_TOTAL_EA.csv": "eurostat_prc_hicp_ainr.csv",
               "eurostat/nama_10_gdp_A_CLV_PCH_PRE_B1GQ_EA.csv": "eurostat_nama_10_gdp.csv",
               "eurostat/une_rt_m_M_NSA_TOTAL_PC_ACT_T_EA21.csv": "eurostat_une_rt_m.csv"},
}


def catalogue():
    """Every cache file of every test: name (relative to data/raw) -> (URL, expected start)."""
    cat = {}
    for build in CATALOGUES.values():
        cat.update(build())
    return cat


def download(url, start, tries=10, first_wait=5, timeout=180):
    """Return (body, number of attempts). Retries on errors, on empty bodies (FRED sometimes sends them)
    and on bodies that do not start as expected (an HTML error page). Waits: 5, 10, 20 ... capped at 60 s."""
    wait, last = first_wait, None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
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
def seed_from(tests_dir):
    """Copy, byte for byte, the raw files the sealed tests downloaded (`<tests_dir>/<ID>/donnees/`) into the
    empty cache slots. Only raw source files are copied, never an analysis file."""
    tests_dir = Path(tests_dir)
    cat = catalogue()
    for tid, names in SEALED_NAMES.items():
        for name, sealed_name in names.items():
            target, source = RAW / name, tests_dir / tid / "donnees" / sealed_name
            if target.exists() or not source.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            _record(name, cat[name][0], f"copied from sealed test folder tests-de-mort/{tid}/donnees/{sealed_name}")


def compare_with_sealed(tests_dir):
    """{cache name: True/False/None}: is the cached file byte-identical (sha256) to the sealed test's copy?
    None when the sealed folder has no copy."""
    tests_dir = Path(tests_dir)
    out = {}
    for tid, names in SEALED_NAMES.items():
        for name, sealed_name in names.items():
            source = tests_dir / tid / "donnees" / sealed_name
            if source.exists() and (RAW / name).exists():
                out[name] = (hashlib.sha256(source.read_bytes()).hexdigest()
                             == hashlib.sha256((RAW / name).read_bytes()).hexdigest())
            else:
                out[name] = None
    return out


# --------------------------------------------------------------------------- reading
def read_excel(path, sheet):
    """pandas.read_excel with a work-around: openpyxl 3.1 refuses the Philadelphia real-time files because
    of a malformed date in their document properties, so we skip reading those properties (as the
    preregistration prescribes, section 4.2)."""
    import openpyxl.reader.excel
    import pandas as pd
    openpyxl.reader.excel.ExcelReader.read_properties = lambda self: None
    return pd.read_excel(path, sheet_name=sheet)


def count_rows(name):
    """Data rows of a cache file (CSV: lines minus header; zip: rows of 1_HICP.csv; xlsx: first sheet)."""
    path = RAW / name
    if name.endswith(".csv"):
        return max(len(path.read_bytes().splitlines()) - 1, 0)
    if name.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            return len(z.read("1_HICP.csv").splitlines()) - 1
    return len(read_excel(path, 0))


def write_provenance(sealed=None):
    """Write data/raw/PROVENANCE.md from provenance.json and the files on disk. `sealed` (from
    compare_with_sealed) adds whether each file is byte-identical to the sealed test's own copy."""
    sealed = sealed or {}
    label = {True: "yes", False: "NO", None: "–"}
    log = _read_log()
    lines = ["# Provenance of the raw data cache", "",
             "Every file below is kept exactly as received. `origin` says whether it was downloaded by",
             "`src/snu/data.py` or copied, byte for byte, from the raw-download folder of a sealed test",
             "(`ideation-finance/tests-de-mort/<ID>/donnees/`, listed in that folder's own PROVENANCE.md). Only raw",
             "source files were copied, never an analysis CSV. Delete the",
             "files in `data/raw/` (keep this one if you like) and run `python run_all.py` to download everything",
             "again. `date (UTC)` is the date the file entered this cache. `rows` = data rows (CSV: lines minus",
             "header; zip: rows of `1_HICP.csv`; xlsx: rows of the first sheet minus header). `same as sealed`",
             "says whether the file is byte-identical (sha256) to the copy in the sealed test's `donnees/` folder.", "",
             "| file | URL | origin | date (UTC) | sha256 | bytes | rows | same as sealed |",
             "|---|---|---|---|---|---|---|---|"]
    for name in sorted(log):
        e = log[name]
        sha = hashlib.sha256((RAW / name).read_bytes()).hexdigest()
        flag = "" if sha == e["sha256"] else " (CHANGED since logged)"
        lines.append(f"| `{name}` | {e['url']} | {e['origin']} | {e['date_utc']} | `{sha}`{flag} | "
                     f"{e['bytes']} | {count_rows(name)} | {label[sealed.get(name)]} |")
    (RAW / "PROVENANCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
