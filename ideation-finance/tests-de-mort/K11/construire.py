#!/usr/bin/env python3
"""K11 -- construit K11_analyse.csv a partir de donnees/ seulement (preinscription, sections 4 et 5).

Usage :
    python3 -I construire.py            # construit le fichier d'analyse et execute les controles 5.3
    python3 -I construire.py --dates    # ecrit seulement la liste des dates FedInvest necessaires (dates_requises.txt)

Entrees : donnees/auctions_query.json (D1) ; donnees/fedinvest/AAAA-MM-JJ.html (D2, une page par date).
"""
import calendar
import csv
import datetime as dt
import html
import json
import math
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")
FI_DIR = os.path.join(DONNEES, "fedinvest")
SORTIE = os.path.join(ICI, "K11_analyse.csv")

D = dt.date


def pdate(s):
    return dt.date.fromisoformat(s)


# ---------------------------------------------------------------------------------------------
# Calendrier C (section 4.3)
# ---------------------------------------------------------------------------------------------
def nieme_jour(annee, mois, jour_semaine, n):
    """n-ieme jour_semaine (0 = lundi) du mois ; n = -1 pour le dernier."""
    if n > 0:
        d = D(annee, mois, 1)
        d += dt.timedelta(days=(jour_semaine - d.weekday()) % 7)
        return d + dt.timedelta(weeks=n - 1)
    d = D(annee, mois, calendar.monthrange(annee, mois)[1])
    return d - dt.timedelta(days=(d.weekday() - jour_semaine) % 7)


def observe(d):
    if d.weekday() == 5:
        return d - dt.timedelta(days=1)
    if d.weekday() == 6:
        return d + dt.timedelta(days=1)
    return d


def feries(annee):
    f = [
        observe(D(annee, 1, 1)),
        nieme_jour(annee, 1, 0, 3),
        nieme_jour(annee, 2, 0, 3),
        nieme_jour(annee, 5, 0, -1),
        observe(D(annee, 7, 4)),
        nieme_jour(annee, 9, 0, 1),
        nieme_jour(annee, 10, 0, 2),
        observe(D(annee, 11, 11)),
        nieme_jour(annee, 11, 3, 4),
        observe(D(annee, 12, 25)),
    ]
    if annee >= 2021:
        f.append(observe(D(annee, 6, 19)))
    return f


SANS_TABLEAU = {D(2012, 10, 30), D(2018, 12, 5)}
DEBUT_C, FIN_C = D(2009, 6, 1), D(2026, 12, 31)


def calendrier_c():
    fer = set()
    for a in range(DEBUT_C.year - 1, FIN_C.year + 2):  # le 1er janvier d'une annee peut etre observe le 31 decembre precedent
        fer.update(feries(a))
    c = []
    d = DEBUT_C
    while d <= FIN_C:
        if d.weekday() < 5 and d not in fer and d not in SANS_TABLEAU:
            c.append(d)
        d += dt.timedelta(days=1)
    return c


# ---------------------------------------------------------------------------------------------
# D1 : adjudications
# ---------------------------------------------------------------------------------------------
def nul(v):
    return v is None or v == "null" or v == ""


def charger_d1():
    with open(os.path.join(DONNEES, "auctions_query.json"), encoding="utf-8") as f:
        return json.load(f)["data"]


def nominale(r):
    return r["inflation_index_security"] != "Yes" and r["floating_rate"] != "Yes"


FAMILLE = {"10-Year": 10, "20-Year": 20, "30-Year": 30, "29-Year 9-Month": 30, "30-Year 3-Month": 30}


def echeance_de_terme(t):
    if t.startswith("9-Year"):
        return 10
    if t.startswith("19-Year"):
        return 20
    if t.startswith("29-Year"):
        return 30
    return None


