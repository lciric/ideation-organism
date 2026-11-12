#!/usr/bin/env python3
"""H16 — statistique principale (§ 6.2), contrôles de schéma (§ 5) et analyses secondaires S1-S3 (§ 6.3).

Usage : python3 -I analyse.py
Lit   : analyse_H16.csv (et rien d'autre)
Écrit : temoin.json (les neuf champs de « champs_verification »), resultats_analyse.json (tout le reste),
        previsions_H16.csv (une ligne par réunion d'évaluation), figure.png
"""
import datetime as dt
import json
import math
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "analyse_H16.csv")

COLONNES = ["rang", "date_reunion", "date_reunion_prec", "d_ois1y_pb", "sigma16_pb", "cible_norm",
            "cible_prec_norm", "act_eu_60j_pct", "brent_60j_pct", "eurusd_60j_pct", "us2a_60j_pp",
            "date_fin_act", "date_fin_brent", "date_fin_eurusd", "date_fin_us2a", "echantillon"]
PRED_MARCHE = ["act_eu_60j_pct", "brent_60j_pct", "eurusd_60j_pct", "us2a_60j_pp"]
PRED = PRED_MARCHE + ["cible_prec_norm"]
DATES_FIN = ["date_fin_act", "date_fin_brent", "date_fin_eurusd", "date_fin_us2a"]
SOUS_PERIODES = [("2010-01-14", "2014-05-08", "taux positifs"),
                 ("2014-06-05", "2022-06-09", "taux négatifs et achats d'actifs"),
                 ("2022-07-21", "2025-10-30", "resserrement puis détente")]


# --------------------------------------------------------------------------- contrôles de schéma (§ 5)
def num(s):
    """Texte → float ; None si vide ; NaN si illisible."""
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return float("nan")


def date(s):
    try:
        d = dt.date.fromisoformat(s)
        return d if d.isoformat() == s else None
    except ValueError:
        return None


