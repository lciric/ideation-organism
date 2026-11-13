"""The estimators against statsmodels where possible, otherwise against hand computations."""
import numpy as np
import pytest
import statsmodels.api as sm

from snu import stats


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
    ref = sm.OLS(y, X).fit(cov_type="hac-groupsum", cov_kwds={"time": t, "maxlags": 4, "use_correction": False})
    _, u, _ = stats.ols(X, y)
    assert np.allclose(np.sqrt(np.diag(stats.driscoll_kraay_cov(X, u, t, 4))), ref.bse)


def test_lags_count_calendar_time_with_gaps():
    """Periods 0, 1, 3: lag 1 pairs only (0, 1); lag 2 pairs (1, 3); an absent period creates no pair
    (the preregistration's reason for not using statsmodels, which counts lags by position)."""
    s, t = np.array([1.0, 2.0, 4.0]), np.array([0, 1, 3])
    by_hand = (1 + 4 + 16) + 2 * (1 - 1 / 3) * (1 * 2) + 2 * (1 - 2 / 3) * (2 * 4)
    assert stats.bartlett_lrv(s, t, 2) == pytest.approx(by_hand)


def test_cluster_se_with_zero_lags(panel):
    t, x, y = panel
    X = sm.add_constant(x)
    ref = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": t, "use_correction": False})
    _, u, _ = stats.ols(X, y)
    assert np.allclose(np.sqrt(np.diag(stats.driscoll_kraay_cov(X, u, t, 0))), ref.bse)


def test_iid_covariance_matches_statsmodels(panel):
    t, x, y = panel
    X = sm.add_constant(x)
    ref = sm.OLS(y, X).fit()
    _, u, _ = stats.ols(X, y)
    assert np.allclose(np.sqrt(np.diag(stats.iid_cov(X, u))), ref.bse)


def test_linear_combination():
    beta, V = np.array([1.0, 2.0]), np.array([[1.0, 0.5], [0.5, 4.0]])
    est, se = stats.combination(beta, V, [1, 1])
    assert est == 3.0 and se == pytest.approx(np.sqrt(1 + 4 + 2 * 0.5))
