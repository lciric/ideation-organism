"""Month-clustered standard errors written from the formula, checked against statsmodels."""
import math

import numpy as np
import pytest
import statsmodels.api as sm

from tap.stats import cluster_mean, ols_cluster

RNG = np.random.default_rng(0)
N, G = 200, 40
CLUSTERS = RNG.integers(0, G, N)
X = np.column_stack([RNG.integers(0, 2, N), np.ones(N)])
Y = 0.5 * X[:, 0] + RNG.normal(size=N) + RNG.normal(size=G)[CLUSTERS]


def statsmodels_se(y, x, groups):
    """statsmodels without its small-sample correction, times sqrt(G/(G-1)) (the preregistered factor)."""
    fit = sm.OLS(y, x).fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": False})
    g = len(np.unique(groups))
    return np.sqrt(np.diag(fit.cov_params()) * g / (g - 1)), fit.params


def test_ols_cluster_matches_statsmodels():
    b, V = ols_cluster(Y, X, CLUSTERS)
    se_sm, b_sm = statsmodels_se(Y, X, CLUSTERS)
    assert np.allclose(b, b_sm)
    assert np.allclose(np.sqrt(np.diag(V)), se_sm, rtol=1e-10)


def test_cluster_mean_matches_statsmodels_constant_regression():
    m = cluster_mean(Y, CLUSTERS)
    se_sm, b_sm = statsmodels_se(Y, np.ones((N, 1)), CLUSTERS)
    assert m["mean"] == pytest.approx(b_sm[0])
    assert m["se"] == pytest.approx(se_sm[0], rel=1e-10)
    assert (m["n"], m["g"]) == (N, len(np.unique(CLUSTERS)))


def test_cluster_mean_formula_by_hand():
    v, months = [1.0, 2.0, 3.0, 6.0], ["a", "a", "b", "c"]
    # mean 3; S_a = -3, S_b = 0, S_c = 3; SE = (1/4) sqrt(3/2 * 18)
    assert cluster_mean(v, months)["se"] == pytest.approx(math.sqrt(1.5 * 18) / 4)
