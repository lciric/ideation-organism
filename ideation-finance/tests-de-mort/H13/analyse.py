#!/usr/bin/env python3
"""H13 — statistique principale, placebo et analyses secondaires S1 à S3, selon la section 6 de la préinscription.

Lit H13_analyse.csv ; écrit temoin.json, resultats_detail.json et figure.png. Déterministe, aucun tirage aléatoire.
"""
import json
import os

import numpy as np
import pandas as pd

import construire

ICI = os.path.dirname(os.path.abspath(__file__))


def mco_hc3(y, X):
    """b = (X'X)^-1 X'y ; V = (X'X)^-1 [sum (e_i/(1-h_i))^2 x_i x_i'] (X'X)^-1 ; aucun autre facteur."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    XtXi = np.linalg.inv(X.T @ X)
    b = XtXi @ X.T @ y
    e = y - X @ b
    h = np.einsum("ij,jk,ik->i", X, XtXi, X)
    u = e / (1.0 - h)
    V = XtXi @ (X.T @ (X * (u ** 2)[:, None])) @ XtXi
    return b, np.sqrt(np.diag(V)), e, h, V


def variables(d):
    v = pd.DataFrame(index=d.index)
    v["y"] = 100.0 * (d["dgs2_j"] - d["dgs2_veille"])
    v["y_veille"] = 100.0 * (d["dgs2_veille"] - d["dgs2_avant_veille"])
    v["N"] = (d["emploi_1re_k"] - d["emploi_3e_k"]) / 100.0
    v["R1"] = d["rev_m1_k"] / 100.0
    v["R2"] = d["rev_m2_k"] / 100.0
    v["U"] = d["d_chomage_pt"]
    v["T"] = d["tendance_12m_k"] / 100.0
    v["Sn"] = d["emploi_1re_k"] / 100.0 - v["T"]
    return v


def matrice(v, extra=()):
    cols = [np.ones(len(v)), v["N"], v["R1"], v["R2"], v["U"], v["T"]] + [v[c] for c in extra]
    return np.column_stack(cols)


def main():
    chemin = os.path.join(ICI, "H13_analyse.csv")
    schema, info = construire.controles(chemin)
    schema_ok = int(all(schema.values()))
    a = pd.read_csv(chemin)

    # ---- décompte des filtres
    filtres = {
        "lignes_fichier": int(len(a)),
        "complet_0": int((a["complet"] == 0).sum()),
        "n_mois_nouveaux_2": int((a["n_mois_nouveaux"] != 1).sum()),
        "revision_large_1": int((a["revision_large"] == 1).sum()),
        "extreme_1": int((a["extreme"] == 1).sum()),
    }
    reste = a
    seq = {}
    for nom, masque in [("apres_complet", lambda d: d["complet"] == 1),
                        ("apres_n_mois_nouveaux", lambda d: d["n_mois_nouveaux"] == 1),
                        ("apres_revision_large", lambda d: d["revision_large"] == 0),
                        ("apres_extreme", lambda d: d["extreme"] == 0)]:
        reste = reste[masque(reste)]
        seq[nom] = int(len(reste))
    filtres["sequentiel"] = seq
    filtres["dates_complet_0"] = a.loc[a["complet"] == 0, "date_publication"].tolist()
    filtres["dates_n_mois_nouveaux_2"] = a.loc[a["n_mois_nouveaux"] != 1, "date_publication"].tolist()

    # ---- échantillon principal
    P = a[a["principal"] == 1]
    v = variables(P)
    n = int(len(v))
    X = matrice(v)
    b, et, e, h, _ = mco_hc3(v["y"], X)
    beta, ET = float(b[1]), float(et[1])
    t = beta / ET
    inf, sup = beta - 1.96 * ET, beta + 1.96 * ET
    marge = min(1.96 - t, sup - 1.0)

    bp, etp, _, _, _ = mco_hc3(v["y_veille"], X)
    t_placebo = abs(float(bp[1]) / float(etp[1]))

    temoin = {
        "schema_ok": schema_ok,
        "n_publications": n,
        "beta_pb_par_100k": beta,
        "erreur_type_pb": ET,
        "t_stat": t,
        "borne_inf_95_pb": inf,
        "borne_sup_95_pb": sup,
        "marge_zone_grise": marge,
        "t_placebo_abs": t_placebo,
    }
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, indent=2)
        f.write("\n")

    noms = ["constante", "N", "R1", "R2", "U", "T"]
    detail = {
        "schema": {str(k): int(x) for k, x in schema.items()},
        "alignement_dgs2_sveny02": info,
        "filtres": filtres,
        "principal": {
            "coefficients": dict(zip(noms, map(float, b))),
            "erreurs_type_hc3": dict(zip(noms, map(float, et))),
            "r2": float(1 - (e @ e) / ((v["y"] - v["y"].mean()) ** 2).sum()),
            "levier_max": float(h.max()),
            "ecart_type_N": float(v["N"].std(ddof=1)),
            "ecart_type_y": float(v["y"].std(ddof=1)),
            "ecart_absolu_moyen_N": float(v["N"].abs().mean()),
            "moyenne_N": float(v["N"].mean()),
            "moyenne_y": float(v["y"].mean()),
            "premiere_date": P["date_publication"].min(),
            "derniere_date": P["date_publication"].max(),
        },
        "placebo": {
            "coefficient_N": float(bp[1]), "erreur_type_hc3": float(etp[1]), "t_abs": t_placebo,
        },
    }

    # ---- recoupement statsmodels (même formule attendue)
    try:
        import statsmodels.api as sm
        r = sm.OLS(v["y"].values, X).fit(cov_type="HC3")
        detail["recoupement_statsmodels"] = {"beta": float(r.params[1]), "erreur_type": float(r.bse[1])}
    except Exception as ex:  # noqa: BLE001
        detail["recoupement_statsmodels"] = {"erreur": repr(ex)}

    # ---- S1 : nature des révisions (emploi seul)
    X1 = np.column_stack([np.ones(n), v["N"]])
    b1, et1, _, _, _ = mco_hc3(v["Sn"], X1)
    p_hat = float(b1[1])
    s1 = {"p_hat": p_hat, "erreur_type_hc3": float(et1[1]), "constante": float(b1[0]), "n": n}
    s1["beta_sur_p_hat"] = (beta / p_hat) if p_hat >= 0.3 else None
    detail["S1"] = s1

    # ---- S2 : à chiffre publié donné
    X2 = matrice(v, extra=("Sn",))
    b2, et2, _, _, _ = mco_hc3(v["y"], X2)
    detail["S2"] = {
        "coefficient_Sn": float(b2[6]), "erreur_type_Sn_hc3": float(et2[6]),
        "coefficient_N_delta": float(b2[1]), "erreur_type_N_hc3": float(et2[1]),
        "rang_X": int(np.linalg.matrix_rank(X2)), "conditionnement_X": float(np.linalg.cond(X2)), "n": n,
    }

    # ---- S3 : sensibilité à la règle A7
    Q = a[(a["complet"] == 1) & (a["n_mois_nouveaux"] == 1) & (a["revision_large"] == 0)]
    v3 = variables(Q)
    b3, et3, _, _, _ = mco_hc3(v3["y"], matrice(v3))
    detail["S3"] = {
        "beta": float(b3[1]), "erreur_type_hc3": float(et3[1]), "n": int(len(Q)),
        "dates_extreme_1_dans_S3": Q.loc[Q["extreme"] == 1, "date_publication"].tolist(),
        "dates_extreme_1_fichier": a.loc[a["extreme"] == 1, "date_publication"].tolist(),
    }

    with open(os.path.join(ICI, "resultats_detail.json"), "w", encoding="utf-8") as f:
        json.dump(detail, f, indent=2, ensure_ascii=False)
        f.write("\n")

    figure(v, X, b, beta, ET, n)

    print(json.dumps(temoin, indent=2))
    print(json.dumps(detail, indent=2, ensure_ascii=False))


def figure(v, X, b, beta, ET, n):
    """Régression partielle (Frisch-Waugh) : y et N purgés de la constante et des quatre contrôles.
    La pente MCO du nuage résiduel est exactement β. Bande : β ± 1,96 × ET (HC3)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    Z = X[:, [0, 2, 3, 4, 5]]
    proj = lambda w: w - Z @ np.linalg.lstsq(Z, w, rcond=None)[0]  # noqa: E731
    yr, nr = proj(v["y"].values), proj(v["N"].values)

    k = 10
    ordre = np.argsort(nr, kind="stable")
    groupes = np.array_split(ordre, k)
    gx = np.array([nr[g].mean() for g in groupes])
    gy = np.array([yr[g].mean() for g in groupes])
    gs = np.array([yr[g].std(ddof=1) / np.sqrt(len(g)) for g in groupes])

    bleu, gris, encre = "#2f6fb0", "#9aa3ad", "#1f2933"
    fig, ax = plt.subplots(figsize=(9, 5.8), dpi=150)
    ax.scatter(nr, yr, s=9, color=gris, alpha=0.45, linewidths=0, label=f"publications (n = {n})", zorder=1)
    xs = np.linspace(nr.min(), nr.max(), 200)
    ax.fill_between(xs, (beta - 1.96 * ET) * xs, (beta + 1.96 * ET) * xs, color=bleu, alpha=0.15, linewidth=0,
                    label="pente ± 1,96 × erreur type HC3", zorder=2)
    ax.plot(xs, beta * xs, color=bleu, linewidth=2, label=f"droite ajustée : β = {beta:+.2f} pb par 100 000".replace(".", ","),
            zorder=3)
    ax.errorbar(gx, gy, yerr=1.96 * gs, fmt="o", color=encre, markersize=5.5, elinewidth=1.1, capsize=2.5,
                label="moyennes par dixième de N (± 1,96 erreur type)", zorder=4)
    ax.axhline(0, color="#c5cbd3", linewidth=0.8, zorder=0)
    ax.axvline(0, color="#c5cbd3", linewidth=0.8, zorder=0)
    ax.set_xlabel("N résiduel : (1re − 3e estimation) / 100 000 emplois, purgé des quatre contrôles")
    ax.set_ylabel("Δ taux à 2 ans le jour de la publication, résiduel (pb)")
    ax.set_title("H13 — variation du taux à 2 ans le jour de l'emploi et partie du chiffre révisée ensuite\n"
                 f"β = {beta:+.3f} pb par 100 000 ; erreur type HC3 {ET:.3f} ; "
                 f"IC 95 % [{beta - 1.96 * ET:+.2f} ; {beta + 1.96 * ET:+.2f}]".replace(".", ","),
                 fontsize=10.5, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(ICI, "figure.png"))
    plt.close(fig)


if __name__ == "__main__":
    main()
