import os

from app.database.database import SessionLocal, Base, engine

APP_PATH = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = os.path.join(APP_PATH, "static")
TEMPLATES_PATH = os.path.join(APP_PATH, "templates")


# Dependency
def get_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
