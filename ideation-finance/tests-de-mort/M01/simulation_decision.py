"""M01 — simulation de la décisivité de la règle de verdict, AVANT scellement.

N'utilise AUCUNE donnée : seulement des chiffres déjà scellés ou déjà publiés dans le registre (listés dans ENTREES).
Ne lit aucun fichier. Résultat : pour chaque scénario de dispersion et chaque « vérité » simulée, la fréquence des
verdicts survit / éliminée / non concluant donnés par la règle de la section 10 de la préinscription.

Usage : python3 simulation_decision.py            (environ une minute ; graine fixe, résultat identique à chaque fois)
"""
import numpy as np

GRAINE = 20261113
TIRAGES = 5000
Z = 1.645  # bornes à 90 % bilatéral = tests unilatéraux à 5 %

# ----------------------------------------------------------------------------- entrées (toutes déjà vues)
ENTREES = {
    # F04 (scellé ; écart-type dans F04/ecarts.md, E6) : V_cmt sur 321 réouvertures, 134 mois
    "f04_ecart_type_v": 2.573, "f04_erreur_type": 0.16135, "f04_n": 321, "f04_mois": 134,
    # F04, découpe descriptive (results/RESULTS.md) : moyenne, erreur type groupée, N, mois
    "f04_avant": (1.375, 0.125, 207, 96), "f04_apres": (0.054, 0.360, 114, 38),
    # F04, intervalles annuels à 95 % (results/RESULTS.md), années après 2021 : (borne basse, borne haute, N)
    "f04_annees": {2022: (-1.10, 1.70, 24), 2023: (-2.69, 2.64, 24), 2024: (-0.74, 1.21, 24),
                   2025: (-1.41, 0.33, 24), 2026: (-1.24, 2.01, 18)},
    # J05 (scellé) : 206 réouvertures avant 2022 (96 mois), 116 après (39 mois) ; K11 : 24 en 2023 (8 mois)
    "j05_n": (206, 116), "j05_mois": (96, 39),
    # J05, analyse S2 (results/RESULTS.md) : erreur type de la baisse de R = première jambe de V_own, N = 206 + 116
    "j05_erreur_type_baisse_r": 0.280,
}

# ICC intra-mois qui redonne le facteur de groupement de F04 : DE = (ET groupée / ET iid)^2 = 1 + (taille moyenne - 1) * ICC
_et_iid = ENTREES["f04_ecart_type_v"] / np.sqrt(ENTREES["f04_n"])
_de = (ENTREES["f04_erreur_type"] / _et_iid) ** 2
ICC = (_de - 1) / (ENTREES["f04_n"] / ENTREES["f04_mois"] - 1)


def sigma_par_adjudication(et_groupee, n, taille_mois):
    """Écart-type par adjudication tiré d'une erreur type groupée : sigma_eff = ET * racine(n) ; sigma = sigma_eff / racine(DE)."""
    return et_groupee * np.sqrt(n) / np.sqrt(1 + (taille_mois - 1) * ICC)


_m, et, n, g = ENTREES["f04_avant"]
SIGMA_AVANT = sigma_par_adjudication(et, n, n / g)
_var_eff = {a: n_a * ((h - b) / (2 * 1.96)) ** 2 for a, (b, h, n_a) in ENTREES["f04_annees"].items()}
_n_hors = sum(ENTREES["f04_annees"][a][2] for a in _var_eff if a != 2023)
SIGMA_APRES_HORS_2023 = np.sqrt(sum(ENTREES["f04_annees"][a][2] * v for a, v in _var_eff.items() if a != 2023) / _n_hors) \
    / np.sqrt(1 + 2 * ICC)
SIGMA_2023 = np.sqrt(_var_eff[2023]) / np.sqrt(1 + 2 * ICC)
# V_own plus bruité que V_cmt : sigma efficace de R = 0,280 / racine(1/206 + 1/116) ; V = deux jambes -> x racine(2) ;
# rapport au sigma efficace de V_cmt dans F04 (0,16135 x racine(321))
K_OWN_STRESS = (ENTREES["j05_erreur_type_baisse_r"] / np.sqrt(1 / 206 + 1 / 116) * np.sqrt(2)) \
    / (ENTREES["f04_erreur_type"] * np.sqrt(ENTREES["f04_n"]))

