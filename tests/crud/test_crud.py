"""Tests for CRUD general low-level functions."""
import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.database.crud import crud
from app.database.models_v2 import User
from app.database.models_v2 import User as UserOrm
from tests.conftest import get_test_db


def test_create_fail_no_tables_error():
    user = User()
    session = get_test_db()
    with pytest.raises(SQLAlchemyError):
        crud.insert(session, user)


def test_get_all_database_models_no_tables_error():
    session = get_test_db()
    assert crud.get_all_database_models(session, UserOrm) == []
