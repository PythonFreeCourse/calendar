import os
from functools import lru_cache

from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app import config
from app.database import SessionLocal
from app.internal.logger_customizer import LoggerCustomizer

GOOGLE_ERROR = config.CLIENT_SECRET_FILE is None
APP_PATH = os.path.dirname(os.path.realpath(__file__))
MEDIA_PATH = os.path.join(APP_PATH, config.MEDIA_DIRECTORY)
STATIC_PATH = os.path.join(APP_PATH, "static")
TEMPLATES_PATH = os.path.join(APP_PATH, "templates")
CURSORS_PATH = os.path.join(MEDIA_PATH, "cursors")
SOUNDS_PATH = os.path.join(STATIC_PATH, "tracks")
templates = Jinja2Templates(directory=TEMPLATES_PATH)
templates.env.add_extension("jinja2.ext.i18n")


# Configure logger
logger = LoggerCustomizer.make_logger(
    config.LOG_PATH,
    config.LOG_FILENAME,
    config.LOG_LEVEL,
    config.LOG_ROTATION_INTERVAL,
    config.LOG_RETENTION_INTERVAL,
    config.LOG_FORMAT,
)

if os.path.isdir(config.UPLOAD_DIRECTORY):
    UPLOAD_PATH = config.UPLOAD_DIRECTORY
else:
    try:
        UPLOAD_PATH = os.path.join(os.getcwd(), config.UPLOAD_DIRECTORY)
        os.mkdir(UPLOAD_PATH)
    except OSError as e:
        logger.critical(e)
        raise OSError(e)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@lru_cache()
def get_settings():
    return config.Settings()
