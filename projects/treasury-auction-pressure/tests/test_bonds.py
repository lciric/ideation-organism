"""Yield-from-price conventions and GSW curve pricing."""
from datetime import date

import pytest

from tap import bonds

# 30-year reopening auctioned 2026-10-08 (CUSIP 912810UW6), from the Fiscal Data auction API:
COUPON, MATURITY, SETTLE = 5.125, date(2056, 8, 15), date(2026, 10, 15)
HIGH_YIELD, HIGH_PRICE, API_ACCRUED = 5.6180, 92.889131, 8.49524 / 10

# GSW parameters and published yields for 2016-09-12 (feds200628.csv); the published yields
# are rounded to four decimals (stored as single-precision floats), hence a 5e-5 tolerance.
GSW = [4.5824987658003, -3.92183425410548, -3.06033964583972, -5.73179297732097, 1.92879499337454, 9.59284179558308]
SVENY = {2: 0.800700008869171, 10: 1.72169995307922, 30: 2.63240003585815}
SVENPY = {10: 1.70220005512238, 30: 2.47359991073608}


def test_coupon_schedule_and_accrued_interest():
    last, nxt, future = bonds.coupon_schedule(MATURITY, SETTLE)
    assert (last, nxt) == (date(2026, 8, 15), date(2027, 2, 15))
    assert len(future) == 60 and future[-1] == MATURITY
    assert bonds.accrued_interest(COUPON, MATURITY, SETTLE) == pytest.approx(API_ACCRUED, abs=1e-6)


def test_treasury_exact_formula_reproduces_auction_price():
    full = bonds.dirty_price(HIGH_YIELD, COUPON, MATURITY, SETTLE, treasury_exact=True)
    assert full - bonds.accrued_interest(COUPON, MATURITY, SETTLE) == pytest.approx(HIGH_PRICE, abs=1e-6)
    assert bonds.yield_from_price(HIGH_PRICE, COUPON, MATURITY, SETTLE, treasury_exact=True) == \
        pytest.approx(HIGH_YIELD, abs=1e-6)


def test_preregistered_formula_is_within_tolerance():
    # The preregistrations compound the fractional first period; the gap to the Treasury's
    # simple-interest formula stays under the 0.001 point tolerance (convention_ok).
    y = bonds.yield_from_price(HIGH_PRICE, COUPON, MATURITY, SETTLE)
    assert 0 < y - HIGH_YIELD < 0.001


def test_brent_and_bisection_agree():
    a = bonds.yield_from_price(101.71875, 2.375, date(2049, 11, 15), date(2021, 3, 4))
    b = bonds.yield_from_price(101.71875, 2.375, date(2049, 11, 15), date(2021, 3, 4), solver="bisect")
    assert abs(a - b) < 1e-10


def test_price_at_par_yield_is_par_on_coupon_date():
    assert bonds.yield_from_price(100.0, 4.0, date(2036, 5, 15), date(2026, 5, 15)) == pytest.approx(4.0, abs=1e-10)


@pytest.mark.parametrize("m", [2, 10, 30])
def test_gsw_zero_yield_matches_sveny(m):
    assert bonds.gsw_zero(m, *GSW) == pytest.approx(SVENY[m], abs=5e-5)


@pytest.mark.parametrize("m", [10, 30])
def test_gsw_par_yield_matches_svenpy(m):
    assert bonds.gsw_par_yield(m, GSW) == pytest.approx(SVENPY[m], abs=5e-5)


def test_gsw_bond_priced_on_coupon_date_has_par_yield():
    # A bond settling on a coupon date whose coupon equals the curve's par yield is worth ~100
    c = bonds.gsw_par_yield(10, GSW)
    y = bonds.gsw_yield(c, date(2026, 9, 12), date(2016, 9, 12), GSW)
    assert y == pytest.approx(c, abs=0.01)
