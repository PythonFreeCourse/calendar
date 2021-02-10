from datetime import datetime, time, timedelta
from typing import Dict, Iterator, Optional, Tuple

from sqlalchemy.orm.session import Session

from app.database.models import Event, SalarySettings
from app.internal.utils import save
from app.routers.salary import config

DEFAULT_SETTINGS = SalarySettings(
    wage=config.MINIMUM_WAGE,
    off_day=config.SATURDAY,
    holiday_category_id=config.ISRAELI_JEWISH,
    regular_hour_basis=config.REGULAR_HOUR_BASIS,
    night_hour_basis=config.NIGHT_HOUR_BASIS,
    night_start=config.NIGHT_START,
    night_end=config.NIGHT_END,
    night_min_len=config.NIGHT_MIN_LEN,
    first_overtime_amount=config.FIRST_OVERTIME_AMOUNT,
    first_overtime_pay=config.FIRST_OVERTIME_PAY,
    second_overtime_pay=config.SECOND_OVERTIME_PAY,
    week_working_hours=config.WEEK_WORKING_HOURS,
    daily_transport=config.STANDARD_TRANSPORT,
)


def get_shift_len(start: datetime, end: datetime) -> float:
    """Returns the total shift length in hours.
    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.

    Returns:
        float: Total shift length in hours.

    Raises:
        None
    """
    return (end - start).seconds / config.HOURS_SECONDS_RATIO


def get_night_times(date: datetime, wage: SalarySettings,
                    prev_day: bool = False) -> Tuple[datetime, datetime]:
    """Returns the start and end times of night for the given date.

    Args:
        date (datetime): The date to return night times for.
        wage (SalarySettings): The relevant salary calculation settings.
        prev_day (bool): If True, returned night times will start on the
                         previous date, and end on the given date.

    Returns:
        tuple(datetime, datetime): The start and end times of night for the
                                   given date.

    Raises:
        None
    """
    sub = timedelta(1 if prev_day else 0)
    return (datetime.combine(date - sub, wage.night_start),
            datetime.combine(date + timedelta(1) - sub, wage.night_end))


def is_night_shift(start: datetime, end: datetime,
                   wage: SalarySettings) -> bool:
    """Returns True if shift is a night shift, False otherwise.

    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.
        wage (SalarySettings): The relevant salary calculation settings.

    Raises:
        None
    """
    if start >= end:
        return False
    if not (datetime.min + (end - start)).time() >= wage.night_min_len:
        return False
    for boolean in (False, True):
        night_start, night_end = get_night_times(start, wage, boolean)
        if (get_total_synchronous_hours(start, end, night_start, night_end)
                >= wage.first_overtime_amount):
            return True
    return False


def get_relevant_holiday_times(
        start: datetime, end: datetime, wage: SalarySettings
) -> Tuple[datetime, datetime]:
    """Returns start and end of holiday times that synchronize with the given
    times, based on the the supplied salary settings.

    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        tuple(datetime, datetime): The start and end times of synchronous
                                   holidays.

    Raises:
        None
    """
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    # if wage.off_day == SATURDAY:
    #     for event_start, event_end in get_shabbat_times(start, end):
    #         if events_synchronize(start, end, event_start, event_end):
    #             return event_start, event_end
    # else:
    #     for event_start, event_end in get_holidays(start, end,
    #                                                wage.holiday_category_id):
    #         if events_synchronize(start, end, event_start, event_end):
    #             return event_start, event_end
    if start.weekday() == wage.off_day:
        date = start.date()
    elif end.weekday() == wage.off_day:
        date = end.date()
    try:
        return (datetime.combine(date, time(0)),
                datetime.combine(date + timedelta(1),
                                 time(0)))
    except NameError:
        return datetime.min, datetime.min


