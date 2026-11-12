"""Construit tests-de-mort/J07/J07_analyse.csv à partir de donnees/ seul (préinscription J07, sections 4 et 5).

Entrées : donnees/downloaddata_PAYEMS.html (D1) et donnees/PAYEMS_*.csv (D2, réponses ALFRED brutes groupées).
Sortie  : J07_analyse.csv (18 colonnes), et un résumé des contrôles imprimé à l'écran
          (également écrit dans construire_controles.json).
"""
import csv
import io
import json
import re
import statistics
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
DON = ICI / "donnees"
SORTIE = ICI / "J07_analyse.csv"

COLONNES = ["date_publication", "mois_reference", "n_mois_nouveaux", "date_millesime_precedent",
            "date_millesime_3e", "date_info_predicteurs", "emploi_1re_k", "emploi_3e_k", "rev_m1_k",
            "rev_m2_k", "tendance_12m_k", "revision_large", "extreme", "complet", "admissible",
            "cible_N_k", "pred_ecart_tendance_k", "pred_somme_revisions_k"]


def mois_idx(s):  # "AAAA-MM-.." -> entier
    return int(s[:4]) * 12 + int(s[5:7]) - 1


def idx_mois(i):
    return f"{i // 12:04d}-{i % 12 + 1:02d}"


# ---------------------------------------------------------------- D1
def dates_d1():
    h = (DON / "downloaddata_PAYEMS.html").read_text()
    i = h.index('name="form[selected_vintage_dates][]"')
    j = h.index("</select>", i)
    d = re.findall(r'<option value="(\d{4}-\d{2}-\d{2})"', h[i:j])
    return [x for x in d if "1989-12-01" <= x <= "2026-03-31"]


# ---------------------------------------------------------------- D2
def lire_d2(dates):
    """Renvoie {date_millesime: {mois_idx: niveau entier}} ; contrôle les en-têtes."""
    L = {}
    fichiers = sorted(DON.glob("PAYEMS_*.csv"))
    for f in fichiers:
        txt = f.read_text(encoding="utf-8")
        rows = list(csv.reader(io.StringIO(txt)))
        entete = rows[0]
        assert entete[0] == "observation_date", f
        vint = []
        for c in entete[1:]:
            mm = re.fullmatch(r"PAYEMS_(\d{4})(\d{2})(\d{2})", c)
            assert mm, (f, c)
            vint.append(f"{mm[1]}-{mm[2]}-{mm[3]}")
        # le nom de fichier donne la première et la dernière date demandées : contrôle de l'ordre et du nombre
        a, b = re.fullmatch(r"PAYEMS_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})\.csv", f.name).groups()
        demandees = [d for d in dates if a <= d <= b]
        assert vint == demandees, (f, vint, demandees)
        for v in vint:
            assert v not in L, v
            L[v] = {}
        for r in rows[1:]:
            if not r:
                continue
            j = mois_idx(r[0])
            assert r[0].endswith("-01"), r[0]
            for v, x in zip(vint, r[1:]):
                if x.strip() != "":
                    L[v][j] = int(x)
    manquants = [d for d in dates if d not in L]
    if manquants:
        sys.exit(f"Millésimes de D1 introuvables dans D2 : {manquants} — fichier non construit (non concluant).")
    return L


