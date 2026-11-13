#!/usr/bin/env python3
"""K20-ZE : statistique de la preinscription (section 6), a partir du SEUL fichier d'analyse K20-ZE_analyse.csv.
Seuls n_violations_schema et n_anomalies_hors_principal viennent des controles de construire.py, relances sur ce fichier.
Ecrit temoin.json et figure.png. Ne calcule aucun verdict.   Usage : python3 -I analyse.py"""
import importlib.util, json, pathlib, sys
import numpy as np
import pandas as pd

ICI = pathlib.Path(__file__).resolve().parent
CSV = ICI / "K20-ZE_analyse.csv"
TCRIT = 1.708
INCIDENTS = []

# ------------------------------------------------------------------ outils
def charge():
    d = pd.read_csv(CSV, dtype={"variable": str, "tour": str, "tour_prec": str, "ref_periode": str,
                                "ref_periode_prec": str, "episode": str})
    d["serie"] = d.variable + "_h" + d.horizon.astype(str)
    return d

SERIES = ["HICP_h0", "HICP_h1", "RGDP_h0", "RGDP_h1", "UNEM_h0", "UNEM_h1"]

def reduire(d, rev, err):
    """6.1 : z_r, z_e par serie, moyenne et ecart-type (n-1) calcules sur les lignes principales ; appliques a toutes les lignes."""
    zr, ze, k = pd.Series(np.nan, d.index), pd.Series(np.nan, d.index), {}
    for g in SERIES:
        m = d.serie == g
        p = m & (d.principal == 1)
        mr, sr = d.loc[p, rev].mean(), d.loc[p, rev].std(ddof=1)
        me, se = d.loc[p, err].mean(), d.loc[p, err].std(ddof=1)
        zr[m] = (d.loc[m, rev] - mr) / sr
        ze[m] = (d.loc[m, err] - me) / se
        k[g] = sr / se
    return zr, ze, k

def dk_cov(X, u, tours, lag, groupes=None):
    """6.4 : somme des scores par tour (tours sans ligne = vecteur nul), poids de Bartlett 1 - j/(lag+1)."""
    h = X * u[:, None]
    p = X.shape[1]
    if groupes is None:
        t0, t1 = int(tours.min()), int(tours.max())
        H = np.zeros((t1 - t0 + 1, p))
        np.add.at(H, (tours - t0).astype(int), h)
    else:
        cles = np.unique(groupes)
        H = np.zeros((len(cles), p))
        np.add.at(H, np.searchsorted(cles, groupes), h)
    Om = H.T @ H
    for j in range(1, lag + 1):
        if j >= len(H): break
        C = H[j:].T @ H[:-j]
        Om += (1 - j / (lag + 1)) * (C + C.T)
    A = np.linalg.inv(X.T @ X)
    return A @ Om @ A

def mco(X, y):
    beta = np.linalg.solve(X.T @ X, X.T @ y)
    return beta, y - X @ beta

def matrice(sous, zr, ze, L, mode="principal"):
    """mode 'principal' : 6 constantes, 6 classes, 6 pentes, c (19) ; 'commun' ; 'variable' ; sous-ensemble de series deduit de sous."""
    series = [g for g in SERIES if (sous.serie == g).any()]
    D = np.column_stack([(sous.serie == g).to_numpy(float) for g in series])
    z, l = zr.loc[sous.index].to_numpy(), L.loc[sous.index].to_numpy(float)
    if mode == "principal":
        X = np.column_stack([D, D * l[:, None], D * z[:, None], z * l])
    elif mode == "commun":
        X = np.column_stack([D, z])
    elif mode == "variable":
        V = np.column_stack([(sous.variable == v).to_numpy(float) for v in ("HICP", "RGDP", "UNEM")])
        X = np.column_stack([D, D * l[:, None], D * z[:, None], V * (z * l)[:, None]])
    return X, ze.loc[sous.index].to_numpy(), series

