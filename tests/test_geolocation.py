import pytest

from app.routers.event import get_location_coordinates


CORRECT_LOCATION_EVENT = {
    'title': 'test title',
    'start_date': '2021-02-18',
    'start_time': '18:00',
    'end_date': '2021-02-18',
    'end_time': '20:00',
    'location_type': 'address',
    'location': 'מנדלה מוכר ספרים 5, תל אביב',
    'description': 'test1',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'public'
}

WRONG_LOCATION_EVENT = {
    'title': 'test title',
    'start_date': '2021-02-18',
    'start_time': '18:00',
    'end_date': '2021-02-18',
    'end_time': '20:00',
    'location_type': 'address',
    'location': 'not a location',
    'description': 'test1',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'public'
}

CORRECT_LOCATIONS = [
    "Tamuz 13, Ashdod",
    "Menachem Begin 21, Tel Aviv",
    "רמב״ן 25, ירושלים"
]

WRONG_LOCATIONS = [
    "not a real location with coords",
    "מיקום לא תקין",
    "https://us02web.zoom.us/j/875384596"
]

@pytest.mark.parametrize("location", CORRECT_LOCATIONS)
def test_get_location_coordinates_correct(location):
    is_valid = True
    assert any(get_location_coordinates(location))
    


@pytest.mark.parametrize("location", WRONG_LOCATIONS)
def test_get_location_coordinates_wrong(location):
    assert not all(get_location_coordinates(location))
