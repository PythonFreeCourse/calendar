from datetime import datetime

import pytest
from pyluach import dates

from app.internal.hebrew_date_view import (
    from_gregorian_to_hebrew_date,
    get_hebrew_date_in_words,
    get_month_name_by_num
)
from app.internal.languages import set_ui_language

DAY = datetime.strptime("2021-01-01", "%Y-%m-%d").date()
ADAR = datetime.strptime("2021-02-15", "%Y-%m-%d").date()
ADAR_A = datetime.strptime("2019-02-15", "%Y-%m-%d").date()
ADAR_B = datetime.strptime("2019-03-08", "%Y-%m-%d").date()

TRANSLATION_DATES = [
    (1, "en", "17 Teves 5781"),
    (2, "he", "י״ז טבת תשפ״א"),
]


@pytest.mark.parametrize(
    "language_id, language_code, expected_translation", TRANSLATION_DATES
)
def test_get_hebrew_date(language_id, language_code, expected_translation):
    set_ui_language(language_code)
    result = get_hebrew_date_in_words(DAY, language_id)
    assert result == expected_translation


def test_from_gregorian_to_hebrew_date_and_find_month_name():
    result = from_gregorian_to_hebrew_date(ADAR)
    assert result == dates.HebrewDate(5781, 12, 3)
    assert get_month_name_by_num(result) == "Adar"


def test_if_leap_year():
    result_a = from_gregorian_to_hebrew_date(ADAR_A)
    result_b = from_gregorian_to_hebrew_date(ADAR_B)
    assert get_month_name_by_num(result_a) == "Adar Rishon"
    assert get_month_name_by_num(result_b) == "Adar Sheni"
