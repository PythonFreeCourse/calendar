import datetime

import pytest
from app.internal.celebrity import get_today_month_and_day


CELEBRITY_PAGE = "/celebrity"
FAKE_TIME = datetime.date(2018, 9, 18)

FAKE_DATES = [
    datetime.date(2020, 1, 1),
    datetime.date(1789, 7, 14),
    datetime.date(1776, 7, 4),
    datetime.date(1945, 1, 27),
    datetime.date(2000, 10, 16)
]


@pytest.fixture
def datetime_mock(monkeypatch):
    class MyDateTime:
        @classmethod
        def today(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, 'date', MyDateTime)


@pytest.mark.parametrize('date_string', FAKE_DATES)
def test_get_today_month_and_day_bad(date_string, datetime_mock):
    assert get_today_month_and_day() != date_string.strftime("%m-%d")


def test_get_today_month_and_day_good(datetime_mock):
    assert get_today_month_and_day() == FAKE_TIME.strftime("%m-%d")


def test_celebrity_page_exists(client):
    resp = client.get(CELEBRITY_PAGE)
    assert resp.ok
    assert b'born today' in resp.content
