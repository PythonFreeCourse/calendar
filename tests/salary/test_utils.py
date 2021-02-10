from datetime import datetime, time, timedelta
from typing import Dict, List, Tuple
from unittest import mock

import pytest
from requests.sessions import Session

from app.database.models import Event, SalarySettings
from app.routers.salary import config, utils

NIGHT_TIMES = [
    (datetime(2020, 1, 15), False,
     (datetime.combine(datetime(2020, 1, 15), config.NIGHT_START),
      datetime.combine(datetime(2020, 1, 16), config.NIGHT_END))),
    (datetime(2020, 1, 15), True,
     (datetime.combine(datetime(2020, 1, 14), config.NIGHT_START),
      datetime.combine(datetime(2020, 1, 15), config.NIGHT_END)))
]

NIGHT_SHIFTS = [
    # Invalid shift
    (datetime(2020, 12, 1, 23, 15), datetime(2020, 12, 1, 5, 15), False),
    # Not during night
    (datetime(2020, 12, 1, 9, 15), datetime(2020, 12, 1, 18, 15), False),
    # Too short - evening
    (datetime(2020, 12, 1, 20, 15), datetime(2020, 12, 1, 23, 15), False),
    # Too short - morning
    (datetime(2020, 12, 1, 5, 15), datetime(2020, 12, 1, 6, 15), False),
    # Same Date
    (datetime(2020, 12, 1, 3, 15), datetime(2020, 12, 1, 7, 15), True),
    # Date changing
    (datetime(2020, 12, 1, 19, 15), datetime(2020, 12, 2, 1, 15), True),
    # Entire night
    (datetime(2020, 12, 1, 19, 15), datetime(2020, 12, 2, 7, 15), True)
]

HOLIDAY_TIMES = [
    (datetime(2020, 1, 3, 15), datetime(2020, 1, 4, 1),  # Friday - Saturday
     (datetime(2020, 1, 4), datetime(2020, 1, 5))),
    (datetime(2020, 1, 4, 15), datetime(2020, 1, 5, 1),  # Saturday - Sunday
     (datetime(2020, 1, 4), datetime(2020, 1, 5))),
    (datetime(2020, 1, 5, 15), datetime(2020, 1, 6, 1),  # Sunday - Monday
     (datetime.min, datetime.min)),
]

SYNC_TIMES = [
    (datetime(2020, 1, 3, 15), datetime(2020, 1, 3, 22),
     datetime(2020, 1, 3, 18, 30), datetime(2020, 1, 4, 2), 3.5),
    (datetime(2020, 1, 3, 15), datetime(2020, 1, 3, 22),
     datetime(2020, 1, 4, 15), datetime(2020, 1, 4, 22), 0.0),
]

HOUR_BASIS = [
    (datetime(2021, 1, 4, 9), datetime(2021, 1, 4, 19),  # Regular shift
     config.REGULAR_HOUR_BASIS),
    (datetime(2021, 1, 4, 18), datetime(2021, 1, 5, 4),  # Night shift
     config.NIGHT_HOUR_BASIS),
]

OVERTIMES = [
    # Short shift
    (datetime(2021, 1, 4, 9), datetime(2021, 1, 4, 14), (5, 0)),
    # Regular shift
    (datetime(2021, 1, 4, 9), datetime(2021, 1, 4, 19), (10.5, 2)),
    # Short night shift
    (datetime(2021, 1, 5, 1), datetime(2021, 1, 5, 6), (5, 0)),
    # Night shift
    (datetime(2021, 1, 4, 18), datetime(2021, 1, 5, 4), (11, 3)),
]

HOLIDAY_HOURS = [
    (datetime(2020, 1, 3, 15), datetime(2020, 1, 4, 1), 1.0),
    (datetime(2020, 1, 4, 15, 30), datetime(2020, 1, 5, 1), 8.5),
    (datetime(2020, 1, 5, 15), datetime(2020, 1, 6, 1), 0.0),
]

