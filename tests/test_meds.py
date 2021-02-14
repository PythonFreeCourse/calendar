from datetime import date, datetime, time
from typing import Dict, List

import pytest
from sqlalchemy.orm.session import Session
from starlette.testclient import TestClient

from app.database.models import Event, User
from app.routers import meds

NAME = 'Pasta'
QUOTE = 'I don\'t like sand. It\'s coarse and rough and irritating and it \
    gets everywhere.'
FORM = {
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


def create_test_form(**kwargs: Dict[str, str]) -> Dict[str, str]:
    form = FORM.copy()
    for k, v in kwargs.items():
        form[k] = v
    return form


FORM_TRANS = [
    (FORM, (NAME, None, 3, time(8), time(22), time(4), time(6), QUOTE,
            datetime(2015, 10, 21, 8), datetime(2015, 10, 22, 22))),
    (create_test_form(first='13:30'), (NAME, time(13, 30), 3, time(8),
                                       time(22), time(4), time(6), QUOTE,
                                       datetime(2015, 10, 21, 13, 30),
                                       datetime(2015, 10, 22, 22))),
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


FORM_VALIDATE = [
    (FORM, [False, False, False]),
    (create_test_form(
        end=FORM['start'], max=FORM['min'], amount='1', late='10:00'
    ), [False, False, False]),
    (create_test_form(end='1985-10-26'), [True, False, False]),
    (create_test_form(max='03:00'), [False, True, False]),
    (create_test_form(late='10:00'), [False, False, True]),
    (create_test_form(amount='60'), [False, False, True]),
    (create_test_form(end='1985-10-26', max='03:00', late='10:00'),
     [True, True, True])
]

CALC_INTERVAL = [
    (create_test_form(amount='1'), 0),
    (FORM, 300),
    (create_test_form(min='00:00', max='23:59'), 420),
]

REMINDER_TIMES = [
    (FORM, [time(10), time(15), time(20)]),
    (create_test_form(amount='1'), [time(15)]),
    (create_test_form(min='00:00', max='23:59'),
     [time(8), time(15), time(22)]),
    (create_test_form(early='13:00', late='02:00'),
     [time(14, 30), time(19, 30), time(0, 30)]),
]

DATETIMES_VALIDATE = [
    (datetime(1605, 11, 5, 23), date(1605, 11, 5), time(8), time(22), False),
    (datetime(1605, 11, 5, 21), date(1605, 11, 5), time(8), time(22), True),
    (datetime(1605, 11, 5, 23), date(1605, 11, 5), time(12), time(2), True),
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
    (FORM, True)
]


@pytest.mark.parametrize('form, form_tuple', FORM_TRANS)
def test_trans_form(form: Dict[str, str], form_tuple: meds.FORM_TUPLE) -> None:
    assert meds.trans_form(form) == form_tuple


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


@pytest.mark.parametrize('form, booleans', FORM_VALIDATE)
def test_validate_form(form: Dict[str, str], booleans: List[bool]) -> None:
    errors = meds.validate_form(form)
    for i, error in enumerate(meds.ERRORS.values()):
        message = error in errors
        assert message is booleans[i]


@pytest.mark.parametrize('form, interval', CALC_INTERVAL)
def test_calc_reminder_interval(form: Dict[str, str], interval: int) -> None:
    assert meds.calc_reminder_interval(form) == interval


@pytest.mark.parametrize('form, times', REMINDER_TIMES)
def test_get_reminder_times(form: Dict[str, str], times: List[time]) -> None:
    assert meds.get_reminder_times(form) == times


@pytest.mark.parametrize('t, day, early, late, boolean', DATETIMES_VALIDATE)
def test_validate_datetime(t: datetime, day: date, early: time, late: time,
                           boolean: bool) -> None:
    assert meds.validate_datetime(t, day, early, late) == boolean


@pytest.mark.parametrize('form, times, datetimes', FIRST)
def test_get_first_day_reminders(form: Dict[str, str], times: List[time],
                                 datetimes: List[datetime]) -> None:
    assert meds.get_first_day_reminders(form, times) == datetimes


@pytest.mark.parametrize('form, datetimes', DATETIMES)
def test_get_reminder_datetimes(form: Dict[str, str],
                                datetimes: List[datetime]) -> None:
    assert meds.get_reminder_datetimes(form) == datetimes


@pytest.mark.parametrize('form, boolean', CREATE)
def test_create_events(session: Session, user: User, form: Dict[str, str],
                       boolean: bool) -> None:
    assert session.query(Event).first() is None
    meds.create_events(session, user, form)
    event = session.query(Event).first()
    assert event
    title = '-' in event.title
    assert title is boolean


def test_meds_page_returns_ok(meds_test_client: TestClient) -> None:
    path = meds.router.url_path_for('meds')
    response = meds_test_client.get(path)
    assert response.ok


def test_meds_send_form(meds_test_client: TestClient,
                        session: Session) -> None:
    assert session.query(Event).first() is None
    path = meds.router.url_path_for('meds')
    response = meds_test_client.post(path, data=FORM, allow_redirects=True)
    assert response.ok
    assert 'PyLendar' in response.text
    assert session.query(Event).first()
