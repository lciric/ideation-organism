#!/usr/bin/env python3
"""H03-v2 — statistique principale et analyses secondaires, à partir du fichier d'analyse seul.

Suit la préinscription scellée, section 6 (étapes 1 à 6, S1, S2, S3). Double précision,
aucun arrondi intermédiaire, aucun tirage aléatoire.
Écrit temoin.json (champs de « champs_verification », nombres seulement),
analyse_detail.json (détail par bloc, pour le rapport) et figure.png.

Usage : python3 analyse.py
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import controles_schema as cs  # noqa: E402

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "H03-v2_analyse.csv")
T_MIN, T_MAX = 8016, 8103
EPS = 1e-12
Q_STUDENT = {11: 1.8125, 10: 1.8331, 9: 1.8595, 8: 1.8946, 7: 1.9432, 6: 2.0150, 5: 2.1318}
CHAMPS = ["n_violations_schema", "n_obs_evaluees", "n_blocs", "r_moyen", "et_r_moyen",
          "borne_basse_ic90", "borne_haute_ic90", "marge_indecision", "r_hors_episode",
          "rapport_eqm_geo", "conflit_gardes", "n_obs_h4_2020", "rapport_eqm_h4_2020",
          "p_dm_hln_h4_2020", "rapport_eqm_global", "rapport_eqm_hors_2021_2022",
          "taux_amelioration", "part_b_positif", "r_moyen_h1", "r_moyen_h2", "r_moyen_h3",
          "r_moyen_h4", "r_moyen_placebo", "et_r_placebo", "n_blocs_placebo"]


def appliquer_regle(df, col_r, borne_cible=True):
    """Étape 2. Pour chaque ligne complète (col_r et erreur présentes) — dont t_cible est dans
    [8016, 8103] si borne_cible — calcule n_A, S_rr, b, c. Renvoie les lignes évaluées."""
    complet = df[df[col_r].notna() & df["erreur"].notna()]
    sorties = []
    par_h = {h: g for h, g in complet.groupby("horizon")}
    for idx, li in complet.iterrows():
        if borne_cible and not (T_MIN <= li["t_cible"] <= T_MAX):
            continue
        g = par_h[li["horizon"]]
        A = g[g["t_lecture"] <= li["t_millesime"]]
        assert idx not in A.index       # la ligne i n'en fait jamais partie
        n_A = len(A)
        if n_A == 0:
            continue
        r = A[col_r].to_numpy(dtype=float)
        e = A["erreur"].to_numpy(dtype=float)
        rb, eb = r.mean(), e.mean()
        s_rr = float(((r - rb) ** 2).sum())
        if not (n_A >= 8 and s_rr > EPS):
            continue
        b = float(((r - rb) * (e - eb)).sum() / s_rr)
        sorties.append({"idx": idx, "millesime": li["millesime"], "t_millesime": int(li["t_millesime"]),
                        "horizon": int(li["horizon"]), "t_cible": int(li["t_cible"]),
                        "r": float(li[col_r]), "e": float(li["erreur"]), "n_A": n_A, "S_rr": s_rr,
                        "b": b, "c": b * float(li[col_r])})
    ev = pd.DataFrame(sorties)
    if len(ev):
        ev["bloc"] = (ev["t_cible"] - T_MIN) // 8
    return ev


def stat_blocs(ev):
    """Étapes 3 à 5. Renvoie un dictionnaire avec R_k par bloc valide, R̄, ET, bornes."""
    blocs = {}
    if len(ev):
        for k, g in ev.groupby("bloc"):
            scc, see = float((g["c"] ** 2).sum()), float((g["e"] ** 2).sum())
            sce = float((g["c"] * g["e"]).sum())
            valide = len(g) >= 16 and scc > EPS and see > EPS
            info = {"n": int(len(g)), "valide": bool(valide), "S_cc": scc, "S_ee": see, "S_ce": sce}
            if valide:
                info["R"] = sce / math.sqrt(scc * see)
                q = float(((g["e"] - g["c"]) ** 2).sum()) / see
                info["Q"] = max(q, 1e-6)
            blocs[int(k)] = info
    ks = sorted(k for k, v in blocs.items() if v["valide"])
    K = len(ks)
    out = {"blocs": blocs, "K": K, "blocs_valides": ks}
    if K < 5:
        out.update({"r_moyen": 0.0, "et": 0.0, "bas": 0.0, "haut": 0.0, "g0": None, "g1": None, "q": None})
        return out
    R = {k: blocs[k]["R"] for k in ks}
    rbar = sum(R.values()) / K
    g0 = sum((R[k] - rbar) ** 2 for k in ks) / (K - 1)
    g1 = sum((R[k] - rbar) * (R[k + 1] - rbar) for k in ks if (k + 1) in R) / (K - 1)
    et = math.sqrt((g0 + 2 * max(g1, 0.0)) / K)
    q = Q_STUDENT[K]
    out.update({"r_moyen": rbar, "et": et, "bas": rbar - q * et, "haut": rbar + q * et,
                "g0": g0, "g1": g1, "q": q})
    return out


def main():
    # Contrôles de schéma sur le fichier
    res = cs.controler(FICHIER)
    n_viol = cs.n_violations(res)

    df = pd.read_csv(FICHIER, dtype={"millesime": str, "cible": str, "millesime_precedent": str,
                                     "millesime_realise": str})
    T = {}
    detail = {}
    T["n_violations_schema"] = n_viol

    # Étape 1 — lignes complètes
    n_completes = int((df["revision"].notna() & df["erreur"].notna()).sum())
    n_completes_plage = int((df["revision"].notna() & df["erreur"].notna()
                             & df["t_cible"].between(T_MIN, T_MAX)).sum())

    # Étapes 2 à 5 — statistique principale
    ev = appliquer_regle(df, "revision")
    sb = stat_blocs(ev)
    K = sb["K"]
    T["n_obs_evaluees"] = int(len(ev))
    T["n_blocs"] = K
    T["r_moyen"] = sb["r_moyen"]
    T["et_r_moyen"] = sb["et"]
    T["borne_basse_ic90"] = sb["bas"]
    T["borne_haute_ic90"] = sb["haut"]
    T["marge_indecision"] = min(-T["borne_basse_ic90"], T["borne_haute_ic90"] - 0.22)

    # Étape 6 — gardes
    if K < 5:
        T["r_hors_episode"] = 0.0
        T["rapport_eqm_geo"] = 1.0
    else:
        hors = [sb["blocs"][k]["R"] for k in sb["blocs_valides"] if k not in (8, 9)]
        T["r_hors_episode"] = sum(hors) / len(hors) if hors else 0.0
        T["rapport_eqm_geo"] = math.exp(sum(math.log(sb["blocs"][k]["Q"]) for k in sb["blocs_valides"]) / K)
    T["conflit_gardes"] = int(T["borne_basse_ic90"] > 0
                              and (T["r_hors_episode"] <= 0 or T["rapport_eqm_geo"] >= 1))

    # S1 — le test de la fiche (horizon 4, t_millesime ≥ 8080, sans borne sur t_cible)
    ev_tous = appliquer_regle(df, "revision", borne_cible=False)
    s1 = ev_tous[(ev_tous["horizon"] == 4) & (ev_tous["t_millesime"] >= 8080)].sort_values("t_millesime")
    n = int(len(s1))
    T["n_obs_h4_2020"] = n
    e1, c1 = s1["e"].to_numpy(), s1["c"].to_numpy()
    T["rapport_eqm_h4_2020"] = float(((e1 - c1) ** 2).sum() / (e1 ** 2).sum()) if n > 0 else 1.0
    dm = dm_etoile = V = None
    p = 1.0
    if n >= 8:
        d = e1 ** 2 - (e1 - c1) ** 2
        dbar = d.mean()
        gam = [float(((d[j:] - dbar) * (d[:n - j] - dbar)).sum() / n) for j in range(4)]
        V = (gam[0] + 2 * (gam[1] + gam[2] + gam[3])) / n
        if V > 0:
            dm = float(dbar / math.sqrt(V))
            dm_etoile = dm * math.sqrt((n + 1 - 8 + 12 / n) / n)
            p = float(stats.t.sf(dm_etoile, n - 1))
    T["p_dm_hln_h4_2020"] = p

    # S2 — lecture en clair
    e, c = ev["e"].to_numpy(), ev["c"].to_numpy()
    T["rapport_eqm_global"] = float(((e - c) ** 2).sum() / (e ** 2).sum())
    hors = ev[~ev["t_cible"].between(8084, 8091)]
    T["rapport_eqm_hors_2021_2022"] = float(((hors["e"] - hors["c"]) ** 2).sum() / (hors["e"] ** 2).sum())
    G = int((np.abs(e - c) < np.abs(e) - 1e-9).sum())
    P = int((np.abs(e - c) > np.abs(e) + 1e-9).sum())
    T["taux_amelioration"] = G / (G + P) if (G + P) > 0 else 0.5
    T["part_b_positif"] = float((ev["b"] > 0).mean())
    par_h = {}
    for h in (1, 2, 3, 4):
        Rs = {}
        for k, g in ev[ev["horizon"] == h].groupby("bloc"):
            scc, see = float((g["c"] ** 2).sum()), float((g["e"] ** 2).sum())
            if len(g) >= 4 and scc > EPS and see > EPS:
                Rs[int(k)] = float((g["c"] * g["e"]).sum()) / math.sqrt(scc * see)
        T[f"r_moyen_h{h}"] = sum(Rs.values()) / len(Rs) if Rs else 0.0
        par_h[h] = Rs

    # S3 — placebo : révision de la ligne de même horizon dont t_millesime vaut t_millesime(i) − 8
    cle = df.set_index(["t_millesime", "horizon"])["revision"]
    df["revision_decalee"] = [cle.get((tm - 8, h), np.nan) for tm, h in zip(df["t_millesime"], df["horizon"])]
    ev_p = appliquer_regle(df, "revision_decalee")
    sp = stat_blocs(ev_p)
    T["r_moyen_placebo"] = sp["r_moyen"]
    T["et_r_placebo"] = sp["et"]
    T["n_blocs_placebo"] = sp["K"]

    # Témoin : exactement les champs de la préinscription, dans l'ordre, nombres seulement
    temoin = {}
    for ch in CHAMPS:
        v = T[ch]
        temoin[ch] = int(v) if isinstance(v, (int, np.integer)) else float(v)
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, indent=1)

    detail = {
        "controles_schema": {str(n): {"ok": int(ok), "detail": d} for n, (ok, d) in sorted(res.items())},
        "n_lignes": int(len(df)),
        "n_lignes_completes": n_completes,
        "n_lignes_completes_cible_8016_8103": n_completes_plage,
        "n_lignes_evaluees": int(len(ev)),
        "n_A_min": int(ev["n_A"].min()), "n_A_max": int(ev["n_A"].max()),
        "evaluees_par_horizon": {str(h): int((ev["horizon"] == h).sum()) for h in (1, 2, 3, 4)},
        "principal": sb,
        "b_par_horizon": {str(h): {"min": float(ev.loc[ev["horizon"] == h, "b"].min()),
                                   "mediane": float(ev.loc[ev["horizon"] == h, "b"].median()),
                                   "max": float(ev.loc[ev["horizon"] == h, "b"].max()),
                                   "part_positive": float((ev.loc[ev["horizon"] == h, "b"] > 0).mean())}
                          for h in (1, 2, 3, 4)},
        "S1": {"n": n, "t_millesime_min": int(s1["t_millesime"].min()) if n else None,
               "t_millesime_max": int(s1["t_millesime"].max()) if n else None,
               "d_barre": float((e1 ** 2 - (e1 - c1) ** 2).mean()) if n else None,
               "V": V, "DM": dm, "DM_etoile": dm_etoile,
               "somme_e2": float((e1 ** 2).sum()), "somme_e_moins_c_2": float(((e1 - c1) ** 2).sum())},
        "S2": {"G": G, "P": P, "egalites": int(len(ev) - G - P),
               "n_hors_2021_2022": int(len(hors)),
               "R_par_horizon_et_bloc": {str(h): {str(k): v for k, v in par_h[h].items()} for h in par_h}},
        "S3": {"n_lignes_completes_placebo": int((df["revision_decalee"].notna() & df["erreur"].notna()).sum()),
               "n_lignes_evaluees_placebo": int(len(ev_p)), "placebo": sp,
               "r_sur_et": (sp["r_moyen"] / sp["et"]) if sp["et"] else None,
               "depasse_1_8_fois_et": int(sp["r_moyen"] > 1.8 * sp["et"])},
        "temoin": temoin,
    }
    with open(os.path.join(ICI, "analyse_detail.json"), "w", encoding="utf-8") as f:
        json.dump(detail, f, ensure_ascii=False, indent=1)
    ev.drop(columns=["idx"]).to_csv(os.path.join(ICI, "lignes_evaluees.csv"), index=False)

    figure(sb, os.path.join(ICI, "figure.png"))

    for ch in CHAMPS:
        print(f"{ch}: {temoin[ch]}")
    return detail


def figure(sb, chemin):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    encre, discret, grille = "#0b0b0b", "#52514e", "#dddcd6"
    bleu, fond = "#2a78d6", "#fcfcfb"
    noms = [f"{2004 + 2 * k}-{str(2005 + 2 * k)[2:]}" for k in range(11)]
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=160)
    fig.patch.set_facecolor(fond)
    ax.set_facecolor(fond)
    K = sb["K"]
    fr = lambda x, n=2: f"{x:+.{n}f}".replace(".", ",").replace("-", "−")
    x0, x1 = -0.6, 10.6
    if K >= 5:
        ax.fill_between([x0, x1], sb["bas"], sb["haut"], color="#8a8983", alpha=0.18, lw=0, zorder=1)
        ax.plot([x0, x1], [sb["r_moyen"]] * 2, color=encre, lw=2, zorder=3)
    ax.plot([x0, x1], [0, 0], color=discret, lw=1, zorder=2)
    ax.plot([x0, x1], [0.22, 0.22], color=discret, lw=1, ls=(0, (4, 3)), zorder=2)
    for k in range(11):
        info = sb["blocs"].get(k)
        if info and info["valide"]:
            ax.vlines(k, 0, info["R"], color=bleu, lw=2, zorder=4)
            ax.plot(k, info["R"], "o", ms=9, color=bleu, mec=fond, mew=2, zorder=5)
            dy = 0.035 if info["R"] >= 0 else -0.035
            ax.text(k, info["R"] + dy, fr(info["R"]), ha="center",
                    va="bottom" if dy > 0 else "top", fontsize=9, color=encre)
        else:
            ax.text(k, 0.03, "non valide", ha="center", fontsize=8, color=discret, rotation=90)
    ax.set_xlim(x0, 13.4)
    ax.set_ylim(-0.55, 0.55)
    ax.set_xticks(range(11))
    ax.set_xticklabels(noms, fontsize=9, color=discret)
    ax.set_yticks([-0.5, -0.25, 0, 0.25, 0.5])
    ax.set_yticklabels(["−0,5", "−0,25", "0", "0,25", "0,5"], fontsize=9, color=discret)
    ax.yaxis.grid(True, color=grille, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(grille)
    ax.tick_params(length=0)
    xt = 10.75
    if K >= 5:
        ax.text(xt, sb["r_moyen"], f"R̄ = {fr(sb['r_moyen'], 3)}", va="center", fontsize=9.5, color=encre,
                fontweight="bold")
        ax.text(xt, sb["haut"] + 0.012, f"borne haute {fr(sb['haut'], 3)}", va="bottom", fontsize=8.5,
                color=discret)
        ax.text(xt, sb["bas"] - 0.012, f"borne basse {fr(sb['bas'], 3)}", va="top", fontsize=8.5,
                color=discret)
    ax.text(xt, 0.22, "0,22 : plus petit effet\nprédit par la fiche", va="center", fontsize=8.5, color=discret)
    ax.set_xlabel("Bloc de deux ans (trimestres cibles)", fontsize=9.5, color=discret)
    ax.set_ylabel("R_k : corrélation non centrée correction × erreur", fontsize=9.5, color=discret)
    fig.suptitle("H03-v2 — statistique principale, bloc par bloc", x=0.065, y=0.975, ha="left",
                 fontsize=13, color=encre, fontweight="bold")
    et = f"{sb['et']:.3f}".replace(".", ",") if K >= 5 else "—"
    ax.set_title(f"Points : R_k de chaque bloc valide (K = {K}). Trait noir : moyenne simple R̄ ; "
                 f"bande grise : intervalle à 90 % de R̄ (Student, ET = {et}).\n"
                 f"R_k peut aller de −1 à 1 ; l'axe est resserré sur ±0,55 pour la lisibilité.",
                 loc="left", fontsize=9, color=discret, pad=10)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(chemin, facecolor=fond)
    plt.close(fig)


if __name__ == "__main__":
    main()
