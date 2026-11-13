"""K01 — statistique principale et analyses secondaires, calculées à partir du seul fichier K01_analyse.csv.

Section 7 de la préinscription : b_IV (2SLS, un instrument, constante par horizon par Frisch-Waugh-Lovell),
écart-type de Driscoll-Kraay (sommes par tour, Newey-West à 8 retards, poids de Bartlett, sans correction),
première étape, forme réduite, garde 2021-2023, descriptifs. Écrit temoin.json (témoin), analyse_details.json
(détails pour le rapport) et figure.png.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import construire  # noqa: E402  (contrôles de schéma refaits sur le fichier)

FICHIER = os.path.join(ICI, "K01_analyse.csv")
C = 1.714
DELTA = 0.15
L = 8
EPISODE = [2021, 2022, 2023]

CHAMPS = ["n_violations_schema", "n_obs_iv", "n_previsionnistes_iv", "n_tours_iv", "b_iv", "et_b_iv_dk8", "t_iv",
          "borne_basse_ic90", "borne_haute_ic90", "marge_indecision", "coef_premiere_etape", "f_premiere_etape",
          "t_forme_reduite", "et_b_iv_grappes_tour", "et_b_iv_grappes_cible", "n_obs_iv_hors_2021_2023",
          "b_iv_hors_2021_2023", "et_b_iv_hors_2021_2023_dk8", "borne_haute_ic90_hors_2021_2023",
          "f_premiere_etape_hors_2021_2023", "conflit_episode", "b_iv_max_sans_une_annee", "b_iv_ef_prev",
          "et_b_iv_ef_prev_dk8", "b_mco_naif", "et_b_mco_naif_dk8", "b_intra_tour_naif",
          "et_b_intra_tour_naif_grappes_tour", "sigma_bruit_necessaire_mco", "sigma_bruit_commun_necessaire_iv",
          "n_obs_avant_2020", "b_iv_avant_2020", "et_b_iv_avant_2020_dk8", "b_mco_ef_avant_2020",
          "et_b_mco_ef_avant_2020_dk8", "n_consensus", "b_consensus", "et_b_consensus_dk8", "n_bce", "b_bce",
          "et_b_bce_dk8", "diff_bce_moins_consensus", "et_diff_dk8", "b_consensus_hors_2021_2023",
          "b_bce_hors_2021_2023"]


# ----------------------------------------------------------------------------- outils
def lrv8(S):
    """LRV₈ = Σ S_t² + 2 Σ_{j=1..8} (1 − j/9) Σ_t S_t S_{t−j} ; couples de tours présents seulement."""
    S = pd.Series(S, dtype=float)
    d = dict(zip(S.index.astype(int), S.to_numpy()))
    tot = float(np.sum(S.to_numpy() ** 2))
    for j in range(1, L + 1):
        w = 1.0 - j / (L + 1)
        tot += 2.0 * w * sum(v * d[t - j] for t, v in d.items() if (t - j) in d)
    return tot


def par(df, valeurs, cle="t_tour"):
    return pd.Series(valeurs, index=df.index).groupby(df[cle].to_numpy()).sum()


def centrer(df, cols, groupes="horizon"):
    return {c: (df[c] - df.groupby(groupes)[c].transform("mean")).to_numpy() for c in cols}


def residus_ef(df, cols):
    """Résidus MCO de chaque colonne sur des indicatrices d'identifiant et l'indicatrice horizon = 1."""
    ids = pd.get_dummies(df["id_prev"], dtype=float).to_numpy()
    X = np.column_stack([ids, (df["horizon"] == 1).astype(float).to_numpy()])
    out = {}
    for c in cols:
        y = df[c].to_numpy(dtype=float)
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        out[c] = y - X @ beta
    return out


def iv_core(df, e, x, z):
    """Étapes 2 à 8 de la section 7 sur des variables déjà centrées (ou résidualisées)."""
    szx, szz, sze = np.sum(z * x), np.sum(z * z), np.sum(z * e)
    r = {}
    if len(df) < 100 or szx == 0 or szz == 0:
        return None
    b = sze / szx
    u = e - b * x
    S = par(df, z * u)
    et = np.sqrt(lrv8(S)) / abs(szx)
    r.update(b=b, et=et, t=b / et, bb=b - C * et, bh=b + C * et)
    pi = szx / szz
    v = x - pi * z
    et_pi = np.sqrt(lrv8(par(df, z * v))) / szz
    r.update(pi=pi, et_pi=et_pi, F=(pi / et_pi) ** 2)
    rho = sze / szz
    w = e - rho * z
    et_rho = np.sqrt(lrv8(par(df, z * w))) / szz
    r.update(rho=rho, t_fr=rho / et_rho)
    r["et_grappes_tour"] = np.sqrt(np.sum(S.to_numpy() ** 2)) / abs(szx)
    Sg = par(df, z * u, "annee_cible")
    r["et_grappes_cible"] = np.sqrt(np.sum(Sg.to_numpy() ** 2)) / abs(szx)
    r["n_grappes_cible"] = len(Sg)
    r["szx"], r["szz"] = szx, szz
    return r


def iv(df):
    m = centrer(df, ["erreur", "revision", "instrument"])
    return iv_core(df, m["erreur"], m["revision"], m["instrument"])


def mco_core(df, e, x):
    sxx = np.sum(x * x)
    if len(df) < 100 or sxx == 0:
        return None
    b = np.sum(x * e) / sxx
    S = par(df, x * (e - b * x))
    return {"b": b, "et": np.sqrt(lrv8(S)) / sxx, "sxx": sxx, "S": S}


def pente_agregee(cel, nmin=20):
    if len(cel) < nmin:
        return None
    m = centrer(cel, ["e", "x"])
    sxx = np.sum(m["x"] ** 2)
    if sxx == 0:
        return None
    b = np.sum(m["x"] * m["e"]) / sxx
    S = par(cel, m["x"] * (m["e"] - b * m["x"]))
    return {"n": len(cel), "b": b, "et": np.sqrt(lrv8(S)) / sxx, "S": S, "D": sxx}


# ----------------------------------------------------------------------------- calcul
def main():
    ctrl = construire.controles(FICHIER)
    n_viol = sum(1 for ok, _ in ctrl.values() if not ok)

    s = pd.read_csv(FICHIER, dtype={"id_prev": str, "millesime": str, "statut": str})
    E = s[s["echantillon_iv"] == 1].copy()
    out = {"n_violations_schema": n_viol, "n_obs_iv": len(E), "n_previsionnistes_iv": E["id_prev"].nunique(),
           "n_tours_iv": E["t_tour"].nunique()}
    det = {}

    # --- principal
    r = iv(E)
    if r is None:
        r = {k: 0.0 for k in ["b", "et", "t", "bb", "bh", "pi", "F", "t_fr", "et_grappes_tour", "et_grappes_cible",
                              "szx"]}
    out.update(b_iv=r["b"], et_b_iv_dk8=r["et"], t_iv=r["t"], borne_basse_ic90=r["bb"], borne_haute_ic90=r["bh"],
               marge_indecision=min(-DELTA - r["bb"], r["bh"]), coef_premiere_etape=r["pi"],
               f_premiere_etape=r["F"], t_forme_reduite=r["t_fr"], et_b_iv_grappes_tour=r["et_grappes_tour"],
               et_b_iv_grappes_cible=r["et_grappes_cible"])
    det["principal"] = {k: v for k, v in r.items() if np.isscalar(v)}

    # --- hors 2021-2023
    Eh = E[~E["annee_cible"].isin(EPISODE)]
    rh = iv(Eh) or {k: 0.0 for k in ["b", "et", "bh", "F"]}
    out.update(n_obs_iv_hors_2021_2023=len(Eh), b_iv_hors_2021_2023=rh["b"], et_b_iv_hors_2021_2023_dk8=rh["et"],
               borne_haute_ic90_hors_2021_2023=rh["bh"], f_premiere_etape_hors_2021_2023=rh["F"])
    out["conflit_episode"] = int(out["borne_haute_ic90"] >= 0 and out["borne_haute_ic90_hors_2021_2023"] < 0)
    det["hors_2021_2023"] = {k: v for k, v in rh.items() if np.isscalar(v)}
    det["hors_2021_2023"]["n_tours"] = int(Eh["t_tour"].nunique())

    # --- retrait d'une année cible à la fois (étapes 1 et 2)
    sans = {}
    for y in range(2002, 2026):
        sub = E[E["annee_cible"] != y]
        m = centrer(sub, ["erreur", "revision", "instrument"])
        szx = np.sum(m["instrument"] * m["revision"])
        sans[y] = float(np.sum(m["instrument"] * m["erreur"]) / szx) if len(sub) >= 100 and szx != 0 else 0.0
    out["b_iv_max_sans_une_annee"] = max(sans.values())
    det["b_iv_sans_une_annee"] = sans

    # --- effets fixes de prévisionniste
    m = residus_ef(E, ["erreur", "revision", "instrument"])
    re_ = iv_core(E, m["erreur"], m["revision"], m["instrument"]) or {"b": 0.0, "et": 0.0}
    out.update(b_iv_ef_prev=re_["b"], et_b_iv_ef_prev_dk8=re_["et"])
    det["ef_prev"] = {k: v for k, v in re_.items() if np.isscalar(v)}

    # --- MCO naïf regroupé
    mc = centrer(E, ["erreur", "revision", "instrument"])
    rm = mco_core(E, mc["erreur"], mc["revision"]) or {"b": 0.0, "et": 0.0, "sxx": 0.0}
    out.update(b_mco_naif=rm["b"], et_b_mco_naif_dk8=rm["et"])

    # --- pente naïve intra-tour (cellule t_tour × annee_cible)
    mi = centrer(E, ["erreur", "revision"], ["t_tour", "annee_cible"])
    sxx = np.sum(mi["revision"] ** 2)
    if len(E) >= 100 and sxx != 0:
        bi = np.sum(mi["revision"] * mi["erreur"]) / sxx
        ui = mi["erreur"] - bi * mi["revision"]
        Si = par(E, mi["revision"] * ui)
        out.update(b_intra_tour_naif=bi, et_b_intra_tour_naif_grappes_tour=np.sqrt(np.sum(Si.to_numpy() ** 2)) / sxx)
    else:
        out.update(b_intra_tour_naif=0.0, et_b_intra_tour_naif_grappes_tour=0.0)

    # --- bornes de bruit
    n = len(E)
    out["sigma_bruit_necessaire_mco"] = float(np.sqrt(max(0.0, -out["b_mco_naif"]) * rm["sxx"] / n)) if n else 0.0
    out["sigma_bruit_commun_necessaire_iv"] = (float(np.sqrt(max(0.0, -out["b_iv"]) * max(0.0, r["szx"] / n)))
                                               if n else 0.0)

    # --- avant 2020
    Ea = E[E["annee_cible"] <= 2019]
    ra = iv(Ea) or {"b": 0.0, "et": 0.0}
    ma = residus_ef(Ea, ["erreur", "revision"])
    rma = mco_core(Ea, ma["erreur"], ma["revision"]) or {"b": 0.0, "et": 0.0}
    out.update(n_obs_avant_2020=len(Ea), b_iv_avant_2020=ra["b"], et_b_iv_avant_2020_dk8=ra["et"],
               b_mco_ef_avant_2020=rma["b"], et_b_mco_ef_avant_2020_dk8=rma["et"])
    det["avant_2020_iv"] = {k: v for k, v in ra.items() if np.isscalar(v)}

    # --- consensus et BCE
    spf = s[s["source"] == "SPF"]
    cons = spf.groupby(["t_tour", "annee_cible"])["prevision"].mean()
    real = s.dropna(subset=["realise"]).groupby("annee_cible")["realise"].first()
    cel = []
    for t in range(8008, 8104):
        an = t // 4  # année du tour : t = 4·an + q − 1, q ∈ {1..4}
        for y in (an, an + 1):
            if y <= 2025:
                cel.append((t, y, y - an))
    cel = pd.DataFrame(cel, columns=["t_tour", "annee_cible", "horizon"])
    cc = cel.copy()
    cc["C"] = [cons.get((t, y), np.nan) for t, y in zip(cc["t_tour"], cc["annee_cible"])]
    cc["Cp"] = [cons.get((t - 1, y), np.nan) for t, y in zip(cc["t_tour"], cc["annee_cible"])]
    cc["x"] = cc["C"] - cc["Cp"]
    cc["e"] = cc["annee_cible"].map(real) - cc["C"]
    cc = cc.dropna(subset=["x", "e"]).reset_index(drop=True)
    b = s[s["source"] == "BCE"].merge(cel, on=["t_tour", "annee_cible", "horizon"])
    bc = pd.DataFrame({"t_tour": b["t_tour"], "annee_cible": b["annee_cible"], "horizon": b["horizon"],
                       "x": b["revision"], "e": b["erreur"]}).dropna(subset=["x", "e"]).reset_index(drop=True)
    rc = pente_agregee(cc)
    rb = pente_agregee(bc)
    out.update(n_consensus=len(cc), b_consensus=rc["b"] if rc else 0.0, et_b_consensus_dk8=rc["et"] if rc else 0.0,
               n_bce=len(bc), b_bce=rb["b"] if rb else 0.0, et_b_bce_dk8=rb["et"] if rb else 0.0)
    if rc and rb:
        out["diff_bce_moins_consensus"] = rb["b"] - rc["b"]
        idx = sorted(set(rb["S"].index) | set(rc["S"].index))
        psi = (rb["S"].reindex(idx, fill_value=0.0) / rb["D"] - rc["S"].reindex(idx, fill_value=0.0) / rc["D"])
        out["et_diff_dk8"] = float(np.sqrt(lrv8(psi)))
    else:
        out["diff_bce_moins_consensus"], out["et_diff_dk8"] = 0.0, 0.0
    rch = pente_agregee(cc[~cc["annee_cible"].isin(EPISODE)].reset_index(drop=True))
    rbh = pente_agregee(bc[~bc["annee_cible"].isin(EPISODE)].reset_index(drop=True))
    out["b_consensus_hors_2021_2023"] = rch["b"] if rch else 0.0
    out["b_bce_hors_2021_2023"] = rbh["b"] if rbh else 0.0
    det["agreges"] = {"n_consensus_h0": int((cc["horizon"] == 0).sum()), "n_consensus_h1": int((cc["horizon"] == 1).sum()),
                      "n_bce_h0": int((bc["horizon"] == 0).sum()), "n_bce_h1": int((bc["horizon"] == 1).sum()),
                      "n_consensus_hors": rch["n"] if rch else 0, "n_bce_hors": rbh["n"] if rbh else 0,
                      "et_b_consensus_hors_dk8": rch["et"] if rch else 0.0,
                      "et_b_bce_hors_dk8": rbh["et"] if rbh else 0.0}

    # --- témoin
    temoin = {}
    for k in CHAMPS:
        v = out[k]
        temoin[k] = int(v) if isinstance(v, (int, np.integer)) else float(v)
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(temoin, f, indent=1)

    det["controles"] = {str(k): bool(ok) for k, (ok, _) in ctrl.items()}
    det["descriptif_echantillon"] = descriptif(E)
    with open(os.path.join(ICI, "analyse_details.json"), "w", encoding="utf-8") as f:
        json.dump(det, f, indent=1, default=float)

    figure(temoin)
    for k in CHAMPS:
        print(f"{k:40s} {temoin[k]}")
    return temoin


def descriptif(E):
    """Moments simples de l'échantillon E (descriptifs)."""
    d = {}
    for c in ["revision", "instrument", "erreur"]:
        d[c] = {"moyenne": float(E[c].mean()), "ecart_type": float(E[c].std()),
                "part_nulle": float((E[c] == 0).mean()) if c != "erreur" else None}
    d["corr_revision_instrument"] = float(np.corrcoef(E["revision"], E["instrument"])[0, 1])
    return d


