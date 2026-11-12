"""J05 — statistique principale et analyses secondaires (section 6 de la préinscription).

Lit J05_analyse.csv. Recalcule avec un code distinct de construire.py (dates de coupon, coupon couru, rendements par
Brent/scipy, courbe GSW vectorisée) les colonnes 16 et 33 à 38 des lignes `avant` et `apres`, puis K avec ces
rendements, sur l'échantillon P défini par les colonnes du fichier (dans_p = 1).
Écrit temoin.json, resultats_analyse.json et figure.png.
Usage : python3 -I analyse.py
"""
import calendar
import datetime as dt
import json
import os

import numpy as np
import pandas as pd
from scipy.optimize import brentq

ICI = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(ICI, "J05_analyse.csv")
Z90 = 1.645


# --------------------------------------------------------------------------------- recalcul indépendant (5.2)
def moins_mois(d, k):
    t = d.year * 12 + (d.month - 1) - k
    a, m = divmod(t, 12)
    m += 1
    return dt.date(a, m, min(d.day, calendar.monthrange(a, m)[1]))


def echeancier(M, d):
    """(T_k > d croissants, L, N)."""
    T = []
    k = 0
    while True:
        t = moins_mois(M, 6 * k)
        if t <= d:
            L = t
            break
        T.append(t)
        k += 1
    T = T[::-1]
    return T, L, T[0]


def ai(c, M, d):
    T, L, N = echeancier(M, d)
    return c / 2 * (d - L).days / (N - L).days


def y_de_p(P, c, M, d):
    T, L, N = echeancier(M, d)
    n = len(T)
    e = np.arange(n) + (N - d).days / (N - L).days
    F_ = np.full(n, c / 2.0)
    F_[-1] += 100.0
    cible = P + ai(c, M, d)
    return brentq(lambda y: float(np.sum(F_ * (1 + y / 200.0) ** (-e))) - cible, -5, 40, xtol=1e-13, rtol=1e-15, maxiter=500)


def zc(p, m):
    b0, b1, b2, b3, t1, t2 = p
    m = np.asarray(m, float)
    a1, a2 = m / t1, m / t2
    f1 = (1 - np.exp(-a1)) / a1
    f2 = (1 - np.exp(-a2)) / a2
    return b0 + b1 * f1 + b2 * (f1 - np.exp(-a1)) + b3 * (f2 - np.exp(-a2))


def fact(p, x, dates):
    m = np.array([(t - x).days for t in dates]) / 365.25
    return np.exp(-zc(p, m) * m / 100.0)


def flux(c, M, d):
    T, _, _ = echeancier(M, d)
    F_ = np.full(len(T), c / 2.0)
    F_[-1] += 100.0
    return T, F_


def gsw_comptant(p, x, c, M):
    T, F_ = flux(c, M, x)
    return y_de_p(float(np.sum(F_ * fact(p, x, T))) - ai(c, M, x), c, M, x)


def gsw_terme(p, J, s, c, M):
    T, F_ = flux(c, M, s)
    plein = float(np.sum(F_ * fact(p, J, T))) / float(fact(p, J, [s])[0])
    return y_de_p(plein - ai(c, M, s), c, M, s)


# ------------------------------------------------------------------------------------------- régression groupée
def mco_groupe(y, X, g):
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    g = np.asarray(g)
    grp = pd.unique(g)
    G = len(grp)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for k in grp:
        i = g == k
        s_ = X[i].T @ u[i]
        meat += np.outer(s_, s_)
    V = G / (G - 1) * XtX_inv @ meat @ XtX_inv
    return b, V, G


