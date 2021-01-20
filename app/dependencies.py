import os

from fastapi.templating import Jinja2Templates

from app import config


APP_PATH = os.path.dirname(os.path.realpath(__file__))
MEDIA_PATH = os.path.join(APP_PATH, config.MEDIA_DIRECTORY)
STATIC_PATH = os.path.join(APP_PATH, "static")
TEMPLATES_PATH = os.path.join(APP_PATH, "templates")

templates = Jinja2Templates(directory=TEMPLATES_PATH)