HOLIDAY_OVERTIMES = [
    # Short shift
    (datetime(2021, 1, 4, 9), datetime(2021, 1, 4, 14), (5, 0)),
    # Regular shift
    (datetime(2021, 1, 4, 9), datetime(2021, 1, 4, 19), (10.5, 2)),
    # Short night shift
    (datetime(2021, 1, 5, 1), datetime(2021, 1, 5, 6), (5, 0)),
    # Night shift
    (datetime(2021, 1, 4, 18), datetime(2021, 1, 5, 4), (11, 3)),
    # Short off-day shift
    (datetime(2021, 1, 2, 9), datetime(2021, 1, 2, 14), (7.5, 0)),
    # Off-day shift
    (datetime(2021, 1, 2, 9), datetime(2021, 1, 2, 19), (15.5, 2)),
    # Night off-day shift
    (datetime(2021, 1, 2, 14), datetime(2021, 1, 3, 0), (16, 3))
]

SHIFTS = [
    # Regular shift
    (datetime(2021, 1, 4, 9), datetime(2021, 1, 4, 19), 315),
    # Night shift
    (datetime(2021, 1, 4, 18), datetime(2021, 1, 5, 4), 330),
    # Off-day shift
    (datetime(2021, 1, 2, 9), datetime(2021, 1, 2, 19), 465),
    # Night off-day shift
    (datetime(2021, 1, 2, 14), datetime(2021, 1, 3, 0), 480),
]

WEEK_SHIFTS = [
    ((Event(start=datetime(2021, 1, 10, 9),
            end=datetime(2021, 1, 10, 19)),), 0.0),
    ((Event(start=datetime(2021, 1, 10, 9),
            end=datetime(2021, 1, 10, 19)),
      Event(start=datetime(2021, 1, 11, 9),
            end=datetime(2021, 1, 11, 17)),
      Event(start=datetime(2021, 1, 12, 9),
            end=datetime(2021, 1, 12, 17)),
      Event(start=datetime(2021, 1, 13, 9),
            end=datetime(2021, 1, 13, 18)),
      Event(start=datetime(2021, 1, 14, 9),
            end=datetime(2021, 1, 14, 17))), 0.0),
    ((Event(start=datetime(2021, 1, 10, 9),
            end=datetime(2021, 1, 10, 19)),
      Event(start=datetime(2021, 1, 11, 9),
            end=datetime(2021, 1, 11, 17)),
      Event(start=datetime(2021, 1, 12, 9),
            end=datetime(2021, 1, 12, 17)),
      Event(start=datetime(2021, 1, 13, 9),
            end=datetime(2021, 1, 13, 18)),
      Event(start=datetime(2021, 1, 14, 9),
            end=datetime(2021, 1, 14, 17)),
      Event(start=datetime(2021, 1, 15, 9),
            end=datetime(2021, 1, 15, 14, 58))), 119.0),
]

MONTHS = [
    (2020, 1, (datetime(2020, 1, 1), datetime(2020, 2, 1))),
    (2020, 12, (datetime(2020, 12, 1), datetime(2021, 1, 1))),
]

MONTH_SHIFTS = [
    (False, 0.0),
    (True, 720.0)
]

TRANSPORT = [
    (6, 11.8, 70.8),
    (0, 11.8, 0.0),
    (21, 0, 0.0),
]

SALARIES = [
    (False, 0, {
        'year': 2021,
        'month': 1,
        'num_of_shifts': 20,
        'base_salary': 4800.0,
        'month_weekly_overtime': 0,
        'transport': 236,
        'bonus': 0,
        'deduction': 0,
        'salary': 5036.0,
    }),
    (True, 10000, {
        'year': 2021,
        'month': 1,
        'num_of_shifts': 20,
        'base_salary': 4800.0,
        'month_weekly_overtime': 0,
        'transport': 236,
        'bonus': 0,
        'deduction': 5036.0,
        'salary': 0.0,
    }),
]

TIMES = [
    ('13:30', time(13, 30)),
    ('15:42:00', time(15, 42))
]

