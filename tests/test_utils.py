from sqlalchemy.orm import Session

import pytest

from app.internal.utils import save


class TestUtils:

    @pytest.mark.utils
    def test_save_success(self, user, session: Session):
        user.username = 'edit_username'
        assert save(user, session=session)

    @pytest.mark.utils
    def test_save_failure(self, session: Session):
        user = 'not a user instance'
        assert not save(user, session=session)
