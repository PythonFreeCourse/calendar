from app.utils.invitation import get_all_invitations, get_invitation_by_id


class TestInvitations:

    def test_get_all_invitations_success(self, invitation, event, user):
        assert get_all_invitations(event=event) == [invitation]
        assert get_all_invitations(recipient=user) == [invitation]

    def test_get_all_invitations_failure(self, user):
        assert get_all_invitations(unknown_parameter=user) == []
        assert get_all_invitations(recipient=None) == []

    def test_get_invitation_by_id(self, invitation):
        assert get_invitation_by_id(invitation.id) == invitation

    def test_repr(self, invitation):
        invitation_repr = (
            f'<Invitation '
            f'({invitation.event.owner}'
            f'to {invitation.recipient})>'
        )
        assert invitation.__repr__() == invitation_repr
