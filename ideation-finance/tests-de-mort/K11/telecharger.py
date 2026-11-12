#!/usr/bin/env python3
"""K11 -- telecharge des pages FedInvest selon la procedure de la preinscription (section 4.2).

Une session par date : GET (temoin + _csrf), POST sans suivre la redirection, GET de securityPriceDetail.
Pause d'une seconde entre dates ; jusqu'a 5 essais par date avec attente croissante. Cache : une date deja
presente dans le dossier de sortie n'est pas retelechargee.

Usage : python3 -I telecharger.py <dossier_sortie> <journal.csv> AAAA-MM-JJ [AAAA-MM-JJ ...]
        python3 -I telecharger.py <dossier_sortie> <journal.csv> @fichier_de_dates
"""
import datetime as dt
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time

BASE = "https://www.treasurydirect.gov/GA-FI/FedInvest/"
RE_CSRF = re.compile(r'name="_csrf" value="([^"]+)"')


def curl(args, sortie):
    r = subprocess.run(["curl", "-sS", "--max-time", "60", "-o", sortie, "-w", "%{http_code}"] + args,
                       capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip()


def une_date(date, dossier):
    with tempfile.TemporaryDirectory() as tmp:
        jar = os.path.join(tmp, "jar")
        p1, p3 = os.path.join(tmp, "p1"), os.path.join(tmp, "p3")
        c1, e = curl(["-c", jar, "-b", jar, BASE + "selectSecurityPriceDate"], p1)
        if c1 != "200":
            return None, f"GET1 {c1} {e}"
        m = RE_CSRF.search(open(p1, encoding="utf-8", errors="replace").read())
        if not m:
            return None, "pas de _csrf"
        tok = m.group(1)
        c2, e = curl(["-c", jar, "-b", jar, "-X", "POST",
                      "--data-urlencode", f"priceDate={date}", "--data-urlencode", "submit=Show Prices",
                      "--data-urlencode", f"_csrf={tok}", BASE + "selectSecurityPriceDate"], os.devnull)
        if c2 != "302":
            return None, f"POST {c2} {e}"
        c3, e = curl(["-c", jar, "-b", jar, BASE + "securityPriceDetail"], p3)
        if c3 != "200":
            return None, f"GET3 {c3} {e}"
        brut = open(p3, "rb").read()
        s = brut.decode("utf-8", errors="replace")
        m = re.search(r"Prices For:\s*([A-Za-z]+ \d{1,2}, \d{4})", s)
        if not m:
            return None, "pas de 'Prices For'"
        affichee = dt.datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()
        with open(os.path.join(dossier, date + ".html"), "wb") as f:
            f.write(brut)
        n = len(re.findall(r"MARKET BASED (?:NOTE|BOND)", s))
        return (c1, c2, c3, len(len(tok) * "x"), affichee, n, hashlib.sha256(brut).hexdigest(), len(tok)), None


def main():
    dossier, journal = sys.argv[1], sys.argv[2]
    dates = []
    for a in sys.argv[3:]:
        if a.startswith("@"):
            dates += [x.strip() for x in open(a[1:]) if x.strip()]
        else:
            dates.append(a)
    os.makedirs(dossier, exist_ok=True)
    neuf = not os.path.exists(journal)
    jf = open(journal, "a", encoding="utf-8")
    if neuf:
        jf.write("date_demandee,horodatage_utc,http_get,http_post,http_detail,date_affichee,n_notes_obligations,sha256,longueur_csrf,essais\n")
    for d in dates:
        if os.path.exists(os.path.join(dossier, d + ".html")):
            continue
        res, err = None, None
        for essai in range(1, 6):
            res, err = une_date(d, dossier)
            if res:
                break
            print(d, "essai", essai, err, flush=True)
            time.sleep(5 * 2 ** (essai - 1))
        if not res:
            print(d, "ECHEC DEFINITIF", err, flush=True)
            jf.write(f"{d},{dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')},,,,,,,,ECHEC {err}\n")
            jf.flush()
            continue
        c1, c2, c3, _, aff, n, sha, ltok = res
        jf.write(f"{d},{dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')},{c1},{c2},{c3},{aff},{n},{sha},{ltok},{essai}\n")
        jf.flush()
        print(d, aff, n, flush=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
