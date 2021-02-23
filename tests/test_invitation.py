from fastapi import status

from app.routers.invitation import get_all_invitations, get_invitation_by_id


class TestInvitations:
    NO_INVITATIONS = b"You don't have any invitations."
    URL = "/invitations/"

    @staticmethod
    def test_view_no_invitations(invitation_test_client):
        response = invitation_test_client.get(TestInvitations.URL)
        assert response.ok
        assert TestInvitations.NO_INVITATIONS in response.content

    @staticmethod
    def test_accept_invitations(user, invitation, invitation_test_client):
        invitation = {"invite_id ": invitation.id}
        resp = invitation_test_client.post(
            TestInvitations.URL, data=invitation)
        assert resp.status_code == status.HTTP_302_FOUND

    @staticmethod
    def test_get_all_invitations_success(invitation, event, user, session):
        invitations = get_all_invitations(event=event, db=session)
        assert invitations == [invitation]
        invitations = get_all_invitations(recipient=user, db=session)
        assert invitations == [invitation]

    @staticmethod
    def test_get_all_invitations_failure(user, session):
        invitations = get_all_invitations(unknown_parameter=user, db=session)
        assert invitations == []

        invitations = get_all_invitations(recipient=None, db=session)
        assert invitations == []

    @staticmethod
    def test_get_invitation_by_id(invitation, session):
        get_invitation = get_invitation_by_id(invitation.id, db=session)
        assert get_invitation == invitation

    @staticmethod
    def test_repr(invitation):
        invitation_repr = (
            f'<Invitation '
            f'({invitation.event.owner}'
            f'to {invitation.recipient})>'
        )
        assert invitation.__repr__() == invitation_repr