def estim(sous, zr, ze, L, lag=8, mode="principal", groupes=None):
    """retourne dict : beta, V, residus, X ; None si < 50 lignes ou X'X singuliere (convention 6.10)"""
    if len(sous) < 50:
        INCIDENTS.append(f"moins de 50 lignes ({len(sous)})"); return None
    X, y, series = matrice(sous, zr, ze, L, mode)
    if np.linalg.matrix_rank(X.T @ X) < X.shape[1]:
        INCIDENTS.append("X'X singuliere"); return None
    beta, u = mco(X, y)
    tours = sous.t_tour.to_numpy()
    V = dk_cov(X, u, tours, lag, groupes=None if groupes is None else sous[groupes].to_numpy())
    return dict(beta=beta, V=V, u=u, X=X, n=len(y), series=series)

def champ_c(sous, zr, ze, L, lag=8, mode="principal", groupes=None):
    r = estim(sous, zr, ze, L, lag, mode, groupes)
    if r is None: return 0.0, 0.0
    return float(r["beta"][-1]), float(np.sqrt(r["V"][-1, -1]))

def grande(d, col, sous_mask):
    """6.2 sur l'ensemble sous_mask, par variable ; retourne la serie L (NaN hors lignes avec la surprise)."""
    L = pd.Series(np.nan, d.index)
    info = {}
    for v in ("HICP", "RGDP", "UNEM"):
        mv = (d.variable == v)
        par_tour = d[mv & sous_mask].groupby("t_tour")[col].first().abs()
        a = par_tour.to_numpy()
        Q = float(np.quantile(a, 2 / 3)); N = len(a)
        ns, nl = int((a > Q).sum()), int((a >= Q).sum())
        stricte = abs(ns / N - 1 / 3) <= abs(nl / N - 1 / 3)
        s = d.loc[mv & d[col].notna(), col].abs()
        L[s.index] = (s > Q).astype(int) if stricte else (s >= Q).astype(int)
        info[v] = dict(Q=Q, N=N, n_strict=ns, n_large=nl, coupure="stricte" if stricte else "large")
    return L, info

def variance_ratio(d, z, L):
    """6.7 : A / a, a = moyenne de (z - m_{g,0})^2 sur toutes les lignes L=0, A idem L=1 (lignes principales)."""
    acc = {0: [], 1: []}
    for g in SERIES:
        for l in (0, 1):
            m = (d.serie == g) & (d.principal == 1) & (L == l)
            zz = z[m].to_numpy()
            acc[l].append((zz - zz.mean()) ** 2)
    a = np.concatenate(acc[0]).mean(); A = np.concatenate(acc[1]).mean()
    return float(A / a), float(a), float(A)

