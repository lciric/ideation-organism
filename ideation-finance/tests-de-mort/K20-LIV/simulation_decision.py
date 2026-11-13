"""K20-LIV — simulation de décision, écrite AVANT le scellement par le rédacteur de préinscription.

Ce script n'ouvre AUCUN fichier de données. Il ne lit ni prévision, ni réalisation, ni erreur, ni révision.
Il n'utilise que :
  1. la grille de l'échantillon principal (variables × cibles), écrite ici par des règles de dates. Elle a été
     établie sur les fichiers réels par la seule PRÉSENCE des cellules (section 5 de la préinscription) ;
  2. les fenêtres d'épisodes (section 6) ;
  3. des dispersions tirées des chiffres scellés de K20 (tests-de-mort/K20/verdict.json) :
       b_moyen = 0,1936 ; k_moyen = 0,2943 ; rapport_variance_revision = 3,0635 ;
       effet de plan = (et_c_dk4 / et_c_iid)^2 = (0,070685 / 0,063872)^2 = 1,2247.

Il applique la règle de verdict préinscrite (section 9) à des panels simulés de mêmes dimensions, sous c = 0 et sous
c = 0,40 (la prédiction), et rapporte la probabilité d'atteindre un verdict : « éliminée » sous c = 0, « survit » sous
c = 0,40. Graine fixe ; 4 000 tirages par cas (au moins 2 000 exigés).

Les autres réglages sont des choix du rédacteur, décrits en section 8 de la préinscription : bruit du consensus nu = 0,05,
moyenne mobile d'ordre 1 (theta = 0,3), volatilité groupée par semestre (0,3). La corrélation commune par date (rho) est
calibrée pour reproduire l'effet de plan de K20. Les sensibilités S-a à S-d suivent le scénario principal ; seul le
scénario principal porte l'exigence (>= 0,80). Sortie : texte sur la console seulement ; aucun fichier écrit.
Durée : environ 25 minutes sur un cœur.

Usage : python3 simulation_decision.py [--tirages 4000] [--graine 20261113] [--rapide]
"""
import argparse
import numpy as np

# ---------------------------------------------------------------------------------------------------------------
# 1. Grille de l'échantillon principal (règles de dates ; comptes vérifiés sur les fichiers par la présence seule)
# ---------------------------------------------------------------------------------------------------------------

def cibles(premiere, derniere, sauf=()):
    """Mois cibles (juin ou décembre) de `premiere` à `derniere` inclus, en sautant `sauf`."""
    out, (a, m) = [], premiere
    while (a, m) <= derniere:
        if (a, m) not in sauf:
            out.append((a, m))
        a, m = (a, 12) if m == 6 else (a + 1, 6)
    return out

GRILLE = {
    "CPI":   cibles((1947, 12), (2025, 12), sauf={(2005, 6)}),
    "UNPR":  cibles((1962, 6), (2025, 12), sauf={(2020, 6), (2020, 12), (2021, 6), (2021, 12)}),
    "PRIME": cibles((1982, 6), (2026, 6)),
    "TBILL": cibles((1993, 6), (2026, 6)),
    "TPHS":  cibles((1970, 12), (2026, 6)),
}
ATTENDU = {"CPI": 156, "UNPR": 124, "PRIME": 89, "TBILL": 67, "TPHS": 112}

# Fenêtres d'épisodes en mois cibles inclus (pic NBER -> creux NBER + 14 mois ; fusion des chevauchements ; E11 joint
# la fenêtre de 2020 aux cibles 2021-2023).
EPISODES = {
    "E1": ((1948, 11), (1950, 12)), "E2": ((1953, 7), (1955, 7)), "E3": ((1957, 8), (1959, 6)),
    "E4": ((1960, 4), (1962, 4)), "E5": ((1969, 12), (1972, 1)), "E6": ((1973, 11), (1976, 5)),
    "E7": ((1980, 1), (1984, 1)), "E8": ((1990, 7), (1992, 5)), "E9": ((2001, 3), (2003, 1)),
    "E10": ((2007, 12), (2010, 8)), "E11": ((2020, 2), (2023, 12)),
}

