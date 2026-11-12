# Controle independant : projections alternees (within) au lieu d'indicatrices, sans reutiliser analyse.py
import sys, numpy as np, pandas as pd
p = pd.read_csv(sys.argv[1], dtype={"date": str})
n_or = p[p.statut=="origine"].groupby("signal").size()
K = set(n_or[n_or>=60].index)
U0 = p[(p.dans_fenetre==1)&p.statut.isin(["origine","attente"])&p.signal.isin(K)]
T0 = p[(p.dans_fenetre==1)&(p.statut=="publie")]
def est(U, Tc, avance=False):
    T = Tc[Tc.signal.isin(set(U.signal)) & Tc.date.isin(set(U.date))]
    i = pd.factorize(U.signal)[0]; t = pd.factorize(U.date)[0]
    def dem(v):
        v = v.astype(float).copy()
        for _ in range(2000):
            v0 = v.copy()
            v -= (np.bincount(i, v)/np.bincount(i))[i]
            v -= (np.bincount(t, v)/np.bincount(t))[t]
            if np.abs(v-v0).max() < 1e-13: break
        return v
    y = U.ret.values; att = (U.statut=="attente").values.astype(float)
    cols = [att]
    if avance: cols.append(((U.statut=="attente")&(U.annee==U.annee_pub-1)).values.astype(float))
    Xd = np.column_stack([dem(c) for c in cols]); yd = dem(y)
    beta = np.linalg.lstsq(Xd, yd, rcond=None)[0]
    if avance: return beta[1]
    # effets fixes : residu partiel r = y - b*att = a_i + l_t + e ; valeurs ajustees des FE = r - dem(r)
    r = y - beta[0]*att
    fe = r - dem(r)                      # a_i + l_t pour chaque ligne de U
    # recuperer a_i et l_t par moindres carres sur la somme (normalisation l_premier_mois=0 non necessaire)
    # resoudre a, l par alternance
    a = np.zeros(i.max()+1); l = np.zeros(t.max()+1)
    for _ in range(5000):
        a_new = np.bincount(i, fe - l[t])/np.bincount(i)
        l_new = np.bincount(t, fe - a_new[i])/np.bincount(t)
        d = max(np.abs(a_new-a).max(), np.abs(l_new-l).max()); a, l = a_new, l_new
        if d < 1e-13: break
    amap = dict(zip(pd.factorize(U.signal)[1], a)); lmap = dict(zip(pd.factorize(U.date)[1], l))
    tau = T.ret.values - (T.signal.map(amap).values + T.date.map(lmap).values + beta[0])
    return tau.mean()/T.moy_origine.mean(), tau.mean(), T.moy_origine.mean(), beta[0], len(T), T.signal.nunique()
full = est(U0, T0); print("complet", full)
th = [est(U0[U0.annee!=g], T0[T0.annee!=g])[0] for g in range(1974, 2014)]
th = np.array(th); G = len(th); se = np.sqrt((G-1)/G*((th-th.mean())**2).sum())
print("se", se, "ic", full[0]-2.12*se, full[0]+2.12*se, "marge", min(full[0]+2.12*se, -0.30-(full[0]-2.12*se)))
d = est(U0, T0, True); dg = np.array([est(U0[U0.annee!=g], T0, True) for g in range(1974, 2014)])
sed = np.sqrt((G-1)/G*((dg-dg.mean())**2).sum()); print("d", d, "se_d", sed, "t", d/sed)
