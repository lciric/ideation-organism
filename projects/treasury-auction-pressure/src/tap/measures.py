"""The four analysis datasets and their preregistered primary statistics.

Column names follow the sealed preregistrations (written in French), so that each file
can be checked against the text that defines it; README.md has a glossary.

- F04:     V = 100 [2E(J) - E(J-5) - E(J+5)], E = Treasury CMT yield - GSW par yield.
- F04-bis: the same V on fiscal-2021 reopenings with the Treasury's old (HS) and new (MC)
           curve methods; D = V_HS - V_MC.
- J05:     K = 100 {[auction high yield - g(J)] - [f(J-5) - g(J-5)]}, g = the security
           valued on the GSW curve, f = the security's yield from its FedInvest price.
- K11:     V with E = reopened security minus the mean of three control securities
           (2nd-4th off-the-run of the same family), all from FedInvest prices.
"""
import math
from datetime import date

import numpy as np
import pandas as pd

from . import bonds, data
from .stats import cluster_mean, interval, ols_cluster

X3 = ["jm5", "j", "jp5"]  # the three window dates J-5, J, J+5


def _num(s):
    """Float of a text field; NaN for '', 'null' or None."""
    return np.nan if s in ("", "null", None) else float(s)


def _iso(d):
    return d.isoformat() if d else ""


def _missing(*values):
    return any(v is None or (isinstance(v, float) and math.isnan(v)) for v in values)


# ============================================================================= F04
F04_TERMS = {  # security_term -> (maturity in years, reopening flag), F04 section 4, D1
    "2-Year": (2, 0), "3-Year": (3, 0), "5-Year": (5, 0), "7-Year": (7, 0),
    "10-Year": (10, 0), "20-Year": (20, 0), "30-Year": (30, 0),
    "9-Year 10-Month": (10, 1), "9-Year 11-Month": (10, 1),
    "19-Year 10-Month": (20, 1), "19-Year 11-Month": (20, 1),
    "29-Year 10-Month": (30, 1), "29-Year 11-Month": (30, 1),
}
F04_COLUMNS = ["id_ligne", "type_ligne", "cusip", "terme_api", "echeance", "reouverture", "principal",
               "date_adjudication", "mois", "montant_offert_mds", "date_j", "date_jm5", "date_jp5",
               "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5", "complet", "fenetre_propre"]


def build_f04(auctions, cmt, gsw, cal):
    """F04 analysis file: one 'reelle' row per auction, one 'placebo' row per principal reopening.

    cmt[maturity][date] and gsw (data.gsw_curve()) hold the yields as text; cal = DGS10 calendar."""
    a = auctions[(auctions.inflation_index_security == "No") & (auctions.floating_rate == "No")]
    real = []  # other security_term values would be dropped; there are none
    for r in a[a.security_term.isin(F04_TERMS)].itertuples():
        maturity, reopening = F04_TERMS[r.security_term]
        real.append({"type_ligne": "reelle", "cusip": r.cusip, "terme_api": r.security_term,
                     "echeance": maturity, "reouverture": reopening,
                     "principal": int(reopening == 1 and maturity in (10, 20, 30)),
                     "date_adjudication": date.fromisoformat(r.auction_date),
                     "montant_offert_mds": float(r.offering_amt) / 1e9})
    auction_dates = {}  # maturity -> [(date, cusip)] of real auctions, for fenetre_propre
    for row in real:
        auction_dates.setdefault(row["echeance"], []).append((row["date_adjudication"], row["cusip"]))

    rows = []
    for row in real + [dict(r, type_ligne="placebo") for r in real if r["principal"]]:
        row = dict(row)
        j0 = row["date_adjudication"]
        dj = j0 if row["type_ligne"] == "reelle" else cal.shift(j0, 10)
        dates = {"jm5": cal.shift(dj, -5), "j": dj, "jp5": cal.shift(dj, 5)}
        m = row["echeance"]
        for x, d in dates.items():
            row[f"date_{x}"] = d
            row[f"cmt_{x}"] = _num(cmt[m].get(d, "")) if d in cal else np.nan
            row[f"gsw_{x}"] = _num(gsw.at[d, f"SVENPY{m:02d}"]) if d in gsw.index else np.nan
        row["complet"] = int(not _missing(*[row[f"{s}_{x}"] for s in ("cmt", "gsw") for x in X3]))
        own = (j0, row["cusip"]) if row["type_ligne"] == "reelle" else None
        lo, hi = dates["jm5"], dates["jp5"]
        row["fenetre_propre"] = int(lo is not None and hi is not None and not any(
            lo <= d <= hi and (d, c) != own for d, c in auction_dates[m]))
        row["id_ligne"] = f"{row['cusip']}_{j0}_{row['type_ligne']}"
        row["mois"] = j0.isoformat()[:7]
        rows.append(row)
    df = pd.DataFrame(rows)
    df = df.sort_values(["date_adjudication", "echeance", "type_ligne", "cusip"]).reset_index(drop=True)
    for c in ["date_adjudication", "date_j", "date_jm5", "date_jp5"]:
        df[c] = df[c].map(_iso)
    return df[F04_COLUMNS]


