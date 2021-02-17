from fastapi import status


class TestFriendview:
    FRIENDVIEW = "/friendview"
    NO_EVENTS = b"No mutual events found..."

    @staticmethod
    def test_friendview_page_no_arguments_when_no_today_events(
        friendview_test_client,
        session,
    ):
        resp = friendview_test_client.get(TestFriendview.FRIENDVIEW)
        assert resp.ok
        assert TestFriendview.NO_EVENTS in resp.content

    @staticmethod
    def test_no_show_events_user_2(friendview_test_client, today_event):
        resp = friendview_test_client.get(TestFriendview.FRIENDVIEW)
        assert resp.status_code == status.HTTP_200_OK
        assert b"event 7" not in resp.content
