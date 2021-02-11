from starlette.status import HTTP_302_FOUND

import pytest

from app.routers.invitation import get_all_invitations, get_invitation_by_id


class TestInvitations:
    NO_INVITATIONS = b"You don't have any invitations."
    URL = "/invitations/"

    @pytest.mark.invitation
    def test_view_no_invitations(self, invitation_test_client):
        resp = invitation_test_client.get(self.URL)
        assert resp.ok
        assert self.NO_INVITATIONS in resp.content

    @pytest.mark.invitation
    def test_accept_invitations(
            self, user, invitation,
            invitation_test_client):
        invitation = {"invite_id ": invitation.id}
        resp = invitation_test_client.post(
            self.URL, data=invitation)
        assert resp.status_code == HTTP_302_FOUND

    @pytest.mark.invitation
    def test_get_all_invitations_success(
            self, invitation, event, user, session
    ):
        invitations = get_all_invitations(event=event, session=session)
        assert invitations == [invitation]
        invitations = get_all_invitations(recipient=user, session=session)
        assert invitations == [invitation]

    @pytest.mark.invitation
    def test_get_all_invitations_failure(self, user, session):
        invitations = get_all_invitations(
            unknown_parameter=user, session=session)
        assert invitations == []

        invitations = get_all_invitations(
            recipient=None, session=session)
        assert invitations == []

    @pytest.mark.invitation
    def test_get_invitation_by_id(self, invitation, session):
        get_invitation = get_invitation_by_id(
            invitation.id, session=session)
        assert get_invitation == invitation

    @pytest.mark.invitation
    def test_repr(self, invitation):
        invitation_repr = (
            f'<Invitation '
            f'({invitation.event.owner}'
            f'to {invitation.recipient})>'
        )
        assert invitation.__repr__() == invitation_repr
