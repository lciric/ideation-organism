#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F04-bis — analyse préinscrite (statistique principale, estimations d'accompagnement, S1 à S3).

Entrées : F04-bis_analyse.csv (fichier d'analyse) ; donnees/fy2021-mc-vs-hs-combined.csv (fichier brut B, pour S3 seulement).
Sorties : temoin.json (les douze champs de la règle), resultats_analyse.json (tout le reste), figure.png.
Aucun tirage aléatoire : le calcul est déterministe.
Lancer :  python3 -I analyse.py
"""
import csv
import datetime as dt
import io
import json
import math
import os

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
ANALYSE = os.path.join(ICI, "F04-bis_analyse.csv")
BRUT_B = os.path.join(ICI, "donnees", "fy2021-mc-vs-hs-combined.csv")
T_CRIT = 2.365      # Student, 7 degrés de liberté, 95 % bilatéral (préinscription, section 5)
SEUIL = 0.9         # pb (préinscription, section 7)

COLONNES = [
    "id_ligne", "cusip", "terme_api", "echeance", "date_adjudication", "mois",
    "date_j", "date_jm5", "date_jp5",
    "cmt_jm5", "cmt_j", "cmt_jp5", "gsw_jm5", "gsw_j", "gsw_jp5",
    "hs_jm5", "hs_j", "hs_jp5", "mc_jm5", "mc_j", "mc_jp5",
    "dans_exercice", "complet", "fenetre_propre",
]
TAUX = COLONNES[9:21]
SUF = ("jm5", "j", "jp5")
DEBUT, FIN = "2020-10-01", "2021-09-30"


# --------------------------------------------------------------------------- contrôles de schéma (section 4)
def schema(chemin):
    brut = open(chemin, "rb").read()
    lignes = list(csv.reader(io.StringIO(brut.decode("utf-8"), newline="")))
    entete, corps = lignes[0], lignes[1:]
    L = [dict(zip(entete, l)) for l in corps]
    c = {}
    c["1"] = entete == COLONNES and brut[:3] != b"\xef\xbb\xbf" and all(len(l) == 24 for l in corps)
    if not c["1"]:
        return c
    ids = [r["id_ligne"] for r in L]
    c["2"] = (len(set(ids)) == len(ids) and all(r["echeance"] in ("10", "20", "30") for r in L)
              and all(r[k] in ("0", "1") for r in L for k in ("dans_exercice", "complet", "fenetre_propre")))
    # Les dates AAAA-MM-JJ se comparent comme des chaînes ; on vérifie d'abord qu'elles sont valides.
    try:
        for r in L:
            for k in ("date_adjudication", "date_j", "date_jm5", "date_jp5"):
                dt.date.fromisoformat(r[k])
        dates_ok = True
    except ValueError:
        dates_ok = False
    c["3"] = dates_ok and all(
        r["date_jm5"] < r["date_j"] < r["date_jp5"] and r["date_j"] == r["date_adjudication"]
        and DEBUT <= r["date_adjudication"] <= FIN and r["mois"] == r["date_adjudication"][:7] for r in L)
    c["4"] = all((r["dans_exercice"] == "1") == (r["date_jm5"] >= DEBUT and r["date_jp5"] <= FIN) for r in L)
    c["5"] = all((r["complet"] == "1") == all(r[k] != "" for k in TAUX) for r in L)
    f = float
    c["6"] = (all(-1 <= f(r[k]) <= 20 for r in L for k in TAUX if r[k] != "")
              and all(abs(f(r["cmt_" + s]) - f(r["gsw_" + s])) <= 1 for r in L for s in SUF
                      if r["cmt_" + s] != "" and r["gsw_" + s] != ""))
    hm = [abs(f(r["hs_" + s]) - f(r["mc_" + s])) for r in L for s in SUF if r["hs_" + s] != "" and r["mc_" + s] != ""]
    c["7"] = all(x <= 0.25 for x in hm) and any(x > 0 for x in hm)
    hc = [abs(f(r["hs_" + s]) - f(r["cmt_" + s])) for r in L for s in SUF if r["hs_" + s] != "" and r["cmt_" + s] != ""]
    c["8"] = all(x <= 0.0051 for x in hc)
    n_ex = sum(r["dans_exercice"] == "1" for r in L)
    c["9"] = len(L) == 24 and 20 <= n_ex <= 24
    return c


def et_groupee(x, grappes):
    """Erreur type groupée : (1/N) * racine( G/(G-1) * somme_g S_g^2 ), S_g = somme des écarts à la moyenne dans g."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    ecarts = pd.Series(x - x.mean())
    s_g = ecarts.groupby(np.asarray(grappes)).sum()
    g = len(s_g)
    return (1.0 / n) * math.sqrt(g / (g - 1) * float((s_g ** 2).sum()))


def main():
    controles = schema(ANALYSE)
    schema_ok = int(len(controles) == 9 and all(controles.values()))

    df = pd.read_csv(ANALYSE, dtype={"id_ligne": str, "cusip": str, "terme_api": str, "mois": str,
                                     "date_adjudication": str, "date_j": str, "date_jm5": str, "date_jp5": str})
    P = df[(df["dans_exercice"] == 1) & (df["complet"] == 1) & (df["fenetre_propre"] == 1)].copy()
    N = len(P)
    G = P["mois"].nunique()

    for m in ("hs", "mc", "cmt"):
        P["v_" + m] = 100.0 * (2 * (P[m + "_j"] - P["gsw_j"]) - (P[m + "_jm5"] - P["gsw_jm5"])
                               - (P[m + "_jp5"] - P["gsw_jp5"]))
    # D par sa formule directe (section 5), sans passer par la courbe ajustée.
    P["d"] = 100.0 * (2 * (P["hs_j"] - P["mc_j"]) - (P["hs_jm5"] - P["mc_jm5"]) - (P["hs_jp5"] - P["mc_jp5"]))
    assert np.allclose(P["d"], P["v_hs"] - P["v_mc"], atol=1e-9)

    d_moy = float(P["d"].mean())
    d_et = et_groupee(P["d"], P["mois"])
    b_inf = d_moy - T_CRIT * d_et
    b_sup = d_moy + T_CRIT * d_et
    marge = min(SEUIL - b_inf, b_sup - SEUIL)
    v_hs_moy = float(P["v_hs"].mean())
    v_mc_moy = float(P["v_mc"].mean())
    v_mc_et = et_groupee(P["v_mc"], P["mois"])
    ecart_max = 100.0 * max(float((P["hs_" + s] - P["cmt_" + s]).abs().max()) for s in SUF)

    temoin = {
        "schema_ok": schema_ok,
        "n_adjudications": int(N),
        "n_grappes": int(G),
        "ecart_max_hs_fred_pb": ecart_max,
        "d_moyen_pb": d_moy,
        "d_erreur_type_pb": d_et,
        "d_borne_inf_95_pb": b_inf,
        "d_borne_sup_95_pb": b_sup,
        "marge_zone_grise": marge,
        "v_hs_moyen_pb": v_hs_moy,
        "v_mc_moyen_pb": v_mc_moy,
        "v_mc_erreur_type_pb": v_mc_et,
    }
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, indent=2)

    # ------------------------------------------------------------------ descriptif
    desc = {}
    desc["controles_schema"] = {k: int(v) for k, v in controles.items()}
    desc["d_ecart_type_pb_ddof1"] = float(P["d"].std(ddof=1))
    desc["d_demi_largeur_intervalle_pb"] = T_CRIT * d_et
    desc["d_valeurs"] = {str(int(k)) if float(k).is_integer() else str(k): int(v)
                         for k, v in P["d"].round(6).value_counts().sort_index().items()}
    desc["v_hs_erreur_type_pb"] = et_groupee(P["v_hs"], P["mois"])
    desc["v_hs_ecart_type_pb_ddof1"] = float(P["v_hs"].std(ddof=1))
    desc["v_mc_ecart_type_pb_ddof1"] = float(P["v_mc"].std(ddof=1))
    desc["identite_v_mc_egal_v_hs_moins_d"] = v_hs_moy - d_moy - v_mc_moy
    par_mois = P.groupby("mois").agg(n=("d", "size"), d_moyen=("d", "mean"), v_hs_moyen=("v_hs", "mean"),
                                     v_mc_moyen=("v_mc", "mean"))
    desc["par_mois"] = {m: {k: (int(v) if k == "n" else float(v)) for k, v in r.items()}
                        for m, r in par_mois.iterrows()}
    # Lecture voisine annoncée par la préinscription (« à très peu près, le test de Student sur les huit moyennes mensuelles »).
    mm = par_mois["d_moyen"].to_numpy()
    desc["student_sur_moyennes_mensuelles"] = {
        "moyenne": float(mm.mean()), "erreur_type": float(mm.std(ddof=1) / math.sqrt(len(mm))), "n_mois": int(len(mm))}

    # S1 — par échéance (sans erreur type).
    desc["S1_par_echeance"] = {
        str(int(e)): {"n": int(len(g)), "d_moyen_pb": float(g["d"].mean()), "v_hs_moyen_pb": float(g["v_hs"].mean()),
                      "v_mc_moyen_pb": float(g["v_mc"].mean())}
        for e, g in P.groupby("echeance")}

    # S2 — d'où vient D ; V du premier test recalculé avec cmt_*.
    desc["S2"] = {
        "hs_moins_mc_moyen_pb": {s: float((100.0 * (P["hs_" + s] - P["mc_" + s])).mean()) for s in SUF},
        "v_cmt_moyen_pb": float(P["v_cmt"].mean()),
        "v_hs_moyen_pb": v_hs_moy,
    }

    # S3 — les jours ordinaires, à partir du fichier brut B (toutes les dates du fichier, positions dans le fichier).
    B = pd.read_csv(BRUT_B, encoding="utf-8-sig")
    B["date"] = pd.to_datetime(B["date"], format="%m/%d/%Y")
    B = B.sort_values("date").reset_index(drop=True)
    s3 = {"n_dates": int(len(B))}
    tous_d = []
    jours_adj = {(r["date_j"], int(r["echeance"])) for _, r in P.iterrows()}
    for e in (10, 20, 30):
        ecart = 100.0 * (B[f"nominal_hs_cmt_{e}yr"] - B[f"nominal_mc_cmt_{e}yr"])
        dt_ = 2 * ecart - ecart.shift(5) - ecart.shift(-5)          # D(t), positions t-5 et t+5 dans le fichier
        valides = dt_.dropna()
        tous_d.append(valides)
        est_adj = B.loc[valides.index, "date"].dt.strftime("%Y-%m-%d").map(lambda x: (x, e) in jours_adj)
        s3[str(e)] = {
            "hs_moins_mc_moyenne_pb": float(ecart.mean()),
            "hs_moins_mc_ecart_type_pb_ddof1": float(ecart.std(ddof=1)),
            "hs_moins_mc_ecart_type_pb_ddof0": float(ecart.std(ddof=0)),
            "D_t_n": int(len(valides)),
            "D_t_moyenne_pb": float(valides.mean()),
            "D_t_ecart_type_pb_ddof1": float(valides.std(ddof=1)),
            "D_t_ecart_type_pb_ddof0": float(valides.std(ddof=0)),
            "D_t_n_jours_adjudication_de_P": int(est_adj.sum()),
        }
    ens = pd.concat(tous_d, ignore_index=True)
    s3["trois_echeances_reunies"] = {
        "D_t_n": int(len(ens)), "D_t_moyenne_pb": float(ens.mean()),
        "D_t_ecart_type_pb_ddof1": float(ens.std(ddof=1)), "D_t_ecart_type_pb_ddof0": float(ens.std(ddof=0))}
    desc["S3"] = s3

    desc["lignes_P"] = [
        {"id_ligne": r["id_ligne"], "echeance": int(r["echeance"]), "date_adjudication": r["date_adjudication"],
         "mois": r["mois"], "v_hs_pb": float(r["v_hs"]), "v_mc_pb": float(r["v_mc"]), "d_pb": float(r["d"]),
         "v_cmt_pb": float(r["v_cmt"])}
        for _, r in P.iterrows()]

    with open(os.path.join(ICI, "resultats_analyse.json"), "w", encoding="utf-8") as f:
        json.dump({"temoin": temoin, "descriptif": desc}, f, ensure_ascii=False, indent=2)

    print(json.dumps(temoin, indent=2))
    print(json.dumps({k: v for k, v in desc.items() if k != "lignes_P"}, ensure_ascii=False, indent=2))
    figure(P, temoin, os.path.join(ICI, "figure.png"))


