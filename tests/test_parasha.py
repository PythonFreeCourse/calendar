from app.internal import load_parasha


def test_if_db_correct():
    example = [{'name': 'Parashat Vayechi', 'hebrew': 'פרשת ויחי', " \
                "'link': 'https://www.hebcal.com/sedrot/vayechi-20210102?i=on&utm_source=js&utm_medium=api', " \
                "'date': '2021-01-02'}]
    result = load_parasha.get_weekly_parasha(example)
    assert result.name == 'Parashat Vayechi'
    assert result.date == '2021-01-02'
    assert result.count() == 1