def f04_v(df, rate="cmt"):
    """V in basis points: 100 [2E(J) - E(J-5) - E(J+5)], E = rate - GSW par yield."""
    e = {x: df[f"{rate}_{x}"] - df[f"gsw_{x}"] for x in X3}
    return 100 * (2 * e["j"] - e["jm5"] - e["jp5"])


def f04_sample(df):
    """Principal sample P: real principal reopenings, complete, clean window."""
    return df[(df.type_ligne == "reelle") & (df.principal == 1) & (df.complet == 1) & (df.fenetre_propre == 1)]


def primary_f04(df, schema_ok):
    p = f04_sample(df)
    main = cluster_mean(f04_v(p), p.mois)
    q = df[(df.type_ligne == "placebo") & (df.complet == 1) & (df.fenetre_propre == 1)]
    placebo = cluster_mean(f04_v(q), q.mois)
    t = main["mean"] / main["se"]
    upper = main["mean"] + 1.96 * main["se"]
    return {"schema_ok": schema_ok, "n_adjudications": main["n"], "n_grappes": main["g"],
            "v_moyen_pb": main["mean"], "erreur_type_pb": main["se"], "t_stat": t,
            "borne_sup_95_pb": upper, "marge_zone_grise": min(2 - t, upper - 0.5),
            "n_placebo": placebo["n"], "t_placebo_abs": abs(placebo["mean"] / placebo["se"])}


def f04_event_path(f04, cmt, gsw, cal, width=10):
    """Descriptive (not preregistered): spread E = CMT - GSW par yield from J-width to J+width.

    For each event of F04's sample P with all 2*width+1 spreads present, E(J+k) - E(J-5)
    in basis points. Returns a long DataFrame: k, period ('2010-2021' / '2022-2026'), mois, e_bp."""
    rows = []
    for r in f04_sample(f04).itertuples():
        j, m = date.fromisoformat(r.date_j), r.echeance
        days = [cal.shift(j, k) for k in range(-width, width + 1)]
        if None in days:
            continue
        e = [_num(cmt[m].get(d, "")) - _num(gsw.at[d, f"SVENPY{m:02d}"]) if d in gsw.index else np.nan
             for d in days]
        if _missing(*e):
            continue
        base = e[width - 5]
        period = "2010-2021" if j.year <= 2021 else "2022-2026"
        rows += [{"k": k, "period": period, "mois": r.mois, "e_bp": 100 * (v - base)}
                 for k, v in zip(range(-width, width + 1), e)]
    return pd.DataFrame(rows)


# ============================================================================= F04-bis
FY_START, FY_END = date(2020, 10, 1), date(2021, 9, 30)
F04BIS_COLUMNS = ["id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois",
                  "date_j", "date_jm5", "date_jp5", "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5",
                  "hs_jm5", "hs_j", "hs_jp5", "mc_jm5", "mc_j", "mc_jp5", "dans_exercice", "complet",
                  "fenetre_propre"]


