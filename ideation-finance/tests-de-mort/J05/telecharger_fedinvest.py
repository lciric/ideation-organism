"""Téléchargement des pages FedInvest (D3) pour J et J-5 de chaque réouverture `avant` et `apres`.

Procédure de la préinscription (section 4, D3), une date à la fois, client par défaut (curl), pause d'une seconde :
 1. GET selectSecurityPriceDate -> témoin de session + champ caché _csrf
 2. POST même adresse, priceDate=AAAA-MM-JJ&submit=Show+Prices&_csrf=<jeton>, avec le témoin -> 302
 3. GET securityPriceDetail avec le témoin -> 200, page HTML

Chaque page de l'étape 3 est conservée telle quelle dans donnees/fedinvest/AAAA-MM-JJ.html (cache : une date déjà
présente n'est pas retéléchargée). Un journal (donnees/fedinvest_journal.csv) note chaque date : heure UTC, codes HTTP,
nombre de tentatives, statut.
Usage : python3 -I telecharger_fedinvest.py
"""
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
CACHE = os.path.join(DON, "fedinvest")
JOURNAL = os.path.join(DON, "fedinvest_journal.csv")
URL1 = "https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate"
URL3 = "https://www.treasurydirect.gov/GA-FI/FedInvest/securityPriceDetail"


def dates_requises():
    """J et J-5 (5 rangs avant J dans le calendrier GSW C) des réouvertures avant/apres."""
    d = json.load(open(os.path.join(DON, "auctions_query.json")))["data"]
    rows = [r for r in d if r["reopening"] == "Yes" and r["inflation_index_security"] != "Yes"
            and r["floating_rate"] != "Yes" and r["security_term"].split("-")[0] in ("9", "19", "29")]
    cal = []
    with open(os.path.join(DON, "feds200628.csv")) as f:
        lignes = f.read().splitlines()[9:]
    rd = csv.DictReader(lignes)
    for r in rd:
        if all(r[k] not in ("NA", "", None) for k in ("BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2")):
            cal.append(r["Date"])
    cal.sort()
    pos = {x: i for i, x in enumerate(cal)}
    out = set()
    for r in rows:
        j = r["auction_date"]
        if j < "2010-01-01":
            continue
        out.add(j)
        if j in pos and pos[j] >= 5:
            out.add(cal[pos[j] - 5])
        else:
            # J absent de C : J-5 = 5 rangs avant la première date de C postérieure à J n'est pas défini ;
            # on prend 5 rangs avant la position d'insertion pour ne rien perdre au téléchargement.
            import bisect
            k = bisect.bisect_left(cal, j)
            if k >= 5:
                out.add(cal[k - 5])
    return sorted(out)


def curl(args):
    p = subprocess.run(["curl", "-sS", "--max-time", "60"] + args, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def une_date(date, dest):
    with tempfile.TemporaryDirectory() as td:
        cj = os.path.join(td, "cj.txt")
        p1 = os.path.join(td, "p1.html")
        rc, out, err = curl(["-c", cj, "-o", p1, "-w", "%{http_code}", URL1])
        c1 = out.strip()
        if rc != 0 or c1 != "200":
            return f"{c1}", "", "", f"etape1 rc={rc} {err.strip()[:100]}"
        m = re.search(r'name="_csrf" value="([^"]+)"', open(p1, encoding="utf-8", errors="replace").read())
        if not m:
            return c1, "", "", "pas de _csrf"
        tok = m.group(1)
        rc, out, err = curl(["-b", cj, "-c", cj, "-o", os.devnull, "-w", "%{http_code}", "-X", "POST",
                             "--data", f"priceDate={date}&submit=Show+Prices&_csrf={tok}", URL1])
        c2 = out.strip()
        if rc != 0 or c2 != "302":
            return c1, c2, "", f"etape2 rc={rc} {err.strip()[:100]}"
        tmp = dest + ".part"
        rc, out, err = curl(["-b", cj, "-c", cj, "-o", tmp, "-w", "%{http_code}", URL3])
        c3 = out.strip()
        if rc != 0 or c3 != "200":
            if os.path.exists(tmp):
                os.remove(tmp)
            return c1, c2, c3, f"etape3 rc={rc} {err.strip()[:100]}"
        html = open(tmp, encoding="utf-8", errors="replace").read()
        if "Prices For:" not in html:
            os.remove(tmp)
            return c1, c2, c3, "page sans 'Prices For:'"
        os.replace(tmp, dest)
        return c1, c2, c3, "ok"


def main():
    os.makedirs(CACHE, exist_ok=True)
    dates = dates_requises()
    print(len(dates), "dates requises", dates[0], dates[-1], flush=True)
    neuf = not os.path.exists(JOURNAL)
    jf = open(JOURNAL, "a", newline="")
    w = csv.writer(jf)
    if neuf:
        w.writerow(["date_demandee", "heure_utc", "http_etape1", "http_etape2", "http_etape3", "tentatives", "statut"])
    echecs = 0
    for i, date in enumerate(dates):
        dest = os.path.join(CACHE, f"{date}.html")
        if os.path.exists(dest):
            continue
        statut = None
        for t in range(1, 6):
            c1, c2, c3, statut = une_date(date, dest)
            if statut == "ok":
                break
            time.sleep(2 ** t)
        w.writerow([date, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), c1, c2, c3, t, statut])
        jf.flush()
        if statut != "ok":
            echecs += 1
            print("ECHEC", date, c1, c2, c3, statut, flush=True)
            if echecs >= 15 and echecs == i + 1:
                print("FedInvest indisponible dès le départ ; arrêt.", flush=True)
                sys.exit(2)
        if i % 25 == 0:
            print(i, date, statut, flush=True)
        time.sleep(1)
    jf.close()
    print("fini ; échecs :", echecs, flush=True)


if __name__ == "__main__":
    main()
