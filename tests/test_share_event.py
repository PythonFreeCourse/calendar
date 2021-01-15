from app.config import session
from app.internal.share_event import sort_emails, send_in_app_invitation, accept, share
from app.utils.invitation import get_all_invitations


class TestShareEvent:

    def test_sort_emails(self, user):
        # the user is being imported
        # so he will be created
        data = [
            'test.email@gmail.com',  # registered user
            'not_logged_in@gmail.com',  # unregistered user
        ]
        sorted_data = sort_emails(data)
        assert sorted_data == {
            'registered': ['test.email@gmail.com'],
            'unregistered': ['not_logged_in@gmail.com']
        }

    def test_send_in_app_invitation_success(self, user, sender, event):
        send_in_app_invitation([user.email], event)
        invitation = get_all_invitations(recipient=user)[0]
        assert invitation.event.owner == sender
        assert invitation.recipient == user
        session.delete(invitation)

    def test_send_in_app_invitation_failure(self, event):
        send_in_app_invitation([event.owner.email], event)
        invitation = get_all_invitations(recipient=event.owner)
        assert invitation == []

    def test_send_email_invitation(self):
        # missing
        pass

    def test_accept(self, invitation):
        accept(invitation)
        assert invitation.status == 'accepted'