UPDATES = [
    ({
         'wage': '35',
         'off_day': '6',
         'holiday_category_id': '7',
         'regular_hour_basis': '19',
         'night_hour_basis': '6.5',
         'night_start': '13:00',
         'night_end': '14:30:00',
         'night_min_len': '20:42',
         'first_overtime_amount': '4',
         'first_overtime_pay': '1',
         'second_overtime_pay': '2',
         'week_working_hours': '80',
         'daily_transport': '20',
     }, True),
    ({}, False)
]


def create_month_shifts(start: datetime, end: datetime,
                        add_sixth_day: bool = False) -> List[Event]:
    shifts = []
    for i in range(4):
        for j in range(6):
            if j < 5 or add_sixth_day:
                shifts.append(Event(
                    start=start + timedelta(i) * 7 + timedelta(j),
                    end=end + timedelta(i) * 7 + timedelta(j)))
    return shifts


def get_event_by_category(*args, **kwargs) -> List[Event]:
    # Code revision required after categories feature is added
    start = datetime(2021, 1, 3, 9)
    end = datetime(2021, 1, 3, 17)
    return create_month_shifts(start, end)


def test_get_shift_len() -> None:
    start = datetime(2020, 1, 1, 1)
    end = start + timedelta(hours=1)
    assert utils.get_shift_len(start, end) == 1
    end += timedelta(minutes=12)
    assert utils.get_shift_len(start, end) == 1.2


@pytest.mark.parametrize('date, prev_day, night_times', NIGHT_TIMES)
def test_get_night_times(wage: SalarySettings, date: datetime, prev_day: bool,
                         night_times: Tuple[datetime, datetime]) -> None:
    assert utils.get_night_times(date, wage, prev_day) == night_times


@pytest.mark.parametrize('start, end, boolean', NIGHT_SHIFTS)
def test_is_night_shift(wage: SalarySettings, start: datetime, end: datetime,
                        boolean: bool) -> None:
    assert utils.is_night_shift(start, end, wage) == boolean


@pytest.mark.parametrize('start, end, dates',
                         HOLIDAY_TIMES)
def test_get_relevant_holiday_times(
        wage: SalarySettings, start: datetime, end: datetime,
        dates: Tuple[datetime, datetime]) -> None:
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    assert utils.get_relevant_holiday_times(
        start, end, wage) == dates


@pytest.mark.parametrize(
    'event_1_start, event_1_end, event_2_start, event_2_end, total',
    SYNC_TIMES)
def test_get_total_synchronous_hours(event_1_start: datetime,
                                     event_1_end: datetime,
                                     event_2_start: datetime,
                                     event_2_end: datetime,
                                     total: float) -> None:
    assert utils.get_total_synchronous_hours(
        event_1_start, event_1_end, event_2_start, event_2_end) == total


@pytest.mark.parametrize('start, end, basis', HOUR_BASIS)
def test_get_hour_basis(wage: SalarySettings, start: datetime,
                        end: datetime, basis: float) -> None:
    assert utils.get_hour_basis(start, end, wage) == basis


@pytest.mark.parametrize('start, end, overtimes', OVERTIMES)
def test_calc_overtime_hours(
        wage: SalarySettings, start: datetime, end: datetime,
        overtimes: Tuple[float, float]) -> None:
    assert utils.calc_overtime_hours(start, end, wage) == overtimes


@pytest.mark.parametrize('shift_start, shift_end, total', HOLIDAY_HOURS)
def test_get_hours_during_holiday(wage: SalarySettings, shift_start: datetime,
                                  shift_end: datetime, total: float) -> None:
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    assert utils.get_hours_during_holiday(
        shift_start, shift_end, wage) == total


@pytest.mark.parametrize('start, end, overtimes', HOLIDAY_OVERTIMES)
def test_adjust_overtime(wage: SalarySettings, start: datetime, end: datetime,
                         overtimes: Tuple[float, float]) -> None:
    assert utils.adjust_overtime(start, end, wage) == overtimes


@pytest.mark.parametrize('start, end, salary', SHIFTS)
def test_calc_shift_salary(wage: SalarySettings, start: datetime,
                           end: datetime, salary: float) -> None:
    assert utils.calc_shift_salary(start, end, wage) == salary


