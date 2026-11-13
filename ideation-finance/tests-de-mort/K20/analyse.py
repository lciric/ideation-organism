"""K20 — statistique principale et analyses secondaires (section 6 de la préinscription).

Lit uniquement K20_analyse.csv. Écrit temoin.json (témoin), resultats_detail.json (tous les
chiffres, y compris b_v, Q_v, t des exclusions) et figure.png.
Usage : python3 -I analyse.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from construire import EPISODES, VARS, controles, lire_fichier  # noqa: E402

Z90 = 1.645


# ---------------------------------------------------------------- outils
def design(d, Lcol, zr, par_variable=False):
    """Régresseurs dans l'ordre préinscrit : 5 constantes, 5 effets de classe, 5 pentes, c
    (ou 5 c_v si par_variable)."""
    D = np.column_stack([(d["variable"] == v).to_numpy(float) for v in VARS])
    L = d[Lcol].to_numpy(float)
    z = d[zr].to_numpy(float)
    cols = [D, D * L[:, None], D * z[:, None]]
    cols.append(D * (z * L)[:, None] if par_variable else (z * L)[:, None])
    return np.column_stack(cols)


def dk(X, u, t, lags):
    """Driscoll-Kraay : scores sommés par trimestre cible (tous les trimestres de min à max,
    vides compris), Newey-West Bartlett à `lags` retards en temps calendaire, sans correction."""
    h = X * u[:, None]
    tmin, tmax = int(t.min()), int(t.max())
    H = np.zeros((tmax - tmin + 1, X.shape[1]))
    np.add.at(H, (t - tmin).astype(int), h)
    om = H.T @ H
    for j in range(1, lags + 1):
        w = 1 - j / (lags + 1)
        G = H[j:].T @ H[:-j]
        om += w * (G + G.T)
    XtXi = np.linalg.inv(X.T @ X)
    return XtXi @ om @ XtXi


def mco(d, ze, zr, Lcol, lags=4, par_variable=False):
    n = len(d)
    k = 20 if par_variable else 16
    if n < 50:
        return None
    X = design(d, Lcol, zr, par_variable)
    y = d[ze].to_numpy(float)
    XtX = X.T @ X
    if np.linalg.matrix_rank(XtX) < k:
        return None
    beta = np.linalg.solve(XtX, X.T @ y)
    u = y - X @ beta
    t = d["t_cible"].to_numpy(int)
    V = dk(X, u, t, lags)
    s2 = u @ u / (n - k)
    Viid = s2 * np.linalg.inv(XtX)
    return {"beta": beta, "V": V, "Viid": Viid, "n": n, "u": u, "X": X}


def se(res, i, lags=None, d=None):
    return float(np.sqrt(res["V"][i, i]))


# ---------------------------------------------------------------- calcul
def main():
    d = lire_fichier()
    out = {}
    detail = {}
    err = controles(d)
    out["n_violations_schema"] = sum(1 for k in err if err[k])
    detail["controles_violes"] = {k: v for k, v in err.items() if v}

    # étape 1 — réduction sur les lignes principales, constantes appliquées à toutes les lignes
    p_mask = d["principal"] == 1
    kv = {}
    for nom_r, nom_e, suf in (("revision", "erreur", ""), ("revision_med", "erreur_med", "_med")):
        d["z_r" + suf] = np.nan
        d["z_e" + suf] = np.nan
        for v in VARS:
            mv = d["variable"] == v
            pv = mv & p_mask
            mr, sr = d.loc[pv, nom_r].mean(), d.loc[pv, nom_r].std(ddof=1)
            me, s_e = d.loc[pv, nom_e].mean(), d.loc[pv, nom_e].std(ddof=1)
            d.loc[mv, "z_r" + suf] = (d.loc[mv, nom_r] - mr) / sr
            d.loc[mv, "z_e" + suf] = (d.loc[mv, nom_e] - me) / s_e
            if suf == "":
                kv[v] = sr / s_e
                detail.setdefault("reduction", {})[v] = {"moy_rev": mr, "s_r": sr, "moy_err": me,
                                                       "s_e": s_e, "k_v": sr / s_e}
            else:
                detail.setdefault("reduction_med", {})[v] = {"n_lignes": int(pv.sum()),
                                                           "n_presentes": int(d.loc[pv, nom_r].notna().sum()),
                                                           "s_r": sr, "s_e": s_e}
    out_k_moyen = float(np.mean([kv[v] for v in VARS]))

    # étape 2 — L recalculé (identique au fichier, contrôle 12) ; on utilise celui du fichier
    d["L"] = d["grande_nouvelle"].astype(float)
    for v in VARS:
        pv = (d["variable"] == v) & p_mask
        detail.setdefault("Q_v", {})[v] = float(np.quantile(np.abs(d.loc[pv, "surprise"]), 2 / 3))

    P = d[p_mask].copy()
    out["n_principal"] = int(len(P))

    # étape 3-5
    r = mco(P, "z_e", "z_r", "L", 4)
    c = float(r["beta"][15])
    et4 = se(r, 15)
    bv = r["beta"][10:15]
    b_moyen = float(np.mean(bv))
    out["c"] = c
    out["et_c_dk4"] = et4
    out["t_c"] = c / et4
    out["borne_basse_ic90"] = c - Z90 * et4
    out["borne_haute_ic90"] = c + Z90 * et4

    # biais mécanique
    m0 = {v: P.loc[(P.variable == v) & (P.L == 0), "z_r"].mean() for v in VARS}
    m1 = {v: P.loc[(P.variable == v) & (P.L == 1), "z_r"].mean() for v in VARS}
    dev0 = (P.loc[P.L == 0, "z_r"] - P.loc[P.L == 0, "variable"].map(m0)) ** 2
    dev1 = (P.loc[P.L == 1, "z_r"] - P.loc[P.L == 1, "variable"].map(m1)) ** 2
    a, A = float(dev0.mean()), float(dev1.mean())
    out["rapport_variance_revision"] = A / a
    out["b_moyen"] = b_moyen
    out["k_moyen"] = out_k_moyen
    out["pente_moyenne_grandes"] = b_moyen + c
    out["biais_mecanique_nu20"] = (2 * b_moyen + out_k_moyen) * 0.10 * (1 / a - 1 / A)
    out["seuil_survie_bas"] = max(0.10, out["biais_mecanique_nu20"])
    out["borne_basse_moins_seuil"] = out["borne_basse_ic90"] - out["seuil_survie_bas"]
    out["marge_indecision"] = min(out["seuil_survie_bas"] - out["borne_basse_ic90"],
                                  out["borne_haute_ic90"] - 0.40)
    detail["a"], detail["A"] = a, A
    detail["b_v"] = dict(zip(VARS, map(float, bv)))
    detail["alpha_v"] = dict(zip(VARS, map(float, r["beta"][0:5])))
    detail["delta_v"] = dict(zip(VARS, map(float, r["beta"][5:10])))
    detail["et_b_v_dk4"] = dict(zip(VARS, [float(np.sqrt(r["V"][i, i])) for i in range(10, 15)]))
    detail["et_b_moyen_dk4"] = float(np.sqrt(np.ones(5) @ r["V"][10:15, 10:15] @ np.ones(5)) / 5)
    g = np.r_[np.zeros(10), np.ones(5) / 5, 1.0]
    detail["et_pente_moyenne_grandes_dk4"] = float(np.sqrt(g @ r["V"] @ g))
    detail["pente_grandes_v"] = {v: float(bv[i] + c) for i, v in enumerate(VARS)}
    detail["et_pente_grandes_v_dk4"] = {}
    for i, v in enumerate(VARS):
        gv = np.zeros(16); gv[10 + i] = 1; gv[15] = 1
        detail["et_pente_grandes_v_dk4"][v] = float(np.sqrt(gv @ r["V"] @ gv))

    # exclusions d'épisodes
    ts, cs = {}, {}
    for k in range(1, 8):
        code = f"E{k}"
        sub = P[P["episode"] != code]
        rk = mco(sub, "z_e", "z_r", "L", 4)
        if rk is None:
            cs[k], ts[k] = 0.0, 0.0
            detail.setdefault("incidents", []).append(f"exclusion {code} : n<50 ou X'X singulière")
        else:
            cs[k] = float(rk["beta"][15])
            ts[k] = cs[k] / se(rk, 15)
        out[f"c_sans_{code}"] = cs[k]
        detail.setdefault("exclusions", {})[code] = {"n": int(len(sub)), "c": cs[k], "t": ts[k],
                                                    "et_dk4": cs[k] / ts[k] if ts[k] else 0.0}
    tmin = min(ts.values())
    out["t_min_sans_episode"] = tmin
    out["c_min_sans_episode"] = min(cs.values())
    out["episode_t_min"] = min(k for k in ts if ts[k] == tmin)
    out["conflit_robustesse"] = int(out["borne_basse_ic90"] > out["seuil_survie_bas"]
                                    and out["borne_haute_ic90"] >= 0.40
                                    and tmin < 1 and out["c_min_sans_episode"] > 0)

    out["n_grands"] = int((P.L == 1).sum())
    out["n_trimestres"] = int(P["t_cible"].nunique())
    out["n_trimestres_grands"] = int(P.loc[P.L == 1, "t_cible"].nunique())
    et_iid = float(np.sqrt(r["Viid"][15, 15]))
    out["et_c_iid"] = et_iid
    out["n_effectif"] = out["n_principal"] * (et_iid / et4) ** 2

    # réordonner selon champs_verification plus tard ; secondaires
    # S2
    r8 = mco(P, "z_e", "z_r", "L", 8)
    r0 = mco(P, "z_e", "z_r", "L", 0)
    out["et_c_dk8"] = se(r8, 15)
    out["et_c_dk0"] = se(r0, 15)
    # S3
    C = d[d["complete"] == 1].copy()
    r3 = mco(C, "z_e", "z_r", "L", 4)
    out["c_avec_pandemie"], out["et_c_avec_pandemie_dk4"] = float(r3["beta"][15]), se(r3, 15)
    detail["n_S3"] = int(len(C))
    # S4
    S4 = P[P["t_cible"] >= 7940]
    r4 = mco(S4, "z_e", "z_r", "L", 4)
    out["c_depuis_1985"], out["et_c_depuis_1985_dk4"] = float(r4["beta"][15]), se(r4, 15)
    detail["n_S4"] = int(len(S4))
    # S5
    S5 = P[P["t_cible"] <= 8079]
    r5 = mco(S5, "z_e", "z_r", "L", 4)
    out["c_avant_2020"], out["et_c_avant_2020_dk4"] = float(r5["beta"][15]), se(r5, 15)
    detail["n_S5"] = int(len(S5))
    # S6
    S6 = P.dropna(subset=["z_r_med", "z_e_med"])
    r6 = mco(S6, "z_e_med", "z_r_med", "L", 4)
    out["c_mediane"], out["et_c_mediane_dk4"] = float(r6["beta"][15]), se(r6, 15)
    detail["n_S6"] = int(len(S6))
    # S7
    P["Lp"] = (np.abs(P["z_r"]) > 1).astype(float)
    r7 = mco(P, "z_e", "z_r", "Lp", 4)
    out["c_coupure_revision"], out["et_c_coupure_revision_dk4"] = float(r7["beta"][15]), se(r7, 15)
    detail["n_Lp1"] = int(P["Lp"].sum())
    # S1
    r1 = mco(P, "z_e", "z_r", "L", 4, par_variable=True)
    for i, v in enumerate(VARS):
        out[f"c_{v}"] = float(r1["beta"][15 + i])
    for i, v in enumerate(VARS):
        out[f"et_c_{v}_dk4"] = se(r1, 15 + i)
    detail["S1_b_v"] = dict(zip(VARS, map(float, r1["beta"][10:15])))
    detail["S1_et_b_v"] = {v: se(r1, 10 + i) for i, v in enumerate(VARS)}
    detail["n_grands_par_variable"] = {v: int(((P.variable == v) & (P.L == 1)).sum()) for v in VARS}
    detail["n_principal_par_variable"] = {v: int((P.variable == v).sum()) for v in VARS}

    ordre = ["n_violations_schema", "n_principal", "c", "et_c_dk4", "t_c", "borne_basse_ic90",
             "borne_haute_ic90", "rapport_variance_revision", "b_moyen", "k_moyen",
             "pente_moyenne_grandes", "biais_mecanique_nu20", "seuil_survie_bas",
             "borne_basse_moins_seuil", "marge_indecision", "t_min_sans_episode",
             "c_min_sans_episode", "episode_t_min", "conflit_robustesse", "n_grands",
             "n_trimestres", "n_trimestres_grands", "et_c_iid", "n_effectif",
             "c_sans_E1", "c_sans_E2", "c_sans_E3", "c_sans_E4", "c_sans_E5", "c_sans_E6",
             "c_sans_E7", "et_c_dk8", "et_c_dk0", "c_avec_pandemie", "et_c_avec_pandemie_dk4",
             "c_depuis_1985", "et_c_depuis_1985_dk4", "c_avant_2020", "et_c_avant_2020_dk4",
             "c_mediane", "et_c_mediane_dk4", "c_coupure_revision", "et_c_coupure_revision_dk4",
             "c_PGDP", "c_RGDP", "c_UNEMP", "c_CPI", "c_TBILL", "et_c_PGDP_dk4", "et_c_RGDP_dk4",
             "et_c_UNEMP_dk4", "et_c_CPI_dk4", "et_c_TBILL_dk4"]
    assert set(ordre) == set(out), set(ordre) ^ set(out)
    temoin = {k: out[k] for k in ordre}
    with open(os.path.join(ICI, "temoin.json"), "w") as f:
        json.dump(temoin, f, indent=2)
    with open(os.path.join(ICI, "resultats_detail.json"), "w") as f:
        json.dump(detail, f, indent=2, ensure_ascii=False, default=str)
    for k in ordre:
        print(f"{k:28s} {temoin[k]}")
    print(json.dumps(detail, indent=1, ensure_ascii=False, default=str))
    figure(temoin, detail, r, r1)


def figure(t, det, r, r1):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [3, 1.3]})
    gris, orange = "#4a6fa5", "#d07a2b"
    x = np.arange(len(VARS) + 1)
    noms = VARS + ["moyenne"]
    # pentes petites (b_v) et grandes (b_v + c) du modèle principal (c commun)
    b = [det["b_v"][v] for v in VARS] + [t["b_moyen"]]
    eb = [det["et_b_v_dk4"][v] for v in VARS] + [det["et_b_moyen_dk4"]]
    g = [det["pente_grandes_v"][v] for v in VARS] + [t["pente_moyenne_grandes"]]
    eg = [det["et_pente_grandes_v_dk4"][v] for v in VARS] + [det["et_pente_moyenne_grandes_dk4"]]
    ax1.errorbar(x - 0.12, b, yerr=Z90 * np.array(eb), fmt="o", color=gris, capsize=3,
                 label="petites surprises (L = 0) : b_v")
    ax1.errorbar(x + 0.12, g, yerr=Z90 * np.array(eg), fmt="s", color=orange, capsize=3,
                 label="grandes surprises (L = 1) : b_v + c (c commun)")
    ax1.axhline(0, color="k", lw=0.6)
    ax1.set_xticks(x, noms)
    ax1.set_ylabel("pente de z_erreur sur z_révision\n(é.-t. d'erreur par é.-t. de révision)")
    ax1.set_title("Pentes par variable, modèle principal à c commun imposé (IC 90 %, DK 4 retards)",
                  fontsize=10)
    ax1.legend(fontsize=8, loc="upper left")
    # c commun et c_v (S1)
    cc = [t[f"c_{v}"] for v in VARS]
    ec = [t[f"et_c_{v}_dk4"] for v in VARS]
    xs = np.arange(len(VARS) + 1)
    ax2.errorbar(xs[:-1], cc, yerr=Z90 * np.array(ec), fmt="o", color="#777777", capsize=3,
                 label="c_v (S1, descriptif)")
    ax2.errorbar([xs[-1]], [t["c"]], yerr=[Z90 * t["et_c_dk4"]], fmt="D", color="k", capsize=4,
                 label="c commun (statistique principale)")
    ax2.axhline(0, color="k", lw=0.6)
    ax2.axhline(t["seuil_survie_bas"], color="#2b8a3e", ls="--", lw=1,
                label=f"plancher de biais = {t['seuil_survie_bas']:.2f}".replace('.', ','))
    ax2.axhline(0.40, color="#b22222", ls=":", lw=1.2, label="prédiction 0,40")
    ax2.set_xticks(xs, VARS + ["c"], rotation=45)
    ax2.set_title("Supplément de pente c (IC 90 %)", fontsize=10)
    ax2.legend(fontsize=7, loc="lower left")
    fig.suptitle((f"K20 — n = {t['n_principal']} lignes principales ; c = {t['c']:.3f} "
                  f"[IC 90 % : {t['borne_basse_ic90']:.3f} ; {t['borne_haute_ic90']:.3f}]").replace(".", ","), fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(ICI, "figure.png"), dpi=130)


if __name__ == "__main__":
    main()