def semestre(a, m):
    return 2 * a + (0 if m == 6 else 1)

def construire_panel(variables):
    v_idx, tau, ep = [], [], []
    for j, v in enumerate(variables):
        assert len(GRILLE[v]) == ATTENDU[v], (v, len(GRILLE[v]))
        for (a, m) in GRILLE[v]:
            v_idx.append(j)
            tau.append(semestre(a, m))
            code = 0
            for k, (deb, fin) in enumerate(EPISODES.values(), start=1):
                if deb <= (a, m) <= fin:
                    code = k
            ep.append(code)
    tau = np.array(tau)
    return np.array(v_idx), tau - tau.min(), np.array(ep), int(tau.max() - tau.min() + 1)

# ---------------------------------------------------------------------------------------------------------------
# 2. Estimation : exactement les étapes de la section 6 (MCO, Driscoll-Kraay par date, Bartlett)
# ---------------------------------------------------------------------------------------------------------------

def dk_var(X, u, tau, nd, lags):
    XtX_inv = np.linalg.inv(X.T @ X)
    H = np.zeros((nd, X.shape[1]))
    np.add.at(H, tau, X * u[:, None])
    om = H.T @ H
    for j in range(1, lags + 1):
        g = H[j:].T @ H[:-j]
        om += (1 - j / (lags + 1)) * (g + g.T)
    return XtX_inv @ om @ XtX_inv, XtX_inv

