from datetime import datetime
from pyluach import dates

from app.internal.hebrew_date_view import (
    get_hebrew_date,
    from_greogian_to_hebrew_date,
    get_month_name_by_num,
)


DAY = datetime.strptime("2021-01-01", "%Y-%m-%d").date()
ADAR = datetime.strptime("2021-02-15", "%Y-%m-%d").date()
ADAR_A = datetime.strptime("2019-02-15", "%Y-%m-%d").date()
ADAR_B = datetime.strptime("2019-03-08", "%Y-%m-%d").date()


def test_get_hebrew_date():
    result = get_hebrew_date(DAY)
    assert result == "י״ז טבת תשפ״א"


def test_from_greogian_to_hebrew_date_and_find_month_name():
    result = from_greogian_to_hebrew_date(ADAR)
    assert result == dates.HebrewDate(5781, 12, 3)
    assert get_month_name_by_num(result) == 'אדר'


def test_if_leap_year():
    result_a = from_greogian_to_hebrew_date(ADAR_A)
    result_b = from_greogian_to_hebrew_date(ADAR_B)
    assert get_month_name_by_num(result_a) == "אדר(א')"
    assert get_month_name_by_num(result_b) == "אדר(ב')"
