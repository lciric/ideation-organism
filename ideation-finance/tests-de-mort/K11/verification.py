"""K11 - verification independante, ecrite a partir du seul texte de preenregistrement.md.

Lit uniquement K11_analyse.csv. Ecrit verification.json (champs_verification, plats)
et verification_detail.json (controles de schema detailles + descriptif) pour le rapport.
"""
import json
import math
import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ICI = Path(__file__).resolve().parent
CSV = ICI / "K11_analyse.csv"

COLONNES = (
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
assert len(COLONNES) == 81

X = ["jm5", "j", "jp5"]
TITRES = ["a", "t1", "t2", "t3"]
METADONNEES = {"hors_calendrier", "temoins_insuffisants", "titre_non_emis_a_jm5"}


# ---------------------------------------------------------------- calendrier C (4.3)
def nieme_jour(an, mois, jour_sem, n):
    d = date(an, mois, 1)
    while d.weekday() != jour_sem:
        d += timedelta(days=1)
    return d + timedelta(days=7 * (n - 1))


def dernier_jour(an, mois, jour_sem):
    d = date(an, mois + 1, 1) - timedelta(days=1) if mois < 12 else date(an, 12, 31)
    while d.weekday() != jour_sem:
        d -= timedelta(days=1)
    return d


def observe(d):
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def feries(an):
    f = [
        observe(date(an, 1, 1)),
        nieme_jour(an, 1, 0, 3),
        nieme_jour(an, 2, 0, 3),
        dernier_jour(an, 5, 0),
        observe(date(an, 7, 4)),
        nieme_jour(an, 9, 0, 1),
        nieme_jour(an, 10, 0, 2),
        observe(date(an, 11, 11)),
        nieme_jour(an, 11, 3, 4),
        observe(date(an, 12, 25)),
    ]
    if an >= 2021:
        f.append(observe(date(an, 6, 19)))
    return f


def calendrier():
    exclus = set()
    for an in range(2009, 2028):  # 2028 : 1er janvier 2028 samedi -> 2027-12-31 (hors plage)
        exclus.update(feries(an))
    exclus.update({date(2012, 10, 30), date(2018, 12, 5)})
    jours = []
    d = date(2009, 6, 1)
    while d <= date(2026, 12, 31):
        if d.weekday() < 5 and d not in exclus:
            jours.append(d)
        d += timedelta(days=1)
    return jours


C = calendrier()
RANG = {d: i for i, d in enumerate(C)}


# ---------------------------------------------------------------- rendement (5.2)
def recule_mois(m, k):
    tot = m.year * 12 + (m.month - 1) - k
    return date(tot // 12, tot % 12 + 1, m.day)


def rendement(prix, coupon, echeance, d):
    """Y(P, d) : 31 CFR 356 annexe B, dates de coupon nominales (M - 6k mois)."""
    dates = []
    k = 0
    while True:
        t = recule_mois(echeance, 6 * k)
        dates.append(t)
        if t <= d:
            break
        k += 1
    L = dates[-1]
    futures = sorted(dates[:-1])  # T_k > d
    N = futures[0]
    n = len(futures)
    frac = (N - d).days / (N - L).days
    ai = (coupon / 2.0) * (d - L).days / (N - L).days
    sale = prix + ai
    flux = [coupon / 2.0] * (n - 1) + [coupon / 2.0 + 100.0]
    expo = np.array([(j - 1) + frac for j in range(1, n + 1)], dtype=float)
    flux = np.array(flux)

    def f(y):
        return float(np.sum(flux * (1.0 + y / 200.0) ** (-expo))) - sale

    lo, hi = -5.0, 50.0
    flo, fhi = f(lo), f(hi)
    assert flo > 0 > fhi, (prix, coupon, echeance, d)
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


# ---------------------------------------------------------------- utilitaires
def D(s):
    return date.fromisoformat(s) if s else None


def F(s):
    return float(s) if s != "" else None


def moy_et(v, mois):
    """Moyenne et ET groupee par mois, formule de la section 6."""
    v = np.asarray(v, dtype=float)
    mois = np.asarray(mois)
    N = len(v)
    m = v.mean()
    groupes = pd.Series(v - m).groupby(mois).sum().values
    G = len(groupes)
    et = math.sqrt(G / (G - 1) * float(np.sum(groupes ** 2))) / N
    return m, et, N, G


def main():
    brut = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    det = {"controles": {}, "violations": {}}
    viol = det["violations"]

    def note(num, ligne, msg):
        viol.setdefault(str(num), []).append({"ligne": ligne, "msg": msg})

    # ---- 1. colonnes
    if list(brut.columns) != COLONNES:
        note(1, None, f"colonnes differentes : {list(brut.columns)}")
    df = brut

    # ---- 2.
    if df.id_ligne.duplicated().any():
        note(2, None, "id_ligne non unique")
    pref = {"9-Year": "10", "19-Year": "20", "29-Year": "30"}
    for _, r in df.iterrows():
        i = r.id_ligne
        if i != f"{r.cusip}_{r.date_adjudication}":
            note(2, i, "id_ligne != cusip_date")
        if len(r.cusip) != 9:
            note(2, i, "cusip pas 9 caracteres")
        attendu = [v for p, v in pref.items() if r.terme_api.startswith(p + " ") or r.terme_api == p]
        if attendu != [r.echeance]:
            note(2, i, f"echeance {r.echeance} vs terme {r.terme_api}")
        J = D(r.date_adjudication)
        if r.mois != r.date_adjudication[:7]:
            note(2, i, "mois")
        if r.annee != str(J.year):
            note(2, i, "annee")
        per = "avant" if date(2010, 1, 1) <= J <= date(2021, 12, 31) else (
            "apres" if date(2022, 1, 1) <= J <= date(2026, 10, 31) else "?")
        if r.periode != per:
            note(2, i, "periode")
        for c in ("identite_fi_ok", "complet", "dans_p"):
            if r[c] not in ("0", "1"):
                note(2, i, f"{c} hors {{0,1}}")

    # ---- 3.
    if len(df) != 324:
        note(3, None, f"{len(df)} lignes")
    cpt = df.groupby(["periode", "echeance"]).size().to_dict()
    att = {("avant", "10"): 97, ("avant", "20"): 14, ("avant", "30"): 96,
           ("apres", "10"): 39, ("apres", "20"): 39, ("apres", "30"): 39}
    if cpt != att:
        note(3, None, f"comptes {cpt}")
    hc = set(df.id_ligne[df.motif_exclusion == "hors_calendrier"])
    if hc != {"9128286T2_2019-06-21"}:
        note(3, None, f"hors_calendrier {hc}")
    ti = df[df.motif_exclusion == "temoins_insuffisants"]
    ok_ti = (len(ti) == 8 and (ti.echeance == "20").all()
             and set(ti.date_adjudication) == set(df[(df.echeance == "20") & (df.date_adjudication >= "2020-06-17")
                                                     & (df.date_adjudication <= "2021-04-21")].date_adjudication))
    if not ok_ti:
        note(3, None, f"temoins_insuffisants {list(ti.id_ligne)}")
    tn = set(df.id_ligne[df.motif_exclusion == "titre_non_emis_a_jm5"])
    if tn != {"912810TC2_2021-12-02"}:
        note(3, None, f"titre_non_emis_a_jm5 {tn}")

    # ---- 4. calendrier
    for _, r in df.iterrows():
        i = r.id_ligne
        J = D(r.date_adjudication)
        if J not in RANG:
            note(4, i, "J hors C")
            continue
        jm5, jp5 = C[RANG[J] - 5], C[RANG[J] + 5]
        if D(r.date_jm5) != jm5:
            note(4, i, f"date_jm5 {r.date_jm5} != {jm5}")
        if D(r.date_jp5) != jp5:
            note(4, i, f"date_jp5 {r.date_jp5} != {jp5}")
        a, b = int(r.ecart_jm5_jours), int(r.ecart_jp5_jours)
        if a != (J - D(r.date_jm5)).days or b != (D(r.date_jp5) - J).days:
            note(4, i, "ecarts != differences de dates")
        if not (7 <= a <= 11 and 7 <= b <= 11):
            note(4, i, f"ecarts {a},{b} hors [7,11]")

    # ---- 5. temoins (partie lisible dans le fichier ; la reconstruction sur D1 n'est pas faisable ici)
    reopened = {}  # cusip -> dates d'adjudication presentes dans le fichier
    for _, r in df.iterrows():
        reopened.setdefault(r.cusip, []).append(D(r.date_adjudication))
    det["temoins_hors_fenetre_adjudication"] = []
    for _, r in df.iterrows():
        if r.motif_exclusion in METADONNEES:
            continue
        i = r.id_ligne
        t = [r.cusip_t1, r.cusip_t2, r.cusip_t3]
        if "" in t or len(set(t)) != 3:
            note(5, i, f"temoins non distincts ou manquants {t}")
        if r.cusip in t or r.cusip_premier_ancien in t:
            note(5, i, "temoin = titre rouvert ou premier ancien")
        try:
            rg = [int(r[f"rang_t{k}"]) for k in (1, 2, 3)]
            if not (rg[0] < rg[1] < rg[2] and rg[0] >= 2):
                note(5, i, f"rangs {rg}")
        except ValueError:
            note(5, i, "rang vide")
        M = D(r.date_echeance)
        ech = [D(r[f"echeance_t{k}"]) for k in (1, 2, 3)]
        if None in ech:
            note(5, i, "echeance temoin vide")
        else:
            if not (ech[0] >= ech[1] >= ech[2] and ech[0] < M):
                note(5, i, "ordre des echeances")
            for k, e in enumerate(ech, 1):
                em = 12 * (M.year - e.year) + (M.month - e.month)
                v = r[f"ecart_mois_t{k}"]
                if v == "" or int(v) != em or not (1 <= em <= 18):
                    note(5, i, f"ecart_mois_t{k}={v} calcule {em}")
        # controle demande par l'orchestrateur : aucun temoin adjuge dans [J-5;J+5] selon le fichier
        lo, hi = D(r.date_jm5), D(r.date_jp5)
        for c in t:
            for dd in reopened.get(c, []):
                if lo <= dd <= hi:
                    det["temoins_hors_fenetre_adjudication"].append((i, c, str(dd)))

    # ---- 6.
    P_mask = df.dans_p == "1"
    for _, r in df[P_mask].iterrows():
        if D(r.date_emission_origine) > D(r.date_jm5):
            note(6, r.id_ligne, "emission d'origine apres J-5")

    # ---- 7, 8, 9, 10
    prix_cols = [f"prix_{t}_{x}" for t in TITRES for x in X]
    rdt_cols = [f"rdt_{t}_{x}_pct" for t in TITRES for x in X]
    coupon_cols = ["taux_coupon_pct", "coupon_t1_pct", "coupon_t2_pct", "coupon_t3_pct"]
    for _, r in df[P_mask].iterrows():
        i = r.id_ligne
        for c in prix_cols:
            v = F(r[c])
            if v is None or not (30 <= v <= 200):
                note(7, i, f"{c}={r[c]}")
        for c in rdt_cols:
            v = F(r[c])
            if v is None or not (-1 <= v <= 20):
                note(7, i, f"{c}={r[c]}")
        for c in coupon_cols:
            v = F(r[c])
            if v is None or not (0 <= v <= 15):
                note(7, i, f"{c}={r[c]}")
        for x in X:
            ya = F(r[f"rdt_a_{x}_pct"])
            for k in (1, 2, 3):
                yk = F(r[f"rdt_t{k}_{x}_pct"])
                if ya is None or yk is None or abs(yk - ya) > 0.60:
                    note(8, i, f"|rdt_t{k}_{x} - rdt_a_{x}| = {None if ya is None or yk is None else abs(yk-ya):.4f}")
        for t in TITRES:
            pm, pj, pp = F(r[f"prix_{t}_jm5"]), F(r[f"prix_{t}_j"]), F(r[f"prix_{t}_jp5"])
            if pj == pm or pj == pp:
                note(9, i, f"prix fige {t}")
        if r.identite_fi_ok != "1":
            note(10, i, "identite_fi_ok != 1")

    # ---- 11. arithmetique des colonnes 71-78 et 80-81 (toutes les lignes)
    def g(r, c):
        return F(r[c])

    for _, r in df.iterrows():
        i = r.id_ligne
        ys = {(t, x): g(r, f"rdt_{t}_{x}_pct") for t in TITRES + ["pa"] for x in X}

        def E(t, x):
            vals = [ys[(t, x)]] + [ys[(f"t{k}", x)] for k in (1, 2, 3)]
            if None in vals:
                return None
            return 100 * (vals[0] - (vals[1] + vals[2] + vals[3]) / 3)

        e = {x: E("a", x) for x in X}
        epa = {x: E("pa", x) for x in X}
        attendu = {
            "e_jm5_pb": e["jm5"], "e_j_pb": e["j"], "e_jp5_pb": e["jp5"],
            "v_pb": None if None in e.values() else 2 * e["j"] - e["jm5"] - e["jp5"],
            "montee_pb": None if None in (e["j"], e["jm5"]) else e["j"] - e["jm5"],
            "detente_pb": None if None in (e["j"], e["jp5"]) else e["j"] - e["jp5"],
            "v_pa_pb": None if None in epa.values() else 2 * epa["j"] - epa["jm5"] - epa["jp5"],
        }
        hy = g(r, "rdt_limite_pct")
        ins = [hy, ys[("a", "jm5")]] + [ys[(f"t{k}", x)] for k in (1, 2, 3) for x in ("j", "jm5")]
        attendu["p_carte_pb"] = None if None in ins else 100 * (
            (hy - ys[("a", "jm5")]) - np.mean([ys[(f"t{k}", "j")] - ys[(f"t{k}", "jm5")] for k in (1, 2, 3)]))
        for c, a in attendu.items():
            v = g(r, c)
            if (a is None) != (v is None):
                if not (a is None and v is None):
                    note(11, i, f"{c} : fichier={r[c]!r} attendu={'vide' if a is None else a}")
            elif a is not None and abs(a - v) > 1e-6:
                note(11, i, f"{c} : fichier={v} attendu={a}")
        prix = [g(r, c) for c in prix_cols]
        comp = int(all(p is not None and p > 0 for p in prix) and r.identite_fi_ok == "1")
        if str(comp) != r.complet:
            note(11, i, f"complet={r.complet} attendu {comp}")
        dp = int(r.motif_exclusion == "" and r.complet == "1")
        if str(dp) != r.dans_p:
            note(11, i, f"dans_p={r.dans_p} attendu {dp}")

    for n in range(1, 12):
        det["controles"][str(n)] = 0 if str(n) in viol else 1
    det["controles"]["5_reconstruction_D1"] = "non executable a partir du seul fichier d'analyse"
    schema_ok = int(all(det["controles"][str(n)] == 1 for n in range(1, 12)))

    # ---- extras de format (hors liste numerotee)
    tri = df.sort_values(["date_adjudication", "echeance"], key=lambda s: s if s.name != "echeance" else s.astype(int))
    det["tri_conforme"] = bool((tri.index == df.index).all())

    # ---- recalcul des rendements sur P
    P = df[P_mask].copy()
    ecart_max = 0.0
    ou_max = None
    mes_v, mes_montee, mes_detente, mes_vpa = [], [], [], []
    for idx, r in P.iterrows():
        ech = {"a": D(r.date_echeance), "t1": D(r.echeance_t1), "t2": D(r.echeance_t2), "t3": D(r.echeance_t3),
               "pa": D(r.echeance_pa)}
        cpn = {"a": F(r.taux_coupon_pct), "t1": F(r.coupon_t1_pct), "t2": F(r.coupon_t2_pct),
               "t3": F(r.coupon_t3_pct), "pa": F(r.coupon_pa_pct)}
        dates = {"jm5": D(r.date_jm5), "j": D(r.date_adjudication), "jp5": D(r.date_jp5)}
        y = {}
        for t in TITRES + ["pa"]:
            for x in X:
                p = F(r[f"prix_{t}_{x}"])
                if p is None or p <= 0 or ech[t] is None or cpn[t] is None:
                    y[(t, x)] = None
                    continue
                y[(t, x)] = rendement(p, cpn[t], ech[t], dates[x])
                if t != "pa":
                    dlt = 100 * abs(y[(t, x)] - F(r[f"rdt_{t}_{x}_pct"]))
                    if dlt > ecart_max:
                        ecart_max, ou_max = dlt, (r.id_ligne, t, x)
        e = {x: 100 * (y[("a", x)] - sum(y[(f"t{k}", x)] for k in (1, 2, 3)) / 3) for x in X}
        mes_v.append(2 * e["j"] - e["jm5"] - e["jp5"])
        mes_montee.append(e["j"] - e["jm5"])
        mes_detente.append(e["j"] - e["jp5"])
        if all(y[("pa", x)] is not None for x in X):
            epa = {x: 100 * (y[("pa", x)] - sum(y[(f"t{k}", x)] for k in (1, 2, 3)) / 3) for x in X}
            mes_vpa.append(2 * epa["j"] - epa["jm5"] - epa["jp5"])
        else:
            mes_vpa.append(np.nan)
    P["V"] = mes_v
    P["MONTEE"] = mes_montee
    P["DETENTE"] = mes_detente
    P["VPA"] = mes_vpa
    P["ech"] = P.echeance.astype(int)
    P["an"] = P.annee.astype(int)
    P["pcarte"] = [F(s) if s != "" else np.nan for s in P.p_carte_pb]
    det["ecart_max_rdt_ou"] = ou_max
    det["ecart_max_v_vs_fichier_pb"] = float(np.max(np.abs(P.V.values - P.v_pb.astype(float).values)))

    apres = P[P.periode == "apres"]
    avant1030 = P[(P.periode == "avant") & P.ech.isin([10, 30])]
    apres1030 = apres[apres.ech.isin([10, 30])]

    m_ap, et_ap, n_ap, g_ap = moy_et(apres.V, apres.mois)
    L = m_ap - 1.645 * et_ap
    U = m_ap + 1.645 * et_ap
    sans23 = apres[apres.an != 2023].V.mean()
    sans30 = apres[apres.ech != 30].V.mean()
    minrob = min(sans23, sans30)
    m_av, et_av, n_av, g_av = moy_et(avant1030.V, avant1030.mois)
    m_ap13, et_ap13, n_ap13, g_ap13 = moy_et(apres1030.V, apres1030.mois)
    baisse = m_av - m_ap13
    et_b = math.sqrt(et_av ** 2 + et_ap13 ** 2)
    bi_b = baisse - 1.645 * et_b

    out = {
        "schema_ok": schema_ok,
        "n_apres": n_ap,
        "n_grappes_apres": g_ap,
        "n_avant_1030": n_av,
        "n_grappes_avant_1030": g_av,
        "n_temoins_figes": int(P.n_temoins_figes.astype(int).sum()),
        "ecart_max_rdt_pb": ecart_max,
        "v_moyen_apres_pb": m_ap,
        "erreur_type_apres_pb": et_ap,
        "borne_inf_90_apres_pb": L,
        "borne_sup_90_apres_pb": U,
        "marge_zone_grise": min(-L, U - 0.5),
        "v_moyen_apres_sans_2023_pb": sans23,
        "v_moyen_apres_sans_30_pb": sans30,
        "min_robustesse_pb": minrob,
        "alerte_robustesse": int(L > 0 and U >= 0.5 and minrob <= 0),
        "v_moyen_avant_1030_pb": m_av,
        "erreur_type_avant_1030_pb": et_av,
        "v_moyen_apres_1030_pb": m_ap13,
        "erreur_type_apres_1030_pb": et_ap13,
        "baisse_1030_pb": baisse,
        "erreur_type_baisse_pb": et_b,
        "borne_inf_90_baisse_pb": bi_b,
        "alerte_instrument": int(U < 0.5 and bi_b <= 0),
    }
    out = {k: (float(v) if isinstance(v, (float, np.floating)) else int(v)) for k, v in out.items()}
    (ICI / "verification.json").write_text(json.dumps(out, indent=2) + "\n")

    # ---- descriptif (pour le rapport seulement)
    def me(s, col):
        s = s[~s[col].isna()]
        if len(s) < 2:
            return None
        m, e, n, gg = moy_et(s[col], s.mois)
        return {"moy": m, "et": e, "n": n, "G": gg}

    desc = {}
    for nom, S in (("apres", apres), ("avant_1030", avant1030), ("apres_1030", apres1030)):
        desc[nom] = {c: me(S, c) for c in ("V", "MONTEE", "DETENTE", "VPA", "pcarte")}
        desc[nom]["ecart_type_V"] = float(S.V.std(ddof=1))
    desc["apres_par_annee"] = {int(a): {"moy": float(s.V.mean()), "n": len(s)} for a, s in apres.groupby("an")}
    desc["apres_par_echeance"] = {int(a): me(s, "V") for a, s in apres.groupby("ech")}
    desc["apres_sans_2023_ni_30"] = float(apres[(apres.an != 2023) & (apres.ech != 30)].V.mean())
    av20 = P[(P.periode == "avant") & (P.ech == 20)]
    desc["avant_20ans"] = {"moy": float(av20.V.mean()), "n": len(av20)}
    desc["avant_1030_par_echeance"] = {int(a): me(s, "V") for a, s in avant1030.groupby("ech")}
    avant_all = P[P.periode == "avant"]
    desc["avant_par_annee"] = {int(a): {"moy": float(s.V.mean()), "n": len(s),
                                        "moy_10": float(s[s.ech == 10].V.mean()) if (s.ech == 10).any() else None,
                                        "moy_30": float(s[s.ech == 30].V.mean()) if (s.ech == 30).any() else None}
                               for a, s in avant_all.groupby("an")}
    desc["avant_1030_par_annee_et"] = {int(a): me(s, "V") for a, s in avant1030.groupby("an")}
    desc["avant_2010_2015"] = me(avant1030[avant1030.an <= 2015], "V")
    desc["avant_2016_2021"] = me(avant1030[avant1030.an >= 2016], "V")
    desc["avant_1030_mediane"] = float(avant1030.V.median())
    desc["avant_1030_part_positive"] = float((avant1030.V > 0).mean())
    desc["apres_mediane"] = float(apres.V.median())
    desc["avant_1030_sans_2020"] = me(avant1030[avant1030.an != 2020], "V")
    for m in (10, 30):
        desc[f"avant_{m}_sans_2020"] = me(avant1030[(avant1030.ech == m) & (avant1030.an != 2020)], "V")
    desc["avant_10_2014_2019"] = me(avant1030[(avant1030.ech == 10) & avant1030.an.between(2014, 2019)], "V")
    pr = P[prix_cols].astype(float).values.ravel()
    desc["part_prix_multiples_1_32"] = float(np.mean(np.isclose((pr * 32) % 1, 0) | np.isclose((pr * 32) % 1, 1)))
    desc["coupon_pa_hors_0_15"] = int(((P.coupon_pa_pct.astype(float) < 0) | (P.coupon_pa_pct.astype(float) > 15)).sum())
    # controle 5 restreint aux lignes dans_p = 1 (lecture alternative)
    desc["controle5_violations_sur_dans_p"] = sorted({v["ligne"] for v in viol.get("5", []) if v["ligne"] in set(P.id_ligne)})
    # valeurs extremes
    PP = P.assign(absV=P.V.abs()).sort_values("absV", ascending=False)
    desc["extremes"] = [(r.id_ligne, float(r.V)) for _, r in PP.head(8).iterrows()]
    det["descriptif"] = desc
    det["lignes_exclues"] = {r.id_ligne: r.motif_exclusion for _, r in df[df.dans_p != "1"].iterrows()}
    det["complet0"] = list(df.id_ligne[df.complet != "1"])
    Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-home-user-ideation-organism/e864f6cc-dddf-5269-b156-91fe04e16180/scratchpad/verification_detail.json").write_text(json.dumps(det, indent=2, default=str) + "\n")
    print(json.dumps(out, indent=2))
    print("schema :", det["controles"])
    for k, v in viol.items():
        print("violation", k, len(v), v[:12])
    print("tri conforme", det["tri_conforme"], "ecart max ou", ou_max, "V vs fichier", det["ecart_max_v_vs_fichier_pb"])
    print("temoins adjuges dans la fenetre (selon fichier):", det["temoins_hors_fenetre_adjudication"])


if __name__ == "__main__":
    main()
