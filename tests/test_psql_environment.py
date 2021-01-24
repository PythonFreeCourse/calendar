import pytest
from app.database.models import PSQLEnvironmentError
from app.main import create_tables


def test_main_create_tables_error(sqlite_engine):
    raised_error = False
    with pytest.raises(PSQLEnvironmentError):
        create_tables(sqlite_engine, True)
        raised_error = True
        assert raised_error
