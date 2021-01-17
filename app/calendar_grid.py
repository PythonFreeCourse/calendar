import calendar
import datetime
from typing import List, Tuple

DAYS_OF_THE_WEEK: List[str] = ['Monday', 'Tuesday', 'Wednesday',
                               'Thursday', 'Friday', 'Saturday', 'Sunday']


def get_date_as_string(date: datetime) -> str:
    return date.strftime("%A %B %b %Y").split()


def get_next_date(date):
    """Generate date objects from a starting given date."""
    while True:
        next_day = date + datetime.timedelta(days=1)
        yield next_day
        date = next_day


def get_day_n_before(date: datetime, n: int) -> datetime:
    return date - datetime.timedelta(days=n)


def get_n_days(date: datetime, n: int) -> List[datetime]:
    g = get_next_date(date)
    days = []
    for day in range(n):
        days.append(next(g))
    return days


def arrange_weeks(dates: List, n: int) -> List[List]:
    """Returns a list of lists with length of n for a given list"""
    weeks = []
    week = []
    for day in dates:
        if len(week) > 0 and len(week) % n - 1 == 0:
            week.append(day)
            weeks.append(week)
            week = []
        else:
            week.append(day)
    return weeks


def get_month_block(date) -> List[List]:
    days = calendar.monthrange(date.year, date.month)
    before = get_day_n_before(date, days[0] + 1)
    cal = get_n_days(before, 1000)
    return arrange_weeks(cal, 7)
