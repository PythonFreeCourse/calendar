import calendar
from datetime import date, datetime, timedelta
import itertools
import locale
from typing import Dict, Iterator, List, Tuple

import pytz

MONTH_BLOCK: int = 6

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")


class Day:
    """A Day class.

    Args:
        date    (datetime): A single datetime date.
    Arguments:
        date    (datetime): A single datetime date.
        sday         (str): The day name.
        dailyevents (List): List of tuples represent daily event information.
                            EX:  [("Front Info", "Back Info")]
        events      (List): List of tuples represent time event name.
                            EX: [("09AP", "Meeting with yam")]
        css         (Dict): All css classes represent day.
    """

    def __init__(self, date: datetime):
        self.date: datetime = date
        self.sday: str = self.date.strftime("%A")
        self.dailyevents: List[Tuple] = []
        self.events: List[Tuple] = []
        self.css: Dict[str, str] = {
            'day_container': 'day',
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily',
                'front',
                'background-warmyellow'
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray'
            ]),
            'event': 'event',
        }

    def __str__(self) -> str:
        return self.date.strftime("%d")

    def display(self) -> str:
        """Returns day date inf the format of 00 MONTH 00"""
        return self.date.strftime("%d %B %y").upper()

    def set_id(self) -> str:
        """Returns day date inf the format of 00-month-0000"""
        return self.date.strftime("%d-%B-%Y")

    @classmethod
    def get_user_local_time(cls) -> datetime:
        greenwich = pytz.timezone('GB')
        return greenwich.localize(datetime.now())

    @classmethod
    def convert_str_to_date(cls, date_string: str) -> datetime:
        return datetime.strptime(date_string, '%d-%B-%Y')

    @classmethod
    def is_weekend(cls, date: date) -> bool:
        """Returns true if this day is represent a weekend."""
        return date.strftime("%A") in Week.DAYS_OF_THE_WEEK[-2:]


class DayWeekend(Day):
    def __init__(self, date: datetime):
        super().__init__(date)
        self.css = {
            'day_container': 'day ',
            'date': ' '.join(['day-number', 'text-gray']),
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily',
                'front',
                'background-warmyellow'
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray'
            ]),
            'event': 'event',
        }


class Today(Day):
    def __init__(self, date: datetime):
        super().__init__(date)
        self.css = {
            'day_container': ' '.join([
                'day',
                'text-darkblue',
                'background-yellow'
            ]),
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily',
                'front',
                'text-lightgray',
                'background-darkblue'
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray'
            ]),
            'event': 'event',
        }


class FirstDayMonth(Day):
    def __init__(self, date: datetime):
        super().__init__(date)
        self.css = {
            'day_container': ' '.join([
                'day',
                'text-darkblue',
                'background-lightgray'
            ]),
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front': ' '.join([
                'daily front',
                'text-lightgray',
                'background-red'
            ]),
            'daily_event_back': ' '.join([
                'daily',
                'back',
                'text-darkblue',
                'background-lightgray'
            ]),
            'event': 'event',
        }

    def __str__(self) -> str:
        return self.date.strftime("%d %b %y").upper()


class Week:
    WEEK_DAYS: int = 7
    DAYS_OF_THE_WEEK: List[str] = calendar.day_name

    def __init__(self, days: List[Day]):
        self.days: List[Day] = days


def create_day(day: datetime) -> Day:
    """Return the currect day object according to given date."""
    if day == date.today():
        return Today(day)
    if int(day.day) == 1:
        return FirstDayMonth(day)
    if Day.is_weekend(day):
        return DayWeekend(day)
    return Day(day)


def get_next_date(date: datetime) -> Iterator[Day]:
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
    return list(calendar.Calendar().itermonthdates(date.year, date.month))[0]


def get_n_days(date: datetime, n: int) -> Iterator[Day]:
    """Generate n dates from a starting given date."""
    next_date_gen = get_next_date(date)
    yield from itertools.islice(next_date_gen, n)


def create_weeks(
        days: Iterator[Day],
        length: int = Week.WEEK_DAYS
) -> List[Week]:
    """Return lists of Weeks objects."""
    ndays: List[Day] = list(days)
    num_days: int = len(ndays)
    return [Week(ndays[i:i + length]) for i in range(0, num_days, length)]


def get_month_block(day: Day, n: int = MONTH_BLOCK) -> List[Week]:
    """Returns a 2D list represent a n days calendar from current month."""
    current = get_first_day_month_block(day.date) - timedelta(days=1)
    num_of_days = Week.WEEK_DAYS * n
    return create_weeks(get_n_days(current, num_of_days))
