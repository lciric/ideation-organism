#!/usr/bin/env python3
"""F01 — statistique principale, garde et analyses secondaires (preenregistrement § 5).

Lit panel.csv seulement. Aucun tirage aleatoire, donc aucune graine.
Usage : python3 -I analyse.py
Sorties : temoin.json (temoin de l'experimentateur), resultats.json (detail), figure.png
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import scipy.linalg
import scipy.sparse as sp

ICI = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, ICI)                     # construire.py (mon propre code, pas les donnees)
from construire import controles            # noqa: E402

F_PANEL = os.path.join(ICI, "panel.csv")
T16 = 2.12                                  # quantile 97,5 % de Student a 16 ddl (§ 5.2)
ANNEES = list(range(1974, 2014))
MIN_ORIGINE = 60
CIBLE = -0.30


# ----------------------------------------------------------------------------
# Moindres carres ordinaires a deux effets fixes + regresseurs supplementaires
# ----------------------------------------------------------------------------
def mco(df, cle1, extras, dense=False):
    """ret = effet[cle1] + effet[date] + extras @ coef + e, MCO non ponderes.

    L'indicatrice du premier mois (ordre chronologique) est omise.
    Renvoie (effets cle1, effets mois, coefs extras, rang, nb colonnes).
    """
    y = df["ret"].to_numpy(float)
    c1, n1 = pd.factorize(df[cle1], sort=True)
    c2, n2 = pd.factorize(df["date"], sort=True)
    n = len(df)
    lig = np.arange(n)
    D1 = sp.csr_matrix((np.ones(n), (lig, c1)), shape=(n, len(n1)))
    g = c2 > 0
    D2 = sp.csr_matrix((np.ones(g.sum()), (lig[g], c2[g] - 1)), shape=(n, len(n2) - 1))
    blocs = [D1, D2]
    if extras:
        blocs.append(sp.csr_matrix(np.column_stack([df[e].to_numpy(float) for e in extras])))
    X = sp.hstack(blocs).tocsr()
    if dense:                               # controle numerique : QR/SVD sur X dense
        coef, _, rang, _ = np.linalg.lstsq(X.toarray(), y, rcond=None)
    else:                                   # equations normales (X'X de taille ~700)
        A = (X.T @ X).toarray()
        coef, _, rang, _ = scipy.linalg.lstsq(A, X.T @ y, lapack_driver="gelsd")
    a = pd.Series(coef[:len(n1)], index=n1)
    l = pd.Series(np.concatenate([[0.0], coef[len(n1):len(n1) + len(n2) - 1]]), index=n2)
    b = dict(zip(extras, coef[len(n1) + len(n2) - 1:]))
    return a, l, b, int(rang), int(X.shape[1])


def jackknife(valeurs_g):
    v = np.asarray(valeurs_g, float)
    G = len(v)
    point = v.mean()
    return float(point), float(np.sqrt((G - 1) / G * np.sum((v - point) ** 2)))


# ----------------------------------------------------------------------------
# Ensembles
# ----------------------------------------------------------------------------
def charger():
    p = pd.read_csv(F_PANEL, dtype={"signal": str, "date": str, "statut": str})
    p["att"] = (p["statut"] == "attente").astype(float)
    p["av"] = ((p["statut"] == "attente") & (p["annee"] == p["annee_pub"] - 1)).astype(float)
    p["sig_statut"] = p["signal"] + "|" + p["statut"]
    n_or = p[p["statut"] == "origine"].groupby("signal").size()
    K = set(n_or[n_or >= MIN_ORIGINE].index)
    return p, K


def base_U(p, K):
    return p[(p["dans_fenetre"] == 1) & p["statut"].isin(["origine", "attente"]) & p["signal"].isin(K)]


def base_T_principal(p):
    return p[(p["dans_fenetre"] == 1) & (p["statut"] == "publie")]


def base_T_s1a(p):                          # annees P a P+4
    return p[(p["dans_fenetre"] == 1) & (p["annee"] >= p["annee_pub"]) & (p["annee"] <= p["annee_pub"] + 4)]


def restreindre_T(Tc, U):
    """T : anomalie et mois presents dans U (§ 5.1)."""
    return Tc[Tc["signal"].isin(set(U["signal"])) & Tc["date"].isin(set(U["date"]))]


# ----------------------------------------------------------------------------
# Estimateurs par imputation
# ----------------------------------------------------------------------------
def imputation(U, Tc, variante="principal", dense=False):
    """Etapes 1 et 2. variante = 'principal' (a[i] + b*att) ou 's2' (effet (anomalie, statut))."""
    if variante == "principal":
        a, l, b, rang, ncol = mco(U, "signal", ["att"], dense)
        T = restreindre_T(Tc, U)
        pred = T["signal"].map(a).to_numpy() + T["date"].map(l).to_numpy() + b["att"]
        b_att = float(b["att"])
    else:
        a, l, b, rang, ncol = mco(U, "sig_statut", [], dense)
        avec_att = set(U.loc[U["statut"] == "attente", "signal"])
        T = restreindre_T(Tc, U)
        T = T[T["signal"].isin(avec_att)]
        pred = (T["signal"] + "|attente").map(a).to_numpy() + T["date"].map(l).to_numpy()
        b_att = None
    tau = T["ret"].to_numpy() - pred
    assert np.isfinite(tau).all(), "prediction non definie pour une ligne de T"
    tau_bar = float(tau.mean())
    m_bar = float(T["moy_origine"].mean())
    return {"theta": tau_bar / m_bar, "tau_bar": tau_bar, "m_bar": m_bar, "b_attente": b_att,
            "n_T": int(len(T)), "n_anomalies_T": int(T["signal"].nunique()),
            "n_U": int(len(U)), "n_attente_U": int((U["statut"] == "attente").sum()),
            "rang": rang, "ncol": ncol, "T": T, "tau": tau}


def analyse_imputation(U, Tc, variante="principal"):
    """Echantillon complet + jackknife par annee civile."""
    complet = imputation(U, Tc, variante)
    dense = imputation(U, Tc, variante, dense=True)
    Tfull = complet["T"]
    blocs = [g for g in ANNEES if (U["annee"] == g).any() or (Tfull["annee"] == g).any()]
    rep = []
    for g in blocs:
        r = imputation(U[U["annee"] != g], Tc[Tc["annee"] != g], variante)
        rep.append({"annee": g, **{k: r[k] for k in ("theta", "tau_bar", "m_bar", "b_attente",
                                                      "n_T", "n_anomalies_T", "n_U", "rang", "ncol")}})
    theta_point, se = jackknife([r["theta"] for r in rep])
    _, se_tau = jackknife([r["tau_bar"] for r in rep])
    out = {k: complet[k] for k in ("theta", "tau_bar", "m_bar", "b_attente", "n_T", "n_anomalies_T",
                                   "n_U", "n_attente_U", "rang", "ncol")}
    out.update({
        "theta_point": theta_point, "se_theta": se, "se_tau_bar_jackknife": se_tau,
        "borne_basse_ic95": complet["theta"] - T16 * se,
        "borne_haute_ic95": complet["theta"] + T16 * se,
        "n_blocs": len(blocs),
        "ecart_max_dense_vs_normales": max(abs(complet[k] - dense[k]) for k in ("theta", "tau_bar")),
        "repliques_rang_incomplet": [r["annee"] for r in rep if r["rang"] < r["ncol"]],
        "repliques": rep,
    })
    if variante == "principal":
        _, out["se_b_attente_jackknife"] = jackknife([r["b_attente"] for r in rep])
    return out, complet


def garde_avance(U):
    """§ 5.3 : coefficient d de l'indicatrice 'derniere annee avant publication'."""
    _, _, b, rang, ncol = mco(U, "signal", ["att", "av"])
    _, _, bd, _, _ = mco(U, "signal", ["att", "av"], dense=True)
    blocs = [g for g in ANNEES if (U["annee"] == g).any()]
    rep = []
    for g in blocs:
        Ug = U[U["annee"] != g]
        _, _, bg, rg, ncg = mco(Ug, "signal", ["att", "av"])
        rep.append({"annee": g, "d": float(bg["av"]), "rang": rg, "ncol": ncg,
                    "n_av": int(Ug["av"].sum())})
    d_point, se_d = jackknife([r["d"] for r in rep])
    return {"d": float(b["av"]), "b_avec_avance": float(b["att"]), "d_point": d_point, "se_d": se_d,
            "t_avance": float(b["av"]) / se_d, "n_lignes_av": int(U["av"].sum()),
            "n_blocs": len(blocs), "rang": rang, "ncol": ncol,
            "ecart_max_dense_vs_normales": abs(float(b["av"]) - float(bd["av"])),
            "repliques_rang_incomplet": [r["annee"] for r in rep if r["rang"] < r["ncol"]],
            "repliques": rep}


