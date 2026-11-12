"""J05 — construction du fichier d'analyse J05_analyse.csv à partir de donnees/ seulement.

Entrées (brutes, non modifiées) :
  donnees/auctions_query.json      (D1, Fiscal Data API v1)
  donnees/feds200628.csv           (D2, paramètres GSW)
  donnees/fedinvest/AAAA-MM-JJ.html (D3, pages FedInvest « securityPriceDetail »)
Sortie : J05_analyse.csv (45 colonnes, section 5 de la préinscription) et construire_journal.json (comptes, contrôles).
Usage : python3 -I construire.py
"""
import bisect
import csv
import datetime as dt
import html as htmlmod
import json
import math
import os
import re
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
DON = os.path.join(ICI, "donnees")
SORTIE = os.path.join(ICI, "J05_analyse.csv")
JOURNAL = os.path.join(ICI, "construire_journal.json")

PARAMS = ("BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2")
COLONNES = [
    "id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois", "periode", "heure_cloture",
    "format_adjudication", "date_reglement", "date_echeance", "taux_coupon_pct", "rdt_limite_pct", "prix_limite",
    "coupon_couru_api", "coupon_couru_calc", "date_gsw_j",
    "beta0_j", "beta1_j", "beta2_j", "beta3_j", "tau1_j", "tau2_j",
    "date_jm5", "beta0_jm5", "beta1_jm5", "beta2_jm5", "beta3_jm5", "tau1_jm5", "tau2_jm5",
    "prix_fi_jm5", "prix_fi_j", "rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct", "rdt_gsw_jm5_pct",
    "rdt_fi_jm5_pct", "rdt_fi_j_pct", "c_pb", "k_pb", "r_fi_pb", "convention_ok", "complet_k", "complet_r", "dans_p",
]
assert len(COLONNES) == 45


# ----------------------------------------------------------------------------------------------- conventions (5.2)
def D(s):
    return dt.date.fromisoformat(s)


def recule_mois(M, k):
    """M reculée de k mois, même jour du mois (dernier jour du mois si ce jour n'existe pas)."""
    a, m = M.year, M.month - k
    while m <= 0:
        m += 12
        a -= 1
    for jour in range(M.day, 27, -1) if M.day > 28 else [M.day]:
        try:
            return dt.date(a, m, jour)
        except ValueError:
            continue
    raise ValueError


def dates_coupon(M, d):
    """Liste croissante des T_k > d (avec M en dernier) et L(d) = dernier T_k <= d."""
    apres = []
    k = 0
    while True:
        T = recule_mois(M, 6 * k)
        if T <= d:
            return sorted(apres), T
        apres.append(T)
        k += 1


def coupon_couru(c, M, d):
    futurs, L = dates_coupon(M, d)
    N = futurs[0]
    return (c / 2.0) * (d - L).days / (N - L).days


def prix_plein_de_y(y, c, M, d):
    futurs, L = dates_coupon(M, d)
    N = futurs[0]
    n = len(futurs)
    w = (N - d).days / (N - L).days
    v = 1.0 / (1.0 + y / 200.0)
    tot = 0.0
    for j in range(1, n + 1):
        F = c / 2.0 + (100.0 if j == n else 0.0)
        tot += F * v ** ((j - 1) + w)
    return tot


def rendement(P, c, M, d):
    """Y(P, d) : rendement (pct) d'un prix pied de coupon P pour règlement d (31 CFR 356 annexe B)."""
    cible = P + coupon_couru(c, M, d)
    f = lambda y: prix_plein_de_y(y, c, M, d) - cible
    lo, hi = -5.0, 40.0
    flo, fhi = f(lo), f(hi)
    assert flo > 0 > fhi, (P, c, M, d)
    # bissection jusqu'à 1e-12 point de pourcentage (exigence : 1e-9)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if fm > 0:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return 0.5 * (lo + hi)


def z_gsw(p, m):
    b0, b1, b2, b3, t1, t2 = p
    x1, x2 = m / t1, m / t2
    e1, e2 = math.exp(-x1), math.exp(-x2)
    l1 = (1 - e1) / x1
    l2 = (1 - e2) / x2
    return b0 + b1 * l1 + b2 * (l1 - e1) + b3 * (l2 - e2)


