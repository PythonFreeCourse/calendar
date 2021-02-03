from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import config
from app.database import engine, models
from app.dependencies import get_db, logger, MEDIA_PATH, STATIC_PATH, templates
from app.internal.quotes import daily_quotes, load_quotes
from app.routers import (
    agenda, categories, dayview, email, event, invitation, profile, search,
    telegram, whatsapp
)
from app.routers.salary import routes as salary
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


create_tables(engine, config.PSQL_ENVIRONMENT)
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

load_quotes.load_daily_quotes(next(get_db()))

app.logger = logger

routers_to_include = [
    agenda.router,
    categories.router,
    dayview.router,
    email.router,
    event.router,
    invitation.router,
    profile.router,
    salary.router,
    search.router,
    telegram.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)

telegram_bot.set_webhook()


# TODO: I add the quote day to the home page
# until the relevant calendar view will be developed.
@app.get("/")
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
        "quote": quote
    })
