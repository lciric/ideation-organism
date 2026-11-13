"""Download the raw data once, keep it on disk, and read it back.

Every file lands in data/raw/ exactly as the server sent it. A file already in the
cache is never downloaded again. Each download is logged (URL, UTC time, sha256) in
data/raw/download_log.csv, which feeds data/raw/PROVENANCE.md.

Server quirks:
- FRED (fred.stlouisfed.org) answers only to curl's or Python's *default* user agent
  (a browser user agent gets the connection closed) and sometimes returns an empty body
  with HTTP 200, so we retry when the body is empty. federalreserve.gov, on the other
  hand, refuses Python's default user agent (HTTP 403). We therefore send curl's default
  user agent string to every host, which all five sources accept.
- FedInvest (treasurydirect.gov) needs a form procedure: GET the form page (session
  cookie + hidden _csrf token), POST the date without following the 302 redirect,
  then GET the detail page with the same cookie. One fresh session per date, and a
  one-second pause between dates.
"""
import csv
import hashlib
import http.cookiejar
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
LOG = RAW / "download_log.csv"
SEED = RAW / "seed_manifest.csv"

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
GSW_URL = "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"
MC_HS_URL = "https://home.treasury.gov/system/files/221/fy2021-mc-vs-hs-combined.csv"
FEDINVEST_FORM = "https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate"
FEDINVEST_DETAIL = "https://www.treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail"

# The three auction queries, copied verbatim from the three preregistrations.
_API = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
AUCTION_URLS = {
    "f04": _API + "?fields=auction_date,security_type,security_term,original_security_term,reopening,"
    "inflation_index_security,floating_rate,offering_amt,cusip,issue_date,maturity_date"
    "&filter=auction_date:gte:2010-01-01,auction_date:lte:2026-09-30,security_type:in:(Note,Bond)"
    "&sort=auction_date&page%5Bsize%5D=10000",
    "j05": _API + "?fields=cusip,auction_date,issue_date,maturity_date,dated_date,first_int_payment_date,"
    "first_int_period,security_type,security_term,reopening,inflation_index_security,floating_rate,"
    "closing_time_comp,auction_format,int_rate,high_yield,high_price,accrued_int_per1000"
    "&filter=auction_date:gte:1991-01-01,auction_date:lte:2026-10-31,security_type:in:(Note,Bond)"
    "&sort=auction_date&page%5Bsize%5D=10000",
    "k11": _API + "?fields=cusip,auction_date,issue_date,maturity_date,security_type,security_term,"
    "original_security_term,reopening,inflation_index_security,floating_rate,closing_time_comp,int_rate,"
    "high_yield,high_price&filter=security_type:in:(Note,Bond),auction_date:lte:2026-10-31"
    "&sort=auction_date&page%5Bsize%5D=10000",
}

MAX_TRIES = 5
USER_AGENT = "curl/8.5.0"  # curl's default user agent (see the module docstring)


# ----------------------------------------------------------------------------- HTTP
def _with_retries(action, what):
    """Run action() up to MAX_TRIES times, waiting 2, 4, 8, 16 s between failures."""
    for attempt in range(1, MAX_TRIES + 1):
        try:
            return action()
        except (urllib.error.URLError, OSError, ValueError) as err:
            if attempt == MAX_TRIES:
                raise RuntimeError(f"{what}: failed after {MAX_TRIES} tries ({err})") from err
            time.sleep(2 ** attempt)


def _get(url, check):
    """GET url with curl's default user agent; check(body) must be True, else retry."""
    def action():
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(request, timeout=120) as resp:
            body = resp.read()
        if not body or not check(body):
            raise ValueError("empty or unexpected body")
        return body
    return _with_retries(action, url)


def _log(name, url, body):
    new = not LOG.exists()
    with open(LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["file", "url", "downloaded_utc", "sha256", "bytes"])
        w.writerow([name, url, datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    hashlib.sha256(body).hexdigest(), len(body)])