# ----------------------------------------------------------------------------- figure
def figure(t):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    lignes = [
        ("b_IV, 2002-2025 (statistique principale)", t["b_iv"], t["et_b_iv_dk8"], True),
        ("b_IV, hors cibles 2021-2023", t["b_iv_hors_2021_2023"], t["et_b_iv_hors_2021_2023_dk8"], False),
        ("b_IV, cibles 2002-2019", t["b_iv_avant_2020"], t["et_b_iv_avant_2020_dk8"], False),
        ("b_IV avec effets fixes de prévisionniste", t["b_iv_ef_prev"], t["et_b_iv_ef_prev_dk8"], False),
        ("MCO naïf regroupé", t["b_mco_naif"], t["et_b_mco_naif_dk8"], False),
        ("Consensus (moyenne SPF)", t["b_consensus"], t["et_b_consensus_dk8"], False),
        ("Projections BCE (MPD)", t["b_bce"], t["et_b_bce_dk8"], False),
    ]
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    ink, muted, accent = "#1f2328", "#6e7781", "#2f5d9e"
    ax.axvspan(-DELTA, 0, color="#eef1f5", zorder=0)
    ax.axvline(0, color=ink, lw=1, zorder=1)
    ax.axvline(-DELTA, color=muted, lw=1, ls="--", zorder=1)
    for i, (nom, b, et, princ) in enumerate(lignes):
        y = len(lignes) - 1 - i
        col = accent if princ else muted
        ax.plot([b - C * et, b + C * et], [y, y], color=col, lw=2.5 if princ else 1.6, solid_capstyle="round")
        ax.plot(b, y, "o", color=col, ms=8 if princ else 6, mec="white", mew=1.5, zorder=3)
        lab = f"{b:+.3f}  [{b - C * et:+.2f} ; {b + C * et:+.2f}]".replace(".", ",")
        ax.text(b + C * et + 0.03, y, lab, va="center", fontsize=8, color=ink)
    ax.set_yticks(range(len(lignes)))
    ax.set_yticklabels([n for n, *_ in lignes][::-1], fontsize=9, color=ink)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.set_xlabel("Pente de l'erreur sur la révision (points d'erreur par point de révision)", fontsize=9)
    ax.text(-DELTA - 0.02, -0.75, "−0,15\n(prédiction H1)", ha="right", va="center", fontsize=7.5, color=muted)
    ax.set_title("K01 — pente erreur-révision, intervalle à 90 % (b ± 1,714 × e.-t. Driscoll-Kraay, 8 retards)",
                 fontsize=10, color=ink, loc="left")
    fig.text(0.01, 0.01, "Seule la première ligne entre dans la règle préinscrite ; les autres sont descriptives "
             "\n(pour elles, l'intervalle b ± 1,714 × e.-t. n'est qu'un repère visuel). Zone grisée : entre −0,15 et 0. "
             "n = 8 595 lignes, 94 prévisionnistes, 96 tours.", fontsize=7, color=muted, ha="left", va="bottom")
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#d0d7de", lw=0.5)
    ax.set_axisbelow(True)
    xmax = max(b + C * et for _, b, et, _ in lignes)
    xmin = min(b - C * et for _, b, et, _ in lignes)
    ax.set_xlim(min(xmin, -0.2) - 0.12, xmax + 0.55)
    ax.set_ylim(-1.2, len(lignes) - 0.4)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(os.path.join(ICI, "figure.png"))


if __name__ == "__main__":
    main()