@pytest.mark.parametrize('shifts, overtime', WEEK_SHIFTS)
def test_calc_weekly_overtime(wage: SalarySettings, shifts: Tuple[Event, ...],
                              overtime: float) -> None:
    assert utils.calc_weekly_overtime(shifts, wage) == overtime


def test_get_event_by_category() -> None:
    # Code revision required after categories feature is added
    shifts = (
        Event(start=datetime(2021, 1, 10, 9),
              end=datetime(2021, 1, 10, 19)),
        Event(start=datetime(2021, 1, 11, 9),
              end=datetime(2021, 1, 11, 17)),
        Event(start=datetime(2021, 1, 12, 9),
              end=datetime(2021, 1, 12, 17)),
        Event(start=datetime(2021, 1, 13, 9),
              end=datetime(2021, 1, 13, 18)),
        Event(start=datetime(2021, 1, 14, 9),
              end=datetime(2021, 1, 14, 17)),
        Event(start=datetime(2021, 1, 15, 9),
              end=datetime(2021, 1, 15, 14, 58)),
    )
    events = utils.get_event_by_category()
    assert len(events) == len(shifts)
    for i, event in enumerate(events):
        assert event.start == shifts[i].start and event.end == shifts[i].end


@pytest.mark.parametrize('year, month, month_times', MONTHS)
def test_get_month_end(year: int, month: int,
                       month_times: Tuple[datetime, datetime]) -> None:
    assert utils.get_month_times(year, month) == month_times


def test_get_relevant_weeks() -> None:
    weeks = [
        (datetime(2020, 12, 27), datetime(2021, 1, 3)),
        (datetime(2021, 1, 3), datetime(2021, 1, 10)),
        (datetime(2021, 1, 10), datetime(2021, 1, 17)),
        (datetime(2021, 1, 17), datetime(2021, 1, 24)),
        (datetime(2021, 1, 24), datetime(2021, 1, 31)),
    ]
    relevant_weeks = utils.get_relevant_weeks(2021, 1)
    for week in weeks:
        assert week == next(relevant_weeks)


@pytest.mark.parametrize('add_sixth_day, total', MONTH_SHIFTS)
def test_get_monthly_overtime(wage: SalarySettings, add_sixth_day: bool,
                              total: float) -> None:
    start = datetime(2021, 1, 3, 9)
    end = datetime(2021, 1, 3, 17)
    shifts = create_month_shifts(start, end, add_sixth_day)
    weeks = utils.get_relevant_weeks(start.year, start.month)
    assert utils.get_monthly_overtime(shifts, weeks, wage) == total


@pytest.mark.parametrize('amount, daily_transport, total', TRANSPORT)
def test_calc_transport(amount: int, daily_transport: float,
                        total: float) -> None:
    assert utils.calc_transport(amount, daily_transport) == total


@pytest.mark.parametrize('overtime, deduction, salary', SALARIES)
@mock.patch('app.routers.salary.utils.get_event_by_category',
            side_effect=get_event_by_category)
def test_calc_salary(
        mocked_func, wage: SalarySettings, overtime: bool,
        deduction: config.NUMERIC, salary: Dict[str, config.NUMERIC]) -> None:
    # Code revision required after categories feature is added
    assert utils.calc_salary(2021, 1, wage, overtime, 0, deduction) == salary


def test_get_settings(salary_session: Session,
                      wage: SalarySettings) -> None:
    assert utils.get_settings(salary_session, wage.user_id,
                              wage.category_id)


@pytest.mark.parametrize('string, formatted_time', TIMES)
def test_get_time_from_string(string: str, formatted_time: time) -> None:
    assert utils.get_time_from_string(string) == formatted_time


@pytest.mark.parametrize('form, boolean', UPDATES)
def test_update_settings(salary_session: Session, wage: SalarySettings,
                         form: Dict[str, str], boolean: bool) -> None:
    assert utils.update_settings(salary_session, wage, form) == boolean
