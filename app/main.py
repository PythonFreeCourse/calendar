from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.config import PSQL_ENVIRONMENT
from app.database import models
from app.database.database import engine
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import (
    agenda, dayview, email, event, invitation, profile, search, telegram,
    whatsapp
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

telegram_bot.set_webhook()


@app.get("/")
@app.logger.catch()
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
    })
