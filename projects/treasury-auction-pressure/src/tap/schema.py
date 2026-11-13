"""Schema checks of each preregistration, applied literally to our own analysis files.

Each function returns a dict {check number: [row ids that fail]}; schema_ok = 1 when the
dict is empty. Checks are written as in the sealed texts, including the two that turned
out to be mis-specified (J05 check 5, K11 check 5): they fail here exactly as they failed
for the experimenter and the verifier, and that is reported, not corrected.
"""
from datetime import date

import numpy as np
import pandas as pd

from . import measures
from .calendar import Calendar, k11_calendar

X3 = measures.X3


def _record(failures, number, df, ok_mask):
    """Add the ids of rows where ok_mask is False under check `number`."""
    bad = list(df.loc[~np.asarray(ok_mask, dtype=bool), "id_ligne"])
    if bad:
        failures.setdefault(number, []).extend(bad)


def _inside(frame, lo, hi):
    """Element-wise lo <= value <= hi for a DataFrame."""
    return (frame >= lo) & (frame <= hi)


def _flag(failures, number, ok, what):
    if not ok:
        failures.setdefault(number, []).append(what)


def check_f04(df):
    f = {}
    _flag(f, 1, list(df.columns) == measures.F04_COLUMNS, "columns")
    _flag(f, 2, df.id_ligne.is_unique, "id_ligne not unique")
    _record(f, 2, df, df.type_ligne.isin(["reelle", "placebo"]) & df.echeance.isin([2, 3, 5, 7, 10, 20, 30])
            & df[["reouverture", "principal", "complet", "fenetre_propre"]].isin([0, 1]).all(axis=1))
    real, placebo = df.type_ligne == "reelle", df.type_ligne == "placebo"
    _record(f, 3, df, (df.date_jm5 != "") & (df.date_jm5 < df.date_j) & (df.date_j < df.date_jp5)
            & (~real | (df.date_j == df.date_adjudication)) & (~placebo | (df.date_j > df.date_adjudication)))
    _record(f, 4, df, df.date_adjudication.between("2010-01-01", "2026-09-30")
            & (df.mois == df.date_adjudication.str[:7]) & (df.montant_offert_mds > 0))
    expected = ((df.reouverture == 1) & df.echeance.isin([10, 20, 30])).astype(int)
    keys = df[real].groupby(["cusip", "date_adjudication"]).size()
    matched = [keys.get((c, d), 0) == 1 for c, d in zip(df.cusip, df.date_adjudication)]
    _record(f, 5, df, (df.principal == expected) & (~placebo | ((df.principal == 1) & np.array(matched))))
    rates = df[[f"{s}_{x}" for s in ("cmt", "gsw") for x in X3]]
    _record(f, 6, df, df.complet == rates.notna().all(axis=1).astype(int))
    in_range = (rates.isna() | ((rates >= -1) & (rates <= 20))).all(axis=1)
    paired = pd.concat([(df[f"cmt_{x}"] - df[f"gsw_{x}"]).abs().fillna(0) <= 1 for x in X3], axis=1).all(axis=1)
    _record(f, 7, df, in_range & paired)
    n = int((real & (df.principal == 1)).sum())
    _flag(f, 8, 300 <= n <= 330, f"{n} principal real rows")
    return f


def check_f04bis(df):
    f = {}
    _flag(f, 1, list(df.columns) == measures.F04BIS_COLUMNS, "columns")
    _flag(f, 2, df.id_ligne.is_unique, "id_ligne not unique")
    _record(f, 2, df, df.echeance.isin([10, 20, 30])
            & df[["dans_exercice", "complet", "fenetre_propre"]].isin([0, 1]).all(axis=1))
    _record(f, 3, df, (df.date_jm5 < df.date_j) & (df.date_j < df.date_jp5) & (df.date_j == df.date_adjudication)
            & df.date_adjudication.between("2020-10-01", "2021-09-30") & (df.mois == df.date_adjudication.str[:7]))
    inside = ((df.date_jm5 >= "2020-10-01") & (df.date_jp5 <= "2021-09-30")).astype(int)
    _record(f, 4, df, df.dans_exercice == inside)
    rates = df[[f"{s}_{x}" for s in ("cmt", "gsw", "hs", "mc") for x in X3]]
    _record(f, 5, df, df.complet == rates.notna().all(axis=1).astype(int))
    ok6 = (rates.isna() | ((rates >= -1) & (rates <= 20))).all(axis=1)
    for x in X3:
        ok6 &= (df[f"cmt_{x}"] - df[f"gsw_{x}"]).abs().fillna(0) <= 1
    _record(f, 6, df, ok6)
    hs_mc = pd.concat([(df[f"hs_{x}"] - df[f"mc_{x}"]).abs() for x in X3], axis=1)
    _record(f, 7, df, (hs_mc.isna() | (hs_mc <= 0.25)).all(axis=1))
    _flag(f, 7, bool((hs_mc > 0).any().any()), "hs equals mc everywhere")
    hs_fred = pd.concat([(df[f"hs_{x}"] - df[f"cmt_{x}"]).abs() for x in X3], axis=1)
    _record(f, 8, df, (hs_fred.isna() | (hs_fred <= 0.0051)).all(axis=1))
    _flag(f, 9, len(df) == 24 and 20 <= int(df.dans_exercice.sum()) <= 24, "row counts")
    return f


