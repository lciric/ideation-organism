"""Sign conventions and definitions, on hand-made examples."""
import numpy as np
import pandas as pd
import pytest

from snu import measures


def test_error_is_outturn_minus_forecast():
    assert measures.forecast_error(3.0, 2.0) == 1.0      # forecast too low -> positive error
    assert measures.forecast_error(1.5, 2.0) == -0.5


def test_revision_is_new_minus_old():
    assert measures.forecast_revision(2.4, 2.0) == pytest.approx(0.4)   # revised up -> positive revision


def test_sticky_forecaster_gives_positive_slope():
    """A forecaster who moves only half way towards the truth under-reacts: positive error-revision slope."""
    rng = np.random.default_rng(1)
    news = rng.normal(size=500)
    old = np.zeros(500)
    new = old + 0.5 * news
    outturn = old + news
    error, revision = measures.forecast_error(outturn, new), measures.forecast_revision(new, old)
    assert np.corrcoef(revision, error)[0, 1] > 0.99


def test_quarter_numbers_of_the_preregistration():
    assert measures.quarter_number(1969, 4) == 7879
    assert measures.quarter_number(1982, 3) == 7930
    assert measures.quarter_number(2026, 3) == 8106
    assert measures.quarter_label(8079) == "2019-Q4"


def test_rtdsm_vintage_numbers():
    assert measures.rtdsm_vintage_number("P96Q2") == measures.quarter_number(1996, 2)
    assert measures.rtdsm_vintage_number("ROUTPUT26Q4") == measures.quarter_number(2026, 4)
    assert measures.rtdsm_vintage_number("P65Q4") == measures.quarter_number(1965, 4)


def test_annualised_growth():
    assert measures.annualised(101.0, 100.0) == pytest.approx(100 * (1.01 ** 4 - 1))
    # the preregistration's check on the first survey: (123.3253 / 122.000)^4 - 1 = 4.4166 %
    assert measures.annualised(123.3253, 122.0) == pytest.approx(4.4166, abs=5e-4)


def test_top_third_is_strict_and_uses_main_rows_only():
    df = pd.DataFrame({"variable": ["A"] * 4, "surprise": [1.0, -2.0, 3.0, 100.0], "main": [1, 1, 1, 0]})
    # quantile 2/3 of |1, 2, 3| = 2.333...: only 3 and 100 are above; the non-main row gets a class too
    assert list(measures.top_third(df, "surprise")) == [0.0, 0.0, 1.0, 1.0]
    df = pd.DataFrame({"variable": ["A"] * 4, "surprise": [1.0, 2.0, 3.0, 2.0], "main": 1})
    # quantile 2/3 of |1, 2, 2, 3| = 2 exactly: a value equal to the cut is not large
    assert list(measures.top_third(df, "surprise")) == [0.0, 0.0, 1.0, 0.0]