def get_total_synchronous_hours(
        event_1_start: datetime, event_1_end: datetime,
        event_2_start: datetime, event_2_end: datetime
) -> float:
    """Returns the total amount of hours that are shared between both events.

    Args:
        event_1_start (datetime): The first event's start time.
        event_1_end (datetime): The first event's end time.
        event_2_start (datetime): The second event's start time.
        event_2_end (datetime): The second event's end time.

    Returns:
        float: Total amount of hours that are shared between both events.

    Raises:
        None
    """
    latest_start = max(event_1_start, event_2_start)
    earliest_end = min(event_1_end, event_2_end)
    if latest_start > earliest_end:
        return 0.0
    return (earliest_end - latest_start).seconds / config.HOURS_SECONDS_RATIO


def get_hour_basis(start: datetime, end: datetime,
                   wage: SalarySettings) -> float:
    """Returns the shift's base hours, not qualifying for overtime.

    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        float: Shift's hour basis.

    Raises:
        None
    """
    if is_night_shift(start, end, wage):
        return wage.night_hour_basis
    return wage.regular_hour_basis


def calc_overtime_hours(start: datetime, end: datetime,
                        wage: SalarySettings) -> Tuple[float, float]:
    """Returns a tuple of the total hours of the shift adjusted for overtime,
    and the total overtime hours.

    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        tuple(float, float): The adjusted total hours of the shift and the
                             overtime hours.

    Raises:
        None
    """
    shift_len = get_shift_len(start, end)
    hour_basis = get_hour_basis(start, end, wage)
    if shift_len <= hour_basis:
        return shift_len, 0.0
    overtime = shift_len - hour_basis
    temp = hour_basis
    if overtime <= wage.first_overtime_amount:
        return temp + overtime * wage.first_overtime_pay, overtime
    return temp + ((overtime - wage.first_overtime_amount)
                   * wage.second_overtime_pay
                   + wage.first_overtime_amount
                   * wage.first_overtime_pay), overtime


def get_hours_during_holiday(start: datetime, end: datetime,
                             wage: SalarySettings) -> float:
    """Returns the total amount of hours of the shifts that are synchronous
    with an holiday.

    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        float: Total amount of hours of the shifts that are synchronous
               with an holiday.

    Raises:
        None
    """
    holiday_start, holiday_end = get_relevant_holiday_times(
        start, end, wage)
    return get_total_synchronous_hours(start, end, holiday_start, holiday_end)


def adjust_overtime(start: datetime, end: datetime,
                    wage: SalarySettings) -> Tuple[float, float]:
    """Returns a tuple of the total hours of the shift adjusted for overtime
    and holidays, and the total overtime hours.

    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        tuple(float, float): The adjusted total hours of the shift and the
                             overtime hours.

    Raises:
        None
    """
    total_hours, overtime = calc_overtime_hours(start, end, wage)
    total_hours += get_hours_during_holiday(start, end, wage) / 2

    return (total_hours, overtime)


def calc_shift_salary(start: datetime, end: datetime,
                      wage: SalarySettings) -> float:
    """Returns the total salary for the given shift, including overtime.

    Args:
        start (datetime): The shift's start time.
        end (datetime): The shift's end time.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        The total salary for the given shift, including overtime.

    Raises:
        None
    """
    return round(adjust_overtime(start, end, wage)[0] * wage.wage, 2)


def calc_weekly_overtime(shifts: Tuple[Event, ...],
                         wage: SalarySettings) -> float:
    """Returns the weekly overtime amount for the supplied shifts.

    Weekly overtime is calculated only for hours exceeding the standard week
    working hours that have not been previously calculated as hourly overtime
    for the individual shifts.

    Args:
        shifts (tuple(Event, ...)): The relevant shifts to calculate weekly
                                    overtime for.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        float: The weekly overtime amount for the supplied shifts.

    Raises:
        None
    """
    total_week_hours = sum(get_shift_len(shift.start, shift.end)
                           for shift in shifts)
    if total_week_hours <= wage.week_working_hours:
        return 0.0
    total_daily_overtime = sum(map(lambda shift: adjust_overtime(
        shift.start, shift.end, wage)[1], shifts))
    overtime = (total_week_hours
                - wage.week_working_hours
                - total_daily_overtime)
    if overtime > 0:
        return round(overtime * wage.wage, 2)
    return 0.0


