from datetime import date

from app.internal import shabbat

SHABBAT_TIME = {'items': [
    {'title': 'Fast begins'},
    {'title': "Ta'anit Esther"},
    {'title': 'Fast ends'},
    {'title': 'Erev Purim'},
    {'title': 'Purim'},
    {'title': 'Candle lighting: 17:15',
     'date': '2021-02-26T17:15:00+02:00',
     'category': 'candles',
     'title_orig': 'Candle lighting',
     'hebrew': 'הדלקת נרות'},
    {'title': 'Parashat Tetzaveh'},
    {'title': 'Havdalah: 18:11',
     'date': '2021-02-27T18:11:00+02:00',
     'category': 'havdalah',
     'title_orig': 'Havdalah',
     'hebrew': 'הבדלה'}
]}
DATE1 = date(2021, 2, 27)
FRIDAY = date(2021, 2, 27)


def test_get_shabbat_if_date_friday():
    result = shabbat.get_shabbat_if_date_friday(SHABBAT_TIME, FRIDAY.date())
    assert result.start_hour == '17:15'

def test_return_none_if_date_no_friday():
    result = shabbat.get_shabbat_if_date_friday(SHABBAT_TIME, DATE1)
    assert result is None
