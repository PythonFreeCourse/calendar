from functools import lru_cache
import os

from fastapi.templating import Jinja2Templates

from app import config
from app.internal.logger_customizer import LoggerCustomizer

APP_PATH = os.path.dirname(os.path.realpath(__file__))
MEDIA_PATH = os.path.join(APP_PATH, config.MEDIA_DIRECTORY)
STATIC_PATH = os.path.join(APP_PATH, "static")
TEMPLATES_PATH = os.path.join(APP_PATH, "templates")
CURSORS_PATH = os.path.join(APP_PATH, "media/cursors/")

templates = Jinja2Templates(directory=TEMPLATES_PATH)
templates.env.add_extension('jinja2.ext.i18n')

# Configure logger
logger = LoggerCustomizer.make_logger(config.LOG_PATH,
                                      config.LOG_FILENAME,
                                      config.LOG_LEVEL,
                                      config.LOG_ROTATION_INTERVAL,
                                      config.LOG_RETENTION_INTERVAL,
                                      config.LOG_FORMAT)


@lru_cache()
def get_settings():
    return config.Settings()