def get_event_by_category(*args, **kwargs):
    """Mock function for event by category search."""
    # Code revision required after categories feature is added
    day_1 = Event(start=datetime(2021, 1, 10, 9),
                  end=datetime(2021, 1, 10, 19))
    day_2 = Event(start=datetime(2021, 1, 11, 9),
                  end=datetime(2021, 1, 11, 17))
    day_3 = Event(start=datetime(2021, 1, 12, 9),
                  end=datetime(2021, 1, 12, 17))
    day_4 = Event(start=datetime(2021, 1, 13, 9),
                  end=datetime(2021, 1, 13, 18))
    day_5 = Event(start=datetime(2021, 1, 14, 9),
                  end=datetime(2021, 1, 14, 17))
    day_6 = Event(start=datetime(2021, 1, 15, 9),
                  end=datetime(2021, 1, 15, 14, 58))

    return (day_1, day_2, day_3, day_4, day_5, day_6)


def get_month_times(year: int, month: int) -> Tuple[datetime, datetime]:
    """Returns the start and end dates for the given year and month.

    Args:
        year (int): The relevant year.
        month (int): The relevant month.

    Returns:
        tuple(datetime, datetime): The start and end dates for the given year
                                   and month.
    Raises:
        ValueError: If  year is smaller than 1 or larger than 9999, or if month
                    is smaller than 1 or larger than 12.
    """
    month_start = datetime(year, month, 1)
    try:
        month_end = datetime(year, month + 1, 1)
    except ValueError:
        month_end = datetime(year + 1, 1, 1)
    return month_start, month_end


def get_relevant_weeks(year: int,
                       month: int) -> Iterator[Tuple[datetime, datetime]]:
    """Yields start and end times of each relevant week for the given year and
    month.

    Args:
        year (int): The relevant year.
        month (int): The relevant month.

    Yields:
        tuple(datetime, datetime): Start and end times of each relevant week
        for the given year and month.

    raises:
        ValueError: If  year is smaller than 1 or larger than 9999, or if month
                    is smaller than 1 or larger than 12.
    """
    month_start, month_end = get_month_times(year, month)
    week_start = month_start - timedelta(month_start.weekday() + 1)
    week_end = week_start + timedelta(7)
    while week_end <= month_end:
        yield week_start, week_end
        week_start = week_end
        week_end += timedelta(7)


def get_monthly_overtime(
        shifts: Tuple[Event, ...],
        weeks: Iterator[Tuple[datetime, datetime]],
        wage: SalarySettings
) -> float:
    """Returns the sum of all weekly overtime for the supplied shifts based on
    the provided weeks.

    Args:
        shifts (tuple(Event, ...)): The relevant shifts to calculate weekly
                                    overtime for.
        weeks (iterator(tuple(datetime, datetime))): Start and end times of
                                                     relevant weeks.
        wage (SalarySettings): The relevant salary calculation settings.

    Returns:
        float: Sum of all weekly overtime for the supplied shifts based on the
               provided weeks.

    Raises:
        None
    """
    monthly_overtime = []
    for week_start, week_end in weeks:
        weekly_shifts = tuple(shift for shift in shifts
                              if week_start <= shift.start <= week_end)
        monthly_overtime.append(calc_weekly_overtime(weekly_shifts, wage))
    return sum(monthly_overtime)


def calc_transport(shifts_amount: int, daily_transport: float) -> float:
    """Returns total monthly transportation refund.

    Args:
        shifts_amount (int): Total of number of monthly shifts.
        daily_transport (float): Refund amount per shift.

    Returns:
        float: Total monthly transportation refund.

    Raises:
        None
    """
    return round(daily_transport * shifts_amount, 2)