def figure(P, t, chemin):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FOND, ENCRE, ENCRE2, GRILLE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
    C_HS, C_MC = "#2a78d6", "#eb6834"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "text.color": ENCRE,
                         "axes.edgecolor": GRILLE, "axes.labelcolor": ENCRE2,
                         "xtick.color": ENCRE2, "ytick.color": ENCRE2})
    P = P.sort_values(["date_adjudication", "echeance"]).reset_index(drop=True)
    n = len(P)
    y = np.arange(n)[::-1]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11, 7.6), dpi=150, gridspec_kw={"width_ratios": [1.55, 1], "wspace": 0.42}, facecolor=FOND)
    for ax in (ax1, ax2):
        ax.set_facecolor(FOND)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
        ax.grid(axis="x", color=GRILLE, linewidth=0.8)
        ax.set_axisbelow(True)

    # Panneau 1 : V de chaque adjudication sous les deux méthodes.
    for yi, (_, r) in zip(y, P.iterrows()):
        ax1.plot([r["v_mc"], r["v_hs"]], [yi, yi], color="#b9b8b2", linewidth=1.4, zorder=2, solid_capstyle="round")
    # Le rond HS est plus grand que le losange MC : quand D = 0, les deux marques restent visibles l'une sur l'autre.
    ax1.scatter(P["v_hs"], y, s=95, color=C_HS, edgecolor=FOND, linewidth=1.2, zorder=3,
                label="V avec l'ancienne méthode (HS)")
    ax1.scatter(P["v_mc"], y, s=26, color=C_MC, marker="D", edgecolor=FOND, linewidth=1.0, zorder=4,
                label="V avec la nouvelle méthode (MC)")
    ax1.axvline(0, color=ENCRE2, linewidth=0.9, zorder=1)
    ax1.axvline(t["v_hs_moyen_pb"], color=C_HS, linewidth=1.2, linestyle=(0, (4, 3)), zorder=1)
    ax1.axvline(t["v_mc_moyen_pb"], color=C_MC, linewidth=1.2, linestyle=(0, (1, 2)), zorder=1)
    ax1.set_yticks(y)
    ax1.set_yticklabels([f"{r['date_adjudication']} · {int(r['echeance'])} ans" for _, r in P.iterrows()], fontsize=8)
    # Séparateurs entre mois (les grappes).
    mois = P["mois"].tolist()
    for i in range(1, n):
        if mois[i] != mois[i - 1]:
            ax1.axhline(y[i] + 0.5, color=GRILLE, linewidth=0.8)
    ax1.set_ylim(-0.7, n - 0.3)
    ax1.set_xlabel("V de l'adjudication, en points de base")
    ax1.set_title(f"V de chacune des {n} réouvertures, calculé deux fois\n"
                  "(rond et losange superposés : même V avec les deux méthodes)",
                  fontsize=9.5, loc="left", color=ENCRE)
    ax1.text(t["v_hs_moyen_pb"] + 0.08, -2.3, f"moyenne HS\n{t['v_hs_moyen_pb']:.2f} pb".replace(".", ","),
             ha="left", va="center", fontsize=8.5, color=ENCRE)
    ax1.text(t["v_mc_moyen_pb"] - 0.08, -2.3, f"moyenne MC\n{t['v_mc_moyen_pb']:.2f} pb".replace(".", ","),
             ha="right", va="center", fontsize=8.5, color=ENCRE)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.065), ncol=2, frameon=False, fontsize=8.5,
               handletextpad=0.3, columnspacing=1.5)

    # Panneau 2 : D de chaque adjudication, puis moyenne et intervalle.
    ax2.axvline(0, color=ENCRE2, linewidth=0.9, zorder=1)
    ax2.axvline(0.9, color=ENCRE, linewidth=1.0, linestyle=(0, (5, 3)), zorder=1)
    ax2.scatter(P["d"], y, s=40, color=ENCRE2, edgecolor=FOND, linewidth=1.2, zorder=3)
    for i in range(1, n):
        if mois[i] != mois[i - 1]:
            ax2.axhline(y[i] + 0.5, color=GRILLE, linewidth=0.8)
    y_moy = -2.7
    ax2.axhline(-0.75, color=ENCRE2, linewidth=0.8)
    ax2.plot([t["d_borne_inf_95_pb"], t["d_borne_sup_95_pb"]], [y_moy, y_moy], color=ENCRE, linewidth=2,
             solid_capstyle="round", zorder=3)
    ax2.scatter([t["d_moyen_pb"]], [y_moy], s=70, color=ENCRE, edgecolor=FOND, linewidth=1.5, zorder=4)
    ax2.set_yticks(list(y) + [y_moy])
    ax2.set_yticklabels([""] * n + ["Moyenne de D\net intervalle à 95 %"], fontsize=8.5)
    ax2.set_ylim(-3.6, n - 0.3)
    xmax = max(2.3, float(P["d"].max()) + 0.6)
    xmin = min(-2.3, float(P["d"].min()) - 0.6)
    ax2.set_xlim(xmin, xmax)
    ax2.text(0.9 + 0.08, -1.3, "seuil : 0,9 pb", ha="left", va="center", fontsize=8, color=ENCRE2)
    ax2.text(t["d_borne_sup_95_pb"] + 0.12, y_moy,
             f"{t['d_moyen_pb']:.2f} pb\n[{t['d_borne_inf_95_pb']:.2f} ; {t['d_borne_sup_95_pb']:.2f}]".replace(".", ","),
             ha="left", va="center", fontsize=8.5, color=ENCRE)
    ax2.set_xlabel("D = V(HS) − V(MC), en points de base")
    ax2.set_title("Différence appariée D par adjudication\n(valeurs entières : fichier arrondi à 0,01 point)",
                  fontsize=9.5, loc="left", color=ENCRE)

    ax1.set_ylim(-3.6, n - 0.3)
    fig.suptitle("F04-bis — V des réouvertures de l'exercice 2021 sous l'ancienne et la nouvelle méthode du Trésor",
                 x=0.012, ha="left", fontsize=11.5, color=ENCRE, y=0.985)
    fig.text(0.012, 0.012,
             f"N = {t['n_adjudications']} adjudications, {t['n_grappes']} mois (grappes). Erreur type groupée par mois : "
             + f"{t['d_erreur_type_pb']:.3f}".replace(".", ",")
             + " pb ; intervalle = moyenne ± 2,365 × erreur type. Traits horizontaux fins : limites de mois.",
             fontsize=7.8, color=ENCRE2, ha="left")
    fig.subplots_adjust(left=0.135, right=0.985, top=0.885, bottom=0.135)
    fig.savefig(chemin, facecolor=FOND)
    plt.close(fig)


if __name__ == "__main__":
    main()
