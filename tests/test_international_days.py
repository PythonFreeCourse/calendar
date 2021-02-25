from datetime import date, timedelta

import pytest

from app.database.models import InternationalDays
from app.internal import international_days
from app.internal.international_days import get_international_day_per_day
from app.internal.json_data_loader import _insert_into_database
from app.internal.utils import create_model, delete_instance

DATE = date(2021, 6, 1)
DAY = "Hamburger day"


@pytest.fixture
def international_day(session):
    inter_day = create_model(
        session,
        InternationalDays,
        id=1,
        day=1,
        month=6,
        international_day="Hamburger day",
    )
    yield inter_day
    delete_instance(session, inter_day)


@pytest.fixture
def all_international_days(session):
    _insert_into_database(
        session,
        "app/resources/international_days.json",
        InternationalDays,
        international_days.get_international_day,
    )
    all_international_days = session.query(InternationalDays)
    yield all_international_days
    for day in all_international_days:
        delete_instance(session, day)


def date_range():
    start = date(2024, 1, 1)
    end = date(2024, 12, 31)
    dates = (end + timedelta(days=1) - start).days
    return [start + timedelta(days=i) for i in range(dates)]


def test_input_day_equal_output_day(session, international_day):
    inter_day = international_days.get_international_day_per_day(
        session,
        DATE,
    ).international_day
    assert inter_day == DAY


def test_international_day_per_day_no_international_days(session):
    result = international_days.get_international_day_per_day(session, DATE)
    assert result is None


def test_all_international_days_per_day(session, all_international_days):
    for day in date_range():
        assert get_international_day_per_day(session, day)
