"""Vérification indépendante F12 : recalcul des champs_verification du § 11 à partir de analyse_F12.csv seul."""
import csv
import json
import math
from datetime import date
from pathlib import Path

import numpy as np

ICI = Path(__file__).resolve().parent
FICHIER = ICI / "analyse_F12.csv"
COLONNES = ["date_reunion", "pays", "source", "periode", "d_ois2y_pb", "d_rdt_pays_pb",
            "d_rdt_de_pb", "d_ecart_pb", "surprise_restrictive"]
NUM = ["d_ois2y_pb", "d_rdt_pays_pb", "d_rdt_de_pb", "d_ecart_pb", "surprise_restrictive"]
COUPLES = {("IT", "EAMPD"), ("ES", "EAMPD"), ("FR", "EAMPD"),
           ("FR", "RIKSBANK"), ("NL", "RIKSBANK"), ("FI", "RIKSBANK")}
BORNES = {"crise": (date(2010, 1, 14), date(2012, 9, 6)),
          "avant": (date(2012, 10, 4), date(2022, 6, 9)),
          "annonce": (date(2022, 7, 21), date(2022, 7, 21)),
          "apres": (date(2022, 9, 8), date(2025, 10, 30))}
ATTENDU_PERIODE = {"crise": 33, "avant": 87, "annonce": 1, "apres": 26}


