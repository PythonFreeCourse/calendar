import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app import config


SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_CONNECTION_STRING", config.DEVELOPMENT_DATABASE_STRING)

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_CONNECTION_STRING")
SQLALCHEMY_DATABASE_URL = "sqlite:///calendar.db"
print(SQLALCHEMY_DATABASE_URL)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