def premieres_adjudications(d1):
    """Pour chaque CUSIP nominal : sa premiere adjudication (reopening = "No", la plus ancienne)."""
    prem = {}
    for r in d1:
        if not nominale(r) or r["reopening"] != "No":
            continue
        c = r["cusip"]
        if c not in prem or r["auction_date"] < prem[c]["auction_date"]:
            prem[c] = r
    return prem


def ecart_mois(m_a, m_t):
    return 12 * (m_a.year - m_t.year) + (m_a.month - m_t.month)


def selection_metadonnees(d1, cal):
    """Reouvertures etudiees (4.1), dates J-5/J+5 (4.3), membres et candidats (4.4, etapes 1 a 3)."""
    rang_c = {d: i for i, d in enumerate(cal)}
    prem = premieres_adjudications(d1)
    dates_par_cusip = {}
    for r in d1:
        dates_par_cusip.setdefault(r["cusip"], []).append(pdate(r["auction_date"]))
    reouv = [r for r in d1 if nominale(r) and r["reopening"] == "Yes"
             and "2010-01-01" <= r["auction_date"] <= "2026-10-31"
             and echeance_de_terme(r["security_term"]) is not None]
    reouv.sort(key=lambda r: (r["auction_date"], echeance_de_terme(r["security_term"])))
    lignes = []
    for r in reouv:
        J = pdate(r["auction_date"])
        ech = echeance_de_terme(r["security_term"])
        a = r["cusip"]
        pa_ = prem[a]
        fam = FAMILLE.get(pa_["original_security_term"])
        assert fam == ech, (a, pa_["original_security_term"], ech)
        assert J in rang_c, ("J hors de C", a, J)
        k = rang_c[J]
        jm5, jp5 = cal[k - 5], cal[k + 5]
        M = pdate(pa_["maturity_date"])
        # etape 1 : membres de la famille en circulation
        membres = [c for c, p in prem.items()
                   if FAMILLE.get(p["original_security_term"]) == fam
                   and pdate(p["auction_date"]) <= J and pdate(p["maturity_date"]) > jp5]
        # etape 2 : ordre
        membres.sort(key=lambda c: (pdate(prem[c]["maturity_date"]), pdate(prem[c]["auction_date"]), c), reverse=True)
        assert membres[0] == a, ("rang 0 different du titre rouvert", a, J, membres[:3])
        # etape 3 : candidats
        cand = []
        for rg, c in enumerate(membres):
            if rg < 2:
                continue
            em = ecart_mois(M, pdate(prem[c]["maturity_date"]))
            if em > 18:
                continue
            if any(jm5 <= x <= jp5 for x in dates_par_cusip.get(c, [])):
                continue
            cand.append((rg, c, em))
        periode = "avant" if r["auction_date"] <= "2021-12-31" else "apres"
        motif = ""
        if r["auction_date"] == "2019-06-21":
            motif = "hors_calendrier"
        elif len(cand) < 3:
            motif = "temoins_insuffisants"
        elif pdate(pa_["issue_date"]) > jm5:
            motif = "titre_non_emis_a_jm5"
        lignes.append(dict(r=r, J=J, ech=ech, jm5=jm5, jp5=jp5, M=M, prem_a=pa_, membres=membres,
                           cand=cand, periode=periode, motif_meta=motif))
    return lignes, prem


# ---------------------------------------------------------------------------------------------
# D2 : pages FedInvest
# ---------------------------------------------------------------------------------------------
ENTETE = ["CUSIP", "SECURITY TYPE", "RATE", "MATURITY DATE", "CALL DATE", "BUY", "SELL", "END OF DAY"]
RE_TR = re.compile(r"<tr>(.*?)</tr>", re.S)
RE_CELL = re.compile(r"<t([dh])[^>]*>(.*?)</t[dh]>", re.S)
RE_DATE = re.compile(r"Prices For:\s*([A-Za-z]+ \d{1,2}, \d{4})")


