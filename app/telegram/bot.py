import asyncio

from app import config
from app.dependencies import get_settings
from .models import Bot

settings: config.Settings = get_settings()

BOT_API = settings.bot_api
WEBHOOK_URL = settings.webhook_url

telegram_bot = Bot(BOT_API, WEBHOOK_URL)

loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)
asyncio.ensure_future(telegram_bot.set_webhook())