def build_f04bis(f04, mchs):
    """F04-bis analysis file: fiscal-2021 principal reopenings of F04 with HS and MC rates added."""
    base = f04[(f04.type_ligne == "reelle") & (f04.principal == 1)
               & (f04.date_adjudication >= FY_START.isoformat()) & (f04.date_adjudication <= FY_END.isoformat())]
    rows = []
    for r in base.to_dict("records"):
        for x in X3:
            d = date.fromisoformat(r[f"date_{x}"])
            inside = FY_START <= d <= FY_END and d in mchs.index
            for method in ("hs", "mc"):
                col = f"nominal_{method}_cmt_{r['echeance']}yr"
                r[f"{method}_{x}"] = _num(mchs.at[d, col]) if inside else np.nan
        r["dans_exercice"] = int(r["date_jm5"] >= FY_START.isoformat() and r["date_jp5"] <= FY_END.isoformat())
        r["complet"] = int(not _missing(*[r[f"{s}_{x}"] for s in ("cmt", "gsw", "hs", "mc") for x in X3]))
        rows.append(r)
    df = pd.DataFrame(rows).sort_values(["date_adjudication", "echeance"]).reset_index(drop=True)
    return df[F04BIS_COLUMNS]


def f04bis_sample(df):
    return df[(df.dans_exercice == 1) & (df.complet == 1) & (df.fenetre_propre == 1)]


def primary_f04bis(df, schema_ok):
    p = f04bis_sample(df)
    v_hs, v_mc = f04_v(p, "hs"), f04_v(p, "mc")
    d = cluster_mean(v_hs - v_mc, p.mois)
    low, high = interval(d["mean"], d["se"], 2.365)
    mc = cluster_mean(v_mc, p.mois)
    gap = max(abs(p[f"hs_{x}"] - p[f"cmt_{x}"]).max() for x in X3)
    return {"schema_ok": schema_ok, "n_adjudications": d["n"], "n_grappes": d["g"],
            "ecart_max_hs_fred_pb": 100 * float(gap), "d_moyen_pb": d["mean"], "d_erreur_type_pb": d["se"],
            "d_borne_inf_95_pb": low, "d_borne_sup_95_pb": high,
            "marge_zone_grise": min(0.9 - low, high - 0.9),
            "v_hs_moyen_pb": float(v_hs.mean()), "v_mc_moyen_pb": mc["mean"], "v_mc_erreur_type_pb": mc["se"]}


# ============================================================================= J05
GSW_PARAMS = ["BETA0", "BETA1", "BETA2", "BETA3", "TAU1", "TAU2"]
PREFIX_TO_MATURITY = {"9-Year": 10, "19-Year": 20, "29-Year": 30}
J05_COLUMNS = [
    "id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois", "periode",
    "heure_cloture", "format_adjudication", "date_reglement", "date_echeance",
    "taux_coupon_pct", "rdt_limite_pct", "prix_limite", "coupon_couru_api", "coupon_couru_calc",
    "date_gsw_j", "beta0_j", "beta1_j", "beta2_j", "beta3_j", "tau1_j", "tau2_j",
    "date_jm5", "beta0_jm5", "beta1_jm5", "beta2_jm5", "beta3_jm5", "tau1_jm5", "tau2_jm5",
    "prix_fi_jm5", "prix_fi_j", "rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct",
    "rdt_gsw_jm5_pct", "rdt_fi_jm5_pct", "rdt_fi_j_pct", "c_pb", "k_pb", "r_fi_pb",
    "convention_ok", "complet_k", "complet_r", "dans_p"]
J05_YIELDS = ["rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct", "rdt_gsw_jm5_pct",
              "rdt_fi_jm5_pct", "rdt_fi_j_pct"]


def maturity_from_term(term):
    """10, 20 or 30 for a reopening term '9-Year ...', '19-Year ...', '29-Year ...' (else None)."""
    return PREFIX_TO_MATURITY.get(term.split(" ")[0])


def period_j05(d):
    if d <= date(2009, 12, 31):
        return "ancien"
    return "avant" if d <= date(2021, 12, 31) else "apres"


def gsw_calendar_dates(gsw):
    """Dates of the GSW file where all six curve parameters are present (J05's calendar C)."""
    ok = (gsw[GSW_PARAMS] != "").all(axis=1)
    return list(gsw.index[ok])


def fedinvest_eod(day, cusip):
    """END OF DAY price of a CUSIP on a date (NaN if the page is empty or the price absent or zero)."""
    prices = data.fedinvest_prices(day)
    row = prices.get(cusip) if prices else None
    return row["eod"] if row and row["eod"] > 0 else np.nan


