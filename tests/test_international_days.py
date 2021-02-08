from datetime import date

import pytest

from app.database.models import InternationalDays
from app.internal import international_days
from tests.utils import create_model, delete_instance

DATE = date(2021, 6, 1)
DAY = "Hamburger day"


@pytest.fixture
def international_day(session):
    inter_day = create_model(
        session, InternationalDays, id=1, day=1, month=6,
        international_day="Hamburger day"
    )
    yield inter_day
    delete_instance(session, inter_day)


def test_input_day_equal_output_day(session, international_day):
    inter_day = international_days. \
        get_international_day_per_day(session, DATE).international_day
    assert inter_day == DAY


def test_international_day_per_day_no_international_days(session):
    assert international_days. \
               get_international_day_per_day(session, DATE) is None
