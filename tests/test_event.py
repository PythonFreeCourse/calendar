class TestEvent:

    def test_eventedit(self, client):
        response = client.get("/event/edit")
        assert response.status_code == 200
        assert b"Edit Event" in response.content

    def test_repr(self, event):
        assert event.__repr__() == f'<Event {event.id}>'
