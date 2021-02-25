from datetime import date

from hebrew_numbers import int_to_gematria
from pyluach import dates, hebrewcal
from pyluach.dates import HebrewDate


HEBREW_LANGUAGE_ID = 2
HEB_MONTH_NAMES = {
    'Tishrei': _("Tishrei"),
    'Cheshvan': _("Cheshvan"),
    'Kislev': _("Kislev"),
    'Teves': _("Teves"),
    'Shvat': _("Shvat"),
    'Adar': _("Adar"),
    'Adar Rishon': _("Adar Rishon"),
    'Adar Sheni': _("Adar Sheni"),
    'Nissan': _("Nissan"),
    'Iyar': _("Iyar"),
    'Sivan': _("Sivan"),
    'Tamuz': _("Tamuz"),
    'Av': _("Av"),
    'Elul': _("Elul"),
}


def get_hebrew_date_in_words(calendar_date: date, language_id: int) -> str:
    """Returns the Hebrew date for the specific day.

    Args:
        calendar_date: The requested date.
        language_id: The user's language.

    Returns:
        A Hebrew date string.
    """

    hebrew_date_object = from_gregorian_to_hebrew_date(calendar_date)
    day = hebrew_date_object.day
    month = get_month_name_by_num(hebrew_date_object)
    month = _("Teves")
    year = hebrew_date_object.year
    if language_id == HEBREW_LANGUAGE_ID:
        day = int_to_gematria(day)
        year = int_to_gematria(year % 1000)
    return ' '.join((str(day), str(month), str(year)))


def get_month_name_by_num(calendar_date: HebrewDate) -> str:
    """Returns the Hebrew name date for the specific day.

        Args:
            calendar_date: The requested date.

        Returns:
            A Hebrew name date.
    """
    for month in hebrewcal.Year(calendar_date.year).itermonths():
        if calendar_date.month == month.month:
            return HEB_MONTH_NAMES[month.name]


def from_gregorian_to_hebrew_date(calendar_date: date) -> HebrewDate:
    """Returns the Hebrew date for the specific gregorian date.

    Args:
        calendar_date: The requested date.

    Returns:
        A HebrewDate object.
    """
    gregorian_date = dates.GregorianDate(
        calendar_date.year,
        calendar_date.month,
        calendar_date.day,
    )
    return gregorian_date.to_heb()
