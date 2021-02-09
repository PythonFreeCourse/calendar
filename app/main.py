from app.config import PSQL_ENVIRONMENT
from app.database import models
from app.database.database import engine, get_db
from app.dependencies import (
    logger, MEDIA_PATH, STATIC_PATH, templates)
from app.internal import daily_quotes, json_data_loader
from app.internal.languages import set_ui_language
from app.internal.security.ouath2 import my_exception_handler
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_401_UNAUTHORIZED
from sqlalchemy.orm import Session


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
app.logger = logger

app.add_exception_handler(HTTP_401_UNAUTHORIZED, my_exception_handler)

json_data_loader.load_to_db(next(get_db()))
# This MUST come before the app.routers imports.
set_ui_language()

from app.routers import (  # noqa: E402
    agenda, calendar, categories, currency, dayview, email,
    event, invitation, login, logout, profile, register,
    search, telegram, whatsapp
)

json_data_loader.load_to_db(next(get_db()))

routers_to_include = [
    agenda.router,
    calendar.router,
    categories.router,
    currency.router,
    dayview.router,
    email.router,
    event.router,
    invitation.router,
    login.router,
    logout.router,
    profile.router,
    register.router,
    search.router,
    telegram.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)


# TODO: I add the quote day to the home page
# until the relevant calendar view will be developed.
@app.get("/")
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "quote": quote,
    })
