import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import config


SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_CONNECTION_STRING", config.DEVELOPMENT_DATABASE_STRING)


def create_env_engine(psql_environment):
    if not psql_environment:
        return create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

    return create_engine(SQLALCHEMY_DATABASE_URL)


engine = create_env_engine(config.PSQL_ENVIRONMENT)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
