from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import config
from app.config import PSQL_ENVIRONMENT
from app.database import engine, models
from app.dependencies import get_db, logger, MEDIA_PATH, STATIC_PATH, templates
from app.internal import daily_quotes, json_data_loader, load_parasha
from app.internal.languages import set_ui_language


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



json_data_loader.load_to_db(next(get_db()))
load_parasha.load_parashot(next(get_db()))
# This MUST come before the app.routers imports.
set_ui_language()


from app.routers import (  # noqa: E402
    agenda, calendar, categories, celebrity, currency, dayview,
    email, event, four_o_four, invitation,parasha, profile, search,
    weekview, telegram, whatsapp,
)
from app.routers.salary import routes as salary



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
    four_o_four.router,
    invitation.router,
    parasha.router,
    profile.router,
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
        "message": "Hello, World!",
        "quote": quote,
    })
