from app.routers.event import by_id
from starlette import status


class TestEvent:

    def test_eventedit(self, client):
        response = client.get("/event/edit")
        assert response.ok
        assert b"Edit Event" in response.content

    def test_eventview_with_id(self, client):
        response = client.get("/event/view/1")
        assert response.ok
        assert b"View Event" in response.content

    def test_eventview_without_id(self, client):
        response = client.get("/event/view")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_repr(self, event):
        assert event.__repr__() == f'<Event {event.id}>'

    def test_successful_deletion(self, event_test_client, session, event):
        respons = event_test_client.delete("/event/1")
        assert respons.status_code == status.HTTP_200_OK
        assert by_id(db=session, event_id=1) is None

    def test_delete_failed(self, event_test_client, event):
        respons = event_test_client.delete("/event/2")
        assert respons.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
