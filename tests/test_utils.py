from app.utils.utils import save


class TestUtils:

    def test_save_success(self, user):
        user.username = 'edit_username'
        assert save(user)

    def test_save_failure(self):
        user = 'not a user instance'
        assert not save(user)