def _y(price, coupon, maturity, settle, solver="brent", treasury_exact=False):
    if _missing(price):
        return np.nan
    return bonds.yield_from_price(price, coupon, maturity, settle, treasury_exact, solver)


def j05_yields(r, solver="brent", treasury_exact=False):
    """Columns 16 and 33-38 of a J05 row, computed from its raw columns (section 5.2)."""
    c, mat, s, j = r["taux_coupon_pct"], r["_maturity"], r["_settle"], r["_j"]
    out = {"coupon_couru_calc": bonds.accrued_interest(c, mat, s),
           "rdt_prix_limite_pct": _y(r["prix_limite"], c, mat, s, solver, treasury_exact)}
    pj = [r[f"{p.lower()}_j"] for p in GSW_PARAMS]
    pm = [r[f"{p.lower()}_jm5"] for p in GSW_PARAMS]
    has_j, has_m = r["date_gsw_j"] != "" and not _missing(*pj), r["date_jm5"] != "" and not _missing(*pm)
    out["rdt_gsw_j_terme_pct"] = bonds.gsw_yield(c, mat, j, pj, s, treasury_exact) if has_j else np.nan
    late = r["periode"] != "ancien"
    out["rdt_gsw_j_pct"] = bonds.gsw_yield(c, mat, j, pj, None, treasury_exact) if has_j and late else np.nan
    jm5 = date.fromisoformat(r["date_jm5"]) if r["date_jm5"] else None
    out["rdt_gsw_jm5_pct"] = bonds.gsw_yield(c, mat, jm5, pm, None, treasury_exact) if has_m else np.nan
    out["rdt_fi_jm5_pct"] = _y(r["prix_fi_jm5"], c, mat, jm5, solver, treasury_exact) if jm5 else np.nan
    out["rdt_fi_j_pct"] = _y(r["prix_fi_j"], c, mat, j, solver, treasury_exact)
    return out


def build_j05(auctions, gsw, cal):
    """J05 analysis file: one row per 10/20/30-year nominal reopening, 1991-2026."""
    a = auctions[(auctions.reopening == "Yes") & (auctions.inflation_index_security != "Yes")
                 & (auctions.floating_rate != "Yes")].copy()
    a["echeance"] = a.security_term.map(maturity_from_term)
    a = a[a.echeance.notna()]
    a = a[a.first_int_period == "Normal"]  # none is dropped in practice
    rows = []
    for r in a.to_dict("records"):
        j = date.fromisoformat(r["auction_date"])
        per = period_j05(j)
        row = {"id_ligne": f"{r['cusip']}_{j}", "cusip": r["cusip"], "terme_api": r["security_term"],
               "echeance": int(r["echeance"]), "date_adjudication": j.isoformat(), "mois": j.isoformat()[:7],
               "periode": per, "heure_cloture": "" if r["closing_time_comp"] == "null" else r["closing_time_comp"],
               "format_adjudication": r["auction_format"], "date_reglement": r["issue_date"],
               "date_echeance": r["maturity_date"], "taux_coupon_pct": _num(r["int_rate"]),
               "rdt_limite_pct": _num(r["high_yield"]), "prix_limite": _num(r["high_price"]),
               "coupon_couru_api": _num(r["accrued_int_per1000"]) / 10,
               "_j": j, "_settle": date.fromisoformat(r["issue_date"]),
               "_maturity": date.fromisoformat(r["maturity_date"])}
        row["date_gsw_j"] = j.isoformat() if j in cal else ""
        jm5 = cal.shift(j, -5) if per != "ancien" else None
        row["date_jm5"] = _iso(jm5)
        for p in GSW_PARAMS:
            row[f"{p.lower()}_j"] = _num(gsw.at[j, p]) if j in cal else np.nan
            row[f"{p.lower()}_jm5"] = _num(gsw.at[jm5, p]) if jm5 else np.nan
        row["prix_fi_jm5"] = fedinvest_eod(jm5, r["cusip"]) if jm5 else np.nan
        row["prix_fi_j"] = fedinvest_eod(j, r["cusip"]) if per != "ancien" else np.nan
        row.update(j05_yields(row))
        rows.append(row)
    df = pd.DataFrame(rows)
    df["c_pb"] = 100 * (df.rdt_limite_pct - df.rdt_gsw_j_terme_pct)
    df["k_pb"] = df.c_pb - 100 * (df.rdt_fi_jm5_pct - df.rdt_gsw_jm5_pct)
    df["r_fi_pb"] = 100 * ((df.rdt_fi_j_pct - df.rdt_gsw_j_pct) - (df.rdt_fi_jm5_pct - df.rdt_gsw_jm5_pct))
    df["convention_ok"] = (((df.rdt_prix_limite_pct - df.rdt_limite_pct).abs() <= 0.001)
                           & ((df.coupon_couru_calc - df.coupon_couru_api).abs() <= 0.001)).astype(int)
    k_inputs = ["rdt_limite_pct", "prix_limite"] + [f"{p.lower()}_{x}" for x in ("j", "jm5") for p in GSW_PARAMS]
    df["complet_k"] = (df[k_inputs + ["prix_fi_jm5"]].notna().all(axis=1)
                       & (df.date_jm5 != "") & (df.date_gsw_j == df.date_adjudication)).astype(int)
    df["complet_r"] = ((df.complet_k == 1) & df.prix_fi_j.notna()).astype(int)
    df["dans_p"] = (df.periode.isin(["avant", "apres"]) & (df.complet_k == 1) & (df.convention_ok == 1)).astype(int)
    df = df.sort_values(["date_adjudication", "echeance"]).reset_index(drop=True)
    return df


