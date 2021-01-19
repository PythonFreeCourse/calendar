class TestEvent:

    def test_eventedit(self, client):
        response = client.get("/event/edit")
        assert response.status_code == 200
        assert b"Edit Event" in response.content

    def test_eventview_with_id(self, client):
        response = client.get("/event/view/1")
        assert response.status_code == 200
        assert b"View Event" in response.content

    def test_eventview_without_id(self, client):
        response = client.get("/event/view")
        assert response.status_code == 404

    def test_repr(self, event):
        assert event.__repr__() == f'<Event {event.id}>'
