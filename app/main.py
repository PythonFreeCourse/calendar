from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import PSQL_ENVIRONMENT
from app.database import models
<<<<<<< HEAD
from app.database.database import engine
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import agenda, event, profile, email, settings


models.Base.metadata.create_all(bind=engine)

=======
from app.database.database import engine, get_db
from app.dependencies import (logger, MEDIA_PATH, STATIC_PATH, templates)
from app.internal.quotes import daily_quotes, load_quotes
from app.routers import (
    agenda, dayview, email, event, invitation, profile, search, telegram,
    whatsapp
)
from app.telegram.bot import telegram_bot


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
>>>>>>> a908f4d43983868565154bd5b072e0a50e284334
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

load_quotes.load_daily_quotes(next(get_db()))

app.logger = logger

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(telegram.router)
app.include_router(dayview.router)
app.include_router(email.router)
<<<<<<< HEAD
app.include_router(settings.router)
=======
app.include_router(invitation.router)
app.include_router(whatsapp.router)
app.include_router(search.router)

telegram_bot.set_webhook()
>>>>>>> a908f4d43983868565154bd5b072e0a50e284334


# TODO: I add the quote day to the home page
# until the relavent calendar view will be developed.
@app.get("/")
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
        "quote": quote
    })
