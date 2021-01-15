class TestEvent:

    def test_repr(self, event):
        assert event.__repr__() == f'<Event {event.id}>'