def s3_mclean_pontiff(p, K=None):
    """§ 5.4 S3 : effets fixes d'anomalie et de mois, indicatrices attente et publiee."""
    S = p[(p["dans_fenetre"] == 1) & p["statut"].isin(["origine", "attente", "publie", "apres"])].copy()
    if K is not None:
        S = S[S["signal"].isin(K)]
    S["pub"] = S["statut"].isin(["publie", "apres"]).astype(float)

    def une(Sg, dense=False):
        _, _, b, rang, ncol = mco(Sg, "signal", ["att", "pub"], dense)
        diff = float(b["pub"] - b["att"])
        mA = float(Sg.groupby("signal")["moy_origine"].first().mean())   # une valeur par anomalie
        mB = float(Sg["moy_origine"].mean())                              # sur les lignes de l'echantillon
        mC = float(Sg.loc[Sg["pub"] == 1, "moy_origine"].mean())          # sur les lignes 'publiee'
        return {"coef_attente": float(b["att"]), "coef_publiee": float(b["pub"]), "difference": diff,
                "moy_A_par_anomalie": mA, "moy_B_par_ligne": mB, "moy_C_lignes_publiees": mC,
                "ratio_A": diff / mA, "ratio_B": diff / mB, "ratio_C": diff / mC,
                "rang": rang, "ncol": ncol}

    complet = une(S)
    dense = une(S, dense=True)
    blocs = [g for g in ANNEES if (S["annee"] == g).any()]
    rep = [{"annee": g, **une(S[S["annee"] != g])} for g in blocs]
    out = dict(complet)
    for k in ("coef_attente", "coef_publiee", "difference", "ratio_A", "ratio_B", "ratio_C"):
        _, out["se_" + k] = jackknife([r[k] for r in rep])
    out.update({"n_lignes": int(len(S)), "n_anomalies": int(S["signal"].nunique()),
                "n_lignes_par_statut": {k: int(v) for k, v in S["statut"].value_counts().items()},
                "n_blocs": len(blocs),
                "ecart_max_dense_vs_normales": max(abs(complet[k] - dense[k]) for k in ("coef_attente", "coef_publiee")),
                "repliques_rang_incomplet": [r["annee"] for r in rep if r["rang"] < r["ncol"]]})
    return out