def fetch(name, url, check=lambda body: True):
    """Return the cached file data/raw/<name>, downloading it first if it is missing."""
    path = RAW / name
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        body = _get(url, check)
        path.write_bytes(body)
        _log(name, url, body)
    return path


# ----------------------------------------------------------------------------- readers
def fred_series(series_id):
    """FRED daily series as a float Series indexed by date (NaN where FRED leaves the field empty)."""
    header = f"observation_date,{series_id}".encode()
    path = fetch(f"{series_id}.csv", FRED_URL.format(series_id), lambda b: b.startswith(header))
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    values = pd.to_numeric(df[series_id].replace("", np.nan))
    return pd.Series(values.values, index=pd.to_datetime(df["observation_date"]).dt.date, name=series_id)


def fred_strings(series_id):
    """Same series as text, exactly as written by FRED (used where a test copies values verbatim)."""
    path = fetch(f"{series_id}.csv", FRED_URL.format(series_id))
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return dict(zip(pd.to_datetime(df["observation_date"]).dt.date, df[series_id]))


def gsw_curve():
    """Fed GSW file (feds200628.csv): text table indexed by date; 'NA' becomes ''."""
    path = fetch("feds200628.csv", GSW_URL, lambda b: b"BETA0" in b and b"SVENPY10" in b)
    df = pd.read_csv(path, skiprows=9, dtype=str, keep_default_na=False)
    df = df.replace("NA", "")
    df.index = pd.to_datetime(df["Date"]).dt.date
    return df


def auctions(key):
    """Fiscal Data auction query ('f04', 'j05' or 'k11') as a text DataFrame ('null' kept as text)."""
    path = fetch(f"auctions_{key}.json", AUCTION_URLS[key], lambda b: b'"total-pages"' in b)
    data = json.loads(path.read_text())
    assert data["meta"]["total-pages"] == 1, "the query must fit in one page"
    return pd.DataFrame(data["data"]).astype(str)


def mc_vs_hs():
    """Treasury file with both curve methods (HS and MC) for fiscal 2021, as text, date-indexed."""
    path = fetch("fy2021-mc-vs-hs-combined.csv", MC_HS_URL, lambda b: b"nominal_hs_cmt_10yr" in b)
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    df.index = [datetime.strptime(s, "%m/%d/%Y").date() for s in df["date"]]
    return df


# ----------------------------------------------------------------------------- FedInvest
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # urllib then raises HTTPError(302), which we expect


def _download_fedinvest(day):
    """Run the three-step form procedure for one date and return the detail page (bytes)."""
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), _NoRedirect())
    opener.addheaders = [("User-Agent", USER_AGENT)]
    form = opener.open(FEDINVEST_FORM, timeout=60).read().decode("utf-8", "replace")
    token = re.search(r'name="_csrf" value="([^"]+)"', form).group(1)
    body = urllib.parse.urlencode({"priceDate": day.isoformat(), "submit": "Show Prices", "_csrf": token})
    try:
        opener.open(FEDINVEST_FORM, data=body.encode(), timeout=60)
        raise ValueError("expected HTTP 302 after the POST")
    except urllib.error.HTTPError as err:
        if err.code != 302:
            raise ValueError(f"POST answered {err.code}") from err
    page = opener.open(FEDINVEST_DETAIL, timeout=60).read()
    if b"Prices For:" not in page:
        raise ValueError("detail page without 'Prices For:'")
    return page


def fedinvest_page(day):
    """Cached FedInvest detail page for one date (downloaded, paced, if missing)."""
    path = RAW / "fedinvest" / f"{day.isoformat()}.html"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        page = _with_retries(lambda: _download_fedinvest(day), f"FedInvest {day}")
        path.write_bytes(page)
        _log(f"fedinvest/{path.name}", FEDINVEST_DETAIL + f" (form POST priceDate={day})", page)
        time.sleep(1.0)
    return path


_ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
_CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)


