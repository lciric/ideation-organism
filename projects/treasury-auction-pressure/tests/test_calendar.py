"""Holiday-aware J-5 / J+5 windows on the federal business-day calendar (K11's calendar C)."""
from datetime import date

import pytest

from tap.calendar import Calendar, federal_holidays, k11_calendar

CAL = Calendar(k11_calendar())


@pytest.mark.parametrize("auction, minus5", [
    (date(2016, 9, 12), date(2016, 9, 2)),   # Monday after Labor Day 2016-09-05
    (date(2021, 7, 12), date(2021, 7, 2)),   # Monday after July 4th observed on 2021-07-05
    (date(2022, 9, 12), date(2022, 9, 2)),   # Monday after Labor Day 2022-09-05
])
def test_monday_after_monday_holiday_is_ten_calendar_days(auction, minus5):
    assert CAL.shift(auction, -5) == minus5
    assert (auction - minus5).days == 10


def test_ordinary_week_is_seven_days():
    assert CAL.shift(date(2023, 3, 8), -5) == date(2023, 3, 1)
    assert CAL.shift(date(2023, 3, 8), 5) == date(2023, 3, 15)


def test_fedinvest_closed_day_is_skipped():
    # 2018-12-05 (national day of mourning) has no FedInvest table: J-5 of 2018-12-12 is 12-04
    assert CAL.shift(date(2018, 12, 12), -5) == date(2018, 12, 4)


def test_christmas_eve_stays_open():
    assert CAL.shift(date(2024, 12, 17), 5) == date(2024, 12, 24)


def test_observed_holidays():
    h2021 = federal_holidays(2021)
    assert date(2021, 6, 18) in h2021      # Juneteenth (Saturday) observed Friday
    assert date(2021, 12, 31) in h2021     # New Year 2022 (Saturday) observed Friday 2021-12-31
    assert date(2021, 7, 5) in h2021       # July 4th (Sunday) observed Monday
    assert not any(d.month == 6 and d.day in (18, 19, 20) for d in federal_holidays(2020))  # no Juneteenth before 2021


def test_holiday_is_not_in_calendar():
    assert date(2016, 9, 5) not in CAL and CAL.shift(date(2016, 9, 5), -5) is None