def lire_page(date):
    """Renvoie {cusip: (type, rate, maturity, eod)} ou None si la page est absente, de mauvaise date ou vide."""
    chemin = os.path.join(FI_DIR, date.isoformat() + ".html")
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8", errors="replace") as f:
        s = f.read()
    m = RE_DATE.search(s)
    if not m or dt.datetime.strptime(m.group(1), "%B %d, %Y").date() != date:
        return None
    lignes = {}
    entete_vu = False
    for tr in RE_TR.findall(s):
        cells = RE_CELL.findall(tr)
        if not cells:
            continue
        vals = [html.unescape(re.sub(r"<[^>]+>", "", v)).strip() for _, v in cells]
        if cells[0][0] == "h":
            if vals == ENTETE:
                entete_vu = True
            continue
        if not entete_vu or len(vals) != 8:
            continue
        cusip = vals[0]
        if cusip in lignes:
            lignes[cusip] = "DOUBLON"
            continue
        lignes[cusip] = (vals[1], vals[2], vals[3], vals[7])
    if not entete_vu or not lignes:
        return None
    return lignes


def prix_eod(page, cusip):
    if page is None or cusip not in page or page[cusip] == "DOUBLON":
        return None
    try:
        p = float(page[cusip][3])
    except ValueError:
        return None
    return p if p > 0 else None


def identite_ok(page, cusip, coupon, maturite):
    if page is None or cusip not in page or page[cusip] == "DOUBLON":
        return False
    typ, rate, mat, _ = page[cusip]
    if typ not in ("MARKET BASED NOTE", "MARKET BASED BOND"):
        return False
    try:
        r = float(rate.rstrip("%"))
        m = dt.datetime.strptime(mat, "%m/%d/%Y").date()
    except ValueError:
        return False
    return abs(r - coupon) < 1e-9 and m == maturite


# ---------------------------------------------------------------------------------------------
# Rendement (section 5.2)
# ---------------------------------------------------------------------------------------------
def moins_mois(d, n):
    a, m = divmod(d.year * 12 + (d.month - 1) - n, 12)
    return D(a, m + 1, d.day)  # erreur si le jour n'existe pas (toutes les echeances sont le 15)


def rendement(P, coupon, M, d):
    """Y(P, d) en pour cent, 31 CFR 356 annexe B ; resolution par bissection a 1e-12 point."""
    T = []
    k = 0
    while True:
        t = moins_mois(M, 6 * k)
        T.append(t)
        if t <= d:
            break
        k += 1
    L = T[-1]
    N = T[-2]
    n = len(T) - 1  # nombre de T_k > d
    frac = (N - d).days / (N - L).days
    ai = coupon / 2 * (d - L).days / (N - L).days
    cible = P + ai

    def valeur(y):
        v = 1.0 / (1.0 + y / 200.0)
        s = 0.0
        for j in range(1, n + 1):
            F = coupon / 2 + (100.0 if j == n else 0.0)
            s += F * v ** ((j - 1) + frac)
        return s

    lo, hi = -5.0, 50.0
    assert valeur(lo) > cible > valeur(hi)
    while hi - lo > 1e-12:
        mid = (lo + hi) / 2
        if valeur(mid) > cible:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------------------------
