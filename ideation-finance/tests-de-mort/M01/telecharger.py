"""M01 - telechargement (preinscription section 5). Usage :
  python3 telecharger.py base        D1 (Fiscal Data), GSW (Fed), FRED DGS10/20/30 -> donnees/
  python3 telecharger.py fedinvest   pages FedInvest, une date par session, reprenable
  python3 telecharger.py provenance  ecrit donnees/PROVENANCE.md
Les fichiers sont enregistres bruts, sans modification. Client : curl par defaut."""
import sys, os, re, json, time, hashlib, subprocess, datetime as dt, tempfile

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import commun as K

DON = os.path.join(ICI, "donnees")
FI = os.path.join(DON, "fedinvest")
LOG = os.path.join(DON, "fedinvest_log.jsonl")
METAB = os.path.join(DON, "meta_base.json")

D1_URL = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?fields=cusip,"
          "auction_date,issue_date,maturity_date,security_type,security_term,original_security_term,reopening,"
          "inflation_index_security,floating_rate,closing_time_comp,int_rate&filter=security_type:in:(Note,Bond),"
          "auction_date:lte:2026-10-31&sort=auction_date&page%5Bsize%5D=10000")
BASE = [
    ("D1_auctions.json", D1_URL),
    ("D3_gsw_feds200628.csv", "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"),
    ("D4_DGS10.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"),
    ("D4_DGS20.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS20"),
    ("D4_DGS30.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS30"),
]
FI_SEL = "https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate"
FI_DET = "https://www.treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail"
ENTETE = ["CUSIP", "SECURITY TYPE", "RATE", "MATURITY DATE", "CALL DATE", "BUY", "SELL", "END OF DAY"]
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
        "November", "December"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def maintenant():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def curl(args, sortie, essais=1):
    """curl par defaut ; renvoie (code http, url de redirection)."""
    for i in range(essais):
        r = subprocess.run(["curl", "-sS", "--max-time", "120", "-o", sortie, "-w", "%{http_code} %{redirect_url}"] + args,
                           capture_output=True, text=True)
        out = r.stdout.split(" ", 1)
        code = int(out[0]) if out[0].isdigit() else 0
        if code and (os.path.getsize(sortie) > 0 or code in (302,)):
            return code, (out[1] if len(out) > 1 else "")
        time.sleep(2)
    return code, ""


# ------------------------------------------------------------------ base
def base():
    os.makedirs(DON, exist_ok=True)
    meta = json.load(open(METAB)) if os.path.exists(METAB) else {}
    for nom, url in BASE:
        chemin = os.path.join(DON, nom)
        if nom in meta and os.path.exists(chemin) and sha(open(chemin, "rb").read()) == meta[nom]["sha256"]:
            print("deja la :", nom)
            continue
        code, _ = curl([url], chemin, essais=5)
        b = open(chemin, "rb").read()
        meta[nom] = {"url": url, "date_telechargement_utc": maintenant(), "http": code, "sha256": sha(b),
                     "octets": len(b), "lignes": b.count(b"\n") + (0 if b.endswith(b"\n") or not b else 1)}
        print(nom, meta[nom]["http"], meta[nom]["octets"], meta[nom]["lignes"])
        json.dump(meta, open(METAB, "w"), indent=1)


# ------------------------------------------------------------------ FedInvest
def dates_utiles():
    d1 = K.charger_d1(os.path.join(DON, "D1_auctions.json"))
    pop = K.population(d1)
    prem = K.premieres(d1)
    par_cusip = {}
    for r in d1:
        par_cusip.setdefault(r["cusip"], []).append(r["auction_date"])
    dates = set()
    n_ok = 0
    for r in pop:
        j = K.iso(r["auction_date"])
        rj = K.RANG[j]
        chev = any(a != r["auction_date"] and abs(K.RANG[K.iso(a)] - rj) <= 10 for a in par_cusip[r["cusip"]])
        if chev:
            continue
        jm5, jp5 = K.fenetre(j)
        n_ok += 1
        dates.update([jm5, j, jp5])
    return sorted(dates), n_ok


