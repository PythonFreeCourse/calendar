from app.dependencies import get_db
from app.internal import load_parasha
from fastapi import Depends


def test_if_db_correct():
    first_parasha = [0, 'Parashat Vayechi', 'פרשת ויחי',
                     'https://www.hebcal.com/sedrot/vayechi-20210102?',
                     'i=on&utm_source=js&utm_medium=api',
                     '2021-01-02']
    result = load_parasha.get_weekly_parasha(Depends(get_db))
    assert result.name is first_parasha[1]
    assert result.date is first_parasha[5]
