"""Statistics written from their formulas (no black boxes), cross-checked in tests/test_stats.py.

Conventions used by all four preregistrations:
- long-run variances use Bartlett weights 1 - j/(L+1) and no small-sample correction;
- lags are counted in calendar time: scores are first summed by period (quarter, survey round),
  and a period with no observation contributes zero, so it creates no pair.
"""
import math

import numpy as np
from scipy import stats as sps


def bartlett_lrv(scores, times, lags):
    """Long-run variance of `scores` summed by integer period `times`:
    Omega = sum_t H_t H_t' + sum_{j=1..L} (1 - j/(L+1)) sum_t (H_t H_{t-j}' + H_{t-j} H_t'),
    where H_t is the sum of the scores of period t (zero for a period with no observation).
    `scores` is (n,) -> returns a float, or (n, k) -> returns a k x k matrix.
    With lags = 0 and `times` = group labels this is the cluster-robust 'meat'."""
    s = np.asarray(scores, dtype=float)
    vector = s.ndim == 1
    if vector:
        s = s[:, None]
    t = np.asarray(times, dtype=int)
    H = np.zeros((t.max() - t.min() + 1, s.shape[1]))
    np.add.at(H, t - t.min(), s)
    omega = H.T @ H
    for j in range(1, lags + 1):
        G = H[j:].T @ H[:-j]
        omega += (1 - j / (lags + 1)) * (G + G.T)
    return float(omega[0, 0]) if vector else omega