# ------------------------------------------------------------------ calcul
def main():
    # controles de schema (4.4) relances sur le fichier
    spec = importlib.util.spec_from_file_location("construire", ICI / "construire.py")
    C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
    sch = C.controles(CSV)

    d = charge()
    P = d.principal == 1
    p = d[P]
    T = {}  # temoin
    T["n_violations_schema"] = int(sch["n_violations_schema"])
    T["n_anomalies_hors_principal"] = int(sch["n_anomalies_hors_principal"])
    T["n_principal"] = int(len(p))
    T["n_tours"] = int(p.t_tour.nunique())
    T["n_annees_cibles"] = int(p.annee_cible.nunique())
    L = d["grande_nouvelle"].astype(float)  # L du fichier ; recalcule ci-dessous pour verification
    Lcalc, infoL = grande(d, "surprise", P)
    assert (L[d.surprise.notna()] == Lcalc[d.surprise.notna()]).all(), "grande_nouvelle du fichier != recalcul 6.2"
    T["n_grands"] = int((L[P] == 1).sum())
    T["n_tours_grands"] = int(p[L[P] == 1].t_tour.nunique())

    zr, ze, k = reduire(d, "revision", "erreur")
    kmoy = float(np.mean([k[g] for g in SERIES]))
    T["k_moyen"] = kmoy

    # 6.3 / 6.4 / 6.5
    r = estim(p, zr, ze, L, 8)
    beta, V = r["beta"], r["V"]
    c, et = float(beta[-1]), float(np.sqrt(V[-1, -1]))
    T["c"], T["et_c_dk8"], T["t_c"] = c, et, c / et
    T["borne_basse_ic90"], T["borne_haute_ic90"] = c - TCRIT * et, c + TCRIT * et
    bg = beta[12:18]
    bmoy = float(bg.mean())
    w = np.zeros(19); w[12:18] = 1 / 6
    etb = float(np.sqrt(w @ V @ w))
    T["b_moyen"], T["et_b_moyen_dk8"], T["borne_basse_b_moyen_ic90"] = bmoy, etb, bmoy - TCRIT * etb
    T["pente_moyenne_grandes"] = bmoy + c
    # 6.6 pente commune
    rc = estim(p, zr, ze, L, 8, mode="commun")
    bc, etbc = float(rc["beta"][-1]), float(np.sqrt(rc["V"][-1, -1]))
    T["b_commun"], T["et_b_commun_dk8"], T["borne_basse_b_commun_ic90"] = bc, etbc, bc - TCRIT * etbc
    T["controle_positif_ok"] = int(T["borne_basse_b_commun_ic90"] > 0 or T["borne_basse_b_moyen_ic90"] > 0)

    # 6.7
    rv, a, A = variance_ratio(d, zr, L)
    T["rapport_variance_revision"] = rv
    # ecart a apprendre apres le tour precedent : p = erreur + revision
    d["ecart_prec"] = d.erreur + d.revision
    zp = pd.Series(np.nan, d.index)
    for g in SERIES:
        m = d.serie == g
        pm = m & P
        zp[m] = (d.loc[m, "ecart_prec"] - d.loc[pm, "ecart_prec"].mean()) / d.loc[pm, "ecart_prec"].std(ddof=1)
    T["rapport_variance_ecart_prec"] = variance_ratio(d, zp, L)[0]
    biais = (2 * bmoy + kmoy) * 0.10 * (1 / a - 1 / A)
    seuil = max(0.10, biais)
    T["biais_mecanique_nu20"], T["seuil_survie_bas"] = float(biais), float(seuil)
    T["borne_basse_moins_seuil"] = T["borne_basse_ic90"] - seuil
    T["pertinence_manquante"] = int(rv < 1.25 and T["borne_basse_moins_seuil"] <= 0)
    T["marge_indecision"] = float(min(seuil - T["borne_basse_ic90"], T["borne_haute_ic90"] - 0.40))

    # 6.8 episodes
    tt = {}
    for kk in ("E1", "E2", "E3"):
        ck, ek = champ_c(p[p.episode != kk], zr, ze, L, 8)
        T[f"c_sans_{kk}"], T[f"t_sans_{kk}"] = ck, (ck / ek if ek > 0 else 0.0)
    ts = {kk: T[f"t_sans_{kk}"] for kk in ("E1", "E2", "E3")}
    kmin = min(ts, key=lambda x: (ts[x], x))
    T["t_min_sans_episode"] = ts[kmin]
    T["episode_t_min"] = int(kmin[1])
    T["c_min_sans_episode"] = min(T[f"c_sans_{kk}"] for kk in ("E1", "E2", "E3"))
    # 6.9
    T["conflit_robustesse"] = int(T["borne_basse_ic90"] > seuil and T["borne_haute_ic90"] >= 0.40
                                  and T["t_min_sans_episode"] < 1 and T["c_min_sans_episode"] > 0)
    # 6.10
    n = len(p)
    sig2 = float(r["u"] @ r["u"]) / (n - 19)
    et_iid = float(np.sqrt(sig2 * np.linalg.inv(r["X"].T @ r["X"])[-1, -1]))
    T["et_c_iid"] = et_iid
    T["n_effectif"] = float(n * (et_iid / et) ** 2)

    # 6.11 secondaires
    for lag in (4, 12, 0):
        T[f"et_c_dk{lag}"] = champ_c(p, zr, ze, L, lag)[1]
    T["et_c_grappes_annee"] = champ_c(p, zr, ze, L, 0, groupes="annee_cible")[1]
    cc = d[d.complete == 1]
    T["c_avec_pandemie"], T["et_c_avec_pandemie_dk8"] = champ_c(cc, zr, ze, L, 8)
    T["c_avant_2020"], T["et_c_avant_2020_dk8"] = champ_c(p[p.annee_cible <= 2019], zr, ze, L, 8)
    T["c_annee_en_cours"], T["et_c_annee_en_cours_dk8"] = champ_c(p[p.horizon == 0], zr, ze, L, 8)
    T["c_annee_suivante"], T["et_c_annee_suivante_dk8"] = champ_c(p[p.horizon == 1], zr, ze, L, 8)
    zrm, zem, _ = reduire(d, "revision_med", "erreur_med")
    T["c_mediane"], T["et_c_mediane_dk8"] = champ_c(p, zrm, zem, L, 8)
    Lp = (zr.abs() > 1).astype(float)
    T["c_coupure_revision"], T["et_c_coupure_revision_dk8"] = champ_c(p, zr, ze, Lp, 8)
    ps = P & d.surprise_consensus.notna()
    L8, info8 = grande(d, "surprise_consensus", ps)
    p8 = d[ps]
    T["n_surprise_consensus"] = int(len(p8))
    T["c_surprise_consensus"], T["et_c_surprise_consensus_dk8"] = champ_c(p8, zr, ze, L8, 8)
    r1 = estim(p, zr, ze, L, 8, mode="variable")
    for i, v in enumerate(("HICP", "RGDP", "UNEM")):
        T[f"c_{v}"] = float(r1["beta"][18 + i]); T[f"et_c_{v}_dk8"] = float(np.sqrt(r1["V"][18 + i, 18 + i]))

    # fichier : types (entiers pour comptes et indicatrices)
    champs = json.loads(re_bloc())["champs_verification"]
    ENT = {"n_violations_schema", "n_anomalies_hors_principal", "n_principal", "n_tours", "n_annees_cibles", "n_grands",
           "n_tours_grands", "controle_positif_ok", "pertinence_manquante", "episode_t_min", "conflit_robustesse",
           "n_surprise_consensus"}
    out = {}
    for ch in champs:
        x = T[ch]
        out[ch] = int(x) if ch in ENT else float(x)
        assert out[ch] == out[ch], f"NaN dans {ch}"
    (ICI / "temoin.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    detail = dict(infoL=infoL, info8=info8, b_g=dict(zip(SERIES, map(float, bg))), k_g={g: float(k[g]) for g in SERIES},
                  a=a, A=A, incidents=INCIDENTS, schema=sch["detail"])
    (ICI / "analyse_detail.json").write_text(json.dumps(detail, indent=1, ensure_ascii=False))
    figure(p, zr, ze, L, r, bmoy, c)
    print(json.dumps(out, indent=1))
    print("detail", json.dumps(detail, indent=1))

