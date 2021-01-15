from icalendar import vCalAddress

from app.config import ICAL_VERSION, PRODUCT_ID
from app.utils.export import create_ical_calendar, create_ical_event, event_to_ical


class TestExport:

    def test_create_ical_calendar(self):
        cal = create_ical_calendar()
        assert cal.get('version') == ICAL_VERSION
        assert cal.get('prodid') == PRODUCT_ID

    def test_create_ical_event(self, event):
        ical_event = create_ical_event(event)
        assert ical_event.get('organizer') == event.owner.email
        assert ical_event.get('summary') == event.title

    def test_add_attendees(self, event, user):
        ical_event = create_ical_event(event)
        ical_event.add(
            'attendee',
            vCalAddress(f'MAILTO:{user.email}'),
            encode=0
        )
        assert vCalAddress(f'MAILTO:{user.email}') == ical_event.get('attendee')

    def test_event_to_ical(self, user, event):
        ical_event = event_to_ical(event, [user.email])

        def does_contain(item: str) -> bool:
            """Returns if calendar contains item."""

            return bytes(item, encoding='utf8') in bytes(ical_event)

        assert does_contain(ICAL_VERSION)
        assert does_contain(PRODUCT_ID)
        assert does_contain(event.owner.email)
        assert does_contain(event.title)

