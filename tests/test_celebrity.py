import datetime

import pytest

from app.internal.celebrity import get_today_month_and_day

CELEBRITY_ROUTE = "/celebrity"
FAKE_TIME = datetime.date(2018, 9, 18)

BAD_DATES = [
    datetime.date(2021, 1, 1),
    datetime.date(1789, 7, 14),
    datetime.date(1776, 7, 4),
    datetime.date(1945, 1, 27),
    datetime.date(2000, 10, 16),
]

GOOD_DATES = [
    datetime.date(2020, 9, 18),
    datetime.date(2019, 9, 18),
    datetime.date(2016, 9, 18),
]


@pytest.fixture
def datetime_mock(monkeypatch):
    class MockDateTime:

        @staticmethod
        def today():
            return FAKE_TIME

    monkeypatch.setattr(datetime, 'date', MockDateTime)


@pytest.mark.parametrize('date', BAD_DATES)
def test_get_today_month_and_day_bad(date, datetime_mock):
    assert get_today_month_and_day() != date.strftime("%m-%d")


@pytest.mark.parametrize('date', GOOD_DATES)
def test_get_today_month_and_day_good(date, datetime_mock):
    assert get_today_month_and_day() == date.strftime("%m-%d")


def test_celebrity_page_exists(client):
    response = client.get(CELEBRITY_ROUTE)
    assert response.ok
    assert b'born today' in response.content