def valide(chemin, date):
    """page valide : date affichee = date demandee et en-tete exact. Un tableau vide est 'absent' mais enregistre."""
    try:
        h = open(chemin, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    m = re.search(r"Prices For:\s*([A-Za-z]+) (\d+), (\d{4})", h)
    if not m or m.group(1) not in MOIS:
        return False
    if dt.date(int(m.group(3)), MOIS.index(m.group(1)) + 1, int(m.group(2))) != date:
        return False
    ent = re.findall(r"<th>(.*?)</th>", h)
    return ent == ENTETE


def une_date(date):
    s = date.isoformat()
    final = os.path.join(FI, s + ".html")
    rec = {"date": s, "utc": maintenant()}
    with tempfile.TemporaryDirectory() as td:
        jar, p1, p2, p3 = (os.path.join(td, n) for n in ("jar", "p1", "p2", "p3"))
        c1, _ = curl(["-c", jar, FI_SEL], p1)
        rec["get_selection"] = c1
        if c1 != 200:
            return rec, None
        h = open(p1, encoding="utf-8", errors="replace").read()
        m = re.search(r'name="_csrf"\s+value="([^"]*)"', h)
        csrf = m.group(1) if m else ""
        rec["csrf_longueur"] = len(csrf)
        if len(csrf) != 96:
            return rec, None
        time.sleep(1)
        c2, redir = curl(["-b", jar, "-c", jar, "-X", "POST", "--data",
                          f"priceDate={s}&submit=Show+Prices&_csrf={csrf}", FI_SEL], p2)
        rec["post"] = c2
        rec["redirection"] = redir
        if c2 != 302:
            return rec, None
        time.sleep(1)
        c3, _ = curl(["-b", jar, "-c", jar, FI_DET], p3)
        rec["get_detail"] = c3
        if c3 != 200:
            return rec, None
        b = open(p3, "rb").read()
        rec["octets"] = len(b)
        rec["sha256"] = sha(b)
        rec["lignes_tableau"] = len(re.findall(r"<tr>\s*(?:<td|<td>)", b.decode("utf-8", "replace")))
        rec["valide"] = valide(p3, date)
        if not rec["valide"]:
            rec["page_rejetee"] = True
            return rec, None
        with open(final, "wb") as g:
            g.write(b)
        return rec, final


def fedinvest():
    os.makedirs(FI, exist_ok=True)
    dates, n = dates_utiles()
    print(f"{n} reouvertures hors chevauchement, {len(dates)} dates", flush=True)
    for i, d in enumerate(dates):
        final = os.path.join(FI, d.isoformat() + ".html")
        if os.path.exists(final) and valide(final, d):
            continue
        for essai in range(3):
            rec, ok = une_date(d)
            rec["essai"] = essai + 1
            with open(LOG, "a") as f:
                f.write(json.dumps(rec) + "\n")
            time.sleep(1)
            if ok or rec.get("page_rejetee"):
                break
            time.sleep(5)
        if i % 25 == 0:
            print(i, d, rec.get("valide"), flush=True)
    manque = [d for d in dates if not os.path.exists(os.path.join(FI, d.isoformat() + ".html"))]
    print("termine ; manquantes :", [d.isoformat() for d in manque], flush=True)


# ------------------------------------------------------------------ PROVENANCE.md
def provenance():
    meta = json.load(open(METAB))
    dates, n = dates_utiles()
    dernier = {}
    if os.path.exists(LOG):
        for l in open(LOG):
            r = json.loads(l)
            dernier.setdefault(r["date"], []).append(r)
    L = ["# PROVENANCE des donnees brutes de M01", "",
         "Les fichiers bruts de `donnees/` ne sont pas versionnes ; ce fichier l'est. Client : curl par defaut, sans suivre les",
         "redirections (FedInvest). Les dates sont en UTC.", "", "## Sources de base", "",
         "| fichier | URL | date de telechargement | HTTP | sha256 | octets | lignes |", "|---|---|---|---|---|---|---|"]
    for nom, m in meta.items():
        L.append(f"| {nom} | {m['url']} | {m['date_telechargement_utc']} | {m['http']} | {m['sha256']} | {m['octets']} | {m['lignes']} |")
    L += ["", "## FedInvest : resume", ""]
    n_ok, n_vide, manque, essais_multi = 0, 0, [], 0
    lignes = []
    for d in dates:
        s = d.isoformat()
        p = os.path.join(FI, s + ".html")
        if not os.path.exists(p):
            manque.append(s)
            continue
        b = open(p, "rb").read()
        nl = b.count(b"\n")
        nt = len(re.findall(r"<tr>\s*<td", b.decode("utf-8", "replace")))
        recs = dernier.get(s, [])
        rec = next((r for r in reversed(recs) if r.get("valide")), {})
        if len(recs) > 1:
            essais_multi += 1
        if nt == 0:
            n_vide += 1
        else:
            n_ok += 1
        lignes.append(f"| {s} | {rec.get('utc', '')} | {rec.get('get_selection', '')}/{rec.get('post', '')}/{rec.get('get_detail', '')}"
                      f" | {rec.get('csrf_longueur', '')} | {sha(b)} | {len(b)} | {nl} | {nt} |")
    L += [f"- Dates demandees (J-5, J, J+5 des {n} reouvertures non exclues par les metadonnees) : {len(dates)}.",
          f"- Pages enregistrees : {n_ok + n_vide} ; avec tableau rempli : {n_ok} ; tableau vide : {n_vide} ; manquantes : {len(manque)} {manque}.",
          f"- Dates ayant demande plus d'un essai : {essais_multi}.",
          "- Procedure par date (une session, pause de 1 s entre requetes) : GET selectSecurityPriceDate (200, jeton `_csrf` de 96 caracteres) ;",
          "  POST `priceDate=AAAA-MM-JJ&submit=Show+Prices&_csrf=...` (302, redirection non suivie) ; GET securityPriceDetail (200).",
          "  Page acceptee si la date affichee (`Prices For:`) est la date demandee et si l'en-tete du tableau est exact.",
          f"- URL : {FI_SEL} puis {FI_DET}.", "",
          "## FedInvest : une ligne par date", "",
          "| date | telechargee (UTC) | HTTP GET/POST/GET | long. jeton | sha256 | octets | lignes | lignes de tableau |",
          "|---|---|---|---|---|---|---|---|"] + lignes
    open(os.path.join(DON, "PROVENANCE.md"), "w").write("\n".join(L) + "\n")
    print("PROVENANCE.md ecrit")


if __name__ == "__main__":
    {"base": base, "fedinvest": fedinvest, "provenance": provenance}[sys.argv[1]]()
