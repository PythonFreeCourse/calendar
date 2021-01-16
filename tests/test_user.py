from app.config import session
from app.utils.user import create_user, does_user_exist, get_users


class TestUser:

    def test_create_user(self):
        user = create_user(
            username='new_test_username',
            password='new_test_password',
            email='new_test.email@gmail.com',
        )
        assert user.username == 'new_test_username'
        assert user.password == 'new_test_password'
        assert user.email == 'new_test.email@gmail.com'
        print(user)
        session.delete(user)

    def test_get_users_success(self, user):
        assert get_users(username=user.username) == [user]
        assert get_users(password=user.password) == [user]
        assert get_users(email=user.email) == [user]

    def test_get_users_failure(self):
        assert get_users(username='wrong username') == []

    def test_does_user_exist_success(self, user):
        assert does_user_exist(username=user.username)
        assert does_user_exist(user_id=user.id)
        assert does_user_exist(email=user.email)

    def test_does_user_exist_failure(self):
        assert not does_user_exist(username='wrong username')

    def test_repr(self, user):
        assert user.__repr__() == f'<User {user.id}>'
