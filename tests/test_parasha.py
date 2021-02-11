from datetime import date

from app.internal import load_parasha as lp


DATE = date(2021, 3, 22)
EXAMPLE=[{'name': 'Parashat Vayechi', 'hebrew': 'פרשת ויחי', " \
            "'link': 'https://www.hebcal.com/sedrot/vayechi-20210102?i=on&utm_source=js&utm_medium=api', " \
            "'date': '2021-01-02'}]


def test_is_parashot_table_empty():
    result = lp.is_parashot_table_empty([])
    assert result == True


def test_if_db_correct(EXAMPLE, DATE):
    result = lp.get_weekly_parasha(EXAMPLE, DATE)
    assert  result.name ==  'Parashat Vayechi'
    assert result.date ==  '2021-01-02'
    assert result.count() == 1
