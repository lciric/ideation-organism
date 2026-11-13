"""M01 -- code du verificateur, ecrit a partir de la seule preinscription scellee (sections 4, 6, 7, 8).
Entrees : M01_analyse.csv ; D1 (Fiscal Data, une requete, chemin passe en argument ou telecharge).
Sortie : verification.json.  Usage : python3 verification.py [chemin_d1.json]
"""
import json, sys, math, datetime as dt, pathlib, subprocess, hashlib, calendar
import numpy as np, pandas as pd
from scipy.optimize import brentq

ICI = pathlib.Path(__file__).resolve().parent
URL_D1 = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query?"
          "fields=cusip,auction_date,issue_date,maturity_date,security_type,security_term,original_security_term,"
          "reopening,inflation_index_security,floating_rate,closing_time_comp,int_rate&filter=security_type:in:"
          "(Note,Bond),auction_date:lte:2026-10-31&sort=auction_date&page%5Bsize%5D=10000")
D = dt.date.fromisoformat

# ---------------------------------------------------------------- calendrier C (4.3), reconstruit a partir du texte
def nieme_jour(an, mois, jour_semaine, n):
    """n-ieme jour_semaine (0 = lundi) du mois ; n = -1 : le dernier."""
    if n > 0:
        d = dt.date(an, mois, 1)
        d += dt.timedelta((jour_semaine - d.weekday()) % 7)
        return d + dt.timedelta(7 * (n - 1))
    d = dt.date(an, mois, calendar.monthrange(an, mois)[1])
    return d - dt.timedelta((d.weekday() - jour_semaine) % 7)

def observe(d):
    if d.weekday() == 5:
        return d - dt.timedelta(1)
    if d.weekday() == 6:
        return d + dt.timedelta(1)
    return d

def feries():
    f = set()
    for an in range(2009, 2028):
        fixes = [dt.date(an, 1, 1), dt.date(an, 7, 4), dt.date(an, 11, 11), dt.date(an, 12, 25)]
        if an >= 2021:
            fixes.append(dt.date(an, 6, 19))
        f |= {observe(x) for x in fixes}
        f |= {nieme_jour(an, 1, 0, 3), nieme_jour(an, 2, 0, 3), nieme_jour(an, 5, 0, -1), nieme_jour(an, 9, 0, 1),
              nieme_jour(an, 10, 0, 2), nieme_jour(an, 11, 3, 4)}
    return f

def calendrier_C():
    fer = feries() | {dt.date(2012, 10, 30), dt.date(2018, 12, 5)}
    d, fin, C = dt.date(2009, 6, 1), dt.date(2026, 12, 31), []
    while d <= fin:
        if d.weekday() < 5 and d not in fer:
            C.append(d)
        d += dt.timedelta(1)
    return C

# ---------------------------------------------------------------- conventions 6.2
def recule_mois(M, k):
    m = M.month - k
    an = M.year + (m - 1) // 12
    m = (m - 1) % 12 + 1
    return dt.date(an, m, min(M.day, calendar.monthrange(an, m)[1]))

def coupons(M, d):
    """T_k > d (croissants), L(d), N(d)."""
    apres, k = [], 0
    while True:
        T = recule_mois(M, 6 * k)
        if T > d:
            apres.append(T); k += 1
        else:
            L = T; break
    apres.reverse()
    return apres, L, apres[0]

def coupon_couru(c, M, d):
    _, L, N = coupons(M, d)
    return (c / 2) * (d - L).days / (N - L).days

def rendement(P, c, M, d):
    Ts, L, N = coupons(M, d)
    n = len(Ts)
    w = (N - d).days / (N - L).days
    F = np.full(n, c / 2); F[-1] += 100.0
    expo = np.arange(n) + w
    cible = P + coupon_couru(c, M, d)
    f = lambda y: float(np.sum(F * (1 + y / 200.0) ** (-expo))) - cible
    return brentq(f, -50.0, 100.0, xtol=1e-12, rtol=1e-15, maxiter=500)

def z_gsw(m, b0, b1, b2, b3, t1, t2):
    a1, a2 = m / t1, m / t2
    e1, e2 = np.exp(-a1), np.exp(-a2)
    return b0 + b1 * (1 - e1) / a1 + b2 * ((1 - e1) / a1 - e1) + b3 * ((1 - e2) / a2 - e2)

