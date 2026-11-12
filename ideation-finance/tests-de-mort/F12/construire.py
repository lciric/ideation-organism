#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F12 — construction du fichier d'analyse `analyse_F12.csv` à partir de `donnees/` seulement.

Suit la préinscription scellée (§ 4 et § 5) :
  - EA-MPD, feuille `Monetary Event Window`, colonnes date, OIS_2Y, DE10Y, IT10Y, ES10Y, FR10Y ;
  - Riksbank, séries journalières DEGVB10Y, NLGVB10Y, FIGVB10Y, FRGVB10Y ;
  - 147 réunions du 2010-01-14 au 2025-10-30, 6 lignes par réunion, 882 lignes, 9 colonnes.

Aucun accès réseau. Usage : python3 -I construire.py
"""
import csv
import datetime as dt
import json
import math
import os
import sys

import openpyxl

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
XLSX = os.path.join(DONNEES, "Dataset_EA-MPD.xlsx")
SORTIE = os.path.join(ICI, "analyse_F12.csv")

FEUILLE = "Monetary Event Window"
COLS_EAMPD = ["date", "OIS_2Y", "DE10Y", "IT10Y", "ES10Y", "FR10Y"]
SERIES_RB = {"DE": "DEGVB10Y", "NL": "NLGVB10Y", "FI": "FIGVB10Y", "FR": "FRGVB10Y"}

DEBUT = dt.date(2010, 1, 14)
FIN = dt.date(2025, 10, 30)          # échantillon figé (amendement A14)
COLONNES = ["date_reunion", "pays", "source", "periode", "d_ois2y_pb", "d_rdt_pays_pb",
            "d_rdt_de_pb", "d_ecart_pb", "surprise_restrictive"]
NDEC = 10                              # décimales écrites (≥ 4 exigées)


def periode(d):
    """Tableau du § 4.1 : répartition par la seule date."""
    if dt.date(2010, 1, 14) <= d <= dt.date(2012, 9, 6):
        return "crise"
    if dt.date(2012, 10, 4) <= d <= dt.date(2022, 6, 9):
        return "avant"
    if d == dt.date(2022, 7, 21):
        return "annonce"
    if dt.date(2022, 9, 8) <= d <= dt.date(2025, 10, 30):
        return "apres"
    raise ValueError(f"date de réunion hors des bornes du § 4.1 : {d}")


def lire_date(v):
    """Date Excel (datetime) ou texte `jj/mm/aaaa` (piège (i) du § 4.1)."""
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, str):
        return dt.datetime.strptime(v.strip(), "%d/%m/%Y").date()
    raise ValueError(f"cellule de date illisible : {v!r}")


def numerique(v):
    """Renvoie un flottant si la cellule est numérique et finie, sinon None (donnée manquante)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    v = float(v)
    return v if math.isfinite(v) else None


def lire_eampd():
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb[FEUILLE]
    lignes = ws.iter_rows(values_only=True)
    entetes = next(lignes)
    idx = {}
    for nom in COLS_EAMPD:
        pos = [i for i, c in enumerate(entetes) if c == nom]
        if len(pos) != 1:
            raise ValueError(f"colonne {nom!r} : {len(pos)} occurrence(s) en ligne 1")
        idx[nom] = pos[0]
    reunions = []
    n_total = 0
    for r in lignes:
        if r[idx["date"]] is None:
            continue
        n_total += 1
        d = lire_date(r[idx["date"]])
        reunions.append({"date": d, **{c: r[idx[c]] for c in COLS_EAMPD[1:]}})
    wb.close()
    return reunions, n_total


def lire_riksbank(serie):
    with open(os.path.join(DONNEES, f"riksbank_{serie}.json"), encoding="utf-8") as f:
        obs = json.load(f)
    out = {}
    for o in obs:
        d = dt.date.fromisoformat(o["date"])
        v = numerique(o["value"])
        if v is None:
            continue
        if d in out:
            raise ValueError(f"{serie} : date en double {d}")
        out[d] = v
    return out


def variation_journaliere(serie, t):
    """§ 4.2 : 100 × (valeur(t) − valeur(s)), s = dernière date cotée strictement avant t,
    à condition que t − s ≤ 5 jours calendaires ; sinon, ou si t n'est pas coté : manquant."""
    if t not in serie:
        return None
    for k in range(1, 6):
        s = t - dt.timedelta(days=k)
        if s in serie:
            return 100.0 * (serie[t] - serie[s])
    return None


def arr(v):
    return None if v is None else round(v, NDEC)


def fmt(v):
    return "" if v is None else f"{v:.{NDEC}f}"