def main():
    dates = dates_d1()
    ctrl = {"n_dates_D1": len(dates), "premiere_date_D1": dates[0], "derniere_date_D1": dates[-1]}
    L = lire_d2(dates)

    fin = {}
    for v in dates:
        mois = sorted(L[v])
        # contrôle : pas de trou à l'intérieur d'un millésime
        assert mois == list(range(mois[0], mois[-1] + 1)), v
        fin[v] = mois[-1]

    def D(j, v):  # variation à l'intérieur du seul millésime v ; None si non calculable
        if j in L[v] and (j - 1) in L[v]:
            return L[v][j] - L[v][j - 1]
        return None

    # ------------------------------------------------ étape 2 : publications
    pubs, corrections = [dates[0]], []
    for k in range(1, len(dates)):
        v = dates[k]
        if fin[v] > fin[dates[k - 1]]:
            pubs.append(v)
        else:
            corrections.append(v)
    prec = {pubs[k]: pubs[k - 1] for k in range(1, len(pubs))}
    ctrl["corrections"] = corrections
    ctrl["n_publications"] = len(pubs)
    periode = [v for v in pubs if "1990-01-01" <= v <= "2025-12-31"]
    ctrl["n_publications_1990_2025"] = len(periode)

    # ------------------------------------------------ étape 4 : publications de révision large
    large = {}
    for w in pubs[1:]:
        mp = fin[prec[w]]
        large[w] = any(L[w].get(j) != L[prec[w]].get(j) for j in range(mp - 11, mp - 1))
    ctrl["publications_revision_large_1989_2026"] = [w for w in pubs[1:] if large[w]]

    lignes = []
    for v in periode:
        m, mp = fin[v], fin[prec[v]]
        n_new = m - mp
        A1 = D(m, v)
        v3 = None
        for w in pubs[pubs.index(v) + 1:]:
            if fin[w] >= m + 2:
                v3 = w
                break
        A3 = D(m, v3) if v3 is not None else None
        R1 = (D(mp, v) - D(mp, prec[v])) if D(mp, v) is not None and D(mp, prec[v]) is not None else None
        R2 = ((D(mp - 1, v) - D(mp - 1, prec[v]))
              if D(mp - 1, v) is not None and D(mp - 1, prec[v]) is not None else None)
        douze = [D(j, prec[v]) for j in range(mp - 11, mp + 1)]
        T = statistics.median(douze) if all(x is not None for x in douze) else None
        borne = v3 if v3 is not None else pubs[-1]
        rl = int(any(large.get(w, False) for w in pubs if v <= w <= borne))
        ext = int(abs(A1) > 1000 or (A3 is not None and abs(A1 - A3) > 500))
        complet = int(A3 is not None and R1 is not None and R2 is not None and T is not None)
        adm = int(complet == 1 and n_new == 1 and rl == 0 and ext == 0)
        lignes.append({
            "date_publication": v,
            "mois_reference": idx_mois(m),
            "n_mois_nouveaux": n_new,
            "date_millesime_precedent": prec[v],
            "date_millesime_3e": v3 or "",
            # A1, R1, R2 sont lus dans v ; T dans prec(v) : le plus récent est v
            "date_info_predicteurs": max(v, prec[v]),
            "emploi_1re_k": A1,
            "emploi_3e_k": "" if A3 is None else A3,
            "rev_m1_k": "" if R1 is None else R1,
            "rev_m2_k": "" if R2 is None else R2,
            "tendance_12m_k": "" if T is None else (f"{T:.1f}"),
            "revision_large": rl,
            "extreme": ext,
            "complet": complet,
            "admissible": adm,
            "cible_N_k": "" if A3 is None else A1 - A3,
            "pred_ecart_tendance_k": "" if T is None else f"{A1 - T:.1f}",
            "pred_somme_revisions_k": "" if (R1 is None or R2 is None) else R1 + R2,
        })

    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLONNES, lineterminator="\n")
        w.writeheader()
        w.writerows(lignes)

    # ------------------------------------------------ comptes par filtre
    ctrl["n_lignes"] = len(lignes)
    ctrl["n_complet_0"] = sum(r["complet"] == 0 for r in lignes)
    ctrl["n_mois_nouveaux_2"] = sum(r["n_mois_nouveaux"] != 1 for r in lignes)
    ctrl["n_revision_large_1"] = sum(r["revision_large"] == 1 for r in lignes)
    ctrl["n_extreme_1"] = sum(r["extreme"] == 1 for r in lignes)
    ctrl["dates_extreme"] = [r["date_publication"] for r in lignes if r["extreme"] == 1]
    ctrl["dates_n_mois_nouveaux_2"] = [r["date_publication"] for r in lignes if r["n_mois_nouveaux"] != 1]
    # filtres séquentiels dans l'ordre complet -> n_mois_nouveaux -> revision_large -> extreme
    seq, reste = {}, lignes
    for nom, test in [("complet", lambda r: r["complet"] == 1), ("n_mois_nouveaux", lambda r: r["n_mois_nouveaux"] == 1),
                      ("revision_large", lambda r: r["revision_large"] == 0), ("extreme", lambda r: r["extreme"] == 0)]:
        avant = len(reste)
        reste = [r for r in reste if test(r)]
        seq[nom] = {"avant": avant, "ecartees": avant - len(reste), "apres": len(reste)}
    ctrl["filtres_sequentiels"] = seq
    ctrl["n_admissibles"] = sum(r["admissible"] for r in lignes)

    ctrl["controles_schema"] = controles_schema(SORTIE)
    ctrl["schema_ok"] = int(all(ctrl["controles_schema"].values()))
    (ICI / "construire_controles.json").write_text(json.dumps(ctrl, ensure_ascii=False, indent=1))
    print(json.dumps(ctrl, ensure_ascii=False, indent=1))


