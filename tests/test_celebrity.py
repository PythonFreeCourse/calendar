import datetime

import pytest
from app.internal.celebrity import get_today_month_and_day


CELEBRITY_PAGE = "/celebrity"
FAKE_TIME = datetime.date(2018, 9, 18)


@pytest.fixture
def datetime_mock(monkeypatch):
    class MyDateTime:
        @classmethod
        def today(cls):
            return FAKE_TIME

    monkeypatch.setattr(datetime, 'date', MyDateTime)


def test_get_today_month_and_day(datetime_mock):
    assert get_today_month_and_day() == FAKE_TIME.strftime("%m-%d")


def test_celebrity_page_exists(client):
    resp = client.get(CELEBRITY_PAGE)
    assert resp.ok
    assert b'born today' in resp.content
