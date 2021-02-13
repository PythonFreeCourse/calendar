import pytest

from app.routers.event import get_location_coordinates
from app.database.models import Event
from sqlalchemy.sql import func


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
        'invited': 'a@gmail.com',
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
        'location': 'not a real location with coords',
        'description': 'test1',
        'invited': 'a@gmail.com',
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
    @pytest.mark.asyncio
    @pytest.mark.parametrize("location", CORRECT_LOCATIONS)
    async def test_get_location_coordinates_correct(location):
        location = await get_location_coordinates(location)
        assert all(list(location))

    @staticmethod
    @pytest.mark.asyncio
    @pytest.mark.parametrize("location", WRONG_LOCATIONS)
    async def test_get_location_coordinates_wrong(location):
        location = await get_location_coordinates(location)
        assert location == location

    @staticmethod
    @pytest.mark.asyncio
    async def test_event_location_correct(event_test_client, session):
        response = event_test_client.post(
            "event/edit",
            data=TestGeolocation.CORRECT_LOCATION_EVENT
        )
        assert response.ok
        event_id = session.query(func.count(Event.id)).scalar()
        url = event_test_client.app.url_path_for('eventview',
                                                 event_id=event_id)
        response = event_test_client.get(url)
        location = await get_location_coordinates(
            TestGeolocation.CORRECT_LOCATION_EVENT['location']
        )
        address = location.location.split(" ")[0]
        assert bytes(address, "utf-8") in response.content

    @staticmethod
    def test_event_location_wrong(event_test_client, session):
        address = TestGeolocation.WRONG_LOCATION_EVENT['location']
        response = event_test_client.post(
            "event/edit",
            data=TestGeolocation.WRONG_LOCATION_EVENT
        )
        assert response.ok
        event_id = session.query(func.count(Event.id)).scalar()
        url = event_test_client.app.url_path_for('eventview',
                                                 event_id=event_id)
        response = event_test_client.get(url)
        assert bytes(address, "utf-8") in response.content