COLONNES = (
    ["id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois", "annee", "periode", "heure_cloture",
     "date_emission_origine", "date_reglement", "date_echeance", "taux_coupon_pct", "date_jm5", "date_jp5",
     "ecart_jm5_jours", "ecart_jp5_jours", "cusip_premier_ancien", "echeance_pa", "coupon_pa_pct",
     "cusip_t1", "cusip_t2", "cusip_t3", "rang_t1", "rang_t2", "rang_t3",
     "echeance_t1", "echeance_t2", "echeance_t3", "coupon_t1_pct", "coupon_t2_pct", "coupon_t3_pct",
     "ecart_mois_t1", "ecart_mois_t2", "ecart_mois_t3", "n_temoins_figes", "n_candidats_absents",
     "prix_a_jm5", "prix_a_j", "prix_a_jp5"]
    + [f"prix_t{k}_{x}" for k in (1, 2, 3) for x in ("jm5", "j", "jp5")]
    + ["prix_pa_jm5", "prix_pa_j", "prix_pa_jp5", "identite_fi_ok", "rdt_limite_pct", "prix_limite",
       "rdt_a_jm5_pct", "rdt_a_j_pct", "rdt_a_jp5_pct"]
    + [f"rdt_t{k}_{x}_pct" for k in (1, 2, 3) for x in ("jm5", "j", "jp5")]
    + ["rdt_pa_jm5_pct", "rdt_pa_j_pct", "rdt_pa_jp5_pct", "e_jm5_pb", "e_j_pb", "e_jp5_pb", "v_pb",
       "montee_pb", "detente_pb", "v_pa_pb", "p_carte_pb", "motif_exclusion", "complet", "dans_p"]
)
assert len(COLONNES) == 81
X3 = ("jm5", "j", "jp5")


def fnum(v):
    if v is None:
        return ""
    if isinstance(v, int):
        return str(v)
    return repr(float(v))


