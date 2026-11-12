#!/usr/bin/env python3
"""H16 — téléchargement des fichiers bruts (aucune modification), avec reprises.
Écrit donnees/<fichier> et donnees/telechargements.json (URL, horodatage UTC, sha256, octets, essais)."""
import hashlib, json, os, subprocess, sys, time, datetime

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
os.makedirs(DON, exist_ok=True)

SOURCES = [
    ("Dataset_EA-MPD.xlsx", "https://www.ecb.europa.eu/pub/pdf/annex/Dataset_EA-MPD.xlsx", 6, 100000),
    ("DCOILBRENTEU.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU", 6, 50000),
    ("DEXUSEU.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXUSEU", 6, 50000),
    ("feds200628.csv", "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv", 5, 5000000),
    ("Europe_3_Factors_Daily_CSV.zip", "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Europe_3_Factors_Daily_CSV.zip", 6, 20000),
]

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

journal = {}
jpath = os.path.join(DON, "telechargements.json")
if os.path.exists(jpath):
    journal = json.load(open(jpath))

for nom, url, essais_max, taille_min in SOURCES:
    dest = os.path.join(DON, nom)
    if nom in journal and os.path.exists(dest) and sha256(dest) == journal[nom]["sha256"]:
        print("déjà présent :", nom); continue
    ok = False
    for essai in range(1, essais_max + 1):
        tmp = dest + ".part"
        r = subprocess.run(["curl", "-sS", "-L", "--max-time", "180", "-o", tmp, "-w", "%{http_code}", url],
                           capture_output=True, text=True)
        code = r.stdout.strip()
        taille = os.path.getsize(tmp) if os.path.exists(tmp) else 0
        print(f"{nom} essai {essai}: http={code} octets={taille} err={r.stderr.strip()[:200]}")
        if r.returncode == 0 and code == "200" and taille >= taille_min:
            os.replace(tmp, dest)
            journal[nom] = {"url": url, "horodatage_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "sha256": sha256(dest), "octets": taille, "essais": essai}
            ok = True
            break
        if os.path.exists(tmp):
            os.remove(tmp)
        time.sleep(min(60, 5 * 2 ** (essai - 1)))
    if not ok:
        journal[nom] = {"url": url, "echec": True, "essais": essais_max}
        print("ÉCHEC :", nom)
    json.dump(journal, open(jpath, "w"), indent=1, ensure_ascii=False)
json.dump(journal, open(jpath, "w"), indent=1, ensure_ascii=False)
