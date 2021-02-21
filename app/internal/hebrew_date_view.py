from hebrew_numbers import int_to_gematria
from pyluach import dates, hebrewcal


def get_month_name_by_num(date) -> str:
    """Returns the Hebrew name date for the specific day.

        Args:
            date: The requested date.

        Returns:
            A Hebrew name date.
        """
    hebrew_dates_translate_dict = {
        'Tishrei': 'תשרי',
        'Cheshvan': 'חשוון',
        'Kislev': 'כסלו',
        'Teves': 'טבת',
        'Shvat': 'שבט',
        'Adar': 'אדר',
        'Adar Rishon': 'אדר',
        'Nissan': 'ניסן',
        'Iyar': 'אייר',
        'Sivan': 'סיון',
        'Tamuz': 'תמוז',
        'Av': 'אב',
        'Elul': 'אלול',
    }
    for month in hebrewcal.Year(date.year).itermonths():
        if date.month == month.month:
            return hebrew_dates_translate_dict[month.name]


def from_greogian_to_hebrew_date(date):
    """Returns the Hebrew date for the specific greogian date.

    Args:
        date: The requested date.

    Returns:
        A Hebrew date string.
    """

    date_split = str(date).split('-')
    new_date_format = [int(x) for x in date_split]
    gregorian_date = dates.GregorianDate(
        new_date_format[0],
        new_date_format[1],
        new_date_format[2]
    )
    return gregorian_date.to_heb()


def get_hebrew_date(date) -> str:
    """Returns the Hebrew date for the specific day.

    Args:
        date: The requested date.

    Returns:
        A Hebrew date string.
    """

    hebrew_date_list = []
    print(date)
    hebrew_date = from_greogian_to_hebrew_date(date)
    hebrew_date_list.append(int_to_gematria(hebrew_date.day))
    hebrew_date_list.append(get_month_name_by_num(hebrew_date))
    hebrew_date_list.append(int_to_gematria(hebrew_date.year % 1000))
    return ' '.join(hebrew_date_list)
