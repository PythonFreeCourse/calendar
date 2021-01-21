import os

import os

from dotenv import load_dotenv

from app import config
from .models import Bot

load_dotenv()


BOT_API = os.getenv("BOT_API", config.BOT_API)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", config.WEBHOOK_URL)

pylander = Bot(BOT_API, WEBHOOK_URL)