def re_bloc():
    import re
    t = (ICI / "preenregistrement.md").read_text()
    return re.findall(r"```json\s*(\{.*?\})\s*```", t, flags=re.S)[-1]

def figure(p, zr, ze, L, r, bmoy, c):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    beta = r["beta"]
    al, de, bg = beta[:6], beta[6:12], beta[12:18]
    ci = p.serie.map({g: i for i, g in enumerate(SERIES)}).to_numpy()
    l = L.loc[p.index].to_numpy()
    x = zr.loc[p.index].to_numpy()
    # erreur reduite, retranchee de la constante, de l'effet de classe et de l'ecart de pente propre a la serie :
    # il reste (pente moyenne b + c * L) * revision + residu
    y = ze.loc[p.index].to_numpy() - al[ci] - de[ci] * l - (bg[ci] - bmoy) * x
    fig, ax = plt.subplots(figsize=(7, 5), dpi=130)
    for lv, col, lab in ((0, "#8a8f98", "petites nouvelles (L = 0)"), (1, "#d95f02", "grandes nouvelles (L = 1)")):
        m = l == lv
        ax.scatter(x[m], y[m], s=14, alpha=0.55, color=col, label=lab, edgecolor="none")
    xs = np.array([x.min(), x.max()])
    ax.plot(xs, bmoy * xs, color="#4d5560", lw=2, label=f"pente des petites nouvelles = {bmoy:.3f}")
    ax.plot(xs, (bmoy + c) * xs, color="#b34700", lw=2, label=f"pente des grandes nouvelles = {bmoy + c:.3f}")
    ax.axhline(0, color="#cccccc", lw=0.8); ax.axvline(0, color="#cccccc", lw=0.8)
    ax.set_xlabel("révision du consensus (réduite)"); ax.set_ylabel("erreur de prévision (réduite, nette des constantes)")
    ax.set_title(f"K20-ZE : c = pente(grandes) - pente(petites) = {c:+.3f}", fontsize=11)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout(); fig.savefig(ICI / "figure.png"); plt.close(fig)

if __name__ == "__main__":
    main()
