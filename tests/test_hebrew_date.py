from app.internal import load_hebrew_view
from app.database.models import HebrewView


def test_if_db_correct():
    example = HebrewView(0, "2021-01-01", "י״ז טבת תשפ״א")
    result = load_hebrew_view.get_hebrew_dates(example)
    assert result.date == "2021-01-01"
    assert result.hebrew_date == "י״ז טבת תשפ״א"
    assert result.count() == 1
