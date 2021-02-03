import pytest

from app.routers.event import get_location_coordinates


class TestGeolocation:

    CORRECT_LOCATION_EVENT = {
        'title': 'test title',
        'start_date': '2021-02-18',
        'start_time': '18:00',
        'end_date': '2021-02-18',
        'end_time': '20:00',
        'location_type': 'address',
        'location': 'אדר 11, אשדוד',
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
        "https://us02web.zoom.us/j/376584566"
    ]

    @staticmethod
    @pytest.mark.parametrize("location", CORRECT_LOCATIONS)
    def test_get_location_coordinates_correct(location):
        assert any(get_location_coordinates(location))

    @staticmethod
    @pytest.mark.parametrize("location", WRONG_LOCATIONS)
    def test_get_location_coordinates_wrong(location):
        assert not all(get_location_coordinates(location))

    @staticmethod
    def test_event_location_correct(event_test_client, user):
        response = event_test_client.post(
            "event/edit",
            data=TestGeolocation.CORRECT_LOCATION_EVENT
        )
        assert response.ok
        url = event_test_client.app.url_path_for('eventview', event_id=1)
        response = event_test_client.get(url)
        location = get_location_coordinates(
            TestGeolocation.CORRECT_LOCATION_EVENT['location']
        )
        location_name = location[2].split()[0]
        assert bytes(location_name, "utf-8") in response.content

    @staticmethod
    def test_event_location_wrong(event_test_client, user):
        response = event_test_client.post(
            "event/edit",
            data=TestGeolocation.WRONG_LOCATION_EVENT
        )
        assert response.ok
        url = event_test_client.app.url_path_for('eventview', event_id=1)
        response = event_test_client.get(url)
        location = get_location_coordinates(
            TestGeolocation.CORRECT_LOCATION_EVENT['location']
        )
        location_name = location[2].split()[0]
        assert not bytes(location_name, "utf-8") in response.content
