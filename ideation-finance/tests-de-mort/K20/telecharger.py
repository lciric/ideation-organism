"""K20 — téléchargement des données brutes (section 4 de la préinscription).

Chaque fichier : jusqu'à 5 essais, délai de 120 s par essai, pause entre essais.
Les fichiers sont écrits tels quels dans donnees/ ; le journal (URL, date UTC, code HTTP,
sha256, taille) va dans construire_journal.json. Un fichier déjà présent et non vide
n'est pas re-téléchargé (cache) : son entrée de journal est conservée.
"""
import hashlib
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
JOURNAL = os.path.join(ICI, "construire_journal.json")

SPF = ("https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/"
       "survey-of-professional-forecasters/historical-data/")
RTD = ("https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/"
       "real-time-data/data-files/xlsx/")
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="

FICHIERS = {
    "meanGrowth.xlsx": SPF + "meanGrowth.xlsx",
    "meanLevel.xlsx": SPF + "meanLevel.xlsx",
    "medianGrowth.xlsx": SPF + "medianGrowth.xlsx",
    "medianLevel.xlsx": SPF + "medianLevel.xlsx",
    "pQvQd.xlsx": RTD + "pQvQd.xlsx",
    "routputQvQd.xlsx": RTD + "routputQvQd.xlsx",
    "UNRATE.csv": FRED + "UNRATE",
    "CPIAUCSL.csv": FRED + "CPIAUCSL",
    "TB3MS.csv": FRED + "TB3MS",
    "USRECQP.csv": FRED + "USRECQP",
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def main():
    os.makedirs(DON, exist_ok=True)
    journal = {}
    if os.path.exists(JOURNAL):
        with open(JOURNAL) as f:
            journal = json.load(f)
    manquants = []
    for nom, url in FICHIERS.items():
        dest = os.path.join(DON, nom)
        if os.path.exists(dest) and os.path.getsize(dest) > 0 and nom in journal:
            print("cache", nom)
            continue
        ok = False
        for essai in range(1, 6):
            try:
                req = urllib.request.Request(url)  # agent par défaut de Python
                with urllib.request.urlopen(req, timeout=120) as r:
                    code = r.status
                    corps = r.read()
                if code == 200 and len(corps) > 0:
                    with open(dest, "wb") as f:
                        f.write(corps)
                    journal[nom] = {
                        "url": url,
                        "date_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "http": code,
                        "essai": essai,
                        "octets": len(corps),
                        "sha256": sha(dest),
                    }
                    print("ok", nom, code, len(corps), "essai", essai)
                    ok = True
                    break
                print("vide ou code", code, nom, "essai", essai)
            except Exception as exc:  # noqa: BLE001
                print("échec", nom, "essai", essai, repr(exc))
            time.sleep(10 * essai)
        if not ok:
            manquants.append(nom)
        time.sleep(3)
        with open(JOURNAL, "w") as f:
            json.dump(journal, f, indent=2, ensure_ascii=False)
    if manquants:
        print("MANQUANTS:", manquants)
        sys.exit(1)


if __name__ == "__main__":
    main()
