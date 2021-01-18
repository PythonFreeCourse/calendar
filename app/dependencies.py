import os

from app.database.database import SessionLocal

APP_PATH = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = os.path.join(APP_PATH, "static")
TEMPLATES_PATH = os.path.join(APP_PATH, "templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