def check_j05(df):
    f = {}
    _flag(f, 1, list(df[measures.J05_COLUMNS].columns) == measures.J05_COLUMNS, "columns")
    expected_maturity = df.terme_api.map(measures.maturity_from_term)
    _flag(f, 2, df.id_ligne.is_unique, "id_ligne not unique")
    _record(f, 2, df, (df.id_ligne == df.cusip + "_" + df.date_adjudication) & (df.cusip.str.len() == 9)
            & (df.echeance == expected_maturity) & (df.mois == df.date_adjudication.str[:7])
            & (df.periode == df.date_adjudication.map(lambda s: measures.period_j05(date.fromisoformat(s))))
            & df[["convention_ok", "complet_k", "complet_r", "dans_p"]].isin([0, 1]).all(axis=1))
    _record(f, 3, df, df.date_adjudication.between("1991-01-01", "2026-10-31"))
    counts = df.periode.value_counts()
    for per, lo, hi in [("ancien", 60, 70), ("avant", 200, 214), ("apres", 112, 120)]:
        _flag(f, 3, lo <= counts.get(per, 0) <= hi, f"{per}: {counts.get(per, 0)} rows")
    delay = (pd.to_datetime(df.date_reglement) - pd.to_datetime(df.date_adjudication)).dt.days
    _record(f, 4, df, (delay > 0) & (delay <= 20) & (df.date_echeance > df.date_reglement))
    # check 5: no look-ahead; J-5 is 7 to 9 calendar days before J and a weekday
    jm5 = pd.to_datetime(df.date_jm5.replace("", None))
    gap = (pd.to_datetime(df.date_adjudication) - jm5).dt.days
    has_jm5 = df.date_jm5 != ""
    _record(f, 5, df, ((df.date_gsw_j == "") | (df.date_gsw_j == df.date_adjudication))
            & (~has_jm5 | (gap.between(7, 9) & (jm5.dt.weekday < 5))))
    yields = df[["rdt_limite_pct"] + measures.J05_YIELDS]
    prices = df[["prix_limite", "prix_fi_jm5", "prix_fi_j"]]
    taus = df[["tau1_j", "tau2_j", "tau1_jm5", "tau2_jm5"]]
    _record(f, 6, df, (yields.isna() | _inside(yields, -1, 20)).all(axis=1)
            & (prices.isna() | _inside(prices, 50, 200)).all(axis=1)
            & (taus.isna() | (taus > 0)).all(axis=1) & df.taux_coupon_pct.between(0, 15))
    a = (df.rdt_fi_jm5_pct - df.rdt_gsw_jm5_pct).abs()
    b = (df.rdt_fi_j_pct - df.rdt_limite_pct).abs()
    _record(f, 7, df, (a.isna() | (a <= 0.60)) & (b.isna() | (b <= 0.40)))
    c = 100 * (df.rdt_limite_pct - df.rdt_gsw_j_terme_pct)
    k = c - 100 * (df.rdt_fi_jm5_pct - df.rdt_gsw_jm5_pct)
    same = [(df[col] - val).abs().fillna(0) <= 1e-6 for col, val in (("c_pb", c), ("k_pb", k))]
    _record(f, 8, df, same[0] & same[1] & (df.c_pb.isna() == c.isna()) & (df.k_pb.isna() == k.isna()))
    return f


