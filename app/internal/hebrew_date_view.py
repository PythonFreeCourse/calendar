from datetime import datetime

from hebrew_numbers import int_to_gematria
from pyluach import dates, hebrewcal


EN_TO_HEB_MONTH_NAMES = {
    'Tishrei': 'תשרי',
    'Cheshvan': 'חשוון',
    'Kislev': 'כסלו',
    'Teves': 'טבת',
    'Shvat': 'שבט',
    'Adar': 'אדר',
    'Adar Rishon': "אדר(א')",
    'Adar Sheni': "אדר(ב')",
    'Nissan': 'ניסן',
    'Iyar': 'אייר',
    'Sivan': 'סיוון',
    'Tamuz': 'תמוז',
    'Av': 'אב',
    'Elul': 'אלול',
}


def get_month_name_by_num(date: datetime) -> str:
    """Returns the Hebrew name date for the specific day.

        Args:
            date: The requested date.

        Returns:
            A Hebrew name date.
    """
    for month in hebrewcal.Year(date.year).itermonths():
        if date.month == month.month:
            return EN_TO_HEB_MONTH_NAMES[month.name]


def from_greogian_to_hebrew_date(date: datetime):
    """Returns the Hebrew date for the specific greogian date.

    Args:
        date: The requested date.

    Returns:
        A Hebrew date string.
    """
    date_split = str(date).split('-')
    new_date_format = [int(x) for x in date_split]
    gregorian_date = dates.GregorianDate(*new_date_format)
    return gregorian_date.to_heb()


def get_hebrew_date_in_words(date: datetime) -> str:
    """Returns the Hebrew date for the specific day.

    Args:
        date: The requested date.

    Returns:
        A Hebrew date string.
    """

    hebrew_date_object = from_greogian_to_hebrew_date(date)
    return ' '.join((
        int_to_gematria(hebrew_date_object.day),
        get_month_name_by_num(hebrew_date_object),
        int_to_gematria(hebrew_date_object.year % 1000)
    ))
