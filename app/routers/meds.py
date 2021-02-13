from datetime import date, datetime, time, timedelta
from typing import Dict, List, Tuple

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from app.database.models import Event, User
from app.dependencies import get_db, templates
from app.internal.utils import (create_model, get_current_user,
                                get_time_from_string)
from app.main import app


router = APIRouter(
    prefix='/meds',
    tags=['meds'],
    dependencies=[Depends(get_db)],
)

ERRORS = {
    'finish': 'Finish Date must must be later than or equal to Start Date',
    'max': 'Maximal Interval must must be larger than or equal to Minimal \
        Interval',
    'range': 'Reminders time range must must be larger than or equal to \
        Minimal Interval',
    'amount': 'Interval between Earliest Reminder and Latest Reminder not \
        long enough for Daily Amount with Minimal Interval'
}


def trans_form(form: Dict[str, str]) -> Tuple[str, time, int, time, time, time,
                                              time, str, datetime, datetime]:
    name = form['name']
    start_date = get_time_from_string(form['start'])
    first = get_time_from_string(form['first'])
    end_date = get_time_from_string(form['end'])
    amount = int(form['amount'])
    early = get_time_from_string(form['early'])
    late = get_time_from_string(form['late'])
    minimum = get_time_from_string(form['min'])
    maximum = get_time_from_string(form['max'])
    first_time = first if first else minimum
    start = datetime.combine(start_date, first_time)
    end = datetime.combine(end_date, maximum)
    note = form['note']
    return (
        name, first, amount, early, late, minimum, maximum, note, start, end)


def convert_time_to_minutes(time_obj: time) -> int:
    return round(time_obj.hour * 60 + time_obj.minute)


def get_interval_in_minutes(early: time, late: time) -> int:
    if early == late:
        0
    extra = 1 if early > late else 0
    early_date = datetime.combine(datetime.min, early)
    late_date = datetime.combine(datetime.min + timedelta(extra), late)
    interval = late_date - early_date
    return round(interval.seconds / 60)


def validate_amount(amount: int, minimum: time, early: time,
                    late: time) -> bool:
    min_time = (amount - 1) * convert_time_to_minutes(minimum)
    interval = get_interval_in_minutes(early, late)
    if min_time <= interval:
        return True
    return False


def validate_form(form: Dict[str, str]) -> List[str]:
    (_, _, amount, early, late, minimum,
     maximum, _, start, end) = trans_form(form)
    errors = []
    if end < start:
        errors.append(ERRORS['finish'])
    if maximum < minimum:
        errors.append(ERRORS['max'])
    if get_interval_in_minutes(early, late) < convert_time_to_minutes(minimum):
        errors.append(ERRORS['range'])
    if not validate_amount(amount, minimum, early, late):
        errors.append(ERRORS['amount'])

    return errors


def calc_reminder_interval(form: Dict[str, str]) -> int:
    (_, _, amount, early, late, minimum, maximum, _, _, _) = trans_form(form)
    if amount == 1:
        return 0
    reminder_interval = get_interval_in_minutes(early, late)
    max_med_interval = round(reminder_interval / (amount - 1))
    min_minutes = convert_time_to_minutes(minimum)
    max_minutes = convert_time_to_minutes(maximum)
    avg_med_interval = round((min_minutes + max_minutes) / 2)
    if avg_med_interval >= max_med_interval:
        return max_med_interval
    return avg_med_interval


def get_reminder_times(form: Dict[str, str]) -> List[time]:
    _, _, amount, early, late, _, _, _, _, _ = trans_form(form)
    interval = calc_reminder_interval(form)
    times = []
    early_reminder = datetime.combine(datetime.min, early)
    for i in range(amount):
        reminder = early_reminder + timedelta(minutes=interval) * i
        times.append(reminder.time())

    wasted_time = get_interval_in_minutes(times[-1], late) / 2
    times = [(datetime.combine(datetime.min, t)
              + timedelta(minutes=wasted_time)).time()
             for t in times]

    return times


def validate_datetime(t: datetime, day: date, early: time, late: time) -> bool:
    early_datetime = datetime.combine(day, early)
    late_datetime = datetime.combine(day, late)
    if late < early:
        late_datetime += timedelta(1)
    return early_datetime <= t <= late_datetime


def get_first_day_reminders(form: Dict[str, str], times: List[time]):
    _, _, amount, early, late, minimum, maximum, _, start, _ = trans_form(form)
    datetimes = []
    datetimes.append(start)
    for t in times:
        if len(datetimes) < amount:
            reminder = datetime.combine(start.date(), t)
            if t < early:
                reminder += timedelta(1)
            if reminder > start:
                interval = get_interval_in_minutes(
                    datetimes[-1].time(), t)
                min_minutes = convert_time_to_minutes(minimum)
                max_minutes = convert_time_to_minutes(maximum)
                if max_minutes >= interval >= min_minutes:
                    datetimes.append(reminder)
                else:
                    reminder = datetimes[-1] + timedelta(
                        minutes=min_minutes)
                    if validate_datetime(reminder,
                                         datetimes[-1].date(),
                                         early, late):
                        datetimes.append(reminder)
    return datetimes


def get_reminder_datetimes(form: Dict[str, str]) -> List[datetime]:
    (_, first, amount, early, late, minimum,
     maximum, _, start, end) = trans_form(form)
    times = get_reminder_times(form)
    datetimes = []
    for day in range((end.date() - start.date()).days + 1):
        if day == 0 and first:
            datetimes.extend(get_first_day_reminders(amount, late,
                                                     minimum, maximum))
        else:
            for t in times:
                extra = 1 if t < early else 0
                day_date = start.date() + timedelta(day + extra)
                day_datetime = datetime.combine(day_date, t)
                datetimes.append(day_datetime)

    return datetimes


def create_events(session: Session, user: User, form: Dict[str, str]) -> None:
    events = []
    name, _, _, _, _, _, _, note, _, _ = trans_form(form)
    times = get_reminder_datetimes(form)
    title = 'It\'s time to take your meds'
    if name:
        title = f'{name.title()} - {title}'
    for event_time in times:
        data = {
            'title': title,
            'start': event_time,
            'end': event_time + timedelta(minutes=5),
            'content': note,
            'owner_id': user.id,
        }
        events.append(create_model(session, Event, **data))
    return events


@router.get('/')
@router.post('/')
async def meds(request: Request,
               session: Session = Depends(get_db)) -> Response:
    form = await request.form()
    user = get_current_user(session)
    errors = []

    data = {
        'name': '',
        'start': date.today(),
        'first': None,
        'end': date.today() + timedelta(7),
        'amount': 1,
        'early': time(8),
        'late': time(22),
        'min': time(0),
        'max': time(23, 59),
        'note': '',
    }

    if form:
        errors = validate_form(form)
        if not errors:
            create_events(session, user, form)
            return RedirectResponse(app.url_path_for('home'), status_code=303)
        data = form

    return templates.TemplateResponse('meds.j2', {
        'request': request,
        'errors': errors,
        'data': data,
    })