def j05_regression(p, column):
    """OLS of `column` on [after, d10, d20, d30] (no constant), clustered by month: (delta, se)."""
    X = np.column_stack([(p.periode == "apres").astype(float)] +
                        [(p.echeance == m).astype(float) for m in (10, 20, 30) if (p.echeance == m).any()])
    b, V = ols_cluster(p[column], X, p.mois)
    return -b[0], math.sqrt(V[0, 0])


def primary_j05(df, schema_ok):
    late = df[df.periode.isin(["avant", "apres"])]
    # second, independent computation of columns 33-38 (bisection instead of Brent)
    gap = 0.0
    for r in late.to_dict("records"):
        again = j05_yields(r, solver="bisect")
        for c in J05_YIELDS:
            if not _missing(again[c], r[c]):
                gap = max(gap, abs(again[c] - r[c]))
    failures = int(((late.convention_ok == 0) & late.rdt_limite_pct.notna() & late.prix_limite.notna()).sum())
    p = df[df.dans_p == 1]
    delta, se = j05_regression(p, "k_pb")
    low, high = interval(delta, se, 1.645)
    before, after = p[p.periode == "avant"], p[p.periode == "apres"]
    return {"schema_ok": schema_ok, "n_avant": len(before), "n_apres": len(after),
            "n_grappes_avant": before.mois.nunique(), "n_grappes_apres": after.mois.nunique(),
            "n_echec_convention": failures, "ecart_max_rdt_pb": 100 * gap,
            "k_moyen_avant_pb": float(before.k_pb.mean()), "k_moyen_apres_pb": float(after.k_pb.mean()),
            "delta_k_pb": delta, "erreur_type_pb": se, "borne_inf_90_pb": low, "borne_sup_90_pb": high,
            "marge_zone_grise": min(-low, high - 0.5)}


# ============================================================================= K11
K11_FAMILIES = {"10-Year": 10, "20-Year": 20, "30-Year": 30, "29-Year 9-Month": 30, "30-Year 3-Month": 30}
K11_OFF_CYCLE = {date(2019, 6, 21)}  # the off-calendar operation excluded by the preregistration
TITLES = ["a", "t1", "t2", "t3"]
K11_COLUMNS = (
    "id_ligne cusip terme_api echeance date_adjudication mois annee periode heure_cloture "
    "date_emission_origine date_reglement date_echeance taux_coupon_pct date_jm5 date_jp5 "
    "ecart_jm5_jours ecart_jp5_jours cusip_premier_ancien echeance_pa coupon_pa_pct "
    "cusip_t1 cusip_t2 cusip_t3 rang_t1 rang_t2 rang_t3 echeance_t1 echeance_t2 echeance_t3 "
    "coupon_t1_pct coupon_t2_pct coupon_t3_pct ecart_mois_t1 ecart_mois_t2 ecart_mois_t3 "
    "n_temoins_figes n_candidats_absents prix_a_jm5 prix_a_j prix_a_jp5 "
    "prix_t1_jm5 prix_t1_j prix_t1_jp5 prix_t2_jm5 prix_t2_j prix_t2_jp5 prix_t3_jm5 prix_t3_j prix_t3_jp5 "
    "prix_pa_jm5 prix_pa_j prix_pa_jp5 identite_fi_ok rdt_limite_pct prix_limite "
    "rdt_a_jm5_pct rdt_a_j_pct rdt_a_jp5_pct "
    "rdt_t1_jm5_pct rdt_t1_j_pct rdt_t1_jp5_pct rdt_t2_jm5_pct rdt_t2_j_pct rdt_t2_jp5_pct "
    "rdt_t3_jm5_pct rdt_t3_j_pct rdt_t3_jp5_pct rdt_pa_jm5_pct rdt_pa_j_pct rdt_pa_jp5_pct "
    "e_jm5_pb e_j_pb e_jp5_pb v_pb montee_pb detente_pb v_pa_pb p_carte_pb motif_exclusion complet dans_p"
).split()


