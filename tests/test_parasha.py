from app.internal import load_parasha
from app.database.models import Parasha


def test_if_db_correct():
    example = Parasha(
       0, 'Parashat Vayechi', 'פרשת ויחי',
       'https://www.hebcal.com/sedrot/vayechi-20210102?'
       'i=on&utm_source=js&utm_medium=api',
       '2021-01-02')
    result = load_parasha.get_weekly_parasha(example)
    assert result.name == 'Parashat Vayechi'
    assert result.date == '2021-01-02'
    assert result.count() == 1