def actu(p, x, date):
    m = (date - x).days / 365.25
    return math.exp(-z_gsw(p, m) * m / 100.0)


def flux_apres(c, M, d):
    futurs, _ = dates_coupon(M, d)
    return [(T, c / 2.0 + (100.0 if T == M else 0.0)) for T in futurs]


def g_comptant(p, x, c, M):
    plein = sum(F * actu(p, x, T) for T, F in flux_apres(c, M, x))
    return rendement(plein - coupon_couru(c, M, x), c, M, x)


def g_terme(p, J, s, c, M):
    plein = sum(F * actu(p, J, T) for T, F in flux_apres(c, M, s)) / actu(p, J, s)
    return rendement(plein - coupon_couru(c, M, s), c, M, s)


# ------------------------------------------------------------------------------------------------------- lectures
def lire_d1():
    d = json.load(open(os.path.join(DON, "auctions_query.json"), encoding="utf-8"))
    return d["data"]


def lire_d2():
    with open(os.path.join(DON, "feds200628.csv"), encoding="utf-8") as f:
        lignes = f.read().splitlines()
    assert lignes[9].startswith("Date,"), "en-tête D2 attendu à la ligne 10"
    rd = csv.DictReader(lignes[9:])
    for k in ("Date",) + PARAMS:
        assert k in rd.fieldnames, k
    gsw = {}
    for r in rd:
        if all(r[k] not in ("NA", "") for k in PARAMS):
            gsw[r["Date"]] = tuple(float(r[k]) for k in PARAMS)
    cal = sorted(gsw)
    return gsw, cal


RE_TR = re.compile(r"<tr>(.*?)</tr>", re.S)
RE_TD = re.compile(r"<td[^>]*>(.*?)</td>", re.S)


def lire_fedinvest(date):
    """Renvoie (statut, {cusip: (rate, end_of_day_str)}) ; statut ok / absente / date_differente / vide."""
    chemin = os.path.join(DON, "fedinvest", f"{date}.html")
    if not os.path.exists(chemin):
        return "absente", {}
    h = open(chemin, encoding="utf-8", errors="replace").read()
    m = re.search(r"Prices For:\s*([A-Za-z]+ \d{1,2}, \d{4})", h)
    if not m:
        return "absente", {}
    affichee = dt.datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()
    if affichee != date:
        return "date_differente", {}
    i = h.find('<table class="data1">')
    if i < 0:
        return "vide", {}
    tab = h[i:h.find("</table>", i)]
    entete = re.findall(r"<th>(.*?)</th>", tab)
    assert entete == ["CUSIP", "SECURITY TYPE", "RATE", "MATURITY DATE", "CALL DATE", "BUY", "SELL", "END OF DAY"], entete
    out = {}
    for tr in RE_TR.findall(tab):
        tds = [htmlmod.unescape(x).strip() for x in RE_TD.findall(tr)]
        if len(tds) != 8:
            continue
        out[tds[0]] = (tds[2], tds[7])
    if not out:
        return "vide", {}
    return "ok", out


# ----------------------------------------------------------------------------------------------------- construction
def periode_de(a):
    if "1991-01-01" <= a <= "2009-12-31":
        return "ancien"
    if "2010-01-01" <= a <= "2021-12-31":
        return "avant"
    if "2022-01-01" <= a <= "2026-10-31":
        return "apres"
    return None


def num(s):
    return None if s in (None, "", "null") else float(s)


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    return str(v)