def fr(x, nd=3):
    """Nombre signe, virgule decimale, vrai signe moins."""
    return f"{x:+.{nd}f}".replace("-", "\u2212").replace(".", ",")


def sans_repliques(d):
    return {k: v for k, v in d.items() if k != "repliques"}


# ----------------------------------------------------------------------------
def figure(res, chemin):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    SURF, TXT, TXT2, GRILLE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
    BLEU, GRIS = "#2a78d6", "#8a8984"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "text.color": TXT,
                         "axes.edgecolor": GRILLE, "axes.labelcolor": TXT2,
                         "xtick.color": TXT2, "ytick.color": TXT2})
    pr = res["principal"]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 5.6), facecolor=SURF,
                                  gridspec_kw={"width_ratios": [1.15, 1], "wspace": 0.42})

    # --- panneau gauche : theta et son intervalle, puis les descriptifs -----
    lignes = [("Principal (§ 5.1)\njugé par la règle du § 7", pr["theta"], pr["se_theta"], BLEU, True)]
    s = res["secondaires_descriptives"]
    for nom, cle in [("S1a — descriptif\nT = années P à P+4", "S1a"),
                     ("S1b — descriptif\ntémoins arrêtés à P−2", "S1b"),
                     ("S2 — descriptif\neffet (anomalie, statut)", "S2")]:
        lignes.append((nom, s[cle]["theta"], s[cle]["se_theta"], GRIS, False))
    lignes.append(("S3 — descriptif\nMcLean-Pontiff, écart / moyenne\nd'origine (lecture A)",
                   s["S3"]["ratio_A"], s["S3"]["se_ratio_A"], GRIS, False))
    ax.set_facecolor(SURF)
    ax.axvspan(-0.40, -0.20, color="#e9e8e3", lw=0, zorder=0)
    ax.axvline(0, color=TXT2, lw=1, zorder=1)
    ax.axvline(CIBLE, color=TXT2, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.axvline(-0.10, color=TXT2, lw=0.8, ls=(0, (1, 3)), zorder=1)
    ys = list(range(len(lignes)))[::-1]
    for y, (nom, th, se, coul, principal) in zip(ys, lignes):
        ax.plot([th - T16 * se, th + T16 * se], [y, y], color=coul, lw=2.4 if principal else 1.6,
                solid_capstyle="round", zorder=3)
        ax.plot([th], [y], "o", ms=9 if principal else 7, color=coul, mec=SURF, mew=2, zorder=4)
        ax.annotate(f"{fr(th)}  [{fr(th - T16 * se)} ; {fr(th + T16 * se)}]", (th, y),
                    xytext=(0, 11), textcoords="offset points", ha="center", fontsize=9,
                    bbox=dict(fc=SURF, ec="none", pad=1.2), zorder=5,
                    color=TXT if principal else TXT2)
    ax.set_yticks(ys)
    ax.set_yticklabels([l[0] for l in lignes], fontsize=9)
    ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(lignes) - 0.25)
    bas = min(th - T16 * se for _, th, se, _, _ in lignes)
    haut = max(th + T16 * se for _, th, se, _, _ in lignes)
    ax.set_xlim(min(bas, -0.45) - 0.05, max(haut, 0.05) + 0.05)
    haut_txt = len(lignes) - 0.33
    ax.text(0.008, haut_txt, "0", ha="left", va="bottom", fontsize=8.5, color=TXT2)
    ax.text(CIBLE, haut_txt, "prédiction −0,30\n(plage −0,40 à −0,20)", ha="center", va="bottom",
            fontsize=8.5, color=TXT2)
    ax.text(-0.10, haut_txt, "seuil −0,10\n", ha="center", va="bottom", fontsize=8.5, color=TXT2)
    ax.set_xlabel("θ = écart traité − contrefactuel, en part du rendement d'origine\n"
                  "point : estimation sur l'échantillon complet ; trait : ± 2,12 × erreur type jackknife (40 années)")
    ax.grid(axis="x", color=GRILLE, lw=0.6, zorder=0)
    from matplotlib.ticker import FuncFormatter
    virgule = FuncFormatter(lambda v, _: f"{v:.2f}".replace("-", "\u2212").replace(".", ","))
    ax.xaxis.set_major_formatter(virgule)
    ax2.yaxis.set_major_formatter(virgule)
    for c in ("top", "right", "left"):
        ax.spines[c].set_visible(False)
    ax.set_title("θ et intervalle à 95 %", loc="left", fontsize=11, pad=34, color=TXT)

    # --- panneau droit : theta_g, une annee retiree a la fois ----------------
    rep = pr["repliques"]
    an = [r["annee"] for r in rep]
    tg = [r["theta"] for r in rep]
    ax2.set_facecolor(SURF)
    ax2.axhline(pr["theta"], color=BLEU, lw=1.2, zorder=2)
    ax2.axhline(0, color=TXT2, lw=1, zorder=1)
    ax2.axhline(CIBLE, color=TXT2, lw=1, ls=(0, (4, 3)), zorder=1)
    ax2.plot(an, tg, "o", ms=6, color=BLEU, mec=SURF, mew=1.2, zorder=3)
    i_min, i_max = int(np.argmin(tg)), int(np.argmax(tg))
    for i in {i_min, i_max}:
        ax2.annotate(f"sans {an[i]} : {fr(tg[i])}", (an[i], tg[i]), xytext=(-6, 9 if i == i_max else -15),
                     textcoords="offset points", ha="right", fontsize=8.5, color=TXT2)
    ax2.text(0, 1.02, f"trait bleu : θ sur l'échantillon complet ({fr(pr['theta'])})",
             transform=ax2.transAxes, va="bottom", ha="left", fontsize=8.5, color=TXT2)
    ax2.text(an[0], CIBLE, " prédiction −0,30", va="bottom", ha="left", fontsize=8.5, color=TXT2)
    ax2.set_ylim(min(min(tg), CIBLE) - 0.05, max(max(tg), 0) + 0.05)
    ax2.set_xlabel("année civile retirée (bloc du jackknife)")
    ax2.set_ylabel("θ recalculé sans cette année")
    ax2.grid(axis="y", color=GRILLE, lw=0.6, zorder=0)
    for c in ("top", "right"):
        ax2.spines[c].set_visible(False)
    ax2.set_title("Sensibilité : θ avec une année retirée", loc="left", fontsize=11, pad=34, color=TXT)

    fig.suptitle("F01 — effet propre à la publication, témoins = anomalies pas encore publiées (1974-2013)",
                 x=0.012, y=0.985, ha="left", fontsize=12.5, color=TXT)
    fig.subplots_adjust(left=0.185, right=0.985, top=0.80, bottom=0.17)
    fig.savefig(chemin, dpi=160, facecolor=SURF)
    plt.close(fig)


