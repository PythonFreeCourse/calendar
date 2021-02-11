import pytest

from app.routers.user import create_user, does_user_exist, get_users


class TestUser:

    @pytest.mark.user
    def test_create_user(self, session):
        user = create_user(
            session=session,
            username='new_test_username',
            password='new_test_password',
            email='new_test.email@gmail.com',
            language='english',
            language_id=1
        )
        assert user.username == 'new_test_username'
        assert user.password == 'new_test_password'
        assert user.email == 'new_test.email@gmail.com'
        assert user.language == 'english'
        session.delete(user)
        session.commit()

    @pytest.mark.user
    def test_get_users_success(self, user, session):
        assert get_users(username=user.username, session=session) == [user]
        assert get_users(password=user.password, session=session) == [user]
        assert get_users(email=user.email, session=session) == [user]

    @pytest.mark.user
    def test_get_users_failure(self, session, user):
        assert get_users(username='wrong username', session=session) == []
        assert get_users(wrong_param=user.username, session=session) == []

    @pytest.mark.user
    def test_does_user_exist_success(self, user, session):
        assert does_user_exist(username=user.username, session=session)
        assert does_user_exist(user_id=user.id, session=session)
        assert does_user_exist(email=user.email, session=session)

    @pytest.mark.user
    def test_does_user_exist_failure(self, session):
        assert not does_user_exist(username='wrong username', session=session)
        assert not does_user_exist(session=session)

    @pytest.mark.user
    def test_repr(self, user):
        assert user.__repr__() == f'<User {user.id}>'
