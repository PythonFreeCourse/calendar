from datetime import datetime, time, timedelta
from typing import Iterator, Tuple

from app.database.models import Event, SalarySettings
from app.routers.salary.config import (DEFAULT_DATETIME, HOURS_SECONDS_RATIO,
                                       NIGHT_END, NIGHT_START, NUMERIC)


def get_shift_len(start: datetime, end: datetime) -> float:
    return (end - start).seconds / HOURS_SECONDS_RATIO


def get_night_times(date: datetime, prev_day: bool = False
                    ) -> Tuple[datetime, datetime]:
    if prev_day:
        sub = timedelta(1)
    else:
        sub = timedelta(0)
    return (datetime.combine(date - sub, time(NIGHT_START)),
            datetime.combine(date + timedelta(1) - sub,
                                      time(NIGHT_END)))


def is_night_shift(start: datetime, end: datetime,
                   wage: SalarySettings) -> bool:
    if not ((end - start).seconds / HOURS_SECONDS_RATIO
            >= wage.first_overtime_amount):
        return False
    for boolean in (False, True):
        night_start, night_end = get_night_times(start, boolean)
        if (get_total_synchronous_hours(start, end, night_start, night_end)
            >= wage.first_overtime_amount):
            return True
    return False


def get_relevant_holiday_times(
    start: datetime, end: datetime,
    off_day: int, holiday_category_id: int
    ) -> Tuple[datetime, datetime]:
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    # if off_day == SATURDAY:
    #     for event_start, event_end in get_shabbat_times(start, end):
    #         if events_synchronize(start, end, event_start, event_end):
    #             return event_start, event_end
    # else:
    #     for event_start, event_end in get_holidays(start, end,
    #                                                holiday_category_id):
    #         if events_synchronize(start, end, event_start, event_end):
    #             return event_start, event_end
    if start.weekday() == off_day:
        date = start.date()
    elif end.weekday() == off_day:
        date = end.date()
    try:
        return (datetime.combine(date, time(0)),
                datetime.combine(date + timedelta(1),
                                          time(0)))
    except NameError:
        return DEFAULT_DATETIME, DEFAULT_DATETIME


def get_total_synchronous_hours(
    event_1_start: datetime, event_1_end: datetime,
    event_2_start: datetime, event_2_end: datetime
    ) -> float:
    if event_2_start <= event_1_start <= event_2_end:
        if event_1_end <= event_2_end:
            start = event_1_start
            end = event_1_end
        else:
            start = event_1_start
            end = event_2_end
    elif event_2_start <= event_1_end <= event_2_end:
        start = event_2_start
        end = event_1_end
    elif event_1_start <= event_2_start and event_1_end >= event_2_end:
        start = event_1_start
        end = event_1_end
    try:
        return get_shift_len(start, end)
    except NameError:
        return 0.0


def get_hours_during_holiday(
    shift_start: datetime, shift_end: datetime,
    wage: SalarySettings
    ) -> float:
    holiday_start, holiday_end = get_relevant_holiday_times(
        shift_start, shift_end, wage.off_day, wage.holiday_category_id)
    return get_total_synchronous_hours(shift_start, shift_end,
                                 holiday_start, holiday_end)


def adjust_overtime(start: datetime, end: datetime,
                    wage: SalarySettings) -> Tuple[float, float]:
    total_hours = 0.0
    overtime = 0.0
    if is_night_shift(start, end, wage):
        hour_basis = wage.night_hour_basis
    else:
        hour_basis = wage.regular_hour_basis
    shift_len = get_shift_len(start, end)
    
    total_hours += get_hours_during_holiday(start, end, wage) / 2

    if shift_len > hour_basis:
        overtime += shift_len - hour_basis
        total_hours += hour_basis
        if overtime > wage.first_overtime_amount:
            total_hours += ((overtime - wage.first_overtime_amount)
                            * wage.second_overtime_pay
                            + wage.first_overtime_amount
                            * wage.first_overtime_pay)
        else:
            total_hours += overtime * wage.first_overtime_pay
    else:
        total_hours += shift_len

    return (total_hours, overtime)


def calc_shift_salary(start: datetime, end: datetime,
                      wage: SalarySettings) -> Tuple[float, float]:
    return round(adjust_overtime(start, end, wage)[0] * wage.wage, 2)


