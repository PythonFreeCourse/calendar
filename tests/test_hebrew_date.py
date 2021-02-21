from datetime import datetime
from pyluach import dates, hebrewcal

from app.internal.hebrew_date_view import *


DAY = datetime.strptime("2021-01-01", "%Y-%m-%d").date()
DAY2 = datetime.strptime("2021-02-21", "%Y-%m-%d").date()


def test_get_hebrew_date():
    result = get_hebrew_date(DAY)
    assert result == "י״ז טבת תשפ״א"


def test_from_greogian_to_hebrew_date_and_find_month_name():
    result = from_greogian_to_hebrew_date(DAY2)
    assert result == dates.HebrewDate(5781, 12, 9)
    assert get_month_name_by_num(result) == 'אדר'

