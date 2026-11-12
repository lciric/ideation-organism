"""Statistique principale et analyses secondaires de J07 (préinscription, section 6), à partir de J07_analyse.csv.

Sorties : temoin.json (les huit champs de vérification, rien d'autre), analyse_resultats.json (tout, y compris
les analyses secondaires descriptives S1-S3), previsions.csv (les prévisions ligne à ligne) et figure.png.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ICI = Path(__file__).resolve().parent


def charger():
    df = pd.read_csv(ICI / "J07_analyse.csv", dtype=str, keep_default_na=False)
    A = df[df["admissible"] == "1"].copy().sort_values("date_publication").reset_index(drop=True)
    A["y"] = A["cible_N_k"].astype(float)
    A["x1"] = A["pred_ecart_tendance_k"].astype(float)
    A["x2"] = A["pred_somme_revisions_k"].astype(float)
    return df, A


def previsions(A, regresseurs):
    """Prévisions récursives : S_i = {j de A : d3_j <= d_i} ; prévision si |S_i| >= 60."""
    d = A["date_publication"].to_numpy()
    d3 = A["date_millesime_3e"].to_numpy()
    y = A["y"].to_numpy()
    X = np.column_stack([np.ones(len(A))] + [A[c].to_numpy() for c in regresseurs])
    sorties = []
    for i in range(len(A)):
        S = np.where(d3 <= d[i])[0]
        if len(S) < 60:
            continue
        b, *_ = np.linalg.lstsq(X[S], y[S], rcond=None)
        y1 = float(X[i] @ b)
        y0 = float(y[S].mean())
        sorties.append({"i": i, "date_publication": d[i], "n_apprentissage": len(S), "y": y[i],
                        "y0": y0, "y1": y1, "b": b.tolist()})
    return sorties


def clark_west(y, y0, y1):
    y, y0, y1 = map(np.asarray, (y, y0, y1))
    e0, e1 = y - y0, y - y1
    f = e0 ** 2 - (e1 ** 2 - (y0 - y1) ** 2)
    P = len(f)
    fb = f.mean()
    g = [np.sum((f[l:] - fb) * (f[:P - l] - fb)) / P for l in range(5)]
    omega = g[0] + 2 * sum((1 - l / 5) * g[l] for l in range(1, 5))
    cw = fb / np.sqrt(omega / P)
    r2 = 1 - np.sum(e1 ** 2) / np.sum(e0 ** 2)
    return {"P": int(P), "cw_stat": float(cw), "f_moyen": float(fb), "omega": float(omega),
            "r2_hors_echantillon": float(r2), "reqm_reference_k": float(np.sqrt(np.mean(e0 ** 2))),
            "reqm_modele_k": float(np.sqrt(np.mean(e1 ** 2))), "f": f}


def cw_statsmodels(f):
    r = sm.OLS(f, np.ones(len(f))).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})
    return float(r.tvalues[0])


def main():
    df, A = charger()
    E = previsions(A, ["x1", "x2"])
    y = [e["y"] for e in E]
    y0 = [e["y0"] for e in E]
    y1 = [e["y1"] for e in E]
    res = clark_west(y, y0, y1)
    f = res.pop("f")
    cw_sm = cw_statsmodels(f)

    temoin = {
        "schema_ok": json.loads((ICI / "construire_controles.json").read_text())["schema_ok"],
        "n_admissibles": int(len(A)),
        "n_previsions": res["P"],
        "premiere_prevision_aaaammjj": int(E[0]["date_publication"].replace("-", "")),
        "cw_stat": res["cw_stat"],
        "r2_hors_echantillon": res["r2_hors_echantillon"],
        "reqm_reference_k": res["reqm_reference_k"],
        "reqm_modele_k": res["reqm_modele_k"],
    }
    (ICI / "temoin.json").write_text(json.dumps(temoin, indent=1))

    sortie = {"principal": temoin, "cw_statsmodels": cw_sm, "f_moyen": res["f_moyen"], "omega": res["omega"],
              "n_apprentissage_premiere_prevision": E[0]["n_apprentissage"],
              "n_apprentissage_derniere_prevision": E[-1]["n_apprentissage"],
              "derniere_prevision": E[-1]["date_publication"]}

    # ---------------- S1 : chaque prédicteur seul (mêmes lignes E)
    s1 = {}
    for nom, regs in [("x1_seul", ["x1"]), ("x2_seul", ["x2"])]:
        Ek = previsions(A, regs)
        assert [e["i"] for e in Ek] == [e["i"] for e in E]
        r = clark_west([e["y"] for e in Ek], [e["y0"] for e in Ek], [e["y1"] for e in Ek])
        r.pop("f")
        s1[nom] = r
    sortie["S1_descriptif"] = s1

    # ---------------- S2 : sous-périodes
    dates = np.array([e["date_publication"] for e in E])
    s2 = {}
    for nom, masque in [("avant_2008", dates < "2008-01-01"),
                        ("2008_2019", (dates >= "2008-01-01") & (dates <= "2019-12-31")),
                        ("2020_et_apres", dates >= "2020-01-01")]:
        r = clark_west(np.array(y)[masque], np.array(y0)[masque], np.array(y1)[masque])
        r.pop("f")
        s2[nom] = r
    sortie["S2_descriptif"] = s2

    # ---------------- S3 : dans l'échantillon, toutes les lignes de A
    X = sm.add_constant(A[["x1", "x2"]].to_numpy())
    ols = sm.OLS(A["y"].to_numpy(), X).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})
    sortie["S3_descriptif"] = {
        "coefficients": dict(zip(["constante", "x1", "x2"], ols.params.tolist())),
        "erreurs_types_nw4": dict(zip(["constante", "x1", "x2"], ols.bse.tolist())),
        "t_nw4": dict(zip(["constante", "x1", "x2"], ols.tvalues.tolist())),
        "r2_dans_echantillon": float(ols.rsquared),
        "moyenne_y": float(A["y"].mean()),
        "ecart_type_y": float(A["y"].std(ddof=1)),
        "ecart_type_y_ddof0": float(A["y"].std(ddof=0)),
        "n": int(len(A)),
        "coefficients_derniere_prevision": dict(zip(["constante", "x1", "x2"], E[-1]["b"])),
    }
    (ICI / "analyse_resultats.json").write_text(json.dumps(sortie, indent=1, ensure_ascii=False))

    pv = pd.DataFrame([{"date_publication": e["date_publication"], "n_apprentissage": e["n_apprentissage"],
                        "y": e["y"], "prev_reference": e["y0"], "prev_modele": e["y1"],
                        "b0": e["b"][0], "b1": e["b"][1], "b2": e["b"][2]} for e in E])
    pv["e0_carre_moins_e1_carre"] = (pv["y"] - pv["prev_reference"]) ** 2 - (pv["y"] - pv["prev_modele"]) ** 2
    pv["f_cw"] = f
    pv.to_csv(ICI / "previsions.csv", index=False)

    figure(pv, temoin)
    print(json.dumps(sortie, indent=1, ensure_ascii=False))


def figure(pv, t):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x = pd.to_datetime(pv["date_publication"])
    cum = pv["e0_carre_moins_e1_carre"].cumsum()
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    ax.axhline(0, color="#888888", lw=0.8)
    ax.plot(x, cum, color="#1f4e79", lw=1.6, drawstyle="steps-post")
    for b in ["2008-01-01", "2020-01-01"]:
        ax.axvline(pd.Timestamp(b), color="#bbbbbb", lw=0.8, ls="--")
    ax.set_ylabel("Somme cumulée de e0² − e1² (milliers²)")
    ax.set_title("J07 — référence (moyenne historique) moins modèle (x1, x2), erreurs quadratiques cumulées\n"
                 f"P = {t['n_previsions']}, R² hors échantillon = {t['r2_hors_echantillon']:.4f}, "
                 f"Clark-West = {t['cw_stat']:.3f} ; au-dessus de 0 : le modèle a fait mieux", fontsize=9)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(ICI / "figure.png")


if __name__ == "__main__":
    main()
