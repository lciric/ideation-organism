"""M01 - fonctions communes de l'experimentateur : calendrier C (4.3), population (4.5), conventions 6.2.
Importe par telecharger.py et construire.py (jamais par analyse.py, qui a son propre code de rendement)."""
import json, bisect, datetime as dt, calendar as _cal, math, os
from scipy.optimize import brentq

DATE = dt.date

# ---------------------------------------------------------------- calendrier C (4.3)
def _nth_weekday(y, m, wd, n):
    d = DATE(y, m, 1)
    d += dt.timedelta((wd - d.weekday()) % 7)
    return d + dt.timedelta(7 * (n - 1))

def _last_weekday(y, m, wd):
    d = DATE(y, m, _cal.monthrange(y, m)[1])
    return d - dt.timedelta((d.weekday() - wd) % 7)

def feries_observes(y0=2009, y1=2027):
    out = set()
    for y in range(y0, y1 + 1):
        nominaux = [DATE(y, 1, 1), _nth_weekday(y, 1, 0, 3), _nth_weekday(y, 2, 0, 3), _last_weekday(y, 5, 0),
                    DATE(y, 7, 4), _nth_weekday(y, 9, 0, 1), _nth_weekday(y, 10, 0, 2), DATE(y, 11, 11),
                    _nth_weekday(y, 11, 3, 4), DATE(y, 12, 25)]
        if y >= 2021:
            nominaux.append(DATE(y, 6, 19))
        for d in nominaux:
            if d.weekday() == 5:
                d -= dt.timedelta(1)
            elif d.weekday() == 6:
                d += dt.timedelta(1)
            out.add(d)
    return out

SANS_TABLEAU = {DATE(2012, 10, 30), DATE(2018, 12, 5)}

def calendrier_C():
    f = feries_observes()
    d, fin, L = DATE(2009, 6, 1), DATE(2026, 12, 31), []
    while d <= fin:
        if d.weekday() < 5 and d not in f and d not in SANS_TABLEAU:
            L.append(d)
        d += dt.timedelta(1)
    return L

C = calendrier_C()
RANG = {d: i for i, d in enumerate(C)}

# ---------------------------------------------------------------- D1 et population (4.5)
def iso(s):
    return DATE.fromisoformat(s)

def charger_d1(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)["data"]

def premieres(d1):
    """cusip -> ligne nominale reopening = No (la premiere adjudication)."""
    p = {}
    for r in d1:
        if r["reopening"] == "No":
            p.setdefault(r["cusip"], []).append(r)
    return p

PREFIXES = (("9-Year", 10), ("19-Year", 20), ("29-Year", 30))

def echeance_de(terme):
    for pre, e in PREFIXES:
        if terme.startswith(pre):
            return e
    return None

def population(d1):
    pop = []
    for r in d1:
        if r["inflation_index_security"] == "Yes" or r["floating_rate"] == "Yes":
            continue
        if r["reopening"] != "Yes":
            continue
        if not ("2010-01-01" <= r["auction_date"] <= "2026-10-31"):
            continue
        if echeance_de(r["security_term"]) is None:
            continue
        pop.append(r)
    pop.sort(key=lambda r: (r["auction_date"], echeance_de(r["security_term"])))
    return pop

def fenetre(j):
    """(J-5, J+5) au rang dans C."""
    k = RANG[j]
    return C[k - 5], C[k + 5]

# ---------------------------------------------------------------- conventions 6.2
def _recul_mois(m, n):
    y, mo = m.year, m.month - n
    while mo <= 0:
        mo += 12
        y -= 1
    return DATE(y, mo, min(m.day, _cal.monthrange(y, mo)[1]))

def dates_coupon(M, d):
    """T_k > d (croissant), L = dernier T_k <= d, N = premier T_k > d."""
    T, k = [], 0
    while True:
        t = _recul_mois(M, 6 * k)
        T.append(t)
        if t <= d:
            break
        k += 1
    L = T[-1]
    apres = sorted(t for t in T if t > d)
    return apres, L, apres[0]

def intcouru(c, M, d):
    apres, L, N = dates_coupon(M, d)
    return (c / 2) * (d - L).days / (N - L).days

def rendement(P, c, M, d):
    """Y(P, d) en pour cent, P pied de coupon."""
    apres, L, N = dates_coupon(M, d)
    n = len(apres)
    w = (N - d).days / (N - L).days
    cible = P + (c / 2) * (d - L).days / (N - L).days
    F = [c / 2] * n
    F[-1] += 100.0
    def f(y):
        q = 1 + y / 200
        return sum(F[j] * q ** -(j + w) for j in range(n)) - cible
    return brentq(f, -90.0, 200.0, xtol=1e-13, rtol=1e-15, maxiter=500)

def z_gsw(m, b0, b1, b2, b3, t1, t2):
    a1 = (1 - math.exp(-m / t1)) / (m / t1)
    a2 = (1 - math.exp(-m / t2)) / (m / t2)
    return b0 + b1 * a1 + b2 * (a1 - math.exp(-m / t1)) + b3 * (a2 - math.exp(-m / t2))

def prix_plein_gsw(c, M, x, par):
    apres, L, N = dates_coupon(M, x)
    tot = 0.0
    for t in apres:
        flux = c / 2 + (100.0 if t == M else 0.0)
        m = (t - x).days / 365.25
        tot += flux * math.exp(-z_gsw(m, *par) * m / 100)
    return tot

def rendement_gsw(c, M, x, par):
    P = prix_plein_gsw(c, M, x, par) - intcouru(c, M, x)
    return rendement(P, c, M, x)