def calc_weekly_overtime(shifts: Tuple[Event, ...],
                       wage: SalarySettings) -> float:
    total_week_hours = sum(get_shift_len(**shift) for shift in shifts)
    if total_week_hours <= wage.week_working_hours:
        return 0.0
    else:
        total_daily_overtime = sum(map(lambda x: 
            adjust_overtime(**x, wage=wage)[1], shifts))
        overtime =  (total_week_hours
                     - wage.week_working_hours
                     - total_daily_overtime)
        if overtime > 0:
            return round(overtime * wage.wage, 2)
        return 0.0


def get_event_by_category(*args):
    # Dummy function
    # Code revision required after categories feature is added
    day_1 = {'start': datetime(2021, 1, 10, 9),
             'end': datetime(2021, 1, 10, 19)}
    day_2 = {'start': datetime(2021, 1, 11, 9),
             'end': datetime(2021, 1, 11, 17)}
    day_3 = {'start': datetime(2021, 1, 12, 9),
             'end': datetime(2021, 1, 12, 17)}
    day_4 = {'start': datetime(2021, 1, 13, 9),
             'end': datetime(2021, 1, 13, 18)}
    day_5 = {'start': datetime(2021, 1, 14, 9),
             'end': datetime(2021, 1, 14, 17)}
    day_6 = {'start': datetime(2021, 1, 15, 9),
             'end': datetime(2021, 1, 15, 14, 58)}

    return (day_1, day_2, day_3, day_4, day_5, day_6)


def get_relevant_weeks(month_start: datetime, month_end: datetime
    ) -> Iterator[Tuple[datetime, datetime]]:
    week_start = month_start - timedelta(month_start.weekday() + 1)
    week_end = week_start + timedelta(7)
    while week_end <= month_end:
        yield week_start, week_end
        week_start = week_end
        week_end += timedelta(7)


def get_monthly_overtime(shifts: Tuple[Event, ...], weeks: Tuple[Event, ...],
                         wage: SalarySettings) -> float:
    monthly_overtime = []
    for week_start, week_end in weeks:
        try:
            weekly_shifts = tuple(shift for shift in shifts
                                if week_start <= shift.start <= week_end)
        except AttributeError:
            weekly_shifts = tuple(shift for shift in shifts
                              if week_start <= shift['start'] <= week_end)
        weekly_overtime = calc_weekly_overtime(weekly_shifts, wage)
        monthly_overtime.append({'week_start': week_start,
                                 'week_end': week_end,
                                 'weekly_overtime': weekly_overtime})
    return monthly_overtime


def calc_salary(year: int, month: int, wage: SalarySettings,
                      deduction: NUMERIC = 0, bonus: NUMERIC = 0) -> float:
    month_start = datetime(year, month, 1)
    try:
        month_end = datetime(year, month + 1, 1)
    except:
        month_end = datetime(year + 1, 1, 1)
    # Code revision required after categories feature is added
    shifts = get_event_by_category(month_start, month_end, wage.user_id,
                                   wage.category_id)
    weeks = get_relevant_weeks(month_start, month_end)
    base_salary = sum(calc_shift_salary(wage=wage, **shift) for shift in shifts)
    month_weekly_overtime = get_monthly_overtime(shifts, weeks, wage)
    salary = round(base_salary
                   + bonus
                   + sum(week['weekly_overtime']
                         for week in month_weekly_overtime),
                   2)
    pension = calc_pension(salary, wage.pension)
    transport = calc_transport(shifts, wage.daily_transport)
    salary += transport
    taxes = calc_taxes(salary, wage.tax_points, pension)
    net_salary = salary - sum((pension, taxes, deduction))
    return {'year': year,
            'month': month,
            'num_of_shifts': len(shifts),
            'base_salary': base_salary,
            'month_weekly_overtime': month_weekly_overtime,
            'transport': transport,
            'salary': salary,
            'taxes': taxes,
            'pension': pension,
            'net_salary': net_salary}


def calc_pension(salary: float, pension_precentage: float) -> float:
    return round(salary * (pension_precentage / 100), 2)


def calc_transport(shifts: Tuple[Event, ...], daily_transport: float) -> float:
    return round(daily_transport * len(shifts), 2)


def calc_taxes(salary, tax_points: float, pension: float) -> float:
    return 0.0