def check_k11(df, auctions):
    """K11 checks 1-11 (check 5 includes the reconstruction of the control ranking on D1)."""
    f = {}
    _flag(f, 1, list(df.columns) == measures.K11_COLUMNS, "columns")
    _flag(f, 2, df.id_ligne.is_unique, "id_ligne not unique")
    years = df.date_adjudication.str[:4].astype(int)
    _record(f, 2, df, (df.id_ligne == df.cusip + "_" + df.date_adjudication) & (df.cusip.str.len() == 9)
            & (df.echeance == df.terme_api.map(measures.maturity_from_term)) & (df.mois == df.date_adjudication.str[:7])
            & (df.annee == years) & (df.periode == np.where(years <= 2021, "avant", "apres"))
            & df[["identite_fi_ok", "complet", "dans_p"]].isin([0, 1]).all(axis=1))
    counts = df.groupby(["periode", "echeance"]).size().to_dict()
    expected = {("avant", 10): 97, ("avant", 20): 14, ("avant", 30): 96,
                ("apres", 10): 39, ("apres", 20): 39, ("apres", 30): 39}
    _flag(f, 3, len(df) == 324 and counts == expected, f"counts {counts}")
    by_reason = {m: set(df.id_ligne[df.motif_exclusion == m]) for m in
                 ("hors_calendrier", "temoins_insuffisants", "titre_non_emis_a_jm5")}
    twenty = df[(df.echeance == 20) & df.date_adjudication.between("2020-06-17", "2021-04-21")]
    _flag(f, 3, by_reason["hors_calendrier"] == {"9128286T2_2019-06-21"}, "hors_calendrier")
    _flag(f, 3, by_reason["temoins_insuffisants"] == set(twenty.id_ligne) and len(twenty) == 8, "temoins_insuffisants")
    _flag(f, 3, by_reason["titre_non_emis_a_jm5"] == {"912810TC2_2021-12-02"}, "titre_non_emis_a_jm5")
    # 4. calendar, exact rank in C
    cal = Calendar(k11_calendar())
    for r in df.itertuples():
        j = date.fromisoformat(r.date_adjudication)
        ok = (j in cal and r.date_jm5 == cal.shift(j, -5).isoformat() and r.date_jp5 == cal.shift(j, 5).isoformat()
              and r.ecart_jm5_jours == (j - date.fromisoformat(r.date_jm5)).days
              and r.ecart_jp5_jours == (date.fromisoformat(r.date_jp5) - j).days
              and 7 <= r.ecart_jm5_jours <= 11 and 7 <= r.ecart_jp5_jours <= 11)
        _flag(f, 4, ok, r.id_ligne)
    # 5. controls of rows not excluded by metadata
    securities = measures.k11_securities(auctions)
    auction_dates = {}
    for a in auctions.itertuples():
        auction_dates.setdefault(a.cusip, []).append(date.fromisoformat(a.auction_date))
    kept = df[~df.motif_exclusion.isin(list(by_reason))]
    for r in kept.to_dict("records"):
        controls = [r[f"cusip_t{k}"] for k in (1, 2, 3)]
        ok = "" not in controls and len(set(controls)) == 3 and r["cusip"] not in controls \
            and r["cusip_premier_ancien"] not in controls
        if ok:
            ranks = [int(r[f"rang_t{k}"]) for k in (1, 2, 3)]
            mats = [date.fromisoformat(r[f"echeance_t{k}"]) for k in (1, 2, 3)]
            gaps = [measures.month_gap(date.fromisoformat(r["date_echeance"]), m) for m in mats]
            j = date.fromisoformat(r["date_adjudication"])
            members, eligible = measures.k11_candidates(r["cusip"], j, date.fromisoformat(r["date_jm5"]),
                                                        date.fromisoformat(r["date_jp5"]), securities, auction_dates)
            allowed = [c for _, c in eligible][:3 + int(r["n_temoins_figes"]) + int(r["n_candidats_absents"])]
            ok = (ranks[0] < ranks[1] < ranks[2] and ranks[0] >= 2 and mats[0] >= mats[1] >= mats[2]
                  and mats[0] < date.fromisoformat(r["date_echeance"])
                  and gaps == [int(r[f"ecart_mois_t{k}"]) for k in (1, 2, 3)] and all(1 <= g <= 18 for g in gaps)
                  and members[1] == r["cusip_premier_ancien"]
                  and [c for c in allowed if c in controls] == controls)
        _flag(f, 5, ok, r["id_ligne"])
    p = df[df.dans_p == 1]
    _record(f, 6, p, p.date_emission_origine <= p.date_jm5)
    price_cols = [f"prix_{t}_{x}" for t in measures.TITLES for x in X3]
    yield_cols = [f"rdt_{t}_{x}_pct" for t in measures.TITLES for x in X3]
    coupons = ["taux_coupon_pct", "coupon_t1_pct", "coupon_t2_pct", "coupon_t3_pct"]
    def num(cols, frame=p):
        return frame[cols].apply(pd.to_numeric, errors="coerce")

    _record(f, 7, p, _inside(num(price_cols), 30, 200).all(axis=1) & _inside(num(yield_cols), -1, 20).all(axis=1)
            & _inside(num(coupons), 0, 15).all(axis=1))
    ok8 = pd.Series(True, index=p.index)
    for x in X3:
        for k in (1, 2, 3):
            ok8 &= (num([f"rdt_t{k}_{x}_pct"]).iloc[:, 0] - num([f"rdt_a_{x}_pct"]).iloc[:, 0]).abs() <= 0.60
    _record(f, 8, p, ok8)
    ok9 = pd.Series(True, index=p.index)
    for t in measures.TITLES:
        pr = num([f"prix_{t}_{x}" for x in X3])
        ok9 &= (pr.iloc[:, 1] != pr.iloc[:, 0]) & (pr.iloc[:, 1] != pr.iloc[:, 2])
    _record(f, 9, p, ok9)
    _record(f, 10, p, p.identite_fi_ok == 1)
    complete = num(price_cols, df).gt(0).all(axis=1) & (df.identite_fi_ok == 1)
    e = num(["e_jm5_pb", "e_j_pb", "e_jp5_pb", "v_pb"], df)
    v_ok = (e.v_pb - (2 * e.e_j_pb - e.e_jm5_pb - e.e_jp5_pb)).abs().fillna(0) <= 1e-6
    _record(f, 11, df, (df.complet == complete.astype(int)) & v_ok & (e.v_pb.isna() == e.e_j_pb.isna())
            & (df.dans_p == ((df.motif_exclusion == "") & (df.complet == 1)).astype(int)))
    return f
