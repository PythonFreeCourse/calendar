from app.internal.calendar_privacy import can_show_calendar
# TODO after user system is merged:
# from app.internal.security.dependancies import CurrentUser
from app.routers.user import create_user


def test_can_show_calendar_public(session, user):
    user.privacy = "Public"
    # TODO to be replaced after user system is merged:
    # current_user = CurrentUser(**user.__dict__)
    current_user = user
    result = can_show_calendar(
        requested_user_username='test_username',
        db=session, current_user=current_user
    )
    assert result is True
    session.commit()


def test_can_show_calendar_private(session, user):
    another_user = create_user(
        session=session,
        username='new_test_username2',
        email='new_test.email2@gmail.com',
        password='passpar_2',
        language_id=1
    )
    current_user = user
    # TODO to be replaced after user system is merged:
    # current_user = CurrentUser(**user.__dict__)

    result_a = can_show_calendar(
        requested_user_username='new_test_username2',
        db=session, current_user=current_user
    )
    result_b = can_show_calendar(
        requested_user_username='test_username',
        db=session, current_user=current_user
    )
    assert result_a is False
    assert result_b is True
    session.delete(another_user)
    session.commit()
