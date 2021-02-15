from app import config
from app.database import engine, models
from app.dependencies import get_db, logger, MEDIA_PATH, STATIC_PATH, templates
from app.internal import daily_quotes, json_data_loader

from app.internal.languages import set_ui_language
from app.internal.security.ouath2 import auth_exception_handler
from app.routers.salary import routes as salary
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


create_tables(engine, config.PSQL_ENVIRONMENT)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")
app.logger = logger

app.add_exception_handler(HTTP_401_UNAUTHORIZED, auth_exception_handler)

json_data_loader.load_to_db(next(get_db()))
# This MUST come before the app.routers imports.
set_ui_language()


from app.routers import (  # noqa: E402

    agenda, calendar, categories, celebrity, currency, dayview,
    email, event, exercise, export, four_o_four, invitation, login, logout, profile,
    register, search, telegram, weekview, whatsapp,
)

json_data_loader.load_to_db(next(get_db()))

routers_to_include = [
    agenda.router,
    calendar.router,
    categories.router,
    celebrity.router,
    currency.router,
    dayview.router,
    weekview.router,
    email.router,
    event.router,
    exercise.router,
    export.router,
    four_o_four.router,
    invitation.router,
    login.router,
    logout.router,
    profile.router,
    register.router,
    salary.router,
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
    return templates.TemplateResponse("index.html", {
        "request": request,
        "quote": quote,
    })
