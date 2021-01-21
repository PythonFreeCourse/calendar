import calendar
import itertools
import locale
from datetime import date, datetime, timedelta
from typing import Any, Generator, Iterator, List

CALENDAR = calendar.Calendar(0)
DISPLAY_BLOCK = 100

locale.setlocale(locale.LC_TIME, ("en", "UTF-8"))


class Week:
    WEEK_DAYS = 7
    DAYS_OF_THE_WEEK = calendar.day_name


class Day:
    def __init__(self, date: datetime):
        self.date = date
        self.sday = self.date.strftime("%A")
        self.dailyevents = [("Daily Event", "More Information")]
        self.events = [
            ("6PM", "Meeting with Ode"),
            ("7PM", "Meeting with Sagi")
        ]
        self.css = {
            'div': 'day',
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': 'daily front bg-warmyellow',
            'daily_event_back': 'daily back t-darkblue bg-lightgray',
            'event': 'event',
        }

    def __str__(self) -> str:
        return self.date.strftime("%d")

    def display(self) -> str:
        """Returns day date inf the format of 00 MONTH 00"""
        return self.date.strftime("%d %B %y").upper()

    @classmethod
    def is_weekend(cls, date: datetime) -> bool:
        """Returns true if this day is represent a weekend."""
        return date.strftime("%A") in Week.DAYS_OF_THE_WEEK[-2:]


class DayWeekend(Day):
    def __init__(self, date: datetime):
        super().__init__(date)
        self.css = {
            'div': 'day ',
            'date': 'day-number t-gray',
            'daily_event': 'month-event',
            'daily_event_front': 'daily front bg-warmyellow',
            'daily_event_back': 'daily back t-darkblue bg-lightgray',
            'event': 'event',
        }


class Today(Day):
    def __init__(self, date: datetime):
        super().__init__(date)
        self.css = {
            'div': 'day t-darkblue bg-yellow',
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': 'daily front t-lightgray bg-darkblue',
            'daily_event_back': 'daily back t-darkblue bg-lightgray',
            'event': 'event',
        }


class FirstDayMonth(Day):
    def __init__(self, date: datetime):
        super().__init__(date)
        self.css = {
            'div': 'day t-darkblue bg-lightgray',
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': 'daily front t-lightgray bg-red',
            'daily_event_back': 'daily back t-darkblue bg-lightgray',
            'event': 'event',
        }

    def __str__(self) -> str:
        return self.date.strftime("%d %b %y").upper()


def create_day(day: datetime) -> Day:
    """Return the currect day object according to given date."""
    if Day.is_weekend(day):
        return DayWeekend(day)
    if day == date.today():
        return Today(day)
    if int(day.day) == 1:
        return FirstDayMonth(day)
    return Day(day)


def get_next_date(date: datetime) -> Generator[Day, None, None]:
    """Generate date objects from a starting given date."""
    yield from (
        create_day(date + timedelta(days=i))
        for i in itertools.count(start=1)
    )


def get_date_before_n_days(date: datetime, n: int) -> datetime:
    """Returns the date before n days."""
    return date - timedelta(days=n)


def get_first_day_month_block(date: datetime) -> datetime:
    """Returns the first date in a month block of given date."""
    return list(CALENDAR.itermonthdates(date.year, date.month))[0]


def get_n_days(date: datetime, n: int) -> Iterator[Day]:
    """Generate n dates from a starting given date."""
    next_date_gen = get_next_date(date)
    yield from itertools.islice(next_date_gen, n)


def split_list_to_lists(dates: List[Any], length: int) -> List[List[Any]]:
    """Return a 2D list with inner lists length of given size."""
    return [dates[i:i + length] for i in range(0, len(dates), length)]


def get_month_block(date: datetime, n: int = DISPLAY_BLOCK) -> List[List[Day]]:
    """Returns a 2D list represent a n days calendar from current month."""
    start = create_day(get_first_day_month_block(date))
    cal = list(get_n_days(start.date, n))
    cal.insert(0, start)
    return split_list_to_lists(cal, Week.WEEK_DAYS)