def main():
    d1 = lire_d1()
    gsw, cal = lire_d2()
    pos = {x: i for i, x in enumerate(cal)}
    journal = {"lignes_d1": len(d1), "derniere_date_gsw": cal[-1], "ecartees_first_int_period": []}

    ech = {"9": 10, "19": 20, "29": 30}
    sel = []
    for r in d1:
        if r["reopening"] != "Yes" or r["inflation_index_security"] == "Yes" or r["floating_rate"] == "Yes":
            continue
        pre = r["security_term"].split("-")[0]
        if not r["security_term"].startswith(pre + "-Year") or pre not in ech:
            continue
        if r["first_int_period"] != "Normal":
            journal["ecartees_first_int_period"].append(r["cusip"] + "_" + r["auction_date"])
            continue
        sel.append(r)
    sel.sort(key=lambda r: (r["auction_date"], ech[r["security_term"].split("-")[0]]))
    journal["selectionnees"] = len(sel)

    cache_fi = {}
    def fi(date):
        if date not in cache_fi:
            cache_fi[date] = lire_fedinvest(date)
        return cache_fi[date]

    sorties = []
    raisons = {"j_absent_de_C": [], "high_yield_ou_price_nul": [], "fi_jm5_page": [], "fi_jm5_cusip_absent": [],
               "fi_jm5_prix_vide_ou_nul": [], "fi_j_page": [], "fi_j_cusip_absent": [], "fi_j_prix_vide_ou_nul": [],
               "taux_fedinvest_different": []}
    for r in sel:
        J = r["auction_date"]
        cus = r["cusip"]
        pid = cus + "_" + J
        per = periode_de(J)
        c = float(r["int_rate"])
        M, s, Jd = D(r["maturity_date"]), D(r["issue_date"]), D(J)
        hy, hp = num(r["high_yield"]), num(r["high_price"])
        ai_api = float(r["accrued_int_per1000"]) / 10.0
        ai_calc = coupon_couru(c, M, s)
        o = {k: None for k in COLONNES}
        o.update(id_ligne=pid, cusip=cus, terme_api=r["security_term"], echeance=ech[r["security_term"].split("-")[0]],
                 date_adjudication=J, mois=J[:7], periode=per,
                 heure_cloture="" if r["closing_time_comp"] == "null" else r["closing_time_comp"],
                 format_adjudication=r["auction_format"], date_reglement=r["issue_date"], date_echeance=r["maturity_date"],
                 taux_coupon_pct=c, rdt_limite_pct=hy, prix_limite=hp, coupon_couru_api=ai_api, coupon_couru_calc=ai_calc)
        if hy is None or hp is None:
            raisons["high_yield_ou_price_nul"].append(pid)
        # GSW à J (doit être le jour même) et J-5
        pj = None
        if J in pos:
            o["date_gsw_j"] = J
            pj = gsw[J]
            for k, v in zip(("beta0_j", "beta1_j", "beta2_j", "beta3_j", "tau1_j", "tau2_j"), pj):
                o[k] = v
        else:
            raisons["j_absent_de_C"].append(pid)
        pm5 = None
        if per in ("avant", "apres") and J in pos and pos[J] >= 5:
            jm5 = cal[pos[J] - 5]
            o["date_jm5"] = jm5
            pm5 = gsw[jm5]
            for k, v in zip(("beta0_jm5", "beta1_jm5", "beta2_jm5", "beta3_jm5", "tau1_jm5", "tau2_jm5"), pm5):
                o[k] = v
        # FedInvest
        if per in ("avant", "apres"):
            for quand, date, col in (("jm5", o["date_jm5"], "prix_fi_jm5"), ("j", J, "prix_fi_j")):
                if date is None:
                    raisons[f"fi_{quand}_page"].append(pid)
                    continue
                st, tab = fi(date)
                if st != "ok":
                    raisons[f"fi_{quand}_page"].append(pid + ":" + st)
                    continue
                if cus not in tab:
                    raisons[f"fi_{quand}_cusip_absent"].append(pid)
                    continue
                rate, eod = tab[cus]
                pv = num(eod.replace(",", "")) if eod else None
                if pv is None or pv == 0.0:
                    raisons[f"fi_{quand}_prix_vide_ou_nul"].append(pid)
                    continue
                try:
                    if abs(float(rate.rstrip("%")) - c) > 1e-9:
                        raisons["taux_fedinvest_different"].append(pid + ":" + rate)
                except ValueError:
                    raisons["taux_fedinvest_different"].append(pid + ":" + rate)
                o[col] = pv
        # Rendements (une valeur dérivée est vide si une entrée l'est)
        if hp is not None:
            o["rdt_prix_limite_pct"] = rendement(hp, c, M, s)
        if pj is not None:
            o["rdt_gsw_j_terme_pct"] = g_terme(pj, Jd, s, c, M)
            if per in ("avant", "apres"):
                o["rdt_gsw_j_pct"] = g_comptant(pj, Jd, c, M)
        if pm5 is not None:
            x = D(o["date_jm5"])
            o["rdt_gsw_jm5_pct"] = g_comptant(pm5, x, c, M)
            if o["prix_fi_jm5"] is not None:
                o["rdt_fi_jm5_pct"] = rendement(o["prix_fi_jm5"], c, M, x)
        if o["prix_fi_j"] is not None:
            o["rdt_fi_j_pct"] = rendement(o["prix_fi_j"], c, M, Jd)
        if hy is not None and o["rdt_gsw_j_terme_pct"] is not None:
            o["c_pb"] = 100.0 * (hy - o["rdt_gsw_j_terme_pct"])
        if o["c_pb"] is not None and o["rdt_fi_jm5_pct"] is not None and o["rdt_gsw_jm5_pct"] is not None:
            o["k_pb"] = o["c_pb"] - 100.0 * (o["rdt_fi_jm5_pct"] - o["rdt_gsw_jm5_pct"])
        if None not in (o["rdt_fi_j_pct"], o["rdt_gsw_j_pct"], o["rdt_fi_jm5_pct"], o["rdt_gsw_jm5_pct"]):
            o["r_fi_pb"] = 100.0 * ((o["rdt_fi_j_pct"] - o["rdt_gsw_j_pct"]) - (o["rdt_fi_jm5_pct"] - o["rdt_gsw_jm5_pct"]))
        # Indicatrices
        o["convention_ok"] = int(o["rdt_prix_limite_pct"] is not None and hy is not None
                                 and abs(o["rdt_prix_limite_pct"] - hy) <= 0.001 and abs(ai_calc - ai_api) <= 0.001)
        entrees_k = ["rdt_limite_pct", "prix_limite", "beta0_j", "beta1_j", "beta2_j", "beta3_j", "tau1_j", "tau2_j",
                     "date_jm5", "beta0_jm5", "beta1_jm5", "beta2_jm5", "beta3_jm5", "tau1_jm5", "tau2_jm5", "prix_fi_jm5"]
        o["complet_k"] = int(all(o[k] is not None for k in entrees_k) and o["date_gsw_j"] == J)
        o["complet_r"] = int(o["complet_k"] == 1 and o["prix_fi_j"] is not None)
        o["dans_p"] = int(per in ("avant", "apres") and o["complet_k"] == 1 and o["convention_ok"] == 1)
        sorties.append(o)

    with open(SORTIE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLONNES)
        for o in sorties:
            w.writerow([fmt(o[k]) for k in COLONNES])

    # ------------------------------------------------------------------ contrôles de schéma (5.3) relus sur le fichier
    ctrl = controles(SORTIE)
    journal["raisons_manquant"] = {k: v for k, v in raisons.items()}
    journal["n_par_raison"] = {k: len(v) for k, v in raisons.items()}
    journal["controles_schema"] = ctrl
    journal["schema_ok"] = int(all(v["ok"] for v in ctrl.values()))
    # comptes à chaque filtre
    cpt = {}
    for per in ("ancien", "avant", "apres"):
        L = [o for o in sorties if o["periode"] == per]
        cpt[per] = {
            "lignes": len(L),
            "high_yield_et_prix_presents": sum(o["rdt_limite_pct"] is not None and o["prix_limite"] is not None for o in L),
            "convention_ok": sum(o["convention_ok"] for o in L),
            "c_pb_present": sum(o["c_pb"] is not None for o in L),
            "complet_k": sum(o["complet_k"] for o in L),
            "complet_k_et_convention_ok": sum(o["complet_k"] * o["convention_ok"] for o in L),
            "dans_p": sum(o["dans_p"] for o in L),
            "complet_r_dans_p": sum(o["complet_r"] * o["dans_p"] for o in L),
            "mois_dans_p": len({o["mois"] for o in L if o["dans_p"]}),
        }
    journal["comptes"] = cpt
    json.dump(journal, open(JOURNAL, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({"comptes": cpt, "n_par_raison": journal["n_par_raison"], "schema_ok": journal["schema_ok"],
                      "controles_en_echec": {k: v for k, v in ctrl.items() if not v["ok"]}}, ensure_ascii=False, indent=1))


def controles(chemin):
    with open(chemin, encoding="utf-8") as f:
        rd = csv.reader(f)
        ent = next(rd)
        L = [dict(zip(ent, r)) for r in rd]
    res = {}
    def put(n, ok, detail=""):
        res[n] = {"ok": bool(ok), "detail": detail}
    put("1_colonnes", ent == COLONNES)
    f_ = lambda x: float(x) if x != "" else None
    # 2
    pb = []
    ids = [r["id_ligne"] for r in L]
    if len(set(ids)) != len(ids):
        pb.append("id non unique")
    for r in L:
        if r["id_ligne"] != r["cusip"] + "_" + r["date_adjudication"] or len(r["cusip"]) != 9:
            pb.append(r["id_ligne"])
        attendu = {"9-Year": "10", "19-Year": "20", "29-Year": "30"}
        e = [v for k, v in attendu.items() if r["terme_api"].startswith(k)]
        if e != [r["echeance"]]:
            pb.append(r["id_ligne"] + ":echeance")
        if r["mois"] != r["date_adjudication"][:7] or r["periode"] != periode_de(r["date_adjudication"]):
            pb.append(r["id_ligne"] + ":mois/periode")
        for k in ("convention_ok", "complet_k", "complet_r", "dans_p"):
            if r[k] not in ("0", "1"):
                pb.append(r["id_ligne"] + ":" + k)
    put("2_identifiants", not pb, pb[:10])
    # 3
    nper = {p: sum(r["periode"] == p for r in L) for p in ("ancien", "avant", "apres")}
    ok3 = all("1991-01-01" <= r["date_adjudication"] <= "2026-10-31" for r in L) and 60 <= nper["ancien"] <= 70 \
        and 200 <= nper["avant"] <= 214 and 112 <= nper["apres"] <= 120
    put("3_dates_et_comptes", ok3, nper)
    # 4
    pb = [r["id_ligne"] for r in L if not (0 < (D(r["date_reglement"]) - D(r["date_adjudication"])).days <= 20
                                           and D(r["date_echeance"]) > D(r["date_reglement"]))]
    # (« postérieure ... d'au plus 20 jours » : lu comme 0 < délai <= 20)
    put("4_reglement_echeance", not pb, pb[:10])
    # 5 pas de regard vers l'avenir
    pb = []
    for r in L:
        J = D(r["date_adjudication"])
        if r["date_gsw_j"] != "" and r["date_gsw_j"] != r["date_adjudication"]:
            pb.append(r["id_ligne"] + ":gsw_j")
        if r["date_gsw_j"] == "" and any(r[k] != "" for k in ("beta0_j", "beta1_j", "beta2_j", "beta3_j", "tau1_j", "tau2_j")):
            pb.append(r["id_ligne"] + ":params_j_sans_date")
        if r["date_jm5"] != "":
            x = D(r["date_jm5"])
            if not (x < J and 7 <= (J - x).days <= 9 and x.weekday() < 5):
                pb.append(r["id_ligne"] + ":jm5")
        elif any(r[k] != "" for k in ("beta0_jm5", "beta1_jm5", "beta2_jm5", "beta3_jm5", "tau1_jm5", "tau2_jm5", "prix_fi_jm5")):
            pb.append(r["id_ligne"] + ":params_jm5_sans_date")
        # prix FedInvest : datés date_jm5 (< J) et J (= J) par construction de la colonne ; rien après J
    put("5_pas_de_regard_vers_avenir", not pb, pb[:10])
    # 6
    pb = []
    for r in L:
        for k in ("rdt_limite_pct", "rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct", "rdt_gsw_jm5_pct",
                  "rdt_fi_jm5_pct", "rdt_fi_j_pct"):
            v = f_(r[k])
            if v is not None and not (-1 <= v <= 20):
                pb.append(r["id_ligne"] + ":" + k)
        for k in ("prix_limite", "prix_fi_jm5", "prix_fi_j"):
            v = f_(r[k])
            if v is not None and not (50 <= v <= 200):
                pb.append(r["id_ligne"] + ":" + k)
        for k in ("tau1_j", "tau2_j", "tau1_jm5", "tau2_jm5"):
            v = f_(r[k])
            if v is not None and not v > 0:
                pb.append(r["id_ligne"] + ":" + k)
        v = f_(r["taux_coupon_pct"])
        if not (0 <= v <= 15):
            pb.append(r["id_ligne"] + ":coupon")
    put("6_plages", not pb, pb[:10])
    # 7
    pb = []
    for r in L:
        a, b = f_(r["rdt_fi_jm5_pct"]), f_(r["rdt_gsw_jm5_pct"])
        if a is not None and b is not None and abs(a - b) > 0.60:
            pb.append(r["id_ligne"] + ":jm5 %.4f" % (a - b))
        a, b = f_(r["rdt_fi_j_pct"]), f_(r["rdt_limite_pct"])
        if a is not None and b is not None and abs(a - b) > 0.40:
            pb.append(r["id_ligne"] + ":j %.4f" % (a - b))
    put("7_appariement", not pb, pb[:10])
    # 8
    pb = []
    for r in L:
        g = {k: f_(r[k]) for k in ("rdt_limite_pct", "rdt_gsw_j_terme_pct", "rdt_fi_jm5_pct", "rdt_gsw_jm5_pct",
                                   "rdt_fi_j_pct", "rdt_gsw_j_pct", "c_pb", "k_pb", "r_fi_pb", "rdt_prix_limite_pct",
                                   "coupon_couru_calc", "coupon_couru_api")}
        def eq(col, val):
            if val is None:
                return g[col] is None
            return g[col] is not None and abs(g[col] - val) <= 1e-6
        cv = None if None in (g["rdt_limite_pct"], g["rdt_gsw_j_terme_pct"]) else 100 * (g["rdt_limite_pct"] - g["rdt_gsw_j_terme_pct"])
        kv = None if None in (cv, g["rdt_fi_jm5_pct"], g["rdt_gsw_jm5_pct"]) else cv - 100 * (g["rdt_fi_jm5_pct"] - g["rdt_gsw_jm5_pct"])
        rv = None if None in (g["rdt_fi_j_pct"], g["rdt_gsw_j_pct"], g["rdt_fi_jm5_pct"], g["rdt_gsw_jm5_pct"]) else \
            100 * ((g["rdt_fi_j_pct"] - g["rdt_gsw_j_pct"]) - (g["rdt_fi_jm5_pct"] - g["rdt_gsw_jm5_pct"]))
        if not (eq("c_pb", cv) and eq("k_pb", kv) and eq("r_fi_pb", rv)):
            pb.append(r["id_ligne"] + ":formules")
        conv = int(g["rdt_prix_limite_pct"] is not None and g["rdt_limite_pct"] is not None
                   and abs(g["rdt_prix_limite_pct"] - g["rdt_limite_pct"]) <= 0.001
                   and g["coupon_couru_calc"] is not None and abs(g["coupon_couru_calc"] - g["coupon_couru_api"]) <= 0.001)
        cols_k = ["rdt_limite_pct", "prix_limite", "beta0_j", "beta1_j", "beta2_j", "beta3_j", "tau1_j", "tau2_j",
                  "beta0_jm5", "beta1_jm5", "beta2_jm5", "beta3_jm5", "tau1_jm5", "tau2_jm5", "prix_fi_jm5"]
        ck = int(all(r[k] != "" for k in cols_k) and r["date_gsw_j"] == r["date_adjudication"])
        cr = int(ck == 1 and r["prix_fi_j"] != "")
        dp = int(r["periode"] in ("avant", "apres") and ck == 1 and conv == 1)
        if (str(conv), str(ck), str(cr), str(dp)) != (r["convention_ok"], r["complet_k"], r["complet_r"], r["dans_p"]):
            pb.append(r["id_ligne"] + ":indicatrices")
    put("8_formules_indicatrices", not pb, pb[:10])
    return res


if __name__ == "__main__":
    main()
