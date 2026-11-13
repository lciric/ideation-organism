"""M01 - analyse (preinscription section 8), a partir de M01_analyse.csv SEULEMENT (+ D1 pour le controle de schema 2/3/5,
via construire.controles). Contient son propre code de rendement (independant de commun.py).
Usage : python3 -I analyse.py   -> temoin.json, figure.png"""
import sys, os, json, math
import numpy as np
import pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
CSV = os.path.join(ICI, "M01_analyse.csv")
Z90 = 1.645


# ------------------------------------------------------------------ second code de rendement (independant)
def coupons(M, d):
    """Dates de coupon strictement posterieures a d (croissantes) et date precedente L (<= d), via pandas DateOffset."""
    M = pd.Timestamp(M)
    d = pd.Timestamp(d)
    k, T = 0, []
    while True:
        t = M - pd.DateOffset(months=6 * k)
        if t <= d:
            L = t
            break
        T.append(t)
        k += 1
    T = T[::-1]
    return T, L


def accrued(c, T, L, d):
    return c / 2 * (pd.Timestamp(d) - L).days / (T[0] - L).days


def yield_newton(prix_pied, c, M, d):
    T, L = coupons(M, d)
    d = pd.Timestamp(d)
    n = len(T)
    w = (T[0] - d).days / (T[0] - L).days
    cible = prix_pied + accrued(c, T, L, d)
    F = np.full(n, c / 2)
    F[-1] += 100.0
    e = np.arange(n) + w
    lo, hi = -50.0, 100.0
    y = 4.0
    for _ in range(200):                      # Newton, avec repli par bissection
        q = 1 + y / 200
        f = np.sum(F * q ** -e) - cible
        fp = np.sum(-F * e * q ** (-e - 1)) / 200
        if f > 0:
            lo = y
        else:
            hi = y
        yn = y - f / fp
        if not (lo < yn < hi):
            yn = 0.5 * (lo + hi)
        if abs(yn - y) < 1e-13:
            y = yn
            break
        y = yn
    return y


def gsw_price(c, M, x, p):
    b0, b1, b2, b3, t1, t2 = p
    T, L = coupons(M, x)
    x = pd.Timestamp(x)
    m = np.array([(t - x).days for t in T]) / 365.25
    u1, u2 = m / t1, m / t2
    z = (b0 + b1 * (1 - np.exp(-u1)) / u1 + b2 * ((1 - np.exp(-u1)) / u1 - np.exp(-u1))
         + b3 * ((1 - np.exp(-u2)) / u2 - np.exp(-u2)))
    F = np.full(len(T), c / 2)
    F[-1] += 100.0
    return float(np.sum(F * np.exp(-z * m / 100)))


def gsw_yield(c, M, x, p):
    T, L = coupons(M, x)
    return yield_newton(gsw_price(c, M, x, p) - accrued(c, T, L, x), c, M, x)


def recalcul_rendements(P):
    """Renvoie ecart_max_rdt_pb (100 x plus grand ecart absolu sur les six colonnes 43-48) et les rendements recalcules."""
    pmax = 0.0
    rec = {}
    for idx, r in P.iterrows():
        c, M = float(r.taux_coupon_pct), r.date_echeance
        for x in ("jm5", "j", "jp5"):
            d = r[f"date_{x}"] if x != "j" else r.date_adjudication
            fi = yield_newton(float(r[f"prix_fi_{x}"]), c, M, d)
            g = gsw_yield(c, M, d, [float(r[f"{b}_{x}"]) for b in ("beta0", "beta1", "beta2", "beta3", "tau1", "tau2")])
            pmax = max(pmax, abs(fi - float(r[f"rdt_fi_{x}_pct"])), abs(g - float(r[f"rdt_gsw_{x}_pct"])))
            rec[(idx, x)] = (fi, g)
    return 100 * pmax, rec


# ------------------------------------------------------------------ statistiques (section 8)
def moy(x):
    return float(np.mean(x))


def et_groupee(x, mois):
    x = np.asarray(x, float)
    N = len(x)
    xb = x.mean()
    s = pd.Series(x - xb).groupby(np.asarray(mois)).sum()
    G = len(s)
    if G < 2:
        return float("nan")
    return float(math.sqrt(G / (G - 1) * float((s ** 2).sum())) / N)


