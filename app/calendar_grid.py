from calendar import monthrange
from typing import Tuple
from datetime import datetime

DAYS_OF_THE_WEEK = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday']


def get_day_name(date: datetime) -> Tuple[str, int]:
    """Returns the name of a day for a given date and its numeric value"""
    day = date.weekday()
    return DAYS_OF_THE_WEEK[day], day


def get_month_days(year: int, month: int) -> Tuple[int, int]:
    """Returns the first and last day in a given month and year."""
    return monthrange(year, month)