def month_gap(later, earlier):
    return 12 * (later.year - earlier.year) + (later.month - earlier.month)


def k11_securities(auctions):
    """First auction of every nominal CUSIP: family, first auction date, issue date, coupon, maturity."""
    nominal = auctions[(auctions.inflation_index_security != "Yes") & (auctions.floating_rate != "Yes")]
    first = nominal[nominal.reopening == "No"].sort_values("auction_date").drop_duplicates("cusip")
    return {r.cusip: {"family": K11_FAMILIES.get(r.original_security_term),
                      "first_auction": date.fromisoformat(r.auction_date),
                      "issue": date.fromisoformat(r.issue_date), "coupon": float(r.int_rate),
                      "maturity": date.fromisoformat(r.maturity_date)} for r in first.itertuples()}


def k11_candidates(cusip, j, jm5, jp5, securities, auction_dates):
    """Ranked family members (rank 0 = the reopened security) and the eligible controls (rank >= 2)."""
    me = securities[cusip]
    members = [c for c, s in securities.items() if s["family"] == me["family"] and s["first_auction"] <= j
               and s["maturity"] > jp5]
    members.sort(key=lambda c: (securities[c]["maturity"], securities[c]["first_auction"], c), reverse=True)
    eligible = [(rank, c) for rank, c in enumerate(members) if rank >= 2
                and month_gap(me["maturity"], securities[c]["maturity"]) <= 18
                and not any(jm5 <= d <= jp5 for d in auction_dates.get(c, ()))]
    return members, eligible


def _eod_at(prices, cusip):
    row = prices.get(cusip) if prices else None
    return row["eod"] if row and row["eod"] > 0 else np.nan


def _identity_ok(prices, cusip, coupon, maturity):
    row = prices.get(cusip) if prices else None
    return bool(row) and abs(row["rate"] - coupon) < 1e-9 and row["maturity"] == maturity


def build_k11(auctions, cal):
    """K11 analysis file: one row per 10/20/30-year nominal reopening, 2010-2026."""
    securities = k11_securities(auctions)
    auction_dates = {}
    for r in auctions.itertuples():
        auction_dates.setdefault(r.cusip, []).append(date.fromisoformat(r.auction_date))
    nominal = auctions[(auctions.inflation_index_security != "Yes") & (auctions.floating_rate != "Yes")]
    studied = nominal[(nominal.reopening == "Yes") & (nominal.auction_date >= "2010-01-01")
                      & (nominal.auction_date <= "2026-10-31")].copy()
    studied["echeance"] = studied.security_term.map(maturity_from_term)
    studied = studied[studied.echeance.notna()]
    rows = []
    for r in studied.to_dict("records"):
        j = date.fromisoformat(r["auction_date"])
        jm5, jp5 = cal.shift(j, -5), cal.shift(j, 5)
        a = securities[r["cusip"]]
        row = {c: "" for c in K11_COLUMNS}
        row.update({"id_ligne": f"{r['cusip']}_{j}", "cusip": r["cusip"], "terme_api": r["security_term"],
                    "echeance": int(r["echeance"]), "date_adjudication": j.isoformat(), "mois": j.isoformat()[:7],
                    "annee": j.year, "periode": "avant" if j.year <= 2021 else "apres",
                    "heure_cloture": r["closing_time_comp"], "date_emission_origine": a["issue"].isoformat(),
                    "date_reglement": r["issue_date"], "date_echeance": r["maturity_date"],
                    "taux_coupon_pct": float(r["int_rate"]), "date_jm5": _iso(jm5), "date_jp5": _iso(jp5),
                    "ecart_jm5_jours": (j - jm5).days, "ecart_jp5_jours": (jp5 - j).days,
                    "identite_fi_ok": 0, "rdt_limite_pct": _num(r["high_yield"]),
                    "prix_limite": _num(r["high_price"]), "complet": 0, "dans_p": 0})
        members, eligible = k11_candidates(r["cusip"], j, jm5, jp5, securities, auction_dates)
        if j in K11_OFF_CYCLE:
            row["motif_exclusion"] = "hors_calendrier"
        elif len(eligible) < 3:
            row["motif_exclusion"] = "temoins_insuffisants"
        elif a["issue"] > jm5:
            row["motif_exclusion"] = "titre_non_emis_a_jm5"
        else:
            _k11_prices(row, r, members, eligible, securities, {"jm5": jm5, "j": j, "jp5": jp5})
        rows.append(row)
    df = pd.DataFrame(rows, columns=K11_COLUMNS)
    return df.sort_values(["date_adjudication", "echeance"]).reset_index(drop=True)


