from app.internal import hebrew_date_view


def test_create_hebrew_dates_object():
    hebrew_dates_fields = {
        'date_gregorian': "2021-01-01",
        'date_hebrew': "י״ז טבת תשפ״א"
        }
    result = hebrew_date_view.create_hebrew_dates_object(hebrew_dates_fields)
    assert result.hebrew_date == "י״ז טבת תשפ״א"
