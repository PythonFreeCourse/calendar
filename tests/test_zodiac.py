from datetime import date

import pytest

from app.internal import zodiac

DATE = date(2021, 3, 22)
DATE2 = date(2021, 4, 10)


@pytest.mark.zodiac
def test_create_zodiac_object():
    zodiac_fields = {
        'name': 'aries',
        'start_month': 3,
        'start_day_in_month': 20,
        'end_month': 4,
        'end_day_in_month': 19
    }
    result = zodiac.create_zodiac_object(zodiac_fields)
    assert result.name == 'aries'
    assert result.start_month == 3
    assert str(result) == "<Zodiac aries 20/3-19/4>"


@pytest.mark.zodiac
def test_get_correct_zodiac_first_half_month(session, zodiac1):
    result = zodiac.get_zodiac_of_day(session, DATE)
    assert result.name == zodiac1.name


@pytest.mark.zodiac
def test_get_correct_zodiac_second_half_month(session, zodiac1):
    result = zodiac.get_zodiac_of_day(session, DATE2)
    assert result.name == zodiac1.name


@pytest.mark.zodiac
def test_get_correct_month_zodiac(session, zodiac1):
    result = zodiac.get_zodiac_of_month(session, DATE2)
    assert result.name == zodiac1.name


@pytest.mark.zodiac
def test_no_zodiac(session, zodiac1):
    result = zodiac.get_zodiac_of_month(session, DATE)
    assert result is None