def ols(X, y):
    """Least squares: returns (beta, residuals, (X'X)^-1)."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    xtx_inv = np.linalg.inv(X.T @ X)
    beta = xtx_inv @ X.T @ y
    return beta, y - X @ beta, xtx_inv


def driscoll_kraay_cov(X, resid, times, lags):
    """Driscoll-Kraay covariance (X'X)^-1 Omega (X'X)^-1, Omega = Bartlett LRV of the period sums of X_i u_i.
    When every period has one observation this is the Newey-West covariance."""
    X = np.asarray(X, dtype=float)
    xtx_inv = np.linalg.inv(X.T @ X)
    omega = bartlett_lrv(X * np.asarray(resid, dtype=float)[:, None], times, lags)
    return xtx_inv @ omega @ xtx_inv


def iid_cov(X, resid):
    """Classical OLS covariance s^2 (X'X)^-1 with s^2 = u'u / (n - p)."""
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    return (resid @ resid) / (n - p) * np.linalg.inv(X.T @ X)


def pearson(x, y):
    return float(np.corrcoef(x, y)[0, 1])


def slope_dk(e, x, z, times, lags):
    """Slope of e on x with one instrument z (z = x gives OLS), all three already demeaned.
    b = sum(z e) / sum(z x); the standard error is Driscoll-Kraay: sqrt(LRV of per-period sums of
    z * (e - b x)) / |sum(z x)|. Returns (b, se, period sums of the scores as used)."""
    e, x, z = (np.asarray(a, dtype=float) for a in (e, x, z))
    szx = np.sum(z * x)
    b = np.sum(z * e) / szx
    score = z * (e - b * x)
    se = math.sqrt(bartlett_lrv(score, times, lags)) / abs(szx)
    return b, se, score


def iv_2sls(e, x, z, times, lags, years):
    """Just-identified 2SLS of e on x with instrument z (all demeaned), the K01 statistic.
    Returns a dict: slope b, Driscoll-Kraay se, first-stage coefficient and F (DK), reduced-form t (DK),
    and descriptive cluster-robust se by period (lags 0) and by `years` (lags 0)."""
    e, x, z = (np.asarray(a, dtype=float) for a in (e, x, z))
    b, se, score = slope_dk(e, x, z, times, lags)
    pi, se_pi, _ = slope_dk(x, z, z, times, lags)          # first stage: x on z
    rho, se_rho, _ = slope_dk(e, z, z, times, lags)        # reduced form: e on z
    szx = abs(np.sum(z * x))
    return {"b": b, "se": se, "t": b / se, "pi": pi, "F": (pi / se_pi) ** 2, "t_rf": rho / se_rho,
            "se_cluster_period": math.sqrt(bartlett_lrv(score, times, 0)) / szx,
            "se_cluster_year": math.sqrt(bartlett_lrv(score, years, 0)) / szx,
            "szx": float(np.sum(z * x))}


def demean_by(values, groups):
    """values minus their mean within each group (the effect of one constant per group, by Frisch-Waugh-Lovell)."""
    v = np.asarray(values, dtype=float)
    g = np.asarray(groups)
    out = v.copy()
    for level in np.unique(g):
        m = g == level
        out[m] = v[m] - v[m].mean()
    return out


def residualise(values, dummies):
    """Residuals of an OLS regression of `values` on the columns of `dummies` (e.g. forecaster fixed effects)."""
    beta, *_ = np.linalg.lstsq(dummies, np.asarray(values, dtype=float), rcond=None)
    return np.asarray(values, dtype=float) - dummies @ beta


def uncentred_corr(c, e):
    """sum(c e) / sqrt(sum(c^2) sum(e^2)): a correlation without subtracting means (H03-v2, block statistic)."""
    c, e = np.asarray(c, dtype=float), np.asarray(e, dtype=float)
    return float(np.sum(c * e) / math.sqrt(np.sum(c * c) * np.sum(e * e)))


def block_mean_se(r_by_block):
    """Mean of block statistics R_k and its standard error with a neighbour-block correction (H03-v2, step 5):
    g0 = sum (R_k - Rbar)^2 / (K - 1); g1 = sum over consecutive valid blocks (k, k+1) of
    (R_k - Rbar)(R_k+1 - Rbar) / (K - 1); se = sqrt((g0 + 2 max(g1, 0)) / K)."""
    ks = sorted(r_by_block)
    K = len(ks)
    rbar = sum(r_by_block.values()) / K
    g0 = sum((r_by_block[k] - rbar) ** 2 for k in ks) / (K - 1)
    g1 = sum((r_by_block[k] - rbar) * (r_by_block[k + 1] - rbar) for k in ks if k + 1 in r_by_block) / (K - 1)
    return rbar, math.sqrt((g0 + 2 * max(g1, 0.0)) / K)


def dm_hln_pvalue(d, lags=3):
    """One-sided Diebold-Mariano test of mean(d) > 0 with the Harvey-Leybourne-Newbold correction
    (forecast horizon h = lags + 1). gamma_j = (1/n) sum (d_i - dbar)(d_{i-j} - dbar), V = (gamma_0 + 2 sum gamma_j)/n,
    DM* = DM sqrt((n + 1 - 2h + h(h-1)/n) / n), p = P(t_{n-1} > DM*). Returns 1 if n < 8 or V <= 0."""
    d = np.asarray(d, dtype=float)
    n = len(d)
    if n < 8:
        return 1.0
    dc = d - d.mean()
    gam = [np.sum(dc[j:] * dc[:n - j]) / n for j in range(lags + 1)]
    V = (gam[0] + 2 * sum(gam[1:])) / n
    if V <= 0:
        return 1.0
    h = lags + 1
    dm_star = d.mean() / math.sqrt(V) * math.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return float(sps.t.sf(dm_star, n - 1))


def moving_block_bootstrap_corr(r, e, block=8, draws=9999, seed=20261112):
    """Moving-block bootstrap of the Pearson correlation (J02, S2). Each draw takes ceil(n/block) block starts
    with rng.integers(0, n - block + 1), glues the blocks and truncates to n; a draw where r or e is constant
    is replaced by the next one. Returns the 5th and 95th percentiles (numpy linear method)."""
    r, e = np.asarray(r, dtype=float), np.asarray(e, dtype=float)
    n = len(r)
    rng = np.random.default_rng(seed)
    k = math.ceil(n / block)
    values = []
    while len(values) < draws:
        starts = rng.integers(0, n - block + 1, size=k)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        rb, eb = r[idx], e[idx]
        if np.all(rb == rb[0]) or np.all(eb == eb[0]):
            continue
        values.append(np.corrcoef(rb, eb)[0, 1])
    return float(np.percentile(values, 5)), float(np.percentile(values, 95))