def calc_salary(
        year: int, month: int, wage: SalarySettings, overtime: bool,
        bonus: config.NUMERIC = 0, deduction: config.NUMERIC = 0,
) -> Dict[str, config.NUMERIC]:
    """Returns all details and calculation for the given year and month based
    on the provided settings, including specified additions or deductions.

    Args:
        year (int): The relevant year.
        month (int): The relevant month.
        wage (SalarySettings): The relevant salary calculation settings.
        overtime (bool): If True, monthly overtime is calculated and added to
                         final salary.
        bonus (int | float, optional): Amount to be added to the final salary.
        deduction (int | float, optional): Amount to be subtracted from the
                                           final salary.

    Returns:
        dict(str: int | float): All details and calculation for the given year
                                and month based on the provided settings,
                                including specified additions or deductions.

    Raises:
        ValueError: If  year is smaller than 1 or larger than 9999, or if month
                    is smaller than 1 or larger than 12.
    """
    # Code revision required after categories feature is added
    month_start, month_end = get_month_times(year, month)
    shifts = get_event_by_category(month_start, month_end, wage.user_id,
                                   wage.category_id)
    weeks = get_relevant_weeks(year, month)
    base_salary = sum(calc_shift_salary(shift.start, shift.end, wage)
                      for shift in shifts)
    if overtime:
        month_weekly_overtime = get_monthly_overtime(shifts, weeks, wage)
    else:
        month_weekly_overtime = 0
    transport = calc_transport(len(shifts), wage.daily_transport)
    salary = round(sum((base_salary, bonus,
                        month_weekly_overtime, transport)), 2)
    if deduction > salary:
        deduction = salary
    salary -= deduction
    return {
        'year': year,
        'month': month,
        'num_of_shifts': len(shifts),
        'base_salary': base_salary,
        'month_weekly_overtime': month_weekly_overtime,
        'transport': transport,
        'bonus': bonus,
        'deduction': deduction,
        'salary': round(salary, 2),
    }


def get_settings(session: Session, user_id: int,
                 category_id: int) -> Optional[SalarySettings]:
    """Returns settings for `user_id` and `category_id` if exists, None
    otherwise.

    Args:
        session (Session): DB session.
        user_id (int): Id of the relevant user.
        category_id (int): Id for the relevant category.

    Returns:
        SalarySettings | None: Settings for the provided user_id and
                               category_id if exists, None otherwise.
    """
    settings = session.query(SalarySettings).filter_by(
        user_id=user_id, category_id=category_id).first()
    session.close()
    return settings


def get_time_from_string(string: str) -> time:
    """Converts time string to a time object.

    Args:
        string (str): Time string.

    Returns:
        datetime.time: Time object.

    raises:
        ValueError: If string is not of format %H:%M:%S' or '%H:%M',
                    or if string is an invalid time.
    """
    try:
        return datetime.strptime(string, config.HOUR_FORMAT).time()
    except ValueError:
        return datetime.strptime(string, config.ALT_HOUR_FORMAT).time()


def update_settings(session: Session, wage: SalarySettings,
                    form: Dict[str, str]) -> bool:
    """Update salary settings instance according to info in `form`.

    Args:
        session (Session): DB session.
        wage (SalarySettings): Settings to be updated.
        form (dict(str: str)): Info to update.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        None
    """
    try:
        wage.wage = form['wage']
        wage.off_day = form['off_day']
        wage.holiday_category_id = form['holiday_category_id']
        wage.regular_hour_basis = form['regular_hour_basis']
        wage.night_hour_basis = form['night_hour_basis']
        wage.night_start = get_time_from_string(form['night_start'])
        wage.night_end = get_time_from_string(form['night_end'])
        wage.night_min_len = get_time_from_string(form['night_min_len'])
        wage.first_overtime_amount = form['first_overtime_amount']
        wage.first_overtime_pay = form['first_overtime_pay']
        wage.second_overtime_pay = form['second_overtime_pay']
        wage.week_working_hours = form['week_working_hours']
        wage.daily_transport = form['daily_transport']

    except KeyError:
        return False

    else:
        save(session, wage)
        return True
