#!/usr/bin/env python3
"""H13 — téléchargement des données brutes (D1 à D5) dans donnees/.

Usage :
    python3 telecharger.py d2     # D2 : PAYEMS par millésime (D1 déjà présent)
    python3 telecharger.py d3     # D3 : UNRATE aux dates de publication (exige D2)
    python3 telecharger.py taux   # D4 et D5 (exige emploi_intermediaire.csv, étape 6 de la préinscription)

Chaque fichier est mis en cache : un fichier déjà présent et valide n'est pas retéléchargé.
Les fichiers sont enregistrés tels que reçus (octets bruts). Un journal est tenu dans donnees/journal_telechargement.tsv.
"""
import datetime
import hashlib
import io
import os
import re
import sys
import time
import urllib.request

import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
JOURNAL = os.path.join(DON, "journal_telechargement.tsv")
LOT = 12


def journal(nom, url, octets):
    h = hashlib.sha256(octets).hexdigest()
    lignes = octets.count(b"\n")
    quand = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    nouveau = not os.path.exists(JOURNAL)
    with open(JOURNAL, "a", encoding="utf-8") as f:
        if nouveau:
            f.write("fichier\tdate_utc\tsha256\toctets\tlignes\turl\n")
        f.write(f"{nom}\t{quand}\t{h}\t{len(octets)}\t{lignes}\t{url}\n")


def recuperer(url, essais=5, min_octets=200):
    """GET avec l'agent utilisateur par défaut de Python ; réessaie avec pause croissante."""
    derniere = None
    for k in range(essais):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                corps = r.read()
            if len(corps) >= min_octets:
                return corps
            derniere = f"corps trop court ({len(corps)} octets)"
        except Exception as e:  # noqa: BLE001
            derniere = repr(e)
        print(f"   essai {k + 1} échoué : {derniere}", flush=True)
        time.sleep(5 * (k + 1))
    raise RuntimeError(f"échec après {essais} essais : {url} ; {derniere}")


def dates_d1():
    h = open(os.path.join(DON, "D1_PAYEMS_downloaddata.html"), encoding="utf-8").read()
    i = h.index('name="form[selected_vintage_dates][]"')
    j = h.index("</select>", i)
    d = re.findall(r'<option value="(\d{4}-\d{2}-\d{2})"', h[i:j])
    return sorted(set(d))


def entete_ok(octets, serie, dates):
    premiere = octets.split(b"\n", 1)[0].decode("utf-8").strip()
    attendu = "observation_date," + ",".join(f"{serie}_{d.replace('-', '')}" for d in dates)
    return premiere == attendu, premiere, attendu


def lots(serie, dates, prefixe):
    n_lots = (len(dates) + LOT - 1) // LOT
    for k in range(n_lots):
        sous = dates[k * LOT:(k + 1) * LOT]
        nom = f"{prefixe}_lot_{k + 1:02d}.csv"
        chemin = os.path.join(DON, nom)
        if os.path.exists(chemin):
            ok, _, _ = entete_ok(open(chemin, "rb").read(), serie, sous)
            if ok:
                print(f"{nom} : en cache", flush=True)
                continue
        url = ("https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=" + ",".join([serie] * len(sous))
               + "&vintage_date=" + ",".join(sous))
        for essai in range(5):
            corps = recuperer(url)
            ok, vu, attendu = entete_ok(corps, serie, sous)
            if ok:
                break
            print(f"   en-tête inattendu (essai {essai + 1}) : {vu[:120]}", flush=True)
            time.sleep(5 * (essai + 1))
        else:
            raise RuntimeError(f"{nom} : en-tête jamais conforme. Attendu {attendu}")
        with open(chemin, "wb") as f:
            f.write(corps)
        journal(nom, url, corps)
        print(f"{nom} : {len(corps)} octets, {len(sous)} millésimes", flush=True)
        time.sleep(2.0)


def d2():
    toutes = dates_d1()
    fen = [d for d in toutes if "1989-12-01" <= d <= "2026-03-31"]
    print(f"D1 : {len(toutes)} dates, {len(fen)} dans la fenêtre, de {fen[0]} à {fen[-1]}")
    lots("PAYEMS", fen, "D2_PAYEMS")


def dates_publication():
    """Étape 2 de la préinscription, à partir des fichiers D2 : dates de publication (toutes, dans la fenêtre D1)."""
    toutes = dates_d1()
    fen = [d for d in toutes if "1989-12-01" <= d <= "2026-03-31"]
    cadres = []
    for k in range((len(fen) + LOT - 1) // LOT):
        c = pd.read_csv(os.path.join(DON, f"D2_PAYEMS_lot_{k + 1:02d}.csv"), index_col=0)
        cadres.append(c)
    niveaux = pd.concat(cadres, axis=1)
    pubs, fin_prec = [], None
    for d in fen:
        fin = niveaux[f"PAYEMS_{d.replace('-', '')}"].last_valid_index()
        if fin_prec is None or fin > fin_prec:
            pubs.append(d)
        fin_prec = fin
    return pubs


def d3():
    pubs = dates_publication()
    print(f"D3 : {len(pubs)} dates de publication")
    lots("UNRATE", pubs, "D3_UNRATE")


def taux():
    inter = os.path.join(ICI, "emploi_intermediaire.csv")
    if not os.path.exists(inter):
        raise SystemExit("emploi_intermediaire.csv absent : l'étape 6 doit précéder le téléchargement des taux.")
    for nom, url, mini in [
        ("D4_DGS2.csv", "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2", 100000),
        ("D5_feds200628.csv", "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv", 5000000),
    ]:
        chemin = os.path.join(DON, nom)
        if os.path.exists(chemin) and os.path.getsize(chemin) >= mini:
            print(f"{nom} : en cache")
            continue
        try:
            corps = recuperer(url, min_octets=mini)
        except RuntimeError as e:
            print(f"{nom} : INJOIGNABLE — {e}")
            continue
        with open(chemin, "wb") as f:
            f.write(corps)
        journal(nom, url, corps)
        print(f"{nom} : {len(corps)} octets")
        time.sleep(2.0)


if __name__ == "__main__":
    {"d2": d2, "d3": d3, "taux": taux}[sys.argv[1]]()