def construire():
    d1 = charger_d1()
    cal = calendrier_c()
    lignes, prem = selection_metadonnees(d1, cal)
    pages = {}

    def page(d):
        if d not in pages:
            pages[d] = lire_page(d)
        return pages[d]

    sortie = []
    for L in lignes:
        r, J, jm5, jp5 = L["r"], L["J"], L["jm5"], L["jp5"]
        dates = (jm5, J, jp5)
        row = {c: None for c in COLONNES}
        row.update(id_ligne=f"{r['cusip']}_{r['auction_date']}", cusip=r["cusip"], terme_api=r["security_term"],
                   echeance=L["ech"], date_adjudication=r["auction_date"], mois=r["auction_date"][:7],
                   annee=J.year, periode=L["periode"], heure_cloture=r["closing_time_comp"],
                   date_emission_origine=L["prem_a"]["issue_date"], date_reglement=r["issue_date"],
                   date_echeance=r["maturity_date"], taux_coupon_pct=float(r["int_rate"]),
                   date_jm5=jm5.isoformat(), date_jp5=jp5.isoformat(),
                   ecart_jm5_jours=(J - jm5).days, ecart_jp5_jours=(jp5 - J).days,
                   rdt_limite_pct=None if nul(r["high_yield"]) else float(r["high_yield"]),
                   prix_limite=None if nul(r["high_price"]) else float(r["high_price"]))
        assert r["maturity_date"] == L["prem_a"]["maturity_date"]
        motif = L["motif_meta"]
        if motif:
            row.update(identite_fi_ok=0, motif_exclusion=motif, complet=0, dans_p=0)
            sortie.append(row)
            continue
        coupon_a = float(r["int_rate"])
        M = L["M"]
        # premier ancien
        pa = L["membres"][1]
        p_pa = prem[pa]
        row.update(cusip_premier_ancien=pa, echeance_pa=p_pa["maturity_date"], coupon_pa_pct=float(p_pa["int_rate"]))
        # etape 4 : temoins
        temoins, n_fig, n_abs = [], 0, 0
        for rg, c, em in L["cand"]:
            if len(temoins) == 3:
                break
            px = [prix_eod(page(d), c) for d in dates]
            if any(p is None for p in px):
                n_abs += 1
                continue
            if px[0] == px[1] or px[1] == px[2]:
                n_fig += 1
                continue
            temoins.append((rg, c, em, px))
        row.update(n_temoins_figes=n_fig, n_candidats_absents=n_abs)
        for k, (rg, c, em, px) in enumerate(temoins, start=1):
            row.update({f"cusip_t{k}": c, f"rang_t{k}": rg, f"echeance_t{k}": prem[c]["maturity_date"],
                        f"coupon_t{k}_pct": float(prem[c]["int_rate"]), f"ecart_mois_t{k}": em})
            for x, p in zip(X3, px):
                row[f"prix_t{k}_{x}"] = p
        pxa = [prix_eod(page(d), r["cusip"]) for d in dates]
        for x, p in zip(X3, pxa):
            row[f"prix_a_{x}"] = p
        pxpa = [prix_eod(page(d), pa) for d in dates]
        for x, p in zip(X3, pxpa):
            row[f"prix_pa_{x}"] = p
        # identite
        ok = len(temoins) == 3
        titres = [(r["cusip"], coupon_a, M)] + [(c, float(prem[c]["int_rate"]), pdate(prem[c]["maturity_date"]))
                                               for _, c, _, _ in temoins]
        for c, cp, mt in titres:
            for d in dates:
                if not identite_ok(page(d), c, cp, mt):
                    ok = False
        row["identite_fi_ok"] = 1 if ok else 0
        # rendements
        def rdt(p, cp, mt, d):
            return None if p is None else rendement(p, cp, mt, d)
        for x, p, d in zip(X3, pxa, dates):
            row[f"rdt_a_{x}_pct"] = rdt(p, coupon_a, M, d)
        for k, (rg, c, em, px) in enumerate(temoins, start=1):
            cp, mt = float(prem[c]["int_rate"]), pdate(prem[c]["maturity_date"])
            for x, p, d in zip(X3, px, dates):
                row[f"rdt_t{k}_{x}_pct"] = rendement(p, cp, mt, d)
        cp_pa, mt_pa = float(p_pa["int_rate"]), pdate(p_pa["maturity_date"])
        for x, p, d in zip(X3, pxpa, dates):
            row[f"rdt_pa_{x}_pct"] = rdt(p, cp_pa, mt_pa, d)
        # E, V
        def moyt(x):
            v = [row[f"rdt_t{k}_{x}_pct"] for k in (1, 2, 3)]
            return None if any(t is None for t in v) else (v[0] + v[1] + v[2]) / 3
        E, Epa = {}, {}
        for x in X3:
            ya, ypa, m = row[f"rdt_a_{x}_pct"], row[f"rdt_pa_{x}_pct"], moyt(x)
            E[x] = None if ya is None or m is None else 100 * (ya - m)
            Epa[x] = None if ypa is None or m is None else 100 * (ypa - m)
        row.update(e_jm5_pb=E["jm5"], e_j_pb=E["j"], e_jp5_pb=E["jp5"])
        if all(E[x] is not None for x in X3):
            row["v_pb"] = 2 * E["j"] - E["jm5"] - E["jp5"]
            row["montee_pb"] = E["j"] - E["jm5"]
            row["detente_pb"] = E["j"] - E["jp5"]
        if all(Epa[x] is not None for x in X3):
            row["v_pa_pb"] = 2 * Epa["j"] - Epa["jm5"] - Epa["jp5"]
        if row["rdt_limite_pct"] is not None and row["rdt_a_jm5_pct"] is not None and len(temoins) == 3:
            dvar = sum(row[f"rdt_t{k}_j_pct"] - row[f"rdt_t{k}_jm5_pct"] for k in (1, 2, 3)) / 3
            row["p_carte_pb"] = 100 * ((row["rdt_limite_pct"] - row["rdt_a_jm5_pct"]) - dvar)
        # motif, complet, dans_p
        douze = pxa + [p for _, _, _, px in temoins for p in px]
        complet = 1 if (len(douze) == 12 and all(p is not None and p > 0 for p in douze) and ok) else 0
        pages_absentes = any(page(d) is None for d in dates)
        if pages_absentes or any(p is None for p in pxa) or len(temoins) < 3:
            motif = "prix_manquant"
        elif pxa[0] == pxa[1] or pxa[1] == pxa[2]:
            motif = "prix_fige"
        row.update(motif_exclusion=motif, complet=complet, dans_p=1 if (motif == "" and complet == 1) else 0)
        sortie.append(row)

    with open(SORTIE, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLONNES)
        for row in sortie:
            w.writerow([fnum(row[c]) if isinstance(row[c], (int, float)) else ("" if row[c] is None else row[c])
                        for c in COLONNES])
    return sortie, lignes, cal, prem, d1


