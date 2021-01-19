from pydantic import BaseSettings


class Settings(BaseSettings):
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