def main():
    reunions, n_total = lire_eampd()
    print(f"EA-MPD, feuille {FEUILLE!r} : {n_total} lignes datées, "
          f"de {min(r['date'] for r in reunions)} à {max(r['date'] for r in reunions)}")
    ech = sorted((r for r in reunions if DEBUT <= r["date"] <= FIN), key=lambda r: r["date"])
    print(f"Filtre 2010-01-14 ≤ date ≤ 2025-10-30 : {len(ech)} réunions")
    dates = [r["date"] for r in ech]
    if len(set(dates)) != len(dates):
        raise ValueError("dates de réunion en double dans EA-MPD")

    rb = {p: lire_riksbank(s) for p, s in SERIES_RB.items()}
    for p, s in SERIES_RB.items():
        print(f"Riksbank {s} : {len(rb[p])} observations, de {min(rb[p])} à {max(rb[p])}")

    lignes = []
    manq_eampd = []
    comptes = {}
    for r in ech:
        d = r["date"]
        per = periode(d)
        comptes[per] = comptes.get(per, 0) + 1
        ois = arr(numerique(r["OIS_2Y"]))
        de = arr(numerique(r["DE10Y"]))
        for c in ("OIS_2Y", "DE10Y", "IT10Y", "ES10Y", "FR10Y"):
            if numerique(r[c]) is None:
                manq_eampd.append((d.isoformat(), per, c, repr(r[c])))
        restr = "" if ois is None else (1 if ois > 0 else 0)
        # --- trois lignes EAMPD : IT, ES, FR
        for pays, col in (("IT", "IT10Y"), ("ES", "ES10Y"), ("FR", "FR10Y")):
            y = arr(numerique(r[col]))
            ec = None if (y is None or de is None) else arr(y - de)
            lignes.append([d.isoformat(), pays, "EAMPD", per, fmt(ois), fmt(y), fmt(de), fmt(ec), restr])
        # --- trois lignes RIKSBANK : FR, NL, FI
        de_j = arr(variation_journaliere(rb["DE"], d))
        for pays in ("FR", "NL", "FI"):
            y_j = arr(variation_journaliere(rb[pays], d))
            if y_j is None or de_j is None:      # vides ensemble ou renseignés ensemble (contrôle 7)
                lignes.append([d.isoformat(), pays, "RIKSBANK", per, fmt(ois), "", "", "", restr])
            else:
                lignes.append([d.isoformat(), pays, "RIKSBANK", per, fmt(ois), fmt(y_j), fmt(de_j),
                               fmt(arr(y_j - de_j)), restr])

    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLONNES)
        w.writerows(lignes)

    print(f"Réunions par période : {comptes}")
    print(f"Cellules EA-MPD vides ou non numériques (5 colonnes, 147 réunions) : {len(manq_eampd)}")
    for m in manq_eampd:
        print("   ", m)
    for per in ("crise", "avant", "annonce", "apres"):
        for pays in ("FR", "NL", "FI"):
            n = sum(1 for l in lignes if l[2] == "RIKSBANK" and l[1] == pays and l[3] == per and l[5] != "")
            print(f"RIKSBANK {pays} {per} : {n} réunions renseignées")
    vides = sorted({l[0] for l in lignes if l[2] == "RIKSBANK" and l[5] == ""})
    print(f"Dates de réunion avec au moins une ligne RIKSBANK vide : {vides}")
    # jour de référence s différent entre le pays et l'Allemagne ? (information seulement)
    decal = []
    for d in dates:
        def prec(serie):
            for k in range(1, 6):
                if d - dt.timedelta(days=k) in serie:
                    return d - dt.timedelta(days=k)
            return None
        ps = {p: prec(rb[p]) for p in rb if d in rb[p]}
        if len(set(ps.values())) > 1:
            decal.append((d.isoformat(), {p: str(v) for p, v in ps.items()}))
    print(f"Réunions où le jour coté précédent diffère entre séries Riksbank : {decal}")
    print(f"Écrit : {SORTIE} ({len(lignes)} lignes de données, {len(COLONNES)} colonnes)")

    # Contrôles de schéma du § 5, refaits sur le fichier écrit
    sys.path.insert(0, ICI)
    from controles_schema import controles
    res = controles(SORTIE)
    for k, (ok, detail) in res.items():
        print(f"  contrôle {k:>2} : {'OK ' if ok else 'ÉCHEC'} {detail}")
    print(f"violations_schema = {sum(1 for ok, _ in res.values() if not ok)}")


if __name__ == "__main__":
    main()
