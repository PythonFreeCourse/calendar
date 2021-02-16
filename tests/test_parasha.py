from app.internal import load_parasha
from sqlalchemy.orm import Session


def test_if_db_correct(session: Session):
    first_parasha = [0, 'Parashat Vayechi', 'פרשת ויחי',
                     'https://www.hebcal.com/sedrot/vayechi-20210102?',
                     'i=on&utm_source=js&utm_medium=api',
                     '2021-01-02']
    result = load_parasha.get_weekly_parasha(session)
    assert result[0].name is first_parasha[1]
    assert result[0].date is first_parasha[5]
