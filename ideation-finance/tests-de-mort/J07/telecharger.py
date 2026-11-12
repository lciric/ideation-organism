"""Téléchargement des données brutes de J07 (D1 déjà téléchargé par curl dans donnees/downloaddata_PAYEMS.html).

D2 : millésimes ALFRED de PAYEMS, requêtes groupées de 12 millésimes au plus (section 4 de la préinscription).
Chaque réponse est enregistrée telle quelle dans donnees/ ; un journal (date, URL, sha256, lignes) est écrit
dans journal_telechargement.csv (hors de donnees/). Les fichiers déjà présents et valides ne sont pas retéléchargés.
"""
import csv
import datetime as dt
import hashlib
import io
import re
import sys
import time
import urllib.request
from pathlib import Path

ICI = Path(__file__).resolve().parent
DON = ICI / "donnees"
JOURNAL = ICI / "journal_telechargement.csv"


def dates_d1():
    h = (DON / "downloaddata_PAYEMS.html").read_text()
    i = h.index('name="form[selected_vintage_dates][]"')
    j = h.index("</select>", i)
    d = re.findall(r'<option value="(\d{4}-\d{2}-\d{2})"', h[i:j])
    return [x for x in d if "1989-12-01" <= x <= "2026-03-31"]


def valide(contenu, groupe):
    if not contenu:
        return False
    txt = contenu.decode("utf-8")
    entete = txt.splitlines()[0].strip().split(",")
    attendu = ["observation_date"] + ["PAYEMS_" + d.replace("-", "") for d in groupe]
    return entete == attendu


def main():
    dates = dates_d1()
    assert len(dates) == 438, len(dates)
    groupes = [dates[k:k + 12] for k in range(0, len(dates), 12)]
    nouveau = not JOURNAL.exists()
    with open(JOURNAL, "a", newline="") as fj:
        w = csv.writer(fj)
        if nouveau:
            w.writerow(["fichier", "url", "horodatage_utc", "sha256", "lignes", "tentatives"])
        for g in groupes:
            nom = f"PAYEMS_{g[0]}_{g[-1]}.csv"
            chemin = DON / nom
            if chemin.exists() and valide(chemin.read_bytes(), g):
                continue
            url = ("https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=" + ",".join(["PAYEMS"] * len(g))
                   + "&vintage_date=" + ",".join(g))
            ok = False
            for t in range(1, 5):  # 1 essai + 3 nouvelles tentatives
                try:
                    with urllib.request.urlopen(url, timeout=60) as r:
                        contenu = r.read()
                except Exception as e:  # noqa: BLE001
                    print("erreur", nom, t, e, file=sys.stderr)
                    contenu = b""
                if valide(contenu, g):
                    ok = True
                    break
                time.sleep(5 * t)
            if not ok:
                print("ÉCHEC", nom, file=sys.stderr)
                continue
            chemin.write_bytes(contenu)
            n = len(list(csv.reader(io.StringIO(contenu.decode("utf-8")))))
            w.writerow([nom, url, dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        hashlib.sha256(contenu).hexdigest(), n, t])
            fj.flush()
            print(nom, n, t)
            time.sleep(2)


if __name__ == "__main__":
    main()
