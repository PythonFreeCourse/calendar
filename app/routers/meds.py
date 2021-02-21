from datetime import date, datetime, time, timedelta
from typing import Dict, Iterator, List, Optional, Tuple

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.orm.session import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from app.database.models import Event
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


def adjust_day(datetime_obj: datetime, early: time, late: time,
               eq: bool = False) -> datetime:
    """Returns datetime_obj as same or following day as needed.

    Args:
        datetime_obj (datetime): Datetime object to adjust.
        early (time): Earlir time object.
        late (time): Later time object.
        eq (bool): Apply time object comparison.

    Returns:
        datetime: Datetime_obj with adjusted date.
    """
    if late < early or eq and late == early:
        datetime_obj += timedelta(days=1)
    return datetime_obj


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
    end_date = adjust_day(end_date, early, late, eq=True)
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
        return 0
    extra = int(early > late)
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
    return min_time <= interval


def validate_events(datetimes: List[datetime]) -> bool:
    """Return True if total amount of reminders is less than max amount, False
    otherwise.

    Args:
        datetimes (list(datetime)): Reminder times.

    Returns:
        bool: True if total amount of reminders is less than amx amount, False
              otherwise.
    """
    return len(list(datetimes)) <= MAX_EVENT_QUANTITY


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
    _, _, amount, early, late, minimum, maximum, _, _, _ = trans_form(form)
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
    times = [(datetime.combine(datetime.min, time_obj)
              + timedelta(minutes=wasted_time)).time()
             for time_obj in times]

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
    late_datetime = adjust_day(late_datetime, early, late)
    return early_datetime <= reminder <= late_datetime


def validate_first_day_reminder(previous: datetime, reminder_time: time,
                                minimum: time, maximum: time) -> bool:
    """Returns True if interval between reminders is valid, false otherwise.

    Args:
        previous (datetime): Previous reminder.
        reminder_time (time): New reminder time.
        minimum (time) - Minimal interval between reminders.
        maximum (time) - Maximal interval between reminders.

    Returns:
        bool: True if interval between reminders is valid, false otherwise.
    """
    interval = get_interval_in_minutes(previous.time(), reminder_time)
    min_minutes = convert_time_to_minutes(minimum)
    max_minutes = convert_time_to_minutes(maximum)
    return max_minutes >= interval >= min_minutes


def get_different_time_reminder(previous: datetime, minimum: time, early: time,
                                late: time) -> Optional[datetime]:
    """Returns datetime object for first day reminder with non-standard time.

    Args:
        previous (datetime): Previous reminder.
        minimum (time) - Minimal interval between reminders.
        early (time): Earliest reminder time.
        late (late): Latest reminder time. Interpreted as following day if
                     earlier than early.

    Returns:
        datetime | None: First day reminder with non-standard time, if valid.
    """
    reminder = previous + timedelta(minutes=convert_time_to_minutes(minimum))
    if validate_datetime(reminder, previous.date(), early, late):
        return reminder


def get_first_day_reminders(form: Dict[str, str],
                            times: List[time]) -> Iterator[datetime]:
    """Generates datetime objects for reminders on the first day.

    Args:
        form (dict(str, str)): Medication form containing all relevant data.
        times (list(time)): Time objects for reminders.

    Yields:
        datetime: First day reminder datetime object.
    """
    _, _, amount, early, late, minimum, maximum, _, start, _ = trans_form(form)
    yield start
    datetime_obj = start
    i = 1
    for time_obj in times:
        if i <= amount:
            reminder = datetime.combine(start.date(), time_obj)
            reminder = adjust_day(reminder, early, time_obj)
            if reminder > start:
                if not validate_first_day_reminder(datetime_obj, time_obj,
                                                   minimum, maximum):
                    reminder = get_different_time_reminder(
                        datetime_obj, minimum, early, late)
                yield reminder
                datetime_obj = reminder
                i += 1


def reminder_generator(times: List[time], early: time, start: datetime,
                       day: date, end: datetime) -> Iterator[datetime]:
    """Generates datetime objects for reminders based on times and date.

    Args:
        times (list(time)): Reminder times.
        early (time): Earliest reminder time.
        start (datetime): First reminder date and time.
        day (date): Reminders date.
        end (datetime) - Last reminder date and time.

    Yields:
        datetime: Reminder datetime object.
    """
    for time_obj in times:
        extra = int(time_obj < early)
        day_date = start.date() + timedelta(day + extra)
        reminder = datetime.combine(day_date, time_obj)
        if reminder <= end:
            yield reminder


def get_reminder_datetimes(form: Dict[str, str]) -> Iterator[datetime]:
    """Generates datetime object for reminders.

    Args:
        form (dict(str, str)): Medication form containing all relevant data.

    Yields:
        datetime: Reminder datetime object.
    """
    _, first, _, early, _, _, _, _, start, end = trans_form(form)
    times = get_reminder_times(form)
    total_days = (end.date() - start.date()).days + 1
    for day in range(total_days):
        if day == 0 and first:
            yield from get_first_day_reminders(form, times)
        else:
            yield from reminder_generator(times, early, start, day, end)


def create_events(session: Session, user_id: int,
                  form: Dict[str, str]) -> None:
    """Creates reminder events in the DB based on form data.

    Args:
        session (Session): DB session.
        user_id (int): ID of user to create events for.
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
            'owner_id': user_id,
        }
        events.append(create_model(session, Event, **data))


@router.get('/')
@router.post('/')
async def meds(request: Request,
               session: Session = Depends(get_db)) -> Response:
    """Renders medication reminders creation form page. Creates reminders in DB
    and redirects to home page upon submition if valid."""
    form = await request.form()
    errors = []

    data = {
        'name': '',
        'start': date.today(),
        'first': None,
        'end': date.today() + timedelta(days=7),
        'amount': 1,
        'early': time(8),
        'late': time(22),
        'min': time(0, 1),
        'max': time(23, 59),
        'note': '',
    }

    if form:
        user = get_current_user(session)
        errors = validate_form(form)
        if not errors:
            create_events(session, user.id, form)
            return RedirectResponse(app.url_path_for('home'), status_code=303)
        data = form

    return templates.TemplateResponse('meds.j2', {
        'request': request,
        'errors': errors,
        'data': data,
        'quantity': MAX_EVENT_QUANTITY,
    })
