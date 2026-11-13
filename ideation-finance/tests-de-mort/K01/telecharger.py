"""K01 — téléchargement des données brutes (section 5 de la préinscription).

Jusqu'à 10 essais par fichier, délai maximal de 120 s par essai, 10 s entre deux essais.
Chaque fichier reçu est écrit tel quel dans donnees/ ; un fichier déjà présent (cache) n'est pas retéléchargé.
Le journal (URL, date et heure UTC, code HTTP, sha256, octets, essais) va dans construire_journal.json.
"""
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
JOURNAL = os.path.join(ICI, "construire_journal.json")
os.makedirs(DONNEES, exist_ok=True)

ESSAIS, DELAI, PAUSE = 10, 120, 10

URL_SPF = "https://www.ecb.europa.eu/stats/prices/indic/forecast/shared/files/SPF_microdata_by_variable.zip"
URL_MPD = "https://data-api.ecb.europa.eu/service/data/MPD/A.U2.HIC.A.{code}.0000?format=csvdata"
URL_EUROSTAT = ("https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_ainr/"
                "A.RCH_A_AVG.TOTAL.EA?format=SDMX-CSV")

MILLESIMES = ["A01"] + [f"{l}{a % 100:02d}" for a in range(2002, 2026) for l in "WGSA"]
assert len(MILLESIMES) == 97


def charger_journal():
    if os.path.exists(JOURNAL):
        with open(JOURNAL, encoding="utf-8") as f:
            return json.load(f)
    return {}


def sha(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def telecharger(url, nom, journal):
    chemin = os.path.join(DONNEES, nom)
    if os.path.exists(chemin) and nom in journal and journal[nom].get("http") == 200:
        return True
    dernier = None
    for essai in range(1, ESSAIS + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research client)"})
            with urllib.request.urlopen(req, timeout=DELAI) as r:
                code = r.status
                contenu = r.read()
            if code == 200 and contenu:
                with open(chemin, "wb") as f:
                    f.write(contenu)
                journal[nom] = {
                    "url": url,
                    "date_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "http": code,
                    "sha256": sha(chemin),
                    "octets": len(contenu),
                    "essais": essai,
                }
                return True
            dernier = f"HTTP {code}"
        except urllib.error.HTTPError as e:
            dernier = f"HTTP {e.code}"
        except Exception as e:  # délai dépassé, connexion coupée…
            dernier = repr(e)
        print(f"  {nom} essai {essai}: {dernier}", file=sys.stderr)
        if essai < ESSAIS:
            time.sleep(PAUSE)
    journal.setdefault("_echecs", {})[nom] = {"url": url, "dernier": dernier,
                                             "date_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    return False


def main():
    journal = charger_journal()
    cibles = [(URL_SPF, "SPF_microdata_by_variable.zip"), (URL_EUROSTAT, "prc_hicp_ainr_A.RCH_A_AVG.TOTAL.EA.csv")]
    cibles += [(URL_MPD.format(code=c), f"MPD_A.U2.HIC.A.{c}.0000.csv") for c in MILLESIMES]
    ok = 0
    for url, nom in cibles:
        if telecharger(url, nom, journal):
            ok += 1
            journal.get("_echecs", {}).pop(nom, None)
        with open(JOURNAL, "w", encoding="utf-8") as f:
            json.dump(journal, f, indent=1, ensure_ascii=False, sort_keys=True)
    print(f"{ok}/{len(cibles)} fichiers présents")
    return 0 if ok == len(cibles) else 1


if __name__ == "__main__":
    sys.exit(main())
