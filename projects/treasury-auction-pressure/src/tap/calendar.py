"""Trading-day calendars and the J-5 / J+5 shifts.

Each test fixes its own calendar C (a sorted list of dates); "J + k" is always the date
k ranks away from J in C, never k calendar days:
- F04 and F04-bis: the dates where FRED's DGS10 has a value;
- J05: the dates where the GSW file has all six curve parameters;
- K11: U.S. federal business days (5 U.S.C. 6103, weekend rule, Juneteenth from 2021)
  minus two days without a FedInvest table (2012-10-30, 2018-12-05).
"""
from datetime import date, timedelta


def _nth_weekday(year, month, weekday, n):
    """n-th given weekday (Monday = 0) of a month."""
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def _last_weekday(year, month, weekday):
    d = date(year + month // 12, month % 12 + 1, 1) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def _observed(d):
    """A holiday on Saturday is observed on Friday, on Sunday the next Monday."""
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def federal_holidays(year):
    """Observed U.S. federal holidays whose observed date falls in `year`."""
    days = set()
    for y in (year, year + 1):  # Jan 1 of year+1 can be observed on Dec 31 of year
        days |= {
            _observed(date(y, 1, 1)),
            _nth_weekday(y, 1, 0, 3),      # Martin Luther King Jr. Day
            _nth_weekday(y, 2, 0, 3),      # Washington's Birthday
            _last_weekday(y, 5, 0),        # Memorial Day
            _observed(date(y, 7, 4)),
            _nth_weekday(y, 9, 0, 1),      # Labor Day
            _nth_weekday(y, 10, 0, 2),     # Columbus Day
            _observed(date(y, 11, 11)),
            _nth_weekday(y, 11, 3, 4),     # Thanksgiving
            _observed(date(y, 12, 25)),
        }
        if y >= 2021:
            days.add(_observed(date(y, 6, 19)))  # Juneteenth
    return {d for d in days if d.year == year}


def federal_business_days(start, end, extra_closed=()):
    """Monday-Friday dates in [start, end] that are not federal holidays nor in extra_closed."""
    closed = set(extra_closed)
    for y in range(start.year, end.year + 1):
        closed |= federal_holidays(y)
    days, d = [], start
    while d <= end:
        if d.weekday() < 5 and d not in closed:
            days.append(d)
        d += timedelta(days=1)
    return days


FEDINVEST_CLOSED = (date(2012, 10, 30), date(2018, 12, 5))  # verified empty FedInvest tables


def k11_calendar():
    """Calendar C of K11 (section 4.3 of its preregistration)."""
    return federal_business_days(date(2009, 6, 1), date(2026, 12, 31), FEDINVEST_CLOSED)


class Calendar:
    """A sorted list of dates with rank arithmetic: cal.shift(d, k) is d + k ranks."""

    def __init__(self, dates):
        self.dates = sorted(dates)
        self.rank = {d: i for i, d in enumerate(self.dates)}

    def __contains__(self, d):
        return d in self.rank

    def shift(self, d, k):
        """Date k ranks after d (k < 0: before); None if d is not in the calendar or out of range."""
        if d not in self.rank:
            return None
        i = self.rank[d] + k
        return self.dates[i] if 0 <= i < len(self.dates) else None
