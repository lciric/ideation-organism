"""Sign conventions of errors and revisions, on hand-made examples."""
import numpy as np
import pandas as pd
import pytest

from ifu import measures, stats
from ifu import vintages as vt


def test_error_is_outturn_minus_forecast():
    assert measures.forecast_error(3.0, 2.0) == 1.0      # forecast too low -> positive error
    assert measures.forecast_error(1.5, 2.0) == -0.5


def test_revision_is_new_minus_old():
    assert measures.forecast_revision(2.4, 2.0) == pytest.approx(0.4)   # revised up -> positive revision


def test_sticky_forecaster_gives_positive_slope():
    """A forecaster who moves only half way towards the truth under-reacts: positive error-revision slope."""
    rng = np.random.default_rng(1)
    truth_news = rng.normal(size=500)
    old = np.zeros(500)
    new = old + 0.5 * truth_news           # revises by half the news
    outturn = old + truth_news             # the news fully materialises
    error, revision = measures.forecast_error(outturn, new), measures.forecast_revision(new, old)
    assert stats.pearson(revision, error) > 0.99


def test_realtime_outturn_reads_status_A_two_quarters_later_then_falls_back():
    def series(rows):
        return pd.DataFrame(rows, columns=["t", "value", "status"])
    q = 8084
    vintages = {q + 2: series([(q, np.nan, "A")]),         # value missing two quarters later
                q + 3: series([(q, 1.7, "A")]),
                q + 4: series([(q, 1.8, "A")])}
    assert vt.realtime_outturn(q, vintages) == (1.7, q + 3)
    vintages[q + 3] = series([(q, 1.7, "F")])               # a projected value is never an outturn
    assert vt.realtime_outturn(q, vintages) == (1.8, q + 4)


def test_j02_outturn_formula_on_a_hand_example():
    # index rises 3% on the same months a year earlier -> 3% year-on-year
    now, before = np.array([103.0, 103.0, 103.0]), np.array([100.0, 100.0, 100.0])
    assert 100 * (now.sum() / before.sum() - 1) == pytest.approx(3.0)
    assert measures.annualised(101.0, 100.0) == pytest.approx(100 * (1.01 ** 4 - 1))
