"""Bond arithmetic: coupon dates, accrued interest, yield from price, GSW curve pricing.

Conventions are those written in sections 5.2 of the J05 and K11 preregistrations:
- coupon dates T_k = maturity moved back 6k months, same day of month (last day of the
  month if that day does not exist), no business-day adjustment;
- accrued interest AI(d) = (c/2) (d - L) / (N - L), L = last T_k <= d, N = first T_k > d;
- yield Y(P, d): the y solving  P + AI(d) = sum_j F_j (1 + y/200)^-[(j-1) + (N-d)/(N-L)].

The preregistrations attribute that formula to 31 CFR 356, Appendix B. The exact Treasury
formula discounts the fractional first period with *simple* interest,
1 / (1 + w y/200); it is available with treasury_exact=True and is used only in a
labelled descriptive variant (it reproduces the auction high price to 1e-7).
"""
import calendar
import math
from datetime import date

from scipy.optimize import brentq


def months_back(d, n):
    """Date n months before d, same day of month (or the month's last day)."""
    total = d.year * 12 + (d.month - 1) - n
    y, m = divmod(total, 12)
    m += 1
    return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def coupon_schedule(maturity, settle):
    """Return (L, N, coupon dates strictly after settle in increasing order)."""
    future, k = [], 0
    while True:
        t = months_back(maturity, 6 * k)
        if t <= settle:
            future.reverse()
            return t, future[0], future
        future.append(t)
        k += 1


def accrued_interest(coupon, maturity, settle):
    """Accrued interest per 100 of face value (coupon in percent per year)."""
    last, nxt, _ = coupon_schedule(maturity, settle)
    return coupon / 2 * (settle - last).days / (nxt - last).days


def dirty_price(y, coupon, maturity, settle, treasury_exact=False):
    """Price plus accrued interest for yield y (percent, semiannual)."""
    last, nxt, future = coupon_schedule(maturity, settle)
    w = (nxt - settle).days / (nxt - last).days
    v = 1 / (1 + y / 200)
    n = len(future)
    total = 0.0
    for j in range(1, n + 1):
        flow = coupon / 2 + (100 if j == n else 0)
        total += flow * v ** ((j - 1) + (0 if treasury_exact else w))
    if treasury_exact:
        total /= 1 + w * y / 200
    return total


def yield_from_price(price, coupon, maturity, settle, treasury_exact=False, solver="brent"):
    """Yield (percent) of a clean price for settlement `settle`; solved to 1e-12 percentage point.

    solver="bisect" gives an independent second computation used to check the first."""
    target = price + accrued_interest(coupon, maturity, settle)

    def gap(y):
        return dirty_price(y, coupon, maturity, settle, treasury_exact) - target

    if solver == "brent":
        return brentq(gap, -20.0, 60.0, xtol=1e-12, rtol=1e-15, maxiter=500)
    lo, hi = -20.0, 60.0  # gap is decreasing in y
    while hi - lo > 1e-12:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if gap(mid) > 0 else (lo, mid)
    return (lo + hi) / 2


# ----------------------------------------------------------------------------- GSW curve
def gsw_zero(m, beta0, beta1, beta2, beta3, tau1, tau2):
    """Svensson zero-coupon yield (percent, continuously compounded) at maturity m years."""
    a1, a2 = m / tau1, m / tau2
    e1, e2 = math.exp(-a1), math.exp(-a2)
    f1, f2 = (1 - e1) / a1, (1 - e2) / a2
    return beta0 + beta1 * f1 + beta2 * (f1 - e1) + beta3 * (f2 - e2)


def gsw_discount(m, params):
    """Discount factor exp(-z(m) m / 100)."""
    return math.exp(-gsw_zero(m, *params) * m / 100)


def gsw_par_yield(n_years, params):
    """Coupon-equivalent par yield (percent) of an n-year semiannual bond on the GSW curve."""
    annuity = sum(gsw_discount(k / 2, params) for k in range(1, 2 * n_years + 1))
    return 200 * (1 - gsw_discount(n_years, params)) / annuity


def _years(later, earlier):
    return (later - earlier).days / 365.25


def gsw_yield(coupon, maturity, curve_date, params, settle=None, treasury_exact=False):
    """Yield of a bond valued on the GSW curve of `curve_date`.

    settle=None: spot value at curve_date (J05's g(x)).
    settle=s:    forward value for settlement s, flows after s discounted to s (J05's g_terme(J))."""
    s = curve_date if settle is None else settle
    _, _, future = coupon_schedule(maturity, s)
    full = sum((coupon / 2 + (100 if t == maturity else 0)) * gsw_discount(_years(t, curve_date), params)
               for t in future)
    if settle is not None:
        full /= gsw_discount(_years(settle, curve_date), params)
    return yield_from_price(full - accrued_interest(coupon, maturity, s), coupon, maturity, s, treasury_exact)
