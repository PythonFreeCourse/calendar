from app.database.models import InvitationStatusEnum
from app.internal.notification import get_all_invitations
from app.routers.share import (
    send_email_invitation,
    send_in_app_invitation,
    share,
    sort_emails,
)


class TestShareEvent:
    def test_share_success(self, user, event, session):
        share(event, [user.email], session)
        invitations = get_all_invitations(
            session=session,
            recipient_id=user.id,
        )
        assert invitations != []

    def test_share_failure(self, event, session):
        participants = [event.owner.email]
        share(event, participants, session)
        invitations = get_all_invitations(
            session=session,
            recipient_id=event.owner.id,
        )
        assert invitations == []

    def test_sort_emails(self, user, session):
        # the user is being imported
        # so he will be created
        data = [
            "test.email@gmail.com",  # registered user
            "not_logged_in@gmail.com",  # unregistered user
        ]
        sorted_data = sort_emails(data, session=session)
        assert sorted_data == {
            "registered": ["test.email@gmail.com"],
            "unregistered": ["not_logged_in@gmail.com"],
        }

    def test_send_in_app_invitation_success(
        self,
        user,
        sender,
        event,
        session,
    ):
        assert send_in_app_invitation([user.email], event, session=session)
        invitation = get_all_invitations(session=session, recipient=user)[0]
        assert invitation.event.owner == sender
        assert invitation.recipient == user
        session.delete(invitation)

    def test_send_in_app_invitation_failure(
        self,
        user,
        sender,
        event,
        session,
    ):
        assert (
            send_in_app_invitation([sender.email], event, session=session)
            is False
        )

    def test_send_email_invitation(self, user, event):
        send_email_invitation([user.email], event)
        # TODO add email tests
        assert True

    def test_accept(self, invitation, session):
        invitation.accept(session=session)
        assert invitation.status == InvitationStatusEnum.ACCEPTED

    def test_decline(self, invitation, session):
        invitation.decline(session=session)
        assert invitation.status == InvitationStatusEnum.DECLINED