def rendement_gsw(par, c, M, x):
    Ts, _, _ = coupons(M, x)
    F = np.full(len(Ts), c / 2); F[-1] += 100.0
    m = np.array([(T - x).days for T in Ts]) / 365.25
    plein = float(np.sum(F * np.exp(-z_gsw(m, *par) * m / 100.0)))
    return rendement(plein - coupon_couru(c, M, x), c, M, x)

# ---------------------------------------------------------------- statistiques (section 8)
def et_groupee(x, mois):
    x = np.asarray(x, float); mois = np.asarray(mois)
    N = len(x); G = len(set(mois))
    if G < 2:
        return float("nan")
    r = x - x.mean()
    s = pd.Series(r).groupby(mois).sum().values
    return float(math.sqrt(G / (G - 1) * np.sum(s ** 2)) / N)

def moy_et(df, col):
    return float(df[col].mean()), et_groupee(df[col].values, df["mois"].values)

def marge(A, B):
    d = B["ecart"].mean() - A["ecart"].mean()
    baisse = A["v_cmt"].mean() - B["v_cmt"].mean()
    return float(d + 0.5 * baisse)

def propre(v):
    if isinstance(v, dict):
        return {k: propre(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [propre(x) for x in v]
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        v = float(v)
        return None if v != v else v
    return v

# ---------------------------------------------------------------- programme
def main():
    if len(sys.argv) > 1:
        brut = pathlib.Path(sys.argv[1]).read_bytes()
    else:
        brut = subprocess.run(["curl", "-sS", URL_D1], capture_output=True, check=True).stdout
    d1 = pd.DataFrame(json.loads(brut)["data"])
    sha_d1 = hashlib.sha256(brut).hexdigest()

    chemin = ICI / "M01_analyse.csv"
    octets = chemin.read_bytes()
    t = pd.read_csv(chemin, dtype=str, keep_default_na=False)
    schema = {}

    # --- contrôle 1 : colonnes
    attendues = ("id_ligne cusip terme_api echeance date_adjudication mois annee periode date_emission_origine "
                 "date_echeance taux_coupon_pct date_jm5 date_jp5 motif_exclusion prix_fi_jm5 prix_fi_j prix_fi_jp5 "
                 "identite_fi_ok").split()
    for x in ["jm5", "j", "jp5"]:
        attendues += [f"{p}_{x}" for p in ["beta0", "beta1", "beta2", "beta3", "tau1", "tau2"]]
    attendues += ["cmt_jm5", "cmt_j", "cmt_jp5", "gswpar_jm5", "gswpar_j", "gswpar_jp5",
                  "rdt_fi_jm5_pct", "rdt_fi_j_pct", "rdt_fi_jp5_pct", "rdt_gsw_jm5_pct", "rdt_gsw_j_pct",
                  "rdt_gsw_jp5_pct", "e_own_jm5_pb", "e_own_j_pb", "e_own_jp5_pb", "e_cmt_jm5_pb", "e_cmt_j_pb",
                  "e_cmt_jp5_pb", "v_own_pb", "v_cmt_pb", "ecart_pb", "complet", "dans_p"]
    schema["c1_colonnes"] = int(len(attendues) == 59 and list(t.columns) == attendues)
    schema["c1_info_bom_absent"] = int(not octets.startswith(b"\xef\xbb\xbf"))

    # --- contrôle 2 : population reconstruite depuis D1
    nom = d1[(d1.inflation_index_security != "Yes") & (d1.floating_rate != "Yes")]
    pop = nom[(nom.reopening == "Yes") & (nom.auction_date >= "2010-01-01") & (nom.auction_date <= "2026-10-31")
              & nom.security_term.str.match(r"^(9|19|29)-Year")]
    ids_pop = set(pop.cusip + "_" + pop.auction_date)
    ids = list(t.id_ligne)
    schema["c2_unicite"] = int(len(ids) == len(set(ids)))
    schema["c2_population"] = int(set(ids) == ids_pop)
    n_pop = len(pop)
    pop_comptes = {f"{e}_{p}": int(((pop.security_term.str.startswith(pfx)) &
                                    ((pop.auction_date <= "2021-12-31") == (p == "avant"))).sum())
                   for e, pfx in [(10, "9-Year"), (20, "19-Year"), (30, "29-Year")] for p in ["avant", "apres"]}
    # tri (6) : par date_adjudication puis echeance -- information, hors contrôle 1/2 au sens strict
    tri_ok = int(list(zip(t.date_adjudication, t.echeance.astype(int))) ==
                 sorted(zip(t.date_adjudication, t.echeance.astype(int))))

    # --- P
    P = t[t.motif_exclusion == ""].copy()
    schema["info_dans_p_coherent"] = int(((t.motif_exclusion == "") == (t.dans_p == "1")).all())
    Pd = t[t.dans_p == "1"].copy()
    assert P.id_ligne.tolist() == Pd.id_ligne.tolist()

    # --- contrôle 3
    premiere = nom[nom.reopening == "No"].groupby("cusip")
    nb_prem = premiere.size()
    pref = {"9-Year": 10, "19-Year": 20, "29-Year": 30}
    def ech(term):
        for k, v in pref.items():
            if term.startswith(k):
                return v
    ok3 = []
    for _, r in P.iterrows():
        ok = r.id_ligne == f"{r.cusip}_{r.date_adjudication}" and len(r.cusip) == 9
        ok &= int(r.echeance) == ech(r.terme_api)
        ok &= r.mois == r.date_adjudication[:7] and int(r.annee) == int(r.date_adjudication[:4])
        ok &= r.periode == ("avant" if r.date_adjudication <= "2021-12-31" else "apres")
        ok &= nb_prem.get(r.cusip, 0) == 1
        if nb_prem.get(r.cusip, 0) == 1:
            p1 = premiere.get_group(r.cusip).iloc[0]
            ok &= abs(float(r.taux_coupon_pct) - float(p1.int_rate)) < 1e-12
            ok &= r.date_echeance == p1.maturity_date and r.date_emission_origine == p1.issue_date
        ok &= r.complet == "1"
        ok &= r.identite_fi_ok in ("0", "1") and r.complet in ("0", "1") and r.dans_p in ("0", "1")
        ok3.append(bool(ok))
    schema["c3_identite_metadonnees"] = int(all(ok3))

    # --- contrôle 4 : calendrier au rang
    C = calendrier_C(); rang = {d: i for i, d in enumerate(C)}
    ok4 = []
    for _, r in P.iterrows():
        J = D(r.date_adjudication)
        ok4.append(J in rang and D(r.date_jm5) == C[rang[J] - 5] and D(r.date_jp5) == C[rang[J] + 5])
    schema["c4_calendrier"] = int(all(ok4))
    J_dans_C_324 = int(all(D(x) in rang for x in t.date_adjudication))

    # --- contrôle 5 : pas d'autre adjudication du même CUSIP à <= 10 rangs ; émission <= J-5
    import bisect
    def rg(d):  # rang d'une date ; une date hors de C prend le rang du premier jour de C qui la suit
        return rang[d] if d in rang else bisect.bisect_left(C, d)
    toutes = d1[d1.cusip.isin(set(P.cusip))]
    ok5 = []
    for _, r in P.iterrows():
        J = D(r.date_adjudication)
        autres = toutes[(toutes.cusip == r.cusip) & (toutes.auction_date != r.date_adjudication)]
        proche = any(abs(rg(D(a)) - rang[J]) <= 10 for a in autres.auction_date)
        ok5.append((not proche) and r.date_emission_origine <= r.date_jm5)
    schema["c5_fenetres_emission"] = int(all(ok5))
    # motifs de la population entiere (information S4 / 4.5), recalcules de facon indépendante
    motifs_recalc = {}
    for _, r in t.iterrows():
        J = D(r.date_adjudication)
        autres = d1[(d1.cusip == r.cusip) & (d1.auction_date != r.date_adjudication)]
        if any(abs(rg(D(a)) - rang[J]) <= 10 for a in autres.auction_date):
            motifs_recalc[r.id_ligne] = "fenetre_chevauchee"
        else:
            p1 = premiere.get_group(r.cusip).iloc[0]
            if p1.issue_date > C[rang[J] - 5].isoformat():
                motifs_recalc[r.id_ligne] = "titre_non_emis_a_jm5"
    motifs_fichier = {r.id_ligne: r.motif_exclusion for _, r in t.iterrows() if r.motif_exclusion}

    # --- contrôle 6
    schema["c6_identite_fi"] = int((P.identite_fi_ok == "1").all())

    # --- contrôle 9 (seconde partie d'abord : colonnes 15-42 remplies)
    c15_42 = attendues[14:42]
    schema["c9_entrees_remplies"] = int((P[c15_42] != "").all().all())
    num = P.copy()
    for c in attendues[14:57]:
        num[c] = pd.to_numeric(num[c], errors="coerce")
    X = ["jm5", "j", "jp5"]

    # --- contrôle 7 : plages
    ok7 = True
    for x in X:
        ok7 &= num[f"prix_fi_{x}"].between(30, 200).all()
        ok7 &= (num[f"tau1_{x}"] > 0).all() and (num[f"tau2_{x}"] > 0).all()
        for c in [f"cmt_{x}", f"gswpar_{x}", f"rdt_fi_{x}_pct", f"rdt_gsw_{x}_pct"]:
            ok7 &= num[c].between(-1, 20).all()
    ok7 &= pd.to_numeric(P.taux_coupon_pct).between(0, 15).all()
    schema["c7_plages"] = int(bool(ok7))

    # --- contrôle 8 : garde d'appariement
    ok8 = True
    for x in X:
        ok8 &= ((num[f"rdt_fi_{x}_pct"] - num[f"rdt_gsw_{x}_pct"]).abs() <= 0.60).all()
        ok8 &= ((num[f"cmt_{x}"] - num[f"gswpar_{x}"]).abs() <= 1).all()
    schema["c8_garde"] = int(bool(ok8))

    # --- contrôle 9 : colonnes 49-57 = formule sur les colonnes du fichier, a 1e-6 pb
    err = []
    for x in X:
        err.append((num[f"e_own_{x}_pb"] - 100 * (num[f"rdt_fi_{x}_pct"] - num[f"rdt_gsw_{x}_pct"])).abs())
        err.append((num[f"e_cmt_{x}_pb"] - 100 * (num[f"cmt_{x}"] - num[f"gswpar_{x}"])).abs())
    err.append((num.v_own_pb - (2 * num.e_own_j_pb - num.e_own_jm5_pb - num.e_own_jp5_pb)).abs())
    err.append((num.v_cmt_pb - (2 * num.e_cmt_j_pb - num.e_cmt_jm5_pb - num.e_cmt_jp5_pb)).abs())
    err.append((num.ecart_pb - (num.v_cmt_pb - num.v_own_pb)).abs())
    err_max_c9 = float(max(e.max() for e in err))
    schema["c9_formules"] = int(err_max_c9 <= 1e-6 and not any(e.isna().any() for e in err))

    regles = ["c1_colonnes", "c2_unicite", "c2_population", "c3_identite_metadonnees", "c4_calendrier",
              "c5_fenetres_emission", "c6_identite_fi", "c7_plages", "c8_garde", "c9_entrees_remplies", "c9_formules"]
    schema_ok = int(all(schema[k] == 1 for k in regles))

    # --- recalcul des six rendements (6.2)
    ecart_rdt = 0.0
    lignes = []
    for _, r in num.iterrows():
        c, M = float(P.loc[r.name, "taux_coupon_pct"]), D(P.loc[r.name, "date_echeance"])
        dates = {"jm5": D(P.loc[r.name, "date_jm5"]), "j": D(P.loc[r.name, "date_adjudication"]),
                 "jp5": D(P.loc[r.name, "date_jp5"])}
        out = {}
        for x in X:
            f = rendement(r[f"prix_fi_{x}"], c, M, dates[x])
            par = [r[f"{p}_{x}"] for p in ["beta0", "beta1", "beta2", "beta3", "tau1", "tau2"]]
            g = rendement_gsw(par, c, M, dates[x])
            ecart_rdt = max(ecart_rdt, abs(f - r[f"rdt_fi_{x}_pct"]), abs(g - r[f"rdt_gsw_{x}_pct"]))
            out[f"f_{x}"], out[f"g_{x}"] = f, g
            out[f"eo_{x}"] = 100 * (f - g)
            out[f"ec_{x}"] = 100 * (r[f"cmt_{x}"] - r[f"gswpar_{x}"])
        out["v_own"] = 2 * out["eo_j"] - out["eo_jm5"] - out["eo_jp5"]
        out["v_cmt"] = 2 * out["ec_j"] - out["ec_jm5"] - out["ec_jp5"]
        out["ecart"] = out["v_cmt"] - out["v_own"]
        out["h"] = 0.5 * out["v_cmt"] - out["v_own"]
        out["monte_own"] = out["eo_j"] - out["eo_jm5"]; out["redesc_own"] = out["eo_j"] - out["eo_jp5"]
        out["monte_cmt"] = out["ec_j"] - out["ec_jm5"]; out["redesc_cmt"] = out["ec_j"] - out["ec_jp5"]
        out.update(id_ligne=P.loc[r.name, "id_ligne"], mois=P.loc[r.name, "mois"], annee=int(P.loc[r.name, "annee"]),
                   periode=P.loc[r.name, "periode"], echeance=int(P.loc[r.name, "echeance"]),
                   prix_identiques=int(len({r.prix_fi_jm5, r.prix_fi_j, r.prix_fi_jp5}) < 3))
        lignes.append(out)
    V = pd.DataFrame(lignes)
    ecart_max_rdt_pb = 100 * ecart_rdt

    A, B = V[V.periode == "avant"], V[V.periode == "apres"]
    v = {}
    v["schema_ok"] = schema_ok
    v["n_avant"], v["n_apres"] = len(A), len(B)
    v["n_grappes_avant"], v["n_grappes_apres"] = A.mois.nunique(), B.mois.nunique()
    v["ecart_max_rdt_pb"] = ecart_max_rdt_pb
    v["v_own_avant_pb"], v["et_v_own_avant_pb"] = moy_et(A, "v_own")
    v["borne_inf_90_v_own_avant_pb"] = v["v_own_avant_pb"] - 1.645 * v["et_v_own_avant_pb"]
    v["controle_positif_ok"] = int(v["borne_inf_90_v_own_avant_pb"] > 0)
    v["v_cmt_avant_pb"], eta_c = moy_et(A, "v_cmt")
    v["v_cmt_apres_pb"], etb_c = moy_et(B, "v_cmt")
    v["baisse_cmt_pb"] = v["v_cmt_avant_pb"] - v["v_cmt_apres_pb"]
    v["et_baisse_cmt_pb"] = math.hypot(eta_c, etb_c)
    v["borne_inf_90_baisse_cmt_pb"] = v["baisse_cmt_pb"] - 1.645 * v["et_baisse_cmt_pb"]
    v["controle_cassure_ok"] = int(v["borne_inf_90_baisse_cmt_pb"] > 0)
    v["v_own_apres_pb"], v["et_v_own_apres_pb"] = moy_et(B, "v_own")
    v["borne_inf_90_v_own_apres_pb"] = v["v_own_apres_pb"] - 1.645 * v["et_v_own_apres_pb"]
    v["baisse_own_pb"] = v["v_own_avant_pb"] - v["v_own_apres_pb"]
    v["et_baisse_own_pb"] = math.hypot(v["et_v_own_avant_pb"], v["et_v_own_apres_pb"])
    v["borne_inf_90_baisse_own_pb"] = v["baisse_own_pb"] - 1.645 * v["et_baisse_own_pb"]
    v["d_pb"] = float(B.ecart.mean() - A.ecart.mean())
    v["et_d_pb"] = math.hypot(et_groupee(A.ecart, A.mois), et_groupee(B.ecart, B.mois))
    v["borne_inf_90_d_pb"] = v["d_pb"] - 1.645 * v["et_d_pb"]
    v["borne_sup_90_d_pb"] = v["d_pb"] + 1.645 * v["et_d_pb"]
    v["marge_moitie_pb"] = v["d_pb"] + 0.5 * v["baisse_cmt_pb"]
    v["et_marge_moitie_pb"] = math.hypot(et_groupee(A.h, A.mois), et_groupee(B.h, B.mois))
    v["marge_moitie_sans_2023_pb"] = marge(A[A.annee != 2023], B[B.annee != 2023])
    v["marge_moitie_sans_30_pb"] = marge(A[A.echeance != 30], B[B.echeance != 30])
    S = (v["borne_inf_90_v_own_apres_pb"] > 0 and v["marge_moitie_pb"] <= 0 and v["marge_moitie_sans_2023_pb"] <= 0
         and v["marge_moitie_sans_30_pb"] <= 0)
    E = (v["borne_inf_90_baisse_own_pb"] > 0 and v["marge_moitie_pb"] > 0 and v["marge_moitie_sans_2023_pb"] > 0
         and v["marge_moitie_sans_30_pb"] > 0)
    v["indecis"] = int(not (S or E))

    # --- descriptif S1-S4
    def bloc(df):
        Ad, Bd = df[df.periode == "avant"], df[df.periode == "apres"]
        o = {"n_avant": len(Ad), "n_apres": len(Bd), "mois_avant": Ad.mois.nunique(), "mois_apres": Bd.mois.nunique()}
        for col in ["v_own", "v_cmt"]:
            for nomp, sub in [("avant", Ad), ("apres", Bd)]:
                o[f"{col}_{nomp}_pb"], o[f"et_{col}_{nomp}_pb"] = moy_et(sub, col)
        if len(Ad) and len(Bd):
            o["d_pb"] = float(Bd.ecart.mean() - Ad.ecart.mean())
            o["et_d_pb"] = math.hypot(et_groupee(Ad.ecart, Ad.mois), et_groupee(Bd.ecart, Bd.mois))
            o["marge_moitie_pb"] = marge(Ad, Bd)
            o["et_marge_moitie_pb"] = math.hypot(et_groupee(Ad.h, Ad.mois), et_groupee(Bd.h, Bd.mois))
        return o
    S1 = {str(e): bloc(V[V.echeance == e]) for e in [10, 20, 30]}
    S2 = {}
    for col in ["monte_own", "redesc_own", "monte_cmt", "redesc_cmt"]:
        for nomp, sub in [("avant", A), ("apres", B)]:
            S2[f"{col}_{nomp}_pb"], S2[f"et_{col}_{nomp}_pb"] = moy_et(sub, col)
        S2[f"baisse_{col}_pb"] = S2[f"{col}_avant_pb"] - S2[f"{col}_apres_pb"]
        S2[f"et_baisse_{col}_pb"] = math.hypot(S2[f"et_{col}_avant_pb"], S2[f"et_{col}_apres_pb"])
    S3 = {"par_annee": {}}
    for an, sub in V.groupby("annee"):
        o = {"n": len(sub), "mois": sub.mois.nunique()}
        for col in ["v_own", "v_cmt"]:
            o[f"{col}_pb"], o[f"et_{col}_pb"] = moy_et(sub, col)
        S3["par_annee"][str(an)] = o
    m2 = (V.annee != 2023) & (V.echeance != 30)
    S3["marge_moitie_sans_2023_ni_30_pb"] = marge(V[m2 & (V.periode == "avant")], V[m2 & (V.periode == "apres")])
    y23 = V[V.annee == 2023]
    S4 = {"sd_v_own_avant_pb": float(A.v_own.std(ddof=1)), "sd_v_own_apres_pb": float(B.v_own.std(ddof=1)),
          "sd_v_own_2023_pb": float(y23.v_own.std(ddof=1)), "sd_v_cmt_avant_pb": float(A.v_cmt.std(ddof=1)),
          "sd_v_cmt_apres_pb": float(B.v_cmt.std(ddof=1)), "sd_v_cmt_2023_pb": float(y23.v_cmt.std(ddof=1)),
          "corr_v_own_v_cmt_avant": float(np.corrcoef(A.v_own, A.v_cmt)[0, 1]),
          "corr_v_own_v_cmt_apres": float(np.corrcoef(B.v_own, B.v_cmt)[0, 1]),
          "n_2023": len(y23), "mois_2023": y23.mois.nunique(),
          "exclues_par_motif": {k: int((t.motif_exclusion == k).sum()) for k in
                                ["fenetre_chevauchee", "titre_non_emis_a_jm5", "valeur_manquante"]},
          "n_p_prix_fi_identique_a_deux_dates": int(V.prix_identiques.sum())}
    v["descriptif"] = {"S1_par_echeance": S1, "S2_deux_jambes": S2, "S3_par_annee": S3, "S4_hypotheses_comptes": S4}
    v["controles_schema"] = {**schema, "c9_ecart_max_formules_pb": err_max_c9}
    v["informations"] = {
        "sha256_d1": sha_d1, "n_lignes_d1": len(d1), "n_population_d1": n_pop, "population_par_echeance": pop_comptes,
        "n_lignes_fichier": len(t), "n_p": len(P), "tri_fichier_ok": tri_ok, "J_dans_C_pour_les_324": J_dans_C_324,
        "motifs_recalcules_sur_D1": motifs_recalc, "motifs_du_fichier": motifs_fichier,
        "controle_arith_d_moins_baisses": v["d_pb"] - (v["baisse_own_pb"] - v["baisse_cmt_pb"]),
        "n_avant_sans_30": int((A.echeance != 30).sum()), "mois_avant_sans_30": A[A.echeance != 30].mois.nunique(),
        "n_apres_sans_2023": int((B.annee != 2023).sum()), "mois_apres_sans_2023": B[B.annee != 2023].mois.nunique()}
    (ICI / "verification.json").write_text(json.dumps(propre(v), ensure_ascii=False, indent=1))
    V.to_csv(pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ICI / "verification_lignes.csv", index=False)
    print(json.dumps(propre({k: x for k, x in v.items() if k not in ("descriptif", "informations")}), indent=1))

if __name__ == "__main__":
    main()
