
from starlette.status import HTTP_302_FOUND, HTTP_200_OK

from app.routers.notification import (
    get_all_invitations, get_invitation_by_id, router
)


class TestNotificationRoutes:
    NO_NOTIFICATIONS = b"You don't have any new notifications."

    def test_view_no_notifications(self, notification_test_client):
        url = router.url_path_for('view_notifications')
        resp = notification_test_client.get(url)
        assert resp.ok
        assert self.NO_NOTIFICATIONS in resp.content

    def test_accept_invitations(
            self, user, invitation,
            notification_test_client):
        data = {"invite_id ": invitation.id}
        url = router.url_path_for('accept_invitations')
        resp = notification_test_client.post(url, data=data)
        assert resp.status_code == HTTP_302_FOUND

    def test_decline_invitations(
            self, user, invitation, notification_test_client, session
    ):
        data = {"invite_id ": invitation.id}
        url = router.url_path_for('decline_invitations')
        resp = notification_test_client.post(url, data=data)
        assert resp.status_code == HTTP_302_FOUND

    def test_mark_message_as_read(
            self, user, message, notification_test_client, session
    ):
        data = {"message_id ": message.id}
        url = router.url_path_for('mark_message_as_read')
        resp = notification_test_client.post(url, data=data)
        assert resp.status_code == HTTP_302_FOUND

    def test_mark_all_as_read(
            self, user, message, sec_message,
            notification_test_client, session
    ):
        url = router.url_path_for('mark_all_as_read')
        resp = notification_test_client.get(url)
        assert resp.status_code == HTTP_200_OK


class TestNotification:

    def test_get_all_invitations_success(
            self, invitation, event, user, session
    ):
        invitations = get_all_invitations(event=event, session=session)
        assert invitations == [invitation]
        invitations = get_all_invitations(recipient=user, session=session)
        assert invitations == [invitation]

    def test_get_all_invitations_failure(self, user, session):
        invitations = get_all_invitations(
            unknown_parameter=user, session=session)
        assert invitations == []

        invitations = get_all_invitations(
            recipient=None, session=session)
        assert invitations == []

    def test_get_invitation_by_id(self, invitation, session):
        get_invitation = get_invitation_by_id(
            invitation.id, session=session)
        assert get_invitation == invitation

    def test_repr(self, invitation):
        invitation_repr = (
            f'<Invitation '
            f'({invitation.event.owner}'
            f'to {invitation.recipient})>'
        )
        assert invitation.__repr__() == invitation_repr
