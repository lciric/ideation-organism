"""M01 -- contrôle croisé du vérificateur, par d'autres chemins que verification.py :
- calendrier : pandas USFederalHolidayCalendar (au lieu de la construction à la main) ;
- rendements : échéancier par dateutil.relativedelta, résolution par Newton (scipy.optimize.newton) au lieu de brentq ;
- ET groupées : statsmodels OLS sur une constante, cov_type='cluster' (facteur G/(G-1)·(N-1)/(N-K), K = 1) ;
- marges : par la moyenne de h (m = moy_B(h) - moy_A(h)... au signe près, voir 4.4) ;
compare enfin aux nombres de verification.json.  Usage : python3 verification_controle.py
"""
import json, pathlib, datetime as dt
import numpy as np, pandas as pd, statsmodels.api as sm
from dateutil.relativedelta import relativedelta
from scipy.optimize import newton
from pandas.tseries.holiday import USFederalHolidayCalendar

ICI = pathlib.Path(__file__).resolve().parent
t = pd.read_csv(ICI / "M01_analyse.csv", keep_default_na=False, dtype=str)
P = t[t.dans_p == "1"].reset_index(drop=True)
ver = json.loads((ICI / "verification.json").read_text())

# --- calendrier par pandas
fer = USFederalHolidayCalendar().holidays("2008-12-01", "2027-12-31")
jours = pd.bdate_range("2009-06-01", "2026-12-31")
jours = jours[~jours.isin(fer) & ~jours.isin(pd.to_datetime(["2012-10-30", "2018-12-05"]))]
C = [d.date() for d in jours]; rang = {d: i for i, d in enumerate(C)}
cal_ok = all(dt.date.fromisoformat(r.date_jm5) == C[rang[dt.date.fromisoformat(r.date_adjudication)] - 5] and
             dt.date.fromisoformat(r.date_jp5) == C[rang[dt.date.fromisoformat(r.date_adjudication)] + 5]
             for r in P.itertuples())

# --- rendements par un autre chemin
def echeancier(M, d):
    k, T = 0, []
    while M - relativedelta(months=6 * k) > d:
        T.append(M - relativedelta(months=6 * k)); k += 1
    return T[::-1], M - relativedelta(months=6 * k)

def Y(prix, c, M, d):
    T, L = echeancier(M, d); N = T[0]
    w = (N - d).days / (N - L).days
    ai = c / 2 * (d - L).days / (N - L).days
    flux = np.array([c / 2] * (len(T) - 1) + [100 + c / 2]); e = np.arange(len(T)) + w
    f = lambda y: np.sum(flux * (1 + y / 200) ** -e) - prix - ai
    fp = lambda y: np.sum(flux * -e / 200 * (1 + y / 200) ** (-e - 1))
    return newton(f, c, fprime=fp, tol=1e-13, maxiter=200)

def G(b, c, M, x):
    T, L = echeancier(M, x); N = T[0]
    ai = c / 2 * (x - L).days / (N - L).days
    flux = np.array([c / 2] * (len(T) - 1) + [100 + c / 2])
    m = np.array([(u - x).days / 365.25 for u in T])
    b0, b1, b2, b3, t1, t2 = b
    z = (b0 + b1 * (1 - np.exp(-m / t1)) / (m / t1) + b2 * ((1 - np.exp(-m / t1)) / (m / t1) - np.exp(-m / t1))
         + b3 * ((1 - np.exp(-m / t2)) / (m / t2) - np.exp(-m / t2)))
    return Y(np.sum(flux * np.exp(-z * m / 100)) - ai, c, M, x)

X = ["jm5", "j", "jp5"]
rows, emax = [], 0.0
for r in P.itertuples():
    c, M = float(r.taux_coupon_pct), dt.date.fromisoformat(r.date_echeance)
    dd = dict(jm5=r.date_jm5, j=r.date_adjudication, jp5=r.date_jp5)
    eo, ec = {}, {}
    for x in X:
        d = dt.date.fromisoformat(dd[x])
        f = Y(float(getattr(r, f"prix_fi_{x}")), c, M, d)
        g = G([float(getattr(r, f"{p}_{x}")) for p in ["beta0", "beta1", "beta2", "beta3", "tau1", "tau2"]], c, M, d)
        emax = max(emax, abs(f - float(getattr(r, f"rdt_fi_{x}_pct"))), abs(g - float(getattr(r, f"rdt_gsw_{x}_pct"))))
        eo[x] = 100 * (f - g); ec[x] = 100 * (float(getattr(r, f"cmt_{x}")) - float(getattr(r, f"gswpar_{x}")))
    vo = 2 * eo["j"] - eo["jm5"] - eo["jp5"]; vc = 2 * ec["j"] - ec["jm5"] - ec["jp5"]
    rows.append(dict(mois=r.mois, per=r.periode, an=int(r.annee), ech=int(r.echeance), vo=vo, vc=vc, e=vc - vo, h=vc / 2 - vo))
V = pd.DataFrame(rows)

def mse(df, col):
    res = sm.OLS(df[col].values, np.ones(len(df))).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(df.mois)[0]})
    return float(res.params[0]), float(res.bse[0])

A, B = V[V.per == "avant"], V[V.per == "apres"]
c = {}
c["ecart_max_rdt_pb"] = 100 * emax
c["v_own_avant_pb"], c["et_v_own_avant_pb"] = mse(A, "vo")
c["borne_inf_90_v_own_avant_pb"] = c["v_own_avant_pb"] - 1.645 * c["et_v_own_avant_pb"]
c["v_own_apres_pb"], c["et_v_own_apres_pb"] = mse(B, "vo")
ca, sa = mse(A, "vc"); cb, sb = mse(B, "vc")
c["v_cmt_avant_pb"], c["v_cmt_apres_pb"] = ca, cb
c["baisse_cmt_pb"], c["et_baisse_cmt_pb"] = ca - cb, np.hypot(sa, sb)
c["baisse_own_pb"] = c["v_own_avant_pb"] - c["v_own_apres_pb"]
ea, sea = mse(A, "e"); eb, seb = mse(B, "e")
c["d_pb"], c["et_d_pb"] = eb - ea, np.hypot(sea, seb)
ha, sha = mse(A, "h"); hb, shb = mse(B, "h")
c["marge_moitie_pb"] = hb - ha      # 4.4 : moyenne de h après moins avant
c["et_marge_moitie_pb"] = np.hypot(sha, shb)
for nom, filtre in [("marge_moitie_sans_2023_pb", V.an != 2023), ("marge_moitie_sans_30_pb", V.ech != 30)]:
    W = V[filtre]
    c[nom] = W[W.per == "apres"].h.mean() - W[W.per == "avant"].h.mean()

print("calendrier pandas conforme pour P :", cal_ok)
print(f"{'champ':34s} {'controle':>14s} {'verification':>14s} {'diff':>10s}")
for k, x in c.items():
    print(f"{k:34s} {x:14.9f} {ver[k]:14.9f} {abs(x - ver[k]):10.2e}")
print("nb mois A, B :", A.mois.nunique(), B.mois.nunique(), " n :", len(A), len(B))