def parse_fedinvest(html):
    """Return (displayed date, {cusip: row}) for the notes and bonds of a FedInvest page.

    row = {"type", "rate" (percent), "maturity" (date), "eod" (END OF DAY price, per 100)}.
    A CUSIP listed twice on a page is dropped (treated as absent)."""
    shown = re.search(r"Prices For:\s*([A-Za-z]+ \d{1,2}, \d{4})", html)
    shown = datetime.strptime(shown.group(1), "%B %d, %Y").date() if shown else None
    rows, seen = {}, set()
    for tr in _ROW.findall(html):
        cells = [c.strip() for c in _CELL.findall(tr)]
        if len(cells) != 8 or cells[1] not in ("MARKET BASED NOTE", "MARKET BASED BOND"):
            continue
        cusip = cells[0]
        if cusip in seen:
            rows.pop(cusip, None)
            continue
        seen.add(cusip)
        rows[cusip] = {"type": cells[1], "rate": float(cells[2].rstrip("%")),
                       "maturity": datetime.strptime(cells[3], "%m/%d/%Y").date(),
                       "eod": float(cells[7]) if cells[7] else np.nan}
    return shown, rows


_PRICE_CACHE = {}


def fedinvest_prices(day):
    """Notes and bonds priced by FedInvest on `day`, or None if the page is empty or shows another date."""
    if day not in _PRICE_CACHE:
        shown, rows = parse_fedinvest(fedinvest_page(day).read_text(encoding="utf-8", errors="replace"))
        _PRICE_CACHE[day] = rows if (shown == day and rows) else None
    return _PRICE_CACHE[day]


# ----------------------------------------------------------------------------- provenance
def _rows(path):
    if path.suffix == ".json":
        return len(json.loads(path.read_text())["data"])
    if path.suffix == ".html":
        return len(parse_fedinvest(path.read_text(encoding="utf-8", errors="replace"))[1])
    if path.name == "feds200628.csv":
        return sum(1 for _ in open(path, encoding="utf-8", errors="replace")) - 10
    return sum(1 for _ in open(path, encoding="utf-8", errors="replace")) - 1


def write_provenance():
    """Write data/raw/PROVENANCE.md: one row per cached file (origin, URL, date, sha256, rows)."""
    def read(path):
        return {r["file"]: r for r in csv.DictReader(open(path))} if path.exists() else {}
    seeded, downloaded = read(SEED), read(LOG)
    lines = [
        "# Provenance of the raw data cache",
        "",
        "Every file is kept byte for byte as received. *Origin* says how it entered this cache:",
        "`seeded` = copied unchanged from the sealed test folder named in the URL column's note (the date is",
        "that folder's own download time, from its PROVENANCE.md or download journal); `downloaded` = fetched",
        "by `src/tap/data.py` (time from `download_log.csv`). Deleting `data/raw/` and rerunning `run_all.py`",
        "re-downloads everything from the URLs below.",
        "",
        "Rows: data lines for CSV files (FRED, Treasury), data records for JSON, data rows after the 9-line",
        "preamble and header for the GSW file, and note/bond rows of the price table for FedInvest pages.",
        "",
        "| File | Origin | URL | Date (UTC) | sha256 | Rows |",
        "|---|---|---|---|---|---|",
    ]
    files = sorted(p for p in RAW.rglob("*") if p.is_file() and p.name not in
                   ("PROVENANCE.md", "download_log.csv", "seed_manifest.csv"))
    for p in files:
        name = p.relative_to(RAW).as_posix()
        if name in downloaded:
            origin, url, when = "downloaded", downloaded[name]["url"], downloaded[name]["downloaded_utc"]
        elif name in seeded:
            s = seeded[name]
            note = f"(copied from `{s['copied_from']}` on {s['copied_utc']})"
            origin, url, when = "seeded", f"{s['url']} {note}", s["original_download_utc"]
        else:
            origin, url, when = "unknown", "", ""
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"| `{name}` | {origin} | {url} | {when} | `{sha}` | {_rows(p)} |")
    (RAW / "PROVENANCE.md").write_text("\n".join(lines) + "\n")
