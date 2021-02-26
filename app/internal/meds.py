from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Iterator, List, Optional, Tuple

from pydantic.main import BaseModel
from sqlalchemy.orm.session import Session

from app.database.models import Event
from app.internal.utils import create_model, get_time_from_string

MAX_EVENT_QUANTITY = 50

ERRORS = {
    "finish": "Finish Date must must be later than or equal to Start Date",
    "max": "Maximal Interval must must be larger than or equal to Minimal \
        Interval",
    "amount": "Interval between Earliest Reminder and Latest Reminder not \
        long enough for Daily Amount with Minimal Interval",
    "quantity": "Total number of reminders can't be larger than "
    + f"{MAX_EVENT_QUANTITY}. Please lower the daily amount, or "
    + "choose a shorter time period.",
}


class Form(BaseModel):
    """Represents a translated form object.

    name (str, optional) - Medication name.
    first (time, optional) - First dose time, if given.
    amount (int) - Daily dosage.
    early (time) - Earliest reminder time.
    late (time) - Latest reminder time.
    min (time) - Minimal interval between reminders.
    max (time) - Maximal interval between reminders.
    start (datetime) - First reminder date and time.
    end (datetime) - Last reminder date and time.
    note (str, optional) - Additional description.
    """

    name: Optional[str]
    first: Optional[time]
    amount: int
    early: time
    late: time
    min: time
    max: time
    start: datetime
    end: datetime
    note: Optional[str]


def adjust_day(
    datetime_obj: datetime,
    early: time,
    late: time,
    eq: bool = False,
) -> datetime:
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


def trans_form(web_form: Dict[str, str]) -> Tuple[Form, Dict[str, Any]]:
    """Converts all form data to useable types and return as a Tuple.

    Args:
        form (dict(str, str)): Form to translate.

    Returns:
        tuple(Form, dict(str, any)): Tuple consisting of:
            - Form object with all converted form data.
            - Dictionary version of Form object.
    """
    form = {}
    form["name"] = web_form["name"]
    start_date = get_time_from_string(web_form["start"])
    form["first"] = get_time_from_string(web_form["first"])
    end_date = get_time_from_string(web_form["end"])
    form["amount"] = int(web_form["amount"])
    form["early"] = get_time_from_string(web_form["early"])
    form["late"] = get_time_from_string(web_form["late"])
    form["min"] = get_time_from_string(web_form["min"])
    form["max"] = get_time_from_string(web_form["max"])
    first_time = form["first"] if form["first"] else form["early"]
    form["start"] = datetime.combine(start_date, first_time)
    end_date = adjust_day(
        end_date,
        web_form["early"],
        web_form["late"],
        eq=True,
    )
    form["end"] = datetime.combine(end_date, form["late"])
    form["note"] = web_form["note"]

    form_obj = Form(**form)
    form["start"] = form["start"].date()
    form["end"] = form["end"].date()
    return form_obj, form


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


def validate_amount(amount: int, min: time, early: time, late: time) -> bool:
    """Returns True if interval is sufficient for reminder amount with minimal
    interval constraint, False otherwise

    Args:
        amount (int): Reminder amount.
        min (time): Minimal interval between reminders.
        early (time) - Earliest reminder time.
        late (time) - Latest reminder time.

    Returns:
        bool: True if interval is sufficient for reminder amount with minimal
              interval constraint, False otherwise
    """
    min_time = (amount - 1) * convert_time_to_minutes(min)
    interval = get_interval_in_minutes(early, late)
    return min_time <= interval


def validate_events(datetimes: Iterator[datetime]) -> bool:
    """Return True if total amount of reminders is less than max amount, False
    otherwise.

    Args:
        datetimes (list(datetime)): Reminder times.

    Returns:
        bool: True if total amount of reminders is less than amx amount, False
              otherwise.
    """
    return len(list(datetimes)) <= MAX_EVENT_QUANTITY


def validate_form(form: Form) -> List[str]:
    """Returns a list of error messages for given form.

    Args:
        form (Form): Form object to validate.

    Returns:
        list(str): Error messages for given form.
    """
    errors = []
    if form.end < form.start:
        errors.append(ERRORS["finish"])
    if form.max < form.min:
        errors.append(ERRORS["max"])
    if not validate_amount(form.amount, form.min, form.early, form.late):
        errors.append(ERRORS["amount"])
    datetimes = get_reminder_datetimes(form)
    if not validate_events(datetimes):
        errors.append(ERRORS["quantity"])

    return errors


def calc_reminder_interval_in_seconds(form: Form) -> int:
    """Returns interval between reminders in seconds.

    Args:
        form (Form): Form object containing all relevant data.

    Returns:
        int: Interval between reminders in seconds.
    """
    if form.amount == 1:
        return 0
    reminder_interval = get_interval_in_minutes(form.early, form.late)
    max_med_interval = reminder_interval / (form.amount - 1)
    min_minutes = convert_time_to_minutes(form.min)
    max_minutes = convert_time_to_minutes(form.max)
    avg_med_interval = (min_minutes + max_minutes) / 2
    return int(min(max_med_interval, avg_med_interval) * 60)


