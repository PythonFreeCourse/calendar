import datetime

import pytest
from app.internal.celebrity import get_today_month_and_day
from hypothesis import given
from hypothesis import strategies as st


CELEBRITY_PAGE = "/celebrity"


@given(fake_date=st.dates(datetime.date(2019, 1, 1), datetime.date(2022, 1, 1)))
def test_get_today_month_and_day(fake_date):
    if datetime.date.today().strftime("%m-%d") == fake_date.strftime("%m-%d"):
        assert get_today_month_and_day() == fake_date.strftime("%m-%d")
    else:
        assert get_today_month_and_day() != fake_date.strftime("%m-%d")


def test_celebrity_page_exists(client):
    resp = client.get(CELEBRITY_PAGE)
    assert resp.ok
    assert b'born today' in resp.content