# ----------------------------------------------------------------------------
def main():
    p, K = charger()
    U = base_U(p, K)
    res = {}

    # effectifs a chaque filtre
    pub_fen = base_T_principal(p)
    T0 = restreindre_T(pub_fen, U)
    res["filtres"] = {
        "lignes_panel": int(len(p)), "anomalies_panel": int(p["signal"].nunique()),
        "lignes_dans_fenetre": int((p["dans_fenetre"] == 1).sum()),
        "anomalies_K_au_moins_60_origine": len(K),
        "anomalies_hors_K": sorted(set(p["signal"]) - K),
        "U_lignes": int(len(U)), "U_origine": int((U["statut"] == "origine").sum()),
        "U_attente": int((U["statut"] == "attente").sum()),
        "U_anomalies": int(U["signal"].nunique()), "U_mois": int(U["date"].nunique()),
        "anomalies_K_sans_ligne_U": sorted(K - set(U["signal"])),
        "publie_dans_fenetre": int(len(pub_fen)), "publie_dans_fenetre_anomalies": int(pub_fen["signal"].nunique()),
        "publie_retire_anomalie_absente_de_U": int((~pub_fen["signal"].isin(set(U["signal"]))).sum()),
        "anomalies_publie_absentes_de_U": sorted(set(pub_fen["signal"]) - set(U["signal"])),
        "publie_retire_mois_absent_de_U": int((pub_fen["signal"].isin(set(U["signal"]))
                                               & ~pub_fen["date"].isin(set(U["date"]))).sum()),
        "T_lignes": int(len(T0)), "T_anomalies": int(T0["signal"].nunique()),
        "T_lignes_par_annee": {int(k): int(v) for k, v in T0.groupby("annee").size().items()},
        "U_attente_par_annee": {int(k): int(v) for k, v in U[U["statut"] == "attente"].groupby("annee").size().items()},
        "U_anomalies_par_annee_min": int(U.groupby("date")["signal"].nunique().min()),
    }
    nT = T0.groupby("annee").size().to_numpy(float)
    res["filtres"]["blocs_effectifs_T"] = float(nT.sum() ** 2 / (nT ** 2).sum())

    # --- principal ----------------------------------------------------------
    pr, complet = analyse_imputation(U, pub_fen, "principal")
    pr["marge_ambiguite"] = min(pr["borne_haute_ic95"], CIBLE - pr["borne_basse_ic95"])
    res["principal"] = pr

    Ua = U[U["statut"] == "attente"]
    res["descriptif_attente"] = {
        "b_attente": pr["b_attente"], "se_b_attente_jackknife": pr["se_b_attente_jackknife"],
        "moy_origine_lignes_T": pr["m_bar"],
        "moy_origine_lignes_attente_U": float(Ua["moy_origine"].mean()),
        "moy_origine_par_anomalie_U": float(U.groupby("signal")["moy_origine"].first().mean()),
    }
    for k in ("moy_origine_lignes_T", "moy_origine_lignes_attente_U", "moy_origine_par_anomalie_U"):
        res["descriptif_attente"]["ratio_sur_" + k] = pr["b_attente"] / res["descriptif_attente"][k]

    # --- garde --------------------------------------------------------------
    res["garde"] = garde_avance(U)

    # --- secondaires (descriptives) -----------------------------------------
    sec = {}
    s1a, _ = analyse_imputation(U, base_T_s1a(p), "principal")
    sec["S1a"] = s1a
    U_b = U[U["av"] == 0]
    s1b, c1b = analyse_imputation(U_b, pub_fen, "principal")
    s1b["T_identique_au_principal"] = int(set(zip(c1b["T"]["signal"], c1b["T"]["date"]))
                                          == set(zip(complet["T"]["signal"], complet["T"]["date"])))
    s1b["n_lignes_attente_retirees"] = int(len(U) - len(U_b))
    sec["S1b"] = s1b
    s2, _ = analyse_imputation(U, pub_fen, "s2")
    sec["S2"] = s2
    sec["S3"] = s3_mclean_pontiff(p, K)
    sec["S3_sans_restriction_K"] = s3_mclean_pontiff(p, None)
    res["secondaires_descriptives"] = sec

    # --- schema (refait sur panel.csv) --------------------------------------
    j = controles({"exclusions": {}})
    res["controles_schema"] = j["controles"]

    temoin = {
        "theta": pr["theta"], "se_theta": pr["se_theta"],
        "borne_basse_ic95": pr["borne_basse_ic95"], "borne_haute_ic95": pr["borne_haute_ic95"],
        "marge_ambiguite": pr["marge_ambiguite"], "tau_bar": pr["tau_bar"], "m_bar": pr["m_bar"],
        "b_attente": pr["b_attente"], "t_avance": res["garde"]["t_avance"],
        "n_lignes_traitees": pr["n_T"], "n_anomalies_traitees": pr["n_anomalies_T"],
        "n_lignes_attente": pr["n_attente_U"], "n_blocs": pr["n_blocs"],
        "n_violations_schema": j["n_violations_schema"],
    }
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, indent=2)
    with open(os.path.join(ICI, "resultats.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    figure(res, os.path.join(ICI, "figure.png"))

    print("=== TEMOIN ===")
    print(json.dumps(temoin, indent=2))
    print("=== FILTRES ===")
    print(json.dumps(res["filtres"], ensure_ascii=False, indent=1))
    print("=== PRINCIPAL (hors repliques) ===")
    print(json.dumps(sans_repliques(pr), indent=1))
    print("=== ATTENTE — DESCRIPTIF ===")
    print(json.dumps(res["descriptif_attente"], indent=1))
    print("=== GARDE ===")
    print(json.dumps(sans_repliques(res["garde"]), indent=1))
    print("=== SECONDAIRES — DESCRIPTIF ===")
    print(json.dumps({k: sans_repliques(v) for k, v in sec.items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
