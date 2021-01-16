from sqlalchemy.orm import Session

from app.utils.utils import save


class TestUtils:

    def test_save_success(self, user, session: Session):
        user.username = 'edit_username'
        assert save(user, session=session)

    def test_save_failure(self, session: Session):
        user = 'not a user instance'
        assert not save(user, session=session)
