"""Means and OLS with standard errors clustered by month, written from the formula.

For a mean (regression on a constant) the preregistered standard error is
    SE = (1/N) * sqrt( G/(G-1) * sum_g S_g^2 ),   S_g = sum_{i in g} (x_i - mean),
and for OLS the sandwich
    V = G/(G-1) (X'X)^-1 [ sum_g (X_g' u_g)(X_g' u_g)' ] (X'X)^-1,
with no other small-sample factor (in particular no (N-1)/(N-K)).
"""
import math

import numpy as np
import pandas as pd


def cluster_mean(values, clusters):
    """Return dict(mean, se, n, g) for the mean of `values` with month-clustered SE."""
    x = np.asarray(values, dtype=float)
    groups = np.asarray(clusters)
    n = len(x)
    mean = x.mean()
    sums = pd.Series(x - mean).groupby(groups).sum().to_numpy()
    g = len(sums)
    se = math.sqrt(g / (g - 1) * float(np.sum(sums ** 2))) / n
    return {"mean": float(mean), "se": se, "n": n, "g": g}


def ols_cluster(y, X, clusters):
    """OLS of y on X (no constant added). Return (coefficients, clustered covariance matrix)."""
    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    groups = np.asarray(clusters)
    bread = np.linalg.inv(X.T @ X)
    b = bread @ X.T @ y
    u = y - X @ b
    meat = np.zeros((X.shape[1], X.shape[1]))
    labels = pd.unique(groups)
    for label in labels:
        score = X[groups == label].T @ u[groups == label]
        meat += np.outer(score, score)
    g = len(labels)
    return b, g / (g - 1) * bread @ meat @ bread


def interval(estimate, se, z):
    """Symmetric interval estimate -/+ z * se."""
    return estimate - z * se, estimate + z * se


def by_group(values, groups, clusters, z=1.96):
    """Clustered mean of `values` within each group (e.g. year): DataFrame with mean, se, n, low, high."""
    rows = []
    frame = pd.DataFrame({"v": np.asarray(values, dtype=float), "grp": np.asarray(groups),
                          "cl": np.asarray(clusters)})
    for label, sub in frame.groupby("grp"):
        m = cluster_mean(sub.v, sub.cl)
        rows.append({"group": label, "mean": m["mean"], "se": m["se"], "n": m["n"],
                     "low": m["mean"] - z * m["se"], "high": m["mean"] + z * m["se"]})
    return pd.DataFrame(rows)