def get_reminder_times(form: Form) -> List[time]:
    """Returns a list of time objects for reminders based on form data.

    Args:
        form (Form): Form object containing all relevant data.

    Returns:
        list(time): Time objects for reminders.
    """
    interval = calc_reminder_interval_in_seconds(form)
    times = []
    early_reminder = datetime.combine(datetime.min, form.early)
    for i in range(form.amount):
        reminder = early_reminder + timedelta(seconds=interval) * i
        times.append(reminder.time())

    wasted_time = get_interval_in_minutes(times[-1], form.late) / 2
    times = [
        (
            datetime.combine(datetime.min, time_obj)
            + timedelta(minutes=wasted_time)
        ).time()
        for time_obj in times
    ]

    return times


def validate_datetime(
    reminder: datetime,
    day: date,
    early: time,
    late: time,
) -> bool:
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


def validate_first_day_reminder(
    previous: datetime,
    reminder_time: time,
    min: time,
    max: time,
) -> bool:
    """Returns True if interval between reminders is valid, false otherwise.

    Args:
        previous (datetime): Previous reminder.
        reminder_time (time): New reminder time.
        min (time) - Minimal interval between reminders.
        max (time) - Maximal interval between reminders.

    Returns:
        bool: True if interval between reminders is valid, false otherwise.
    """
    interval = get_interval_in_minutes(previous.time(), reminder_time)
    min_minutes = convert_time_to_minutes(min)
    max_minutes = convert_time_to_minutes(max)
    return max_minutes >= interval >= min_minutes


def get_different_time_reminder(
    previous: datetime,
    min: time,
    early: time,
    late: time,
) -> Optional[datetime]:
    """Returns datetime object for first day reminder with non-standard time.

    Args:
        previous (datetime): Previous reminder.
        min (time) - Minimal interval between reminders.
        early (time): Earliest reminder time.
        late (late): Latest reminder time. Interpreted as following day if
                     earlier than early.

    Returns:
        datetime | None: First day reminder with non-standard time, if valid.
    """
    reminder = previous + timedelta(minutes=convert_time_to_minutes(min))
    if validate_datetime(reminder, previous.date(), early, late):
        return reminder


def create_first_day_reminder(
    form: Form,
    reminder_time: time,
    previous: datetime,
) -> Optional[datetime]:
    """Returns datetime object for reminder on first day.

    form (Form): Form object containing all relevant data.
    reminder_time (time): Time object for new reminder.
    previous (datetime): Previous reminder.

    Returns:
        datetime | None: First day reminder.
    """
    reminder = datetime.combine(form.start.date(), reminder_time)
    reminder = adjust_day(reminder, form.early, reminder_time)
    if reminder > form.start:
        if not validate_first_day_reminder(
            previous,
            reminder_time,
            form.min,
            form.max,
        ):
            reminder = get_different_time_reminder(
                previous,
                form.min,
                form.early,
                form.late,
            )
        return reminder


def get_first_day_reminders(
    form: Form,
    times: List[time],
) -> Iterator[datetime]:
    """Generates datetime objects for reminders on the first day.

    Args:
        form (Form): Form object containing all relevant data.
        times (list(time)): Time objects for reminders.

    Yields:
        datetime: First day reminder datetime object.
    """
    yield form.start
    previous = form.start
    i = 1
    for reminder_time in times:
        if i <= form.amount:
            new = create_first_day_reminder(form, reminder_time, previous)
            if new:
                yield new
                previous = new
                i += 1


def reminder_generator(
    times: List[time],
    early: time,
    start: datetime,
    day: date,
    end: datetime,
) -> Iterator[datetime]:
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


def get_reminder_datetimes(form: Form) -> Iterator[datetime]:
    """Generates datetime object for reminders.

    Args:
        form (Form): Form object containing all relevant data.

    Yields:
        datetime: Reminder datetime object.
    """
    times = get_reminder_times(form)
    total_days = (form.end.date() - form.start.date()).days + 1
    for day in range(total_days):
        if day == 0 and form.first:
            yield from get_first_day_reminders(form, times)
        else:
            yield from reminder_generator(
                times,
                form.early,
                form.start,
                day,
                form.end,
            )


def create_events(session: Session, user_id: int, form: Form) -> None:
    """Creates reminder events in the DB based on form data.

    Args:
        session (Session): DB session.
        user_id (int): ID of user to create events for.
        form (Form): Form object containing all relevant data.
    """
    title = "It's time to take your meds"
    if form.name:
        title = f"{form.name.title()} - {title}"
    datetimes = get_reminder_datetimes(form)
    for event_time in datetimes:
        event_data = {
            "title": title,
            "start": event_time,
            "end": event_time + timedelta(minutes=5),
            "content": form.note,
            "owner_id": user_id,
        }
        create_model(session, Event, **event_data)
