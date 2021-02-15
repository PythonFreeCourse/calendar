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

MAX_EVENT_QUANTITY = 50

FORM_TUPLE = Tuple[str, time, int, time, time, time, time, str, datetime,
                   datetime]

ERRORS = {
    'finish': 'Finish Date must must be later than or equal to Start Date',
    'max': 'Maximal Interval must must be larger than or equal to Minimal \
        Interval',
    'amount': 'Interval between Earliest Reminder and Latest Reminder not \
        long enough for Daily Amount with Minimal Interval',
    'quantity': 'Total number of reminders can\'t be larger than '
                + f'{MAX_EVENT_QUANTITY}. Please lower the daily amount, or '
                + 'choose a shorter time period.'
}


def trans_form(form: Dict[str, str]) -> FORM_TUPLE:
    """Converts all form data to useable types and return as a Tuple.

    Args:
        form (dict(str, str)): Form to translate.

    Returns:
        tuple(...): All converted form data.
                        name (str) - Medication name.
                        first (time | None) - First dose time, if given.
                        amount (int) - Daily dosage.
                        early (time) - Earliest reminder time.
                        late (time) - Latest reminder time.
                        minimum (time) - Minimal interval between reminders.
                        maximum (time) - Maximal interval between reminders.
                        note (str) - Additional description.
                        start (datetime) - First reminder date and time.
                        end (datetime) - Last reminder date and time.
    """
    name = form['name']
    start_date = get_time_from_string(form['start'])
    first = get_time_from_string(form['first'])
    end_date = get_time_from_string(form['end'])
    amount = int(form['amount'])
    early = get_time_from_string(form['early'])
    late = get_time_from_string(form['late'])
    minimum = get_time_from_string(form['min'])
    maximum = get_time_from_string(form['max'])
    first_time = first if first else early
    start = datetime.combine(start_date, first_time)
    if late <= early:
        end_date += timedelta(1)
    end = datetime.combine(end_date, late)
    note = form['note']
    return (
        name, first, amount, early, late, minimum, maximum, note, start, end)


def convert_time_to_minutes(time_obj: time) -> int:
    """Returns time object as minutes.

    Args:
        time_obj (time): Time object to convert to minutes.

    Returns:
        int: Total minutes in time object.
    """
    return round(time_obj.hour * 60 + time_obj.minute)


def get_interval_in_minutes(early: time, late: time) -> int:
    """Returns interval between 2 time objects in minutes.

    Args:
        early (time): Earlier time object.
        late (time): Later time object. Interpreted as following day if earlier
        than early.

    Returns:
        int: Interval between time objects in minutes.
    """
    if early == late:
        0
    extra = 1 if early > late else 0
    early_date = datetime.combine(datetime.min, early)
    late_date = datetime.combine(datetime.min + timedelta(extra), late)
    interval = late_date - early_date
    return round(interval.seconds / 60)


def validate_amount(amount: int, minimum: time, early: time,
                    late: time) -> bool:
    """Returns True if interval is sufficient for reminder amount with minimal
    interval constraint, False otherwise

    Args:
        amount (int): Reminder amount.
        minimum (time): Minimal interval between reminders.
        early (time) - Earliest reminder time.
        late (time) - Latest reminder time.

    Returns:
        bool: True if interval is sufficient for reminder amount with minimal
              interval constraint, False otherwise
    """
    min_time = (amount - 1) * convert_time_to_minutes(minimum)
    interval = get_interval_in_minutes(early, late)
    if min_time <= interval:
        return True
    return False


def validate_events(datetimes: List[datetime]) -> bool:
    """Return True if total amount of reminders is less than amx amount, False
    otherwise.

    Args:
        datetimes (list(datetime)): Reminder times.

    Returns:
        bool: True if total amount of reminders is less than amx amount, False
              otherwise.
    """
    return len(datetimes) <= MAX_EVENT_QUANTITY


def validate_form(form: Dict[str, str]) -> List[str]:
    """Returns a list of error messages for given form.

    Args:
        form (dict(str, str)): Form to validate.

    Returns:
        list(str): Error messages for given form.
    """
    (_, _, amount, early, late, minimum,
     maximum, _, start, end) = trans_form(form)
    errors = []
    if end < start:
        errors.append(ERRORS['finish'])
    if maximum < minimum:
        errors.append(ERRORS['max'])
    if not validate_amount(amount, minimum, early, late):
        errors.append(ERRORS['amount'])
    datetimes = get_reminder_datetimes(form)
    if not validate_events(datetimes):
        errors.append(ERRORS['quantity'])

    return errors


