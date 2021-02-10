import pytest

from app.database import create_env_engine
from app.database.models import PSQLEnvironmentError
from app.main import create_tables


def test_main_create_tables_error(sqlite_engine):
    raised_error = False
    with pytest.raises(PSQLEnvironmentError):
        create_tables(sqlite_engine, True)
        raised_error = True
        assert raised_error


def test_database_create_engine():
    sqlalchemy_database_url = "postgresql://postgres:1234@localhost/postgres"
    engine = create_env_engine(True, sqlalchemy_database_url)
    assert 'postgres' in str(engine.url)
    sqlalchemy_database_url = "sqlite:///./test1.db"
    engine = create_env_engine(False, sqlalchemy_database_url)
    assert 'sqlite' in str(engine.url)
