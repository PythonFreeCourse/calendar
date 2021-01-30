from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import PSQL_ENVIRONMENT
from app.database import models
from app.database.database import engine, get_db
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.internal.quotes import load_quotes, daily_quotes
from app.routers import (
    agenda, celebrity, dayview, email, event, invitation, profile, search,
    telegram, whatsapp
    )
from app.telegram.bot import telegram_bot
from app.internal.logger_customizer import LoggerCustomizer
from app import config


def create_tables(engine, psql_environment):
    if 'sqlite' in str(engine.url) and psql_environment:
        raise models.PSQLEnvironmentError(
            "You're trying to use PSQL features on SQLite env.\n"
            "Please set app.config.PSQL_ENVIRONMENT to False "
            "and run the app again."
        )
    else:
        models.Base.metadata.create_all(bind=engine)


create_tables(engine, PSQL_ENVIRONMENT)
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

load_quotes.load_daily_quotes(next(get_db()))

# Configure logger
logger = LoggerCustomizer.make_logger(config.LOG_PATH,
                                      config.LOG_FILENAME,
                                      config.LOG_LEVEL,
                                      config.LOG_ROTATION_INTERVAL,
                                      config.LOG_RETENTION_INTERVAL,
                                      config.LOG_FORMAT)
app.logger = logger

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(telegram.router)
app.include_router(dayview.router)
app.include_router(email.router)
app.include_router(invitation.router)
app.include_router(whatsapp.router)
app.include_router(search.router)
app.include_router(celebrity.router)

telegram_bot.set_webhook()


# TODO: I add the quote day to the home page
# until the relavent calendar view will be developed.
@app.get("/")
@app.logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
        "quote": quote
    })
