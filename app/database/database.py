from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import config

settings = config.get_settings()
SQLALCHEMY_DATABASE_URL = settings.database_connection_string


def create_env_engine(psql_environment, sqlalchemy_database_url):
    if not psql_environment:
        return create_engine(
            sqlalchemy_database_url, connect_args={"check_same_thread": False})

    return create_engine(sqlalchemy_database_url)


engine = create_env_engine(config.PSQL_ENVIRONMENT, SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
