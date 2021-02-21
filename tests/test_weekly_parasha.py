from app.internal import weekly_parasha


def test_create_parasha_object():
    parashot_fields = {
        'name': 'Parashat Vayechi',
        'hebrew': 'פרשת ויחי',
        'link': 'https://www.hebcal.com/sedrot/vayechi-20210102?'
        'i=on&utm_source=js&utm_medium=api'
    }
    result = weekly_parasha.create_parasha_object(parashot_fields)
    assert result.name == 'Parashat Vayechi'