def diff(df_b, df_a, col):
    """(estimation B - A, ET) pour la colonne col (Series ou callable)."""
    f = (lambda d: d[col]) if isinstance(col, str) else col
    xa, xb = f(df_a), f(df_b)
    return moy(xb) - moy(xa), math.sqrt(et_groupee(xa, df_a.mois) ** 2 + et_groupee(xb, df_b.mois) ** 2)


def marge(A, B):
    """m = D + 0,5 x baisse de V_cmt, sur les lignes A, B fournies."""
    D = moy(B.ecart_pb) - moy(A.ecart_pb)
    baisse_cmt = moy(A.v_cmt_pb) - moy(B.v_cmt_pb)
    return D + 0.5 * baisse_cmt


def jn(x):
    """float -> valeur JSON (None si non fini)."""
    if isinstance(x, (np.integer,)):
        return int(x)
    x = float(x)
    return x if math.isfinite(x) else None


def nettoyer(o):
    """remplace les nombres non finis par None (JSON valide), les types numpy par des types python."""
    if isinstance(o, dict):
        return {k: nettoyer(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [nettoyer(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return float(o) if math.isfinite(o) else None
    return o


def main():
    df = pd.read_csv(CSV, dtype=str, keep_default_na=False)
    num = [c for c in df.columns if c not in ("id_ligne", "cusip", "terme_api", "date_adjudication", "mois", "periode",
                                              "date_emission_origine", "date_echeance", "date_jm5", "date_jp5",
                                              "motif_exclusion")]
    for c in num:
        df[c] = pd.to_numeric(df[c].replace("", np.nan))
    P = df[df.motif_exclusion == ""].copy()
    A, B = P[P.periode == "avant"], P[P.periode == "apres"]
    T = {}

    # schema (section 7) sur le fichier ecrit
    import construire as C
    res = C.controles(CSV)
    T["schema_ok"] = C.schema_ok(res)

    # recalcul independant des rendements (second code)
    T["ecart_max_rdt_pb"], _ = recalcul_rendements(P)

    T["n_avant"], T["n_apres"] = len(A), len(B)
    T["n_grappes_avant"], T["n_grappes_apres"] = A.mois.nunique(), B.mois.nunique()
    T["v_own_avant_pb"] = moy(A.v_own_pb)
    T["et_v_own_avant_pb"] = et_groupee(A.v_own_pb, A.mois)
    T["borne_inf_90_v_own_avant_pb"] = T["v_own_avant_pb"] - Z90 * T["et_v_own_avant_pb"]
    T["controle_positif_ok"] = int(T["borne_inf_90_v_own_avant_pb"] > 0)
    T["v_cmt_avant_pb"], T["v_cmt_apres_pb"] = moy(A.v_cmt_pb), moy(B.v_cmt_pb)
    T["baisse_cmt_pb"] = T["v_cmt_avant_pb"] - T["v_cmt_apres_pb"]
    T["et_baisse_cmt_pb"] = math.sqrt(et_groupee(A.v_cmt_pb, A.mois) ** 2 + et_groupee(B.v_cmt_pb, B.mois) ** 2)
    T["borne_inf_90_baisse_cmt_pb"] = T["baisse_cmt_pb"] - Z90 * T["et_baisse_cmt_pb"]
    T["controle_cassure_ok"] = int(T["borne_inf_90_baisse_cmt_pb"] > 0)
    T["v_own_apres_pb"] = moy(B.v_own_pb)
    T["et_v_own_apres_pb"] = et_groupee(B.v_own_pb, B.mois)
    T["borne_inf_90_v_own_apres_pb"] = T["v_own_apres_pb"] - Z90 * T["et_v_own_apres_pb"]
    T["baisse_own_pb"] = T["v_own_avant_pb"] - T["v_own_apres_pb"]
    T["et_baisse_own_pb"] = math.sqrt(et_groupee(A.v_own_pb, A.mois) ** 2 + et_groupee(B.v_own_pb, B.mois) ** 2)
    T["borne_inf_90_baisse_own_pb"] = T["baisse_own_pb"] - Z90 * T["et_baisse_own_pb"]
    T["d_pb"], T["et_d_pb"] = diff(B, A, "ecart_pb")
    T["borne_inf_90_d_pb"] = T["d_pb"] - Z90 * T["et_d_pb"]
    T["borne_sup_90_d_pb"] = T["d_pb"] + Z90 * T["et_d_pb"]
    T["marge_moitie_pb"] = T["d_pb"] + 0.5 * T["baisse_cmt_pb"]
    h = lambda d: 0.5 * d.v_cmt_pb - d.v_own_pb
    _, T["et_marge_moitie_pb"] = diff(B, A, h)
    T["marge_moitie_sans_2023_pb"] = marge(A[A.annee != 2023], B[B.annee != 2023])
    T["marge_moitie_sans_30_pb"] = marge(A[A.echeance != 30], B[B.echeance != 30])
    S = (T["borne_inf_90_v_own_apres_pb"] > 0 and T["marge_moitie_pb"] <= 0 and T["marge_moitie_sans_2023_pb"] <= 0
         and T["marge_moitie_sans_30_pb"] <= 0)
    E = (T["borne_inf_90_baisse_own_pb"] > 0 and T["marge_moitie_pb"] > 0 and T["marge_moitie_sans_2023_pb"] > 0
         and T["marge_moitie_sans_30_pb"] > 0)
    T["indecis"] = 0 if (S or E) else 1

    # controle arithmetique
    arith = abs(T["d_pb"] - (T["baisse_own_pb"] - T["baisse_cmt_pb"]))
    assert arith < 1e-9, arith
    ent = {"n_avant", "n_apres", "n_grappes_avant", "n_grappes_apres", "schema_ok", "controle_positif_ok",
           "controle_cassure_ok", "indecis"}
    out = {k: (int(v) if k in ent else jn(v)) for k, v in T.items()}

    # ---------------- descriptif S1-S4 (sans effet sur le verdict)
    desc = {"controle_arithmetique_d_moins_baisses": arith, "profil_S_tient": int(S), "profil_E_tient": int(E)}
    def blocs(a, b):
        return {"v_own": {"avant": [moy(a.v_own_pb), et_groupee(a.v_own_pb, a.mois)], "apres": [moy(b.v_own_pb), et_groupee(b.v_own_pb, b.mois)]},
                "v_cmt": {"avant": [moy(a.v_cmt_pb), et_groupee(a.v_cmt_pb, a.mois)], "apres": [moy(b.v_cmt_pb), et_groupee(b.v_cmt_pb, b.mois)]}}
    s1 = {}
    for e in (10, 20, 30):
        a, b = A[A.echeance == e], B[B.echeance == e]
        d_ = {"n_avant": len(a), "n_apres": len(b), "n_grappes_avant": int(a.mois.nunique()), "n_grappes_apres": int(b.mois.nunique())}
        d_.update(blocs(a, b))
        d_["D"] = [moy(b.ecart_pb) - moy(a.ecart_pb), math.sqrt(et_groupee(a.ecart_pb, a.mois) ** 2 + et_groupee(b.ecart_pb, b.mois) ** 2)]
        d_["m"] = marge(a, b)
        s1[str(e)] = d_
    desc["S1_par_echeance"] = s1
    s2 = {}
    for nom, (cj, cm, cp) in {"own": ("e_own_j_pb", "e_own_jm5_pb", "e_own_jp5_pb"), "cmt": ("e_cmt_j_pb", "e_cmt_jm5_pb", "e_cmt_jp5_pb")}.items():
        for jam, (c1, c2) in {"montee": (cj, cm), "redescente": (cj, cp)}.items():
            f = lambda d, c1=c1, c2=c2: d[c1] - d[c2]
            xa, xb = f(A), f(B)
            s2[f"{jam}_{nom}"] = {"avant": [moy(xa), et_groupee(xa, A.mois)], "apres": [moy(xb), et_groupee(xb, B.mois)],
                                  "baisse": diff(B, A, f)[0] * -1, "et_baisse": diff(B, A, f)[1]}
    desc["S2_jambes"] = s2
    s3 = {}
    for an, g in P.groupby("annee"):
        s3[str(int(an))] = {"n": len(g), "n_mois": int(g.mois.nunique()), "v_own": [moy(g.v_own_pb), et_groupee(g.v_own_pb, g.mois)],
                            "v_cmt": [moy(g.v_cmt_pb), et_groupee(g.v_cmt_pb, g.mois)]}
    desc["S3_par_annee"] = s3
    sans = P[(P.annee != 2023) & (P.echeance != 30)]
    desc["S3_marge_moitie_sans_2023_et_sans_30_pb"] = marge(sans[sans.periode == "avant"], sans[sans.periode == "apres"])
    y23 = P[P.annee == 2023]
    s4 = {"ecart_type_n_moins_1": {
        "v_own_avant": float(A.v_own_pb.std(ddof=1)), "v_own_apres": float(B.v_own_pb.std(ddof=1)), "v_own_2023": float(y23.v_own_pb.std(ddof=1)),
        "v_cmt_avant": float(A.v_cmt_pb.std(ddof=1)), "v_cmt_apres": float(B.v_cmt_pb.std(ddof=1)), "v_cmt_2023": float(y23.v_cmt_pb.std(ddof=1))},
        "correlation_v_own_v_cmt": {"avant": float(np.corrcoef(A.v_own_pb, A.v_cmt_pb)[0, 1]), "apres": float(np.corrcoef(B.v_own_pb, B.v_cmt_pb)[0, 1])},
        "lignes_exclues_par_motif": {str(k): int(v) for k, v in df[df.motif_exclusion != ""].motif_exclusion.value_counts().items()},
        "n_lignes_fichier": len(df), "n_lignes_P": len(P)}
    pr = P[["prix_fi_jm5", "prix_fi_j", "prix_fi_jp5"]]
    ident = ((pr.prix_fi_jm5 == pr.prix_fi_j) | (pr.prix_fi_j == pr.prix_fi_jp5) | (pr.prix_fi_jm5 == pr.prix_fi_jp5))
    s4["n_lignes_P_prix_identique_a_deux_dates"] = int(ident.sum())
    s4["n_lignes_P_prix_identique_aux_trois_dates"] = int(((pr.prix_fi_jm5 == pr.prix_fi_j) & (pr.prix_fi_j == pr.prix_fi_jp5)).sum())
    desc["S4_hypotheses_et_comptes"] = s4
    desc["controles_schema"] = {str(n): [bool(res[n][0]), res[n][1]] for n in range(1, 10)}
    out["descriptif"] = nettoyer(desc)
    with open(os.path.join(ICI, "temoin.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    for k, v in out.items():
        if k != "descriptif":
            print(f"{k} = {v}")
    figure(A, B, T)


def figure(A, B, T):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=150)
    vals = [("V_cmt (courbe du Tresor)", "#4C72B0", A.v_cmt_pb, B.v_cmt_pb), ("V_own (prix du titre)", "#C44E52", A.v_own_pb, B.v_own_pb)]
    for k, (nom, col, a, b) in enumerate(vals):
        for p, (s, pos) in enumerate(((a, A), (b, B))):
            m, e = moy(s), et_groupee(s, pos.mois)
            ax.bar(p * 3 + k, m, 0.9, yerr=Z90 * e, color=col, capsize=4, label=nom if p == 0 else None)
            ax.text(p * 3 + k, m + Z90 * e + 0.05, f"{m:.2f}", ha="center", fontsize=8)
    ax.set_xticks([0.5, 3.5])
    ax.set_xticklabels([f"2010-2021 (n={T['n_avant']})", f"2022-2026 (n={T['n_apres']})"])
    ax.axhline(0, color="k", lw=0.6)
    ax.set_ylabel("V moyen, pb (barres : IC a 90 %)")
    ax.set_title(f"M01 : D = {T['d_pb']:.2f} pb ; m = {T['marge_moitie_pb']:.2f} pb", fontsize=10)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(ICI, "figure.png"))


if __name__ == "__main__":
    main()
