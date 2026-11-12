"""J05 - verification independante.

Lit uniquement J05_analyse.csv (et suit le texte de preenregistrement.md).
Recalcule les colonnes 16 et 33-38 avec les conventions de la section 5.2, puis K,
la regression sans constante avec effets fixes d'echeance et l'erreur type groupee par mois.
Ecrit verification.json (champs de "champs_verification" uniquement) et imprime un
diagnostic detaille (controles de schema, fragilite) sur la sortie standard.
"""
import calendar
import json
import math
import os
import sys
from datetime import date

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "J05_analyse.csv")
SORTIE = os.path.join(ICI, "verification.json")

COLONNES = [
    "id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois", "periode",
    "heure_cloture", "format_adjudication", "date_reglement", "date_echeance",
    "taux_coupon_pct", "rdt_limite_pct", "prix_limite", "coupon_couru_api", "coupon_couru_calc",
    "date_gsw_j", "beta0_j", "beta1_j", "beta2_j", "beta3_j", "tau1_j", "tau2_j",
    "date_jm5", "beta0_jm5", "beta1_jm5", "beta2_jm5", "beta3_jm5", "tau1_jm5", "tau2_jm5",
    "prix_fi_jm5", "prix_fi_j", "rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct",
    "rdt_gsw_jm5_pct", "rdt_fi_jm5_pct", "rdt_fi_j_pct", "c_pb", "k_pb", "r_fi_pb",
    "convention_ok", "complet_k", "complet_r", "dans_p",
]
assert len(COLONNES) == 45


# ---------------------------------------------------------------- conventions 5.2
def d_(s):
    return date.fromisoformat(s)


def recule_mois(M, k6):
    """M reculee de k6 mois, meme jour (dernier jour du mois si inexistant)."""
    y, m = M.year, M.month - k6
    while m <= 0:
        m += 12
        y -= 1
    jour = min(M.day, calendar.monthrange(y, m)[1])
    return date(y, m, jour)


def echeancier(M, d):
    """Retourne (L, N, liste des T_k > d en ordre croissant)."""
    futurs = []
    k = 0
    while True:
        T = recule_mois(M, 6 * k)
        if T > d:
            futurs.append(T)
            k += 1
        else:
            L = T
            break
    futurs.reverse()
    return L, futurs[0], futurs


def coupon_couru(c, M, d):
    L, N, _ = echeancier(M, d)
    return (c / 2.0) * (d - L).days / (N - L).days


def prix_plein_de_y(y, c, M, d):
    L, N, fut = echeancier(M, d)
    w = (N - d).days / (N - L).days
    n = len(fut)
    v = 1.0 / (1.0 + y / 200.0)
    tot = 0.0
    for j in range(1, n + 1):
        F = c / 2.0 + (100.0 if j == n else 0.0)
        tot += F * v ** ((j - 1) + w)
    return tot


def Y(P, c, M, d):
    """Rendement (pour cent) d'un prix pied de coupon P pour reglement d (31 CFR 356 ann. B)."""
    L, N, fut = echeancier(M, d)
    assert len(fut) > 1
    cible = P + coupon_couru(c, M, d)
    f = lambda y: prix_plein_de_y(y, c, M, d) - cible
    return brentq(f, -50.0, 100.0, xtol=1e-12, rtol=1e-15, maxiter=500)


def z_gsw(m, b0, b1, b2, b3, t1, t2):
    a1 = m / t1
    a2 = m / t2
    e1 = math.exp(-a1)
    e2 = math.exp(-a2)
    f1 = (1 - e1) / a1
    f2 = (1 - e2) / a2
    return b0 + b1 * f1 + b2 * (f1 - e1) + b3 * (f2 - e2)


def D_gsw(dt, x, par):
    m = (dt - x).days / 365.25
    return math.exp(-z_gsw(m, *par) * m / 100.0)


def g_comptant(c, M, x, par):
    _, _, fut = echeancier(M, x)
    plein = 0.0
    for T in fut:
        F = c / 2.0 + (100.0 if T == M else 0.0)
        plein += F * D_gsw(T, x, par)
    P = plein - coupon_couru(c, M, x)
    return Y(P, c, M, x)


def g_terme(c, M, J, s, par):
    _, _, fut = echeancier(M, s)
    Ds = D_gsw(s, J, par)
    plein = 0.0
    for T in fut:
        F = c / 2.0 + (100.0 if T == M else 0.0)
        plein += F * D_gsw(T, J, par) / Ds
    P = plein - coupon_couru(c, M, s)
    return Y(P, c, M, s)