def calc_reminder_interval_in_seconds(form: Dict[str, str]) -> int:
    """Returns interval between reminders in seconds.

    Args:
        form (dict(str, str)): Medication form containing all relevant data.

    Returns:
        int: Interval between reminders in seconds.
    """
    (_, _, amount, early, late, minimum, maximum, _, _, _) = trans_form(form)
    if amount == 1:
        return 0
    reminder_interval = get_interval_in_minutes(early, late)
    max_med_interval = reminder_interval / (amount - 1)
    min_minutes = convert_time_to_minutes(minimum)
    max_minutes = convert_time_to_minutes(maximum)
    avg_med_interval = (min_minutes + max_minutes) / 2
    if avg_med_interval >= max_med_interval:
        return int(max_med_interval * 60)
    return int(avg_med_interval * 60)


def get_reminder_times(form: Dict[str, str]) -> List[time]:
    """Returns a list of time objects for reminders based on form data.

    Args:
        form (dict(str, str)): Medication form containing all relevant data.

    Returns:
        list(time): Time objects for reminders.
    """
    _, _, amount, early, late, _, _, _, _, _ = trans_form(form)
    interval = calc_reminder_interval_in_seconds(form)
    times = []
    early_reminder = datetime.combine(datetime.min, early)
    for i in range(amount):
        reminder = early_reminder + timedelta(seconds=interval) * i
        times.append(reminder.time())

    wasted_time = get_interval_in_minutes(times[-1], late) / 2
    times = [(datetime.combine(datetime.min, t)
              + timedelta(minutes=wasted_time)).time()
             for t in times]

    return times


def validate_datetime(reminder: datetime, day: date, early: time,
                      late: time) -> bool:
    """Returns True if reminder is between earlist and latest reminder times on
    a given date or equal to any of them, False otherwise.

    Args:
        reminder (datetime): Datetime object to validate.
        day (date): Date for earlist reminder.
        early (time): Earliest reminder time.
        late (late): Latest reminder time. Interpreted as following day if
                     earlier than early.

    Returns:
        bool: True if reminder is between earlist and latest reminder times on
              a given date or equal to any of them, False otherwise.
    """
    early_datetime = datetime.combine(day, early)
    late_datetime = datetime.combine(day, late)
    if late < early:
        late_datetime += timedelta(1)
    return early_datetime <= reminder <= late_datetime


def get_first_day_reminders(form: Dict[str, str],
                            times: List[time]) -> List[datetime]:
    """Returns a list of datetime object for reminders on the first day.

    Args:
        form (dict(str, str)): Medication form containing all relevant data.
        times (list(time)): Time objects for reminders.

    Returns:
        list(datetime): Datetime objects for reminders on first day.
    """
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
    """Returns a list of datetime object for reminders.

    Args:
        form (dict(str, str)): Medication form containing all relevant data.

    Returns:
        list(datetime): Datetime objects for reminders.
    """
    _, first, _, early, late, _, _, _, start, end = trans_form(form)
    times = get_reminder_times(form)
    datetimes = []
    total_days = (end.date() - start.date()).days + 1
    for day in range(total_days):
        if day == 0 and first:
            datetimes.extend(get_first_day_reminders(form, times))
        else:
            for t in times:
                extra = 1 if t < early else 0
                day_date = start.date() + timedelta(day + extra)
                reminder = datetime.combine(day_date, t)
                if reminder <= end:
                    datetimes.append(reminder)

    return datetimes


def create_events(session: Session, user: User, form: Dict[str, str]) -> None:
    """Creates reminder events in the DB based on form data.

    Args:
        session (Session): DB session.
        user (User): User instance to create events for.
        form (dict(str, str)): Medication form containing all relevant data.
    """
    events = []
    name, _, _, _, _, _, _, note, _, _ = trans_form(form)
    title = 'It\'s time to take your meds'
    if name:
        title = f'{name.title()} - {title}'
    datetimes = get_reminder_datetimes(form)
    for event_time in datetimes:
        data = {
            'title': title,
            'start': event_time,
            'end': event_time + timedelta(minutes=5),
            'content': note,
            'owner_id': user.id,
        }
        events.append(create_model(session, Event, **data))


@router.get('/')
@router.post('/')
async def meds(request: Request,
               session: Session = Depends(get_db)) -> Response:
    """Renders medication reminders creation form page. Creates reminders in DB
    and redirects to home page upon submition if valid."""
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
        'min': time(0, 1),
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
        'quantity': MAX_EVENT_QUANTITY,
    })
