import calendar
import itertools
from datetime import datetime, timedelta

from typing import Any, Iterator, Generator, List, Tuple

DAYS_OF_THE_WEEK: List[str] = ['Monday', 'Tuesday', 'Wednesday',
                               'Thursday', 'Friday', 'Saturday', 'Sunday']
CALENDAR = calendar.Calendar(0)


def get_date_as_string(date: datetime) -> List[str]:
    """Returns list represent date as string."""
    return date.strftime("%A %B %b %Y").split()


def get_next_date(date: datetime) -> Generator[datetime, None, None]:
    """Generate date objects from a starting given date."""
    yield from (date + timedelta(days=i) for i in itertools.count(start=1))


def get_date_before_n_days(date: datetime, n: int) -> datetime:
    """Returns the date before n days."""
    return date - timedelta(days=n)


def get_first_day_month_block(date):
    return list(CALENDAR.itermonthdates(date.year, date.month))[0]


def get_n_days(date: datetime, n: int) -> Iterator[datetime]:
    """Generate n dates from a starting given date."""
    next_date_gen = get_next_date(date)
    yield from itertools.islice(next_date_gen, n)


def split_list_to_lists(dates: List[Any], length: int) -> List[List[Any]]:
    """Return a 2D list with inner lists length of given size."""
    return [dates[i:i + length] for i in range(0, len(dates), length)]


def get_month_block(date: datetime, n: int = 100) -> List[List]:
    """Returns a 2D list represent a n days calendar from current month."""
    start = get_first_day_month_block(date)
    cal = list(get_n_days(start, n))
    cal.insert(0, start)
    return split_list_to_lists(cal, 7)