def controles_schema(chemin):
    """Les huit contrôles de schéma de la section 5, relus depuis le fichier écrit."""
    import datetime as dt
    with open(chemin, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    entete, data = rows[0], rows[1:]
    R = [dict(zip(entete, r)) for r in data]
    c = {}
    c["1_colonnes"] = entete == COLONNES and all(len(r) == 18 for r in data)
    d = [r["date_publication"] for r in R]
    c["2_lignes_dates"] = (425 <= len(R) <= 435 and len(set(d)) == len(d)
                           and all(d[k] < d[k + 1] for k in range(len(d) - 1))
                           and all("1990-01-01" <= x <= "2025-12-31" for x in d))
    mr = [r["mois_reference"] for r in R]
    ok3 = all(mr[k] < mr[k + 1] for k in range(len(mr) - 1))
    for r in R:
        e = (dt.date.fromisoformat(r["date_publication"]) - dt.date.fromisoformat(r["mois_reference"] + "-01")).days
        ok3 &= 28 <= e <= 110
    c["3_mois_reference"] = ok3
    c["4_domaines"] = (all(r["n_mois_nouveaux"] in ("1", "2") for r in R)
                       and sum(r["n_mois_nouveaux"] == "2" for r in R) <= 2
                       and all(r[k] in ("0", "1") for r in R
                               for k in ("revision_large", "extreme", "complet", "admissible")))
    ok5 = True
    for r in R:
        ok5 &= r["date_millesime_precedent"] < r["date_publication"]
        ok5 &= r["date_info_predicteurs"] <= r["date_publication"]
        if r["date_millesime_3e"]:
            ok5 &= r["date_publication"] < r["date_millesime_3e"] <= "2026-03-31"
    c["5_datation_predicteurs"] = bool(ok5)
    ok6 = True
    for r in R:
        A1 = int(r["emploi_1re_k"])
        A3 = int(r["emploi_3e_k"]) if r["emploi_3e_k"] else None
        T = float(r["tendance_12m_k"]) if r["tendance_12m_k"] else None
        R1 = int(r["rev_m1_k"]) if r["rev_m1_k"] else None
        R2 = int(r["rev_m2_k"]) if r["rev_m2_k"] else None
        ok6 &= (r["cible_N_k"] == "") if A3 is None else (int(r["cible_N_k"]) == A1 - A3)
        ok6 &= (r["pred_ecart_tendance_k"] == "") if T is None else (float(r["pred_ecart_tendance_k"]) == A1 - T)
        ok6 &= ((r["pred_somme_revisions_k"] == "") if (R1 is None or R2 is None)
                else int(r["pred_somme_revisions_k"]) == R1 + R2)
        ext = int(abs(A1) > 1000 or (A3 is not None and abs(A1 - A3) > 500))
        comp = int(A3 is not None and R1 is not None and R2 is not None and T is not None)
        adm = int(comp == 1 and r["n_mois_nouveaux"] == "1" and r["revision_large"] == "0" and ext == 0)
        ok6 &= int(r["extreme"]) == ext and int(r["complet"]) == comp and int(r["admissible"]) == adm
        if T is not None:
            ok6 &= (2 * T) == int(2 * T)
    c["6_definitions"] = bool(ok6)
    ok7 = True
    for r in R:
        for k in ("emploi_1re_k", "tendance_12m_k", "rev_m1_k", "rev_m2_k"):
            if r[k]:
                ok7 &= abs(float(r[k])) <= 25000
    c["7_bornes"] = bool(ok7)
    l = [r for r in R if r["date_publication"] == "1990-02-02"]
    c["8_ligne_1990_02_02"] = (len(l) == 1 and l[0]["mois_reference"] == "1990-01" and l[0]["emploi_1re_k"] == "275"
                               and l[0]["date_millesime_3e"] == "1990-04-06" and l[0]["emploi_3e_k"] == "361"
                               and l[0]["cible_N_k"] == "-86")
    return c


if __name__ == "__main__":
    main()
