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
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
RAW = Path(os.environ.get("SNU_RAW_DIR", PROJECT / "data" / "raw"))

PHILLY_SPF = ("https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/"
              "survey-of-professional-forecasters/historical-data/")
PHILLY_RTDSM = "https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/real-time-data/data-files/xlsx/"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

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


CATALOGUES = {"K20": k20_catalogue}


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


# --------------------------------------------------------------------------- seeding from the sealed test
def seed_from(folder):
    """Copy, byte for byte, the raw files the sealed test K20 downloaded (its flat `donnees/` folder) into
    the empty cache slots. Only raw source files are copied, never an analysis file."""
    folder = Path(folder)
    cat = k20_catalogue()
    for name in cat:
        target, source = RAW / name, folder / Path(name).name
        if target.exists() or not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        _record(name, cat[name][0], f"copied from sealed test folder tests-de-mort/K20/donnees/{source.name}")


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
    """Data rows of a cache file (CSV: lines minus header; xlsx: rows of the first sheet)."""
    path = RAW / name
    if name.endswith(".csv"):
        return max(len(path.read_bytes().splitlines()) - 1, 0)
    return len(read_excel(path, 0))


def write_provenance():
    """Write data/raw/PROVENANCE.md from provenance.json and the files on disk."""
    log = _read_log()
    lines = ["# Provenance of the raw data cache", "",
             "Every file below is kept exactly as received. `origin` says whether it was downloaded by",
             "`src/snu/data.py` or copied, byte for byte, from the raw-download folder of the sealed test K20",
             "(`ideation-finance/tests-de-mort/K20/donnees/`, downloaded there on 2026-11-12 and listed in that",
             "folder's own PROVENANCE.md). Only raw source files were copied, never an analysis CSV. Delete the",
             "files in `data/raw/` (keep this one if you like) and run `python run_all.py` to download everything",
             "again. `date (UTC)` is the date the file entered this cache. `rows` = data rows (CSV: lines minus",
             "header; xlsx: rows of the first sheet minus header).", "",
             "| file | URL | origin | date (UTC) | sha256 | bytes | rows |", "|---|---|---|---|---|---|---|"]
    for name in sorted(log):
        e = log[name]
        sha = hashlib.sha256((RAW / name).read_bytes()).hexdigest()
        flag = "" if sha == e["sha256"] else " (CHANGED since logged)"
        lines.append(f"| `{name}` | {e['url']} | {e['origin']} | {e['date_utc']} | `{sha}`{flag} | "
                     f"{e['bytes']} | {count_rows(name)} |")
    (RAW / "PROVENANCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
