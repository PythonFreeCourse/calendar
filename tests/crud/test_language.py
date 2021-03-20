"""Tests for CRUD functions of the Language model."""
import pytest
from sqlalchemy.orm import Session

from app.database.crud import language as crud

LANGUAGE_ID_TESTS = [
    (1, True),
    (2, True),
    (50, False),
]


@pytest.mark.parametrize("language_id, is_valid", LANGUAGE_ID_TESTS)
def test_get_by_id(session_v2: Session, language_id: int, is_valid: bool):
    language = crud.get_by_id(session_v2, language_id)
    if is_valid:
        assert language
    else:
        assert language is None


def test_get_all_users(session_v2: Session):
    languages = crud.get_all(session_v2)
    assert len(languages) > 0
