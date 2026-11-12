#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F12 — statistique principale (§ 6.1) et analyses secondaires S1-S3 (§ 6.2) de la préinscription scellée.

Lit uniquement `analyse_F12.csv`. Écrit `temoin.json`, `resultats_analyse.json`, `figure.png`, `figure_S2.png`.
Usage : python3 -I analyse.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, ICI)
from controles_schema import controles  # noqa: E402

CSV = os.path.join(ICI, "analyse_F12.csv")
T_10 = 1.32      # constante fixée (Student 24 ddl, unilatéral 10 %)
T_5 = 1.66       # constante fixée (Student 85 ddl, unilatéral 5 %)


# ---------------------------------------------------------------- estimateur du § 6.1
def pente_hc3(x, y):
    """MCO avec constante ; pente b et variance HC3 en formule fermée (§ 6.1)."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    n = len(x)
    xc = x - x.mean()
    yc = y - y.mean()
    S = np.sum(xc ** 2)
    b = np.sum(xc * yc) / S
    e = yc - b * xc
    h = 1.0 / n + xc ** 2 / S
    V = np.sum(xc ** 2 * e ** 2 / (1.0 - h) ** 2) / S ** 2
    return b, V, n


def pente(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    xc = x - x.mean()
    return np.sum(xc * (y - y.mean())) / np.sum(xc ** 2)


def difference(tab):
    """tab : DataFrame (date_reunion, periode, x, y) → pentes par régime, d, se_d."""
    out = {}
    for r in ("avant", "apres"):
        s = tab[tab["periode"] == r]
        b, V, n = pente_hc3(s["x"], s["y"])
        out[f"n_{r}"] = int(n)
        out[f"b_{r}"] = float(b)
        out[f"se_b_{r}"] = float(np.sqrt(V))
        out[f"V_{r}"] = float(V)
    out["d"] = out["b_apres"] - out["b_avant"]
    out["se_d"] = float(np.sqrt(out["V_apres"] + out["V_avant"]))
    out["d_haut"] = out["d"] + T_10 * out["se_d"]
    out["d_bas"] = out["d"] - T_10 * out["se_d"]
    return out


def moyenne_pays(df, source, pays):
    """Par réunion : x = d_ois2y_pb, y = moyenne des d_ecart_pb des pays donnés (tous renseignés)."""
    s = df[(df["source"] == source) & (df["pays"].isin(pays))]
    piv = s.pivot(index="date_reunion", columns="pays", values="d_ecart_pb")
    piv = piv.dropna(how="any")
    y = piv[list(pays)].mean(axis=1)
    meta = s.drop_duplicates("date_reunion").set_index("date_reunion")[["periode", "d_ois2y_pb", "surprise_restrictive"]]
    tab = pd.DataFrame({"periode": meta.loc[y.index, "periode"], "x": meta.loc[y.index, "d_ois2y_pb"],
                        "y": y, "restr": meta.loc[y.index, "surprise_restrictive"]})
    return tab.sort_index().reset_index()


def main():
    df = pd.read_csv(CSV, dtype={"date_reunion": str, "pays": str, "source": str, "periode": str})
    res = {}

    # ------------------------------------------------------------ contrôles de schéma
    ctl = controles(CSV)
    violations = sum(1 for ok, _ in ctl.values() if not ok)
    print("Contrôles de schéma (§ 5) :")
    for k, (ok, detail) in ctl.items():
        print(f"  {k:>2} : {'OK ' if ok else 'ÉCHEC'} {detail}")
    print(f"violations_schema = {violations}\n")

    # ------------------------------------------------------------ statistique principale
    tab = moyenne_pays(df, "EAMPD", ["IT", "ES"])
    princ = tab[tab["periode"].isin(["avant", "apres"])].reset_index(drop=True)
    P = difference(princ)
    t_b_avant = P["b_avant"] / P["se_b_avant"]

    # retrait d'une réunion
    d_sans = []
    for i in range(len(princ)):
        s = princ.drop(index=i)
        ba = pente(s.loc[s["periode"] == "avant", "x"], s.loc[s["periode"] == "avant", "y"])
        bp = pente(s.loc[s["periode"] == "apres", "x"], s.loc[s["periode"] == "apres", "y"])
        d_sans.append((princ.loc[i, "date_reunion"], princ.loc[i, "periode"], float(bp - ba)))
    d_sans_df = pd.DataFrame(d_sans, columns=["date_retiree", "periode", "d"])
    i_max = d_sans_df["d"].idxmax()
    i_min = d_sans_df["d"].idxmin()
    d_max_sans_une = float(d_sans_df.loc[i_max, "d"])

    non_informatif = int((P["se_d"] > 0.16) and (P["d_haut"] >= 0) and (P["d_bas"] <= -0.15))

    temoin = {
        "n_avant": P["n_avant"],
        "n_apres": P["n_apres"],
        "b_avant": P["b_avant"],
        "b_apres": P["b_apres"],
        "d_hat": P["d"],
        "se_d": P["se_d"],
        "d_borne_haute": P["d_haut"],
        "d_borne_basse": P["d_bas"],
        "t_b_avant": float(t_b_avant),
        "d_max_sans_une": d_max_sans_une,
        "non_informatif": non_informatif,
        "violations_schema": int(violations),
    }
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, indent=2)
        f.write("\n")

    print("STATISTIQUE PRINCIPALE (§ 6.1)")
    for k, v in temoin.items():
        print(f"  {k} = {v}")
    print(f"  se_b_avant = {P['se_b_avant']:.6f} ; se_b_apres = {P['se_b_apres']:.6f}")
    print(f"  retrait d'une réunion : d max = {d_max_sans_une:.6f} (sans {d_sans_df.loc[i_max, 'date_retiree']}, "
          f"{d_sans_df.loc[i_max, 'periode']}) ; d min = {d_sans_df.loc[i_min, 'd']:.6f} "
          f"(sans {d_sans_df.loc[i_min, 'date_retiree']}, {d_sans_df.loc[i_min, 'periode']})")

    # descriptifs de l'échantillon principal (pour le compte rendu)
    desc = {}
    for r in ("avant", "apres"):
        s = princ[princ["periode"] == r]
        xc = s["x"] - s["x"].mean()
        b = P[f"b_{r}"]
        e = (s["y"] - s["y"].mean()) - b * xc
        desc[r] = {"sd_x": float(s["x"].std(ddof=1)), "sd_y": float(s["y"].std(ddof=1)),
                   "sd_residu": float(np.sqrt(np.sum(e ** 2) / (len(s) - 2))),
                   "n_effectif_pente": float(np.sum(xc ** 2) ** 2 / np.sum(xc ** 4)),
                   "x_min": float(s["x"].min()), "x_max": float(s["x"].max()),
                   "levier_max": float((1 / len(s) + xc ** 2 / np.sum(xc ** 2)).max()),
                   "date_levier_max": s.loc[(xc ** 2).idxmax(), "date_reunion"],
                   "n_restrictives": int(s["restr"].sum())}
        print(f"  {r} : {desc[r]}")

    # contre-épreuve de la formule fermée avec statsmodels (même HC3)
    try:
        import statsmodels.api as sm
        chk = {}
        for r in ("avant", "apres"):
            s = princ[princ["periode"] == r]
            m = sm.OLS(s["y"].values, sm.add_constant(s["x"].values)).fit(cov_type="HC3")
            chk[r] = (float(m.params[1]), float(m.bse[1]))
        print(f"  contre-épreuve statsmodels HC3 : avant b={chk['avant'][0]:.6f} se={chk['avant'][1]:.6f} ; "
              f"apres b={chk['apres'][0]:.6f} se={chk['apres'][1]:.6f}")
        res["controle_statsmodels"] = chk
    except Exception as exc:  # la contre-épreuve n'est pas nécessaire au calcul
        print(f"  contre-épreuve statsmodels impossible : {exc}")

    res["principal"] = {**temoin, "se_b_avant": P["se_b_avant"], "se_b_apres": P["se_b_apres"],
                        "d_min_sans_une": float(d_sans_df.loc[i_min, "d"]),
                        "date_d_max_sans_une": d_sans_df.loc[i_max, "date_retiree"],
                        "date_d_min_sans_une": d_sans_df.loc[i_min, "date_retiree"],
                        "n_retraits_d_positif": int((d_sans_df["d"] >= 0).sum()),
                        "descriptifs": desc}

    # ------------------------------------------------------------ S1 — placebo journalier (descriptif)
    print("\nS1 — PLACEBO PAYS PEU ENDETTÉS, JOURNALIER (descriptif)")
    rk = df[(df["source"] == "RIKSBANK") & df["periode"].isin(["avant", "apres"])]
    ea = df[(df["source"] == "EAMPD") & df["periode"].isin(["avant", "apres"])]
    de_rk = rk.dropna(subset=["d_rdt_de_pb"]).groupby("date_reunion")["d_rdt_de_pb"].first()
    de_ea = ea.groupby("date_reunion")["d_rdt_de_pb"].first()
    cal = pd.DataFrame({"jour": de_rk, "intra": de_ea.reindex(de_rk.index)})
    kappa, V_k, n_k = pente_hc3(cal["intra"], cal["jour"])
    r2 = float(np.corrcoef(cal["intra"], cal["jour"])[0, 1] ** 2)
    print(f"  (a) calage : kappa = {kappa:.4f} (erreur type HC3 {np.sqrt(V_k):.4f}, n = {n_k}, R² = {r2:.4f}) ; "
          f"seuil 0,5 → placebo {'non informatif' if kappa < 0.5 else 'retenu'}")
    S1 = {"kappa": float(kappa), "se_kappa": float(np.sqrt(V_k)), "n_kappa": int(n_k), "r2_kappa": r2,
          "placebo_non_informatif": int(kappa < 0.5)}

    plc = moyenne_pays(df, "RIKSBANK", ["NL", "FI"])
    plc = plc[plc["periode"].isin(["avant", "apres"])].reset_index(drop=True)
    Q = difference(plc)
    print(f"  (b) placebo NL/FI : n = {Q['n_avant']}/{Q['n_apres']} ; b_avant = {Q['b_avant']:.4f} ({Q['se_b_avant']:.4f}) ; "
          f"b_apres = {Q['b_apres']:.4f} ({Q['se_b_apres']:.4f}) ; d_placebo = {Q['d']:.4f} ; se_placebo = {Q['se_d']:.4f} ; "
          f"intervalle ±1,32 se : [{Q['d_bas']:.4f} ; {Q['d_haut']:.4f}]")
    S1["placebo"] = {k: Q[k] for k in ("n_avant", "n_apres", "b_avant", "se_b_avant", "b_apres", "se_b_apres",
                                         "d", "se_d", "d_bas", "d_haut")}

    fr_j = moyenne_pays(df, "RIKSBANK", ["FR"])
    fr_j = fr_j[fr_j["periode"].isin(["avant", "apres"])].reset_index(drop=True)
    fr_i_all = moyenne_pays(df, "EAMPD", ["FR"])
    fr_i = fr_i_all[fr_i_all["periode"].isin(["avant", "apres"])].reset_index(drop=True)
    fr_i_m = fr_i[fr_i["date_reunion"].isin(fr_j["date_reunion"])].reset_index(drop=True)
    for nom, t in (("FR journalier (RIKSBANK)", fr_j), ("FR intrajournalier (EAMPD), toutes réunions", fr_i),
                   ("FR intrajournalier (EAMPD), mêmes dates que RIKSBANK", fr_i_m)):
        R = difference(t)
        print(f"  (c) pont {nom} : n = {R['n_avant']}/{R['n_apres']} ; b_avant = {R['b_avant']:.4f} ({R['se_b_avant']:.4f}) ; "
              f"b_apres = {R['b_apres']:.4f} ({R['se_b_apres']:.4f}) ; d = {R['d']:.4f} ; se = {R['se_d']:.4f}")
        S1["pont_" + nom] = {k: R[k] for k in ("n_avant", "n_apres", "b_avant", "se_b_avant", "b_apres",
                                               "se_b_apres", "d", "se_d", "d_bas", "d_haut")}
    S1["lecture_baisse_aussi_placebo"] = int(Q["d_haut"] < 0)
    print(f"  lecture fixée : d_placebo + 1,32 × se_placebo = {Q['d_haut']:.4f} "
          f"({'< 0' if Q['d_haut'] < 0 else '≥ 0'})")
    res["S1"] = S1

    # ------------------------------------------------------------ S2 — fenêtres glissantes (descriptif)
    print("\nS2 — STABILITÉ DE LA PENTE AVANT LE TPI (descriptif)")
    pre = tab[tab["periode"].isin(["crise", "avant"])].sort_values("date_reunion").reset_index(drop=True)
    L = 26
    fen = []
    for i in range(len(pre) - L + 1):
        w = pre.iloc[i:i + L]
        fen.append((w["date_reunion"].iloc[0], w["date_reunion"].iloc[-1], float(pente(w["x"], w["y"]))))
    fen = pd.DataFrame(fen, columns=["debut", "fin", "b_w"])
    part = float((fen["b_w"] <= P["b_apres"]).mean())
    S2 = {"n_reunions": int(len(pre)), "n_fenetres": int(len(fen)), "b_w_min": float(fen["b_w"].min()),
          "b_w_mediane": float(fen["b_w"].median()), "b_w_max": float(fen["b_w"].max()),
          "fenetre_min": fen.loc[fen["b_w"].idxmin(), ["debut", "fin"]].tolist(),
          "fenetre_max": fen.loc[fen["b_w"].idxmax(), ["debut", "fin"]].tolist(),
          "n_fenetres_basses": int((fen["b_w"] <= P["b_apres"]).sum()), "part_fenetres_basses": part,
          "b_apres": P["b_apres"]}
    print(f"  {S2['n_reunions']} réunions, {S2['n_fenetres']} fenêtres de 26 ; b_w min = {S2['b_w_min']:.4f} "
          f"({S2['fenetre_min']}), médiane = {S2['b_w_mediane']:.4f}, max = {S2['b_w_max']:.4f} ({S2['fenetre_max']})")
    print(f"  part_fenetres_basses (b_w ≤ b_apres = {P['b_apres']:.4f}) = {S2['n_fenetres_basses']}/{len(fen)} = {part:.4f} "
          f"(seuil de lecture 0,10)")
    fen.to_csv(os.path.join(ICI, "S2_fenetres.csv"), index=False, float_format="%.6f")
    res["S2"] = S2

    # ------------------------------------------------------------ S3 — surprises restrictives (descriptif)
    print("\nS3 — SURPRISES RESTRICTIVES SEULEMENT (descriptif)")
    rst = princ[princ["restr"] == 1].reset_index(drop=True)
    R3 = difference(rst)
    print(f"  n = {R3['n_avant']}/{R3['n_apres']} ; b_avant = {R3['b_avant']:.4f} ({R3['se_b_avant']:.4f}) ; "
          f"b_apres = {R3['b_apres']:.4f} ({R3['se_b_apres']:.4f}) ; d_restrictif = {R3['d']:.4f} ; se = {R3['se_d']:.4f}")
    res["S3"] = {k: R3[k] for k in ("n_avant", "n_apres", "b_avant", "se_b_avant", "b_apres", "se_b_apres", "d", "se_d")}

    with open(os.path.join(ICI, "resultats_analyse.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
        f.write("\n")

    figures(princ, P, d_sans_df, fen)


# ---------------------------------------------------------------- figures
def fr(v, nd=3, signe=True):
    """Nombre au format français (virgule décimale, signe moins typographique)."""
    t = f"{v:+.{nd}f}" if signe else f"{v:.{nd}f}"
    return t.replace(".", ",").replace("-", "−")


def figures(princ, P, d_sans_df, fen):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
    C = {"avant": "#2a78d6", "apres": "#eb6834"}
    NOM = {"avant": "Avant TPI (oct. 2012 – juin 2022, 87 réunions)",
           "apres": "Après TPI (sept. 2022 – oct. 2025, 26 réunions)"}
    virgule = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−"))
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                         "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF})

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(13, 5.8), gridspec_kw={"width_ratios": [1.35, 1]})

    # --- nuage : une réunion = un point, droites MCO par régime
    for r in ("avant", "apres"):
        s = princ[princ["periode"] == r]
        ax.scatter(s["x"], s["y"], s=34, color=C[r], edgecolor=SURF, linewidth=0.8, zorder=3,
                   label=f"{NOM[r]} : pente {fr(P[f'b_{r}'])}")
        xs = np.array([s["x"].min(), s["x"].max()])
        ax.plot(xs, s["y"].mean() + P[f"b_{r}"] * (xs - s["x"].mean()), color=C[r], linewidth=2, zorder=2)
    ax.axhline(0, color=GRID, linewidth=1, zorder=1)
    ax.axvline(0, color=GRID, linewidth=1, zorder=1)
    ax.grid(color=GRID, linewidth=0.6, zorder=0)
    ax.xaxis.set_major_formatter(virgule)
    ax.yaxis.set_major_formatter(virgule)
    ax.set_xlabel("Surprise OIS 2 ans dans la fenêtre de la réunion (pb)")
    ax.set_ylabel("Variation de l'écart moyen IT/ES − DE à 10 ans (pb)")
    ax.set_title("Chaque point est une réunion ; droites MCO par régime", loc="left", fontsize=10.5, color=INK)
    ax.legend(frameon=False, loc="upper left", fontsize=9, handletextpad=0.3, borderaxespad=0.2)
    ax.set_ylim(top=max(princ["y"].max() * 1.32, 10))

    # --- estimations avec intervalles ± 1,32 × erreur type HC3
    lignes = [("Pente avant (b_avant)", P["b_avant"], P["se_b_avant"], C["avant"]),
              ("Pente après (b_apres)", P["b_apres"], P["se_b_apres"], C["apres"]),
              ("Différence (d_hat)", P["d"], P["se_d"], INK)]
    ypos = [4, 3, 2]
    etiq = []
    for (nom, v, se, col), yp in zip(lignes, ypos):
        ax2.plot([v - T_10 * se, v + T_10 * se], [yp, yp], color=col, linewidth=2, solid_capstyle="round", zorder=3)
        ax2.scatter([v], [yp], s=64, color=col, edgecolor=SURF, linewidth=1.2, zorder=4)
        etiq.append(f"{nom}\n{fr(v)}  (erreur type {fr(se, signe=False)})")
    # étendue de d quand on retire une réunion (113 retraits)
    dmin, dmax = d_sans_df["d"].min(), d_sans_df["d"].max()
    ax2.plot([dmin, dmax], [1, 1], color=INK2, linewidth=2, solid_capstyle="butt", zorder=3)
    ax2.scatter([dmin, dmax], [1, 1], s=90, color=INK2, marker="|", zorder=4)
    etiq.append(f"d en retirant une réunion\nde {fr(dmin)} à {fr(dmax)}")
    ax2.axvline(0, color=INK2, linewidth=1, zorder=1)
    ax2.axvline(-0.15, color=INK2, linewidth=1, linestyle=(0, (4, 3)), zorder=1)
    ax2.annotate("0", (0, 4.62), xytext=(4, 0), textcoords="offset points", ha="left", fontsize=8.5, color=INK2)
    ax2.annotate("seuil de taille −0,15", (-0.15, 4.62), xytext=(-4, 0), textcoords="offset points",
                 ha="right", fontsize=8.5, color=INK2)
    ax2.set_yticks(ypos + [1])
    ax2.set_yticklabels(etiq, color=INK, fontsize=9)
    ax2.set_ylim(0.4, 4.9)
    ax2.tick_params(axis="y", length=0)
    ax2.grid(axis="x", color=GRID, linewidth=0.6, zorder=0)
    ax2.xaxis.set_major_formatter(virgule)
    ax2.set_xlabel("pb d'écart par pb de surprise")
    ax2.set_title("Estimations ; barres = ± 1,32 × erreur type HC3\n(seuil unilatéral 10 % préinscrit)",
                  loc="left", fontsize=10.5, color=INK)
    lo = min(P["d"] - T_10 * P["se_d"], dmin, -0.15, P["b_apres"] - T_10 * P["se_b_apres"])
    hi = max(P["b_avant"] + T_10 * P["se_b_avant"], P["b_apres"] + T_10 * P["se_b_apres"], dmax, 0)
    pad = 0.08 * (hi - lo)
    ax2.set_xlim(lo - pad, hi + pad)

    fig.suptitle("F12 — Réponse de l'écart Italie/Espagne − Allemagne (10 ans) aux surprises OIS 2 ans, "
                 "avant et après le TPI (EA-MPD, fenêtre de la réunion)", x=0.01, ha="left", fontsize=11.5, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(os.path.join(ICI, "figure.png"), dpi=160)
    plt.close(fig)

    # --- S2 : pente par fenêtre glissante de 26 réunions, selon la date de fin de fenêtre
    fig, ax = plt.subplots(figsize=(10, 4.8))
    fin = pd.to_datetime(fen["fin"])
    ax.plot(fin, fen["b_w"], color=C["avant"], linewidth=2, zorder=3,
            label="b_w : pente sur 26 réunions consécutives (crise + avant, 95 fenêtres)")
    ax.scatter(fin, fen["b_w"], s=14, color=C["avant"], edgecolor=SURF, linewidth=0.5, zorder=4)
    ax.axhline(P["b_apres"], color=C["apres"], linewidth=2, zorder=2,
               label=f"b_apres = {fr(P['b_apres'])} (26 réunions après le TPI)")
    ax.axhline(0, color=GRID, linewidth=1, zorder=1)
    ax.grid(color=GRID, linewidth=0.6, zorder=0)
    ax.yaxis.set_major_formatter(virgule)
    ax.set_ylim(top=fen["b_w"].max() + 0.45)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    ax.set_xlabel("Date de fin de la fenêtre")
    ax.set_ylabel("Pente (pb d'écart par pb de surprise)")
    ax.set_title("F12, S2 (descriptif) — pente IT/ES − DE sur OIS 2 ans par fenêtre glissante de 26 réunions, "
                 "2010-2022", loc="left", fontsize=10.5, color=INK)
    fig.tight_layout()
    fig.savefig(os.path.join(ICI, "figure_S2.png"), dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