def controles_schema(brut):
    """brut : DataFrame de chaînes (cellule vide = ''). Renvoie {numéro: True si le contrôle réussit}."""
    ok = {}
    n = len(brut)
    ok[1] = (n == 315) and (list(brut.columns) == COLONNES)
    if list(brut.columns) != COLONNES:
        return {k: False for k in range(1, 11)}
    R = brut.to_dict("records")
    dates = [date(r["date_reunion"]) for r in R]
    # 2
    c2 = [r["rang"] for r in R] == [str(i) for i in range(1, n + 1)]
    c2 = c2 and all(d is not None for d in dates) and all(dates[i] < dates[i + 1] for i in range(n - 1))
    reperes = {1: "1999-01-07", 168: "2009-12-03", 169: "2010-01-14", 315: "2025-10-30"}
    c2 = c2 and all(k <= n and R[k - 1]["date_reunion"] == v for k, v in reperes.items())
    ok[2] = bool(c2)
    # 3
    ok[3] = R[0]["date_reunion_prec"] == "" and all(R[i]["date_reunion_prec"] == R[i - 1]["date_reunion"] for i in range(1, n))
    # 4
    d = [num(r["d_ois1y_pb"]) for r in R]
    ok[4] = all(v is not None and math.isfinite(v) and abs(v) < 100 for v in d)
    # 5
    sig = [num(r["sigma16_pb"]) for r in R]
    c5 = True
    for i in range(n):
        if i + 1 <= 16:
            c5 = c5 and sig[i] is None
        else:
            prec = d[i - 16:i]
            if sig[i] is None or any(v is None or not math.isfinite(v) for v in prec):
                c5 = False
            else:
                s = max(float(np.std(np.array(prec), ddof=1)), 0.25)
                c5 = c5 and math.isfinite(sig[i]) and abs(sig[i] - s) <= 1e-6
    ok[5] = bool(c5)
    # 6
    cn = [num(r["cible_norm"]) for r in R]
    c6 = True
    for i in range(n):
        if i + 1 <= 16:
            c6 = c6 and cn[i] is None
        else:
            c6 = c6 and cn[i] is not None and sig[i] is not None and d[i] is not None \
                and math.isfinite(cn[i]) and abs(cn[i] - d[i] / sig[i]) <= 1e-6
    ok[6] = bool(c6)
    # 7
    cp = [num(r["cible_prec_norm"]) for r in R]
    c7 = True
    for i in range(n):
        if i + 1 <= 17:
            c7 = c7 and cp[i] is None
        else:
            c7 = c7 and cp[i] is not None and cn[i - 1] is not None and math.isfinite(cp[i]) \
                and abs(cp[i] - cn[i - 1]) <= 1e-6
    ok[7] = bool(c7)
    # 8 — antériorité
    c8 = True
    for i, r in enumerate(R):
        for c in DATES_FIN:
            if r[c] != "":
                df = date(r[c])
                c8 = c8 and df is not None and dates[i] is not None and df < dates[i] and (dates[i] - df).days <= 10
            elif r["echantillon"] in ("estimation", "evaluation"):
                c8 = False
    ok[8] = bool(c8)
    # 9
    bornes = {"act_eu_60j_pct": 100, "brent_60j_pct": 300, "eurusd_60j_pct": 50, "us2a_60j_pp": 5}
    c9 = True
    for r in R:
        if r["echantillon"] in ("estimation", "evaluation"):
            for c in PRED + ["cible_norm"]:
                v = num(r[c])
                c9 = c9 and v is not None and math.isfinite(v)
                if c in bornes:
                    c9 = c9 and v is not None and abs(v) < bornes[c]
    ok[9] = bool(c9)
    # 10
    c10 = True
    for i, r in enumerate(R):
        if i + 1 <= 17:
            att = "rodage"
        elif any(num(r[c]) is None or not math.isfinite(num(r[c])) for c in PRED + ["cible_norm"]):
            att = "exclue"
        elif r["date_reunion"] <= "2009-12-03":
            att = "estimation"
        else:
            att = "evaluation"
        c10 = c10 and r["echantillon"] == att
    ok[10] = bool(c10)
    return ok


