"""J02 - statistique principale et analyses secondaires (section 6 de la preinscription), a partir du seul fichier
J02_analyse.csv. Ecrit temoin.json (champs_verification, nombres seulement) et analyse_detail.json (details descriptifs).
Usage : python3 -I analyse.py
"""
import json, math, pathlib, sys
import numpy as np
import pandas as pd

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from controles_schema import controler  # noqa: E402

FICHIER = ICI / "J02_analyse.csv"
Z = 1.645


def charger():
    d = pd.read_csv(FICHIER, dtype=str, keep_default_na=False)
    d["t_cible"] = d["t_cible"].astype(int)
    d["annee_cible"] = d["annee_cible"].astype(int)
    for c in ("revision", "erreur"):
        d[c] = pd.to_numeric(d[c].replace("", np.nan))
    comp = d[d["revision"].notna() & d["erreur"].notna()].sort_values("t_cible").reset_index(drop=True)
    return d, comp


def pearson(r, e):
    r = np.asarray(r, float); e = np.asarray(e, float)
    if len(r) < 2:
        return 0.0
    rc, ec = r - r.mean(), e - e.mean()
    den = math.sqrt((rc ** 2).sum() * (ec ** 2).sum())
    return float((rc * ec).sum() / den) if den > 0 else 0.0


def nw_s(v, t, L):
    """S = Gamma_0 + 2 sum_{j=1..L} (1 - j/(L+1)) Gamma_j ; Gamma_j sur les couples dont t_cible differe de j."""
    pos = {int(tt): i for i, tt in enumerate(t)}
    S = float((v ** 2).sum())
    for j in range(1, L + 1):
        g = sum(v[i] * v[pos[int(tt) - j]] for i, tt in enumerate(t) if int(tt) - j in pos)
        S += 2 * (1 - j / (L + 1)) * g
    return S


def pente(sub, L=4):
    """Etapes 1 a 9 sur un (sous-)echantillon de lignes completes ; convention : n < 10 ou variance nulle -> zeros."""
    r = sub["revision"].to_numpy(float); e = sub["erreur"].to_numpy(float); t = sub["t_cible"].to_numpy(int)
    n = len(r)
    vide = {"n": n, "beta_z": 0.0, "et": 0.0, "t": 0.0, "bas": 0.0, "haut": 0.0, "beta_brut": 0.0,
            "et_brut": 0.0, "s_r": 0.0, "s_e": 0.0, "S": 0.0}
    if n < 10:
        return vide
    s_r, s_e = r.std(ddof=1), e.std(ddof=1)
    if s_r == 0 or s_e == 0:
        return vide
    z = (r - r.mean()) / s_r
    y = (e - e.mean()) / s_e
    szz = float((z ** 2).sum())
    b = float((z * y).sum() / szz)
    u = y - b * z
    v = z * u
    S = nw_s(v, t, L)
    et = math.sqrt(S) / szz
    return {"n": n, "beta_z": b, "et": et, "t": b / et, "bas": b - Z * et, "haut": b + Z * et,
            "beta_brut": b * s_e / s_r, "et_brut": et * s_e / s_r, "s_r": float(s_r), "s_e": float(s_e), "S": S}


def bootstrap(comp, B=9999, bloc=8, graine=20261112):
    r = comp["revision"].to_numpy(float); e = comp["erreur"].to_numpy(float)
    n = len(r)
    k = math.ceil(n / bloc)
    rng = np.random.default_rng(graine)
    stats, rejets = [], 0
    while len(stats) < B:
        debuts = rng.integers(0, n - 7, size=k)
        idx = np.concatenate([np.arange(s, s + bloc) for s in debuts])[:n]
        rb, eb = r[idx], e[idx]
        if rb.std() == 0 or eb.std() == 0:
            rejets += 1
            continue
        stats.append(pearson(rb, eb))
    stats = np.array(stats)
    return float(np.percentile(stats, 5)), float(np.percentile(stats, 95)), rejets, stats