def _k11_prices(row, r, members, eligible, securities, dates):
    """Fill controls, prices, yields, E, V and the exclusion flags of one K11 row."""
    pages = {x: data.fedinvest_prices(d) for x, d in dates.items()}
    coupon, maturity = row["taux_coupon_pct"], date.fromisoformat(r["maturity_date"])
    titles = {"a": (r["cusip"], coupon, maturity)}
    if len(members) > 1:
        pa = members[1]
        titles["pa"] = (pa, securities[pa]["coupon"], securities[pa]["maturity"])
        row.update({"cusip_premier_ancien": pa, "echeance_pa": securities[pa]["maturity"].isoformat(),
                    "coupon_pa_pct": securities[pa]["coupon"]})
    frozen = absent = 0
    controls = []
    for rank, c in eligible:
        if len(controls) == 3:
            break
        p = [_eod_at(pages[x], c) for x in X3]
        if _missing(*p):
            absent += 1
        elif p[1] == p[0] or p[1] == p[2]:
            frozen += 1
        else:
            controls.append((rank, c))
    for k, (rank, c) in enumerate(controls, 1):
        s = securities[c]
        titles[f"t{k}"] = (c, s["coupon"], s["maturity"])
        row.update({f"cusip_t{k}": c, f"rang_t{k}": rank, f"echeance_t{k}": s["maturity"].isoformat(),
                    f"coupon_t{k}_pct": s["coupon"], f"ecart_mois_t{k}": month_gap(maturity, s["maturity"])})
    row["n_temoins_figes"], row["n_candidats_absents"] = frozen, absent
    y = {}
    for t, (c, cpn, mat) in titles.items():
        for x in X3:
            price = _eod_at(pages[x], c)
            row[f"prix_{t}_{x}"] = price
            y[(t, x)] = row[f"rdt_{t}_{x}_pct"] = _y(price, cpn, mat, dates[x])
    k11_derived(row, y)
    row["identite_fi_ok"] = int(len(controls) == 3 and all(
        _identity_ok(pages[x], titles[t][0], titles[t][1], titles[t][2]) for t in TITLES for x in X3))
    prices_a = [row[f"prix_a_{x}"] for x in X3]
    twelve = [row[f"prix_{t}_{x}"] for t in TITLES for x in X3] if len(controls) == 3 else [np.nan]
    row["complet"] = int(not _missing(*twelve) and row["identite_fi_ok"] == 1)
    if any(pages[x] is None for x in X3) or _missing(*prices_a) or len(controls) < 3:
        row["motif_exclusion"] = "prix_manquant"
    elif prices_a[1] == prices_a[0] or prices_a[1] == prices_a[2]:
        row["motif_exclusion"] = "prix_fige"
    row["dans_p"] = int(row["motif_exclusion"] == "" and row["complet"] == 1)


