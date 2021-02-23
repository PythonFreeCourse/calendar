from datetime import date, datetime, time
from typing import Dict, List

import pytest
from sqlalchemy.orm.session import Session

from app.database.models import Event, User
from app.internal import meds

NAME = 'Pasta'
QUOTE = 'I don\'t like sand. It\'s coarse and rough and irritating and it \
    gets everywhere.'
WEB_FORM = {
    'name': NAME,
    'start': '2015-10-21',
    'first': '',
    'end': '2015-10-22',
    'amount': '3',
    'early': '08:00',
    'late': '22:00',
    'min': '04:00',
    'max': '06:00',
    'note': QUOTE,
}
FORM = meds.trans_form(WEB_FORM)[0]


def create_test_form(form_dict: bool = False,
                     **kwargs: Dict[str, str]) -> meds.Form:
    form = WEB_FORM.copy()
    for k, v in kwargs.items():
        form[k] = v
    if form_dict:
        return form
    translated_form, _ = meds.trans_form(form)
    return translated_form


ADJUST = [
    (datetime(2015, 10, 21), time(8), time(22), False, datetime(2015, 10, 21)),
    (datetime(2015, 10, 21), time(8), time(22), True, datetime(2015, 10, 21)),
    (datetime(2015, 10, 21), time(8), time(8), False, datetime(2015, 10, 21)),
    (datetime(2015, 10, 21), time(8), time(8), True, datetime(2015, 10, 22)),
    (datetime(2015, 10, 21), time(8), time(2), False, datetime(2015, 10, 22)),
    (datetime(2015, 10, 21), time(8), time(2), True, datetime(2015, 10, 22)),
]

FORM_TRANS = [
    (WEB_FORM, meds.Form(
        name=NAME, first=None, amount=3, early=time(8), late=time(22),
        min=time(4), max=time(6), start=datetime(2015, 10, 21, 8),
        end=datetime(2015, 10, 22, 22), note=QUOTE),
     {'name': NAME, 'first': None, 'amount': 3, 'early': time(8),
      'late': time(22), 'min': time(4), 'max': time(6),
      'start': date(2015, 10, 21), 'end': date(2015, 10, 22),
      'note': QUOTE}),
    (create_test_form(form_dict=True, first='13:30'), meds.Form(
        name=NAME, first=time(13, 30), amount=3, early=time(8), late=time(22),
        min=time(4), max=time(6), start=datetime(2015, 10, 21, 13, 30),
        end=datetime(2015, 10, 22, 22), note=QUOTE),
     {'name': NAME, 'first': time(13, 30), 'amount': 3, 'early': time(8),
      'late': time(22), 'min': time(4), 'max': time(6),
      'start': date(2015, 10, 21), 'end': date(2015, 10, 22), 'note': QUOTE}),
]

TIMES = [
    (time(13), 780),
    (time(17, 26), 1046),
]

INTERVAL_MINUTE = [
    (time(4), time(4), 0),
    (time(8), time(22), 840),
    (time(12), time(2), 840),
]

AMOUNTS = [
    (1, time(12), time(9), time(17), True),
    (2, time(4), time(8), time(22), True),
    (3, time(8), time(10), time(20), False),
]

EVENTS = [
    (FORM, True),
    (create_test_form(amount='60'), False),
    (create_test_form(end='2015-11-22'), False),
]

FORM_VALIDATE = [
    (FORM, [False, False, False, False]),
    (create_test_form(
        end=WEB_FORM['start'], max=WEB_FORM['min'], amount='1', late='10:00'
    ), [False, False, False, False]),
    (create_test_form(end='1985-10-26'), [True, False, False, False]),
    (create_test_form(max='03:00'), [False, True, False, False]),
    (create_test_form(late='10:00'), [False, False, True, False]),
    (create_test_form(min='00:01', amount='60'), [False, False, False, True]),
    (create_test_form(
        end='1985-10-26', max='03:00', late='10:00', amount="60"
    ), [True, True, True, False]),
    (create_test_form(max='03:00', late='10:00', amount="60"),
     [False, True, True, True]),
]

CALC_INTERVAL = [
    (create_test_form(amount='1'), 0),
    (FORM, 18000),
    (create_test_form(min='00:01', max='23:59'), 25200),
]

REMINDER_TIMES = [
    (FORM, [time(10), time(15), time(20)]),
    (create_test_form(amount='1'), [time(15)]),
    (create_test_form(min='00:01', max='23:59'),
     [time(8), time(15), time(22)]),
    (create_test_form(early='13:00', late='02:00'),
     [time(14, 30), time(19, 30), time(0, 30)]),
]

