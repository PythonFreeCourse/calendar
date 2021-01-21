import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import config


SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_CONNECTION_STRING", config.DEVELOPMENT_DATABASE_STRING)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)