# ----------------------------------------------------------------------------- plan d'échantillon
def plan(n10_avant=97, n20_avant=13, apres_moins_un_20=True):
    """Lignes (mois, échéance, année, période). Avant : 96 mois de réouvertures à 10 et 30 ans (8 par an, 2010-2021),
    une réouverture à 10 ans de plus dans un mois de 2019 si n10_avant = 97, une de moins si 95 (M01 exclut les deux réouvertures à 10 ans de juin 2019),
    et les 20 ans dans les 13 derniers mois. Après : 39 mois (8 par an 2022-2025, 7 en 2026), trois échéances par mois."""
    mois, ech, an, per = [], [], [], []
    for g in range(96):
        for m in (10, 30):
            mois.append(g); ech.append(m); an.append(2010 + g // 8); per.append(0)
    extra = n10_avant - 96
    if extra == 1:
        mois.append(75); ech.append(10); an.append(2019); per.append(0)
    elif extra == -1:  # M01 exclut les deux réouvertures à 10 ans de juin 2019 : on retire celle du mois 75
        idx = [i for i in range(len(mois)) if ech[i] == 10 and mois[i] == 75][0]
        for L in (mois, ech, an, per):
            L.pop(idx)
    for g in range(96 - n20_avant, 96):
        mois.append(g); ech.append(20); an.append(2010 + g // 8); per.append(0)
    for k in range(39):
        for m in (10, 20, 30):
            if apres_moins_un_20 and k == 38 and m == 20:
                continue
            mois.append(96 + k); ech.append(m); an.append(2022 + k // 8); per.append(1)
    return np.array(mois), np.array(ech), np.array(an), np.array(per)


# ----------------------------------------------------------------------------- statistiques (formules de la section 8)
def moyenne_groupee(x, mois):
    """Moyenne et erreur type groupée par mois : ET = (1/N) racine( G/(G-1) somme_g S_g^2 ), S_g = somme (x - moyenne)."""
    n = len(x); m = x.mean()
    s = np.bincount(mois, weights=x - m)
    G = int((np.bincount(mois) > 0).sum())
    return m, np.sqrt(G / (G - 1) * (s ** 2).sum()) / n


def champs(vc, vo, mois, per, garde):
    av, ap = garde & (per == 0), garde & (per == 1)
    oa_m, oa_e = moyenne_groupee(vo[ap], mois[ap]); ob_m, ob_e = moyenne_groupee(vo[av], mois[av])
    ca_m, ca_e = moyenne_groupee(vc[ap], mois[ap]); cb_m, cb_e = moyenne_groupee(vc[av], mois[av])
    ga_m, _ = moyenne_groupee((vc - vo)[ap], mois[ap]); gb_m, _ = moyenne_groupee((vc - vo)[av], mois[av])
    d = ga_m - gb_m
    baisse_cmt = cb_m - ca_m
    return {
        "bi_own_avant": ob_m - Z * ob_e,
        "bi_baisse_cmt": baisse_cmt - Z * np.hypot(cb_e, ca_e),
        "bi_own_apres": oa_m - Z * oa_e,
        "bi_baisse_own": (ob_m - oa_m) - Z * np.hypot(ob_e, oa_e),
        "marge": d + 0.5 * baisse_cmt,
    }


def verdict(t, s23, s30):
    """Règle de la section 10, gardes de données mises à part (échantillon complet, schéma valide)."""
    if not (t["bi_own_avant"] > 0 and t["bi_baisse_cmt"] > 0):
        return "nc"  # contrôle positif ou contrôle de la cassure en échec
    survit = t["bi_own_apres"] > 0 and t["marge"] <= 0 and s23["marge"] <= 0 and s30["marge"] <= 0
    elimine = t["bi_baisse_own"] > 0 and t["marge"] > 0 and s23["marge"] > 0 and s30["marge"] > 0
    return "s" if survit else ("e" if elimine else "nc")


# ----------------------------------------------------------------------------- tirages
def simuler(moyennes, sigmas, rho, rng, P):
    """V_cmt et V_own : moyenne de la période + effet du mois (part ICC de la variance) + bruit propre ;
    corrélation rho entre les deux mesures, pour l'effet du mois comme pour le bruit propre."""
    mois, ech, an, per = P
    uniq = np.unique(mois)
    pos = np.searchsorted(uniq, mois)
    a = rng.standard_normal((len(uniq), 2)); a[:, 1] = rho * a[:, 0] + np.sqrt(1 - rho ** 2) * a[:, 1]
    e = rng.standard_normal((len(mois), 2)); e[:, 1] = rho * e[:, 0] + np.sqrt(1 - rho ** 2) * e[:, 1]
    bruit = np.sqrt(ICC) * a[pos] + np.sqrt(1 - ICC) * e
    (mc, mo) = moyennes
    vc = mc[per] + sigmas[:, 0] * bruit[:, 0]
    vo = mo[per] + sigmas[:, 1] * bruit[:, 1]
    return vc, vo


def frequences(moyennes, scenario, rho, P, tirages=TIRAGES):
    rng = np.random.default_rng(GRAINE)
    mois, ech, an, per = P
    sig = scenario(P)
    tous = np.ones(len(mois), bool)
    sans23 = ~((per == 1) & (an == 2023))
    sans30 = ech != 30
    n = {"s": 0, "e": 0, "nc": 0}
    for _ in range(tirages):
        vc, vo = simuler(moyennes, sig, rho, rng, P)
        n[verdict(champs(vc, vo, mois, per, tous), champs(vc, vo, mois, per, sans23),
                  champs(vc, vo, mois, per, sans30))] += 1
    return {k: v / tirages for k, v in n.items()}


def homoscedastique(k_own=1.0):
    def f(P):
        s = np.full(len(P[0]), ENTREES["f04_ecart_type_v"])
        return np.column_stack([s, k_own * s])
    return f


def heteroscedastique(k_own=1.0):
    def f(P):
        _, _, an, per = P
        s = np.where(per == 0, SIGMA_AVANT, np.where(an == 2023, SIGMA_2023, SIGMA_APRES_HORS_2023))
        return np.column_stack([s, k_own * s])
    return f


CB, CA = ENTREES["f04_avant"][0], ENTREES["f04_apres"][0]  # V_cmt : 1,375 avant, 0,054 après
VERITES = {
    "mesure (V_own inchangé)":            (np.array([CB, CA]), np.array([CB, CB])),
    "marché (V_own baisse comme V_cmt)":  (np.array([CB, CA]), np.array([CB, CA])),
    "mixte, moitié":                      (np.array([CB, CA]), np.array([CB, (CB + CA) / 2])),
    "mixte, F04-bis additif (0,78)":      (np.array([CB, CA]), np.array([CB, CA + 0.78])),
    "mesure, instrument atténué (0,85)":  (np.array([CB, CA]), np.array([0.85, 0.85])),
    "marché, instrument atténué (0,85)":  (np.array([CB, CA]), np.array([0.85, CA])),
}
SCENARIOS = [
    ("A  énoncé : sigma 2,57, groupement F04, rho 0", homoscedastique(), 0.0),
    ("A' énoncé, rho 0,5", homoscedastique(), 0.5),
    ("B  hétéroscédastique (2023 bruyante), rho 0", heteroscedastique(), 0.0),
    ("B' hétéroscédastique, rho 0,5", heteroscedastique(), 0.5),
    ("C  B + V_own %.2f fois plus bruité, rho 0" % K_OWN_STRESS, heteroscedastique(K_OWN_STRESS), 0.0),
    ("C' B + V_own %.2f fois plus bruité, rho 0,5" % K_OWN_STRESS, heteroscedastique(K_OWN_STRESS), 0.5),
]

if __name__ == "__main__":
    print(f"ICC = {ICC:.3f} ; sigma avant = {SIGMA_AVANT:.2f} ; après hors 2023 = {SIGMA_APRES_HORS_2023:.2f} ; "
          f"2023 = {SIGMA_2023:.2f} ; facteur V_own (stress) = {K_OWN_STRESS:.2f}")
    P_j05 = plan()
    assert ((P_j05[3] == 0).sum(), (P_j05[3] == 1).sum()) == (206, 116)
    assert ((P_j05[3] == 1) & (P_j05[2] == 2023)).sum() == 24
    print(f"plan J05 : 206 avant / 116 après ; {TIRAGES} tirages ; graine {GRAINE}")
    for nom, scen, rho in SCENARIOS:
        print("\n" + nom)
        for v, mu in VERITES.items():
            f = frequences(mu, scen, rho, P_j05)
            print(f"  {v:38s} survit {f['s']:.3f}  éliminée {f['e']:.3f}  non concluant {f['nc']:.3f}")
    P_m01 = plan(n10_avant=95, n20_avant=13, apres_moins_un_20=False)
    assert ((P_m01[3] == 0).sum(), (P_m01[3] == 1).sum()) == (204, 117)
    print("\nContrôle : comptes attendus de M01 (204 avant / 117 après), scénario A")
    for v in list(VERITES)[:2]:
        f = frequences(VERITES[v], homoscedastique(), 0.0, P_m01)
        print(f"  {v:38s} survit {f['s']:.3f}  éliminée {f['e']:.3f}  non concluant {f['nc']:.3f}")