# ---------------------------------------------------------------------------------------------
# Controles de schema (section 5.3), relus depuis le fichier ecrit
# ---------------------------------------------------------------------------------------------
def controles(cal, d1):
    with open(SORTIE, encoding="utf-8", newline="") as f:
        rd = csv.reader(f)
        entete = next(rd)
        rows = [dict(zip(entete, x)) for x in rd]
    res = {}
    fl = lambda v: float(v) if v != "" else None
    # 1
    res[1] = entete == COLONNES
    # 2
    ok = len({r["id_ligne"] for r in rows}) == len(rows)
    for r in rows:
        ok &= r["id_ligne"] == f"{r['cusip']}_{r['date_adjudication']}" and len(r["cusip"]) == 9
        ok &= int(r["echeance"]) == echeance_de_terme(r["terme_api"])
        ok &= r["mois"] == r["date_adjudication"][:7] and int(r["annee"]) == int(r["date_adjudication"][:4])
        ok &= r["periode"] == ("avant" if r["date_adjudication"] <= "2021-12-31" else "apres")
        ok &= all(r[c] in ("0", "1") for c in ("identite_fi_ok", "complet", "dans_p"))
    res[2] = bool(ok)
    # 3
    from collections import Counter
    cpt = Counter((r["periode"], int(r["echeance"])) for r in rows)
    ok = len(rows) == 324 and cpt == Counter({("avant", 10): 97, ("avant", 20): 14, ("avant", 30): 96,
                                               ("apres", 10): 39, ("apres", 20): 39, ("apres", 30): 39})
    ok &= [r["id_ligne"] for r in rows if r["motif_exclusion"] == "hors_calendrier"] == ["9128286T2_2019-06-21"]
    ti = [r for r in rows if r["motif_exclusion"] == "temoins_insuffisants"]
    ok &= len(ti) == 8 and all(r["echeance"] == "20" and "2020-06-17" <= r["date_adjudication"] <= "2021-04-21" for r in ti)
    ok &= len([r for r in rows if r["echeance"] == "20" and "2020-06-17" <= r["date_adjudication"] <= "2021-04-21"]) == 8
    ok &= [r["id_ligne"] for r in rows if r["motif_exclusion"] == "titre_non_emis_a_jm5"] == ["912810TC2_2021-12-02"]
    res[3] = bool(ok)
    # 4
    rang = {d: i for i, d in enumerate(cal)}
    ok = True
    for r in rows:
        J, a, b = pdate(r["date_adjudication"]), pdate(r["date_jm5"]), pdate(r["date_jp5"])
        ok &= J in rang and cal[rang[J] - 5] == a and cal[rang[J] + 5] == b
        ok &= int(r["ecart_jm5_jours"]) == (J - a).days and int(r["ecart_jp5_jours"]) == (b - J).days
        ok &= 7 <= (J - a).days <= 11 and 7 <= (b - J).days <= 11
    res[4] = bool(ok)
    # 5 : refait les etapes 1 a 3 de 4.4 de facon independante
    prem = premieres_adjudications(d1)
    dates_c = {}
    for x in d1:
        dates_c.setdefault(x["cusip"], []).append(x["auction_date"])
    ok = True
    meta = ("hors_calendrier", "temoins_insuffisants", "titre_non_emis_a_jm5")
    for r in rows:
        if r["motif_exclusion"] in meta:
            continue
        t = [r[f"cusip_t{k}"] for k in (1, 2, 3)]
        if "" in t:
            # ligne prix_manquant sans trois temoins : on verifie seulement les temoins presents
            pass
        tp = [c for c in t if c]
        ok &= len(set(tp)) == len(tp) and r["cusip"] not in tp and r["cusip_premier_ancien"] not in tp
        rg = [int(r[f"rang_t{k}"]) for k in (1, 2, 3) if r[f"rang_t{k}"]]
        ok &= rg == sorted(set(rg)) and all(x >= 2 for x in rg)
        ec = [r[f"echeance_t{k}"] for k in (1, 2, 3) if r[f"echeance_t{k}"]]
        ok &= ec == sorted(ec, reverse=True) and all(e < r["date_echeance"] for e in ec)
        Ma = pdate(r["date_echeance"])
        for k in (1, 2, 3):
            if r[f"echeance_t{k}"]:
                em = ecart_mois(Ma, pdate(r[f"echeance_t{k}"]))
                ok &= int(r[f"ecart_mois_t{k}"]) == em and 1 <= em <= 18
        J, a, b = r["date_adjudication"], r["date_jm5"], r["date_jp5"]
        fam = FAMILLE[prem[r["cusip"]]["original_security_term"]]
        mem = sorted([c for c, p in prem.items() if FAMILLE.get(p["original_security_term"]) == fam
                      and p["auction_date"] <= J and p["maturity_date"] > b],
                     key=lambda c: (prem[c]["maturity_date"], prem[c]["auction_date"], c), reverse=True)
        ok &= mem[0] == r["cusip"] and mem[1] == r["cusip_premier_ancien"]
        cand = [c for i, c in enumerate(mem) if i >= 2
                and ecart_mois(Ma, pdate(prem[c]["maturity_date"])) <= 18
                and not any(a <= x <= b for x in dates_c.get(c, []))]
        s = int(r["n_temoins_figes"]) + int(r["n_candidats_absents"])
        pos = [cand.index(c) if c in cand else 10 ** 6 for c in tp]
        ok &= pos == sorted(pos) and all(p < 3 + s for p in pos)
        ok &= all(int(r[f"rang_t{k}"]) == mem.index(r[f"cusip_t{k}"]) for k in (1, 2, 3) if r[f"cusip_t{k}"])
    res[5] = bool(ok)
    P = [r for r in rows if r["dans_p"] == "1"]
    # 6
    res[6] = all(r["date_emission_origine"] <= r["date_jm5"] for r in P)
    # 7
    ok = True
    pcols = ["prix_a_jm5", "prix_a_j", "prix_a_jp5"] + [f"prix_t{k}_{x}" for k in (1, 2, 3) for x in X3]
    ycols = ["rdt_a_jm5_pct", "rdt_a_j_pct", "rdt_a_jp5_pct"] + [f"rdt_t{k}_{x}_pct" for k in (1, 2, 3) for x in X3]
    ccols = ["taux_coupon_pct", "coupon_t1_pct", "coupon_t2_pct", "coupon_t3_pct"]
    for r in P:
        ok &= all(30 <= float(r[c]) <= 200 for c in pcols)
        ok &= all(-1 <= float(r[c]) <= 20 for c in ycols)
        ok &= all(0 <= float(r[c]) <= 15 for c in ccols)
    res[7] = bool(ok)
    # 8
    res[8] = all(abs(float(r[f"rdt_t{k}_{x}_pct"]) - float(r[f"rdt_a_{x}_pct"])) <= 0.60
                 for r in P for k in (1, 2, 3) for x in X3)
    # 9
    ok = True
    for r in P:
        for t in ["a", "t1", "t2", "t3"]:
            ok &= r[f"prix_{t}_j"] != r[f"prix_{t}_jm5"] and r[f"prix_{t}_j"] != r[f"prix_{t}_jp5"]
            ok &= float(r[f"prix_{t}_j"]) != float(r[f"prix_{t}_jm5"]) and float(r[f"prix_{t}_j"]) != float(r[f"prix_{t}_jp5"])
    res[9] = bool(ok)
    # 10
    res[10] = all(r["identite_fi_ok"] == "1" for r in P)
    # 11
    ok = True
    for r in rows:
        y = {c: fl(r[c]) for c in entete if c.startswith("rdt_") or c.startswith("prix_")}

        def E(t, x):
            vals = [y[f"rdt_{t}_{x}_pct"]] + [y[f"rdt_t{k}_{x}_pct"] for k in (1, 2, 3)]
            if any(v is None for v in vals):
                return None
            return 100 * (vals[0] - (vals[1] + vals[2] + vals[3]) / 3)

        def egal(col, val):
            v = fl(r[col])
            if val is None:
                return v is None
            return v is not None and abs(v - val) <= 1e-6

        ea = {x: E("a", x) for x in X3}
        ep = {x: E("pa", x) for x in X3}
        if r["motif_exclusion"] in meta:
            continue
        ok &= egal("e_jm5_pb", ea["jm5"]) and egal("e_j_pb", ea["j"]) and egal("e_jp5_pb", ea["jp5"])
        full = all(ea[x] is not None for x in X3)
        ok &= egal("v_pb", 2 * ea["j"] - ea["jm5"] - ea["jp5"] if full else None)
        ok &= egal("montee_pb", ea["j"] - ea["jm5"] if full else None)
        ok &= egal("detente_pb", ea["j"] - ea["jp5"] if full else None)
        fp = all(ep[x] is not None for x in X3)
        ok &= egal("v_pa_pb", 2 * ep["j"] - ep["jm5"] - ep["jp5"] if fp else None)
        ins = [fl(r["rdt_limite_pct"]), y["rdt_a_jm5_pct"]] + [y[f"rdt_t{k}_{x}_pct"] for k in (1, 2, 3) for x in ("j", "jm5")]
        pc = None
        if all(v is not None for v in ins):
            pc = 100 * ((ins[0] - ins[1]) - sum(y[f"rdt_t{k}_j_pct"] - y[f"rdt_t{k}_jm5_pct"] for k in (1, 2, 3)) / 3)
        ok &= egal("p_carte_pb", pc)
        douze = [y[c] for c in pcols]
        cpl = 1 if all(v is not None and v > 0 for v in douze) and r["identite_fi_ok"] == "1" else 0
        ok &= int(r["complet"]) == cpl
        ok &= int(r["dans_p"]) == (1 if r["motif_exclusion"] == "" and cpl == 1 else 0)
    for r in rows:
        if r["motif_exclusion"] in meta:
            ok &= r["complet"] == "0" and r["dans_p"] == "0"
    res[11] = bool(ok)
    return res, rows