def main():
    d, comp = charger()
    ctrl = controler(FICHIER)
    n = len(comp)
    p = pente(comp, 4)
    p8 = pente(comp, 8)
    # garde : retirer deux annees civiles consecutives
    garde = {}
    for Y in range(1999, 2026):
        s = comp[~comp["annee_cible"].isin([Y, Y + 1])]
        garde[Y] = pearson(s["revision"], s["erreur"]) if len(s) >= 10 else 0.0
    vmin = min(garde.values())
    ymin = min(Y for Y, v in garde.items() if v == vmin)
    marge = min(-p["bas"], p["haut"] - 0.40)
    conflit = 1 if (p["bas"] > 0 and p["haut"] >= 0.40 and vmin <= 0) else 0
    # S1
    s1 = pente(comp[comp["t_cible"] <= 8079], 4)
    # S2
    bb_bas, bb_haut, rejets, stats = bootstrap(comp)
    # S3
    s3 = pente(comp[(comp["t_cible"] < 8084) | (comp["t_cible"] > 8095)], 4)
    une = {}
    for Y in range(1999, 2027):
        s = comp[comp["annee_cible"] != Y]
        une[Y] = pearson(s["revision"], s["erreur"]) if len(s) >= 10 else 0.0
    vmin1 = min(une.values())

    convention = n < 10 or p["s_r"] == 0 or p["s_e"] == 0
    temoin = {
        "n_violations_schema": ctrl["n_violations_schema"],
        "n_cibles": n,
        "beta_z": p["beta_z"],
        "et_beta_z_nw4": p["et"],
        "t_nw4": p["t"],
        "borne_basse_ic90": p["bas"],
        "borne_haute_ic90": p["haut"],
        "marge_indecision": marge,
        "beta_z_min_sans_deux_ans": vmin,
        "annee_debut_min": ymin,
        "conflit_robustesse": conflit,
        "beta_brut": p["beta_brut"],
        "et_beta_brut_nw4": p["et_brut"],
        "ecart_type_revision": p["s_r"],
        "ecart_type_erreur": p["s_e"],
        "n_avant_2020": s1["n"],
        "beta_z_avant_2020": s1["beta_z"],
        "beta_brut_avant_2020": s1["beta_brut"],
        "et_beta_brut_avant_2020_nw4": s1["et_brut"],
        "et_beta_z_nw8": p8["et"],
        "bb_borne_basse_ic90": bb_bas,
        "bb_borne_haute_ic90": bb_haut,
        "n_hors_2021_2023": s3["n"],
        "beta_z_hors_2021_2023": s3["beta_z"],
        "et_beta_z_hors_2021_2023_nw4": s3["et"],
        "beta_z_min_sans_une_annee": vmin1,
    }
    if convention:
        temoin = {k: (v if k in ("n_violations_schema", "n_cibles") else 0) for k, v in temoin.items()}
    (ICI / "temoin.json").write_text(json.dumps(temoin, indent=1))

    # verification croisee statsmodels (aucune cible ne manque -> equivalence annoncee a l'etape 7)
    sm_et = None
    try:
        import statsmodels.api as sm
        r = comp["revision"].to_numpy(float); e = comp["erreur"].to_numpy(float)
        z = (r - r.mean()) / r.std(ddof=1); y = (e - e.mean()) / e.std(ddof=1)
        fit = sm.OLS(y, sm.add_constant(z)).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})
        sm_et = {"beta": float(fit.params[1]), "et": float(fit.bse[1]), "cibles_contigues": bool(
            (np.diff(comp["t_cible"].to_numpy()) == 1).all())}
    except Exception as exc:  # pragma: no cover
        sm_et = {"erreur": repr(exc)}
    detail = {
        "controles_schema": ctrl,
        "principal": p, "nw8": p8, "S1_avant_2020": s1, "S3_hors_2021_2023": s3,
        "garde_sans_deux_ans": {str(k): v for k, v in garde.items()},
        "sans_une_annee": {str(k): v for k, v in une.items()},
        "annee_min_sans_une_annee": min(Y for Y, v in une.items() if v == vmin1),
        "bootstrap": {"B": len(stats), "rejets": rejets, "moyenne": float(stats.mean()),
                      "mediane": float(np.median(stats)), "p5": bb_bas, "p95": bb_haut},
        "moyennes": {"revision": float(comp["revision"].mean()), "erreur": float(comp["erreur"].mean())},
        "part_revisions_nulles": float((comp["revision"].abs() < 1e-9).mean()),
        "statsmodels_hac4": sm_et,
        "convention_zeros_appliquee": convention,
    }
    (ICI / "analyse_detail.json").write_text(json.dumps(detail, indent=1, ensure_ascii=False))
    print(json.dumps(temoin, indent=1))
    figure(comp, p)


def figure(comp, p):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    r = comp["revision"].to_numpy(float); e = comp["erreur"].to_numpy(float)
    z = (r - r.mean()) / r.std(ddof=1); y = (e - e.mean()) / e.std(ddof=1)
    ep = ((comp["t_cible"] >= 8084) & (comp["t_cible"] <= 8095)).to_numpy()
    fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=150)
    xs = np.linspace(min(z.min(), -3) - 0.3, max(z.max(), 3) + 0.3, 200)
    ax.fill_between(xs, p["bas"] * xs, p["haut"] * xs, color="#2a6fdb", alpha=0.15, lw=0,
                    label=f"IC 90 % Newey-West (4 retards) : [{p['bas']:.3f} ; {p['haut']:.3f}]".replace(".", ","))
    ax.plot(xs, 0.40 * xs, color="#888888", ls="--", lw=1, label="pente prédite par la fiche : 0,40")
    ax.plot(xs, p["beta_z"] * xs, color="#2a6fdb", lw=2, label=f"pente estimée β_z = {p['beta_z']:.3f}".replace(".", ","))
    jit = 0  # pas de bruit ajouté : les révisions arrondies à 0,1 se superposent
    ax.scatter(z[~ep], y[~ep] + jit, s=22, color="#444444", alpha=0.7, label=f"cibles hors 2021-2023 (n = {(~ep).sum()})")
    ax.scatter(z[ep], y[ep], s=40, color="#d94f1e", marker="D", edgecolor="white", lw=0.6,
               label=f"cibles 2021T1-2023T4 (n = {ep.sum()})")
    for zi, yi, c in zip(z[ep], y[ep], comp.loc[ep, "cible"]):
        ax.annotate(c.replace("-Q", "T"), (zi, yi), fontsize=6, color="#d94f1e", xytext=(3, 3), textcoords="offset points")
    ax.axhline(0, color="#cccccc", lw=0.8, zorder=0); ax.axvline(0, color="#cccccc", lw=0.8, zorder=0)
    ax.set_xlim(xs.min(), xs.max())
    ax.set_xlabel("révision réduite  z = (r − r̄) / s_r   (r = f₂ − f₃)")
    ax.set_ylabel("erreur réduite  y = (e − ē) / s_e   (e = réalisé − f₂)")
    ax.set_title(f"J02 — erreur sur révision à horizon 2, cibles 1999T4-2026T3 (n = {p['n']})", fontsize=10)
    ax.legend(fontsize=7, loc="upper left", frameon=False)
    ax.text(0.99, 0.01, "Révisions multiples de 0,1 point : beaucoup de points se superposent (aucun bruit ajouté).",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6, color="#666666")
    fig.tight_layout()
    fig.savefig(ICI / "figure.png")


if __name__ == "__main__":
    main()
