import pytest
from app.config import PSQL_ENVIRONMENT
from app.database.database import create_env_engine
from app.database.models import PSQLEnvironmentError
from app.main import create_tables


def test_main_create_tables_error(sqlite_engine):
    raised_error = False
    with pytest.raises(PSQLEnvironmentError):
        create_tables(sqlite_engine, True)
        raised_error = True
        assert raised_error


def test_database_create_engine():
    if PSQL_ENVIRONMENT:
        engine = create_env_engine(True)
        assert 'postgres' in str(engine.url)
    else:
        engine = create_env_engine(False)
        assert 'sqlite' in str(engine.url)
