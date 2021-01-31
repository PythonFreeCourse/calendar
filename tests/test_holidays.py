import pytest
from app.database.models import Event
from app.routers import profile
import os


class TestHolidaysImport:
    HOLIDAYS = '/profile/import_holidays'

    @staticmethod
    def test_import_holidays_page_exists(client):
        resp = client.get(TestHolidaysImport.HOLIDAYS)
        assert resp.ok
        assert b'Import holidays using ics file' in resp.content

    def test_get_holidays(self, session, user):
        current_folder = os.path.dirname(os.path.realpath(__file__))
        resource_folder = os.path.join(current_folder, 'resources')
        test_file = os.path.join(resource_folder, 'ics_example.txt')
        with open(test_file) as file:
            ics_content = file.read()
            holidays = profile.get_holidays_from_file(ics_content, session)
            profile.save_holidays_to_db(holidays, session)
        assert len(session.query(Event).all()) == 4