def num(s):
    """Nombre ou None (vide / non numérique)."""
    if s is None or s.strip() == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def lire():
    with open(FICHIER, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        entete = next(r)
        lignes = [row for row in r]
    return entete, lignes


def controles(entete, lignes):
    echecs = {}
    rows = [dict(zip(entete, l)) for l in lignes]
    # 1
    echecs[1] = not (len(lignes) == 882 and entete == COLONNES and all(len(l) == 9 for l in lignes))
    # 2
    cles = [(r.get("date_reunion"), r.get("pays"), r.get("source")) for r in rows]
    par_date = {}
    for d, p, s in cles:
        par_date.setdefault(d, []).append((p, s))
    ok2 = len(set(cles)) == len(cles) and all(
        len(v) == 6 and set(v) == COUPLES for v in par_date.values())
    echecs[2] = not ok2
    # 3
    try:
        dates = sorted({date.fromisoformat(d) for d in par_date})
        ok_fmt = all(len(d) == 10 for d in par_date)
    except (ValueError, TypeError):
        dates, ok_fmt = [], False
    per_dates = {}
    for r in rows:
        per_dates.setdefault(r.get("periode"), set()).add(r.get("date_reunion"))
    ok3 = (ok_fmt and len(dates) == 147 and dates and dates[0] == date(2010, 1, 14)
           and dates[-1] == date(2025, 10, 30)
           and set(per_dates) == set(ATTENDU_PERIODE)
           and all(len(per_dates[k]) == v for k, v in ATTENDU_PERIODE.items()))
    echecs[3] = not ok3
    # 4
    ok4 = True
    for r in rows:
        try:
            d = date.fromisoformat(r["date_reunion"])
        except (ValueError, TypeError):
            ok4 = False
            continue
        b = BORNES.get(r["periode"])
        if b is None or not (b[0] <= d <= b[1]):
            ok4 = False
    echecs[4] = not ok4
    # 5
    ok5 = True
    ois = {}
    for r in rows:
        v = num(r["d_ois2y_pb"])
        if v is None:
            ok5 = False
        ois.setdefault(r["date_reunion"], set()).add(v)
    ok5 = ok5 and all(len(s) == 1 for s in ois.values())
    echecs[5] = not ok5
    # 6
    ok6 = True
    de_e = {}
    for r in rows:
        if r["source"] == "EAMPD":
            if any(num(r[c]) is None for c in NUM):
                ok6 = False
            de_e.setdefault(r["date_reunion"], set()).add(num(r["d_rdt_de_pb"]))
    ok6 = ok6 and all(len(s) == 1 for s in de_e.values())
    echecs[6] = not ok6
    # 7
    ok7 = True
    de_r = {}
    for r in rows:
        if r["source"] == "RIKSBANK":
            vals = [num(r[c]) for c in ("d_rdt_pays_pb", "d_rdt_de_pb", "d_ecart_pb")]
            n_none = sum(v is None for v in vals)
            if n_none not in (0, 3):
                ok7 = False
            if n_none == 0:
                de_r.setdefault(r["date_reunion"], set()).add(vals[1])
    ok7 = ok7 and all(len(s) == 1 for s in de_r.values())
    echecs[7] = not ok7
    # 8
    ok8 = True
    for r in rows:
        a, b, e = num(r["d_rdt_pays_pb"]), num(r["d_rdt_de_pb"]), num(r["d_ecart_pb"])
        if None not in (a, b, e) and abs(e - (a - b)) > 1e-6:
            ok8 = False
    echecs[8] = not ok8
    # 9
    ok9 = True
    for r in rows:
        x, s = num(r["d_ois2y_pb"]), r["surprise_restrictive"].strip()
        if x is None or s not in ("0", "1") or (s == "1") != (x > 0):
            ok9 = False
    echecs[9] = not ok9
    # 10
    ok10 = True
    for r in rows:
        for c in NUM:
            v = num(r[c])
            if r[c].strip() != "" and (v is None or not math.isfinite(v) or abs(v) >= 300):
                ok10 = False
    echecs[10] = not ok10
    return echecs, rows


def pente_hc3(x, y):
    n = len(x)
    xc, yc = x - x.mean(), y - y.mean()
    S = np.sum(xc ** 2)
    b = np.sum(xc * yc) / S
    e = yc - b * xc
    h = 1.0 / n + xc ** 2 / S
    V = np.sum(xc ** 2 * e ** 2 / (1 - h) ** 2) / S ** 2
    return b, V


def main():
    entete, lignes = lire()
    echecs, rows = controles(entete, lignes)
    violations = sum(echecs.values())

    # Échantillon principal
    data = {}
    for r in rows:
        if r["source"] == "EAMPD" and r["pays"] in ("IT", "ES") and r["periode"] in ("avant", "apres"):
            data.setdefault((r["periode"], r["date_reunion"]), {})["x"] = num(r["d_ois2y_pb"])
            data[(r["periode"], r["date_reunion"])][r["pays"]] = num(r["d_ecart_pb"])
    reg = {"avant": [], "apres": []}
    for (p, d), v in sorted(data.items(), key=lambda kv: kv[0][1]):
        if v.get("x") is None or v.get("IT") is None or v.get("ES") is None:
            continue  # donnée manquante : la réunion sort (§ 4.1)
        reg[p].append((d, v["x"], (v["IT"] + v["ES"]) / 2))
    X = {k: np.array([t[1] for t in v]) for k, v in reg.items()}
    Y = {k: np.array([t[2] for t in v]) for k, v in reg.items()}
    D = {k: [t[0] for t in v] for k, v in reg.items()}

    b_av, V_av = pente_hc3(X["avant"], Y["avant"])
    b_ap, V_ap = pente_hc3(X["apres"], Y["apres"])
    d_hat = b_ap - b_av
    se_d = math.sqrt(V_av + V_ap)
    se_b_av = math.sqrt(V_av)
    haute, basse = d_hat + 1.32 * se_d, d_hat - 1.32 * se_d

    loo = []
    for k in ("avant", "apres"):
        for i in range(len(X[k])):
            m = np.ones(len(X[k]), bool)
            m[i] = False
            bk, _ = pente_hc3(X[k][m], Y[k][m])
            dd = (bk - b_av) if k == "apres" else (b_ap - bk)
            loo.append((dd, k, D[k][i]))
    d_max = max(loo)[0]

    non_inf = int(se_d > 0.16 and haute >= 0 and basse <= -0.15)

    out = {
        "n_avant": len(X["avant"]),
        "n_apres": len(X["apres"]),
        "b_avant": b_av,
        "b_apres": b_ap,
        "d_hat": d_hat,
        "se_d": se_d,
        "d_borne_haute": haute,
        "d_borne_basse": basse,
        "t_b_avant": b_av / se_b_av,
        "d_max_sans_une": d_max,
        "non_informatif": non_inf,
        "violations_schema": violations,
    }
    (ICI / "verification.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    # Diagnostics (console seulement)
    print(json.dumps(out, indent=2))
    print("contrôles en échec :", [k for k, v in echecs.items() if v])
    print("se_b_apres", math.sqrt(V_ap))
    loo.sort()
    print("LOO d max (top 3):", loo[-3:])
    print("LOO d min (top 3):", loo[:3])
    try:
        import statsmodels.api as sm
        for k in ("avant", "apres"):
            m = sm.OLS(Y[k], sm.add_constant(X[k])).fit(cov_type="HC3")
            print("statsmodels", k, m.params[1], m.bse[1])
    except ImportError:
        pass
    return X, Y, D


if __name__ == "__main__":
    main()
