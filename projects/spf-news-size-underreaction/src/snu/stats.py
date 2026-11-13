"""Least squares and Driscoll-Kraay standard errors, written from their formulas (checked against
statsmodels in tests/test_stats.py).

Conventions of the preregistration (section 6, step 4):
- long-run variances use Bartlett weights 1 - j/(L+1) and no small-sample correction;
- lags are counted in calendar time: scores are first summed by period (target quarter), and a quarter
  with no observation contributes zero, so it creates no pair.
"""
import math

import numpy as np


def bartlett_lrv(scores, times, lags):
    """Long-run variance of `scores` summed by integer period `times`:
    Omega = sum_t H_t H_t' + sum_{j=1..L} (1 - j/(L+1)) sum_t (H_t H_{t-j}' + H_{t-j} H_t'),
    where H_t is the sum of the scores of period t (zero for a period with no observation).
    `scores` is (n,) -> returns a float, or (n, k) -> returns a k x k matrix.
    With lags = 0 this is the cluster-robust 'meat' (clusters = periods)."""
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
    """Driscoll-Kraay covariance (X'X)^-1 Omega (X'X)^-1, Omega = Bartlett long-run variance of the
    per-period sums of X_i u_i. With one observation per period this is the Newey-West covariance."""
    X = np.asarray(X, dtype=float)
    xtx_inv = np.linalg.inv(X.T @ X)
    omega = bartlett_lrv(X * np.asarray(resid, dtype=float)[:, None], times, lags)
    return xtx_inv @ omega @ xtx_inv


def iid_cov(X, resid):
    """Classical OLS covariance s^2 (X'X)^-1 with s^2 = u'u / (n - p)."""
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    return (resid @ resid) / (n - p) * np.linalg.inv(X.T @ X)


def combination(beta, V, w):
    """Estimate and standard error of the linear combination w'beta, given covariance V."""
    w = np.asarray(w, dtype=float)
    return float(w @ beta), math.sqrt(float(w @ V @ w))
