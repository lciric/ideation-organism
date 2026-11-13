"""The estimators against statsmodels where possible, otherwise against hand computations."""
import math

import numpy as np
import pytest
import statsmodels.api as sm

from ifu import stats


@pytest.fixture
def panel():
    rng = np.random.default_rng(0)
    T, g = 40, 4
    t = np.repeat(np.arange(T), g)
    x = rng.normal(size=T * g) + np.repeat(rng.normal(size=T), g)
    y = 0.5 * x + rng.normal(size=T * g) + np.repeat(rng.normal(size=T), g)
    return t, x, y


def test_newey_west_matches_statsmodels_hac():
    rng = np.random.default_rng(3)
    x = rng.normal(size=120)
    y = 0.3 * x + np.convolve(rng.normal(size=122), [1, 0.6, 0.3], "valid")
    X = sm.add_constant(x)
    ref = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 4, "use_correction": False})
    beta, u, _ = stats.ols(X, y)
    V = stats.driscoll_kraay_cov(X, u, np.arange(120), 4)   # one observation per period = Newey-West
    assert np.allclose(beta, ref.params)
    assert np.allclose(np.sqrt(np.diag(V)), ref.bse)


def test_driscoll_kraay_matches_statsmodels_groupsum(panel):
    t, x, y = panel
    X = sm.add_constant(x)
    ref = sm.OLS(y, X).fit(cov_type="hac-groupsum", cov_kwds={"time": t, "maxlags": 3, "use_correction": False})
    _, u, _ = stats.ols(X, y)
    assert np.allclose(np.sqrt(np.diag(stats.driscoll_kraay_cov(X, u, t, 3))), ref.bse)


def test_lags_count_calendar_time_with_gaps():
    """Periods 0, 1, 3: lag 1 pairs only (0, 1); lag 2 pairs (1, 3); an absent period creates no pair."""
    s, t = np.array([1.0, 2.0, 4.0]), np.array([0, 1, 3])
    by_hand = (1 + 4 + 16) + 2 * (1 - 1 / 3) * (1 * 2) + 2 * (1 - 2 / 3) * (2 * 4)
    assert stats.bartlett_lrv(s, t, 2) == pytest.approx(by_hand)


def test_cluster_se_with_zero_lags(panel):
    t, x, y = panel
    X = sm.add_constant(x)
    ref = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": t, "use_correction": False})
    _, u, _ = stats.ols(X, y)
    assert np.allclose(np.sqrt(np.diag(stats.driscoll_kraay_cov(X, u, t, 0))), ref.bse)


def test_2sls_against_hand_computation(panel):
    t, x, y = panel
    rng = np.random.default_rng(5)
    z = x + rng.normal(size=len(x))
    e, xd, zd = y - y.mean(), x - x.mean(), z - z.mean()
    res = stats.iv_2sls(e, xd, zd, t, 2, t % 7)
    # just-identified 2SLS = cov(z, y) / cov(z, x); also = (Z'X)^-1 Z'y with a constant
    Z, Xm = sm.add_constant(z), sm.add_constant(x)
    beta = np.linalg.solve(Z.T @ Xm, Z.T @ y)
    assert res["b"] == pytest.approx(np.cov(z, y)[0, 1] / np.cov(z, x)[0, 1])
    assert res["b"] == pytest.approx(beta[1])
    # first stage = OLS of x on z; second stage on fitted values gives the same slope
    pi = np.sum(zd * xd) / np.sum(zd * zd)
    assert res["pi"] == pytest.approx(pi)
    assert np.sum(pi * zd * e) / np.sum((pi * zd) ** 2) == pytest.approx(res["b"])
    # DK se by hand: sandwich with the instrument
    u = e - res["b"] * xd
    meat = stats.bartlett_lrv(zd * u, t, 2)
    assert res["se"] == pytest.approx(math.sqrt(meat) / abs(np.sum(zd * xd)))
    # F of the first stage = squared robust t of pi
    _, se_pi, _ = stats.slope_dk(xd, zd, zd, t, 2)
    assert res["F"] == pytest.approx((pi / se_pi) ** 2)


def test_slope_dk_with_z_equal_x_is_ols_dk(panel):
    t, x, y = panel
    e, xd = y - y.mean(), x - x.mean()
    b, se, _ = stats.slope_dk(e, xd, xd, t, 3)
    X = sm.add_constant(x)
    ref = sm.OLS(y, X).fit(cov_type="hac-groupsum", cov_kwds={"time": t, "maxlags": 3, "use_correction": False})
    assert b == pytest.approx(ref.params[1])
    assert se == pytest.approx(ref.bse[1], rel=1e-9)


def test_block_statistic_example_of_the_h03v2_preregistration():
    """Two perfect blocks (8 and 9) and nine null blocks: t = 1.49 without the neighbour term, 1.13 with it."""
    R = {k: 0.0 for k in range(11)}
    R[8] = R[9] = 1.0
    rbar, se = stats.block_mean_se(R)
    g0 = sum((v - rbar) ** 2 for v in R.values()) / 10
    assert rbar / math.sqrt(g0 / 11) == pytest.approx(1.49, abs=0.005)
    assert rbar / se == pytest.approx(1.13, abs=0.005)


def test_uncentred_correlation():
    assert stats.uncentred_corr([1, 2], [2, 4]) == pytest.approx(1.0)
    assert stats.uncentred_corr([1, 1], [1, -1]) == pytest.approx(0.0)


def test_dm_hln_matches_formula():
    rng = np.random.default_rng(2)
    d = rng.normal(0.2, 1, size=30)
    n = len(d)
    dc = d - d.mean()
    V = (np.sum(dc * dc) / n + 2 * sum(np.sum(dc[j:] * dc[:-j]) / n for j in (1, 2, 3))) / n
    dm = d.mean() / math.sqrt(V) * math.sqrt((n + 1 - 8 + 12 / n) / n)
    from scipy import stats as sps
    assert stats.dm_hln_pvalue(d) == pytest.approx(sps.t.sf(dm, n - 1))
    assert stats.dm_hln_pvalue(d[:5]) == 1.0
