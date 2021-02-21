from app.internal.notification import get_all_invitations, get_invitation_by_id
from app.routers.notification import router
from tests.fixtures.client_fixture import login_client


class TestNotificationRoutes:
    NO_NOTIFICATIONS = b"You don't have any new notifications."
    NEW_NOTIFICATIONS_URL = router.url_path_for("view_notifications")
    LOGIN_DATA = {"username": "registered_user", "password": "registered_user"}

    def test_view_no_notifications(
        self,
        registered_user,
        notification_test_client,
    ):
        login_client(notification_test_client, self.LOGIN_DATA)
        url = router.url_path_for("view_notifications")
        resp = notification_test_client.get(url)
        assert resp.ok
        assert self.NO_NOTIFICATIONS in resp.content

    def test_accept_invitations(
        self,
        registered_user,
        invitation,
        notification_test_client,
    ):
        login_client(notification_test_client, self.LOGIN_DATA)
        data = {"invite_id": invitation.id, "next": self.NEW_NOTIFICATIONS_URL}
        url = router.url_path_for("accept_invitations")
        resp = notification_test_client.post(url, data=data)
        assert resp.ok

    def test_decline_invitations(
        self,
        registered_user,
        invitation,
        notification_test_client,
        session,
    ):
        login_client(notification_test_client, self.LOGIN_DATA)
        data = {"invite_id": invitation.id, "next": self.NEW_NOTIFICATIONS_URL}
        url = router.url_path_for("decline_invitations")
        resp = notification_test_client.post(url, data=data)
        assert resp.ok

    def test_mark_message_as_read(
        self,
        registered_user,
        message,
        notification_test_client,
        session,
    ):
        login_client(notification_test_client, self.LOGIN_DATA)
        data = {"message_id": message.id, "next": self.NEW_NOTIFICATIONS_URL}
        url = router.url_path_for("mark_message_as_read")
        resp = notification_test_client.post(url, data=data)
        assert resp.ok

    def test_mark_all_as_read(
        self,
        registered_user,
        message,
        sec_message,
        notification_test_client,
        session,
    ):
        login_client(notification_test_client, self.LOGIN_DATA)
        url = router.url_path_for("mark_all_as_read")
        data = {"next": self.NEW_NOTIFICATIONS_URL}
        resp = notification_test_client.post(url, data=data)
        assert resp.ok


class TestNotification:
    def test_get_all_invitations_success(
        self,
        invitation,
        event,
        user,
        session,
    ):
        invitations = get_all_invitations(event=event, session=session)
        assert invitations == [invitation]
        invitations = get_all_invitations(recipient=user, session=session)
        assert invitations == [invitation]

    def test_get_all_invitations_failure(self, user, session):
        invitations = get_all_invitations(
            unknown_parameter=user,
            session=session,
        )
        assert invitations == []

        invitations = get_all_invitations(recipient=None, session=session)
        assert invitations == []

    def test_get_invitation_by_id(self, invitation, session):
        get_invitation = get_invitation_by_id(invitation.id, session=session)
        assert get_invitation == invitation

    def test_invitation_repr(self, invitation):
        invitation_repr = (
            f"<Invitation ({invitation.event.owner} "
            f"to {invitation.recipient})>"
        )
        assert invitation.__repr__() == invitation_repr

    def test_message_repr(self, message):
        message_repr = f"<Message {message.id}>"
        assert message.__repr__() == message_repr
