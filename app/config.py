import os
from typing import Tuple

from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings

# flake8: noqa

# general
DOMAIN = 'Our-Domain'

# DATABASE
DEVELOPMENT_DATABASE_STRING = "sqlite:///./dev.db"
# Set the following True if working on PSQL environment or set False otherwise
PSQL_ENVIRONMENT = False

# MEDIA
MEDIA_DIRECTORY = 'media'
PICTURE_EXTENSION = '.png'
AVATAR_SIZE = (120, 120)

# API-KEYS
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

# export
ICAL_VERSION = '2.0'
PRODUCT_ID = '-//Our product id//'

# email
email_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME") or "user",
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD") or "password",
    MAIL_FROM=os.getenv("MAIL_FROM") or "a@a.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
)

# PATHS
STATIC_ABS_PATH = os.path.abspath("static")


class Settings(BaseSettings):
    # DATABASE
    database_connection_string: str = DEVELOPMENT_DATABASE_STRING
    # MEDIA
    media_directory: str = MEDIA_DIRECTORY
    media_picture_extension: str = PICTURE_EXTENSION
    media_avatar_size: Tuple[int, int] = AVATAR_SIZE
    # EMAILS
    smtp_username: str = "no-username"
    smtp_password: str = "no-password"
    smtp_from_email: str = "invite@calendar-app.com"
    smtp_port: int = 3999
    smtp_server: str = "localhost"
    smtp_use_tls: bool = False
    smtp_use_ssl: bool = False
    smtp_use_credentials: bool = False


def get_settings():
    return Settings()