DATETIMES_VALIDATE = [
    (datetime(1605, 11, 5, 23), date(1605, 11, 5), time(8), time(22), False),
    (datetime(1605, 11, 5, 21), date(1605, 11, 5), time(8), time(22), True),
    (datetime(1605, 11, 5, 23), date(1605, 11, 5), time(12), time(2), True),
]

VALIDATE_FIRST = [
    (datetime(2015, 10, 21, 10, 45), time(15), time(4), time(6), True),
    (datetime(2015, 10, 21, 10, 45), time(12), time(4), time(6), False),
    (datetime(2015, 10, 21, 10, 45), time(17), time(4), time(6), False),
]

DIFFERENT = [
    (datetime(2015, 10, 21, 11, 45), time(4), time(8), time(22),
     datetime(2015, 10, 21, 15, 45)),
    (datetime(2015, 10, 21, 20, 45), time(4), time(8), time(22), None)
]

CREATE_FIRST = [
    (create_test_form(first='10:45'), time(15), datetime(2015, 10, 21, 10, 45),
     datetime(2015, 10, 21, 15)),
    (create_test_form(first='10:45'), time(14), datetime(2015, 10, 21, 10, 45),
     datetime(2015, 10, 21, 14, 45)),
    (create_test_form(first='20:30', late='02:00'), time(1),
     datetime(2015, 10, 21, 20, 30), datetime(2015, 10, 22, 1)),
    (create_test_form(first='21:30', late='02:00'), time(1),
     datetime(2015, 10, 21, 21, 30), datetime(2015, 10, 22, 1, 30)),
    (create_test_form(first='16:30', late='02:00'), time(10),
     datetime(2015, 10, 21, 16, 30), None),
]

FIRST = [
    (create_test_form(first='10:45'), [time(10), time(15), time(20)],
     [datetime(2015, 10, 21, 10, 45), datetime(2015, 10, 21, 15),
      datetime(2015, 10, 21, 20)]),
    (create_test_form(first='13:30'), [time(10), time(15), time(20)],
     [datetime(2015, 10, 21, 13, 30), datetime(2015, 10, 21, 17, 30),
      datetime(2015, 10, 21, 21, 30)]),
    (create_test_form(first='17:20'), [time(10), time(15), time(20)],
     [datetime(2015, 10, 21, 17, 20), datetime(2015, 10, 21, 21, 20)]),
    (create_test_form(first='16:43', early='12:00', late='02:00'),
     [time(14), time(19), time(0)],
     [datetime(2015, 10, 21, 16, 43), datetime(2015, 10, 21, 20, 43),
      datetime(2015, 10, 22, 0, 43)]),
]

REMINDERS = [
    ([time(10), time(15), time(20)], time(8), datetime(2015, 10, 21, 8),
     0, datetime(2015, 10, 22, 22),
     [datetime(2015, 10, 21, 10), datetime(2015, 10, 21, 15),
      datetime(2015, 10, 21, 20)]),
    ([time(10), time(15), time(20)], time(8), datetime(2015, 10, 21, 8),
     1, datetime(2015, 10, 22, 22),
     [datetime(2015, 10, 22, 10), datetime(2015, 10, 22, 15),
      datetime(2015, 10, 22, 20)]),
    ([time(10), time(15), time(20)], time(8), datetime(2015, 10, 21, 8),
     2, datetime(2015, 10, 22, 22), []),
]

DATETIMES = [
    (FORM, [datetime(2015, 10, 21, 10), datetime(2015, 10, 21, 15),
            datetime(2015, 10, 21, 20), datetime(2015, 10, 22, 10),
            datetime(2015, 10, 22, 15), datetime(2015, 10, 22, 20)]),
    (create_test_form(first='13:30'),
     [datetime(2015, 10, 21, 13, 30), datetime(2015, 10, 21, 17, 30),
      datetime(2015, 10, 21, 21, 30), datetime(2015, 10, 22, 10),
      datetime(2015, 10, 22, 15), datetime(2015, 10, 22, 20)]),
]

CREATE = [
    (create_test_form(name=None), False),
    (FORM, True),
]


@pytest.mark.parametrize('datetime_obj, early, late, eq, new_obj', ADJUST)
def test_adjust_day(datetime_obj: datetime, early: time, late: time, eq: bool,
                    new_obj: datetime) -> None:
    assert meds.adjust_day(datetime_obj, early, late, eq) == new_obj


