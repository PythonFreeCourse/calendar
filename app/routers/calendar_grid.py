import calendar
import itertools
import locale
from datetime import date, datetime, timedelta
from typing import Any, Generator, Iterator, List

CALENDAR = calendar.Calendar(0)
DISPLAY_BLOCK = 100
MONTH_BLOCK = 5
LAST_SHOWED_DAY = None

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
            ("00AM", "event 01"),
            ("00PM", "event 02")
        ]
        self.css = {
            'div': 'day',
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

    @classmethod
    def is_weekend(cls, date: datetime) -> bool:
        """Returns true if this day is represent a weekend."""
        return date.strftime("%A") in Week.DAYS_OF_THE_WEEK[-2:]


class DayWeekend(Day):
    def __init__(self, date: datetime):
        super().__init__(date)
        self.css = {
            'div': 'day ',
            'date': ' '.join(['day-number',  'text-gray']),
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
            'div':  ' '.join(['day', 'text-darkblue', 'background-yellow']),
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
            'div': ' '.join([
                'day',
                'text-darkblue',
                'background-lightgray'
            ]),
            'date': 'day-number',
            'daily_event': 'month-event',
            'daily_event_front':  ' '.join([
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


def create_day(day: datetime) -> Day:
    """Return the currect day object according to given date."""
    if day == date.today():
        return Today(day)
    if Day.is_weekend(day):
        return DayWeekend(day)
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


def get_month_block(day: Day, n: int = MONTH_BLOCK * 2) -> List[List[Day]]:
    """Returns a 2D list represent a n days calendar from current month."""
    current = get_first_day_month_block(day.date) - timedelta(days=1)
    block = []
    for i in range(n):
        week = list(get_n_days(current, Week.WEEK_DAYS))
        block.append(week)
        current = week[-1].date
    LAST_SHOWED_DAY = block[-1][-1].date
    return block