def baisse(df, col):
    """Δ = −b (coefficient de `apres`) dans y = b·apres + a10·d10 + a20·d20 + a30·d30, ET groupée par mois."""
    X = np.column_stack([(df["periode"] == "apres").astype(float)] + [(df["echeance"] == e).astype(float) for e in (10, 20, 30)])
    b, V, G = mco_groupe(df[col].values, X, df["mois"].values)
    return {"delta_pb": float(-b[0]), "erreur_type_pb": float(np.sqrt(V[0, 0])), "n": int(len(df)), "grappes": int(G),
            "a10": float(b[1]), "a20": float(b[2]), "a30": float(b[3])}


def main():
    df = pd.read_csv(F, dtype={"cusip": str, "mois": str})
    D = lambda s: dt.date.fromisoformat(s)
    pa = ["beta0", "beta1", "beta2", "beta3", "tau1", "tau2"]

    # ---------------------------------------------------- recalcul des colonnes 16 et 33-38 (lignes avant/apres)
    cols = ["coupon_couru_calc", "rdt_prix_limite_pct", "rdt_gsw_j_terme_pct", "rdt_gsw_j_pct", "rdt_gsw_jm5_pct",
            "rdt_fi_jm5_pct", "rdt_fi_j_pct"]
    mien = {k: np.full(len(df), np.nan) for k in cols}
    for i, r in df.iterrows():
        c, M, s, J = r["taux_coupon_pct"], D(r["date_echeance"]), D(r["date_reglement"]), D(r["date_adjudication"])
        mien["coupon_couru_calc"][i] = ai(c, M, s)
        if pd.notna(r["prix_limite"]):
            mien["rdt_prix_limite_pct"][i] = y_de_p(r["prix_limite"], c, M, s)
        pj = [r[k + "_j"] for k in pa]
        if not any(pd.isna(pj)):
            mien["rdt_gsw_j_terme_pct"][i] = gsw_terme(pj, J, s, c, M)
            if r["periode"] in ("avant", "apres"):
                mien["rdt_gsw_j_pct"][i] = gsw_comptant(pj, J, c, M)
        pm = [r[k + "_jm5"] for k in pa]
        if pd.notna(r["date_jm5"]) and not any(pd.isna(pm)):
            x = D(r["date_jm5"])
            mien["rdt_gsw_jm5_pct"][i] = gsw_comptant(pm, x, c, M)
            if pd.notna(r["prix_fi_jm5"]):
                mien["rdt_fi_jm5_pct"][i] = y_de_p(r["prix_fi_jm5"], c, M, x)
        if pd.notna(r["prix_fi_j"]):
            mien["rdt_fi_j_pct"][i] = y_de_p(r["prix_fi_j"], c, M, J)
    aa = df["periode"].isin(["avant", "apres"]).values
    ecarts = {}
    for k in cols:
        a, b = mien[k][aa], df[k].values[aa]
        manque = np.isnan(a) != np.isnan(b)
        ecarts[k] = {"ecart_max": float(np.nanmax(np.abs(a - b))) if np.any(~np.isnan(a) & ~np.isnan(b)) else 0.0,
                     "presence_differente": int(manque.sum())}
    ecart_max_rdt_pb = 100.0 * max(ecarts[k]["ecart_max"] for k in cols[1:])
    assert all(ecarts[k]["presence_differente"] == 0 for k in cols), ecarts

    # n_echec_convention, selon mon calcul
    hy = df["rdt_limite_pct"].values
    conv_mien = (np.abs(mien["rdt_prix_limite_pct"] - hy) <= 0.001) & (np.abs(mien["coupon_couru_calc"] - df["coupon_couru_api"].values) <= 0.001)
    present = aa & df["rdt_limite_pct"].notna().values & df["prix_limite"].notna().values
    n_echec_convention = int(np.sum(present & ~conv_mien))

    # K, C, R avec mes rendements
    df["k_mien"] = 100 * (hy - mien["rdt_gsw_j_terme_pct"]) - 100 * (mien["rdt_fi_jm5_pct"] - mien["rdt_gsw_jm5_pct"])
    df["r_mien"] = 100 * ((mien["rdt_fi_j_pct"] - mien["rdt_gsw_j_pct"]) - (mien["rdt_fi_jm5_pct"] - mien["rdt_gsw_jm5_pct"]))
    df["pi_mien"] = 100 * (mien["rdt_fi_jm5_pct"] - mien["rdt_gsw_jm5_pct"])
    df["a_mien"] = df["k_mien"] - df["r_mien"]

    # ------------------------------------------------------------------------------------ statistique principale
    P = df[df["dans_p"] == 1].copy()
    assert P["k_mien"].notna().all()
    res = baisse(P, "k_mien")
    d, et = res["delta_pb"], res["erreur_type_pb"]
    L, U = d - Z90 * et, d + Z90 * et
    av, ap = P[P["periode"] == "avant"], P[P["periode"] == "apres"]
    temoin = {
        "schema_ok": None,  # rempli plus bas à partir de construire_journal.json
        "n_avant": int(len(av)), "n_apres": int(len(ap)),
        "n_grappes_avant": int(av["mois"].nunique()), "n_grappes_apres": int(ap["mois"].nunique()),
        "n_echec_convention": n_echec_convention, "ecart_max_rdt_pb": ecart_max_rdt_pb,
        "k_moyen_avant_pb": float(av["k_mien"].mean()), "k_moyen_apres_pb": float(ap["k_mien"].mean()),
        "delta_k_pb": d, "erreur_type_pb": et, "borne_inf_90_pb": L, "borne_sup_90_pb": U,
        "marge_zone_grise": min(-L, U - 0.5),
    }
    j = json.load(open(os.path.join(ICI, "construire_journal.json"), encoding="utf-8"))
    temoin["schema_ok"] = int(j["schema_ok"])
    json.dump(temoin, open(os.path.join(ICI, "temoin.json"), "w"), indent=1)

    # ---------------------------------------------------------------------------- analyses secondaires (descriptives)
    desc = {}
    # S1 : C en niveau, avec mes rendements (lignes ancien comprises) ; échantillon défini par les colonnes du fichier
    df["c_mien"] = 100 * (hy - mien["rdt_gsw_j_terme_pct"])
    s1a = df[df["c_pb"].notna() & (df["convention_ok"] == 1)].copy()
    assert s1a["c_mien"].notna().all()
    desc["S1a_c_apres_vs_ancien_avant"] = baisse(s1a, "c_mien")
    desc["S1a_c_apres_vs_ancien_avant"]["n_par_periode"] = s1a["periode"].value_counts().to_dict()
    P["c_mien"] = 100 * (P["rdt_limite_pct"].values - mien["rdt_gsw_j_terme_pct"][P.index])
    desc["S1b_c_sur_P"] = baisse(P, "c_mien")
    # S2
    PR = P[P["complet_r"] == 1]
    desc["S2_R_montee_cloture"] = baisse(PR, "r_mien")
    desc["S2_A_decote_et_apres_midi"] = baisse(PR, "a_mien")
    desc["S2_moyennes"] = {per: {"R": float(PR[PR.periode == per]["r_mien"].mean()), "A": float(PR[PR.periode == per]["a_mien"].mean()),
                                 "n": int((PR.periode == per).sum())} for per in ("avant", "apres")}
    # S3
    desc["S3_prime_moyenne_pb"] = {f"{per}_{e}": float(P[(P.periode == per) & (P.echeance == e)]["pi_mien"].mean())
                                   for per in ("avant", "apres") for e in (10, 20, 30)}
    desc["S3_prime_n"] = {f"{per}_{e}": int(((P.periode == per) & (P.echeance == e)).sum()) for per in ("avant", "apres") for e in (10, 20, 30)}
    desc["S3_prime_par_periode_pb"] = {per: float(P[P.periode == per]["pi_mien"].mean()) for per in ("avant", "apres")}
    desc["S3_delta_prime"] = baisse(P, "pi_mien")
    # écarts-types
    desc["ecart_type_k_avant_pb"] = float(av["k_mien"].std(ddof=1))
    desc["ecart_type_k_apres_pb"] = float(ap["k_mien"].std(ddof=1))
    # compléments descriptifs
    desc["k_moyen_par_periode_et_echeance"] = {f"{per}_{e}": float(P[(P.periode == per) & (P.echeance == e)]["k_mien"].mean())
                                              for per in ("avant", "apres") for e in (10, 20, 30)}
    desc["coefficients_principaux"] = res
    # K par année (pour la figure) : moyenne et IC à 90 % groupé par mois
    P["annee"] = P["date_adjudication"].str[:4].astype(int)
    par_an = []
    for an, g in P.groupby("annee"):
        X = np.ones((len(g), 1))
        b, V, G = mco_groupe(g["k_mien"].values, X, g["mois"].values)
        par_an.append({"annee": int(an), "n": int(len(g)), "mois": int(G), "moyenne": float(b[0]), "et": float(np.sqrt(V[0, 0]))})
    desc["k_par_annee"] = par_an
    # sensibilité : statistique avec les k_pb du fichier (doit coïncider)
    desc["delta_avec_k_pb_du_fichier"] = baisse(P, "k_pb")["delta_pb"]
    out = {"temoin": temoin, "ecarts_recalcul": ecarts, "ecart_max_coupon_couru": ecarts["coupon_couru_calc"]["ecart_max"],
           "descriptif": desc}
    json.dump(out, open(os.path.join(ICI, "resultats_analyse.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(temoin, indent=1))
    figure(par_an, temoin)


def figure(par_an, t):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    encre, gris, accent = "#1f2933", "#8a949e", "#2a6f97"
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=150)
    x = [p["annee"] for p in par_an]
    m = [p["moyenne"] for p in par_an]
    e = [Z90 * p["et"] for p in par_an]
    ax.axhline(0, color=gris, lw=0.8)
    ax.axvline(2021.5, color=encre, lw=1.2, ls="--")
    ax.errorbar(x, m, yerr=e, fmt="o", color=accent, ms=6, lw=1.6, capsize=3, label="K moyen par année (IC à 90 %, groupé par mois)")
    for p in par_an:
        ax.text(p["annee"], 0.015, f"n={p['n']}", transform=ax.get_xaxis_transform(), ha="center", fontsize=7, color=gris)
    ax.hlines(t["k_moyen_avant_pb"], 2009.6, 2021.4, color=encre, lw=2, label=f"moyenne simple 2010-2021 : {t['k_moyen_avant_pb']:.2f} pb")
    ax.hlines(t["k_moyen_apres_pb"], 2021.6, 2026.4, color=encre, lw=2, ls=":", label=f"moyenne simple 2022-2026 : {t['k_moyen_apres_pb']:.2f} pb")
    yl = ax.get_ylim()
    ax.set_xticks(range(2010, 2027))
    ax.set_xlabel("année d'adjudication")
    ax.set_ylabel("K (pb)")
    ax.set_title(f"J05 — K par année, réouvertures à 10, 20 et 30 ans (échantillon P)\n"
                 f"baisse estimée Δ (effets fixes d'échéance, ET groupée par mois) = {t['delta_k_pb']:.3f} pb, IC à 90 % [{t['borne_inf_90_pb']:.3f} ; {t['borne_sup_90_pb']:.3f}]",
                 fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e4e7eb", lw=0.6)
    ax.legend(fontsize=8, frameon=False, loc="upper left")
    yl = ax.get_ylim()
    ax.set_ylim(yl[0] - 0.08 * (yl[1] - yl[0]), yl[1] + 0.12 * (yl[1] - yl[0]))
    ax.text(2021.55, 0.985, "coupure 1er janv. 2022", transform=ax.get_xaxis_transform(), fontsize=8, color=encre, va="top")
    fig.tight_layout()
    fig.savefig(os.path.join(ICI, "figure.png"))


if __name__ == "__main__":
    main()