def mco(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta, y - X @ beta

def regression_principale(ze, zr, L, v_idx, tau, nd, V, lags=2):
    D = np.eye(V)[v_idx]
    X = np.hstack([D, D * L[:, None], D * zr[:, None], (zr * L)[:, None]])
    beta, u = mco(X, ze)
    Vdk, XtX_inv = dk_var(X, u, tau, nd, lags)
    n, p = X.shape
    se_iid = np.sqrt(XtX_inv[-1, -1] * (u @ u) / (n - p))
    return beta, np.sqrt(Vdk[-1, -1]), se_iid

def appliquer_regle(e, r, s, v_idx, tau, ep, nd, V, nu_bar, n_ep):
    # Étape 1 : réduction par variable
    ze, zr, kv = np.empty_like(e), np.empty_like(r), np.empty(V)
    for j in range(V):
        m = v_idx == j
        sr, se_ = r[m].std(ddof=1), e[m].std(ddof=1)
        zr[m] = (r[m] - r[m].mean()) / sr
        ze[m] = (e[m] - e[m].mean()) / se_
        kv[j] = sr / se_
    # Étape 2 : grande nouvelle = tiers supérieur de |surprise| par variable
    L = np.zeros_like(e)
    for j in range(V):
        m = v_idx == j
        L[m] = (np.abs(s[m]) > np.quantile(np.abs(s[m]), 2 / 3)).astype(float)
    # Étapes 3 à 5
    beta, et_c, et_iid = regression_principale(ze, zr, L, v_idx, tau, nd, V)
    c = beta[-1]
    b_moyen = beta[2 * V:3 * V].mean()
    lo, hi = c - 1.645 * et_c, c + 1.645 * et_c
    # Rapport de variance et biais mécanique (bruit mesuré : nu_LIV = 2 x moyenne des parts médianes)
    a_, A_ = [], []
    for j in range(V):
        for l, acc in ((0, a_), (1, A_)):
            m = (v_idx == j) & (L == l)
            acc.append((zr[m] - zr[m].mean()) ** 2)
    a, A = np.concatenate(a_).mean(), np.concatenate(A_).mean()
    nu_liv = 2 * nu_bar
    biais = (2 * b_moyen + kv.mean()) * (nu_liv / 2) * (1 / a - 1 / A)
    seuil = max(0.10, biais)
    marge = min(seuil - lo, hi - 0.40)
    # Garde d'épisodes
    t_ex, c_ex = [], []
    for k in range(1, n_ep + 1):
        m = ep != k
        if m.all():
            continue  # épisode sans ligne dans ce panel : rien à retirer
        bk, ek, _ = regression_principale(ze[m], zr[m], L[m], v_idx[m], tau[m], nd, V)
        c_ex.append(bk[-1]); t_ex.append(bk[-1] / ek)
    t_min, c_min = (min(t_ex), min(c_ex)) if t_ex else (np.inf, np.inf)
    conflit = int(lo > seuil and hi >= 0.40 and t_min < 1 and c_min > 0)
    # Contrôle positif : pente de sous-réaction de base REGROUPÉE (régression de Coibion-Gorodnichenko sur toutes
    # les lignes principales, constantes propres à chaque variable, une seule pente, sans classe).
    D = np.eye(V)[v_idx]
    Xb = np.hstack([D, zr[:, None]])
    bb, ub = mco(Xb, ze)
    Vb, _ = dk_var(Xb, ub, tau, nd, 2)
    # Champ dérivé controle_positif_ok : 1 si la borne basse à 90 % de la pente regroupée est > 0, ou si tout
    # l'intervalle à 90 % de c est sous 0 (une interaction nettement négative n'est pas une interaction nulle).
    ctrl = int((bb[-1] - 1.645 * np.sqrt(Vb[-1, -1]) > 0) or (hi < 0))
    # Règle (section 9 ; mêmes opérateurs que verdict.py)
    non_concl = (A / a < 1.25) or (ctrl < 1) or (marge >= 0) or (conflit >= 1)
    if non_concl:
        verdict = "non concluant"
    elif (lo - seuil > 0) and (hi >= 0.40) and (t_min >= 1.0):
        verdict = "survit"
    else:
        verdict = "éliminée"
    return verdict, dict(c=c, et_c=et_c, et_iid=et_iid, ratio=A / a, biais=biais, seuil=seuil, ctrl=ctrl, b=bb[-1])

# ---------------------------------------------------------------------------------------------------------------
# 3. Processus simulé
# ---------------------------------------------------------------------------------------------------------------

def tirer(rng, n, queues):
    if queues is None:
        return rng.standard_normal(n)
    return rng.standard_t(queues, n) / np.sqrt(queues / (queues - 2))

def echelle_dates(rng, nd, vol, phi=0.7):
    """Volatilité groupée par date : log-échelle AR(1) (phi = 0,7 par semestre), normalisée pour E[échelle^2] = 1."""
    if vol == 0:
        return np.ones(nd)
    z = np.empty(nd)
    z[0] = rng.standard_normal()
    for t in range(1, nd):
        z[t] = phi * z[t - 1] + np.sqrt(1 - phi ** 2) * rng.standard_normal()
    return np.exp(vol * z - vol ** 2)

def simuler(rng, P, c, v_idx, tau, nd, V):
    n = len(v_idx)
    rho, th = P["rho"], P["theta"]
    sig = echelle_dates(rng, nd, P["vol"])[tau]
    g = tirer(rng, nd, P["queues"])
    w = tirer(rng, nd + 1, P["queues"])
    hcom = (w[1:] + th * w[:-1]) / np.sqrt(1 + th ** 2)
    wid = tirer(rng, V * (nd + 1), P["queues"]).reshape(V, nd + 1)
    hid = (wid[:, 1:] + th * wid[:, :-1]) / np.sqrt(1 + th ** 2)
    s0 = np.sqrt(rho) * g[tau] + np.sqrt(1 - rho) * tirer(rng, n, P["queues"])
    s_star = sig * s0                                           # surprise vraie
    r_star = sig * (s0 + np.sqrt(P["sig_eta2"]) * rng.standard_normal(n))   # révision vraie
    var_rs = 1 + P["sig_eta2"]
    om = P["nu_bar"] / 2 * var_rs / (1 - P["nu_bar"])          # variance du bruit d'une enquête
    e1, e2 = np.sqrt(om) * rng.standard_normal(n), np.sqrt(om) * rng.standard_normal(n)
    r = r_star + e2 - e1                                        # révision publiée
    s = s_star - 0.75 * e1                                      # surprise : contient le bruit de l'enquête s
    L = np.zeros(n)
    for j in range(V):
        m = v_idx == j
        L[m] = (np.abs(s[m]) > np.quantile(np.abs(s[m]), 2 / 3)).astype(float)
    sr = np.sqrt(var_rs + 2 * om)
    se_ = sr / P["k"]
    b_raw, c_raw = P["b"] * se_ / sr, c * se_ / sr
    su2 = se_ ** 2 * (1 - P["b"] ** 2) - om
    u = sig * np.sqrt(su2) * (np.sqrt(rho) * hcom[tau] + np.sqrt(1 - rho) * hid[v_idx, tau])
    e = b_raw * r_star + c_raw * r_star * L + u - e2           # erreur publiée : contient - bruit de l'enquête s+1
    return e, r, s

def calibrer_sig_eta2(rng, P, cible):
    """sig_eta2 tel que le rapport A/a observé vaille `cible` (grand échantillon, une variable)."""
    lo, hi = 0.0, 20.0
    n = 200_000
    zeta = rng.standard_normal(n)
    sig = np.exp(P["vol"] * zeta - P["vol"] ** 2)
    s0 = tirer(rng, n, P["queues"])
    eta = rng.standard_normal(n)
    e1, e2 = rng.standard_normal(n), rng.standard_normal(n)
    for _ in range(40):
        mid = (lo + hi) / 2
        om = P["nu_bar"] / 2 * (1 + mid) / (1 - P["nu_bar"])
        r = sig * (s0 + np.sqrt(mid) * eta) + np.sqrt(om) * (e2 - e1)
        s = sig * s0 - 0.75 * np.sqrt(om) * e1
        L = np.abs(s) > np.quantile(np.abs(s), 2 / 3)
        ratio = r[L].var() / r[~L].var()
        lo, hi = (mid, hi) if ratio > cible else (lo, mid)
    return (lo + hi) / 2

def calibrer_rho(rng, P, cible_effet, v_idx, tau, nd, V, n_ep, ep, tirages=300):
    """rho (corrélation commune par date) tel que E[(et_dk/et_iid)^2] vaille l'effet de plan de K20."""
    meilleur = None
    for rho in np.round(np.arange(0.0, 0.951, 0.05), 2):
        Q = dict(P, rho=rho)
        ratios = []
        for _ in range(tirages):
            e, r, s = simuler(rng, Q, 0.0, v_idx, tau, nd, V)
            _, d = appliquer_regle(e, r, s, v_idx, tau, ep, nd, V, Q["nu_bar"], 0)
            ratios.append((d["et_c"] / d["et_iid"]) ** 2)
        m = float(np.mean(ratios))
        if meilleur is None or abs(m - cible_effet) < abs(meilleur[1] - cible_effet):
            meilleur = (rho, m)
    return meilleur

def scenario(nom, P, variables, tirages, graine, cs=(0.0, 0.40)):
    v_idx, tau, ep, nd = construire_panel(variables)
    V, n_ep = len(variables), len(EPISODES)
    rng = np.random.default_rng(graine)
    P = dict(P)
    P["sig_eta2"] = calibrer_sig_eta2(rng, P, P["rapport"])
    rho, effet = calibrer_rho(rng, P, P["effet_plan"], v_idx, tau, nd, V, n_ep, ep)
    P["rho"] = rho
    print(f"\n=== Scénario {nom} : variables {variables}, n = {len(v_idx)}, dates (semestres) = {len(np.unique(tau))}, "
          f"plage = {nd}")
    print(f"    paramètres : b = {P['b']}, k = {P['k']}, rapport visé = {P['rapport']}, nu_bar = {P['nu_bar']}, "
          f"queues = {P['queues']}, theta = {P['theta']}, vol = {P['vol']} ; calibrés : sig_eta2 = {P['sig_eta2']:.3f}, "
          f"rho = {float(rho)} (effet de plan simulé {effet:.2f}, visé {P['effet_plan']:.2f})")
    lignes_ep = {k: int((ep == i).sum()) for i, k in enumerate(EPISODES, start=1)}
    print(f"    lignes principales par épisode : {lignes_ep} ; hors épisode : {int((ep == 0).sum())}")
    res = {}
    for c in cs:
        compte = {"survit": 0, "éliminée": 0, "non concluant": 0}
        stats = []
        for _ in range(tirages):
            e, r, s = simuler(rng, P, c, v_idx, tau, nd, V)
            verdict, d = appliquer_regle(e, r, s, v_idx, tau, ep, nd, V, P["nu_bar"], n_ep)
            compte[verdict] += 1
            stats.append((d["c"], d["et_c"], d["ratio"], d["seuil"], d["ctrl"]))
        st = np.array(stats)
        pr = {k: v / tirages for k, v in compte.items()}
        res[c] = pr
        print(f"    c vrai = {c:+.2f} : survit {pr['survit']:.3f} | éliminée {pr['éliminée']:.3f} | "
              f"non concluant {pr['non concluant']:.3f} || moyenne c^ {st[:, 0].mean():+.3f}, é.-t. de c^ "
              f"{st[:, 0].std():.3f}, et_c_dk2 moyen {st[:, 1].mean():.3f}, rapport moyen {st[:, 2].mean():.2f}, "
              f"plancher moyen {st[:, 3].mean():.3f}, contrôle positif réussi {st[:, 4].mean():.3f}")
    return res

# Dispersions scellées de K20 (tests-de-mort/K20/verdict.json, chiffres du vérificateur)
K20 = dict(b=0.1936, k=0.2943, rapport=3.0635, effet_plan=(0.070685 / 0.063872) ** 2)
PRINCIPAL = dict(K20, nu_bar=0.05, queues=None, theta=0.3, vol=0.3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tirages", type=int, default=4000)
    ap.add_argument("--graine", type=int, default=20261113)
    ap.add_argument("--rapide", action="store_true", help="300 tirages, pour essai")
    a = ap.parse_args()
    t = 300 if a.rapide else a.tirages
    cinq = ["CPI", "UNPR", "PRIME", "TBILL", "TPHS"]
    print("Simulation de décision K20-LIV — aucune donnée de résultat lue.")
    # Scénario principal : dispersions de K20, plan retenu (cinq variables). C'est lui qui décide (>= 0,80 exigé).
    res = scenario("PRINCIPAL (dispersions de K20)", PRINCIPAL, cinq, t, a.graine, cs=(-0.40, -0.20, 0.0, 0.10, 0.20, 0.40, 0.60))
    # Sensibilités, rapportées, hors exigence.
    scenario("S-a : quatre variables sans TPHS", PRINCIPAL, cinq[:4], t, a.graine + 1)
    scenario("S-b : cibles en niveau (rapport 5, k = 1)", dict(PRINCIPAL, rapport=5.0, k=1.0), cinq, t, a.graine + 2)
    scenario("S-c : pessimiste (rapport 5, k = 1, queues t5, effet de plan 2, bruit nu_bar 0,10)",
             dict(PRINCIPAL, rapport=5.0, k=1.0, queues=5, effet_plan=2.0, nu_bar=0.10, vol=0.6), cinq, t, a.graine + 3)
    scenario("S-d : sous-réaction de base faible (b = 0,10)", dict(PRINCIPAL, b=0.10), cinq, t, a.graine + 4)
    p_elim, p_surv = res[0.0]["éliminée"], res[0.40]["survit"]
    print(f"\nDÉCISION (scénario principal) : P(éliminée | c = 0) = {p_elim:.3f} ; P(survit | c = 0,40) = {p_surv:.3f} ; "
          f"exigence >= 0,80 pour les deux : {'TENUE' if min(p_elim, p_surv) >= 0.80 else 'NON TENUE'}")

if __name__ == "__main__":
    main()