# --------------------------------------------------------------------------- prévisions
def mco(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def previsions(y, X, est_idx_de, eval_idx, reference="moyenne", gel=None):
    """Pour chaque t de eval_idx : fenêtre A_t = est_idx_de(t). Renvoie m, p (tableaux alignés sur eval_idx).
    reference : 'moyenne' (moyenne de y sur A_t) ou 'zero'. gel : coefficients fixés (sinon MCO sur A_t)."""
    m, p, nA = [], [], []
    for t in eval_idx:
        A = est_idx_de(t)
        nA.append(len(A))
        m.append(float(np.mean(y[A])) if reference == "moyenne" else 0.0)
        b = gel if gel is not None else mco(X[A], y[A])
        p.append(float(X[t] @ b))
    return np.array(m), np.array(p), nA


def stats_cw(y_eval, m, p):
    e0, e1, d = y_eval - m, y_eval - p, p - m
    f = e0 ** 2 - e1 ** 2 + d ** 2
    P = len(f)
    fbar = float(np.mean(f))
    s_f = math.sqrt(float(np.sum((f - fbar) ** 2)) / (P - 1))
    se = s_f / math.sqrt(P)
    return {"P": P, "r2_oos": 1.0 - float(np.sum(e1 ** 2)) / float(np.sum(e0 ** 2)), "cw_fbar": fbar, "cw_se": se,
            "cw_t": fbar / se, "sse0": float(np.sum(e0 ** 2)), "sse1": float(np.sum(e1 ** 2)),
            "e0": e0, "e1": e1, "d": d, "f": f}


def cw_t_de(f):
    P = len(f)
    fbar = float(np.mean(f))
    return fbar / (math.sqrt(float(np.sum((f - fbar) ** 2)) / (P - 1)) / math.sqrt(P))


def main():
    brut = pd.read_csv(FICHIER, dtype=str, keep_default_na=False, encoding="utf-8")
    ctrl = controles_schema(brut)
    violations = sum(1 for v in ctrl.values() if not v)
    print("Contrôles de schéma :", ctrl, "→ violations_schema =", violations)

    df = pd.read_csv(FICHIER)
    util = df[df["echantillon"].isin(["estimation", "evaluation"])].sort_values("date_reunion").reset_index(drop=True)
    y = util["cible_norm"].to_numpy(float)
    X = np.column_stack([np.ones(len(util))] + [util[c].to_numpy(float) for c in PRED])
    dates = util["date_reunion"].to_numpy(str)
    assert all(dates[i] < dates[i + 1] for i in range(len(dates) - 1))
    eval_idx = [i for i in range(len(util)) if util.loc[i, "echantillon"] == "evaluation"]
    estim_idx = [i for i in range(len(util)) if util.loc[i, "echantillon"] == "estimation"]
    n_eval, n_estim_init = len(eval_idx), len(estim_idx)

    # ---- § 6.1-6.2 : schéma principal (fenêtre croissante, référence = moyenne passée)
    croissante = lambda t: [i for i in range(len(util)) if dates[i] < dates[t]]  # dates strictement antérieures
    m, p, nA = previsions(y, X, croissante, eval_idx)
    S = stats_cw(y[eval_idx], m, p)
    assert np.allclose(S["f"], 2 * S["e0"] * S["d"])  # identité du § 6.2
    f = S["f"]
    cw_sans = np.array([cw_t_de(np.delete(f, k)) for k in range(len(f))])
    k_min = int(np.argmin(cw_sans))
    cw_min = float(cw_sans[k_min])
    survie = [S["r2_oos"] > 0, S["cw_t"] >= 1.645, cw_min >= 1.282]
    zone_grise = int(S["cw_t"] >= 1.282 and not all(survie))

    temoin = {"n_eval": n_eval, "n_estim_init": n_estim_init, "r2_oos": S["r2_oos"], "cw_fbar": S["cw_fbar"],
              "cw_se": S["cw_se"], "cw_t": S["cw_t"], "cw_t_min_sans_une": cw_min, "zone_grise": zone_grise,
              "violations_schema": violations}
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as fh:
        json.dump(temoin, fh, indent=2)
        fh.write("\n")
    print("\n=== Témoin ===")
    for k, v in temoin.items():
        print(f"{k} = {v!r}")
    print(f"fenêtre d'estimation : {nA[0]} lignes pour la première réunion, {nA[-1]} pour la dernière")
    print(f"réunion dont le retrait donne le minimum : {dates[eval_idx[k_min]]} (f_t = {f[k_min]:.6f})")

    prev = pd.DataFrame({"rang": util.loc[eval_idx, "rang"].to_numpy(), "date_reunion": dates[eval_idx],
                         "n_fenetre": nA, "y": y[eval_idx], "m": m, "p": p, "e0": S["e0"], "e1": S["e1"],
                         "d": S["d"], "f": f, "cw_t_sans_cette_reunion": cw_sans})
    prev.to_csv(os.path.join(ICI, "previsions_H16.csv"), index=False, float_format="%.12g")

    res = {"principal": {k: S[k] for k in ("P", "r2_oos", "cw_fbar", "cw_se", "cw_t", "sse0", "sse1")}}
    res["principal"].update({"cw_t_min_sans_une": cw_min, "reunion_du_minimum": str(dates[eval_idx[k_min]]),
                             "cw_t_max_sans_une": float(cw_sans.max()),
                             "reunion_du_maximum": str(dates[eval_idx[int(np.argmax(cw_sans))]]),
                             "conditions_paragraphe_8": {"r2_oos>0": bool(survie[0]), "cw_t>=1.645": bool(survie[1]),
                                                   "cw_t_min_sans_une>=1.282": bool(survie[2])},
                             "zone_grise": zone_grise, "controles_schema": {str(k): bool(v) for k, v in ctrl.items()},
                             "somme_f": float(f.sum()), "somme_e0e1": float((S["e0"] ** 2 - S["e1"] ** 2).sum())})

    # ---- S1 : régression dans l'échantillon, 298 lignes, HC3
    mod = sm.OLS(y, X).fit()
    hc3 = mod.get_robustcov_results(cov_type="HC3")
    noms = ["constante"] + PRED
    s1 = {"n": int(mod.nobs), "r2": float(mod.rsquared), "r2_ajuste": float(mod.rsquared_adj),
          "coefficients": {nm: {"b": float(b), "se_hc3": float(se), "t_hc3": float(b / se)}
                           for nm, b, se in zip(noms, mod.params, hc3.bse)}}

    def lecture(b, se, pos, neg):
        if b - 1.645 * se > 0:
            return pos
        if b + 1.645 * se < 0:
            return neg
        return "signe non établi"
    ca, cp = s1["coefficients"]["act_eu_60j_pct"], s1["coefficients"]["cible_prec_norm"]
    s1["lecture_actions"] = lecture(ca["b"], ca["se_hc3"], "signe de la lecture A", "signe de la lecture B")
    s1["lecture_cible_prec"] = lecture(cp["b"], cp["se_hc3"], "signe positif (opposé à Worms)", "signe négatif (celui de Worms)")
    s1["forme_previsible_apres_coup_pas_en_temps_reel"] = bool(s1["r2"] > 0.03 and S["r2_oos"] <= 0)
    res["S1"] = s1

    # ---- S2 : autres schémas, mêmes réunions d'évaluation
    def resume(St):
        return {"r2_oos": St["r2_oos"], "cw_t": St["cw_t"], "cw_fbar": St["cw_fbar"], "cw_se": St["cw_se"],
                "r2_oos>0": bool(St["r2_oos"] > 0), "cw_t>=1.645": bool(St["cw_t"] >= 1.645)}
    b_gel = mco(X[estim_idx], y[estim_idx])
    ma, pa, _ = previsions(y, X, croissante, eval_idx, reference="zero", gel=b_gel)
    glissante = lambda t: [i for i in range(len(util)) if dates[i] < dates[t]][-100:]
    mb, pb, nB = previsions(y, X, glissante, eval_idx)
    assert set(nB) == {100}
    mc, pc, _ = previsions(y, X, croissante, eval_idx, reference="zero")
    res["S2"] = {"a_gel_2009_reference_zero": resume(stats_cw(y[eval_idx], ma, pa)),
                 "b_fenetre_glissante_100": resume(stats_cw(y[eval_idx], mb, pb)),
                 "c_principal_reference_zero": resume(stats_cw(y[eval_idx], mc, pc))}

    # ---- S3a : sous-périodes
    de = dates[eval_idx]
    s3a, tot_f = [], float(f.sum())
    for deb, fin, nom in SOUS_PERIODES:
        sel = (de >= deb) & (de <= fin)
        se0, se1 = float((S["e0"][sel] ** 2).sum()), float((S["e1"][sel] ** 2).sum())
        s3a.append({"debut": deb, "fin": fin, "nom": nom, "n": int(sel.sum()), "somme_f": float(f[sel].sum()),
                    "somme_e0_2": se0, "somme_e1_2": se1, "r2_oos": 1 - se1 / se0,
                    "part_de_somme_f_totale": float(f[sel].sum()) / tot_f if tot_f != 0 else None})
    assert sum(x["n"] for x in s3a) == n_eval
    res["S3a"] = {"sous_periodes": s3a, "somme_f_totale": tot_f,
                  "plus_de_la_moitie_dans_une_sous_periode": [x["nom"] for x in s3a if tot_f != 0 and x["somme_f"] / tot_f > 0.5]}

    # ---- S3b : cible en points de base bruts, mêmes lignes
    d_prec = df["d_ois1y_pb"].shift(1)
    brute = df.assign(d_prec=d_prec)
    brute = brute[brute["echantillon"].isin(["estimation", "evaluation"])].sort_values("date_reunion").reset_index(drop=True)
    assert list(brute["rang"]) == list(util["rang"])
    yb = brute["d_ois1y_pb"].to_numpy(float)
    Xb = np.column_stack([np.ones(len(brute))] + [brute[c].to_numpy(float) for c in PRED_MARCHE] + [brute["d_prec"].to_numpy(float)])
    mbr, pbr, _ = previsions(yb, Xb, croissante, eval_idx)
    Sb = stats_cw(yb[eval_idx], mbr, pbr)
    s3b = resume(Sb)
    s3b["depend_de_la_normalisation"] = bool(((Sb["r2_oos"] > 0) != (S["r2_oos"] > 0)) or ((Sb["cw_t"] >= 1.645) != (S["cw_t"] >= 1.645)))
    res["S3b"] = s3b

    # ---- plancher : recalculé depuis le fichier
    dd = df["d_ois1y_pb"].to_numpy(float)
    s_brut = np.array([np.std(dd[i - 16:i], ddof=1) if i >= 16 else np.nan for i in range(len(df))])
    actif = s_brut < 0.25
    res["plancher"] = {"reunions_rang>=17": int(np.nansum(actif)),
                       "lignes_utilisables": int(actif[df["echantillon"].isin(["estimation", "evaluation"]).to_numpy()].sum()),
                       "evaluation": int(actif[(df["echantillon"] == "evaluation").to_numpy()].sum()),
                       "plus_petit_ecart_type_brut_pb": float(np.nanmin(s_brut)),
                       "date_du_plus_petit": str(df.loc[int(np.nanargmin(s_brut)), "date_reunion"])}
    res["descriptif_cible_evaluation"] = {"max_abs_y": float(np.abs(y[eval_idx]).max()),
                                          "date_max_abs_y": str(de[int(np.abs(y[eval_idx]).argmax())]),
                                          "max_abs_d": float(np.abs(S["d"]).max()),
                                          "date_max_abs_d": str(de[int(np.abs(S["d"]).argmax())])}

    with open(os.path.join(ICI, "resultats_analyse.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("\n=== Analyses secondaires (descriptives) ===")
    print(json.dumps({k: res[k] for k in ("S1", "S2", "S3a", "S3b", "plancher", "descriptif_cible_evaluation")}, indent=2, ensure_ascii=False))
    print(json.dumps(res["principal"], indent=2, ensure_ascii=False))

    figure(de, S, s3a, temoin)


# --------------------------------------------------------------------------- figure (fixée au § 6.3)
def figure(de, S, s3a, temoin):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    ENCRE, SECOND, MUET, GRILLE, AXE, FOND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
    BLEU, ORANGE = "#2a78d6", "#eb6834"
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": AXE, "axes.labelcolor": SECOND,
                         "xtick.color": MUET, "ytick.color": MUET, "text.color": ENCRE})
    fr = lambda v, fmt: format(v, fmt).replace(".", ",").replace("-", "−")  # virgule décimale dans le texte
    x = np.array([dt.date.fromisoformat(s) for s in de])
    cum_diff = np.cumsum(S["e0"] ** 2 - S["e1"] ** 2)
    cum_f = np.cumsum(S["f"])

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(14, 6.6), dpi=150, facecolor=FOND,
                                  gridspec_kw={"width_ratios": [2.4, 1], "wspace": 0.2, "top": 0.86})
    for a in (ax, ax2):
        a.set_facecolor(FOND)
        for c in ("top", "right"):
            a.spines[c].set_visible(False)
        a.grid(True, color=GRILLE, linewidth=0.6)
        a.set_axisbelow(True)
    lo = min(cum_diff.min(), cum_f.min(), 0.0)
    hi = max(cum_diff.max(), cum_f.max(), 0.0)
    marge = 0.08 * (hi - lo)
    ax.set_ylim(lo - marge, hi + 2.2 * marge)
    teintes = ["#f0efec", "#e6e5df", "#f0efec"]
    for (sp, t) in zip(s3a, teintes):
        d0, d1 = dt.date.fromisoformat(sp["debut"]), dt.date.fromisoformat(sp["fin"])
        ax.axvspan(d0, d1, color=t, zorder=0, linewidth=0)
        ax.text(d0 + (d1 - d0) / 2, hi + 1.9 * marge,
                f"{sp['debut'][:4]}–{sp['fin'][:4]} · {sp['n']} réunions\n{sp['nom']}\nΣ f = {fr(sp['somme_f'], '+.2f')} ; R² hors éch. = {fr(100 * sp['r2_oos'], '+.1f')} %",
                ha="center", va="top", fontsize=8, color=SECOND, linespacing=1.35)
    ax.axhline(0, color=MUET, linewidth=1.0)
    ax.step(x, cum_diff, where="post", color=BLEU, linewidth=2, label="Σ (e0² − e1²) : gain brut du modèle sur la moyenne passée")
    ax.step(x, cum_f, where="post", color=ORANGE, linewidth=2, label="Σ f : terme de Clark-West (gain corrigé du bruit d'estimation)")
    ax.annotate(fr(cum_diff[-1], "+.2f"), (x[-1], cum_diff[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=ENCRE)
    ax.annotate(fr(cum_f[-1], "+.2f"), (x[-1], cum_f[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9, color=ENCRE)
    ax.set_ylabel("somme cumulée (carrés de la cible normalisée)")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(dt.date(2009, 11, 1), dt.date(2026, 9, 1))
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.07), ncol=1, frameon=False, fontsize=9)
    fig.suptitle(f"H16 — prévision récursive (cinq prédicteurs) contre moyenne passée, {temoin['n_eval']} réunions de la BCE, 2010-2025\n"
                 f"R² hors échantillon = {fr(100 * temoin['r2_oos'], '+.2f')} % ; Clark-West t = {fr(temoin['cw_t'], '+.3f')} "
                 f"(seuils préinscrits : 1,282 et 1,645) ; minimum sans une réunion = {fr(temoin['cw_t_min_sans_une'], '+.3f')}",
                 x=0.075, y=0.985, ha="left", fontsize=11, color=ENCRE)
    ax.set_title("Sommes cumulées sur les réunions d'évaluation (au-dessus de zéro : le modèle fait mieux que la moyenne passée)",
                 loc="left", fontsize=9, color=SECOND)

    # encart (panneau de droite) : écart de prévision contre surprise réalisée, les deux centrés sur la moyenne passée
    ax2.axhline(0, color=AXE, linewidth=0.8)
    ax2.axvline(0, color=AXE, linewidth=0.8)
    ax2.scatter(S["d"], S["e0"], s=22, color=BLEU, alpha=0.75, edgecolors=FOND, linewidths=0.6)
    ax2.set_xlabel("p − m : prévision du modèle moins moyenne passée")
    ax2.set_ylabel("y − m : cible réalisée moins moyenne passée")
    r = float(np.corrcoef(S["d"], S["e0"])[0, 1])
    ax2.set_title(f"Encart : prévision contre réalisation (corrélation = {fr(r, '+.3f')})",
                  loc="left", fontsize=9, color=SECOND)
    fig.savefig(os.path.join(ICI, "figure.png"), bbox_inches="tight", facecolor=FOND)
    plt.close(fig)


if __name__ == "__main__":
    main()
