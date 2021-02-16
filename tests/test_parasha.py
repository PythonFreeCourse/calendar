from app.internal import weekly_parasha


def test_create_parasha_object():
    parashot_fields = {
        'name': 'Parashat Vayechi',
        'hebrew_name': 'פרשת ויחי',
        'link': 'https://www.hebcal.com/sedrot/vayechi-20210102?'
        'i=on&utm_source=js&utm_medium=api',
        'date': '2021-01-02'
    }
    result = weekly_parasha.create_parasha_object(parashot_fields)
    assert result.name == 'Parashat Vayechi'
    assert result.date == '2021-01-02'
