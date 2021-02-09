from app.internal.calendar_privacy import can_show_calendar
# after user system is merged:
# from app.internal.security.dependancies import CurrentUser
from app.routers.user import create_user


USER_DATA = {
    'username': 'new_test_username',
    'email': 'new_test.email@gmail.com',
    'password': 'new_test_password',
    'language': 'english',
    'language_id': 1
}


def test_can_show_calendar_public(session):
    user = create_user(
            session=session,
            **USER_DATA
    )
    user.privacy = "Public"
    #  to be replaced after user system is merged:
    # current_user = CurrentUser(**user.__dict__)
    current_user = user
    result = can_show_calendar(
        requested_user_username='new_test_username',
        db=session, current_user=current_user
    )
    assert result
    session.delete(user)
    session.commit()


def test_can_show_calendar_private(session):
    user = create_user(
        session=session,
        **USER_DATA
    )
    another_user = create_user(
        session=session,
        username='new_test_username2',
        email='new_test.email2@gmail.com',
        password='passpar_2',
        language='english',
        language_id=1
    )
    current_user = user
    # to be replaced after user system is merged:
    # current_user = CurrentUser(**user.__dict__)

    result_a = can_show_calendar(
        requested_user_username='new_test_username2',
        db=session, current_user=current_user
    )
    result_b = can_show_calendar(
        requested_user_username='new_test_username',
        db=session, current_user=current_user
    )
    assert not result_a
    assert result_b
    session.delete(user)
    session.delete(another_user)
    session.commit()