def dates_requises():
    d1 = charger_d1()
    cal = calendrier_c()
    lignes, _ = selection_metadonnees(d1, cal)
    ds = set()
    for L in lignes:
        if not L["motif_meta"]:
            ds.update([L["jm5"], L["J"], L["jp5"]])
    return sorted(ds), lignes


def main():
    if "--dates" in sys.argv:
        ds, lignes = dates_requises()
        with open(os.path.join(ICI, "dates_requises.txt"), "w") as f:
            f.write("\n".join(d.isoformat() for d in ds) + "\n")
        print(len(ds), "dates ;", sum(1 for d in ds if d.year >= 2022), "en 2022-2026")
        return
    sortie, lignes, cal, prem, d1 = construire()
    from collections import Counter
    print("lignes :", len(sortie))
    print("motifs :", Counter(r["motif_exclusion"] for r in sortie))
    print("dans_p :", sum(r["dans_p"] for r in sortie))
    print("n_temoins_figes (toutes lignes) :", sum(r["n_temoins_figes"] or 0 for r in sortie),
          " n_candidats_absents :", sum(r["n_candidats_absents"] or 0 for r in sortie))
    res, rows = controles(cal, d1)
    for k in sorted(res):
        print(f"controle {k:2d} : {'OK' if res[k] else 'ECHEC'}")
    print("schema_ok =", int(all(res.values())))


if __name__ == "__main__":
    main()
