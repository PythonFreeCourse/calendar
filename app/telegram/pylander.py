from app import config
from app.dependencies import get_settings
from .models import Bot


settings: config.Settings = get_settings()

BOT_API = settings.bot_api
WEBHOOK_URL = settings.webhook_url

pylander = Bot(BOT_API, WEBHOOK_URL)