@pytest.mark.parametrize('form, form_obj ,form_dict', FORM_TRANS)
def test_trans_form(form: Dict[str, str], form_obj: meds.Form,
                    form_dict: Dict[str, str]) -> None:
    translated_form_obj, translated_form_dict = meds.trans_form(form)
    assert translated_form_obj == form_obj
    assert translated_form_dict == form_dict


@pytest.mark.parametrize('time_obj, minutes', TIMES)
def test_convert_time_to_minutes(time_obj: time, minutes: int) -> None:
    assert meds.convert_time_to_minutes(time_obj) == minutes


@pytest.mark.parametrize('early, late, interval', INTERVAL_MINUTE)
def test_get_interval_in_minutes(early: time, late: time,
                                 interval: int) -> None:
    assert meds.get_interval_in_minutes(early, late) == interval


@pytest.mark.parametrize('amount, minimum, early, late, boolean', AMOUNTS)
def test_validate_amount(amount: int, minimum: time, early: time, late: time,
                         boolean: bool) -> None:
    assert meds.validate_amount(amount, minimum, early, late) == boolean


@pytest.mark.parametrize('form, boolean', EVENTS)
def test_validate_events(form: meds.Form, boolean: bool) -> None:
    datetimes = meds.get_reminder_datetimes(form)
    assert meds.validate_events(datetimes) is boolean


@pytest.mark.parametrize('form, booleans', FORM_VALIDATE)
def test_validate_form(form: meds.Form, booleans: List[bool]) -> None:
    errors = meds.validate_form(form)
    for i, error in enumerate(meds.ERRORS.values()):
        message = error in errors
        print(i, error, message)
        assert message is booleans[i]


@pytest.mark.parametrize('form, interval', CALC_INTERVAL)
def test_calc_reminder_interval_in_seconds(form: meds.Form,
                                           interval: int) -> None:
    assert meds.calc_reminder_interval_in_seconds(form) == interval


@pytest.mark.parametrize('form, times', REMINDER_TIMES)
def test_get_reminder_times(form: meds.Form, times: List[time]) -> None:
    assert meds.get_reminder_times(form) == times


@pytest.mark.parametrize('t, day, early, late, boolean', DATETIMES_VALIDATE)
def test_validate_datetime(t: datetime, day: date, early: time, late: time,
                           boolean: bool) -> None:
    assert meds.validate_datetime(t, day, early, late) == boolean


@pytest.mark.parametrize('previous, reminder_time, minimum, maximum, boolean',
                         VALIDATE_FIRST)
def test_validate_first_day_reminder(previous: datetime, reminder_time: time,
                                     minimum: time, maximum: time,
                                     boolean: bool) -> None:
    assert meds.validate_first_day_reminder(
        previous, reminder_time, minimum, maximum) == boolean


@pytest.mark.parametrize('previous, minimum, early, late, reminder', DIFFERENT)
def test_get_different_time_reminder(
    previous: datetime, minimum: time, early: time, late: time,
        reminder: datetime) -> None:
    new = meds.get_different_time_reminder(previous, minimum, early, late)
    assert new == reminder


@pytest.mark.parametrize('form, time_obj, previous, reminder', CREATE_FIRST)
def test_create_first_day_reminder(form: meds.Form, time_obj: time,
                                   previous: datetime,
                                   reminder: datetime) -> None:
    new = meds.create_first_day_reminder(form, time_obj, previous)
    assert new == reminder


@pytest.mark.parametrize('form, times, datetimes', FIRST)
def test_get_first_day_reminders(form: meds.Form, times: List[time],
                                 datetimes: List[datetime]) -> None:
    assert list(meds.get_first_day_reminders(form, times)) == datetimes


@pytest.mark.parametrize('times, early, start, day, end, reminders', REMINDERS)
def test_reminder_generator(
    times: List[time], early: time, start: datetime, day: date, end: datetime,
        reminders: List[datetime]) -> None:
    new = list(meds.reminder_generator(times, early, start, day, end))
    assert new == reminders


@pytest.mark.parametrize('form, datetimes', DATETIMES)
def test_get_reminder_datetimes(form: meds.Form,
                                datetimes: List[datetime]) -> None:
    assert list(meds.get_reminder_datetimes(form)) == datetimes


@pytest.mark.parametrize('form, boolean', CREATE)
def test_create_events(session: Session, user: User, form: meds.Form,
                       boolean: bool) -> None:
    assert session.query(Event).first() is None
    meds.create_events(session, user.id, form)
    event = session.query(Event).first()
    assert event
    title = '-' in event.title
    assert title is boolean
