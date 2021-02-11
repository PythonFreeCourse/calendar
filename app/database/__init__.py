import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_CONNECTION_STRING", config.DEVELOPMENT_DATABASE_STRING)


def create_env_engine(psql_environment, sqlalchemy_database_url):
    if not psql_environment:
        return create_engine(
            sqlalchemy_database_url, connect_args={"check_same_thread": False})

    return create_engine(sqlalchemy_database_url)


engine = create_env_engine(config.PSQL_ENVIRONMENT, SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