# ---------------------------------------------------------------- regression
def ols_cluster(y, X, grappes):
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    g_uniq = pd.unique(np.asarray(grappes))
    meat = np.zeros((X.shape[1], X.shape[1]))
    gr = np.asarray(grappes)
    for g in g_uniq:
        idx = gr == g
        s_g = X[idx].T @ u[idx]
        meat += np.outer(s_g, s_g)
    G = len(g_uniq)
    V = G / (G - 1) * XtX_inv @ meat @ XtX_inv
    return b, V, u


def design(sub):
    ap = (sub["periode"] == "apres").astype(float).values
    cols = [ap]
    noms = ["apres"]
    for e in (10, 20, 30):
        dd = (sub["echeance_i"] == e).astype(float).values
        if dd.sum() > 0:
            cols.append(dd)
            noms.append(f"d{e}")
    return np.column_stack(cols), noms


def stat_delta(sub, col):
    X, _ = design(sub)
    b, V, u = ols_cluster(sub[col].values, X, sub["mois"].values)
    delta = -b[0]
    et = math.sqrt(V[0, 0])
    return delta, et, b, V


# ---------------------------------------------------------------- main
def main():
    raw = pd.read_csv(FICHIER, dtype=str, keep_default_na=False)
    rapport = {"schema": {}, "details": {}}
    viol = {}

    def note(num, msg, ids):
        ids = list(ids)
        if ids:
            viol.setdefault(num, []).append((msg, ids))

    # --- controle 1
    ok1 = list(raw.columns) == COLONNES
    if not ok1:
        viol.setdefault(1, []).append(("colonnes", list(raw.columns)))

    df = raw.copy()

    def num(col):
        return pd.to_numeric(df[col].replace("", np.nan), errors="coerce")

    numcols = COLONNES[11:16] + COLONNES[17:23] + COLONNES[24:45]
    for c in numcols:
        df[c + "_n"] = num(c)
    df["echeance_i"] = pd.to_numeric(df["echeance"], errors="coerce")

    present = lambda c: df[c] != ""

    # --- controle 2
    note(2, "id_ligne non unique", df.loc[df["id_ligne"].duplicated(keep=False), "id_ligne"])
    note(2, "id_ligne != cusip_date", df.loc[df["id_ligne"] != df["cusip"] + "_" + df["date_adjudication"], "id_ligne"])
    note(2, "cusip pas 9 caracteres", df.loc[df["cusip"].str.len() != 9, "id_ligne"])

    def ech_attendue(t):
        if t.startswith("9-Year"):
            return 10
        if t.startswith("19-Year"):
            return 20
        if t.startswith("29-Year"):
            return 30
        return None

    ea = df["terme_api"].map(ech_attendue)
    note(2, "echeance incoherente", df.loc[(ea != df["echeance_i"]) | ea.isna(), "id_ligne"])
    note(2, "mois incoherent", df.loc[df["mois"] != df["date_adjudication"].str[:7], "id_ligne"])

    def per_attendue(s):
        if "1991-01-01" <= s <= "2009-12-31":
            return "ancien"
        if "2010-01-01" <= s <= "2021-12-31":
            return "avant"
        if "2022-01-01" <= s <= "2026-10-31":
            return "apres"
        return None

    note(2, "periode incoherente", df.loc[df["date_adjudication"].map(per_attendue) != df["periode"], "id_ligne"])
    for c in ["convention_ok", "complet_k", "complet_r", "dans_p"]:
        note(2, f"{c} hors {{0,1}}", df.loc[~df[c].isin(["0", "1"]), "id_ligne"])

    # --- controle 3
    note(3, "date_adjudication hors 1991-01-01..2026-10-31",
         df.loc[(df["date_adjudication"] < "1991-01-01") | (df["date_adjudication"] > "2026-10-31"), "id_ligne"])
    cnt = df["periode"].value_counts()
    rapport["schema"]["comptes_periode"] = cnt.to_dict()
    for p, lo, hi in [("ancien", 60, 70), ("avant", 200, 214), ("apres", 112, 120)]:
        n = int(cnt.get(p, 0))
        if not (lo <= n <= hi):
            viol.setdefault(3, []).append((f"compte {p}={n} hors [{lo},{hi}]", []))

    # --- controle 4
    dj = df["date_adjudication"].map(d_)
    ds = df["date_reglement"].map(d_)
    dm = df["date_echeance"].map(d_)
    delai = (ds - dj).map(lambda t: t.days)
    note(4, "reglement pas dans ]J, J+20]", df.loc[(delai <= 0) | (delai > 20), "id_ligne"])
    note(4, "echeance <= reglement", df.loc[dm <= ds, "id_ligne"])

    # --- controle 5
    pj = [f"{b}_j" for b in ["beta0", "beta1", "beta2", "beta3", "tau1", "tau2"]]
    pm = [f"{b}_jm5" for b in ["beta0", "beta1", "beta2", "beta3", "tau1", "tau2"]]
    any_pj = df[pj].ne("").any(axis=1)
    any_pm = df[pm].ne("").any(axis=1)
    note(5, "parametres J sans date_gsw_j", df.loc[any_pj & (df["date_gsw_j"] == ""), "id_ligne"])
    note(5, "parametres J-5 sans date_jm5", df.loc[any_pm & (df["date_jm5"] == ""), "id_ligne"])
    rj = present("date_gsw_j")
    note(5, "date_gsw_j != date_adjudication", df.loc[rj & (df["date_gsw_j"] != df["date_adjudication"]), "id_ligne"])
    rm = present("date_jm5")
    ecart_j5 = pd.Series(np.nan, index=df.index)
    wd = pd.Series(np.nan, index=df.index)
    for i in df.index[rm]:
        x = d_(df.at[i, "date_jm5"])
        ecart_j5[i] = (dj[i] - x).days
        wd[i] = x.weekday()
    df["ecart_j5"] = ecart_j5
    note(5, "date_jm5 >= date_adjudication", df.loc[rm & (ecart_j5 <= 0), "id_ligne"])
    bad_gap = rm & ((ecart_j5 < 7) | (ecart_j5 > 9))
    note(5, "date_jm5 a un ecart hors 7..9 jours civils", df.loc[bad_gap, "id_ligne"])
    note(5, "date_jm5 pas un jour lundi-vendredi", df.loc[rm & (wd >= 5), "id_ligne"])
    note(5, "prix_fi_jm5 sans date_jm5", df.loc[present("prix_fi_jm5") & ~rm, "id_ligne"])
    rapport["details"]["ecart_jm5_distribution"] = ecart_j5.dropna().astype(int).value_counts().sort_index().to_dict()

    # --- controle 6
    for c in ["rdt_limite_pct", "rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct",
              "rdt_gsw_jm5_pct", "rdt_fi_jm5_pct", "rdt_fi_j_pct"]:
        v = df[c + "_n"]
        note(6, f"{c} hors [-1,20]", df.loc[v.notna() & ((v < -1) | (v > 20)), "id_ligne"])
    for c in ["prix_limite", "prix_fi_jm5", "prix_fi_j"]:
        v = df[c + "_n"]
        note(6, f"{c} hors [50,200]", df.loc[v.notna() & ((v < 50) | (v > 200)), "id_ligne"])
    for c in ["tau1_j", "tau2_j", "tau1_jm5", "tau2_jm5"]:
        v = df[c + "_n"]
        note(6, f"{c} <= 0", df.loc[v.notna() & (v <= 0), "id_ligne"])
    v = df["taux_coupon_pct_n"]
    note(6, "taux_coupon_pct hors [0,15]", df.loc[v.isna() | (v < 0) | (v > 15), "id_ligne"])

    # --- controle 7
    a = (df["rdt_fi_jm5_pct_n"] - df["rdt_gsw_jm5_pct_n"]).abs()
    note(7, "|f(J-5)-g(J-5)| > 0.60", df.loc[a.notna() & (a > 0.60), "id_ligne"])
    b_ = (df["rdt_fi_j_pct_n"] - df["rdt_limite_pct_n"]).abs()
    note(7, "|f(J)-high_yield| > 0.40", df.loc[b_.notna() & (b_ > 0.40), "id_ligne"])

    # --- controle 8
    c_f = 100 * (df["rdt_limite_pct_n"] - df["rdt_gsw_j_terme_pct_n"])
    k_f = c_f - 100 * (df["rdt_fi_jm5_pct_n"] - df["rdt_gsw_jm5_pct_n"])
    r_f = 100 * ((df["rdt_fi_j_pct_n"] - df["rdt_gsw_j_pct_n"]) - (df["rdt_fi_jm5_pct_n"] - df["rdt_gsw_jm5_pct_n"]))
    for nom, calc in [("c_pb", c_f), ("k_pb", k_f), ("r_fi_pb", r_f)]:
        fich = df[nom + "_n"]
        mism = (calc.isna() != fich.isna()) | ((calc - fich).abs() > 1e-6)
        note(8, f"{nom} != formule", df.loc[mism, "id_ligne"])
    conv = ((df["rdt_prix_limite_pct_n"] - df["rdt_limite_pct_n"]).abs() <= 0.001) & \
           ((df["coupon_couru_calc_n"] - df["coupon_couru_api_n"]).abs() <= 0.001)
    conv = conv.astype(int)
    k_cols = ["rdt_limite_pct", "prix_limite"] + pj + pm + ["prix_fi_jm5"]
    ck = (df[k_cols].ne("").all(axis=1) & (df["date_gsw_j"] == df["date_adjudication"])).astype(int)
    cr = ((ck == 1) & present("prix_fi_j")).astype(int)
    dp = (df["periode"].isin(["avant", "apres"]) & (ck == 1) & (conv == 1)).astype(int)
    for nom, calc in [("convention_ok", conv), ("complet_k", ck), ("complet_r", cr), ("dans_p", dp)]:
        note(8, f"{nom} != definition", df.loc[pd.to_numeric(df[nom], errors="coerce") != calc, "id_ligne"])

    schema_ok = 1 if (ok1 and not viol) else 0
    rapport["schema"]["violations"] = {str(k): [(m, ids) for m, ids in v] for k, v in viol.items()}

    # ------------------------------------------------ recalcul independant (avant, apres)
    ecarts = {c: [] for c in ["coupon_couru_calc", "rdt_prix_limite_pct", "rdt_gsw_j_terme_pct",
                              "rdt_gsw_j_pct", "rdt_gsw_jm5_pct", "rdt_fi_jm5_pct", "rdt_fi_j_pct"]}
    mine = {c: pd.Series(np.nan, index=df.index) for c in ecarts}
    n_echec = 0
    echecs = []
    vides_incoherents = []
    for i in df.index[df["periode"].isin(["avant", "apres"])]:
        r = df.loc[i]
        c = r["taux_coupon_pct_n"]
        M = dm[i]
        J = dj[i]
        s = ds[i]
        ai = coupon_couru(c, M, s)
        mine["coupon_couru_calc"][i] = ai
        if not math.isnan(r["prix_limite_n"]):
            mine["rdt_prix_limite_pct"][i] = Y(r["prix_limite_n"], c, M, s)
        parj = [r[p + "_n"] for p in pj]
        if r["date_gsw_j"] != "" and not any(math.isnan(v) for v in parj):
            Jg = d_(r["date_gsw_j"])
            mine["rdt_gsw_j_terme_pct"][i] = g_terme(c, M, Jg, s, parj)
            mine["rdt_gsw_j_pct"][i] = g_comptant(c, M, Jg, parj)
        parm = [r[p + "_n"] for p in pm]
        if r["date_jm5"] != "" and not any(math.isnan(v) for v in parm):
            x = d_(r["date_jm5"])
            mine["rdt_gsw_jm5_pct"][i] = g_comptant(c, M, x, parm)
        if r["date_jm5"] != "" and not math.isnan(r["prix_fi_jm5_n"]):
            mine["rdt_fi_jm5_pct"][i] = Y(r["prix_fi_jm5_n"], c, M, d_(r["date_jm5"]))
        if not math.isnan(r["prix_fi_j_n"]):
            mine["rdt_fi_j_pct"][i] = Y(r["prix_fi_j_n"], c, M, J)
        for col in ecarts:
            a_, b2 = mine[col][i], r[col + "_n"]
            if not (math.isnan(a_) or math.isnan(b2)):
                ecarts[col].append(abs(a_ - b2))
            elif math.isnan(a_) != math.isnan(b2):
                vides_incoherents.append((r["id_ligne"], col))
        if not math.isnan(r["rdt_limite_pct_n"]) and not math.isnan(r["prix_limite_n"]):
            ok = (abs(mine["rdt_prix_limite_pct"][i] - r["rdt_limite_pct_n"]) <= 0.001 and
                  abs(ai - r["coupon_couru_api_n"]) <= 0.001)
            if not ok:
                n_echec += 1
                echecs.append(r["id_ligne"])

    yld = ["rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct", "rdt_gsw_jm5_pct",
           "rdt_fi_jm5_pct", "rdt_fi_j_pct"]
    ecart_max_rdt_pb = 100 * max(max(ecarts[c]) for c in yld if ecarts[c])
    rapport["details"]["ecart_max_par_colonne_pb"] = {c: (100 * max(v) if v else None) for c, v in ecarts.items()}
    rapport["details"]["ecart_max_coupon_couru_calc_pour100"] = max(ecarts["coupon_couru_calc"])
    rapport["details"]["vides_incoherents"] = vides_incoherents
    rapport["details"]["echecs_convention"] = echecs

    # mon K, mon R
    df["K_v"] = 100 * ((df["rdt_limite_pct_n"] - mine["rdt_gsw_j_terme_pct"]) -
                       (mine["rdt_fi_jm5_pct"] - mine["rdt_gsw_jm5_pct"]))
    df["C_v"] = 100 * (df["rdt_limite_pct_n"] - mine["rdt_gsw_j_terme_pct"])
    df["R_v"] = 100 * ((mine["rdt_fi_j_pct"] - mine["rdt_gsw_j_pct"]) -
                       (mine["rdt_fi_jm5_pct"] - mine["rdt_gsw_jm5_pct"]))
    df["annee"] = df["date_adjudication"].str[:4]

    P = df[df["dans_p"] == "1"].copy()
    assert P["K_v"].notna().all()
    n_av = int((P["periode"] == "avant").sum())
    n_ap = int((P["periode"] == "apres").sum())
    g_av = int(P.loc[P["periode"] == "avant", "mois"].nunique())
    g_ap = int(P.loc[P["periode"] == "apres", "mois"].nunique())
    delta, et, b, V = stat_delta(P, "K_v")
    L = delta - 1.645 * et
    U = delta + 1.645 * et
    Mz = min(-L, U - 0.5)
    res = {
        "schema_ok": schema_ok,
        "n_avant": n_av,
        "n_apres": n_ap,
        "n_grappes_avant": g_av,
        "n_grappes_apres": g_ap,
        "n_echec_convention": n_echec,
        "ecart_max_rdt_pb": ecart_max_rdt_pb,
        "k_moyen_avant_pb": float(P.loc[P["periode"] == "avant", "K_v"].mean()),
        "k_moyen_apres_pb": float(P.loc[P["periode"] == "apres", "K_v"].mean()),
        "delta_k_pb": float(delta),
        "erreur_type_pb": float(et),
        "borne_inf_90_pb": float(L),
        "borne_sup_90_pb": float(U),
        "marge_zone_grise": float(Mz),
    }
    with open(SORTIE, "w") as f:
        json.dump(res, f, indent=2)

    # ------------------------------------------------ controles croises et fragilite (stdout)
    out = {"verification": res, "schema": rapport["schema"], "details": rapport["details"]}
    # statsmodels
    try:
        import statsmodels.api as sm
        X, _ = design(P)
        grp = pd.factorize(P["mois"])[0]
        m = sm.OLS(P["K_v"].values, X).fit(cov_type="cluster", cov_kwds={"groups": grp, "use_correction": False})
        G = len(set(grp))
        out["statsmodels_et_G_sur_Gm1"] = float(math.sqrt(m.cov_params()[0, 0] * G / (G - 1)))
        out["statsmodels_b"] = float(m.params[0])
    except Exception as e:  # pragma: no cover
        out["statsmodels_erreur"] = repr(e)
    # K du fichier
    d2, e2, _, _ = stat_delta(P, "k_pb_n")
    out["delta_avec_k_du_fichier"] = (d2, e2)
    out["ecart_max_K_moi_vs_fichier_pb"] = float((P["K_v"] - P["k_pb_n"]).abs().max())

    def resume(sub, col="K_v"):
        d, e, _, _ = stat_delta(sub, col)
        return {"delta": round(d, 4), "et": round(e, 4), "L": round(d - 1.645 * e, 4),
                "U": round(d + 1.645 * e, 4), "n": len(sub),
                "n_av": int((sub["periode"] == "avant").sum()), "n_ap": int((sub["periode"] == "apres").sum())}

    fr = {}
    fr["moyenne_K_par_annee"] = P.groupby("annee")["K_v"].agg(["mean", "count", "std"]).round(3).to_dict("index")
    fr["moyenne_K_par_periode_echeance"] = P.groupby(["periode", "echeance_i"])["K_v"].agg(["mean", "count"]).round(3).reset_index().to_dict("records")
    # delta par annee apres (contre tout avant)
    par_an = {}
    for an in sorted(P.loc[P["periode"] == "apres", "annee"].unique()):
        sub = P[(P["periode"] == "avant") | (P["annee"] == an)]
        par_an[an] = resume(sub)
    fr["delta_par_annee_apres_vs_avant"] = par_an
    # sans chaque annee (avant ou apres)
    sans_an = {}
    for an in sorted(P["annee"].unique()):
        sans_an[an] = resume(P[P["annee"] != an])
    fr["sans_chaque_annee"] = sans_an
    fr["sans_chaque_echeance"] = {str(e): resume(P[P["echeance_i"] != e]) for e in (10, 20, 30)}
    fr["chaque_echeance_seule"] = {str(e): resume(P[P["echeance_i"] == e]) for e in (10, 20, 30)}
    # 5 plus influentes : changement exact de b par retrait d'une ligne
    infl = []
    for i in P.index:
        d, _, _, _ = stat_delta(P.drop(index=i), "K_v")
        infl.append((abs(d - delta), d - delta, i))
    infl.sort(reverse=True)
    top5 = [i for _, _, i in infl[:5]]
    fr["top5_influentes"] = [{"id": P.at[i, "id_ligne"], "K": round(P.at[i, "K_v"], 3),
                              "periode": P.at[i, "periode"], "effet_sur_delta": round(dd, 4)}
                             for _, dd, i in infl[:5]]
    fr["sans_top5"] = resume(P.drop(index=top5))
    fr["sd_K"] = {p: float(P.loc[P["periode"] == p, "K_v"].std(ddof=1)) for p in ("avant", "apres")}
    # mediane, descriptif
    fr["mediane_K"] = {p: float(P.loc[P["periode"] == p, "K_v"].median()) for p in ("avant", "apres")}
    out["fragilite"] = fr

    # sans les lignes en violation de schema (descriptif)
    ids_viol = sorted({x for v in viol.values() for _, ids in v for x in ids})
    out["ids_en_violation"] = ids_viol
    if ids_viol:
        Q = P[~P["id_ligne"].isin(ids_viol)]
        d, e, _, _ = stat_delta(Q, "K_v")
        out["sans_lignes_en_violation"] = {
            "n_avant": int((Q["periode"] == "avant").sum()), "n_apres": int((Q["periode"] == "apres").sum()),
            "n_grappes_avant": int(Q.loc[Q["periode"] == "avant", "mois"].nunique()),
            "n_grappes_apres": int(Q.loc[Q["periode"] == "apres", "mois"].nunique()),
            "k_moyen_avant": float(Q.loc[Q["periode"] == "avant", "K_v"].mean()),
            "k_moyen_apres": float(Q.loc[Q["periode"] == "apres", "K_v"].mean()),
            "delta": d, "et": e, "L": d - 1.645 * e, "U": d + 1.645 * e,
            "Mz": min(-(d - 1.645 * e), d + 1.645 * e - 0.5)}
        cols = ["id_ligne", "periode", "date_adjudication", "date_jm5", "ecart_j5", "dans_p", "K_v"]
        out["lignes_en_violation"] = df.loc[df["id_ligne"].isin(ids_viol), cols].to_dict("records")

    # S1, S2, S3 descriptifs
    s = {}
    S1a = df[df["C_v"].notna() & (df["convention_ok"] == "1")] if False else None
    # S1 (a) : C sur ancien/avant/apres -- pour ancien, le recalcul g_terme est fait ci-dessous
    s["S1b_P"] = resume(P, "C_v")
    R = P[P["complet_r"] == "1"].copy()
    R["A_v"] = R["K_v"] - R["R_v"]
    s["S2_R"] = resume(R, "R_v")
    s["S2_A"] = resume(R, "A_v")
    P["Pi_v"] = 100 * (mine["rdt_fi_jm5_pct"] - mine["rdt_gsw_jm5_pct"])
    s["S3_Pi"] = resume(P, "Pi_v")
    s["S3_moyennes"] = P.groupby(["periode", "echeance_i"])["Pi_v"].mean().round(3).reset_index().to_dict("records")
    out["secondaires"] = s

    print(json.dumps(out, indent=1, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