def k11_derived(row, y):
    """Columns 71-78 from the yields y[(title, date)] (NaN propagates)."""
    def e(t, x):
        vals = [y.get((t, x), np.nan)] + [y.get((f"t{k}", x), np.nan) for k in (1, 2, 3)]
        return np.nan if _missing(*vals) else 100 * (vals[0] - sum(vals[1:]) / 3)
    ea = {x: e("a", x) for x in X3}
    epa = {x: e("pa", x) for x in X3}
    row.update({"e_jm5_pb": ea["jm5"], "e_j_pb": ea["j"], "e_jp5_pb": ea["jp5"],
                "v_pb": 2 * ea["j"] - ea["jm5"] - ea["jp5"], "montee_pb": ea["j"] - ea["jm5"],
                "detente_pb": ea["j"] - ea["jp5"], "v_pa_pb": 2 * epa["j"] - epa["jm5"] - epa["jp5"]})
    legs = [y.get((f"t{k}", "j"), np.nan) - y.get((f"t{k}", "jm5"), np.nan) for k in (1, 2, 3)]
    row["p_carte_pb"] = 100 * ((row["rdt_limite_pct"] - y.get(("a", "jm5"), np.nan)) - sum(legs) / 3)


def primary_k11(df, schema_ok):
    p = df[df.dans_p == 1].copy()
    gap = 0.0  # second computation of the 12 yields (bisection) against the file
    for r in p.to_dict("records"):
        mats = {"a": r["date_echeance"], "t1": r["echeance_t1"], "t2": r["echeance_t2"], "t3": r["echeance_t3"]}
        cpns = {"a": r["taux_coupon_pct"], "t1": r["coupon_t1_pct"], "t2": r["coupon_t2_pct"], "t3": r["coupon_t3_pct"]}
        days = {"jm5": r["date_jm5"], "j": r["date_adjudication"], "jp5": r["date_jp5"]}
        for t in TITLES:
            for x in X3:
                again = bonds.yield_from_price(float(r[f"prix_{t}_{x}"]), float(cpns[t]), date.fromisoformat(mats[t]),
                                               date.fromisoformat(days[x]), solver="bisect")
                gap = max(gap, abs(again - float(r[f"rdt_{t}_{x}_pct"])))
    p["v"] = p.v_pb.astype(float)
    p["ech"] = p.echeance.astype(int)
    after = p[p.periode == "apres"]
    before_1030 = p[(p.periode == "avant") & p.ech.isin([10, 30])]
    after_1030 = after[after.ech.isin([10, 30])]
    m = cluster_mean(after.v, after.mois)
    low, high = interval(m["mean"], m["se"], 1.645)
    no23 = float(after[after.annee != 2023].v.mean())
    no30 = float(after[after.ech != 30].v.mean())
    robust = min(no23, no30)
    b = cluster_mean(before_1030.v, before_1030.mois)
    a = cluster_mean(after_1030.v, after_1030.mois)
    drop = b["mean"] - a["mean"]
    se_drop = math.sqrt(b["se"] ** 2 + a["se"] ** 2)
    drop_low = drop - 1.645 * se_drop
    return {"schema_ok": schema_ok, "n_apres": m["n"], "n_grappes_apres": m["g"],
            "n_avant_1030": b["n"], "n_grappes_avant_1030": b["g"],
            "n_temoins_figes": int(p.n_temoins_figes.astype(int).sum()), "ecart_max_rdt_pb": 100 * gap,
            "v_moyen_apres_pb": m["mean"], "erreur_type_apres_pb": m["se"],
            "borne_inf_90_apres_pb": low, "borne_sup_90_apres_pb": high, "marge_zone_grise": min(-low, high - 0.5),
            "v_moyen_apres_sans_2023_pb": no23, "v_moyen_apres_sans_30_pb": no30, "min_robustesse_pb": robust,
            "alerte_robustesse": int(low > 0 and high >= 0.5 and robust <= 0),
            "v_moyen_avant_1030_pb": b["mean"], "erreur_type_avant_1030_pb": b["se"],
            "v_moyen_apres_1030_pb": a["mean"], "erreur_type_apres_1030_pb": a["se"],
            "baisse_1030_pb": drop, "erreur_type_baisse_pb": se_drop, "borne_inf_90_baisse_pb": drop_low,
            "alerte_instrument": int(high < 0.5 and drop_low <= 0)}
